"""Step 0 on NIS-Elements 6.10: call every function that can be called without a set-up.

Runs INSIDE NIS-Elements, started by step0_calls.mac. Where step0_test.py checks the bridge's
own functions, this goes through NIS's whole function list and really calls what can be
called without an image, a file or a dialog:

Hardware only: the Device section (stage, nosepiece, filters, shutters, lights, PFS, ...)
and Acquire (camera) of NIS's function list.

  1. getters without arguments (Get..., Is..., ...Count): direct through nis.call_proc
  2. getters that hand values back (numbers through a pointer, texts), with an index or a
     type guessed: through a macro (directly these fail or crash NIS on 6.10)
  3. every Set... with a matching Get...: set the value the Get read, read it again
  4. Set...Position with a number of positions (filters, nosepiece, condenser, zoom, ...)
     and on/off Set...State (shutters, lights, TIRF mirror, ...): set another position or
     the other state, read it, set the first one back, read it

Writes are on by default (simulator only). On a real microscope set ALLOW_SET_SAME and
ALLOW_CHANGE to False.

If NIS dies or hangs, run it again: results\\calls_progress.jsonl remembers every call; a call
that started but never finished is marked "NIS died or hung" and skipped, the rest go on
where they stopped. NIS's heap corruption can show up a few calls after its cause, so the
log keeps the calls before it. Delete calls_progress.jsonl to start over.

A function that opened a dialog in an earlier run (results\\dialogs.log, written by
dialog_watcher.py) is not called again.

Results: results\\functions_called.csv (one line per call; stays on the NIS computer, as it
is made from NIS's function list) and results\\step0_calls.log.

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
import re
import time

import nis

# -- settings -------------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "results")
NIS_DIR = r"C:\Program Files\NIS-Elements"
ALLOW_SET_SAME = True  # stage 3: set the value that is already there
ALLOW_CHANGE = True  # stage 4: set another position or step, then put the first one back
TEXT_LENGTH = 256
NOT_SET = -123456789.0
SLOW_S = 3.0  # a call this slow probably waited for a dialog
SECTIONS = {"Device", "Acquire"}  # hardware only: microscope devices and the camera

# Functions that wait for the user, open a window, or act on files, windows or databases:
# never called here, whatever their name says.
NEVER = re.compile(r"^(_|Int_)|Dialog|Wizard|Browse|Show|Ask|Input|Event|Wait|Pause|Exit|"
                   r"Excel|ODBC|Jobs|Org_|Window|File|Folder|Path|Password|User|License|"
                   r"Delete|Remove|Close|Clear|Reset|Init|Calibrate|Exec|Run|Macro|Python|"
                   r"JS|ECMA|IJ_|Clipboard|Print|Report|Database|Db_|S3_", re.I)
GETTER = re.compile(r"(^|_)(Get|Is)[A-Z_]|Get[A-Z_]|(Count|Positions|Steps)$")
SETTER = re.compile(r"(^|_)Set[A-Z_]|Set[A-Z_]")
DR_ERRORS = range(-7, 0)  # DR_UNKNOWNERROR .. DR_NOTINITIALIZED
INT_TYPES = {"int", "long", "lx_int32", "bool", "dword", "word", "byte", "unsigned", "int64"}

os.makedirs(OUT_DIR, exist_ok=True)
log_file = open(os.path.join(OUT_DIR, "step0_calls.log"), "a", encoding="utf-8")
PROGRESS = os.path.join(OUT_DIR, "calls_progress.jsonl")
MACRO_FILE = os.path.join(OUT_DIR, "step0_calls.mac").replace("\\", "/")
TEXT_FILE = os.path.join(OUT_DIR, "step0_calls_text").replace("\\", "/")


def log(text):
    log_file.write(f"{time.strftime('%H:%M:%S')} {text}".encode("ascii", "backslashreplace")
                   .decode() + "\n")
    log_file.flush()


# -- what earlier runs found ----------------------------------------------------------------
done, died = {}, set()
if os.path.exists(PROGRESS):
    started = set()
    with open(PROGRESS, encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if record["event"] == "start":
                started.add(record["key"])
            else:
                done[record["key"]] = record
    died = started - set(done)
progress = open(PROGRESS, "a", encoding="utf-8")


def remember(record):
    progress.write(json.dumps(record, default=repr) + "\n")
    progress.flush()


# Functions whose call opened a dialog in an earlier run (dialog_watcher.py writes them down):
# not called again, so a rerun needs nobody at the keyboard.
DIALOGS = os.path.join(OUT_DIR, "dialogs.log")
gave_dialog = set()
if os.path.exists(DIALOGS):
    with open(DIALOGS, encoding="utf-8") as handle:
        gave_dialog = set(re.findall(r"= ([A-Za-z_][\w.]*)\(", handle.read()))

for key in died:  # NIS died or hung during these last time: record that, never call again
    stage, name, arguments = key.split("|", 2)
    record = {"event": "done", "key": key, "stage": stage, "function": name, "route": "",
              "arguments": arguments, "outcome": "NIS died or hung during this call "
              "(or a call just before it corrupted the heap)", "seconds": ""}
    remember(record)
    done[key] = record


# -- NIS's function list and signatures (read here, never stored in the repository) -----------
def function_list():
    paths = sorted(glob.glob(os.path.join(NIS_DIR, "**", "FunctionList*.htm*"), recursive=True))
    with open(paths[0], encoding="latin-1") as handle:
        text = handle.read()
    parts = re.split(r"<h2>(.*?)</h2>", text)
    functions = {}
    for index in range(1, len(parts), 2):
        section = html.unescape(parts[index]).strip()
        for row in re.findall(r"<tr>(.*?)</tr>", parts[index + 1], re.S):
            name = re.search(r'<td title="([^"]+)"', row)
            if name:
                functions.setdefault(html.unescape(name.group(1)).strip(), section)
    return functions


def signatures():
    path = glob.glob(os.path.join(NIS_DIR, "Docs", "nis", "*", "lunr_fr.js"))[0]
    with open(path, encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    found = {}
    for part in text.split("{% raw %}")[1:]:
        match = re.match(r"\s*(?:[A-Za-z_]\w*\s+\**\s*)?([A-Za-z_][\w.]*)\s*\(((?:\\n|[^)])*)\)"
                         r"\s*;?\s*\{% endraw %\}", part)
        if match and match.group(1) not in found:
            arguments = [" ".join(a.replace("\\n", " ").split()) for a in match.group(2).split(",")]
            found[match.group(1)] = [parse(a) for a in arguments if a]
    return found


def parse(argument):
    """'double *LpStgX' -> {'type': 'double', 'pointer': True, 'name': 'LpStgX'}"""
    words = argument.replace("*", " * ").split()
    pointer = "*" in words
    words = [w for w in words if w != "*"]
    kind = "unsigned" if words[:1] == ["unsigned"] else (words[0] if words else "?")
    return {"type": kind, "pointer": pointer, "name": words[-1] if len(words) > 1 else ""}


def guesses(argument):
    """Values to try for an argument that goes in."""
    name = argument["name"].lower()
    if argument["type"] == "double":
        return ["0.0"]
    if "index" in name or "idx" in name:
        return ["0"]
    if "type" in name:
        return ["0", "1", "2", "3", "4", "5"]
    return ["1"]


# -- calling ------------------------------------------------------------------------------
_counter = [0]


def direct(name, *args):
    out = nis.call_proc(name, *args)
    out = list(out) if isinstance(out, (list, tuple)) else [out]
    return out[0], out[1:]


def macro(name, plan):
    """Call name in a macro. plan: one entry per argument, ("in", text) or ("out", kind) with
    kind 'double', 'int' or 'text'. Hands back (return value, [values handed back])."""
    _counter[0] += 1
    prefix = f"step0c_{_counter[0]}_"
    declarations, statements, filled, outs = [f"global double {prefix}r;"], [], [], []
    for index, (role, what) in enumerate(plan):  # NIS wants every declaration before a statement
        variable = f"{prefix}{index}"
        if role == "in":
            filled.append(what)
        elif what == "text":
            declarations.append(f"char {variable}[{TEXT_LENGTH}];")
            statements.append(f"{variable}[0] = 0;")
            filled.append(variable)
            outs.append((variable, "text"))
        else:
            declarations.append(f"global {what} {variable};")
            statements.append(f"{variable} = {NOT_SET:.1f};" if what == "double" else f"{variable} = -12345;")
            filled.append("&" + variable)
            outs.append((variable, what))
    lines = declarations + statements + [f"{prefix}r = {name}({', '.join(filled)});"]
    for variable, kind in outs:
        if kind == "text":
            path = f"{TEXT_FILE}_{variable}.bin"
            if os.path.exists(path):
                os.remove(path)
            lines.append(f'WriteFile("{path}", {variable}, 2 * strlen({variable}));')
    with open(MACRO_FILE, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    try:
        ran = nis.call_proc("RunMacro", MACRO_FILE)
        ran = ran[0] if isinstance(ran, (list, tuple)) else ran
        if ran != 1:
            raise RuntimeError(f"RunMacro returned {ran!r}")

        def variable_value(variable):
            got = nis.call_proc("GetVariableValue", variable)
            return got[0] if isinstance(got, (list, tuple)) else got

        values = []
        for variable, kind in outs:
            if kind == "text":
                path = f"{TEXT_FILE}_{variable}.bin"
                text = ""
                if os.path.exists(path):
                    with open(path, "rb") as handle:
                        text = handle.read().decode("utf-16-le", "replace").split("\0")[0]
                    os.remove(path)
                values.append(text)
            else:
                got = variable_value(variable)
                values.append(None if got in (NOT_SET, -12345) else (int(got) if kind == "int" else got))
        result = variable_value(prefix + "r")
    finally:
        try:
            nis.call_proc("DeleteVariables", prefix)
        except Exception:  # noqa: BLE001
            pass
    return (int(result) if isinstance(result, float) and result.is_integer() else result), values


def attempt(stage, name, route, arguments, function):
    """One call, remembered before and after; a call done in an earlier run is not repeated."""
    key = f"{stage}|{name}|{arguments}"
    if key in done:
        return done[key]
    if name in gave_dialog:
        record = {"event": "done", "key": key, "stage": stage, "function": name, "route": route,
                  "arguments": arguments, "ok": False, "seconds": "",
                  "outcome": "skipped: opened a dialog in an earlier run (see dialogs.log)"}
        done[key] = record
        return record
    log(f"call {stage} {name}({arguments}) {route}")
    remember({"event": "start", "key": key})
    started = time.perf_counter()
    record = {"event": "done", "key": key, "stage": stage, "function": name, "route": route,
              "arguments": arguments}
    try:
        result, values = function()
        record.update(ok=True, result=result, values=values, outcome="ok")
    except Exception as error:  # noqa: BLE001 - the error is the answer
        message = str(error)
        outcome = "not in this NIS" if "Procedure not found" in message else f"error: {message}"
        record.update(ok=False, outcome=outcome)
    record["seconds"] = round(time.perf_counter() - started, 3)
    if record["seconds"] > SLOW_S:
        record["outcome"] += f" (slow: {record['seconds']} s, a dialog?)"
    log(f"  -> {record['outcome']} {record.get('result', '')!r} {record.get('values', '')!r}")
    remember(record)
    done[key] = record
    return record


def answered(record):
    """A Get's record that holds a usable value: ran, and did not return a DR error code."""
    return record.get("ok") and not (isinstance(record.get("result"), int)
                                     and record["result"] in DR_ERRORS)


