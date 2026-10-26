"""Step 2, the watch window: progress, dialogs, and the end. A program of its own, outside NIS.

Started by step2_calls.py with NIS's own python.exe:

    python step2_watch.py NIS_PID RESULTS_FOLDER

Every 0.3 s it reads results\\step2_current.json and shows how far the run is. A call that
opens a window of NIS's (a dialog, a message, a file chooser) would wait for a person; this
notes the window and its text in results\\step2_dialogs.jsonl, with the function that opened
it, and closes it: Cancel, No, Close or OK, in that order, else it asks the window to close.
It never touches "Confirm Interrupting Macro", so the macro Stop button keeps working.

Standard library only.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-26
License: MIT
"""

import json
import os
import sys
import time

NIS_PID = int(sys.argv[1]) if len(sys.argv) > 1 else 0
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
CURRENT = os.path.join(OUT_DIR, "step2_current.json")
DIALOGS = os.path.join(OUT_DIR, "step2_dialogs.jsonl")
NEVER_TOUCH = ("Confirm Interrupting Macro",)
BUTTONS = ("cancel", "no", "close", "ok", "continue", "abort", "ignore")  # first found is pressed
WAIT_BEFORE_CLOSING_S = 1.0  # a window must stay this long before it is closed
HANG_S = 60  # a call this long is hung: NIS is closed and started again, and the run carries on
MAX_RESTARTS = 200  # after this many restarts of NIS, stop restarting
MACRO = os.path.join(os.path.dirname(os.path.abspath(OUT_DIR)), "step2.mac")
RESTARTS = os.path.join(OUT_DIR, "step2_restarts.txt")
WINDOWS = sys.platform == "win32"

if WINDOWS:
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32")
    kernel32 = ctypes.WinDLL("kernel32")
    ENUM = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    WM_CLOSE, BM_CLICK = 0x0010, 0x00F5


def text(hwnd):
    buffer = ctypes.create_unicode_buffer(512)
    user32.GetWindowTextW(hwnd, buffer, 512)
    return buffer.value


def class_name(hwnd):
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buffer, 256)
    return buffer.value


def nis_windows():
    """The visible top-level windows of NIS."""
    found = []

    def visit(hwnd, _):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == NIS_PID and user32.IsWindowVisible(hwnd):
            found.append(hwnd)
        return True

    user32.EnumWindows(ENUM(visit), 0)
    return found


def children(hwnd):
    found = []

    def visit(child, _):
        found.append((child, class_name(child), text(child)))
        return True

    user32.EnumChildWindows(hwnd, ENUM(visit), 0)
    return found


def close(hwnd):
    """Press the first of BUTTONS the window has; else ask the window to close. Says what it did."""
    buttons = [(h, t) for h, c, t in children(hwnd) if c.lower() == "button" and t]
    for wanted in BUTTONS:
        for child, label in buttons:
            if label.replace("&", "").strip().lower() == wanted:
                user32.PostMessageW(child, BM_CLICK, 0, 0)
                return f"pressed {label.replace('&', '')}"
    user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
    return "asked to close"


def nis_exe():
    """The full path of the running nis_ar.exe, to start it again after a crash or hang."""
    if not WINDOWS:
        return None
    handle = kernel32.OpenProcess(0x1000, False, NIS_PID)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        return None
    buffer = ctypes.create_unicode_buffer(1024)
    size = wintypes.DWORD(1024)
    ok = kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size))
    kernel32.CloseHandle(handle)
    return buffer.value if ok else None


