# nis-assistant

A chat window where you ask for things at the Nikon microscope in your own
words. A language model (Gemini by default; OpenAI, a server of your own or a
model file on this computer also work) does them with the microscope and
explains what it did. The model never touches the
microscope directly: it can only call a small set of tools written here, and
every tool checks what it is asked before acting. Pydantic AI is the Python
library that connects the model to those tools.

It is also a demonstration of the other two parts: it runs its acquisitions as
useq sequences on the nis-engine, explains them in useq terms (the
classic form and useq v2), runs sequences made in other useq tools, and can
read the source code of all three parts and of useq-schema to explain how
things work.

This is part 3 of three; see the [overview](../README.md). The
[tutorial](docs/tutorial.md) is a first conversation step by step, with what
to expect and why; this README is the reference.

## Install and start

On the microscope computer, parts 1 and 2 first, then this part:

```
pip install -e ../1_nis_bridge
pip install -e ../2_nis_engine
pip install -e .
```

Then one command starts everything: NIS-Elements with the bridge macro (when
it is not open yet), and the window, which connects as soon as the bridge
answers:

```
nis-assistant --start-nis --output D:\runs
```

`python -m nis_assistant` does the same. Without `--start-nis`, start the bridge
in NIS-Elements as part 1's README describes; the window opens either way, and
says which macro file to run when the bridge is not there.

`--output` is where acquisitions are saved; without it, they go to
`nis_assistant_runs` in your home folder. `--font-size 13` makes the letters
bigger (the default is 11), and the divider between the chat and the image can
be dragged.

### Choosing the model

The **Model** line at the top of the window folds open to the choice. A cloud
model needs an API key, which you type into the panel; it stays in memory for
this session only and is never written anywhere. Each message costs a small
amount; the provider's pricing page says how much.

| Provider | Default model | Key from |
|---|---|---|
| Gemini | `gemini-3.5-flash-lite` (generous free tier) | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `gpt-5-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-style server | `gemma4:31b` at `http://localhost:11434/v1` | none, unless the server asks |

Press *Use this model*; the conversation so far is kept. A key can also come
from the environment (`GEMINI_API_KEY`, `OPENAI_API_KEY`): the panel then says
so, and the field can stay empty. `--model openai:gpt-5-mini` on the command
line starts with that choice. OpenAI (and an OpenAI-style server) needs its
library: `pip install -e ".[openai]"`.

An **OpenAI-style server** is anything that speaks the OpenAI chat API: Ollama,
vLLM, LM Studio, or a gateway at your institute. Tick *Can see images* when its
model can look at pictures. Such a server must allow requests of about 6,000
tokens; Ollama does not by default (set `OLLAMA_CONTEXT_LENGTH=16384`).

A **file on this computer** (`.gguf`, from Hugging Face) is served by the window
itself, with no internet at all: `pip install "llama-cpp-python[server]"`, put
the file in `nis_assistant_models` in your home folder (or choose another folder
in the panel), pick it and press *Use this model*. A model can see images when
its projector file (`mmproj` in the name) sits next to it. Small models make
more mistakes with the tools; the instructions are written for the cloud
models above, not tuned for small ones.

The **Vision model** box names the model shown camera images; by default it is
the same one. A separate choice helps when the language model cannot see.

Things to try: *Where is the stage?* · *What do you see?* · *Is it in focus?* ·
*Switch to FITC at 50 ms* · *Take a Z-stack of 10 um in 1 um steps in DAPI and FITC here* ·
*Image a 3 by 3 grid of tiles around here* · *Run the useq sequence in D:\sequences\cells.json* ·
*Show me the useq sequence for that plan* · *How does the engine move the stage? Show me the code* ·
*What is new in useq v2?* · *Move the sample a little to the left* · *Look again: has anything
changed since the first image?* · *Look every three minutes and tell me whether it drifts*

## What it can do

As tools: check the setup (whether NIS-Elements and its bridge answer, and
whether an optical configuration exists; when not, it hands you the steps:
the full path of `start_bridge.mac` and how to run it, or how to add an
optical configuration in NIS), read the microscope, move the stage, change the
optical configuration, exposure, objective and PFS, focus (PFS or the NIS
image sweep), look at an image and describe it, ask about the images already
seen, and set a schedule. Acquisitions go through useq:

