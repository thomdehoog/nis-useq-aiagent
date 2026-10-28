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
from typing import Any

from . import optconf
from .readers import Readers
from .settings import (
    AUTOFOCUS_MAX_SPEED,
    AUTOFOCUS_RANGE_UM,
    AUTOFOCUS_SPEED,
    OPTCONF_NEW_ONLY,
    OPTCONF_OVERWRITE,
    PFS_SETTLE_S,
)


def _number(args: dict, key: str) -> float:
    try:
        return float(args[key])
    except KeyError:
        raise ValueError(f"missing argument {key!r}") from None
    except (TypeError, ValueError):
        raise ValueError(f"argument {key!r} must be a number") from None


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
    "set_pfs",
    "autofocus",
    "snap",
)
