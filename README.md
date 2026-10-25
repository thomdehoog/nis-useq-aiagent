# Step 0: test what NIS-Elements lets our Python do

## Run it

1. Unzip `nikon-step0.zip` on the desktop (or to `C:\nikon-step0\`). Any folder name works.
2. Start NIS without hardware: Win+R, then
   `"C:\Program Files\NIS-Elements\nis_ar.exe" -passive`
3. In NIS: Macro > Run Macro From File > `step0.mac` in that folder.
4. Wait until NIS responds again (a minute at most).
5. Bring back the `results` folder that appears next to the files.

## The results

- `step0_summary.txt`: one line per check, ok or FAIL.
- `step0_report.json`: everything in full.
- `step0.log`: the run step by step. If NIS hangs, the last line names the call.

Without hardware, these are expected and fine: readings that say `DR_NOTAVAILABLE`, and
camera or device functions listed as missing.

## Writes (later, with hardware)

All writes are off. To test one, open `step0_test.py` in Notepad, change one
`ALLOW_... = False` to `True`, save, and run `step0.mac` again. One at a time, with someone at
the microscope. Each write is put back afterwards.

## Note by hand

- Help > About: is it AR?
- With the bridge running: what does the flickering text at the bottom say? (screenshot)

## How we connect

```
┌──────────────────── NIS-Elements ────────────────────┐
│                                                      │
│ step0.mac ──► NIS's Python ──► nis.mac ──────────────┼──► microscope
│ (a macro)     (step0_test.py)  (any function)        │
│                    │                                 │
└────────────────────┼─────────────────────────────────┘
                     ▼
                 results\  (the report)
```

1. **The macro** is the way in: NIS runs macros, and one line of macro starts Python.
2. **NIS's own Python** runs our code, inside NIS. No separate Python is needed.
3. **`nis.mac`** is Nikon's documented door from that Python to every macro function: stage,
   focus, optical configurations, capture, saving … by name, with the values coming back.
4. **The microscope** does what the function says.

The driver later works the same way, with one step added: the Python inside NIS listens for
requests from our software outside NIS.

```
our software  ──►  NIS's Python  ──►  nis.mac  ──►  microscope
(outside NIS)      (started by a macro)
```
