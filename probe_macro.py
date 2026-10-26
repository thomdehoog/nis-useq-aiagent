# NIS-Elements 6.10 probe: can NIS's macro language make the calls that fail through nis.call_proc?
# Through call_proc, numbers handed back (double *) fail with a dialog, and texts handed back with a
# max length (GetOptConfName, Stg_GetNosepieceObjectiveName) kill NIS within a few calls. Here Python
# only writes a small macro file and runs it with RunMacro (a text in); the macro makes the call
# itself and leaves the answer in a global variable (read back with GetVariableValue, a text in and
# a number out) or in a file (read by Python). Steps go from harmless to the calls that crashed.
import os, time, nis

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
OUT = HERE + "/results"
os.makedirs(OUT, exist_ok=True)
MACRO = OUT + "/probe_macro_step.mac"
TEXT_FILE = OUT + "/probe_macro_text.bin"
log_file = open(OUT + "/probe_macro.log", "a", encoding="utf-8")


def log(text):
    line = f"{time.strftime('%H:%M:%S')} {text}"
    log_file.write(line.encode("ascii", "backslashreplace").decode() + "\n")
    log_file.flush()


def call(name, *args):
    """nis.call_proc, logged; a refusal is logged and handed back as the answer."""
    try:
        out = nis.call_proc(name, *args)
    except Exception as error:  # noqa: BLE001
        out = f"{type(error).__name__}: {error}"
    log(f"  {name}{args!r} -> {out!r}")
    return out


def run_macro(text):
    """Write text to a macro file and run it through RunMacro."""
    with open(MACRO, "w", encoding="utf-8") as handle:
        handle.write(text)
    return call("RunMacro", MACRO)


def number(name):
    out = call("GetVariableValue", name)
    return out[0] if isinstance(out, (list, tuple)) else out


def text_from_file():
    """The text a macro wrote with WriteFile: 8-bit or 16-bit characters, zeros dropped."""
    try:
        data = open(TEXT_FILE, "rb").read()
    except OSError as error:
        return f"no file: {error}"
    os.remove(TEXT_FILE)
    wide = len(data) > 1 and data[1:2] == b"\0"
    return (data.decode("utf-16-le", "replace") if wide else data.decode("utf-8", "replace")).split("\0")[0]


def step(title, function):
    log(f"STEP {title}")
    try:
        log(f"  answer: {function()!r}")
    except Exception as error:  # noqa: BLE001
        log(f"  failed: {type(error).__name__}: {error}")


def plain_global():
    run_macro("global double step0_a;\nstep0_a = 2.5;\n")
    return number("step0_a")


def stage_xy():
    run_macro("global double step0_x, step0_y;\nStgGetPosXY(&step0_x, &step0_y);\n")
    return number("step0_x"), number("step0_y")


def stage_z_and_limits():
    run_macro("global double step0_z, step0_x0, step0_y0, step0_x1, step0_y1;\n"
              "StgGetPosZ(&step0_z, 0);\n"
              "StgXY_GetLimits(&step0_x0, &step0_y0, &step0_x1, &step0_y1);\n")
    return {n: number("step0_" + n) for n in ("z", "x0", "y0", "x1", "y1")}


def text_macro(call_text):
    run_macro("char step0_t[256];\nstep0_t[0] = 0;\n" + call_text +
              f'\nWriteFile("{TEXT_FILE}", step0_t, 2 * strlen(step0_t));\n')
    return text_from_file()


log(f"start, NIS {call('Get_InfoStr', 1, 256)!r}")
step("a global variable set by a macro", plain_global)
step("StgGetPosXY in a macro", stage_xy)
step("StgGetPosZ and StgXY_GetLimits in a macro", stage_z_and_limits)
step("GetOptConfName in a macro", lambda: text_macro("GetOptConfName(0, step0_t, 255);"))
for attempt in range(20):  # through call_proc this killed NIS within 2 to 6 calls
    position = attempt % 5 + 1
    step(f"Stg_GetNosepieceObjectiveName({position}) in a macro, {attempt + 1} of 20",
         lambda: text_macro(f"Stg_GetNosepieceObjectiveName({position}, step0_t, 255);"))
for second in range(15):
    time.sleep(1)
    log(f"alive after {second + 1} s, objective {call('Stg_GetNosepiecePosition')!r}")
log("done: no crash")
