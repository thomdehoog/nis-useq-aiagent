"""Step 0 on NIS-Elements 6.10: what NIS-Elements lets our Python do, measured on the simulator.

Runs INSIDE NIS-Elements, started by step0.mac (Macro > Run Macro From File). Every NIS
function is called through nis.call_proc: NIS's own way of calling a macro function by name,
as a macro does. Nothing is called through a DLL. It answers:

  1. What NIS's Python offers on 6.10 (the nis module: call_proc; is nis.mac there?).
  2. How nis.call_proc takes values that a function hands back (numbers and texts), and
     what it does with a name that does not exist.
  3. How many functions NIS's own function list has, by section, and whether every function
     the bridge calls is in it. The list is NOT part of this folder (it is Nikon's): the test
     reads it on the NIS computer, from a FunctionList*.html next to this file or in the NIS
     folder.
  4. What every reading the bridge does returns, and how long a call takes.
  5. Every write the bridge does (on by default, for the simulator): each one confirmed and
     put back.
  6. Whether every function in NIS's list can be reached through nis.call_proc, without
     running it (runs right after 3). One line per function in functions_reachable.csv
     (stays on the NIS computer, like the list).

Every result goes to step0_report.json and step0_summary.txt in OUT_DIR. Before each call
the log names it, so if NIS hangs, the last line of step0.log says which call it was.

Standard library and NIS's own `nis` module only.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-26
License: MIT
"""

import csv
import glob
import html
import json
import os
import platform
import re
import sys
import time
import traceback

# -- settings: edit before a run ----------------------------------------------------------
HERE = os.environ.get("STEP0_HERE", r"C:\nikon-step0-610")  # where this folder was copied to
OUT_DIR = os.path.join(HERE, "results")
NIS_DIR = r"C:\Program Files\NIS-Elements"  # searched for FunctionList*.html

# The writes are on: this run is meant for the Ti2 simulator. On a real microscope, set
# them to False and switch them on one at a time, with someone at the microscope.
ALLOW_STAGE = True  # XY, Z and XYZ by STAGE_STEP_UM / Z_STEP_UM and back
ALLOW_OPTICAL_CONFIGURATION = True  # select another optical configuration, then the first again
ALLOW_EXPOSURE = True  # Camera_ExposureSet to EXPOSURE_MS
ALLOW_NOSEPIECE = True  # another objective, then the first again
ALLOW_PFS = True  # Perfect Focus on and off again, if there is one
ALLOW_AUTOFOCUS = True  # StgFocusInRangeEx over AUTOFOCUS_RANGE_UM, then Z put back
ALLOW_CAPTURE = True  # capture one image, save it as TIFF in OUT_DIR, close it
ALLOW_CAMERA_READ = False  # Camera_ExposureGet: on the 6.10 simulator it opened a blocking dialog

STAGE_STEP_UM = 10.0
Z_STEP_UM = 1.0
EXPOSURE_MS = 50.0
AUTOFOCUS_RANGE_UM = 20.0
AUTOFOCUS_SPEED = 30
PFS_WAIT_S = 5.0  # how long to wait for Perfect Focus to report the new status
TIMING_REPEATS = 20
TEXT_LENGTH = 256  # room for a text a function hands back

# The bridge's own constants (1_nis_bridge/nis_bridge/settings.py)
INFOSTR_VERSION = 1
TIFF_ALL_LAYERS = 18
CLOSE_WITHOUT_ASKING = 2

# -- NIS's own codes ------------------------------------------------------------------------
DR_CODES = {
    1: "DR_OK", 2: "DR_PARTIALLYOK", 0: "DR_CANCELED", -1: "DR_UNKNOWNERROR",
    -2: "DR_BADPARAMETER", -3: "DR_NOTSUPPORTED", -4: "DR_NOTAVAILABLE",
    -5: "DR_NOTAUTOMATIC", -6: "DR_NOTCALIBRATED", -7: "DR_NOTINITIALIZED",
}

