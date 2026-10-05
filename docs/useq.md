# useq-schema: the classic API and useq v2

This is a complete guide to [useq-schema](https://github.com/pymmcore-plus/useq-schema),
the library the engine (part 2) and the assistant (part 3) use to describe
acquisitions, written for a biologist who wants to understand and write
sequences. It covers the classic `useq.MDASequence`, which every useq tool
reads and writes, and the newer `useq.v2.MDASequence`, which generalises it.
Everything here was checked against useq-schema 0.9.2, the version the
engine requires; the examples print what that version prints.

## Contents

1. [What useq is](#what-useq-is)
2. [The classic MDASequence](#the-classic-mdasequence)
   - [Positions](#positions)
   - [Channels](#channels)
   - [Z plans](#z-plans)
   - [Time plans](#time-plans)
   - [Grid and multi-point plans](#grid-and-multi-point-plans)
   - [Well plates](#well-plates)
   - [Axis order](#axis-order)
   - [Per-position sequences](#per-position-sequences)
   - [Hardware autofocus](#hardware-autofocus)
   - [Properties, actions and the setup event](#properties-actions-and-the-setup-event)
   - [The shutter and the timer](#the-shutter-and-the-timer)
3. [The MDAEvent](#the-mdaevent)
4. [Saving, loading and inspecting](#saving-loading-and-inspecting)
5. [useq v2](#useq-v2)
   - [Axes instead of fields](#axes-instead-of-fields)
   - [The classic fields still work](#the-classic-fields-still-work)
   - [Your own axis](#your-own-axis)
   - [Nested sequences](#nested-sequences)
   - [Skipping combinations](#skipping-combinations)
   - [Transforms](#transforms)
   - [Infinite time plans](#infinite-time-plans)
   - [What v2 does not do yet (0.9.2)](#what-v2-does-not-do-yet-092)
6. [What NisEngine does with each field](#what-nisengine-does-with-each-field)
7. [Classic or v2?](#classic-or-v2)

## What useq is

A multi-dimensional acquisition is a set of images taken over several
*axes*: time points, stage positions, grid tiles, channels and Z planes.
useq-schema describes such an acquisition as a single Python object, an
`MDASequence`, from which it generates the list of images to take, in order,
each as an `MDAEvent`: go to this x, y, z; use this channel at this exposure;
wait until this time; snap.

useq is only the description. It does not know any microscope. An
*acquisition engine*, such as `NisEngine` in this repository or the
pymmcore-plus engine for Micro-Manager, carries the events out. Because the
description is separate from the hardware, the same sequence can be built in
a GUI (the MDA widget of pymmcore-widgets, napari-micromanager), saved as a
JSON or YAML file, sent to a colleague, and run on a different microscope.

The five axes have one-letter names used throughout:

| Letter | Axis | Comes from |
|---|---|---|
| `t` | time point | `time_plan` |
| `p` | stage position | `stage_positions` |
| `g` | grid tile around a position | `grid_plan` |
| `c` | channel | `channels` |
| `z` | Z plane | `z_plan` |

Units are micrometres for positions, milliseconds for exposures, seconds
for time.

## The classic MDASequence

```python
import useq

sequence = useq.MDASequence(
    stage_positions=[{"x": 0, "y": 0, "z": 100, "name": "A"},
                     {"x": 500, "y": 0, "z": 110, "name": "B"}],
    channels=[{"config": "DAPI", "exposure": 20},
              {"config": "BF", "exposure": 5, "do_stack": False}],
    z_plan={"range": 2, "step": 1},
    time_plan={"interval": 60, "loops": 2},
)
```

Each field can be given as a plain dictionary, as above, or as the
corresponding useq object (`useq.Position(...)`, `useq.ZRangeAround(...)`);
useq converts the dictionaries. A sequence is immutable once made; to change
it, make a new one, or `sequence.replace(z_plan=...)`.

The sequence knows its sizes and generates its events:

```python
>>> sequence.sizes
{'t': 2, 'p': 2, 'g': 0, 'c': 2, 'z': 3}
>>> len(list(sequence))
16                      # not 2*2*2*3 = 24: BF takes one plane, not three
>>> for event in sequence:
...     print(dict(event.index), event.channel.config, event.x_pos, event.z_pos, event.min_start_time)
{'t': 0, 'p': 0, 'c': 0, 'z': 0} DAPI 0.0 99.0 0.0
{'t': 0, 'p': 0, 'c': 0, 'z': 1} DAPI 0.0 100.0 0.0
{'t': 0, 'p': 0, 'c': 0, 'z': 2} DAPI 0.0 101.0 0.0
{'t': 0, 'p': 0, 'c': 1, 'z': 1} BF 0.0 100.0 0.0
{'t': 0, 'p': 1, 'c': 0, 'z': 0} DAPI 500.0 109.0 0.0
...
```

Each event's `index` says where it sits on every axis; its other fields say
what to do. A Z plane is `None` for an axis that is not used, which an
engine reads as "stay where you are".

### Positions

`stage_positions` is a list of `Position` objects, each with `x`, `y`, `z`
(um) and an optional `name`. A tuple `(x, y, z)` or `(x, y)` is accepted
too. Any of the three may be left out (`None`): the engine then does not
move that axis. A position may also carry its own `sequence` (see
[Per-position sequences](#per-position-sequences)) and `properties` to set
when the stage arrives there.

```python
stage_positions=[(0, 0, 100), {"x": 500, "y": 0, "z": 110, "name": "B"}]
```

Positions are what the engine will send to the stage, in the stage's own
coordinates. A relative Z plan or grid is laid out *around* each position,
which is why those positions need a z, or an x and y.

### Channels

A `Channel` names a configuration (for NIS-Elements, an optical
configuration) and, optionally, how to image it:

| Field | Meaning | Default |
|---|---|---|
| `config` | the configuration's name (`"DAPI"`) | required |
| `group` | the configuration group; ignored by NisEngine | `"Channel"` |
| `exposure` | ms; `None` keeps the current exposure | `None` |
| `do_stack` | `False`: one plane at the position's z, even when there is a Z plan | `True` |
| `z_offset` | um added to every z of this channel (a focus offset between channels) | `0` |
| `acquire_every` | image this channel only every nth time point | `1` |
| `camera` | which camera; ignored by NisEngine | `None` |

A bare string `"DAPI"` is a channel with everything at its default.

```python
channels=[
    {"config": "DAPI", "exposure": 20},
    {"config": "FITC", "exposure": 100, "acquire_every": 2, "z_offset": 3},
    {"config": "BF", "exposure": 5, "do_stack": False},
]
```

With a 3-plane Z plan and 3 time points, this gives DAPI 3 planes every
time point; FITC 3 planes shifted up by 3 um at time points 0 and 2 only;
BF one plane at the position's z every time point. The events come out
with the channel as the inner loop within each time point and position
(see [Axis order](#axis-order)).

### Z plans

A Z plan is a list of Z positions. The *relative* ones are offsets around
each stage position's z; the *absolute* ones are stage coordinates and
ignore the position's z.

| Plan | Fields | Planes |
|---|---|---|
| `ZRangeAround` | `range`, `step` | symmetric around z: `{"range": 4, "step": 1}` gives -2, -1, 0, 1, 2 |
| `ZAboveBelow` | `above`, `below`, `step` | asymmetric: `{"above": 3, "below": 1, "step": 1}` gives -1, 0, 1, 2, 3 |
| `ZRelativePositions` | `relative` | an explicit list of offsets: `{"relative": [-5, 0, 5]}` |
| `ZTopBottom` | `top`, `bottom`, `step` | absolute, from `bottom` to `top` |
| `ZAbsolutePositions` | `absolute` | an explicit list of absolute z |

All have `go_up` (default `True`): planes from the lowest up. `useq` picks
the plan type from the fields you give, so a dictionary is enough. The
lowest plane is always visited; the highest is visited when the step
divides the range exactly, and otherwise is the last plane within the range.

```python
>>> list(useq.ZRangeAround(range=4, step=1))
[-2.0, -1.0, 0.0, 1.0, 2.0]
>>> useq.ZTopBottom(top=110, bottom=100, step=5).num_positions()
3
```

### Time plans

A time plan is a list of start times in seconds from the start of the
sequence. Each event gets its as `min_start_time`; the engine (or in
pymmcore-plus the runner) waits until that time before the event. Intervals
can be seconds (a number), a `timedelta`, or a dictionary such as
`{"minutes": 5}`.

| Plan | Fields | Example |
|---|---|---|
| `TIntervalLoops` | `interval`, `loops` | `{"interval": 60, "loops": 10}`: 10 time points a minute apart |
| `TDurationLoops` | `duration`, `loops` | `{"duration": 3600, "loops": 7}`: 7 time points over an hour |
| `TIntervalDuration` | `interval`, `duration` | `{"interval": 60, "duration": 600}`: every minute for ten minutes, 11 time points |
| `MultiPhaseTimePlan` | `phases`, a list of the above | fast then slow |

A list of plans is a multi-phase plan; the phases run one after the other,
and the first time point of a later phase coincides with the last of the
earlier one:

```python
>>> seq = useq.MDASequence(channels=["DAPI"], time_plan=[{"interval": 1, "loops": 3}, {"interval": 10, "loops": 2}])
>>> [e.min_start_time for e in seq]
[0.0, 1.0, 2.0, 12.0]
```

`prioritize_duration` (default `False`, except for `TIntervalDuration`)
tells an engine what to keep when imaging takes longer than the interval:
the number of frames, or the total duration.

`sequence.estimate_duration()` gives a rough total, from the exposures and
the time plan.

### Grid and multi-point plans

A grid plan images several fields of view. The *relative* grids are tiles
around each stage position; the *absolute* ones cover an area in stage
coordinates and ignore the positions' x and y.

| Plan | Fields | Tiles |
|---|---|---|
| `GridRowsColumns` | `rows`, `columns`, `relative_to` | a block of rows x columns tiles centred on the position (`relative_to="center"`, the default) or with its top-left tile on it (`"top_left"`) |
| `GridWidthHeight` | `width`, `height`, `relative_to` | as many tiles as cover a width x height area (um) around the position |
| `GridFromEdges` | `top`, `left`, `bottom`, `right` | absolute: tiles covering the rectangle between these stage coordinates |
| `GridFromPolygon` | `vertices`, `convex_hull`, `offset` | absolute: tiles covering a polygon |
| `RandomPoints` | `num_points`, `max_width`, `max_height`, `shape`, ... | random fields within an ellipse or rectangle around the position |

All grids share `overlap` (percent, one number or `(x, y)`), `mode` (the
visiting order: `row_wise`, `column_wise`, `row_wise_snake` (the default),
`column_wise_snake`, `spiral`), and `fov_width`, `fov_height`: the size of
one camera field in um, which decides how far apart the tiles are.

**The field of view must be given.** useq does not know your camera or
objective. Without `fov_width` and `fov_height`, a grid is laid out as if a
field were 1 um wide:

```python
>>> g = useq.MDASequence(stage_positions=[(1000, 2000, 5)], channels=["DAPI"],
...                      grid_plan={"rows": 2, "columns": 2})
>>> [(e.x_pos, e.y_pos) for e in g]
[(999.5, 2000.5), (1000.5, 2000.5), (1000.5, 1999.5), (999.5, 1999.5)]   # 1 um apart: useless
>>> g = useq.MDASequence(stage_positions=[(1000, 2000, 5)], channels=["DAPI"],
...                      grid_plan={"rows": 2, "columns": 2, "overlap": 10, "fov_width": 100, "fov_height": 80})
>>> [(e.x_pos, e.y_pos) for e in g]
[(955.0, 2036.0), (1045.0, 2036.0), (1045.0, 1964.0), (955.0, 1964.0)]   # 90 x 72 um apart (10 % overlap), snake order
```

This is why `NisEngine` refuses a grid without a field of view, and offers
`engine.field_of_view()` to measure it from NIS's pixel calibration.

### Well plates

`stage_positions` can be a `WellPlatePlan` instead of a list: a named plate
format, the stage coordinate of well A1, the wells to visit, and optionally
points within each well. useq expands it to positions named after the wells:

```python
>>> plan = useq.WellPlatePlan(plate="96-well", a1_center_xy=(0, 0), selected_wells=((0, 0), (0, 1)))
>>> [(p.name, p.x, p.y) for p in plan]
[('A1', 0.0, 0.0), ('A2', 9000.0, 0.0)]
```

`useq.registered_well_plate_keys()` lists the known formats; `rotation`
and `well_points_plan` handle a tilted plate and several fields per well.

### Axis order

`axis_order` says which axis is the outer loop and which the inner. The
default is `"tpgcz"`: for each time point, for each position, for each
tile, for each channel, each Z plane. So a Z-stack is taken in one channel
before switching to the next, which spares the filter wheel; `"tpgzc"`
would switch channels at every plane, for better registration between
channels at the cost of time. Any permutation of the five letters is
allowed, with two rules: `z` may not come before `p` when a position has
its own Z plan, and an absolute grid overrides the positions' x and y.

### Per-position sequences

A position may carry its own `sequence`, whose fields replace the main
sequence's at that position: a different Z range at a thicker sample, a
different grid, or its own channels.

```python
>>> s = useq.MDASequence(
...     stage_positions=[{"x": 0, "y": 0, "z": 100, "sequence": {"z_plan": {"range": 4, "step": 2}}},
...                      {"x": 1, "y": 1, "z": 5}],
...     channels=["DAPI"], z_plan={"range": 2, "step": 1})
>>> [(dict(e.index), e.z_pos) for e in s]
[({'p': 0, 'c': 0, 'z': 0}, 98.0), ({'p': 0, 'c': 0, 'z': 1}, 100.0), ({'p': 0, 'c': 0, 'z': 2}, 102.0),
 ({'p': 1, 'c': 0, 'z': 0}, 4.0),  ({'p': 1, 'c': 0, 'z': 1}, 5.0),   ({'p': 1, 'c': 0, 'z': 2}, 6.0)]
```

A per-position sequence may not have stage positions of its own.

### Hardware autofocus

`autofocus_plan=useq.AxesBasedAF(axes=("p",))` inserts a hardware autofocus
event (for Nikon: lock the Perfect Focus System) every time one of the named
axes changes: here, at each new position. `axes=("t", "p")` focuses at
every time point and position. The autofocus event comes before the first
image at that place, and is an event of its own with the action
`HardwareAutofocus`:

```python
>>> s = useq.MDASequence(stage_positions=[(0, 0, 0), (1, 1, 1)], channels=["DAPI"],
...                      z_plan={"range": 2, "step": 1}, autofocus_plan=useq.AxesBasedAF(axes=("p",)))
>>> [(dict(e.index), type(e.action).__name__, e.z_pos) for e in s]
[({'p': 0, 'c': 0, 'z': 0}, 'HardwareAutofocus', 0.0),    # at the position's own z
 ({'p': 0, 'c': 0, 'z': 0}, 'AcquireImage', -1.0),
 ({'p': 0, 'c': 0, 'z': 1}, 'AcquireImage', 0.0),
 ({'p': 0, 'c': 0, 'z': 2}, 'AcquireImage', 1.0),
 ({'p': 1, 'c': 0, 'z': 0}, 'HardwareAutofocus', 1.0), ...]
```

An autofocus plan cannot be combined with an absolute Z plan. The plan's
`autofocus_device_name` and `autofocus_motor_offset` are for systems with
an offset motor; NisEngine refuses an offset.

### Properties, actions and the setup event

An event can carry `properties`, a list of `(device, property, value)`
triples to set before imaging, on a channel or on a position:

```python
{"config": "DAPI", "exposure": 20, "properties": [("Nosepiece", "Position", 2)]}
```

useq does not define the device and property names; the engine does.
NisEngine knows `("Nosepiece", "Position", slot)` and
`("PFS", "State", "On" or "Off")` and refuses others.

An event's `action` says what to do there. `AcquireImage` (the default)
takes an image; `HardwareAutofocus` focuses; `CustomAction(name=..., data=...)`
is anything else an engine understands. NisEngine understands one custom
action, `CustomAction(name="autofocus", data={"range_um": 50, "speed": 30})`,
the NIS image-based focus sweep.

A sequence may have a `setup` event, which is not part of the iteration but
is handed to the engine before the run, for example to set a camera ROI or
binning. NisEngine does not use it.

### The shutter and the timer

`keep_shutter_open_across=("z",)` marks events with `keep_shutter_open=True`
when only the named axes change between one event and the next, so an
engine can leave the illumination on through a Z-stack. NisEngine ignores
it, since NIS-Elements controls the shutter. `reset_event_timer` marks the
first event of each time point, so that `min_start_time` counts from there.

## The MDAEvent

The engine never sees the sequence as a whole, only its events. An
`MDAEvent` has:

| Field | Meaning |
|---|---|
| `index` | `{"t": 0, "p": 1, "c": 0, "z": 2}`: where this event sits on each axis |
| `x_pos`, `y_pos`, `z_pos` | the absolute stage position in um, each `None` for "do not move this axis" |
| `pos_name` | the position's name |
| `channel` | `config` and `group`, or `None` for "keep the current channel" |
| `exposure` | ms, or `None` for "keep" |
| `min_start_time` | seconds since the start (or the last timer reset) before which the event may not begin |
| `properties` | `(device, property, value)` triples to set first |
| `action` | `AcquireImage`, `HardwareAutofocus` or a `CustomAction` |
| `roi`, `slm_image` | a camera region of interest; an image for a spatial light modulator (NisEngine refuses both) |
| `keep_shutter_open`, `reset_event_timer` | see above |
| `sequence` | the sequence this event came from |
| `metadata` | anything else, as a dictionary |

Events can be made by hand and given to a runner as a plain list, without
any sequence, which is how a script can do something useq's plans do not
cover. `NisEngine` checks events it is given directly in the same way.

## Saving, loading and inspecting

A sequence is data, and serialises to JSON or YAML with only the fields
that differ from the defaults:

```python
sequence.model_dump_json(exclude_defaults=True, indent=2)   # a string
sequence.yaml()                                             # a string
useq.MDASequence.from_file("plan.json")                     # .json or .yaml
useq.MDASequence.model_validate_json(text)
```

```yaml
channels:
- config: DAPI
  exposure: 20.0
- config: BF
  do_stack: false
  exposure: 5.0
stage_positions:
- name: A
  x: 0.0
  y: 0.0
  z: 100.0
time_plan:
  interval: 60.0
  loops: 2
z_plan:
  range: 2.0
  step: 1.0
```

This is the file that pymmcore-widgets and napari-micromanager save and
load, that the assistant writes next to each acquisition as `.useq.json`,
and that `plan_useq_sequence` reads. To inspect a sequence: `sizes`,
`shape`, `used_axes`, `iter_axis("z")`, `estimate_duration()`, and `print`,
which shows every field with its defaults filled in. A grid plan has
`plot()` to draw its tiles.

## useq v2

`useq.v2` is the generalisation of the classic sequence, in the same
package (`import useq.v2 as v2`). Where the classic sequence has five fixed
fields, one per axis, a v2 sequence is a tuple of *axes*, any number of
them, each of which yields its values and says what it contributes to every
event. The five classic plans are such axes, so a v2 sequence accepts the
classic fields unchanged, but you can also add axes of your own, nest a
sequence inside an axis value, and transform the stream of events.

### Axes instead of fields

```python
import useq.v2 as v2

v = v2.MDASequence(
    stage_positions=[{"x": 0, "y": 0, "z": 100}, {"x": 500, "y": 0, "z": 110}],
    channels=[{"config": "DAPI", "exposure": 20}],
    z_plan={"range": 2, "step": 1},
    time_plan={"interval": 60, "loops": 2},
)
>>> [a.axis_key for a in v.axes]
['t', 'p', 'c', 'z']
>>> type(v.axes[3]).__name__
'ZRangeAround'
```

The classic keyword arguments were converted into four axis objects in the
standard order. Each is an `AxisIterable`: it has an `axis_key` (the
letter), it iterates over its values (`list(v.axes[3])` gives the three Z
offsets), and it has `contribute_to_mda_event(value, index)`, which returns
the fields that value adds to an event: the Z plan contributes `z_pos`, the
channels plan contributes `channel` and `exposure`, the time plan
`min_start_time`, the positions `x_pos`, `y_pos`, `z_pos` and `pos_name`.

The sequence steps through every combination of the axes' values in
`axis_order` (the order of `axes` when not given), asks each axis for its
contribution, merges them into one `MDAEvent` (relative positions are added
to absolute ones, so a Z offset lands on the position's z), and runs the
events through the transforms. The events are the same `MDAEvent` objects
as in the classic API, so an engine that runs classic sequences runs v2
sequences too.

### The classic fields still work

`stage_positions`, `channels`, `z_plan`, `grid_plan`, `time_plan`,
`autofocus_plan`, `keep_shutter_open_across`, `metadata` and `axis_order`
mean what they do in the classic API, and the plan classes have the same
names and fields (`v2.ZRangeAround`, `v2.TIntervalLoops`,
`v2.GridRowsColumns`, ...). The sequence also still answers `sizes`,
`channels`, `z_plan` and the other classic properties, by looking up the
axis of that key. Positions are `v2.Position`, with an `is_relative` flag
in place of the classic `RelativePosition` class.

### Your own axis

Anything you would loop over can be an axis. `SimpleValueAxis` yields plain
values; override `contribute_to_mda_event` to say what each value means
for the event. An incubator temperature:

```python
from useq.v2 import SimpleValueAxis

class Temperature(SimpleValueAxis[float]):
    axis_key: str = "temp"
    def contribute_to_mda_event(self, value, index):
        return {"metadata": {"temperature": value}}

v = v2.MDASequence(axes=(Temperature(values=[25.0, 37.0]), v2.ChannelsPlan(values=["DAPI"])))
>>> [(dict(e.index), e.metadata) for e in v]
[({'temp': 0, 'c': 0}, {'temperature': 25.0}), ({'temp': 1, 'c': 0}, {'temperature': 37.0})]
```

An engine that knows what `temperature` in the metadata means can act on
it; one that does not, ignores it. `axes=` and the classic fields cannot be
mixed in one call; build the classic plans as axis objects
(`v2.ChannelsPlan(values=[...])`, `v2.StagePositions(values=[...])`,
`v2.ZRangeAround(...)`) and put them in `axes`.

### Nested sequences

A value of an axis can itself be a sequence, with `value` set to the value
it stands for. Its axes then replace the parent's axes of the same key, or
add new ones, for that value only. This is the general form of the classic
per-position sequence:

```python
v = v2.MDASequence(
    stage_positions=[
        v2.Position(x=0, y=0, z=0),
        v2.MDASequence(value=v2.Position(x=1, y=1, z=1), z_plan={"range": 2, "step": 1}),
    ],
    channels=["DAPI"],
)
>>> [(dict(e.index), e.x_pos, e.z_pos) for e in v]
[({'p': 0, 'c': 0}, 0.0, 0.0),
 ({'p': 1, 'c': 0, 'z': 0}, 1.0, 0.0), ({'p': 1, 'c': 0, 'z': 1}, 1.0, 1.0), ({'p': 1, 'c': 0, 'z': 2}, 1.0, 2.0)]
```

The first position gets one image; the second gets a Z-stack of its own.
The same works on any axis: a time point with extra channels, a channel
with its own Z range.

### Skipping combinations

Each axis has `should_skip(prefix)`, called with the combination about to be
emitted (the index, value and axis of every axis so far), and can return
`True` to drop it. This is how a v2 axis can express "this channel only at
every other time point" or "no Z-stack in brightfield", generally, for any
rule you can write in Python:

```python
class BrightfieldOnePlane(v2.ChannelsPlan):
    def should_skip(self, prefix):
        channel = prefix["c"][1]
        z = prefix.get("z")
        return channel.config == "BF" and z is not None and z[0] != 1   # keep the middle plane only
```

### Transforms

After the events are built, each passes through the sequence's
`transforms`, each of which may change it, drop it, or insert events
around it. Three come with useq, and the sequence adds them itself when
the corresponding field is set:

| Transform | Added when | Does |
|---|---|---|
| `ResetEventTimerTransform` | there is a time axis | marks the first event of each time point with `reset_event_timer` |
| `AutoFocusTransform` | `autofocus_plan` is set | inserts the `HardwareAutofocus` events |
| `KeepShutterOpenTransform` | `keep_shutter_open_across` is set | sets `keep_shutter_open` between events that differ only on those axes |

A transform of your own is a callable `(event, previous_event, make_next_event)
-> list[MDAEvent]`: for example one that inserts a wash step between
positions, or doubles the exposure of every tenth frame.

### Infinite time plans

A v2 `TIntervalDuration` without a `duration` runs forever: the sequence
yields events until the run is stopped, and `sizes` raises
`Cannot determine length of infinite time plan`. (In 0.9.2 `is_finite()`
still returns `True` for such a sequence; do not rely on it.)

### What v2 does not do yet (0.9.2)

Checked in this version; later versions may differ.

- **Reading a v2 sequence back from JSON fails.** `v2.MDASequence.model_dump_json()`
  works, but `model_validate_json` of the result raises (the axes are
  abstract types when deserialised). A v2 sequence made from the classic
  fields can be saved and loaded as a classic `useq.MDASequence` instead,
  which the engine also runs. This is why the assistant's
  `plan_useq_sequence` reads classic sequences only.
- **`do_stack`, `acquire_every` and `z_offset` on a channel are ignored.**
  A v2 channels axis contributes only `config` and `exposure`. With
  `{"config": "BF", "do_stack": False}` the brightfield channel gets the
  whole Z-stack; `acquire_every: 2` images every time point; `z_offset: 3`
  shifts nothing. Write a `should_skip` or a transform for these, or use
  the classic sequence.
- **An autofocus event is placed at the first Z plane**, not at the
  position's own z as in the classic API (compare the two autofocus
  listings above: `z_pos` -1.0 against 0.0).
- **The pymmcore-plus writers (0.18) do not keep the axes of a v2
  sequence**: an OME-TIFF written from a v2 run is one flat stack of
  images, without the channel and Z dimensions. Use the classic sequence
  when the saved file matters.

## What NisEngine does with each field

| useq | On the Nikon, through the bridge |
|---|---|
| `x_pos`, `y_pos`, `z_pos` | `move` to the absolute position (um), only on the axes given; checked against the stage limits first |
| `channel.config` | `select_optical_configuration`; `group` is ignored |
| `exposure` | `set_exposure` (ms); NIS cannot report the exposure a configuration brings, so the metadata carries the exposure the sequence set, or 0 |
| `properties` | `("Nosepiece", "Position", n)`: `set_objective`; `("PFS", "State", "On"/"Off")`: `set_pfs`; anything else is refused |
| `AcquireImage` | `snap` to a temporary TIFF, read back, handed to the runner |
| `HardwareAutofocus` | `set_pfs on`, wait for the lock, `set_pfs off`; later Z moves at that position are shifted by the distance the focus moved; an `autofocus_motor_offset` is refused |
| `CustomAction("autofocus", {"range_um", "speed"})` | the NIS image-based focus sweep, then the same Z shift |
| `min_start_time` | the pymmcore-plus runner waits |
| `roi`, `slm_image`, other custom actions | refused before the run |
| `keep_shutter_open`, `setup` | ignored; NIS controls the shutter |

Before anything moves, the engine checks every event against what NIS
offers, and the plans for the two mistakes useq itself cannot catch: a
relative Z plan or grid without a position to lay it around, and a grid
without a field of view.

## Classic or v2?

Use the **classic** `useq.MDASequence` when the experiment fits positions,
channels, Z, time and tiles, when you want the saved OME-TIFF to carry the
axes, when you will save the sequence to a file, and when the channel
options `do_stack`, `acquire_every` and `z_offset` matter. It is what the
assistant's plans use, and what every other useq tool reads and writes.

Use **v2** when the experiment has an axis useq did not foresee (a
temperature, a drug concentration, a laser power series), when one axis
value needs different sub-axes from the others, when a rule for skipping
combinations is easier to write than to express with the classic options,
or when the run should go on until stopped. Run it with the same
`MDARunner` and `NisEngine`; the events are the same.

Both are described in the useq-schema documentation at
<https://pymmcore-plus.github.io/useq-schema/>. The assistant can read the
library's source for you: *What is new in useq v2?* and *How does a v2 axis
contribute to an event? Show me the code.*

---

MIT license. Thom de Hoog, Center for Microscopy and Image Analysis (ZMB),
University of Zurich. thom.dehoog@zmb.uzh.ch, thomdehoog@gmail.com.
If you use this work or build on its ideas, please acknowledge the author in
what you make from it.
