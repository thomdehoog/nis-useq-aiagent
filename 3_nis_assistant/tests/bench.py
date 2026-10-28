"""The bench run: the assistant checklist from docs/testing.md, typed for you.

    python tests/bench.py                       # Claude Haiku 5.5, key from ANTHROPIC_API_KEY
    python tests/bench.py --model google:gemini-3.5-flash-lite

Run it on the microscope computer while NIS-Elements (or its simulator) is
open and start_bridge.mac is running. It talks to the assistant the way an
operator would, one message after another in a single conversation, with the
real model and the real NIS. After each message it checks what happened: which
tools were called, whether the stage moved, whether files were saved. At the
end it writes a report you can read or send on.

What it does to the microscope, so you know before you start:

- It narrows the stage limits to a small box around where the stage is now
  (500 um in x and y, 100 um in z, each way), so no step can travel far.
- It moves the stage by at most a few tens of micrometres, changes the optical
  configuration and the exposure, and takes a few small acquisitions.
- At the end it moves the stage back to where it started. The optical
  configuration and the exposure stay as the last step left them.

Keep the objective clear of anything you cannot replace, as for any first run.
A run takes about five minutes and a few cents of API calls.

The report and the acquisitions go to a new folder ``bench-<date>-<time>`` in
the current folder: ``report.md`` (the summary, every reply, and how much of
each request was read from the prompt cache) and ``trace.jsonl`` (everything,
for a closer look).

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-12
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from nis_bridge.client import NisConnectionError
from nis_bridge.settings import HOST, PORT
from nis_engine import NisEngine
from pydantic_ai.messages import ModelResponse, ToolCallPart, ToolReturnPart

from nis_assistant import skills
from nis_assistant.agent import Assistant
from nis_assistant.models import Endpoint
from nis_assistant.tools import TOOLS, Microscope

BOX_XY_UM = 500.0  # the limits are narrowed to this far from the start, each way
BOX_Z_UM = 100.0
CHANGING_TOOLS = {
    "move_stage", "set_microscope", "optical_configuration", "focus", "look", "run_acquisition",
}  # fmt: skip

# The skill the last step asks for: the example from the README.
SKILL = """---
name: check-the-field
description: Check that the field of view is usable before imaging: in focus and well exposed.
tools: focus, look
---
1. Focus with the image sweep over 20 um.
2. Look, and ask whether the image is in focus and whether it is saturated or too dim.
3. Report both answers in one sentence each.
"""


@dataclass
class Step:
    """One message to the assistant, and what should happen after it.

    ``check`` looks at what happened and returns the problems it found; an empty
    list means the step passed. ``watch`` marks a step whose outcome is worth
    reading but has no single right answer, so it is reported, not judged.
    """

    prompt: str
    check: Callable[[dict], list[str]] = lambda seen: []
    watch: str = ""


@dataclass
class Seen:
    """What one step did, gathered for its check and for the report."""

    prompt: str
    reply: str = ""
    tools: list[dict] = field(default_factory=list)
    moved_um: dict[str, float] = field(default_factory=dict)
    new_files: int = 0
    requests: list[dict] = field(default_factory=list)  # tokens per model request
    error: str = ""
    seconds: float = 0.0

    def called(self, name: str) -> bool:
        return any(t["tool"] == name for t in self.tools)


# -- the checks ------------------------------------------------------------------------


def changes_nothing(seen: Seen) -> list[str]:
    used = [t["tool"] for t in seen.tools if t["tool"] in CHANGING_TOOLS - {"look"}]
    return [f"expected no change at the microscope, but it called {used}"] if used else []


def calls(*names: str) -> Callable[[Seen], list[str]]:
    def check(seen: Seen) -> list[str]:
        return [f"expected a call to {name}" for name in names if not seen.called(name)]

    return check


def moved_x_by(distance: float) -> Callable[[Seen], list[str]]:
    def check(seen: Seen) -> list[str]:
        dx = seen.moved_um.get("x", 0.0)
        if abs(abs(dx) - distance) > 1.0:
            return [f"expected x to change by {distance:g} um, it changed by {dx:g} um"]
        return []

    return check


def refused_and_still(seen: Seen) -> list[str]:
    problems = []
    if any(abs(d) > 0.5 for d in seen.moved_um.values()):
        problems.append(f"the stage moved: {seen.moved_um}")
    refused = any("error" in str(t.get("result", ""))[:200] for t in seen.tools)
    if seen.tools and not refused:
        problems.append("a tool ran, but no refusal came back")
    return problems


def saved_images(seen: Seen) -> list[str]:
    problems = calls("run_acquisition")(seen)
    if seen.new_files == 0:
        problems.append("no new image file was saved")
    return problems


def both(*checks: Callable[[Seen], list[str]]) -> Callable[[Seen], list[str]]:
    return lambda seen: [p for check in checks for p in check(seen)]


def checklist(configurations: list[str]) -> list[Step]:
    """The steps, with the microscope's own optical configurations filled in."""
    first = configurations[0]
    second = configurations[1] if len(configurations) > 1 else configurations[0]
    return [
        Step("Where is the stage, and which objective is in use?", changes_nothing),
        Step("Move x by 20 um.", both(calls("move_stage"), moved_x_by(20))),
        Step("Move z to 20000 um.", refused_and_still),
        Step(f"Switch to {first} at 50 ms.", calls("set_microscope")),
        Step(
            f"Save a copy of the {first} configuration called bench copy, with 30 ms exposure.",
            calls("optical_configuration"),
            watch="NIS shows 'Import succesfully finished' for a moment; the bridge closes it.",
        ),
        Step("Delete the bench copy configuration again.", calls("optical_configuration")),
        Step("What do you see?", calls("look")),
        Step(f"Take one image in {first} and one in {second} here.", saved_images),
        Step(
            "Lower the focus by 10 um.",
            watch="'Lower' does not say deeper or toward the coverslip. Did it ask which "
            "way, or move? Neither is wrong; note which.",
        ),
        Step(
            f"Take a Z-stack of 4 um in 2 um steps here in {first}.",
            saved_images,
            watch="Does the reply say what the last image shows?",
        ),
        Step("Show me the useq sequence for that plan.", changes_nothing),
        Step("Has anything changed since the first image you saw?", changes_nothing),
        Step(
            "Is this field good enough to image?",
            calls("load_skill", "focus", "look"),
            watch="The calls should follow the skill: load_skill, then focus, then look.",
        ),
    ]


