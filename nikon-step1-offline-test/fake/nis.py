"""A stand-in for NIS's `nis` module: nis.mac by name, nis.ptr types, nis.log."""
class _Ptr:
    def __init__(self, v): self._v = v
    def get(self): return self._v
    def set(self, v): self._v = v
class ptr:
    double = staticmethod(lambda: _Ptr(0.0)); char = staticmethod(lambda: _Ptr(""))
    int = staticmethod(lambda: _Ptr(0))
def _getz(z, flag):
    if not isinstance(z, _Ptr): raise TypeError("argument 1 must be nis.ptr.double")
    z.set(250.0); return 1
def _info(i, t): t.set("7.01.03 (Build 2233)"); return 1
class _Mac:
    StgGetPosZ = staticmethod(_getz); Get_InfoStr = staticmethod(_info)
    StgGetPosXY = staticmethod(lambda x, y: -4); GetOptConfCount = staticmethod(lambda: 3)
    Stg_GetPFSStatus = staticmethod(lambda: -1)
    def __getattr__(self, n): raise AttributeError(f"no macro function {n}")
mac = _Mac()
logged = []
def log(t): logged.append(t); print("nis.log:", t)
