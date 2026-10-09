"""The microscope, as the assistant holds it: the engine, and the window's side
of the conversation.

``Microscope`` is what every tool in ``tools.py`` is handed. It carries the
``NisEngine`` (part 2) through which the bridge in NIS-Elements is reached,
and next to it everything the conversation needs to remember between tool
calls: where images and warnings go in the window, the vision model and its
eyes, the schedules, the plans that were checked, where the stage was when
the operator last wrote, and which long moves have already been asked about.
``state()`` is the reading sent to the model with every message.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-09
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import useq
from nis_engine import NisEngine
from pymmcore_plus.mda import MDARunner

from .eyes import Eyes
from .schedules import Scheduler
from .settings import CLOCK_FORMAT, DEFAULT_AXES, MODEL


@dataclass
class Microscope:
    """The engine plus the window's side of the conversation."""

    engine: NisEngine
    output_dir: Path
    on_image: Callable[[np.ndarray, str], None] = lambda image, caption: None
    on_warning: Callable[[str], None] = lambda text: None
    on_tool: Callable[[str, dict], None] = lambda name, args: None  # each tool call, as it starts
    vision_model: Any = MODEL  # a model name, a model object, or a test model
    vision: bool = True  # False when the vision model cannot be shown images
    _eyes: Eyes | None = field(default=None, repr=False)  # see the ``eyes`` property
    # What a positive move on each axis does to the sample in the image (settings.AXIS_CHOICES).
    axes: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_AXES))
    scheduler: Scheduler = field(default_factory=Scheduler)  # what is to happen later
    # Whether a reply that called no tool is challenged once (see guards.py).
    # Off for scripted tests, on in the window.
    challenge_no_tool: bool = False
    plans: dict[str, useq.MDASequence] = field(default_factory=dict)  # plan id -> sequence
    planned_in: dict[str, int] = field(default_factory=dict)  # plan id -> turn it was last shown
    runner: MDARunner | None = None  # set while an acquisition runs, so it can be stopped
    # Set by Cancel: every further tool call in this turn does nothing.
    cancel: threading.Event = field(default_factory=threading.Event)
    # Where the stage was when the operator last wrote, or where they last agreed
    # to go. Moves are measured from here, so small steps cannot add up to a long
    # move unasked.
    anchor: dict[str, float] | None = None
    turn: int = 0  # the operator's messages so far
    # Long moves the assistant asked the operator about, and in which turn.
    go_ahead_asked: dict[str, int] = field(default_factory=dict)

    # -- the connection to NIS-Elements -----------------------------------------------------

    @property
    def client(self):
        return self.engine.client

    def ensure_connected(self) -> None:
        """Open the connection to the bridge again when it was closed.

        The connection closes after a timeout, or when the bridge in NIS-Elements
        was stopped and started again. A request on a closed connection would
        fail, so this runs before the microscope is read. When the bridge is not
        there, the reconnect raises, and the caller says so to the operator.
        """
        if self.engine.client.closed:
            self.engine.reconnect()

    # -- readings --------------------------------------------------------------------------

    def where(self) -> dict[str, Any]:
        """The stage position and the objective in use: what a picture depends on."""
        objectives = self.client.request("get_objectives")
        current = objectives["current"]
        return {
            "position_um": self.client.request("get_position"),
            "objective": {"slot": current, "name": objectives["objectives"].get(str(current))},
        }

    def state(self) -> dict[str, Any]:
        """A compact picture of the microscope, sent with every message from the operator."""
        return {
            **self.where(),
            "stage_limits_um": self.engine.limits(),
            "pfs": self.client.request("get_pfs")["meaning"],
            "clock": time.strftime(CLOCK_FORMAT),
            "schedules": self.scheduler.listing(),
        }

    # -- the conversation's side -------------------------------------------------------------

    @property
    def eyes(self) -> Eyes:
        """The vision model's own conversation, built from ``vision_model`` on first use.

        When ``vision_model`` is changed, the next look gets new eyes, so the
        model in use is always the one the eyes talk to; the images seen with
        the old one are forgotten, since another model cannot read its turns.
        """
        if self._eyes is None or self._eyes.model is not self.vision_model:
            self._eyes = Eyes(self.vision_model)
        return self._eyes

    @eyes.setter
    def eyes(self, eyes: Eyes) -> None:
        self._eyes, self.vision_model = eyes, eyes.model

    def forget(self) -> None:
        """Drop everything that belongs to the conversation so far.

        The checked plans, the record of which long moves were asked about, the
        schedules and the images the eyes have seen all go; the connection and
        the stage limits stay. Clear context does this, through
        ``Assistant.clear``, so a new conversation starts with nothing left over
        from the old one.
        """
        self.plans.clear()
        self.planned_in.clear()
        self.go_ahead_asked.clear()
        self.scheduler.clear()
        self.eyes.reset()

    def stop(self) -> None:
        """Cancel the assistant's turn, end a running acquisition, and drop every schedule.

        A single stage move that NIS has already started runs to its end; the
        joystick or NIS-Elements itself stops it sooner. The schedules go too,
        or one could start the microscope again a moment after Stop was pressed.
        """
        self.cancel.set()
        self.scheduler.clear()
        if self.runner is not None:
            self.runner.cancel()