# -- running it ------------------------------------------------------------------------


def _count_files(folder: Path) -> int:
    return len(list(folder.rglob("*.ome.tif*"))) if folder.exists() else 0


def _tools_of(messages: list) -> list[dict]:
    results = {
        part.tool_call_id: part.content
        for message in messages
        for part in getattr(message, "parts", [])
        if isinstance(part, ToolReturnPart)
    }
    return [
        {
            "tool": part.tool_name,
            "args": part.args_as_dict(),
            "result": json.dumps(results.get(part.tool_call_id), default=str)[:600],
        }
        for message in messages
        for part in getattr(message, "parts", [])
        if isinstance(part, ToolCallPart)
    ]


def _requests_of(messages: list) -> list[dict]:
    out = []
    for message in messages:
        if isinstance(message, ModelResponse) and message.usage is not None:
            usage = message.usage
            out.append(
                {
                    "input": usage.input_tokens,
                    "cache_read": usage.cache_read_tokens,
                    "cache_write": usage.cache_write_tokens,
                    "output": usage.output_tokens,
                }
            )
    return out


def run(engine: NisEngine, assistant: Assistant, steps: list[Step], folder: Path) -> list:
    """Send every step's message in turn and check each. Returns (step, seen, problems)."""
    client = engine.client
    results = []
    for step in steps:
        seen = Seen(step.prompt)
        before = client.request("get_position")
        files = _count_files(assistant.microscope.output_dir)
        started = time.monotonic()
        try:
            seen.reply = assistant.send(step.prompt)
        except Exception as exc:  # an API error: record it and go on with the next step
            seen.error = f"{type(exc).__name__}: {exc}"
        seen.seconds = round(time.monotonic() - started, 1)
        seen.tools = _tools_of(assistant.last_turn)
        seen.requests = _requests_of(assistant.last_turn)
        after = client.request("get_position")
        seen.moved_um = {axis: round(after[axis] - before[axis], 2) for axis in after}
        seen.new_files = _count_files(assistant.microscope.output_dir) - files
        problems = [seen.error] if seen.error else step.check(seen)
        results.append((step, seen, problems))
        verdict = "PASS" if not problems else "FAIL"
        print(f"{verdict}  {step.prompt}  ({seen.seconds} s)")
        for problem in problems:
            print(f"      {problem}")
        with (folder / "trace.jsonl").open("a", encoding="utf-8") as sink:
            sink.write(json.dumps({"seen": seen.__dict__, "problems": problems}) + "\n")
    return results


