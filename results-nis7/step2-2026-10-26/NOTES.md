# Step 2 on NIS-Elements AR 7.01.03, microscope off: progress

Every AR macro function called once through `nis.mac`, with no arguments. The table so far:
[STEP2_FUNCTIONS.md](STEP2_FUNCTIONS.md) (spreadsheet: `step2_functions.csv`). Functions not
reached yet show as *not called*.

## Where it stands: 520 of 3667 (14 %), 2026-10-26 18:27

| Result | Number |
|---|---:|
| ran | 101 |
| needs arguments | 252 |
| not reachable | 149 |
| needs the camera (not run, camera off) | 16 |
| crashed or hung | 2 (+1 running when stopped) |

Run 5 (`run5/`), version that still closed NIS on a hang: the readings (Get*, Is*) first,
then the rest. Hung: `GetYeastFocusCtiterion`, `_ManualLargeImage`, and `_StitchLargeImage`
(running when NIS was closed the third time; the run did not carry on after that).

## What the runs taught

| Run | Files | What happened | Changed since |
|---|---|---|---|
| 1, 2 | `run1_`, `run2_` | `_CaptureEDF` waits for the camera (returned by itself after 153 s); NIS closed at 60 s | camera functions not run with the camera off |
| 3 | `run3_` | `Experiment_DetectParfocalities`, `Experiment_RunAutoAll`, `Experiment_RunAutoBrightnessOnAllChannels` hung | Experiment_, Auto*, focus, shading, ND run: not run with the camera off |
| 4 | `run4_` | stopped after 188 readings: the progress file was locked by the watch window (WinError 5) | the progress file never stops the run |
| 5 | `run5/` | 520 functions; 3 hangs, NIS closed for each | NIS never closed; Escape on a hang; what a call changes is put back |

- Restarting NIS from outside works on 7.01: `nis_ar.exe -c RunMacro("...step2.mac")`.
- NIS's own `python.exe` (`C:\Program Files\NIS-Elements\Python\`) runs the watch window.
- Underscore functions such as `_ManualLargeImage` open NIS setup windows that are not
  standard dialogs, so the watch window cannot close them.

Next: carry on from 521 with the current files (never closes NIS, Escape on a hang, puts back).
