"""The tools: everything the model can ask the microscope to do, one function each.

Each tool checks what it is asked before acting, and answers with data the
model can read: the result, or an "error" with what was refused, why, and
what to do next (the advice in ``instructions.py``). The two big steps,
starting an acquisition and moving the stage far, are not carried out in the
turn the model first asks for them: the tool answers that the operator's
go-ahead is needed (``needs_go_ahead``), and the step runs only in the next
turn, after the operator has replied. That rule is in this code, not in the
model's instructions.

``TOOLS`` lists them; ``agent.py`` registers them on the Agent. This is the
place to look up or add a tool. At the end are two guards on the model's reply
itself (``REPLY_GUARDS``): an empty reply, and a reply that claims to have done
something in a turn that called no tool, each go back to the model once.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from __future__ import annotations

import asyncio
import contextlib
import functools
import inspect
import os
import re
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import nis_bridge
import nis_engine
import numpy as np
import useq
from nis_bridge.install_macros import MACRO
from nis_bridge.settings import FOCUS_TIMEOUT_S
from pydantic import BaseModel
from pydantic_ai import ModelRetry, RunContext
from pydantic_ai.messages import ToolCallPart
from pymmcore_plus.mda import MDARunner

from .images import image_statistics, snap
from .instructions import (
    BRIDGE_MACRO_MISSING,
    BRIDGE_STEPS,
    CALLED_NOTHING_CHALLENGE,
    CANCELLED_ADVICE,
    EMPTY_REPLY_CHALLENGE,
    EMPTY_REPLY_FALLBACK,
    FAILURE_ADVICE,
    GO_AHEAD_ADVICE,
    LAST_IMAGE_QUESTION,
    LIMIT_ADVICE,
    OPTCONF_STEPS,
    OPTIONS_ADVICE,
    START_ADVICE,
)
from .memory import _is_operator_turn
from .microscope import Microscope
from .plans import AcquisitionPlan, PositionSpec, count_images, describe, plan_to_sequence
from .settings import (
    CONFIRM_XY_UM,
    CONFIRM_Z_UM,
    MAX_EXPOSURE_MS,
    MAX_SWEEP_UM,
    SOURCE_LINES,
    SOURCE_MATCHES,
)

# The source code the assistant may read to explain how things work: the three
# parts and useq-schema as installed, nothing else on the computer.
SOURCE_ROOTS = {
    "nis_bridge": Path(nis_bridge.__file__).parent,
    "nis_engine": Path(nis_engine.__file__).parent,
    "nis_assistant": Path(__file__).parent,
    "useq": Path(useq.__file__).parent,
}


def refusal(
    ctx: RunContext[Microscope], code: str, message: str, advice: str, **details: Any
) -> dict[str, Any]:
    """A refused action, as data the model reads, with what to do about it.

    Limit breaches and invalid values also go to the window's warning banner,
    so the operator sees them whatever the model says.
    """
    if code in ("limit", "invalid"):
        ctx.deps.on_warning(message)
    return {"error": {"code": code, "message": message, **details, "advice": advice}}


def needs_go_ahead(ctx: RunContext[Microscope], key: str, summary: str) -> dict | None:
    """None if the operator has had the chance to agree to this action; else the
    answer that tells the assistant to ask first.

    The first request for a long move is only noted. The same request in the
    operator's next turn (after they read the question and replied) goes ahead.
    Whether the reply was a yes is for the model to read; that the operator saw
    the question before anything moved is guaranteed here.
    """
    if ctx.deps.go_ahead_asked.pop(key, None) == ctx.deps.turn - 1:
        return None
    ctx.deps.go_ahead_asked[key] = ctx.deps.turn
    return {"status": "needs_go_ahead", "not_done_yet": summary, "advice": GO_AHEAD_ADVICE}


def guarded_tool(fn: Callable) -> Callable:
    """The checks every tool shares, around the tool itself.

    Before the tool runs: nothing runs after Cancel, and the window hears of
    each call as it starts. Afterwards: any error (a refusal from NIS, a full
    disk) becomes a failure the assistant can explain, instead of ending the
    turn with a crash. Pydantic AI's ModelRetry, which hands a malformed call
    back to the model, passes through unchanged.
    """

    def before(ctx: RunContext[Microscope], kwargs: dict) -> dict | None:
        if ctx.deps.cancel.is_set():
            return {"status": "cancelled", "advice": CANCELLED_ADVICE}
        args = {  # what the model asked for, without the arguments it left out
            k: v.model_dump(exclude_none=True) if isinstance(v, BaseModel) else v
            for k, v in kwargs.items()
            if v is not None
        }
        ctx.deps.on_tool(fn.__name__, args)
        return None

    def failed(exc: Exception) -> dict:
        return {
            "error": {
                "code": "failed",
                "message": f"{type(exc).__name__}: {exc}",
                "advice": FAILURE_ADVICE,
            }
        }

    if inspect.iscoroutinefunction(fn):

        @functools.wraps(fn)
        async def async_wrapper(ctx: RunContext[Microscope], *args: Any, **kwargs: Any) -> Any:
            if (stopped := before(ctx, kwargs)) is not None:
                return stopped
            try:
                return await fn(ctx, *args, **kwargs)
            except ModelRetry:
                raise
            except Exception as exc:
                return failed(exc)

        return async_wrapper

    @functools.wraps(fn)
    def wrapper(ctx: RunContext[Microscope], *args: Any, **kwargs: Any) -> Any:
        if (stopped := before(ctx, kwargs)) is not None:
            return stopped
        try:
            return fn(ctx, *args, **kwargs)
        except ModelRetry:
            raise
        except Exception as exc:
            return failed(exc)

    return wrapper


def bridge_steps() -> list[str]:
    """How to start the bridge, with the macro's full path (or how to write the macro first)."""
    macro = str(MACRO)
    if MACRO.exists():
        return [step.format(macro=macro) for step in BRIDGE_STEPS]
    return [BRIDGE_MACRO_MISSING.format(macro=macro), *BRIDGE_STEPS[:2]]


