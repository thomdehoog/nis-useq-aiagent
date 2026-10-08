"""The assistant's tools and approvals, with a scripted model in place of the real one.

``Script`` plays the model: it makes the tool calls it is given, in order, so
each test controls exactly what "the model" asks for and checks what the
microscope (the real bridge over a fake NIS) and the operator see.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

import json
import time
from pathlib import Path

import numpy as np
import pytest
import tifffile
import useq

pytest.importorskip("pydantic_ai")
pytest.importorskip("pymmcore_plus")

from nis_bridge.client import NisConnectionError
from nis_engine import NisEngine
from pydantic_ai.messages import (
    BinaryContent,
    ModelResponse,
    RetryPromptPart,
    TextPart,
    ThinkingPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models.function import FunctionModel

from nis_assistant.agent import Assistant, axes_section
from nis_assistant.eyes import Eyes, last_turns
from nis_assistant.images import as_png, binned, image_statistics
from nis_assistant.instructions import (
    CALLED_NOTHING_CHALLENGE,
    GO_AHEAD_ADVICE,
    LIMIT_ADVICE,
    OPTIONS_ADVICE,
)
from nis_assistant.models import Endpoint
from nis_assistant.settings import DEFAULT_MODEL_SETTINGS, HISTORY_KEEP_TURNS
from nis_assistant.tools import Microscope


class Script:
    """A stand-in for the model: each call returns the next step.

    A step is text (the answer), a (tool name, arguments) pair (a tool call), a
    whole ModelResponse, or an exception (the model call fails, as when the API
    is overloaded).
    """

    def __init__(self, *steps):
        self.steps = list(steps)
        self.requests = []  # what the model was sent, per call

    def __call__(self, messages, info):
        self.requests.append(messages)
        step = self.steps.pop(0)
        if isinstance(step, Exception):
            raise step
        if isinstance(step, ModelResponse):
            return step
        if isinstance(step, str):
            return ModelResponse(parts=[TextPart(step)])
        name, args = step
        return ModelResponse(parts=[ToolCallPart(name, args)])

    def model(self):
        return FunctionModel(self)


@pytest.fixture
def microscope(port, tmp_path):
    engine = NisEngine("127.0.0.1", port, timeout=5.0)
    scope = Microscope(engine, output_dir=tmp_path / "runs")
    scope.vision = False  # no vision model in most tests; those with one say so
    scope.images, scope.warnings, scope.tools = [], [], []
    scope.on_image = lambda image, caption: scope.images.append((image, caption))
    scope.on_warning = scope.warnings.append
    scope.on_tool = lambda name, args: scope.tools.append((name, args))
    yield scope
    engine.close()


def talk(microscope, *steps):
    script = Script(*steps)
    return Assistant(microscope, model=script.model()), script


def tool_results(assistant):
    return [
        part.content
        for message in assistant.history
        for part in message.parts
        if isinstance(part, ToolReturnPart)
    ]


def moves(fake):
    return [call for call in fake.calls if call.startswith("move")]


# -- reading and small actions -----------------------------------------------------


def test_every_message_carries_the_microscope_state(microscope):
    assistant, script = talk(microscope, "Hello!")
    assert assistant.send("hi") == "Hello!"
    prompt = script.requests[0][-1].parts[-1].content
    assert prompt.startswith("hi") and "<microscope_state>" in prompt and "position_um" in prompt


def test_a_quoted_state_block_is_taken_out_of_the_reply(microscope):
    quoted = 'Exposure set.\n\n<microscope_state>{"position_um": {"x": 1}}</microscope_state>'
    cut_off = 'Done. <microscope_state>{"position_um": {"x": 1'  # a block the model did not close
    assistant, _ = talk(microscope, quoted, cut_off)
    assert assistant.send("50 ms please") == "Exposure set."
    assert assistant.send("thanks") == "Done."
    assert "<microscope_state>" in assistant.history[1].parts[0].content  # its own copy stays


def test_the_model_acts_one_step_at_a_time():
    assert DEFAULT_MODEL_SETTINGS["parallel_tool_calls"] is False
    assert DEFAULT_MODEL_SETTINGS["max_tokens"] >= 16000


def test_status(microscope):
    assistant, _ = talk(microscope, ("get_status", {}), "Here is the status.")
    assistant.send("where are we?")
    status = tool_results(assistant)[0]
    assert status["position_um"] == {"x": 1000.0, "y": -500.0, "z": 500.0}
    assert "DAPI" in status["optical_configurations"]


def test_the_window_hears_of_each_tool_call(microscope):
    assistant, _ = talk(microscope, ("move_stage", {"x": 1100}), "Moved.")
    assistant.send("move a little")
    assert microscope.tools == [("move_stage", {"x": 1100})]


def test_small_move_runs_at_once(microscope, fake):
    assistant, _ = talk(microscope, ("move_stage", {"x": 1100, "z": 510}), "Moved.")
    assistant.send("move a little")
    assert moves(fake) == ["move_xyz(1100,-500,510)"]


def test_limit_breach_is_refused_with_advice_and_shown_in_the_window(microscope, fake):
    assistant, _ = talk(microscope, ("move_stage", {"z": 20000}), "That is outside the limits.")
    assistant.send("go to z 20 mm")
    error = tool_results(assistant)[0]["error"]
    assert error["code"] == "limit" and error["advice"] == LIMIT_ADVICE
    assert error["message"].startswith("z = 20000 um is outside the stage limits [0, 10000]")
    assert microscope.warnings == [error["message"]] and moves(fake) == []


# -- long moves are asked about in the chat first ------------------------------------------

LONG = ("move_stage", {"x": 20000})


def test_a_long_move_is_asked_about_in_the_chat_first(microscope, fake):
    assistant, _ = talk(microscope, LONG, "Shall I move 19 mm to x = 20 mm?", LONG, "We are there.")
    assert assistant.send("go to x 20 mm") == "Shall I move 19 mm to x = 20 mm?"
    question = tool_results(assistant)[0]
    assert question["status"] == "needs_go_ahead" and question["advice"] == GO_AHEAD_ADVICE
    assert "19000 um in XY" in question["not_done_yet"] and moves(fake) == []

    assert assistant.send("yes, go ahead") == "We are there."
    assert moves(fake) == ["move_xy(20000,-500)"]


def test_when_the_operator_says_no_nothing_moves(microscope, fake):
    assistant, _ = talk(microscope, LONG, "Shall I?", "OK, we stay here.")
    assistant.send("go to x 20 mm")
    assert assistant.send("no, stay") == "OK, we stay here." and moves(fake) == []


def test_asking_twice_in_one_turn_is_not_a_go_ahead(microscope, fake):
    assistant, _ = talk(microscope, LONG, LONG, "Shall I?")
    assistant.send("go to x 20 mm")
    assert [r["status"] for r in tool_results(assistant)] == ["needs_go_ahead"] * 2
    assert moves(fake) == []


def test_a_go_ahead_counts_only_for_the_next_message(microscope, fake):
    assistant, _ = talk(microscope, LONG, "Shall I?", "Sure.", LONG, "Shall I?")
    assistant.send("go to x 20 mm")
    assistant.send("hmm, tell me something else first")
    assistant.send("do it")  # two messages later: asked again, not moved
    assert tool_results(assistant)[-1]["status"] == "needs_go_ahead" and moves(fake) == []


def test_small_steps_that_add_up_are_asked_about_too(microscope, fake):
    steps = [("move_stage", {"z": 500 + 60 * n}) for n in (1, 2)]
    assistant, _ = talk(microscope, *steps, "Shall I go on?")
    assistant.send("walk the focus up")
    # 560 ran (60 um from where the stage was); 620 is 120 um from there, so it asks
    assert moves(fake) == ["move_z(560)"]
    assert "120 um in Z" in tool_results(assistant)[1]["not_done_yet"]


# -- settings ------------------------------------------------------------------------------


def test_settings_change_without_asking(microscope, fake):
    call = {"optical_configuration": "FITC", "exposure_ms": 20.4, "objective_slot": 4}
    assistant, _ = talk(microscope, ("set_microscope", call), "Set.")
    assistant.send("the 60x in FITC at 20 ms")
    assert tool_results(assistant)[0] == {
        "optical_configuration": "FITC",
        "objective_slot": 4,
        "exposure_ms": 20,
    }
    assert fake.nosepiece == 4


@pytest.mark.parametrize(
    ("call", "message", "options"),
    [
        (
            {"optical_configuration": "GFP"},
            "'GFP' is not an optical configuration",
            ["DAPI", "FITC", "TxRed", "Brightfield"],
        ),
        ({"objective_slot": 3}, "no objective in nosepiece slot 3", None),
        ({"exposure_ms": 1e9}, "between 0 and 60000 ms", None),
    ],
)
def test_bad_settings_are_refused_before_anything_changes(microscope, fake, call, message, options):
    assistant, _ = talk(microscope, ("set_microscope", {**call, "pfs_on": True}), "Not possible.")
    assistant.send("change it")
    error = tool_results(assistant)[0]["error"]
    assert error["code"] == "invalid" and message in error["message"] and fake.calls == []
    if options:
        assert error["configured_options"] == options and error["advice"] == OPTIONS_ADVICE


def test_an_empty_slot_refusal_lists_the_fitted_objectives(microscope):
    assistant, _ = talk(microscope, ("set_microscope", {"objective_slot": 3}), "Slot 3 is empty.")
    assistant.send("use slot 3")
    assert tool_results(assistant)[0]["error"]["configured_options"] == {
        "1": "Plan Apo 10x",
        "2": "Apo 20x WI",
        "4": "Plan Apo 60x WI",
    }


def test_a_nis_error_becomes_a_failure_with_advice(microscope, fake):
    fake.autofocus_result = 0
    assistant, _ = talk(microscope, ("focus", {"method": "image_sweep"}), "Focus failed.")
    assert assistant.send("autofocus please") == "Focus failed."
    error = tool_results(assistant)[0]["error"]
    assert error["message"] == "RuntimeError: StgFocusInRangeEx: focus not found (0)"
    assert error["code"] == "failed" and "propose one fix as a question" in error["advice"]


# -- cancelling and failing ------------------------------------------------------------------


def test_after_cancel_no_tool_does_anything(microscope, fake):
    def cancel_after_the_first_call(name, args):
        microscope.cancel.set()  # the operator presses Cancel during the first move

    microscope.on_tool = cancel_after_the_first_call
    steps = [("move_stage", {"x": 1100}), ("move_stage", {"x": 1200}), "Stopped."]
    assistant, _ = talk(microscope, *steps, ("move_stage", {"x": 1300}), "Moved.")
    assistant.send("move twice")
    assert moves(fake) == ["move_xy(1100,-500)"]
    assert tool_results(assistant)[1]["status"] == "cancelled"
    microscope.on_tool = lambda name, args: None
    assistant.send("move again")  # a new message starts without the cancel
    assert moves(fake)[-1] == "move_xy(1300,-500)"


def test_the_conversation_survives_a_model_failure_after_a_move(microscope, fake):
    overloaded = RuntimeError("API overloaded (529)")
    step = ("move_stage", {"x": 1500})
    assistant, _ = talk(microscope, step, overloaded, "We are at x 1.5 mm.")
    with pytest.raises(RuntimeError, match="overloaded"):
        assistant.send("go to x 1.5 mm")
    assert moves(fake) == ["move_xy(1500,-500)"]  # the move did happen
    assert assistant.send("are we there?") == "We are at x 1.5 mm."  # and the talk goes on
    assert tool_results(assistant)[0]["x"] == 1500  # the model got the move's result


# -- focus and vision -----------------------------------------------------------------


def test_pfs_focus_leaves_the_pfs_as_it_was(microscope, fake):
    assistant, _ = talk(microscope, ("focus", {"method": "pfs"}), "In focus.")
    assistant.send("focus")
    assert tool_results(assistant)[0] == {
        "focused": True,
        "z_before_um": 500.0,
        "z_after_um": 502.0,
    }
    assert fake.pfs_on is False


@pytest.mark.parametrize(
    ("z", "range_um", "code", "message"),
    [
        (500, 500, "invalid", "between 0 and 100 um"),
        (9980, 100, "limit", "a 100 um sweep around z = 9980 um would leave the Z limits"),
    ],
)
def test_focus_sweep_is_small_and_inside_the_limits(microscope, fake, z, range_um, code, message):
    fake.position["z"] = z
    call = {"method": "image_sweep", "range_um": range_um}
    assistant, _ = talk(microscope, ("focus", call), "Refused.")
    assistant.send("find focus")
    error = tool_results(assistant)[0]["error"]
    assert error["code"] == code and message in error["message"]
    assert not any("autofocus" in c for c in fake.calls)


def test_look_shows_the_image_and_asks_a_vision_model(microscope):
    vision = Script("A uniform field with no visible structures.")
    microscope.vision_model, microscope.vision = vision.model(), True
    assistant, _ = talk(microscope, ("look", {"question": "what do you see?"}), "Nothing yet.")
    assistant.send("look at the sample")

    result = tool_results(assistant)[0]
    assert result["answer"] == "A uniform field with no visible structures."
    assert result["statistics"]["saturated_percent"] == 0.0
    image, caption = microscope.images[0]
    assert image.shape == (48, 64) and caption == "what do you see?"
    # the vision model got the question, the measurements and a PNG
    question, png = vision.requests[0][-1].parts[-1].content
    assert "what do you see?" in question and "sharpness" in question
    assert png.media_type == "image/png"


def test_the_eyes_remember_earlier_images(microscope, fake):
    vision = Script("Three spots.", "The same three spots as in image 1; nothing moved.")
    microscope.vision_model, microscope.vision = vision.model(), True
    look = ("look", {"question": "what do you see?"})
    again = ("look", {"question": "has anything changed since the image before?"})
    assistant, _ = talk(microscope, look, again, "Nothing moved.")
    assistant.send("look twice and compare")
    first, second = tool_results(assistant)
    assert first["images_seen"] == 1 and second["images_seen"] == 2
    assert second["answer"].startswith("The same three spots")
    # the second request to the eyes carries the first image's turn and its answer
    history = vision.requests[1]
    texts = [
        p.content for m in history for p in m.parts if isinstance(p, (UserPromptPart, TextPart))
    ]
    assert any(t == "Three spots." for t in texts)
    prompt = history[-1].parts[-1].content[0]
    assert prompt.startswith("Image 2,") and "position_um" in prompt and "objective" in prompt
    assert fake.captures == 2


def picture(row, col):
    """A camera image with one bright spot, for the fake camera to show."""
    rows, cols = np.mgrid[0:48, 0:64]
    image = np.full((48, 64), 100.0)
    image[(rows - row) ** 2 + (cols - col) ** 2 <= 5**2] = 4000
    return image.astype(np.uint16)


def test_a_look_over_earlier_images_measures_the_drift(microscope, fake):
    fake.calibrated = True  # 0.108 um per pixel
    vision = Script("One spot.", "The spot moved a little to the right.")
    microscope.vision_model, microscope.vision = vision.model(), True
    fake.frame = picture(24, 30)
    first = ("look", {"question": "what do you see?", "label": "before"})
    assistant, _ = talk(microscope, first, "A spot.")
    assistant.send("look and label it 'before'")
    fake.frame = picture(24, 36)  # the sample drifts 6 pixels to the right
    again = ("look", {"question": "has it drifted since 'before'?", "frames": "1"})
    assistant, script = talk(microscope, again, "It drifted 0.6 um to the right.")
    assistant.send("has it drifted?")
    result = tool_results(assistant)[0]
    assert [i["n"] for i in result["images"]] == [1, 2] and result["images"][0]["label"] == "before"
    (change,) = result["changes"]
    shift = change["since_first"]["image_shift_um"]
    assert shift["right"] == pytest.approx(6 * 0.108, abs=0.1) and abs(shift["up"]) < 0.1
    assert result["answer"].startswith("The spot moved")
    # the eyes were shown both images, oldest first, then the question
    content = vision.requests[1][-1].parts[-1].content
    texts = [c for c in content if isinstance(c, str)]
    assert texts[1].startswith("Image 1,") and "labelled 'before'" in texts[1]
    assert (
        texts[2].startswith("Image 2,") and texts[-1] == "Question: has it drifted since 'before'?"
    )
    assert sum(isinstance(c, BinaryContent) for c in content) == 2
    # the state carries the images in brief, and the map with the labelled place
    assistant, script = talk(microscope, "Yes.")
    assistant.send("ok")
    state = state_sent(script)
    assert state["frames"]["count"] == 2 and state["frames"]["labels"] == {"before": 1}
    assert state["map"]["labels"]["before"]["x"] == 1000.0
    assert state["map"]["objectives"][0]["objective"] == "Plan Apo 10x"


def test_a_look_without_a_new_image_shows_the_kept_ones(microscope, fake):
    microscope.vision = False
    assistant, _ = talk(microscope, ("look", {"question": "what?", "snap": False}), "Nothing yet.")
    assistant.send("show me")
    assert "no image has been taken" in tool_results(assistant)[0]["error"]["message"]
    steps = [
        ("look", {"question": "what?"}),
        ("look", {"question": "again?", "snap": False}),
        "Ok.",
    ]
    assistant, _ = talk(microscope, *steps)
    assistant.send("look, then look at it again")
    fresh, kept = tool_results(assistant)
    assert fresh["image"]["n"] == 1 and kept["image"]["n"] == 1 and "statistics" not in kept
    assert fake.captures == 1  # the second look took no image
    # "last 1" with a new image means the one taken before it, compared with the new one
    assistant, _ = talk(microscope, ("look", {"question": "?", "frames": "last 1"}), "Ok.")
    assistant.send("look again and compare")
    compared = tool_results(assistant)[0]
    assert [i["n"] for i in compared["images"]] == [1, 2] and compared["changes"][0]["n"] == 2
    assistant, _ = talk(microscope, ("look", {"question": "what?", "frames": "7"}), "No.")
    assistant.send("show image 7")
    assert "no image 7" in tool_results(assistant)[0]["error"]["message"]


def test_the_last_image_of_a_run_is_kept_and_can_be_looked_at_during_a_run(
    microscope, slow_camera, monkeypatch
):
    from nis_assistant import tools as tools_module

    monkeypatch.setattr(tools_module, "RUN_HOLD_S", 0.2)
    microscope.vision = False
    steps = [
        ("plan_acquisition", LAPSE),
        "Start?",
        RUN_LAPSE,
        ("look", {"question": "what?"}),  # a new image: the camera is the run's
        ("look", {"question": "what?", "snap": False}),  # kept images: fine
        "Running.",
    ]
    assistant, _ = talk(microscope, *steps)
    assistant.send("6 time points")
    assistant.send("yes")
    refused, kept = tool_results(assistant)[-2:]
    assert (
        refused["error"]["code"] == "busy" and "no image has been taken" in kept["error"]["message"]
    )
    microscope.run.finished.wait(10)
    microscope.settle_run()
    assert microscope.run.result["last_image_number"] == 1
    assert microscope.frames.frames[0]["source"] == "run stack_test-1"
    assert microscope.frames.frames[0]["position_um"]["x"] == 100.0


def test_ask_eyes_asks_about_the_images_seen_without_a_new_one(microscope, fake):
    vision = Script("Three spots.", "Still three; nothing has moved.")
    microscope.vision_model, microscope.vision = vision.model(), True
    steps = [
        ("look", {"question": "what do you see?"}),
        ("ask_eyes", {"question": "has the sample moved?"}),
        "No.",
    ]
    assistant, _ = talk(microscope, *steps)
    assistant.send("look, then tell me whether it moved")
    asked = tool_results(assistant)[1]
    assert asked["answer"] == "Still three; nothing has moved." and asked["images_seen"] == 1
    assert fake.captures == 1  # no new image for the question
    assert vision.requests[1][-1].parts[-1].content.startswith("No new image.")


def test_ask_eyes_before_any_look_says_so(microscope):
    vision = Script()
    microscope.vision_model, microscope.vision = vision.model(), True
    assistant, _ = talk(microscope, ("ask_eyes", {"question": "anything?"}), "Look first.")
    assistant.send("what did you see?")
    assert "look first" in tool_results(assistant)[0]["answer"] and vision.requests == []


def test_older_images_are_detached_but_their_words_stay(microscope):
    vision = Script("One.", "Two.", "Three.")
    microscope.vision_model, microscope.vision = vision.model(), True
    microscope.eyes = Eyes(vision.model(), frames_kept=1)
    look = ("look", {"question": "what?"})
    assistant, _ = talk(microscope, look, look, look, "Done.")
    assistant.send("look three times")
    turns = [m for m in microscope.eyes._history if isinstance(m.parts[0], UserPromptPart)]
    assert len(turns) == 3
    with_image = [any(isinstance(c, BinaryContent) for c in t.parts[0].content) for t in turns]
    assert with_image == [False, False, True]  # only the newest keeps its picture
    assert "[image no longer attached]" in turns[0].parts[0].content
    assert "Image 1," in turns[0].parts[0].content[0]  # the words stay


def test_the_eyes_see_the_last_image_of_a_run_and_forget_on_clear(microscope, fake):
    vision = Script("A dim, even field.")
    microscope.vision_model, microscope.vision = vision.model(), True
    steps = [("plan_acquisition", PLAN), RUN, "Start?", RUN, "Saved."]
    assistant, _ = talk(microscope, *steps)
    assistant.send("take a stack at a")
    assistant.send("yes")
    assert microscope.eyes.frames == 1
    assistant.clear()
    assert microscope.eyes.frames == 0 and microscope.eyes._history == []


def test_the_eyes_keep_only_the_last_so_many_looks(microscope):
    vision = Script("One.", "Two.", "Three.")
    microscope.vision_model, microscope.vision = vision.model(), True
    microscope.eyes = Eyes(vision.model(), turns_kept=2)
    look = ("look", {"question": "what?"})
    assistant, _ = talk(microscope, look, look, look, "Done.")
    assistant.send("look three times")
    turns = [m for m in microscope.eyes._history if isinstance(m.parts[0], UserPromptPart)]
    assert len(turns) == 2 and "Image 2," in turns[0].parts[0].content[0]
    assert last_turns([], 3) == []


def test_a_failing_vision_model_is_reported_and_the_image_not_counted(microscope, fake):
    vision = Script(RuntimeError("the vision model is down"))
    microscope.vision_model, microscope.vision = vision.model(), True
    assistant, _ = talk(microscope, ("look", {"question": "what?"}), "Sorry.")
    assistant.send("look")
    result = tool_results(assistant)[0]
    assert (
        result["error"]["code"] == "failed" and "vision model is down" in result["error"]["message"]
    )
    assert microscope.eyes.frames == 0 and fake.captures == 1
    # the last image of a run: the run is not turned into a failure by the describing
    vision = Script(RuntimeError("still down"))
    microscope.vision_model = vision.model()
    steps = [("plan_acquisition", PLAN), RUN, "Start?", RUN, "Saved."]
    assistant, _ = talk(microscope, *steps)
    assistant.send("take a stack at a")
    assistant.send("yes")
    run = tool_results(assistant)[-1]
    assert run["finished"] == "completed" and "still down" in run["last_image"]["vision_error"]


def test_ask_eyes_with_a_model_that_cannot_see(microscope):
    microscope.vision = False
    assistant, _ = talk(microscope, ("ask_eyes", {"question": "anything?"}), "No.")
    assistant.send("what did you see?")
    assert "cannot see" in tool_results(assistant)[0]["note"]


def test_changing_the_vision_model_gives_new_eyes(microscope):
    first, second = Script("One."), Script("Two.")
    microscope.vision_model, microscope.vision = first.model(), True
    assistant, _ = talk(microscope, ("look", {"question": "what?"}), "Done.")
    assistant.send("look")
    assert microscope.eyes.frames == 1
    microscope.vision_model = second.model()  # as Assistant.use does
    assert microscope.eyes.frames == 0 and microscope.eyes.model is microscope.vision_model


def test_a_model_that_cannot_see_gets_the_numbers_only(microscope):
    microscope.vision = False
    assistant, _ = talk(microscope, ("look", {"question": "what do you see?"}), "Dark.")
    assistant.send("look")
    result = tool_results(assistant)[0]
    assert "answer" not in result and "cannot see" in result["note"]
    assert result["statistics"]["max"] >= 0 and len(microscope.images) == 1


def test_binning_averages_blocks():
    image = np.arange(16, dtype=np.float64).reshape(4, 4)
    small = binned(image, 2)
    assert small.shape == (2, 2) and small[0, 0] == np.mean([0, 1, 4, 5])
    assert binned(image[:3, :3], 2).shape == (1, 1)  # the ragged edge is dropped
    assert binned(np.zeros((4, 4, 3)), 2).shape == (2, 2, 3)  # colour keeps its planes


# -- the coordinate system ---------------------------------------------------------------


def test_the_model_is_told_the_coordinate_system(microscope):
    assistant, script = talk(microscope, "Hello!")
    assistant.send("hi")
    told = script.requests[0][-1].instructions
    assert "right is +x and left is -x; up is +y and down is -y" in told
    assert "deeper into the sample is +z and toward the coverslip is -z" in told
    microscope.axes = {"x": "left", "y": "down", "z": "toward the coverslip"}
    assistant, script = talk(microscope, "Hello again!")
    assistant.send("hi")
    told = script.requests[0][-1].instructions
    assert "left is +x and right is -x; down is +y and up is -y" in told
    assert "toward the coverslip is +z and deeper into the sample is -z" in told


def test_a_missing_or_unknown_axis_choice_takes_the_default():
    told = axes_section({"y": "down", "z": "sideways"})
    assert "right is +x" in told and "down is +y" in told and "deeper into the sample is +z" in told


# -- schedules ---------------------------------------------------------------------------


def test_a_schedule_is_set_and_shows_in_the_state(microscope):
    steps = [
        ("schedule", {"name": "watch", "instruction": "look", "every_seconds": 180}),
        "Every three minutes.",
        "Hello.",
    ]
    assistant, script = talk(microscope, *steps)
    assistant.send("look every three minutes")
    result = tool_results(assistant)[0]
    assert result["scheduled"]["name"] == "watch" and result["scheduled"]["every_seconds"] == 180
    assert "watch" in [s["name"] for s in microscope.scheduler.listing()]
    assistant.send("hi")
    state = json.loads(
        script.requests[-1][-1]
        .parts[-1]
        .content.split("<microscope_state>")[1][: -len("</microscope_state>")]
    )
    assert state["schedules"][0]["name"] == "watch" and len(state["clock"]) == 8


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ({"name": "x", "instruction": "look", "every_seconds": 1}, "at least"),
        ({"name": "x", "instruction": "look"}, "exactly one of"),
        ({"name": "x", "instruction": "look", "at": "25:99"}, "HH:MM"),
    ],
)
def test_a_bad_schedule_is_refused_with_the_reason(microscope, args, message):
    assistant, _ = talk(microscope, ("schedule", args), "Refused.")
    assistant.send("later")
    error = tool_results(assistant)[0]["error"]
    assert error["code"] == "invalid" and message in error["message"]
    assert microscope.scheduler.listing() == []


def test_cancel_schedule_by_name_and_an_unknown_name_lists_the_known(microscope):
    microscope.scheduler.add("watch", "look", every_seconds=60)
    assistant, _ = talk(microscope, ("cancel_schedule", {"name": "nope"}), "Which one?")
    assistant.send("cancel it")
    error = tool_results(assistant)[0]["error"]
    assert error["code"] == "invalid" and error["configured_options"] == ["watch"]
    assistant, _ = talk(microscope, ("cancel_schedule", {"name": "watch"}), "Cancelled.")
    assistant.send("cancel the watch")
    assert (
        tool_results(assistant)[0]["cancelled"] == ["watch"] and not microscope.scheduler.listing()
    )


def test_a_scheduled_turn_is_not_the_operators(microscope, fake):
    # A scheduled move does not move the anchor, so repeated small steps still add up
    # to a question; and it does not count as the reply to a pending question.
    assistant, _ = talk(microscope, ("move_stage", {"x": 1600}), "Moved.")
    assistant.send("move x to 1600")
    step = ("move_stage", {"x": 2200})
    assistant, _ = talk(microscope, step, "Shall I?", step, "Shall I?")
    assistant.send("[scheduled 'creep'] move x 600 further", scheduled=True)
    assert tool_results(assistant)[-1]["status"] == "needs_go_ahead"
    assistant.send("[scheduled 'creep'] move x 600 further", scheduled=True)
    assert tool_results(assistant)[-1]["status"] == "needs_go_ahead"
    assert moves(fake) == ["move_xy(1600,-500)"]
    assert microscope.turn == 1  # scheduled turns do not count as the operator's


def test_stop_and_clear_drop_every_schedule(microscope):
    microscope.scheduler.add("watch", "look", every_seconds=60)
    microscope.stop()
    assert microscope.scheduler.listing() == []
    microscope.scheduler.add("watch", "look", every_seconds=60)
    Assistant(microscope).clear()
    assert microscope.scheduler.listing() == []


# -- checking the setup ---------------------------------------------------------------


def test_check_setup_reports_a_running_bridge_and_its_configurations(microscope):
    assistant, _ = talk(microscope, ("check_setup", {}), "All good.")
    assistant.send("is everything set up?")
    result = tool_results(assistant)[0]
    assert result["bridge"] == "running" and result["optical_configurations"]
    assert "steps_for_the_operator" not in result


def test_check_setup_walks_through_adding_an_optical_configuration(microscope, fake):
    fake.configurations.clear()
    assistant, _ = talk(microscope, ("check_setup", {}), "Add one first.")
    assistant.send("image in DAPI")
    result = tool_results(assistant)[0]
    assert result["optical_configurations"] == [] and "no optical configuration" in result["note"]
    assert "New Optical Configuration" in " ".join(result["steps_for_the_operator"])


def test_check_setup_says_how_to_start_a_missing_bridge(microscope, tmp_path, monkeypatch):
    from nis_assistant import tools as tools_module

    # The bridge went away: the connection is closed and cannot be made again.
    microscope.engine.client.close()

    def no_bridge():
        raise NisConnectionError("no bridge at 127.0.0.1:54468")

    monkeypatch.setattr(microscope.engine, "reconnect", no_bridge)
    monkeypatch.setattr(tools_module, "MACRO", tmp_path / "start_bridge.mac")
    assistant, script = talk(microscope, ("check_setup", {}), "Start the bridge first.")
    assert assistant.send("where is the stage?") == "Start the bridge first."
    # the model was told the microscope does not answer, not shown an error
    assert "not answering" in script.requests[0][0].parts[0].content
    result = tool_results(assistant)[0]
    assert result["bridge"] == "not answering"
    steps = " ".join(result["steps_for_the_operator"])
    assert "install_macros" in steps and "Run Macro From File" in steps
    (tmp_path / "start_bridge.mac").write_text("")
    assistant, _ = talk(microscope, ("check_setup", {}), "Start it.")
    assistant.send("hello")
    steps = " ".join(tool_results(assistant)[0]["steps_for_the_operator"])
    assert str(tmp_path / "start_bridge.mac") in steps and "install_macros" not in steps


def test_a_camera_failure_is_reported_with_advice(microscope, fake):
    fake.camera_fails = True
    assistant, _ = talk(microscope, ("look", {"question": "what do you see?"}), "No image.")
    assistant.send("look")
    error = tool_results(assistant)[0]["error"]
    assert "camera did not answer" in error["message"] and error["code"] == "failed"


@pytest.mark.parametrize("shape", [(2000, 1000), (300, 200, 3)], ids=["mono", "colour"])
def test_image_statistics_and_png(shape):
    image = np.zeros(shape, dtype=np.uint16)
    image[:10, :10] = 65535
    stats = image_statistics(image)
    assert stats["max"] == 65535 and stats["saturated_percent"] > 0
    assert as_png(image).media_type == "image/png"


# -- guards on the reply ---------------------------------------------------------------


def test_an_empty_reply_is_handed_back_once(microscope):
    assistant, script = talk(microscope, "_", "The stage is at x 0.")
    assert assistant.send("where?") == "The stage is at x 0."
    challenge = script.requests[1][-1].parts[-1].content
    assert "empty" in challenge
    assistant, _ = talk(microscope, "_", "...")  # empty twice: a plain fallback line
    assert "no answer in words" in assistant.send("where?")


def test_a_reply_that_called_nothing_is_challenged_when_asked(microscope):
    microscope.challenge_no_tool = True
    # the model claims to have acted; challenged, it does act, and its new reply is the answer
    assistant, script = talk(
        microscope, "I moved the stage.", ("get_status", {}), "Here is the status."
    )
    assert assistant.send("status") == "Here is the status."
    assert "No tool was called" in script.requests[1][-1].parts[-1].content
    # challenged and still nothing to call: the first reply reaches the operator as it was
    assistant, _ = talk(microscope, "Hello, how can I help?", "SAME")
    assert assistant.send("hi") == "Hello, how can I help?"
    # the "SAME" exchange is not kept: the next turn's model sees only the first reply
    assistant, script = talk(microscope, "Hello.", "SAME", "You can image.", "SAME")
    assert assistant.send("hi") == "Hello."
    assert [type(m).__name__ for m in assistant.history] == ["ModelRequest", "ModelResponse"]
    assert assistant.send("what can I do?") == "You can image."
    seen = [part for message in script.requests[2] for part in message.parts]
    assert not any(isinstance(p, RetryPromptPart) for p in seen)
    assert "SAME" not in str([getattr(p, "content", "") for p in seen])
    # a reply that opens with the guard's word, or echoes the challenge, is not passed on
    assistant, _ = talk(microscope, "SAME\nHello.", "SAME")
    assert assistant.send("hi") == "Hello."
    assistant, _ = talk(microscope, "SAME", "Hello.", "SAME")
    assert assistant.send("hi") == "Hello."
    echoed = "Validation feedback:\n" + CALLED_NOTHING_CHALLENGE
    assistant, _ = talk(microscope, echoed, "Hi.", "SAME")
    assert assistant.send("hi") == "Hi."
    # a challenge that led to a tool call stays in the history
    assistant, _ = talk(microscope, "I moved it.", ("get_status", {}), "Here is the status.")
    assistant.send("status")
    assert any(isinstance(p, RetryPromptPart) for m in assistant.history for p in m.parts)
    # off by default: no challenge, one request
    microscope.challenge_no_tool = False
    assistant, script = talk(microscope, "Hello.")
    assert assistant.send("hi") == "Hello." and len(script.requests) == 1


def test_use_switches_the_model_and_its_settings(microscope):
    assistant = Assistant(microscope)
    assert assistant.model_settings is DEFAULT_MODEL_SETTINGS
    assistant.use(Endpoint.from_preset("Gemini", api_key="k"))
    assert type(assistant.model).__name__ == "GoogleModel"
    assert assistant.model_settings["temperature"] == 0.0 and microscope.vision
    assert microscope.vision_model is assistant.model
    server = Endpoint.from_preset("OpenAI-style server")
    assistant.use(Endpoint.from_preset("OpenAI", api_key="k"), vision=server)
    assert type(microscope.vision_model).__name__ == "OpenAIChatModel" and not microscope.vision


# -- planning and running an acquisition ----------------------------------------------


PLAN = {  # the flat form, as the model sends it
    "name": "stack_test",
    "positions": [{"x": 100, "y": 200, "z": 500, "name": "a"}],
    "channels": [{"config": "DAPI", "exposure_ms": 20}, {"config": "FITC"}],
    "z_stack": {"range_um": 2, "step_um": 1},
}
RUN = ("run_acquisition", {"plan_id": "stack_test-1"})


def test_an_acquisition_starts_only_after_the_operator_saw_the_plan(microscope, fake):
    microscope.vision_model, microscope.vision = Script("A dim, even field.").model(), True
    steps = [("plan_acquisition", PLAN), RUN, "Shall I start these 6 images?", RUN, "Saved."]
    assistant, _ = talk(microscope, *steps)
    assert assistant.send("take a two-channel stack at a") == "Shall I start these 6 images?"
    plan, question = tool_results(assistant)
    assert plan["plan_id"] == "stack_test-1" and plan["images"] == 6
    assert "a at x 100, y 200, z 500 um" in plan["summary"] and "900 um in XY" in plan["summary"]
    assert question["status"] == "needs_go_ahead" and "6 images" in question["not_done_yet"]
    assert fake.captures == 0 and moves(fake) == []  # nothing happened yet

    assert assistant.send("yes, start") == "Saved."
    run = tool_results(assistant)[-1]
    assert run["images"] == 6 and run["finished"] == "completed"
    assert tifffile.imread(run["saved_to"]).shape == (2, 3, 48, 64)
    assert list(microscope.output_dir.glob("*.useq.json")) and len(microscope.images) == 6
    # the last image was described, so the reply can say what was imaged
    assert run["last_image"]["description"] == "A dim, even field."
    assert run["last_image"]["statistics"]["max"] >= 0


def test_a_model_that_cannot_see_gets_the_last_image_numbers_only(microscope, fake):
    microscope.vision = False
    steps = [("plan_acquisition", PLAN), RUN, "Start?", RUN, "Saved."]
    assistant, _ = talk(microscope, *steps)
    assistant.send("take a stack at a")
    assistant.send("yes")
    last = tool_results(assistant)[-1]["last_image"]
    assert "description" not in last and "cannot see" in last["note"]


def test_the_plan_comes_back_as_a_useq_sequence(microscope):
    assistant, _ = talk(microscope, ("plan_acquisition", PLAN), "Here is the plan.")
    assistant.send("plan a stack at a")
    sequence = useq.MDASequence(**tool_results(assistant)[0]["useq_sequence"])
    assert len(list(sequence)) == 6 and sequence.channels[0].config == "DAPI"


def test_a_plan_the_operator_declines_is_not_run(microscope, fake):
    steps = [("plan_acquisition", PLAN), RUN, "Shall I start?", "OK, not now."]
    assistant, _ = talk(microscope, *steps)
    assistant.send("take a stack")
    assistant.send("no")
    assert fake.captures == 0 and not microscope.output_dir.exists()


def test_a_plan_from_earlier_in_the_conversation_is_asked_about_again(microscope, fake):
    steps = [
        ("plan_acquisition", PLAN),
        "Shall I start?",
        "OK, not now.",
        RUN,
        "Shall I start it now?",
    ]
    assistant, _ = talk(microscope, *steps)
    assistant.send("plan a stack at a")
    assistant.send("no, later")
    assistant.send("run it now")  # the plan is two messages old: a new question, no run
    assert tool_results(assistant)[-1]["status"] == "needs_go_ahead" and fake.captures == 0


def test_the_saved_sequence_is_written_as_utf8(microscope, monkeypatch):
    """Windows would otherwise write it in its own encoding, which useq cannot read back."""
    encodings, real_write = [], Path.write_text

    def write_text(self, data, **kwargs):
        encodings.append(kwargs.get("encoding"))
        return real_write(self, data, **kwargs)

    monkeypatch.setattr(Path, "write_text", write_text)
    named = {**PLAN, "positions": [{"x": 100, "y": 200, "z": 500, "name": "Zürich_Δ"}]}
    steps = [("plan_acquisition", named), "Shall I start?", RUN, "Saved."]
    assistant, _ = talk(microscope, *steps)
    assistant.send("a stack")
    assistant.send("yes")
    (saved,) = microscope.output_dir.glob("*.useq.json")
    assert encodings == ["utf-8"]
    assert useq.MDASequence.from_file(saved).stage_positions[0].name == "Zürich_Δ"


def test_a_far_away_plan_says_so(microscope):
    far = {**PLAN, "positions": [{"x": 50000, "y": 30000, "z": 900}]}
    assistant, _ = talk(microscope, ("plan_acquisition", far), "Shall I? It is far.")
    assistant.send("image over there")
    summary = tool_results(assistant)[0]["summary"]
    assert "49000 um in XY and 401 um in Z" in summary and "This includes a long move." in summary


def test_the_run_images_exactly_the_planned_positions(microscope, fake):
    here = {**PLAN, "positions": []}  # "here" is fixed when the plan is made
    steps = [
        ("plan_acquisition", here),
        ("move_stage", {"x": 1100}),
        "Shall I start?",
        RUN,
        "Done.",
    ]
    assistant, _ = talk(microscope, *steps)
    assistant.send("stack here")
    assert "here at x 1000, y -500, z 500 um" in tool_results(assistant)[0]["summary"]
    assistant.send("yes")
    assert fake.position["x"] == 1000.0  # imaged at the planned x, not where the stage went


def test_a_tiled_plan_measures_the_field_and_makes_a_useq_grid(microscope, fake):
    fake.calibrated = True  # 0.108 um per pixel, 64 x 48 pixels
    tiled = {**PLAN, "z_stack": None, "grid": {"rows": 2, "columns": 3, "overlap_percent": 10}}
    assistant, _ = talk(microscope, ("plan_acquisition", tiled), "Shall I start?")
    assistant.send("tile around a")
    plan = tool_results(assistant)[0]
    grid = plan["useq_sequence"]["grid_plan"]
    assert (grid["rows"], grid["columns"]) == (2, 3) and grid["fov_width"] == pytest.approx(6.912)
    assert plan["images"] == 12 and "each as 2 x 3 tiles" in plan["summary"]
    assert fake.captures == 1 and moves(fake) == []  # one image to measure the field, no move


def test_a_run_over_several_positions_is_saved_as_a_folder(microscope, fake):
    fake.calibrated = True
    tiled = {**PLAN, "z_stack": None, "grid": {"rows": 1, "columns": 2}}
    steps = [("plan_acquisition", tiled), "Shall I start?", RUN, "Saved."]
    assistant, _ = talk(microscope, *steps)
    assistant.send("two tiles at a")
    assistant.send("yes")
    folder = Path(tool_results(assistant)[-1]["saved_to"])
    assert folder.is_dir() and len(list(folder.glob("*.ome.tiff"))) == 2


def test_a_grid_without_a_pixel_calibration_is_refused(microscope):
    tiled = {**PLAN, "grid": {"rows": 2, "columns": 2}}
    assistant, _ = talk(microscope, ("plan_acquisition", tiled), "The objective is not calibrated.")
    assistant.send("tile it")
    assert "no pixel calibration" in tool_results(assistant)[0]["error"]["message"]


def test_channels_can_skip_the_stack_and_time_points(microscope):
    plan = {
        **PLAN,
        "channels": [
            {"config": "DAPI"},
            {"config": "Brightfield", "do_stack": False},
            {"config": "FITC", "acquire_every": 2, "z_offset_um": 1.5},
        ],
        "time_points": 2,
        "interval_s": 5,
    }
    assistant, _ = talk(microscope, ("plan_acquisition", plan), "Shall I start?")
    assistant.send("plan it")
    result = tool_results(assistant)[0]
    # per time point: DAPI 3 planes + Brightfield 1; FITC 3 planes at the first only
    assert result["images"] == 2 * (3 + 1) + 3
    assert "Brightfield (one plane)" in result["summary"]
    assert "FITC (every 2 time points, +1.5 um in z)" in result["summary"]
    assert "2 time points 5 s apart" in result["summary"]


SEQUENCE = {  # a classic useq MDASequence, as another useq tool would save it
    "stage_positions": [{"x": 1200, "y": -500, "z": 500, "name": "cell"}],
    "channels": [{"config": "DAPI", "exposure": 30}, {"config": "TxRed"}],
    "z_plan": {"range": 4, "step": 2},
}


def test_a_useq_file_from_elsewhere_is_checked_and_run(microscope, fake, tmp_path):
    path = tmp_path / "from_widgets.json"
    path.write_text(json.dumps(SEQUENCE))
    call = ("plan_useq_sequence", {"name": "widgets", "path": str(path)})
    run = ("run_acquisition", {"plan_id": "widgets-1"})
    assistant, _ = talk(microscope, call, "Shall I start?", run, "Saved.")
    assistant.send(f"run the sequence in {path}")
    plan = tool_results(assistant)[0]
    assert plan["images"] == 6 and "cell at x 1200, y -500, z 500 um" in plan["summary"]
    assert fake.captures == 0  # nothing starts before the operator agrees

    assistant.send("yes")
    run_result = tool_results(assistant)[-1]
    assert tifffile.imread(run_result["saved_to"]).shape == (2, 3, 48, 64)
    (saved,) = microscope.output_dir.glob("*.useq.json")
    assert useq.MDASequence.from_file(saved) == useq.MDASequence(**SEQUENCE)


def test_a_useq_sequence_without_positions_is_imaged_here(microscope):
    inline = {"channels": [{"config": "FITC"}]}
    call = ("plan_useq_sequence", {"name": "inline", "sequence": inline})
    assistant, _ = talk(microscope, call, "Shall I start?")
    assistant.send("run this sequence")
    assert "here at x 1000, y -500, z 500 um" in tool_results(assistant)[0]["summary"]


@pytest.mark.parametrize(
    "args",
    [{"path": "no/such/file.json"}, {"sequence": {"channels": "not a list"}}],
    ids=["missing file", "not a sequence"],
)
def test_an_unreadable_useq_sequence_is_refused(microscope, args):
    call = ("plan_useq_sequence", {"name": "bad", **args})
    assistant, _ = talk(microscope, call, "That did not work.")
    assistant.send("run it")
    error = tool_results(assistant)[0]["error"]
    assert error["code"] == "invalid" and "no useq sequence could be read" in error["message"]


def test_plan_with_a_problem_is_refused_before_anything_moves(microscope, fake):
    bad = {**PLAN, "positions": [{"x": 100, "y": 200, "z": 20000}]}
    assistant, _ = talk(microscope, ("plan_acquisition", bad), "That plan cannot run.")
    assistant.send("plan it")
    error = tool_results(assistant)[0]["error"]
    assert error["code"] == "limit" and "outside the stage limits" in error["message"]
    assert microscope.warnings and moves(fake) == [] and fake.captures == 0


def test_repeated_position_names_are_refused_when_planning(microscope):
    twice = {**PLAN, "positions": [{"x": 100, "y": 200, "z": 500, "name": "cell"}] * 2}
    assistant, _ = talk(microscope, ("plan_acquisition", twice), "Two positions share a name.")
    assistant.send("plan it")
    assert "used more than once: cell" in tool_results(assistant)[0]["error"]["message"]


def test_a_sequence_whose_positions_have_only_z(microscope):
    call = ("plan_useq_sequence", {"name": "z_only", "sequence": {"stage_positions": [{"z": 500}]}})
    assistant, _ = talk(microscope, call, "Planned.")
    assistant.send("plan it")
    assert "#1 at z 500 um" in tool_results(assistant)[0]["summary"]


def test_a_useq_v2_sequence_as_json_is_refused_clearly(microscope):
    v2_json = {"axes": [{"axis_key": "c", "values": []}]}
    call = ("plan_useq_sequence", {"name": "v2", "sequence": v2_json})
    assistant, _ = talk(microscope, call, "That is a v2 sequence.")
    assistant.send("run it")
    assert "useq v2 sequence" in tool_results(assistant)[0]["error"]["message"]


def test_a_plan_that_became_invalid_before_its_run_is_refused_with_the_limit(microscope, fake):
    steps = [("plan_acquisition", PLAN), "Shall I start?", RUN, "The plan is outside the limits."]
    assistant, _ = talk(microscope, *steps)
    assistant.send("a stack at a")
    microscope.engine.set_limits(x=(500, None))  # the operator narrows the limits meanwhile
    assistant.send("yes")
    assert tool_results(assistant)[-1]["error"]["code"] == "limit" and microscope.warnings
    assert fake.captures == 0


def test_stop_while_a_run_is_being_prepared_prevents_it(microscope, fake):
    real_check = microscope.engine.check

    def check_then_stop(sequence):
        events = real_check(sequence)
        microscope.stop()  # the operator presses Stop microscope during the check
        return events

    steps = [("plan_acquisition", PLAN), "Shall I start?", RUN, "Stopped."]
    assistant, _ = talk(microscope, *steps)
    assistant.send("a stack at a")
    microscope.engine.check = check_then_stop
    assistant.send("yes")
    assert tool_results(assistant)[-1]["status"] == "cancelled" and fake.captures == 0


def test_a_run_that_loses_the_connection_says_what_was_saved(microscope, fake):
    steps = [("plan_acquisition", PLAN), "Shall I start?", RUN, "The connection was lost."]
    assistant, _ = talk(microscope, *steps)
    assistant.send("a stack at a")
    real_request, snaps = microscope.engine.client.request, []

    def request(op, **args):
        snaps.extend([op] if op == "snap" else [])
        if len(snaps) >= 4:  # the size check and two images, then NIS stops answering
            raise NisConnectionError("connection lost during 'snap'")
        return real_request(op, **args)

    microscope.engine.client.request = request
    assistant.send("yes")
    result = tool_results(assistant)[-1]
    assert result["finished"] == "failed" and "connection lost" in result["error"]["message"]
    assert result["images"] == 2 and result["saved_to"]


# -- a run that takes longer than one turn --------------------------------------------------

LAPSE = {**PLAN, "z_stack": None, "channels": [{"config": "DAPI"}], "time_points": 6}
RUN_LAPSE = ("run_acquisition", {"plan_id": "stack_test-1"})


@pytest.fixture
def slow_camera(fake):
    """A camera that takes a while per image, so a run outlasts the turn's hold."""
    import time as _time

    real_capture = fake.capture

    def capture():
        _time.sleep(0.15)
        real_capture()

    fake.capture = capture
    return fake


