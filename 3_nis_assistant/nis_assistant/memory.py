"""The conversation: kept whole, its size measured, and a quoted state block taken
out of a reply.

The history is append-only until Clear. It is never shortened or rewritten: a
provider caches an unchanged beginning cheaply, and a model reasons best over
what it actually said. The window shows the size of the last request and stops
at a ceiling per model instead.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic_ai.messages import ModelMessage

STATE_BLOCK = re.compile(
    r"\s*<microscope_state(_then)?>.*?(</microscope_state(_then)?>|\Z)", re.DOTALL
)


def without_state_block(reply: str) -> str:
    """The reply without a copy of the <microscope_state> block.

    Some models paste the state reading they were sent back into their answer,
    although told not to. The operator should not see it, so it is taken out
    here. The model's own copy in the history stays as it was, since editing
    an earlier answer would spoil the model's check on its earlier reasoning.
    """
    return STATE_BLOCK.sub("", reply).strip() or "(The assistant gave no answer in words.)"


def last_request_tokens(messages: list[ModelMessage]) -> int:
    """The input tokens of the last request the model answered: what each request of this
    session costs now. 0 when the provider counted nothing."""
    for message in reversed(messages):
        usage: Any = getattr(message, "usage", None)
        if getattr(message, "kind", None) == "response" and usage is not None:
            return usage.input_tokens or 0
    return 0
