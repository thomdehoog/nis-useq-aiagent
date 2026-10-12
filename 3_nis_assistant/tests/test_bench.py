"""The bench run itself, offline: against the fake NIS, with a scripted model that
makes one move and otherwise only answers in words. No real model is called.

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

import bench
from test_agent import Script, microscope  # noqa: F401  (microscope is a fixture)

from nis_assistant.agent import Assistant


def test_the_bench_checks_each_step_and_writes_a_report(microscope, tmp_path):  # noqa: F811
    steps = bench.checklist(["DAPI", "FITC"])[:3]  # read, move x by 20, a refused z
    script = Script("It is at x 1000.", ("move_stage", {"x": 1020}), "Moved.", "Refused.")
    assistant = Assistant(microscope, model=script.model())
    results = bench.run(microscope.engine, assistant, steps, tmp_path)

    verdicts = [problems for _, _, problems in results]
    assert verdicts[0] == [] and verdicts[1] == []  # a read only; a 20 um move in x
    assert verdicts[2] == []  # nothing moved and no tool ran: a refusal in words is fine
    assert results[1][1].moved_um["x"] == pytest.approx(20)

    text = bench.report(results, "scripted", "fake", tmp_path)
    assert "3 of 3 steps passed" in text and (tmp_path / "report.md").exists()
    assert (tmp_path / "trace.jsonl").read_text().count("\n") == 3


def test_a_step_that_does_not_happen_is_reported_with_the_reason(microscope, tmp_path):  # noqa: F811
    step = bench.checklist(["DAPI"])[1]  # move x by 20 um
    assistant = Assistant(microscope, model=Script("Sure, done.").model())
    ((_, _, problems),) = bench.run(microscope.engine, assistant, [step], tmp_path)
    assert "expected a call to move_stage" in problems
    assert any("changed by 0 um" in p for p in problems)
