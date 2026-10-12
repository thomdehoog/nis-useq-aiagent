"""Skills: how a skill file is read, and how the assistant offers and hands over skills.

A scripted model stands in for the real one (see ``Script`` in test_agent.py), so
these tests check the plumbing: what the model is told and which tools it is
offered, not how well a real model uses a skill. That is the evaluation's job.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-12
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

import pytest

pytest.importorskip("pydantic_ai")
pytest.importorskip("pymmcore_plus")

from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import FunctionModel
from test_agent import microscope, tool_results  # noqa: F401  (microscope is a fixture)

from nis_assistant import skills
from nis_assistant.agent import Assistant
from nis_assistant.tools import TOOLS

KNOWN = [tool.__name__ for tool in TOOLS]
FIND_CELLS = """---
name: find-cells
description: Find a field with cells in it and bring them into focus.
tools: look, move_stage, focus
---
1. Look at the current field.
2. If there are no cells, move one field to the right and look again.
"""


class Recorder:
    """A scripted model that also keeps what it was offered: instructions and tools."""

    def __init__(self, *steps):
        self.steps, self.offered, self.instructions = list(steps), [], []

    def __call__(self, messages, info):
        self.offered.append({tool.name for tool in info.function_tools})
        self.instructions.append(messages[-1].instructions or "")
        step = self.steps.pop(0)
        if isinstance(step, str):
            return ModelResponse(parts=[TextPart(step)])
        return ModelResponse(parts=[ToolCallPart(*step)])


# -- reading a skill file ---------------------------------------------------------------


def test_a_skill_file_is_read_into_its_parts():
    skill = skills.parse(FIND_CELLS, known_tools=KNOWN)
    assert skill.name == "find-cells"
    assert skill.description.startswith("Find a field with cells")
    assert skill.tools == ("look", "move_stage", "focus")
    assert skill.steps.startswith("1. Look at the current field.")


@pytest.mark.parametrize(
    ("text", "problem"),
    [
        ("name: a\ndescription: b\n\nsteps", "head between two '---' lines"),
        ("---\nname: a\n---\nsteps", "needs a name and a description"),
        ("---\nname: a\ndescription: b\n---\n", "no steps"),
        ("---\nname: Find cells!\ndescription: b\n---\nsteps", "small letters"),
        ("---\nname: a\ndescription: b\ntools: look, zoom_in\n---\nsteps", "zoom_in"),
        ("---\nname: a\ndescription: b\n---\n" + "x" * 9000, "at most"),
    ],
)
def test_a_skill_file_with_a_mistake_says_what_is_wrong(text, problem):
    with pytest.raises(ValueError, match=problem):
        skills.parse(text, known_tools=KNOWN)


def test_a_folder_loads_the_good_files_and_reports_the_others(tmp_path):
    (tmp_path / "find-cells.md").write_text(FIND_CELLS, encoding="utf-8")
    (tmp_path / "again.md").write_text(FIND_CELLS, encoding="utf-8")  # the same name twice
    (tmp_path / "broken.md").write_text("no head at all", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("not a skill", encoding="utf-8")  # only .md is read
    found, problems = skills.load(tmp_path, KNOWN)
    assert list(found) == ["find-cells"]
    assert len(problems) == 2
    assert any("broken.md" in p for p in problems)
    assert any("repeats the name" in p for p in problems)


def test_a_missing_folder_means_no_skills(tmp_path):
    assert skills.load(tmp_path / "nowhere", KNOWN) == ({}, [])
    assert skills.load(None, KNOWN) == ({}, [])


# -- the assistant and its skills -------------------------------------------------------


def test_without_skills_neither_the_list_nor_load_skill_is_offered(microscope):  # noqa: F811
    model = Recorder("Hello!")
    Assistant(microscope, model=FunctionModel(model)).send("hi")
    assert "load_skill" not in model.offered[0]
    assert "Skills are" not in model.instructions[0]


def test_with_skills_the_model_sees_their_names_and_can_load_one(microscope):  # noqa: F811
    microscope.skills = {"find-cells": skills.parse(FIND_CELLS, known_tools=KNOWN)}
    model = Recorder(("load_skill", {"name": "find-cells"}), "I will look first.")
    assistant = Assistant(microscope, model=FunctionModel(model))
    assistant.send("Find me some cells")
    assert "load_skill" in model.offered[0]
    told = model.instructions[0]
    assert "- find-cells: Find a field with cells in it and bring them into focus." in told
    assert "1. Look at the current field." not in told  # the steps come only when loaded
    result = tool_results(assistant)[0]
    assert result["skill"] == "find-cells" and result["steps"].startswith("1. Look")
    assert result["tools"] == ["look", "move_stage", "focus"]
    assert microscope.tools == [("load_skill", {"name": "find-cells"})]  # the window hears of it


def test_an_unknown_skill_is_refused_with_the_names_there_are(microscope):  # noqa: F811
    microscope.skills = {"find-cells": skills.parse(FIND_CELLS, known_tools=KNOWN)}
    model = Recorder(("load_skill", {"name": "centre"}), "There is no such skill.")
    assistant = Assistant(microscope, model=FunctionModel(model))
    assistant.send("Centre the sample")
    error = tool_results(assistant)[0]["error"]
    assert error["code"] == "not_found" and error["configured_options"] == ["find-cells"]