def state_sent(script, call=-1):
    """The <microscope_state> the model was sent with the latest message of a call."""
    prompts = [
        part.content
        for message in script.requests[call]
        for part in message.parts
        if isinstance(part, UserPromptPart) and isinstance(part.content, str)
    ]
    return json.loads(prompts[-1].split("<microscope_state>")[1][: -len("</microscope_state>")])


def test_a_long_run_returns_while_under_way_and_the_request_continues(
    microscope, slow_camera, monkeypatch
):
    from nis_assistant import tools as tools_module

    monkeypatch.setattr(tools_module, "RUN_HOLD_S", 0.2)
    microscope.vision_model, microscope.vision = Script("The last frame.").model(), True
    steps = [
        ("plan_acquisition", LAPSE),
        "Start 6 time points?",
        RUN_LAPSE,
        ("move_stage", {"x": 1100}),  # the stage is the run's: refused
        ("wait", {"until": "done"}),
        ("look", {"question": "what?"}),  # after a wait: left alone
        "- [x] start\n- [ ] report\nRunning; I will report when it is done.",
        "Done: 6 images saved. The last frame shows the same field.",
    ]
    assistant, script = talk(microscope, *steps)
    assistant.send("run 6 time points and tell me what the last one shows")
    assert assistant.send("yes").startswith("- [x] start")
    started, refused, waiting, left_alone = tool_results(assistant)[-4:]
    assert started["status"] == "running" and started["of"] == 6 and "wait" in started["advice"]
    assert refused["error"]["code"] == "busy" and "is running" in refused["error"]["message"]
    assert waiting["waiting"]["until"] == "done" and left_alone["error"]["code"] == "waiting"
    assert slow_camera.calls.count("capture") < 6 and microscope.run_in_progress()
    request = microscope.requests.current
    assert request.plan == ["[x] start", "[ ] report"] and request.turns == 1
    assert request.prompt == "yes"  # the go-ahead opened the request the run belongs to
    assert microscope.requests.due(microscope.run_is_done) is None  # still running

    microscope.run.finished.wait(10)
    came_back, result = microscope.requests.due(microscope.run_is_done)
    assert came_back is request and result.endswith("until done: met")
    reply = assistant.send(f"[continuation of request 2] {result}", scheduled=True, request=2)
    assert reply.startswith("Done: 6 images")
    state = state_sent(script)
    assert state["acquisition"]["status"] == "completed" and state["acquisition"]["images"] == 6
    assert state["acquisition"]["last_image"]["description"] == "The last frame."
    assert state["request"]["number"] == 2 and state["request"]["plan"] == request.plan
    assert request.turns == 2 and request.continuations == 1
    assert microscope.anchor["x"] == 100.0  # where the run left the stage


