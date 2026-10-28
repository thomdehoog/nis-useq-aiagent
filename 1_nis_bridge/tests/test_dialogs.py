"""ClickOk: OK is pressed on NIS's "import finished" message, and on nothing else.

On Windows a real message box is opened in this process, as NIS would open it.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-28
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

import sys
import threading
import time

import pytest

from nis_bridge.dialogs import ClickOk, is_the_message
from nis_bridge.settings import OPTCONF_IMPORT_DONE

TITLE, TEXT = OPTCONF_IMPORT_DONE
FINISHED = "Optical Configurations Import succesfully finished."
QUESTION = "There is already an optical configuration with the same name: BF"


def test_only_the_finished_message_is_the_one():
    assert is_the_message(TITLE, [FINISHED, "&OK"], TITLE, TEXT)
    assert not is_the_message("Import Optical Configuration", [QUESTION, "Cancel"], TITLE, TEXT)
    assert not is_the_message(TITLE, [QUESTION, "&OK"], TITLE, TEXT)  # another text
    assert not is_the_message(TITLE, [FINISHED], TITLE, TEXT)  # no OK button to press


def open_box(title: str, text: str, answers: list) -> threading.Thread:
    import ctypes

    def show():
        answers.append(ctypes.windll.user32.MessageBoxW(None, text, title, 0))

    thread = threading.Thread(target=show, daemon=True)
    thread.start()
    return thread


@pytest.mark.skipif(sys.platform != "win32", reason="a Windows message box")
def test_presses_ok_on_the_finished_message_only():
    import ctypes

    answers: list = []
    with ClickOk(TITLE, TEXT) as watcher:
        other = open_box(TITLE, QUESTION, answers)
        finished = open_box(TITLE, FINISHED, answers)
        finished.join(timeout=5)
        time.sleep(0.5)  # time enough to press the other one too, if it would
        assert not finished.is_alive() and answers == [1]  # IDOK
        assert other.is_alive() and watcher.pressed == 1
    hwnd = ctypes.windll.user32.FindWindowW("#32770", TITLE)
    ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE: end the test's box
    other.join(timeout=5)
    assert not other.is_alive()