# -- the stages -------------------------------------------------------------------------------
listed = function_list()
found = signatures()
log(f"start: {len(listed)} functions in the list, {len(found)} signatures, "
    f"{len(done)} calls known from earlier runs ({len(died)} died)")
readings = {}  # Get name -> {in-argument texts: record} for every call that answered


def plan_for(arguments):
    """How to call a getter, or None if it takes something we cannot make up."""
    plan = []
    for index, argument in enumerate(arguments):
        if argument["type"] in ("char", "char8") and argument["pointer"]:
            plan.append(("out", "text"))
        elif argument["pointer"] and argument["type"] == "double":
            plan.append(("out", "double"))
        elif argument["pointer"] and argument["type"] in INT_TYPES:
            plan.append(("out", "int"))
        elif argument["pointer"] or argument["type"] not in INT_TYPES | {"double"}:
            return None  # wchar, arrays of other types, structures: not made up here
        elif plan and plan[-1] == ("out", "text") and re.search(
                r"len|size|max|count|chars|buffer", argument["name"], re.I):
            plan.append(("in", str(TEXT_LENGTH - 1)))
        else:
            plan.append(("in", guesses(argument)))
    return plan


for name in sorted(listed):
    if (listed[name] not in SECTIONS or not GETTER.search(name) or SETTER.search(name)
            or NEVER.search(name) or name not in found):
        continue
    arguments = found[name]
    if not arguments:  # stage 1
        record = attempt("1 getter", name, "direct", "", lambda: direct(name))
        if answered(record):
            readings[name] = {(): record}
        continue
    plan = plan_for(arguments)  # stage 2
    if plan is None:
        continue
    choices = next((i for i, (role, what) in enumerate(plan) if isinstance(what, list)), None)
    options = plan[choices][1] if choices is not None else [None]
    for option in options:  # every type that answers (filter wheel 0, 1, ...), not only the first
        concrete = [(role, option if isinstance(what, list) and i == choices else
                     (what[0] if isinstance(what, list) else what))
                    for i, (role, what) in enumerate(plan)]
        shown = ", ".join(what if role == "in" else f"<{what} out>" for role, what in concrete)
        record = attempt("2 getter (values out)", name, "macro", shown,
                         lambda: macro(name, concrete))
        if answered(record):
            inputs = tuple(what for role, what in concrete if role == "in")
            readings.setdefault(name, {})[inputs] = record


