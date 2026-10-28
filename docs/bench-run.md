# Bench run, done by Claude Code

This page is written for Claude Code (or another coding assistant) on the
microscope computer. It tests pull request #8 (branch `agent/clean-skills`)
on NIS-Elements from start to finish and writes a report. When everything
passes, it asks the operator for a yes and then merges the pull request into
`main`. The operator does three things:

1. Opens NIS-Elements (the microscope or its Ti2 simulator) and runs
   `start_bridge.mac` (*Macro > Run Macro From File...*).
2. Opens Claude Code in this repository, pastes an Anthropic API key into the
   chat, and types:

   ```
   Read docs/bench-run.md and do what it says. The key is above.
   ```

3. Answers yes or no when asked whether to merge.

The whole run takes about 20 minutes, most of it waiting for the model.

---

## Instructions for the coding assistant

Work through the steps in order. Tell the operator in one line what you are
starting before each step, since they may be watching. Do not change any code;
this is a test, and a failure is a finding to report, not something to fix
here. If a step fails, stop that step, keep its output, and go on to the
report (step 7).

### The API key

The operator pasted an Anthropic API key into the chat. Use it only as the
environment variable `ANTHROPIC_API_KEY`, set for the commands that need it
(steps 5 and 6). Never write it to a file, a commit, a log or the report, and
never print it. If no key was pasted, ask for one before step 5.

### Step 1: the branch

```
git fetch origin
git checkout agent/clean-skills
git pull origin agent/clean-skills
```

If the working tree has local changes, stop and ask the operator what to do
with them; do not discard them.

### Step 2: the packages

The Python environment is the conda environment `nis` (see the README). Run
every Python command in it, for example through `conda run -n nis
--no-capture-output ...`, or activate it if your shell allows.

```
pip install -e "./1_nis_bridge[test]" -e "./2_nis_engine[test]" -e "./3_nis_assistant[test,anthropic]"
```

### Step 3: the bridge answers

```
python -c "from nis_engine import NisEngine; e = NisEngine(); print(e.client.request('ping')); print(e.client.request('get_optical_configurations'))"
```

If this fails, ask the operator to start `start_bridge.mac` in NIS-Elements and
try again. If NIS lists no optical configuration, ask the operator to make one
(*Calibration > New Optical Configuration*) and try again.

### Step 4: the hardware tests

These use a scripted model, so they cost nothing. Run them in order:

```
pytest -m hardware -s 1_nis_bridge
pytest -m hardware -s 2_nis_engine
pytest -m hardware -s 3_nis_assistant
```

All three must pass. A skipped test is fine when its reason says the
simulator lacks the hardware (for example a pixel calibration); note it.

### Step 5: the automatic bench run

This sends the assistant checklist from `docs/testing.md` to the real model
(Claude Haiku 5.5) on the running NIS, checks each step and writes a report.
It narrows the stage limits to a small box first and moves the stage back at
the end. Run it from the repository's top folder, with the key set:

```
python 3_nis_assistant/tests/bench.py
```

It prints PASS or FAIL per step and writes `bench-<date>-<time>/report.md`.
Read the report. Every step must pass. Steps marked *To read* also need your
judgement: say in one sentence each what the assistant did there.

The prompt cache line at the end of the report should say that about 90 % or
more of the input was read from the cache. Much less means caching does not
work, which counts as a failure.

### Step 6: the acquisition cases

These run against the fake microscope that ships with part 1, not against
NIS, so they can run while NIS is open. They are the cases not yet rerun since
the last change to the instructions. With the key set:

```
cd 3_nis_assistant
python tests/evals.py --model anthropic:claude-haiku-5-5 --only acquisition-two-channels,acquisition-z-stack,acquisition-time-lapse,useq-file-run --repeat 3
python tests/evals.py --model anthropic:claude-haiku-5-5 --holdout --only h-acquisition-two-channels,h-acquisition-z-stack,h-acquisition-time-lapse,h-useq-file-run --repeat 3
cd ..
```

Each case runs three times. Pass means at least 11 of the 12 runs pass in each
of the two commands, with no case failing twice. The trace files
`evals-*.jsonl` stay in `3_nis_assistant`; do not commit them.

### Step 7: the report

Write the report for the operator in the chat, in plain sentences:

- Each of steps 1 to 6: passed or failed, and for a failure the exact output.
- The bench steps marked *To read*, one sentence each.
- The cache percentage.
- The NIS-Elements version (from the ping in step 3).

Also save it as `bench-report.md` in the bench folder from step 5, next to
`report.md`. Do not commit the bench folder.

### Step 8: the merge, with the operator's yes

Only when steps 3, 4, 5 and 6 all passed as defined above, end the report
with this question: "Everything passed. Shall I merge pull request #8 into
main?" Wait for the answer. On a clear yes:

```
git checkout main
git pull origin main
git merge --no-ff agent/clean-skills -m "Merge pull request #8 from thomdehoog/agent/clean-skills"
git push origin main
```

If the merge has a conflict, or the push is refused, run `git merge --abort`
if a merge is in progress, and tell the operator. Do not force anything.

If anything did not pass, do not offer the merge. Tell the operator what
failed and that the report is in the bench folder, so they can bring it back.

### Afterwards: the live demo

Leave the operator with the window open for the demo:

```
nis-assistant
```

The Model panel opens on Anthropic with `claude-haiku-5-5` filled in; the
operator pastes the key there and presses *Connect*. Remind them to
set the limit fields in the Model panel before the first move.
