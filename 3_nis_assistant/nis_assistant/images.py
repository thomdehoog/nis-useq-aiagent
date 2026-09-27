"""Pictures for the model and the window: one snap, its statistics, and a PNG.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
"""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

import numpy as np
import tifffile
from nis_bridge.settings import SNAP_TIMEOUT_S
from PIL import Image
from pydantic_ai import BinaryContent

from .settings import LOOK_BIN, LOOK_MAX_SIDE


def snap(client) -> np.ndarray:
    """One image with the current settings, outside any acquisition run."""
    with tempfile.TemporaryDirectory(prefix="nis_assistant_look_") as folder:
        path = Path(folder) / "look.tif"
        client.request("snap", path=str(path), timeout=SNAP_TIMEOUT_S)
        return tifffile.imread(path)


def _gray(image: np.ndarray) -> np.ndarray:
    """One 2-D plane: colour images are averaged, stacks are projected."""
    data = image.astype(np.float64)
    if data.ndim == 3:
        data = data[..., :3].mean(axis=-1) if data.shape[-1] in (3, 4) else data.max(axis=0)
    return data


def image_statistics(image: np.ndarray) -> dict[str, float]:
    """Numbers that help judge an image without a model: brightness, saturation, sharpness."""
    data = _gray(image)
    top = np.iinfo(image.dtype).max if image.dtype.kind in "ui" else image.max()
    saturated = image >= top
    if saturated.ndim == 3:  # a pixel counts once, whichever colour or plane is saturated
        colour = image.shape[-1] in (3, 4)
        saturated = saturated.any(axis=-1 if colour else 0)
    gy, gx = np.gradient(data)
    return {
        "min": float(data.min()),
        "max": float(data.max()),
        "mean": round(float(data.mean()), 1),
        "saturated_percent": round(float(saturated.mean() * 100), 2),
        "sharpness": round(float(np.mean(gx**2 + gy**2) / max(data.mean(), 1.0)), 2),
    }


def as_png(image: np.ndarray, bin: int = LOOK_BIN, max_side: int = LOOK_MAX_SIDE) -> BinaryContent:
    """An 8-bit PNG for the vision model: binned, contrast stretched, at most ``max_side`` px.

    Each output pixel is the mean of a ``bin`` x ``bin`` block; a still larger
    image is binned further until it fits ``max_side``. Colour images stay in
    colour; other multi-plane images are projected.
    """
    colour = image.ndim == 3 and image.shape[-1] in (3, 4)
    data = image[..., :3].astype(np.float64) if colour else _gray(image)
    step = max(bin, int(np.ceil(max(data.shape[:2]) / max_side)))
    data = binned(data, step)
    lo, hi = np.percentile(data, (0.5, 99.5))
    scaled = np.clip((data - lo) / max(hi - lo, 1e-9) * 255, 0, 255).astype(np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(scaled).save(buffer, format="PNG")
    return BinaryContent(data=buffer.getvalue(), media_type="image/png")


def binned(data: np.ndarray, n: int) -> np.ndarray:
    """The image with each n x n block replaced by its mean (a ragged edge is dropped)."""
    if n <= 1:
        return data
    h, w = (data.shape[0] // n) * n, (data.shape[1] // n) * n
    data = data[:h, :w]
    shape = (h // n, n, w // n, n, *data.shape[2:])
    return data.reshape(shape).mean(axis=(1, 3))
