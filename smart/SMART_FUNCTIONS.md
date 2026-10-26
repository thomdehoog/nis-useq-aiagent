# NIS functions for smart microscopy

**838 of 3667** AR macro functions: the state of the microscope, and what
we can change, acquire and save. Left out: image analysis, measurement, binary, image
processing, export, organizer, visualization, user interface, macro language.

*read*: reads a state. *set*: changes a state. *action*: does something (capture, save,
autofocus). *dialog*: opens a NIS window for a person, not for the driver.
*Reachable*: offered by name with the microscope off (step 0). *Step 2*: called with no
arguments, microscope off (empty: not reached yet). Made by `make_smart_list.py`;
spreadsheet: `smart_functions.csv`.

| Group | Covers | read | set | action | dialog | Total | Reachable now |
|---|---|---:|---:|---:|---:|---:|---:|
| [Stage XY and Z](#stage-xy-and-z) | position, moves, limits, speed, piezo, joystick, slide loader | 71 | 44 | 26 | 8 | 149 | 148 |
| [Objectives and nosepiece](#objectives-and-nosepiece) | objective position and names, correction collar | 12 | 8 | 7 | 9 | 36 | 34 |
| [Focus](#focus) | Perfect Focus System, autofocus, focus surface | 17 | 16 | 23 | 11 | 67 | 55 |
| [Optical configurations](#optical-configurations) | select, list and read optical configurations | 3 | 4 | 5 | 7 | 19 | 17 |
| [Confocal and spinning disk](#confocal-and-spinning-disk) | spinning disk speed and on/off, A1/AX/C2 confocal settings | 2 | 7 | 14 | 4 | 27 | 4 |
| [Light sources](#light-sources) | lamps, LEDs, lasers, intensity, voltage, iris, light ND filter | 41 | 17 | 4 | 1 | 63 | 60 |
| [Shutters](#shutters) | open, close and state of shutters | 15 | 9 | 0 | 3 | 27 | 22 |
| [Filters and turrets](#filters-and-turrets) | filter wheels, turrets, ND filters | 19 | 8 | 0 | 1 | 28 | 20 |
| [Light path and optics](#light-path-and-optics) | light path, condenser, aperture, zoom, relay lens, analyzer, TIRF | 40 | 24 | 4 | 2 | 70 | 44 |
| [Camera](#camera) | exposure, gain, binning, format, ROI, trigger mode, temperature | 34 | 46 | 15 | 3 | 98 | 19 |
| [Acquisition](#acquisition) | capture, live, freeze, RAM capture, ND experiments | 11 | 19 | 41 | 9 | 80 | 59 |
| [Calibration](#calibration) | pixel size and image calibration | 5 | 2 | 4 | 1 | 12 | 12 |
| [Image documents and files](#image-documents-and-files) | save, open, close, image info, files, disk space, memory | 7 | 6 | 15 | 9 | 37 | 37 |
| [Incubation and environment](#incubation-and-environment) | incubator, heat stage, perfusion, water | 18 | 13 | 17 | 0 | 48 | 38 |
| [Triggers and stimulation](#triggers-and-stimulation) | TTL, triggers, DMD and patterns | 25 | 10 | 21 | 3 | 59 | 45 |
| [Microscope](#microscope) | presence, sleep, the device log, NIS version | 6 | 6 | 6 | 0 | 18 | 12 |
| **All** | | **326** | **239** | **202** | **71** | **838** | **626** |

## Stage XY and Z

Position, moves, limits, speed, piezo, joystick, slide loader.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `PiezoXYGetPosition` | read | yes | not called |  |
| `StgGetAbsPosZ` | read | yes | needs arguments | error: Bad number of parameters |
| `StgGetInitValuesXY` | read | yes | needs arguments | error: Bad number of parameters |
| `StgGetList` | read | yes | needs arguments | error: Bad number of parameters |
| `StgGetListEx` | read | yes | needs arguments | error: Bad number of parameters |
| `StgGetPos` | read | yes | needs arguments | error: Bad number of parameters |
| `StgGetPosXY` | read | yes | needs arguments | error: Bad number of parameters |
| `StgGetPosZ` | read | yes | needs arguments | error: Bad number of parameters |
| `StgGetRelativeMovements` | read | yes | needs arguments | error: Bad number of parameters |
| `StgXY_GetBlockAxis` | read | yes | needs arguments | error: Bad number of parameters |
| `StgXY_GetBlockAxisSupported` | read | yes | needs arguments | error: Bad number of parameters |
| `StgXY_GetJoystickSpeed` | read | yes | ran | -4.0 |
| `StgXY_GetJoystickSpeedSteps` | read | yes | ran | -4 |
| `StgXY_GetLimits` | read | yes | needs arguments | error: Bad number of parameters |
| `StgXY_GetMotorSpeed` | read | yes | ran | -4.0 |
| `StgXY_GetMotorSpeedSteps` | read | yes | ran | -4 |
| `StgXY_GetPrecision` | read | yes | ran | -4.0 |
| `StgXY_GetSettleTime` | read | yes | ran | -4.0 |
| `StgXY_GetSpeedRamp` | read | yes | ran | -4 |
| `StgXY_GetSpeedRampSteps` | read | yes | ran | -4 |
| `StgXY_GetSpeedVector` | read | yes | needs arguments | error: Bad number of parameters |
| `StgXY_GetStepJoystickSpeed` | read | yes | needs arguments | error: Bad number of parameters |
| `StgXY_GetStepMotorSpeed` | read | yes | needs arguments | error: Bad number of parameters |
| `StgXY_IsInLoadingPosition` | read | yes | needs arguments | error: Bad number of parameters |
| `StgXY_IsJoystickSpeedControllable` | read | yes | ran | 0 |
| `StgXY_IsMotorSpeedControllable` | read | yes | ran | 0 |
| `StgXY_IsPrecisionControllable` | read | yes | ran | 0 |
| `StgXY_IsPresent` | read | yes | ran | 0 |
| `StgXY_IsSettleTimeControllable` | read | yes | ran | 0 |
| `StgXY_IsSpeedRampControllable` | read | yes | ran | 0 |
| `StgXY_IsSpeedVectorControllable` | read | yes | ran | 0 |
| `StgXY_IsVirtualJoystickSupported` | read | yes | ran | 0 |
| `StgZ_GetActiveZ` | read | yes | ran | 0 |
| `StgZ_GetEscape` | read | yes | ran | 0 |
| `StgZ_GetJoystickSpeed` | read | yes | ran | -3.0 |
| `StgZ_GetJoystickSpeedSteps` | read | yes | ran | -3 |
| `StgZ_GetJoystickZStep` | read | yes | ran | 5.0 |
| `StgZ_GetLimits` | read | yes | needs arguments | error: Bad number of parameters |
| `StgZ_GetLimitsMultiple` | read | yes | needs arguments | error: Bad number of parameters |
| `StgZ_GetMotorSpeed` | read | yes | ran | -3.0 |
| `StgZ_GetMotorSpeedSteps` | read | yes | ran | -3 |
| `StgZ_GetPiezoDevice` | read | yes | ran | 0 |
| `StgZ_GetReferencePosition` | read | yes | needs arguments | error: Bad number of parameters |
| `StgZ_GetSpeedRamp` | read | yes | ran | -3 |
| `StgZ_GetSpeedRampSteps` | read | yes | ran | -3 |
| `StgZ_GetStepJoystickSpeed` | read | yes | needs arguments | error: Bad number of parameters |
| `StgZ_GetStepMotorSpeed` | read | yes | needs arguments | error: Bad number of parameters |
| `StgZ_IsJoystickSpeedControllable` | read | yes | ran | -1 |
| `StgZ_IsMotorSpeedControllable` | read | yes | ran | -1 |
| `StgZ_IsPresent` | read | yes | needs arguments | error: Bad number of parameters |
| `StgZ_IsSpeedRampControllable` | read | yes | ran | -1 |
| `StgZ_IsVirtualJoystickSupported` | read | yes | ran | -1 |
| `Stg_GetBarCode` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetBarCodeEx` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetCassetteCount` | read | yes | ran | 0 |
| `Stg_GetLastBarCode` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetLoadedSlide` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetSlideCount` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetSlideLoaderHolderCapacity` | read | yes | ran | 0 |
| `Stg_IsBarCodeScanned` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_IsCassettePresent` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_IsCassetteScanned` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_IsMouseJoystickZ` | read | yes | ran | 1 |
| `Stg_IsSlideLoaded` | read | yes | ran | 0 |
| `Stg_IsSlideLoaderCassetteManipulationAllowed` | read | yes | ran | 0 |
| `Stg_IsSlideLoaderInitialized` | read | yes | ran | 0 |
| `Stg_IsSlidePresent` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_IsSlidePresentEx` | read | yes | ran | 0 |
| `Stg_LinearActuator_GetDescription` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_LinearActuator_GetPosition` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_SlideLoaderGetHwStatus` | read | yes | not called |  |
| `PiezoXYMoveToHomePosition` | set | yes | not called |  |
| `PiezoXYMoveToXYPosition` | set | yes | not called |  |
| `StgEnableJoystick` | set | yes | not called |  |
| `StgEnableJoystickXY` | set | yes | not called |  |
| `StgEnableJoystickZ` | set | yes | not called |  |
| `StgMove` | set | yes | not called |  |
| `StgMoveMainZ` | set | yes | not called |  |
| `StgMovePiezoZ` | set | yes | not called |  |
| `StgMovePiezoZToHomeKeepZ` | set | yes | not called |  |
| `StgMovePiezoZToHomePosition` | set | yes | not called |  |
| `StgMoveXY` | set | yes | not called |  |
| `StgMoveXYScan` | set | yes | not called |  |
| `StgMoveXYToRoi` | set | yes | not called |  |
| `StgMoveXYZScan` | set | yes | not called |  |
| `StgMoveZ` | set | yes | not called |  |
| `StgMoveZNamed` | set | yes | not called |  |
| `StgSetRelativeMovements` | set | yes | not called |  |
| `StgToggleJoystick` | set | yes | not called |  |
| `StgToggleJoystickXY` | set | yes | not called |  |
| `StgToggleJoystickZ` | set | yes | not called |  |
| `StgXY_MoveToAcquisitionPosition` | set | yes | not called |  |
| `StgXY_MoveToLoadingPosition` | set | yes | not called |  |
| `StgXY_MoveVirtualJoystickAtSpeed` | set | yes | not called |  |
| `StgXY_SetBlockAxis` | set | yes | not called |  |
| `StgXY_SetJoystickSpeed` | set | yes | not called |  |
| `StgXY_SetLimits` | set | yes | not called |  |
| `StgXY_SetMotorSpeed` | set | yes | not called |  |
| `StgXY_SetPrecision` | set | yes | not called |  |
| `StgXY_SetSettleTime` | set | yes | not called |  |
| `StgXY_SetSpeedRamp` | set | yes | not called |  |
| `StgXY_SetSpeedVector` | set | yes | not called |  |
| `StgZ_MoveVirtualJoystickAtSpeed` | set | yes | not called |  |
| `StgZ_SetActiveZ` | set | yes | not called |  |
| `StgZ_SetJoystickSpeed` | set | yes | not called |  |
| `StgZ_SetJoystickZStep` | set | yes | not called |  |
| `StgZ_SetKeepPosition` | set | yes | not called |  |
| `StgZ_SetLimits` | set | yes | not called |  |
| `StgZ_SetMotorSpeed` | set | yes | not called |  |
| `StgZ_SetSpeedRamp` | set | yes | not called |  |
| `Stg_EnableMouseJoystickZ` | set | yes | not called |  |
| `Stg_LinearActuator_SetPosition` | set | yes | not called |  |
| `Stg_SetSlidePresent` | set | yes | not called |  |
| `Stg_SlideLoaderMoveAtVelocity` | set | yes | not called |  |
| `Stg_ToggleMouseJoystickZ` | set | yes | not called |  |
| `PI_GcsCommand` | action | yes | not called |  |
| `StgInitiate` | action | yes | not called |  |
| `StgInitiateXY` | action | yes | not called |  |
| `StgInitiateZ` | action | yes | not called |  |
| `StgJoystickOff` | action | yes | not called |  |
| `StgJoystickOn` | action | yes | not called |  |
| `StgXY_DrawCircleAsync_Start` | action | yes | not called |  |
| `StgXY_DrawCircleAsync_Stop` | action | yes | not called |  |
| `StgXY_DrawCircleAsync_WaitAngle` | action | yes | not called |  |
| `StgZ_AutoFocus` | action | yes | not called |  |
| `StgZ_Escape` | action | yes | not called |  |
| `StgZ_Refocus` | action | yes | not called |  |
| `Stg_AllowSlideLoaderCassetteManipulation` | action | yes | not called |  |
| `Stg_CaptureSlidePreview` | action | no | not called |  |
| `Stg_InitializeSlideLoader` | action | yes | not called |  |
| `Stg_LoadSlideFrom` | action | yes | not called |  |
| `Stg_LoadSlideToPreparationPosition` | action | yes | not called |  |
| `Stg_PreScanBarCode` | action | yes | not called |  |
| `Stg_ScanCassette` | action | yes | not called |  |
| `Stg_SlideLoaderShowError` | action | yes | not called |  |
| `Stg_SlideLoaderWarmInitAvailable` | action | yes | not called |  |
| `Stg_SlideloaderCheckStageEmpty` | action | yes | not called |  |
| `Stg_StopSlideLoader` | action | yes | not called |  |
| `Stg_TransferSlide` | action | yes | not called |  |
| `Stg_UnloadSlide` | action | yes | not called |  |
| `Stg_UnloadSlideTo` | action | yes | not called |  |
| `_JoystickManager` | dialog | yes | not called |  |
| `_StgConfig` | dialog | yes | not called |  |
| `_StgConfigXY` | dialog | yes | not called |  |
| `_StgConfigZ` | dialog | yes | not called |  |
| `_StgInitiate` | dialog | yes | not called |  |
| `_StgInitiateZ` | dialog | yes | not called |  |
| `_Stg_InitializeSlideLoader` | dialog | yes | not called |  |
| `_Stg_SetupMouseJoystickZ` | dialog | yes | not called |  |

## Objectives and nosepiece

Objective position and names, correction collar.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `GetCurrentObjName` | read | yes | needs arguments | error: Bad number of parameters |
| `GetObjType` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_CorrectionCollar_GetDescription` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_CorrectionCollar_GetPosition` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetNosepieceObjectiveCode` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetNosepieceObjectiveName` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetNosepieceObjectiveRefractiveIndex` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetNosepiecePosition` | read | yes | ran | 0 |
| `Stg_GetNosepiecePositions` | read | yes | ran | 0 |
| `Stg_GetObjectiveNameFromCode` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_IsNosepiecePresent` | read | yes | ran | 0 |
| `Stg_WID_GetObjectiveWet` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_WID_Get |
| `ChangeObjective` | set | yes | not called |  |
| `RestoreObjectives` | set | yes | not called |  |
| `RestoreObjectivesEx` | set | yes | not called |  |
| `Stg_CorrectionCollar_SetPosition` | set | yes | not called |  |
| `Stg_Nosepiece_EnableRotation` | set | no | not called |  |
| `Stg_SetNosepieceObjective` | set | yes | not called |  |
| `Stg_SetNosepieceObjectiveName` | set | yes | not called |  |
| `Stg_SetNosepiecePosition` | set | yes | not called |  |
| `AddObjective` | action | yes | not called |  |
| `AddObjectiveEx` | action | yes | not called |  |
| `ApplyObjectivesXYOffset` | action | yes | not called |  |
| `BackupObjectives` | action | yes | not called |  |
| `DeleteObjective` | action | yes | not called |  |
| `DeleteObjectives` | action | yes | not called |  |
| `Stg_DropOil` | action | yes | not called |  |
| `_BackupObjectives` | dialog | yes | not called |  |
| `_CalibrateObjective` | dialog | yes | not called |  |
| `_CalibrateObjective2` | dialog | yes | not called |  |
| `_CalibrateObjective3` | dialog | yes | not called |  |
| `_ExploreObjectives` | dialog | yes | not called |  |
| `_ObjectiveClearance` | dialog | yes | not called |  |
| `_ObjectivesXYOffset` | dialog | yes | not called |  |
| `_RestoreObjectives` | dialog | yes | not called |  |
| `_Stg_NosepieceSetup` | dialog | yes | not called |  |

## Focus

Perfect Focus System, autofocus, focus surface.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `StgGetFocusPlanePosition` | read | yes | needs arguments | error: Bad number of parameters |
| `StgGetFocusPlaneType` | read | yes | ran | 0 |
| `StgGetPFSPlanePoints` | read | yes | ran | 0 |
| `StgIsFocusPlaneValid` | read | yes | ran | 0 |
| `StgIsPFSPlaneValid` | read | yes | ran | 0 |
| `Stg_GetPFSLEDSwitch` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPFSL |
| `Stg_GetPFSLensOffsetPosition` | read | yes | ran | 0 |
| `Stg_GetPFSStatus` | read | yes | ran | 0 |
| `Stg_GetTIRFFocusEx` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_HTIRF_GetFocus` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_G |
| `Stg_IsPFSPresent` | read | yes | ran | 0 |
| `Stg_PFSGetDishType` | read | yes | not called |  |
| `Stg_PFSGetDishTypeChangeable` | read | yes | not called |  |
| `Stg_PFSIsDMInserted` | read | yes | not called |  |
| `Stg_PFSIsDMMotorized` | read | yes | not called |  |
| `Stg_PFSIsSignalOutputEnabled` | read | yes | not called |  |
| `VCS_GetFocusLens` | read | no | not called |  |
| `EnableFocusCriterium` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'EnableFocus |
| `ResetFocusCriteriumMax` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'ResetFocusC |
| `StgFocusSetCriterion` | set | yes | not called |  |
| `StgResetPFSPlane` | set | yes | not called |  |
| `StgSetFocusPlane` | set | yes | not called |  |
| `Stg_HTIRF_SetFocus` | set | no | not called |  |
| `Stg_HTIRF_SetXYFocus` | set | no | not called |  |
| `Stg_PFSEnableSignalOutput` | set | yes | not called |  |
| `Stg_PFSSetDishType` | set | yes | not called |  |
| `Stg_PFSSetLEDPower` | set | no | not called |  |
| `Stg_SetPFSFocus` | set | yes | not called |  |
| `Stg_SetPFSLEDSwitch` | set | no | not called |  |
| `Stg_SetPFSLensOffsetPosition` | set | yes | not called |  |
| `Stg_SetPFSStatus` | set | yes | not called |  |
| `Stg_SetTIRFFocusEx` | set | yes | not called |  |
| `VCS_SetFocusLens` | set | no | not called |  |
| `Experiment_RunAutoBrightnessAndFocusOnAllChannels` | action | no | not reachable | AttributeError: 'Macro' object has no attribute 'Experiment_ |
| `RunAutoFocusLong` | action | yes | not called |  |
| `RunAutoFocusShort` | action | no | not called |  |
| `RunAutoFocusSmartRange` | action | yes | not called |  |
| `RunFastAutoFocus` | action | yes | not called |  |
| `StgFocus` | action | yes | not called |  |
| `StgFocusAdaptive` | action | yes | not called |  |
| `StgFocusAdaptiveTwoPasses` | action | yes | not called |  |
| `StgFocusCriteria` | action | yes | not called |  |
| `StgFocusInRange` | action | yes | not called |  |
| `StgFocusInRangeEx` | action | yes | not called |  |
| `StgFocusInRangeExTwoPasses` | action | yes | not called |  |
| `StgFocusInRangeTwoPasses` | action | yes | not called |  |
| `StgFocusPFS` | action | yes | not called |  |
| `StgFocusPlane` | action | yes | not called |  |
| `StgScanFocus` | action | yes | not called |  |
| `StgUsePFSPlane` | action | yes | not called |  |
| `Stg_LoadLastFocusSurfacePoints` | action | yes | not called |  |
| `Stg_PFSFindOffset` | action | yes | not called |  |
| `Stg_PFSInsertExtractDM` | action | yes | not called |  |
| `Stg_PFSSignalOutputTest` | action | yes | not called |  |
| `Stg_RemoveFocusSurfacePoints` | action | yes | not called |  |
| `Stg_WaitForPFS` | action | yes | not called |  |
| `StgFocusSetCriterionDialog` | dialog | yes | not called |  |
| `StgSetupFocus` | dialog | yes | not called |  |
| `StgSetupFocusAdaptiveTwoPasses` | dialog | yes | not called |  |
| `StgSetupFocusContinuousTwoPasses` | dialog | yes | not called |  |
| `StgSetupFocusEx` | dialog | yes | not called |  |
| `StgSetupFocusOffset` | dialog | yes | not called |  |
| `StgSetupFocusTwoPasses` | dialog | yes | not called |  |
| `_SetupFastAutoFocus` | dialog | yes | not called |  |
| `_StgSetupFocus` | dialog | yes | not called |  |
| `_StgSetupFocusPlane` | dialog | yes | not called |  |
| `_StgSetupPFSFocus` | dialog | yes | not called |  |

## Optical configurations

Select, list and read optical configurations.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `GetOptConfCount` | read | yes | ran | 0 |
| `GetOptConfName` | read | yes | needs arguments | error: Bad number of parameters |
| `GetSelectedOptConf` | read | yes | needs arguments | error: Bad number of parameters |
| `RestoreOptConf` | set | yes | not called |  |
| `RestoreOptConfEx` | set | yes | not called |  |
| `SelectOptConf` | set | yes | not called |  |
| `SelectOptConf_HWOnly` | set | yes | not called |  |
| `AddOptConf` | action | yes | not called |  |
| `BackupOptConf` | action | yes | not called |  |
| `DeleteOptConf` | action | yes | not called |  |
| `DeleteOptConfs` | action | yes | not called |  |
| `UnselectOptConf` | action | yes | not called |  |
| `_AddOptConf` | dialog | yes | not called |  |
| `_AddOptConfForFluo` | dialog | yes | not called |  |
| `_BackupOptConf` | dialog | yes | not called |  |
| `_ExploreOptConf` | dialog | yes | not called |  |
| `_OptConfSelStimulDevice` | dialog | no | not called |  |
| `_RestoreOptConf` | dialog | yes | not called |  |
| `_SelectActiveStimOptConf` | dialog | no | not called |  |

## Confocal and spinning disk

Spinning disk speed and on/off, A1/AX/C2 confocal settings.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `A1VAASGetParams` | read | no | not called |  |
| `Stg_GetDiskSpeed` | read | yes | ran | 7298712 |
| `A1ApplyStimulationSettings` | set | no | not called |  |
| `A1EnableIRLaserCOMPortConnection` | set | no | not called |  |
| `A1SetOutputPort` | set | no | not called |  |
| `A1VAASSetParams` | set | no | not called |  |
| `C2SwitchLever` | set | no | not called |  |
| `Stg_SetDiskSpeed` | set | yes | not called |  |
| `Stg_SetDisk_On_Off` | set | yes | not called |  |
| `A1AutoGain` | action | no | not called |  |
| `A1AutoGainSimple` | action | no | not called |  |
| `A1AutoOffset` | action | no | not called |  |
| `A1Capture1DZ` | action | no | not called |  |
| `A1Capture1DZ_IntensityCorr` | action | no | not called |  |
| `A1IRLaserAutoAlign` | action | no | not called |  |
| `A1Live1DZ` | action | no | not called |  |
| `A1Live1DZ_IntensityCorr` | action | no | not called |  |
| `A1TestSWTrigger` | action | no | not called |  |
| `AxNSPARC_CheckNSPARCAlignment` | action | no | not called |  |
| `AxNSPARC_RunNSPARCAlignment` | action | no | not called |  |
| `ConfocalAX_MeasureCurrentIlluminationPower` | action | no | not called |  |
| `ConfocalAX_MeasureIlluminationPower` | action | no | not called |  |
| `Stg_SyncDiskSpeed` | action | yes | not called |  |
| `A1ShowSetupGUI` | dialog | no | not called |  |
| `LineChannelSeriesSetup` | dialog | no | not called |  |
| `_A1AutoGain` | dialog | no | not called |  |
| `_A1AutoGain_Setup` | dialog | no | not called |  |

## Light sources

Lamps, LEDs, lasers, intensity, voltage, iris, light ND filter.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `Stg_GetDMDAssociatedLightId` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetLaserOutputModality` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetLase |
| `Stg_GetLaserOutputNumPorts` | read | yes | ran | 0 |
| `Stg_GetLaserOutputPortUsed` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetLaserOutputPortUsedEx` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetLightIrisIntensity` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetLightIrisIntensitySteps` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetLightIrisSteps` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetLightState` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetLightStepVoltage` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetLightVoltage` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetLightVoltageSteps` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetMultiLaserCount` | read | yes | ran | 0 |
| `Stg_GetMultiLaserLineNDFilter` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetMultiLaserLineName` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetMultiLaserLineUsed` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetMultiLaserModality` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetMult |
| `Stg_GetMultiLaserName` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetMultiLaserNumLines` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetMultiLaserOpMode` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetMultiLaserPower` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetMultiLaserPowerSteps` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetMultiLaserStepPower` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetMultiLaserWavelength` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_IsLightPresent` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_GetCount` | read | yes | ran | 0 |
| `Stg_Light_GetIrisIntensity` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_GetIrisSteps` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_GetNDFilterControllable` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_GetNDFilterPosition` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_GetNDFilterStepPosition` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_GetNDFilterSteps` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_GetName` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_GetRemoteSwitch` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_GetState` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_GetStepIrisIntensity` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_GetStepVoltage` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_GetVoltage` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_GetVoltageSteps` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_IsIrisControllable` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_IsVoltageControllable` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Light_SetIrisIntensity` | set | yes | not called |  |
| `Stg_Light_SetNDFilterPosition` | set | yes | not called |  |
| `Stg_Light_SetRemoteSwitch` | set | yes | not called |  |
| `Stg_Light_SetState` | set | yes | not called |  |
| `Stg_Light_SetVoltage` | set | yes | not called |  |
| `Stg_SetLaserOutputPortUsed` | set | yes | not called |  |
| `Stg_SetLaserOutputPortUsedEx` | set | yes | not called |  |
| `Stg_SetLightIrisIntensity` | set | yes | not called |  |
| `Stg_SetLightState` | set | yes | not called |  |
| `Stg_SetLightVoltage` | set | yes | not called |  |
| `Stg_SetMultiLaserLineAltSeq` | set | yes | not called |  |
| `Stg_SetMultiLaserLineNDFilter` | set | yes | not called |  |
| `Stg_SetMultiLaserLineName` | set | yes | not called |  |
| `Stg_SetMultiLaserLineUsed` | set | yes | not called |  |
| `Stg_SetMultiLaserOpMode` | set | yes | not called |  |
| `Stg_SetMultiLaserPower` | set | yes | not called |  |
| `Stg_SetMultiLaserWavelength` | set | yes | not called |  |
| `Stg_DisplayLED` | action | no | not called |  |
| `Stg_StartMultiLaserAdvancedAltSeq` | action | yes | not called |  |
| `Stg_StartMultiLaserAdvancedAltSeqEx` | action | yes | not called |  |
| `Stg_StopMultiLaserAdvancedAltSeq` | action | yes | not called |  |
| `_Stg_CalibrateMultiLaserLine` | dialog | yes | not called |  |

## Shutters

Open, close and state of shutters.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `Stg_GetCSUShutterState` | read | yes | ran | 0 |
| `Stg_GetDMDAssociatedShutterCount` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetDMDAssociatedShutterId` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetDMDAssociatedShuttersOpenState` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetShutterAperture` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetShutterApertureSteps` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetShutterCount` | read | yes | ran | 0 |
| `Stg_GetShutterName` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetShutterSpeed` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetShut |
| `Stg_GetShutterSpeedSteps` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetShut |
| `Stg_GetShutterState` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetShutterStateEx` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetShutterStepAperture` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetShutterStepSpeed` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetShut |
| `Stg_IsShutterPresent` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_CloseFirstShutter` | set | yes | not called |  |
| `Stg_OpenFirstShutter` | set | yes | not called |  |
| `Stg_SetCSUShutterState` | set | yes | not called |  |
| `Stg_SetDMDAssociatedShuttersOpenState` | set | yes | not called |  |
| `Stg_SetShutterAperture` | set | yes | not called |  |
| `Stg_SetShutterSpeed` | set | no | not called |  |
| `Stg_SetShutterState` | set | yes | not called |  |
| `Stg_SetShutterStateEx` | set | yes | not called |  |
| `Stg_ToggleFirstShutter` | set | yes | not called |  |
| `_ShutterSelStimulDevice` | dialog | no | not called |  |
| `_Stg_FiltersShutters` | dialog | yes | not called |  |
| `_Stg_RenameShutter` | dialog | yes | not called |  |

## Filters and turrets

Filter wheels, turrets, ND filters.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `Stg_Filter_GetCount` | read | yes | ran | 0 |
| `Stg_Filter_GetName` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Filter_GetPosition` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Filter_GetPositionCount` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Filter_GetPositionName` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Filter_GetSpeed` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_Filter_ |
| `Stg_Filter_GetSpeedSteps` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_Filter_ |
| `Stg_Filter_GetStepSpeed` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_Filter_ |
| `Stg_GetFilterName` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetFilterPosition` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetFilterPositions` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetFilterSpeed` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetFilt |
| `Stg_GetFilterSpeedSteps` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetFilt |
| `Stg_GetFilterStepSpeed` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetFilt |
| `Stg_GetNDFilterPosition` | read | yes | ran | 0.0 |
| `Stg_GetNDFilterStepPosition` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetNDFilterSteps` | read | yes | ran | 0 |
| `Stg_IsFilterPresent` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_IsNDFilterPresent` | read | yes | ran | 0 |
| `EnableSelectOCFromFilter` | set | yes | not called |  |
| `Stg_Filter_SetPosition` | set | yes | not called |  |
| `Stg_Filter_SetPositionName` | set | yes | not called |  |
| `Stg_Filter_SetSpeed` | set | no | not called |  |
| `Stg_SetFilterName` | set | yes | not called |  |
| `Stg_SetFilterPosition` | set | yes | not called |  |
| `Stg_SetFilterSpeed` | set | no | not called |  |
| `Stg_SetNDFilterPosition` | set | yes | not called |  |
| `_ProbesAndFilters` | dialog | yes | not called |  |

## Light path and optics

Light path, condenser, aperture, zoom, relay lens, analyzer, TIRF.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `Camera_RelayLensGet` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Rela |
| `GetCurrentLightPathName` | read | yes | needs arguments | error: Bad number of parameters |
| `GetCurrentObjMagnification` | read | yes | ran | 0.0 |
| `GetLightPathCount` | read | yes | ran | 5 |
| `GetLightPathIndexName` | read | yes | needs arguments | error: Bad number of parameters |
| `GetObjMagnification` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetAnalyzerState` | read | yes | ran | 0 |
| `Stg_GetAperturePosition` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetApertureStepPosition` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetApertureSteps` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetCondenserPosition` | read | yes | ran | 0 |
| `Stg_GetCondenserPositions` | read | yes | ran | 0 |
| `Stg_GetLightPathPosition` | read | yes | ran | 0 |
| `Stg_GetLightPathPositions` | read | yes | ran | 0 |
| `Stg_GetRelayLensPosition` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetTIRFAngleEx` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetTIRFDirectionEx` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetTIRFMirror` | read | yes | ran | 0 |
| `Stg_GetTIRFPosition` | read | yes | ran | 0.0 |
| `Stg_GetTIRFPositionEx` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetZoomPosition` | read | yes | ran | 1.0 |
| `Stg_GetZoomStepPosition` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetZoomSteps` | read | yes | ran | 0 |
| `Stg_HTIRF_GetAngle` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_G |
| `Stg_HTIRF_GetDirection` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_G |
| `Stg_HTIRF_GetX` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_G |
| `Stg_HTIRF_GetY` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_G |
| `Stg_HTIRF_IsGradationND` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_I |
| `Stg_HTIRF_IsLambdaQP` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_I |
| `Stg_IsAnalyzerPresent` | read | yes | ran | 0 |
| `Stg_IsAperturePresent` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_IsCondenserPresent` | read | yes | ran | 0 |
| `Stg_IsLightPathPresent` | read | yes | ran | 0 |
| `Stg_IsZoomManual` | read | yes | ran | 1 |
| `Stg_IsZoomPresent` | read | yes | ran | 0 |
| `Stg_LUNB_GetCylindricalLensMounted` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_LUNB_Ge |
| `Stg_LUNB_GetCylindricalLensPosition` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_LUNB_Ge |
| `Stg_LUNB_GetRelayLensMounted` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_LUNB_Ge |
| `Stg_LUNB_GetRelayLensPosition` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_LUNB_Ge |
| `Stg_NSTORM_GetZoom` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_NSTORM_ |
| `Camera_RelayLensSet` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Rela |
| `LockCameraMagnification` | set | yes | needs arguments | error: Bad number of parameters |
| `SelectLightPath` | set | yes | not called |  |
| `Stg_HTIRF_SetAlignmentName` | set | no | not called |  |
| `Stg_HTIRF_SetAngle` | set | no | not called |  |
| `Stg_HTIRF_SetDirection` | set | no | not called |  |
| `Stg_HTIRF_SetX` | set | no | not called |  |
| `Stg_HTIRF_SetXY` | set | no | not called |  |
| `Stg_HTIRF_SetY` | set | no | not called |  |
| `Stg_LUNB_SetCylindricalLensPosition` | set | no | not called |  |
| `Stg_LUNB_SetRelayLensPosition` | set | no | not called |  |
| `Stg_NSTORM_SetZoom` | set | no | not called |  |
| `Stg_SetAnalyzerState` | set | yes | not called |  |
| `Stg_SetAperturePosition` | set | yes | not called |  |
| `Stg_SetCondenserPosition` | set | yes | not called |  |
| `Stg_SetLightPathPosition` | set | yes | not called |  |
| `Stg_SetRelayLensPosition` | set | yes | not called |  |
| `Stg_SetTIRFAngleEx` | set | yes | not called |  |
| `Stg_SetTIRFDirectionEx` | set | yes | not called |  |
| `Stg_SetTIRFMirror` | set | yes | not called |  |
| `Stg_SetTIRFMouseWheel` | set | yes | not called |  |
| `Stg_SetTIRFPosition` | set | yes | not called |  |
| `Stg_SetTIRFPositionEx` | set | yes | not called |  |
| `Stg_SetZoomPosition` | set | yes | not called |  |
| `DeleteLightPathLastUsed` | action | yes | not called |  |
| `Stg_Bioluminescence_Mode` | action | no | not called |  |
| `Stg_LoadZoomCorrection` | action | yes | not called |  |
| `Stg_ShowZoomConfig` | action | no | not called |  |
| `_DefineCameraLightPath` | dialog | no | not called |  |
| `_Stg_ShowZoomConfig` | dialog | no | not called |  |

## Camera

Exposure, gain, binning, format, ROI, trigger mode, temperature.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `CameraFormatGet` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraForma |
| `CameraGet_Average` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_A |
| `CameraGet_AverageCH` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_A |
| `CameraGet_AverageToQuality` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_A |
| `CameraGet_AverageToQualityCH` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_A |
| `CameraGet_Exposure` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_E |
| `CameraGet_FileName` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_F |
| `CameraGet_FlexibleHeight` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_F |
| `CameraGet_FrameDuration` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_F |
| `CameraGet_HWTrgInEnabled` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_H |
| `CameraGet_HWTrgOutEnabled` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_H |
| `CameraGet_Integrate` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_I |
| `CameraGet_IntegrateCH` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_I |
| `CameraGet_IntegrateToQualityCH` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_I |
| `CameraGet_Negate` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_N |
| `CameraGet_Rotate` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_R |
| `CameraGet_StimulationTime` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_S |
| `CameraGet_ToRGB` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_T |
| `CameraGet_UseDriverMetadata` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_U |
| `Camera_AngleGet` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Angl |
| `Camera_AverageGet` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Aver |
| `Camera_ExposureGet` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Expo |
| `Camera_GainBGet` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Gain |
| `Camera_GainRGet` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Gain |
| `Camera_IntegrateGet` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Inte |
| `Camera_RotateGet` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Rota |
| `Camera_SensorModeGet` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Sens |
| `Camera_TemperatureGet` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Temp |
| `Camera_TriggerModeGet` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Trig |
| `GetFollowExposureMode` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'GetFollowEx |
| `TrigAcq_GetChannel` | read | yes | not called |  |
| `TrigAcq_GetLine` | read | yes | not called |  |
| `TrigAcq_GetParameters` | read | yes | not called |  |
| `TrigAcq_GetUsedCustomDevices` | read | yes | not called |  |
| `CameraCmd_AverageReset` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_A |
| `CameraCmd_SetDefaults` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_S |
| `CameraCmd_TurnFanOff` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_T |
| `CameraCmd_TurnFanOn` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_T |
| `CameraFormatSet` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraForma |
| `CameraSet_Average` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_A |
| `CameraSet_AverageCH` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_A |
| `CameraSet_AverageToQuality` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_A |
| `CameraSet_AverageToQualityCH` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_A |
| `CameraSet_Exposure` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_E |
| `CameraSet_FileName` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_F |
| `CameraSet_FlexibleHeight` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_F |
| `CameraSet_FlipH` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_F |
| `CameraSet_FlipV` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_F |
| `CameraSet_FrameDuration` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_F |
| `CameraSet_HWTrgInEnabled` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_H |
| `CameraSet_HWTrgOutEnabled` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_H |
| `CameraSet_Integrate` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_I |
| `CameraSet_IntegrateCH` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_I |
| `CameraSet_IntegrateToQualityCH` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_I |
| `CameraSet_Negate` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_N |
| `CameraSet_Rotate` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_R |
| `CameraSet_StimulationTime` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_S |
| `CameraSet_ToRGB` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_T |
| `CameraSet_UseDriverMetadata` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_U |
| `CameraSettings_Load` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSetti |
| `CameraSettings_Remove` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSetti |
| `CameraSettings_RemoveAll` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSetti |
| `CameraSettings_Save` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSetti |
| `Camera_AverageSet` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Aver |
| `Camera_ExposureSet` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Expo |
| `Camera_GainBSet` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Gain |
| `Camera_GainRSet` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Gain |
| `Camera_IntegrateSet` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Inte |
| `Camera_RotateSet` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Rota |
| `Camera_SensorModeSet` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Sens |
| `Camera_TriggerModeSet` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_Trig |
| `ChangeFollowExposureMode` | set | no | not reachable | AttributeError: 'Macro' object has no attribute 'ChangeFollo |
| `ROISet` | set | no | not called |  |
| `ROISetLargeFOV` | set | no | not called |  |
| `ROISetOptimalFOV` | set | no | not called |  |
| `SetSaveExposure` | set | yes | not called |  |
| `SetSaveExposureSetting` | set | yes | not called |  |
| `TrigAcq_SelectDevice` | set | yes | not called |  |
| `TrigAcq_SelectDeviceEx` | set | yes | not called |  |
| `TrigAcq_SetParameters` | set | yes | not called |  |
| `CameraCmd_AutoExposure` | action | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_A |
| `CameraCmd_AutoWhite` | action | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_A |
| `CameraCmd_OnePushWB` | action | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_O |
| `CameraUpdateGUI` | action | no | not reachable | AttributeError: 'Macro' object has no attribute 'CameraUpdat |
| `MatchCameraROI` | action | yes | not called |  |
| `Stg_TriggerInternalCamera` | action | no | not called |  |
| `TrigAcq_AddChannel` | action | yes | not called |  |
| `TrigAcq_AddLine` | action | yes | not called |  |
| `TrigAcq_AddLineEx` | action | yes | not called |  |
| `TrigAcq_DeleteAllItems` | action | yes | not called |  |
| `TrigAcq_DeleteChannel` | action | yes | not called |  |
| `TrigAcq_DeleteLine` | action | yes | not called |  |
| `TrigAcq_ModifyChannel` | action | yes | not called |  |
| `TrigAcq_ModifyLine` | action | yes | not called |  |
| `TrigAcq_UseCustomDevices` | action | yes | not called |  |
| `_CameraSetAverageToQuality` | dialog | no | not reachable | AttributeError: 'Macro' object has no attribute '_CameraSetA |
| `_LoadCameraROIFromFile` | dialog | no | not called |  |
| `_SaveCameraROIToFile` | dialog | no | not called |  |

## Acquisition

Capture, live, freeze, RAM capture, ND experiments.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `ND_GetLambdaChannel` | read | yes | not called |  |
| `ND_GetMultipointEnabled` | read | yes | not called |  |
| `ND_GetMultipointName` | read | yes | not called |  |
| `ND_GetTimeExp` | read | yes | not called |  |
| `ND_GetTimeExpPhase` | read | yes | not called |  |
| `ND_GetTimeLapsePhaseCount` | read | yes | not called |  |
| `ND_GetTimePhase` | read | yes | not called |  |
| `ND_GetTimePhaseSchedule` | read | yes | not called |  |
| `ND_GetZSeriesExp` | read | yes | not called |  |
| `ND_GetZSeriesType` | read | yes | not called |  |
| `ND_IsInExperimentCapture` | read | yes | not called |  |
| `AutoCaptureAndStore` | set | yes | not called |  |
| `MCHCapturingOpen` | set | yes | not called |  |
| `MCHCapturingSetPlane` | set | yes | not called |  |
| `ND_RunMultipointSet` | set | yes | not called |  |
| `ND_SetLambdaEnabled` | set | yes | not called |  |
| `ND_SetLambdaExp` | set | yes | not called |  |
| `ND_SetLambdaRepresentation` | set | yes | not called |  |
| `ND_SetMultiPoints` | set | yes | not called |  |
| `ND_SetMultiPointsEx` | set | yes | not called |  |
| `ND_SetMultipointEnabled` | set | yes | not called |  |
| `ND_SetMultipointExp` | set | yes | not called |  |
| `ND_SetTimeEnabled` | set | yes | not called |  |
| `ND_SetTimeExp` | set | yes | not called |  |
| `ND_SetTimeExpPhase` | set | yes | not called |  |
| `ND_SetZSeriesExp` | set | yes | not called |  |
| `ND_SetZSeriesType` | set | yes | not called |  |
| `RAMCapturingEnable` | set | no | not called |  |
| `RAMCapturingSetFrames` | set | no | not called |  |
| `RAMCapturingSetTime` | set | no | not called |  |
| `Acquire` | action | no | not called |  |
| `AcquireEx` | action | no | not called |  |
| `AutoCapture` | action | yes | not called |  |
| `AutoCapture2` | action | no | not called |  |
| `Capture` | action | yes | needs the camera | not run: the camera is off |
| `CaptureEx` | action | yes | needs the camera | not run: the camera is off |
| `CaptureExWithName` | action | yes | needs the camera | not run: the camera is off |
| `CaptureFast` | action | no | not reachable | AttributeError: 'Macro' object has no attribute 'CaptureFast |
| `CapturePreview` | action | no | not called |  |
| `CapturePreview2` | action | no | not called |  |
| `CapturePreviewNoMsgLoop` | action | no | not called |  |
| `CapturePreviewSync` | action | no | not called |  |
| `FineGrab` | action | no | not reachable | AttributeError: 'Macro' object has no attribute 'FineGrab' |
| `FineGrab2` | action | no | not called |  |
| `Freeze` | action | no | not called |  |
| `Freeze2` | action | no | not called |  |
| `Freeze_LiveOrND` | action | yes | not called |  |
| `Live` | action | no | not called |  |
| `LiveSync` | action | no | not called |  |
| `LiveSync2` | action | no | not called |  |
| `MCHCapturingAuto` | action | yes | not called |  |
| `MCHCapturingCapture` | action | yes | not called |  |
| `MCHCapturingFinish` | action | yes | not called |  |
| `MCHCapturingLive` | action | yes | not called |  |
| `MCHCapturingNew` | action | yes | not called |  |
| `ND_CustomCapture` | action | yes | not called |  |
| `ND_DefineExperiment` | action | yes | not called |  |
| `ND_PauseExperiment` | action | yes | not called |  |
| `ND_ResumeExperiment` | action | yes | not called |  |
| `ND_RunExperiment` | action | yes | not called |  |
| `ND_RunExperimentNoProgressBar` | action | yes | not called |  |
| `ND_RunExperimentWithZIntensityCorrection` | action | yes | not called |  |
| `ND_RunLambdaExp` | action | yes | not called |  |
| `ND_RunMultipointExp` | action | yes | not called |  |
| `ND_RunNDAdvanced` | action | yes | not called |  |
| `ND_RunSequentialStimulationExp` | action | yes | not called |  |
| `ND_RunSimultaneousStimulationExp` | action | yes | not called |  |
| `ND_RunTimeExp` | action | yes | not called |  |
| `ND_RunZSeriesExp` | action | yes | not called |  |
| `ND_RunZSeriesExpWithZIntensityCorrection` | action | yes | not called |  |
| `RAMCapturing` | action | no | not called |  |
| `_Acquire` | dialog | no | not called |  |
| `_CaptureHDR` | dialog | yes | needs the camera | not run: the camera is off |
| `_CaptureZStack` | dialog | yes | needs the camera | not run: the camera is off |
| `_Grabbing` | dialog | yes | needs the camera | not run: the camera is off |
| `_MCHCapturingSetup` | dialog | yes | not called |  |
| `_ND_CaptureMultipointManually` | dialog | yes | not called |  |
| `_ND_CaptureTimelapseManually` | dialog | yes | not called |  |
| `_ND_CaptureZManually` | dialog | yes | not called |  |
| `_RAMCapturingSettings` | dialog | no | not called |  |

## Calibration

Pixel size and image calibration.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `GetCalibrationViewUnit` | read | yes | needs arguments | error: Bad number of parameters |
| `Get_Calibration` | read | yes | needs arguments | error: Bad number of parameters |
| `Get_CalibrationAngleMatrix` | read | yes | needs arguments | error: Bad number of parameters |
| `Get_CurrentCalibration` | read | yes | needs arguments | error: Bad number of parameters |
| `Get_ImageCalibration` | read | yes | needs arguments | error: Bad number of parameters |
| `SetCalibrationViewPrecision` | set | yes | not called |  |
| `SetCalibrationViewUnit` | set | yes | not called |  |
| `SaveImageCalibration` | action | yes | not called |  |
| `StgCalibrateXYAutomatic` | action | yes | not called |  |
| `Stg_CalibratedAnalogOutputWrite` | action | yes | not called |  |
| `Stg_Perfusion_LoadCalibrationFromXML` | action | yes | not called |  |
| `_QuickCalibration` | dialog | yes | not called |  |

## Image documents and files

Save, open, close, image info, files, disk space, memory.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `GetFileAbsTime` | read | yes | ran | -1.0 |
| `GetFreeDiskSpace` | read | yes | needs arguments | error: Bad number of parameters |
| `GetOpenedDocumentList` | read | yes | needs arguments | error: Bad number of parameters |
| `Get_FileSize` | read | yes | needs arguments | error: Bad number of parameters |
| `Get_FileTitle` | read | yes | needs arguments | error: Bad number of parameters |
| `Get_Filename` | read | yes | needs arguments | error: Bad number of parameters |
| `Get_ImageInfo` | read | yes | needs arguments | error: Bad number of parameters |
| `ImageOpen` | set | yes | not called |  |
| `ImageReuseCameraSettings` | set | yes | not called |  |
| `ImageReuseDeviceSettings` | set | yes | not called |  |
| `ImageReuseStimulationSettings` | set | yes | not called |  |
| `SetCaptureCreatesNewDoc` | set | yes | not called |  |
| `SetMaxMemoryImageSize` | set | yes | not called |  |
| `CloseAllDocuments` | action | yes | not called |  |
| `CloseAllDocumentsButCurrent` | action | yes | not called |  |
| `CloseCurrentDocument` | action | yes | not called |  |
| `DeleteCurrentImage` | action | yes | not called |  |
| `ImageReload` | action | yes | not called |  |
| `ImageReuseCameraROI` | action | yes | not called |  |
| `ImageReuseExperiment` | action | yes | not called |  |
| `ImageReuseOptConf` | action | yes | not called |  |
| `ImageSave` | action | yes | not called |  |
| `ImageSaveAs` | action | yes | not called |  |
| `ImageSaveAsEx` | action | yes | not called |  |
| `ImageSaveNext` | action | yes | not called |  |
| `OpenDocument` | action | yes | not called |  |
| `SaveAll` | action | yes | not called |  |
| `SaveCurrentDocument` | action | yes | not called |  |
| `ImageSaveNextSuppressDialog` | dialog | yes | not called |  |
| `_CloseAllDocuments` | dialog | yes | not called |  |
| `_CloseAllDocumentsButCurrent` | dialog | yes | not called |  |
| `_CloseCurrentDocument` | dialog | yes | not called |  |
| `_ImageOpen` | dialog | yes | not called |  |
| `_ImageSave` | dialog | yes | not called |  |
| `_ImageSaveAs` | dialog | yes | not called |  |
| `_ImageSaveNextSettings` | dialog | yes | not called |  |
| `_SetTempFilesPathForNextSession` | dialog | yes | not called |  |

## Incubation and environment

Incubator, heat stage, perfusion, water.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `Stg_HeatStageGetCurrentTemperature` | read | yes | not called |  |
| `Stg_HeatStageGetStatus` | read | yes | not called |  |
| `Stg_HeatStage_GetCount` | read | yes | ran | 0 |
| `Stg_HeatStage_GetCurrentTemperature` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_HeatStage_GetName` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_HeatStage_GetStatus` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Incubator_GetCurrentGas` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Incubator_GetCurrentHumidity` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Incubator_GetCurrentPressure` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Incubator_GetPressureRange` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Incubator_GetTargetGas` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Incubator_GetTargetHumidity` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Incubator_GetTargetPressure` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_Perfusion_GetState` | read | yes | ran | 0 |
| `Stg_WID_GetLastReplenishmentTime` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_WID_Get |
| `Stg_WID_GetReplenishmentRemainingTimeInSeconds` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_WID_Get |
| `Stg_WID_GetReplenishmentTimePeriodInSeconds` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_WID_Get |
| `Stg_WID_GetWaterInitiated` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_WID_Get |
| `Stg_HeatStageHoldCurrentTemperature` | set | yes | not called |  |
| `Stg_HeatStageSetTemperature` | set | yes | not called |  |
| `Stg_HeatStageSetTemperatureRate` | set | yes | not called |  |
| `Stg_HeatStage_HoldCurrentTemperature` | set | yes | not called |  |
| `Stg_HeatStage_SetTemperature` | set | yes | not called |  |
| `Stg_HeatStage_SetTemperatureRate` | set | yes | not called |  |
| `Stg_Incubator_SetAtmosphericPressure` | set | yes | not called |  |
| `Stg_Incubator_SetTargetGas` | set | yes | not called |  |
| `Stg_Incubator_SetTargetHumidity` | set | yes | not called |  |
| `Stg_Incubator_SetTargetPressure` | set | yes | not called |  |
| `Stg_Incubator_SetVacuumPressure` | set | yes | not called |  |
| `Stg_Perfusion_Purge_mL` | set | yes | not called |  |
| `Stg_Perfusion_SetSolvent` | set | yes | not called |  |
| `Stg_HeatStageContinueCooling` | action | yes | not called |  |
| `Stg_HeatStageContinueHeating` | action | yes | not called |  |
| `Stg_HeatStageIsPresent` | action | yes | not called |  |
| `Stg_HeatStageStartHeatingCooling` | action | yes | not called |  |
| `Stg_HeatStageStopHeatingCooling` | action | yes | not called |  |
| `Stg_HeatStage_ContinueCooling` | action | yes | not called |  |
| `Stg_HeatStage_ContinueHeating` | action | yes | not called |  |
| `Stg_HeatStage_StartHeatingCooling` | action | yes | not called |  |
| `Stg_HeatStage_StopHeatingCooling` | action | yes | not called |  |
| `Stg_Perfusion_Clean` | action | yes | not called |  |
| `Stg_Perfusion_Dispence_mL` | action | yes | not called |  |
| `Stg_WID_Abort` | action | no | not called |  |
| `Stg_WID_AllowAutomaticReplenishment` | action | no | not called |  |
| `Stg_WID_Discharge` | action | no | not called |  |
| `Stg_WID_Initiate` | action | no | not called |  |
| `Stg_WID_Replenish` | action | no | not called |  |
| `Stg_WID_WaitForFinish` | action | no | not called |  |

## Triggers and stimulation

TTL, triggers, DMD and patterns.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `GetActivePFIForTriggering` | read | yes | needs arguments | error: Bad number of parameters |
| `IsPatternDefined` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetDMDActivePatternId` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetDMDAssociatedSwitcherId` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetDMDA |
| `Stg_GetDMDAssociatedSwitcherPosition` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetDMDA |
| `Stg_GetDMDCalibrated` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetDMDDeviceCount` | read | yes | ran | 0 |
| `Stg_GetDMDDeviceName` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetDMDPatternCount` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetDMDPatternId` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetDMDPatternIdByName` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetDMDPatternName` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetPatternDeviceName` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPatt |
| `Stg_GetPatternId` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPatt |
| `Stg_GetPatternIdByName` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPatt |
| `Stg_GetPatternName` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPatt |
| `Stg_GetPatternState` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPatt |
| `Stg_GetPinConfiguredForTTLOutput` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPinC |
| `Stg_GetPinConfiguredForTTLOutputPulse` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPinC |
| `Stg_GetPinTTLOutputState` | read | no | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPinT |
| `Stg_GetTTLStatus` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_TTLOutputGetControlMode` | read | yes | not called |  |
| `Stg_TTLOutputGetControlModePulses` | read | yes | not called |  |
| `Stg_TTLOutputGetPulseActiveState` | read | yes | not called |  |
| `Stg_TTLOutputGetPulseTime` | read | yes | not called |  |
| `Mosaic_SetPattern` | set | no | not called |  |
| `SelectPattern` | set | yes | not called |  |
| `SetActivePFIForTriggering` | set | yes | not called |  |
| `StgSetTrigger` | set | yes | not called |  |
| `Stg_SetDMDActivePatternId` | set | yes | not called |  |
| `Stg_SetPinTTLOutputPulse` | set | no | not called |  |
| `Stg_SetPinTTLOutputState` | set | no | not called |  |
| `Stg_TTLOutputSetControlMode` | set | yes | not called |  |
| `Stg_TTLOutputSetPulseActiveState` | set | yes | not called |  |
| `Stg_TTLOutputSetPulseTime` | set | yes | not called |  |
| `AddPattern` | action | yes | not called |  |
| `AddPatternEx` | action | yes | not called |  |
| `RemovePattern` | action | yes | not called |  |
| `Stg_AnalogInputRead` | action | yes | not called |  |
| `Stg_AnalogOutputRead` | action | yes | not called |  |
| `Stg_AnalogOutputWrite` | action | yes | not called |  |
| `Stg_DIOReadInputs` | action | yes | not called |  |
| `Stg_DMD_AppendRoiAsPattern` | action | yes | not called |  |
| `Stg_PulseTTL` | action | yes | not called |  |
| `Stg_StimDev_AddPatternFromImage` | action | no | not called |  |
| `Stg_TTLInputRead` | action | yes | not called |  |
| `Stg_TTLOutputDoAction` | action | yes | not called |  |
| `Stg_TTLOutputDoActionAsync` | action | yes | not called |  |
| `Stg_TTLOutputPulse` | action | yes | not called |  |
| `Stg_TTLOutputPulseAsync` | action | yes | not called |  |
| `Stg_TTLOutputPulsesTrain` | action | yes | not called |  |
| `Stg_TTLOutputPulsesTrainAbort` | action | yes | not called |  |
| `Stg_TTLOutputPulsesTrainAsync` | action | yes | not called |  |
| `Stg_TTLOutputPulsesTrainFinished` | action | yes | not called |  |
| `Stg_TTLOutputWrite` | action | yes | not called |  |
| `Stg_WriteTTL` | action | yes | not called |  |
| `_Stg_CalibrateAnalogInput` | dialog | yes | not called |  |
| `_Stg_CalibrateAnalogOutput` | dialog | yes | not called |  |
| `_TriggeredAcquisition` | dialog | yes | not called |  |

## Microscope

Presence, sleep, the device log, NIS version.

| Function | Kind | Reachable now | Step 2 | Answer |
|---|---|---|---|---|
| `GetDeviceCommunicationLog` | read | yes | ran | 1 |
| `Get_Info` | read | yes | needs arguments | error: Bad number of parameters |
| `Get_InfoStr` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetLineIndex` | read | yes | needs arguments | error: Bad number of parameters |
| `Stg_GetMicroscopeSleep` | read | yes | ran | 0 |
| `Stg_IsMicroscopePresent` | read | yes | ran | 0 |
| `ClearLog` | set | yes | not called |  |
| `Stg_CloseMicroscopeDoor` | set | no | not called |  |
| `Stg_EnableMicControlPad` | set | yes | not called |  |
| `Stg_OpenMicroscopeDoor` | set | no | not called |  |
| `Stg_SetBlockMicroscopeAccessories` | set | no | not called |  |
| `Stg_ToggleMicControlPad` | set | yes | not called |  |
| `DeviceCommunicationLog` | action | yes | not called |  |
| `Stg_MicroscopeMuteSound` | action | no | not called |  |
| `Stg_MicroscopeOperationSound` | action | no | not called |  |
| `Stg_MicroscopeSleep` | action | yes | not called |  |
| `Stg_RemoveInterlock` | action | yes | not called |  |
| `Stg_ShutdownMicroscope` | action | no | not called |  |
