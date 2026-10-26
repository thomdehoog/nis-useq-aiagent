"""A stand-in for NIS's `nis` module for step 2: functions by name, some missing, some with arguments."""


class error(Exception):
    pass


def log(text):
    print("nis.log:", text)


class _Mac:
    def __getattr__(self, name):
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
