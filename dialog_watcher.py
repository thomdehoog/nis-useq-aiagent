# Close NIS-Elements' blocking dialogs during an unattended step0 run, and note what each said.
# Runs OUTSIDE NIS (any Python on the same desktop): every half second it looks for a dialog
# window (class #32770) of nis_ar.exe, logs its title and text to results\dialogs.log, and
# presses its OK button (a dialog without one, e.g. a question, is left open). Ends when runner\done.txt appears or after --minutes.
#   python dialog_watcher.py [--minutes 30]
import ctypes, os, sys, time
from ctypes import wintypes

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "results", "dialogs.log")
DONE = os.path.join(HERE, "runner", "done.txt")
user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32")
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
BM_CLICK = 0x00F5


def text_of(hwnd):
    buffer = ctypes.create_unicode_buffer(1024)
    user32.GetWindowTextW(hwnd, buffer, 1024)
    return buffer.value


def class_of(hwnd):
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buffer, 256)
    return buffer.value


def process_name(hwnd):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    handle = kernel32.OpenProcess(0x1000, False, pid.value)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        return ""
    buffer = ctypes.create_unicode_buffer(512)
    size = wintypes.DWORD(512)
    kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size))
    kernel32.CloseHandle(handle)
    return os.path.basename(buffer.value).lower()


def children(hwnd):
    found = []
    user32.EnumChildWindows(hwnd, WNDENUMPROC(lambda h, _: found.append(h) or True), 0)
    return found


def nis_dialogs():
    found = []

    def visit(hwnd, _):
        if (user32.IsWindowVisible(hwnd) and class_of(hwnd) == "#32770"
                and process_name(hwnd) == "nis_ar.exe"):
            found.append(hwnd)
        return True
    user32.EnumWindows(WNDENUMPROC(visit), 0)
    return found


def main():
    minutes = float(sys.argv[sys.argv.index("--minutes") + 1]) if "--minutes" in sys.argv else 30
    end = time.time() + 60 * minutes
    closed = 0
    while time.time() < end and not os.path.exists(DONE):
        for dialog in nis_dialogs():
            parts = [text_of(c) for c in children(dialog) if class_of(c) == "Static" and text_of(c)]
            button = next((c for c in children(dialog) if class_of(c) == "Button"
                           and text_of(c).replace("&", "").strip().lower() == "ok"), None)  # only OK: never answer a question
            with open(LOG, "a", encoding="utf-8") as handle:
                handle.write(f"{time.strftime('%H:%M:%S')} {text_of(dialog)!r}: "
                             f"{' | '.join(p.replace(chr(10), ' ') for p in parts)} "
                             f"-> {'pressed ' + text_of(button) if button else 'no OK button, left open'}\n")
            if button:
                user32.PostMessageW(button, BM_CLICK, 0, 0)
                closed += 1
            time.sleep(0.3)
        time.sleep(0.5)
    print(f"closed {closed} dialogs")


if __name__ == "__main__":
    main()
