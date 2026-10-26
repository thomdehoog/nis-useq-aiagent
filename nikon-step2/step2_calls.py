"""Step 2 of the Nikon driver: call every macro function of NIS-Elements AR, and note what happens.

Runs INSIDE NIS-Elements, started by step2.mac (Macro > Run Macro From File). The macro
loops; each pass calls the next functions for about 50 ms, so NIS stays responsive and the
macro Stop button works. Every function in ar_functions.txt (3667) is called once through
nis.mac, with no arguments, on NIS's own thread:

  ran              it needed no arguments, and it ran; its return value is kept
  needs the camera not run: capture, live, grab or autofocus, with the camera off
  needs arguments  NIS answered "Bad number of parameters": reachable, not run
  error            NIS or nis.mac answered with another error
  not reachable    nis.mac does not offer it (camera, other hardware, modules)
  crashed or hung  NIS crashed or hung on it; the next run carries on after it

Nothing is skipped. The functions that would end the run itself (quit NIS, stop or run a
macro) come last. Before each call the function is written to results\\step2_calls.jsonl,
so after a crash or hang, running step2.mac again carries on after that function.

A separate program, step2_watch.py with NIS's own python.exe, shows the progress in a
window, notes every dialog a call opens and closes it, and says FINISHED at the end.

Standard library and NIS's own `nis` module only. Microscope off.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-26
License: MIT
"""

import json
import os
import re
import subprocess
import sys
import time

VERSION = "2026-10-26 step 2"

# -- settings ------------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "results")
STOP_FILE = os.environ.get("STEP2_STOP_FILE", r"C:\Users\Public\nikon-step2.stop")
CALLS = os.path.join(OUT_DIR, "step2_calls.jsonl")  # one line before and one after each call
CURRENT = os.path.join(OUT_DIR, "step2_current.json")  # what runs now, for the watch window
SLICE_S = 0.05  # how long one pass of the macro loop keeps calling
VALUE_CHARS = 300  # how much of a return value is kept
START_WATCH = os.environ.get("STEP2_WATCH", "1") == "1"  # open the watch window (step2_watch.py)

# Last, because they end the run: quitting NIS, stopping or starting macros.
LAST = re.compile(r"(^|_)(Exit|Quit|Restart|Reboot|Shut_?down|Log_?off|Log_?out)|Macro|^Python_",
                  re.IGNORECASE)

# With the camera off these wait for it (_CaptureEDF: 153 s): not run then, marked so.
NEEDS_CAMERA = re.compile(r"Captur|Grab|Live|Acqui|AutoFocus|HDR|Freeze_", re.IGNORECASE)

try:
    import nis  # exists only inside NIS-Elements
except ImportError:
    nis = None

os.makedirs(OUT_DIR, exist_ok=True)


def read_functions():
    names = []
    with open(os.path.join(HERE, "ar_functions.txt"), encoding="utf-8") as handle:
        for line in handle:
            if line.strip() and not line.startswith("#"):
                name, section = (line.rstrip("\n").split("\t") + [""])[:2]
                names.append((name, section))
    first = [n for n in names if not LAST.search(n[0])]
    return first + [n for n in names if LAST.search(n[0])]


def read_done():
    """Functions with an answer, and the one that was running when NIS went down (if any)."""
    done, started = {}, None
    if os.path.exists(CALLS):
        with open(CALLS, encoding="utf-8") as handle:
            for line in handle:
                try:
                    record = json.loads(line)
                except ValueError:
                    continue  # a line cut short by a crash
                if record.get("phase") == "start":
                    started = record["fn"]
                elif record.get("phase") == "end":
                    done[record["fn"]] = record
                    if record["fn"] == started:
                        started = None
    return done, started


def write(record):
    with open(CALLS, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, default=repr) + "\n")
        handle.flush()
        os.fsync(handle.fileno())  # on disk before the call, even if NIS crashes in it


def show(**fields):
    fields["t"] = time.time()
    tmp = CURRENT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(fields, handle, default=repr)
    os.replace(tmp, CURRENT)


def short(value):
    text = repr(value)
    return text if len(text) <= VALUE_CHARS else text[:VALUE_CHARS] + " ..."


def describe(function):
    """What nis.mac tells about a function without calling it (its prototype, if it has one)."""
    info = {}
    for attr in ("__doc__", "__text_signature__"):
        try:
            value = getattr(function, attr, None)
        except Exception:  # noqa: BLE001
            value = None
        if value:
            info[attr.strip("_")] = str(value)[:VALUE_CHARS]
    return info


