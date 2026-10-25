"""Step 0 of the Nikon driver: what NIS-Elements lets our Python do, measured on the microscope.

Runs INSIDE NIS-Elements, started by step0.mac (Macro > Run Macro From File). It answers:

  1. Which ways of calling a macro function work from NIS's Python here:
     nis.mac (documented), nis.call_proc (NIS 6.10 only), ctypes on g5_regprocs.dll.
  2. Whether every function the AR edition includes can be reached by name (coverage check;
     nothing is called for this).
  3. What the readings return on this microscope, and how long each call takes.
  4. Optional, switched on below: small writes, each confirmed and put back.

Every result goes to step0_report.json and step0_summary.txt in OUT_DIR. Before each call
the log names it, so if NIS hangs, the last line of step0.log says which call it was.

Standard library and NIS's own `nis` module only.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-25
License: MIT
"""

import ctypes as ct
import json
import os
import platform
import sys
import time
import traceback

# -- settings: edit before a run ----------------------------------------------------------
HERE = os.environ.get("STEP0_HERE", r"C:\nikon-step0")  # where this folder was copied to
OUT_DIR = os.path.join(HERE, "results")

ALLOW_STAGE = False  # move XY by STAGE_STEP_UM and back, Z by Z_STEP_UM and back
ALLOW_OPTICAL_CONFIGURATION = False  # select another optical configuration, then the first again
ALLOW_CAPTURE = False  # capture one image, save it as TIFF in OUT_DIR, close it
ALLOW_CAMERA_READ = False  # CameraGet_Exposure: on the simulator a camera read opened a blocking dialog
ALLOW_COMMAND_TEXT = False  # Int_ExecuteCommand on NIS's own process (the fallback route); may hang

STAGE_STEP_UM = 10.0
Z_STEP_UM = 1.0
TIMING_REPEATS = 20

# -- NIS's own codes ------------------------------------------------------------------------
DR_CODES = {
    1: "DR_OK", 2: "DR_PARTIALLYOK", 0: "DR_CANCELED", -1: "DR_UNKNOWNERROR",
    -2: "DR_BADPARAMETER", -3: "DR_NOTSUPPORTED", -4: "DR_NOTAVAILABLE",
    -5: "DR_NOTAUTOMATIC", -6: "DR_NOTCALIBRATED", -7: "DR_NOTINITIALIZED",
}

report = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "settings": {
    "ALLOW_STAGE": ALLOW_STAGE, "ALLOW_OPTICAL_CONFIGURATION": ALLOW_OPTICAL_CONFIGURATION,
    "ALLOW_CAPTURE": ALLOW_CAPTURE, "ALLOW_CAMERA_READ": ALLOW_CAMERA_READ,
    "ALLOW_COMMAND_TEXT": ALLOW_COMMAND_TEXT}, "checks": []}
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

check("python", lambda: {"version": sys.version, "executable": sys.executable,
                         "platform": platform.platform()}, group="environment")
check("nis module", lambda: {"present": nis is not None,
                             "names": sorted(n for n in dir(nis) if not n.startswith("__")) if nis else []},
      group="environment")
check("nis.mac", lambda: {"present": hasattr(nis, "mac"), "type": repr(type(nis.mac)),
                          "listed_names": len(dir(nis.mac))}, group="environment")
check("nis.ptr", lambda: {"present": hasattr(nis, "ptr"),
                          "types": sorted(n for n in dir(nis.ptr) if not n.startswith("_"))},
      group="environment")


def unknown_name_resolves():
    """Control for the coverage check: does nis.mac answer for a name that does not exist?"""
    try:
        getattr(nis.mac, "ThisFunctionDoesNotExist_Step0")
        return {"resolves": True}
    except Exception as error:  # noqa: BLE001
        return {"resolves": False, "error": f"{type(error).__name__}: {error}"}


check("unknown name (control)", unknown_name_resolves, group="environment")

# -- 2. the three ways of calling, on the same readings -------------------------------------
regprocs = None
try:
    regprocs = ct.cdll.g5_regprocs  # already loaded by NIS; the bridge calls it this way today
except Exception:  # noqa: BLE001 - without it the ctypes checks fail on their own and the rest runs
    pass


def mac_version():
    text = nis.ptr.char()
    result = nis.mac.Get_InfoStr(1, text)
    return {"return": result, "version": text.get()}


def ctypes_version():
    buf = ct.create_unicode_buffer(64)
    fn = regprocs.Get_InfoStr
    fn.argtypes, fn.restype = [ct.c_int32, ct.c_wchar_p], ct.c_int32
    return {"return": fn(1, buf), "version": buf.value}


