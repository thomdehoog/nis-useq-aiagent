"""A stand-in for NIS's `nis` module for step 2: functions by name, some missing, some with arguments."""


class error(Exception):
    pass


def log(text):
    print("nis.log:", text)


_state = {"panel": 0}


class _Mac:
    def __getattr__(self, name):
        if name == "GetPanel":
            return lambda: _state["panel"]
        if name == "TogglePanel":
            def toggle():
                _state["panel"] ^= 1
            return toggle
        if name == "ShowThing":
            def show():
                _state["panel"] = 5
            return show
        if name.startswith("Camera"):  # absent without a camera, as in step 0
            raise AttributeError(f"'Macro' object has no attribute '{name}'")
        if name == "CRASH_ME":
            raise SystemExit("simulated crash")

        def function(*args):
            if name.startswith(("Get", "Stg")):
                return 1
            if name.startswith("Fail"):
                raise error("Function failed")
            raise error("Bad number of parameters")
        function.__doc__ = f"int {name}(...)"
        return function


mac = _Mac()
