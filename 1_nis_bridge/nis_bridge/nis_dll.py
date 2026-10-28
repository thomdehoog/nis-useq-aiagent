"""C to Python: the NIS-Elements functions the bridge calls, one thin wrapper each.

NIS-Elements ships its own Python, and every NIS macro function (``StgMoveXY``,
``Capture``, ``ImageSaveAs`` ...) is also exported by ``g5_regprocs.dll``, a C
library. ``NisDll`` calls them through ``ctypes``, turns their return codes
into Python exceptions and their output values into plain Python, and does
nothing else: the meaning of a request lives in ``readers.py`` and
``commands.py``. What the DLL does not export (most camera settings) goes
through ``nis_macro.py`` instead: slower (about 24 ms), but NIS 6.10's
``nis.call_proc`` cannot hand values back safely on its own. Signatures
come from the macro reference installed with NIS (Docs/nis/eng_ar). Units are
micrometres. Tests replace this class with ``fake.FakeNisApi``.

Standard library only: this runs inside NIS-Elements.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import ctypes as ct
from typing import Any

from .dialogs import ClickOk
from .nis_macro import NisMacro
from .settings import (
    CAMERA_MODE,
    CAMERA_MODES,
    CLOSE_WITHOUT_ASKING,
    INFOSTR_VERSION,
    OPTCONF_IMPORT_DONE,
    TIFF_ALL_LAYERS,
)

# What NIS's own codes mean; lookup tables, not settings. 1 and 2 mean success.
DR_CODES = {
    1: "DR_OK",
    2: "DR_PARTIALLYOK",
    0: "DR_CANCELED",
    -1: "DR_UNKNOWNERROR",
    -2: "DR_BADPARAMETER",
    -3: "DR_NOTSUPPORTED",
    -4: "DR_NOTAVAILABLE",
    -5: "DR_NOTAUTOMATIC",
    -6: "DR_NOTCALIBRATED",
    -7: "DR_NOTINITIALIZED",
}

# Stg_GetPFSStatus values.
PFS_STATUS = {
    -1: "error or not connected",
    0: "off, in range",
    1: "on, focused",
    3: "off, out of range",
    4: "off, PFS optics not set (dichroic mirror out)",
    5: "on, searching",
    6: "on, search stopped (cannot find focus)",
    7: "disabled, objective not supported",
}


class NisError(RuntimeError):
    """A NIS function returned an error code."""


def _check(rc: int, what: str) -> None:
    if rc not in (1, 2):
        raise NisError(f"{what}: {DR_CODES.get(rc, 'unknown code')} ({rc})")


def _check_negative(value: int, what: str) -> int:
    """Raise for a negative DR code, which every NIS function uses for failure.

    This is for functions whose success value is a count, or is not documented.
    """
    if value < 0:
        _check(value, what)
    return int(value)


# ---------------------------------------------------------------------------
# NIS functions, one small method each. Signatures come from the macro
# reference installed with NIS (Docs/nis/eng_ar). Units: micrometres.
# ---------------------------------------------------------------------------


class NisDll:
    def __init__(self) -> None:
        self._dll = ct.cdll.g5_regprocs
        self._functions: dict[str, Any] = {}
        self._macro = NisMacro()  # for what the DLL does not export

    def _fn(self, name: str, argtypes: list, restype: Any = ct.c_int32) -> Any:
        if name not in self._functions:
            fn = getattr(self._dll, name)
            fn.argtypes, fn.restype = argtypes, restype
            self._functions[name] = fn
        return self._functions[name]

    def version(self) -> str:
        buf = ct.create_unicode_buffer(64)
        self._fn("Get_InfoStr", [ct.c_int32, ct.c_wchar_p])(INFOSTR_VERSION, buf)
        return buf.value

    # stage
    def get_position(self) -> dict[str, float]:
        x, y, z = ct.c_double(), ct.c_double(), ct.c_double()
        fn = self._fn("StgGetPos", [ct.POINTER(ct.c_double)] * 3)
        _check(fn(ct.byref(x), ct.byref(y), ct.byref(z)), "StgGetPos")
        return {"x": x.value, "y": y.value, "z": z.value}

    def get_limits(self) -> dict[str, dict[str, float]]:
        x0, y0, x1, y1 = (ct.c_double() for _ in range(4))
        fn = self._fn("StgXY_GetLimits", [ct.POINTER(ct.c_double)] * 4)
        _check(fn(ct.byref(x0), ct.byref(y0), ct.byref(x1), ct.byref(y1)), "StgXY_GetLimits")
        z0, z1 = ct.c_double(), ct.c_double()
        fn = self._fn("StgZ_GetLimits", [ct.POINTER(ct.c_double)] * 2)
        _check(fn(ct.byref(z0), ct.byref(z1)), "StgZ_GetLimits")
        return {
            "x": {"min": x0.value, "max": x1.value},
            "y": {"min": y0.value, "max": y1.value},
            "z": {"min": z0.value, "max": z1.value},
        }

    def move_xyz(self, x: float, y: float, z: float) -> None:
        fn = self._fn("StgMove", [ct.c_double, ct.c_double, ct.c_double, ct.c_int32])
        _check(fn(x, y, z, 0), "StgMove")

    def move_xy(self, x: float, y: float) -> None:
        _check(self._fn("StgMoveXY", [ct.c_double, ct.c_double, ct.c_int32])(x, y, 0), "StgMoveXY")

    def move_z(self, z: float) -> None:
        _check(self._fn("StgMoveZ", [ct.c_double, ct.c_int32])(z, 0), "StgMoveZ")

    # optical configurations and camera
    def optical_configurations(self) -> list[str]:
        count = self._fn("GetOptConfCount", [])()
        get_name = self._fn("GetOptConfName", [ct.c_int32, ct.c_wchar_p, ct.c_int32])
        names = []
        for index in range(max(count, 0)):
            buf = ct.create_unicode_buffer(256)
            get_name(index, buf, 256)
            names.append(buf.value)
        return names

    def select_optical_configuration(self, name: str) -> None:
        _check_negative(self._fn("SelectOptConf", [ct.c_wchar_p])(name), f"SelectOptConf({name})")

    def backup_optical_configurations(self, path: str) -> None:
        """Write every optical configuration to ``path`` as XML (see ``optconf.py``)."""
        _check_negative(self._fn("BackupOptConf", [ct.c_wchar_p])(path), "BackupOptConf")

    def import_optical_configurations(self, path: str, options: int) -> None:
        """Import the configurations in the XML file at ``path`` into NIS's.

        ``options`` says what happens to a name NIS already has (settings.py). NIS
        ends with a message that waits for a click, and has no way to leave it out;
        it is pressed here.
        """
        fn = self._fn("RestoreOptConfEx", [ct.c_wchar_p, ct.c_int32])
        with ClickOk(*OPTCONF_IMPORT_DONE):
            _check_negative(fn(path, options), "RestoreOptConfEx")

    def delete_optical_configuration(self, name: str) -> None:
        fn = self._fn("DeleteOptConf", [ct.c_wchar_p])
        _check_negative(fn(name), f"DeleteOptConf({name})")

    def set_exposure_ms(self, exposure_ms: float) -> float:
        """Set the camera exposure; return the value NIS applied (it may round it).

        Not exported by the DLL; NIS registers it internally and ``nis.call_proc``
        reaches it by name. It answers with a list: the return value, then each
        argument as it is after the call. Only a value goes in, so no macro is needed.
        """
        import nis  # exists only inside NIS-Elements

        out = nis.call_proc("Camera_ExposureSet", float(exposure_ms))
        out = list(out) if isinstance(out, (list, tuple)) else [out]
        return float(out[1]) if len(out) > 1 else float(exposure_ms)

    # lights (lamps and LEDs, by name), lasers (a multi-laser's lines) and filter changers
    def _name(self, function: str, index: int) -> str:
        """A device name from a Get...Name(index, buffer) function; '' when there is none."""
        buf = ct.create_unicode_buffer(256)
        self._fn(function, [ct.c_int32, ct.c_wchar_p])(index, buf)
        return buf.value

    def light_names(self) -> list[str]:
        count = _check_negative(self._fn("Stg_Light_GetCount", [])(), "Stg_Light_GetCount")
        return [self._name("Stg_Light_GetName", i) for i in range(count)]

    def light_on(self, name: str) -> bool:
        state = self._fn("Stg_Light_GetState", [ct.c_wchar_p])(name)
        return bool(_check_negative(state, f"Stg_Light_GetState({name})"))

    def set_light_on(self, name: str, on: bool) -> None:
        fn = self._fn("Stg_Light_SetState", [ct.c_wchar_p, ct.c_int32])
        _check(fn(name, 1 if on else 0), f"Stg_Light_SetState({name})")

    def light_voltage_controllable(self, name: str) -> bool:
        return self._fn("Stg_Light_IsVoltageControllable", [ct.c_wchar_p])(name) == 1

    def light_voltage(self, name: str) -> float:
        fn = self._fn("Stg_Light_GetVoltage", [ct.c_wchar_p], ct.c_double)
        return float(fn(name))

    def set_light_voltage(self, name: str, volts: float) -> None:
        """NIS takes the closest voltage it can set."""
        fn = self._fn("Stg_Light_SetVoltage", [ct.c_wchar_p, ct.c_double])
        _check(fn(name, volts), f"Stg_Light_SetVoltage({name})")

    def light_iris_controllable(self, name: str) -> bool:
        return self._fn("Stg_Light_IsIrisControllable", [ct.c_wchar_p])(name) == 1

    def light_iris(self, name: str) -> float:
        return float(self._fn("Stg_Light_GetIrisIntensity", [ct.c_wchar_p], ct.c_double)(name))

    def set_light_iris(self, name: str, intensity: float) -> None:
        fn = self._fn("Stg_Light_SetIrisIntensity", [ct.c_wchar_p, ct.c_double])
        if fn(name, intensity) != 1:
            raise NisError(f"Stg_Light_SetIrisIntensity({name}, {intensity:g}) was refused")

    def laser_names(self) -> list[str]:
        count = _check_negative(self._fn("Stg_GetMultiLaserCount", [])(), "Stg_GetMultiLaserCount")
        return [self._name("Stg_GetMultiLaserName", i) for i in range(count)]

    def laser_line_count(self, laser: str) -> int:
        return max(int(self._fn("Stg_GetMultiLaserNumLines", [ct.c_wchar_p])(laser)), 0)

    def laser_line_name(self, laser: str, line: int) -> str:
        buf = ct.create_unicode_buffer(256)
        fn = self._fn("Stg_GetMultiLaserLineName", [ct.c_wchar_p, ct.c_int32, ct.c_wchar_p])
        fn(laser, line, buf)
        return buf.value

    def laser_wavelength_nm(self, laser: str, line: int) -> int:
        fn = self._fn("Stg_GetMultiLaserWavelength", [ct.c_wchar_p, ct.c_int32])
        return int(fn(laser, line))

    def laser_line_on(self, laser: str, line: int) -> bool:
        fn = self._fn("Stg_GetMultiLaserLineUsed", [ct.c_wchar_p, ct.c_int32])
        return fn(laser, line) == 1

    def set_laser_line_on(self, laser: str, line: int, on: bool) -> None:
        fn = self._fn("Stg_SetMultiLaserLineUsed", [ct.c_wchar_p, ct.c_int32, ct.c_int32])
        if fn(laser, line, 1 if on else 0) != 1:
            raise NisError(f"Stg_SetMultiLaserLineUsed({laser}, {line}) was refused")

    def laser_power(self, laser: str, line: int) -> int:
        return int(self._fn("Stg_GetMultiLaserPower", [ct.c_wchar_p, ct.c_int32])(laser, line))

    def laser_power_steps(self, laser: str, line: int) -> int:
        fn = self._fn("Stg_GetMultiLaserPowerSteps", [ct.c_wchar_p, ct.c_int32])
        return int(fn(laser, line))

    def set_laser_power(self, laser: str, line: int, power: int) -> None:
        fn = self._fn("Stg_SetMultiLaserPower", [ct.c_wchar_p, ct.c_int32, ct.c_uint32])
        if fn(laser, line, power) != 1:
            raise NisError(f"Stg_SetMultiLaserPower({laser}, {line}, {power}) was refused")

    def shutter_names(self) -> list[str]:
        count = _check_negative(self._fn("Stg_GetShutterCount", [])(), "Stg_GetShutterCount")
        fn = self._fn("Stg_GetShutterName", [ct.c_int32, ct.c_wchar_p, ct.c_int32])
        names = []
        for index in range(count):
            buf = ct.create_unicode_buffer(256)
            fn(index, buf, 255)
            names.append(buf.value)
        return names

    def shutter_open(self, name: str) -> bool:
        return self._fn("Stg_GetShutterStateEx", [ct.c_wchar_p])(name) == 1

    def set_shutter_open(self, name: str, open_: bool) -> None:
        fn = self._fn("Stg_SetShutterStateEx", [ct.c_wchar_p, ct.c_int32])
        _check_negative(fn(name, 1 if open_ else 0), f"Stg_SetShutterStateEx({name})")

    # the transmitted light path: condenser, apertures, zoom, analyzer
    def condenser_present(self) -> bool:
        return self._fn("Stg_IsCondenserPresent", [])() == 1

    def condenser_position(self) -> int:
        position = self._fn("Stg_GetCondenserPosition", [])()
        return _check_negative(position, "Stg_GetCondenserPosition")

    def condenser_count(self) -> int:
        count = self._fn("Stg_GetCondenserPositions", [])()
        return _check_negative(count, "Stg_GetCondenserPositions")

    def set_condenser_position(self, position: int) -> None:
        fn = self._fn("Stg_SetCondenserPosition", [ct.c_int32])
        _check_negative(fn(position), f"Stg_SetCondenserPosition({position})")

    def aperture_steps(self, kind: int) -> int:
        return max(int(self._fn("Stg_GetApertureSteps", [ct.c_int32])(kind)), 0)

    def aperture(self, kind: int) -> float:
        return float(self._fn("Stg_GetAperturePosition", [ct.c_int32], ct.c_double)(kind))

    def set_aperture(self, kind: int, size: float) -> None:
        fn = self._fn("Stg_SetAperturePosition", [ct.c_int32, ct.c_double])
        _check_negative(fn(kind, size), f"Stg_SetAperturePosition({kind}, {size:g})")

    def zoom_present(self) -> bool:
        return self._fn("Stg_IsZoomPresent", [])() == 1

    def zoom_manual(self) -> bool:
        return self._fn("Stg_IsZoomManual", [])() == 1

    def zoom(self) -> float:
        return float(self._fn("Stg_GetZoomPosition", [], ct.c_double)())

    def set_zoom(self, zoom: float) -> None:
        """NIS takes the closest zoom the hardware has."""
        _check_negative(self._fn("Stg_SetZoomPosition", [ct.c_double])(zoom), "Stg_SetZoomPosition")

    def analyzer_present(self) -> bool:
        return self._fn("Stg_IsAnalyzerPresent", [])() == 1

    def analyzer_in(self) -> bool:
        return self._fn("Stg_GetAnalyzerState", [])() == 1

    def set_analyzer_in(self, inserted: bool) -> None:
        fn = self._fn("Stg_SetAnalyzerState", [ct.c_int32])
        _check_negative(fn(1 if inserted else 0), "Stg_SetAnalyzerState")

    # heating and cooling stages (read only)
    def heat_stage_names(self) -> list[str]:
        count = max(int(self._fn("Stg_HeatStage_GetCount", [])()), 0)
        return [self._name("Stg_HeatStage_GetName", i) for i in range(count)]

    def heat_stage_temperature(self, name: str) -> float:
        fn = self._fn("Stg_HeatStage_GetCurrentTemperature", [ct.c_wchar_p], ct.c_double)
        return float(fn(name))

    def heat_stage_status(self, name: str) -> int:
        return int(self._fn("Stg_HeatStage_GetStatus", [ct.c_wchar_p])(name))

    # the light path port (camera, eyepieces ...), the spinning disk, the piezo Z drive
    def port_present(self) -> bool:
        return self._fn("Stg_IsLightPathPresent", [])() == 1

    def port(self) -> int:
        return _check_negative(
            self._fn("Stg_GetLightPathPosition", [])(), "Stg_GetLightPathPosition"
        )

    def port_count(self) -> int:
        count = self._fn("Stg_GetLightPathPositions", [])()
        return _check_negative(count, "Stg_GetLightPathPositions")

    def set_port(self, port: int) -> None:
        fn = self._fn("Stg_SetLightPathPosition", [ct.c_int32])
        _check_negative(fn(port), f"Stg_SetLightPathPosition({port})")

    def disk_shutter_open(self) -> bool:
        return self._fn("Stg_GetCSUShutterState", [])() == 1

    def set_disk_shutter_open(self, open_: bool) -> None:
        fn = self._fn("Stg_SetCSUShutterState", [ct.c_int32])
        _check_negative(fn(1 if open_ else 0), "Stg_SetCSUShutterState")

    def disk_speed_rpm(self) -> int:
        return int(self._fn("Stg_GetDiskSpeed", [])())

    def set_disk_speed_rpm(self, rpm: int) -> None:
        _check_negative(self._fn("Stg_SetDiskSpeed", [ct.c_int32])(rpm), "Stg_SetDiskSpeed")

    def piezo_present(self) -> bool:
        return self._fn("StgZ_GetPiezoDevice", [])() >= 0

    def move_piezo_z(self, distance_um: float) -> None:
        """Move the piezo Z drive by ``distance_um`` (relative). NIS cannot read its position."""
        fn = self._fn("StgMovePiezoZ", [ct.c_double, ct.c_int32])
        _check_negative(fn(distance_um, 1), f"StgMovePiezoZ({distance_um:g})")

    def center_piezo_z(self) -> None:
        """Center the piezo and keep the focus (Devices > Keep Z position and center Piezo Z)."""
        _check_negative(self._fn("StgMovePiezoZToHomeKeepZ", [])(), "StgMovePiezoZToHomeKeepZ")

    def filter_changer_names(self) -> list[str]:
        count = _check_negative(self._fn("Stg_Filter_GetCount", [])(), "Stg_Filter_GetCount")
        return [self._name("Stg_Filter_GetName", i) for i in range(count)]

    def filter_position(self, changer: str) -> int:
        position = self._fn("Stg_Filter_GetPosition", [ct.c_wchar_p])(changer)
        return _check_negative(position, f"Stg_Filter_GetPosition({changer})")

    def filter_position_count(self, changer: str) -> int:
        count = self._fn("Stg_Filter_GetPositionCount", [ct.c_wchar_p])(changer)
        return _check_negative(count, f"Stg_Filter_GetPositionCount({changer})")

    def filter_name(self, changer: str, position: int) -> str:
        buf = ct.create_unicode_buffer(256)
        fn = self._fn(
            "Stg_Filter_GetPositionName", [ct.c_wchar_p, ct.c_int32, ct.c_wchar_p, ct.c_int32]
        )
        fn(changer, position, buf, 255)
        return buf.value

    def set_filter_position(self, changer: str, position: int) -> None:
        fn = self._fn("Stg_Filter_SetPosition", [ct.c_wchar_p, ct.c_int32])
        _check_negative(fn(changer, position), f"Stg_Filter_SetPosition({changer}, {position})")

    def exposure_ms(self) -> float:
        """The camera exposure. Not exported by the DLL, and ``Camera_ExposureGet`` hands
        the value back, so through a macro (directly it opens a blocking dialog). It
        returns 0 even when it works, so only the value is used."""
        return self._macro.call("Camera_ExposureGet", "{ms}", doubles=("ms",))[1]["ms"]

    def camera(self) -> dict[str, Any]:
        """The current camera: name, driver, sensor size and pixel, format and ROI.

        None of these is exported by the DLL; each goes through a macro.
        """
        call = self._macro.call
        name = call("GetCurrentCameraName", "{name}", texts=("name",))[1]["name"]
        driver = call("GetCurrentCameraDriverName", "{name}", texts=("name",))[1]["name"]
        size = call(
            "GetCameraResolution",
            f"{CAMERA_MODE}, {{w}}, {{h}}, {{px}}",
            ints=("w", "h"),
            doubles=("px",),
        )[1]
        fmt = call("CameraFormatGet", f"{CAMERA_MODE}, {{fmt}}", texts=("fmt",))[1]["fmt"]
        roi = call(
            "ROIGet", "{left}, {top}, {right}, {bottom}", ints=("left", "top", "right", "bottom")
        )[1]
        return {
            "name": name,
            "driver": driver,
            "width_px": size["w"],
            "height_px": size["h"],
            "pixel_um": size["px"],
            "format": fmt,
            "roi": roi,
        }

    def camera_averaging(self) -> int:
        """Frames averaged per image (1: none). Through a macro: it hands the value back."""
        return self._macro.call("Camera_AverageGet", "{n}", ints=("n",))[1]["n"]

    def camera_integration(self) -> int:
        """Frames summed per image (1: none)."""
        return self._macro.call("Camera_IntegrateGet", "{n}", ints=("n",))[1]["n"]

    def set_camera_format(self, camera_format: str) -> None:
        """Set the format (binning, bit depth), e.g. "FMT 2x2 16", for live and for capture.

        NIS keeps the old one when the camera has no such format; the caller reads back.
        """
        for mode in CAMERA_MODES:
            self._macro.call("CameraFormatSet", f'{mode}, "{camera_format}"')

    def set_roi(self, left: int, top: int, right: int, bottom: int) -> None:
        self._macro.call("ROISet", f"{left}, {top}, {right}, {bottom}")

    def set_camera_averaging(self, frames: int) -> None:
        self._macro.call("Camera_AverageSet", f"{frames}")

    def set_camera_integration(self, frames: int) -> None:
        self._macro.call("Camera_IntegrateSet", f"{frames}")

    def incubator(self, key: str) -> dict[str, float]:
        """Gas (%) and pressure (mbar), now and as set, of the incubator ``key`` ('' = the one).

        NIS has no function that lists incubators; with none, the values are 0.
        """
        values = {}
        for what, function in (
            ("gas_percent", "Stg_Incubator_GetCurrentGas"),
            ("target_gas_percent", "Stg_Incubator_GetTargetGas"),
            ("pressure_mbar", "Stg_Incubator_GetCurrentPressure"),
            ("target_pressure_mbar", "Stg_Incubator_GetTargetPressure"),
        ):
            values[what] = self._macro.call(function, f'"{key}", {{v}}', doubles=("v",))[1]["v"]
        return values

    # nosepiece
    def nosepiece_present(self) -> bool:
        return bool(self._fn("Stg_IsNosepiecePresent", [])())

    def nosepiece_count(self) -> int:
        count = self._fn("Stg_GetNosepiecePositions", [])()
        return _check_negative(count, "Stg_GetNosepiecePositions")

    def nosepiece_position(self) -> int:
        position = self._fn("Stg_GetNosepiecePosition", [])()
        return _check_negative(position, "Stg_GetNosepiecePosition")

    def objective_name(self, position: int) -> str:
        buf = ct.create_unicode_buffer(256)
        fn = self._fn("Stg_GetNosepieceObjectiveName", [ct.c_int32, ct.c_wchar_p, ct.c_int32])
        _check(fn(position, buf, 256), f"Stg_GetNosepieceObjectiveName({position})")
        return buf.value

    def set_nosepiece_position(self, position: int) -> None:
        fn = self._fn("Stg_SetNosepiecePosition", [ct.c_int32])
        _check(fn(position), f"Stg_SetNosepiecePosition({position})")

    # focus
    def pfs_present(self) -> bool:
        return bool(self._fn("Stg_IsPFSPresent", [])())

    def pfs_status(self) -> int:
        return int(self._fn("Stg_GetPFSStatus", [])())

    def set_pfs(self, on: bool) -> None:
        _check_negative(
            self._fn("Stg_SetPFSStatus", [ct.c_int32])(1 if on else 0), "Stg_SetPFSStatus"
        )

    def pfs_offset(self) -> int:
        return int(self._fn("Stg_GetPFSLensOffsetPosition", [])())

    def set_pfs_offset(self, offset: int) -> None:
        fn = self._fn("Stg_SetPFSLensOffsetPosition", [ct.c_int32])
        _check_negative(fn(offset), f"Stg_SetPFSLensOffsetPosition({offset})")

    def pfs_dish_changeable(self) -> bool:
        return self._fn("Stg_PFSGetDishTypeChangeable", [])() == 1

    def pfs_dish(self) -> int:
        return int(self._fn("Stg_PFSGetDishType", [])())

    def set_pfs_dish(self, dish: int) -> None:
        _check_negative(self._fn("Stg_PFSSetDishType", [ct.c_int32])(dish), "Stg_PFSSetDishType")

    def wait_for_pfs(self, timeout_s: float) -> None:
        self._fn("Stg_WaitForPFS", [ct.c_double])(timeout_s)

    def autofocus(self, range_um: float, speed: int) -> int:
        """Image-based focus sweep over ``range_um`` around the current Z; 1 = found."""
        return int(self._fn("StgFocusInRangeEx", [ct.c_double, ct.c_double])(range_um, speed))

    # images
    def capture(self) -> None:
        # Checked, so that a failed capture never lets the save and close that follow
        # act on another image open in NIS, such as the operator's own.
        _check_negative(self._fn("Capture", [])(), "Capture")

    def pixel_size_um(self) -> float:
        """Calibration of the current image in um/px; 0 when uncalibrated."""
        name = ct.create_unicode_buffer(256)
        cal, aspect, unit = ct.c_double(), ct.c_double(), ct.c_int32()
        fn = self._fn(
            "Get_Calibration",
            [
                ct.c_wchar_p,
                ct.POINTER(ct.c_double),
                ct.POINTER(ct.c_double),
                ct.POINTER(ct.c_int32),
            ],
            ct.c_double,
        )
        fn(name, ct.byref(cal), ct.byref(aspect), ct.byref(unit))
        return cal.value

    def save_tiff(self, path: str) -> None:
        self._fn("ImageSaveAs", [ct.c_wchar_p, ct.c_int32, ct.c_int32])(path, TIFF_ALL_LAYERS, 0)

    def close_document(self) -> None:
        self._fn("CloseCurrentDocument", [ct.c_int32])(CLOSE_WITHOUT_ASKING)