def mac_xy():
    x, y = nis.ptr.double(), nis.ptr.double()
    result = nis.mac.StgGetPosXY(x, y)
    return {"return": dr(result), "x": x.get(), "y": y.get()}


def call_proc_xy():
    """nis.call_proc existed in NIS 6.10; NIS 7.01 has none."""
    if not hasattr(nis, "call_proc"):
        return {"present": False}
    out = nis.call_proc("StgGetPosXY", 0.0, 0.0)
    return {"present": True, "raw": repr(out)}


def ctypes_xy():
    x, y = ct.c_double(), ct.c_double()
    fn = regprocs.StgGetPosXY
    fn.argtypes, fn.restype = [ct.POINTER(ct.c_double)] * 2, ct.c_int32
    return {"return": dr(fn(ct.byref(x), ct.byref(y))), "x": x.value, "y": y.value}


check("Get_InfoStr via nis.mac", mac_version, group="routes")
check("Get_InfoStr via ctypes", ctypes_version, group="routes")
check("StgGetPosXY via nis.mac", mac_xy, group="routes")
check("StgGetPosXY via nis.call_proc", call_proc_xy, group="routes")
check("StgGetPosXY via ctypes", ctypes_xy, group="routes")

# -- 3. coverage: can every AR function be reached by name? (nothing is called) --------------
def coverage():
    names = []
    with open(os.path.join(HERE, "ar_functions.txt"), encoding="utf-8") as handle:
        for line in handle:
            if line.strip() and not line.startswith("#"):
                names.append(line.split("\t")[0])
    listed = set(dir(nis.mac))
    in_listing = [n for n in names if n in listed]
    resolvable, missing = [], []
    for name in names:
        try:
            getattr(nis.mac, name)
            resolvable.append(name)
        except Exception:  # noqa: BLE001
            missing.append(name)
    return {"ar_functions": len(names), "listed_by_dir": len(in_listing),
            "resolvable": len(resolvable), "missing": missing}


check("every AR function by name", coverage, group="coverage")

# -- 4. readings through nis.mac, with timing ------------------------------------------------
def reading(name, build):
    check(name, build, group="readings")


def ptr_call(function_name, *args, dr_code=False):
    """Call nis.mac.<function_name>; hand back the return value and every nis.ptr value.

    The return value is shown as it is: a count, a yes/no or a value. Only where the manual
    documents a DR code (``dr_code=True``) is its meaning added.
    """
    result = getattr(nis.mac, function_name)(*args)
    values = [a.get() if hasattr(a, "get") else a for a in args]
    return {"return": dr(result) if dr_code else result, "values": values}


reading("StgGetPosZ", lambda: ptr_call("StgGetPosZ", nis.ptr.double(), 0, dr_code=True))
reading("StgXY_GetLimits",
        lambda: ptr_call("StgXY_GetLimits", *(nis.ptr.double() for _ in range(4)), dr_code=True))
reading("StgZ_GetLimits",
        lambda: ptr_call("StgZ_GetLimits", nis.ptr.double(), nis.ptr.double(), dr_code=True))
reading("GetOptConfCount", lambda: ptr_call("GetOptConfCount"))


def optical_configurations():
    count = nis.mac.GetOptConfCount()
    names = []
    for index in range(max(count, 0)):
        text = nis.ptr.char()
        nis.mac.GetOptConfName(index, text, 256)
        names.append(text.get())
    return {"count": count, "names": names}


def selected_optical_configuration():
    """GetSelectedOptConf hands back three texts; which one holds the name is what we learn here."""
    return ptr_call("GetSelectedOptConf", nis.ptr.char(), nis.ptr.char(), nis.ptr.char(), 256)


reading("optical configurations", optical_configurations)
reading("GetSelectedOptConf", selected_optical_configuration)
reading("Stg_IsNosepiecePresent", lambda: ptr_call("Stg_IsNosepiecePresent"))
reading("Stg_GetNosepiecePosition", lambda: ptr_call("Stg_GetNosepiecePosition"))
reading("Stg_GetNosepiecePositions", lambda: ptr_call("Stg_GetNosepiecePositions"))


def objectives():
    count = nis.mac.Stg_GetNosepiecePositions()
    names = {}
    for position in range(1, max(count, 0) + 1):
        text = nis.ptr.char()
        result = nis.mac.Stg_GetNosepieceObjectiveName(position, text, 256)
        names[position] = {"return": dr(result), "name": text.get()}
    return names


