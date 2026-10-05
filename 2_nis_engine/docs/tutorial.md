# nis-engine, step by step

This is a walk-through for a biologist who wants to run multi-dimensional
acquisitions (channels, Z-stacks, positions, time points, tiles) on a Nikon
microscope from Python, with no experience of useq. It explains the idea,
takes a first Z-stack, and then builds up to more complex experiments. The
[README](../README.md) is the reference: what every useq field does on the
Nikon, and what the engine refuses.

You need part 1 (`nis-bridge`) working first: its
[tutorial](../../1_nis_bridge/docs/tutorial.md) gets you to a first snapped
image. Everything below assumes the bridge is running in NIS-Elements, or the
fake NIS (`python -m nis_bridge.fake`) is running in another window.

## The idea

With the bridge alone you can snap an image, move, and change channel: single
steps. An experiment is a pattern of such steps: "at each of these three
positions, in DAPI and in FITC, take 11 planes 1 um apart, every 5 minutes
for an hour". Writing that as nested loops is possible, but every experiment
needs new loops, mistakes are easy, and the result is a heap of TIFF files
with the metadata in their names.

**useq-schema** solves the first half. It is a small, widely used Python
library that describes an acquisition as a single object, an `MDASequence`
(multi-dimensional acquisition sequence): positions, channels, a Z plan, a
time plan, a grid plan. From that it works out every single image to take, in
order, each as an `MDAEvent` that says "go to x, y, z; use this channel at
this exposure; snap". useq is a description, not a microscope driver; the
same description can be made by a GUI (pymmcore-widgets, napari-micromanager)
or by hand, and saved as a JSON file.

**pymmcore-plus** solves the second half. Its `MDARunner` walks through the
events of a sequence, hands each one to an *engine* to carry out, and passes
the images that come back to a *writer* that saves them as one OME-TIFF with
all the metadata, or to a viewer.

**nis-engine** is the engine for Nikon. `NisEngine` takes each event from the
runner and carries it out through the bridge: move, select the optical
configuration, set the exposure, snap, return the image.

```
useq.MDASequence  ──►  MDARunner  ──►  NisEngine  ──►  bridge  ──►  microscope
(the experiment)       (the loop)      (this part)     (part 1)
                           │
                           └──►  OME-TIFF writer, viewers
```

The pieces you write are the sequence and three lines to run it.

## Step 1: install

In the same environment as part 1, in the repository folder:

```
pip install -e "./2_nis_engine[test]"
```

## Step 2: a first Z-stack

Open Python. First connect and read what the microscope offers:

```python
from nis_engine import NisEngine

engine = NisEngine()                      # connects to the bridge
here = engine.client.request("get_position")
channels = engine.client.request("get_optical_configurations")
print(here, channels)
```

`engine.client` is the part-1 client, so every bridge request is available
when you need it. Now the experiment. A Z-stack of 4 um in 1 um steps, in the
first channel, at the current position:

```python
import useq

sequence = useq.MDASequence(
    stage_positions=[{"x": here["x"], "y": here["y"], "z": here["z"]}],
    channels=[{"config": channels[0], "exposure": 20}],
    z_plan={"range": 4, "step": 1},
)
```

Read it as a sentence: at this position, in this channel at 20 ms, planes
from 2 um below to 2 um above the position's z, 1 um apart. Before running
it, see what useq makes of it:

```python
print(sequence.sizes)              # {'p': 1, 'c': 1, 'z': 5}
for event in sequence:
    print(event.index, event.z_pos)
```

Five events, with z from `here["z"] - 2` to `here["z"] + 2`. The axis letters
are useq's: `p` positions, `c` channels, `z` planes, `t` time points, `g`
grid tiles.

Now run it:

```python
from pymmcore_plus.mda import MDARunner

runner = MDARunner()
runner.set_engine(engine)
runner.run(sequence, output="first_stack.ome.tiff")
```

Watch NIS: the stage goes to the first plane, the image window flashes five
times, and `first_stack.ome.tiff` appears in your working folder. Open it in
Fiji (drag it in; Bio-Formats recognises OME-TIFF) and you will see a stack
of five planes, with the Z positions and the channel name in the metadata.
Nothing in the file name needed to carry that information.