def get_again(name, inputs):
    """Read a Get again the way it answered: its return value, or what it handed back."""
    record = readings[name][tuple(inputs)]
    if record["route"] == "direct":
        return direct(name)[0]
    plan = [("in", value) for value in inputs] + [
        ("out", "text" if isinstance(v, str) else ("int" if isinstance(v, int) else "double"))
        for v in record["values"]]
    result, values = macro(name, plan)
    return values if values else result


def as_macro_text(value):
    return '"' + value.replace('"', "") + '"' if isinstance(value, str) else repr(value)


def fits(arguments, values):
    """Does every argument of a Set take the value meant for it: a text for a text, a number
    for a number? (A Get's char * can be an input, e.g. a gas name, not a text it hands back.)"""
    for argument, value in zip(arguments, values):
        is_text = argument["type"] in ("char", "char8")
        if is_text != isinstance(value, str) or (argument["pointer"] and not is_text):
            return False
    return True


def range_of(get_name, inputs):
    """How many positions a Get...Position has, from its Get...Positions or ...Steps."""
    for name in (get_name.replace("Position", "Positions"), get_name.replace("Position", "Steps"),
                 get_name.replace("Position", "PositionCount")):
        if name != get_name and name in readings:
            record = readings[name].get(tuple(inputs)) or readings[name].get(())
            if record and isinstance(record["result"], int):
                return record["result"]
    return None


