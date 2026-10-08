"""The images the assistant has seen this session, and what code measures on them.

Every image a look takes, and the last image of each acquisition, is kept here
as a small copy with its number, time, where it was taken (stage position
and objective), an optional label, and a few measured numbers: brightness,
saturation, sharpness, where the signal sits in the field, and the stage move
that would bring it to the centre. With two of these copies, code can measure
how far the sample has moved between them (by phase correlation, a standard
way to find the shift between two pictures) in micrometres when NIS has a
pixel calibration for the objective, or in pixels otherwise. The eyes (the
vision model) still judge what a picture shows; this gives the assistant the
numbers it should not guess at, so "has it drifted?" is a measurement.

The map is one entry of the microscope state, derived from the history: per
objective, where the sample is in stage coordinates, the best focus found so
far from the sharpness of the images taken at that place, and the labelled
places ("look and label this 'before'"), so a request can find them again.

The history is used from two threads (a look on the turn's thread, an
acquisition on its own): a lock keeps every change whole.

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

import numpy as np

from .images import binned, image_statistics
from .settings import (
    CLOCK_FORMAT,
    FRAME_COPY_SIDE,
    FRAME_HISTORY_BYTES,
    LOOK_FRAMES_MAX,
    MAP_PLACE_FRAMES,
    MAP_SAME_PLACE_UM,
    MAP_SATURATED_MAX_PERCENT,
    MAP_SIGNAL_MIN,
)


class FrameHistory:
    """The images of the session, newest last, as small copies with their measures.

    The copies are capped at FRAME_HISTORY_BYTES in all; the oldest go first,
    and the numbers keep counting. ``clock`` gives the time in seconds.
    """

    def __init__(
        self, clock: Callable[[], float] = time.time, max_bytes: int = FRAME_HISTORY_BYTES
    ) -> None:
        self.clock = clock
        self.max_bytes = max_bytes
        self.frames: list[dict[str, Any]] = []
        self._count = 0
        self._lock = threading.Lock()

    def add(
        self,
        image: np.ndarray,
        source: str,
        context: dict[str, Any],
        pixel_size_um: float | None = None,
        axes: dict[str, str] | None = None,
        label: str | None = None,
        stats: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Keep an image: a small copy, where it was taken (``context`` is the stage
        position and objective, as ``Microscope.where`` gives them), and its measures.
        Returns the new entry."""
        stats = stats or image_statistics(image)
        plane = _plane(image)
        step = max(1, int(np.ceil(max(plane.shape) / FRAME_COPY_SIDE)))
        small = binned(plane, step).astype(np.float32)
        field_um = None
        if pixel_size_um:
            field_um = (plane.shape[1] * pixel_size_um, plane.shape[0] * pixel_size_um)
        with self._lock:
            self._count += 1
            entry: dict[str, Any] = {
                "n": self._count,
                "t": self.clock(),
                "source": source,
                "position_um": context.get("position_um"),
                "objective": (context.get("objective") or {}).get("name"),
                "measures": _measures(stats, plane.shape, field_um, axes or {}),
                "image": small,
                "bin": step,  # camera pixels per pixel of the copy
                "field_um": field_um,
            }
            if label:
                entry["label"] = str(label)
            self.frames.append(entry)
            while (
                len(self.frames) > 1
                and sum(f["image"].nbytes for f in self.frames) > self.max_bytes
            ):
                self.frames.pop(0)
            return entry

    def pick(self, chosen: Any) -> list[dict[str, Any]]:
        """The frames ``chosen`` names: "last 3", "4", "1,7", "3-10", or labels, one or
        more ("before", "before, after"). At most LOOK_FRAMES_MAX; a ValueError names a
        frame or label the history does not hold."""
        with self._lock:
            frames = list(self.frames)
        by_number = {f["n"]: f for f in frames}
        text = str(chosen).strip().lower()
        labels = {f["label"].lower(): f for f in frames if f.get("label")}
        wanted = [part.strip().strip("'\"") for part in text.split(",")]
        if wanted and all(part in labels for part in wanted):
            picked = [labels[part] for part in wanted]
        elif match := re.fullmatch(r"last\s*(\d+)", text):
            picked = frames[-int(match.group(1)) :] if int(match.group(1)) > 0 else []
        elif match := re.fullmatch(r"(\d+)\s*-\s*(\d+)", text):
            low, high = int(match.group(1)), int(match.group(2))
            picked = [f for f in frames if low <= f["n"] <= high]
        elif re.fullmatch(r"\d+(\s*,\s*\d+)*", text):
            numbers = [int(n) for n in text.split(",")]
            missing = [n for n in numbers if n not in by_number]
            if missing:
                held = f"{frames[0]['n']} to {frames[-1]['n']}" if frames else "none"
                raise ValueError(
                    f"no image {', '.join(map(str, missing))}; the history holds {held}"
                )
            picked = [by_number[n] for n in numbers]
        else:
            known = ", ".join(repr(f["label"]) for f in frames if f.get("label")) or "none"
            raise ValueError(
                "frames is 'last 3', image numbers like '1,7', a range like '3-10', or a "
                f"label; the labels are {known}"
            )
        if len(picked) > LOOK_FRAMES_MAX:
            raise ValueError(f"at most {LOOK_FRAMES_MAX} images in one look")
        return picked

    def find(self, label: str) -> dict[str, Any] | None:
        """The newest frame with this label, or None."""
        with self._lock:
            for entry in reversed(self.frames):
                if entry.get("label") == label:
                    return entry
        return None

    @staticmethod
    def brief(entry: dict[str, Any]) -> dict[str, Any]:
        """An image as the model reads it: number, time, source, label, where, measures."""
        out: dict[str, Any] = {
            "n": entry["n"],
            "time": time.strftime(CLOCK_FORMAT, time.localtime(entry["t"])),
            "source": entry["source"],
        }
        if entry.get("label"):
            out["label"] = entry["label"]
        out["position_um"] = entry["position_um"]
        out["objective"] = entry["objective"]
        out.update(entry["measures"])
        return out

    @staticmethod
    def compare(picked: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """For each image after the first: how far the content moved since the first
        and since the previous one, and how the sharpness and brightness changed."""
        out = []
        for index, entry in enumerate(picked[1:], 1):
            row = {"n": entry["n"]}
            for name, other in (("since_first", picked[0]), ("since_previous", picked[index - 1])):
                row[name] = _change(other, entry)
            out.append(row)
        return out

    def listing(self) -> dict[str, Any] | None:
        """For the microscope state: how many images, their labels, and the last three."""
        with self._lock:
            frames = list(self.frames)
        if not frames:
            return None
        keys = ("max", "saturated_percent", "sharpness", "centre_move_um")
        last = [
            {
                "n": f["n"],
                "time": time.strftime(CLOCK_FORMAT, time.localtime(f["t"])),
                "source": f["source"],
                **{k: f["measures"][k] for k in keys if k in f["measures"]},
            }
            for f in frames[-3:]
        ]
        return {
            "count": len(frames),
            "numbers": f"{frames[0]['n']}-{frames[-1]['n']}",
            "labels": {f["label"]: f["n"] for f in frames if f.get("label")},
            "last": last,
        }

    def clear(self) -> None:
        with self._lock:
            self.frames, self._count = [], 0


def _plane(image: np.ndarray) -> np.ndarray:
    """One 2-D plane of an image: colour averaged, a stack projected."""
    data = np.asarray(image, dtype=np.float64)
    if data.ndim == 3:
        data = data[..., :3].mean(axis=-1) if data.shape[-1] in (3, 4) else data.max(axis=0)
    return data


def _measures(
    stats: dict[str, Any],
    shape: tuple[int, ...],
    field_um: tuple[float, float] | None,
    axes: dict[str, str],
) -> dict[str, Any]:
    """The numbers kept with an image, and where its signal sits."""
    out = {k: stats[k] for k in ("max", "mean", "saturated_percent", "sharpness") if k in stats}
    centroid = stats.get("signal_centroid")
    if centroid is None:
        return {**out, "signal": "none"}
    # The offset of the signal from the centre, as a fraction of the field, right and up.
    right, up = centroid["col"] - 0.5, 0.5 - centroid["row"]
    out["offset_px"] = {"right": round(right * shape[1], 1), "up": round(up * shape[0], 1)}
    if field_um is not None:
        out["offset_um"] = {
            "right": round(right * field_um[0], 1),
            "up": round(up * field_um[1], 1),
        }
        # The stage move that brings the signal to the centre: the operator's choice of
        # what +x and +y do to the picture says the sign.
        sign_x = 1.0 if axes.get("x", "right") == "right" else -1.0
        sign_y = 1.0 if axes.get("y", "up") == "up" else -1.0
        out["centre_move_um"] = {
            "x": round(-right * field_um[0] * sign_x, 1),
            "y": round(-up * field_um[1] * sign_y, 1),
        }
    return out


def shift(before: np.ndarray, after: np.ndarray) -> dict[str, float] | None:
    """How far the content moved from ``before`` to ``after``, in pixels of the copies
    (right and down), by phase correlation, with a confidence from 0 to 1 (the share
    of the correlation in its peak). None when the two are not the same size."""
    a = np.asarray(before, dtype=np.float64)
    b = np.asarray(after, dtype=np.float64)
    if a.shape != b.shape or a.ndim != 2:
        return None
    a, b = a - a.mean(), b - b.mean()
    cross = np.fft.fft2(b) * np.conj(np.fft.fft2(a))
    correlation = np.fft.ifft2(cross / (np.abs(cross) + 1e-9)).real
    row, col = np.unravel_index(int(np.argmax(correlation)), correlation.shape)
    peak = float(correlation[row, col])

    def centred(index: int, size: int) -> int:
        return index - size if index > size // 2 else index

    def refine(values: np.ndarray, index: int) -> float:
        # A parabola through the peak and its neighbours gives a fraction of a pixel.
        left, mid, right = values[index - 1], values[index], values[(index + 1) % len(values)]
        bend = left - 2 * mid + right
        return 0.0 if bend == 0 else float(0.5 * (left - right) / bend)

    down = centred(row, a.shape[0]) + refine(correlation[:, col], row)
    across = centred(col, a.shape[1]) + refine(correlation[row, :], col)
    return {
        "right": round(float(across), 2),
        "down": round(float(down), 2),
        "confidence": round(peak, 3),
    }


def _change(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    change = {
        "seconds": round(after["t"] - before["t"], 1),
        "sharpness": round(after["measures"]["sharpness"] - before["measures"]["sharpness"], 2),
        "max": round(after["measures"]["max"] - before["measures"]["max"], 1),
    }
    a, b = before["image"], after["image"]
    if a.shape == b.shape and before["objective"] == after["objective"]:
        moved = shift(a, b)
        if moved is not None:
            # From the copy's pixels to the camera's, and to micrometres when known.
            rows, cols = b.shape
            field = after.get("field_um")
            if field is not None:
                change["image_shift_um"] = {
                    "right": round(moved["right"] * field[0] / cols, 1),
                    "up": round(-moved["down"] * field[1] / rows, 1),
                }
            else:  # no pixel calibration: in camera pixels
                change["image_shift_px"] = {
                    "right": round(moved["right"] * after["bin"], 1),
                    "up": round(-moved["down"] * after["bin"], 1),
                }
            change["shift_confidence"] = moved["confidence"]
    return change


def flag(entry: dict[str, Any]) -> str | None:
    """Why an image cannot be measured from (no signal, saturated), or None."""
    measures = entry["measures"]
    if measures.get("signal") == "none":
        return "no signal"
    if measures["max"] - measures["mean"] < MAP_SIGNAL_MIN * max(measures["max"], 1.0):
        return "no signal"
    if measures["saturated_percent"] > MAP_SATURATED_MAX_PERCENT:
        return "saturated"
    return None


def sample_map(history: FrameHistory) -> dict[str, Any] | None:
    """The map: per objective, newest first, where the stage would centre the sample,
    the best focus from the images taken at that place, and the labelled places.
    Images that cannot be measured from are left out and named. None without images."""
    with history._lock:
        frames = list(history.frames)
    if not frames:
        return None
    now = history.clock()
    groups: dict[Any, list[dict[str, Any]]] = {}
    for entry in frames:
        groups.setdefault(entry["objective"], []).append(entry)
    out = []
    for objective, group in sorted(groups.items(), key=lambda g: -g[1][-1]["t"]):
        usable = [f for f in group if flag(f) is None and f["position_um"] is not None]
        row: dict[str, Any] = {"objective": objective}
        if place := _place(usable, now):
            row["sample_at"] = place
        if focus := _focus(usable, now):
            row["best_focus"] = focus
        left_out = {f["n"]: flag(f) for f in group if flag(f)}
        if left_out:
            row["left_out"] = left_out
        out.append(row)
    labels = {
        f["label"]: {**f["position_um"], "image": f["n"], "age_s": int(now - f["t"])}
        for f in frames
        if f.get("label") and f["position_um"] is not None
    }
    return {"objectives": out, **({"labels": labels} if labels else {})}


def _place(usable: list[dict[str, Any]], now: float) -> dict[str, Any] | None:
    """Where the stage would centre the sample: each image's position plus its centring
    move, the median over the last few images."""
    found = [
        (
            f["position_um"]["x"] + f["measures"]["centre_move_um"]["x"],
            f["position_um"]["y"] + f["measures"]["centre_move_um"]["y"],
            f,
        )
        for f in usable[-MAP_PLACE_FRAMES:]
        if f["measures"].get("centre_move_um")
    ]
    if not found:
        return None
    return {
        "x": round(float(np.median([p[0] for p in found])), 1),
        "y": round(float(np.median([p[1] for p in found])), 1),
        "images": [p[2]["n"] for p in found],
        "age_s": int(now - found[-1][2]["t"]),
    }


def _focus(usable: list[dict[str, Any]], now: float) -> dict[str, Any] | None:
    """The sharpest z among the images taken where the newest one was (within
    MAP_SAME_PLACE_UM in x and y), refined with a parabola through its neighbours; at
    the edge of the z values seen, which way to search."""
    if not usable:
        return None
    here = usable[-1]["position_um"]
    curve: dict[float, float] = {}
    for f in usable:
        p = f["position_um"]
        if all(abs(p[a] - here[a]) <= MAP_SAME_PLACE_UM for a in ("x", "y")):
            curve[p["z"]] = max(curve.get(p["z"], 0.0), f["measures"]["sharpness"])
    if len(curve) < 2:
        return None
    positions = sorted(curve)
    index = max(range(len(positions)), key=lambda i: curve[positions[i]])
    best = positions[index]
    out: dict[str, Any] = {
        "z": round(best, 1),
        "images_used": len(positions),
        "age_s": int(now - usable[-1]["t"]),
    }
    if index in (0, len(positions) - 1):
        out["edge"] = "search lower z" if index == 0 else "search higher z"
        return out
    (z0, z1, z2) = positions[index - 1 : index + 2]
    (v0, v1, v2) = (curve[z] for z in (z0, z1, z2))
    denominator = (z0 - z1) * (z0 - z2) * (z1 - z2)
    if denominator:
        a = (z2 * (v1 - v0) + z1 * (v0 - v2) + z0 * (v2 - v1)) / denominator
        b = (z2**2 * (v0 - v1) + z1**2 * (v2 - v0) + z0**2 * (v1 - v2)) / denominator
        if a < 0:
            out["z"] = round(float(np.clip(-b / (2 * a), z0, z2)), 1)
    out["plus_minus"] = round(min(z1 - z0, z2 - z1) / 2, 1)
    return out
