"""A fake NIS-Elements: a microscope in memory, for testing without one.

``FakeNisApi`` stands in for ``nis_dll.NisDll``: an in-memory microscope whose
limits, objective names and optical configurations match the Ti2 simulator.
``running_bridge`` puts the real bridge server in front of it, so code built
on the client (an engine, an assistant) can be tested end to end:

    with running_bridge(FakeNisApi()) as server:
        client = NisClient("127.0.0.1", server.server_address[1])

``python -m nis_bridge.fake`` serves it on the bridge's usual port instead, so
the engine and the assistant can be tried without a microscope.

``save_tiff`` writes a real 16-bit TIFF whose pixels all equal the capture
number, so a test can tell which capture ended up in which frame, or the
picture in ``frame`` when one is set. Needs numpy and tifffile, which the
bridge itself does not.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager

import numpy as np
import tifffile

from . import dispatch, optconf
from .nis_dll import NisError
from .settings import HOST, PORT

IMAGE_SHAPE = (48, 64)  # height, width

# The shape of NIS's optical configuration backup (BackupOptConf), cut down to what
# optconf.py reads: one <OptN> per configuration, an exposure for fast and quality.
_BACKUP = (
    '<?xml version="1.0" encoding="UTF-16"?><variant version="1.0">'
    '<optconf_backup runtype="CLxListVariant"><OpticalConfigs runtype="CLxListVariant">'
    "{blocks}</OpticalConfigs>"
    '<Objectives runtype="CLxListVariant"></Objectives></optconf_backup></variant>'
)
_BLOCK = (
    '<Opt{i} runtype="CLxListVariant"><Name runtype="CLxStringW" value="{name}"/>'
    '<ObjectiveName runtype="CLxStringW" value="Plan Apo 10x"/>'
    '<CameraSettingList runtype="CLxListVariant">'
    '<CameraUserName runtype="CLxStringW" value="Fake camera"/>'
    '<LightPathName runtype="CLxStringW" value="L100"/>'
    '<wszFormatText runtype="CLxStringW" value="16-bit - No Binning"/>'
    '<dBinningX runtype="double" value="1.000000000000000"/>'
    '<PropertiesFast runtype="CLxListVariant"><Exposure runtype="double" value="{ms:.15f}"/>'
    '<CaptureMaxExposure runtype="double" value="1000.000000000000000"/></PropertiesFast>'
    '<PropertiesQuality runtype="CLxListVariant"><Exposure runtype="double" value="{ms:.15f}"/>'
    "</PropertiesQuality></CameraSettingList></Opt{i}>"
)


class FakeNisApi:
    def __init__(self, *, pfs: bool = True, calibrated: bool = False) -> None:
        self.position = {"x": 1000.0, "y": -500.0, "z": 500.0}
        self.limits = {
            "x": {"min": -57000.0, "max": 57000.0},
            "y": {"min": -37500.0, "max": 37500.0},
            "z": {"min": 0.0, "max": 10000.0},
        }
        self.configurations = ["DAPI", "FITC", "TxRed", "Brightfield"]
        self.saved_exposures = dict.fromkeys(self.configurations, 100.0)  # ms
        self.import_fails = 0  # how many imports to come answer but add nothing
        self.objectives = {1: "Plan Apo 10x", 2: "Apo 20x WI", 3: "", 4: "Plan Apo 60x WI"}
        # lights, lasers and filter changers, named as on the Ti2 simulator
        self.lights = {"DIA": {"on": False, "voltage": None, "iris": 0.5}}
        self.lasers = {
            "SpectraIII": [
                {"name": f"{nm} nm", "wavelength_nm": nm, "on": False, "power": 0}
                for nm in (405, 440, 475, 510, 555, 575, 637, 748)
            ]
        }
        self.power_steps = 101  # laser power 0 to 100
        self.filters = {
            "Turret-Up": ["DAPI", "GFP", "mCherry", "", "Cy5", "Empty"],
            "Turret-Lo": ["", "Empty"],
        }
        self.filter_positions = dict.fromkeys(self.filters, 1)
        self.shutters = {"DIA LED": False, "EPI": False}  # open or not
        self.condenser = {"position": 1, "positions": 7}
        self.apertures = {1: {"size": 100.0, "steps": 1001}}  # by NIS's type: 1 epi-field
        self.zoom_state = {"zoom": 1.0, "manual": True}
        self.analyzer = False
        self.analyzer_moves = True  # the simulator's analyzer does not
        self.pfs_offset_value, self.pfs_dish_value = 3000, 0
        self.heat_stages = {}  # name: temperature
        self.port_state = {"position": 1, "positions": 4}  # None: no light path port
        self.disk = {"shutter_open": False, "speed_rpm": 4000}
        self.piezo = None  # um moved in all, or None: no piezo Z drive
        self.nosepiece = 1
        self.has_pfs = pfs
        self.pfs_on = False
        self.focal_plane_z = 502.0  # where the PFS locks
        self.autofocus_result = 1
        self.calibrated = calibrated
        self.image_shape = IMAGE_SHAPE
        self.frame: np.ndarray | None = None  # a picture to save instead of the plain one
        self.camera_fails = False
        self.exposure = 33.0  # ms, as the Ti2 simulator starts
        self.camera_format = "FMT 1x1 16"
        self.camera_formats = ("FMT 1x1 16", "FMT 2x2 16", "FMT 4x4 16")  # what it has
        self.roi = {"left": 512, "top": 512, "right": 1536, "bottom": 1536}
        self.averaging = self.integration = 1
        self.incubators = {}  # key: {gas_percent, ...}
        self.captures = 0
        self.open_images = 0
        self.calls: list[str] = []

    def version(self) -> str:
        return "6.10.02 (Build 2031)"

    # stage
    def get_position(self) -> dict[str, float]:
        return dict(self.position)

    def get_limits(self) -> dict[str, dict[str, float]]:
        return {axis: dict(bounds) for axis, bounds in self.limits.items()}

    def _refuse_beyond_limits(self, **target: float) -> None:
        """Like a real stage: a target outside the limits set in NIS is refused."""
        for axis, value in target.items():
            if not self.limits[axis]["min"] <= value <= self.limits[axis]["max"]:
                raise NisError(f"StgMove: {axis} = {value:g} is outside the stage limits (-2)")

    def move_xyz(self, x: float, y: float, z: float) -> None:
        self._refuse_beyond_limits(x=x, y=y, z=z)
        self.calls.append(f"move_xyz({x:g},{y:g},{z:g})")
        self.position = {"x": x, "y": y, "z": z}

    def move_xy(self, x: float, y: float) -> None:
        self._refuse_beyond_limits(x=x, y=y)
        self.calls.append(f"move_xy({x:g},{y:g})")
        self.position.update(x=x, y=y)

    def move_z(self, z: float) -> None:
        self._refuse_beyond_limits(z=z)
        self.calls.append(f"move_z({z:g})")
        self.position["z"] = z

    # optical configurations and camera
    def optical_configurations(self) -> list[str]:
        return list(self.configurations)

    def select_optical_configuration(self, name: str) -> None:
        self.calls.append(f"config({name})")

    def backup_optical_configurations(self, path: str) -> None:
        blocks = "".join(
            _BLOCK.format(i=i, name=name, ms=self.saved_exposures.get(name, 100.0))
            for i, name in enumerate(self.configurations)
        )
        optconf.write(path, _BACKUP.format(blocks=blocks))

    def import_optical_configurations(self, path: str, options: int) -> None:
        xml = optconf.read(path)
        for start, end, name in optconf.blocks(xml):
            exists = [n for n in self.configurations if optconf.matches(n, name)]
            if exists and options == 0:
                raise NisError(f"RestoreOptConfEx: {name!r} exists; NIS would wait in a dialog")
            if self.import_fails:
                self.import_fails -= 1
                return  # NIS answers, but nothing changes
            if exists and options == 2:  # only names NIS does not have
                continue
            self.calls.append(f"import({name},{options})")
            if not exists:
                self.configurations.append(name)
            self.saved_exposures[exists[0] if exists else name] = optconf.settings(xml[start:end])[
                "exposure_ms"
            ]

    def delete_optical_configuration(self, name: str) -> None:
        self.calls.append(f"delete({name})")
        if name in self.configurations:  # like NIS: an unknown name is no error
            self.configurations.remove(name)
            self.saved_exposures.pop(name, None)

    def set_exposure_ms(self, exposure_ms: float) -> float:
        self.calls.append(f"exposure({exposure_ms:g})")
        self.exposure = max(1.0, round(exposure_ms))  # the camera applies whole milliseconds
        return self.exposure

    def exposure_ms(self) -> float:
        return self.exposure

    def camera(self) -> dict:
        return {  # as the Ti2 simulator answers
            "name": "Hamamatsu C11440-22C 9Z0022",
            "driver": "Hamamatsu Simulator",
            "width_px": 2048,
            "height_px": 2048,
            "pixel_um": 6.5,
            "format": self.camera_format,
            "roi": dict(self.roi),
        }

    def camera_averaging(self) -> int:
        return self.averaging

    def camera_integration(self) -> int:
        return self.integration

    def set_camera_format(self, camera_format: str) -> None:
        self.calls.append(f"format({camera_format})")
        if camera_format in self.camera_formats:  # like NIS: an unknown one changes nothing
            self.camera_format = camera_format

    def set_roi(self, left: int, top: int, right: int, bottom: int) -> None:
        self.calls.append(f"roi({left},{top},{right},{bottom})")
        self.roi = {"left": left, "top": top, "right": right, "bottom": bottom}

    def set_camera_averaging(self, frames: int) -> None:
        self.calls.append(f"averaging({frames})")
        self.averaging = frames

    def set_camera_integration(self, frames: int) -> None:
        self.calls.append(f"integration({frames})")
        self.integration = frames

    def incubator(self, key: str) -> dict:
        zero = dict.fromkeys(
            ("gas_percent", "target_gas_percent", "pressure_mbar", "target_pressure_mbar"), 0.0
        )
        return self.incubators.get(key, zero)  # like NIS without one: zeros

    # lights, lasers and filter changers
    def _light(self, name: str) -> dict:
        if name not in self.lights:
            raise NisError(f"Stg_Light: {name!r}: DR_NOTAVAILABLE (-4)")
        return self.lights[name]

    def light_names(self) -> list[str]:
        return list(self.lights)

    def light_on(self, name: str) -> bool:
        return self._light(name)["on"]

    def set_light_on(self, name: str, on: bool) -> None:
        self.calls.append(f"light({name},{'on' if on else 'off'})")
        self._light(name)["on"] = on

    def light_voltage_controllable(self, name: str) -> bool:
        return self._light(name)["voltage"] is not None

    def light_voltage(self, name: str) -> float:
        return self._light(name)["voltage"]

    def set_light_voltage(self, name: str, volts: float) -> None:
        self.calls.append(f"voltage({name},{volts:g})")
        self._light(name)["voltage"] = round(volts, 1)  # NIS takes the closest step

    def light_iris_controllable(self, name: str) -> bool:
        return self._light(name)["iris"] is not None

    def light_iris(self, name: str) -> float:
        return self._light(name)["iris"]

    def set_light_iris(self, name: str, intensity: float) -> None:
        self.calls.append(f"iris({name},{intensity:g})")
        self._light(name)["iris"] = intensity

    def laser_names(self) -> list[str]:
        return list(self.lasers)

    def laser_line_count(self, laser: str) -> int:
        return len(self.lasers.get(laser, []))

    def _line(self, laser: str, index: int) -> dict:
        return self.lasers[laser][index]  # NIS counts lines from 0

    def laser_line_name(self, laser: str, line: int) -> str:
        return self._line(laser, line)["name"]

    def laser_wavelength_nm(self, laser: str, line: int) -> int:
        return self._line(laser, line)["wavelength_nm"]

    def laser_line_on(self, laser: str, line: int) -> bool:
        return self._line(laser, line)["on"]

    def set_laser_line_on(self, laser: str, line: int, on: bool) -> None:
        self.calls.append(f"laser({laser},{line},{'on' if on else 'off'})")
        self._line(laser, line)["on"] = on

    def laser_power(self, laser: str, line: int) -> int:
        return self._line(laser, line)["power"]

    def laser_power_steps(self, laser: str, line: int) -> int:
        return self.power_steps

    def set_laser_power(self, laser: str, line: int, power: int) -> None:
        self.calls.append(f"power({laser},{line},{power})")
        self._line(laser, line)["power"] = power

    def shutter_names(self) -> list[str]:
        return list(self.shutters)

    def shutter_open(self, name: str) -> bool:
        return self.shutters[name]

    def set_shutter_open(self, name: str, open_: bool) -> None:
        self.calls.append(f"shutter({name},{'open' if open_ else 'closed'})")
        self.shutters[name] = open_

    def condenser_present(self) -> bool:
        return self.condenser is not None

    def condenser_position(self) -> int:
        return self.condenser["position"]

    def condenser_count(self) -> int:
        return self.condenser["positions"]

    def set_condenser_position(self, position: int) -> None:
        self.calls.append(f"condenser({position})")
        self.condenser["position"] = position

    def aperture_steps(self, kind: int) -> int:
        return self.apertures.get(kind, {"steps": 0})["steps"]

    def aperture(self, kind: int) -> float:
        return self.apertures[kind]["size"]

    def set_aperture(self, kind: int, size: float) -> None:
        self.calls.append(f"aperture({kind},{size:g})")
        self.apertures[kind]["size"] = size

    def zoom_present(self) -> bool:
        return self.zoom_state is not None

    def zoom_manual(self) -> bool:
        return self.zoom_state["manual"]

    def zoom(self) -> float:
        return self.zoom_state["zoom"]

    def set_zoom(self, zoom: float) -> None:
        self.calls.append(f"zoom({zoom:g})")
        self.zoom_state["zoom"] = 1.5 if zoom > 1.25 else 1.0  # the closest step NIS has

    def analyzer_present(self) -> bool:
        return True

    def analyzer_in(self) -> bool:
        return self.analyzer

    def set_analyzer_in(self, inserted: bool) -> None:
        self.calls.append(f"analyzer({'in' if inserted else 'out'})")
        if self.analyzer_moves:
            self.analyzer = inserted

    def heat_stage_names(self) -> list[str]:
        return list(self.heat_stages)

    def heat_stage_temperature(self, name: str) -> float:
        return self.heat_stages[name]

    def heat_stage_status(self, name: str) -> int:
        return 3  # holding

    def pfs_offset(self) -> int:
        return self.pfs_offset_value

    def set_pfs_offset(self, offset: int) -> None:
        self.calls.append(f"pfs_offset({offset})")
        self.pfs_offset_value = offset

    def pfs_dish_changeable(self) -> bool:
        return True

    def pfs_dish(self) -> int:
        return self.pfs_dish_value

    def set_pfs_dish(self, dish: int) -> None:
        self.calls.append(f"pfs_dish({dish})")
        self.pfs_dish_value = dish

    def port_present(self) -> bool:
        return self.port_state is not None

    def port(self) -> int:
        return self.port_state["position"]

    def port_count(self) -> int:
        return self.port_state["positions"]

    def set_port(self, port: int) -> None:
        self.calls.append(f"port({port})")
        self.port_state["position"] = port

    def disk_shutter_open(self) -> bool:
        return self.disk["shutter_open"]

    def set_disk_shutter_open(self, open_: bool) -> None:
        self.calls.append(f"disk_shutter({'open' if open_ else 'closed'})")
        self.disk["shutter_open"] = open_

    def disk_speed_rpm(self) -> int:
        return self.disk["speed_rpm"]

    def set_disk_speed_rpm(self, rpm: int) -> None:
        self.calls.append(f"disk_speed({rpm})")
        self.disk["speed_rpm"] = rpm

    def piezo_present(self) -> bool:
        return self.piezo is not None

    def move_piezo_z(self, distance_um: float) -> None:
        self.calls.append(f"piezo({distance_um:g})")
        self.piezo += distance_um

    def center_piezo_z(self) -> None:
        self.calls.append("piezo(center)")
        self.piezo = 0.0

    def filter_changer_names(self) -> list[str]:
        return list(self.filters)

    def filter_position(self, changer: str) -> int:
        return self.filter_positions[changer]

    def filter_position_count(self, changer: str) -> int:
        return len(self.filters[changer])

    def filter_name(self, changer: str, position: int) -> str:
        return self.filters[changer][position - 1]

    def set_filter_position(self, changer: str, position: int) -> None:
        if not 1 <= position <= len(self.filters[changer]):
            raise NisError(f"Stg_Filter_SetPosition({changer}, {position}): DR_BADPARAMETER (-2)")
        self.calls.append(f"filter({changer},{position})")
        self.filter_positions[changer] = position

    # nosepiece
    def nosepiece_present(self) -> bool:
        return True

    def nosepiece_count(self) -> int:
        return len(self.objectives)

    def nosepiece_position(self) -> int:
        return self.nosepiece

    def objective_name(self, position: int) -> str:
        return self.objectives[position]

    def set_nosepiece_position(self, position: int) -> None:
        if position not in self.objectives:
            raise NisError(f"Stg_SetNosepiecePosition({position}): DR_BADPARAMETER (-2)")
        self.calls.append(f"objective({position})")
        self.nosepiece = position

    # focus
    def pfs_present(self) -> bool:
        return self.has_pfs

    def pfs_status(self) -> int:
        return 1 if self.pfs_on else 0

    def set_pfs(self, on: bool) -> None:
        self.calls.append(f"pfs({'on' if on else 'off'})")
        self.pfs_on = on

    def wait_for_pfs(self, timeout_s: float) -> None:
        self.position["z"] = self.focal_plane_z

    def autofocus(self, range_um: float, speed: int) -> int:
        self.calls.append(f"autofocus({range_um:g},{speed})")
        if self.autofocus_result == 1:
            self.position["z"] += 3.0  # the sharpest plane was 3 um higher
        return self.autofocus_result

    # images
    def capture(self) -> None:
        if self.camera_fails:
            raise NisError("Capture: the camera did not answer (-8)")
        self.captures += 1
        self.open_images += 1
        self.calls.append("capture")

    def pixel_size_um(self) -> float:
        return 0.108 if self.calibrated else 0.0

    def save_tiff(self, path: str) -> None:
        if not self.open_images:
            raise NisError("ImageSaveAs: no image is open")
        image = self.frame if self.frame is not None else np.full(self.image_shape, self.captures)
        tifffile.imwrite(path, image.astype(np.uint16))

    def close_document(self) -> None:
        self.open_images = max(0, self.open_images - 1)


@contextmanager
def running_bridge(fake: FakeNisApi) -> Iterator[dispatch.BridgeServer]:
    """The real bridge server on a free local port, with ``fake`` behind it.

    A background thread stands in for the NIS macro loop that runs the requests.
    """
    server = dispatch.serve(fake, HOST, 0)
    stop = threading.Event()

    def macro_loop() -> None:
        while not stop.is_set():
            server.pump(wait_s=0.01)

    thread = threading.Thread(target=macro_loop, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        stop.set()
        thread.join()
        server.shutdown()
        server.server_close()


def main() -> None:
    """Serve a fake NIS on the bridge's usual port until Ctrl+C."""
    server = dispatch.serve(FakeNisApi(calibrated=True), HOST, PORT)
    print(f"A fake NIS-Elements answers on port {PORT}. Press Ctrl+C to stop it.")
    try:
        while True:
            server.pump(wait_s=0.05)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
