# Step 0 results

## 2026-10-26: NIS-Elements AR 6.10.02, Ti2 simulator

One run, with all writes on. 26 of 27 checks passed; the one failure is the test's own
`nis.call_proc` probe (see below). Every NIS function the bridge calls works through ctypes.

### What the run settles

| Question | Answer |
|---|---|
| NIS and its Python | NIS-Elements 6.10.02 (Build 2031), Python 3.12.1 |
| ctypes on `g5_regprocs.dll` | **Works** for every function the bridge calls, except `Camera_ExposureSet` (not exported) |
| Does 6.10 have `nis.mac`? | **No.** `nis` has `call_proc`, `log`, `error`, `stdout_hook`, `stderr_hook`; no `mac`, no `ptr` |
| `nis.call_proc` | There, and it reaches `Camera_ExposureSet`. An out-argument wants a count or a sequence, not a number: `call_proc("StgGetPosXY", 0.0, 0.0)` fails with *Expected count (int) or sequence* |
| Is the ctypes name lookup real? | **Yes**: an unknown name does not resolve |
| Not exported by the DLL | `Camera_ExposureSet`, `Camera_ExposureGet`, `Int_ExecuteCommand` |
| Speed of one call | ctypes 0.003 ms median (max 0.024 ms) |

So the bridge needs two routes: ctypes (and `nis.call_proc` for the exposure) on 6.10, and
`nis.mac` on 7.01, which has no `nis.call_proc`.

### Readings (ctypes)

| Reading | Answer |
|---|---|
| XYZ | 39904.7, -13433.1, 500 µm |
| Limits | X -57000 to 57000, Y -37500 to 37500, Z 0 to 10000 µm |
| Optical configurations | 1: `Spinning Disk (2):BF` |
| Selected optical configuration | empty: `GetSelectedOptConf` returned 0, as on NIS 7 |
| Nosepiece | 6 positions, at 4. Names: 10x, 20x, 40x, 60x, 100x; **position 6 empty: name `""`, return DR_OK** |
| Perfect Focus | present, status 0 (off, in range) |
| Calibration | uncalibrated with no image open; 0.1084 µm/px (60x) after a capture |

### Writes (ctypes), each put back

| Write | Answer |
|---|---|
| `StgMoveXY` 10 µm and back | DR_OK; read back exactly; 0.19 s per move |
| `StgMoveZ` 1 µm and back | DR_OK; read back exactly |
| `StgMove` XYZ and back | DR_OK; read back exactly |
| `SelectOptConf` | skipped: only one optical configuration |
| `Camera_ExposureSet` 50 ms (`nis.call_proc`) | answered `[0, 50.0]`: return 0, value 50 |
| `Stg_SetNosepiecePosition` 4 → 5 → 4 | DR_OK; read back exactly |
| `Stg_SetPFSStatus` on, then off | on worked (status 1). **Off was not seen**: straight after, the status still read 1, and `Stg_WaitForPFS` returned at once. Perfect Focus may have been left on |
| `StgFocusInRangeEx` | skipped, because Perfect Focus was still on |
| `Capture`, `ImageSaveAs`, `CloseCurrentDocument` | image saved (8.6 MB TIFF); **`Capture` returned 0 (DR_CANCELED) although it worked**; `ImageSaveAs` and `CloseCurrentDocument` returned 0 |

### What this means for the bridge

- An empty nosepiece slot is an empty name with DR_OK, not an error (one of the two open
  questions in `docs/testing.md`; on the simulator).
- `Capture` returns 0 on success, so a check must only treat negative values as failure, as the
  bridge's `_check_negative` already does.
- Switching Perfect Focus off is not visible at once; the bridge already waits `PFS_SETTLE_S`.

### Changed in the test after this run

- The `nis.call_proc` probe now tries both forms the error asks for (a count, a sequence).
- Perfect Focus: the status is polled until it changes (up to 5 s), and the report says whether
  it was put back.
- Autofocus now runs before the Perfect Focus round trip, so it is not skipped.
- The coverage check found 1 name in NIS's function list: the name extraction did not match
  that file's format. Fixed: it now reads 4071 functions in 20 sections, 4041 of them in the AR
  edition (350 of those with a module), and reports reachability per section.
