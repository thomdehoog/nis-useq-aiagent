# NIS-Elements 6.10.02: the functions we can run

Every macro function our Python called for real on the Ti2 simulator (2026-10-26) and that worked: `step0_test.py` (the bridge's functions) and `step0_calls.py` (the hardware functions). Made by `make_function_table.py`. About 3000 more are reachable but not called yet: they need an image, a file or a set-up (RESULTS.md).

- **Fastest route**: *DLL* = exported by g5_regprocs.dll (ctypes, about 0.003 ms); *call_proc* = only through `nis.call_proc`, values going in (about 0.5 ms); *macro* = only through `nis.call_proc`, and it hands a value back, so inside a NIS macro (about 20 ms).
- **Result**: *works* = answered with a value; *set, read back* = set to the value it had and read back unchanged; *changed and put back* = set to another position or state, read back, and set back.

| Category | Can run | Through the DLL | Only through `nis.call_proc` |
|---|---|---|---|
| Camera | 43 | 1 | 42 |
| Condenser, aperture, zoom, light path | 22 | 22 | 0 |
| Confocal, A1, AX, C2, galvo | 1 | 0 | 1 |
| DMD and patterns | 8 | 7 | 1 |
| Filters | 19 | 19 | 0 |
| Incubator and heating | 12 | 7 | 5 |
| Lights and lasers | 36 | 35 | 1 |
| Objectives and nosepiece | 11 | 11 | 0 |
| Optical configurations | 3 | 3 | 0 |
| Other devices | 8 | 7 | 1 |
| Perfect Focus and autofocus | 15 | 13 | 2 |
| Shutters | 15 | 12 | 3 |
| Slide loader | 14 | 14 | 0 |
| Stage XY | 25 | 25 | 0 |
| Stage Z | 23 | 23 | 0 |
| TIRF | 7 | 7 | 0 |
| Triggers and TTL | 9 | 5 | 4 |
| AdvancedAPI | 1 | 0 | 1 |
| ImageDocument | 2 | 2 | 0 |
| Macro | 2 | 2 | 0 |
| System | 3 | 3 | 0 |
| **Total** | **279** | **218** | **61** |

### Camera

| Function | Fastest route | Result |
|---|---|---|
| `CameraFormatGet` | macro | works |
| `CameraFormatSet` | call_proc | set, read back |
| `CameraGet_Average` | macro | works |
| `CameraGet_AverageCH` | macro | works |
| `CameraGet_AverageToQuality` | macro | works |
| `CameraGet_AverageToQualityCH` | macro | works |
| `CameraGet_FlexibleHeight` | macro | works |
| `CameraGet_HWTrgOutEnabled` | macro | works |
| `CameraGet_Integrate` | macro | works |
| `CameraGet_IntegrateCH` | macro | works |
| `CameraGet_IntegrateToQualityCH` | macro | works |
| `CameraGet_Negate` | macro | works |
| `CameraGet_Rotate` | macro | works |
| `CameraSet_Average` | call_proc | set, read back |
| `CameraSet_AverageToQuality` | call_proc | set, read back |
| `CameraSet_FlexibleHeight` | call_proc | set, read back |
| `CameraSet_Integrate` | call_proc | set, read back |
| `CameraSet_Negate` | call_proc | set, read back |
| `CameraSet_Rotate` | call_proc | set, read back |
| `Camera_AngleGet` | macro | works |
| `Camera_AverageGet` | macro | works |
| `Camera_AverageSet` | call_proc | set, read back |
| `Camera_ExposureGet` | macro | works |
| `Camera_ExposureSet` | call_proc | works |
| `Camera_IntegrateGet` | macro | works |
| `Camera_IntegrateSet` | call_proc | set, read back |
| `Camera_RelayLensGet` | macro | works |
| `Camera_RelayLensSet` | call_proc | set, read back |
| `Camera_RotateGet` | macro | works |
| `Camera_RotateSet` | call_proc | set, read back |
| `Camera_TriggerModeGet` | macro | works |
| `Camera_TriggerModeSet` | call_proc | set, read back |
| `Capture` | DLL | works |
| `GetActiveGrabber` | call_proc | works |
| `GetActiveGrabberCount` | call_proc | works |
| `GetCameraName` | macro | works |
| `GetCameraResolution` | macro | works |
| `GetCurrentCameraDriverName` | macro | works |
| `GetCurrentCameraName` | macro | works |
| `GetShadingEnabled` | call_proc | works |
| `ROIGet` | macro | works |
| `ROISet` | call_proc | set, read back |
| `SetActiveGrabber` | call_proc | set, read back |

### Condenser, aperture, zoom, light path

| Function | Fastest route | Result |
|---|---|---|
| `Stg_GetAnalyzerState` | DLL | works |
| `Stg_GetAperturePosition` | DLL | works |
| `Stg_GetApertureStepPosition` | DLL | works |
| `Stg_GetApertureSteps` | DLL | works |
| `Stg_GetCondenserPosition` | DLL | works |
| `Stg_GetCondenserPositions` | DLL | works |
| `Stg_GetDiskSpeed` | DLL | works |
| `Stg_GetRelayLensPosition` | DLL | works |
| `Stg_GetZoomPosition` | DLL | works |
| `Stg_GetZoomStepPosition` | DLL | works |
| `Stg_GetZoomSteps` | DLL | works |
| `Stg_IsAnalyzerPresent` | DLL | works |
| `Stg_IsAperturePresent` | DLL | works |
| `Stg_IsCondenserPresent` | DLL | works |
| `Stg_IsZoomManual` | DLL | works |
| `Stg_IsZoomPresent` | DLL | works |
| `Stg_SetAnalyzerState` | DLL | set, read back |
| `Stg_SetAperturePosition` | DLL | changed and put back |
| `Stg_SetCondenserPosition` | DLL | changed and put back |
| `Stg_SetDiskSpeed` | DLL | set, read back |
| `Stg_SetRelayLensPosition` | DLL | set, read back |
| `Stg_SetZoomPosition` | DLL | set, read back |

### Confocal, A1, AX, C2, galvo

| Function | Fastest route | Result |
|---|---|---|
| `ACC_GetCorrectedStack` | macro | works |

### DMD and patterns

| Function | Fastest route | Result |
|---|---|---|
| `IsPatternDefined` | DLL | works |
| `Stg_GetDMDActivePatternId` | macro | works |
| `Stg_GetDMDDeviceCount` | DLL | works |
| `Stg_GetDMDDeviceName` | DLL | works |
| `Stg_GetDMDPatternCount` | DLL | works |
| `Stg_GetDMDPatternId` | DLL | works |
| `Stg_GetDMDPatternIdByName` | DLL | works |
| `Stg_GetDMDPatternName` | DLL | works |

### Filters

| Function | Fastest route | Result |
|---|---|---|
| `Stg_Filter_GetCount` | DLL | works |
| `Stg_Filter_GetName` | DLL | works |
| `Stg_Filter_GetPosition` | DLL | works |
| `Stg_Filter_GetPositionCount` | DLL | works |
| `Stg_Filter_GetPositionName` | DLL | works |
| `Stg_GetFilterName` | DLL | works |
| `Stg_GetFilterPosition` | DLL | works |
| `Stg_GetFilterPositions` | DLL | works |
| `Stg_GetNDFilterPosition` | DLL | works |
| `Stg_GetNDFilterStepPosition` | DLL | works |
| `Stg_GetNDFilterSteps` | DLL | works |
| `Stg_IsFilterPresent` | DLL | works |
| `Stg_IsNDFilterPresent` | DLL | works |
| `Stg_Light_GetNDFilterControllable` | DLL | works |
| `Stg_Light_GetNDFilterPosition` | DLL | works |
| `Stg_Light_GetNDFilterStepPosition` | DLL | works |
| `Stg_Light_GetNDFilterSteps` | DLL | works |
| `Stg_SetFilterPosition` | DLL | changed and put back |
| `Stg_SetNDFilterPosition` | DLL | set, read back |

### Incubator and heating

| Function | Fastest route | Result |
|---|---|---|
| `Stg_HeatStageGetCurrentTemperature` | DLL | works |
| `Stg_HeatStageGetStatus` | DLL | works |
| `Stg_HeatStage_GetCount` | DLL | works |
| `Stg_HeatStage_GetCurrentTemperature` | DLL | works |
| `Stg_HeatStage_GetName` | DLL | works |
| `Stg_HeatStage_GetStatus` | DLL | works |
| `Stg_Incubator_GetCurrentGas` | macro | works |
| `Stg_Incubator_GetCurrentPressure` | macro | works |
| `Stg_Incubator_GetPressureRange` | macro | works |
| `Stg_Incubator_GetTargetGas` | macro | works |
| `Stg_Incubator_GetTargetPressure` | macro | works |
| `Stg_Perfusion_GetState` | DLL | works |

### Lights and lasers

| Function | Fastest route | Result |
|---|---|---|
| `Stg_GetDMDAssociatedLightId` | macro | works |
| `Stg_GetLaserOutputNumPorts` | DLL | works |
| `Stg_GetLaserOutputPortUsed` | DLL | works |
| `Stg_GetLaserOutputPortUsedEx` | DLL | works |
| `Stg_GetLightIrisIntensity` | DLL | works |
| `Stg_GetLightIrisIntensitySteps` | DLL | works |
| `Stg_GetLightIrisSteps` | DLL | works |
| `Stg_GetLightStepVoltage` | DLL | works |
| `Stg_GetLightVoltage` | DLL | works |
| `Stg_GetLightVoltageSteps` | DLL | works |
| `Stg_GetMultiLaserCount` | DLL | works |
| `Stg_GetMultiLaserLineName` | DLL | works |
| `Stg_GetMultiLaserLineUsed` | DLL | works |
| `Stg_GetMultiLaserName` | DLL | works |
| `Stg_GetMultiLaserNumLines` | DLL | works |
| `Stg_GetMultiLaserOpMode` | DLL | works |
| `Stg_GetMultiLaserPower` | DLL | works |
| `Stg_GetMultiLaserPowerSteps` | DLL | works |
| `Stg_GetMultiLaserStepPower` | DLL | works |
| `Stg_GetMultiLaserWavelength` | DLL | works |
| `Stg_IsLightPresent` | DLL | works |
| `Stg_Light_GetCount` | DLL | works |
| `Stg_Light_GetIrisIntensity` | DLL | works |
| `Stg_Light_GetIrisSteps` | DLL | works |
| `Stg_Light_GetName` | DLL | works |
| `Stg_Light_GetRemoteSwitch` | DLL | works |
| `Stg_Light_GetState` | DLL | works |
| `Stg_Light_GetStepIrisIntensity` | DLL | works |
| `Stg_Light_GetStepVoltage` | DLL | works |
| `Stg_Light_GetVoltage` | DLL | works |
| `Stg_Light_GetVoltageSteps` | DLL | works |
| `Stg_Light_IsIrisControllable` | DLL | works |
| `Stg_Light_IsVoltageControllable` | DLL | works |
| `Stg_SetLaserOutputPortUsed` | DLL | set, read back |
| `Stg_SetLightIrisIntensity` | DLL | set, read back |
| `Stg_SetLightVoltage` | DLL | set, read back |

### Objectives and nosepiece

| Function | Fastest route | Result |
|---|---|---|
| `GetCurrentObjMagnification` | DLL | works |
| `GetObjMagnification` | DLL | works |
| `GetObjType` | DLL | works |
| `Stg_GetNosepieceObjectiveCode` | DLL | works |
| `Stg_GetNosepieceObjectiveName` | DLL | works |
| `Stg_GetNosepieceObjectiveRefractiveIndex` | DLL | works |
| `Stg_GetNosepiecePosition` | DLL | works |
| `Stg_GetNosepiecePositions` | DLL | works |
| `Stg_GetObjectiveNameFromCode` | DLL | works |
| `Stg_IsNosepiecePresent` | DLL | works |
| `Stg_SetNosepiecePosition` | DLL | changed and put back |

### Optical configurations

| Function | Fastest route | Result |
|---|---|---|
| `GetOptConfCount` | DLL | works |
| `GetOptConfName` | DLL | works |
| `GetSelectedOptConf` | DLL | works |

### Other devices

| Function | Fastest route | Result |
|---|---|---|
| `GetCurrentObjName` | DLL | works |
| `GetFollowExposureMode` | macro | works |
| `Stg_GetMicroscopeSleep` | DLL | works |
| `Stg_IsMicroscopePresent` | DLL | works |
| `Stg_IsMouseJoystickZ` | DLL | works |
| `Stg_IsStatusStored` | DLL | works |
| `Stg_LinearActuator_GetDescription` | DLL | works |
| `Stg_LinearActuator_GetPosition` | DLL | works |

### Perfect Focus and autofocus

| Function | Fastest route | Result |
|---|---|---|
| `StgFocusInRangeEx` | DLL | works |
| `StgGetFocusPlaneType` | DLL | works |
| `StgGetPFSPlanePoints` | DLL | works |
| `Stg_GetPFSLEDSwitch` | call_proc | works |
| `Stg_GetPFSLensOffsetPosition` | DLL | works |
| `Stg_GetPFSStatus` | DLL | works |
| `Stg_GetTIRFFocusEx` | DLL | works |
| `Stg_IsPFSPresent` | DLL | works |
| `Stg_PFSGetDishType` | DLL | works |
| `Stg_PFSGetDishTypeChangeable` | DLL | works |
| `Stg_PFSSetDishType` | DLL | set, read back |
| `Stg_SetPFSLEDSwitch` | call_proc | changed and put back |
| `Stg_SetPFSLensOffsetPosition` | DLL | set, read back |
| `Stg_SetPFSStatus` | DLL | works |
| `Stg_WaitForPFS` | DLL | works |

### Shutters

| Function | Fastest route | Result |
|---|---|---|
| `Stg_GetCSUShutterState` | DLL | works |
| `Stg_GetDMDAssociatedShutterCount` | macro | works |
| `Stg_GetDMDAssociatedShutterId` | macro | works |
| `Stg_GetDMDAssociatedShuttersOpenState` | macro | works |
| `Stg_GetShutterAperture` | DLL | works |
| `Stg_GetShutterApertureSteps` | DLL | works |
| `Stg_GetShutterCount` | DLL | works |
| `Stg_GetShutterName` | DLL | works |
| `Stg_GetShutterState` | DLL | works |
| `Stg_GetShutterStateEx` | DLL | works |
| `Stg_GetShutterStepAperture` | DLL | works |
| `Stg_IsShutterPresent` | DLL | works |
| `Stg_SetCSUShutterState` | DLL | set, read back |
| `Stg_SetShutterAperture` | DLL | set, read back |
| `Stg_SetShutterState` | DLL | changed and put back |

### Slide loader

| Function | Fastest route | Result |
|---|---|---|
| `Stg_GetBarCode` | DLL | works |
| `Stg_GetBarCodeEx` | DLL | works |
| `Stg_GetCassetteCount` | DLL | works |
| `Stg_GetLastBarCode` | DLL | works |
| `Stg_GetSlideCount` | DLL | works |
| `Stg_GetSlideLoaderHolderCapacity` | DLL | works |
| `Stg_IsBarCodeScanned` | DLL | works |
| `Stg_IsCassettePresent` | DLL | works |
| `Stg_IsCassetteScanned` | DLL | works |
| `Stg_IsSlideLoaded` | DLL | works |
| `Stg_IsSlideLoaderCassetteManipulationAllowed` | DLL | works |
| `Stg_IsSlidePresent` | DLL | works |
| `Stg_IsSlidePresentEx` | DLL | works |
| `Stg_SlideLoaderGetHwStatus` | DLL | works |

### Stage XY

| Function | Fastest route | Result |
|---|---|---|
| `StgGetPos` | DLL | works |
| `StgGetPosXY` | DLL | works |
| `StgGetRelativeMovements` | DLL | works |
| `StgMove` | DLL | works |
| `StgMoveXY` | DLL | works |
| `StgXY_GetBlockAxisSupported` | DLL | works |
| `StgXY_GetJoystickSpeed` | DLL | works |
| `StgXY_GetLimits` | DLL | works |
| `StgXY_GetMotorSpeed` | DLL | works |
| `StgXY_GetMotorSpeedSteps` | DLL | works |
| `StgXY_GetPrecision` | DLL | works |
| `StgXY_GetSettleTime` | DLL | works |
| `StgXY_GetSpeedVector` | DLL | works |
| `StgXY_GetStepMotorSpeed` | DLL | works |
| `StgXY_IsJoystickSpeedControllable` | DLL | works |
| `StgXY_IsMotorSpeedControllable` | DLL | works |
| `StgXY_IsPrecisionControllable` | DLL | works |
| `StgXY_IsPresent` | DLL | works |
| `StgXY_IsSettleTimeControllable` | DLL | works |
| `StgXY_IsSpeedRampControllable` | DLL | works |
| `StgXY_IsSpeedVectorControllable` | DLL | works |
| `StgXY_IsVirtualJoystickSupported` | DLL | works |
| `StgXY_SetLimits` | DLL | set, read back |
| `StgXY_SetMotorSpeed` | DLL | set, read back |
| `StgXY_SetSpeedVector` | DLL | set, read back |

### Stage Z

| Function | Fastest route | Result |
|---|---|---|
| `StgGetAbsPosZ` | DLL | works |
| `StgGetPosZ` | DLL | works |
| `StgMoveZ` | DLL | works |
| `StgZ_GetActiveZ` | DLL | works |
| `StgZ_GetEscape` | DLL | works |
| `StgZ_GetJoystickSpeed` | DLL | works |
| `StgZ_GetJoystickSpeedSteps` | DLL | works |
| `StgZ_GetJoystickZStep` | DLL | works |
| `StgZ_GetLimits` | DLL | works |
| `StgZ_GetLimitsMultiple` | DLL | works |
| `StgZ_GetMotorSpeed` | DLL | works |
| `StgZ_GetMotorSpeedSteps` | DLL | works |
| `StgZ_GetReferencePosition` | DLL | works |
| `StgZ_GetStepJoystickSpeed` | DLL | works |
| `StgZ_GetStepMotorSpeed` | DLL | works |
| `StgZ_IsJoystickSpeedControllable` | DLL | works |
| `StgZ_IsMotorSpeedControllable` | DLL | works |
| `StgZ_IsPresent` | DLL | works |
| `StgZ_SetActiveZ` | DLL | set, read back |
| `StgZ_SetJoystickSpeed` | DLL | set, read back |
| `StgZ_SetJoystickZStep` | DLL | set, read back |
| `StgZ_SetLimits` | DLL | set, read back |
| `StgZ_SetMotorSpeed` | DLL | set, read back |

### TIRF

| Function | Fastest route | Result |
|---|---|---|
| `Stg_GetTIRFAngleEx` | DLL | works |
| `Stg_GetTIRFDirectionEx` | DLL | works |
| `Stg_GetTIRFMirror` | DLL | works |
| `Stg_GetTIRFPosition` | DLL | works |
| `Stg_GetTIRFPositionEx` | DLL | works |
| `Stg_SetTIRFMirror` | DLL | set, read back |
| `Stg_SetTIRFPosition` | DLL | set, read back |

### Triggers and TTL

| Function | Fastest route | Result |
|---|---|---|
| `GetActivePFIForTriggering` | DLL | works |
| `Stg_GetPinConfiguredForTTLOutput` | macro | works |
| `Stg_GetPinConfiguredForTTLOutputPulse` | macro | works |
| `Stg_GetPinTTLOutputState` | macro | works |
| `Stg_SetPinTTLOutputState` | call_proc | set, read back |
| `Stg_TTLOutputGetControlMode` | DLL | works |
| `Stg_TTLOutputGetControlModePulses` | DLL | works |
| `Stg_TTLOutputGetPulseActiveState` | DLL | works |
| `Stg_TTLOutputGetPulseTime` | DLL | works |

### AdvancedAPI

| Function | Fastest route | Result |
|---|---|---|
| `strlen` | macro | works |

### ImageDocument

| Function | Fastest route | Result |
|---|---|---|
| `CloseCurrentDocument` | DLL | works |
| `ImageSaveAs` | DLL | works |

### Macro

| Function | Fastest route | Result |
|---|---|---|
| `GetVariableValue` | DLL | works |
| `RunMacro` | DLL | works |

### System

| Function | Fastest route | Result |
|---|---|---|
| `DeleteVariables` | DLL | works |
| `Get_Calibration` | DLL | works |
| `Get_InfoStr` | DLL | works |