def check_setup(ctx: RunContext[Microscope]) -> dict[str, Any]:
    """Whether NIS-Elements and its bridge answer, and whether an optical
    configuration exists, with the steps for the operator when not.

    Call it when the microscope does not answer, or when no optical
    configuration is listed; it moves nothing.
    """
    engine = ctx.deps.engine
    try:
        ctx.deps.ensure_connected()
        info = engine.client.request("ping")
    except Exception as exc:  # the bridge is not there, or NIS is closed
        return {
            "bridge": "not answering",
            "error": str(exc),
            "steps_for_the_operator": bridge_steps(),
        }
    configurations = engine.client.request("get_optical_configurations")
    result: dict[str, Any] = {
        "bridge": "running",
        "nis_elements": info.get("nis"),
        "optical_configurations": configurations,
    }
    if not configurations:
        result["note"] = (
            "NIS lists no optical configuration, so nothing can be imaged in a named "
            "channel until one exists."
        )
        result["steps_for_the_operator"] = OPTCONF_STEPS
    return result


@guarded_tool
def get_status(ctx: RunContext[Microscope]) -> dict[str, Any]:
    """Everything the microscope reports: position, limits, objectives, optical
    configurations and the Perfect Focus System (PFS)."""
    client = ctx.deps.client
    return {
        "position_um": client.request("get_position"),
        "stage_limits_um": ctx.deps.engine.limits(),
        "objectives": client.request("get_objectives"),
        "optical_configurations": client.request("get_optical_configurations"),
        "pfs": client.request("get_pfs"),
    }


