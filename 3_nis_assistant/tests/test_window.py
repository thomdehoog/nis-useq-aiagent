"""The chat window, offscreen, with a scripted model and the fake NIS behind the bridge.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
"""

import time

import pytest

pytest.importorskip("pytestqt")
pytest.importorskip("pydantic_ai")

from nis_bridge.client import NisConnectionError
from nis_engine import NisEngine
from PySide6.QtWidgets import QMessageBox
from test_agent import Script, moves

from nis_assistant.agent import Assistant
from nis_assistant.tools import Microscope
from nis_assistant.window import AssistantWindow


@pytest.fixture
def open_window(qtbot, port, tmp_path):
    engines, windows = [], []

    def make(*steps, vision=None):
        engine = NisEngine("127.0.0.1", port, timeout=5.0)
        engines.append(engine)
        microscope = Microscope(engine, output_dir=tmp_path)
        if vision is not None:
            microscope.vision_model = Script(vision).model()
        else:
            microscope.vision = False  # no vision model: the look and run tools skip it
        window = AssistantWindow(Assistant(microscope, model=Script(*steps).model()))
        # A failed test may leave a turn running; the window refuses to close then
        # (with a dialog nobody can click), so the turn is ended before the close.
        qtbot.addWidget(window, before_close_func=settle)
        windows.append(window)
        return window

    def settle(window):
        window.stop_microscope()
        qtbot.waitUntil(lambda: not window.busy, timeout=10000)

    yield make
    for engine in engines:
        engine.close()


def ask(qtbot, window, text):
    window.prompt.setText(text)
    window.send()
    qtbot.waitUntil(lambda: not window.busy, timeout=10000)
    return window.transcript.toPlainText()


def test_a_question_and_its_answer(qtbot, open_window):
    window = open_window("The stage is at x 1000 um.")
    assert "Stage x 1000.0" in window.status.text()
    transcript = ask(qtbot, window, "where is the stage?")
    assert "where is the stage?" in transcript and "The stage is at x 1000 um." in transcript


def start(window, text):
    window.prompt.setText(text)
    window.send()


def test_a_long_move_is_asked_about_in_the_chat(qtbot, open_window, fake):
    long = ("move_stage", {"x": 20000})
    window = open_window(long, "Shall I move 19 mm to x = 20 mm?", long, "We are at x 20 mm.")
    transcript = ask(qtbot, window, "go to x 20 mm")
    assert "Shall I move 19 mm to x = 20 mm?" in transcript and moves(fake) == []
    assert "We are at x 20 mm." in ask(qtbot, window, "yes")
    assert moves(fake) == ["move_xy(20000,-500)"] and "Stage x 20000.0" in window.status.text()


def test_cancel_prompt_stops_the_assistant(qtbot, open_window, fake):
    slow_move = fake.move_xy

    def move_xy(x, y):  # a slower stage, so there is time to press Cancel prompt
        time.sleep(0.3)
        slow_move(x, y)

    fake.move_xy = move_xy
    window = open_window(("move_stage", {"x": 1100}), ("move_stage", {"x": 1200}), "Stopped.")
    window.show_tools.setChecked(True)
    start(window, "move twice")
    qtbot.waitUntil(lambda: "move_stage" in window.transcript.toPlainText(), timeout=10000)
    window.cancel_button.click()
    qtbot.waitUntil(lambda: not window.busy, timeout=10000)
    assert moves(fake) == ["move_xy(1100,-500)"]  # the second move did not run
    assert "Cancelled." in window.transcript.toPlainText()


def test_tool_calls_show_when_asked(qtbot, open_window):
    window = open_window(("move_stage", {"x": 1100}), "Moved.", ("get_status", {}), "Here.")
    ask(qtbot, window, "move a little")
    assert "move_stage" not in window.transcript.toPlainText()
    window.show_tools.setChecked(True)
    assert "get_status()" in ask(qtbot, window, "status?")