def test_the_state_shows_a_running_acquisition(microscope, slow_camera, monkeypatch):
    from nis_assistant import tools as tools_module

    monkeypatch.setattr(tools_module, "RUN_HOLD_S", 0.2)
    steps = [("plan_acquisition", LAPSE), "Start?", RUN_LAPSE, "Under way.", "Still going."]
    assistant, script = talk(microscope, *steps)
    assistant.send("6 time points")
    assistant.send("yes")
    assistant.send("how far is it?")
    running = state_sent(script)["acquisition"]
    assert running["status"] == "running" and running["images"] < 6 and running["of"] == 6
    microscope.stop()  # Stop microscope ends it after the current image
    microscope.run.finished.wait(10)
    assert microscope.run.report()["status"] == "canceled" and microscope.requests.open() is None


def test_wait_with_nothing_running_and_waiting_twice(microscope):
    steps = [("wait", {"until": "done"}), ("wait", {"until": "60"}), ("wait", {"until": 60}), "OK."]
    assistant, _ = talk(microscope, *steps)
    assistant.send("wait for it")
    nothing, waiting, again = tool_results(assistant)
    assert nothing["done"] is True and "no acquisition" in nothing["note"]
    assert waiting["waiting"] == {"until": 60.0, "max_s": 60}
    assert again["error"]["code"] == "refused" and "already waits" in again["error"]["message"]
    assert microscope.warnings == []  # a model's slip, not the microscope's fault


