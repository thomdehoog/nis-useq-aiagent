"""Requests: what one message from the operator set going, over as many turns as it takes.

A message the operator types opens a request. Some requests are over in one
turn ("move x by 20 um"). Others take longer than one turn can: "run the
time lapse and tell me what the last image shows" starts a run that may take
an hour. The assistant then calls the ``wait`` tool, which ends its turn and
leaves a continuation pending here; when the run is done (or the time has
passed), the window starts the next turn of the same request on its own,
with a message that says what was waited for. A schedule set during a
request ("look every three minutes") fires as a turn of that request too.

Such a turn is written by the machine, not typed by the operator, and the
assistant is told so: it does not count as the operator's go-ahead for an
acquisition or a long stage move, and moves are still measured from where
the stage was when the operator last wrote.

A checklist the assistant writes in a reply ("- [ ] focus", "- [x] centre")
is kept as the request's plan and shown back to it with every turn, so a
plan with several steps survives the turns it takes.

Two threads use this at once: the assistant's tools, on the turn's thread,
and the window's clock, which asks every second whether a wait is over. A
lock keeps every change whole.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-08
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import re
import threading
import time
from collections.abc import Callable
from typing import Any

from .settings import CONTINUATIONS_MAX, PLAN_STEPS_MAX, SCHEDULE_MIN_SECONDS, WAIT_MAX_S

# A checklist line in a reply: "- [ ] focus" or "* [x] centre the sample".
_CHECKLIST = re.compile(r"^\s*[-*]\s*\[([ xX])\]\s*(.+?)\s*$", re.MULTILINE)


class Request:
    """One request: the operator's words, how many turns and tokens it has taken so far,
    its plan, and the wait it has pending, if any."""

    def __init__(self, number: int, prompt: str, started: float) -> None:
        self.number = number
        self.prompt = prompt
        self.started = started
        self.turns = 0
        self.tokens = 0
        self.continuations = 0  # how often a wait has brought it back
        self.plan: list[str] = []  # the checklist from its latest reply that had one
        self.wait: dict[str, Any] | None = None  # {"until", "max_s", "since"} while waiting
        self.ended: str | None = None  # why it ended, or None while it is open

    def brief(self, now: float) -> dict[str, Any]:
        """The request as the microscope state shows it to the assistant."""
        out: dict[str, Any] = {
            "number": self.number,
            "prompt": self.prompt[:200],
            "turn": self.turns,
            "minutes": round((now - self.started) / 60, 1),
        }
        if self.plan:
            out["plan"] = self.plan
        if self.wait:
            out["waiting"] = {
                "until": self.wait["until"],
                "for_s": int(now - self.wait["since"]),
            }
        return out


class Requests:
    """The requests of a session: the current one, and the one with a wait pending (at
    most one at a time). ``clock`` gives the time in seconds; the tests pass their own."""

    def __init__(self, clock: Callable[[], float] = time.time) -> None:
        self.clock = clock
        self.current: Request | None = None
        self.waiting: Request | None = None
        self._known: dict[int, Request] = {}
        self._count = 0
        self._lock = threading.Lock()

    def typed(self, prompt: str) -> Request:
        """A message the operator typed: it opens a new request."""
        with self._lock:
            self._count += 1
            self.current = Request(self._count, prompt, self.clock())
            self._known[self.current.number] = self.current
            return self.current

    def machine(self, number: int | None) -> Request:
        """A turn the machine wrote for request ``number``: a schedule that fell due, or
        a wait that is over. A number this session does not know (a schedule set before
        Clear context, for example) gets a request of its own."""
        with self._lock:
            request = self._known.get(number) if number is not None else None
            if request is None:
                self._count += 1
                request = Request(self._count, "(scheduled)", self.clock())
                self._known[self._count] = request
            self.current = request
            return request

    def finish_turn(self, reply: str, tokens: int) -> None:
        """After a turn: count it, and keep a checklist in the reply as the plan."""
        with self._lock:
            request = self.current
            if request is None:
                return
            request.turns += 1
            request.tokens += tokens
            steps = [
                f"[{'x' if mark.strip() else ' '}] {text}"
                for mark, text in _CHECKLIST.findall(reply or "")
            ]
            if steps:
                request.plan = steps[:PLAN_STEPS_MAX]

    def wait(self, until: Any, max_s: float | None = None) -> dict[str, Any]:
        """Leave a continuation pending for the current request.

        ``until`` is "done" (the acquisition this session is running has
        ended), or a number of seconds. ``max_s`` caps the wait; a wait is
        never longer than WAIT_MAX_S. Returns the wait as set. Raises
        ValueError, with the reason, when the turn already waits, another
        request is waiting, or the request has continued too often.
        """
        with self._lock:
            request = self.current
            if request is None or request.ended:
                raise ValueError("there is no request to continue")
            if request.wait is not None:
                raise ValueError("this turn already waits: end it now with one short sentence")
            if self.waiting is not None and self.waiting is not request:
                raise ValueError(
                    f"request {self.waiting.number} is already waiting; one wait at a time"
                )
            if request.continuations >= CONTINUATIONS_MAX:
                raise ValueError(
                    f"this request has continued {request.continuations} times; tell the "
                    "operator where it stands and let them say whether to go on"
                )
            condition = _until(until)
            limit = float(max_s) if max_s else WAIT_MAX_S
            if isinstance(condition, float):
                limit = min(limit, condition) if max_s else condition
            request.wait = {
                "until": condition,
                "max_s": min(limit, WAIT_MAX_S),
                "since": self.clock(),
            }
            self.waiting = request
            return dict(request.wait)

    def is_waiting(self) -> bool:
        """True while the current request's turn has asked to wait: it should end now."""
        return self.current is not None and self.current.wait is not None

    def due(self, done: Callable[[], bool]) -> tuple[Request, str] | None:
        """The continuation that has come due, as (request, what happened), or None.

        ``done`` says whether what the request waits for ("done") has ended;
        the window passes the acquisition's state. A wait past its cap comes
        due as "not met", so a run that never ends cannot hold a request forever.
        """
        with self._lock:
            request = self.waiting
            if request is None or request.wait is None:
                return None
            wait = request.wait
            waited = self.clock() - wait["since"]
            until = wait["until"]
            if isinstance(until, float):
                met = waited >= until
            else:
                try:
                    met = bool(done())
                except Exception:
                    met = False
            if not met and waited < wait["max_s"]:
                return None
            what = "the time" if isinstance(until, float) else until
            outcome = "met" if met else f"not met after the limit of {int(wait['max_s'])} s"
            result = f"waited {int(waited)} s until {what}: {outcome}"
            request.wait, self.waiting = None, None
            request.continuations += 1
            return request, result

    def end(self, reason: str) -> None:
        """End the open requests: Stop microscope, Cancel, Clear context."""
        with self._lock:
            for request in (self.current, self.waiting):
                if request is not None and request.ended is None:
                    request.ended, request.wait = reason, None
            self.waiting = None

    def open(self) -> Request | None:
        """The request the window shows: the waiting one, else the current one while open."""
        request = self.waiting or self.current
        return request if request is not None and request.ended is None else None


def _until(until: Any) -> str | float:
    """'done', or a number of seconds (at least SCHEDULE_MIN_SECONDS)."""
    if isinstance(until, str) and until.strip().lower() in ("done", "idle", "finished"):
        return "done"
    try:
        if isinstance(until, bool):
            raise TypeError
        seconds = float(until)
    except (TypeError, ValueError):
        raise ValueError(f"until is 'done' or a number of seconds, not {until!r}") from None
    if seconds < SCHEDULE_MIN_SECONDS:
        raise ValueError(f"wait at least {SCHEDULE_MIN_SECONDS} seconds")
    return seconds
