"""Step 1 of the Nikon driver: can software outside NIS call NIS functions, without NIS crashing
or showing an error?

Runs INSIDE NIS-Elements, started by step1.mac (Macro > Run Macro From File). The macro
starts this server, then loops; each pass of the loop hands this Python a moment to run the
requests that came in. So every NIS call runs on NIS's own thread, one at a time, as the
bridge on NIS 6.10 did (camera calls crashed NIS from any other thread).

The test is feasibility only, with the microscope off: readings, no moves, no camera.

  1. Does the macro loop keep this Python and its server alive between passes?
  2. Do requests from another program (step1_client.cmd, PowerShell) arrive and come back?
  3. Do failures come back as a reply: an unknown function, a function that is not there
     without hardware, wrong arguments, a Python error, a broken request? Or does NIS show
     a dialog or crash?
  4. How fast is one round trip, and does NIS stay usable while the loop runs?
  5. Does the server stop cleanly on request, and can it be started again?

The same checks run twice: once from a thread inside NIS's Python (the self-test, at start),
and once from outside NIS (step1_client.cmd). A thread also watches for dialog windows of
NIS and writes their text to the log. Everything goes to results\\ next to this file.

Standard library and NIS's own `nis` module only.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-26
License: MIT
"""

import json
import os
import platform
import queue
import socketserver
import subprocess
import sys
import threading
import time
import traceback

VERSION = "2026-10-26 run-by-itself"  # in the log, so a run shows which files it used

# -- settings: edit before a run ----------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "results")
HOST = "127.0.0.1"  # this computer only
PORT = 54471  # not the bridge's 54470, so the two never meet
STOP_FILE = os.environ.get("STEP1_STOP_FILE", r"C:\Users\Public\nikon-step1.stop")  # loop ends when it exists
MAX_RUN_S = 300  # the loop ends by itself after 5 minutes, whatever happens
PUMP_WAIT_S = 0.05  # how long one pass of the macro loop waits for a request
REQUEST_TIMEOUT_S = 30.0  # a request not started by then is answered "timeout" and never run
MAX_HOLD_S = 5.0  # the longest "hold" (keeps NIS's thread busy, to see if NIS freezes)
SELF_TEST = True  # run the checks from a thread inside NIS's Python at start
WATCH_DIALOGS = True  # note every dialog window NIS opens (only notes; never clicks)
AUTO_CLIENT = True  # after the self-test, start the outside client (step1_client.py) by itself
CLIENT_TIMEOUT_S = 180  # if the client has not finished by then, it is stopped, and so is the run

# Only these NIS functions may be called in step 1: readings, nothing that moves or captures.
READS = {
    "Get_InfoStr", "StgGetPosZ", "StgGetPosXY", "StgXY_GetLimits", "StgZ_GetLimits",
    "GetOptConfCount", "GetOptConfName", "GetSelectedOptConf", "Stg_IsNosepiecePresent",
    "Stg_GetNosepiecePositions", "Stg_IsPFSPresent", "Stg_GetPFSStatus", "Get_Calibration",
}
UNKNOWN = "ThisFunctionDoesNotExist_Step1"  # let through on purpose: how nis.mac says "no such"
PTR_TYPES = {"byte", "char", "char8", "double", "dword", "int", "int64", "long", "short", "word"}

sys.path.insert(0, HERE) if HERE not in sys.path else None
import importlib  # noqa: E402
import step1_checks as checks  # noqa: E402

checks = importlib.reload(checks)  # a second run picks up an edited file

try:
    import nis  # exists only inside NIS-Elements
except ImportError:
    nis = None

os.makedirs(OUT_DIR, exist_ok=True)
_log_lock = threading.Lock()
_log_file = open(os.path.join(OUT_DIR, "step1.log"), "a", encoding="utf-8")

state = {
    "started": time.strftime("%Y-%m-%d %H:%M:%S"), "version": VERSION, "file": __file__,
    "python": sys.version, "platform": platform.platform(), "pid": os.getpid(),
    "nis_module": nis is not None,
    "main_thread": None,  # the thread start() ran on: NIS's own
    "pumps": 0, "pumps_off_main_thread": 0, "longest_gap_s": 0.0,
    "requests": 0, "replies_ok": 0, "replies_error": 0, "timeouts": 0,
    "pump_errors": [], "dialogs": [], "self_test": [], "client": None, "stopped_by": None,
}
_jobs = queue.Queue()
_server = None
_t0 = time.monotonic()
_last_pump = None
_stop_requested = False
_stopped = False
_self_test_thread = None  # also runs the outside client; stop() waits for it a little


