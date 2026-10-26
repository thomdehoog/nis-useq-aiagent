"""Make the table of step 2: every AR function, and what happened when it was called.

    python make_table.py RESULTS_FOLDER [OUTPUT_FOLDER]

Reads step2_calls.jsonl and step2_dialogs.jsonl from the results folder (and step 0's
functions.csv next to the repository, if there) and writes STEP2_FUNCTIONS.md and
step2_functions.csv. Standard library only.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-26
License: MIT
"""

import csv
import json
import os
import sys

RESULTS = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else RESULTS
ORDER = ["ran", "needs arguments", "needs the camera", "error", "not reachable", "crashed or hung", "not called"]
HERE = os.path.dirname(os.path.abspath(__file__))

names = []
with open(os.path.join(HERE, "ar_functions.txt"), encoding="utf-8") as handle:
    for line in handle:
        if line.strip() and not line.startswith("#"):
            names.append(tuple((line.rstrip("\n").split("\t") + [""])[:2]))

calls = {}
with open(os.path.join(RESULTS, "step2_calls.jsonl"), encoding="utf-8") as handle:
    for line in handle:
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if record.get("phase") == "end":
            calls[record["fn"]] = record

dialogs = {}
path = os.path.join(RESULTS, "step2_dialogs.jsonl")
if os.path.exists(path):
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except ValueError:
                continue
            text = f"'{record.get('title')}': {' | '.join(record.get('texts', []))}"[:150]
            dialogs.setdefault(record.get("fn"), []).append(text)

rows = []
for name, section in names:
    record = calls.get(name, {})
    rows.append({"function": name, "section": section, "result": record.get("result", "not called"),
                 "detail": record.get("detail", ""), "dialog": " / ".join(dialogs.get(name, [])),
                 "ms": record.get("ms", ""), "prototype": record.get("doc", ""),
                 "changed": json.dumps(record["changed"]) if record.get("changed") else "",
                 "put_back": record.get("put_back", ""),
                 "back_as_before": {True: "yes", False: "no"}.get(record.get("back_as_before"), "")})

with open(os.path.join(OUT, "step2_functions.csv"), "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

sections = sorted({r["section"] for r in rows})
count = lambda rs, res: sum(r["result"] == res for r in rs)  # noqa: E731
used = [res for res in ORDER if count(rows, res)]
cell = lambda t: str(t).replace("|", "\\|").replace("\n", " ")  # noqa: E731
lines = ["# Step 2: every AR function, called", "",
         "Every macro function of NIS-Elements AR 7.01.03, called once through `nis.mac` with no",
         "arguments, microscope off. *ran*: it needed no arguments and ran. *needs arguments*: NIS",
         "answered \"Bad number of parameters\", so it is reachable but was not run. *dialog*: a",
         "window the call opened, closed by the watch window. Spreadsheet: `step2_functions.csv`.", "",
         "| Section | " + " | ".join(used) + " | Total |", "|---|" + "---:|" * (len(used) + 1)]
for section in sections:
    rs = [r for r in rows if r["section"] == section]
    lines.append(f"| [{section}](#{section.lower()}) | " + " | ".join(str(count(rs, u)) for u in used)
                 + f" | {len(rs)} |")
lines.append("| **All** | " + " | ".join(f"**{count(rows, u)}**" for u in used) + f" | **{len(rows)}** |")
for section in sections:
    lines += ["", f"## {section}", "", "| Function | Result | Answer | Dialog | Changed | Put back |", "|---|---|---|---|---|---|"]
    for r in (r for r in rows if r["section"] == section):
        lines.append(f"| `{r['function']}` | {r['result']} | {cell(r['detail'])[:120]} | {cell(r['dialog'])} | {cell(r['changed'])[:120]} | {cell(r['put_back'])} {r['back_as_before']} |")
with open(os.path.join(OUT, "STEP2_FUNCTIONS.md"), "w", encoding="utf-8") as handle:
    handle.write("\n".join(lines) + "\n")
print(f"{len(rows)} functions: " + ", ".join(f"{u} {count(rows, u)}" for u in used))
