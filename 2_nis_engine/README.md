# nis-engine

Run [useq-schema](https://github.com/pymmcore-plus/useq-schema) acquisitions on
a Nikon microscope through NIS-Elements.

This is part 2 of three; see the [overview](../README.md). It needs part 1
(`nis-bridge`) running in NIS-Elements. The [tutorial](docs/tutorial.md) is
a longer walk-through that builds up from a first Z-stack to a
multi-position time-lapse; this page is the complete documentation of the
package.

## Contents

1. [The idea](#the-idea)
2. [Install](#install)
3. [A first acquisition, step by step](#a-first-acquisition-step-by-step)
4. [What happens during a run](#what-happens-during-a-run)
5. [Building up the experiment](#building-up-the-experiment)
6. [Checking a plan before running it](#checking-a-plan-before-running-it)
7. [Narrower limits for a session](#narrower-limits-for-a-session)
8. [Saving and loading sequences](#saving-and-loading-sequences)
9. [What each useq field does](#what-each-useq-field-does)
10. [useq v2](#useq-v2)
11. [When the engine says no](#when-the-engine-says-no)
12. [Good to know](#good-to-know)
13. [Tests](#tests)
14. [Files](#files)

## The idea

With the bridge alone you can snap an image, move, and change channel:
single steps. An experiment is a pattern of such steps: at each of these
positions, in each of these channels, a Z-stack, every few minutes for an
hour. Writing that as nested loops is possible, but each experiment needs
new loops, mistakes are easy, and the result is a heap of TIFF files with
the metadata in their names.

**useq-schema** describes an acquisition as a single object, an
`MDASequence` (multi-dimensional acquisition sequence): positions,
channels, a Z plan, a time plan, a grid plan. From that it works out every
image to take, in order, each as an `MDAEvent` that says: go to x, y, z; use
this channel at this exposure; snap. useq is the community's shared
description, not a microscope driver: the same sequence can be made by a GUI
(pymmcore-widgets, napari-micromanager) or by hand, and saved as a JSON file.

**pymmcore-plus** provides the `MDARunner`, which walks through the events
of a sequence, hands each one to an *engine* to carry out, and passes the
images that come back to a writer that saves them as one OME-TIFF with all
the metadata, or to a viewer.

**nis-engine** is the engine for Nikon. `NisEngine` takes each event from
the runner and carries it out through the bridge: move, select the optical
configuration, set the exposure, snap, return the image.

```
useq.MDASequence  ──►  MDARunner  ──►  NisEngine  ──►  NisClient ── socket ── bridge in NIS
(the experiment)       pymmcore-plus   this part       part 1 (nis-bridge)
                           │
                           └──►  OME-TIFF writer, viewers
```

Positions are NIS stage coordinates in micrometres (um), exactly as NIS
shows them; nothing here converts coordinate systems.

## Install

On the microscope computer, part 1 first, then this part:

```
pip install -e "./1_nis_bridge[test]"
pip install -e "./2_nis_engine[test]"
```

Start the bridge in NIS-Elements as part 1's README describes (or, to try
things without a microscope, `python -m nis_bridge.fake`).

## A first acquisition, step by step

Connect and read what the microscope offers:

```python
from nis_engine import NisEngine

engine = NisEngine()                                   # connects to the bridge
here = engine.client.request("get_position")
channels = engine.client.request("get_optical_configurations")
```

`engine.client` is the part-1 client, so every bridge request is available.

Describe the experiment. A Z-stack of 4 um in 1 um steps, in the first
channel, at the current position:

```python
import useq

sequence = useq.MDASequence(
    stage_positions=[{"x": here["x"], "y": here["y"], "z": here["z"]}],
    channels=[{"config": channels[0], "exposure": 20}],
    z_plan={"range": 4, "step": 1},
)
print(sequence.sizes)              # {'p': 1, 'c': 1, 'z': 5}
```

Read it as: at this position, in this channel at 20 ms, planes from 2 um
below to 2 um above the position's z, 1 um apart. The axis letters are
useq's: `p` positions, `c` channels, `z` planes, `t` time points, `g` grid
tiles. `for event in sequence` lists the five events with their z.

Run it:

```python
from pymmcore_plus.mda import MDARunner

runner = MDARunner()
runner.set_engine(engine)
runner.run(sequence, output="first_stack.ome.tiff")
```

The stage goes to the first plane, NIS captures five images, and
`first_stack.ome.tiff` appears in the working folder. Open it in Fiji (drag
it in; Bio-Formats reads OME-TIFF) or napari: a stack of five planes, with
the Z positions and the channel name in the metadata. With more than one
position, the writer makes a folder named after the output, with one file
per position inside.

## What happens during a run

The runner calls the engine in a fixed order. The error messages and the
metadata refer to these moments.

1. **Setup.** The engine reads what the microscope offers (stage limits,
   optical configurations, fitted objectives, whether there is a PFS), and
   snaps one image with the current settings, so that the writer knows the
   image size and pixel size before the first frame. This is why a run
   captures one more image than the sequence has.
2. **Check.** Before anything moves, the whole plan is checked (see
   [Checking a plan](#checking-a-plan-before-running-it)). One bad event and
   the whole sequence is refused.
3. **Each event.** Move (only the axes the event names), select the channel
   if it changed, set the exposure if it changed, apply properties (objective
   slot, PFS on or off); then snap, or run the focus action. The image goes
   to the runner with its metadata: position, pixel size, exposure, time.
4. **Teardown.** Temporary images are removed, and the PFS is put back the
   way the run found it, if NIS still answers. Other settings (stage
   position, objective, optical configuration) stay as the run left them.

## Building up the experiment

Each of these is a change to the sequence above; they combine freely.

**Two channels**, each with its own exposure. With a Z plan this gives
channels x planes images; the default axis order `tpgcz` takes each
channel's stack in one go, which keeps the filter wheel still.

```python
channels=[{"config": "DAPI", "exposure": 20}, {"config": "FITC", "exposure": 100}],
```

**A single-plane channel** within a stack, for example brightfield:

```python
{"config": "BF", "exposure": 5, "do_stack": False},
```

**Several positions.** Read them from NIS first: move there with the
joystick, call `get_position`, and note the numbers. Each position carries
its own z, so a relative Z plan is laid out around each position's own focus.

```python
stage_positions=[
    {"x": 100.0, "y": 200.0, "z": 3000.0, "name": "well_A1"},
    {"x": 9100.0, "y": 200.0, "z": 3010.0, "name": "well_A2"},
],
```

**A time-lapse.** Waiting between time points is the runner's job. Time is
the outermost axis, so each time point visits every position.

```python
time_plan={"interval": 300, "loops": 12},   # every 5 minutes, 12 times
```

**Tiles.** A grid of overlapping tiles around each position needs the size
of the camera field in um. The engine measures it with one image and NIS's
pixel calibration for the objective in use:

```python
width, height = engine.field_of_view()      # takes one image; ValueError without a calibration
grid_plan={"rows": 2, "columns": 2, "overlap": (10, 10), "fov_width": width, "fov_height": height},
```

Stitching is a separate step (Fiji, for example); the OME-TIFF carries each
tile's stage position.

**Focus with the Perfect Focus System** at each time point and position:

```python
autofocus_plan=useq.AxesBasedAF(axes=("t", "p")),
```

The engine switches the PFS on, waits for the lock, and switches it off
again so it does not fight the Z moves that follow. Later steps at that
position are shifted in Z by the distance the focus moved, so the stack
stays centred on the focus found.

**Change objective** or switch the PFS within a sequence, as properties on
a channel or position:

```python
{"config": "DAPI", "exposure": 20, "properties": [("Nosepiece", "Position", 2)]},
```

A complete example, two wells, two channels, 11-plane stacks, focus locked
at each visit, every 10 minutes for an hour:

```python
sequence = useq.MDASequence(
    stage_positions=[
        {"x": 100.0, "y": 200.0, "z": 3000.0, "name": "A1"},
        {"x": 9100.0, "y": 200.0, "z": 3010.0, "name": "A2"},
    ],
    channels=[{"config": "DAPI", "exposure": 20}, {"config": "FITC", "exposure": 100}],
    z_plan={"range": 10, "step": 1},
    time_plan={"interval": 600, "loops": 6},
    autofocus_plan=useq.AxesBasedAF(axes=("t", "p")),
)
print(sequence.sizes)            # {'t': 6, 'p': 2, 'c': 2, 'z': 11}: 264 images
engine.check(sequence)
runner.run(sequence, output="wells.ome.tiff")   # a folder wells/ with A1 and A2
```

## Checking a plan before running it

Before anything moves, the engine checks the whole plan and refuses it as a
whole if something is wrong:

- every position against the stage limits;
- every channel name against the NIS optical configurations;
- every property and action, including their values;
- relative Z plans and grids, which need a stage position with x, y and z to be
  laid out around (otherwise useq produces offsets around 0 um, and the stage
  would be sent there);
- tiling grids, which need the camera field in um (otherwise useq places the
  tiles 1 um apart).

`engine.check(sequence)` runs the same checks without moving or imaging, and
returns the steps it would take, so you can look at a plan first:

```python
events = engine.check(sequence)   # raises ValueError naming the first problem
print(len(events), "events")
```

## Narrower limits for a session

NIS has its own stage limits, which the engine always respects. To stay
inside a smaller area, for example that of one slide, so that a typo in a
position cannot send the objective into the stage insert, narrow the limits
for the session:

```python
engine.set_limits(x=(-5000, 5000), z=(None, 3000))  # um; None or a missing axis: NIS's own
print(engine.limits())                              # the limits now in force
```

These come on top of the NIS limits: an axis can get narrower, never wider.
One check can only happen during the run: after a focus action, later Z moves
at that position include the focus correction, and a corrected move that would
leave the limits stops the run at that point.

## Saving and loading sequences

A sequence is data, and saves as a small JSON file that other useq tools
can load:

```python
open("wells.useq.json", "w").write(sequence.model_dump_json(exclude_defaults=True, indent=2))
sequence = useq.MDASequence.from_file("wells.useq.json")
```

The same file can be made in pymmcore-widgets' MDA editor or loaded into
napari-micromanager. The positions are the one part that does not travel
between instruments, since they are stage coordinates of this one.

## What each useq field does

The useq fields themselves (every Z, time and grid plan, well plates,
per-position sequences, the axis order) are documented in
[docs/useq.md](../../docs/useq.md). This table is what the engine does with
them.

| Field | On the Nikon |
|---|---|
| `x_pos`, `y_pos`, `z_pos` | Absolute stage position (um). Missing means "stay". |
| `channel.config` | Name of a NIS optical configuration. `group` is ignored. |
| `exposure` | Camera exposure (ms). |
| `properties` | `("Nosepiece", "Position", 2)` turns to slot 2. `("PFS", "State", "On")` or `"Off"` switches the Perfect Focus System (PFS). |
| `action` | `AcquireImage` snaps an image. `HardwareAutofocus` locks focus with the PFS, then switches it off. `CustomAction(name="autofocus", data={"range_um": 50, "speed": 30})` runs the NIS image-based focus sweep. |
| `min_start_time` | Handled by the runner (time-lapse). |

After a focus action, later steps at the same position are shifted in Z by
the distance the focus moved.

Not supported, and refused before the run: camera ROI, SLM images, other
custom actions, and colour cameras (set the camera to monochrome in NIS).
`keep_shutter_open` is ignored because NIS handles the shutter.

## useq v2

The new `useq.v2.MDASequence` runs the same way (`import useq.v2 as v2`, then
`v2.MDASequence(...)` with the same fields), and adds axes of your own,
nested sequences, skip rules and event transforms. Four cautions with
useq-schema 0.9.2: the pymmcore-plus file writers (0.18) save a v2 sequence
as one flat stack of images, without its channel and Z axes, so use the
classic `useq.MDASequence` when the saved file matters; a v2 sequence
cannot be read back from its own JSON; an autofocus plan focuses at the
first plane of a Z-stack, where the classic form focuses at the position's
own z; and a channel's `do_stack`, `acquire_every` and `z_offset` are
ignored. [docs/useq.md](../../docs/useq.md) documents both APIs in full.

## When the engine says no

The check refuses a plan with a `ValueError` naming the first problem. The
common ones:

| Message | What to change |
|---|---|
| `event p=1, c=0, z=3: z = 3215 um is outside the stage limits [..] um` | Lower the position's z, shorten the Z range, or widen a limit you set. |
| `'fitc' is not an optical configuration in NIS-Elements; known: DAPI, FITC` | Names must match NIS exactly, including case. |
| `the Z plan is relative, but a stage position has no z` | Give each position a z, or use an absolute plan such as `ZTopBottom`. |
| `the grid needs the field of view` | Add `fov_width` and `fov_height`, from `engine.field_of_view()`. |
| `NIS reports no pixel calibration for the objective in use` | Calibrate the objective in NIS, or give the field size yourself. |
| `the camera gives colour or multi-plane images` | Set the camera to monochrome in NIS. |

During a run, a focus that fails does not stop the run: the engine logs a
warning and continues without the shift (as pymmcore-plus does). A lost
connection to the bridge does stop it; restart `start_bridge.mac` in NIS
and call `engine.reconnect()`, which keeps the session limits.

## Good to know

- The engine and NIS must run on the same computer: each image is saved by
  NIS as a temporary TIFF and read back.
- NIS cannot report the camera exposure. Frame metadata carries the exposure
  NIS applied when the sequence set one, or 0 when it set none (when the
  optical configuration brought its own).
- `NisEngine(connect=False)` starts disconnected, for a program that should
  open before NIS-Elements is running; `engine.reconnect()` connects it later.

## Tests

```
pip install -e ".[test]"
pytest                    # offline, a few seconds, over nis-bridge's fake NIS
pytest -m hardware -s     # on NIS-Elements with the bridge running (step 2 in docs/testing.md)
ruff check . && ruff format --check .   # lint and formatting, rules in pyproject.toml
```

## Files

| File | What it is |
|---|---|
| `nis_engine/checks.py` | May this sequence run? What an event may hold, the limit check, the plan checks. The place to look up or extend what the engine accepts. |
| `nis_engine/engine.py` | `NisEngine`: runs each step on the bridge, the session limits, the field of view. |
| `docs/tutorial.md` | The walk-through, from a first Z-stack to a multi-position time-lapse. |

MIT license. Thom de Hoog, Center for Microscopy and Image Analysis (ZMB),
University of Zurich. thom.dehoog@zmb.uzh.ch, thomdehoog@gmail.com. 2026-09-27.
