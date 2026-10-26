# Step 1, run 1: 2026-10-26, NIS-Elements AR 7.01.03, microscope off

The first version of step 1 (self-test only, no outside client). NIS started normally, not
with `-passive`. Ended with the macro Stop button, so `stop()` did not run and the summary
has no end time.

- All 13 self-test checks ok; every NIS call on NIS's own thread; no pump errors, no timeouts.
- Deliberate failures came back as replies, no dialog: unknown function (`AttributeError`),
  wrong arguments (`error: Bad number of parameters`), Python error, a move (refused).
- Round trip 11 ms median, set by the macro loop's `Wait(0.01)`.
- Optical configurations: 0 (step 0 with `-passive`: 3).

Dialogs noted:

| Time | Dialog | Source |
|---|---|---|
| 17:34:18 | untitled, button "Continue" | the macro's own `WaitText` message |
| 17:35:38 | "Command Interpreter Error: Cannot Evaluate the Expression. `EnableShading(2)`" | the shading correction button (pressed in place of Stop, see run 2); `EnableShading` is a camera function, absent without the camera (step 0) |
| 17:35:48 | "Interrupt Macro Execution?" | the Stop button |
