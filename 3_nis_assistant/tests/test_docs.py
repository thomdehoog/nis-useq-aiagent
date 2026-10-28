"""The documentation stays true to the code: the front page lists every tool.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-28
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""


def test_the_front_page_lists_every_tool_and_only_those():
    """README.md's table of what the assistant can call stays the same as TOOLS:
    every tool, and the number of options each takes."""
    import inspect
    import re
    from pathlib import Path

    from nis_assistant.tools import TOOLS

    front = Path(__file__).parents[2] / "README.md"
    table = front.read_text(encoding="utf-8").split("What the assistant can call:", 1)[1]
    listed = dict(re.findall(r"^\| `(\w+)` \| ([^|]+) \|", table, re.M))
    options = {}
    for tool in TOOLS:
        params = inspect.signature(getattr(tool, "__wrapped__", tool)).parameters
        count = len([name for name in params if name != "ctx"])
        options[tool.__name__] = str(count) if count else "–"  # noqa: RUF001 - the table's en dash for "none"
    assert {name: shown.strip() for name, shown in listed.items()} == options