One thing to know: you will see the image window flash six times, not five.
Every run begins with one extra snap at the current settings, so that the
writer learns the image size and pixel size before the first real frame.

## Step 3: understanding what happened

The runner called the engine in a fixed order. It helps to know it, because
the error messages and the metadata refer to these moments.

1. **Setup.** The engine reads what the microscope offers (stage limits,
   optical configurations, fitted objectives, whether there is a PFS), and
   takes the probe image.
2. **Check.** Before anything moves, every event is checked: each position
   against the stage limits, each channel name against the configurations,
   each property and action against what the Nikon can do. One bad event and
   the whole sequence is refused, with a message naming the event. Nothing
   has moved yet.
3. **Each event.** Move (only the axes the event names), select the channel
   if it changed, set the exposure if it changed, apply properties (objective
   slot, PFS on or off), then snap, or run the focus action. The image goes
   to the runner with its metadata (position, pixel size, exposure, time).
4. **Teardown.** Temporary files are removed, and the PFS is put back the way
   the run found it. The stage, objective and channel stay as the run left
   them.

You can run step 2 on its own, without imaging anything, to look at a plan
first:

```python
events = engine.check(sequence)       # raises ValueError naming the problem, or
print(len(events), "events")          # returns the events it would run
```

Get into the habit of calling `engine.check` on a new sequence before you
run it. It is quick and moves nothing.

## Step 4: building up the experiment

Each of these is a change to the `MDASequence` above. They combine freely.

**Two channels.** A list of channels; each has its own exposure.

```python
channels=[
    {"config": "DAPI", "exposure": 20},
    {"config": "FITC", "exposure": 100},
],
```

With the Z plan this gives channels x planes images. The order is channel
first, then planes (`axis_order` defaults to `tpgcz`: time, position, grid,
channel, Z), so each channel's stack is taken in one go, which keeps the
filter wheel still.

**A brightfield channel with a single plane.** Not every channel needs the
stack:

```python
{"config": "BF", "exposure": 5, "do_stack": False},
```

**Several positions.** A list, each with x, y and z, and a name if you like.
Read the positions from NIS first: move the stage by hand or with the
joystick, call `get_position`, and note the numbers.

```python
stage_positions=[
    {"x": 100.0, "y": 200.0, "z": 3000.0, "name": "well_A1"},
    {"x": 9100.0, "y": 200.0, "z": 3010.0, "name": "well_A2"},
],
```

Each position carries its own z, so a relative Z plan (`range` around the
position) is laid out around each position's own focus. This is why the
engine insists on a z for every position when the Z plan is relative: without
one, useq would produce planes around 0 um, and the stage would be sent there.

With more than one position the writer makes a *folder* named after the
output, with one OME-TIFF per position inside, instead of a single file.

**A time-lapse.**

```python
time_plan={"interval": 300, "loops": 12},   # every 5 minutes, 12 times
```

Waiting between time points is the runner's job; the engine only images.
Time is the outermost axis, so each time point visits every position.

**Tiles.** To image an area larger than the camera field, a grid of
overlapping tiles around each position. useq needs to know how large the
field is in micrometres to space the tiles; the engine can measure it with one
image, from the pixel calibration NIS has for the objective in use:

```python
width, height = engine.field_of_view()        # takes one image

grid_plan={
    "rows": 2, "columns": 2,
    "overlap": (10, 10),                       # percent
    "fov_width": width, "fov_height": height,
},
```

If `field_of_view` raises "no pixel calibration", calibrate the objective in
NIS, or give the field size yourself if you know it. Stitching the tiles together is a separate step, in Fiji or elsewhere;
the OME-TIFF carries each tile's stage position.

**Focus with the Perfect Focus System.** Lock focus at each time point and
position before imaging:

```python
autofocus_plan=useq.AxesBasedAF(axes=("t", "p")),
```

The engine switches the PFS on, waits for the lock, and switches it off
again so it does not fight the Z moves of the stack. The Z-stack that follows
is centred on the focus the PFS found, not on the planned z: the engine
remembers how far the focus moved at that position and shifts later Z moves
there by the same amount.

**Change objective within a sequence.** Properties on a channel or position:

```python
{"config": "DAPI", "exposure": 20, "properties": [("Nosepiece", "Position", 2)]},
```

The engine knows two properties: `("Nosepiece", "Position", slot)` and
`("PFS", "State", "On" or "Off")`. Anything else is refused at the check.