def first(value):
    value = value[0] if isinstance(value, list) and len(value) == 1 else value
    return int(value) if isinstance(value, float) and value.is_integer() else value


for set_name in sorted(listed):
    get_name = set_name.replace("Set", "Get", 1)
    if (listed[set_name] not in SECTIONS or not SETTER.search(set_name) or NEVER.search(set_name)
            or get_name not in readings or set_name not in found):
        continue
    for inputs, record in sorted(readings[get_name].items()):
        current = record["values"] if record["values"] else [record["result"]]
        if any(v is None for v in current):
            continue
        call_with = [*(float(i) if "." in i else int(i) for i in inputs), *current]
        if len(found[set_name]) != len(call_with) or not fits(found[set_name], call_with):
            continue  # the Set does not take what the Get gave
        shown = ", ".join(str(v) for v in [*inputs, *(as_macro_text(v) for v in current)])
        if ALLOW_SET_SAME:  # stage 3
            record3 = attempt("3 set same value", set_name, "direct", shown,
                              lambda: (direct(set_name, *call_with)[0],
                                       [get_again(get_name, inputs)]))
            if record3.get("ok") and record3["outcome"] == "ok":
                after = record3["values"][0]
                after = after if isinstance(after, list) else [after]
                if after != current:
                    record3["outcome"] = f"ok, but read back {after!r} instead of {current!r}"
                    remember(record3)
        value = first(current)
        if not ALLOW_CHANGE or len(current) != 1 or not isinstance(value, int):
            continue
        if re.search(r"State|Mirror|Switch", set_name) and value in (0, 1):
            other = 1 - value  # on/off, open/closed, in/out
        elif "Position" in set_name:
            count = range_of(get_name, inputs)
            if count is None or count < 2:
                continue
            # positions count from 0 on some devices and from 1 on others; one step down from
            # 2 or more, or up from 0 or 1, stays in range either way
            other = value - 1 if value >= 2 else value + 1
        else:
            continue  # a speed, voltage or intensity is not a step: stage 3 only
        other_typed = float(other) if isinstance(current[0], float) else other

        def change_and_back():
            answer = {"to": other_typed,
                      "set": direct(set_name, *call_with[:-1], other_typed)[0]}
            answer["read_after_set"] = first(get_again(get_name, inputs))
            answer["back"] = direct(set_name, *call_with)[0]
            answer["read_after_back"] = first(get_again(get_name, inputs))
            return answer["set"], [answer]

        record4 = attempt("4 change and back", set_name, "direct",
                          f"{shown} -> {other_typed} -> {current[0]}", change_and_back)
        if record4.get("ok") and record4["outcome"] == "ok":
            answer = record4["values"][0]
            if answer["read_after_set"] != other or answer["read_after_back"] != value:
                record4["outcome"] = (f"ok, but read {answer['read_after_set']!r} after the change "
                                      f"and {answer['read_after_back']!r} after putting it back")
                remember(record4)


# -- the table ----------------------------------------------------------------------------
with open(os.path.join(OUT_DIR, "functions_called.csv"), "w", newline="", encoding="utf-8") as h:
    writer = csv.writer(h)
    writer.writerow(("function", "section", "stage", "route", "arguments", "outcome", "returned",
                     "handed back", "seconds"))
    for record in sorted(done.values(), key=lambda r: (r["function"], r["stage"])):
        writer.writerow((record["function"], listed.get(record["function"], ""), record["stage"],
                         record["route"], record["arguments"], record["outcome"],
                         repr(record.get("result", "")),
                         json.dumps(record.get("values", ""), ensure_ascii=False, default=repr),
                         record["seconds"]))
counts = {}
for record in done.values():
    outcome = record["outcome"].split(":")[0].split(",")[0].split(" (")[0]
    counts.setdefault(record["stage"], {}).setdefault(outcome, 0)
    counts[record["stage"]][outcome] += 1
log(f"done: {json.dumps(counts)}")
log_file.close()
progress.close()
