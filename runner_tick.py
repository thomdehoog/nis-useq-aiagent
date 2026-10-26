# One pass of the step0 runner, called over and over by step0_runner.mac on NIS's main thread.
# If runner\request.txt names a script, run it here (inside NIS, as if its macro had been run
# by hand) and write runner\done.txt. Lets a script outside NIS run the step0 scripts one
# after the other without anyone at the keyboard.
import os, runpy, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
INBOX = os.path.join(HERE, "runner")
REQUEST = os.path.join(INBOX, "request.txt")
os.makedirs(INBOX, exist_ok=True)


def note(text):
    with open(os.path.join(INBOX, "runner.log"), "a", encoding="utf-8") as handle:
        handle.write(f"{time.strftime('%H:%M:%S')} {text}\n")


if os.path.exists(REQUEST):
    with open(REQUEST, encoding="utf-8") as handle:
        script = handle.read().strip()
    os.replace(REQUEST, os.path.join(INBOX, "running.txt"))
    for name in ("done.txt",):
        if os.path.exists(os.path.join(INBOX, name)):
            os.remove(os.path.join(INBOX, name))
    note(f"run {script}")
    started = time.perf_counter()
    outcome = "ok"
    try:
        path = script if os.path.isabs(script) else os.path.join(HERE, script)
        os.environ["STEP0_HERE"] = os.path.dirname(path)
        runpy.run_path(path, run_name="__main__")
    except BaseException:  # noqa: BLE001 - report everything, keep the runner alive
        outcome = traceback.format_exc(limit=5)
    seconds = round(time.perf_counter() - started, 1)
    note(f"end {script}: {outcome.splitlines()[-1] if outcome != 'ok' else 'ok'} ({seconds} s)")
    with open(os.path.join(INBOX, "done.txt"), "w", encoding="utf-8") as handle:
        handle.write(f"{script}\n{seconds} s\n{outcome}\n")
    os.remove(os.path.join(INBOX, "running.txt"))