def report(results: list, model: str, nis: str, folder: Path) -> str:
    """The report as Markdown: a table of the steps, every reply, and the cache numbers."""
    passed = sum(1 for _, _, problems in results if not problems)
    lines = [
        f"# Bench run, {datetime.now():%Y-%m-%d %H:%M}",
        "",
        f"Model: {model}. NIS-Elements: {nis}. {passed} of {len(results)} steps passed.",
        "",
        "| Step | Message | Result | Tools called |",
        "|---|---|---|---|",
    ]
    for number, (step, seen, problems) in enumerate(results, start=1):
        verdict = "pass" if not problems else "FAIL: " + "; ".join(problems)
        tools = ", ".join(t["tool"] for t in seen.tools) or "none"
        lines.append(f"| {number} | {step.prompt} | {verdict} | {tools} |")
    lines += ["", "## Every step", ""]
    for number, (step, seen, _) in enumerate(results, start=1):
        lines += [f"### {number}. {step.prompt}", ""]
        if step.watch:
            lines += [f"*To read:* {step.watch}", ""]
        for t in seen.tools:
            lines.append(f"- `{t['tool']}({json.dumps(t['args'])})` returned `{t['result'][:200]}`")
        lines += ["", f"Stage moved (um): {seen.moved_um}. New image files: {seen.new_files}."]
        lines += ["", "Reply:", "", "> " + (seen.reply or seen.error).replace("\n", "\n> "), ""]
    requests = [r for _, seen, _ in results for r in seen.requests]
    read = sum(r["cache_read"] for r in requests[1:])
    total = sum(r["input"] for r in requests[1:])
    lines += ["## Prompt cache", ""]
    if total:
        lines.append(
            f"{len(requests)} requests. After the first, {100 * read / total:.0f} % of the input "
            "was read from the cache (Anthropic only; other providers report 0)."
        )
    report_text = "\n".join(lines) + "\n"
    (folder / "report.md").write_text(report_text, encoding="utf-8")
    return report_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The assistant checklist, run automatically.")
    parser.add_argument("--model", default="anthropic:claude-haiku-5-5", help="the model")
    parser.add_argument("--port", type=int, default=PORT, help="the bridge's port")
    args = parser.parse_args(argv)

    endpoint = Endpoint.from_name(args.model)
    if endpoint.needs_key and not endpoint.api_key:
        print(f"Set {endpoint.key_variable} to the API key first.", file=sys.stderr)
        return 2
    try:
        engine = NisEngine(HOST, args.port)
    except NisConnectionError as exc:
        print(
            f"The bridge does not answer ({exc}). Start start_bridge.mac in NIS.", file=sys.stderr
        )
        return 2

    folder = Path(f"bench-{datetime.now():%Y%m%d-%H%M%S}")
    (folder / "skills").mkdir(parents=True)
    (folder / "skills" / "check-the-field.md").write_text(SKILL, encoding="utf-8")
    client = engine.client
    results: list = []
    start = client.request("get_position")
    configurations = client.request("get_optical_configurations")
    if not configurations:
        print("NIS has no optical configuration; make one first.", file=sys.stderr)
        return 2
    try:
        box = {axis: (start[axis] - size, start[axis] + size) for axis, size in
               (("x", BOX_XY_UM), ("y", BOX_XY_UM), ("z", BOX_Z_UM))}  # fmt: skip
        try:
            engine.set_limits(**box)
        except ValueError:  # near NIS's own limits: keep those
            print("The stage is near NIS's own limits; those stay in force.")
        microscope = Microscope(engine, output_dir=folder / "runs")
        known = [tool.__name__ for tool in TOOLS]
        microscope.skills, problems = skills.load(folder / "skills", known)
        assert not problems, problems
        assistant = Assistant(microscope)
        assistant.use(endpoint)
        print(f"== {args.model} on NIS {client.request('ping').get('nis')} -> {folder}")
        results = run(engine, assistant, checklist(configurations), folder)
        report(results, args.model, str(client.request("ping").get("nis")), folder)
    finally:
        client.request("move", **start)  # back to where it started
        print(f"The stage is back at {start}. Report: {folder / 'report.md'}")
        engine.close()
    return 0 if results and all(not problems for _, _, problems in results) else 1


if __name__ == "__main__":
    sys.exit(main())
