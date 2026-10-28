"""Optical configurations as NIS-Elements writes them to a backup file.

NIS 6.10 has no macro function that changes one setting of an optical
configuration (``AddOptConf`` refuses every argument count), but it writes all of
them to an XML file (``BackupOptConf``) and reads such a file back
(``RestoreOptConfEx``). So an edit is: back up, take that configuration's block,
change it, and import a file that holds only the changed block, over the old one.
For a name NIS already has the import overwrites it (options 1) or leaves it
(options 2); options 0 would ask in a dialog, so the bridge never uses it.

The file is UTF-16 XML. Each configuration is one ``<OptN runtype="CLxListVariant">``
element under ``<OpticalConfigs>``. The blocks are cut and joined as text, never
re-serialised, so NIS gets back exactly what it wrote except the values changed.
NIS lists a configuration with its light path in front ("Spinning Disk (2):BF");
``matches`` accepts that name or the part after the last colon.

Standard library only: this runs inside NIS-Elements.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-28
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import re
from html import unescape
from xml.sax.saxutils import escape

ENCODING = "utf-16"  # BackupOptConf writes UTF-16 with a byte order mark
_OPEN = re.compile(r'<Opt(\d+) runtype="CLxListVariant">')
_LIST_END = "</OpticalConfigs>"
_NAME = re.compile(r'(<Name runtype="CLxStringW" value=")([^"]*)("/>)')
_EXPOSURE = re.compile(r'(<Exposure runtype="double" value=")([^"]*)(")')
_TEXTS = {  # what settings() reports: its key, and the first element of that name
    "objective": "ObjectiveName",
    "camera": "CameraUserName",
    "format": "wszFormatText",
    "light_path": "LightPathName",
}
_NUMBERS = {
    "exposure_ms": "Exposure",
    "max_exposure_ms": "CaptureMaxExposure",
    "binning": "dBinningX",
}


def read(path: str) -> str:
    with open(path, "rb") as handle:
        return handle.read().decode(ENCODING)


def write(path: str, xml: str) -> None:
    with open(path, "wb") as handle:
        handle.write(xml.encode(ENCODING))


def blocks(xml: str) -> list[tuple[int, int, str]]:
    """Every configuration in the file: (start, end, name), in file order."""
    found = []
    for match in _OPEN.finditer(xml):
        close = f"</Opt{match.group(1)}>"
        end = xml.index(close, match.start()) + len(close)
        found.append((match.start(), end, name_of(xml[match.start() : end])))
    return found


def name_of(block: str) -> str:
    match = _NAME.search(block)
    return unescape(match.group(2)) if match else ""


def short(name: str) -> str:
    """The name without the light path NIS puts in front of it."""
    return name.rsplit(":", 1)[-1]


def matches(listed: str, name: str) -> bool:
    return listed == name or short(listed) == short(name)


def find(xml: str, name: str) -> str:
    """The block of the configuration called ``name``; KeyError if there is none."""
    found = [b for b in blocks(xml) if b[2] == name] or [
        b for b in blocks(xml) if matches(b[2], name)
    ]
    if len(found) != 1:
        raise KeyError(f"{len(found)} optical configurations match {name!r} in the backup")
    start, end, _ = found[0]
    return xml[start:end]


def settings(block: str) -> dict:
    """What a configuration holds that the bridge can read: name, camera, exposure ..."""
    values: dict = {"name": name_of(block)}
    for key, tag in _TEXTS.items():
        match = re.search(rf'<{tag} runtype="CLxStringW" value="([^"]*)"', block)
        values[key] = unescape(match.group(1)) if match else None
    for key, tag in _NUMBERS.items():
        match = re.search(rf'<{tag} runtype="double" value="([^"]*)"', block)
        values[key] = float(match.group(1)) if match else None
    return values


def renamed(block: str, name: str) -> str:
    """The block with another name (only the configuration's own, the first one)."""
    value = escape(name, {'"': "&quot;"})
    return _NAME.sub(lambda m: m.group(1) + value + m.group(3), block, count=1)


def with_exposure(block: str, exposure_ms: float) -> str:
    """The block with every exposure in it (fast and quality, each camera) set."""
    return _EXPOSURE.sub(lambda m: f"{m.group(1)}{exposure_ms:.15f}{m.group(3)}", block)


def only(xml: str, block: str) -> str:
    """The backup file with ``block`` as its one configuration, for an import."""
    found = blocks(xml)
    if not found:
        raise ValueError("the backup holds no optical configuration")
    first, last = found[0][0], xml.index(_LIST_END, found[-1][1])
    number = _OPEN.match(block).group(1)
    block = block.replace(f"<Opt{number} ", "<Opt0 ", 1)
    block = block[: -len(f"</Opt{number}>")] + "</Opt0>"
    return xml[:first] + block + xml[last:]
