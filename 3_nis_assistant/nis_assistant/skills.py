"""Skills: short procedures, written in plain text, that the assistant follows when a
request matches one.

A skill is one Markdown file (``.md``) in the skills folder. It starts with a short
head between two ``---`` lines, then the steps in your own words:

    ---
    name: find-cells
    description: Find a field with cells in it and bring them into focus.
    tools: look, move_stage, focus
    ---
    1. Look at the current field. If it shows cells, go to step 3.
    2. Move the stage by one field width to the right and look again, at most five times.
    3. Focus with the image sweep and look once more to check.
    Report where the cells are and how sharp the image is.

The head needs a ``name`` and a ``description``; ``tools`` is optional and lists the
tools the steps use, so that a misspelt tool name is caught when the file is read.

The model is shown only each skill's name and description, which keeps every request
small. When a request matches a skill, the model calls ``load_skill`` and gets the
steps. A skill does not let the model do anything it could not do before: it is
advice on how to chain the same tools, and every tool still checks the limits.

Skills live in a folder of their own (by default ``nis_assistant_skills`` in your
home folder), so each lab keeps its own. None ship with the assistant.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-12
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .settings import SKILL_MAX_CHARS

NAME = re.compile(r"[a-z0-9][a-z0-9_-]{0,39}")


@dataclass(frozen=True)
class Skill:
    """One skill as read from its file."""

    name: str
    description: str
    tools: tuple[str, ...]
    steps: str
    path: Path | None = None


def parse(text: str, path: Path | None = None, known_tools: Iterable[str] = ()) -> Skill:
    """One skill from the text of its file.

    ``known_tools`` are the tool names a skill may list; when given, a name outside
    them is an error. Raises ValueError with a sentence on what is wrong.
    """
    where = path.name if path is not None else "the skill"
    if len(text) > SKILL_MAX_CHARS:
        raise ValueError(f"{where} has {len(text)} characters; at most {SKILL_MAX_CHARS}.")
    lines = text.lstrip("﻿").splitlines()
    stripped = [line.strip() for line in lines]
    if not lines or stripped[0] != "---" or "---" not in stripped[1:]:
        raise ValueError(f"{where} must start with a head between two '---' lines.")
    end = 1 + stripped[1:].index("---")
    head: dict[str, str] = {}
    for line in lines[1:end]:
        key, sep, value = line.partition(":")
        if sep:
            head[key.strip().lower()] = value.strip()
    name, description = head.get("name", "").lower(), head.get("description", "")
    if not name or not description:
        raise ValueError(f"{where}: the head needs a name and a description.")
    if not NAME.fullmatch(name):
        raise ValueError(
            f"{where}: the name {name!r} may hold only small letters, digits, - and _ (at most 40)."
        )
    tools = tuple(t.strip() for t in head.get("tools", "").split(",") if t.strip())
    known = set(known_tools)
    unknown = [t for t in tools if known and t not in known]
    if unknown:
        raise ValueError(f"{where} names tools the assistant does not have: {', '.join(unknown)}.")
    steps = "\n".join(lines[end + 1 :]).strip()
    if not steps:
        raise ValueError(f"{where} has no steps after the head.")
    return Skill(name, description, tools, steps, path)


def load(folder: Path | str | None, known_tools: Iterable[str] = ()) -> tuple[dict, list[str]]:
    """Every skill in a folder, by name, and one sentence for each file that could not be used.

    A missing folder is not an error: it simply means no skills. A file with a
    mistake is left out and reported, so one bad file does not stop the others.
    """
    skills: dict[str, Skill] = {}
    problems: list[str] = []
    if folder is None or not Path(folder).is_dir():
        return skills, problems
    known = tuple(known_tools)
    for path in sorted(Path(folder).glob("*.md")):
        try:
            skill = parse(path.read_text(encoding="utf-8"), path, known)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            problems.append(f"Skill not loaded: {exc}")
            continue
        if skill.name in skills:
            problems.append(f"Skill not loaded: {path.name} repeats the name {skill.name!r}.")
            continue
        skills[skill.name] = skill
    return skills, problems


def listing(skills: dict[str, Skill]) -> str:
    """The skills as the model sees them: one line each, the name and the description."""
    return "\n".join(f"- {s.name}: {s.description}" for s in skills.values())
