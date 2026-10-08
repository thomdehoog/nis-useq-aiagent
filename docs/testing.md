# Testing on NIS-Elements

With NIS-Elements running, `start_bridge.mac` started, and the `nis` conda
environment active, test the parts in order, and stop at the first step that
fails, since each builds on the one before. Always name the part's folder, as
shown. Everything stays within 100
um of where the stage is, and the stage is moved back afterwards; still, keep
the objective clear of the sample for the first run.

```
pytest -m hardware -s 1_nis_bridge      # 1. read, move a little, configuration and exposure, snap
pytest -m hardware -s 2_nis_engine      # 2. camera field, limit check, useq v2 and classic, tiles, channel options, a sequence file
pytest -m hardware -s 3_nis_assistant   # 3. the assistant's tools, with a scripted model (no API calls)
```

`-s` prints what NIS reported and where the images were saved. Tests that need
a pixel calibration for the objective in use (the camera field, tiles) are
skipped without one, and say so. In step 2, a yellow pymmcore-plus warning
about `do_stack=False` is expected; the test checks the saved images itself.

## The assistant with a real model

Then try the assistant with the real model (`nis-assistant`; choose the model
and type its key in the Model panel at the top), in this order, and check each
answer against NIS. NIS needs at least one optical configuration (Calibration
> New Optical Configuration); without one, the assistant walks you through
adding it:

1. *Where is the stage, and which objective is in use?* (reads only)
2. *Move x by 20 um.* (moves at once) and *Move x by 5 mm.* (asks first; answer *no*)
3. *Move z to 20000 um.* (refused: red banner, nothing moves)
4. *Switch to* a configuration NIS has, *at 50 ms.*
5. *What do you see?* (the image appears on the right)
6. *Take a Z-stack of 4 um in 2 um steps here in* a configuration. (shows the
   plan and asks; answer *yes*; the files appear in the output folder)
7. *Image a 2 by 2 grid of tiles around here.* (needs a pixel calibration)
8. *Show me the useq sequence for that plan*, *What is new in useq v2?*, and
   *How does the engine move the stage? Show me the code.*
9. *Move the sample 100 um to the left.* (check on the screen that it went left; if
   not, change the Coordinate system box in the Model panel)
10. *Look again: has anything changed since the first image?* (the eyes compare with
    what they saw in step 5)
11. *Look every three minutes and tell me whether the sample drifts.* (a scheduled
    turn appears in the chat when it is due, and a row above the input line counts
    down to the next one; *Cancel schedule* in that row, or *Stop microscope*,
    cancels it)
12. *Look and call this "before".* Nudge the stage a little with the joystick, then
    *Has it drifted since "before"?* (the answer gives the shift in um, measured from
    the two images; it needs a pixel calibration for the objective)
13. *Take 10 time points 30 s apart here in* a configuration, *and tell me what the
    last image shows.* Answer *yes*. (the assistant says the run is under way and
    ends its turn; the request line above the input shows it waiting; type a
    question meanwhile; when the run ends, the chat shows "Request N continues" and
    the assistant reports the result and the last image)
14. *What was the focus before I moved it?* (answered from the session store)

## Let a coding assistant do it

To let a coding assistant on the microscope computer do all of this, give it this prompt:

```
In this repository, test the three parts on this NIS-Elements computer.
NIS-Elements is running and start_bridge.mac has been started (ask me if the
bridge does not answer). Work in three steps and stop at the first
failure, showing me the output and what you think went wrong; do not change
code without asking.
1. Run `pytest -m hardware -s 1_nis_bridge`.
2. Run `pytest -m hardware -s 2_nis_engine`, and tell me the shapes of the
   images it saved (it prints them).
3. Run `pytest -m hardware -s 3_nis_assistant`. Then start the window with
   `nis-assistant` and tell me, one at a time, the prompts from the checklist
   in docs/testing.md, and what to look for after each.
Finish with a short report: what passed, what was skipped and why, and
anything that looked wrong.
```

## Status

Validated on 2026-09-26 on NIS-Elements AR 6.10.02 with the Ti2 simulator:
all hardware tests of the three parts, and the assistant with Gemini. The code
was then reorganised into smaller files (2026-09-27), without changing what it
does, and re-tested on the fake NIS only; the next run on NIS-Elements will
confirm it there. Not yet run on a live Ti2 with a sample. Two things only a
real turret can settle: how an empty nosepiece slot is reported, and whether a
failing `Capture` returns a negative code.

---

MIT license. Thom de Hoog, Center for Microscopy and Image Analysis (ZMB),
University of Zurich. thom.dehoog@zmb.uzh.ch, thomdehoog@gmail.com.
If you use this work or build on its ideas, please acknowledge the author in
what you make from it.
