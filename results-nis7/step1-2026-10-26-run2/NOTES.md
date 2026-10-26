# Step 1, runs 2 and 3: 2026-10-26, NIS-Elements AR 7.01.03, microscope off

Two more runs (17:39 and 17:44) in the same NIS session as run 1 (pid 25448). Both still ran
the *old* step 1 files (self-test only): the macro took the first `step1_bridge.py` it
found, an older copy, not the new one in `Desktop\nikon-step1\nikon-step1\`. Since then the
macro takes the newest copy, and the log names the file and version.

- Each run: all 13 self-test checks ok, identical to run 1. Starting again in the same NIS
  session works: "closing the server of an earlier run", then a clean start.
- `EnableShading(2)` "Cannot Evaluate the Expression" (17:42 to 17:43, six dialogs, and
  run 1's at 17:35): the shading correction button, pressed in place of the macro Stop
  button. Without the camera NIS cannot run it. Not the test.
- The untitled dialogs with a "Continue" button at each start are the macro's own
  `WaitText(...)` messages.
- "Confirm Interrupting Macro": the Stop button.
