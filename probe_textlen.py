# NIS-Elements 6.10 probe: does a bigger text buffer stop the crash?
# Text-plus-max-length functions (GetOptConfName, Stg_GetNosepieceObjectiveName) killed NIS within
# one to three calls with a 256 buffer and max length 64; Get_InfoStr (no max length) never did.
# Here: Stg_GetNosepieceObjectiveName 20 times with a 4096 buffer and max length 64, then 15 s idle.
import os, time, nis

HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
log_file = open(os.path.join(HERE, "results", "probe_textlen.log"), "a", encoding="utf-8")


def log(text):
    log_file.write(f"{time.strftime('%H:%M:%S')} {text}\n".encode("ascii", "backslashreplace").decode())
    log_file.flush()


BUFFER, MAX_LENGTH = 4096, 64
log(f"start: buffer {BUFFER}, max length {MAX_LENGTH}")
for attempt in range(20):
    position = attempt % 5 + 1
    log(f"call {attempt + 1}: Stg_GetNosepieceObjectiveName({position}, {BUFFER}, {MAX_LENGTH})")
    log(f"  -> {nis.call_proc('Stg_GetNosepieceObjectiveName', position, BUFFER, MAX_LENGTH)!r}")
for second in range(15):
    time.sleep(1)
    nis.call_proc("Stg_GetNosepiecePosition")
    log(f"alive after {second + 1} s")
log("done: no crash")
