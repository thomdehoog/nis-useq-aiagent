# Build results\FUNCTIONS_6.10.md: every function in NIS's list, by category, with what we know:
# reachable through nis.call_proc, exported by g5_regprocs.dll, the route it needs, and what our
# runs found when calling it. Runs OUTSIDE NIS, after step0_test.py and step0_calls.py:
#   python make_function_table.py
# The table is made from Nikon's list and help, so it stays on this computer (results\ is
# not committed).
import csv, json, os, re, struct

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
DLL = r"C:\Program Files\NIS-Elements\g5_regprocs.dll"
DR = {"-1", "-2", "-3", "-4", "-5", "-6", "-7"}

# Hardware (NIS sections Device and Acquire) by device; the first pattern that matches wins.
DEVICES = [
    ("Camera", r"^Camera|Camera|^CameraFormat|^ROI|Grabber|Shading|Live|Freeze|Grab|Capture|RAMCapturing|AutoExposure"),
    ("Optical configurations", r"OptConf"),
    ("Objectives and nosepiece", r"Nosepiece|Objective|ObjMagnification|ObjType|CorrectionCollar"),
    ("Perfect Focus and autofocus", r"PFS|Focus|^VCS"),
    ("Stage Z", r"^StgZ|PosZ|AbsPosZ|MoveZ"),
    ("Stage XY", r"^StgXY|StgGetPos|StgMove|^StgSet|^StgGet|^Stg[A-Z]|LoadingPosition"),
    ("Filters", r"Filter"),
    ("Shutters", r"Shutter|CSU"),
    ("Lights and lasers", r"Light|Laser|LED|Lamp|Iris"),
    ("Condenser, aperture, zoom, light path", r"Condenser|Aperture|Zoom|Analyzer|LightPath|RelayLens|Cylindrical|Disk"),
    ("TIRF", r"TIRF"),
    ("Incubator and heating", r"Incubator|Heat|Perfusion|WID_"),
    ("DMD and patterns", r"DMD|Pattern"),
    ("Triggers and TTL", r"Trig|TTL|Pin|PFI"),
    ("Confocal, A1, AX, C2, galvo", r"^A1|^AX|^C2|Confocal|Galvo|^ACC"),
    ("Slide loader", r"Slide|Cassette|BarCode"),
]


def dll_exports(path):
    data = open(path, "rb").read()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    count = struct.unpack_from("<H", data, pe + 6)[0]
    opt = pe + 24
    dirs = opt + (112 if struct.unpack_from("<H", data, opt)[0] == 0x20B else 96)
    export = struct.unpack_from("<I", data, dirs)[0]
    sections = opt + struct.unpack_from("<H", data, pe + 20)[0]
    table = [struct.unpack_from("<8sIIII", data, sections + 40 * i) for i in range(count)]

    def offset(rva):
        for _, size, va, raw_size, raw in table:
            if va <= rva < va + max(size, raw_size):
                return rva - va + raw
    base = offset(export)
    names_count, names = struct.unpack_from("<I", data, base + 24)[0], struct.unpack_from("<I", data, base + 32)[0]
    found = set()
    for i in range(names_count):
        p = offset(struct.unpack_from("<I", data, offset(names) + 4 * i)[0])
        found.add(data[p:data.index(b"\0", p)].decode("ascii", "replace"))
    return found


def read_csv(name):
    path = os.path.join(RESULTS, name)
    return list(csv.DictReader(open(path, encoding="utf-8"))) if os.path.exists(path) else []