## Step 5: a complete example

Two wells, DAPI and FITC, 11-plane stacks, focus locked at each visit,
every 10 minutes for an hour:

```python
import useq
from pymmcore_plus.mda import MDARunner
from nis_engine import NisEngine

engine = NisEngine()

sequence = useq.MDASequence(
    stage_positions=[
        {"x": 100.0, "y": 200.0, "z": 3000.0, "name": "A1"},
        {"x": 9100.0, "y": 200.0, "z": 3010.0, "name": "A2"},
    ],
    channels=[
        {"config": "DAPI", "exposure": 20},
        {"config": "FITC", "exposure": 100},
    ],
    z_plan={"range": 10, "step": 1},
    time_plan={"interval": 600, "loops": 6},
    autofocus_plan=useq.AxesBasedAF(axes=("t", "p")),
)

print(sequence.sizes)            # {'t': 6, 'p': 2, 'c': 2, 'z': 11}: 264 images
engine.check(sequence)           # refuses the whole plan if anything is wrong

runner = MDARunner()
runner.set_engine(engine)
runner.run(sequence, output="wells.ome.tiff")   # makes a folder wells/ with A1 and A2
```

## Step 6: keep the stage inside a safe area

NIS has its own stage limits, and the engine always respects them. For one
session you can narrow them, for example to the area of one slide, so that a
typo in a position cannot send the objective into the stage insert:

```python
engine.set_limits(x=(-5000, 5000), y=(-3000, 3000), z=(None, 3200))
print(engine.limits())      # the limits now in force, NIS's narrowed by yours
```

`None` keeps NIS's own limit on that side. The limits can only get narrower
than NIS's, never wider, and a check against them happens before every move.

## Step 7: save, share and reuse a sequence

A sequence is data, and saves as a small JSON file:

```python
open("wells.useq.json", "w").write(sequence.model_dump_json(exclude_defaults=True, indent=2))
```

and loads again:

```python
sequence = useq.MDASequence.from_file("wells.useq.json")
```

This is the point of building on useq: the same file can be made in
pymmcore-widgets' MDA editor, loaded into napari-micromanager, or sent to a
colleague who runs it on a different microscope with a different engine. The
positions are the one part that does not travel, since they are stage
coordinates of this instrument.

## When the engine says no

The check refuses a plan with a message naming the first problem. The common
ones:

- *`event p=1, c=0, z=3: z = 3215 um is outside the stage limits [..] um`*:
  the top of a Z-stack went past the limit. Lower the position's z, shorten
  the range, or, if the limit is one you set, widen it.
- *`'fitc' is not an optical configuration in NIS-Elements; known: DAPI, FITC`*:
  names must match NIS exactly, including case.
- *`the Z plan is relative, but a stage position has no z`*: add a z to each
  position (or use an absolute plan such as `ZTopBottom`).
- *`the grid needs the field of view`*: add `fov_width` and `fov_height`,
  from `engine.field_of_view()`.
- *`the camera gives colour or multi-plane images`*: set the camera to
  monochrome in NIS.

During a run, a focus that fails does not stop the run: the engine logs a
warning and continues without the shift. A lost connection to the bridge
does stop it; restart `start_bridge.mac` in NIS and call `engine.reconnect()`.

## Good to know

- Positions are NIS stage coordinates in micrometres, exactly as NIS shows
  them. Nothing here converts between coordinate systems.
- The engine and NIS must run on the same computer: each image is saved by
  NIS as a temporary TIFF and read back.
- NIS cannot report the camera exposure. The metadata carries the exposure
  the sequence set, or 0 when it set none (when the optical configuration
  brought its own).
- useq has a newer form, `useq.v2.MDASequence`, which the engine also runs.
  Prefer the classic form shown here when the saved file matters: the
  pymmcore-plus writers currently save a v2 sequence as one flat stack.

## Where to go next

- The [README](../README.md): the table of every useq field and what it does
  on the Nikon, and the cautions on useq v2.
- The [useq-schema documentation](https://pymmcore-plus.github.io/useq-schema/)
  for every kind of Z, grid and time plan.
- Part 3, [nis-assistant](../../3_nis_assistant/docs/tutorial.md): the same
  sequences, planned in a conversation.