def log(text):
    line = f"{time.strftime('%H:%M:%S')} {text}"
    with _log_lock:
        _log_file.write(line + "\n")
        _log_file.flush()


def save():
    with _log_lock:
        with open(os.path.join(OUT_DIR, "step1_report.json"), "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=1, default=repr)


# -- what a request does, on NIS's thread ---------------------------------------------------
def make_arg(arg):
    """A JSON argument as nis.mac takes it: {"ptr": "double"} becomes nis.ptr.double()."""
    if isinstance(arg, dict):
        kind = arg.get("ptr")
        if kind not in PTR_TYPES:
            raise ValueError(f"unknown ptr type {kind!r}; one of {sorted(PTR_TYPES)}")
        return getattr(nis.ptr, kind)()
    return arg


def call(fn, args):
    if fn not in READS and fn != UNKNOWN:
        raise PermissionError(f"{fn} is not on the step 1 list of readings")
    if nis is None:
        raise RuntimeError("the nis module is missing: this is not NIS's Python")
    values = [make_arg(a) for a in args]
    result = getattr(nis.mac, fn)(*values)
    return {"return": result, "values": [v.get() if hasattr(v, "get") else v for v in values]}


def run(request):
    op = request.get("op")
    if op == "ping":
        return {"pid": os.getpid(), "uptime_s": round(time.monotonic() - _t0, 2),
                "pumps": state["pumps"], "on_main_thread": threading.get_ident() == state["main_thread"]}
    if op == "call":
        return call(request.get("fn"), request.get("args", []))
    if op == "raise":
        raise RuntimeError("step 1: a deliberate Python error, to see it come back as a reply")
    if op == "hold":
        seconds = min(float(request.get("seconds", 1)), MAX_HOLD_S)
        time.sleep(seconds)
        return {"held_s": seconds}
    raise ValueError(f"unknown op {op!r}; one of ping, call, raise, hold, shutdown")


class Job:
    def __init__(self, request):
        self.request = request
        self.lock = threading.Lock()  # decides between "started" and "cancelled"
        self.started = self.cancelled = False
        self.done = threading.Event()
        self.reply = None


def run_job(job):
    with job.lock:
        if job.cancelled:
            return
        job.started = True
    name = job.request.get("fn") or job.request.get("op")
    log(f"RUN   {name}")  # before the call: if NIS hangs, this is the last line
    started = time.perf_counter()
    try:
        job.reply = {"ok": True, "answer": run(job.request)}
        state["replies_ok"] += 1
    except BaseException as error:  # noqa: BLE001 - every failure goes back as a reply
        job.reply = {"ok": False, "error": f"{type(error).__name__}: {error}"}
        state["replies_error"] += 1
    job.reply["nis_ms"] = round(1000 * (time.perf_counter() - started), 3)
    log(f"DONE  {name}: {'ok' if job.reply['ok'] else job.reply['error']}")
    job.done.set()


# -- the server: socket threads queue requests, NIS's thread runs them ----------------------
def answer(line):
    state["requests"] += 1
    try:
        request = json.loads(line)
        if not isinstance(request, dict):
            raise ValueError("a request is a JSON object")
    except ValueError as error:
        state["replies_error"] += 1
        return {"ok": False, "error": f"bad request: {error}"}
    if request.get("op") == "shutdown":
        request_stop("shutdown request from the client")
        return {"ok": True, "answer": {"stopping": True}}
    job = Job(request)
    _jobs.put(job)
    if not job.done.wait(REQUEST_TIMEOUT_S):
        with job.lock:
            if not job.started:
                job.cancelled = True
                state["timeouts"] += 1
                return {"ok": False, "error": f"timeout: NIS did not take the request within "
                                              f"{REQUEST_TIMEOUT_S} s (is the macro loop running?)"}
        job.done.wait()  # NIS is running it: wait for the end
    return job.reply


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        log(f"connection from {self.client_address[0]}:{self.client_address[1]}")
        while True:
            try:
                line = self.rfile.readline()
            except OSError:
                break
            if not line:
                break
            reply = answer(line.decode("utf-8", "replace"))
            try:
                self.wfile.write((json.dumps(reply, default=repr) + "\n").encode("utf-8"))
            except OSError:
                log("the client left before its reply")
                break
        log("connection closed")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = False  # never two servers on one port
    daemon_threads = True


# -- the three calls the macro makes ------------------------------------------------------
def start():
    """Open the server (the macro's first line)."""
    global _server, _last_pump, _self_test_thread
    state["main_thread"] = threading.get_ident()
    main = sys.modules["__main__"].__dict__
    old = main.pop("_step1_server", None)  # left by an earlier run stopped with the Stop button
    if old is not None:
        log("closing the server of an earlier run")
        try:
            old.shutdown()
            old.server_close()
        except Exception as error:  # noqa: BLE001
            log(f"could not close it: {error}")
    log(f"start: step 1 version {VERSION}, file {os.path.abspath(__file__)}")
    log(f"start: Python {sys.version.split()[0]}, pid {os.getpid()}, nis module {nis is not None}")
    try:
        _server = Server((HOST, PORT), Handler)
    except OSError as error:
        log(f"could not listen on port {PORT}: {error}")
        state["stopped_by"] = f"could not listen: {error}"
        save()
        open(STOP_FILE, "w").close()
        return
    main["_step1_server"] = _server
    threading.Thread(target=_server.serve_forever, kwargs={"poll_interval": 0.05},
                     name="step1-server", daemon=True).start()
    log(f"listening on {HOST}:{PORT}")
    _last_pump = time.monotonic()
    if WATCH_DIALOGS and sys.platform == "win32":
        threading.Thread(target=watch_dialogs, name="step1-dialogs", daemon=True).start()
    if SELF_TEST:
        _self_test_thread = threading.Thread(target=self_test, name="step1-self-test", daemon=True)
        _self_test_thread.start()
    save()
    if nis is not None:
        nis.log(f"step 1: listening on port {PORT}")


def pump():
    """Run the requests that came in (each pass of the macro loop). Never raises."""
    global _last_pump
    try:
        now = time.monotonic()
        if _last_pump is not None:
            state["longest_gap_s"] = max(state["longest_gap_s"], round(now - _last_pump, 3))
        state["pumps"] += 1
        if threading.get_ident() != state["main_thread"]:
            state["pumps_off_main_thread"] += 1
        if _server is None:
            open(STOP_FILE, "w").close()
            return
        try:
            run_job(_jobs.get(timeout=PUMP_WAIT_S))
            while True:
                run_job(_jobs.get_nowait())
        except queue.Empty:
            pass
        if (_stop_requested or now - _t0 > MAX_RUN_S) and not os.path.exists(STOP_FILE):
            if not _stop_requested:
                state["stopped_by"] = f"{MAX_RUN_S} s limit"
            open(STOP_FILE, "w").close()
        _last_pump = time.monotonic()
    except BaseException as error:  # noqa: BLE001 - an error here would reach NIS every pass
        if len(state["pump_errors"]) < 20:
            state["pump_errors"].append(f"{type(error).__name__}: {error}")
            log(f"pump error: {traceback.format_exc()}")


def stop():
    """Close the server and write the summary (the macro's last line)."""
    global _server, _stopped
    if _stopped:
        return
    _stopped = True
    if state["stopped_by"] is None:
        state["stopped_by"] = "the macro's Stop button or the stop file"
    if _server is not None:
        _server.shutdown()
        _server.server_close()
        sys.modules["__main__"].__dict__.pop("_step1_server", None)
        _server = None
    if _self_test_thread is not None:
        _self_test_thread.join(timeout=10)  # the client checks the server closed, then ends
    state["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    state["run_s"] = round(time.monotonic() - _t0, 1)
    state["pumps_per_s"] = round(state["pumps"] / max(state["run_s"], 0.1), 1)
    save()
    write_summary()
    log(f"stopped ({state['stopped_by']})")
    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)
    if nis is not None:
        nis.log("step 1: stopped; see the results folder")


def write_summary():
    s = state
    lines = [
        f"step 1, {s['started']} to {s.get('finished', '?')}, stopped by: {s['stopped_by']}",
        f"version {s['version']}, {s['file']}",
        f"Python {s['python'].split()[0]}, nis module: {s['nis_module']}",
        f"macro loop: {s['pumps']} passes, {s.get('pumps_per_s', '?')} per second, longest gap "
        f"{s['longest_gap_s']} s, passes not on NIS's thread: {s['pumps_off_main_thread']}",
        f"requests: {s['requests']}, ok {s['replies_ok']}, error replies {s['replies_error']}, "
        f"timeouts {s['timeouts']}",
        f"pump errors: {len(s['pump_errors'])}  {s['pump_errors'][:3]}",
        f"dialogs seen: {len(s['dialogs'])}",
        f"outside client (see step1_client.txt): {s['client']}",
    ] + [f"   {d}" for d in s["dialogs"]] + ["", "self-test (from inside NIS's Python):"]
    lines += s["self_test"] or ["   did not run"]
    with open(os.path.join(OUT_DIR, "step1_summary.txt"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


# -- the self-test, and the outside client ------------------------------------------------
def self_test():
    """Run the checks from a thread, through the socket, as a program outside NIS would."""
    time.sleep(0.5)
    out = state["self_test"]
    try:
        checks.run(PORT, out, on_line=lambda _: save())
    except Exception as error:  # noqa: BLE001
        out.append(f"FAIL self-test stopped: {type(error).__name__}: {error}")
    log("self-test done: " + ("all ok" if all(x.startswith("ok") for x in out) else "see summary"))
    save()
    write_summary()
    if AUTO_CLIENT:
        run_client()


def request_stop(reason):
    global _stop_requested
    if state["stopped_by"] is None:
        state["stopped_by"] = reason
    _stop_requested = True


def python_exe():
    """NIS's own python.exe, if NIS ships one; None if not."""
    names = ("python.exe", "python3.exe", "python", "python3")
    folders = [os.path.dirname(sys.executable), sys.base_prefix, sys.prefix,
               os.path.join(sys.base_prefix, "Scripts")]
    if os.path.basename(sys.executable).lower().startswith("python"):
        return sys.executable
    for folder in folders:
        for name in names:
            path = os.path.join(folder, name)
            if os.path.isfile(path):
                return path
    return None


def client_done(report):
    try:
        with open(report, encoding="utf-8") as handle:
            return any(line.startswith("done:") for line in handle)
    except OSError:
        return False


def run_client():
    """Start the outside client as its own program, in a window of its own, then end the run.

    The window shows each check as it runs and says FINISHED at the end; it stays open until
    someone presses Enter, and the run does not wait for that. First choice: step1_client.py with NIS's own python.exe. Without one: step1_client.ps1
    with Windows PowerShell. The client ends the run with a shutdown request; if it cannot,
    this does.
    """
    python = python_exe()
    state["client_python_search"] = {"sys.executable": sys.executable, "base_prefix": sys.base_prefix,
                                     "found": python}
    if python:
        command = [python, "-I", os.path.join(HERE, "step1_client.py"), str(PORT)]
    else:
        command = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                   "-File", os.path.join(HERE, "step1_client.ps1")]
    log("starting the outside client: " + " ".join(command))
    try:
        process = subprocess.Popen(command, cwd=HERE,
                                   creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
    except OSError as error:
        state["client"] = f"could not start {command[0]}: {error}"
        log(state["client"])
        request_stop("the outside client could not be started")
        return
    report = os.path.join(OUT_DIR, "step1_client.txt")
    deadline = time.monotonic() + CLIENT_TIMEOUT_S
    name = os.path.basename(command[0])
    while True:  # until the client exits, or has written its last line and waits for Enter
        if process.poll() is not None:
            state["client"] = f"{name}, exit code {process.returncode}"
            break
        if client_done(report):
            state["client"] = f"{name}, finished; its window waits for Enter"
            break
        if time.monotonic() > deadline:
            process.kill()
            state["client"] = f"{name} did not finish within {CLIENT_TIMEOUT_S} s; stopped"
            break
        time.sleep(0.2)
    log(f"outside client: {state['client']}")
    request_stop("the outside client finished")


# -- dialogs: does NIS show one? -----------------------------------------------------------
def watch_dialogs():
    """Every 0.3 s, note new dialog windows (class #32770) of this process. Never clicks."""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32")
    proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    seen = set()

    def text(hwnd, getter, size=1024):
        buffer = ctypes.create_unicode_buffer(size)
        getter(hwnd, buffer, size)
        return buffer.value

    def visit(hwnd, _):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == os.getpid() and user32.IsWindowVisible(hwnd) and hwnd not in seen \
                and text(hwnd, user32.GetClassNameW, 256) == "#32770":
            seen.add(hwnd)
            parts = []
            child = proc(lambda h, _: parts.append(text(h, user32.GetWindowTextW)) or True)
            user32.EnumChildWindows(hwnd, child, 0)
            entry = f"{time.strftime('%H:%M:%S')} '{text(hwnd, user32.GetWindowTextW)}': " \
                    + " | ".join(p for p in parts if p)[:400]
            state["dialogs"].append(entry)
            log(f"DIALOG {entry}")
        return True

    callback = proc(visit)
    while not _stopped:
        try:
            user32.EnumWindows(callback, 0)
        except Exception as error:  # noqa: BLE001
            log(f"dialog watcher stopped: {error}")
            return
        time.sleep(0.3)
