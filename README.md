# Step 0: test what NIS-Elements 6.10 lets our Python do

Run on **NIS-Elements AR 6.10.02**
on the Ti2 simulator: the version the bridge was built and tested on. Every NIS function is
called through `nis.call_proc`, NIS's own way of calling a macro function by name, and not
through a DLL. The results can be compared with NIS 7 (branch `agent/nis-7-step0`).

Two scripts:

- `step0_test.py` (`step0.mac`): every function the bridge uses, readings and writes, and
  whether every function in NIS's list can be reached.
- `step0_calls.py` (`step0_calls.mac`): every hardware function (Device and Acquire) that needs
  no image, file or dialog, called for real: getters, setters set to their own value, and
  positions and on/off states changed and put back.

Results so far: [RESULTS.md](RESULTS.md).

## Run it

1. Download this branch (GitHub: Code > Download ZIP) and unzip it on the desktop (or to
   `C:\nikon-step0-610\`). Any folder name works. The NIS 7 folder can stay on the desktop:
   `step0.mac` runs the newest `step0_test.py` whose first line says 6.10, so older
   downloads can stay too. The first line of `step0.log` names the file that ran.
2. Start NIS-Elements 6.10 with the Ti2 simulator.
3. In NIS: Macro > Run Macro From File > `step0.mac` in that folder.
4. Wait until NIS responds again (under a minute: the writes move the simulated stage).
5. Then the same with `step0_calls.mac` (about 5 minutes). Functions of devices the simulator
   does not have open *Command Interpreter Error* dialogs; click OK, or run
   `python dialog_watcher.py` on the same computer first: it presses OK and notes each dialog.
   If NIS dies, start it and run the macro again: it goes on where it stopped and skips the call
   NIS died in.
6. Bring back the `results` folder that appears next to the files.

### Without anyone at the keyboard

`step0_runner.mac` keeps a small loop running inside NIS. Write a script name (e.g.
`step0_calls.py`) into `runnerequest.txt`; NIS runs it as if its macro had been started by
hand and writes `runner\done.txt`. The macro holds the folder's path as a literal: edit it if
the folder is not `Desktop
is-useq-aiagent-nis-6p1-step0`. Stop it with the macro Stop button
or by creating `runner\stop.txt`.

The test counts the functions in NIS's own `FunctionList_6.10.02.html`, by section. It finds
it under `C:\Program Files\NIS-Elements` (or next to `step0_test.py`). The list is Nikon's and
is **not** part of this branch.

## The results

- `step0_summary.txt`: one line per check, ok or FAIL.
- `step0_report.json`: everything in full.
- `step0.log`: the run step by step. If NIS hangs, the last line names the call.
- `functions_reachable.csv`: every function in NIS's list, and whether `nis.call_proc`
  reaches it.
- `functions_calls.csv`: every function in NIS's list with its signature (from NIS's help
  index), the route it needs, and what this run called.
- `functions_called.csv`, `step0_calls.log`: one line per call of `step0_calls.py`.
- `dialogs.log`: every dialog `dialog_watcher.py` closed.

The csv files are made from Nikon's list and help, so they stay out of the repository like the
list.

## Every function in the list: reachable?

Early in the run, right after the function list is counted. 6.10 has no `nis.mac` to look a
name up without calling it, so each name is called with one argument that no NIS function can
take. If `nis.call_proc` refuses the argument, it found the function and ran nothing ("yes").
If it answers as for a name that does not exist (*Procedure not found*), NIS does not have the
function in this run ("no"). Before the sweep, three control calls check that this is safe: a
name that does not exist, `GetOptConfCount` (takes no argument) and `Stg_SetNosepiecePosition`
(the objective must not change). If one of them fails, no name is swept.

Once the log says `END reach / every function in NIS's list`, the reachability results are
saved.

## What it calls

Every NIS function in `1_nis_bridge/nis_bridge/nis_dll.py`, all through `nis.call_proc`, by
one of two routes:

- **direct**, `nis.call_proc(name, *args)`, for functions that only take values in, and for
  `Get_InfoStr`'s text.
- **macro**, for functions that hand values back through an argument. Directly, a number
  handed back fails with a blocking dialog, and a text with a max length corrupts NIS's heap
  and kills it a few calls later (RESULTS.md). So the test writes a few lines of NIS macro, runs
  them with `RunMacro`, and reads the numbers back with `GetVariableValue` and a text from a
  file the macro wrote. `probe_macro.py` and `probe_textlen.py` show the two sides on their own.

| | Functions |
|---|---|
| Readings | `Get_InfoStr`, `StgGetPos`, `StgXY_GetLimits`, `StgZ_GetLimits`, `GetOptConfCount`, `GetOptConfName`, `Stg_IsNosepiecePresent`, `Stg_GetNosepiecePositions`, `Stg_GetNosepiecePosition`, `Stg_GetNosepieceObjectiveName`, `Stg_IsPFSPresent`, `Stg_GetPFSStatus`, `Get_Calibration` |
| Writes, each put back | `StgMoveXY`, `StgMoveZ`, `StgMove`, `SelectOptConf`, `Camera_ExposureSet`, `Stg_SetNosepiecePosition`, `Stg_SetPFSStatus`, `Stg_WaitForPFS`, `StgFocusInRangeEx`, `Capture`, `ImageSaveAs`, `CloseCurrentDocument` |
| Also read, to compare with NIS 7 | `StgGetPosXY`, `StgGetPosZ`, `GetSelectedOptConf` |

It also checks what `nis.call_proc` does with a name that does not exist, that the macro route
works, and times a call each way.

## Writes

Unlike on NIS 7, the writes are **on**: this run is for the simulator. `Camera_ExposureSet`
leaves the exposure at 50 ms. On a real microscope, open `step0_test.py` in Notepad, set every
`ALLOW_... = True` to `False`, and switch them on one at a time, with someone at the
microscope. In `step0_calls.py`, set `ALLOW_SET_SAME` and `ALLOW_CHANGE` to `False`.

## Note by hand

- Help > About: the version and edition (AR?).

## How we connect

```
┌──────────────────── NIS-Elements ────────────────────┐
│                                                      │
│ step0.mac ──► NIS's Python ──► nis.call_proc ────────┼──► microscope
│ (a macro)     (step0_test.py)  (any function,       │    (simulator)
│                    │            by name; RunMacro    │
│                    │            for values handed    │
│                    │            back)                │
└────────────────────┼─────────────────────────────────┘
                     ▼
                 results\  (the report)
```

1. **The macro** is the way in: NIS runs macros, and one line of macro starts Python.
2. **NIS's own Python** runs our code, inside NIS.
3. **`nis.call_proc`** calls any macro function by name, as a macro does, with the values
   coming back. It is 6.10's door; NIS 7.01 has `nis.mac` instead. 6.10 has no `nis.mac`
   (first run, 2026-10-26).
4. **The microscope** (here the simulator) does what the function says.
