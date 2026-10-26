# Step 0 results

## 2026-10-26, runs 3 to 10: why NIS crashed, and the macro route

NIS-Elements 6.10.02 (Build 2031), Ti2 simulator. Everything through `nis.call_proc`; no DLL.

### What crashed NIS

Six step0 runs and four probes. NIS died with heap corruption (`0xc0000374` in ntdll; once an
access violation, `0xc0000005`) 4 to 8 s after a call, so the last line of the log named
whatever check ran next, not the cause. Lining up the crash times (Windows event log) with the
calls, then probing one call shape at a time:

| Call shape through `nis.call_proc` | Example | Result |
|---|---|---|
| No arguments, or only values going in | `Stg_GetNosepiecePosition()`, `StgMoveZ(501.0, 0)` | **Works** |
| A text handed back, no max length | `Get_InfoStr(1, 256)` | **Works** (21 calls in a row) |
| A number handed back (`double *`, `int *`) | `StgGetPosXY`, `StgGetPosZ`, `StgXY_GetLimits`, `Camera_ExposureGet` | **Fails**: *Failed to run procedure* and a blocking dialog |
| A text handed back with a max length | `GetOptConfName(i, 256, 64)`, `Stg_GetNosepieceObjectiveName(p, 256, 64)` | **Kills NIS**: the right answer comes back, then NIS dies within 1 to 6 calls. A 4096 buffer only delays it. Windows' `HeapValidate` after every call sees nothing |
| A refused argument (the reachability sweep) | 4071 names | **Safe**: refused, nothing runs |

`probe_textlen.py` reproduces the crash: `Stg_GetNosepieceObjectiveName` in a loop.

### The macro route

For every call that hands values back, Python writes a few lines of NIS macro, runs them with
`nis.call_proc("RunMacro", file)` and reads the answer back: numbers from global macro variables
with `GetVariableValue`, texts from a file the macro writes with `WriteFile` (UTF-16). So Python
itself never passes an out-argument to `nis.call_proc`. `RunMacro` works from inside our Python,
which itself runs from a macro.

```
global double step0_1_r, step0_1_x, step0_1_y;
step0_1_x = -123456789.0;
step0_1_y = -123456789.0;
step0_1_r = StgGetPosXY(&step0_1_x, &step0_1_y);
```

- `probe_macro.py`: XY, Z, limits, `GetOptConfName`, and `Stg_GetNosepieceObjectiveName` 20
  times, then 15 s idle: no crash; the same values as ctypes in the first run.
- About 300 macro runs since, no crash.
- Every declaration must come before the first statement. A `char` declared after a statement
  opens *Command Interpreter Error* (first run with the route: `GetSelectedOptConf` and
  `Get_Calibration` waited for OK).
- A call that fails inside the macro (a device that is not there) opens *Command Interpreter
  Error: Cannot Evaluate the Expression*, which blocks until OK. `dialog_watcher.py` closes
  them (OK only) and writes each to `results\dialogs.log`; `step0_calls.py` does not call such
  a function again.
- Speed: `StgGetPosXY` through a macro 24 ms (median); a direct call 0.5 ms.

### step0_test.py: 29 of 29

| | Answer |
|---|---|
| Readings (macro route) | XYZ 39904.7, -13433.1, 500 µm; limits X ±57000, Y ±37500, Z 0 to 10000 µm; objective names (with λ); calibration 0.1084 µm/px, `Plan Apo VC 60xA WI DIC N2`; exposure 33 ms |
| `GetSelectedOptConf` | returns 0 and three empty texts (as with ctypes) |
| Moves XY, Z, XYZ and back | DR_OK, read back exactly |
| Objective 4 → 5 → 4 | DR_OK, read back exactly |
| `Camera_ExposureSet` 50 ms | read back 50 (was 33); `Camera_ExposureGet` returns 0 although it works |
| Perfect Focus on and back | status 1, then 0: put back |
| Autofocus (`StgFocusInRangeEx`) | needs the speed as an integer (*Expected integer* with a float); returned 0, Z 500 → 505.4, put back to 500 |
| Capture, save, close | 8.6 MB TIFF; `Capture` returns 0 |