# Every NIS function the bridge calls (1_nis_bridge/nis_bridge/nis_dll.py), in its order.
BRIDGE_FUNCTIONS = [
    "Get_InfoStr", "StgGetPos", "StgXY_GetLimits", "StgZ_GetLimits", "StgMove", "StgMoveXY",
    "StgMoveZ", "GetOptConfCount", "GetOptConfName", "SelectOptConf", "Camera_ExposureSet",
    "Stg_IsNosepiecePresent", "Stg_GetNosepiecePositions", "Stg_GetNosepiecePosition",
    "Stg_GetNosepieceObjectiveName", "Stg_SetNosepiecePosition", "Stg_IsPFSPresent",
    "Stg_GetPFSStatus", "Stg_SetPFSStatus", "Stg_WaitForPFS", "StgFocusInRangeEx", "Capture",
    "Get_Calibration", "ImageSaveAs", "CloseCurrentDocument",
]

report = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "settings": {
    name: value for name, value in globals().items() if name.startswith("ALLOW_")}, "checks": []}
os.makedirs(OUT_DIR, exist_ok=True)
log_file = open(os.path.join(OUT_DIR, "step0.log"), "a", encoding="utf-8")


def log(text):
    line = f"{time.strftime('%H:%M:%S')} {text}"
    log_file.write(line + "\n")
    log_file.flush()
    print(line)


def check(name, function, *, group):
    """Run one check; record its answer or its error, and how long it took."""
    log(f"START {group} / {name}")
    started = time.perf_counter()
    entry = {"group": group, "name": name}
    try:
        entry["answer"] = function()
        entry["ok"] = True
    except KeyboardInterrupt:
        raise
    except BaseException as error:  # noqa: BLE001 - every failure is a finding, even SystemExit
        entry["ok"] = False
        entry["error"] = f"{type(error).__name__}: {error}"
        entry["traceback"] = traceback.format_exc(limit=3)
    entry["seconds"] = round(time.perf_counter() - started, 4)
    log(f"END   {group} / {name}: {'ok' if entry['ok'] else entry['error']} ({entry['seconds']} s)")
    report["checks"].append(entry)
    save()
    return entry


