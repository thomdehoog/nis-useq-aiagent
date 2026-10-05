# nis-bridge, step by step

This is a walk-through for someone who works at a Nikon microscope and would
like to control it from Python, with no experience of this package. It
explains the idea, gets you to a first image, and then shows a few small
scripts you can adapt. The [README](../README.md) is the complete
documentation: every request the bridge answers, how it works inside, and
every file.

## The idea

NIS-Elements has a Python inside it: you can write a macro, and from that
macro call Python, and from that Python call NIS functions like "move the
stage" or "capture an image". That is useful, but it is NIS's own Python
interpreter: it has no packages beyond numpy, you cannot install any, and no
other program on the computer can call into it.

The bridge is the way around this. It is a small server that runs inside
NIS, in that interpreter, and does one thing: it receives requests from
outside, such as "report the stage position" or "capture an image and save it
at this path", carries each out by calling the corresponding NIS functions,
and returns the result. Your own Python, in an environment of your own with
whatever packages you need, sends the requests and reads the results.

```
your Python (any packages)          NIS-Elements
    NisClient  ───── message ─────►  bridge  ──► StgMoveXY, Capture, ...
               ◄───── answer ──────
```

Two consequences that you will meet below:

- The messages travel over a network connection, but one that never leaves
  your computer (`127.0.0.1`, port 54470). Your Python and NIS must run on the
  same machine.
- The bridge runs only while a NIS macro runs. The macro is a loop that
  lets the bridge process requests; when you stop the macro, the bridge
  stops.

## Before you start

- NIS-Elements on the microscope computer, with the microscope, or with its
  simulated Ti2 for trying things out.
- Python 3.10 or newer, installed separately from NIS. If you have never set
  one up: install Python from python.org, then in a command window make an
  environment of your own and activate it:

  ```
  python -m venv nis-env
  nis-env\Scripts\activate
  ```

  You will see `(nis-env)` in front of the prompt. Do this activation step in
  every new command window.
- This repository, cloned or downloaded, for example to `C:\nis-useq-aiagent`.

## Step 1: install the package

In the activated environment, in the repository folder:

```
pip install -e "./1_nis_bridge[test]"
```

`-e` matters: NIS will be pointed at this folder, so the code must stay here.

## Step 2: tell NIS where the bridge is

NIS starts the bridge through a macro, and that macro needs to know the folder
you just installed from. Write it once:

```
python -m nis_bridge.install_macros
```

This creates `1_nis_bridge/nis_bridge/start_bridge.mac`. Open it in a text
editor if you are curious: a handful of lines that import the bridge, start
it, and loop until you press Stop.

## Step 3: start the bridge

Two ways.

**By hand.** Start NIS-Elements. In its menu choose *Macro > Run Macro From
File...* and pick `start_bridge.mac`. NIS shows "nis-bridge: running on port
54470", and the macro keeps running. That is correct; the bridge runs
inside it. Do not stop the macro until you are done.

**In one command.** From your command window:

```
python -m nis_bridge.start
```

This starts NIS-Elements with the macro and waits until the bridge answers. If
NIS is already open, it tells you which macro to run by hand instead.

Check that it works:

```
python -c "from nis_bridge.client import NisClient; print(NisClient().request('ping'))"
```

You should see something like
`{'bridge': '0.2.0', 'protocol': 2, 'nis': '6.10.02 ...'}`. If instead you see
"no bridge at 127.0.0.1:54470", NIS is not running or the macro is not.

## Step 4: a first session

Open Python (`python` in the command window) and enter the lines below. Each
sends one request and prints the result.

```python
from nis_bridge.client import NisClient

nis = NisClient()
```

Connecting already sent one message (`ping`) and checked that the bridge
speaks the same version as your client.

**Where is the stage?**

```python
here = nis.request("get_position")
print(here)
```

`{'x': 1234.5, 'y': -678.9, 'z': 3456.7}`: the stage coordinates in
micrometres, exactly as NIS shows them in its own stage window. Compare them
with NIS now, so you trust the numbers.

**Move it a little.**

```python
nis.request("move", x=here["x"] + 20)
```

The stage moves 20 um in x. Axes you do not mention stay where they are. The
answer is the position after the move, read back from NIS, not merely the
number you asked for.

Note what did *not* happen: nothing checked whether 20 um further was a safe
place to go. `move` does what it is told; only NIS itself refuses a position
outside its stage limits. Keep that in mind when you write scripts, and read
about part 2 (`nis-engine`) if you want moves checked against limits you set.

**Which channels are there?**

```python
names = nis.request("get_optical_configurations")
print(names)
```

An optical configuration in NIS is a saved set of settings for one channel:
filter cube, light source, exposure, and so on. If this list is empty, make
one in NIS first (*Calibration > New Optical Configuration*), because almost
everything you image goes through them.

**Select one and take a picture.**

```python
from pathlib import Path

nis.request("select_optical_configuration", name=names[0])
reply = nis.request("snap", path=str(Path.home() / "first.tif"))
print(reply)
```

