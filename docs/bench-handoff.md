# Bench test handoff (2026-10-10)

A note for picking the work up on the microscope computer. The full checklist
is in [testing.md](testing.md); this page says what changed, what to watch,
and what to bring back.

## What is new on `main` since the last bench run

- **No asking in between.** A tool call within the limits runs at once: long
  stage moves and acquisitions included. A call outside them is refused with
  the limit, the range or the options (red banner, nothing moves).
- **A short manual.** The model's instructions (`3_nis_assistant/nis_assistant/instructions.py`)
  are about 35 lines now.
- **Anthropic models**, with prompt caching. Install the extra once (below).
- **Gone:** the Local AI mode, schedules and the clock tools. For imaging over
  time the assistant plans an acquisition with time points.

Simulator status: 114 unit tests pass and CI is green on `main`. The fake-NIS
eval with Haiku passed 53 of 58 cases. The five failures were fixed afterwards
(three stale cases, two manual lines, one case that wrongly expected "focus up"
to mean +z: the assistant now rightly asks which way), and a rerun of the
fixed cases with Haiku passed all of them.

## Get it running

```
git pull                                   # on main
conda activate nis
pip install -e "./1_nis_bridge[test]" -e "./2_nis_engine[test]" -e "./3_nis_assistant[test,anthropic]"
```

Start NIS-Elements and `start_bridge.mac` (or use `nis-assistant --start-nis`).

## Before the first move

1. **Set the limit fields** below the chat to a safe box around the sample.
   Nothing asks before a long move any more; the limits are the safety.
2. Keep the objective clear of the sample for the first run.
3. Type the API key in the Model panel only (never in a file).

## The test, in order

1. `pytest -m hardware -s 1_nis_bridge`
2. `pytest -m hardware -s 2_nis_engine`
3. `pytest -m hardware -s 3_nis_assistant`
4. `nis-assistant`, then the 11 prompts in [testing.md](testing.md#the-assistant-with-a-real-model).

Watch closely:

- *Move x by 5 mm* now moves at once (within the limits).
- *Move z to 20000 um* is refused, and the assistant does not try a nearby value.
- *Stop microscope* during an acquisition, and *Cancel prompt* during a move.
- A task of several steps (*switch to DAPI, take a Z-stack, then describe it*)
  runs through without a question in between.

Two things only a real turret settles: how an empty nosepiece slot is
reported, and whether a failing `Capture` returns a negative code.

## Bring back

1. **What passed, what failed** (the pytest output, and any odd reply).
2. **The ND acquisition macro names**, needed for WP1 (acquisition run by
   NIS itself). In NIS-Elements open *Macro > Command* and note the functions
   that define, run, report the status of and stop an ND experiment. Known so
   far: `ND_DefineExperiment`, `ND_SetZSeriesExp`, `ND_GetZSeriesExp`,
   `ND_RunZSeriesExp`. A screenshot of the list is enough.
3. The NIS-Elements version (Help > About).

## What comes next

From [agent-plan.md](https://github.com/thomdehoog/nis-useq-aiagent/blob/agent/plan/docs/agent-plan.md)
(on branch `agent/plan`):

- **WP4, one registry:** the assistant's microscope tools generated from the
  bridge's commands and readers. Waits for this bench test.
- **WP1:** NIS ND acquisition, once the macro names are known.
- **WP6, skills, and WP7, evaluation:** after WP4.

## Prompt for a coding assistant on the microscope computer

```
Read docs/bench-handoff.md and docs/testing.md in this repository. Run the
three hardware test steps in order and stop at the first failure, showing me
the output; do not change code without asking. Then walk me through the
assistant checklist one prompt at a time. Finish with a short report: what
passed, what was skipped and why, anything that looked wrong. Finally help me
list the ND_* functions under Macro > Command in NIS-Elements.
```
