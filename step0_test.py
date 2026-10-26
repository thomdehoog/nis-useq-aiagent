"""Step 0 on NIS-Elements 6.10: what NIS-Elements lets our Python do, measured on the simulator.

Runs INSIDE NIS-Elements, started by step0.mac (Macro > Run Macro From File). Every NIS
function is called through nis.call_proc: NIS's own way of calling a macro function by name,
as a macro does. Nothing is called through a DLL. Two routes:

  - direct: nis.call_proc(name, *args), for functions that only take values in.
  - macro: for functions that hand values back through an argument (double *, int *, a text
    with a max length). Through call_proc directly these fail with a blocking dialog
    (numbers) or corrupt NIS's heap and kill it a few calls later (texts with a max length;
    2026-10-26). So Python writes a few lines of NIS macro, runs them with RunMacro, and reads
    the numbers back with GetVariableValue and a text from a file the macro wrote.

It answers:

  1. What NIS's Python offers on 6.10 (the nis module: call_proc; is nis.mac there?).
  2. What nis.call_proc does with a name that does not exist, and whether the macro route
     works.
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
  7. For every function in NIS's list: its signature (from NIS's help index), which route
     it needs, and whether this run called it and how that went: functions_calls.csv (stays
     on the NIS computer, like the list).

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
NIS_DIR = r"C:\Program Files\NIS-Elements"  # searched for FunctionList*.html and lunr_fr.js

# The writes are on: this run is meant for the Ti2 simulator. On a real microscope, set
# them to False and switch them on one at a time, with someone at the microscope.
ALLOW_STAGE = True  # XY, Z and XYZ by STAGE_STEP_UM / Z_STEP_UM and back
ALLOW_OPTICAL_CONFIGURATION = True  # select another optical configuration, then the first again
ALLOW_EXPOSURE = True  # Camera_ExposureSet to EXPOSURE_MS
ALLOW_NOSEPIECE = True  # another objective, then the first again
ALLOW_PFS = True  # Perfect Focus on and off again, if there is one
ALLOW_AUTOFOCUS = True  # StgFocusInRangeEx over AUTOFOCUS_RANGE_UM, then Z put back
ALLOW_CAPTURE = True  # capture one image, save it as TIFF in OUT_DIR, close it
ALLOW_CAMERA_READ = True  # Camera_ExposureGet, through a macro (directly it opened a blocking dialog)
RUN_SWEEP = True  # the reachability sweep: every name in NIS's list, refused, nothing runs

STAGE_STEP_UM = 10.0
Z_STEP_UM = 1.0
EXPOSURE_MS = 50.0
AUTOFOCUS_RANGE_UM = 20.0
AUTOFOCUS_SPEED = 30
PFS_WAIT_S = 5.0  # how long to wait for Perfect Focus to report the new status
TIMING_REPEATS = 20
TEXT_LENGTH = 256  # room for a text a function hands back
NOT_SET = -123456789.0  # a macro's number before the call; still there after it = not written

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

# -- 2. the two routes: direct, and through a macro -------------------------------------------
# nis.call_proc(name, *args) answers with a list: the return value, then each argument as it
# is after the call. What 6.10 does with an argument the function writes into (2026-10-26):
#   double * / int *          "Failed to run procedure" and a blocking dialog
#   char * with a max length  the right text, then heap corruption: NIS dies 1-6 calls later
#   char * without one        works with a count: Get_InfoStr(1, 256) -> [1, 1, '6.10.02 ...']
# So everything a function hands back goes through a macro (macro_call below).
TESTED = {}  # function -> (route, outcome) for every function this run really called
MACRO_FILE = os.path.join(OUT_DIR, "step0_call.mac").replace("\\", "/")
TEXT_FILE = os.path.join(OUT_DIR, "step0_text.bin").replace("\\", "/")
_macro_count = [0]


def raw(name, *args):
    return nis.call_proc(name, *args)


def tested(name, route, outcome):
    TESTED[name] = (route, outcome)


def unknown_name():
    """Control: what does nis.call_proc do with a name that does not exist?"""
    try:
        return {"raises": False, "answer": repr(raw("ThisFunctionDoesNotExist_Step0"))}
    except Exception as error:  # noqa: BLE001
        return {"raises": True, "error": f"{type(error).__name__}: {error}"}


def value(item):
    """One handed-back argument as plain Python: a number, or a text."""
    if isinstance(item, (bytes, bytearray)):
        return bytes(item).split(b"\0")[0].decode("utf-8", "replace")
    if isinstance(item, (list, tuple)):
        if len(item) == 1:
            return value(item[0])
        return [value(i) for i in item]
    if isinstance(item, str):
        return item.split("\0")[0].rstrip()
    return item


def call(name, *args):
    """Direct route: call a NIS function that only takes values in (or Get_InfoStr's text).

    Hands back its return value and every argument after the call."""
    try:
        out = raw(name, *args)
    except Exception as error:
        tested(name, "direct", f"error: {error}")
        raise
    out = list(out) if isinstance(out, (list, tuple)) else [out]
    tested(name, "direct", f"ok, returned {out[0]!r}")
    return out[0], [value(v) for v in out[1:]]


def macro_call(name, arguments, doubles=(), ints=(), texts=()):
    """Macro route: NIS's macro language makes the call; Python only runs the macro.

    arguments is the argument list as macro text, with {name} where a value comes back, e.g.
    macro_call("StgGetPosXY", "{x}, {y}", doubles="xy"). Numbers come back through global
    variables (GetVariableValue), each text through a file the macro writes with WriteFile
    (UTF-16). Hands back (return value, {name: value}).
    """
    _macro_count[0] += 1
    prefix = f"step0_{_macro_count[0]}_"
    globals_ = {n: prefix + n for n in ("r", *doubles, *ints)}
    files = {n: TEXT_FILE.replace(".bin", f"_{n}.bin") for n in texts}
    lines = ["global double " + ", ".join([globals_["r"]] + [globals_[n] for n in doubles]) + ";"]
    if ints:
        lines.append("global int " + ", ".join(globals_[n] for n in ints) + ";")
    lines += [f"char {prefix}{n}[{TEXT_LENGTH}];" for n in texts]  # declarations first
    for n in (*doubles, *ints):
        lines.append(f"{globals_[n]} = {NOT_SET:.1f};" if n in doubles else f"{globals_[n]} = -12345;")
    lines += [f"{prefix}{n}[0] = 0;" for n in texts]
    places = {n: "&" + globals_[n] for n in (*doubles, *ints)}
    places.update({n: prefix + n for n in texts})
    filled = arguments.format(**places)
    lines.append(f"{globals_['r']} = {name}({filled});")
    for n in texts:
        lines.append(f'WriteFile("{files[n]}", {prefix}{n}, 2 * strlen({prefix}{n}));')
        if os.path.exists(files[n]):
            os.remove(files[n])
    with open(MACRO_FILE, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    try:
        ran = raw("RunMacro", MACRO_FILE)
        ran = ran[0] if isinstance(ran, (list, tuple)) else ran
        if ran != 1:
            raise RuntimeError(f"RunMacro returned {ran!r} for {name}({filled})")
        answers = {}
        for n, variable in globals_.items():
            got = raw("GetVariableValue", variable)
            got = got[0] if isinstance(got, (list, tuple)) else got
            if n != "r" and got in (NOT_SET, -12345):
                raise RuntimeError(f"{name} did not write {n}")
            answers[n] = int(got) if n in ints else got
        for n, path in files.items():
            if not os.path.exists(path):  # WriteFile of an empty text may write no file
                answers[n] = ""
                continue
            with open(path, "rb") as handle:
                answers[n] = handle.read().decode("utf-16-le", "replace").split("\0")[0]
            os.remove(path)
    except Exception as error:
        tested(name, "macro", f"error: {error}")
        raise
    finally:
        try:
            raw("DeleteVariables", prefix)
        except Exception:  # noqa: BLE001 - leftover globals do no harm; names are unique
            pass
    result = answers.pop("r")
    result = int(result) if float(result).is_integer() else result
    tested(name, "macro", f"ok, returned {result!r}")
    for helper in ("RunMacro", "GetVariableValue", "DeleteVariables"):  # the route's own calls
        TESTED.setdefault(helper, ("direct", "ok (used by the macro route)"))
    return result, answers


def macro_route():
    """Control: does a macro run from here, and does a global come back?"""
    result, answers = macro_call("strlen", '"step0"')
    if result != 5:
        raise RuntimeError(f"strlen(\"step0\") through a macro gave {result!r}, not 5")
    return {"strlen(\"step0\")": result, "macro file": MACRO_FILE}


if nis is not None and hasattr(nis, "call_proc"):
    check("unknown name (control)", unknown_name, group="call_proc")
    check("the macro route works", macro_route, group="call_proc")


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


REACHED = {}  # function -> (reached: yes/no/ran, what call_proc said), filled by the sweep


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
    if not RUN_SWEEP:
        return {"skipped": "RUN_SWEEP is False"}
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
        REACHED[name] = (reached, error or "")
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


# -- 4. every reading the bridge does ---------------------------------------------------------
def version():
    result, after = call("Get_InfoStr", INFOSTR_VERSION, TEXT_LENGTH)  # direct: works on 6.10
    return {"return": result, "version": after[1]}


def stage_position():
    result, a = macro_call("StgGetPos", "{x}, {y}, {z}", doubles="xyz")
    return {"return": dr(result), **a}


def xy_position():
    result, a = macro_call("StgGetPosXY", "{x}, {y}", doubles="xy")
    return {"return": dr(result), **a}


def z_position():
    result, a = macro_call("StgGetPosZ", "{z}, 0", doubles="z")
    return {"return": dr(result), **a}


def limits():
    xy, a = macro_call("StgXY_GetLimits", "{a}, {b}, {c}, {d}", doubles="abcd")
    z, b = macro_call("StgZ_GetLimits", "{a}, {b}", doubles="ab")
    return {"StgXY_GetLimits": dr(xy), "x": [a["a"], a["c"]], "y": [a["b"], a["d"]],
            "StgZ_GetLimits": dr(z), "z": [b["a"], b["b"]]}


def optical_configurations():
    count, _ = call("GetOptConfCount")
    names = []
    for index in range(max(count, 0)):
        names.append(text_out("GetOptConfName", f"{index}, {{text}}, {TEXT_LENGTH - 1}")[1])
    return {"GetOptConfCount": count, "names": names}


def text_out(name, arguments):
    """A function that hands back one text, through the macro route: (return, text)."""
    result, a = macro_call(name, arguments, texts=("text",))
    return result, a["text"]


def selected_optical_configuration():
    """GetSelectedOptConf hands back three texts (objective, camera, microscope part)."""
    result, a = macro_call("GetSelectedOptConf", f"{{o}}, {{c}}, {{m}}, {TEXT_LENGTH - 1}",
                           texts="ocm")
    return {"return": result, "texts": [a["o"], a["c"], a["m"]]}


def nosepiece():
    answer = {name: call(name)[0] for name in (
        "Stg_IsNosepiecePresent", "Stg_GetNosepiecePositions", "Stg_GetNosepiecePosition")}
    names = {}
    for position in range(1, max(answer["Stg_GetNosepiecePositions"], 0) + 1):
        result, text = text_out("Stg_GetNosepieceObjectiveName",
                                f"{position}, {{text}}, {TEXT_LENGTH - 1}")
        names[position] = {"return": dr(result), "name": text}
    answer["objectives"] = names
    return answer


def pfs():
    return {"Stg_IsPFSPresent": call("Stg_IsPFSPresent")[0],
            "Stg_GetPFSStatus": call("Stg_GetPFSStatus")[0]}


def pfs_on():
    return bool(call("Stg_IsPFSPresent")[0]) and call("Stg_GetPFSStatus")[0] in (1, 5, 6)


def calibration():
    result, a = macro_call("Get_Calibration", "{name}, {cal}, {aspect}, {unit}",
                           doubles=("cal", "aspect"), ints=("unit",), texts=("name",))
    return {"return": result, "name": a["name"], "um_per_px": a["cal"], "aspect": a["aspect"],
            "unit": a["unit"]}


def exposure_reading():
    result, a = macro_call("Camera_ExposureGet", "{ms}", doubles=("ms",))
    return {"return": dr(result), "exposure_ms": a["ms"]}


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
    reading("Camera_ExposureGet", exposure_reading)


def timing():
    """StgGetPosXY TIMING_REPEATS times through the macro route, and a direct call to compare."""
    def times_of(function):
        times = []
        for _ in range(TIMING_REPEATS):
            started = time.perf_counter()
            function()
            times.append(time.perf_counter() - started)
        times.sort()
        return {"median_ms": round(1000 * times[len(times) // 2], 3),
                "max_ms": round(1000 * times[-1], 3)}
    return {"StgGetPosXY (macro)": times_of(xy_position),
            "Stg_GetNosepiecePosition (direct)": times_of(lambda: call("Stg_GetNosepiecePosition"))}


check("timing", timing, group="timing")


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
    answer = {"before": exposure_reading() if ALLOW_CAMERA_READ else None}
    answer["Camera_ExposureSet"] = call("Camera_ExposureSet", float(EXPOSURE_MS))[0]
    answer["read_after_set"] = exposure_reading() if ALLOW_CAMERA_READ else None
    return answer


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
        "StgFocusInRangeEx", float(AUTOFOCUS_RANGE_UM), int(AUTOFOCUS_SPEED))[0]}
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


# -- 7. every function: its signature, the route it needs, and what this run saw ------------
# The signatures come from NIS's help search index (Docs\nis\eng_ar\lunr_fr.js, C form, e.g.
# "StgGetPosXY(double *LpStgX, double *LpStgY)"). Read at run time on the NIS computer; the
# csv stays there. The route is read off the signature:
#   direct            only values go in (or nothing): nis.call_proc(name, *args)
#   macro             a number comes back through a pointer (double *, int *, ...), or a text
#                     with a max length after it: through call_proc these fail or crash NIS
#   macro (text out?) a char * without a length, in a Get/Read/Query function: likely a text
#                     handed back (Get_InfoStr is one, and works direct with a count)
#   direct (text in?) a char * without a length otherwise: likely a text going in (a file
#                     name, a setting); RunMacro and GetVariableValue are such, and work direct
#   unknown           no signature in the help index
# The "?" routes are read off names only; the help's parameter text says which it is.
LENGTH_NAME = re.compile(r"len|size|max|count|chars|buffer", re.I)
GETTER_NAME = re.compile(r"(^|_)(Get|Read|Query|Find|Retrieve)|Get[A-Z_]", re.I)


def signatures():
    paths = glob.glob(os.path.join(NIS_DIR, "Docs", "nis", "*", "lunr_fr.js"))
    if not paths:
        return {}
    with open(paths[0], encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    found = {}
    for part in text.split("{% raw %}")[1:]:
        match = re.match(r"\s*(?:[A-Za-z_]\w*\s+\**\s*)?([A-Za-z_][\w.]*)\s*\(((?:\\n|[^)])*)\)"
                         r"\s*;?\s*\{% endraw %\}", part)  # some start with the return type
        if match and match.group(1) not in found:
            arguments = [" ".join(a.replace("\\n", " ").split()) for a in match.group(2).split(",")]
            found[match.group(1)] = [a for a in arguments if a]
    return found


def route_of(name, arguments):
    """The route a function needs, and the argument shapes that decided it."""
    shapes = []
    for index, argument in enumerate(arguments):
        words = argument.replace("*", " * ").split()
        pointer = "*" in words
        kind = words[0] if words else "?"
        if pointer and kind in ("char", "wchar", "char8"):
            following = arguments[index + 1] if index + 1 < len(arguments) else ""
            with_length = "*" not in following and bool(LENGTH_NAME.search(following.split()[-1] if following else ""))
            shapes.append("text out + length" if with_length else "text in or out")
        elif pointer:
            shapes.append("number out")
        else:
            shapes.append("value in")
    if "number out" in shapes or "text out + length" in shapes:
        route = "macro"
    elif "text in or out" in shapes:
        route = "macro (text out?)" if GETTER_NAME.search(name) else "direct (text in?)"
    else:
        route = "direct"
    return route, " / ".join(dict.fromkeys(shapes)) or "no arguments"


def function_calls():
    path = function_list_file()
    if path is None:
        return {"skipped": f"no FunctionList*.html next to this file or under {NIS_DIR}"}
    found = signatures()
    rows, counts = [], {}
    for name, (section, edition) in sorted(names_in_function_list(path).items()):
        arguments = found.get(name)
        route, shape = route_of(name, arguments) if arguments is not None else ("unknown", "")
        reached, said = REACHED.get(name, ("not swept", ""))
        tested_route, outcome = TESTED.get(name, ("", "not called"))
        if reached == "no":
            route = "not in this NIS"
        rows.append((name, section, edition, reached, f"{name}({', '.join(arguments or [])})"
                     if arguments is not None else "", shape, route, tested_route, outcome))
        counts[route] = counts.get(route, 0) + 1
    with open(os.path.join(OUT_DIR, "functions_calls.csv"), "w", newline="",
              encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("function", "section", "in AR", "reached", "signature (NIS help)",
                         "arguments", "route", "called this run by", "outcome"))
        writer.writerows(rows)
    return {"functions": len(rows), "with a signature": sum(bool(r[4]) for r in rows),
            "by route": counts,
            "called this run": {n: f"{r} - {o}" for n, (r, o) in sorted(TESTED.items())}}


check("every function: route and what this run saw", function_calls, group="calls")


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
