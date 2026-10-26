"""The NIS functions smart microscopy needs: the state of the microscope, and what we can change.

    python smart/make_smart_list.py

Reads ar_functions.txt (every AR macro function), step 0's functions.csv (reachable without
hardware) and step 2's results (called with no arguments, if there), and writes
smart/SMART_FUNCTIONS.md and smart/smart_functions.csv: each function in its group, with
its kind:

  read     reads a state (Get*, Is*, *_Get*)
  set      changes a state (Set*, Move*, Select*, Enable*, Toggle* ...)
  action   does something (capture, autofocus, save, open, close ...)
  dialog   opens a NIS setup window for a person (functions starting with _, *Setup*, Show*)

Left out on purpose: image analysis, measurement, binary, image processing, export,
organizer, visualization, the user interface and the macro language.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-26
License: MIT
"""

import csv
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "smart")
STEP2 = os.path.join(ROOT, "results-nis7", "step2-2026-10-26", "step2_functions.csv")

# (group, what it covers, sections it may come from, pattern). First match wins.
GROUPS = [
    ("Stage XY and Z", "position, moves, limits, speed, piezo, joystick, slide loader",
     {"Device", "Acquire"},
     r"^_?Stg(XY|Z)_|^_?Stg(Get|Set)?Pos|^_?StgMove|^_?StgRelative|Piezo|Joystick|^_?Stg_?(XY|Z)\w*Speed"
     r"|SlideLoader|SlidePresent|^_?StgZ?_?Home|^_?StgXY|^_?StgZ|Stg_?LinearActuator|PI_GcsCommand"
     r"|^_?StgInitiate|^_?StgConfig|^StgGet(InitValues|RelativeMovements|AbsPosZ|List)|^StgSetRelativeMovements"
     r"|Slide|Cassette|BarCode"),
    ("Objectives and nosepiece", "objective position and names, correction collar",
     {"Device", "Calibration"}, r"Nosepiece|Objective|CorrectionCollar|^GetCurrentObjName|^GetObjType|DropOil"),
    ("Focus", "Perfect Focus System, autofocus, focus surface",
     {"Device", "Acquire"}, r"PFS|AutoFocus|Focus|Refocus"),
    ("Optical configurations", "select, list and read optical configurations",
     {"Acquire", "Device"}, r"OptConf"),
    ("Confocal and spinning disk", "spinning disk speed and on/off, A1/AX/C2 confocal settings",
     {"Device"}, r"Disk|^_?A1(?!CC)|^C2|^Confocal|^AxNSPARC|LineChannelSeries"),
    ("Light sources", "lamps, LEDs, lasers, intensity, voltage, iris, light ND filter",
     {"Device", "Acquire"}, r"Light(?!Path)|Laser|Lamp|(?-i:LED)|Lumencor|Spectra|Intensilight|Iris"),
    ("Shutters", "open, close and state of shutters", {"Device", "Acquire"}, r"Shutter"),
    ("Filters and turrets", "filter wheels, turrets, ND filters", {"Device", "Acquire"},
     r"Filter|Turret|NDFilter"),
    ("Light path and optics", "light path, condenser, aperture, zoom, relay lens, analyzer, TIRF",
     {"Device", "Acquire"},
     r"LightPath|Condenser|Aperture|Zoom|Analyzer|RelayLens|TIRF|Magnification|Polarizer|DIC"
     r"|Bioluminescence|CylindricalLens"),
    ("Camera", "exposure, gain, binning, format, ROI, trigger mode, temperature",
     {"Acquire", "Device"},
     r"^_?Camera|CameraROI|Exposure|Binning|ROISet|CameraFormat|TrigAcq|Stg_TriggerInternalCamera"),
    ("Acquisition", "capture, live, freeze, RAM capture, ND experiments",
     {"Acquire", "ND"},
     r"Captur|^_?Live$|LiveSync|^_?Freeze|FineGrab|^_?Grab|RAMCapturing|^ND_Run|^ND_(Pause|Resume|Stop)Experiment"
     r"|^ND_IsInExperiment|^_?ND_Define|^ND_(Get|Set)(Time|ZSeries|Multipoint|Lambda)|^_?Acquire"),
    ("Calibration", "pixel size and image calibration", {"Calibration", "System", "Device"},
     r"Calibration|^Get_Calibration|^StgCalibrate|^Stg_Calibrate"),
    ("Image documents and files", "save, open, close, image info, files, disk space, memory",
     {"ImageDocument", "System"},
     r"^_?ImageSave|^SaveCurrentDocument|^SaveAll|^_?ImageOpen$|^OpenDocument$|^_?Close(Current|All)"
     r"|^GetOpenedDocumentList|^Get_ImageInfo|^DeleteCurrentImage|^SetCaptureCreatesNewDoc"
     r"|^SetMaxMemoryImageSize|^GetFreeDiskSpace|^Get_File(Size|name|Title)|^ImageReuse|^ImageReload"
     r"|^_?SetTempFilesPath|^GetFileAbsTime"),
    ("Incubation and environment", "incubator, heat stage, perfusion, water", {"Device"},
     r"Incubator|HeatStage|Perfusion|Water|WID_|Temperature(?!Get$)"),
    ("Triggers and stimulation", "TTL, triggers, DMD and patterns", {"Device", "Acquire"},
     r"TTL|Trigger|DMD|Pattern|Stimul|Analog|DIO"),
    ("Microscope", "presence, sleep, the device log, NIS version", {"Device", "System"},
     r"Microscope|DeviceCommunicationLog|^ClearLog$|^Get_InfoStr$|^Get_Info$|^Stg_IsStatusStored"
     r"|^Stg_(Store|Restore)Status|MicControlPad|Interlock|^Stg_GetLineIndex"),
]