NIS captures one image with the current settings, saves it as a TIFF at the
path you gave, and closes the image window it opened, so windows do not pile
up. The answer gives the path and the pixel size in micrometres (`None` when
the objective has no calibration in NIS). Open `first.tif` in Fiji or in
NIS: it is a plain 16-bit image.

**Back to where you started, and close.**

```python
nis.request("move", **here)
nis.close()
```

That is the whole vocabulary: read something, change something, snap. The
README lists every request; there are fifteen.

## Step 5: when something goes wrong

Three kinds of error can come back, and each tells you where to look.

- **`ValueError`**: your request was malformed. `nis.request("move")` with no
  axis, or `set_exposure` with a word instead of a number. Fix the call.
- **`RuntimeError`**: NIS refused or failed. The message carries NIS's own
  return code, for example `StgMoveXY: DR_NOTINITIALIZED (-7)` when the stage
  is not initialised, or `focus not found` from the autofocus. Look at NIS.
- **`NisConnectionError`**: the bridge is not there, or stopped answering. The
  message says what to check: usually that NIS is running and the macro is
  still running in it. After this error the client is closed; make a new
  `NisClient()` once the bridge is back.

Every request also has a time limit (30 s by default, longer for a snap or
an autofocus). If NIS has not even started your request by then, the bridge
drops it, so a move you gave up on never happens later by surprise.

## Step 6: try it without a microscope

The package includes a fake NIS-Elements: a microscope in memory, with the
limits, objectives and optical configurations of the Ti2 simulator. In one
command window, leave this running:

```
python -m nis_bridge.fake
```

It answers on the same port as the real bridge, so everything above works
unchanged. Its images are flat (every pixel holds the capture number), but the
positions, names and errors behave like the real thing. Stop it with Ctrl+C.
This is the quickest way to learn the package on your own laptop.

## Small scripts to adapt

A script is just the session above, written in a file and run with
`python myscript.py`. The `with` form closes the connection for you.

**A row of positions, one image each.**

```python
from pathlib import Path
from nis_bridge.client import NisClient

out = Path.home() / "row"
out.mkdir(exist_ok=True)

with NisClient() as nis:
    start = nis.request("get_position")
    nis.request("select_optical_configuration", name="DAPI")
    nis.request("set_exposure", exposure_ms=50)
    for i in range(5):
        nis.request("move", x=start["x"] + i * 200)   # 200 um apart
        nis.request("snap", path=str(out / f"pos_{i}.tif"))
    nis.request("move", **start)
```

**A time-lapse at one position.**

```python
import time
from pathlib import Path
from nis_bridge.client import NisClient

out = Path.home() / "timelapse"
out.mkdir(exist_ok=True)

with NisClient() as nis:
    for t in range(12):                              # 12 images, 10 s apart
        nis.request("snap", path=str(out / f"t_{t:03d}.tif"))
        time.sleep(10)
```

**Lock focus with the PFS before imaging.**

```python
with NisClient() as nis:
    pfs = nis.request("get_pfs")
    if pfs["present"]:
        print(nis.request("set_pfs", on=True))       # waits for the lock, reports status
    nis.request("snap", path="focused.tif")
```

**Change objective (check first that the turret can turn freely).**

```python
with NisClient() as nis:
    print(nis.request("get_objectives"))   # which slot is in use, and what is in each
    nis.request("set_objective", position=2)
```

Each of these does exactly what it says and nothing more. For anything with
channels x Z x time x positions, writing the loops yourself gets tedious and
error-prone; that is what part 2, `nis-engine`, is for. It describes the whole
experiment in one object (a useq sequence), checks it against the microscope
before anything moves, and saves the result as one OME-TIFF.

## Points to be aware of

- **The macro keeps running.** It has to: NIS crashes if a camera command
  runs from any thread but its main one, and the running macro *is* that
  thread. The bridge's socket threads only queue your requests; the macro
  loop runs them one at a time.
- **Only these fifteen requests exist.** The bridge never runs macro text you
  send it. If you need something it does not offer, add a method to
  `commands.py` or `readers.py` (the README says how).
- **Units.** Micrometres for positions, milliseconds for exposure, slot
  numbers from 1 for objectives.
- **Answers are read back.** After `move` or `set_exposure`, the answer is
  what NIS reports afterwards, which can differ from what you asked (NIS
  rounds exposures, for instance).
- **One client at a time is simplest.** Several programs can connect, but
  their requests are queued and run in turn.
- **The log.** The bridge writes `nis-bridge.log` in the Windows temp folder
  (`%TEMP%`). When a request fails inside NIS, the details are there.

## Where to go next

- The [README](../README.md): the table of all requests and what each
  returns, and the list of files.
- Part 2, [nis-engine](../../2_nis_engine/docs/tutorial.md): whole
  acquisitions as useq sequences.
- Part 3, [nis-assistant](../../3_nis_assistant/docs/tutorial.md): the same
  microscope, in plain language through a chat window.