- `plan_acquisition` turns a plan into a `useq.MDASequence` and has the engine
  check every event without moving. A plan has positions, channels (each with
  its exposure, and optionally a single plane instead of the Z-stack, only
  every nth time point, or a focus offset), a Z-stack, a grid of tiles around
  each position, time points, and PFS focus locking. For tiles, the camera
  field is measured with one image, so the objective needs a pixel
  calibration in NIS.
- `plan_useq_sequence` loads a classic useq sequence made elsewhere
  (pymmcore-widgets, napari-micromanager, a script) from a `.json` or `.yaml`
  file, or as JSON, and checks it the same way. (useq-schema cannot yet read a
  v2 sequence back from a file.)
- `run_acquisition` runs a checked sequence with the pymmcore-plus runner and
  saves it as OME-TIFF (a folder with one file per position when there are
  several), with the sequence itself next to it as `.useq.json`, which other
  useq tools can load again. When the run ends, the last image (the one left
  on the right of the window) is described in a sentence or two.
- `search_source` and `read_source` search and read the source of the three
  parts and of useq-schema (read only, nothing else on the computer).

Plans run as a classic `useq.MDASequence`, because the pymmcore-plus file
writers (0.18) keep the channel and Z axes only for that form.

**The eyes remember.** The vision model has a conversation of its own for the
session: every look is a turn in it, with the image, its time, the stage
position and objective, and the measured numbers, so *is this sharper than
before?* and *has the sample moved since the first image?* are answered by
looking, and `ask_eyes` puts a question to the images already seen without
taking a new one. The last eight images stay attached; older turns keep their
words, and beyond forty looks the oldest are dropped. The last image of an
acquisition is shown to the eyes too. Clear context makes the eyes forget with
the rest, and so does choosing another vision model, since one model cannot
read another's images and answers.

**The coordinate system.** Microscopes differ in what a positive stage move
does to the picture on the screen. The *Coordinate system* box in the Model
panel says what +x, +y and +z do to the sample in the image (right or left,
up or down, deeper into the sample or toward the coverslip). The assistant is
told, so *move it a bit to the left* or *go 10 um deeper* becomes a signed
move on the right axis, and it says which axis and sign it used.

**Schedules.** *Look every three minutes and tell me whether anything
changed*, *in ten minutes switch the PFS off*, *at 15:00 start the plan*:
the assistant sets a named schedule, and the window's clock sends each due
instruction as a turn of its own, marked `[scheduled 'name']` in the chat,
through the same tools and checks as anything you type, and never while a
turn is running. A scheduled turn is not yours: a scheduled acquisition or
long stage move still asks for your go-ahead in the chat and waits until you
answer, and moves are still measured from where the stage was when you last
wrote. The state the assistant reads with every message carries the clock
and the schedules. At most ten schedules, none more often than every five
seconds. A scheduled turn that fails cancels its schedule, so a dead model
does not repeat the same error every period. *Stop microscope* and *Clear
context* cancel them all.

## How it stays safe

- **Stage limits you can see and narrow.** Below the chat, six fields (X-, X+,
  Y-, Y+, Z-, Z+) show the limits in force in um. Type a tighter value (for
  example 3000 in Z+) and press *Apply limits*; an empty field keeps NIS's own
  limit on that side, and *Use NIS limits* goes back to NIS's limits
  everywhere. The assistant is told the limits in force with every message.
- **Checks before acting.** Moves are checked against the stage limits, and
  settings against the NIS configuration lists. The image-based focus sweep is
  limited to 100 um and must stay inside the Z limits.
- **Refusals come with advice.** A refused or failed action comes back to the
  assistant with what was refused, why, and what to do next. After a limit
  breach it is told to stop and leave the next number to you, rather than try
  a nearby value. When a name is not known (an optical configuration, an empty
  nosepiece slot), the refusal lists the microscope's own names.
- **A red banner for refusals.** A limit breach or an invalid value is also
  shown in the window directly, whatever the assistant says.
- **Big steps are agreed in the chat first.** Starting an acquisition always
  waits for you: the assistant shows the plan and asks, and the run can start
  only after your reply. A stage move of more than 1 mm in XY or 100 um in Z
  works the same way ("Shall I move 19 mm to x = 20 mm?"). Moves are measured
  from where the stage was when you last wrote, so small steps that add up
  also ask. That the question comes first is in the code, not only in the
  model's instructions. Everything else runs at once.
