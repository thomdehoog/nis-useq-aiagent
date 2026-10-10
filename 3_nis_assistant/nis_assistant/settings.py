"""Every constant of the assistant, in one place.

The model's instructions and the advice it is given with a refusal are prose
and stay in ``instructions.py``; the numbers and names that one might want to
change are all here. Times are seconds, distances micrometres.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
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
    "Anthropic": {
        "kind": "anthropic",
        "model": "claude-haiku-5-5",
        "key_env": "ANTHROPIC_API_KEY",
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
PREFIXES = {
    "google": "Gemini",
    "google-gla": "Gemini",
    "anthropic": "Anthropic",
    "openai": "OpenAI",
}
# Sampling and retries for every model, cloud or local. An assistant that drives an
# instrument wants the most likely tool call, not a creative one, so the temperature
# is 0.
TEMPERATURE = 0.0
TOOL_CALL_RETRIES = 3  # a malformed tool call goes back to the model up to three times
MODEL_SETTINGS: dict[str, dict[str, Any]] = {
    # max_tokens: room for a full acquisition plan. parallel_tool_calls False: one
    # action at a time, so each is seen before the next.
    "google": {"temperature": TEMPERATURE, "max_tokens": 16000, "parallel_tool_calls": False},
    # Anthropic: no temperature (claude-haiku-5-5 refuses one), and prompt caching. The tool
    # definitions and the instructions are cached for an hour, as they never change and an
    # operator may pause longer than five minutes; the growing history for five minutes, as its
    # new part is written on every request. Three of Anthropic's four breakpoints, the hour
    # first, as the API requires. A request then pays the full price for its new part only.
    "anthropic": {
        "max_tokens": 16000,
        "parallel_tool_calls": False,
        "anthropic_cache_tool_definitions": "1h",
        "anthropic_cache_instructions": "1h",
        "anthropic_cache": "5m",
    },
    "openai": {"temperature": TEMPERATURE, "parallel_tool_calls": False},
    "openai-compatible": {"temperature": TEMPERATURE},  # small servers reject the parallel flag
}
DEFAULT_MODEL_SETTINGS = MODEL_SETTINGS["google"]  # the settings that go with MODEL

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
# The eyes' conversation is also cut to this many looks, oldest first, so a look every
# few minutes for a whole day does not send the whole day with every question.
VISION_TURNS_KEPT = 40

# -- schedules ---------------------------------------------------------------------------
CLOCK_FORMAT = "%H:%M:%S"  # how the state and the eyes write a time of day

# The conversation is kept whole until Clear, so each request carries the session. The
# window shows the last request's input tokens, warns above the first number and sends no
# message above the second. Gemini 3.5 and Haiku 5.5 take a million tokens; Haiku's price
# per token rises on a request above 100,000, which is where its warning sits. An
# OpenAI-style server has no known window.
CONTEXT_TOKENS = {  # provider preset: (warn above, refuse above)
    "Gemini": (500_000, 900_000),
    "Anthropic": (100_000, 900_000),
    "OpenAI": (200_000, 360_000),
}
CONTEXT_LARGE = "The session is large: each request costs more. Clear it when the work allows."
CONTEXT_FULL = "The session is as large as this model takes: Clear it to continue."
# A server whose context window is smaller than one request answers with one of these.
CONTEXT_TOO_SMALL_SIGNS = ("exceed_context_size", "exceeds the available context size")
CONTEXT_TOO_SMALL_HELP = (
    "The model server's context window is smaller than one request (about 6,000 tokens). "
    "Give it 16,384 or more: for Ollama, set OLLAMA_CONTEXT_LENGTH=16384 on the server, "
    "or make a copy of the model with PARAMETER num_ctx 16384."
)

# -- the window --------------------------------------------------------------------------
OUTPUT_FOLDER = "nis_assistant_runs"  # in the home folder, when --output is not given
FONT_POINTS = 11  # the window's letters: Qt's default of 9 is small at a microscope