def save():
    with open(os.path.join(OUT_DIR, "step0_report.json"), "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1, default=repr)


def dr(value):
    """A return value the manual documents as a DR code, with its meaning beside it."""
    return f"{value} ({DR_CODES.get(value, 'not a DR code')})" if isinstance(value, int) else value


# -- 1. the environment ---------------------------------------------------------------------
try:
    import nis  # exists only inside NIS-Elements
except ImportError:
    nis = None

log(f"running {os.path.abspath(__file__)}, results in {OUT_DIR}")
check("python", lambda: {"version": sys.version, "executable": sys.executable,
                         "platform": platform.platform(), "script": os.path.abspath(__file__)},
      group="environment")
check("nis module", lambda: {"present": nis is not None,
                             "names": sorted(n for n in dir(nis) if not n.startswith("__")) if nis else [],
                             "call_proc": nis is not None and hasattr(nis, "call_proc"),
                             "mac": nis is not None and hasattr(nis, "mac")},
      group="environment")

# -- 2. how nis.call_proc takes values back ---------------------------------------------------
# nis.call_proc(name, *args) answers with a list: the return value, then each argument as it
# is after the call. The first run showed that an argument the function writes into wants a
# count (int) or a sequence, not a plain number. Both forms are tried, for a number and for a
# text, on readings only; the form that works is used for the rest of the run.
FORMS = {"number": None, "text": None}


def raw(name, *args):
    return nis.call_proc(name, *args)


def unknown_name():
    """Control: what does nis.call_proc do with a name that does not exist?"""
    try:
        return {"raises": False, "answer": repr(raw("ThisFunctionDoesNotExist_Step0"))}
    except Exception as error:  # noqa: BLE001
        return {"raises": True, "error": f"{type(error).__name__}: {error}"}


def try_forms(name, kinds, build, good):
    """Call name once per form; keep the first form whose answer passes good()."""
    answer = {}
    for form, args in build.items():
        try:
            out = raw(name, *args)
            answer[form] = {"raw": repr(out), "good": bool(good(out))}
            if answer[form]["good"] and FORMS[kinds] is None:
                FORMS[kinds] = form
        except Exception as error:  # noqa: BLE001 - the other forms may still work
            answer[form] = {"error": f"{type(error).__name__}: {error}"}
    answer["chosen"] = FORMS[kinds]
    return answer


def number_forms():
    """StgGetPosXY(double *x, double *y): two numbers handed back."""
    def good(out):
        return isinstance(out, (list, tuple)) and len(out) == 3 and all(
            isinstance(value(v), (int, float)) for v in out[1:])
    return try_forms("StgGetPosXY", "number", {"count": (1, 1), "sequence": ([0.0], [0.0])}, good)


def text_forms():
    """Get_InfoStr(int what, char *text): a text handed back (the NIS version)."""
    def good(out):
        return isinstance(out, (list, tuple)) and len(out) == 3 and "6." in str(value(out[2]))
    return try_forms("Get_InfoStr", "text", {
        "count": (INFOSTR_VERSION, TEXT_LENGTH),
        "sequence": (INFOSTR_VERSION, [""] * TEXT_LENGTH),
        "string": (INFOSTR_VERSION, " " * TEXT_LENGTH)}, good)


def value(item):
    """One handed-back argument as plain Python: a number, or a text."""
    if isinstance(item, (bytes, bytearray)):
        return bytes(item).split(b"\0")[0].decode("utf-8", "replace")
    if isinstance(item, (list, tuple)):
        if len(item) == 1:
            return value(item[0])
        if all(isinstance(c, str) and len(c) <= 1 for c in item):
            return "".join(item).split("\0")[0]
        return [value(i) for i in item]
    if isinstance(item, str):
        return item.split("\0")[0].rstrip()
    return item


def N():
    """An argument the function writes a number into, in the form that worked."""
    return 1 if FORMS["number"] != "sequence" else [0.0]


def T():
    """An argument the function writes a text into, in the form that worked."""
    return {"sequence": [""] * TEXT_LENGTH, "string": " " * TEXT_LENGTH}.get(FORMS["text"],
                                                                           TEXT_LENGTH)


def call(name, *args):
    """Call a NIS function; hand back its return value and every argument after the call."""
    out = raw(name, *args)
    out = list(out) if isinstance(out, (list, tuple)) else [out]
    return out[0], [value(v) for v in out[1:]]


if nis is not None and hasattr(nis, "call_proc"):
    check("unknown name (control)", unknown_name, group="call_proc")


# -- 3. NIS's own function list: how many, by section (nothing is called) -----------------
def function_list_file():
    candidates = sorted(glob.glob(os.path.join(HERE, "FunctionList*.htm*")))
    candidates += sorted(glob.glob(os.path.join(NIS_DIR, "**", "FunctionList*.htm*"), recursive=True))
    return candidates[0] if candidates else None


def names_in_function_list(path):
    """Function names from NIS's HTML list, with their section and whether AR includes them.

    The list has one <h2> per section and one row per function, with the name in
    <td title="..."> and one column per edition (D, BR, AR): a circle means included, a module
    name means included with that module, empty means not in that edition.
    """
    with open(path, encoding="latin-1") as handle:
        text = handle.read()
    parts = re.split(r"<h2>(.*?)</h2>", text)
    functions = {}
    for index in range(1, len(parts), 2):
        section = html.unescape(parts[index]).strip()
        for row in re.findall(r"<tr>(.*?)</tr>", parts[index + 1], re.S):
            name = re.search(r'<td title="([^"]+)"', row)
            if not name:
                continue
            cells = [re.sub(r"\s+", "", html.unescape(re.sub(r"<[^>]+>", "", cell)))
                     for cell in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
            ar = cells[3] if len(cells) > 3 else ""
            edition = "yes" if ar == "\u25cb" else (f"module {ar}" if ar else "no")
            functions.setdefault(html.unescape(name.group(1)).strip(), (section, edition))
    return functions


def function_list():
    path = function_list_file()
    if path is None:
        return {"skipped": f"no FunctionList*.html next to this file or under {NIS_DIR}"}
    functions = names_in_function_list(path)
    by_section = {}
    for section, edition in functions.values():
        counts = by_section.setdefault(section, {"all": 0, "AR": 0, "AR with module": 0})
        counts["all"] += 1
        if edition == "yes":
            counts["AR"] += 1
        elif edition.startswith("module"):
            counts["AR with module"] += 1
    return {"file": path, "functions": len(functions),
            "AR": sum(c["AR"] for c in by_section.values()),
            "AR with module": sum(c["AR with module"] for c in by_section.values()),
            "by_section": by_section,
            "bridge functions missing from the list": [
                n for n in BRIDGE_FUNCTIONS if n not in functions]}


check("NIS's function list", function_list, group="function list")

# -- 6. can every function in NIS's list be reached? (nothing is run) -----------------------
# 6.10 has no nis.mac to look a name up without calling it. So each name is called with one
# argument that no NIS function can take: if nis.call_proc refuses the argument, it found the
# function and ran nothing; if it answers as for a name that does not exist ("Procedure not
# found"), NIS does not have it. Three control calls first show that such a call runs nothing;
# if one fails, no name is swept. Early in the run: the second run (2026-10-26) showed that
# numbers handed back open a blocking dialog, and NIS crashed after GetOptConfName.
class NotAValue:
    """An argument no NIS function can take."""


def refused(name):
    """nis.call_proc(name, NotAValue()): the error, with the name taken out; None if it ran."""
    try:
        raw(name, NotAValue())
        return None
    except Exception as error:  # noqa: BLE001 - the error is the answer
        return f"{type(error).__name__}: {error}".replace(name, "<name>")


def reach_controls():
    unknown = refused("ThisFunctionDoesNotExist_Step0")
    no_arguments = refused("GetOptConfCount")  # takes no argument: is the extra one refused?
    # Z cannot be read back through call_proc on 6.10 (a number handed back fails), so the
    # objective is the write that must not happen: its position comes back as the return value.
    before = call("Stg_GetNosepiecePosition")[0]
    with_arguments = refused("Stg_SetNosepiecePosition")  # takes (int): refused, and it stays?
    after = call("Stg_GetNosepiecePosition")[0]
    answer = {"unknown name": unknown, "GetOptConfCount": no_arguments,
              "Stg_SetNosepiecePosition": with_arguments, "objective_before": before,
              "objective_after": after}
    problems = []
    if unknown is None:
        problems.append("an unknown name raised nothing")
    for name, error in (("GetOptConfCount", no_arguments),
                        ("Stg_SetNosepiecePosition", with_arguments)):
        if error is None:
            problems.append(f"{name} ran with an argument it cannot take")
        elif error == unknown:
            problems.append(f"{name} answered like an unknown name")
    if after != before:
        problems.append("the objective changed")
    answer["safe to sweep"] = not problems
    answer["problems"] = problems
    return answer


def reach_all():
    """Every name in NIS's list: reached (refused the argument), not there, or it ran."""
    controls = report["checks"][-1]
    if not controls["ok"] or not controls["answer"]["safe to sweep"]:
        return {"skipped": "the control calls did not show the sweep is safe"}
    path = function_list_file()
    if path is None:
        return {"skipped": f"no FunctionList*.html next to this file or under {NIS_DIR}"}
    unknown = controls["answer"]["unknown name"]
    rows, counts = [], {}
    for name, (section, edition) in sorted(names_in_function_list(path).items()):
        log(f"reach {name}")
        error = refused(name)
        reached = "ran" if error is None else ("no" if error == unknown else "yes")
        rows.append((name, section, edition, reached, error or ""))
        key = "AR" if edition == "yes" else ("AR with module" if edition.startswith("module")
                                              else "not in AR")
        counts.setdefault(key, {"yes": 0, "no": 0, "ran": 0})[reached] += 1
    with open(os.path.join(OUT_DIR, "functions_reachable.csv"), "w", newline="",
              encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("function", "section", "in AR", "reached", "call_proc said"))
        writer.writerows(rows)
    # ponytail: one example error per kind is enough to read the run; the csv has them all
    return {"functions": len(rows), "reached": sum(r[3] == "yes" for r in rows),
            "by edition": counts, "ran (should be none)": [r[0] for r in rows if r[3] == "ran"],
            "kinds of refusal": sorted({r[4] for r in rows if r[3] == "yes"})[:20]}


if nis is not None and hasattr(nis, "call_proc"):
    check("controls: a refused call runs nothing", reach_controls, group="reach")
    check("every function in NIS's list", reach_all, group="reach")


if nis is not None and hasattr(nis, "call_proc"):
    check("numbers handed back", number_forms, group="call_proc")
    check("texts handed back", text_forms, group="call_proc")


# -- 4. every reading the bridge does ---------------------------------------------------------
def version():
    result, after = call("Get_InfoStr", INFOSTR_VERSION, T())
    return {"return": result, "version": after[1]}


def stage_position():
    result, after = call("StgGetPos", N(), N(), N())
    return {"return": dr(result), "x": after[0], "y": after[1], "z": after[2]}


def xy_position():
    result, after = call("StgGetPosXY", N(), N())
    return {"return": dr(result), "x": after[0], "y": after[1]}


def z_position():
    result, after = call("StgGetPosZ", N(), 0)
    return {"return": dr(result), "z": after[0]}


def limits():
    xy, a = call("StgXY_GetLimits", N(), N(), N(), N())
    z, b = call("StgZ_GetLimits", N(), N())
    return {"StgXY_GetLimits": dr(xy), "x": [a[0], a[2]], "y": [a[1], a[3]],
            "StgZ_GetLimits": dr(z), "z": [b[0], b[1]]}


def optical_configurations():
    count, _ = call("GetOptConfCount")
    names = []
    for index in range(max(count, 0)):
        _, after = call("GetOptConfName", index, T(), TEXT_LENGTH)
        names.append(after[1])
    return {"GetOptConfCount": count, "names": names}


def selected_optical_configuration():
    """GetSelectedOptConf hands back three texts; which one holds the name is what we learn."""
    result, after = call("GetSelectedOptConf", T(), T(), T(), TEXT_LENGTH)
    return {"return": result, "texts": after[:3]}


def nosepiece():
    answer = {name: call(name)[0] for name in (
        "Stg_IsNosepiecePresent", "Stg_GetNosepiecePositions", "Stg_GetNosepiecePosition")}
    names = {}
    for position in range(1, max(answer["Stg_GetNosepiecePositions"], 0) + 1):
        result, after = call("Stg_GetNosepieceObjectiveName", position, T(), TEXT_LENGTH)
        names[position] = {"return": dr(result), "name": after[1]}
    answer["objectives"] = names
    return answer


def pfs():
    return {"Stg_IsPFSPresent": call("Stg_IsPFSPresent")[0],
            "Stg_GetPFSStatus": call("Stg_GetPFSStatus")[0]}


def pfs_on():
    return bool(call("Stg_IsPFSPresent")[0]) and call("Stg_GetPFSStatus")[0] in (1, 5, 6)


def calibration():
    result, after = call("Get_Calibration", T(), N(), N(), N())
    return {"return": result, "name": after[0], "um_per_px": after[1], "aspect": after[2],
            "unit": after[3]}


def reading(name, build):
    check(name, build, group="readings")


reading("Get_InfoStr", version)
reading("StgGetPos", stage_position)
reading("StgGetPosXY", xy_position)
reading("StgGetPosZ", z_position)
reading("limits", limits)
reading("optical configurations", optical_configurations)
reading("GetSelectedOptConf", selected_optical_configuration)
reading("nosepiece", nosepiece)
reading("Perfect Focus", pfs)
reading("Get_Calibration (no image open)", calibration)
if ALLOW_CAMERA_READ:
    reading("Camera_ExposureGet", lambda: dict(zip(("return", "after"), call("Camera_ExposureGet", N()))))


def timing():
    """StgGetPosXY TIMING_REPEATS times through nis.call_proc."""
    times = []
    for _ in range(TIMING_REPEATS):
        started = time.perf_counter()
        call("StgGetPosXY", N(), N())
        times.append(time.perf_counter() - started)
    times.sort()
    return {"median_ms": round(1000 * times[len(times) // 2], 3),
            "max_ms": round(1000 * times[-1], 3)}


check("StgGetPosXY timing", timing, group="timing")


# -- 5. writes, each confirmed and put back --------------------------------------------------
def stage_round_trip():
    start = stage_position()
    lim = limits()
    low, high = min(lim["x"]), max(lim["x"])
    if start["x"] + STAGE_STEP_UM <= high:
        target = start["x"] + STAGE_STEP_UM
    elif start["x"] - STAGE_STEP_UM >= low:
        target = start["x"] - STAGE_STEP_UM
    else:
        return {"skipped": f"no room for {STAGE_STEP_UM} um within the X limits {low}..{high}"}
    steps = {"start": start, "limits_x": [low, high]}
    started = time.perf_counter()
    steps["StgMoveXY"] = dr(call("StgMoveXY", target, start["y"], 0)[0])
    steps["move_s"] = round(time.perf_counter() - started, 3)
    steps["read_after_move"] = stage_position()
    steps["StgMoveXY back"] = dr(call("StgMoveXY", start["x"], start["y"], 0)[0])
    steps["read_after_back"] = stage_position()
    return steps


def z_round_trip():
    if pfs_on():
        return {"skipped": "Perfect Focus is on; a Z move would fight it"}
    start = z_position()["z"]
    steps = {"start": start, "StgMoveZ": dr(call("StgMoveZ", start + Z_STEP_UM, 0)[0])}
    steps["read_after_move"] = z_position()["z"]
    steps["StgMoveZ back"] = dr(call("StgMoveZ", start, 0)[0])
    steps["read_after_back"] = z_position()["z"]
    return steps


def xyz_round_trip():
    """StgMove: the bridge's move of all three axes at once."""
    if pfs_on():
        return {"skipped": "Perfect Focus is on; a Z move would fight it"}
    start = stage_position()
    step = STAGE_STEP_UM if start["x"] + STAGE_STEP_UM <= max(limits()["x"]) else -STAGE_STEP_UM
    steps = {"start": start, "StgMove": dr(
        call("StgMove", start["x"] + step, start["y"], start["z"] + Z_STEP_UM, 0)[0])}
    steps["read_after_move"] = stage_position()
    steps["StgMove back"] = dr(call("StgMove", start["x"], start["y"], start["z"], 0)[0])
    steps["read_after_back"] = stage_position()
    return steps


def optical_configuration_round_trip():
    names = optical_configurations()["names"]
    if len(names) < 2:
        return {"skipped": "fewer than two optical configurations"}
    first, other = names[0], names[1]
    steps = {"before": selected_optical_configuration()["texts"]}
    steps["SelectOptConf other"] = call("SelectOptConf", other)[0]
    steps["read_after_select"] = selected_optical_configuration()["texts"]
    steps["SelectOptConf first"] = call("SelectOptConf", first)[0]
    steps["read_after_first"] = selected_optical_configuration()["texts"]
    steps["selected"] = [other, first]
    return steps


def exposure():
    result, after = call("Camera_ExposureSet", float(EXPOSURE_MS))
    return {"return": result, "after": after}


def nosepiece_round_trip():
    if not call("Stg_IsNosepiecePresent")[0]:
        return {"skipped": "no nosepiece"}
    count = call("Stg_GetNosepiecePositions")[0]
    start = call("Stg_GetNosepiecePosition")[0]
    if count < 2 or start < 1:
        return {"skipped": f"positions {count}, current {start}"}
    other = start % count + 1
    steps = {"start": start,
             "Stg_SetNosepiecePosition": dr(call("Stg_SetNosepiecePosition", other)[0])}
    steps["read_after_move"] = call("Stg_GetNosepiecePosition")[0]
    steps["Stg_SetNosepiecePosition back"] = dr(call("Stg_SetNosepiecePosition", start)[0])
    steps["read_after_back"] = call("Stg_GetNosepiecePosition")[0]
    return steps


def autofocus():
    if pfs_on():
        return {"skipped": "Perfect Focus is on"}
    start = z_position()["z"]
    steps = {"start": start, "StgFocusInRangeEx": call(
        "StgFocusInRangeEx", AUTOFOCUS_RANGE_UM, float(AUTOFOCUS_SPEED))[0]}
    steps["z_after"] = z_position()["z"]
    steps["StgMoveZ back"] = dr(call("StgMoveZ", start, 0)[0])
    steps["read_after_back"] = z_position()["z"]
    return steps


def pfs_round_trip():
    if not call("Stg_IsPFSPresent")[0]:
        return {"skipped": "no Perfect Focus"}
    start = call("Stg_GetPFSStatus")[0]
    on = start in (1, 5, 6)

    def settle(want_on):
        """Poll the status until it says on (or off), up to PFS_WAIT_S; the first run read 1
        (on) straight after switching off, so the status may lag behind the switch."""
        started = time.perf_counter()
        while True:
            status = call("Stg_GetPFSStatus")[0]
            if (status in (1, 5, 6)) == want_on or time.perf_counter() - started > PFS_WAIT_S:
                return {"status": status, "after_s": round(time.perf_counter() - started, 3)}
            time.sleep(0.1)

    steps = {"start": start, "Stg_SetPFSStatus": call("Stg_SetPFSStatus", 0 if on else 1)[0]}
    steps["Stg_WaitForPFS"] = call("Stg_WaitForPFS", PFS_WAIT_S)[0]
    steps["read_after_set"] = settle(not on)
    steps["Stg_SetPFSStatus back"] = call("Stg_SetPFSStatus", 1 if on else 0)[0]
    steps["read_after_back"] = settle(on)
    steps["put_back"] = (steps["read_after_back"]["status"] in (1, 5, 6)) == on
    return steps


def capture_save_close():
    path = os.path.join(OUT_DIR, "step0_capture.tif")
    if os.path.exists(path):
        os.remove(path)
    steps = {"Capture": dr(call("Capture")[0])}
    steps["Get_Calibration"] = calibration()
    steps["ImageSaveAs"] = call("ImageSaveAs", path, TIFF_ALL_LAYERS, 0)[0]
    steps["saved_file"] = os.path.exists(path)
    steps["bytes"] = os.path.getsize(path) if steps["saved_file"] else 0
    steps["CloseCurrentDocument"] = call("CloseCurrentDocument", CLOSE_WITHOUT_ASKING)[0]
    return steps


if ALLOW_STAGE:
    check("XY move and back", stage_round_trip, group="writes")
    check("Z move and back", z_round_trip, group="writes")
    check("XYZ move and back", xyz_round_trip, group="writes")
if ALLOW_OPTICAL_CONFIGURATION:
    check("optical configuration and back", optical_configuration_round_trip, group="writes")
if ALLOW_EXPOSURE:
    check("Camera_ExposureSet", exposure, group="writes")
if ALLOW_NOSEPIECE:
    check("objective and back", nosepiece_round_trip, group="writes")
if ALLOW_AUTOFOCUS:
    check("autofocus, then Z back", autofocus, group="writes")
if ALLOW_PFS:
    check("Perfect Focus and back", pfs_round_trip, group="writes")
if ALLOW_CAPTURE:
    check("capture, save, close", capture_save_close, group="writes")



# -- the summary ----------------------------------------------------------------------------
report["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
save()
with open(os.path.join(OUT_DIR, "step0_summary.txt"), "w", encoding="utf-8") as handle:
    for entry in report["checks"]:
        state = "ok  " if entry["ok"] else "FAIL"
        answer = entry.get("answer", entry.get("error"))
        text = json.dumps(answer, default=repr)
        if len(text) > 300:
            text = text[:300] + " ..."
        handle.write(f"{state} {entry['group']:<12} {entry['name']:<40} {entry['seconds']:>8} s  {text}\n")
log(f"done: {sum(e['ok'] for e in report['checks'])} of {len(report['checks'])} checks ok; see {OUT_DIR}")
log_file.close()
