# nis-assistant, step by step

This is a walk-through for a biologist who wants to use the chat assistant at
a Nikon microscope, and would like to understand what it does with a request
before trusting it with the stage. It explains how the assistant works, gets
you through a first conversation, and then goes through each of its abilities
with what to expect. The [README](../README.md) is the complete
documentation.

You need parts 1 and 2 installed and the bridge running in NIS-Elements (or
the fake NIS, `python -m nis_bridge.fake`, in another window). Their
tutorials ([bridge](../../1_nis_bridge/docs/tutorial.md),
[engine](../../2_nis_engine/docs/tutorial.md)) are worth reading, but not
required: the assistant uses them for you.

## The idea

You type a request in your own words: *take a Z-stack of 10 um in DAPI and
FITC here*. A language model (Gemini, OpenAI, or one running on this
computer) reads it, and decides what to do. But the model does not touch the
microscope. It can only ask for a small set of **tools**, written in this
package, such as "read the status", "move the stage to x, y, z", "plan this
acquisition", "run plan 3". Every tool checks what it is asked before doing
anything, and refuses what is outside the limits or outside what the
microscope has. The model gets the tool's answer, and tells you what happened.

```
you ──► chat window ──► language model ──► tools ──► NisEngine ──► bridge ──► microscope
                              ▲               │        (part 2)     (part 1)
                              └── answers ────┘
```

So there are two layers of safety. The model is *told* to be careful, in
instructions it reads with every message; but the rules that matter (a move
outside the limits is refused, an acquisition or a long move starts only after
you have agreed in the chat) are in the tools' code, and hold whatever the
model says.

The assistant is also a demonstration of the other two parts: its
acquisitions are useq sequences run on the engine, and it can show you those
sequences and explain, from the source code, how any part works.

## Step 1: install and start

In the same environment as parts 1 and 2, in the repository folder:

```
pip install -e "./3_nis_assistant[test]"
```

Then:

```
nis-assistant --start-nis --output D:\runs
```

`--start-nis` starts NIS-Elements with the bridge macro when NIS is not open
yet; leave it out if the bridge is already running. `--output` is where
acquisitions are saved (by default `nis_assistant_runs` in your home
folder). A window opens: the conversation on the left with its buttons and
the stage limits below it, and on the right the latest image and the
microscope status.

## Step 2: choose a model

The assistant needs a language model, and the first time you must tell it
which. The **Model** line at the top of the window folds open.

