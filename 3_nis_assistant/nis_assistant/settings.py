"""Every constant of the assistant, in one place.

The model's instructions and the advice it is given with a refusal are prose
and stay in ``instructions.py``; the numbers and names that one might want to
change are all here. Times are seconds, distances micrometres.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
"""

from typing import Any

# -- the model -------------------------------------------------------------------------
# The providers the window offers. vision: the model can be shown a camera image, so
# the "look" tool gets a real answer about the picture; without it the tool answers
# from the measured numbers only.
PROVIDERS: dict[str, dict[str, Any]] = {
    "Gemini": {
        "kind": "google",
        "model": "gemini-3.5-flash-lite",  # generous free tier, native tool calling
        "key_env": "GEMINI_API_KEY",
        "key_env_also": "GOOGLE_API_KEY",  # the older name, still honoured
        "vision": True,
    },
    "OpenAI": {
        "kind": "openai",
        "model": "gpt-5-mini",
        "key_env": "OPENAI_API_KEY",
        "vision": True,
    },
    "OpenAI-style server": {
        "kind": "openai-compatible",
        "model": "gemma4:31b",  # needs about 20 GB of GPU memory; smaller ones garble arguments
        "base_url": "http://localhost:11434/v1",  # an Ollama or vLLM already running somewhere
        "vision": False,  # set by the operator in the window when their server can see
    },
}
DEFAULT_PROVIDER = "Gemini"
MODEL = "google:gemini-3.5-flash-lite"  # the model when no endpoint is chosen (tests, evals)
# The short names Pydantic AI uses in a "provider:model" string, by provider preset.
PREFIXES = {"google": "Gemini", "google-gla": "Gemini", "openai": "OpenAI"}
# Sampling and retries for every model, cloud or local. An assistant that drives an
# instrument wants the most likely tool call, not a creative one, so the temperature
# is 0.
TEMPERATURE = 0.0
TOOL_CALL_RETRIES = 3  # a malformed tool call goes back to the model up to three times
MODEL_SETTINGS: dict[str, dict[str, Any]] = {
    # max_tokens: room for a full acquisition plan. parallel_tool_calls False: one
    # action at a time, so each is seen before the next.
    "google": {"temperature": TEMPERATURE, "max_tokens": 16000, "parallel_tool_calls": False},
    "openai": {"temperature": TEMPERATURE, "parallel_tool_calls": False},
    "openai-compatible": {"temperature": TEMPERATURE},  # small servers reject the parallel flag
}
DEFAULT_MODEL_SETTINGS = MODEL_SETTINGS["google"]  # the settings that go with MODEL

# -- a model file served on this computer (local.py) ------------------------------------
MODELS_FOLDER = "nis_assistant_models"  # in the home folder, unless another is chosen
MODEL_SUFFIXES = (".gguf",)
# The context window the server is started with. llama-cpp-python's own default
# is 2,048 tokens, less than one request here (the instructions, the tools and
# the state reading are about 6,000 tokens). 32K holds a request, a good number
# of turns, tool results and a margin.
CONTEXT_TOKENS = 32768
BATCH_TOKENS = 2048  # prompt batches: the long prefix is processed in fewer passes than at 512
FLASH_ATTENTION = True  # smaller memory and faster attention where the build supports it
SERVER_POLL_MS = 500  # how often the window asks whether the server is up
SERVER_START_TIMEOUT_S = 300  # a large file can take minutes to load from a slow disk

# -- the tools -------------------------------------------------------------------------
# A stage move that travels further than this from where the stage was when the
# operator last wrote (on any one axis, in um) needs their go-ahead in the chat.
CONFIRM_XY_UM = 1000.0
CONFIRM_Z_UM = 100.0
MAX_SWEEP_UM = 100.0  # the longest image-based focus sweep
MAX_EXPOSURE_MS = 60000.0
# For the rough duration in a plan's summary: the time per image besides the
# exposure (moves, saving), and the exposure assumed when a channel sets none.
SECONDS_PER_IMAGE = 1.5
GUESSED_EXPOSURE_MS = 100.0
# The camera image the vision model is shown is binned n x n first (each output pixel
# is the mean of an n x n block): 2 keeps a 2048-pixel camera image at 1024 pixels,
# enough for "is it centred" or "is it saturated", and averaging keeps dim detail
# that picking every other pixel would lose.
LOOK_BIN = 2
LOOK_MAX_SIDE = 1024  # a still larger image is binned further until it fits

# The source-reading tools.
SOURCE_MATCHES = 40  # search results returned at most
SOURCE_LINES = 200  # lines read at most in one go

# -- the coordinate system ---------------------------------------------------------------
# What a positive move on each axis does to the sample in the image, as the operator
# sees it on their screen, so that "left", "up" and "deeper" mean one thing. The first
# choice of each pair is the default; the window's Coordinate system box changes it.
AXIS_CHOICES = {
    "x": ("right", "left"),
    "y": ("up", "down"),
    "z": ("deeper into the sample", "toward the coverslip"),
}
DEFAULT_AXES = {axis: choices[0] for axis, choices in AXIS_CHOICES.items()}

# -- the eyes ----------------------------------------------------------------------------
# The vision model keeps a conversation of its own for the session, with every image a
# look took, so it can compare the current image with earlier ones. The newest images
# stay attached; older turns keep their text (time, settings, numbers, and what the eyes
# said) and lose the picture, which keeps the cost of a look about one image.
VISION_FRAMES_KEPT = 8

# -- schedules ---------------------------------------------------------------------------
# "Look every three minutes", "in ten minutes start the plan": the assistant sets a
# schedule and the window's clock fires each due instruction as a turn of its own.
SCHEDULE_MIN_SECONDS = 5  # no schedule fires more often than this
SCHEDULES_MAX = 10
SCHEDULED_TURN = "[scheduled '{name}'] {instruction}"  # how a fired instruction is worded

# The conversation is made smaller now and then, between turns (see memory.compact()).
HISTORY_COMPACT_AFTER = 15  # operator turns before the history is made smaller
HISTORY_KEEP_TURNS = 10  # turns kept when it is; older ones are forgotten
HISTORY_FULL_TURNS = 3  # the newest turns keep their state readout and tool results in full
HISTORY_RESULT_CHARS = 300  # an older tool result is cut to this many characters

# -- the window --------------------------------------------------------------------------
OUTPUT_FOLDER = "nis_assistant_runs"  # in the home folder, when --output is not given
FONT_POINTS = 11  # the window's letters: Qt's default of 9 is small at a microscope
