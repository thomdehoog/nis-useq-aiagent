"""A scripted model in place of the real one, for the tests of every part of the assistant.

``Script`` plays the model: it makes the tool calls it is given, in order, so
a test controls exactly what "the model" asks for, and then checks what the
microscope (the real bridge over a fake NIS) and the operator see. The two
helpers read back what happened: ``tool_results`` the answers the tools gave
in a conversation, ``moves`` the stage moves the fake NIS recorded.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-09
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import FunctionModel


class Script:
    """A stand-in for the model: each call returns the next step.

    A step is text (the answer), a (tool name, arguments) pair (a tool call), a
    whole ModelResponse, or an exception (the model call fails, as when the API
    is overloaded).
    """

    def __init__(self, *steps):
        self.steps = list(steps)
        self.requests = []  # what the model was sent, per call

    def __call__(self, messages, info):
        self.requests.append(messages)
        step = self.steps.pop(0)
        if isinstance(step, Exception):
            raise step
        if isinstance(step, ModelResponse):
            return step
        if isinstance(step, str):
            return ModelResponse(parts=[TextPart(step)])
        name, args = step
        return ModelResponse(parts=[ToolCallPart(name, args)])

    def model(self):
        return FunctionModel(self)


def tool_results(assistant):
    """Every answer a tool gave in the conversation so far, oldest first."""
    return [
        part.content
        for message in assistant.history
        for part in message.parts
        if isinstance(part, ToolReturnPart)
    ]


def moves(fake):
    """The stage moves the fake NIS recorded, as "move_xy(x,y)" and "move_z(z)"."""
    return [call for call in fake.calls if call.startswith("move")]