### step0_calls.py: the hardware functions (Device and Acquire sections)

Every getter and setter that needs no image, file or dialog, called for real:

| Stage | Functions | Works | Rest |
|---|---|---|---|
| 1. Getters without arguments, direct | 99 | 73 | 18 not in this NIS; 8 DR errors (not supported) |
| 2. Getters that hand values back, macro (index or type guessed; every type tried) | 187 | 137 | 36 open a dialog (device not simulated: A1, confocal, DMD, triggered acquisition, filter and shutter speeds, some camera settings); 10 hand back nothing; 4 DR errors |
| 3. Set the value the Get read, read again | 51 | 37 | 4 not in this NIS; 3 not supported; 6 a Get's text is an input (gas, channel name), not filled in; `StgSetRelativeMovements` reads back differently |
| 4. Change and back (positions, on/off states) | 19 changes | 12 | 7: the Set returned 0 and nothing changed (shutters 2 to 5, CSU shutter, TIRF mirror, analyzer, zoom) |

Changed and put back: objective, condenser, filter wheels 0, 1, 2 and 5, aperture 1 and 3,
shutters 0 and 1, PFS LED. Help-index signatures can be wrong: `CameraGet_Exposure` is listed
with a plain `double` that it writes into (*Found Mismatch in dimensions*).

