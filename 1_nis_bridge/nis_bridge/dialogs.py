"""Press OK on one NIS message that would otherwise stop the bridge.

Some NIS functions end with a message box that waits for a click, which blocks
NIS's main thread and so the bridge: ``RestoreOptConfEx`` says "Optical
Configurations Import succesfully finished." ``ClickOk`` watches, from a thread of
its own and only while such a call runs, for a dialog of this NIS process whose
title and text match exactly, and presses its OK button. Any other dialog, such
as the import's question which configuration to keep, is left for the operator.

    with ClickOk(title, text):
        nis_function()

Standard library only: this runs inside NIS-Elements.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-28
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import logging
import threading

from .settings import DIALOG_POLL_S

log = logging.getLogger("nis_bridge")

DIALOG_CLASS = "#32770"  # what Windows calls a standard dialog box
OK_LABELS = ("OK", "&OK")
BM_CLICK = 0x00F5


def is_the_message(title: str, texts: list[str], want_title: str, want_text: str) -> bool:
    """The dialog to press OK on: this title, this text, and an OK button."""
    return (
        title == want_title
        and any(want_text in text for text in texts)
        and any(text in OK_LABELS for text in texts)
    )


class ClickOk:
    """While in the ``with`` block, press OK on the message ``title`` / ``text``."""

    def __init__(self, title: str, text: str) -> None:
        self.title, self.text = title, text
        self.pressed = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._watch, daemon=True)

    def __enter__(self) -> ClickOk:
        self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self._stop.set()
        self._thread.join()

    def _watch(self) -> None:
        try:
            windows = _Windows()
        except (AttributeError, OSError):  # not Windows: nothing to watch
            return
        clicked = set()  # a dialog takes a moment to close; press its OK once
        while not self._stop.wait(DIALOG_POLL_S):
            for dialog in windows.dialogs():
                if dialog in clicked:
                    continue
                children = windows.children(dialog)
                texts = [windows.text(child) for child in children]
                if is_the_message(windows.text(dialog), texts, self.title, self.text):
                    button = next(c for c, t in zip(children, texts, strict=True) if t in OK_LABELS)
                    windows.click(button)
                    clicked.add(dialog)
                    self.pressed += 1
                    log.info("pressed OK on %r", self.title)


class _Windows:
    """The few user32 calls ClickOk needs, for windows of this process."""

    def __init__(self) -> None:
        import ctypes
        from ctypes import wintypes

        self.ctypes, self.wintypes = ctypes, wintypes
        self.user32 = ctypes.WinDLL("user32")
        self.pid = ctypes.WinDLL("kernel32").GetCurrentProcessId()
        self.callback = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def _collect(self, enum, *args) -> list:
        found = []
        enum(*args, self.callback(lambda hwnd, _: found.append(hwnd) or True), 0)
        return found

    def dialogs(self) -> list:
        mine = []
        for hwnd in self._collect(self.user32.EnumWindows):
            pid = self.wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, self.ctypes.byref(pid))
            ours = pid.value == self.pid and self.class_of(hwnd) == DIALOG_CLASS
            if ours and self.user32.IsWindowVisible(hwnd):
                mine.append(hwnd)
        return mine

    def children(self, hwnd) -> list:
        return self._collect(self.user32.EnumChildWindows, hwnd)

    def text(self, hwnd) -> str:
        buffer = self.ctypes.create_unicode_buffer(1024)
        self.user32.GetWindowTextW(hwnd, buffer, 1024)
        return buffer.value

    def class_of(self, hwnd) -> str:
        buffer = self.ctypes.create_unicode_buffer(256)
        self.user32.GetClassNameW(hwnd, buffer, 256)
        return buffer.value

    def click(self, button) -> None:
        # Posted, not sent: the dialog's thread is NIS's main thread, busy in the dialog
        self.user32.PostMessageW(button, BM_CLICK, 0, 0)
