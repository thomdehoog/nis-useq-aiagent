# Step 1: can software outside NIS call NIS, without a crash or an error message?

Feasibility only, on **NIS-Elements AR 7.01.03** with the **microscope off**: readings only,
no moves, no camera. It runs by itself: one macro, nothing else to click, and no Python to
install, because NIS brings its own.

## Run it

1. Unzip `nikon-step1.zip` on the desktop (or to `C:\nikon-step1\`). A folder inside a folder is fine.
2. Start NIS (normally, or without hardware with `"C:\Program Files\NIS-Elements\nis_ar.exe" -passive`).
3. In NIS: Macro > Run Macro From File > `step1.mac` in that folder.
4. After a few seconds a black window opens and shows each check as it runs. Leave NIS
   alone until it says **STEP 1 FINISHED** (about half a minute); NIS's status bar then also
   says "step 1: FINISHED". Press Enter to close the window. If no window opens, the run
   still stops by itself, at the latest after 5 minutes.
5. Bring back the `results` folder, and note by hand:
   - Did NIS show any dialog or error message? (screenshot)
   - Did NIS stay usable while it ran? (At one point NIS is kept busy for 3 s on purpose.)
   - Was NIS started normally or with `-passive`?

## The results

- `step1_summary.txt`: the macro loop, the counts, dialogs seen, and the self-test, one line per check.
- `step1_client.txt`: the same checks from a program outside NIS, plus two connections at
  once, a client leaving mid-request, NIS busy for 3 s, and the stop.
- `step1_report.json`: everything in full.
- `step1.log`: the run step by step. If NIS hangs or crashes, the last `RUN` line names the call.

Expected: every line `ok`. Lines such as "unknown function" or "Python error" are *meant* to
fail inside, and pass when the failure comes back as a reply instead of a dialog or a crash.

## How it works

```
┌─────────────────────── NIS-Elements ───────────────────────┐
│                                                            │
│ step1.mac ── loop ──► NIS's Python: pump() ──► nis.mac ────┼──► (readings)
│                           ▲  runs queued requests,         │
│                           │  on NIS's own thread           │
│                 server thread (step1_bridge.py)            │
│                           ▲          │ self-test thread    │
└───────────────────────────┼──────────┼─────────────────────┘
                            │          │ starts
       127.0.0.1:54471, one │          ▼
       JSON line each way   └── step1_client.py, a program of its own,
                                 run by NIS's own python.exe
```

1. The macro has NIS's Python start `step1_bridge.py` (the same way `step0.mac` started
   `step0_test.py`), then loops: each pass calls `pump()`, which runs the requests that came
   in. So NIS functions run only on NIS's own thread, one at a time.
2. A thread runs the checks (`step1_checks.py`) through the server: the self-test.
3. Then NIS's Python starts `step1_client.py` as a separate program, with NIS's own
   `python.exe`. That is the real test: a program outside NIS, the way our software will
   call NIS later. If NIS has no `python.exe`, it uses `step1_client.ps1` (PowerShell) instead.
4. The client runs the same checks and more, then asks the server to stop; the macro ends.

- Only readings may be called (`READS` in `step1_bridge.py`); a move is refused.
- Every error, in a request or in NIS's answer, goes back to the client as a reply.
- A thread notes every dialog window NIS opens, with its text (it never clicks).
- Running the macro again is safe: it closes what an earlier run left behind.

A request is one line of JSON, for example
`{"op": "call", "fn": "StgGetPosZ", "args": [{"ptr": "double"}, 0]}`; the reply is one line,
`{"ok": true, "answer": {"return": 1, "values": [250.0, 0]}, "nis_ms": 0.02}`.

## If something goes wrong

- No `step1_client.txt`: the outside client could not start. `step1_summary.txt` says why
  (line "outside client"); the self-test still ran. By hand: double-click `step1_client.cmd`
  while the macro runs.
- NIS hangs: the last `RUN` line of `results\step1.log` names the call.

## Tested offline

`python nikon-step1-offline-test/run.py` (in the repository) runs the macro's own Python
lines against a stand-in `nis` module, with a loop on the main thread in place of the macro.
The self-test and the outside client run for real. All checks pass, the run stops by itself
in about 10 s, and it also stops cleanly when no client can be started. Not tested offline:
the macro language itself, NIS's own `python.exe`, the PowerShell fallback, the dialog
watcher, and NIS.
