"""The images seen, measured in code: shift, the history, and the map.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-08
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

import numpy as np
import pytest
from test_schedules import Clock

from nis_assistant.frames import FrameHistory, sample_map, shift
from nis_assistant.images import image_statistics, signal_centroid

AXES = {"x": "right", "y": "up", "z": "deeper into the sample"}


def spot(row: int, col: int, shape=(96, 128), value=4000) -> np.ndarray:
    """A camera image with one bright disc, on a dark level of 100."""
    rows, cols = np.mgrid[: shape[0], : shape[1]]
    image = np.full(shape, 100.0)
    image[(rows - row) ** 2 + (cols - col) ** 2 <= 8**2] = value
    return image.astype(np.uint16)


def where(x=1000.0, y=-500.0, z=500.0, objective="Plan Apo 10x"):
    return {"position_um": {"x": x, "y": y, "z": z}, "objective": {"name": objective}}


def test_shift_finds_how_far_the_content_moved():
    before = spot(40, 60)
    moved = shift(before, spot(37, 65))  # 5 pixels right, 3 up
    assert moved["right"] == pytest.approx(5, abs=0.3) and moved["down"] == pytest.approx(
        -3, abs=0.3
    )
    assert moved["confidence"] > 0.2
    assert shift(before, np.zeros((10, 10))) is None  # not the same size


def test_the_signal_centroid_and_a_flat_image():
    assert signal_centroid(np.full((10, 10), 7.0)) is None
    centroid = signal_centroid(spot(24, 96).astype(float))
    assert centroid == {"row": pytest.approx(0.25, abs=0.02), "col": pytest.approx(0.75, abs=0.02)}
    assert image_statistics(spot(24, 96))["signal_centroid"]["row"] == pytest.approx(0.25, abs=0.02)


def test_an_image_is_kept_with_its_measures_and_the_move_that_centres_it():
    history = FrameHistory(Clock())
    entry = history.add(spot(24, 96), "look", where(), pixel_size_um=0.5, axes=AXES, label="before")
    brief = history.brief(entry)
    assert brief["n"] == 1 and brief["label"] == "before" and brief["objective"] == "Plan Apo 10x"
    # the spot sits a quarter of the field right of and above the centre
    assert brief["offset_um"] == {"right": pytest.approx(16, abs=1), "up": pytest.approx(12, abs=1)}
    # with +x moving the sample right, centring it means moving x by minus that
    assert brief["centre_move_um"]["x"] == pytest.approx(-16, abs=1)
    assert brief["centre_move_um"]["y"] == pytest.approx(-12, abs=1)
    # with +x moving the sample left, the other way
    flipped = history.add(spot(24, 96), "look", where(), 0.5, {**AXES, "x": "left"})
    assert flipped["measures"]["centre_move_um"]["x"] == pytest.approx(16, abs=1)
    assert history.find("before") is entry and history.find("after") is None


def test_comparing_images_measures_the_drift_in_um_or_in_pixels():
    clock = Clock()
    history = FrameHistory(clock)
    first = history.add(spot(40, 60), "look", where(), 0.5, AXES)
    clock.now += 180
    second = history.add(spot(37, 65), "look", where(), 0.5, AXES)
    (change,) = history.compare([first, second])
    since = change["since_first"]
    assert since["seconds"] == 180 and change["since_previous"] == since
    assert since["image_shift_um"] == {
        "right": pytest.approx(2.5, abs=0.2),
        "up": pytest.approx(1.5, abs=0.2),
    }
    # without a pixel calibration, the shift is in camera pixels
    history = FrameHistory(clock)
    first = history.add(spot(40, 60), "look", where(), None, AXES)
    second = history.add(spot(37, 65), "look", where(), None, AXES)
    (change,) = history.compare([first, second])
    assert change["since_first"]["image_shift_px"] == {
        "right": pytest.approx(5, abs=0.3),
        "up": pytest.approx(3, abs=0.3),
    }
    assert "image_shift_um" not in change["since_first"] and "offset_um" not in first["measures"]


def test_picking_images_by_count_numbers_or_range():
    history = FrameHistory(Clock())
    for _n in range(5):
        history.add(spot(40, 60), "look", where(), 0.5, AXES)
    assert [f["n"] for f in history.pick("last 2")] == [4, 5]
    assert [f["n"] for f in history.pick("1,4")] == [1, 4]
    assert [f["n"] for f in history.pick("2-3")] == [2, 3]
    assert [f["n"] for f in history.pick("3")] == [3]
    with pytest.raises(ValueError, match="no image 9"):
        history.pick("9")
    with pytest.raises(ValueError, match="labels are none"):
        history.pick("the first one")
    history.frames[1]["label"], history.frames[3]["label"] = "before", "after"
    assert [f["n"] for f in history.pick("before")] == [2]
    assert [f["n"] for f in history.pick("'Before', after")] == [2, 4]
    with pytest.raises(ValueError, match="labels are 'before', 'after'"):
        history.pick("later")


def test_the_oldest_copies_go_but_the_numbers_keep_counting():
    history = FrameHistory(Clock(), max_bytes=2 * 96 * 128 * 4)
    for _n in range(4):
        history.add(spot(40, 60), "look", where(), 0.5, AXES)
    assert [f["n"] for f in history.frames] == [3, 4]
    assert history.listing()["numbers"] == "3-4" and history.listing()["count"] == 2
    history.clear()
    assert history.listing() is None


def test_the_map_places_the_sample_and_finds_the_best_focus():
    clock = Clock()
    history = FrameHistory(clock)
    assert sample_map(history) is None
    # three images at the same place, the middle z sharpest: the focus is between them
    history.add(spot(48, 64) // 2, "look", where(z=500), 0.5, AXES)  # dimmer, less sharp
    history.add(spot(48, 64), "look", where(z=502), 0.5, AXES)
    history.add(spot(48, 64) // 3, "look", where(z=504), 0.5, AXES)
    flat = history.add(np.full((96, 128), 100, dtype=np.uint16), "look", where(z=506), 0.5, AXES)
    history.add(spot(48, 64), "look", where(z=502), 0.5, AXES, label="cell")
    clock.now += 30
    found = sample_map(history)
    (row,) = found["objectives"]
    assert row["objective"] == "Plan Apo 10x"
    assert row["sample_at"]["x"] == pytest.approx(1000, abs=1)  # the spot is centred
    assert row["sample_at"]["y"] == pytest.approx(-500, abs=1)
    assert 500 < row["best_focus"]["z"] < 504 and row["best_focus"]["plus_minus"] == 1.0
    assert row["left_out"] == {flat["n"]: "no signal"}
    assert found["labels"]["cell"]["z"] == 502 and found["labels"]["cell"]["age_s"] == 30
    # at the edge of the z values seen, the map says which way to search
    history = FrameHistory(clock)
    history.add(spot(48, 64) // 2, "look", where(z=500), 0.5, AXES)
    history.add(spot(48, 64), "look", where(z=502), 0.5, AXES)
    assert sample_map(history)["objectives"][0]["best_focus"]["edge"] == "search higher z"
