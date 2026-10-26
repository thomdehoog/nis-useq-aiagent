"""NIS functions the DLL does not export, called through a few lines of NIS macro.

``g5_regprocs.dll`` (``nis_dll.py``) exports about two thirds of NIS's macro
functions; most camera settings are missing. NIS's Python reaches every one of
them by name through ``nis.call_proc``, but on NIS-Elements 6.10 that breaks on
any argument the function writes a value into: a number handed back fails with
a blocking dialog, and a text handed back with a max length corrupts NIS's heap
and kills it a few calls later (branch ``nis-6p1-step0``, RESULTS.md).

So a function that hands values back is called inside a macro: Python writes
the macro to a file and runs it with ``RunMacro``; the macro calls the function
with its own variables and leaves the numbers in global variables (read back
with ``GetVariableValue``) and each text in a file (UTF-16). Python itself never
passes an out-argument to ``nis.call_proc``. About 24 ms per call, against
0.003 ms through the DLL: for what the DLL lacks, not for fast loops.

A function that fails inside a macro (a device that is not there) opens NIS's
blocking *Command Interpreter Error* dialog, so check a device is there first.

Standard library only: this runs inside NIS-Elements.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-26
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import itertools
import os
import tempfile
from typing import Any

NOT_SET = -123456789.0  # a number before the call; still there after it = not written
NOT_SET_INT = -12345
TEXT_LENGTH = 256
_counter = itertools.count(1)


class MacroError(RuntimeError):
    """The macro route did not get an answer back."""


def macro_text(
    name: str,
    arguments: str,
    prefix: str,
    doubles: tuple = (),
    ints: tuple = (),
    texts: dict | None = None,
) -> str:
    """The macro that calls ``name``; ``arguments`` has ``{x}`` where value x comes back.

    ``texts`` maps each text to the file the macro writes it to. NIS wants every
    declaration before the first statement.
    """
    texts = texts or {}
    places = {n: f"&{prefix}{n}" for n in (*doubles, *ints)}
    places.update({n: f"{prefix}{n}" for n in texts})
    declarations = ["global double " + ", ".join(f"{prefix}{n}" for n in ("r", *doubles)) + ";"]
    if ints:
        declarations.append("global int " + ", ".join(f"{prefix}{n}" for n in ints) + ";")
    declarations += [f"char {prefix}{n}[{TEXT_LENGTH}];" for n in texts]
    statements = [f"{prefix}{n} = {NOT_SET:.1f};" for n in doubles]
    statements += [f"{prefix}{n} = {NOT_SET_INT};" for n in ints]
    statements += [f"{prefix}{n}[0] = 0;" for n in texts]
    statements.append(f"{prefix}r = {name}({arguments.format(**places)});")
    statements += [
        f'WriteFile("{path}", {prefix}{n}, 2 * strlen({prefix}{n}));' for n, path in texts.items()
    ]
    return "\n".join(declarations + statements) + "\n"


class NisMacro:
    """Calls NIS functions inside a macro and hands back what they wrote."""

    def __init__(self, folder: str | None = None) -> None:
        self.folder = folder or os.path.join(tempfile.gettempdir(), "nis_bridge_macro")
        os.makedirs(self.folder, exist_ok=True)

    def _path(self, name: str) -> str:
        return os.path.join(self.folder, name).replace("\\", "/")

    def call(
        self, name: str, arguments: str, doubles: tuple = (), ints: tuple = (), texts: tuple = ()
    ) -> tuple[Any, dict]:
        """Call ``name`` in a macro; hand back (return value, {value name: value}).

        ``macro.call("StgGetPosXY", "{x}, {y}", doubles=("x", "y"))``
        """
        import nis  # exists only inside NIS-Elements

        prefix = f"nisbridge_{next(_counter)}_"
        files = {n: self._path(f"{prefix}{n}.txt") for n in texts}
        for path in files.values():
            if os.path.exists(path):
                os.remove(path)
        macro = self._path("call.mac")
        with open(macro, "w", encoding="utf-8") as handle:
            handle.write(macro_text(name, arguments, prefix, doubles, ints, files))
        try:
            ran = _first(nis.call_proc("RunMacro", macro))
            if ran != 1:
                raise MacroError(f"{name}: RunMacro returned {ran!r}")
            answers: dict = {}
            for n in (*doubles, *ints):
                value = _first(nis.call_proc("GetVariableValue", prefix + n))
                if value in (NOT_SET, NOT_SET_INT):
                    raise MacroError(f"{name} did not write {n}")
                answers[n] = int(value) if n in ints else float(value)
            for n, path in files.items():
                answers[n] = ""  # WriteFile writes nothing for an empty text
                if os.path.exists(path):
                    with open(path, "rb") as handle:
                        answers[n] = handle.read().decode("utf-16-le", "replace").split("\0")[0]
                    os.remove(path)
            result = _first(nis.call_proc("GetVariableValue", prefix + "r"))
        finally:
            try:
                nis.call_proc("DeleteVariables", prefix)
            except Exception:  # noqa: BLE001 - a leftover global does no harm; names are unique
                pass
        return (int(result) if float(result).is_integer() else result), answers


def _first(out: Any) -> Any:
    """``nis.call_proc`` answers with a list: the return value first."""
    return out[0] if isinstance(out, (list, tuple)) else out
