"""Which model the assistant talks to, and how it is reached.

The chat window offers a few providers. Choosing one fills in a sensible model
name (and, for a server you run yourself, its address); the operator types the
API key into the window. The key stays in memory for the session only: it is
never written to a file, a log, or the conversation. An empty key field falls
back to the environment variable named in the preset, so `set GEMINI_API_KEY=...`
before starting still works.

Three kinds of connection exist:

- ``google``: Gemini, through Google's API.
- ``openai``: OpenAI's own API.
- ``openai-compatible``: any server that speaks the OpenAI chat API. That is
  Ollama, vLLM, LM Studio, a company gateway, or a model file this window serves
  itself (see ``local.py``). Such a server needs a base URL, and a key only if
  it asks for one.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

# vision: the model can be shown a camera image, so the "look" tool gets a real answer
# about the picture. Without it the tool answers from the measured numbers only.
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
# The short names pydantic-ai uses in a "provider:model" string, by provider preset.
PREFIXES = {
    "google": "Gemini",
    "google-gla": "Gemini",
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
    "openai": {"temperature": TEMPERATURE, "parallel_tool_calls": False},
    "openai-compatible": {"temperature": TEMPERATURE},  # small servers reject the parallel flag
}


@dataclass
class Endpoint:
    """One model as chosen in the window. The key is held in memory only."""

    provider: str
    kind: str
    model: str
    api_key: str = field(default="", repr=False)
    base_url: str = ""
    vision: bool = False  # may be shown a camera image (the "look" tool's side call)

    @classmethod
    def from_preset(
        cls,
        provider: str,
        model: str = "",
        api_key: str = "",
        base_url: str = "",
        vision: bool | None = None,
    ) -> Endpoint:
        """Fill the blanks from the provider preset.

        An empty model or base URL takes the preset's; an empty key takes the
        preset's environment variable, which may itself be unset.
        """
        preset = PROVIDERS[provider]
        key = api_key.strip()
        for variable in (preset.get("key_env"), preset.get("key_env_also")):
            if not key and variable:
                key = os.environ.get(variable, "")
        return cls(
            provider=provider,
            kind=preset["kind"],
            model=model.strip() or preset["model"],
            api_key=key,
            base_url=base_url.strip() or preset.get("base_url", ""),
            vision=bool(preset.get("vision", False)) if vision is None else vision,
        )

    @classmethod
    def from_name(cls, name: str) -> Endpoint:
        """An endpoint from a pydantic-ai style name such as ``google:gemini-3.5-flash-lite``.

        This is what the ``--model`` command line option takes. A name without a
        known provider prefix is sent to an OpenAI-style server.
        """
        prefix, _, model = name.partition(":")
        provider = PREFIXES.get(prefix.lower())
        if provider is None:
            return cls.from_preset("OpenAI-style server", model=name)
        return cls.from_preset(provider, model=model)

    @property
    def needs_key(self) -> bool:
        return self.kind != "openai-compatible"

    @property
    def key_variable(self) -> str | None:
        """The environment variable that could hold this endpoint's key, if any."""
        return PROVIDERS[self.provider].get("key_env")

    @property
    def name(self) -> str:
        """A short label for the window's status line and error messages."""
        return f"{self.provider}: {self.model}"

    @property
    def settings(self) -> dict[str, Any]:
        return MODEL_SETTINGS[self.kind]


def build_model(endpoint: Endpoint) -> Any:
    """The pydantic-ai model object for an endpoint.

    The provider libraries are imported here, not at the top, so the window starts
    even when only one of them is installed.
    """
    if endpoint.kind == "google":
        from pydantic_ai.models.google import GoogleModel
        from pydantic_ai.providers.google import GoogleProvider

        return GoogleModel(endpoint.model, provider=GoogleProvider(api_key=endpoint.api_key))
    # OpenAI itself, and any OpenAI-compatible server; a local server needs no key.
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    provider = OpenAIProvider(
        base_url=endpoint.base_url or None, api_key=endpoint.api_key or "not-needed"
    )
    return OpenAIChatModel(endpoint.model, provider=provider)


def missing_key_advice(endpoint: Endpoint) -> str:
    """One sentence on how to give the key, for a message to the operator."""
    if not endpoint.needs_key:
        return "This server refused the request; if it wants a key, type it in the Model panel."
    variable = endpoint.key_variable
    return (
        f"Type the {endpoint.provider} API key in the Model panel and press Use this model, "
        f"or set {variable} before starting."
    )