def test_clear_context_empties_the_chat_and_the_memory(qtbot, open_window):
    window = open_window("One.", "Two.")
    ask(qtbot, window, "good morning")
    window.clear_context()
    assert "good morning" not in window.transcript.toPlainText() and window.assistant.history == []


def test_a_limit_breach_shows_the_red_banner(qtbot, open_window, fake):
    window = open_window(("move_stage", {"z": 20000}), "That is outside the limits.")
    ask(qtbot, window, "go to z 20 mm")
    assert (
        window.warning.isVisibleTo(window) and "outside the stage limits" in window.warning.text()
    )
    assert moves(fake) == []


def test_looking_fills_the_image_panel(qtbot, open_window):
    window = open_window(("look", {"question": "focus?"}), "Looks flat.", vision="A flat field.")
    ask(qtbot, window, "look")
    assert window.image.pixmap() is not None and not window.image.pixmap().isNull()
    assert window.caption.text() == "focus?"


def test_the_model_panel_folds_and_applies_a_choice(qtbot, open_window, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    window = open_window()
    panel = window.panel
    assert panel.body.isHidden() and "no model" in panel.summary.text()
    panel.toggle.setChecked(True)
    assert not panel.body.isHidden()
    picker = panel.language
    picker.provider.setCurrentText("Gemini")
    assert picker.model.text() == "gemini-3.5-flash-lite" and picker.base_url.isHidden()
    # without a key, nothing changes and the panel stays open with the advice
    panel.apply()
    assert "The model was not changed" in window.transcript.toPlainText()
    assert "GEMINI_API_KEY" in panel.note.text() and not panel.body.isHidden()
    # with a key, the assistant talks to that model and the panel folds shut
    picker.key.setText("secret")
    panel.apply()
    assert window.assistant.endpoint.provider == "Gemini"
    assert type(window.assistant.model).__name__ == "GoogleModel"
    assert "Gemini" in panel.summary.text() and panel.body.isHidden()
    assert "Talking to Gemini" in window.transcript.toPlainText()
    assert "secret" not in window.transcript.toPlainText()


def test_a_server_picker_shows_its_address_and_a_file_picker_its_files(
    qtbot, open_window, tmp_path
):
    window = open_window()
    picker = window.panel.vision
    assert picker.same
    picker.mode.setCurrentText("Cloud")
    picker.provider.setCurrentText("OpenAI-style server")
    assert not picker.base_url.isHidden() and not picker.sees.isHidden()
    picker.sees.setChecked(True)
    assert picker.cloud_endpoint().vision and not picker.cloud_endpoint().needs_key
    (tmp_path / "tiny-1b.gguf").write_bytes(b"")
    picker.models_folder = tmp_path
    picker.mode.setCurrentText("File on this computer")
    assert picker.local_model.currentText() == "tiny-1b.gguf" and picker.key.isHidden()
    assert picker.local_path() == tmp_path / "tiny-1b.gguf"


def test_the_preferences_change_the_output_folder_and_the_letters(qtbot, open_window, tmp_path):
    window = open_window()
    prefs = window.panel.preferences
    prefs.output.setText(str(tmp_path / "elsewhere"))
    prefs.output.editingFinished.emit()
    assert window.assistant.microscope.output_dir == tmp_path / "elsewhere"
    assert "elsewhere" in window.transcript.toPlainText()
    prefs.font_size.setValue(14)
    assert window.transcript.font().pointSize() == 14


def test_the_coordinate_box_tells_the_assistant(qtbot, open_window):
    window = open_window("Hello.")
    window.axes_box.combos["x"].setCurrentText("left")
    assert window.assistant.microscope.axes["x"] == "left"
    assert "+x moves the sample left" in window.transcript.toPlainText()
    ask(qtbot, window, "hi")
    told = window.assistant.last_turn[0].instructions
    assert "left is +x and right is -x" in told


def test_a_due_schedule_waits_for_a_running_turn(qtbot, open_window, fake):
    slow = fake.get_position

    def slow_position():  # a slow stage read, so the first turn takes a few seconds
        time.sleep(2.0)
        return slow()

    fake.get_position = slow_position
    window = open_window(("get_status", {}), "Slow status.", "Fired.")
    scheduler = window.assistant.microscope.scheduler
    scheduler.add("watch", "hello", every_seconds=60)
    scheduler.clock = lambda: time.time() + 61
    start(window, "status")  # a turn is running; the due schedule must wait
    qtbot.wait(1200)
    assert "[scheduled" not in window.transcript.toPlainText() and window.busy
    qtbot.waitUntil(lambda: "Fired." in window.transcript.toPlainText(), timeout=20000)
    transcript = window.transcript.toPlainText()
    assert transcript.index("Slow status.") < transcript.index("[scheduled")


def test_a_failing_scheduled_turn_cancels_its_schedule(qtbot, open_window):
    window = open_window()  # an empty script: the model fails on the first call
    scheduler = window.assistant.microscope.scheduler
    scheduler.add("watch", "look", every_seconds=60)
    scheduler.clock = lambda: time.time() + 61
    qtbot.waitUntil(lambda: "is cancelled" in window.transcript.toPlainText(), timeout=10000)
    assert scheduler.listing() == [] and "Something went wrong" in window.transcript.toPlainText()


def test_a_due_schedule_runs_as_its_own_turn_and_stop_drops_it(qtbot, open_window):
    set_it = ("schedule", {"name": "watch", "instruction": "status", "every_seconds": 60})
    window = open_window(set_it, "Every minute.", ("get_status", {}), "Here is the status.")
    ask(qtbot, window, "status every minute")
    scheduler = window.assistant.microscope.scheduler
    assert [s["name"] for s in scheduler.listing()] == ["watch"]
    scheduler.clock = lambda: time.time() + 61  # a minute passes
    qtbot.waitUntil(
        lambda: "[scheduled 'watch'] status" in window.transcript.toPlainText(), timeout=5000
    )
    qtbot.waitUntil(lambda: not window.busy, timeout=10000)
    assert "Here is the status." in window.transcript.toPlainText()
    window.stop_microscope()
    assert (
        scheduler.listing() == []
        and "every schedule is cancelled" in window.transcript.toPlainText()
    )


def test_the_halves_sit_in_a_splitter(qtbot, open_window):
    window = open_window()
    assert window.splitter.count() == 2


def test_an_error_is_shown_and_the_window_stays_usable(qtbot, open_window):
    window = open_window()  # the script is empty: the "model" fails on the first call
    transcript = ask(qtbot, window, "hello")
    assert "Something went wrong" in transcript and window.prompt.isEnabled()


PLAN = {"name": "run", "channels": [{"config": "DAPI"}], "time_points": 12}


def test_an_acquisition_runs_from_the_window_and_stop_ends_it(qtbot, open_window, fake):
    slow_capture = fake.capture

    def capture():  # a slower camera, so there is time to press Stop
        time.sleep(0.1)
        slow_capture()

    fake.capture = capture
    run = ("run_acquisition", {"plan_id": "run-1"})
    window = open_window(
        ("plan_acquisition", PLAN), "Shall I start 12 images?", run, "Stopped early."
    )
    assert "Shall I start 12 images?" in ask(qtbot, window, "take 12 images")
    assert fake.captures == 0  # nothing starts before the operator agrees
    start(window, "yes")
    qtbot.waitUntil(lambda: window.caption.text().startswith("frame 3"), timeout=10000)
    window.stop_button.click()
    qtbot.waitUntil(lambda: not window.busy, timeout=10000)
    transcript = window.transcript.toPlainText()
    assert "Stop: the assistant is cancelled" in transcript and "Stopped early." in transcript
    assert 3 <= fake.captures < 12


def test_while_nis_starts_the_window_waits_and_then_connects(qtbot, port, tmp_path):
    engine = NisEngine("127.0.0.1", port, timeout=5.0, connect=False)
    microscope = Microscope(engine, output_dir=tmp_path, vision=False)
    window = AssistantWindow(Assistant(microscope, model=Script("Hi.").model()), nis_starting=True)
    qtbot.addWidget(window)
    assert "being started" in window.transcript.toPlainText()
    connected = lambda: "Connected to NIS-Elements" in window.transcript.toPlainText()  # noqa: E731
    qtbot.waitUntil(connected, timeout=10000)
    assert "Stage x" in window.status.text() and window.limit_fields["x", "-"].text()
    engine.close()


def test_without_the_bridge_the_window_opens_and_says_which_file_to_run(
    qtbot, port, tmp_path, monkeypatch
):
    from nis_assistant import tools as tools_module

    monkeypatch.setattr(tools_module, "MACRO", tmp_path / "start_bridge.mac")
    (tmp_path / "start_bridge.mac").write_text("")
    engine = NisEngine("127.0.0.1", port, timeout=5.0, connect=False)  # as main() does
    microscope = Microscope(engine, output_dir=tmp_path, vision=False)
    window = AssistantWindow(Assistant(microscope, model=Script("At x 1000.").model()))
    qtbot.addWidget(window)
    transcript = window.transcript.toPlainText()
    assert "bridge is not running" in transcript
    assert str(tmp_path / "start_bridge.mac") in transcript and "Run Macro From File" in transcript
    # the bridge is there by the first message (here: it always was): the window connects
    assert "At x 1000." in ask(qtbot, window, "where?")
    assert "Stage x" in window.status.text()
    engine.close()


def test_the_window_will_not_close_mid_action(qtbot, open_window, monkeypatch):
    told = []
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: told.append(a[1]))
    window = open_window("Hi.")
    window._set_busy(True)
    assert window.close() is False and told == ["Still working"]
    window._set_busy(False)
    assert window.close() is True


