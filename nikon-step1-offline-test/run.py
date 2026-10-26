"""Offline test of step 1: python nikon-step1-offline-test/run.py

Stand-in for step1.mac: the same Python strings, a main-thread loop, then a client like step1_client.ps1."""
import os, sys, json, socket, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fake"))
import shutil, tempfile
src = os.path.join(tempfile.mkdtemp(), "nikon-step1")
shutil.copytree(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "nikon-step1"), src, ignore=shutil.ignore_patterns("results"))
STOP = "C:/Users/Public/nikon-step1.stop"
mac = open(os.path.join(src, "step1.mac")).read()
import re
lines = re.findall(r'Python_RunString\("(.*)"\);', mac)
first, pump_line, stop_line = lines
first = first.replace("'C:/nikon-step1/step1_bridge.py'", repr(os.path.join(src, "step1_bridge.py")), 1)
# the stop file path is Windows-only; map it to a local one
STOP_LOCAL = "/tmp/nikon-step1.stop"
os.environ["STEP1_STOP_FILE"] = STOP_LOCAL
fix = lambda s: s.replace(STOP, STOP_LOCAL)
g = {"__name__": "__main__"}
exec(fix(first), g)
m = sys.modules["step1_bridge"]
m.STOP_FILE = STOP_LOCAL
client_out = []
def client():
    time.sleep(3)  # after the self-test
    c = socket.create_connection(("127.0.0.1", 54471)); f = c.makefile("rwb")
    def send(line, fh=f):
        fh.write(line.encode() + b"\n"); fh.flush(); return json.loads(fh.readline())
    for line, want in [('{"op": "ping"}', True), ('{"op": "call", "fn": "Get_InfoStr", "args": [1, {"ptr": "char"}]}', True),
        ('{"op": "call", "fn": "ThisFunctionDoesNotExist_Step1", "args": []}', False), ('{"op": "call", "fn": "StgMoveZ", "args": [0, 0]}', False),
        ('this is not json', False), ('{"op": "raise"}', False)]:
        r = send(line); client_out.append(("ok  " if r["ok"] is want else "FAIL") + " " + line + " -> " + json.dumps(r)[:120])
    c2 = socket.create_connection(("127.0.0.1", 54471)); f2 = c2.makefile("rwb")
    f2.write(b'{"op": "hold", "seconds": 1}\n'); f2.flush(); c2.close()
    time.sleep(1.5)
    r = send('{"op": "ping"}'); client_out.append(("ok  " if r["ok"] else "FAIL") + " ping after leaver")
    r = send('{"op": "call", "fn": "StgGetPosZ", "args": ["text"]}'); client_out.append(("ok  " if not r["ok"] else "FAIL") + " wrong args -> " + r.get("error",""))
    r = send('{"op": "shutdown"}'); client_out.append(("ok  " if r["ok"] else "FAIL") + " shutdown")
threading.Thread(target=client, daemon=True).start()
t0 = time.time()
while not os.path.exists(STOP_LOCAL) and time.time() - t0 < 60:
    exec(fix(pump_line), g); time.sleep(0.01)
exec(fix(stop_line), g)
print("\n".join(client_out))
print(open(os.path.join(src, "results", "step1_summary.txt")).read())
time.sleep(0.5)
try: socket.create_connection(("127.0.0.1", 54471), timeout=1); print("FAIL still listening")
except OSError: print("ok   closed after stop")
print("stop file left:", os.path.exists(STOP_LOCAL))