def test_a_scheduled_turn_belongs_to_the_request_that_set_it(microscope):
    steps = [
        ("schedule", {"name": "watch", "instruction": "look", "every_seconds": 60}),
        "Every minute.",
        "Looked.",
    ]
    assistant, script = talk(microscope, *steps)
    assistant.send("look every minute")
    item = dict(microscope.scheduler._items["watch"])
    assert item["request"] == 1
    assistant.send("[scheduled 'watch'] look", scheduled=True, request=item["request"])
    assert microscope.requests.current.number == 1 and microscope.requests.current.turns == 2
    assert state_sent(script)["request"]["prompt"] == "look every minute"


def test_clear_forgets_the_requests_but_not_a_running_acquisition(
    microscope, slow_camera, monkeypatch
):
    from nis_assistant import tools as tools_module

    monkeypatch.setattr(tools_module, "RUN_HOLD_S", 0.2)
    steps = [("plan_acquisition", LAPSE), "Start?", RUN_LAPSE, ("wait", {"until": "done"}), "Ok."]
    assistant, _ = talk(microscope, *steps)
    assistant.send("6 time points")
    assistant.send("yes")
    assistant.clear()
    assert microscope.requests.open() is None and microscope.run_in_progress()
    microscope.run.finished.wait(10)
    Assistant(microscope).clear()
    assert microscope.run is None