@guarded_tool
def move_stage(
    ctx: RunContext[Microscope],
    x: float | None = None,
    y: float | None = None,
    z: float | None = None,
) -> dict[str, Any]:
    """Move the stage to an absolute position.

    Args:
        x: stage x in um; leave out to keep.
        y: stage y in um; leave out to keep.
        z: focus z in um; leave out to keep.
    """
    client = ctx.deps.client
    target = {axis: v for axis, v in (("x", x), ("y", y), ("z", z)) if v is not None}
    if not target:
        raise ModelRetry("Give at least one of x, y, z.")
    limits = ctx.deps.engine.limits()
    for axis, value in target.items():
        lo, hi = limits[axis]["min"], limits[axis]["max"]
        if not lo <= value <= hi:
            return refusal(
                ctx,
                "limit",
                f"{axis} = {value:g} um is outside the stage limits [{lo:g}, {hi:g}] um. "
                "The stage did not move.",
                LIMIT_ADVICE,
            )
    here = client.request("get_position")
    anchor = ctx.deps.anchor or here
    xy_step = max(abs(target.get(a, here[a]) - anchor[a]) for a in ("x", "y"))
    z_step = abs(target.get("z", here["z"]) - anchor["z"])
    if xy_step <= CONFIRM_XY_UM and z_step <= CONFIRM_Z_UM:
        return client.request("move", **target)
    where = ", ".join(f"{a} = {v:g} um" for a, v in target.items())
    summary = (
        f"move the stage to {where}: {xy_step:.0f} um in XY and {z_step:.0f} um in Z "
        "from where it was when the operator last wrote"
    )
    if (question := needs_go_ahead(ctx, f"move {sorted(target.items())}", summary)) is not None:
        return question
    moved = client.request("move", **target)
    ctx.deps.anchor = moved  # the operator agreed to this position
    return moved


@guarded_tool
def set_microscope(
    ctx: RunContext[Microscope],
    optical_configuration: str | None = None,
    exposure_ms: float | None = None,
    objective_slot: int | None = None,
    pfs_on: bool | None = None,
) -> dict[str, Any]:
    """Change optical settings. Leave out what should stay as it is.

    Args:
        optical_configuration: name of a NIS optical configuration, e.g. "DAPI".
        exposure_ms: camera exposure in milliseconds.
        objective_slot: nosepiece slot of the objective, counting from 1.
        pfs_on: switch the Perfect Focus System on (true) or off (false).
    """
    client = ctx.deps.client
    # Everything is checked first; only then does anything change.
    if optical_configuration is not None:
        known = client.request("get_optical_configurations")
        if optical_configuration not in known:
            return refusal(
                ctx,
                "invalid",
                f"{optical_configuration!r} is not an optical configuration in NIS-Elements",
                OPTIONS_ADVICE,
                configured_options=known,
            )
    if exposure_ms is not None and not 0 < exposure_ms <= MAX_EXPOSURE_MS:
        return refusal(
            ctx,
            "invalid",
            f"the exposure must be between 0 and {MAX_EXPOSURE_MS:g} ms",
            FAILURE_ADVICE,
        )
    if objective_slot is not None:
        objectives = client.request("get_objectives")["objectives"]
        if not objectives.get(str(objective_slot)):
            fitted = {slot: name for slot, name in objectives.items() if name}
            return refusal(
                ctx,
                "invalid",
                f"there is no objective in nosepiece slot {objective_slot}",
                OPTIONS_ADVICE,
                configured_options=fitted,
            )

    applied: dict[str, Any] = {}
    if optical_configuration is not None:
        reply = client.request("select_optical_configuration", name=optical_configuration)
        applied["optical_configuration"] = reply["selected"]
    if objective_slot is not None:
        reply = client.request("set_objective", position=objective_slot)
        applied["objective_slot"] = reply["current"]
    if exposure_ms is not None:
        reply = client.request("set_exposure", exposure_ms=exposure_ms)
        applied["exposure_ms"] = reply["exposure_ms"]
    if pfs_on is not None:
        applied["pfs"] = client.request("set_pfs", on=pfs_on)["meaning"]
    return applied


