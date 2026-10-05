# nis-useq-aiagent

This repository consists of three things to control the NIS-Elements
microscope software through Python:

1. **nis-bridge:** control NIS-Elements from your own Python. → [README](1_nis_bridge/README.md) · [tutorial](1_nis_bridge/docs/tutorial.md)
2. **nis-engine:** run [useq](https://github.com/pymmcore-plus/useq-schema) acquisitions on a Nikon microscope. → [README](2_nis_engine/README.md) · [tutorial](2_nis_engine/docs/tutorial.md)
3. **nis-assistant:** talk to your microscope through an AI agent. → [README](3_nis_assistant/README.md) · [tutorial](3_nis_assistant/docs/tutorial.md)

Each part is its own Python package and builds on the one before it, so you
can use only the part you need:

```
nis-assistant ──> nis-engine ──> nis-bridge ──> NIS-Elements ──> microscope
```

Each part's README is its complete documentation, from the idea to the
reference; each tutorial is a longer step-by-step walk-through to a first
result. [docs/useq.md](docs/useq.md) documents useq-schema itself, the
classic API and useq v2, as parts 2 and 3 use it.

## Install

On the microscope computer, with NIS-Elements installed. Python comes from
conda, in an environment of its own, separate from the Python inside
NIS-Elements: install [Miniforge](https://github.com/conda-forge/miniforge)
(conda with the conda-forge channel), open a *Miniforge Prompt*, and make
the environment:

```
conda create -n nis -c conda-forge python=3.12
conda activate nis
```

Then, in that environment, clone the repository and install the three parts
into it:

```
git clone https://github.com/thomdehoog/nis-useq-aiagent
cd nis-useq-aiagent
pip install -e "./1_nis_bridge[test]"
pip install -e "./2_nis_engine[test]"
pip install -e "./3_nis_assistant[test]"
```

`conda activate nis` is needed in every new prompt before any command
below.

Then one command starts NIS-Elements with the bridge and opens the chat window:

```
nis-assistant --start-nis
```

To use only the bridge or the engine, see their READMEs.

## Try it without a microscope

Part 1 includes a fake NIS-Elements. Start it and leave it running:

```
python -m nis_bridge.fake
```

Everything in the three READMEs then works against it, including the chat
window. Stop it with Ctrl+C.

## Testing

Each part has tests that run against the fake (`pytest 1_nis_bridge`, and so
on) and hardware tests for NIS-Elements. See [docs/testing.md](docs/testing.md)
for the hardware checklist and the current status.

## Status

| | |
|---|---|
| **Tested** | On the Ti2 simulator of NIS-Elements AR 6.10.02: all hardware tests of the three parts, and the assistant with Gemini. |
| **Not yet** | Run on a real microscope with a sample. |
| **Next** | Testing on a Ti2 with a sample, following [docs/testing.md](docs/testing.md). |

## A quick look at the assistant

![The assistant window: a chat on the left, the latest image on the right](docs/assistant-window.png)

*The assistant on a Ti2 (NIS-Elements 6.10, Gemini as the model): it asks
which channel, shows the plan, runs it as a useq sequence, and describes the
image it took.*

## Licence and acknowledgement

MIT licence. Written by Thom de Hoog, Center for Microscopy and Image
Analysis (ZMB), University of Zurich: thom.dehoog@zmb.uzh.ch,
thomdehoog@gmail.com.

If you use any part of this repository, or build on its ideas, in your own
software, experiments or publications, please acknowledge the author by name
and e-mail address. Every file carries the same request in its header.
