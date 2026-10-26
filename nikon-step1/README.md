# Step 1: can software outside NIS call NIS, without a crash or an error message?

Feasibility only, on **NIS-Elements AR 7.01.03** with the **microscope off**: readings only,
no moves, no camera. No Python is needed on the computer: NIS runs its own Python, and the
outside program is Windows PowerShell.

## Run it

1. Unzip `nikon-step1.zip` on the desktop (or to `C:\nikon-step1\`). A folder inside a folder is fine.
2. Start NIS without hardware: Win+R, then
   `"C:\Program Files\NIS-Elements\nis_ar.exe" -passive`
3. In NIS: Macro > Run Macro From File > `step1.mac` in that folder.
   NIS's status bar says "step 1: running on port 54471". The macro keeps running; that is
   intended. A self-test runs by itself in the first seconds.
4. Double-click `step1_client.cmd` in the same folder. A black window runs the checks from
   outside NIS. When it says "NIS will now be busy for 3 seconds", try moving the NIS window
   or opening a menu, and note whether NIS responds.
5. At the end the client stops the server and the macro ends by itself ("step 1: stopped").
   If it does not, press the macro Stop button.
6. Bring back the `results` folder, and note by hand:
   - Did NIS show any dialog or error message? (screenshot)
   - Did NIS stay usable while the macro ran, and during the 3 busy seconds?

## The results

- `step1_summary.txt`: the macro loop, the counts, dialogs seen, and the self-test, one line per check.
- `step1_client.txt`: the same checks from outside NIS (PowerShell), plus two connections at
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
└───────────────────────────┼────────────────────────────────┘
                            │ 127.0.0.1:54471, one JSON line each way
                 step1_client.cmd (PowerShell, outside NIS)
```

- The macro starts `step1_bridge.py` once, then loops: each pass calls `pump()`, which runs
  the requests that came in. So NIS functions run only on NIS's own thread, one at a time.
- The server only queues requests. Only readings may be called (`READS` in
  `step1_bridge.py`); a move is refused.
- Every error, in a request or in NIS's answer, goes back to the client as a reply.
- A thread notes every dialog window NIS opens, with its text (it never clicks).
- The loop ends on a `shutdown` request, after 15 minutes, or with the macro Stop button.
  Running the macro again is safe: it closes what an earlier run left behind.

A request is one line of JSON, for example
`{"op": "call", "fn": "StgGetPosZ", "args": [{"ptr": "double"}, 0]}`; the reply is one line,
`{"ok": true, "answer": {"return": 1, "values": [250.0, 0]}, "nis_ms": 0.02}`.

## If something goes wrong

- The client says "no bridge on port 54471": the macro is not running, or step 3 failed.
  Look at `results\step1.log`.
- PowerShell is blocked on this computer: the self-test inside NIS still runs. Send
  `step1_summary.txt`.
- NIS hangs: the last line of `results\step1.log` names the call.

## Tested offline

`../nikon-step1-offline-test/run.py` runs the macro's own Python lines against a stand-in
`nis` module, with a loop on the main thread in place of the macro and a client sending the
same lines as `step1_client.ps1`. All checks pass there, including a second start after a
run that was never stopped. Not tested offline: the macro language itself, the PowerShell
client, the dialog watcher, and NIS.