The full tables stay on the NIS computer (made from Nikon's list): `results\functions_called.csv`
(one line per call) and `results\functions_calls.csv` (every function: signature, route,
reached, what this run called).

### What this means for the bridge on 6.10

- `nis.call_proc` for calls that take values in; a macro for everything handed back. No DLL.
- The bridge's readings each cost about 24 ms through a macro.
- A missing device opens a blocking dialog; the bridge must not call functions for devices it
  has not seen (`Stg_Is...Present`, or the getters of stage 1 first).

## 2026-10-26, second run: everything through nis.call_proc

NIS-Elements 6.10.02 (Build 2031), Ti2 simulator, test 9e97f46. NIS crashed halfway.

| Question | Answer |
|---|---|
| A name that does not exist | `nis.error: Procedure not found` |
| A text handed back (`Get_InfoStr`) | **Works** with a count (`256`), a sequence and a string: `[1, 1, '6.10.02 (Build 2031)']` |
| A number handed back (`StgGetPosXY`) | **Fails** with a count and with a sequence: `nis.error: Failed to run procedure`, and NIS opens a blocking dialog: *Command Interpreter Error: Cannot Evaluate the Expression. StgGetPosXY(LpStgX,LpStgY)* |
| `StgGetPos`, `StgGetPosXY`, `StgGetPosZ`, `StgXY_GetLimits` | Fail the same way, one dialog each |
| `GetOptConfCount`, `GetOptConfName` | Work |
| Function list | 4071 functions, 3691 in AR, 350 more in AR with a module; all bridge functions in it |
| Crash | Right after `GetOptConfName`, before the next check started |

The dialog names the arguments as Nikon's macro reference does (`LpStgX`, `LpStgY`), so
`nis.call_proc` seems to build a macro expression from the function's own parameter names.

### Changed in the test after this run

- The reachability sweep runs right after the function list, before the number probe, the
  readings and the writes.
- Its write control is the objective (`Stg_SetNosepiecePosition`, read back as a return
  value), since Z cannot be read through `nis.call_proc`.

## 2026-10-26: NIS-Elements AR 6.10.02, Ti2 simulator

One run, with all writes on. 26 of 27 checks passed; the one failure is the test's own
`nis.call_proc` probe (see below). Every NIS function the bridge calls works through ctypes.

### What the run settles

| Question | Answer |
|---|---|
| NIS and its Python | NIS-Elements 6.10.02 (Build 2031), Python 3.12.1 |
| ctypes on `g5_regprocs.dll` | **Works** for every function the bridge calls, except `Camera_ExposureSet` (not exported) |
| Does 6.10 have `nis.mac`? | **No.** `nis` has `call_proc`, `log`, `error`, `stdout_hook`, `stderr_hook`; no `mac`, no `ptr` |
| `nis.call_proc` | There, and it reaches `Camera_ExposureSet`. An out-argument wants a count or a sequence, not a number: `call_proc("StgGetPosXY", 0.0, 0.0)` fails with *Expected count (int) or sequence* |
| Is the ctypes name lookup real? | **Yes**: an unknown name does not resolve |
| Not exported by the DLL | `Camera_ExposureSet`, `Camera_ExposureGet`, `Int_ExecuteCommand` |
| Speed of one call | ctypes 0.003 ms median (max 0.024 ms) |

So the bridge needs two routes: ctypes (and `nis.call_proc` for the exposure) on 6.10, and
`nis.mac` on 7.01, which has no `nis.call_proc`.

### Readings (ctypes)

| Reading | Answer |
|---|---|
| XYZ | 39904.7, -13433.1, 500 µm |
| Limits | X -57000 to 57000, Y -37500 to 37500, Z 0 to 10000 µm |
| Optical configurations | 1: `Spinning Disk (2):BF` |
| Selected optical configuration | empty: `GetSelectedOptConf` returned 0, as on NIS 7 |
| Nosepiece | 6 positions, at 4. Names: 10x, 20x, 40x, 60x, 100x; **position 6 empty: name `""`, return DR_OK** |
| Perfect Focus | present, status 0 (off, in range) |
| Calibration | uncalibrated with no image open; 0.1084 µm/px (60x) after a capture |

### Writes (ctypes), each put back

| Write | Answer |
|---|---|
| `StgMoveXY` 10 µm and back | DR_OK; read back exactly; 0.19 s per move |
| `StgMoveZ` 1 µm and back | DR_OK; read back exactly |
| `StgMove` XYZ and back | DR_OK; read back exactly |
| `SelectOptConf` | skipped: only one optical configuration |
| `Camera_ExposureSet` 50 ms (`nis.call_proc`) | answered `[0, 50.0]`: return 0, value 50 |
| `Stg_SetNosepiecePosition` 4 → 5 → 4 | DR_OK; read back exactly |
| `Stg_SetPFSStatus` on, then off | on worked (status 1). **Off was not seen**: straight after, the status still read 1, and `Stg_WaitForPFS` returned at once. Perfect Focus may have been left on |
| `StgFocusInRangeEx` | skipped, because Perfect Focus was still on |
| `Capture`, `ImageSaveAs`, `CloseCurrentDocument` | image saved (8.6 MB TIFF); **`Capture` returned 0 (DR_CANCELED) although it worked**; `ImageSaveAs` and `CloseCurrentDocument` returned 0 |

### What this means for the bridge

- An empty nosepiece slot is an empty name with DR_OK, not an error (one of the two open
  questions in `docs/testing.md`; on the simulator).
- `Capture` returns 0 on success, so a check must only treat negative values as failure, as the
  bridge's `_check_negative` already does.
- Switching Perfect Focus off is not visible at once; the bridge already waits `PFS_SETTLE_S`.

### Changed in the test after this run

- The `nis.call_proc` probe now tries both forms the error asks for (a count, a sequence).
- Perfect Focus: the status is polled until it changes (up to 5 s), and the report says whether
  it was put back.
- Autofocus now runs before the Perfect Focus round trip, so it is not skipped.
- The coverage check found 1 name in NIS's function list: the name extraction did not match
  that file's format. Fixed: it now reads 4071 functions in 20 sections, 4041 of them in the AR
  edition (350 of those with a module), and reports reachability per section.

### Changed in the test after this run: no DLL

Every function is now called through `nis.call_proc`, NIS's own way of calling a macro function
by name; nothing goes through `g5_regprocs.dll` any more. The test first learns how
`nis.call_proc` takes values handed back (a count or a sequence; for a text also a string), and
checks what it does with an unknown name. The reachability check by name, which needed the
DLL, is replaced by a count of NIS's function list per section.