def test_a_closed_connection_is_opened_again_with_the_next_message(microscope):
    assistant, _ = talk(microscope, "Hello again.")
    microscope.engine.client.close()
    assert assistant.send("are you there?") == "Hello again."
    assert not microscope.engine.client.closed


def test_a_plan_with_an_unknown_channel_lists_the_known_ones(microscope):
    bad = {**PLAN, "channels": [{"config": "GFP"}]}
    assistant, _ = talk(microscope, ("plan_acquisition", bad), "GFP is not set up.")
    assistant.send("plan it in GFP")
    error = tool_results(assistant)[0]["error"]
    assert error["configured_options"] == ["DAPI", "FITC", "TxRed", "Brightfield"]


def test_a_malformed_plan_goes_back_to_the_model(microscope):
    bad = {**PLAN, "channels": []}  # a plan needs at least one channel
    assistant, script = talk(
        microscope, ("plan_acquisition", bad), ("plan_acquisition", PLAN), "OK."
    )
    assistant.send("plan it")
    retry = script.requests[1][-1].parts[-1]
    assert retry.part_kind == "retry-prompt"  # Pydantic caught it before our code ran
    assert tool_results(assistant)[0]["plan_id"] == "stack_test-1"


# -- one clock ---------------------------------------------------------------------------------


