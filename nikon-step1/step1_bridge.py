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
import socket
import socketserver
import sys
import threading
import time
import traceback

# -- settings: edit before a run ----------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "results")
HOST = "127.0.0.1"  # this computer only
PORT = 54471  # not the bridge's 54470, so the two never meet
STOP_FILE = os.environ.get("STEP1_STOP_FILE", r"C:\Users\Public\nikon-step1.stop")  # loop ends when it exists
MAX_RUN_S = 900  # the loop ends by itself after 15 minutes
PUMP_WAIT_S = 0.05  # how long one pass of the macro loop waits for a request
REQUEST_TIMEOUT_S = 30.0  # a request not started by then is answered "timeout" and never run
MAX_HOLD_S = 5.0  # the longest "hold" (keeps NIS's thread busy, to see if NIS freezes)
SELF_TEST = True  # run the checks from a thread inside NIS's Python at start
WATCH_DIALOGS = True  # note every dialog window NIS opens (only notes; never clicks)

# Only these NIS functions may be called in step 1: readings, nothing that moves or captures.
READS = {
    "Get_InfoStr", "StgGetPosZ", "StgGetPosXY", "StgXY_GetLimits", "StgZ_GetLimits",
    "GetOptConfCount", "GetOptConfName", "GetSelectedOptConf", "Stg_IsNosepiecePresent",
    "Stg_GetNosepiecePositions", "Stg_IsPFSPresent", "Stg_GetPFSStatus", "Get_Calibration",
}
UNKNOWN = "ThisFunctionDoesNotExist_Step1"  # let through on purpose: how nis.mac says "no such"
PTR_TYPES = {"byte", "char", "char8", "double", "dword", "int", "int64", "long", "short", "word"}

try:
    import nis  # exists only inside NIS-Elements
except ImportError:
    nis = None

os.makedirs(OUT_DIR, exist_ok=True)
_log_lock = threading.Lock()
_log_file = open(os.path.join(OUT_DIR, "step1.log"), "a", encoding="utf-8")

state = {
    "started": time.strftime("%Y-%m-%d %H:%M:%S"),
    "python": sys.version, "platform": platform.platform(), "pid": os.getpid(),
    "nis_module": nis is not None,
    "main_thread": None,  # the thread start() ran on: NIS's own
    "pumps": 0, "pumps_off_main_thread": 0, "longest_gap_s": 0.0,
    "requests": 0, "replies_ok": 0, "replies_error": 0, "timeouts": 0,
    "pump_errors": [], "dialogs": [], "self_test": [], "stopped_by": None,
}
_jobs = queue.Queue()
_server = None
_t0 = time.monotonic()
_last_pump = None
_stop_requested = False
_stopped = False


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
        global _stop_requested
        _stop_requested = True
        state["stopped_by"] = "shutdown request"
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
    global _server, _last_pump
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
        threading.Thread(target=self_test, name="step1-self-test", daemon=True).start()
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
        f"Python {s['python'].split()[0]}, nis module: {s['nis_module']}",
        f"macro loop: {s['pumps']} passes, {s.get('pumps_per_s', '?')} per second, longest gap "
        f"{s['longest_gap_s']} s, passes not on NIS's thread: {s['pumps_off_main_thread']}",
        f"requests: {s['requests']}, ok {s['replies_ok']}, error replies {s['replies_error']}, "
        f"timeouts {s['timeouts']}",
        f"pump errors: {len(s['pump_errors'])}  {s['pump_errors'][:3]}",
        f"dialogs seen: {len(s['dialogs'])}",
    ] + [f"   {d}" for d in s["dialogs"]] + ["", "self-test (from inside NIS's Python):"]
    lines += s["self_test"] or ["   did not run"]
    with open(os.path.join(OUT_DIR, "step1_summary.txt"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


# -- the checks, as a client would send them ----------------------------------------------
# (name, request, should the reply be ok?) step1_client.ps1 sends the same.
CHECKS = [
    ("ping", {"op": "ping"}, True),
    ("NIS version", {"op": "call", "fn": "Get_InfoStr", "args": [1, {"ptr": "char"}]}, True),
    ("Z position", {"op": "call", "fn": "StgGetPosZ", "args": [{"ptr": "double"}, 0]}, True),
    ("XY position (not there without hardware)",
     {"op": "call", "fn": "StgGetPosXY", "args": [{"ptr": "double"}, {"ptr": "double"}]}, True),
    ("optical configurations", {"op": "call", "fn": "GetOptConfCount", "args": []}, True),
    ("PFS status", {"op": "call", "fn": "Stg_GetPFSStatus", "args": []}, True),
    ("unknown function", {"op": "call", "fn": UNKNOWN, "args": []}, False),
    ("function not on the list (a move)", {"op": "call", "fn": "StgMoveZ", "args": [0, 0]}, False),
    ("Python error", {"op": "raise"}, False),
    ("unknown op", {"op": "fly"}, False),
]
# Last, because it hands NIS's own code a wrong value: if anything crashes NIS, it is this.
LAST_CHECKS = [
    ("wrong arguments", {"op": "call", "fn": "StgGetPosZ", "args": ["text"]}, False),
]


def self_test():
    """Run CHECKS from a thread, through the socket, like a program outside NIS would."""
    time.sleep(0.5)
    out = state["self_test"]
    try:
        with socket.create_connection((HOST, PORT), timeout=REQUEST_TIMEOUT_S + 5) as sock:
            stream = sock.makefile("rwb")

            def send(raw):
                stream.write(raw.encode("utf-8") + b"\n")
                stream.flush()
                return json.loads(stream.readline())

            def check(name, request, want_ok):
                started = time.perf_counter()
                reply = send(json.dumps(request))
                ms = round(1000 * (time.perf_counter() - started), 1)
                passed = reply.get("ok") is want_ok
                text = json.dumps(reply.get("answer", reply.get("error")), default=repr)[:200]
                out.append(f"{'ok  ' if passed else 'FAIL'} {name:<42} {ms:>8} ms  {text}")
                save()

            for name, request, want_ok in CHECKS:
                check(name, request, want_ok)
            reply = send("this is not json")
            out.append(f"{'ok  ' if reply.get('ok') is False else 'FAIL'} {'broken request':<42}"
                       f"{'':>12}  {reply.get('error')}")
            times = []
            for _ in range(100):
                started = time.perf_counter()
                send(json.dumps(CHECKS[2][1]))
                times.append(1000 * (time.perf_counter() - started))
            times.sort()
            out.append(f"ok   100 x Z position, round trip: median {times[50]:.1f} ms, "
                       f"max {times[-1]:.1f} ms")
            save()
            for name, request, want_ok in LAST_CHECKS:
                check(name, request, want_ok)
    except Exception as error:  # noqa: BLE001
        out.append(f"FAIL self-test stopped: {type(error).__name__}: {error}")
    log("self-test done: " + ("all ok" if all(x.startswith("ok") for x in out) else "see summary"))
    save()
    write_summary()


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
