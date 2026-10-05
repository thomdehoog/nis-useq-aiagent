# nis-bridge

Control NIS-Elements from your own Python.

This is part 1 of three; see the [overview](../README.md). It has no useq in
it, so it is useful on its own for any Python that needs to drive a Nikon
microscope. The [tutorial](docs/tutorial.md) is a longer walk-through with
example scripts; this page is the complete documentation of the package.

Status: the NIS functions it calls were validated on NIS-Elements AR 6.10.02
with the Ti2 simulator. The package itself is tested offline, against a fake
NIS behind the real bridge server; its hardware tests are for NIS-Elements.

## Contents

1. [The idea](#the-idea)
2. [Install](#install)
3. [Start the bridge in NIS-Elements](#start-the-bridge-in-nis-elements)
4. [First use, step by step](#first-use-step-by-step)
5. [Errors and timeouts](#errors-and-timeouts)
6. [The requests the bridge answers](#the-requests-the-bridge-answers)
7. [Testing without a microscope](#testing-without-a-microscope)
8. [How it works inside](#how-it-works-inside)
9. [Adding a request](#adding-a-request)
10. [Tests](#tests)
11. [Files](#files)

## The idea

NIS-Elements has a Python interpreter inside it: a macro can call Python,
and that Python can call NIS functions such as "move the stage" or "capture
an image". But it is NIS's own interpreter, with no packages beyond numpy,
no way to install any, and no way for another program to call into it.

The bridge is the way around this. It is a small server that runs inside
NIS, in that interpreter, and does one thing: it receives requests from
outside, such as "report the stage position" or "capture an image and save it
at this path", carries each out by calling the corresponding NIS functions,
and returns the result. Your own Python, in an environment of your own with
whatever packages you need, sends the requests through `NisClient` and reads
the results.

```
your Python                     NIS-Elements
NisClient ── socket ─────────── dispatch ── readers, commands ── nis_dll ── g5_regprocs.dll
             127.0.0.1 only     (Python inside NIS, started by a macro)
```

Two consequences:

- The requests travel over a network connection that never leaves the
  computer (`127.0.0.1`, port 54470). Your Python and NIS-Elements must run
  on the same machine.
- The bridge runs only while a NIS macro runs. The macro is a loop that lets
  the bridge process requests on NIS's main thread; when the macro is
  stopped, the bridge stops.

## Install

You need NIS-Elements on the microscope computer (with the microscope, or
its simulated Ti2), and a conda environment of your own, separate from the
Python inside NIS: install [Miniforge](https://github.com/conda-forge/miniforge)
(conda with the conda-forge channel), then in a Miniforge Prompt:

```
conda create -n nis -c conda-forge python=3.12
conda activate nis
```

In that environment, in the repository folder:

```
pip install -e "./1_nis_bridge[test]"
```

Install it editable (`-e`), as shown: the start macro points NIS-Elements at
this folder, so the bridge must run from here, not from a copy in
site-packages. `[test]` adds what the tests need.

## Start the bridge in NIS-Elements

1. Write the start macro for this computer (once; it contains this folder's path):

   ```
   python -m nis_bridge.install_macros
   ```

   This creates `nis_bridge/start_bridge.mac`: a few lines that import the
   bridge, start it, and loop until the macro is stopped.

2. Start NIS-Elements (with the microscope or the simulator).
3. In NIS: *Macro > Run Macro From File...* and pick `nis_bridge/start_bridge.mac`.
   The macro keeps running while the bridge is up. That is intended: camera
   commands crash NIS unless they run on its main thread, and the macro loop
   is that thread. Press the macro **Stop** button to end it. Running the macro
   again later is safe; it closes whatever an earlier run left behind.

Or let one command do steps 1 to 3: it writes the macro if needed, starts
NIS-Elements with the macro (NIS runs a macro command as it opens), and waits
until the bridge answers. When NIS-Elements is already open, it names the
macro to run by hand instead.

```
python -m nis_bridge.start
```

NIS then shows "nis-bridge: running on port 54470". To check from your own
Python:

```
python -c "from nis_bridge.client import NisClient; print(NisClient().request('ping'))"
```

This prints the bridge and protocol versions and the NIS version. "no
bridge at 127.0.0.1:54470" means NIS is not running, or the macro is not.

The bridge writes a log to `nis-bridge.log` in the Windows temp folder.

## First use, step by step

Open Python and enter the lines below. Each sends one request and prints
the result.

```python
from nis_bridge.client import NisClient

nis = NisClient()                    # connects, and checks the protocol version
```

**Read the stage position.**

```python
here = nis.request("get_position")   # {"x": ..., "y": ..., "z": ...} in um
```

These are NIS stage coordinates in micrometres, exactly as NIS shows them.
Compare them with NIS's stage window.

**Move a little.**

```python
nis.request("move", x=here["x"] + 20)
```

Moves are absolute; axes left out stay where they are. The result is the
position after the move, read back from NIS, not the number asked for.
`move` goes exactly where it is told: this part does not check the stage
limits itself, and only NIS may refuse. For moves checked against the limits
(and limits you can narrow), use `NisEngine` from part 2.

**List the optical configurations and select one.**

```python
names = nis.request("get_optical_configurations")
nis.request("select_optical_configuration", name=names[0])
```

An optical configuration is a named set of settings for one channel (filter
cube, light source, exposure, ...). If the list is empty, make one in NIS
first (*Calibration > New Optical Configuration*).

**Capture an image.**

```python
from pathlib import Path

reply = nis.request("snap", path=str(Path.home() / "snap.tif"))
print(reply["path"], reply["pixel_size_um"])
```

NIS captures one image with the current settings, saves it as a TIFF at the
path, and closes the image window it opened. `pixel_size_um` is `None` when
the objective has no calibration in NIS.

**Go back and close.**

```python
nis.request("move", **here)
nis.close()
```

In a script, the `with` form closes the connection for you:

```python
with NisClient() as nis:
    ...
```

The [tutorial](docs/tutorial.md) continues from here with scripts for a row
of positions, a time-lapse, focus locking and objective changes.

## Errors and timeouts

Three kinds of error can come back, and each tells you where to look.

| Raised | Meaning | What to do |
|---|---|---|
| `ValueError` | The request was malformed: a missing or wrong argument. | Fix the call. |
| `RuntimeError` | NIS refused or failed; the message carries NIS's own code, for example `StgMoveXY: DR_NOTINITIALIZED (-7)`. | Look at NIS-Elements. |
| `NisConnectionError` | The bridge is not there, or stopped answering; the message says what to check. | Check NIS and the macro; then make a new `NisClient()`. |

Every request carries how long the client will wait (30 s by default; longer
for a snap or an autofocus). A request NIS has not started by then is
dropped, so a late move never happens after the client gave up (for example
when the macro was stopped). After a timeout or connection error the client
is closed; connect again once the bridge is back.

## The requests the bridge answers

Only these requests exist; the bridge never runs macro text sent to it. Two are
about the bridge itself (`dispatch.py`), six only read (`readers.py`), and the
rest change something (`commands.py`). Units: micrometres for positions,
milliseconds for exposure, nosepiece slots numbered from 1.

| Request | Arguments | Returns |
|---|---|---|
| `ping` | | the bridge and protocol versions, and NIS's version |
| `shutdown` | | stops the bridge |
| `get_version` | | the NIS-Elements version |
| `get_position` | | `x`, `y`, `z` in um |
| `get_limits` | | the stage limits set in NIS, per axis `min` and `max` in um |
| `move` | any of `x`, `y`, `z` (um, absolute) | the position after the move |
| `get_optical_configurations` | | the configuration names |
| `select_optical_configuration` | `name` | the selected name |
| `set_exposure` | `exposure_ms` | the exposure NIS applied (it may round) |
| `get_objectives` | | the current nosepiece slot and the objective in each slot |
| `set_objective` | `position` (slot, from 1) | the current slot |
| `get_pfs` | | whether the Perfect Focus System is present, on, and in focus |
| `set_pfs` | `on`, optionally `timeout_s` | the PFS state after switching |
| `autofocus` | `range_um`, `speed` | the position after NIS's image-based focus sweep |
| `snap` | `path` | the path of the saved TIFF and the pixel size in um (None when not calibrated) |

A command's result is always read back from NIS after the change, so it can
differ from what was asked (NIS rounds exposures, for instance).

## Testing without a microscope

`nis_bridge.fake` is a fake NIS-Elements: a microscope in memory whose
limits, objectives and optical configurations match the Ti2 simulator. Its
images are flat (every pixel holds the capture number), but positions, names
and errors behave like the real thing. To try things by hand, serve it on
the bridge's usual port, in place of NIS (Ctrl+C stops it):

```
python -m nis_bridge.fake
```

In your own tests, `running_bridge` puts the real bridge server in front of it
on a free port, so code built on the client is tested end to end:

```python
from nis_bridge.client import NisClient
from nis_bridge.fake import FakeNisApi, running_bridge

with running_bridge(FakeNisApi()) as server:
    client = NisClient("127.0.0.1", server.server_address[1])
```

## How it works inside

**The protocol.** One JSON object per line, in each direction:

```
request:  {"id": 7, "op": "get_position", "args": {}, "timeout": 30.0}
success:  {"id": 7, "ok": true, "result": {"x": 100.0, "y": -20.0, "z": 500.0}}
failure:  {"id": 7, "ok": false, "kind": "RuntimeError", "error": "StgMove: DR_NOTINITIALIZED (-7)"}
```

`kind` is `ValueError` for a bad request and `RuntimeError` when NIS refused
or failed; the client raises the same type. The client and bridge check that
they speak the same protocol version when connecting.

**The main thread.** Every NIS call must run on NIS's main thread; `Capture`
from any other thread crashes NIS-Elements. So the bridge's socket threads
only queue requests, and the macro loop runs them one at a time by calling
`pump` on each pass. This is why the macro must keep running, and why
requests from several clients are served in turn.

**Timeouts.** A request that has not started when its timeout expires is
marked cancelled and never run; one that has started runs to its end, and the
client is told it is still running.

**The NIS functions.** Every NIS macro function (`StgMoveXY`, `Capture`,
`ImageSaveAs`, ...) is also exported by `g5_regprocs.dll`, a C library that
ships with NIS. `nis_dll.py` calls them with `ctypes`, turns their return
codes into Python exceptions and their output values into plain Python.
Signatures come from the macro reference installed with NIS-Elements
(`C:\Program Files\NIS-Elements\Docs\nis\eng_ar\`). `Camera_ExposureSet` is
not exported; the bridge reaches it through NIS's own `nis.call_proc`.

**Standard library only** on the bridge side, because it runs inside
NIS-Elements' own Python (NIS 6.10 bundles Python 3.12 with numpy and nothing
else).

## Adding a request

A request that only reads belongs in `readers.py`; one that changes
something belongs in `commands.py`. Add a method, and its name to `READS` or
`COMMANDS`; nothing else changes, since the client sends the name and the
dispatcher runs it. A command follows the same shape as the existing ones:

1. check the arguments, and refuse bad ones with `ValueError`;
2. call NIS through `self.api` (a thin wrapper in `nis_dll.py`, which raises
   `RuntimeError` when NIS refuses; add one there if the function is new);
3. read the state back through `self.read` and return that, not what was
   asked for.

Then add the same behaviour to `fake.py`, so the offline tests cover it.

## Tests

```
pip install -e ".[test]"
pytest                    # offline, a few seconds
pytest -m hardware -s     # on NIS-Elements with the bridge running (step 1 in docs/testing.md)
ruff check . && ruff format --check .   # lint and formatting, rules in pyproject.toml
```

## Files

| File | What it is |
|---|---|
| `nis_bridge/readers.py` | The read-only requests, one method each: they observe NIS and change nothing. |
| `nis_bridge/commands.py` | The requests that change something, one method each, all in the same shape (check, call NIS, read back). The place to look up or add a command. |
| `nis_bridge/nis_dll.py` | C to Python: the raw NIS functions of `g5_regprocs.dll`, one thin wrapper each. |
| `nis_bridge/dispatch.py` | The server inside NIS: the queue, the main-thread pump, the timeouts. |
| `nis_bridge/bridge.py` | What `start_bridge.mac` calls: start, pump, stop. |
| `nis_bridge/settings.py` | Every constant: ports, timeouts, defaults. |
| `nis_bridge/protocol.py` | The message format both sides share. |
| `nis_bridge/client.py` | `NisClient`: the connection from your Python. |
| `nis_bridge/install_macros.py` | Writes `start_bridge.mac`. |
| `nis_bridge/start.py` | Starts NIS-Elements with the macro and waits for the bridge. |
| `nis_bridge/fake.py` | A fake NIS for tests. |
| `docs/tutorial.md` | The walk-through, with example scripts. |

MIT license. Thom de Hoog, Center for Microscopy and Image Analysis (ZMB),
University of Zurich. thom.dehoog@zmb.uzh.ch, thomdehoog@gmail.com.
If you use this work or build on its ideas, please acknowledge the author in
what you make from it.