def call(name, section):
    record = {"fn": name, "section": section, "phase": "end"}
    try:
        function = getattr(nis.mac, name)
    except Exception as error:  # noqa: BLE001
        record.update(result="not reachable", detail=f"{type(error).__name__}: {error}")
        return record
    record.update(describe(function))
    if not state.get("camera") and NEEDS_CAMERA.search(name):
        record.update(result="needs the camera", detail="not run: the camera is off")
        return record
    write({"fn": name, "phase": "start", "t": time.time()})
    started = time.perf_counter()
    try:
        value = function()
        record.update(result="ran", detail=short(value))
    except Exception as error:  # noqa: BLE001 - every answer is a finding
        text = f"{type(error).__name__}: {error}"
        needs = "number of parameters" in str(error).lower()
        record.update(result="needs arguments" if needs else "error", detail=text[:VALUE_CHARS])
    record["ms"] = round(1000 * (time.perf_counter() - started), 2)
    return record


# -- what the macro calls ------------------------------------------------------------------
state = {}


def start():
    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)
    functions = read_functions()
    done, crashed = read_done()
    if crashed:  # NIS went down in this call last time: note it, never call it again
        record = {"fn": crashed, "section": dict(functions).get(crashed, ""), "phase": "end",
                  "result": "crashed or hung", "detail": "NIS crashed or hung in this call; "
                  "the run was started again after it"}
        write(record)
        done[crashed] = record
    todo = [f for f in functions if f[0] not in done]
    counts = {}
    for record in done.values():
        counts[record["result"]] = counts.get(record["result"], 0) + 1
    state["camera"] = nis is not None and hasattr(nis.mac, "GetCurrentCameraName")
    state.update(todo=todo, index=0, total=len(functions), counts=counts, started=time.time(),
                 resumed=len(done))
    write({"fn": "-", "phase": "run", "version": VERSION, "file": __file__, "python": sys.version,
           "pid": os.getpid(), "time": time.strftime("%Y-%m-%d %H:%M:%S"),
           "camera": state["camera"], "already_done": len(done), "to_do": len(todo), "crashed_last_time": crashed})
    show(i=len(done), n=len(functions), fn="", counts=counts, done=not todo)
    if START_WATCH:
        start_watch()
    if nis is not None:
        nis.log(f"step 2: {len(todo)} of {len(functions)} functions to call")
    if not todo:
        finish()


def pump():
    """Call the next functions for SLICE_S seconds (each pass of the macro loop). Never raises."""
    try:
        if not state.get("todo"):
            finish()
            return
        until = time.perf_counter() + SLICE_S
        while state["index"] < len(state["todo"]) and time.perf_counter() < until:
            name, section = state["todo"][state["index"]]
            done_before = state["resumed"] + state["index"]
            show(i=done_before, n=state["total"], fn=name, counts=state["counts"], done=False)
            record = call(name, section)
            write(record)
            state["counts"][record["result"]] = state["counts"].get(record["result"], 0) + 1
            state["index"] += 1
        if state["index"] >= len(state["todo"]):
            finish()
    except BaseException as error:  # noqa: BLE001 - an error here would reach NIS every pass
        with open(os.path.join(OUT_DIR, "step2_errors.txt"), "a", encoding="utf-8") as handle:
            handle.write(f"{time.strftime('%H:%M:%S')} {type(error).__name__}: {error}\n")
        open(STOP_FILE, "w").close()


def finish():
    if state.get("finished"):
        return
    state["finished"] = True
    show(i=state["total"], n=state["total"], fn="", counts=state["counts"], done=True)
    with open(os.path.join(OUT_DIR, "step2_summary.txt"), "w", encoding="utf-8") as handle:
        handle.write(f"step 2 ({VERSION}), {time.strftime('%Y-%m-%d %H:%M:%S')}: "
                     f"{state['total']} functions called with no arguments\n")
        for result, count in sorted(state["counts"].items(), key=lambda kv: -kv[1]):
            handle.write(f"  {result:<16} {count}\n")
    open(STOP_FILE, "w").close()


def stop():
    """The macro's last line: also after the Stop button, so the window says so."""
    if not state.get("finished"):
        show(i=state.get("resumed", 0) + state.get("index", 0), n=state.get("total", 0), fn="",
             counts=state.get("counts", {}), done=False, stopped=True)
    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)


# -- the watch window ------------------------------------------------------------------------
def python_exe():
    """NIS's own python.exe (C:\\Program Files\\NIS-Elements\\Python\\python.exe on 7.01)."""
    if os.path.basename(sys.executable).lower().startswith("python"):
        return sys.executable
    for folder in (sys.base_prefix, sys.prefix, os.path.dirname(sys.executable)):
        path = os.path.join(folder, "python.exe")
        if os.path.isfile(path):
            return path
    return None


def start_watch():
    python = python_exe()
    if not python:
        return
    command = [python, "-I", os.path.join(HERE, "step2_watch.py"), str(os.getpid()), OUT_DIR]
    try:
        subprocess.Popen(command, cwd=HERE, creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
    except OSError as error:
        with open(os.path.join(OUT_DIR, "step2_errors.txt"), "a", encoding="utf-8") as handle:
            handle.write(f"could not start the watch window: {error}\n")
