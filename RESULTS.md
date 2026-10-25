# Step 0 results

## 2026-10-25: NIS-Elements 7.01.03, without hardware

Two runs on the microscope computer, both on purpose without the microscope switched on: the
first with NIS started as `-passive`, the second with the test's fixes (timing per route, plain
return values). All 25 checks of the second run passed.

### How many functions can our Python call?

| | Number |
|---|---|
| Macro functions the AR edition includes | 3667 |
| **Reachable by name through `nis.mac`, without hardware** | **3089 (84 %)** |
| Called by the test and confirmed working | about 20 (the readings below) |
| Not reachable without hardware | 578 |

Every function with its answer, by section: [FUNCTIONS.md](FUNCTIONS.md) (as a spreadsheet:
`functions.csv`).

The 578 fall into four groups:

- **Camera, live and ROI** (`CameraSet_Exposure`, `Live`, `ROISet` …): NIS makes these only when
  a camera is connected. Expected to come with the hardware on.
- **Hardware this system does not have:** confocal (A1, AX), TIRF, water dispenser, STORM.
- **Modules:** NIS.ai, hardness, welding, SIM, HCA and others, probably not licensed or installed.
- **The Nk libraries** (NkSocket, NkWindow, NkComPort, NkString): available once a macro has
  loaded them with `import("….dll")`.

### What else the runs settle

| Question | Answer |
|---|---|
| NIS and its Python | NIS-Elements 7.01.03 (Build 2233), Python 3.12.4 |
| Does `nis.mac` work from our Python, outside a JOB? | **Yes**, with the same values as ctypes |
| Is the name lookup real? | **Yes**: an unknown name raises `AttributeError` |
| `nis.call_proc` (used by the bridge on NIS 6.10) | **Gone in 7.01**: `nis` has `mac`, `ptr`, `log`, `error`, `stdout_hook`, `stderr_hook` |
| `nis.ptr` types | byte, char, char8, double, dword, int, int64, long, short, word |
| Speed of one call | `nis.mac` 0.006 ms median (max 0.027 ms), ctypes 0.003 ms, on a reading that answered at once |

### Readings without hardware

| Reading | Answer |
|---|---|
| Z | 250 µm, limits 0 to 500 µm |
| XY | not available (-4) |
| Optical configurations | 3: `Eyepiece - EPI:Eye DAPI`, `Eyepiece - EPI:Eye GFP`, `Eyepiece - EPI:Eye BF` |
| Selected optical configuration | empty (`GetSelectedOptConf` returned 0) |
| Nosepiece, Perfect Focus | not present |
| Calibration | uncalibrated |

### Next

1. With the hardware on, all writes off: the camera functions in the coverage, the real readings,
   and why `GetSelectedOptConf` comes back empty.
2. Then each write on its own: XY and Z there and back, optical configuration, capture, save and
   close.
