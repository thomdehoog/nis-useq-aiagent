"""Offline test of step 1:  python nikon-step1-offline-test/run.py

Stands in for NIS: runs the three Python lines of step1.mac (start, pump in a loop on the
main thread, stop) against fake/nis.py. Everything else is the real thing: the self-test,
and the outside client the bridge starts by itself (here with this Python, as python.exe).
The folder is copied first, so no results land in the repository. Exit code: FAIL lines.
"""

import os
import re
import shutil
import socket
import sys
import tempfile
import time

TESTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TESTS, "fake"))
src = os.path.join(tempfile.mkdtemp(), "nikon-step1")
shutil.copytree(sys.argv[1] if len(sys.argv) > 1 else os.path.join(TESTS, "..", "nikon-step1"), src,
                ignore=shutil.ignore_patterns("results", "__pycache__"))

STOP = "C:/Users/Public/nikon-step1.stop"
STOP_LOCAL = os.path.join(os.path.dirname(src), "nikon-step1.stop")
os.environ["STEP1_STOP_FILE"] = STOP_LOCAL

macro = open(os.path.join(src, "step1.mac")).read()
first, pump_line, stop_line = (s.replace(STOP, STOP_LOCAL)
                               for s in re.findall(r'Python_RunString\("(.*)"\);', macro))
first = first.replace("'C:/nikon-step1/step1_bridge.py'", repr(os.path.join(src, "step1_bridge.py")), 1)

g = {"__name__": "__main__"}
exec(first, g)
t0 = time.time()
while not os.path.exists(STOP_LOCAL) and time.time() - t0 < 120:  # the macro loop
    exec(pump_line, g)
    time.sleep(0.01)
exec(stop_line, g)

results = os.path.join(src, "results")
summary = open(os.path.join(results, "step1_summary.txt")).read()
client_file = os.path.join(results, "step1_client.txt")
client = open(client_file).read() if os.path.exists(client_file) else "FAIL no step1_client.txt\n"
print(summary)
print("outside client:")
print(client)
try:
    socket.create_connection(("127.0.0.1", 54471), timeout=1).close()
    print("FAIL still listening after stop")
except OSError:
    print("ok   closed after stop")
print(f"stop file left: {os.path.exists(STOP_LOCAL)}; run took {time.time() - t0:.1f} s")
sys.exit(sum(x.startswith("FAIL") for x in (summary + client).splitlines()))
