# Step 1, run 4: 2026-10-26 17:55, NIS-Elements AR 7.01.03, microscope off

The first run of the version that runs by itself. **19 of 19 checks ok** from a program
outside NIS (`step1_client.txt`, copied from its window).

- **NIS ships its own `python.exe`:** `C:\Program Files\NIS-Elements\Python\python.exe`
  (3.12.4). The bridge started the client with it, as a separate program (pid 25016; NIS
  is pid 25448). So software outside NIS needs no Python of its own on this computer.
- Requests from outside reached NIS's Python, ran on NIS's own thread, and came back:
  readings, and every deliberate failure as an error reply (unknown function, a move
  refused, Python error, unknown op, broken request, wrong arguments).
- Two connections at once, and a client leaving mid-request: fine.
- Round trip 10.9 ms median (max 11.5 ms), set by the macro loop's `Wait(0.01)`.
- NIS held busy for 3 s, then answering again at once.
- Stop on request: the bridge closed, and the macro ended by itself.
- Same NIS session as runs 1 to 3 (pid 25448).

- From the summary and log: the whole run took 15.2 s; 231 requests, 0 timeouts, 0 pump
  errors; all 265 passes of the macro loop on NIS's own thread; the self-test also 14 of 14
  ok. The only dialog: the macro's own `WaitText` message ("Continue") at the start. No
  error dialog, no crash.
- Python inside NIS: `sys.executable` is `nis_ar.exe`, `sys.base_prefix` is
  `C:\Program Files\NIS-Elements\Python`, where `python.exe` is.

**Step 1 answered: yes.** Software outside NIS can call NIS functions through NIS's own
Python, with every error coming back as a reply, and without NIS crashing or showing an
error. Not yet tested: with the microscope on, and calls that move or capture.
