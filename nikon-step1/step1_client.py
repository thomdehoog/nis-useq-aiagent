"""Step 1, the outside half: a program that is not NIS sends requests to step1_bridge.py.

Started by the bridge itself, with NIS's own python.exe, so nothing needs installing:

    python step1_client.py PORT

It runs the checks in step1_checks.py, asks the bridge to stop, checks that it did, and
writes results\\step1_client.txt. Exit code: the number of FAIL lines.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-26
License: MIT
"""

import os
import socket
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import step1_checks as checks  # noqa: E402

OUT = os.path.join(HERE, "results", "step1_client.txt")


def main(port):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    report = open(OUT, "w", encoding="utf-8")

    def write(text):
        report.write(text + "\n")
        report.flush()
        print(text, flush=True)

    print("=" * 78)
    print(" STEP 1 IS RUNNING. Leave NIS alone until this window says FINISHED.")
    print(" (At one point NIS is kept busy for 3 s on purpose.)")
    print("=" * 78, flush=True)

    write(f"step 1 client, {time.strftime('%Y-%m-%d %H:%M:%S')}, Python {sys.version.split()[0]}, "
          f"{sys.executable}, pid {os.getpid()}")
    out = []
    try:
        checks.run(port, out, outside=True, on_line=write)
        conn = checks.Connection(port)
        out.append(checks.check(conn, "shutdown", '{"op": "shutdown"}', True))
        write(out[-1])
        conn.close()
        time.sleep(3)
        try:
            socket.create_connection((checks.HOST, port), timeout=2).close()
            out.append("FAIL the bridge still answers 3 s after shutdown")
        except OSError:
            out.append("ok   the bridge is closed after shutdown")
        write(out[-1])
    except Exception as error:  # noqa: BLE001
        out.append(f"FAIL client stopped: {type(error).__name__}: {error}")
        write(out[-1])
    fails = sum(text.startswith("FAIL") for text in out)
    oks = sum(text.startswith("ok") for text in out)
    write(f"done: {oks} ok, {fails} FAIL")
    report.close()
    print()
    print("=" * 78)
    print(f" STEP 1 FINISHED: {oks} ok, {fails} FAIL. NIS can be used again.")
    print(f" Send the folder {os.path.dirname(OUT)}")
    print(" (and say whether NIS showed any dialog).")
    print("=" * 78, flush=True)
    if sys.stdin is not None and sys.stdin.isatty():
        try:
            input(" Press Enter to close this window. ")
        except EOFError:
            pass
    return fails


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 54471))
