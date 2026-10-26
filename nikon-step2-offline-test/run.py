"""Offline test of step 2:  python nikon-step2-offline-test/run.py

Runs step2.mac's Python lines against fake/nis.py on a short function list: a first run that
"crashes" in one function (the process ends there), a second run that carries on after it.
Exit code: 0 when every function has exactly one answer and the crash is noted.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

TESTS = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(TESTS, "..", "nikon-step2")

if len(sys.argv) > 1 and sys.argv[1] == "--macro":  # one run of the macro, in its own process
    work = sys.argv[2]
    sys.path.insert(0, os.path.join(TESTS, "fake"))
    stop = os.path.join(work, "stop")
    os.environ["STEP2_STOP_FILE"] = stop
    os.environ["STEP2_WATCH"] = "0"
    first, pump, last = (s.replace("C:/Users/Public/nikon-step2.stop", stop)
                         for s in re.findall(r'Python_RunString\("(.*)"\);', open(os.path.join(work, "step2.mac")).read()))
    first = first.replace("'C:/nikon-step2/step2_calls.py'", repr(os.path.join(work, "step2_calls.py")), 1)
    g = {"__name__": "__main__"}
    exec(first, g)
    while not os.path.exists(stop):
        exec(pump, g)
    exec(last, g)
    sys.exit(0)

work = os.path.join(tempfile.mkdtemp(), "nikon-step2")
shutil.copytree(SRC, work, ignore=shutil.ignore_patterns("results", "__pycache__"))
names = ["GetA", "StgB", "SetC", "FailD", "CameraE", "CRASH_ME", "GetF", "RunMacroG", "ExitH", "GetPanel", "TogglePanel", "ShowThing"]
with open(os.path.join(work, "ar_functions.txt"), "w") as handle:
    handle.write("# test list\n" + "".join(f"{n}\tTest\n" for n in names))
src = open(os.path.join(work, "step2_calls.py")).read()
# the simulated crash: SystemExit from getattr ends the process, as a NIS crash would
open(os.path.join(work, "step2_calls.py"), "w").write(src.replace(
    "    try:\n        function = getattr(nis.mac, name)",
    "    if name == 'CRASH_ME':\n        write({'fn': name, 'phase': 'start'})\n        os._exit(3)\n"
    "    try:\n        function = getattr(nis.mac, name)"))
first = subprocess.run([sys.executable, __file__, "--macro", work]).returncode
second = subprocess.run([sys.executable, __file__, "--macro", work]).returncode
records = [json.loads(l) for l in open(os.path.join(work, "results", "step2_calls.jsonl"))]
ends = {r["fn"]: r for r in records if r.get("phase") == "end"}
order = [r["fn"] for r in records if r.get("phase") == "end"]
for name in names:
    r = ends.get(name, {})
    print(f"{name:<12} {r.get('result', 'MISSING'):<16} {r.get('detail', '')} {r.get('changed', '')} {r.get('put_back', '')} {r.get('back_as_before', '')}")
print("order:", order)
print(open(os.path.join(work, "results", "step2_summary.txt")).read())
ok = (first == 3 and second == 0 and set(ends) == set(names) and len(order) == len(names)
      and ends["CRASH_ME"]["result"] == "crashed or hung" and order[-2:] == ["RunMacroG", "ExitH"]
      and ends["TogglePanel"].get("back_as_before") is True
      and ends["ShowThing"].get("changed") == {"GetPanel": ["0", "5"]})
print("PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
