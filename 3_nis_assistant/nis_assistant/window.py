"""A chat window for the microscope assistant.

    nis-assistant --output D:\\runs

Needs the bridge running in NIS-Elements and a model to talk to: the Model panel
at the top of the window chooses one (a cloud model with its API key, a server you
run yourself, or a model file on this computer). Left: the conversation, the buttons,
and the stage limits in force, which the operator can narrow. Right: the latest
image, the microscope status, and a red banner for anything refused. The divider
between the two halves can be dragged. A clock in the window fires the schedules
the assistant sets ("look every three minutes") as turns of their own.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import threading
from collections.abc import Callable
from pathlib import Path

import numpy as np
from nis_bridge import start as nis_start
from nis_bridge.client import NisConnectionError
from nis_bridge.settings import HOST, PORT
from nis_engine import NisEngine
from pydantic_ai.exceptions import UnexpectedModelBehavior
from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtGui import QCloseEvent, QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from . import models
from .agent import Assistant
from .images import as_png
from .instructions import SCHEDULED_TURN
from .local import CONTEXT_TOO_SMALL_HELP, CONTEXT_TOO_SMALL_SIGNS
from .panel import AxesBox, ModelPanel, PreferencesBox
from .settings import DEFAULT_PROVIDER, FONT_POINTS, OUTPUT_FOLDER
from .tools import Microscope, bridge_steps

# The colour of each voice in the transcript.
COLOURS = {"you": "#1a5fb4", "assistant": "#26a269", "system": "#b00020", "scheduled": "#8a5a00"}

WELCOME = (
    "Hello. I can move the stage, change the optical settings, focus, look at the "
    "sample and run acquisitions. Ask me in your own words, for example "
    "<i>What do you see?</i> or <i>Take a 3-channel Z-stack of 10 um here</i>. "
    "Before a long stage move I ask you here first."
)


class _Signals(QObject):
    """Carries results from the assistant's thread to the window's thread."""

    reply = Signal(str)
    error = Signal(str)
    image = Signal(object, str)
    warning = Signal(str)
    tool = Signal(str, dict)


class AssistantWindow(QMainWindow):
    """The chat window. ``endpoint`` is the model to start with; None keeps the
    assistant's own (a test passes one in that way) and leaves the panel to the operator."""

    def __init__(
        self,
        assistant: Assistant,
        endpoint: models.Endpoint | None = None,
        nis_starting: bool = False,
    ) -> None:
        super().__init__()
        self.assistant = assistant
        self._waited_s = 0.0
        self.setWindowTitle("Nikon microscope assistant")
        self.resize(1200, 750)

        self.signals = _Signals()
        self.signals.reply.connect(self._show_reply)
        self.signals.error.connect(self._show_error)
        self.signals.image.connect(self._show_image)
        self.signals.warning.connect(self._show_warning)
        self.signals.tool.connect(self._show_tool)
        microscope = assistant.microscope
        microscope.on_image = self.signals.image.emit
        microscope.on_warning = self.signals.warning.emit
        microscope.on_tool = self.signals.tool.emit

        # left: the conversation
        self.transcript = QTextBrowser()
        self.prompt = QLineEdit(placeholderText="Ask the microscope assistant ...")
        self.prompt.returnPressed.connect(self.send)
        self.send_button = QPushButton("Send", clicked=self.send)
        self.stop_button = QPushButton("Stop microscope", clicked=self.stop_microscope)
        self.stop_button.setStyleSheet("color:#b00020; font-weight:bold")
        input_row = QHBoxLayout()
        input_row.addWidget(self.prompt, 1)
        input_row.addWidget(self.send_button)
        input_row.addWidget(self.stop_button)
        self.cancel_button = QPushButton("Cancel prompt", clicked=self.cancel_prompt)
        self.clear_button = QPushButton("Clear context", clicked=self.clear_context)
        self.show_tools = QCheckBox("Show tool calls")
        buttons_row = QHBoxLayout()
        buttons_row.addWidget(self.cancel_button)
        buttons_row.addWidget(self.clear_button)
        buttons_row.addWidget(self.show_tools)
        buttons_row.addStretch(1)
        # below: the stage limits in force, one field per side; the operator can narrow them
        self.limit_fields = {
            (axis, side): QLineEdit(placeholderText="NIS") for axis in "xyz" for side in "-+"
        }
        for edit in self.limit_fields.values():
            edit.setMinimumWidth(64)  # room for "-57000" in full: a sign cut off would mislead
        self.apply_limits_button = QPushButton("Apply limits", clicked=self.apply_limits)
        self.nis_limits_button = QPushButton("Use NIS limits", clicked=self.use_nis_limits)
        # The buttons sit on the row above, so the left half can be made narrow.
        buttons_row.addWidget(self.apply_limits_button)
        buttons_row.addWidget(self.nis_limits_button)
        limits_row = QHBoxLayout()
        limits_row.addWidget(QLabel("Stage limits (um):"))
        for (axis, side), edit in self.limit_fields.items():
            limits_row.addWidget(QLabel(f"{axis.upper()}{side}"))
            limits_row.addWidget(edit, 1)

        # top: which model, folding open to the choice and the preferences
        self.preferences = PreferencesBox(
            microscope.output_dir, self.font().pointSize(), self.set_output_dir, self.set_font_size
        )
        self.axes_box = AxesBox(microscope.axes, self.set_axes)
        self.panel = ModelPanel(
            self.use_model,
            lambda text: self._say("system", text),
            self.preferences,
            axes=self.axes_box,
        )
        # The window's clock: every second, a schedule that fell due runs as a turn.
        self._tick = QTimer(self)
        self._tick.timeout.connect(self.fire_due_schedule)
        self._tick.start(1000)

        left = QVBoxLayout()
        left.addWidget(self.panel)
        left.addWidget(self.transcript, 1)
        left.addLayout(input_row)
        left.addLayout(buttons_row)
        left.addLayout(limits_row)

        # right: warning, image, status
        self.warning = QLabel(wordWrap=True)
        self.warning.setStyleSheet(
            "background:#b00020; color:white; padding:8px; font-weight:bold; border-radius:4px"
        )
        self.warning.hide()
        self.image = QLabel("No image yet.", alignment=Qt.AlignmentFlag.AlignCenter)
        self.image.setMinimumSize(480, 480)
        self.image.setStyleSheet("background:#111; color:#aaa")
        self.caption = QLabel(wordWrap=True)
        self.status = QLabel(wordWrap=True)
        self.status.setStyleSheet("color:#555")
        right = QVBoxLayout()
        right.addWidget(self.warning)
        right.addWidget(self.image, 1)
        right.addWidget(self.caption)
        right.addWidget(self.status)

        # the two halves, with a divider the operator can drag
        left_widget, right_widget = QWidget(), QWidget()
        left_widget.setLayout(left)
        right_widget.setLayout(right)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        self.splitter.setChildrenCollapsible(False)
        self.setCentralWidget(self.splitter)

        self._say("assistant", WELCOME, escape=False)
        if nis_starting:
            self._say(
                "system",
                "NIS-Elements is being started with the bridge macro. This takes a minute or "
                "two; the window connects by itself once the bridge answers.",
            )
            QTimer.singleShot(int(nis_start.POLL_S * 1000), self._wait_for_bridge)
        elif self.assistant.microscope.engine.client.closed:
            self._say_bridge_steps()
        self._refresh_status()
        self._show_limits()
        if endpoint is not None:
            self.panel.language.show_endpoint(endpoint)
            self.panel.apply()

    def _wait_for_bridge(self) -> None:
        """While NIS-Elements starts: try the bridge now and then, until it answers."""
        engine = self.assistant.microscope.engine
        try:
            engine.reconnect()
        except (RuntimeError, OSError):
            self._waited_s += nis_start.POLL_S
            if self._waited_s >= nis_start.START_TIMEOUT_S:
                self._say("system", "NIS-Elements did not come up with the bridge in time.")
                self._say_bridge_steps()
            else:
                QTimer.singleShot(int(nis_start.POLL_S * 1000), self._wait_for_bridge)
            return
        self._say("system", "Connected to NIS-Elements.")
        self._refresh_status()
        self._show_limits()

    def _say_bridge_steps(self) -> None:
        """The bridge is not answering: say which file to run in NIS-Elements, and how."""
        self._say(
            "system",
            "NIS-Elements is not answering: the bridge is not running.\n"
            + "\n".join(f"{i}. {step}" for i, step in enumerate(bridge_steps(), 1)),
        )

    def set_output_dir(self, folder: Path) -> None:
        """Save the next acquisitions in this folder (made when the first run saves)."""
        self.assistant.microscope.output_dir = folder
        self._say("system", f"Images are saved in {folder}.")

    def set_font_size(self, points: int) -> None:
        """Bigger or smaller letters, everywhere in the window, at once."""
        app = QApplication.instance()
        font = QFont(app.font())
        font.setPointSize(points)
        app.setFont(font)
        for widget in [self, *self.findChildren(QWidget)]:
            widget.setFont(font)

    def set_axes(self, axes: dict[str, str]) -> None:
        """Tell the assistant what a positive move on each axis does to the sample."""
        self.assistant.microscope.axes = axes
        said = ", ".join(f"+{axis} moves the sample {what}" for axis, what in axes.items())
        self._say("system", f"Coordinate system: {said}.")

    def use_model(self, endpoint: models.Endpoint, vision: models.Endpoint | None) -> None:
        """The panel's choice: talk to this model from the next message on.

        The chat is kept. The eyes start afresh when their model changes, since
        another model cannot read the images and answers of the old one.
        """
        seen = self.assistant.microscope.eyes.frames
        self.assistant.use(endpoint, vision)
        note = (
            f" The eyes start afresh; the {seen} images seen so far are forgotten." if seen else ""
        )
        self._say("system", f"Talking to {endpoint.name}.{note}")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Do not close in the middle of an action: the microscope would be left mid-way."""
        if self.busy:
            QMessageBox.information(
                self,
                "Still working",
                "The assistant is still working on the microscope. Wait until it is done, "
                "or press Stop microscope, then close.",
            )
            event.ignore()
            return
        self.panel.stop_servers()  # a model file served by this window ends with it
        event.accept()

    # -- one turn of the conversation ----------------------------------------------

    def send(self) -> None:
        text = self.prompt.text().strip()
        if not text or self.busy:
            return
        self.prompt.clear()
        self.warning.hide()
        self._say("you", text)
        self._in_background(lambda: self.assistant.send(text))

    def fire_due_schedule(self) -> None:
        """The window's clock calls this every second. When no turn is running and a
        schedule is due, its instruction runs as a turn of its own, marked as
        scheduled in the transcript; while a turn runs it waits for the next tick.
        """
        if self.busy:
            return
        item = self.assistant.microscope.scheduler.pop_due()
        if item is None:
            return
        text = SCHEDULED_TURN.format(name=item["name"], instruction=item["instruction"])
        self.warning.hide()
        self._say("scheduled", text)
        self._in_background(lambda: self.assistant.send(text, scheduled=True), item["name"])

    @property
    def busy(self) -> bool:
        return not self.send_button.isEnabled()

    def _in_background(self, turn: Callable[[], str], schedule: str | None = None) -> None:
        """Run one assistant turn off the window's thread, so the window stays responsive.

        A turn that fails ends with its error in the transcript. When it was a
        scheduled turn, that schedule is cancelled too, or a schedule with a
        dead model would repeat the same error every period.
        """
        self._set_busy(True)

        def work() -> None:
            try:
                self.signals.reply.emit(turn())
            except Exception as exc:
                text = _explain(exc, self.assistant.endpoint)
                if schedule and self.assistant.microscope.scheduler.cancel(schedule):
                    text += f" The schedule '{schedule}' is cancelled."
                self.signals.error.emit(text)

        threading.Thread(target=work, daemon=True).start()

    def _show_reply(self, text: str) -> None:
        self._say("assistant", text)
        self._set_busy(False)
        self._refresh_status()

    def _show_error(self, text: str) -> None:
        self._say("system", text)
        self._set_busy(False)

    # -- the operator's say: Cancel prompt, Stop, Clear ---------------------------------

    def cancel_prompt(self) -> None:
        """Stop the assistant, not the microscope: further tool calls in this turn do nothing.

        What the assistant already started (a move, an acquisition) runs on; Stop
        microscope ends an acquisition.
        """
        if not self.busy:
            return
        self.assistant.microscope.cancel.set()
        self._say("system", "Cancelled. The assistant stops after its current step.")

    def stop_microscope(self) -> None:
        """Cancel the assistant, end a running acquisition after the current image, and
        drop every schedule."""
        self.assistant.microscope.stop()
        self._say(
            "system",
            "Stop: the assistant is cancelled, a running acquisition ends after the "
            "current image, and every schedule is cancelled. A single stage move already "
            "under way finishes; use the joystick or NIS-Elements to stop it sooner.",
        )

    def clear_context(self) -> None:
        """Forget the conversation, in the window and in the assistant's memory."""
        if self.busy:
            return
        self.assistant.clear()
        self.transcript.clear()
        self._say("assistant", WELCOME, escape=False)

    # -- stage limits -------------------------------------------------------------------

    def apply_limits(self) -> None:
        """Use the numbers typed in the six limit fields, on top of the limits set in NIS.

        An empty field keeps NIS's own limit on that side.
        """
        values = {}
        for (axis, side), edit in self.limit_fields.items():
            text = edit.text().strip()
            try:
                values[axis, side] = float(text) if text else None
            except ValueError:
                self._show_warning(f"{axis.upper()}{side}: write a number in um, not {text!r}")
                return
        limits = {axis: (values[axis, "-"], values[axis, "+"]) for axis in "xyz"}
        if self._set_limits(**limits):
            self.warning.hide()
            self._show_limits(announce=True)

    def use_nis_limits(self) -> None:
        if self._set_limits():
            self._show_limits(announce=True)

    def _set_limits(self, **limits) -> bool:
        """Apply limits on the engine; True if they were applied, else a warning."""
        engine = self.assistant.microscope.engine
        try:
            if engine.client.closed:
                engine.reconnect()
            engine.set_limits(**limits)
        except ValueError as exc:
            self._show_warning(f"limits not applied: {exc}")
            return False
        except RuntimeError as exc:  # NIS or the bridge is not reachable
            self._show_warning(f"limits not applied, the microscope did not answer: {exc}")
            return False
        return True

    def _show_limits(self, announce: bool = False) -> None:
        """Fill the fields with the limits in force (a value beyond NIS's is cut to NIS's)."""
        try:
            limits = self.assistant.microscope.engine.limits()
        except (RuntimeError, ValueError):
            return  # the status line already says the microscope is not reachable
        for (axis, side), edit in self.limit_fields.items():
            edit.setText(f"{limits[axis]['min' if side == '-' else 'max']:g}")
        if announce:
            ranges = ", ".join(
                f"{a.upper()} {limits[a]['min']:g} to {limits[a]['max']:g}" for a in "xyz"
            )
            self._say("system", f"Stage limits in use (um): {ranges}.")

    # -- the right-hand side ----------------------------------------------------------

    def _show_image(self, image: np.ndarray, caption: str) -> None:
        pixmap = QPixmap()
        pixmap.loadFromData(as_png(image).data)
        self.image.setPixmap(
            pixmap.scaled(
                self.image.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.caption.setText(caption)

    def _show_tool(self, name: str, args: dict) -> None:
        if self.show_tools.isChecked():
            call = html.escape(
                f"{name}({', '.join(f'{k}={json.dumps(v)}' for k, v in args.items())})"
            )
            self.transcript.append(f'<p style="color:#888; margin:0">&#8250; {call}</p>')

    def _show_warning(self, text: str) -> None:
        self.warning.setText(f"Refused: {text}")
        self.warning.show()

    def _refresh_status(self) -> None:
        engine = self.assistant.microscope.engine
        try:
            if engine.client.closed:
                engine.reconnect()
            state = self.assistant.microscope.state()
        except (RuntimeError, ValueError, OSError) as exc:
            self.status.setText(f"Microscope not reachable: {exc}")
            return
        p = state["position_um"]
        self.status.setText(
            f"Stage x {p['x']:.1f}, y {p['y']:.1f}, z {p['z']:.1f} um  ·  "
            f"objective {state['objective']['name']}  ·  PFS {state['pfs']}"
        )

    # -- small helpers ------------------------------------------------------------------

    def _say(self, who: str, text: str, escape: bool = True) -> None:
        colour = COLOURS[who]
        body = html.escape(text).replace("\n", "<br>") if escape else text
        self.transcript.append(f'<p><b style="color:{colour}">{who}</b><br>{body}</p>')

    def _set_busy(self, busy: bool) -> None:
        self.send_button.setEnabled(not busy)
        self.prompt.setEnabled(not busy)
        self.apply_limits_button.setEnabled(not busy)
        self.nis_limits_button.setEnabled(not busy)
        self.clear_button.setEnabled(not busy)
        self.cancel_button.setEnabled(busy)
        self.send_button.setText("Working ..." if busy else "Send")


def _explain(exc: Exception, endpoint: models.Endpoint | None) -> str:
    """Turn a failure into a sentence for the operator."""
    if isinstance(exc, UnexpectedModelBehavior):  # e.g. the model declined to answer
        return f"The assistant could not answer: {exc.message}"
    text = f"{type(exc).__name__}: {exc}"
    lowered = text.lower()
    if any(sign in lowered for sign in ("api_key", "api key", "authentication", "401")):
        where = f" {endpoint.name}" if endpoint else ""
        advice = models.missing_key_advice(endpoint) if endpoint else "check the API key."
        return f"The assistant could not reach the model{where}: {advice} ({text})"
    if any(sign in text for sign in CONTEXT_TOO_SMALL_SIGNS):
        return f"The model server refused the request. {CONTEXT_TOO_SMALL_HELP} ({text})"
    return f"Something went wrong: {text}"


def _start_nis() -> bool:
    """Start NIS-Elements with the bridge macro; True when it was started.

    When NIS-Elements is already open, nothing can be started from outside: the
    window then shows the macro steps instead.
    """
    if nis_start.nis_is_running():
        return False
    macro = nis_start.MACRO if nis_start.MACRO.exists() else nis_start.install()
    try:
        nis_start.start_nis(macro)
    except (FileNotFoundError, OSError) as exc:
        print(f"NIS-Elements was not started: {exc}", file=sys.stderr)
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chat with the Nikon microscope assistant.")
    parser.add_argument("--port", type=int, default=PORT, help="the bridge's port")
    parser.add_argument(
        "--output",
        default=str(Path.home() / OUTPUT_FOLDER),
        help="folder for the acquisitions (default: nis_assistant_runs in your home folder)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="the model to start with, e.g. google:gemini-3.5-flash-lite or "
        "openai:gpt-5-mini; without it, the Model panel's default, which can be "
        "changed in the window",
    )
    parser.add_argument(
        "--font-size", type=int, default=FONT_POINTS, help=f"letter size in points ({FONT_POINTS})"
    )
    parser.add_argument(
        "--start-nis",
        action="store_true",
        help="start NIS-Elements with the bridge macro when the bridge does not answer "
        "(nis_ar.exe from its usual place, or from the NIS_ELEMENTS variable)",
    )
    args = parser.parse_args(argv)

    app = QApplication(sys.argv[:1])
    font = QFont(app.font())
    font.setPointSize(args.font_size)
    app.setFont(font)
    nis_starting = False
    try:
        engine = NisEngine(HOST, args.port)
    except NisConnectionError:
        # The window opens anyway and says how to start the bridge; it connects
        # with the first message once the bridge is running.
        engine = NisEngine(HOST, args.port, connect=False)
        nis_starting = args.start_nis and _start_nis()
    microscope = Microscope(engine, output_dir=Path(args.output), challenge_no_tool=True)
    endpoint = (
        models.Endpoint.from_name(args.model)
        if args.model
        else models.Endpoint.from_preset(DEFAULT_PROVIDER)
    )
    window = AssistantWindow(Assistant(microscope), endpoint=endpoint, nis_starting=nis_starting)
    window.show()
    try:
        return app.exec()
    finally:
        engine.close()


if __name__ == "__main__":
    raise SystemExit(main())