@guarded_tool
def focus(
    ctx: RunContext[Microscope],
    method: Literal["pfs", "image_sweep"] = "pfs",
    range_um: float = 50.0,
) -> dict[str, Any]:
    """Find focus.

    Args:
        method: "pfs" locks focus with the Perfect Focus System; "image_sweep" moves
            the focus through range_um around the current z and stops at the
            sharpest image.
        range_um: total height of the image sweep, in um (at most 100).
    """
    client = ctx.deps.client
    before = client.request("get_position")["z"]
    if method == "pfs":
        was_on = client.request("get_pfs")["on"]
        result = client.request("set_pfs", on=True, timeout_s=10.0)
        if not was_on:
            client.request("set_pfs", on=False)  # leave the PFS as it was
        if result["status"] != 1:
            return {
                "focused": False,
                "pfs": result["meaning"],
                "z_um": before,
                "advice": FAILURE_ADVICE,
            }
    else:
        if not 0 < range_um <= MAX_SWEEP_UM:
            return refusal(
                ctx,
                "invalid",
                f"the focus sweep range must be between 0 and {MAX_SWEEP_UM:g} um",
                FAILURE_ADVICE,
            )
        limits = ctx.deps.engine.limits()["z"]
        low, high = before - range_um / 2, before + range_um / 2
        if low < limits["min"] or high > limits["max"]:
            return refusal(
                ctx,
                "limit",
                f"a {range_um:g} um sweep around z = {before:g} um would leave the Z limits "
                f"[{limits['min']:g}, {limits['max']:g}] um. Nothing moved.",
                LIMIT_ADVICE,
            )
        client.request("autofocus", range_um=range_um, timeout=FOCUS_TIMEOUT_S)
    after = client.request("get_position")["z"]
    return {"focused": True, "z_before_um": before, "z_after_um": after}


@guarded_tool
async def look(ctx: RunContext[Microscope], question: str) -> dict[str, Any]:
    """Take one image with the current settings and answer a question about it.

    The answer comes from the eyes, which have seen every image of this session:
    ask them to compare with an earlier image when that is the question.

    Args:
        question: what to find out, e.g. "what do you see?", "is it in focus?",
            "is it sharper than the image before?".
    """
    image = await asyncio.to_thread(snap, ctx.deps.client)
    stats = image_statistics(image)
    ctx.deps.on_image(image, question)
    if not ctx.deps.vision:
        return {
            "statistics": stats,
            "note": "the model in use cannot see images; judge from the numbers",
        }
    # A separate conversation: the image never enters the chat history, which
    # keeps long conversations small; the eyes remember it instead.
    eyes = ctx.deps.eyes
    answer = await eyes.look(image, question, stats, _image_context(ctx.deps))
    return {"answer": answer, "statistics": stats, "images_seen": eyes.frames}


@guarded_tool
async def ask_eyes(ctx: RunContext[Microscope], question: str) -> dict[str, Any]:
    """Ask the eyes about the images already seen in this session, without taking
    a new image: "has the sample moved since the first image?", "which image
    was sharpest?".

    Args:
        question: what to compare or recall across the images seen.
    """
    if not ctx.deps.vision:
        return {"note": "the model in use cannot see images; nothing was looked at"}
    eyes = ctx.deps.eyes
    return {"answer": await eyes.ask(question), "images_seen": eyes.frames}


def _image_context(microscope: Microscope) -> dict[str, Any]:
    """Where the picture was taken, for the eyes' record of it; empty if the read fails."""
    try:
        return microscope.where()
    except (RuntimeError, OSError, ValueError):  # the bridge is gone, or NIS refused
        return {}


@guarded_tool
def plan_acquisition(ctx: RunContext[Microscope], plan: AcquisitionPlan) -> dict[str, Any]:
    """Turn a plan into a useq MDASequence and check it on the microscope, without
    moving. A plan with a grid takes one image to measure the camera field.

    Returns a plan id, a summary to tell the operator before starting it, and
    the useq sequence itself.
    """
    if not plan.positions:  # fix "here" now, so the run images exactly what was checked
        here = ctx.deps.client.request("get_position")
        plan = plan.model_copy(update={"positions": [PositionSpec(**here, name="here")]})
    fov_um = None
    if plan.grid is not None:
        try:
            fov_um = plan.grid.fov_um or ctx.deps.engine.field_of_view()
        except ValueError as exc:
            return refusal(ctx, "invalid", str(exc), FAILURE_ADVICE)
    return keep_plan(ctx, plan.name, plan_to_sequence(plan, fov_um))


