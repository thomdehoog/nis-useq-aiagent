"""The Model panel at the top of the chat window.

A single line shows which model is in use; clicking it folds the panel open.
Inside are two boxes: the language model that runs the conversation, and the
vision model that is shown camera images (by default the same one). Each box
names a cloud model (provider, model, API key) or an OpenAI-style server (its
address). "Use this model" applies the choice; the conversation so far is kept. Below them, the
Coordinate system box says what a positive move on each axis does to the
sample in the image, and the Preferences box where images are saved.

The API key typed here stays in memory for this session only.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import models
from .models import Endpoint
from .settings import (
    AXIS_CHOICES,
    DEFAULT_PROVIDER,
    PROVIDERS,
)

CLOUD = "Cloud"
SAME = "Same as language model"


class ModelPicker(QGroupBox):
    """A titled box that names one model.

    The fields are the provider, the model name, the API key and, for an
    OpenAI-style server, its address. The vision box has a Type dropdown with one
    more choice, "Same as language model".
    """

    changed = Signal()

    def __init__(self, title: str, same_as: bool = False):
        super().__init__(title)
        grid = QGridLayout(self)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)
        self.grid = grid

        self.mode = QComboBox()
        self.mode.addItems(([SAME] if same_as else []) + [CLOUD])
        self.provider = QComboBox()
        self.provider.addItems(list(PROVIDERS))
        self.provider.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.model = QLineEdit()
        self.model.setMinimumWidth(140)
        self.key = QLineEdit()
        self.key.setEchoMode(QLineEdit.EchoMode.Password)
        self.key.setMinimumWidth(120)
        self.base_url = QLineEdit()
        self.base_url.setMinimumWidth(160)
        self.sees = QCheckBox("Can see images")
        self.sees.setToolTip(
            "Tick when this server's model can look at pictures, so the assistant "
            "shows it the camera image. Untick for a text-only model."
        )

        self.labels = {
            name: QLabel(text)
            for name, text in {
                "mode": "Type",
                "provider": "Provider",
                "model": "Model",
                "key": "API key",
                "base_url": "Address",
            }.items()
        }
        # Line one: the type and what names the model. Line two, cloud only: the key,
        # and for a server its address. The model column takes the leftover width.
        grid.addWidget(self.labels["mode"], 0, 0)
        grid.addWidget(self.mode, 0, 1)
        grid.addWidget(self.labels["provider"], 0, 2)
        grid.addWidget(self.provider, 0, 3)
        grid.addWidget(self.labels["model"], 0, 4)
        grid.addWidget(self.model, 0, 5, 1, 3)
        grid.addWidget(self.labels["key"], 1, 2)
        grid.addWidget(self.key, 1, 3, 1, 2)
        grid.addWidget(self.labels["base_url"], 1, 5)
        grid.addWidget(self.base_url, 1, 6)
        grid.addWidget(self.sees, 1, 7)
        grid.setColumnStretch(5, 1)

        self.provider.setCurrentText(DEFAULT_PROVIDER)
        self.mode.setCurrentText(SAME if same_as else CLOUD)
        self.mode.currentTextChanged.connect(self._on_mode_changed)
        self.provider.currentTextChanged.connect(self._on_provider_changed)
        for widget in (self.mode, self.provider):
            widget.currentTextChanged.connect(lambda *_: self.changed.emit())
        self._on_provider_changed(DEFAULT_PROVIDER)
        if not same_as:  # the language box has one type only
            self.labels["mode"].hide()
            self.mode.hide()

    # -- what is chosen -------------------------------------------------------------------

    @property
    def same(self) -> bool:
        """True when this box defers to the language model (the vision box's first choice)."""
        return self.mode.currentText() == SAME

    def cloud_endpoint(self) -> Endpoint:
        provider = self.provider.currentText()
        kind = PROVIDERS[provider]["kind"]
        vision = self.sees.isChecked() if kind == "openai-compatible" else None
        return Endpoint.from_preset(
            provider, self.model.text(), self.key.text(), self.base_url.text(), vision=vision
        )

    def show_endpoint(self, endpoint: Endpoint) -> None:
        """Fill the fields from an endpoint, e.g. the one named on the command line."""
        self.mode.setCurrentText(CLOUD)
        self.provider.setCurrentText(endpoint.provider)
        self.model.setText(endpoint.model)
        if endpoint.kind == "openai-compatible":
            self.base_url.setText(endpoint.base_url)
            self.sees.setChecked(endpoint.vision)

    # -- the fields ----------------------------------------------------------------------

    def _on_mode_changed(self, *_) -> None:
        """Show the fields for the type chosen."""
        cloud = self.mode.currentText() == CLOUD
        server = cloud and PROVIDERS[self.provider.currentText()]["kind"] == ("openai-compatible")
        for name in ("provider", "model", "key"):
            self.labels[name].setVisible(cloud)
            getattr(self, name).setVisible(cloud)
        for widget in (self.labels["base_url"], self.base_url, self.sees):
            widget.setVisible(server)

    def _on_provider_changed(self, name: str) -> None:
        """Prefill the preset and say where the key comes from when the field is left empty."""
        preset = PROVIDERS[name]
        self.model.setText(preset["model"])
        self.base_url.setText(preset.get("base_url", ""))
        variable = preset.get("key_env")
        in_env = bool(variable and os.environ.get(variable))
        if preset["kind"] == "openai-compatible":
            placeholder = "only if the server asks for one"
        elif in_env:
            placeholder = f"using {variable} from the environment"
        else:
            placeholder = f"{name} API key"
        self.key.setPlaceholderText(placeholder)
        self._on_mode_changed()


class AxesBox(QGroupBox):
    """The Coordinate system box: what a positive move on x, y and z does to the
    sample in the image, as the operator sees it on the screen.

    Microscopes differ in this, so the assistant is told the choice and turns
    "left", "up" and "deeper" into signed moves with it. ``on_change`` gets the
    choice as a dict such as {"x": "right", "y": "up", "z": "deeper into the
    sample"} whenever it changes.
    """

    def __init__(self, axes: dict[str, str], on_change: Callable[[dict[str, str]], None]) -> None:
        super().__init__("Coordinate system")
        self.on_change = on_change
        self.setToolTip(
            "Watch the sample on the screen while the stage moves in the positive "
            "direction of each axis, and choose what you see."
        )
        self.combos: dict[str, QComboBox] = {}
        grid = QGridLayout(self)
        grid.setHorizontalSpacing(8)
        for column, (axis, choices) in enumerate(AXIS_CHOICES.items()):
            combo = QComboBox()
            combo.addItems(list(choices))
            combo.setCurrentText(axes[axis] if axes.get(axis) in choices else choices[0])
            combo.currentTextChanged.connect(lambda *_: self.on_change(self.axes()))
            grid.addWidget(QLabel(f"{axis}+ moves the sample"), 0, 2 * column)
            grid.addWidget(combo, 0, 2 * column + 1)
            self.combos[axis] = combo
        grid.setColumnStretch(2 * len(AXIS_CHOICES), 1)

    def axes(self) -> dict[str, str]:
        """The choice as the assistant takes it: axis -> what a positive move does."""
        return {axis: combo.currentText() for axis, combo in self.combos.items()}


class PreferencesBox(QGroupBox):
    """The third box: where acquisitions are saved, and the size of the letters.

    ``on_output`` gets the folder as a Path when it changes; ``on_font`` the
    point size. Both take effect at once.
    """

    def __init__(
        self,
        output_dir: Path,
        font_points: int,
        on_output: Callable[[Path], None],
        on_font: Callable[[int], None],
    ) -> None:
        super().__init__("Preferences")
        self.on_output, self.on_font = on_output, on_font
        self.output = QLineEdit(str(output_dir))
        self.output.setToolTip("Acquisitions are saved here, as OME-TIFF with the useq sequence")
        self.output.editingFinished.connect(self._output_changed)
        self.browse = QPushButton("Browse ...", clicked=self.choose_output)
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setSuffix(" pt")
        self.font_size.setValue(font_points)
        self.font_size.valueChanged.connect(self.on_font)
        grid = QGridLayout(self)
        grid.setHorizontalSpacing(8)
        grid.addWidget(QLabel("Save images in"), 0, 0)
        grid.addWidget(self.output, 0, 1)
        grid.addWidget(self.browse, 0, 2)
        grid.addWidget(QLabel("Letter size"), 0, 3)
        grid.addWidget(self.font_size, 0, 4)
        grid.setColumnStretch(1, 1)

    def _output_changed(self) -> None:
        text = self.output.text().strip()
        if text:
            self.on_output(Path(text))

    def choose_output(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Save images in", self.output.text())
        if folder:
            self.output.setText(folder)
            self._output_changed()


class ModelPanel(QWidget):
    """One line that names the model in use, folding open to the pickers and the preferences.

    ``apply`` (also the "Use this model" button) builds the endpoints and hands
    them to ``on_use``.
    """

    def __init__(
        self,
        on_use: Callable[[Endpoint, Endpoint | None], None],
        say: Callable[[str], None],
        preferences: PreferencesBox | None = None,
        axes: AxesBox | None = None,
    ) -> None:
        super().__init__()
        self.on_use = on_use
        self.say = say
        self.preferences = preferences
        self.axes = axes

        self.toggle = QToolButton()
        self.toggle.setCheckable(True)
        self.toggle.setChecked(False)
        self.toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle.setStyleSheet("QToolButton { border: none; font-weight: bold }")
        self.toggle.toggled.connect(self._fold)
        self.summary = QLabel("no model chosen yet")
        self.summary.setStyleSheet("color:#555")
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(self.toggle)
        header.addWidget(self.summary, 1)

        self.language = ModelPicker("Language model")
        self.vision = ModelPicker("Vision model", same_as=True)
        self.use_button = QPushButton("Use this model", clicked=self.apply)
        self.note = QLabel(wordWrap=True)
        self.note.setStyleSheet("color:#555")
        buttons = QHBoxLayout()
        buttons.addWidget(self.use_button)
        buttons.addWidget(self.note, 1)
        body = QVBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.addWidget(self.language)
        body.addWidget(self.vision)
        body.addLayout(buttons)
        if axes is not None:
            body.addWidget(axes)
        if preferences is not None:
            body.addWidget(preferences)
        self.body = QWidget()
        self.body.setLayout(body)
        self.body.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)
        layout.addWidget(self.body)
        self._fold(False)

    def _fold(self, open_: bool) -> None:
        self.body.setVisible(open_)
        self.toggle.setArrowType(Qt.ArrowType.DownArrow if open_ else Qt.ArrowType.RightArrow)
        self.toggle.setText("Model" if open_ else "Model:")

    # -- applying a choice -----------------------------------------------------------------

    def apply(self) -> None:
        """Use what the pickers say."""
        self.note.setText("")
        endpoints: dict[str, Endpoint | None] = {}
        try:
            for role, picker in (("language", self.language), ("vision", self.vision)):
                if picker.same:
                    endpoints[role] = None
                    continue
                endpoint = picker.cloud_endpoint()
                if endpoint.needs_key and not endpoint.api_key:
                    raise RuntimeError(models.missing_key_advice(endpoint))
                endpoints[role] = endpoint
        except RuntimeError as exc:
            self.note.setText(str(exc))
            self.say(f"The model was not changed: {exc}")
            self.toggle.setChecked(True)  # open, so the operator sees what to fill in
            return
        language, vision = endpoints["language"], endpoints["vision"]
        try:
            self.on_use(language, vision)
        except Exception as exc:  # a provider library that is not installed, most likely
            self.note.setText(str(exc))
            self.say(f"The model was not changed: {exc}")
            return
        seeing = vision or language
        sight = "" if seeing.vision else " (cannot see images)"
        self.summary.setText(language.name + (f", vision {vision.name}" if vision else "") + sight)
        self.note.setText("In use.")
        self.toggle.setChecked(False)