- **One action at a time,** so each result is seen before the next action.
- **Looking stays out of the chat.** The image goes to the model in a separate
  request with a few measured numbers (brightness, saturation, sharpness),
  binned 2 x 2 so a 2048-pixel camera image arrives at 1024 pixels. A model
  that cannot see gets the numbers only.
- **Two checks on the reply.** An empty reply goes back to the model once. A
  reply that claims to have done something in a turn that called no tool also
  goes back once, with that fact; the model then acts, or its first reply is
  shown as it was.
- **Cancel prompt** stops the assistant: every further tool call in that turn
  does nothing. **Stop microscope** also ends a running acquisition after the
  image being taken. A single stage move that NIS has already started runs to
  its end; the joystick or NIS-Elements stops it sooner. The window does not
  close while the assistant is still working.
- **Clear context** forgets the conversation; **Show tool calls** lists each
  tool call in the chat as it happens.

To keep long conversations quick, the assistant forgets older messages: after
15 of your messages it keeps the newest 10.

Changing the objective does not ask first, so check that the objectives can
turn freely. If the connection to NIS was lost (for example because the macro
was stopped), restart `start_bridge.mac`; the window reconnects with your next
message.

Not supported: camera ROI and binning, several cameras, colour cameras, and
pausing a run.

## Tests

```
pip install -e ".[test]"
pytest                    # offline, about 10 s: a scripted model over a fake NIS
pytest -m hardware -s     # on NIS-Elements with the bridge running (step 3 in the overview)
ruff check . && ruff format --check .   # lint and formatting, rules in pyproject.toml
```

## For maintainers: the evaluation

The tests check the code. Whether the assistant does what an operator expects
(acts when a request is clear, asks when it is not, stops at a limit, ignores
instructions hidden in the data) depends on the model, and is checked by the
evaluation. It runs every case in `tests/eval_cases.json` through the real
assistant, with a real model and the fake NIS, and scores the result. Each
run costs API calls.

```
python tests/evals.py --model openai:gpt-5-mini                # needs OPENAI_API_KEY
python tests/evals.py --model google:gemini-3.5-flash-lite     # needs GOOGLE_API_KEY and the [google] extra
python tests/evals.py --holdout --repeat 3                     # other wording; shows cases that pass only sometimes
python tests/evals.py --scoreboard evals-*.jsonl               # pass rates per model and per category
```

Change the instructions while looking at `eval_cases.json` only, then check
with `--holdout`: that shows whether a change made the assistant better, or
only fitted it to the cases.

## Files

| File | What it is |
|---|---|
| `nis_assistant/tools.py` | The tools: everything the model can ask for, one function each, with the go-ahead rule, the refusals and the two guards on a reply. The place to look up or add a tool. |
| `nis_assistant/instructions.py` | The prose the model reads: its instructions, the advice given with a refusal, and the setup steps it passes on. |
| `nis_assistant/plans.py` | The plan format, plan to useq sequence, and the plan summary. |
| `nis_assistant/images.py` | One snap, its statistics, and the binned PNG for the model. |
| `nis_assistant/eyes.py` | The vision model's own conversation: the images seen this session, compared on request. |
| `nis_assistant/schedules.py` | The schedules the assistant sets, and when each is due. |
| `nis_assistant/memory.py` | The conversation made smaller now and then. |
| `nis_assistant/models.py` | The ways to reach a model: a provider preset, an API key held in memory, the model object. |
| `nis_assistant/local.py` | A `.gguf` model file served on this computer by llama.cpp. |
| `nis_assistant/agent.py` | The assembly: the Agent with the tools and guards, and `Assistant`, one conversation. |
| `nis_assistant/settings.py` | Every constant: the provider presets, the coordinate choices, go-ahead distances, memory sizes, window defaults. |
| `nis_assistant/window.py` | The chat window (`nis-assistant`), with the Model panel from `panel.py`. |
| `tests/evals.py` | The evaluation with a real model; `eval_cases.json` and `eval_cases_holdout.json`. |

MIT license. Thom de Hoog, Center for Microscopy and Image Analysis (ZMB),
University of Zurich. thom.dehoog@zmb.uzh.ch, thomdehoog@gmail.com. 2026-09-27.
