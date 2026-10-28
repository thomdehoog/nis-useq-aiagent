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
from .settings import OPTCONF_FOLDER, PFS_ON_STATUSES


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

    def get_objectives(self, args: dict) -> dict:
        if not self.api.nosepiece_present():
            return {"current": None, "objectives": {}}
        names = {p: self.api.objective_name(p) for p in range(1, self.api.nosepiece_count() + 1)}
        return {
            "current": self.api.nosepiece_position(),
            "objectives": {p: name for p, name in names.items() if name},
        }

    def get_pfs(self, args: dict) -> dict:
        if not self.api.pfs_present():
            return {"present": False, "on": False, "status": None, "meaning": "no PFS"}
        status = self.api.pfs_status()
        return {
            "present": True,
            "on": status in PFS_ON_STATUSES,
            "status": status,
            "meaning": PFS_STATUS.get(status, "unknown"),
        }


READS = (
    "get_version",
    "get_position",
    "get_limits",
    "get_optical_configurations",
    "get_optical_configuration",
    "get_objectives",
    "get_pfs",
)