# Image processing and analysis that live next to the hardware functions: not for the driver.
EXCLUDE = re.compile(r"ACC|Unmixing|DeepSIM|Distortion|MultiView|MultiExcitation|ROIEnabled|Shading"
                     r"|EDF|HDR_|ShowAcquisitionToolbar|CaptureButton|_ROIDefineOnCaptured")
DIALOG = re.compile(r"^_|Setup|^Show|Dialog|Wizard")
READ = re.compile(r"Get(?=[A-Z_]|$)|(^_?|_|Stg|PFS)Is[A-Z]")
SET = re.compile(r"Set|Move|Select|Enable|Disable|Toggle|Lock|Unlock|Open(?!.*Document)|Close(?!.*Document)"
                 r"|Turn|Switch|Home|Store|Restore|Clear|Reset|Hold|Purge|Change")


def kind(name):
    if DIALOG.search(name):
        return "dialog"
    if READ.search(name):
        return "read"
    if SET.search(name):
        return "set"
    return "action"


def main():
    names = []
    with open(os.path.join(ROOT, "ar_functions.txt"), encoding="utf-8") as handle:
        for line in handle:
            if line.strip() and not line.startswith("#"):
                names.append(tuple(line.rstrip("\n").split("\t")[:2]))
    reach = {r["function"]: r["reachable_without_hardware"]
             for r in csv.DictReader(open(os.path.join(ROOT, "functions.csv"), encoding="utf-8"))}
    step2 = {}
    if os.path.exists(STEP2):
        step2 = {r["function"]: r for r in csv.DictReader(open(STEP2, encoding="utf-8"))}

    rows = []
    for name, section in names:
        if EXCLUDE.search(name):
            continue
        for group, _, sections, pattern in GROUPS:
            if section in sections and re.search(pattern, name, re.IGNORECASE):
                s2 = step2.get(name, {})
                rows.append({"function": name, "group": group, "kind": kind(name), "section": section,
                             "reachable_without_hardware": reach.get(name, ""),
                             "step2": s2.get("result", ""), "step2_answer": s2.get("detail", "")})
                break

    with open(os.path.join(HERE, "smart_functions.csv"), "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    kinds = ["read", "set", "action", "dialog"]
    lines = ["# NIS functions for smart microscopy", "",
             f"**{len(rows)} of {len(names)}** AR macro functions: the state of the microscope, and what",
             "we can change, acquire and save. Left out: image analysis, measurement, binary, image",
             "processing, export, organizer, visualization, user interface, macro language.", "",
             "*read*: reads a state. *set*: changes a state. *action*: does something (capture, save,",
             "autofocus). *dialog*: opens a NIS window for a person, not for the driver.",
             "*Reachable*: offered by name with the microscope off (step 0). *Step 2*: called with no",
             "arguments, microscope off (empty: not reached yet). Made by `make_smart_list.py`;",
             "spreadsheet: `smart_functions.csv`.", "",
             "| Group | Covers | read | set | action | dialog | Total | Reachable now |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for group, covers, _, _ in GROUPS:
        rs = [r for r in rows if r["group"] == group]
        anchor = re.sub(r"[^a-z0-9 -]", "", group.lower()).replace(" ", "-")
        lines.append(f"| [{group}](#{anchor}) | {covers} | "
                     + " | ".join(str(sum(r["kind"] == k for r in rs)) for k in kinds)
                     + f" | {len(rs)} | {sum(r['reachable_without_hardware'] == 'yes' for r in rs)} |")
    lines.append("| **All** | | " + " | ".join(f"**{sum(r['kind'] == k for r in rows)}**" for k in kinds)
                 + f" | **{len(rows)}** | **{sum(r['reachable_without_hardware'] == 'yes' for r in rows)}** |")
    for group, covers, _, _ in GROUPS:
        lines += ["", f"## {group}", "", covers[0].upper() + covers[1:] + ".", "",
                  "| Function | Kind | Reachable now | Step 2 | Answer |", "|---|---|---|---|---|"]
        for r in sorted((r for r in rows if r["group"] == group), key=lambda r: (kinds.index(r["kind"]), r["function"])):
            answer = r["step2_answer"].replace("|", "\\|")[:60]
            lines.append(f"| `{r['function']}` | {r['kind']} | {r['reachable_without_hardware']} | {r['step2']} | {answer} |")
    with open(os.path.join(HERE, "SMART_FUNCTIONS.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"{len(rows)} functions")
    for group, *_ in GROUPS:
        print(f"  {group:<28} {sum(r['group'] == group for r in rows)}")


if __name__ == "__main__":
    main()
