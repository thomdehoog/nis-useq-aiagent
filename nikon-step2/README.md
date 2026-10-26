# Step 2: call every NIS function, and note what happens

All 3667 macro functions of NIS-Elements AR 7.01.03, each called once, **microscope off**.
Nothing is skipped. It runs by itself; nothing to install.

## Run it

1. Unzip `nikon-step2.zip` on the desktop.
2. Start NIS (microscope off).
3. In NIS: Macro > Run Macro From File > `step2.mac` in that folder.
4. A black window opens and shows the progress (`[1234/3667] FunctionName`) and every window
   a call opens, which it closes. Leave NIS alone until it says **STEP 2 FINISHED**.
5. Send the `results` folder.

**If NIS crashes or hangs:** close NIS (Task Manager if needed), start it again, and run
`step2.mac` again. It carries on after the function that crashed, and marks that one
"crashed or hung". Repeat until FINISHED. The macro Stop button pauses the same way.

## How

- The macro loops; each pass has NIS's Python call the next functions for 50 ms, each
  through `nis.mac`, with no arguments, on NIS's own thread, inside try/except.
- Before each call its name goes to `results\step2_calls.jsonl` (written to disk at once),
  and its answer after. So after a crash the last `start` line names the function.
- The functions that end a run (quit NIS, stop or run a macro) come last.
- `step2_watch.py` runs as a program of its own with NIS's own `python.exe`: it shows the
  progress, and closes any window a call opens (Cancel, No, Close or OK, in that order),
  noting it in `results\step2_dialogs.jsonl`. It never touches "Confirm Interrupting Macro".

## What each function gets

| Result | Meaning |
|---|---|
| ran | it needs no arguments and ran; its return value is kept |
| needs arguments | NIS answered "Bad number of parameters": reachable, not run (a later pass, with real arguments) |
| error | another error from NIS |
| not reachable | NIS does not offer it now (camera, other hardware, modules) |
| crashed or hung | NIS went down in this call |

`make_table.py results` turns the results into `STEP2_FUNCTIONS.md` and `step2_functions.csv`.
