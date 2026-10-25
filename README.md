# Step 0: test what NIS-Elements lets our Python do

Run on **NIS-Elements AR 7.01.03 (Build 2233)**, with its own Python 3.12.4 (version and Python as reported by the test itself, 2026-10-25; edition from Help > About).

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

- Help > About: is it AR? (2026-10-25: yes)
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

The options for connecting our software to NIS:

1. **TCP via NIS's own Python** (`socketserver`, 127.0.0.1): our choice. Standard library,
   values come back, already working in the bridge.
2. **NkSocket:** Nikon's TCP in a macro. The same idea, but text commands only, no values back.
3. **COM port (NkComPort):** serial, for devices such as an Arduino, not for programs.
4. **Windows COM/ActiveX:** NIS offers none.
5. **REST API:** from Nikon, but it needs a separate licence.
6. **Files or named pipes:** possible, but slower or more fiddly, with no benefit.

## What our Python can reach, with the microscope off

Step 0 on NIS-Elements 7.01.03, 2026-10-25, microscope switched off. Reachable means `nis.mac` offers the function by name. Every function: [FUNCTIONS.md](FUNCTIONS.md).

| Section | Reachable | Not reachable | Total |
|---|---:|---:|---:|
| Acquire | 153 | 199 | 352 |
| AdvancedAPI | 148 | 0 | 148 |
| Analysis | 208 | 20 | 228 |
| Applications | 38 | 160 | 198 |
| Binary | 385 | 7 | 392 |
| Calibration | 21 | 0 | 21 |
| Device | 502 | 112 | 614 |
| ExportResults | 57 | 0 | 57 |
| Image | 524 | 61 | 585 |
| ImageDocument | 143 | 4 | 147 |
| Macro | 59 | 3 | 62 |
| Measure | 173 | 0 | 173 |
| Misc | 7 | 0 | 7 |
| ND | 215 | 5 | 220 |
| Organizer | 75 | 0 | 75 |
| System | 105 | 6 | 111 |
| UserInterface | 26 | 0 | 26 |
| View | 201 | 1 | 202 |
| Visualization | 49 | 0 | 49 |
| **All** | **3089** | **578** | **3667** |

Most of what is not reachable needs the camera (Acquire: camera, live, ROI), belongs to hardware this system does not have (Device), or to modules not installed (Applications).
