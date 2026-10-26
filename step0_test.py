"""Step 0 on NIS-Elements 6.10: what NIS-Elements lets our Python do, measured on the simulator.

Runs INSIDE NIS-Elements, started by step0.mac (Macro > Run Macro From File). It answers:

  1. Which ways of calling a macro function work from NIS's Python on 6.10:
     ctypes on g5_regprocs.dll (what the bridge uses), nis.call_proc (what the bridge uses
     for the exposure), and nis.mac (the NIS 7 route; is it already in 6.10?).
  2. Whether every function the bridge calls, and every function in NIS's own function list,
     can be reached by name (coverage check; nothing is called for this). The list is NOT
     part of this folder (it is Nikon's): the test reads it on the NIS computer, from a
     FunctionList*.html next to this file or in the NIS folder.
  3. What every reading the bridge does returns on 6.10, and how long a call takes.
  4. Every write the bridge does (on by default, for the simulator): each one confirmed and
     put back.

Every result goes to step0_report.json and step0_summary.txt in OUT_DIR. Before each call
the log names it, so if NIS hangs, the last line of step0.log says which call it was.

Standard library and NIS's own `nis` module only.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-26
License: MIT
"""

import ctypes as ct
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
ALLOW_EXPOSURE = True  # Camera_ExposureSet through nis.call_proc, as the bridge does
ALLOW_NOSEPIECE = True  # another objective, then the first again
ALLOW_PFS = True  # Perfect Focus on and off again, if there is one
ALLOW_AUTOFOCUS = True  # StgFocusInRangeEx over AUTOFOCUS_RANGE_UM, then Z put back
ALLOW_CAPTURE = True  # capture one image, save it as TIFF in OUT_DIR, close it
ALLOW_CAMERA_READ = False  # Camera_ExposureGet: on the 6.10 simulator it opened a blocking dialog
ALLOW_COMMAND_TEXT = False  # Int_ExecuteCommand on NIS's own process; may hang

STAGE_STEP_UM = 10.0
Z_STEP_UM = 1.0
EXPOSURE_MS = 50.0
AUTOFOCUS_RANGE_UM = 20.0
AUTOFOCUS_SPEED = 30
PFS_WAIT_S = 5.0
TIMING_REPEATS = 20

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
# Not in the bridge, but read by the NIS 7 Step 0 too, to compare the two versions.
EXTRA_FUNCTIONS = ["StgGetPosXY", "StgGetPosZ", "GetSelectedOptConf", "Camera_ExposureGet",
                   "Int_ExecuteCommand"]

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

regprocs = None
try:
    regprocs = ct.cdll.g5_regprocs  # already loaded by NIS; the bridge calls it this way
except Exception:  # noqa: BLE001 - without it the ctypes checks fail on their own and the rest runs
    pass

HAS_MAC = nis is not None and hasattr(nis, "mac")
HAS_CALL_PROC = nis is not None and hasattr(nis, "call_proc")

check("python", lambda: {"version": sys.version, "executable": sys.executable,
                         "platform": platform.platform()}, group="environment")
check("nis module", lambda: {"present": nis is not None,
                             "names": sorted(n for n in dir(nis) if not n.startswith("__")) if nis else []},
      group="environment")
check("routes", lambda: {"ctypes g5_regprocs": regprocs is not None, "nis.call_proc": HAS_CALL_PROC,
                         "nis.mac": HAS_MAC, "nis.ptr": nis is not None and hasattr(nis, "ptr")},
      group="environment")
if HAS_MAC:
    check("nis.mac", lambda: {"type": repr(type(nis.mac)), "listed_names": len(dir(nis.mac))},
          group="environment")
if nis is not None and hasattr(nis, "ptr"):
    check("nis.ptr", lambda: sorted(n for n in dir(nis.ptr) if not n.startswith("_")),
          group="environment")


def ctypes_resolves(name):
    try:
        getattr(regprocs, name)
        return True
    except Exception:  # noqa: BLE001
        return False


def mac_resolves(name):
    try:
        getattr(nis.mac, name)
        return True
    except Exception:  # noqa: BLE001
        return False


