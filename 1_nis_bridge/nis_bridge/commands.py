"""The commands a client may ask for: everything that changes NIS-Elements.

Each public method of ``Commands`` is one command, in the same shape:

1. check the arguments, and refuse bad ones with ``ValueError``;
2. call NIS through ``self.api`` (see ``nis_dll.py``), which raises
   ``RuntimeError`` when NIS refuses;
3. read the state back through ``self.read`` (see ``readers.py``) and return
   that, not what was asked for.

To add a command, add a method here and its name to ``COMMANDS``. Nothing
else changes: the client sends the name, and the dispatcher runs it. A request
that only reads belongs in ``readers.py`` instead.

Standard library only: this runs inside NIS-Elements.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import os
import re
from typing import Any

from . import optconf
from .readers import Readers
from .settings import (
    APERTURES,
    AUTOFOCUS_MAX_SPEED,
    AUTOFOCUS_RANGE_UM,
    AUTOFOCUS_SPEED,
    MAX_FRAMES,
    OPTCONF_NEW_ONLY,
    OPTCONF_OVERWRITE,
    PFS_DISHES,
    PFS_SETTLE_S,
    PIEZO_MAX_STEP_UM,
    PROBE_SWITCH,
)


def _number(args: dict, key: str) -> float:
    try:
        return float(args[key])
    except KeyError:
        raise ValueError(f"missing argument {key!r}") from None
    except (TypeError, ValueError):
        raise ValueError(f"argument {key!r} must be a number") from None


def _whole(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


class Commands:
    def __init__(self, api: Any, read: Readers) -> None:
        self.api = api
        self.read = read

    def move(self, args: dict) -> dict:
        """Absolute move of any of x, y, z (um); axes left out stay where they are."""
        target = {
            axis: _number(args, axis) for axis in ("x", "y", "z") if args.get(axis) is not None
        }
        if not target:
            raise ValueError("move needs at least one of 'x', 'y', 'z'")
        if "x" in target or "y" in target:
            here = self.read.get_position({})
            x, y = target.get("x", here["x"]), target.get("y", here["y"])
            if "z" in target:
                self.api.move_xyz(x, y, target["z"])
            else:
                self.api.move_xy(x, y)
        else:
            self.api.move_z(target["z"])
        return self.read.get_position({})

    def select_optical_configuration(self, args: dict) -> dict:
        name = args.get("name")
        if name not in self.api.optical_configurations():
            raise ValueError(f"unknown optical configuration {name!r}")
        self.api.select_optical_configuration(name)
        return {"selected": name}

    def set_exposure(self, args: dict) -> dict:
        exposure_ms = _number(args, "exposure_ms")
        if exposure_ms <= 0:
            raise ValueError("'exposure_ms' must be positive")
        return {"exposure_ms": self.api.set_exposure_ms(exposure_ms)}

    def edit_optical_configuration(self, args: dict) -> dict:
        """Change a saved optical configuration: for now its camera exposure (ms).

        NIS has no call for this (see ``optconf.py``): the configurations are backed
        up, and the changed one is imported over the old one. ``backup`` in the reply
        is the file from before.
        """
        name = self.read.configuration_name(args, "name")
        backup = self.read.backup(keep=True)
        xml = optconf.read(backup)
        changed = self._changed(optconf.find(xml, name), args)
        self._import(xml, changed, OPTCONF_OVERWRITE)
        now = self.read.get_optical_configuration({"name": name})
        if now["exposure_ms"] != optconf.settings(changed)["exposure_ms"]:
            raise RuntimeError(f"RestoreOptConfEx returned but {name!r} did not change")
        return {**now, "backup": backup}

    def copy_optical_configuration(self, args: dict) -> dict:
        """Save a copy of a configuration under ``new_name``, with any changes given."""
        name = self.read.configuration_name(args, "name")
        new_name = args.get("new_name")
        if not isinstance(new_name, str) or not new_name.strip() or ":" in new_name:
            raise ValueError("'new_name' must be a name without ':'")
        new_name = new_name.strip()
        taken = [n for n in self.api.optical_configurations() if optconf.matches(n, new_name)]
        if taken:  # an import of a name NIS has would wait for a click in a dialog
            raise ValueError(f"NIS already has an optical configuration {taken[0]!r}")
        backup = self.read.backup(keep=True)
        xml = optconf.read(backup)
        block = optconf.renamed(optconf.find(xml, name), new_name)
        before = self.api.optical_configurations()
        self._import(xml, self._changed(block, args), OPTCONF_NEW_ONLY)
        added = [n for n in self.api.optical_configurations() if n not in before]
        if len(added) != 1:
            raise RuntimeError(
                f"RestoreOptConfEx added {len(added)} optical configurations: {added}"
            )
        return {**self.read.get_optical_configuration({"name": added[0]}), "backup": backup}

    def delete_optical_configuration(self, args: dict) -> dict:
        """Delete a configuration; ``backup`` in the reply still holds it."""
        name = self.read.configuration_name(args, "name")
        backup = self.read.backup(keep=True)
        self.api.delete_optical_configuration(name)
        if name in self.api.optical_configurations():
            raise RuntimeError(f"DeleteOptConf returned but NIS still lists {name!r}")
        return {"deleted": name, "backup": backup}

    def _changed(self, block: str, args: dict) -> str:
        """The block with the changes asked for in ``args``; at least one when editing."""
        if args.get("exposure_ms") is None:
            if "new_name" in args:
                return block  # a copy may keep every setting
            raise ValueError("nothing to change: give 'exposure_ms'")
        exposure_ms = _number(args, "exposure_ms")
        limit = optconf.settings(block)["max_exposure_ms"]
        if exposure_ms <= 0 or (limit and exposure_ms > limit):
            raise ValueError(f"'exposure_ms' must be above 0 and at most {limit or 'the max'}")
        return optconf.with_exposure(block, exposure_ms)

    def _import(self, xml: str, block: str, options: int) -> None:
        """Import ``block`` into NIS; ``options`` says what a name NIS has gets."""
        path = os.path.join(self.read.optconf_folder(), "import.xml")
        optconf.write(path, optconf.only(xml, block))
        self.api.import_optical_configurations(path, options)

    def set_light(self, args: dict) -> dict:
        """Switch a lamp or LED on or off, and set its voltage or iris; reads it back."""
        lights = {light["name"]: light for light in self.read.get_lights({})}
        name = args.get("name")
        if name not in lights:
            raise ValueError(f"unknown light {name!r}; NIS has: {', '.join(lights) or 'none'}")
        on, voltage, iris = args.get("on"), args.get("voltage"), args.get("iris")
        if on is None and voltage is None and iris is None:
            raise ValueError("nothing to change: give 'on', 'voltage' or 'iris'")
        if on is not None and not isinstance(on, bool):
            raise ValueError("'on' must be true or false")
        if voltage is not None and lights[name]["voltage"] is None:
            raise ValueError(f"NIS does not control the voltage of {name!r}")
        if iris is not None and lights[name]["iris"] is None:
            raise ValueError(f"NIS does not control the iris of {name!r}")
        if voltage is not None:
            self.api.set_light_voltage(name, _number(args, "voltage"))
        if iris is not None:
            self.api.set_light_iris(name, _number(args, "iris"))
        if on is not None:
            self.api.set_light_on(name, on)
        return next(light for light in self.read.get_lights({}) if light["name"] == name)

    def set_laser(self, args: dict) -> dict:
        """Switch a laser line on or off and set its power; reads the line back.

        The line is given by ``line`` (its number, from 1) or ``wavelength_nm``;
        ``laser`` names the light source and may be left out when NIS has one.
        """
        lasers = self.read.get_lasers({})
        name = args.get("laser")
        if name is None and len(lasers) == 1:
            name = lasers[0]["name"]
        found = [laser for laser in lasers if laser["name"] == name]
        if not found:
            known = ", ".join(laser["name"] for laser in lasers) or "none"
            raise ValueError(f"unknown laser {name!r}; NIS has: {known}")
        lines = found[0]["lines"]
        if args.get("line") is not None:
            chosen = [x for x in lines if x["line"] == args["line"]]
        else:
            chosen = [x for x in lines if x["wavelength_nm"] == args.get("wavelength_nm")]
        if len(chosen) != 1:
            offered = ", ".join(f"{x['line']}: {x['wavelength_nm']} nm" for x in lines)
            raise ValueError(f"give 'line' or 'wavelength_nm' of one line; {name} has {offered}")
        line = chosen[0]
        on, power = args.get("on"), args.get("power")
        if on is None and power is None:
            raise ValueError("nothing to change: give 'on' or 'power'")
        if on is not None and not isinstance(on, bool):
            raise ValueError("'on' must be true or false")
        if power is not None:
            top = line["power_steps"] - 1
            if not isinstance(power, int) or isinstance(power, bool) or not 0 <= power <= top:
                raise ValueError(f"'power' must be a whole number from 0 to {top}")
            self.api.set_laser_power(name, line["line"] - 1, power)
        if on is not None:
            self.api.set_laser_line_on(name, line["line"] - 1, on)
        again = next(laser for laser in self.read.get_lasers({}) if laser["name"] == name)
        now = next(x for x in again["lines"] if x["line"] == line["line"])
        reply = {"laser": name, **now}
        if power is not None and now["power"] != power:
            # The Ti2 simulator takes the power and reads 0 back; a real light source may differ.
            reply["note"] = (
                f"NIS reads back power {now['power']}, not the {power} asked; "
                "check the laser panel in NIS-Elements"
            )
        return reply

    def set_shutter(self, args: dict) -> dict:
        """Open or close a shutter, by name."""
        names = self.api.shutter_names()
        name, open_ = args.get("name"), args.get("open")
        if name not in names:
            raise ValueError(f"unknown shutter {name!r}; NIS has: {', '.join(names) or 'none'}")
        if not isinstance(open_, bool):
            raise ValueError("'open' must be true or false")
        self.api.set_shutter_open(name, open_)
        return {"name": name, "open": self.api.shutter_open(name)}

    def set_light_path(self, args: dict) -> dict:
        """Set any of: ``condenser`` (position), ``aperture`` with ``size`` (field,
        epi_field or dia), ``zoom``, ``analyzer`` (inserted or not). Reads the path back.

        Everything is checked before anything moves.
        """
        path = self.read.get_light_path({})
        condenser, zoom, analyzer = args.get("condenser"), args.get("zoom"), args.get("analyzer")
        aperture, size = args.get("aperture"), args.get("size")
        if all(v is None for v in (condenser, aperture, zoom, analyzer)):
            raise ValueError(
                "nothing to change: give 'condenser', 'aperture', 'zoom' or 'analyzer'"
            )
        if condenser is not None:
            if path["condenser"] is None:
                raise ValueError("NIS has no condenser it controls")
            top = path["condenser"]["positions"]
            if (
                not isinstance(condenser, int)
                or isinstance(condenser, bool)
                or not 0 <= condenser <= top
            ):
                raise ValueError(f"'condenser' must be a position from 0 to {top}")
        if aperture is not None:
            if aperture not in path["apertures"]:
                known = ", ".join(path["apertures"]) or "none"
                raise ValueError(f"unknown aperture {aperture!r}; NIS controls: {known}")
            size = _number(args, "size")
        if zoom is not None:
            if path["zoom"] is None or path["zoom"]["manual"]:
                raise ValueError("NIS cannot set the zoom: there is none, or it is turned by hand")
            zoom = _number(args, "zoom")
        if analyzer is not None:
            if path["analyzer"] is None:
                raise ValueError("NIS has no analyzer it controls")
            if not isinstance(analyzer, bool):
                raise ValueError("'analyzer' must be true (in) or false (out)")
        if condenser is not None:
            self.api.set_condenser_position(condenser)
        if aperture is not None:
            self.api.set_aperture(APERTURES[aperture], size)
        if zoom is not None:
            self.api.set_zoom(zoom)
        if analyzer is not None:
            self.api.set_analyzer_in(analyzer)
            if self.api.analyzer_in() is not analyzer:
                raise RuntimeError("Stg_SetAnalyzerState returned but the analyzer did not move")
        return self.read.get_light_path({})

    def set_pfs_offset(self, args: dict) -> dict:
        """Set the PFS offset (the plane PFS keeps, NIS's units) and dish (glass, plastic)."""
        if not self.api.pfs_present():
            raise RuntimeError("no Perfect Focus System (PFS) is connected")
        offset, dish = args.get("offset"), args.get("dish")
        if offset is None and dish is None:
            raise ValueError("nothing to change: give 'offset' or 'dish'")
        if offset is not None and (not isinstance(offset, int) or isinstance(offset, bool)):
            raise ValueError("'offset' must be a whole number")
        if dish is not None:
            if dish not in PFS_DISHES:
                raise ValueError(f"'dish' must be one of {', '.join(PFS_DISHES)}")
            if not self.api.pfs_dish_changeable():
                raise ValueError("this PFS does not let the dish type be changed")
        if offset is not None:
            self.api.set_pfs_offset(offset)
        if dish is not None:
            self.api.set_pfs_dish(PFS_DISHES[dish])
        return self.read.get_pfs({})

    def set_camera(self, args: dict) -> dict:
        """Set any of: ``format`` (NIS's name, e.g. "FMT 2x2 16") or ``binning`` (2 for
        2x2, in the current format), ``roi`` ({left, top, right, bottom} in sensor
        pixels), ``averaging`` and ``integration`` (frames per image, 1 = none).

        Everything is checked first; the camera is read back after.
        """
        camera = self.read.get_camera({})
        fmt, binning, roi = args.get("format"), args.get("binning"), args.get("roi")
        averaging, integration = args.get("averaging"), args.get("integration")
        if all(v is None for v in (fmt, binning, roi, averaging, integration)):
            raise ValueError(
                "nothing to change: give 'format', 'binning', 'roi', 'averaging' or 'integration'"
            )
        if fmt is not None and binning is not None:
            raise ValueError("give 'format' or 'binning', not both")
        if binning is not None:
            if not _whole(binning) or not 1 <= binning <= 8:
                raise ValueError("'binning' must be a whole number from 1 to 8")
            if not re.search(r"\b\d+x\d+\b", camera["format"]):
                raise ValueError(f"the format {camera['format']!r} names no binning to change")
            fmt = re.sub(r"\b\d+x\d+\b", f"{binning}x{binning}", camera["format"], count=1)
        if fmt is not None and (not isinstance(fmt, str) or not fmt or '"' in fmt):
            raise ValueError("'format' must be a format name, such as 'FMT 1x1 16'")
        if roi is not None:
            corners = ("left", "top", "right", "bottom")
            if not isinstance(roi, dict) or not all(_whole(roi.get(c)) for c in corners):
                raise ValueError("'roi' must be {left, top, right, bottom} in whole pixels")
            width, height = camera["width_px"], camera["height_px"]
            if not (
                0 <= roi["left"] < roi["right"] <= width
                and 0 <= roi["top"] < roi["bottom"] <= height
            ):
                raise ValueError(f"the ROI must lie inside the sensor, {width} x {height} pixels")
        for key, value in (("averaging", averaging), ("integration", integration)):
            if value is not None and (not _whole(value) or not 1 <= value <= MAX_FRAMES):
                raise ValueError(f"'{key}' must be a whole number from 1 to {MAX_FRAMES}")
        if fmt is not None:
            self.api.set_camera_format(fmt)
        if roi is not None:
            self.api.set_roi(roi["left"], roi["top"], roi["right"], roi["bottom"])
        if averaging is not None:
            self.api.set_camera_averaging(averaging)
        if integration is not None:
            self.api.set_camera_integration(integration)
        now = self.read.get_camera({})
        if fmt is not None and now["format"] != fmt:
            raise RuntimeError(f"the camera has no format {fmt!r}; it kept {now['format']!r}")
        return now

    def set_port(self, args: dict) -> dict:
        """Send the light to a port (``port``), and set the spinning disk: ``disk_shutter``
        (open or not) and ``disk_speed_rpm``. Reads them back."""
        state = self.read.get_port()
        port, shutter, rpm = args.get("port"), args.get("disk_shutter"), args.get("disk_speed_rpm")
        if port is None and shutter is None and rpm is None:
            raise ValueError("nothing to change: give 'port', 'disk_shutter' or 'disk_speed_rpm'")
        if port is not None:
            if state["port"] is None:
                raise ValueError("NIS has no light path port it controls")
            top = state["port"]["positions"]
            if not _whole(port) or not 0 <= port <= top:
                raise ValueError(f"'port' must be a position from 0 to {top}")
        if shutter is not None and not isinstance(shutter, bool):
            raise ValueError("'disk_shutter' must be true (open) or false (closed)")
        if rpm is not None and (not _whole(rpm) or rpm < 0):
            raise ValueError("'disk_speed_rpm' must be a whole number of RPM, 0 or more")
        if port is not None:
            self.api.set_port(port)
        if rpm is not None:
            self.api.set_disk_speed_rpm(rpm)
        if shutter is not None:
            self.api.set_disk_shutter_open(shutter)
        return self.read.get_port()

    def move_piezo_z(self, args: dict) -> dict:
        """Move the piezo Z drive by ``distance_um`` (at most PIEZO_MAX_STEP_UM), or
        ``center`` it keeping the focus. NIS has no call that reads the piezo position."""
        if not self.api.piezo_present():
            raise RuntimeError("no piezo Z drive is connected")
        if args.get("center") is True:
            self.api.center_piezo_z()
            return {"centered": True}
        distance = _number(args, "distance_um")
        if abs(distance) > PIEZO_MAX_STEP_UM:
            raise ValueError(f"a piezo move is at most {PIEZO_MAX_STEP_UM:g} um")
        self.api.move_piezo_z(distance)
        return {"moved_um": distance}

    def probe_macro(self, args: dict) -> list:
        """Run one NIS function in a macro and hand back what it returned, to find out how
        a device is driven. Off unless the file PROBE_SWITCH is in the package folder: a
        tool for development, never for an assistant. ``arguments`` is the macro's
        argument list with {name} where a value comes back; ``ints``/``doubles``/``texts``
        name those values."""
        switch = os.path.join(os.path.dirname(os.path.abspath(__file__)), PROBE_SWITCH)
        if not os.path.exists(switch):
            raise ValueError(f"probing is off: create {switch} to turn it on")
        function = args.get("function")
        if not isinstance(function, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", function):
            raise ValueError("'function' must be a NIS function name")
        return self.api.macro(
            function,
            str(args.get("arguments", "")),
            args.get("ints", ()),
            args.get("doubles", ()),
            args.get("texts", ()),
        )

    def escape(self, args: dict) -> dict:
        """``on`` true lowers the objective away from the sample (Escape); false brings it
        back to the focus it left (Refocus)."""
        on = args.get("on")
        if not isinstance(on, bool):
            raise ValueError("'on' must be true (escape) or false (back to focus)")
        if on:
            self.api.escape()
        else:
            self.api.refocus()
        return {"escaped": self.api.escaped(), **self.read.get_position({})}

    def live(self, args: dict) -> dict:
        """Start (``on`` true) or freeze (false) NIS's live view. Nothing is saved."""
        on = args.get("on")
        if not isinstance(on, bool):
            raise ValueError("'on' must be true (live) or false (freeze)")
        self.api.live(on)
        return {"live": on}

    def auto_exposure(self, args: dict) -> dict:
        """Let NIS choose the exposure from what the camera sees now; the exposure it chose."""
        self.api.auto_exposure()
        return {"exposure_ms": self.api.exposure_ms()}

    def safe_state(self, args: dict) -> dict:
        """Everything that sends light to the sample off: every laser line, every shutter
        and the spinning disk shutter closed, every lamp off. Says what it switched off.

        Each part is tried even when another fails; the failures are reported.
        """
        done: dict = {"lasers_off": [], "shutters_closed": [], "lights_off": [], "failed": []}

        def attempt(what: str, action) -> bool:
            try:
                action()
                return True
            except RuntimeError as exc:
                done["failed"].append(f"{what}: {exc}")
                return False

        for laser in self.read.get_lasers({}):
            for line in laser["lines"]:
                if line["on"] and attempt(
                    f"{line['wavelength_nm']} nm",
                    lambda name=laser["name"], index=line["line"] - 1: self.api.set_laser_line_on(
                        name, index, False
                    ),
                ):
                    done["lasers_off"].append(line["wavelength_nm"])
        for shutter in self.read.get_shutters({}):
            if shutter["open"] and attempt(
                shutter["name"], lambda n=shutter["name"]: self.api.set_shutter_open(n, False)
            ):
                done["shutters_closed"].append(shutter["name"])
        if self.api.disk_shutter_open() and attempt(
            "disk shutter", lambda: self.api.set_disk_shutter_open(False)
        ):
            done["shutters_closed"].append("spinning disk")
        for light in self.read.get_lights({}):
            if light["on"] and attempt(
                light["name"], lambda n=light["name"]: self.api.set_light_on(n, False)
            ):
                done["lights_off"].append(light["name"])
        return done

    def set_filter(self, args: dict) -> dict:
        """Turn a filter changer to ``position`` (from 1) or to the filter named ``filter``."""
        changers = {c["name"]: c for c in self.read.get_filters({})}
        name = args.get("changer")
        if name not in changers:
            raise ValueError(
                f"unknown filter changer {name!r}; NIS has: {', '.join(changers) or 'none'}"
            )
        filters = changers[name]["filters"]
        position = args.get("position")
        if position is None:
            named = [p for p, f in filters.items() if f and f == args.get("filter")]
            if len(named) != 1:
                raise ValueError(
                    f"give 'position' or one 'filter' of {name}: "
                    + ", ".join(f"{p}: {f}" for p, f in filters.items())
                )
            position = named[0]
        if position not in filters:
            raise ValueError(f"{name} has positions 1 to {len(filters)}")
        self.api.set_filter_position(name, position - 1)  # NIS counts from 0
        now = next(c for c in self.read.get_filters({}) if c["name"] == name)
        return {
            "changer": name,
            "position": now["position"],
            "filter": filters.get(now["position"]),
        }

    def set_objective(self, args: dict) -> dict:
        position = args.get("position")
        if not isinstance(position, int) or isinstance(position, bool) or position < 1:
            raise ValueError("'position' must be a nosepiece position (1, 2, ...)")
        self.api.set_nosepiece_position(position)
        return {"current": self.api.nosepiece_position()}

    def set_pfs(self, args: dict) -> dict:
        """Switch the Perfect Focus System on (waiting up to ``timeout_s`` to lock) or off."""
        on = args.get("on")
        if not isinstance(on, bool):
            raise ValueError("'on' must be true or false")
        if not self.api.pfs_present():
            raise RuntimeError("no Perfect Focus System (PFS) is connected")
        self.api.set_pfs(on)
        if on:
            self.api.wait_for_pfs(float(args.get("timeout_s", PFS_SETTLE_S)))
        return self.read.get_pfs({})

    def autofocus(self, args: dict) -> dict:
        range_um = float(args.get("range_um", AUTOFOCUS_RANGE_UM))
        speed = int(args.get("speed", AUTOFOCUS_SPEED))
        if range_um <= 0 or not 0 <= speed <= AUTOFOCUS_MAX_SPEED:
            raise ValueError(
                f"'range_um' must be positive and 'speed' between 0 and {AUTOFOCUS_MAX_SPEED}"
            )
        rc = self.api.autofocus(range_um, speed)
        if rc != 1:
            reason = {0: "focus not found", -3: "image is all black or all white"}
            raise RuntimeError(f"StgFocusInRangeEx: {reason.get(rc, 'failed')} ({rc})")
        return self.read.get_position({})

    def snap(self, args: dict) -> dict:
        """Capture one image, save it as TIFF at ``path``, close its window in NIS.

        ``pixel_size_um`` is None when the objective has no calibration in NIS.
        """
        path = args.get("path")
        if not isinstance(path, str) or not path:
            raise ValueError("'path' must be a file path")
        self.api.capture()
        try:
            pixel_size_um = self.api.pixel_size_um()  # read while the image is still open
            self.api.save_tiff(path)
        finally:
            self.api.close_document()  # never leave capture windows piling up in NIS
        if not os.path.exists(path):
            raise RuntimeError(f"ImageSaveAs returned but no file appeared at {path}")
        return {"path": path, "pixel_size_um": pixel_size_um if pixel_size_um > 0 else None}


COMMANDS = (
    "move",
    "select_optical_configuration",
    "edit_optical_configuration",
    "copy_optical_configuration",
    "delete_optical_configuration",
    "set_exposure",
    "set_objective",
    "set_light",
    "set_laser",
    "set_filter",
    "set_shutter",
    "set_light_path",
    "set_pfs_offset",
    "set_camera",
    "set_port",
    "move_piezo_z",
    "escape",
    "live",
    "auto_exposure",
    "safe_state",
    "probe_macro",
    "set_pfs",
    "autofocus",
    "snap",
)
