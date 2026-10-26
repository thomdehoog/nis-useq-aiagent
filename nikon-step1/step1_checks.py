"""Step 1: the checks a client sends to step1_bridge.py, shared by both clients.

The self-test (a thread inside NIS's Python) and step1_client.py (a program outside NIS,
started by the bridge) run the same list, so their answers can be compared line by line.
Each check is (name, request, should the reply be ok?). Checks that should *not* be ok are
deliberate failures: they pass when the failure comes back as a reply, not as a dialog or
a crash.

Standard library only.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-26
License: MIT
"""

import json
import socket
import time

HOST = "127.0.0.1"
UNKNOWN = "ThisFunctionDoesNotExist_Step1"  # the bridge lets this through to nis.mac on purpose
Z = {"op": "call", "fn": "StgGetPosZ", "args": [{"ptr": "double"}, 0]}

CHECKS = [
    ("ping", {"op": "ping"}, True),
    ("NIS version", {"op": "call", "fn": "Get_InfoStr", "args": [1, {"ptr": "char"}]}, True),
    ("Z position", Z, True),
    ("XY position (not there without hardware)",
     {"op": "call", "fn": "StgGetPosXY", "args": [{"ptr": "double"}, {"ptr": "double"}]}, True),
    ("optical configurations", {"op": "call", "fn": "GetOptConfCount", "args": []}, True),
    ("PFS status", {"op": "call", "fn": "Stg_GetPFSStatus", "args": []}, True),
    ("unknown function", {"op": "call", "fn": UNKNOWN, "args": []}, False),
    ("function not on the list (a move)", {"op": "call", "fn": "StgMoveZ", "args": [0, 0]}, False),
    ("Python error", {"op": "raise"}, False),
    ("unknown op", {"op": "fly"}, False),
]
# Last, because it hands NIS's own code a wrong value: if anything crashes NIS, it is this.
LAST_CHECKS = [
    ("wrong arguments", {"op": "call", "fn": "StgGetPosZ", "args": ["text"]}, False),
    ("ping after wrong arguments", {"op": "ping"}, True),
]


class Connection:
    """One connection to the bridge; send() takes a request line and returns the reply."""

    def __init__(self, port, timeout=40.0):
        self.sock = socket.create_connection((HOST, port), timeout=timeout)
        self.stream = self.sock.makefile("rwb")

    def send(self, line):
        self.stream.write(line.encode("utf-8") + b"\n")
        self.stream.flush()
        reply = self.stream.readline()
        if not reply:
            raise ConnectionError("the bridge closed the connection")
        return json.loads(reply)

    def close(self):
        try:
            self.stream.close()
        finally:
            self.sock.close()


def line(passed, name, ms, text):
    text = text if len(text) <= 200 else text[:200] + " ..."
    ms_text = f"{ms:>8.1f} ms" if ms is not None else " " * 11
    return f"{'ok  ' if passed else 'FAIL'} {name:<42} {ms_text}  {text}"


def check(conn, name, raw, want_ok):
    started = time.perf_counter()
    try:
        reply = conn.send(raw)
    except Exception as error:  # noqa: BLE001 - no reply is a finding too
        return line(False, name, None, f"no reply: {type(error).__name__}: {error}")
    ms = 1000 * (time.perf_counter() - started)
    text = json.dumps(reply.get("answer"), default=repr) if reply.get("ok") else str(reply.get("error"))
    return line(reply.get("ok") is want_ok, name, ms, text)


def run(port, out, outside=False, on_line=None):
    """Run every check through a new connection; append one line per check to ``out``."""

    def add(text):
        out.append(text)
        if on_line:
            on_line(text)

    conn = Connection(port)
    try:
        for name, request, want_ok in CHECKS:
            add(check(conn, name, json.dumps(request), want_ok))
        add(check(conn, "broken request", "this is not json", False))

        times = []
        for _ in range(100):
            started = time.perf_counter()
            conn.send(json.dumps(Z))
            times.append(1000 * (time.perf_counter() - started))
        times.sort()
        add(f"ok   100 x Z position, round trip: median {times[50]:.1f} ms, max {times[-1]:.1f} ms")

        if outside:
            try:  # two programs at once
                second = Connection(port)
                add(check(second, "second connection at the same time", '{"op": "ping"}', True))
                second.close()
            except OSError as error:
                add(line(False, "second connection at the same time", None, str(error)))
            try:  # a client that leaves before its reply
                leaver = Connection(port)
                leaver.stream.write(b'{"op": "hold", "seconds": 1}\n')
                leaver.stream.flush()
                leaver.close()
                time.sleep(1.5)
                add(check(conn, "ping after a client left mid-request", '{"op": "ping"}', True))
            except OSError as error:
                add(line(False, "client leaving mid-request", None, str(error)))
            add(check(conn, "NIS busy for 3 s (hold)", '{"op": "hold", "seconds": 3}', True))

        for name, request, want_ok in LAST_CHECKS:
            add(check(conn, name, json.dumps(request), want_ok))
    finally:
        conn.close()
