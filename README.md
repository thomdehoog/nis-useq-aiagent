# Step 0: test what NIS-Elements 6.10 lets our Python do

The mirror of the NIS 7 Step 0 (branch `agent/nis-7-step0`), for **NIS-Elements AR 6.10.02**
on the Ti2 simulator: the version the bridge was built and tested on. It calls every NIS
function the bridge uses, so the two versions can be compared function by function.

## Run it

1. Download this branch (GitHub: Code > Download ZIP) and unzip it on the desktop (or to
   `C:\nikon-step0-610\`). Any folder name works. The NIS 7 folder can stay on the desktop:
   `step0.mac` only runs a `step0_test.py` whose first line says 6.10.
2. Start NIS-Elements 6.10 with the Ti2 simulator.
3. In NIS: Macro > Run Macro From File > `step0.mac` in that folder.
4. Wait until NIS responds again (a minute or two: the writes move the simulated stage).
5. Bring back the `results` folder that appears next to the files.

Optional, for the coverage check: copy NIS's own `FunctionList_6.10.02.html` next to
`step0_test.py`. The test also looks for it under `C:\Program Files\NIS-Elements`. The list is
Nikon's and is **not** part of this branch; neither is anything made from it. The per-function
answer goes to `results\functions.csv`, which stays on the NIS computer.

## The results

- `step0_summary.txt`: one line per check, ok or FAIL.
- `step0_report.json`: everything in full.
- `step0.log`: the run step by step. If NIS hangs, the last line names the call.
- `functions.csv`: per function in NIS's list, reachable by name or not (local only, see above).

## What it calls

Every NIS function in `1_nis_bridge/nis_bridge/nis_dll.py`, the way the bridge calls it
(ctypes on `g5_regprocs.dll`; `nis.call_proc` for `Camera_ExposureSet`):

| | Functions |
|---|---|
| Readings | `Get_InfoStr`, `StgGetPos`, `StgXY_GetLimits`, `StgZ_GetLimits`, `GetOptConfCount`, `GetOptConfName`, `Stg_IsNosepiecePresent`, `Stg_GetNosepiecePositions`, `Stg_GetNosepiecePosition`, `Stg_GetNosepieceObjectiveName`, `Stg_IsPFSPresent`, `Stg_GetPFSStatus`, `Get_Calibration` |
| Writes, each put back | `StgMoveXY`, `StgMoveZ`, `StgMove`, `SelectOptConf`, `Camera_ExposureSet`, `Stg_SetNosepiecePosition`, `Stg_SetPFSStatus`, `Stg_WaitForPFS`, `StgFocusInRangeEx`, `Capture`, `ImageSaveAs`, `CloseCurrentDocument` |
| Also read, to compare with NIS 7 | `StgGetPosXY`, `StgGetPosZ`, `GetSelectedOptConf` |

It also tries each of the three ways of calling (ctypes, `nis.call_proc`, `nis.mac`) on the
same reading, and times them.

## Writes

Unlike on NIS 7, the writes are **on**: this run is for the simulator. `Camera_ExposureSet`
leaves the exposure at 50 ms (it cannot be read back without a blocking dialog). On a real
microscope, open `step0_test.py` in Notepad, set every `ALLOW_... = True` to `False`, and switch
them on one at a time, with someone at the microscope.

Off by default, as on NIS 7: `ALLOW_CAMERA_READ` (`Camera_ExposureGet` opened a blocking dialog
on the 6.10 simulator) and `ALLOW_COMMAND_TEXT` (`Int_ExecuteCommand`, may hang).

## Note by hand

- Help > About: the version and edition (AR?).

## How we connect

```
┌──────────────────── NIS-Elements ────────────────────┐
│                                                      │
│ step0.mac ──► NIS's Python ──► g5_regprocs.dll ──────┼──► microscope
│ (a macro)     (step0_test.py)  (ctypes; call_proc    │    (simulator)
│                    │            for the exposure)    │
└────────────────────┼─────────────────────────────────┘
                     ▼
                 results\  (the report)
```

On 6.10 the bridge reaches NIS through ctypes on `g5_regprocs.dll`, and through
`nis.call_proc` for the one function the DLL does not export. NIS 7.01 has no
`nis.call_proc` but has `nis.mac`; this run shows whether 6.10 already has `nis.mac`.
