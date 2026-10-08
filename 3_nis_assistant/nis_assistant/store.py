"""The session store: every turn of the conversation, kept in full, in memory.

To keep a long conversation quick, the assistant's memory (``memory.py``)
forgets older turns and shortens the ones it keeps. What that leaves out is
here: the operator's words, the microscope state the model was given, every
tool call with its result, and the reply, for every turn of the session. Two
tools hand it back on request: ``recall_turn`` returns one turn in full, or
the turns in which a state value changed ("when did the focus change?"), and
``search_history`` finds earlier turns by words ("which well did I say this
is?"). Nothing is written to disk; Clear context empties it.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-08
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import json
import re
import time
from collections.abc import Callable
from typing import Any

from pydantic_ai.messages import ModelMessage, ToolCallPart, ToolReturnPart

from .settings import CLOCK_FORMAT, RECALL_RESULT_CHARS, SEARCH_MATCHES


class SessionStore:
    """Every turn of the session in full. ``clock`` gives the time in seconds."""

    def __init__(self, clock: Callable[[], float] = time.time) -> None:
        self.clock = clock
        self.turns: list[dict[str, Any]] = []

    def begin(
        self,
        prompt: str,
        state: dict[str, Any] | None,
        origin: str = "operator",
        request: int | None = None,
    ) -> int:
        """Open a turn: the operator's words (or the machine's, for a scheduled turn or
        a continuation: ``origin`` says which), the state the model was given, and the
        request the turn belongs to. Returns the turn's number, counting from 1."""
        entry: dict[str, Any] = {
            "turn": len(self.turns) + 1,
            "time": time.strftime(CLOCK_FORMAT, time.localtime(self.clock())),
            "prompt": prompt,
            "origin": origin,
            "state": state,
            "tools": [],
            "reply": None,
        }
        if request is not None:
            entry["request"] = request
        self.turns.append(entry)
        return entry["turn"]

    def finish(self, messages: list[ModelMessage], reply: str | None) -> None:
        """Close the latest turn with its tool calls (read from the messages the turn
        exchanged with the model) and the reply."""
        if self.turns:
            self.turns[-1]["tools"] = turn_trace(messages)
            self.turns[-1]["reply"] = reply

    def recall(self, turn: int | None = None, changed: str | None = None) -> dict[str, Any]:
        """One turn in full (1 is the first, -1 the newest), or, with ``changed``, the
        turns in which that state value (a dotted key such as "position_um.z" or "pfs")
        changed, with its value before and after."""
        if changed:
            found, previous = [], None
            for entry in self.turns:
                value = _get(entry["state"], changed)
                if previous is not None and value != previous:
                    found.append(
                        {
                            "turn": entry["turn"],
                            "time": entry["time"],
                            "from": previous,
                            "to": value,
                            "prompt": entry["prompt"][:120],
                        }
                    )
                previous = value
            return {"key": changed, "changes": found, "turns": len(self.turns)}
        if not self.turns:
            return {"error": {"code": "not_found", "message": "no turns yet"}}
        index = -1 if turn is None else turn - 1 if turn > 0 else turn
        try:
            entry = self.turns[index]
        except IndexError:
            message = f"no turn {turn}; the session has {len(self.turns)}"
            return {"error": {"code": "not_found", "message": message}}
        return {key: entry[key] for key in ("turn", "time", "prompt", "state", "tools", "reply")}

    def search(self, query: str, limit: int = SEARCH_MATCHES) -> dict[str, Any]:
        """The turns whose operator message, reply or tool results contain the words of
        ``query``, best matches first. A lookup by words: it needs no model."""
        words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 1]
        hits = []
        for entry in self.turns:
            text = " ".join(
                [entry["prompt"], entry["reply"] or "", json.dumps(entry["tools"], default=str)]
            ).lower()
            score = sum(text.count(w) for w in words)
            if score:
                hit = {
                    "turn": entry["turn"],
                    "time": entry["time"],
                    "prompt": entry["prompt"][:200],
                    "reply": (entry["reply"] or "")[:200],
                }
                hits.append((score, hit))
        hits.sort(key=lambda pair: (-pair[0], pair[1]["turn"]))
        return {
            "query": query,
            "matches": [hit for _, hit in hits[:limit]],
            "turns": len(self.turns),
        }

    def clear(self) -> None:
        self.turns = []


def turn_trace(messages: list[ModelMessage]) -> list[dict[str, Any]]:
    """The tool calls of one turn, in order, each with its arguments and what it returned."""
    calls, returns, order = {}, {}, []
    for message in messages:
        for part in getattr(message, "parts", []):
            if isinstance(part, ToolCallPart):
                calls[part.tool_call_id] = {"tool": part.tool_name, "args": part.args_as_dict()}
                order.append(part.tool_call_id)
            elif isinstance(part, ToolReturnPart):
                returns[part.tool_call_id] = _brief(part.content)
    return [dict(calls[call_id], result=returns.get(call_id)) for call_id in order]


def _brief(content: Any) -> str:
    """A tool result for the store: text, cut short."""
    text = content if isinstance(content, str) else json.dumps(content, default=str)
    return text[:RECALL_RESULT_CHARS]


def _get(state: Any, dotted: str) -> Any:
    """The value at a dotted key in the state, or None."""
    value = state
    for key in dotted.split("."):
        value = value.get(key) if isinstance(value, dict) else None
    return value