def unknown_name_resolves():
    """Control for the name checks: does a name that does not exist resolve?"""
    name = "ThisFunctionDoesNotExist_Step0"
    answer = {"ctypes": ctypes_resolves(name) if regprocs else None}
    if HAS_MAC:
        answer["nis.mac"] = mac_resolves(name)
    return answer


check("unknown name (control)", unknown_name_resolves, group="environment")

# -- 2. the ways of calling, on the same readings -------------------------------------------
def ctypes_fn(name, argtypes, restype=ct.c_int32):
    fn = getattr(regprocs, name)
    fn.argtypes, fn.restype = argtypes, restype
    return fn


def ctypes_version():
    buf = ct.create_unicode_buffer(64)
    result = ctypes_fn("Get_InfoStr", [ct.c_int32, ct.c_wchar_p])(INFOSTR_VERSION, buf)
    return {"return": result, "version": buf.value}


def mac_version():
    text = nis.ptr.char()
    return {"return": nis.mac.Get_InfoStr(INFOSTR_VERSION, text), "version": text.get()}


def ctypes_xy():
    x, y = ct.c_double(), ct.c_double()
    fn = ctypes_fn("StgGetPosXY", [ct.POINTER(ct.c_double)] * 2)
    return {"return": dr(fn(ct.byref(x), ct.byref(y))), "x": x.value, "y": y.value}


def call_proc_xy():
    """nis.call_proc answers with a list: the return value, then each argument after the call."""
    return {"raw": repr(nis.call_proc("StgGetPosXY", 0.0, 0.0))}


def mac_xy():
    x, y = nis.ptr.double(), nis.ptr.double()
    return {"return": dr(nis.mac.StgGetPosXY(x, y)), "x": x.get(), "y": y.get()}


check("Get_InfoStr via ctypes", ctypes_version, group="routes")
check("StgGetPosXY via ctypes", ctypes_xy, group="routes")
if HAS_CALL_PROC:
    check("StgGetPosXY via nis.call_proc", call_proc_xy, group="routes")
if HAS_MAC:
    check("Get_InfoStr via nis.mac", mac_version, group="routes")
    check("StgGetPosXY via nis.mac", mac_xy, group="routes")

# -- 3. coverage: can every function be reached by name? (nothing is called) ----------------
def bridge_names():
    answer = {}
    for name in BRIDGE_FUNCTIONS + EXTRA_FUNCTIONS:
        answer[name] = {"ctypes": ctypes_resolves(name) if regprocs else None}
        if HAS_MAC:
            answer[name]["nis.mac"] = mac_resolves(name)
    return answer


check("bridge functions by name", bridge_names, group="coverage")

def function_list_file():
    candidates = sorted(glob.glob(os.path.join(HERE, "FunctionList*.htm*")))
    candidates += sorted(glob.glob(os.path.join(NIS_DIR, "**", "FunctionList*.htm*"), recursive=True))
    return candidates[0] if candidates else None