reading("objective names", objectives)
reading("Stg_IsPFSPresent", lambda: ptr_call("Stg_IsPFSPresent"))
reading("Stg_GetPFSStatus", lambda: ptr_call("Stg_GetPFSStatus"))
reading("Get_Calibration", lambda: ptr_call("Get_Calibration", nis.ptr.char(), nis.ptr.double(),
                                            nis.ptr.double(), nis.ptr.int()))
if ALLOW_CAMERA_READ:
    reading("CameraGet_Exposure (run-time function)",
            lambda: ptr_call("CameraGet_Exposure", 0, nis.ptr.double()))


def timing():
    """The same reading TIMING_REPEATS times through each route that is there.

    A route that fails is recorded with its error; the other routes are still timed.
    """
    answer = {}
    routes = {"nis.mac": mac_xy, "ctypes": ctypes_xy}
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

# -- 5. writes, only when switched on above; each confirmed and put back ----------------------
def stage_round_trip():
    x, y = nis.ptr.double(), nis.ptr.double()
    nis.mac.StgGetPosXY(x, y)
    start_x, start_y = x.get(), y.get()
    limits = [nis.ptr.double() for _ in range(4)]
    nis.mac.StgXY_GetLimits(*limits)
    x0, y0, x1, y1 = (v.get() for v in limits)
    low, high = min(x0, x1), max(x0, x1)
    if start_x + STAGE_STEP_UM <= high:
        target = start_x + STAGE_STEP_UM
    elif start_x - STAGE_STEP_UM >= low:
        target = start_x - STAGE_STEP_UM
    else:
        return {"skipped": f"no room for {STAGE_STEP_UM} um within the X limits {low}..{high}"}
    steps = {"limits_x": [low, high]}
    started = time.perf_counter()
    steps["move"] = dr(nis.mac.StgMoveXY(target, start_y, 0))
    steps["move_s"] = round(time.perf_counter() - started, 3)
    nis.mac.StgGetPosXY(x, y)
    steps["read_after_move"] = [x.get(), y.get()]
    steps["back"] = dr(nis.mac.StgMoveXY(start_x, start_y, 0))
    nis.mac.StgGetPosXY(x, y)
    steps["read_after_back"] = [x.get(), y.get()]
    steps["start"] = [start_x, start_y]
    return steps


def z_round_trip():
    if nis.mac.Stg_IsPFSPresent() and nis.mac.Stg_GetPFSStatus() in (1, 5, 6):
        return {"skipped": "Perfect Focus is on; a Z move would fight it"}
    z = nis.ptr.double()
    nis.mac.StgGetPosZ(z, 0)
    start = z.get()
    steps = {"start": start, "move": dr(nis.mac.StgMoveZ(start + Z_STEP_UM, 0))}
    nis.mac.StgGetPosZ(z, 0)
    steps["read_after_move"] = z.get()
    steps["back"] = dr(nis.mac.StgMoveZ(start, 0))
    nis.mac.StgGetPosZ(z, 0)
    steps["read_after_back"] = z.get()
    return steps


def optical_configuration_round_trip():
    names = optical_configurations()["names"]
    if len(names) < 2:
        return {"skipped": "fewer than two optical configurations"}
    first, other = names[0], names[1]
    steps = {"before": selected_optical_configuration()["values"][:3]}
    steps["select_other"] = nis.mac.SelectOptConf(other)
    steps["read_after_select"] = selected_optical_configuration()["values"][:3]
    steps["select_first"] = nis.mac.SelectOptConf(first)
    steps["read_after_first"] = selected_optical_configuration()["values"][:3]
    steps["selected"] = [other, first]
    return steps


def capture_save_close():
    path = os.path.join(OUT_DIR, "step0_capture.tif")
    steps = {"capture": nis.mac.Capture()}
    info = nis.ptr.char()
    steps["Get_Calibration"] = ptr_call("Get_Calibration", info, nis.ptr.double(), nis.ptr.double(),
                                        nis.ptr.int())
    steps["save"] = nis.mac.ImageSaveAs(path, 18, 0)
    steps["saved_file"] = os.path.exists(path)
    steps["close"] = nis.mac.CloseCurrentDocument(2)
    return steps


def command_text():
    """The fallback route: macro text on NIS's own process. Harmless text: it only sets a title."""
    result = nis.mac.Int_ExecuteCommand(os.getpid(), 'WaitText(1, "step0: command text works");')
    return {"return": result}


if ALLOW_STAGE:
    check("XY move and back", stage_round_trip, group="writes")
    check("Z move and back", z_round_trip, group="writes")
if ALLOW_OPTICAL_CONFIGURATION:
    check("optical configuration and back", optical_configuration_round_trip, group="writes")
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