def test_one_clock_drives_the_state_the_run_the_images_and_the_requests(microscope, fake):
    from test_schedules import Clock

    clock = Clock(time.mktime((2026, 10, 8, 9, 0, 0, 0, 0, -1)))
    microscope.scheduler.clock = clock
    microscope.requests.clock = microscope.frames.clock = microscope.store.clock = clock
    microscope.vision = False
    steps = [("look", {"question": "?"}), ("plan_acquisition", PLAN), "Start?", RUN, "Saved."]
    assistant, script = talk(microscope, *steps)
    assistant.send("look, then plan")
    assert state_sent(script)["clock"] == "09:00:00"
    clock.now += 90
    assistant.send("yes")
    state = state_sent(script)
    assert state["clock"] == "09:01:30" and state["frames"]["last"][0]["time"] == "09:00:00"
    assert microscope.requests.current.brief(clock.now)["minutes"] == 0.0
    assert microscope.run.result["duration_s"] == 0.0  # the clock did not move during the run
    assert microscope.store.turns[-1]["time"] == "09:01:30"


# -- the state-change trail and the session store ---------------------------------------------


def test_a_tool_answer_ends_with_what_changed_at_the_microscope(microscope, fake):
    on = ("set_microscope", {"pfs_on": True})
    assistant, _ = talk(microscope, on, ("focus", {"method": "pfs"}), "Done.")
    assistant.send("PFS on, then focus")
    pfs, focused = tool_results(assistant)
    # the answer carries the PFS itself; the focus move the PFS made is what changed besides
    assert pfs == {
        "pfs": "on, focused",
        "state_changed": {"position_um": {"x": 1000.0, "y": -500.0, "z": 502.0}},
    }
    assert "state_changed" not in focused  # z is in its own answer, the PFS as the model saw it
    # a move made with the joystick between two tool calls shows in the next answer
    assistant, _ = talk(microscope, ("look", {"question": "?"}), ("look", {"question": "?"}), "Ok.")
    microscope.vision = False
    real_capture = fake.capture

    def capture():
        real_capture()
        fake.position["x"] = 1234.0  # the operator nudges the joystick during the look

    fake.capture = capture
    assistant.send("look twice")
    first, second = tool_results(assistant)
    assert first["state_changed"]["position_um"]["x"] == 1234.0
    assert "state_changed" not in second  # nothing changed since the model saw it
    # a move's own answer is the position: no repeat under state_changed
    assistant, _ = talk(microscope, ("move_stage", {"x": 1300}), "Moved.")
    assistant.send("move")
    assert tool_results(assistant)[0] == {"x": 1300.0, "y": -500.0, "z": 502.0}  # z: the PFS


