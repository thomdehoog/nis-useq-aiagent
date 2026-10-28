"""The questions a client may ask: readers observe NIS-Elements and change nothing.

Each public method of ``Readers`` is one read-only request. They are safe to
call at any time, and the commands use them to read back what they did.

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
import tempfile
import time
from typing import Any

from . import optconf
from .nis_dll import PFS_STATUS
from .settings import (
    APERTURES,
    HEAT_STAGE_STATUS,
    OPTCONF_FOLDER,
    PFS_DISHES,
    PFS_ON_STATUSES,
)


def _or_none(read: Any, *args: Any) -> Any:
    """A reading, or None when NIS says it cannot give it (not supported, not present)."""
    try:
        return read(*args)
    except RuntimeError:
        return None


class Readers:
    def __init__(self, api: Any) -> None:
        self.api = api

    def get_version(self, args: dict) -> str:
        """The NIS-Elements version, as NIS reports it."""
        return self.api.version()

    def get_position(self, args: dict) -> dict:
        return self.api.get_position()

    def get_limits(self, args: dict) -> dict:
        return self.api.get_limits()

    def get_optical_configurations(self, args: dict) -> list:
        return self.api.optical_configurations()

    def get_optical_configuration(self, args: dict) -> dict:
        """What one optical configuration holds: camera, format, exposure, light path ..."""
        name = self.configuration_name(args, "name")
        return optconf.settings(optconf.find(optconf.read(self.backup()), name))

    # -- helpers for the optical configuration requests, not requests themselves --

    def configuration_name(self, args: dict, key: str) -> str:
        """The configuration named in ``args[key]``, as NIS lists it; ValueError if none."""
        name = args.get(key)
        listed = self.api.optical_configurations()
        found = [n for n in listed if n == name] or [
            n for n in listed if isinstance(name, str) and optconf.matches(n, name)
        ]
        if len(found) != 1:
            raise ValueError(
                f"unknown optical configuration {name!r}; NIS has: {', '.join(listed)}"
            )
        return found[0]

    def optconf_folder(self) -> str:
        """Where the backups and the files to import are written."""
        folder = os.path.join(tempfile.gettempdir(), OPTCONF_FOLDER)
        os.makedirs(folder, exist_ok=True)
        return folder

    def backup(self, keep: bool = False) -> str:
        """Write all optical configurations to an XML file and return its path.

        ``keep``: a file of its own with the time in its name, so a change can be
        undone by hand; otherwise one file that each read overwrites.
        """
        folder = self.optconf_folder()
        stamp = f"{time.strftime('%Y%m%d-%H%M%S')}-{time.time_ns() // 1_000_000 % 1000:03d}"
        name = f"backup-{stamp}.xml" if keep else "read.xml"
        path = os.path.join(folder, name)
        if os.path.exists(path):
            os.remove(path)
        self.api.backup_optical_configurations(path)
        if not os.path.exists(path):
            raise RuntimeError(f"BackupOptConf returned but wrote no file at {path}")
        return path

    def get_lights(self, args: dict) -> list:
        """Each lamp or LED NIS has: on or off, and its voltage and iris where NIS controls them.

        A value NIS cannot read or control is None.
        """
        api = self.api
        return [
            {
                "name": name,
                "on": _or_none(api.light_on, name),
                "voltage": api.light_voltage(name)
                if api.light_voltage_controllable(name)
                else None,
                "iris": api.light_iris(name) if api.light_iris_controllable(name) else None,
            }
            for name in api.light_names()
        ]

    def get_lasers(self, args: dict) -> list:
        """Each multi-laser light source and its lines: wavelength, on, power.

        Lines are numbered from 1 here, as NIS shows them; NIS's own index is one less.
        """
        return [
            {
                "name": laser,
                "lines": [
                    {
                        "line": index + 1,
                        "name": self.api.laser_line_name(laser, index),
                        "wavelength_nm": self.api.laser_wavelength_nm(laser, index),
                        "on": self.api.laser_line_on(laser, index),
                        "power": self.api.laser_power(laser, index),
                        "power_steps": self.api.laser_power_steps(laser, index),
                    }
                    for index in range(self.api.laser_line_count(laser))
                ],
            }
            for laser in self.api.laser_names()
        ]

    def get_filters(self, args: dict) -> list:
        """Each filter changer (turret, wheel): its position and the filter in each position."""
        changers = []
        for name in self.api.filter_changer_names():
            count = self.api.filter_position_count(name)
            changers.append(
                {
                    "name": name,
                    "position": self.api.filter_position(name),
                    "filters": {p: self.api.filter_name(name, p) for p in range(1, count + 1)},
                }
            )
        return changers

    def get_shutters(self, args: dict) -> list:
        """Each shutter NIS has, by name, and whether it is open."""
        return [{"name": n, "open": self.api.shutter_open(n)} for n in self.api.shutter_names()]

    def get_light_path(self, args: dict) -> dict:
        """The transmitted light path: condenser, apertures, zoom, analyzer.

        A part NIS does not have is None; an aperture is listed only when NIS has
        steps for it. ``zoom_manual``: the zoom is turned by hand, NIS cannot set it.
        """
        api = self.api
        condenser = (
            {"position": api.condenser_position(), "positions": api.condenser_count()}
            if api.condenser_present()
            else None
        )
        apertures = {
            name: {"size": api.aperture(kind), "steps": api.aperture_steps(kind)}
            for name, kind in APERTURES.items()
            if api.aperture_steps(kind) > 0
        }
        zoom = {"zoom": api.zoom(), "manual": api.zoom_manual()} if api.zoom_present() else None
        analyzer = {"inserted": api.analyzer_in()} if api.analyzer_present() else None
        return {"condenser": condenser, "apertures": apertures, "zoom": zoom, "analyzer": analyzer}

    def get_environment(self, args: dict) -> dict:
        """Heating and cooling stages: temperature and what they are doing. Reads only."""
        return {
            "heat_stages": [
                {
                    "name": name,
                    "temperature": self.api.heat_stage_temperature(name),
                    "status": HEAT_STAGE_STATUS.get(self.api.heat_stage_status(name), "unknown"),
                }
                for name in self.api.heat_stage_names()
            ]
        }

    def get_objectives(self, args: dict) -> dict:
        if not self.api.nosepiece_present():
            return {"current": None, "objectives": {}}
        names = {p: self.api.objective_name(p) for p in range(1, self.api.nosepiece_count() + 1)}
        return {
            "current": self.api.nosepiece_position(),
            "objectives": {p: name for p, name in names.items() if name},
        }

    def get_camera(self, args: dict) -> dict:
        """The current camera and its exposure (through macros on 6.10: about 0.1 s)."""
        return {**self.api.camera(), "exposure_ms": self.api.exposure_ms()}

    def get_pfs(self, args: dict) -> dict:
        if not self.api.pfs_present():
            return {"present": False, "on": False, "status": None, "meaning": "no PFS"}
        status = self.api.pfs_status()
        dishes = {number: name for name, number in PFS_DISHES.items()}
        return {
            "present": True,
            "on": status in PFS_ON_STATUSES,
            "status": status,
            "meaning": PFS_STATUS.get(status, "unknown"),
            "offset": self.api.pfs_offset(),
            "dish": dishes.get(self.api.pfs_dish()) if self.api.pfs_dish_changeable() else None,
        }


READS = (
    "get_version",
    "get_position",
    "get_limits",
    "get_optical_configurations",
    "get_optical_configuration",
    "get_objectives",
    "get_lights",
    "get_lasers",
    "get_filters",
    "get_shutters",
    "get_light_path",
    "get_environment",
    "get_pfs",
    "get_camera",
)
