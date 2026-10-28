"""The documentation stays true to the code: the front page lists every tool.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-28
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""


def test_the_front_page_lists_every_tool_and_only_those():
    """README.md's table of what the assistant can call stays the same as TOOLS."""
    import re
    from pathlib import Path

    from nis_assistant.tools import TOOLS

    front = Path(__file__).parents[2] / "README.md"
    table = front.read_text(encoding="utf-8").split("What the assistant can call:", 1)[1]
    listed = re.findall(r"^\| `(\w+)` \|", table, re.M)
    assert sorted(listed) == sorted(tool.__name__ for tool in TOOLS)