def test_six_limit_fields_show_and_narrow_the_stage_limits(qtbot, open_window, fake):
    window = open_window(("move_stage", {"z": 700}), "That is outside the limits you set.")
    fields = window.limit_fields
    assert fields["z", "-"].text() == "0" and fields["z", "+"].text() == "10000"  # NIS's own

    fields["z", "-"].setText("400")
    fields["z", "+"].setText("600")
    fields["x", "+"].setText("")  # empty: keep NIS's limit on that side
    window.apply_limits()
    assert fields["z", "-"].text() == "400" and fields["z", "+"].text() == "600"
    assert fields["x", "+"].text() == "57000"
    assert "Z 400 to 600" in window.transcript.toPlainText()

    ask(qtbot, window, "focus up to 700")
    assert "z = 700 um is outside the stage limits [400, 600]" in window.warning.text()
    assert moves(fake) == []

    window.use_nis_limits()
    assert fields["z", "+"].text() == "10000"


def test_limits_that_are_not_numbers_or_not_a_range_are_refused(qtbot, open_window):
    window = open_window()
    window.limit_fields["y", "-"].setText("five mm")
    window.apply_limits()
    assert window.warning.isVisibleTo(window) and "Y-: write a number" in window.warning.text()
    window.limit_fields["y", "-"].setText("600")
    window.limit_fields["y", "+"].setText("400")
    window.apply_limits()
    assert "the minimum must be below the maximum" in window.warning.text()
    assert window.assistant.microscope.engine.user_limits == {}


def test_the_limit_buttons_say_so_when_the_microscope_does_not_answer(qtbot, open_window):
    window = open_window()
    engine = window.assistant.microscope.engine
    engine.client.close()

    def no_bridge():
        raise NisConnectionError("no bridge at 127.0.0.1:54470")

    engine.reconnect = no_bridge
    window.use_nis_limits()
    assert "the microscope did not answer" in window.warning.text()