The simplest start is Gemini: get a free API key at
[aistudio.google.com](https://aistudio.google.com), paste it into the panel,
and press *Use this model*. The key stays in memory for this session and is
never written to disk. OpenAI works the same way with a key from
[platform.openai.com](https://platform.openai.com). Each message costs a
fraction of a cent; the provider's pricing page says how much.

If your institute does not allow cloud models, or you want no internet at
all, the README describes two other choices: a server you run yourself
(Ollama and the like), and a model file on this computer. Small models make
more mistakes with the tools, so start with a cloud model to learn what good
behaviour looks like.

## Step 3: a first conversation

Type each of these and read the answer before the next. Check what the
assistant says against NIS-Elements itself; the whole point of this first
session is to learn when to trust it.

**"Where is the stage, and which objective is in use?"**

The assistant reads the microscope and answers with the position in
micrometres and the objective. Nothing moves. The status panel on the right
shows the same numbers.

**"Move x by 20 um."**

The stage moves at once, and the answer says the new position. Small moves do
not ask first.

**"Move x by 5 mm."**

This time the assistant does *not* move. It tells you where the stage would
go and how far, and asks whether to go ahead. Answer *no*. Any move of more
than 1 mm in XY or 100 um in Z works like this: the tool refuses to carry it
out in the turn it was first asked, and runs it only if your next message
agrees. The distance is measured from where the stage was when you last
wrote, so ten small moves that add up to a long one also ask.

**"Move z to 20000 um."** (or any value outside the limits shown below the chat)

Refused: a red banner appears in the window, and the assistant tells you the
limit. It is told not to try a nearby value instead; the next number is
yours to give.

**"Switch to DAPI at 50 ms."** (use a configuration your NIS has)

The optical configuration changes and the exposure is set. If you misspell
the name, the refusal lists the names NIS has, and the assistant either
corrects an obvious spelling (*fitc* for *FITC*) or asks you which one you
meant. It is not allowed to pick a different configuration on its own.

**"What do you see?"**

The assistant takes one image, which appears on the right, and describes it
in a few sentences. Where the description comes from is explained below
(*The eyes*).

**"Take a Z-stack of 4 um in 2 um steps here in DAPI."**

The assistant plans the acquisition, which means: it builds a useq sequence
and has the engine check every image of it against the stage limits and the
configurations, without moving. Then it tells you the plan in a sentence
(three images, which channel, the Z range, roughly how long, how far the
stage will travel) and asks whether to start. Answer *yes*. The run starts,
each image appears on the right as it is taken, and at the end the files are
in the output folder: an OME-TIFF and, next to it, the sequence as
`.useq.json`. The assistant then describes the last image.

An acquisition always asks first, however small, and can only start in the
turn right after the plan was shown. If you talk about something else in
between, it shows the plan again and asks again.

**"Show me the useq sequence for that plan."**

The assistant prints the sequence, and explains the fields. This is the same
object part 2's tutorial builds by hand.

That is the shape of every interaction: the assistant acts at once when the
request is clear and small; asks one question when something is missing
(which axis, how far, which channel); shows the plan and waits when the step
is big; and refuses, with the reason, when the step is outside the limits.

## What each ability does

**Reading and changing settings.** Position, objective, optical
configuration, exposure, PFS state, focus. Changing the objective does not
ask first, so make sure the turret can turn freely with your sample in
place.

**Focusing.** *Focus* or *is it in focus?* uses the PFS when there is one,
or the NIS image-based focus sweep (*focus with an image sweep over 40
um*). The sweep is limited to 100 um and must stay inside the Z limits.

**Looking.** *What do you see?*, *Is it in focus?*, *Are the cells
confluent?* Each takes one image.

**Acquisitions.** A plan has positions (empty means here), channels with
their exposures, a Z-stack, a grid of tiles, time points with an interval,
and focus locking with the PFS. Say what you want in words:

- *Take DAPI and FITC here, 10 um stack in 1 um steps, brightfield as a
  single plane.*
- *Every 5 minutes for an hour, image these two positions in FITC, locking
  the PFS each time.* (Give positions as numbers, or move the stage there
  with the joystick and say *here*; the assistant reads the position from NIS.)
- *Image a 3 by 3 grid of tiles around here with 10% overlap.* The camera
  field is measured with one image, so the objective needs a pixel
  calibration in NIS.
- *Run the useq sequence in D:\sequences\cells.json.* A sequence made in
  another useq tool (pymmcore-widgets, napari-micromanager) is loaded and
  checked the same way.

**Explaining.** *How does the engine move the stage? Show me the code.*
*What is new in useq v2?* The assistant searches and reads the source of the
three parts and of useq-schema, and quotes the file and line. It is told to
look things up rather than answer from memory.

**Schedules.** *Look every three minutes and tell me whether the sample
drifts.* *In ten minutes switch the PFS off.* *At 15:00 start the plan.* The
assistant sets a named schedule, and the window sends the instruction as a
message of its own when due, marked `[scheduled 'name']` in the chat. A
scheduled turn goes through the same tools and checks as anything you type;
an acquisition or long move in it still asks in the chat and waits for you.
*Stop microscope* cancels every schedule. At most ten schedules, none more
often than every five seconds.

## The eyes

When the assistant looks, the image does not go into the chat. It goes, in a
separate request, to a *vision* model (by default the same model) together
with a few measured numbers: brightness, saturation, sharpness. The vision
model has a conversation of its own for the session, in which every image it
has seen is a turn, with its time, the stage position and the objective. So
it can compare:

- *Look again: has anything changed since the first image?*
- *Is this sharper than before?*
- *Which of the images so far was best exposed?* (`ask_eyes`: a question to
  the images already seen, without taking a new one)

The comparison is qualitative: reliable for *the cells have moved left*,
*it is less sharp than a minute ago*, *the right half is saturated*; it is
not a measurement. Whether an
image is well exposed comes from the numbers, not from the picture, because
each picture is contrast-stretched before the model sees it. The last eight
images stay attached; older turns keep their words only. *Clear context*
makes the eyes forget with everything else.

## The coordinate system

Microscopes differ in what a positive stage move does to the picture on the
screen: +x may move the sample left or right, +z deeper or towards the
coverslip. The assistant cannot know this, so you tell it once. The
*Coordinate system* box in the Model panel has a choice for each axis. Then
*move the sample a little to the left* or *go 10 um deeper* becomes a signed
move on the right axis, and the assistant says which axis and sign it used.

Check it on your first session: say *move the sample 100 um to the left*,
and watch the live image in NIS. If it went right, change the x choice in the
box.

## The stage limits

Below the chat, six fields show the limits in force in micrometres: NIS's
own, or tighter ones you type. Before working on a precious sample, narrow Z+
to a little above your focus (for example 3000 if focus is at 2950) and
press *Apply limits*. From then on no move, no Z-stack and no focus sweep can
go past it, whatever the assistant is asked. *Use NIS limits* goes back to
NIS's own. The assistant is told the limits in force with every message, so
it can plan within them.

## The buttons

- **Cancel prompt** stops the assistant in the middle of a turn: every
  further tool call in that turn does nothing.
- **Stop microscope** also ends a running acquisition after the image being
  taken, and cancels every schedule. A single stage move that NIS has
  already started runs to its end; the joystick or NIS stops it sooner.
- **Clear context** forgets the conversation (and the eyes' images).
- **Show tool calls** lists each tool call in the chat as it happens: which
  tool, with which arguments, and what came back. Switch it on for your
  first sessions; it shows exactly what the assistant did, as opposed to
  what it says.

## How a request becomes an action

For when you want to know what is going on under the hood, one turn in
detail:

1. You type a message. The window appends the current *microscope state* to
   it: position, objective, configuration, PFS, the limits in force, the
   clock, the schedules. The model always reasons from a fresh reading, not
   from memory.
2. The model reads its instructions (the same every time), the conversation
   so far, and your message, and decides: answer in words, ask you a
   question, or call a tool. Tool calls happen one at a time, so each result
   is seen before the next.
3. The tool checks the request. It either does the thing and returns the
   result (the position after a move, the plan summary), or returns an
   *error* with what was refused, why, and a line of advice for the model
   ("tell the operator the limit and stop"), or returns *needs go-ahead*
   with a summary of what it would do.
4. The model reads the answer and either calls another tool, or writes its
   reply to you.
5. Two guards look at the reply before you see it. An empty reply goes back
   to the model once. A reply that claims to have done something in a turn
   that called no tool also goes back once, with that fact: the model then
   acts, or its original reply is shown.

After 15 of your messages, the assistant forgets the oldest ones and keeps
the newest 10, so long sessions stay quick.

## Good habits

- Keep NIS-Elements visible next to the window, and check it after each
  action. The status panel shows what the assistant read; NIS shows what is
  true.
- Narrow the Z limit before you start. It costs nothing and removes the one
  mistake that damages things.
- Say numbers with units (*20 um*, *50 ms*). When the assistant asks which
  axis or how far, it is because you did not say; answer rather than letting
  it guess, which it is told not to do.
- Read the plan before saying *yes*. The sentence names the number of images,
  the channels, the Z range, the time points and how far the stage travels.
- Switch *Show tool calls* on when something looks odd.

## What it will not do

No camera ROI or binning, several cameras, colour cameras (set the camera to
monochrome in NIS), or pausing a run. It never runs macro text or touches
files outside the output folder (it reads source code, nothing else). It
cannot see without taking an image: the state it reads has no picture in it.

## When something is wrong

- **"The microscope does not answer."** The bridge is not running. The
  assistant gives the steps: the path of `start_bridge.mac` and how to run
  it in NIS. After restarting it, just send another message; the window
  reconnects.
- **"NIS lists no optical configuration."** Make one in NIS (*Calibration >
  New Optical Configuration*); the assistant walks you through it.
- **A red banner.** Something was refused: a limit, an unknown name, an
  invalid value. The assistant's reply says which; the banner is there so
  you see it even if the reply is unclear.
- **The model's reply is empty or odd.** Press *Cancel prompt*, then try
  again or switch model. Small local models in particular sometimes answer a
  refusal with nothing; the guards above catch most of this.
- **An API error.** The key is wrong, the quota is spent, or the internet is
  down. The message comes through in red; fix the key in the panel.

## Where to go next

- The [README](../README.md): every tool, the model choices in detail, and
  how the assistant's behaviour is evaluated.
- *Show me the useq sequence for that plan* and then part 2's
  [tutorial](../../2_nis_engine/docs/tutorial.md): the same experiment, as
  code you can keep and rerun.
