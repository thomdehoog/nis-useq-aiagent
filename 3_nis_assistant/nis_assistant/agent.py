"""The assistant, assembled: the Agent with its tools, and one conversation.

Built on Pydantic AI. The tools (``tools.py``) are what the model
can ask the microscope to do; the instructions (``instructions.py``) are what
it is told; the memory (``memory.py``) keeps a long conversation small; the
models (``models.py``) are the ways to reach a model. ``Assistant`` is one
conversation: a message in, the answer out.

    microscope = Microscope(NisEngine(), output_dir=Path("runs"))
    assistant = Assistant(microscope)
    print(assistant.send("Take a 3-channel Z-stack here"))

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
"""

from __future__ import annotations

import json
from typing import Any

from pydantic_ai import Agent, capture_run_messages
from pydantic_ai.messages import ModelMessage, ModelRequest

from . import models
from .instructions import INSTRUCTIONS
from .memory import compact, without_state_block
from .settings import DEFAULT_MODEL_SETTINGS, MODEL, TOOL_CALL_RETRIES
from .tools import REPLY_GUARDS, TOOLS, Microscope

agent = Agent(
    deps_type=Microscope,
    output_type=str,
    instructions=INSTRUCTIONS,
    retries=TOOL_CALL_RETRIES,
    defer_model_check=True,
)
for tool in TOOLS:
    agent.tool(sequential=True)(tool)  # one tool call at a time, so each result is seen
for guard in REPLY_GUARDS:
    agent.output_validator(guard)


class Assistant:
    """A conversation with the microscope assistant. Not thread-safe: one turn at a time."""

    def __init__(
        self,
        microscope: Microscope,
        model: Any = MODEL,
        model_settings: dict[str, Any] | None = None,
    ) -> None:
        self.microscope = microscope
        self.model = model
        self.model_settings = DEFAULT_MODEL_SETTINGS if model_settings is None else model_settings
        self.endpoint: models.Endpoint | None = None  # what the window chose, if it did
        self.history: list[ModelMessage] = []
        self.last_turn: list[ModelMessage] = []  # the latest turn's messages, for traces

    def send(self, text: str) -> str:
        """One operator message in, the assistant's answer out."""
        self.microscope.cancel.clear()
        try:
            if self.microscope.engine.client.closed:  # after a timeout, or a restarted bridge
                self.microscope.engine.reconnect()
            state = self.microscope.state()
            self.microscope.anchor = state["position_um"]
        except (RuntimeError, ValueError, OSError) as exc:
            # No bridge, or NIS is closed: the model still gets the message, so it
            # can call check_setup and tell the operator what to do.
            state = {"microscope": f"not answering: {exc}"}
            self.microscope.anchor = None
        self.microscope.turn += 1
        prompt = f"{text}\n\n<microscope_state>{json.dumps(state)}</microscope_state>"
        with capture_run_messages() as messages:
            try:
                result = agent.run_sync(
                    prompt,
                    message_history=self.history,
                    deps=self.microscope,
                    model=self.model,
                    model_settings=self.model_settings,
                )
            except Exception:
                # When the model call fails after tools already ran (for example an
                # overloaded API), keep what happened: the next message then carries
                # those tool results, and the conversation can go on.
                if messages and isinstance(messages[-1], ModelRequest):
                    self.last_turn = list(messages[len(self.history) :])
                    self.history = list(messages)
                raise
        self.last_turn = result.new_messages()
        self.history = compact(result.all_messages())
        return without_state_block(result.output)

    def use(self, endpoint: models.Endpoint, vision: models.Endpoint | None = None) -> None:
        """Talk to another model from the next message on; the conversation is kept.

        ``vision`` names the model shown camera images; None means the same one.
        """
        self.endpoint = endpoint
        self.model = models.build_model(endpoint)
        self.model_settings = endpoint.settings
        seeing = vision or endpoint
        self.microscope.vision_model = self.model if vision is None else models.build_model(seeing)
        self.microscope.vision = seeing.vision

    def clear(self) -> None:
        """Forget the conversation; the next message starts a new one."""
        self.history, self.last_turn = [], []
        self.microscope.plans.clear()
        self.microscope.planned_in.clear()
        self.microscope.go_ahead_asked.clear()
