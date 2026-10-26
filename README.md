# Step 0: test what NIS-Elements 6.10 lets our Python do

Run on **NIS-Elements AR 6.10.02 (Build 2031)** on the Ti2 simulator, with its own Python 3.12.1 (version and Python as reported by the test itself, 2026-10-26). Every NIS function goes through `nis.call_proc`; no DLL. The same test for NIS-Elements 7.01: branch `agent/nis-7-step0`. Results in full: [RESULTS.md](RESULTS.md).

## Run it

1. Download this branch (GitHub: Code > Download ZIP) and unzip it on the desktop (or to
   `C:\nikon-step0-610\`). Any folder name works: `step0.mac` runs the newest
   `step0_test.py` whose first line says 6.10.
2. Start NIS-Elements 6.10 with the Ti2 simulator.
3. In NIS: Macro > Run Macro From File > `step0.mac` in that folder (under a minute): the
   bridge's functions, and whether every function in NIS's list can be reached.
4. Then `step0_calls.mac` (about 5 minutes): every hardware function that needs no image, file
   or dialog, called for real. Devices the simulator does not have open *Command Interpreter
   Error* dialogs: click OK, or first run `python dialog_watcher.py` on the same computer, which
   presses OK for you. If NIS dies, start it and run the macro again: it goes on where it
   stopped.
5. Bring back the `results` folder that appears next to the files.

Without anyone at the keyboard: `step0_runner.mac` keeps a loop running inside NIS. Write a
script name (e.g. `step0_calls.py`) into `runner\request.txt`; NIS runs it and writes
`runner\done.txt`. The macro holds the folder's path: edit it if the folder is not
`Desktop\nis-useq-aiagent-nis-6p1-step0`. Stop it with the macro Stop button or
`runner\stop.txt`.

## The results

- `step0_summary.txt`: one line per check, ok or FAIL.
- `step0_report.json`: everything in full.
- `step0.log`, `step0_calls.log`: the runs step by step. If NIS hangs, the last line names the call.
- `functions_reachable.csv`, `functions_calls.csv`, `functions_called.csv`: per function.
- `dialogs.log`: every dialog `dialog_watcher.py` closed.

The test reads NIS's own function list and help on the NIS computer. The csv files are made
from them, so they stay out of the repository.

## Writes

The writes are **on**: this run is for the simulator. They move the stage, the objective,
Perfect Focus and other devices, and put each one back. On a real microscope, open
`step0_test.py` in Notepad and set every `ALLOW_... = True` to `False`; in `step0_calls.py`,
set `ALLOW_SET_SAME` and `ALLOW_CHANGE` to `False`. Then switch them on one at a time, with
someone at the microscope.

## How we connect

```
┌──────────────────── NIS-Elements ────────────────────┐
│                                                      │
│ step0.mac ──► NIS's Python ──► nis.call_proc ────────┼──► microscope
│ (a macro)     (step0_test.py)  (any function,       │    (simulator)
│                    │            by name)             │
│                    │               └─ RunMacro       │
│                    │                  (values back)  │
└────────────────────┼─────────────────────────────────┘
                     ▼
                 results\  (the report)
```

1. **The macro** is the way in: NIS runs macros, and one line of macro starts Python.
2. **NIS's own Python** runs our code, inside NIS. No separate Python is needed.
3. **`nis.call_proc`** calls any macro function by name, as a macro does. It is 6.10's door;
   6.10 has no `nis.mac`, and NIS 7.01 has no `nis.call_proc`.
4. **The microscope** (here the simulator) does what the function says.

**When a value comes back, `nis.call_proc` directly is not the way to go.** A number handed
back fails with a blocking dialog. A text handed back with a maximum length (`GetOptConfName`,
`Stg_GetNosepieceObjectiveName`) corrupts NIS's memory (heap corruption): the answer is right,
then NIS crashes within 1 to 6 calls. So for a value that comes back, Python writes a few lines
of NIS macro, runs them with `nis.call_proc("RunMacro", file)`, and reads the answer back from
macro variables and a file: about 20 ms per call, no crashes in about 850 runs.

The driver later works the same way, with one step added: the Python inside NIS listens for
requests from our software outside NIS.

```
our software  ──►  NIS's Python  ──►  nis.call_proc / RunMacro  ──►  microscope
(outside NIS)      (started by a macro)
```

## What our Python can reach, on the simulator

Reachable means `nis.call_proc` finds the function by name; it was not run. Every function: [FUNCTIONS.md](https://github.com/thomdehoog/nis-useq-aiagent/blob/agent/nis-6-step0/FUNCTIONS.md) (branch `agent/nis-6-step0`).

| Section | Reachable | Not reachable | Total |
|---|---:|---:|---:|
| Acquire | 260 | 76 | 336 |
| AdvancedAPI | 146 | 2 | 148 |
| Analysis | 209 | 18 | 227 |
| Applications | 38 | 158 | 196 |
| Binary | 350 | 49 | 399 |
| Calibration | 21 | 0 | 21 |
| Device | 509 | 176 | 685 |
| ExportResults | 57 | 0 | 57 |
| Image | 547 | 21 | 568 |
| ImageDocument | 141 | 2 | 143 |
| Macro | 59 | 0 | 59 |
| Measure | 173 | 0 | 173 |
| Misc | 7 | 0 | 7 |
| ND | 204 | 6 | 210 |
| Organizer | 75 | 0 | 75 |
| System | 103 | 7 | 110 |
| UserInterface | 26 | 0 | 26 |
| View | 201 | 1 | 202 |
| Visualization | 49 | 0 | 49 |
| **All** | **3175** | **516** | **3691** |

Most of what is not reachable belongs to hardware the simulator does not have (Device), to modules not installed (Applications), or to the camera driver (Acquire).

## What our Python can run, on the simulator

Called for real and worked: the bridge's functions (`step0_test.py`) and the hardware functions (`step0_calls.py`). Every function with its route and result: [CALLABLE.md](CALLABLE.md). About 3000 more are reachable but not called yet: they need an image, a file or a set-up.

| Category | Can run | Through the DLL | Only through `nis.call_proc` |
|---|---:|---:|---:|
| Camera | 43 | 1 | 42 |
| Condenser, aperture, zoom, light path | 22 | 22 | 0 |
| Confocal, A1, AX, C2, galvo | 1 | 0 | 1 |
| DMD and patterns | 8 | 7 | 1 |
| Filters | 19 | 19 | 0 |
| Incubator and heating | 12 | 7 | 5 |
| Lights and lasers | 36 | 35 | 1 |
| Objectives and nosepiece | 11 | 11 | 0 |
| Optical configurations | 3 | 3 | 0 |
| Other devices | 8 | 7 | 1 |
| Perfect Focus and autofocus | 15 | 13 | 2 |
| Shutters | 15 | 12 | 3 |
| Slide loader | 14 | 14 | 0 |
| Stage XY | 25 | 25 | 0 |
| Stage Z | 23 | 23 | 0 |
| TIRF | 7 | 7 | 0 |
| Triggers and TTL | 9 | 5 | 4 |
| AdvancedAPI | 1 | 0 | 1 |
| ImageDocument | 2 | 2 | 0 |
| Macro | 2 | 2 | 0 |
| System | 3 | 3 | 0 |
| **All** | **279** | **218** | **61** |

Through the DLL means `g5_regprocs.dll` exports it too (about 0.003 ms a call); the run itself used `nis.call_proc`. Only through `nis.call_proc`: directly when values only go in (about 0.5 ms), inside a macro when a value comes back (about 20 ms). Most camera settings are only there.