def main():
    functions = read_csv("functions_calls.csv")
    called = read_csv("functions_called.csv")
    exported = dll_exports(DLL)
    dialogs = set()
    if os.path.exists(os.path.join(RESULTS, "dialogs.log")):
        dialogs = set(re.findall(r"= ([A-Za-z_][\w.]*)\(", open(os.path.join(RESULTS, "dialogs.log"), encoding="utf-8").read()))

    # What our runs found, best result per function.
    rank = {"changed and put back": 6, "works": 5, "set, read back the same": 5, "set, nothing changed": 3,
            "reads back differently": 3, "answered DR error": 2, "handed back nothing": 2,
            "opened a dialog": 1, "error": 1, "not in this NIS": 0}
    found = {}
    used = {}  # the route our runs really called it by: direct or macro
    for r in called:
        if r["outcome"].startswith("ok"):
            used.setdefault(r["function"], r["route"])
    for r in functions:
        if r["outcome"].startswith("ok") and r["called this run by"]:
            used.setdefault(r["function"], r["called this run by"])

    def note(name, verdict):
        if rank.get(verdict, 0) >= rank.get(found.get(name, ""), -1):
            found[name] = verdict
    for r in called:
        values = json.loads(r["handed back"]) if r["handed back"] else []
        stage = r["stage"][0]
        if r["function"] in dialogs:
            verdict = "opened a dialog"
        elif r["outcome"].startswith("not in this NIS"):
            verdict = "not in this NIS"
        elif not r["outcome"].startswith("ok"):
            verdict = "error"
        elif stage == "4":
            verdict = "set, nothing changed" if "but read" in r["outcome"] else "changed and put back"
        elif "but read" in r["outcome"]:
            verdict = "reads back differently"
        elif r["returned"] in DR:
            verdict = "answered DR error"
        elif stage == "2" and values and all(v is None for v in values):
            verdict = "handed back nothing"
        else:
            verdict = "set, read back the same" if stage == "3" else "works"
        note(r["function"], verdict)
    for r in functions:  # the bridge's own functions, from step0_test.py
        if r["outcome"].startswith("ok"):
            note(r["function"], "works")
        elif r["outcome"].startswith("error"):
            note(r["function"], "error")

    def category(r):
        if r["section"] in ("Device", "Acquire"):
            for title, pattern in DEVICES:
                if re.search(pattern, r["function"]):
                    return "Hardware", title
            return "Hardware", "Other devices"
        return "Not hardware", r["section"]

    groups = {}
    for r in functions:
        groups.setdefault(category(r), []).append(r)

    lines = ["# NIS-Elements 6.10.02: every macro function, by category", "",
             "Made by `make_function_table.py` from NIS's function list and help, g5_regprocs.dll and "
             "the step0 runs on the Ti2 simulator. Stays on this computer.", "",
             "- **Reach**: `nis.call_proc` finds it by name (sweep: called with an argument it cannot take, nothing ran).",
             "- **DLL**: exported by g5_regprocs.dll.",
             "- **Route** (from the signature): *direct* = `nis.call_proc`, only values go in; *macro* = hands a value "
             "back, so through a NIS macro (directly it fails or crashes NIS on 6.10); *?* = a text that may go in "
             "or come back.",
             "- **Our runs**: what calling it for real gave; empty = not called (it needs an image, a file or a set-up).",
             ""]
    summary = ["| Category | Functions | Reach | DLL | Called | Works |", "|---|---|---|---|---|---|"]
    body = []
    for (kind, title) in sorted(groups, key=lambda k: (k[0] != "Hardware", k[1])):
        rows = sorted(groups[(kind, title)], key=lambda r: r["function"])
        reach = sum(r["reached"] == "yes" for r in rows)
        in_dll = sum(r["function"] in exported for r in rows)
        tried = [found[r["function"]] for r in rows if r["function"] in found]
        works = sum(v in ("works", "changed and put back", "set, read back the same") for v in tried)
        summary.append(f"| {kind}: {title} | {len(rows)} | {reach} | {in_dll} | {len(tried)} | {works} |")
        body += [f"## {kind}: {title}", "",
                 f"{len(rows)} functions, {reach} reachable, {in_dll} in the DLL, {len(tried)} called, {works} work.", "",
                 "| Function | Reach | DLL | Route | Our runs | Signature |", "|---|---|---|---|---|---|"]
        for r in rows:
            route = r["route"].replace("direct (text in?)", "direct?").replace("macro (text out?)", "macro?")
            route = "" if route in ("not in this NIS", "unknown") else route
            body.append(f"| `{r['function']}` | {'yes' if r['reached'] == 'yes' else 'no'} | "
                        f"{'yes' if r['function'] in exported else ''} | {route} | {found.get(r['function'], '')} | "
                        f"{r['signature (NIS help)'].replace('|', '/')} |")
        body.append("")
    lines += ["## Overview", ""] + summary + [""] + body
    out = os.path.join(RESULTS, "FUNCTIONS_6.10.md")
    with open(out, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    with open(os.path.join(RESULTS, "functions_by_category.csv"), "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("kind", "category", "function", "reach", "dll", "route", "our runs", "signature"))
        for (kind, title), rows in sorted(groups.items()):
            for r in sorted(rows, key=lambda r: r["function"]):
                writer.writerow((kind, title, r["function"], r["reached"], r["function"] in exported,
                                 r["route"], found.get(r["function"], ""), r["signature (NIS help)"]))
    # The functions we can run: called for real and they worked. Names and our results only.
    good = ("works", "changed and put back", "set, read back the same")
    shown = {"works": "works", "changed and put back": "changed and put back",
             "set, read back the same": "set, read back"}
    callable_lines = ["| Category | Can run | Through the DLL | Only through `nis.call_proc` |",
                      "|---|---|---|---|"]
    callable_body = []
    total = [0, 0]
    for (kind, title) in sorted(groups, key=lambda k: (k[0] != "Hardware", k[1])):
        rows = [r for r in sorted(groups[(kind, title)], key=lambda r: r["function"])
                if found.get(r["function"]) in good]
        if not rows:
            continue
        dll = sum(r["function"] in exported for r in rows)
        total = [total[0] + len(rows), total[1] + dll]
        callable_lines.append(f"| {title} | {len(rows)} | {dll} | {len(rows) - dll} |")
        callable_body += [f"### {title}", "", "| Function | Fastest route | Result |", "|---|---|---|"]
        for r in rows:
            route = "DLL" if r["function"] in exported else (
                "macro" if used.get(r["function"]) == "macro" else "call_proc")
            callable_body.append(f"| `{r['function']}` | {route} | {shown[found[r['function']]]} |")
        callable_body.append("")
    callable_lines.append(f"| **Total** | **{total[0]}** | **{total[1]}** | **{total[0] - total[1]}** |")
    with open(os.path.join(RESULTS, "CALLABLE_6.10.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join([
            "# NIS-Elements 6.10.02: the functions we can run", "",
            "Every macro function our Python called for real on the Ti2 simulator (2026-10-26) and that "
            "worked: `step0_test.py` (the bridge's functions) and `step0_calls.py` (the hardware "
            "functions). Made by `make_function_table.py`. About 3000 more are reachable but not "
            "called yet: they need an image, a file or a set-up (RESULTS.md).", "",
            "- **Fastest route**: *DLL* = exported by g5_regprocs.dll (ctypes, about 0.003 ms); "
            "*call_proc* = only through `nis.call_proc`, values going in (about 0.5 ms); *macro* = only "
            "through `nis.call_proc`, and it hands a value back, so inside a NIS macro (about 20 ms).",
            "- **Result**: *works* = answered with a value; *set, read back* = set to the value it "
            "had and read back unchanged; *changed and put back* = set to another position or state, "
            "read back, and set back.", ""] + callable_lines + [""] + callable_body) + "\n")
    print(out)
    print("\n".join(callable_lines))


if __name__ == "__main__":
    main()