@guarded_tool
def plan_useq_sequence(
    ctx: RunContext[Microscope],
    name: str,
    path: str | None = None,
    sequence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Load a classic useq MDASequence made elsewhere and check it, like
    plan_acquisition.

    This is how a sequence from another useq tool (pymmcore-widgets,
    napari-micromanager, a script) runs on this microscope. Positions are NIS
    stage coordinates in um; a sequence without positions is imaged where the
    stage is now. Returns the same as plan_acquisition. A useq v2 sequence
    cannot be read from JSON yet (useq-schema 0.9 does not save its axes), so
    only the classic form works here.

    Args:
        name: short name for the saved files: letters, digits, - and _.
        path: a .json or .yaml file that holds a classic useq MDASequence.
        sequence: the MDASequence itself, as the JSON object useq writes.
    """
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", name):
        raise ModelRetry("name may hold only letters, digits, - and _ (at most 40).")
    if (path is None) == (sequence is None):
        raise ModelRetry("Give either path or sequence, not both.")
    if sequence is not None and "axes" in sequence:
        message = (
            "this is a useq v2 sequence, which useq-schema cannot read back from JSON yet; "
            "save it as a classic MDASequence (stage_positions, channels, z_plan, ...)"
        )
        return refusal(ctx, "invalid", message, FAILURE_ADVICE)
    try:
        loaded = useq.MDASequence.from_file(path) if path else useq.MDASequence(**sequence)
    except (OSError, ValueError) as exc:  # a missing file, or not a valid sequence
        message = f"no useq sequence could be read: {str(exc)[:500]}"
        return refusal(ctx, "invalid", message, FAILURE_ADVICE)
    if not loaded.stage_positions:  # fix "here" now, as plan_acquisition does
        here = ctx.deps.client.request("get_position")
        loaded = loaded.replace(stage_positions=[useq.Position(**here, name="here")])
    return keep_plan(ctx, name, loaded)


def keep_plan(ctx: RunContext[Microscope], name: str, sequence: useq.MDASequence) -> dict:
    """Check a useq sequence event by event and keep it under a new plan id."""
    names = [p.name for p in sequence.stage_positions if p.name]
    repeated = sorted({n for n in names if names.count(n) > 1})
    if repeated:  # the file writers need a different name for each position
        message = f"each position needs its own name; used more than once: {', '.join(repeated)}"
        return refusal(ctx, "invalid", message, FAILURE_ADVICE)
    try:
        events = ctx.deps.engine.check(sequence)
    except ValueError as exc:
        return plan_refusal(ctx, exc)
    plan_id = f"{name}-{len(ctx.deps.plans) + 1}"
    ctx.deps.plans[plan_id] = sequence
    ctx.deps.planned_in[plan_id] = ctx.deps.turn
    return {
        "plan_id": plan_id,
        "images": count_images(events),
        "summary": describe(sequence, events, ctx.deps.client.request("get_position")),
        "useq_sequence": sequence.model_dump(mode="json", exclude_defaults=True),
    }


def plan_refusal(ctx: RunContext[Microscope], exc: ValueError) -> dict:
    """The engine's objection to a plan, with the advice that fits it."""
    message = f"the plan cannot run as written: {exc}"
    if "outside the stage limits" in message:
        return refusal(ctx, "limit", message, LIMIT_ADVICE)
    if "optical configuration" in message:
        known = ctx.deps.client.request("get_optical_configurations")
        return refusal(ctx, "invalid", message, OPTIONS_ADVICE, configured_options=known)
    return refusal(ctx, "invalid", message, FAILURE_ADVICE)


@guarded_tool
async def run_acquisition(ctx: RunContext[Microscope], plan_id: str) -> dict[str, Any]:
    """Run a plan made by plan_acquisition or plan_useq_sequence. The images are
    saved as OME-TIFF (one file, or a folder with one file per position when
    there are several), with the useq sequence next to them as .useq.json.

    Args:
        plan_id: the id the planning tool returned.
    """
    sequence = ctx.deps.plans.get(plan_id)
    if sequence is None:
        return refusal(
            ctx,
            "invalid",
            f"there is no plan with id {plan_id!r}",
            OPTIONS_ADVICE,
            configured_options=list(ctx.deps.plans),
        )
    try:  # the microscope, or the limits, may have changed since planning
        events = ctx.deps.engine.check(sequence)
    except ValueError as exc:
        return plan_refusal(ctx, exc)
    # The run goes ahead only in the turn right after the plan (or this question)
    # was shown, so that the operator's reply to it is the go-ahead. A plan from
    # earlier in the conversation is asked about again.
    if ctx.deps.planned_in[plan_id] != ctx.deps.turn - 1:
        ctx.deps.planned_in[plan_id] = ctx.deps.turn
        here = ctx.deps.client.request("get_position")
        summary = f"start acquisition {plan_id!r}: {describe(sequence, events, here)}"
        return {"status": "needs_go_ahead", "not_done_yet": summary, "advice": START_ADVICE}

    stem = f"{datetime.now():%Y%m%d_%H%M%S}_{plan_id}"
    ctx.deps.output_dir.mkdir(parents=True, exist_ok=True)
    output = ctx.deps.output_dir / f"{stem}.ome.tiff"
    saved = sequence.model_dump_json(exclude_defaults=True, indent=2)
    (ctx.deps.output_dir / f"{stem}.useq.json").write_text(saved, encoding="utf-8")

    # The runner lives on the assistant's thread. Without this, pymmcore-plus
    # would pick Qt signals whenever the chat window is open, which needs qtpy.
    os.environ.setdefault("PYMM_SIGNALS_BACKEND", "psygnal")
    frames = _FrameCounter(ctx.deps.on_image)
    runner = ctx.deps.runner = MDARunner()
    runner.set_engine(ctx.deps.engine)
    if ctx.deps.cancel.is_set():  # Stop was pressed while the run was being prepared
        ctx.deps.runner = None
        return {"status": "cancelled", "advice": CANCELLED_ADVICE}
    started, error = time.perf_counter(), None
    try:
        # The run blocks for as long as the acquisition takes; a thread keeps the
        # assistant's own event loop free, which the vision request below needs.
        await asyncio.to_thread(runner.run, sequence, output=[frames, output])
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        ctx.deps.runner = None
    with contextlib.suppress(Exception):  # the connection may be gone after an error
        ctx.deps.anchor = ctx.deps.client.request("get_position")
    # With several positions (tiles count too) the writer makes a folder of the
    # same name, with one OME-TIFF per position, instead of one file.
    saved_to = output if output.exists() else ctx.deps.output_dir / stem
    result = {
        "images": frames.count,
        "finished": "failed" if error else str(runner.status.finish_reason),
        "duration_s": round(time.perf_counter() - started, 1),
        "saved_to": str(saved_to),
    }
    if error:
        result["error"] = {"code": "failed", "message": error, "advice": FAILURE_ADVICE}
    if frames.last is not None:
        # The image the operator sees on the right: a few numbers, and a short
        # description from the vision model, so the reply can say what was imaged.
        result["last_image"] = await describe_image(ctx.deps, frames.last, LAST_IMAGE_QUESTION)
    return result


async def describe_image(
    microscope: Microscope, image: np.ndarray, question: str
) -> dict[str, Any]:
    """The measured numbers for an image and, when the model can see, its answer.

    It runs on the assistant's own event loop: the vision model may be the very
    same client as the chat model, and a client must stay on one loop. A failing
    description is reported, not raised, so a finished acquisition is never
    turned into a failure by the describing afterwards.
    """
    stats = image_statistics(image)
    if not microscope.vision:
        return {"statistics": stats, "note": "the model in use cannot see images"}
    try:
        answer = await microscope.eyes.look(image, question, stats, _image_context(microscope))
    except Exception as exc:
        return {"statistics": stats, "vision_error": f"{type(exc).__name__}: {exc}"}
    return {"statistics": stats, "description": answer}


# -- schedules ---------------------------------------------------------------------------


@guarded_tool
def schedule(
    ctx: RunContext[Microscope],
    name: str,
    instruction: str,
    every_seconds: int | None = None,
    in_seconds: int | None = None,
    at: str | None = None,
) -> dict[str, Any]:
    """Have an instruction carried out later, as if the operator typed it then:
    every_seconds repeats it, in_seconds does it once after a delay, at does it
    once at a clock time. Exactly one of the three is given. Returns the
    schedule as set and every schedule now in place.

    Args:
        name: a short name, to cancel it by.
        instruction: what to do then, in the operator's words: "look and tell me
            whether anything changed".
        every_seconds: repeat this often; every three minutes is 180.
        in_seconds: once, this long from now; in ten minutes is 600.
        at: once, at this clock time, 24-hour "HH:MM".
    """
    try:
        added = ctx.deps.scheduler.add(name, instruction, every_seconds, in_seconds, at)
    except ValueError as exc:
        return refusal(ctx, "invalid", str(exc), FAILURE_ADVICE)
    return {"scheduled": added, "schedules": ctx.deps.scheduler.listing()}


@guarded_tool
def cancel_schedule(ctx: RunContext[Microscope], name: str) -> dict[str, Any]:
    """Cancel a schedule by its name, or every one with "all".

    Args:
        name: the schedule's name, or "all".
    """
    cancelled = ctx.deps.scheduler.cancel(name)
    if not cancelled:
        names = [item["name"] for item in ctx.deps.scheduler.listing()]
        message = f"no schedule named {name!r}"
        return refusal(ctx, "invalid", message, OPTIONS_ADVICE, configured_options=names)
    return {"cancelled": cancelled, "schedules": ctx.deps.scheduler.listing()}


@guarded_tool
def search_source(ctx: RunContext[Microscope], text: str) -> dict[str, Any]:
    """Search the source code of the three parts and of useq-schema (v2 included)
    for a word or phrase, to explain how something works.

    Returns matching lines as "file:line: text". When nothing matches, returns
    the list of files that can be read instead.

    Args:
        text: the word or phrase to find, for example "def setup_event" or
            "grid_plan"; upper and lower case do not matter.
    """
    files = source_files()
    matches = [
        f"{name}:{number}: {line.strip()[:160]}"
        for name, path in files.items()
        for number, line in enumerate(_lines(path), start=1)
        if text.lower() in line.lower()
    ]
    if not matches:
        return {"matches": [], "files": list(files)}
    return {"matches": matches[:SOURCE_MATCHES], "more": max(0, len(matches) - SOURCE_MATCHES)}


@guarded_tool
def read_source(
    ctx: RunContext[Microscope], file: str, start_line: int = 1, lines: int = 80
) -> dict[str, Any]:
    """Read part of a source file of the three parts or of useq-schema, with line numbers.

    Args:
        file: a file as search_source names it, for example "nis_engine/engine.py"
            or "useq/v2/_mda_sequence.py".
        start_line: the first line to read, counting from 1.
        lines: how many lines to read, at most 200.
    """
    files = source_files()
    if file not in files:
        message = f"{file!r} is not a source file here"
        return refusal(ctx, "not_found", message, OPTIONS_ADVICE, configured_options=list(files))
    text = _lines(files[file])
    start = max(1, start_line)
    chunk = text[start - 1 : start - 1 + max(1, min(lines, SOURCE_LINES))]
    return {
        "file": file,
        "lines": f"{start} to {start + len(chunk) - 1} of {len(text)}",
        "text": "\n".join(f"{start + i}: {line}" for i, line in enumerate(chunk)),
    }


def source_files() -> dict[str, Path]:
    """The files the assistant may read, by name: "nis_engine/engine.py", "useq/v2/..."."""
    return {
        f"{label}/{path.relative_to(root).as_posix()}": path
        for label, root in SOURCE_ROOTS.items()
        for path in sorted(root.rglob("*.py"))
    }


def _lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


class _FrameCounter:
    """A pymmcore-plus output handler: counts frames and shows each in the window."""

    def __init__(self, on_image: Callable[[np.ndarray, str], None]) -> None:
        self.on_image, self.count = on_image, 0
        self.last: np.ndarray | None = None  # the image left on the window when the run ends

    def frameReady(self, image: np.ndarray, event: useq.MDAEvent, meta: dict) -> None:
        self.count += 1
        self.last = image
        index = ", ".join(f"{getattr(k, 'value', k)}={v}" for k, v in event.index.items())
        self.on_image(image, f"frame {self.count} ({index})")


TOOLS = (
    check_setup,
    get_status,
    move_stage,
    set_microscope,
    focus,
    look,
    ask_eyes,
    plan_acquisition,
    plan_useq_sequence,
    run_acquisition,
    schedule,
    cancel_schedule,
    search_source,
    read_source,
)


# -- guards on the reply ----------------------------------------------------------------


def hand_back_an_empty_reply(ctx: RunContext[Microscope], output: str) -> str:
    """A reply with no letter or digit goes back to the model once.

    A second empty reply reaches the operator as a plain sentence rather than as,
    say, an underscore.
    """
    asked = ctx.deps.__dict__.setdefault("_empty_asked", set())
    if re.search(r"[^\W_]", output or ""):
        asked.discard(ctx.run_id)
        return output
    if ctx.run_id in asked:
        asked.discard(ctx.run_id)
        return EMPTY_REPLY_FALLBACK
    asked.add(ctx.run_id)
    raise ModelRetry(EMPTY_REPLY_CHALLENGE)


GUARD_WORD = re.compile(r"^\s*SAME\b[\s.:!-]*")  # the one word CALLED_NOTHING_CHALLENGE asks for


def challenge_a_reply_that_called_nothing(ctx: RunContext[Microscope], output: str) -> str:
    """A small model answers "stop" with "I have stopped the microscope." and no call.

    The one thing known without reading the reply is that the turn called nothing,
    so such a reply goes back to the model once with that fact. If it then calls
    a tool, the turn goes on and its new reply reports what happened. If it does
    not, the operator gets the first reply word for word: asked to repeat itself
    a small model writes something shorter and worse, so it is asked for one word
    instead. Costs one short request on a turn that sends no command. Off unless
    the microscope's ``challenge_no_tool`` is set (the window sets it).
    """
    if not ctx.deps.challenge_no_tool or ctx.deps.cancel.is_set():
        return output
    first = ctx.deps.__dict__.setdefault("_first_reply", {})
    starts = [i for i, m in enumerate(ctx.messages) if _is_operator_turn(m)]
    turn = ctx.messages[starts[-1] :] if starts else ctx.messages
    called = any(isinstance(part, ToolCallPart) for m in turn for part in getattr(m, "parts", []))
    if not called and ctx.run_id in first:
        return first.pop(ctx.run_id)  # challenged, and still nothing called: as it was
    first.pop(ctx.run_id, None)
    # "SAME" and the challenge are for this guard, never for the operator: a reply
    # that opens with them, or holds nothing else, is asked for again.
    reply = GUARD_WORD.sub("", output, count=1).strip()
    if not reply or CALLED_NOTHING_CHALLENGE[:40] in reply:
        raise ModelRetry(EMPTY_REPLY_CHALLENGE)
    if called:
        return reply
    first[ctx.run_id] = reply
    raise ModelRetry(CALLED_NOTHING_CHALLENGE)


REPLY_GUARDS = (hand_back_an_empty_reply, challenge_a_reply_that_called_nothing)