def test_the_session_store_recalls_and_searches_earlier_turns(microscope, fake):
    steps = [
        ("set_microscope", {"exposure_ms": 30}),
        "This is well A1 at 30 ms.",
        ("move_stage", {"z": 540}),
        "Focus moved to 540.",
        ("recall_turn", {"changed": "position_um.z"}),
        ("search_history", {"query": "well a1"}),
        ("recall_turn", {"turn": 1}),
        ("recall_turn", {"turn": 9}),
        "The focus was at 500 before; this is well A1.",
    ]
    assistant, _ = talk(microscope, *steps)
    assistant.send("30 ms, and remember this is well A1")
    assistant.send("focus to 540")
    assistant.send("what was the focus before, and which well is this?")
    changes, found, first, missing = tool_results(assistant)[2:]
    assert changes["changes"] == [
        {
            "turn": 3,
            "time": changes["changes"][0]["time"],
            "from": 500.0,
            "to": 540.0,
            "prompt": "what was the focus before, and which well is this?",
        },
    ]
    assert found["matches"][0]["turn"] == 1 and "well A1" in found["matches"][0]["reply"]
    assert (
        first["prompt"] == "30 ms, and remember this is well A1" and first["origin"]
        if "origin" in first
        else True
    )
    assert (
        first["tools"][0]["tool"] == "set_microscope"
        and first["state"]["position_um"]["z"] == 500.0
    )
    assert first["tools"][0]["result"] == '{"exposure_ms": 30}'
    assert (
        missing["error"]["code"] == "not_found"
        and "the session has 3" in missing["error"]["message"]
    )
    store = microscope.store
    assert [t["origin"] for t in store.turns] == ["operator"] * 3 and store.turns[-1][
        "request"
    ] == 3
    assistant.clear()
    assert store.turns == []


