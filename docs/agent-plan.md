# Plan: the NIS assistant, lean and on the microscope's own procedures

Version 1.0, 10 October 2026. Applies `agent-lessons.md` (from mesoSPIM-control, branch
`agent/roadmap-2`) to this repository. Each work package is its own branch and pull request into
`main`; tick an item with its date and commit when it is done.

## Decisions (the owner's)

1. **The microscope's own procedures.** Acquisitions are NIS-Elements' own ND acquisition: NIS
   drives the timing, the stage, the Perfect Focus and the file. The assistant defines and starts
   it, reads its progress, and can stop it. It never assembles its own loop of moves and snaps,
   and it has no timer of its own. The useq engine (part 2) stays as a product for people who
   want useq; the assistant does not use it to run acquisitions.
2. **General, not fitted.** A short general manual; the tools carry the detail. No line, override
   or case is written to pass one evaluation case. Fitting is per instrument, in its skills.
3. **Safety is the instrument's.** Limits the bridge enforces, the busy state and Stop protect
   every client alike. No go-ahead gate or guard in the assistant.
4. **One way in.** The assistant's tools come from the bridge's command list, with the same
   checks and refusals; MCP or other clients reach the same commands.
5. **Cloud models first,** with prompt caching on Anthropic.

## WP1. Native ND acquisitions (branch `agent/nd`)

- [ ] **1.1 The macro functions.** From the macro reference installed with NIS
  (Docs/nis/eng_ar, Macro > Command list), the exact signatures to define an ND experiment
  (`ND_DefineExperiment` and the per-dimension setters such as `ND_SetZSeriesExp`), to run it, to
  read whether it runs and how far it is, and to stop it. **Needs the owner:** the names and
  signatures of the run, status and stop functions, which this session could not reach.
- [ ] **1.2 Bridge commands.** `define_nd_acquisition` (time points and interval, XY points, Z
  range and step, optical configurations, PFS, file), `run_nd_acquisition`, `get_nd_progress`,
  `stop_nd_acquisition`, in `commands.py` and `readers.py`, with the fake in `fake.py`. Each
  checks its arguments and reads the state back, like every other command.
- [ ] **1.3 The assistant's tools.** One tool to define and start, returning "running" at once;
  the turn ends; the window reads the progress and writes one line when it finishes. A tool to
  read the progress and one to stop. `run_acquisition` over useq retires from the assistant.
- [ ] **1.4 Tests and docs.** The bridge's tests on the fake, a hardware test on the Ti2
  simulator, the README and tutorial of part 3.

## WP2. Lean, for cloud models (branch `agent/lean`)

- [ ] **2.1 Anthropic and caching.** A Claude preset (claude-haiku-5-5) through
  `pydantic-ai-slim[anthropic]`, with tool definitions and instructions cached for an hour and
  the history for five minutes; the other providers unchanged. A test reads the cache marks off
  the request on the wire.
- [ ] **2.2 No timer.** `schedules.py`, the schedule tools and the window's clock go; a time
  course is NIS's own time loop (WP1).
- [ ] **2.3 No small-model scaffolding.** History compaction (`memory.py`), the "called nothing"
  challenge and the local-model mode go. The history is append-only until Clear; the window shows
  the session's size and refuses a turn past a ceiling per model.
- [ ] **2.4 Every tool sequential.**

## WP3. Safety at the bridge (branch `agent/limits`)

- [ ] The go-ahead gate and `guarded_tool` go. The bridge refuses moves outside the stage
  limits for every client; the assistant reports a refusal and does not retry with another value.

## WP4. One registry (branch `agent/registry`)

- [ ] The assistant's tools are generated from the bridge's `COMMANDS` and readers, each with a
  factual description and a schema; refusals list the instrument's options. The hand-written
  wrappers in `tools.py` shrink to the tools that are the assistant's own (looking at an image).

## WP5. A short manual (with WP2)

- [ ] `instructions.py` (233 lines) becomes about 30: who the assistant serves, units and axes,
  tool results and the state are data, nothing reported that no tool shows, and the rule for
  unclear requests: suggest what you would do and ask before doing it; if you don't know, ask.

## WP6. Skills (branch `agent/skills`)

- [ ] `skills.py` from mesoSPIM-control: one Markdown file per skill in a folder next to the
  settings, listed by description, loaded with `load_skill` before the first change. None ship.

## WP7. Evaluation

- [ ] Single runs against the fake; failures sorted into the framework's and the instrument's;
  the test checked before the model is blamed. Haiku and flash-lite once each per package.

## Order

WP2.1 first (small, independent), then WP1 once 1.1 is answered, then WP2.2 to WP5, then WP6.
