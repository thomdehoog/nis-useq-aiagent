"""The requests on their own, with a clock the test controls.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-08
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

import pytest
from test_schedules import Clock

from nis_assistant.requests import Requests
from nis_assistant.settings import CONTINUATIONS_MAX, WAIT_MAX_S


@pytest.fixture
def clock():
    return Clock()


def test_a_typed_message_opens_a_request_and_a_machine_turn_continues_it(clock):
    requests = Requests(clock)
    first = requests.typed("run the time lapse")
    assert first.number == 1 and requests.open() is first
    requests.finish_turn("Started.", tokens=120)
    assert first.turns == 1 and first.tokens == 120
    # a schedule or a continuation comes back as a turn of the same request
    assert requests.machine(1) is first and requests.current is first
    # a number nobody knows (a schedule from before Clear context) gets a request of its own
    other = requests.machine(99)
    assert other.number == 2 and other.prompt == "(scheduled)"


def test_a_checklist_in_the_reply_becomes_the_plan(clock):
    requests = Requests(clock)
    requests.typed("centre, focus, then image")
    requests.finish_turn("- [x] centre\n- [ ] focus\n- [ ] image\nCentred.", tokens=1)
    assert requests.current.plan == ["[x] centre", "[ ] focus", "[ ] image"]
    requests.finish_turn("No list here.", tokens=1)
    assert requests.current.plan == ["[x] centre", "[ ] focus", "[ ] image"]  # kept
    clock.now += 90
    brief = requests.current.brief(clock.now)
    assert brief["minutes"] == 1.5 and brief["plan"][0] == "[x] centre" and brief["turn"] == 2


def test_a_wait_comes_due_when_its_condition_holds_or_its_cap_passes(clock):
    requests = Requests(clock)
    request = requests.typed("run it and tell me")
    pending = requests.wait("done")
    assert pending["until"] == "done" and pending["max_s"] == WAIT_MAX_S
    assert requests.is_waiting() and request.brief(clock.now)["waiting"]["until"] == "done"
    clock.now += 30
    assert requests.due(lambda: False) is None  # the run goes on
    came_back, result = requests.due(lambda: True)
    assert came_back is request and result == "waited 30 s until done: met"
    assert request.continuations == 1 and not requests.is_waiting()
    # seconds: due when the time has passed, and the cap is the time itself
    pending = requests.wait(120)
    assert pending["until"] == 120.0 and pending["max_s"] == 120.0
    clock.now += 119
    assert requests.due(lambda: True) is None
    clock.now += 1
    assert requests.due(lambda: False)[1] == "waited 120 s until the time: met"
    # a cap that passes before the condition holds: the request comes back anyway
    requests.wait("done", max_s=60)
    clock.now += 60
    assert (
        requests.due(lambda: False)[1] == "waited 60 s until done: not met after the limit of 60 s"
    )


@pytest.mark.parametrize(
    ("until", "message"),
    [("soon", "'done' or a number of seconds"), (1, "at least"), (True, "'done' or a number")],
)
def test_a_bad_wait_says_what_is_wrong(clock, until, message):
    requests = Requests(clock)
    requests.typed("wait")
    with pytest.raises(ValueError, match=message):
        requests.wait(until)


def test_one_wait_at_a_time_and_not_too_many(clock):
    requests = Requests(clock)
    first = requests.typed("first")
    requests.wait("done")
    with pytest.raises(ValueError, match="already waits"):
        requests.wait("done")
    requests.typed("second")  # the operator writes meanwhile: a new request
    with pytest.raises(ValueError, match="request 1 is already waiting"):
        requests.wait(60)
    assert requests.open() is first  # the window shows the one that waits
    first.continuations = CONTINUATIONS_MAX
    requests.machine(1)
    requests.due(lambda: True)  # the first wait is over
    with pytest.raises(ValueError, match="continued"):
        requests.wait("done")
    with pytest.raises(ValueError, match="no request"):
        Requests(clock).wait("done")


def test_ending_drops_the_wait(clock):
    requests = Requests(clock)
    request = requests.typed("run it")
    requests.wait("done")
    requests.end("stopped")
    assert request.ended == "stopped" and request.wait is None
    assert requests.due(lambda: True) is None and requests.open() is None
    with pytest.raises(ValueError, match="no request"):
        requests.wait("done")  # an ended request does not continue