def restart(exe, reason, fn):
    """Close NIS if it still runs, start it again with step2.mac, and end this window.

    The new run notes the function NIS went down in as "crashed or hung" and carries on after it.
    """
    count = 1
    if os.path.exists(RESTARTS):
        with open(RESTARTS, encoding="utf-8") as handle:
            count = sum(1 for _ in handle) + 1
    with open(RESTARTS, "a", encoding="utf-8") as handle:
        handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\t{fn}\t{reason}\n")
    print(f" {fn}: {reason}.", flush=True)
    if count > MAX_RESTARTS:
        end([f"NIS went down {count} times; no more restarts.", "Start NIS and run step2.mac by hand."])
        return
    if not exe:
        end(["Start NIS again and run step2.mac: it carries on after that function."])
        return
    if nis_alive():
        print(" Closing NIS ...", flush=True)
        handle = kernel32.OpenProcess(0x0001 | 0x00100000, False, NIS_PID)  # TERMINATE | SYNCHRONIZE
        if handle:
            kernel32.TerminateProcess(handle, 1)
            kernel32.WaitForSingleObject(handle, 20000)
            kernel32.CloseHandle(handle)
        time.sleep(2)
    macro = MACRO.replace("\\", "\\\\")
    print(f" Starting NIS again (restart {count}); the run carries on after {fn}.", flush=True)
    print(" If it does not carry on within 3 minutes: run step2.mac by hand.", flush=True)
    import subprocess
    flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    subprocess.Popen([exe, "-c", f'RunMacro("{macro}")'], creationflags=flags, close_fds=True)
    time.sleep(5)


def nis_alive():
    if not WINDOWS:
        try:
            os.kill(NIS_PID, 0)
            return True
        except OSError:
            return False
    handle = kernel32.OpenProcess(0x00100000, False, NIS_PID)  # SYNCHRONIZE
    if not handle:
        return False
    alive = kernel32.WaitForSingleObject(handle, 0) == 0x00000102  # WAIT_TIMEOUT
    kernel32.CloseHandle(handle)
    return alive


def read_current():
    try:
        with open(CURRENT, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def counts_text(counts):
    return ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))


def end(lines):
    print()
    print("=" * 78)
    for line in lines:
        print(" " + line)
    print("=" * 78, flush=True)
    if sys.stdin is not None and sys.stdin.isatty():
        try:
            input(" Press Enter to close this window. ")
        except EOFError:
            pass


def main():
    print("=" * 78)
    print(" STEP 2 IS RUNNING: every NIS function is called once. Leave NIS alone until")
    print(" this window says FINISHED. Dialogs that calls open are closed by this window.")
    print("=" * 78, flush=True)
    baseline = set(nis_windows()) if WINDOWS else set()
    exe = nis_exe()
    seen, acted = {}, {}
    last_print, last_fn, fn_since = 0.0, None, time.time()
    while True:
        current = read_current() or {}
        now = time.time()
        fn = current.get("fn")
        if fn != last_fn:
            last_fn, fn_since = fn, now
        if now - last_print > 1.0:
            last_print = now
            line = f"[{current.get('i', 0)}/{current.get('n', '?')}] now: {fn or '-'}"
            if fn and now - fn_since > 2:
                line += f" (reachable, running in NIS {int(now - fn_since)} s; NIS restarts at {HANG_S} s)"
            print(line, flush=True)
            print(f"      so far: {counts_text(current.get('counts', {}))}", flush=True)
        if fn and not current.get("done") and now - fn_since > HANG_S:
            restart(exe, f"no answer for {HANG_S} s (hung)", fn)
            return
        if current.get("done"):
            end([f"STEP 2 FINISHED: {current.get('n')} functions called.",
                 counts_text(current.get("counts", {})),
                 f"Send the folder {OUT_DIR}"])
            return
        if current.get("stopped"):
            end([f"Step 2 stopped at {current.get('i')} of {current.get('n')} (the macro Stop button).",
                 "Run step2.mac again to carry on where it stopped."])
            return
        if not nis_alive():
            restart(exe, "NIS closed or crashed", fn or "the run")
            return
        if WINDOWS:
            for hwnd in nis_windows():
                if hwnd in baseline:
                    continue
                title = text(hwnd)
                if title in NEVER_TOUCH:
                    continue
                first = seen.setdefault(hwnd, now)
                if now - first < WAIT_BEFORE_CLOSING_S or now - acted.get(hwnd, 0) < 2.0:
                    continue
                texts = [t for _, _, t in children(hwnd) if t][:20]
                did = close(hwnd)
                acted[hwnd] = now
                record = {"time": time.strftime("%H:%M:%S"), "fn": fn, "title": title,
                          "class": class_name(hwnd), "texts": texts, "action": did}
                with open(DIALOGS, "a", encoding="utf-8") as handle:
                    handle.write(json.dumps(record) + "\n")
                print(f"   window from {fn}: '{title}' {' | '.join(texts)[:80]} -> {did}", flush=True)
        time.sleep(0.3)


if __name__ == "__main__":
    main()