def names_in_function_list(path):
    """Function names from Nikon's HTML list: link texts and names written as name(...)."""
    with open(path, encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    found = set(re.findall(r"<a\b[^>]*>\s*([A-Za-z_][A-Za-z0-9_]{2,})\s*</a>", text))
    plain = html.unescape(re.sub(r"<[^>]+>", " ", text))
    found |= set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]{2,})\s*\(", plain))
    return sorted(found)


def coverage():
    path = function_list_file()
    if path is None:
        return {"skipped": f"no FunctionList*.html next to this file or under {NIS_DIR}"}
    names = names_in_function_list(path)
    answer = {"file": path, "names_found": len(names)}
    routes = {"ctypes": ctypes_resolves} if regprocs else {}
    if HAS_MAC:
        routes["nis.mac"] = mac_resolves
    reachable = {}
    for route, resolves in routes.items():
        hits = [n for n in names if resolves(n)]
        answer[route] = {"reachable": len(hits), "not_reachable": len(names) - len(hits)}
        reachable[route] = set(hits)
    # Per name, in the results folder only: this list comes from Nikon's file and stays local.
    with open(os.path.join(OUT_DIR, "functions.csv"), "w", encoding="utf-8") as handle:
        handle.write("function," + ",".join(routes) + "\n")
        for name in names:
            handle.write(name + "," + ",".join("yes" if name in reachable[r] else "no"
                                               for r in routes) + "\n")
    answer["bridge functions missing from the list"] = [
        n for n in BRIDGE_FUNCTIONS if n not in names]
    return answer


check("every function in NIS's list, by name", coverage, group="coverage")

# -- 4. every reading the bridge does, through ctypes as the bridge does it ------------------
D = ct.POINTER(ct.c_double)


def reading(name, build):
    check(name, build, group="readings")


def stage_position():
    x, y, z = ct.c_double(), ct.c_double(), ct.c_double()
    result = ctypes_fn("StgGetPos", [D] * 3)(ct.byref(x), ct.byref(y), ct.byref(z))
    return {"return": dr(result), "x": x.value, "y": y.value, "z": z.value}


def z_position():
    z = ct.c_double()
    result = ctypes_fn("StgGetPosZ", [D, ct.c_int32])(ct.byref(z), 0)
    return {"return": dr(result), "z": z.value}


def limits():
    x0, y0, x1, y1, z0, z1 = (ct.c_double() for _ in range(6))
    xy = ctypes_fn("StgXY_GetLimits", [D] * 4)(*(ct.byref(v) for v in (x0, y0, x1, y1)))
    z = ctypes_fn("StgZ_GetLimits", [D] * 2)(ct.byref(z0), ct.byref(z1))
    return {"StgXY_GetLimits": dr(xy), "x": [x0.value, x1.value], "y": [y0.value, y1.value],
            "StgZ_GetLimits": dr(z), "z": [z0.value, z1.value]}


def optical_configurations():
    count = ctypes_fn("GetOptConfCount", [])()
    get_name = ctypes_fn("GetOptConfName", [ct.c_int32, ct.c_wchar_p, ct.c_int32])
    names = []
    for index in range(max(count, 0)):
        buf = ct.create_unicode_buffer(256)
        get_name(index, buf, 256)
        names.append(buf.value)
    return {"GetOptConfCount": count, "names": names}


def selected_optical_configuration():
    """GetSelectedOptConf hands back three texts; which one holds the name is what we learn."""
    texts = [ct.create_unicode_buffer(256) for _ in range(3)]
    fn = ctypes_fn("GetSelectedOptConf", [ct.c_wchar_p] * 3 + [ct.c_int32])
    return {"return": fn(*texts, 256), "texts": [t.value for t in texts]}


def nosepiece():
    answer = {"Stg_IsNosepiecePresent": ctypes_fn("Stg_IsNosepiecePresent", [])(),
              "Stg_GetNosepiecePositions": ctypes_fn("Stg_GetNosepiecePositions", [])(),
              "Stg_GetNosepiecePosition": ctypes_fn("Stg_GetNosepiecePosition", [])()}
    get_name = ctypes_fn("Stg_GetNosepieceObjectiveName", [ct.c_int32, ct.c_wchar_p, ct.c_int32])
    names = {}
    for position in range(1, max(answer["Stg_GetNosepiecePositions"], 0) + 1):
        buf = ct.create_unicode_buffer(256)
        names[position] = {"return": dr(get_name(position, buf, 256)), "name": buf.value}
    answer["objectives"] = names
    return answer


def pfs():
    return {"Stg_IsPFSPresent": ctypes_fn("Stg_IsPFSPresent", [])(),
            "Stg_GetPFSStatus": ctypes_fn("Stg_GetPFSStatus", [])()}


def calibration():
    name = ct.create_unicode_buffer(256)
    cal, aspect, unit = ct.c_double(), ct.c_double(), ct.c_int32()
    fn = ctypes_fn("Get_Calibration", [ct.c_wchar_p, D, D, ct.POINTER(ct.c_int32)], ct.c_double)
    result = fn(name, ct.byref(cal), ct.byref(aspect), ct.byref(unit))
    return {"return": result, "name": name.value, "um_per_px": cal.value,
            "aspect": aspect.value, "unit": unit.value}


reading("StgGetPos", stage_position)
reading("StgGetPosZ", z_position)
reading("limits", limits)
reading("optical configurations", optical_configurations)
reading("GetSelectedOptConf", selected_optical_configuration)
reading("nosepiece", nosepiece)
reading("Perfect Focus", pfs)
reading("Get_Calibration (no image open)", calibration)
if ALLOW_CAMERA_READ:
    reading("Camera_ExposureGet via nis.call_proc",
            lambda: {"raw": repr(nis.call_proc("Camera_ExposureGet", 0.0))})


def timing():
    """The same reading TIMING_REPEATS times through each route that is there."""
    answer = {}
    routes = {"ctypes": ctypes_xy}
    if HAS_CALL_PROC:
        routes["nis.call_proc"] = call_proc_xy
    if HAS_MAC:
        routes["nis.mac"] = mac_xy
    for route, function in routes.items():
        times = []
        try:
            for _ in range(TIMING_REPEATS):
                started = time.perf_counter()
                function()
                times.append(time.perf_counter() - started)
        except Exception as error:  # noqa: BLE001 - one route failing leaves the others
            answer[route] = {"error": f"{type(error).__name__}: {error}"}
            continue
        times.sort()
        answer[route] = {"median_ms": round(1000 * times[len(times) // 2], 3),
                         "max_ms": round(1000 * times[-1], 3)}
    return answer


check("StgGetPosXY timing", timing, group="timing")

# -- 5. writes, each confirmed and put back ---------------------------------------------------
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
    move_xy = ctypes_fn("StgMoveXY", [ct.c_double, ct.c_double, ct.c_int32])
    steps = {"start": start, "limits_x": [low, high]}
    started = time.perf_counter()
    steps["StgMoveXY"] = dr(move_xy(target, start["y"], 0))
    steps["move_s"] = round(time.perf_counter() - started, 3)
    steps["read_after_move"] = stage_position()
    steps["StgMoveXY back"] = dr(move_xy(start["x"], start["y"], 0))
    steps["read_after_back"] = stage_position()
    return steps


def z_round_trip():
    if ctypes_fn("Stg_IsPFSPresent", [])() and ctypes_fn("Stg_GetPFSStatus", [])() in (1, 5, 6):
        return {"skipped": "Perfect Focus is on; a Z move would fight it"}
    move_z = ctypes_fn("StgMoveZ", [ct.c_double, ct.c_int32])
    start = z_position()["z"]
    steps = {"start": start, "StgMoveZ": dr(move_z(start + Z_STEP_UM, 0))}
    steps["read_after_move"] = z_position()["z"]
    steps["StgMoveZ back"] = dr(move_z(start, 0))
    steps["read_after_back"] = z_position()["z"]
    return steps


def xyz_round_trip():
    """StgMove: the bridge's move of all three axes at once."""
    if ctypes_fn("Stg_IsPFSPresent", [])() and ctypes_fn("Stg_GetPFSStatus", [])() in (1, 5, 6):
        return {"skipped": "Perfect Focus is on; a Z move would fight it"}
    move = ctypes_fn("StgMove", [ct.c_double, ct.c_double, ct.c_double, ct.c_int32])
    start = stage_position()
    lim = limits()
    step = STAGE_STEP_UM if start["x"] + STAGE_STEP_UM <= max(lim["x"]) else -STAGE_STEP_UM
    steps = {"start": start,
             "StgMove": dr(move(start["x"] + step, start["y"], start["z"] + Z_STEP_UM, 0))}
    steps["read_after_move"] = stage_position()
    steps["StgMove back"] = dr(move(start["x"], start["y"], start["z"], 0))
    steps["read_after_back"] = stage_position()
    return steps


def optical_configuration_round_trip():
    names = optical_configurations()["names"]
    if len(names) < 2:
        return {"skipped": "fewer than two optical configurations"}
    select = ctypes_fn("SelectOptConf", [ct.c_wchar_p])
    first, other = names[0], names[1]
    steps = {"before": selected_optical_configuration()["texts"]}
    steps["SelectOptConf other"] = select(other)
    steps["read_after_select"] = selected_optical_configuration()["texts"]
    steps["SelectOptConf first"] = select(first)
    steps["read_after_first"] = selected_optical_configuration()["texts"]
    steps["selected"] = [other, first]
    return steps


def exposure():
    """Camera_ExposureSet is not exported by the DLL; the bridge reaches it by nis.call_proc."""
    answer = {"ctypes resolves": ctypes_resolves("Camera_ExposureSet")}
    if not HAS_CALL_PROC:
        answer["skipped"] = "no nis.call_proc"
        return answer
    answer["raw"] = repr(nis.call_proc("Camera_ExposureSet", float(EXPOSURE_MS)))
    return answer


def nosepiece_round_trip():
    if not ctypes_fn("Stg_IsNosepiecePresent", [])():
        return {"skipped": "no nosepiece"}
    count = ctypes_fn("Stg_GetNosepiecePositions", [])()
    start = ctypes_fn("Stg_GetNosepiecePosition", [])()
    if count < 2 or start < 1:
        return {"skipped": f"positions {count}, current {start}"}
    other = start % count + 1
    set_position = ctypes_fn("Stg_SetNosepiecePosition", [ct.c_int32])
    steps = {"start": start, "Stg_SetNosepiecePosition": dr(set_position(other))}
    steps["read_after_move"] = ctypes_fn("Stg_GetNosepiecePosition", [])()
    steps["Stg_SetNosepiecePosition back"] = dr(set_position(start))
    steps["read_after_back"] = ctypes_fn("Stg_GetNosepiecePosition", [])()
    return steps


def pfs_round_trip():
    if not ctypes_fn("Stg_IsPFSPresent", [])():
        return {"skipped": "no Perfect Focus"}
    set_status = ctypes_fn("Stg_SetPFSStatus", [ct.c_int32])
    wait = ctypes_fn("Stg_WaitForPFS", [ct.c_double])
    status = ctypes_fn("Stg_GetPFSStatus", [])
    start = status()
    on = start in (1, 5, 6)
    steps = {"start": start, "Stg_SetPFSStatus": set_status(0 if on else 1)}
    steps["Stg_WaitForPFS"] = wait(PFS_WAIT_S)
    steps["read_after_set"] = status()
    steps["Stg_SetPFSStatus back"] = set_status(1 if on else 0)
    steps["Stg_WaitForPFS back"] = wait(PFS_WAIT_S)
    steps["read_after_back"] = status()
    return steps


def autofocus():
    if ctypes_fn("Stg_IsPFSPresent", [])() and ctypes_fn("Stg_GetPFSStatus", [])() in (1, 5, 6):
        return {"skipped": "Perfect Focus is on"}
    start = z_position()["z"]
    focus = ctypes_fn("StgFocusInRangeEx", [ct.c_double, ct.c_double])
    steps = {"start": start, "StgFocusInRangeEx": focus(AUTOFOCUS_RANGE_UM, AUTOFOCUS_SPEED)}
    steps["z_after"] = z_position()["z"]
    steps["StgMoveZ back"] = dr(ctypes_fn("StgMoveZ", [ct.c_double, ct.c_int32])(start, 0))
    steps["read_after_back"] = z_position()["z"]
    return steps


def capture_save_close():
    path = os.path.join(OUT_DIR, "step0_capture.tif")
    if os.path.exists(path):
        os.remove(path)
    steps = {"Capture": dr(ctypes_fn("Capture", [])())}
    steps["Get_Calibration"] = calibration()
    save_as = ctypes_fn("ImageSaveAs", [ct.c_wchar_p, ct.c_int32, ct.c_int32])
    steps["ImageSaveAs"] = save_as(path, TIFF_ALL_LAYERS, 0)
    steps["saved_file"] = os.path.exists(path)
    steps["bytes"] = os.path.getsize(path) if steps["saved_file"] else 0
    steps["CloseCurrentDocument"] = ctypes_fn("CloseCurrentDocument", [ct.c_int32])(
        CLOSE_WITHOUT_ASKING)
    return steps


def command_text():
    """The fallback route: macro text on NIS's own process. Harmless text: it only sets a title."""
    fn = ctypes_fn("Int_ExecuteCommand", [ct.c_int32, ct.c_wchar_p])
    return {"return": fn(os.getpid(), 'WaitText(1, "step0: command text works");')}


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
if ALLOW_PFS:
    check("Perfect Focus and back", pfs_round_trip, group="writes")
if ALLOW_AUTOFOCUS:
    check("autofocus, then Z back", autofocus, group="writes")
if ALLOW_CAPTURE:
    check("capture, save, close", capture_save_close, group="writes")
if ALLOW_COMMAND_TEXT:
    check("Int_ExecuteCommand on own process", command_text, group="writes")

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
