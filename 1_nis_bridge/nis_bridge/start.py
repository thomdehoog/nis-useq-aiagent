"""Start NIS-Elements with the bridge running, from one command.

    python -m nis_bridge.start

NIS-Elements can run a macro command as it starts (its ``-c`` switch), so the
bridge macro can be started together with the program: no clicking through
Macro > Run Macro From File. This module checks whether the bridge already
answers, writes the macro if it is missing, starts NIS-Elements with it when
NIS is not running yet, and waits until the bridge answers.

When NIS-Elements is already open but the bridge is not running, nothing can
be started from outside: NIS runs one instance, and a second one only brings
the first to the front. The operator then runs the macro by hand; the message
says which file.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path

from .install_macros import PACKAGE_DIR, install
from .protocol import DEFAULT_HOST, DEFAULT_PORT

NIS_EXECUTABLE = Path(r"C:\Program Files\NIS-Elements\nis_ar.exe")
NIS_EXECUTABLE_VARIABLE = "NIS_ELEMENTS"  # points to nis_ar.exe when it is somewhere else
START_TIMEOUT_S = 240  # NIS-Elements with a real microscope takes a while to come up
POLL_S = 2.0
MACRO = PACKAGE_DIR / "start_bridge.mac"


def bridge_answers(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> bool:
    """True when something listens on the bridge's port."""
    try:
        with socket.create_connection((host, port), timeout=1.0):
            return True
    except OSError:
        return False


def nis_executable() -> Path:
    """Where nis_ar.exe is: the NIS_ELEMENTS environment variable, else the usual place."""
    return Path(os.environ.get(NIS_EXECUTABLE_VARIABLE) or NIS_EXECUTABLE)


def nis_is_running() -> bool:
    """True when an nis_ar.exe process exists (Windows only; False elsewhere)."""
    if sys.platform != "win32":
        return False
    out = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq nis_ar.exe", "/NH"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    return "nis_ar.exe" in out.lower()


def start_command(macro: Path, executable: Path | None = None) -> list[str]:
    """The command that starts NIS-Elements and runs the bridge macro as it opens."""
    exe = executable or nis_executable()
    return [str(exe), "-c", f'RunMacro("{macro}")']


def start_nis(macro: Path, executable: Path | None = None) -> subprocess.Popen:
    """Start NIS-Elements with the macro; raise with advice when the program is not found."""
    command = start_command(macro, executable)
    exe = Path(command[0])
    if not exe.exists():
        raise FileNotFoundError(
            f"NIS-Elements was not found at {exe}. Set {NIS_EXECUTABLE_VARIABLE} to the "
            "full path of nis_ar.exe."
        )
    return subprocess.Popen(command)


def ensure_bridge(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    timeout_s: float = START_TIMEOUT_S,
    say: Callable[[str], None] = print,
    executable: Path | None = None,
) -> bool:
    """Make the bridge answer: start NIS-Elements with the macro when needed, and wait.

    Returns True when the bridge answers. Returns False, after saying what to
    do, when NIS-Elements is already open without the bridge (run the macro by
    hand) or when it did not come up within ``timeout_s``.
    """
    if bridge_answers(host, port):
        say("The bridge in NIS-Elements answers.")
        return True
    macro = MACRO if MACRO.exists() else install(port=port)
    if nis_is_running():
        say(
            "NIS-Elements is open but the bridge is not running. In NIS-Elements choose "
            f"Macro > Run Macro From File... and pick {macro}"
        )
        return False
    say(f"Starting NIS-Elements with {macro.name} ...")
    start_nis(macro, executable)
    return wait_for_bridge(host, port, timeout_s, say)


def wait_for_bridge(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    timeout_s: float = START_TIMEOUT_S,
    say: Callable[[str], None] = print,
) -> bool:
    """Wait until the bridge answers, at most ``timeout_s`` seconds."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if bridge_answers(host, port):
            say("The bridge in NIS-Elements answers.")
            return True
        time.sleep(POLL_S)
    say(
        f"The bridge did not answer within {timeout_s:.0f} s. If NIS-Elements is open, choose "
        f"Macro > Run Macro From File... and pick {MACRO}"
    )
    return False


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Start NIS-Elements with the bridge running.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="the bridge's port")
    parser.add_argument(
        "--timeout", type=float, default=START_TIMEOUT_S, help="seconds to wait for the bridge"
    )
    args = parser.parse_args(argv)
    return 0 if ensure_bridge(port=args.port, timeout_s=args.timeout) else 1


if __name__ == "__main__":
    raise SystemExit(main())
