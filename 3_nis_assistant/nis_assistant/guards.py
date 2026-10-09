"""Two guards on the model's reply itself, before the operator sees it.

The tools check what the model asks for; these check what it says. An empty
reply (one with no letter or digit in it) goes back to the model once. A
reply that claims to have done something in a turn that called no tool also
goes back once, with that fact; the model then acts, or its first reply is
shown as it was. Pydantic AI runs them as output validators, so a guard that
raises ``ModelRetry`` sends its text to the model as one more request in the
same turn. ``REPLY_GUARDS`` lists them; ``agent.py`` registers them.

Each guard remembers, per run, whether it has already spoken up, in a field
of the ``Microscope`` the tools share (``empty_reply_asked``,
``first_reply``), so that it asks once and never loops.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-09
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import re

from pydantic_ai import ModelRetry, RunContext
from pydantic_ai.messages import ToolCallPart

from .instructions import CALLED_NOTHING_CHALLENGE, EMPTY_REPLY_CHALLENGE, EMPTY_REPLY_FALLBACK
from .memory import is_operator_turn
from .microscope import Microscope


def hand_back_an_empty_reply(ctx: RunContext[Microscope], output: str) -> str:
    """A reply with no letter or digit goes back to the model once.

    A second empty reply reaches the operator as a plain sentence rather than as,
    say, an underscore.
    """
    asked = ctx.deps.empty_reply_asked
    if re.search(r"[^\W_]", output or ""):
        asked.discard(ctx.run_id)
        return output
    if ctx.run_id in asked:
        asked.discard(ctx.run_id)
        return EMPTY_REPLY_FALLBACK
    asked.add(ctx.run_id)
    raise ModelRetry(EMPTY_REPLY_CHALLENGE)


GUARD_WORD = re.compile(r"^\s*SAME\b[\s.:!-]*")  # the one word CALLED_NOTHING_CHALLENGE asks for


def challenge_a_reply_that_called_nothing(ctx: RunContext[Microscope], output: str) -> str:
    """A small model answers "stop" with "I have stopped the microscope." and no call.

    The one thing known without reading the reply is that the turn called nothing,
    so such a reply goes back to the model once with that fact. If it then calls
    a tool, the turn goes on and its new reply reports what happened. If it does
    not, the operator gets the first reply word for word: asked to repeat itself
    a small model writes something shorter and worse, so it is asked for one word
    instead. Costs one short request on a turn that sends no command. Off unless
    the microscope's ``challenge_no_tool`` is set (the window sets it).
    """
    if not ctx.deps.challenge_no_tool or ctx.deps.cancel.is_set():
        return output
    first = ctx.deps.first_reply
    starts = [i for i, m in enumerate(ctx.messages) if is_operator_turn(m)]
    turn = ctx.messages[starts[-1] :] if starts else ctx.messages
    called = any(isinstance(part, ToolCallPart) for m in turn for part in getattr(m, "parts", []))
    if not called and ctx.run_id in first:
        return first.pop(ctx.run_id)  # challenged, and still nothing called: as it was
    first.pop(ctx.run_id, None)
    # "SAME" and the challenge are for this guard, never for the operator: a reply
    # that opens with them, or holds nothing else, is asked for again.
    reply = GUARD_WORD.sub("", output, count=1).strip()
    if not reply or CALLED_NOTHING_CHALLENGE[:40] in reply:
        raise ModelRetry(EMPTY_REPLY_CHALLENGE)
    if called:
        return reply
    first[ctx.run_id] = reply
    raise ModelRetry(CALLED_NOTHING_CHALLENGE)


REPLY_GUARDS = (hand_back_an_empty_reply, challenge_a_reply_that_called_nothing)