def test_a_failed_turn_is_still_in_the_store(microscope):
    assistant, _ = talk(microscope, ("move_stage", {"x": 1500}), RuntimeError("API overloaded"))
    with pytest.raises(RuntimeError):
        assistant.send("go to 1.5 mm")
    (turn,) = microscope.store.turns
    assert turn["tools"][0]["tool"] == "move_stage" and turn["reply"] is None


# -- reading the source ----------------------------------------------------------------------


def test_the_source_of_the_three_parts_and_useq_can_be_read(microscope):
    steps = [
        ("search_source", {"text": "def setup_event"}),
        ("read_source", {"file": "useq/v2/_mda_sequence.py", "start_line": 1, "lines": 3}),
        "Here is how it works.",
    ]
    assistant, _ = talk(microscope, *steps)
    assistant.send("how does the engine move the stage?")
    found, read = tool_results(assistant)
    assert any(m.startswith("nis_engine/engine.py:") for m in found["matches"])
    assert read["lines"].startswith("1 to 3 of") and read["text"].startswith("1: ")


def test_nothing_outside_those_sources_can_be_read(microscope):
    assistant, _ = talk(microscope, ("read_source", {"file": "../../etc/passwd"}), "No.")
    assistant.send("read that file")
    error = tool_results(assistant)[0]["error"]
    assert error["code"] == "not_found" and "nis_engine/engine.py" in error["configured_options"]
    parts = ("nis_bridge/", "nis_engine/", "nis_assistant/", "useq/")
    assert all(f.startswith(parts) for f in error["configured_options"])
    assert microscope.warnings == []  # not a fault at the microscope: no red banner


# -- memory ----------------------------------------------------------------------------------


def answer(n):
    """A model answer with its reasoning attached, as some models send it."""
    return ModelResponse(parts=[ThinkingPart("thinking", signature=f"sig{n}"), TextPart(f"{n}")])


def operator_prompts(history):
    return [
        part.content
        for message in history
        for part in message.parts[:1]
        if isinstance(part, UserPromptPart)
    ]


def test_the_history_only_grows_until_it_is_long(microscope):
    assistant, _ = talk(microscope, *[answer(n) for n in range(1, 16)])
    grown = []
    for n in range(1, 16):
        assistant.send(f"message {n}")
        assert assistant.history[: len(grown)] == grown  # nothing earlier was changed
        grown = list(assistant.history)


def test_a_long_conversation_is_made_smaller_between_turns(microscope):
    steps = [answer(n) for n in range(1, 17)]
    steps[7:7] = [("get_status", {})]  # turn 8 reads the (long) status first
    assistant, _ = talk(microscope, *steps)
    for n in range(1, 17):
        assistant.send(f"message {n}")

    prompts = operator_prompts(assistant.history)
    assert len(prompts) == HISTORY_KEEP_TURNS and prompts[0].startswith("message 7")
    # the newest three turns keep the full state; older ones keep a one-line reading
    assert ["<microscope_state>" in p for p in prompts] == [False] * 7 + [True] * 3
    assert "<microscope_state_then>" in prompts[0] and "position_um" in prompts[0]
    # the old reasoning is left out, all of it, so what remains passes the model's check
    parts = [part for message in assistant.history for part in message.parts]
    assert not any(isinstance(part, ThinkingPart) for part in parts)
    assert any(isinstance(part, TextPart) and part.content == "16" for part in parts)
    (status,) = tool_results(assistant)
    assert status.endswith("(shortened in memory)")


def test_clear_context_forgets_the_conversation(microscope):
    assistant, script = talk(microscope, "One.", "Two.")
    assistant.send("first")
    assistant.clear()
    assistant.send("second")
    assert operator_prompts(script.requests[1]) == [script.requests[1][-1].parts[0].content]
