"""Choosing a model: presets, keys from the window or the environment, and model objects.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

import pytest

pytest.importorskip("pydantic_ai")

from nis_assistant import models
from nis_assistant.models import Endpoint


def test_a_preset_fills_the_blanks(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    endpoint = Endpoint.from_preset("Gemini")
    assert endpoint.kind == "google" and endpoint.model == "gemini-3.5-flash-lite"
    assert endpoint.api_key == "" and endpoint.needs_key and endpoint.vision
    assert endpoint.name == "Gemini: gemini-3.5-flash-lite"


def test_a_typed_key_wins_over_the_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "from-env")
    assert Endpoint.from_preset("Gemini").api_key == "from-env"
    assert Endpoint.from_preset("Gemini", api_key=" typed ").api_key == "typed"


def test_the_older_google_variable_still_counts(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "older-name")
    assert Endpoint.from_preset("Gemini").api_key == "older-name"


def test_a_server_needs_no_key_and_keeps_its_address():
    endpoint = Endpoint.from_preset("OpenAI-style server", base_url=" http://box:8000/v1 ")
    assert not endpoint.needs_key and endpoint.base_url == "http://box:8000/v1"
    assert not endpoint.vision
    assert Endpoint.from_preset("OpenAI-style server", vision=True).vision


def test_a_command_line_name_maps_to_a_preset(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    endpoint = Endpoint.from_name("openai:gpt-5-mini")
    assert endpoint.provider == "OpenAI" and endpoint.model == "gpt-5-mini"
    assert Endpoint.from_name("google-gla:gemini-3.5-flash-lite").provider == "Gemini"
    other = Endpoint.from_name("gemma4:31b")  # no known prefix: a server of one's own
    assert other.kind == "openai-compatible" and other.model == "gemma4:31b"


def test_each_kind_builds_its_model_object():
    google = models.build_model(Endpoint.from_preset("Gemini", api_key="k"))
    assert type(google).__name__ == "GoogleModel" and google.model_name == "gemini-3.5-flash-lite"
    server = models.build_model(Endpoint.from_preset("OpenAI-style server"))
    assert type(server).__name__ == "OpenAIChatModel" and server.model_name == "gemma4:31b"


def test_the_settings_follow_the_kind():
    assert Endpoint.from_preset("Gemini").settings["temperature"] == 0.0
    assert "parallel_tool_calls" not in Endpoint.from_preset("OpenAI-style server").settings


def test_the_advice_names_the_variable():
    advice = models.missing_key_advice(Endpoint.from_preset("OpenAI", api_key="x"))
    assert "OPENAI_API_KEY" in advice and "Model panel" in advice
    assert "server" in models.missing_key_advice(Endpoint.from_preset("OpenAI-style server"))


# -- model files on this computer -----------------------------------------------------------


def test_an_anthropic_request_is_cached_and_carries_no_temperature():
    """On Anthropic the tool definitions and the instructions are cached for an hour and the
    history for five minutes: three of the four breakpoints, the hour first, as the API asks.
    claude-haiku-5-5 refuses a temperature. The request pydantic-ai sends is read off the wire."""
    import json

    import httpx2 as httpx  # the Anthropic SDK takes its own fork of httpx
    from anthropic import AsyncAnthropic
    from pydantic_ai import Agent, Tool
    from pydantic_ai.models.anthropic import AnthropicModel
    from pydantic_ai.providers.anthropic import AnthropicProvider

    bodies = []

    def answer(request):
        bodies.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "id": "m",
                "type": "message",
                "role": "assistant",
                "model": "claude-haiku-5-5",
                "content": [{"type": "text", "text": "ok"}],
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {"input_tokens": 10, "output_tokens": 1},
            },
        )

    endpoint = Endpoint.from_preset("Anthropic", api_key="k")
    transport = httpx.MockTransport(answer)
    client = AsyncAnthropic(api_key="k", http_client=httpx.AsyncClient(transport=transport))
    model = AnthropicModel(endpoint.model, provider=AnthropicProvider(anthropic_client=client))

    def first(a: int) -> str:
        return "1"

    def second(b: int) -> str:
        return "2"

    agent = Agent(
        model,
        instructions="the instructions",
        tools=[Tool(first), Tool(second)],
        model_settings=endpoint.settings,
    )
    agent.run_sync("turn two", message_history=agent.run_sync("turn one").all_messages())
    assert len(bodies) == 2
    hour, five_minutes = {"type": "ephemeral", "ttl": "1h"}, {"type": "ephemeral", "ttl": "5m"}
    for body in bodies:
        assert body["cache_control"] == five_minutes
        assert [t.get("cache_control") for t in body["tools"]] == [None, hour]
        assert body["system"][-1]["cache_control"] == hour
        assert "temperature" not in body
    for provider in ("Gemini", "OpenAI", "OpenAI-style server"):
        settings = Endpoint.from_preset(provider, api_key="k").settings
        assert not any(key.startswith("anthropic_") for key in settings)


def test_the_anthropic_preset_and_its_prefix(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "from-env")
    endpoint = Endpoint.from_name("anthropic:claude-haiku-5-5")
    assert (endpoint.provider, endpoint.kind) == ("Anthropic", "anthropic")
    assert endpoint.model == "claude-haiku-5-5"
    assert endpoint.api_key == "from-env" and endpoint.vision
    assert type(models.build_model(endpoint)).__name__ == "AnthropicModel"
