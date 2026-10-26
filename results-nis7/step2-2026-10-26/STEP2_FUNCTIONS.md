# Step 2: every AR function, called

Every macro function of NIS-Elements AR 7.01.03, called once through `nis.mac` with no
arguments, microscope off. *ran*: it needed no arguments and ran. *needs arguments*: NIS
answered "Bad number of parameters", so it is reachable but was not run. *dialog*: a
window the call opened, closed by the watch window. Spreadsheet: `step2_functions.csv`.

| Section | ran | needs arguments | needs the camera | not reachable | crashed or hung | not called | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| [Acquire](#acquire) | 4 | 15 | 16 | 109 | 1 | 207 | 352 |
| [AdvancedAPI](#advancedapi) | 1 | 9 | 0 | 0 | 0 | 138 | 148 |
| [Analysis](#analysis) | 1 | 5 | 0 | 0 | 0 | 222 | 228 |
| [Applications](#applications) | 0 | 0 | 0 | 1 | 0 | 197 | 198 |
| [Binary](#binary) | 1 | 1 | 0 | 0 | 0 | 390 | 392 |
| [Calibration](#calibration) | 0 | 4 | 0 | 0 | 0 | 17 | 21 |
| [Device](#device) | 77 | 126 | 0 | 39 | 0 | 372 | 614 |
| [ExportResults](#exportresults) | 0 | 0 | 0 | 0 | 0 | 57 | 57 |
| [Image](#image) | 0 | 4 | 0 | 0 | 1 | 580 | 585 |
| [ImageDocument](#imagedocument) | 1 | 9 | 0 | 0 | 0 | 137 | 147 |
| [Macro](#macro) | 0 | 2 | 0 | 0 | 0 | 60 | 62 |
| [Measure](#measure) | 2 | 54 | 0 | 0 | 0 | 117 | 173 |
| [Misc](#misc) | 0 | 0 | 0 | 0 | 0 | 7 | 7 |
| [ND](#nd) | 1 | 0 | 0 | 0 | 0 | 219 | 220 |
| [Organizer](#organizer) | 4 | 12 | 0 | 0 | 0 | 59 | 75 |
| [System](#system) | 5 | 7 | 0 | 0 | 0 | 99 | 111 |
| [UserInterface](#userinterface) | 0 | 0 | 0 | 0 | 0 | 26 | 26 |
| [View](#view) | 4 | 4 | 0 | 0 | 0 | 194 | 202 |
| [Visualization](#visualization) | 0 | 0 | 0 | 0 | 0 | 49 | 49 |
| **All** | **101** | **252** | **16** | **149** | **2** | **3147** | **3667** |

## Acquire

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `CameraCmd_AutoExposure` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_AutoExposure' |  |  |   |
| `CameraCmd_AutoWhite` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_AutoWhite' |  |  |   |
| `CameraCmd_AverageReset` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_AverageReset' |  |  |   |
| `CameraCmd_OnePushWB` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_OnePushWB' |  |  |   |
| `CameraCmd_SetDefaults` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_SetDefaults' |  |  |   |
| `CameraCmd_TurnFanOff` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_TurnFanOff' |  |  |   |
| `CameraCmd_TurnFanOn` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraCmd_TurnFanOn' |  |  |   |
| `CameraGet_Average` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_Average' |  |  |   |
| `CameraGet_AverageCH` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_AverageCH' |  |  |   |
| `CameraGet_AverageToQuality` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_AverageToQuality' |  |  |   |
| `CameraGet_AverageToQualityCH` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_AverageToQualityCH' |  |  |   |
| `CameraGet_Exposure` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_Exposure' |  |  |   |
| `CameraGet_FileName` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_FileName' |  |  |   |
| `CameraGet_FlexibleHeight` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_FlexibleHeight' |  |  |   |
| `CameraGet_FrameDuration` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_FrameDuration' |  |  |   |
| `CameraGet_HWTrgInEnabled` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_HWTrgInEnabled' |  |  |   |
| `CameraGet_HWTrgOutEnabled` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_HWTrgOutEnabled' |  |  |   |
| `CameraGet_Integrate` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_Integrate' |  |  |   |
| `CameraGet_IntegrateCH` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_IntegrateCH' |  |  |   |
| `CameraGet_IntegrateToQualityCH` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_IntegrateToQualityCH' |  |  |   |
| `CameraGet_Negate` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_Negate' |  |  |   |
| `CameraGet_Rotate` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_Rotate' |  |  |   |
| `CameraGet_StimulationTime` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_StimulationTime' |  |  |   |
| `CameraGet_ToRGB` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_ToRGB' |  |  |   |
| `CameraGet_UseDriverMetadata` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraGet_UseDriverMetadata' |  |  |   |
| `CameraSet_Average` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_Average' |  |  |   |
| `CameraSet_AverageCH` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_AverageCH' |  |  |   |
| `CameraSet_AverageToQuality` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_AverageToQuality' |  |  |   |
| `CameraSet_AverageToQualityCH` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_AverageToQualityCH' |  |  |   |
| `CameraSet_Exposure` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_Exposure' |  |  |   |
| `CameraSet_FileName` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_FileName' |  |  |   |
| `CameraSet_FlexibleHeight` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_FlexibleHeight' |  |  |   |
| `CameraSet_FlipH` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_FlipH' |  |  |   |
| `CameraSet_FlipV` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_FlipV' |  |  |   |
| `CameraSet_FrameDuration` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_FrameDuration' |  |  |   |
| `CameraSet_HWTrgInEnabled` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_HWTrgInEnabled' |  |  |   |
| `CameraSet_HWTrgOutEnabled` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_HWTrgOutEnabled' |  |  |   |
| `CameraSet_Integrate` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_Integrate' |  |  |   |
| `CameraSet_IntegrateCH` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_IntegrateCH' |  |  |   |
| `CameraSet_IntegrateToQualityCH` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_IntegrateToQualityCH' |  |  |   |
| `CameraSet_Negate` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_Negate' |  |  |   |
| `CameraSet_Rotate` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_Rotate' |  |  |   |
| `CameraSet_StimulationTime` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_StimulationTime' |  |  |   |
| `CameraSet_ToRGB` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_ToRGB' |  |  |   |
| `CameraSet_UseDriverMetadata` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSet_UseDriverMetadata' |  |  |   |
| `CameraFormatGet` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraFormatGet' |  |  |   |
| `CameraFormatSet` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraFormatSet' |  |  |   |
| `CameraSettings_Load` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSettings_Load' |  |  |   |
| `CameraSettings_Remove` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSettings_Remove' |  |  |   |
| `CameraSettings_RemoveAll` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSettings_RemoveAll' |  |  |   |
| `CameraSettings_Save` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraSettings_Save' |  |  |   |
| `CameraUpdateGUI` | not reachable | AttributeError: 'Macro' object has no attribute 'CameraUpdateGUI' |  |  |   |
| `Camera_AngleGet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_AngleGet' |  |  |   |
| `Camera_AverageGet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_AverageGet' |  |  |   |
| `Camera_AverageSet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_AverageSet' |  |  |   |
| `Camera_ExposureGet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_ExposureGet' |  |  |   |
| `Camera_ExposureSet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_ExposureSet' |  |  |   |
| `Camera_GainRGet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_GainRGet' |  |  |   |
| `Camera_GainRSet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_GainRSet' |  |  |   |
| `Camera_GainBGet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_GainBGet' |  |  |   |
| `Camera_GainBSet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_GainBSet' |  |  |   |
| `Camera_IntegrateGet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_IntegrateGet' |  |  |   |
| `Camera_IntegrateSet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_IntegrateSet' |  |  |   |
| `Camera_RelayLensGet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_RelayLensGet' |  |  |   |
| `Camera_RelayLensSet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_RelayLensSet' |  |  |   |
| `Camera_RotateGet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_RotateGet' |  |  |   |
| `Camera_RotateSet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_RotateSet' |  |  |   |
| `Camera_SensorModeGet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_SensorModeGet' |  |  |   |
| `Camera_SensorModeSet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_SensorModeSet' |  |  |   |
| `Camera_TemperatureGet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_TemperatureGet' |  |  |   |
| `Camera_TriggerModeGet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_TriggerModeGet' |  |  |   |
| `Camera_TriggerModeSet` | not reachable | AttributeError: 'Macro' object has no attribute 'Camera_TriggerModeSet' |  |  |   |
| `ChangeFollowExposureMode` | not reachable | AttributeError: 'Macro' object has no attribute 'ChangeFollowExposureMode' |  |  |   |
| `EnableFocusCriterium` | not reachable | AttributeError: 'Macro' object has no attribute 'EnableFocusCriterium' |  |  |   |
| `EnableMouseXY` | needs arguments | error: Bad number of parameters |  |  |   |
| `EnableTrackXY` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetCameraName` | not reachable | AttributeError: 'Macro' object has no attribute 'GetCameraName' |  |  |   |
| `GetCameraResolution` | not reachable | AttributeError: 'Macro' object has no attribute 'GetCameraResolution' |  |  |   |
| `GetCurrentCameraDriverName` | not reachable | AttributeError: 'Macro' object has no attribute 'GetCurrentCameraDriverName' |  |  |   |
| `GetCurrentCameraName` | not reachable | AttributeError: 'Macro' object has no attribute 'GetCurrentCameraName' |  |  |   |
| `GetFollowExposureMode` | not reachable | AttributeError: 'Macro' object has no attribute 'GetFollowExposureMode' |  |  |   |
| `InputCameraEx` | not reachable | AttributeError: 'Macro' object has no attribute 'InputCameraEx' |  |  |   |
| `InputHWUnit` | not reachable | AttributeError: 'Macro' object has no attribute 'InputHWUnit' |  |  |   |
| `LockCameraMagnification` | needs arguments | error: Bad number of parameters |  |  |   |
| `ManualIntegration` | not reachable | AttributeError: 'Macro' object has no attribute 'ManualIntegration' |  |  |   |
| `ResetFocusCriteriumMax` | not reachable | AttributeError: 'Macro' object has no attribute 'ResetFocusCriteriumMax' |  |  |   |
| `ShowShadingCorrections` | needs the camera | not run: the camera is off |  |  |   |
| `TestMacroToClipboard_CameraGet` | not called |  |  |  |   |
| `TestMacroToClipboard_CameraGetAndSet` | not called |  |  |  |   |
| `ToggleInputSetup` | not reachable | AttributeError: 'Macro' object has no attribute 'ToggleInputSetup' |  |  |   |
| `TrackXYSetup` | ran | None |  |  |   |
| `_CameraSetAverageToQuality` | not reachable | AttributeError: 'Macro' object has no attribute '_CameraSetAverageToQuality' |  |  |   |
| `_InputCameraEx` | not reachable | AttributeError: 'Macro' object has no attribute '_InputCameraEx' |  |  |   |
| `_InputDriver` | not reachable | AttributeError: 'Macro' object has no attribute '_InputDriver' |  |  |   |
| `_InputHWUnit` | not reachable | AttributeError: 'Macro' object has no attribute '_InputHWUnit' |  |  |   |
| `_InputHWUnitAndCamera` | not reachable | AttributeError: 'Macro' object has no attribute '_InputHWUnitAndCamera' |  |  |   |
| `_InputHWUnitAndCamera2` | not reachable | AttributeError: 'Macro' object has no attribute '_InputHWUnitAndCamera2' |  |  |   |
| `_InputSetup` | not reachable | AttributeError: 'Macro' object has no attribute '_InputSetup' |  |  |   |
| `_ManualIntegration` | not reachable | AttributeError: 'Macro' object has no attribute '_ManualIntegration' |  |  |   |
| `Capture` | needs the camera | not run: the camera is off |  |  |   |
| `CaptureEx` | needs the camera | not run: the camera is off |  |  |   |
| `CaptureExWithName` | needs the camera | not run: the camera is off |  |  |   |
| `CaptureFast` | not reachable | AttributeError: 'Macro' object has no attribute 'CaptureFast' |  |  |   |
| `FineGrab` | not reachable | AttributeError: 'Macro' object has no attribute 'FineGrab' |  |  |   |
| `_CaptureEDF` | needs the camera | not run: the camera is off |  |  |   |
| `_CaptureHDR` | needs the camera | not run: the camera is off |  |  |   |
| `_CaptureZStack` | needs the camera | not run: the camera is off |  |  |   |
| `_Grabbing` | needs the camera | not run: the camera is off |  |  |   |
| `MultiViewEnable` | not reachable | AttributeError: 'Macro' object has no attribute 'MultiViewEnable' |  |  |   |
| `MultiViewEnabled` | not reachable | AttributeError: 'Macro' object has no attribute 'MultiViewEnabled' |  |  |   |
| `MultiViewSourceSet` | not reachable | AttributeError: 'Macro' object has no attribute 'MultiViewSourceSet' |  |  |   |
| `MultiViewSwitch` | not reachable | AttributeError: 'Macro' object has no attribute 'MultiViewSwitch' |  |  |   |
| `_MultiViewSourceDefine` | not reachable | AttributeError: 'Macro' object has no attribute '_MultiViewSourceDefine' |  |  |   |
| `Experiment_ClearChannelParfocalityOffsets` | needs the camera | not run: the camera is off |  |  |   |
| `Experiment_DetectParfocalities` | needs the camera | not run: the camera is off |  |  |   |
| `Experiment_RunAutoAll` | needs the camera | not run: the camera is off |  |  |   |
| `Experiment_RunAutoBrightnessAndFocusOnAllChannels` | not reachable | AttributeError: 'Macro' object has no attribute 'Experiment_RunAutoBrightnessAndFocusOnAllChannels' |  |  |   |
| `Experiment_RunAutoBrightnessOnAllChannels` | needs the camera | not run: the camera is off |  |  |   |
| `Experiment_SaveChannelParfocalityOffsets` | needs the camera | not run: the camera is off |  |  |   |
| `_Experiment_ShowExperimentSetupDialog` | needs arguments | error: Bad number of parameters |  |  |   |
| `IlluminationSequence_Run` | not reachable | AttributeError: 'Macro' object has no attribute 'IlluminationSequence_Run' |  |  |   |
| `_IlluminationSequence` | not reachable | AttributeError: 'Macro' object has no attribute '_IlluminationSequence' |  |  |   |
| `LargeImageGrabbingWithName` | needs the camera | not run: the camera is off |  |  |   |
| `SplitLargeImage` | needs arguments | error: Bad number of parameters |  |  |   |
| `StitchLargeImage` | needs arguments | error: Bad number of parameters |  |  |   |
| `StitchLargeImageEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `_LargeImageGrabbing` | needs the camera | not run: the camera is off |  |  |   |
| `_LargeImageGrabbingFreeShape` | needs the camera | not run: the camera is off |  |  |   |
| `_ManualLargeImage` | crashed or hung | NIS crashed or hung in this call; the run was started again after it |  |  |   |
| `_SplitLargeImage` | ran | -9 |  |  |   |
| `_StitchLargeImage` | not called |  |  |  |   |
| `LiveWindowSetup` | not called |  |  |  |   |
| `SplitHorizontallyLiveBottom` | not called |  |  |  |   |
| `SplitHorizontallyLiveTop` | not called |  |  |  |   |
| `SplitVerticallyLiveLeft` | not called |  |  |  |   |
| `SplitVerticallyLiveRight` | not called |  |  |  |   |
| `ViewAlternateLive` | not called |  |  |  |   |
| `ViewBinaryMaskedLive` | not called |  |  |  |   |
| `ViewDifferenceLive` | not called |  |  |  |   |
| `ViewInterlacedLive` | not called |  |  |  |   |
| `ViewLiveRectangle` | not called |  |  |  |   |
| `ViewPseudoRedGreenLive` | not called |  |  |  |   |
| `ViewTransparentLive` | not called |  |  |  |   |
| `_DefineCameraCorrection` | not called |  |  |  |   |
| `LiveProcessing` | not called |  |  |  |   |
| `LiveProcessingToggleGUI` | not called |  |  |  |   |
| `MCHCapturingAuto` | not called |  |  |  |   |
| `MCHCapturingCapture` | not called |  |  |  |   |
| `MCHCapturingFinish` | not called |  |  |  |   |
| `MCHCapturingLive` | not called |  |  |  |   |
| `MCHCapturingNew` | not called |  |  |  |   |
| `MCHCapturingOpen` | not called |  |  |  |   |
| `MCHCapturingSetPlane` | not called |  |  |  |   |
| `_MCHCapturingSetup` | not called |  |  |  |   |
| `MultiExcitationEnable` | not called |  |  |  |   |
| `MultiExcitationEnabled` | not called |  |  |  |   |
| `MultiExcitationSequenceSet` | not called |  |  |  |   |
| `MultiExcitationSwitch` | not called |  |  |  |   |
| `TrigAcq_AddChannel` | not called |  |  |  |   |
| `TrigAcq_AddLine` | not called |  |  |  |   |
| `TrigAcq_AddLineEx` | not called |  |  |  |   |
| `TrigAcq_DeleteAllItems` | not called |  |  |  |   |
| `TrigAcq_DeleteChannel` | not called |  |  |  |   |
| `TrigAcq_DeleteLine` | not called |  |  |  |   |
| `TrigAcq_GetChannel` | not called |  |  |  |   |
| `TrigAcq_GetLine` | not called |  |  |  |   |
| `TrigAcq_GetParameters` | not called |  |  |  |   |
| `TrigAcq_GetUsedCustomDevices` | not called |  |  |  |   |
| `TrigAcq_ModifyChannel` | not called |  |  |  |   |
| `TrigAcq_ModifyLine` | not called |  |  |  |   |
| `TrigAcq_SelectDevice` | not called |  |  |  |   |
| `TrigAcq_SelectDeviceEx` | not called |  |  |  |   |
| `TrigAcq_SetParameters` | not called |  |  |  |   |
| `TrigAcq_UseCustomDevices` | not called |  |  |  |   |
| `_MultiExcitationSequenceDefine` | not called |  |  |  |   |
| `_TriggeredAcquisition` | not called |  |  |  |   |
| `AutoCapture2` | not called |  |  |  |   |
| `CapturePreview2` | not called |  |  |  |   |
| `FineGrab2` | not called |  |  |  |   |
| `Freeze2` | not called |  |  |  |   |
| `GetActiveGrabber` | not reachable | AttributeError: 'Macro' object has no attribute 'GetActiveGrabber' |  |  |   |
| `GetActiveGrabberCount` | not reachable | AttributeError: 'Macro' object has no attribute 'GetActiveGrabberCount' |  |  |   |
| `Live2` | not called |  |  |  |   |
| `LiveSync2` | not called |  |  |  |   |
| `SetActiveGrabber` | not called |  |  |  |   |
| `ZStack_Live2` | not called |  |  |  |   |
| `_DefineCameraLightPath` | not called |  |  |  |   |
| `_InputDriver2` | not called |  |  |  |   |
| `EnableCameraCorrection` | not called |  |  |  |   |
| `EnableCameraCorrectionFQ` | not called |  |  |  |   |
| `_TestAndView` | not called |  |  |  |   |
| `RAMCapturing` | not called |  |  |  |   |
| `RAMCapturingEnable` | not called |  |  |  |   |
| `RAMCapturingSetFrames` | not called |  |  |  |   |
| `RAMCapturingSetTime` | not called |  |  |  |   |
| `_RAMCapturingSettings` | not called |  |  |  |   |
| `ROIEnable` | not called |  |  |  |   |
| `ROIEnabled` | not called |  |  |  |   |
| `ROIGet` | not called |  |  |  |   |
| `ROISet` | not called |  |  |  |   |
| `ROISetLargeFOV` | not called |  |  |  |   |
| `ROISetOptimalFOV` | not called |  |  |  |   |
| `_LoadCameraROIFromFile` | not called |  |  |  |   |
| `_ROIDefine` | not called |  |  |  |   |
| `_ROIDefineLargeFOV` | not called |  |  |  |   |
| `_ROIDefineOnCaptured` | not called |  |  |  |   |
| `_ROIDefineOptimalFOV` | not called |  |  |  |   |
| `_SaveCameraROIToFile` | not called |  |  |  |   |
| `Confocal_GetScanArea` | not called |  |  |  |   |
| `Confocal_GetScanAreaCropped` | not called |  |  |  |   |
| `Confocal_GetScanAreaLine` | not called |  |  |  |   |
| `Confocal_GetScanAreaMode` | not called |  |  |  |   |
| `Confocal_ResetScanArea` | not called |  |  |  |   |
| `Confocal_ReuseScanAreaSettings` | not called |  |  |  |   |
| `Confocal_SetScanArea` | not called |  |  |  |   |
| `Confocal_SetScanAreaCropped` | not called |  |  |  |   |
| `Confocal_SetScanAreaLine` | not called |  |  |  |   |
| `ApplyShading` | not called |  |  |  |   |
| `AutoshadeAtOnce` | not called |  |  |  |   |
| `AutoshadeAtOnceND` | not called |  |  |  |   |
| `EnableCommonShading` | not called |  |  |  |   |
| `EnableShading` | not called |  |  |  |   |
| `EnableShadingFQ` | not called |  |  |  |   |
| `GetShadingEnabled` | not reachable | AttributeError: 'Macro' object has no attribute 'GetShadingEnabled' |  |  |   |
| `IsShadingMapAvailable` | not reachable | AttributeError: 'Macro' object has no attribute 'IsShadingMapAvailable' |  |  |   |
| `ToggleShading` | not called |  |  |  |   |
| `_CaptureShading` | not called |  |  |  |   |
| `_DeleteShadings` | not called |  |  |  |   |
| `_ImageSaveAsShading` | not called |  |  |  |   |
| `_ShowShading` | not called |  |  |  |   |
| `GetActivePFIForTriggering` | needs arguments | error: Bad number of parameters |  |  |   |
| `SetActivePFIForTriggering` | not called |  |  |  |   |
| `Acquire` | not called |  |  |  |   |
| `AcquireEx` | not called |  |  |  |   |
| `_Acquire` | not called |  |  |  |   |
| `_SelectTwainSource` | not called |  |  |  |   |
| `AVIAcquisitionStart` | not called |  |  |  |   |
| `AVIAcquisitionStop` | not called |  |  |  |   |
| `CreateAVIFromSequence` | not called |  |  |  |   |
| `CreateAVIFromSequenceEx` | not called |  |  |  |   |
| `CreateSequenceFromAVI` | not called |  |  |  |   |
| `_CreateAVIFromSequence` | not called |  |  |  |   |
| `_CreateSequenceFromAVI` | not called |  |  |  |   |
| `_SaveAVI` | not called |  |  |  |   |
| `AutoCapture` | not called |  |  |  |   |
| `AutoCreateCorrectionImages` | not called |  |  |  |   |
| `AutoCreateShadingCorrectionImage` | not called |  |  |  |   |
| `AutoCaptureAndStore` | not called |  |  |  |   |
| `CaptureButtonEvent` | not called |  |  |  |   |
| `CapturePreview` | not called |  |  |  |   |
| `CapturePreviewNoMsgLoop` | not called |  |  |  |   |
| `CapturePreviewSync` | not called |  |  |  |   |
| `EnableDistortion` | not called |  |  |  |   |
| `Freeze` | not called |  |  |  |   |
| `Freeze_LiveOrND` | not called |  |  |  |   |
| `GetDistortionEnabled` | not reachable | AttributeError: 'Macro' object has no attribute 'GetDistortionEnabled' |  |  |   |
| `GetShadingDefined` | not reachable | AttributeError: 'Macro' object has no attribute 'GetShadingDefined' |  |  |   |
| `IsDistortionMapAvailable` | needs arguments | error: Bad number of parameters |  |  |   |
| `Live` | not called |  |  |  |   |
| `LiveNoMsgLoop` | not called |  |  |  |   |
| `LiveSync` | not called |  |  |  |   |
| `ND_IsAcqTabChecked` | not called |  |  |  |   |
| `RunAutoBrightness` | not called |  |  |  |   |
| `SetFindMode` | not called |  |  |  |   |
| `ShowAcquisitionToolbarAutoall` | not called |  |  |  |   |
| `ShowAcquisitionToolbarAutofocus` | not called |  |  |  |   |
| `ShowAcquisitionToolbarAutosignal` | not called |  |  |  |   |
| `ShowAcquisitionToolbarCapture` | not called |  |  |  |   |
| `ShowAcquisitionToolbarDeshading` | not called |  |  |  |   |
| `ShowAcquisitionToolbarFind` | not called |  |  |  |   |
| `ShowAcquisitionToolbarLargeImage` | not called |  |  |  |   |
| `ShowAcquisitionToolbarLive` | not called |  |  |  |   |
| `ShowAcquisitionToolbarNDAcquire` | not called |  |  |  |   |
| `ShowInputSetup` | not called |  |  |  |   |
| `StageOverviewClear` | not called |  |  |  |   |
| `ZStack_Live` | not called |  |  |  |   |
| `_CaptureButtonSetup` | not called |  |  |  |   |
| `AddPattern` | not called |  |  |  |   |
| `AddPatternEx` | not called |  |  |  |   |
| `IsPatternDefined` | needs arguments | error: Bad number of parameters |  |  |   |
| `ManualShot` | not called |  |  |  |   |
| `MatchCameraROI` | not called |  |  |  |   |
| `RemovePattern` | not called |  |  |  |   |
| `SelectPattern` | not called |  |  |  |   |
| `Stg_GalvoXY_GetScanningTime` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GalvoXY_GetScanningTime' |  |  |   |
| `_SelectActiveStimOptConf` | not called |  |  |  |   |
| `AddOptConf` | not called |  |  |  |   |
| `BackupExpSetups` | not called |  |  |  |   |
| `BackupOptConf` | not called |  |  |  |   |
| `DeleteExpSetups` | not called |  |  |  |   |
| `DeleteOptConf` | not called |  |  |  |   |
| `DeleteOptConfs` | not called |  |  |  |   |
| `EnableSelectOCFromFilter` | not called |  |  |  |   |
| `GetOptConfCount` | ran | 0 |  |  |   |
| `GetOptConfName` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetSelectedOptConf` | needs arguments | error: Bad number of parameters |  |  |   |
| `RestoreExpSetups` | not called |  |  |  |   |
| `RestoreOptConf` | not called |  |  |  |   |
| `RestoreOptConfEx` | not called |  |  |  |   |
| `SelectOptConf` | not called |  |  |  |   |
| `SelectOptConf_HWOnly` | not called |  |  |  |   |
| `SetOpticalConfChanged` | not called |  |  |  |   |
| `SetSaveCameraSetting` | not called |  |  |  |   |
| `SetSaveExposure` | not called |  |  |  |   |
| `SetSaveExposureSetting` | not called |  |  |  |   |
| `UnselectOptConf` | not called |  |  |  |   |
| `_AddOptConf` | not called |  |  |  |   |
| `_AddOptConfForFluo` | not called |  |  |  |   |
| `_BackupOptConf` | not called |  |  |  |   |
| `_ExploreOptConf` | not called |  |  |  |   |
| `_OptConfSelStimulDevice` | not called |  |  |  |   |
| `_ProbesAndFilters` | not called |  |  |  |   |
| `_RestoreOptConf` | not called |  |  |  |   |
| `_ShutterSelStimulDevice` | not called |  |  |  |   |
| `Stg_ConnectDevice` | not called |  |  |  |   |
| `Stg_DisconnectDevice` | not called |  |  |  |   |
| `Stg_IsStatusStored` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_StatusGet` | not called |  |  |  |   |
| `Stg_StatusSet` | not called |  |  |  |   |
| `Stg_StatusStoreAs` | not called |  |  |  |   |
| `SwitchObjectiveAlert` | not called |  |  |  |   |
| `_ApplyObjectivesXYOffset` | not called |  |  |  |   |
| `_CorrectionManager` | not called |  |  |  |   |
| `_DeviceManagerv2` | not called |  |  |  |   |
| `_JoystickManager` | not called |  |  |  |   |
| `_ListOfPoints` | not called |  |  |  |   |
| `_ManageDevices` | not called |  |  |  |   |
| `Mosaic_SetPattern` | not called |  |  |  |   |
| `CopyUserData` | not called |  |  |  |   |
| `DeleteLightPathLastUsed` | not called |  |  |  |   |
| `DeleteUserData` | not called |  |  |  |   |
| `GetLightPathCount` | ran | 5 |  |  |   |
| `GetLightPathIndexName` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetCurrentLightPathName` | needs arguments | error: Bad number of parameters |  |  |   |
| `SelectLightPath` | not called |  |  |  |   |
| `SelectSetupAndHWConfiguration` | not called |  |  |  |   |
| `SelectSetupAndHWConfigurationNoDialog` | not called |  |  |  |   |
| `ShowDeviceControlDocker` | not called |  |  |  |   |
| `ShowDeviceManagerPad` | not called |  |  |  |   |
| `BlockPort` | not called |  |  |  |   |
| `ClearPort` | not called |  |  |  |   |
| `ClosePort` | not called |  |  |  |   |
| `EnablePortCursors` | not called |  |  |  |   |
| `OpenPort` | not called |  |  |  |   |
| `ReadPort` | not called |  |  |  |   |
| `ReadPortEx` | not called |  |  |  |   |
| `UnblockPort` | not called |  |  |  |   |
| `WaitDeviceTimeOut` | not called |  |  |  |   |
| `WritePort` | not called |  |  |  |   |
| `WritePortAndWait` | not called |  |  |  |   |
| `WritePortEx` | not called |  |  |  |   |
| `_WritePort` | not called |  |  |  |   |

## AdvancedAPI

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `Int_AddItemComboBox` | not called |  |  |  |   |
| `Int_CreateComboBox` | not called |  |  |  |   |
| `Int_ShowComboBox` | not called |  |  |  |   |
| `Int_GetString` | not called |  |  |  |   |
| `Int_GetValue` | not called |  |  |  |   |
| `Int_GetValueEx` | not called |  |  |  |   |
| `Int_Query` | not called |  |  |  |   |
| `Int_Question` | not called |  |  |  |   |
| `Int_DrawCircle` | not called |  |  |  |   |
| `Int_DrawEllipse` | not called |  |  |  |   |
| `Int_DrawLine` | not called |  |  |  |   |
| `Int_DrawMarker` | not called |  |  |  |   |
| `Int_DrawPoly` | not called |  |  |  |   |
| `Int_DrawRectangle` | not called |  |  |  |   |
| `Int_MeasureHorizLineWithCenter` | not called |  |  |  |   |
| `Int_GetKeyString` | not called |  |  |  |   |
| `Int_GetKeyValue` | not called |  |  |  |   |
| `Int_SetKeyString` | not called |  |  |  |   |
| `Int_SetKeyValue` | not called |  |  |  |   |
| `Int_ExecProgram` | not called |  |  |  |   |
| `Int_ExecProgramWait` | not called |  |  |  |   |
| `Int_ExecuteCommand` | not called |  |  |  |   |
| `Int_ExecuteMacro` | not called |  |  |  |   |
| `Int_FindDifferentApp` | not called |  |  |  |   |
| `Int_ListAddButton` | not called |  |  |  |   |
| `Int_ListAddString` | not called |  |  |  |   |
| `Int_ListClose` | not called |  |  |  |   |
| `Int_ListCreateWindow` | not called |  |  |  |   |
| `Int_ListDefineFixed` | not called |  |  |  |   |
| `Int_ListDeleteString` | not called |  |  |  |   |
| `Int_ListGetData` | not called |  |  |  |   |
| `Int_ListInsertString` | not called |  |  |  |   |
| `Int_ListOutput` | not called |  |  |  |   |
| `Int_ListReset` | not called |  |  |  |   |
| `Int_ListSetHeader` | not called |  |  |  |   |
| `Int_ListShow` | not called |  |  |  |   |
| `SortArrayDbl` | not called |  |  |  |   |
| `SortArrayInt` | not called |  |  |  |   |
| `abs` | not called |  |  |  |   |
| `acos` | not called |  |  |  |   |
| `asin` | not called |  |  |  |   |
| `atan` | not called |  |  |  |   |
| `atof` | not called |  |  |  |   |
| `atoi` | not called |  |  |  |   |
| `cos` | not called |  |  |  |   |
| `fabs` | not called |  |  |  |   |
| `hypot` | not called |  |  |  |   |
| `log` | not called |  |  |  |   |
| `max` | not called |  |  |  |   |
| `min` | not called |  |  |  |   |
| `pow` | not called |  |  |  |   |
| `random` | not called |  |  |  |   |
| `rng` | not called |  |  |  |   |
| `round` | not called |  |  |  |   |
| `sgn` | not called |  |  |  |   |
| `sin` | not called |  |  |  |   |
| `sqrt` | not called |  |  |  |   |
| `tan` | not called |  |  |  |   |
| `UpdateMeanAndVariance` | not called |  |  |  |   |
| `memcmp` | not called |  |  |  |   |
| `memcpy` | not called |  |  |  |   |
| `memset` | not called |  |  |  |   |
| `Int_AppendMenu` | not called |  |  |  |   |
| `Int_AppendMenuEx` | not called |  |  |  |   |
| `Int_AssignKey` | not called |  |  |  |   |
| `Int_DeleteMenu` | not called |  |  |  |   |
| `Int_DeleteMenuEx` | not called |  |  |  |   |
| `Int_DeleteMenuGroupEx` | not called |  |  |  |   |
| `Int_HideLuciaMenu` | not called |  |  |  |   |
| `Int_InsertMenu` | not called |  |  |  |   |
| `Int_SetMenuAccel` | not called |  |  |  |   |
| `Int_SetMenuAccelEx` | not called |  |  |  |   |
| `Int_SetMenuState` | not called |  |  |  |   |
| `Int_SetMenuStateEx` | not called |  |  |  |   |
| `Int_SetMenuStringEx` | not called |  |  |  |   |
| `Int_ShowLuciaMenu` | not called |  |  |  |   |
| `Int_ShowUserMenuEx` | not called |  |  |  |   |
| `RestoreLuciaMenu` | not called |  |  |  |   |
| `Int_GetEvents` | not called |  |  |  |   |
| `Int_GetMouseClickSubPixelPos` | not called |  |  |  |   |
| `Int_GetMousePos` | not called |  |  |  |   |
| `Int_PostMessage` | not called |  |  |  |   |
| `Int_PostMouseMessage` | not called |  |  |  |   |
| `Int_RegisterWindowForKeyDown` | not called |  |  |  |   |
| `Int_WaitForEvent` | not called |  |  |  |   |
| `Int_WaitForMouseEvent` | not called |  |  |  |   |
| `MAKELPARAM` | not called |  |  |  |   |
| `Heart_Analyze_New` | not called |  |  |  |   |
| `Int_ConvertData` | not called |  |  |  |   |
| `Int_GetAppSystemColor` | not called |  |  |  |   |
| `Int_RescaleHist` | not called |  |  |  |   |
| `Int_SetFocus` | not called |  |  |  |   |
| `IsClipboardOK` | ran | 0 |  |  |   |
| `Region_Set_Rotation` | not called |  |  |  |   |
| `Sql_Connect` | not called |  |  |  |   |
| `Sql_Disconnect` | not called |  |  |  |   |
| `Sql_DisconnectAll` | not called |  |  |  |   |
| `Sql_Query` | not called |  |  |  |   |
| `_SelectColor` | not called |  |  |  |   |
| `GetOCRImageText` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetOCRInfo` | needs arguments | error: Bad number of parameters |  |  |   |
| `PathExtension` | not called |  |  |  |   |
| `PathFilename` | not called |  |  |  |   |
| `PathModifyStem` | not called |  |  |  |   |
| `PathParentPath` | not called |  |  |  |   |
| `PathReplaceExtension` | not called |  |  |  |   |
| `PathReplaceFilename` | not called |  |  |  |   |
| `PathStem` | not called |  |  |  |   |
| `RTF_CreateReport` | not called |  |  |  |   |
| `RTF_FindQuestion` | not called |  |  |  |   |
| `RTF_OpenFile` | not called |  |  |  |   |
| `RTF_ReplaceAllLuciaFeatures` | not called |  |  |  |   |
| `RTF_ReplaceLuciaFeature` | not called |  |  |  |   |
| `RTF_ReplacePicture` | not called |  |  |  |   |
| `RTF_ReplaceQuestion` | not called |  |  |  |   |
| `RTF_ReplaceVariables` | not called |  |  |  |   |
| `Get_BValue` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_BinaryValue` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_GValue` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_Histogram` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_PixelValue` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_Profile` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_RValue` | needs arguments | error: Bad number of parameters |  |  |   |
| `Int_AnalyzeFunction` | not called |  |  |  |   |
| `RGB` | not called |  |  |  |   |
| `WavelengthToColor` | not called |  |  |  |   |
| `MultiByteToWideChar` | not called |  |  |  |   |
| `StrExchangeChar` | not called |  |  |  |   |
| `WideCharToMultiByte` | not called |  |  |  |   |
| `sprintf` | not called |  |  |  |   |
| `sprintf_l` | not called |  |  |  |   |
| `strcat` | not called |  |  |  |   |
| `strchr` | not called |  |  |  |   |
| `strcmp` | not called |  |  |  |   |
| `strcmpi` | not called |  |  |  |   |
| `strcpy` | not called |  |  |  |   |
| `stristr` | not called |  |  |  |   |
| `strlen` | not called |  |  |  |   |
| `strlwr` | not called |  |  |  |   |
| `strrchr` | not called |  |  |  |   |
| `strstr` | not called |  |  |  |   |
| `strupr` | not called |  |  |  |   |
| `Int_CloseTextWindow` | not called |  |  |  |   |
| `Int_CreateTextWindow` | not called |  |  |  |   |
| `Int_CreateWindow` | not called |  |  |  |   |
| `Int_OutputWindow` | not called |  |  |  |   |
| `Int_SetWindowState` | not called |  |  |  |   |
| `Int_SetWindowText` | not called |  |  |  |   |

## Analysis

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `_AssayConfiguration` | not called |  |  |  |   |
| `_AssayDefinition` | not called |  |  |  |   |
| `_AssayUserManagement` | not called |  |  |  |   |
| `_DefaultAssayDefinition` | not called |  |  |  |   |
| `_ServiceSettings` | not called |  |  |  |   |
| `_ServiceSettingsLite` | not called |  |  |  |   |
| `PixelClassifierAddClasses` | not called |  |  |  |   |
| `PixelClassifierDefineBayes` | not called |  |  |  |   |
| `PixelClassifierDefineManual` | not called |  |  |  |   |
| `PixelClassifierDefineNeural` | not called |  |  |  |   |
| `PixelClassifierDefinitionClose` | not called |  |  |  |   |
| `PixelClassifierDefinitionReset` | not called |  |  |  |   |
| `PixelClassifierDeselectInputChannel` | not called |  |  |  |   |
| `PixelClassifierExportToExcel` | not called |  |  |  |   |
| `PixelClassifierGetClassCount` | not called |  |  |  |   |
| `PixelClassifierGetMeasuredArea` | not called |  |  |  |   |
| `PixelClassifierInROI` | not called |  |  |  |   |
| `PixelClassifierLoadSettings` | not called |  |  |  |   |
| `PixelClassifierND` | not called |  |  |  |   |
| `PixelClassifierRefresh` | not called |  |  |  |   |
| `PixelClassifierRemoveAllData` | not called |  |  |  |   |
| `PixelClassifierRemoveClasses` | not called |  |  |  |   |
| `PixelClassifierRemoveData` | not called |  |  |  |   |
| `PixelClassifierSaveSettings` | not called |  |  |  |   |
| `PixelClassifierSelectInputChannel` | not called |  |  |  |   |
| `PixelClassifierSelectInputData` | not called |  |  |  |   |
| `PixelClassifierSetClassCount` | not called |  |  |  |   |
| `PixelClassifierSetSmooth` | not called |  |  |  |   |
| `PixelClassifierShowAreaFract` | not called |  |  |  |   |
| `PixelClassifierStore` | not called |  |  |  |   |
| `_PixelClassifierLoadSettings` | not called |  |  |  |   |
| `_PixelClassifierND` | not called |  |  |  |   |
| `_PixelClassifierSaveSettings` | not called |  |  |  |   |
| `ColocalizationLoadSettings` | not called |  |  |  |   |
| `ColocalizationSaveSettings` | not called |  |  |  |   |
| `_ColocalizationLoadSettings` | not called |  |  |  |   |
| `_ColocalizationSaveSettings` | not called |  |  |  |   |
| `GPA_OpenResults` | not called |  |  |  |   |
| `_GPA_Remeasure` | not called |  |  |  |   |
| `_GPA_Run` | not called |  |  |  |   |
| `_GPA_RunAsAdministrator` | not called |  |  |  |   |
| `_GPA_Definition` | not called |  |  |  |   |
| `_GPA_DefinitionsUpdate` | not called |  |  |  |   |
| `ObjectClassifierExportToClipboard` | not called |  |  |  |   |
| `ObjectClassifierExportToExcel` | not called |  |  |  |   |
| `ObjectClassifierExportToFile` | not called |  |  |  |   |
| `ObjectClassifierLoadSettings` | not called |  |  |  |   |
| `ObjectClassifierSaveSettings` | not called |  |  |  |   |
| `_ObjectClassifierExportToFile` | not called |  |  |  |   |
| `_ObjectClassifierLoadSettings` | not called |  |  |  |   |
| `_ObjectClassifierSaveSettings` | not called |  |  |  |   |
| `ObjectCountAutoUpdate` | not called |  |  |  |   |
| `ObjectCountExportDetailedToExcel` | not called |  |  |  |   |
| `ObjectCountExportDetailedToFile` | not called |  |  |  |   |
| `ObjectCountExportRawToExcel` | not called |  |  |  |   |
| `ObjectCountExportRawToFile` | not called |  |  |  |   |
| `ObjectCountGenerateBinary` | not called |  |  |  |   |
| `ObjectCountGenerateBinaryND` | not called |  |  |  |   |
| `ObjectCountGetCount` | not called |  |  |  |   |
| `ObjectCountGetObjectFeature` | not called |  |  |  |   |
| `ObjectCountLoadSettings` | not called |  |  |  |   |
| `ObjectCountRestrObjAt` | not called |  |  |  |   |
| `ObjectCountRestrObjSel` | not called |  |  |  |   |
| `ObjectCountRestrReset` | not called |  |  |  |   |
| `ObjectCountRestrSet` | not called |  |  |  |   |
| `ObjectCountSaveSettings` | not called |  |  |  |   |
| `ObjectCountUpdate` | not called |  |  |  |   |
| `_ObjectCountLoadSettings` | not called |  |  |  |   |
| `_ObjectCountSaveSettings` | not called |  |  |  |   |
| `Profile_Data_ExportClipboard` | not called |  |  |  |   |
| `Profile_Data_ExportExcel` | not called |  |  |  |   |
| `Profile_Data_Recalculate` | not called |  |  |  |   |
| `Profile_DefineCross` | not called |  |  |  |   |
| `Profile_DefineLine` | not called |  |  |  |   |
| `Profile_DefinePolyLine` | not called |  |  |  |   |
| `Profile_ExportAll` | not called |  |  |  |   |
| `Profile_Graph_ExportClipboard` | not called |  |  |  |   |
| `Profile_Graph_Redraw` | not called |  |  |  |   |
| `Profile_Options` | not called |  |  |  |   |
| `Profile_SetAutoScale` | not called |  |  |  |   |
| `Profile_SetNumProfiles` | not called |  |  |  |   |
| `Profile_SetView` | not called |  |  |  |   |
| `Profile_ShowGrid` | not called |  |  |  |   |
| `_Profile_Data_ExportFile` | not called |  |  |  |   |
| `_Profile_Graph_ExportFile` | not called |  |  |  |   |
| `_Profile_Options` | not called |  |  |  |   |
| `TMeas_Data_Clipboard` | not called |  |  |  |   |
| `TMeas_Data_ExportExcel` | not called |  |  |  |   |
| `TMeas_Data_ExportFile` | not called |  |  |  |   |
| `TMeas_Data_GetNumDecimals` | not called |  |  |  |   |
| `TMeas_Data_Reset` | not called |  |  |  |   |
| `TMeas_Data_SetNumDecimals` | not called |  |  |  |   |
| `TMeas_GetFeaturesList` | not called |  |  |  |   |
| `TMeas_GetFeaturesNumber` | not called |  |  |  |   |
| `TMeas_Graph_Clipboard` | not called |  |  |  |   |
| `TMeas_Graph_DefineTimeWnd` | not called |  |  |  |   |
| `TMeas_Graph_ExportFile` | not called |  |  |  |   |
| `TMeas_Graph_FindValueX` | not called |  |  |  |   |
| `TMeas_Graph_GetBackColor` | not called |  |  |  |   |
| `TMeas_Graph_GetLineThick` | not called |  |  |  |   |
| `TMeas_Graph_GetVerticalAxisScale` | not called |  |  |  |   |
| `TMeas_Graph_InsertDistanceX` | not called |  |  |  |   |
| `TMeas_Graph_SetBackColor` | not called |  |  |  |   |
| `TMeas_Graph_SetLineThick` | not called |  |  |  |   |
| `TMeas_Graph_SetVerticalAxisScale` | not called |  |  |  |   |
| `TMeas_Graph_Set_Settings` | not called |  |  |  |   |
| `TMeas_Graph_Set_XAxis_Settings` | not called |  |  |  |   |
| `TMeas_Graph_Set_YAxis_Settings` | not called |  |  |  |   |
| `TMeas_Graph_ShowGrid` | not called |  |  |  |   |
| `TMeas_Meas_Clear` | not called |  |  |  |   |
| `TMeas_Meas_Insert` | not called |  |  |  |   |
| `TMeas_Meas_ResetData` | not called |  |  |  |   |
| `TMeas_MeasureWholeND` | not called |  |  |  |   |
| `TMeas_Probe_DuplicateProbe` | not called |  |  |  |   |
| `TMeas_Probe_EnableProbe` | not called |  |  |  |   |
| `TMeas_Probe_HighlightProbe` | not called |  |  |  |   |
| `TMeas_Probe_RemoveProbe` | not called |  |  |  |   |
| `TMeas_Probes_Copy` | not called |  |  |  |   |
| `TMeas_Probes_GetNumProbes` | not called |  |  |  |   |
| `TMeas_Probes_Paste` | not called |  |  |  |   |
| `TMeas_Probes_RemoveAllProbes` | not called |  |  |  |   |
| `TMeas_SetFeatureLeft` | not called |  |  |  |   |
| `TMeas_SetFeatureRight` | not called |  |  |  |   |
| `TMeas_SetROIDyesMode` | not called |  |  |  |   |
| `TMeas_ShowControl` | not called |  |  |  |   |
| `TMeas_Start` | not called |  |  |  |   |
| `TMeas_Stop` | not called |  |  |  |   |
| `TMeas_Timing_GetType` | not called |  |  |  |   |
| `TMeas_Timing_SetEveryFrame` | not called |  |  |  |   |
| `TMeas_Timing_SetInterval` | not called |  |  |  |   |
| `TMeas_Timing_SetType` | not called |  |  |  |   |
| `_TMeas_Data_ExportFile` | not called |  |  |  |   |
| `_TMeas_DefineProbes` | not called |  |  |  |   |
| `_TMeas_DefineRatio` | not called |  |  |  |   |
| `_TMeas_Graph_ExportFile` | not called |  |  |  |   |
| `_TMeas_Graph_PickValueFromProbe` | not called |  |  |  |   |
| `_TMeas_Meas_Measure` | not called |  |  |  |   |
| `_TMeas_Options` | not called |  |  |  |   |
| `_TMeas_Probes_FromFile` | not called |  |  |  |   |
| `_TMeas_Probes_ToFile` | not called |  |  |  |   |
| `_TMeas_ShowEventsSetup` | not called |  |  |  |   |
| `AddMovingROIs` | not called |  |  |  |   |
| `BinaryFromMask` | not called |  |  |  |   |
| `BinaryFromMaskND` | not called |  |  |  |   |
| `BinarySwapMask` | not called |  |  |  |   |
| `BinaryToMask` | not called |  |  |  |   |
| `BinaryToMaskMP` | not called |  |  |  |   |
| `ChangeROIType` | not called |  |  |  |   |
| `ClearMeasROI` | not called |  |  |  |   |
| `ColorizeAllROIObjects` | not called |  |  |  |   |
| `CombineROI` | not called |  |  |  |   |
| `CopyAllROIs` | not called |  |  |  |   |
| `CopyROI` | not called |  |  |  |   |
| `CopyROIToBinaryEx` | not called |  |  |  |   |
| `CopySelectedTracksToNewBinLayer` | not called |  |  |  |   |
| `CopyUntrackedObjectsToNewBinaryLayer` | not called |  |  |  |   |
| `CreateBezierROI` | not called |  |  |  |   |
| `CreateDocumentFromROI` | not called |  |  |  |   |
| `CreateDocumentFromSelectedROIs` | not called |  |  |  |   |
| `CreateEllipseROI` | not called |  |  |  |   |
| `CreateLineROI` | not called |  |  |  |   |
| `CreatePolygonROI` | not called |  |  |  |   |
| `CreateRectangleROI` | not called |  |  |  |   |
| `DeleteROI` | not called |  |  |  |   |
| `DuplicateROI` | not called |  |  |  |   |
| `ExportTrackedROIsToXML` | not called |  |  |  |   |
| `GetROICount` | ran | None |  |  |   |
| `GetROIIdFromIndex` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetROIIndexFromID` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetROIInfo` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetROIPos` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetSelectedROIs` | needs arguments | error: Bad number of parameters |  |  |   |
| `InflateROI` | not called |  |  |  |   |
| `IntersectBinaryWithMask` | not called |  |  |  |   |
| `IntersectBinaryWithMaskND` | not called |  |  |  |   |
| `InvertROI` | not called |  |  |  |   |
| `InvertROIAdd` | not called |  |  |  |   |
| `KeepROIsWithIntensity` | not called |  |  |  |   |
| `LoadROI` | not called |  |  |  |   |
| `LockROI` | not called |  |  |  |   |
| `MaskEdit` | not called |  |  |  |   |
| `MaskOn` | not called |  |  |  |   |
| `MeasROIProperties` | not called |  |  |  |   |
| `MoveBinaryFromMask` | not called |  |  |  |   |
| `MoveBinaryFromMaskND` | not called |  |  |  |   |
| `MoveBinaryToMask` | not called |  |  |  |   |
| `MoveBinaryToMaskMP` | not called |  |  |  |   |
| `MoveTrackedBinaryToMask` | not called |  |  |  |   |
| `MoveSelectedTracksToNewBinLayer` | not called |  |  |  |   |
| `MoveUntrackedObjectsToNewBinaryLayer` | not called |  |  |  |   |
| `PasteROI` | not called |  |  |  |   |
| `ProfileFromROI` | not called |  |  |  |   |
| `ROIFromInvertedGraticule` | not called |  |  |  |   |
| `ROIShowAllTracks` | not called |  |  |  |   |
| `ROIShowLabels` | not called |  |  |  |   |
| `ROIShowStimulationButtons` | not called |  |  |  |   |
| `ROIStatisticsExportRawToExcel` | not called |  |  |  |   |
| `ROIStatisticsExportRawToFile` | not called |  |  |  |   |
| `ROIStatisticsGetData` | not called |  |  |  |   |
| `RemoveAllTouchingROIs` | not called |  |  |  |   |
| `RemoveTouchingROIs` | not called |  |  |  |   |
| `RenumberAllROIObjects` | not called |  |  |  |   |
| `SaveROIAs` | not called |  |  |  |   |
| `SelectAllROIs` | not called |  |  |  |   |
| `SelectROI` | not called |  |  |  |   |
| `SetROIColor` | not called |  |  |  |   |
| `SetROIPos` | not called |  |  |  |   |
| `SetRoiVisibility` | not called |  |  |  |   |
| `ShowMeasROI` | not called |  |  |  |   |
| `ToggleDecInfo` | not called |  |  |  |   |
| `ToggleMeasROI` | not called |  |  |  |   |
| `ToggleRoi_MolecularCentroid` | not called |  |  |  |   |
| `ToggleSnapToMolecules` | not called |  |  |  |   |
| `TrackedBinaryToMask` | not called |  |  |  |   |
| `TrackingBinaryByID` | not called |  |  |  |   |
| `_BinaryFromMaskND` | not called |  |  |  |   |
| `_BinaryToMask` | not called |  |  |  |   |
| `_DrawAutoDetectROI` | not called |  |  |  |   |
| `_DrawSimpleROI` | not called |  |  |  |   |
| `_IntersectBinaryWithMask` | not called |  |  |  |   |
| `_LoadROI` | not called |  |  |  |   |
| `_MeasROIProperties` | not called |  |  |  |   |
| `_MoveBinaryFromMaskND` | not called |  |  |  |   |
| `_MoveBinaryToMask` | not called |  |  |  |   |
| `_SaveROIAs` | not called |  |  |  |   |
| `_SimpleROIEditor` | not called |  |  |  |   |
| `_TrackingROIEditor` | not called |  |  |  |   |
| `SelectAllVectorsAndROIs` | not called |  |  |  |   |

## Applications

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `HDR_CaptureHDRImage` | not called |  |  |  |   |
| `HDR_CreateHDRFromND` | not called |  |  |  |   |
| `HDR_CreateHDRImage` | not called |  |  |  |   |
| `HDR_CreateRFImage` | not called |  |  |  |   |
| `AboutFilters` | not called |  |  |  |   |
| `FiltersDefaultLayout` | not called |  |  |  |   |
| `FiltersGetData` | not called |  |  |  |   |
| `FiltersGetDataRecordsCount` | not called |  |  |  |   |
| `FiltersGetStat` | not called |  |  |  |   |
| `FiltersSaveLargestParticleImages` | not called |  |  |  |   |
| `FiltersSaveLargestParticleImagesEx` | not called |  |  |  |   |
| `FinishFilters` | not called |  |  |  |   |
| `GetCurrentFilterMeasurementDate` | not reachable | AttributeError: 'Macro' object has no attribute 'GetCurrentFilterMeasurementDate' |  |  |   |
| `HelpOnFilters` | not called |  |  |  |   |
| `InitFilters` | not called |  |  |  |   |
| `ObjectiveInfo` | not called |  |  |  |   |
| `StartFilters` | not called |  |  |  |   |
| `_ExportFilterFile` | not called |  |  |  |   |
| `GA_Connect` | not called |  |  |  |   |
| `GA_ShowAcquistion` | not called |  |  |  |   |
| `GA_ShowControlBar` | not called |  |  |  |   |
| `HD_CloseReport` | not called |  |  |  |   |
| `HD_DisplayCrossHair` | not called |  |  |  |   |
| `HD_DisplayData` | not called |  |  |  |   |
| `HD_DisplayGraph` | not called |  |  |  |   |
| `HD_EmptyData` | not called |  |  |  |   |
| `HD_IsDataWindow` | not called |  |  |  |   |
| `HD_IsGraphWindow` | not called |  |  |  |   |
| `_HD_DefineOrigin` | not called |  |  |  |   |
| `_HD_MarkIndentorPos` | not called |  |  |  |   |
| `_HD_MeasMethod` | not called |  |  |  |   |
| `_HD_Measure` | not called |  |  |  |   |
| `_HD_NewSample` | not called |  |  |  |   |
| `_HD_NewTest` | not called |  |  |  |   |
| `_HD_Setup` | not called |  |  |  |   |
| `_HD_ShowReport` | not called |  |  |  |   |
| `_HD_SurfaceTreatment` | not called |  |  |  |   |
| `AlignCurrentNDDocument` | not called |  |  |  |   |
| `AlignCurrentNDDocumentRect` | not called |  |  |  |   |
| `GPU_HDR_CreateHDRImage` | not called |  |  |  |   |
| `GPU_EDF_CreateEDFImage` | not called |  |  |  |   |
| `CreateWidefieldFromSIM` | not called |  |  |  |   |
| `_CreateWidefieldFromSIM` | not called |  |  |  |   |
| `Denoise3DCurrentNDDocument` | not called |  |  |  |   |
| `ND_StitchMultipoint` | not called |  |  |  |   |
| `ND_StitchMultipointFile` | not called |  |  |  |   |
| `ND_StitchMultipointFileEx` | not called |  |  |  |   |
| `ND_StitchMultipointGa3` | not called |  |  |  |   |
| `STORMVV_ImportMoleculeList` | not called |  |  |  |   |
| `SelectBestFocusedFromND` | not called |  |  |  |   |
| `ShowFocusedGraphFromND` | not called |  |  |  |   |
| `_GPU_EDF_CreateEDFImage` | not called |  |  |  |   |
| `_GPU_HDR_CreateHDRImage` | not called |  |  |  |   |
| `_HDR_CaptureHDRImage` | not called |  |  |  |   |
| `_HDR_CreateHDRImage` | not called |  |  |  |   |
| `_ND_StitchMultipoint` | not called |  |  |  |   |
| `_ND_StitchMultipointFile` | not called |  |  |  |   |
| `_SelectBestFocusedFromND` | not called |  |  |  |   |
| `_SelectFocusedCriterion` | not called |  |  |  |   |
| `_ND_StitchMultipointGa3` | not called |  |  |  |   |
| `_ND_StitchMultipointAutoSelect` | not called |  |  |  |   |
| `_MeasureWeld` | not called |  |  |  |   |
| `_MeasureWeldHistory` | not called |  |  |  |   |
| `_WeldCustomParams` | not called |  |  |  |   |
| `_WeldingSettings` | not called |  |  |  |   |
| `DeleteMolecules` | not called |  |  |  |   |
| `LoadMolecules` | not called |  |  |  |   |
| `MoleculesSnapshot` | not called |  |  |  |   |
| `NSTORMRender` | not called |  |  |  |   |
| `NSTORMRenderVolume` | not called |  |  |  |   |
| `NSTORMSetLightPath` | not called |  |  |  |   |
| `NSTORMSetMultilaser` | not called |  |  |  |   |
| `SaveMolecules` | not called |  |  |  |   |
| `ShowMoleculeColorScale` | not called |  |  |  |   |
| `_LoadMolecules` | not called |  |  |  |   |
| `_MoleculesToRaster` | not called |  |  |  |   |
| `_NSTORMAcquisition` | not called |  |  |  |   |
| `_NSTORMAnalysisNew` | not called |  |  |  |   |
| `_NSTORMLayersAutocorrelate` | not called |  |  |  |   |
| `_NSTORMRender` | not called |  |  |  |   |
| `_NSTORMRenderVolume` | not called |  |  |  |   |
| `_Deconv_MAPAutomatic` | not called |  |  |  |   |
| `_Deconv_ExtractPSF` | not called |  |  |  |   |
| `_ReconstructVC` | not called |  |  |  |   |
| `ImmunoHistoChemistryND` | not called |  |  |  |   |
| `fnInit_BatchGA3_DLL` | not called |  |  |  |   |
| `fnPush_BatchGA3_Data` | not called |  |  |  |   |
| `fnGet_BatchGA3_NextRecipeAndFile` | not called |  |  |  |   |
| `JSEval` | not called |  |  |  |   |
| `JSEvalToDouble` | not called |  |  |  |   |
| `JSEvalToInt` | not called |  |  |  |   |
| `JSEvalToString` | not called |  |  |  |   |
| `LimSim_CreateOTF` | not called |  |  |  |   |
| `LimSim_PreviewHide` | not called |  |  |  |   |
| `LimSim_PreviewSetParams` | not called |  |  |  |   |
| `LimSim_PreviewShow` | not called |  |  |  |   |
| `LimSim_Reconstruct` | not called |  |  |  |   |
| `LimSim_SIM` | not called |  |  |  |   |
| `LimSim_SIM_UserDlg` | not called |  |  |  |   |
| `_HCA_CreateJobFixed` | not called |  |  |  |   |
| `_HCA_CreateJobLive` | not called |  |  |  |   |
| `_HCA_DuplicateJob` | not called |  |  |  |   |
| `_HCA_ViewJobDefinition` | not called |  |  |  |   |
| `NkComPort_Open` | not called |  |  |  |   |
| `NkComPort_IsConnected` | not called |  |  |  |   |
| `NkComPort_GetConnectionDetails` | not called |  |  |  |   |
| `NkComPort_Close` | not called |  |  |  |   |
| `NkComPort_Read` | not called |  |  |  |   |
| `NkComPort_ReadLine` | not called |  |  |  |   |
| `NkComPort_Write` | not called |  |  |  |   |
| `NkComPort_WriteLine` | not called |  |  |  |   |
| `NkComPort_ListPorts` | not called |  |  |  |   |
| `NkComPort_SelectPortDialog` | not called |  |  |  |   |
| `NkSocket_Listen` | not called |  |  |  |   |
| `NkSocket_IsListening` | not called |  |  |  |   |
| `NkSocket_Connect` | not called |  |  |  |   |
| `NkSocket_IsConnected` | not called |  |  |  |   |
| `NkSocket_Close` | not called |  |  |  |   |
| `NkSocket_Write` | not called |  |  |  |   |
| `NkSocket_Read` | not called |  |  |  |   |
| `NkSocket_WriteLine` | not called |  |  |  |   |
| `NkSocket_ReadLine` | not called |  |  |  |   |
| `NkSocket_WriteLineA` | not called |  |  |  |   |
| `NkSocket_ReadLineA` | not called |  |  |  |   |
| `NkSocket_IsValid` | not called |  |  |  |   |
| `NkSocket_GetErrorDescription` | not called |  |  |  |   |
| `strncmp` | not called |  |  |  |   |
| `strncopy` | not called |  |  |  |   |
| `strtok` | not called |  |  |  |   |
| `strcspn` | not called |  |  |  |   |
| `strpbrk` | not called |  |  |  |   |
| `strsplit` | not called |  |  |  |   |
| `RegexFree` | not called |  |  |  |   |
| `RegexGetErrorDescription` | not called |  |  |  |   |
| `RegexMatches` | not called |  |  |  |   |
| `RegexSearch` | not called |  |  |  |   |
| `RegexGetMatchCount` | not called |  |  |  |   |
| `RegexGetMatch` | not called |  |  |  |   |
| `StrMapCreate` | not called |  |  |  |   |
| `StrMapFree` | not called |  |  |  |   |
| `StrMapSet` | not called |  |  |  |   |
| `StrMapUnset` | not called |  |  |  |   |
| `StrMapFind` | not called |  |  |  |   |
| `StrMapGet` | not called |  |  |  |   |
| `StrMapParseOptions` | not called |  |  |  |   |
| `NkWindow_GetMainWindow` | not called |  |  |  |   |
| `NkWindow_GetMainWindowNext` | not called |  |  |  |   |
| `NkWindow_FindWindow` | not called |  |  |  |   |
| `NkWindow_FindWindowDeep` | not called |  |  |  |   |
| `NkWindow_FindWindowByText` | not called |  |  |  |   |
| `NkWindow_GetWindow` | not called |  |  |  |   |
| `NkWindow_GetParent` | not called |  |  |  |   |
| `NkWindow_GetWindowLong` | not called |  |  |  |   |
| `NkWindow_SetWindowLong` | not called |  |  |  |   |
| `NkWindow_DestroyWindow` | not called |  |  |  |   |
| `NkWindow_ShowWindow` | not called |  |  |  |   |
| `NkWindow_SendMessage` | not called |  |  |  |   |
| `NkWindow_SendMessageString` | not called |  |  |  |   |
| `NkWindow_SendMessagePointer` | not called |  |  |  |   |
| `NkWindow_PostMessage` | not called |  |  |  |   |
| `NkWindow_GetWindowRect` | not called |  |  |  |   |
| `NkWindow_SetWindowRect` | not called |  |  |  |   |
| `NkWindow_SetWindowPos` | not called |  |  |  |   |
| `NkWindow_GetWindowPos` | not called |  |  |  |   |
| `NkWindow_GetWindowSize` | not called |  |  |  |   |
| `NkWindow_SetWindowSize` | not called |  |  |  |   |
| `NkWindow_SetForeground` | not called |  |  |  |   |
| `NkWindow_SendMouseInput` | not called |  |  |  |   |
| `NkWindow_SendKeyboardInput` | not called |  |  |  |   |
| `NkDialog_Create` | not called |  |  |  |   |
| `NkDialog_AddRemoveOptions` | not called |  |  |  |   |
| `NkDialog_AddRow` | not called |  |  |  |   |
| `NkDialog_AddColumn` | not called |  |  |  |   |
| `NkDialog_AddControl` | not called |  |  |  |   |
| `NkDialog_AddControlEx` | not called |  |  |  |   |
| `NkDialog_AddMacroMessageHandler` | not called |  |  |  |   |
| `NkDialog_FindControl` | not called |  |  |  |   |
| `NkDialog_SendMessage` | not called |  |  |  |   |
| `NkDialog_SendMessageString` | not called |  |  |  |   |
| `NkLsEdit_SetRange` | not called |  |  |  |   |
| `NkLsEdit_SetScale` | not called |  |  |  |   |
| `NkLsEdit_SetFormat` | not called |  |  |  |   |
| `NkLsEdit_SetUnit` | not called |  |  |  |   |
| `NkLsEdit_SetValue` | not called |  |  |  |   |
| `NkLsEdit_GetValue` | not called |  |  |  |   |
| `NkLsEdit_SetFlags` | not called |  |  |  |   |
| `NkLsEdit_GetFlags` | not called |  |  |  |   |
| `NkPMTGainEdit_IsNkPMTGainEditWindow` | not called |  |  |  |   |
| `NkPMTGainEdit_SetCalibration` | not called |  |  |  |   |
| `NkPMTGainEdit_AttachToHighVoltage` | not called |  |  |  |   |
| `NkProgressBar_SetCompletionText` | not called |  |  |  |   |
| `NkFile_Write` | not called |  |  |  |   |
| `NkFile_Append` | not called |  |  |  |   |
| `NkFile_FindFirstFile` | not called |  |  |  |   |
| `NkFile_FindNextFile` | not called |  |  |  |   |
| `NkFile_FindClose` | not called |  |  |  |   |
| `NkFile_GetOpenFileName` | not called |  |  |  |   |
| `NkFile_BrowseForFolder` | not called |  |  |  |   |

## Binary

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `ConvertTo4Connectivity` | not called |  |  |  |   |
| `ConvertTo4ConnectivityGa3` | not called |  |  |  |   |
| `ConvertTo4ConnectivityND` | not called |  |  |  |   |
| `ConvertTo8Connectivity` | not called |  |  |  |   |
| `ConvertTo8ConnectivityGa3` | not called |  |  |  |   |
| `ConvertTo8ConnectivityND` | not called |  |  |  |   |
| `ConvexHull` | not called |  |  |  |   |
| `ConvexHullGa3` | not called |  |  |  |   |
| `ConvexHullND` | not called |  |  |  |   |
| `CreateMaxIPBinary` | not called |  |  |  |   |
| `CreateMaxIPBinaryExt` | not called |  |  |  |   |
| `CreateMinIPBinary` | not called |  |  |  |   |
| `CreateMinIPBinaryExt` | not called |  |  |  |   |
| `DefineMatrix` | not called |  |  |  |   |
| `Expand` | not called |  |  |  |   |
| `ExpandND` | not called |  |  |  |   |
| `GranulometryFast` | not called |  |  |  |   |
| `GranulometryFastExt` | not called |  |  |  |   |
| `GranulometryFastGa3` | not called |  |  |  |   |
| `GranulometryFastND` | not called |  |  |  |   |
| `HitOrMiss` | not called |  |  |  |   |
| `HitOrMissND` | not called |  |  |  |   |
| `HomotopicMarking` | not called |  |  |  |   |
| `HomotopicMarkingGa3` | not called |  |  |  |   |
| `HomotopicMarkingND` | not called |  |  |  |   |
| `Medial_Axis` | not called |  |  |  |   |
| `Medial_AxisGa3` | not called |  |  |  |   |
| `Medial_AxisND` | not called |  |  |  |   |
| `MorphoSeparateObjects` | not called |  |  |  |   |
| `MorphoSeparateObjectsGa3` | not called |  |  |  |   |
| `MorphoSeparateObjectsEx` | not called |  |  |  |   |
| `MorphoSeparateObjectsExND` | not called |  |  |  |   |
| `MorphoSeparateObjectsND` | not called |  |  |  |   |
| `Pruning` | not called |  |  |  |   |
| `PruningGa3` | not called |  |  |  |   |
| `PruningND` | not called |  |  |  |   |
| `Quench` | not called |  |  |  |   |
| `QuenchEx` | not called |  |  |  |   |
| `QuenchExND` | not called |  |  |  |   |
| `QuenchND` | not called |  |  |  |   |
| `Skeletonize` | not called |  |  |  |   |
| `SkeletonizeGa3` | not called |  |  |  |   |
| `SkeletonizeND` | not called |  |  |  |   |
| `Thickening` | not called |  |  |  |   |
| `ThickeningND` | not called |  |  |  |   |
| `UltimateErosion` | not called |  |  |  |   |
| `UltimateErosionGa3` | not called |  |  |  |   |
| `UltimateErosionND` | not called |  |  |  |   |
| `ZonesOfInfluence` | not called |  |  |  |   |
| `ZonesOfInfluenceFast` | not called |  |  |  |   |
| `ZonesOfInfluenceFastND` | not called |  |  |  |   |
| `ZonesOfInfluenceGa3` | not called |  |  |  |   |
| `ZonesOfInfluenceFastGa3` | not called |  |  |  |   |
| `ZonesOfInfluenceND` | not called |  |  |  |   |
| `_ConvertTo4Connectivity` | not called |  |  |  |   |
| `_ConvertTo4ConnectivityGa3` | not called |  |  |  |   |
| `_ConvertTo8Connectivity` | not called |  |  |  |   |
| `_ConvertTo8ConnectivityGa3` | not called |  |  |  |   |
| `_ConvexHull` | not called |  |  |  |   |
| `_ConvexHullGa3` | not called |  |  |  |   |
| `_Expand` | not called |  |  |  |   |
| `_GranulometryFast` | not called |  |  |  |   |
| `_GranulometryFastGa3` | not called |  |  |  |   |
| `_HitOrMiss` | not called |  |  |  |   |
| `_HomotopicMarking` | not called |  |  |  |   |
| `_HomotopicMarkingGa3` | not called |  |  |  |   |
| `_Medial_Axis` | not called |  |  |  |   |
| `_Medial_AxisGa3` | not called |  |  |  |   |
| `_MorphoSeparateObjects` | not called |  |  |  |   |
| `_MorphoSeparateObjectsGa3` | not called |  |  |  |   |
| `_Pruning` | not called |  |  |  |   |
| `_PruningGa3` | not called |  |  |  |   |
| `_Quench` | not called |  |  |  |   |
| `_Skeletonize` | not called |  |  |  |   |
| `_SkeletonizeGa3` | not called |  |  |  |   |
| `_Thickening` | not called |  |  |  |   |
| `_UltimateErosion` | not called |  |  |  |   |
| `_UltimateErosionGa3` | not called |  |  |  |   |
| `_ZonesOfInfluence` | not called |  |  |  |   |
| `_ZonesOfInfluenceGa3` | not called |  |  |  |   |
| `_ZonesOfInfluenceFastGa3` | not called |  |  |  |   |
| `_ZonesOfInfluenceFast` | not called |  |  |  |   |
| `CleanBinary` | not called |  |  |  |   |
| `CleanBinaryND` | not called |  |  |  |   |
| `CloseHolesBinary` | not called |  |  |  |   |
| `CloseHolesBinaryND` | not called |  |  |  |   |
| `ConnectObjectsBinary` | not called |  |  |  |   |
| `ConnectObjectsBinaryGa3` | not called |  |  |  |   |
| `ConnectObjectsBinaryND` | not called |  |  |  |   |
| `CreateCentroidsBinary` | not called |  |  |  |   |
| `CreateCentroidsBinaryND` | not called |  |  |  |   |
| `SmoothBinary` | not called |  |  |  |   |
| `SmoothBinaryND` | not called |  |  |  |   |
| `_ConnectObjectsBinary` | not called |  |  |  |   |
| `_ConnectObjectsBinaryGa3` | not called |  |  |  |   |
| `_CreateCentroidsBinary` | not called |  |  |  |   |
| `_SmoothBinary` | not called |  |  |  |   |
| `_SmoothBinaryND` | not called |  |  |  |   |
| `BinaryEdit` | not called |  |  |  |   |
| `GraticuleClear` | not called |  |  |  |   |
| `GraticuleEdit` | not called |  |  |  |   |
| `GraticuleEditEx` | not called |  |  |  |   |
| `ImageEdit` | not called |  |  |  |   |
| `ImageEditEx` | not called |  |  |  |   |
| `SampleHolderEditor` | not called |  |  |  |   |
| `InsertCircle` | not called |  |  |  |   |
| `InsertCircleND` | not called |  |  |  |   |
| `InsertEllipse` | not called |  |  |  |   |
| `InsertEllipseND` | not called |  |  |  |   |
| `InsertLine` | not called |  |  |  |   |
| `InsertLineND` | not called |  |  |  |   |
| `InsertLines` | not called |  |  |  |   |
| `InsertLinesND` | not called |  |  |  |   |
| `InsertMarker` | not called |  |  |  |   |
| `InsertMarkerND` | not called |  |  |  |   |
| `InsertMarkers` | not called |  |  |  |   |
| `InsertMarkersND` | not called |  |  |  |   |
| `InsertPoly` | not called |  |  |  |   |
| `InsertRectangle` | not called |  |  |  |   |
| `InsertRectangleND` | not called |  |  |  |   |
| `_InsertLineCircle` | not called |  |  |  |   |
| `BinLayerClipboardCopy` | not called |  |  |  |   |
| `BinLayerClipboardPaste` | not called |  |  |  |   |
| `BinLayerCopy` | not called |  |  |  |   |
| `BinLayerDelete` | not called |  |  |  |   |
| `BinLayerDuplicate` | not called |  |  |  |   |
| `BinLayerFillFramesND` | not called |  |  |  |   |
| `BinLayerGetNameFromID` | not called |  |  |  |   |
| `BinLayerGetNameFromIndex` | not called |  |  |  |   |
| `BinLayerMerge` | not called |  |  |  |   |
| `BinLayerMergeND` | not called |  |  |  |   |
| `BinLayerSelect` | not called |  |  |  |   |
| `BinLayerSetColor` | not called |  |  |  |   |
| `BinLayerSetColorEx` | not called |  |  |  |   |
| `BinLayerSetComponent` | not called |  |  |  |   |
| `BinLayerStore` | not called |  |  |  |   |
| `BinLayerSynchronizeBinariesWithChannels` | not called |  |  |  |   |
| `GetGrayImageFromBinLayer` | needs arguments | error: Bad number of parameters |  |  |   |
| `ProcessBinLayer` | not called |  |  |  |   |
| `_BinLayerOperation` | not called |  |  |  |   |
| `_BinLayerSetColor` | not called |  |  |  |   |
| `LinCloseBinary` | not called |  |  |  |   |
| `LinCloseBinaryGa3` | not called |  |  |  |   |
| `LinCloseBinaryND` | not called |  |  |  |   |
| `LinDilateBinary` | not called |  |  |  |   |
| `LinDilateBinaryGa3` | not called |  |  |  |   |
| `LinDilateBinaryND` | not called |  |  |  |   |
| `LinErodeBinary` | not called |  |  |  |   |
| `LinErodeBinaryGa3` | not called |  |  |  |   |
| `LinErodeBinaryND` | not called |  |  |  |   |
| `LinOpenBinary` | not called |  |  |  |   |
| `LinOpenBinaryGa3` | not called |  |  |  |   |
| `LinOpenBinaryND` | not called |  |  |  |   |
| `_LinCloseBinary` | not called |  |  |  |   |
| `_LinCloseBinaryGa3` | not called |  |  |  |   |
| `_LinDilateBinary` | not called |  |  |  |   |
| `_LinDilateBinaryGa3` | not called |  |  |  |   |
| `_LinErodeBinary` | not called |  |  |  |   |
| `_LinErodeBinaryGa3` | not called |  |  |  |   |
| `_LinOpenBinary` | not called |  |  |  |   |
| `_LinOpenBinaryGa3` | not called |  |  |  |   |
| `SetEditInOverlay` | not called |  |  |  |   |
| `CleanBinaryGa3` | not called |  |  |  |   |
| `CloseBinary` | not called |  |  |  |   |
| `CloseBinaryGa3` | not called |  |  |  |   |
| `CloseBinaryND` | not called |  |  |  |   |
| `CloseHolesBinaryGa3` | not called |  |  |  |   |
| `ConnectEndings` | not called |  |  |  |   |
| `Contour` | not called |  |  |  |   |
| `ContourGa3` | not called |  |  |  |   |
| `ContourND` | not called |  |  |  |   |
| `CutBranches` | not called |  |  |  |   |
| `CutBranchesGa3` | not called |  |  |  |   |
| `DetectBranching` | not called |  |  |  |   |
| `DetectBranchingGa3` | not called |  |  |  |   |
| `DetectBranchingND` | not called |  |  |  |   |
| `DetectEnding` | not called |  |  |  |   |
| `DetectEndingGa3` | not called |  |  |  |   |
| `DetectEndingND` | not called |  |  |  |   |
| `DilateBinary` | not called |  |  |  |   |
| `DilateBinaryGa3` | not called |  |  |  |   |
| `DilateBinaryND` | not called |  |  |  |   |
| `ErodeBinary` | not called |  |  |  |   |
| `ErodeBinaryGa3` | not called |  |  |  |   |
| `ErodeBinaryND` | not called |  |  |  |   |
| `FillHoles` | not called |  |  |  |   |
| `FillHolesGa3` | not called |  |  |  |   |
| `FillHolesND` | not called |  |  |  |   |
| `OpenBinary` | not called |  |  |  |   |
| `OpenBinaryGa3` | not called |  |  |  |   |
| `OpenBinaryND` | not called |  |  |  |   |
| `VanishObjects` | not called |  |  |  |   |
| `_CleanBinaryGa3` | not called |  |  |  |   |
| `_CloseBinaryGa3` | not called |  |  |  |   |
| `_CloseHolesBinaryGa3` | not called |  |  |  |   |
| `_ConnectEndings` | not called |  |  |  |   |
| `_Contour` | not called |  |  |  |   |
| `_ContourGa3` | not called |  |  |  |   |
| `_CutBranches` | not called |  |  |  |   |
| `_CutBranchesGa3` | not called |  |  |  |   |
| `_DetectBranching` | not called |  |  |  |   |
| `_DetectBranchingGa3` | not called |  |  |  |   |
| `_DetectEnding` | not called |  |  |  |   |
| `_DetectEndingGa3` | not called |  |  |  |   |
| `_DilateBinaryGa3` | not called |  |  |  |   |
| `_ErodeBinaryGa3` | not called |  |  |  |   |
| `_FillHolesGa3` | not called |  |  |  |   |
| `_OpenBinaryGa3` | not called |  |  |  |   |
| `_VanishObjects` | not called |  |  |  |   |
| `BinaryFromReference` | not called |  |  |  |   |
| `BinaryFromReferenceND` | not called |  |  |  |   |
| `BinaryMore` | not called |  |  |  |   |
| `BinaryOperations` | not called |  |  |  |   |
| `BinaryOperationsND` | not called |  |  |  |   |
| `BinarySwapReference` | not called |  |  |  |   |
| `BinaryToReference` | not called |  |  |  |   |
| `_BinaryMore` | not called |  |  |  |   |
| `_BinaryOperations` | not called |  |  |  |   |
| `AutoSegmentation` | not called |  |  |  |   |
| `BinarySegmentationCall` | not called |  |  |  |   |
| `BinarySegmentationDefine` | not called |  |  |  |   |
| `ColocalizeND` | not called |  |  |  |   |
| `ColorizeBinaryObjects` | not called |  |  |  |   |
| `ComponentThreshold` | not called |  |  |  |   |
| `ComponentThresholdND` | not called |  |  |  |   |
| `DefineComponentThreshold` | not called |  |  |  |   |
| `DefineComponentThresholdMCh` | not called |  |  |  |   |
| `DefineThreshold` | not called |  |  |  |   |
| `DefineThresholdCalcComp` | not called |  |  |  |   |
| `DefineThresholdHsiGa3` | not called |  |  |  |   |
| `DefineThresholdIHS` | not called |  |  |  |   |
| `DefineThresholdIntensity` | not called |  |  |  |   |
| `DefineThresholdIntGa3` | not called |  |  |  |   |
| `DefineThresholdMCHChannel` | not called |  |  |  |   |
| `DefineThresholdMchGa3` | not called |  |  |  |   |
| `DefineThresholdMchOnChannelGa3` | not called |  |  |  |   |
| `DefineThresholdMCHOperation` | not called |  |  |  |   |
| `DefineThresholdMethod` | not called |  |  |  |   |
| `DefineThresholdProcessing` | not called |  |  |  |   |
| `DefineThresholdProcessingGa3` | not called |  |  |  |   |
| `DefineThresholdProcessingOnChannel` | not called |  |  |  |   |
| `DefineThresholdProcessingOnChannelGa3` | not called |  |  |  |   |
| `DefineThresholdRGB` | not called |  |  |  |   |
| `DefineThresholdRgbGa3` | not called |  |  |  |   |
| `DefineThresholdRestrictionCircularity` | not called |  |  |  |   |
| `DefineThresholdRestrictionCircularityGa3` | not called |  |  |  |   |
| `DefineThresholdRestrictionCircularityOnChannel` | not called |  |  |  |   |
| `DefineThresholdRestrictionCircularityOnChannelGa3` | not called |  |  |  |   |
| `DefineThresholdRestrictionSize` | not called |  |  |  |   |
| `DefineThresholdRestrictionSizeGa3` | not called |  |  |  |   |
| `DefineThresholdRestrictionSizeOnChannel` | not called |  |  |  |   |
| `DefineThresholdRestrictionSizeOnChannelGa3` | not called |  |  |  |   |
| `EnableDynamicThreshold` | not called |  |  |  |   |
| `GBasedSegmentation` | not called |  |  |  |   |
| `GetOtsuThreshold` | ran | -1 |  |  |   |
| `HomogeneousSegmentation` | not called |  |  |  |   |
| `LineDetection` | not called |  |  |  |   |
| `LoadThresholdGa3` | not called |  |  |  |   |
| `ObjectCountThresholdND` | not called |  |  |  |   |
| `ResetThresholdGa3` | not called |  |  |  |   |
| `ResetThresholdIHS` | not called |  |  |  |   |
| `SaveThresholdGa3` | not called |  |  |  |   |
| `SegmentTightBorders` | not called |  |  |  |   |
| `ShowBinaryObjectID` | not called |  |  |  |   |
| `SpotDetection3DLoadSettings` | not called |  |  |  |   |
| `SpotDetection3DSaveSettings` | not called |  |  |  |   |
| `SpotDetectionLoadSettings` | not called |  |  |  |   |
| `SpotDetectionSaveSettings` | not called |  |  |  |   |
| `SpotDetection` | not called |  |  |  |   |
| `Threshold` | not called |  |  |  |   |
| `Threshold3D` | not called |  |  |  |   |
| `ThresholdAndCopyOriginal` | not called |  |  |  |   |
| `ThresholdAndCopyOriginalND` | not called |  |  |  |   |
| `ThresholdAuto` | not called |  |  |  |   |
| `ThresholdCalcComp` | not called |  |  |  |   |
| `ThresholdCalcCompND` | not called |  |  |  |   |
| `ThresholdEdgesII` | not called |  |  |  |   |
| `ThresholdGa3` | not called |  |  |  |   |
| `ThresholdIHS` | not called |  |  |  |   |
| `ThresholdIHSND` | not called |  |  |  |   |
| `ThresholdLoadSettings` | not called |  |  |  |   |
| `ThresholdND` | not called |  |  |  |   |
| `ThresholdOnComponent` | not called |  |  |  |   |
| `ThresholdOnComponentND` | not called |  |  |  |   |
| `ThresholdOtsu` | not called |  |  |  |   |
| `ThresholdSaveSettings` | not called |  |  |  |   |
| `WoundSegmentation` | not called |  |  |  |   |
| `WoundSegmentation3D` | not called |  |  |  |   |
| `_ComponentThreshold` | not called |  |  |  |   |
| `_DeepTrain` | not called |  |  |  |   |
| `_DefineComponentThreshold` | not called |  |  |  |   |
| `_DefineGraticuleMask` | not called |  |  |  |   |
| `_DefineThreshold` | not called |  |  |  |   |
| `_DefineThreshold3D` | not called |  |  |  |   |
| `_DefineThresholdX` | not called |  |  |  |   |
| `_DefineThresholdAll` | not called |  |  |  |   |
| `_DefineThresholdCalcComp` | not called |  |  |  |   |
| `_DefineThresholdEdgesII` | not called |  |  |  |   |
| `_DefineThresholdGa3` | not called |  |  |  |   |
| `_DefineThresholdHsiGa3` | not called |  |  |  |   |
| `_DefineThresholdIHS` | not called |  |  |  |   |
| `_DefineThresholdIntGa3` | not called |  |  |  |   |
| `_DefineThresholdMchGa3` | not called |  |  |  |   |
| `_DefineThresholdRgbGa3` | not called |  |  |  |   |
| `_DetectAllBinary` | not called |  |  |  |   |
| `_DetectCirclesHough` | not called |  |  |  |   |
| `_DetectComponentBinary` | not called |  |  |  |   |
| `_DetectLines` | not called |  |  |  |   |
| `_DetectLinesHough` | not called |  |  |  |   |
| `_GA3_SpotDetection` | not called |  |  |  |   |
| `_GBasedSegmentation` | not called |  |  |  |   |
| `_HomogeneousSegmentation` | not called |  |  |  |   |
| `_SpotDetection` | not called |  |  |  |   |
| `_SpotDetection3DLoadSettings` | not called |  |  |  |   |
| `_SpotDetection3DSaveSettings` | not called |  |  |  |   |
| `_SpotDetectionLoadSettings` | not called |  |  |  |   |
| `_SpotDetectionSaveSettings` | not called |  |  |  |   |
| `_ThresholdCalcComp` | not called |  |  |  |   |
| `_ThresholdIHS` | not called |  |  |  |   |
| `_ThresholdLoadSettings` | not called |  |  |  |   |
| `_ThresholdOtsu` | not called |  |  |  |   |
| `_ThresholdSaveSettings` | not called |  |  |  |   |
| `_WoundSegmentation` | not called |  |  |  |   |
| `_WoundSegmentation3D` | not called |  |  |  |   |
| `BinaryCentroids3D` | not called |  |  |  |   |
| `CleanBinary3D` | not called |  |  |  |   |
| `CloseBinary3D` | not called |  |  |  |   |
| `CloseHolesBinary3D` | not called |  |  |  |   |
| `ConvexHull3D` | not called |  |  |  |   |
| `DetectBranching3D` | not called |  |  |  |   |
| `DetectEnding3D` | not called |  |  |  |   |
| `DilateBinary3D` | not called |  |  |  |   |
| `DistanceTransformBinary3D` | not called |  |  |  |   |
| `DistanceTransformBinary3DEx` | not called |  |  |  |   |
| `ErodeBinary3D` | not called |  |  |  |   |
| `EuclideanCloseBinary3D` | not called |  |  |  |   |
| `EuclideanDilateBinary3D` | not called |  |  |  |   |
| `EuclideanErodeBinary3D` | not called |  |  |  |   |
| `EuclideanOpenBinary3D` | not called |  |  |  |   |
| `FillHolesBinary3D` | not called |  |  |  |   |
| `GrowObjectsBinary3D` | not called |  |  |  |   |
| `OpenBinary3D` | not called |  |  |  |   |
| `SeparateObjectsBinary3D` | not called |  |  |  |   |
| `Skeletonize3D` | not called |  |  |  |   |
| `SmoothBinary3D` | not called |  |  |  |   |
| `SpotDetection3D` | not called |  |  |  |   |
| `_BinaryCentroids3D` | not called |  |  |  |   |
| `_CleanBinary3D` | not called |  |  |  |   |
| `_CloseBinary3D` | not called |  |  |  |   |
| `_CloseHolesBinary3D` | not called |  |  |  |   |
| `_DilateBinary3D` | not called |  |  |  |   |
| `_DistanceTransformBinary3D` | not called |  |  |  |   |
| `_ErodeBinary3D` | not called |  |  |  |   |
| `_EuclideanCloseBinary3D` | not called |  |  |  |   |
| `_EuclideanDilateBinary3D` | not called |  |  |  |   |
| `_EuclideanErodeBinary3D` | not called |  |  |  |   |
| `_EuclideanOpenBinary3D` | not called |  |  |  |   |
| `_FillHolesBinary3D` | not called |  |  |  |   |
| `_GA3_SpotDetection3D` | not called |  |  |  |   |
| `_GrowObjectsBinary3D` | not called |  |  |  |   |
| `_OpenBinary3D` | not called |  |  |  |   |
| `_SeparateObjectsBinary3D` | not called |  |  |  |   |
| `_SpotDetection3D` | not called |  |  |  |   |
| `_SpotDetection3DPrev2D` | not called |  |  |  |   |
| `_SmoothBinary3D` | not called |  |  |  |   |
| `BinaryFromGraticuleMask` | not called |  |  |  |   |
| `BinaryGetBoundingRect` | not called |  |  |  |   |
| `BinaryToColor` | not called |  |  |  |   |
| `BinaryWatershed` | not called |  |  |  |   |
| `ClearBinary` | not called |  |  |  |   |
| `ClearBinaryND` | not called |  |  |  |   |
| `ConnectObjects3D` | not called |  |  |  |   |
| `InvertBinary` | not called |  |  |  |   |
| `InvertBinaryGa3` | not called |  |  |  |   |
| `InvertBinaryND` | not called |  |  |  |   |
| `ObjectProcessing` | not called |  |  |  |   |
| `ProcessBinLayerGa3` | not called |  |  |  |   |
| `RemoveAllTouchingBinary` | not called |  |  |  |   |
| `RemoveAllTouchingBinaryGa3` | not called |  |  |  |   |
| `SetShowBinLayerContours` | not called |  |  |  |   |
| `SmoothBinaryGa3` | not called |  |  |  |   |
| `TrackBinaries` | not called |  |  |  |   |
| `TrackBinariesParam` | not called |  |  |  |   |
| `UpdateObjectsFeatures3D` | not called |  |  |  |   |
| `_ClearBinary` | not called |  |  |  |   |
| `_InvertBinary` | not called |  |  |  |   |
| `_InvertBinaryGa3` | not called |  |  |  |   |
| `_KeepSegmenting` | not called |  |  |  |   |
| `_ObjectProcessing` | not called |  |  |  |   |
| `_RemoveAllTouchingBinary` | not called |  |  |  |   |
| `_RemoveAllTouchingBinaryGa3` | not called |  |  |  |   |
| `_SmoothBinaryGa3` | not called |  |  |  |   |

## Calibration

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `Calibrate2` | not called |  |  |  |   |
| `Calibrate3` | not called |  |  |  |   |
| `Calibrate4_8` | not called |  |  |  |   |
| `Calibrate4_8Close` | not called |  |  |  |   |
| `CalibrateDefault` | not called |  |  |  |   |
| `Measurement_Channel` | not called |  |  |  |   |
| `Measurement_ChannelMask` | not called |  |  |  |   |
| `_CalibrateBrightness` | not called |  |  |  |   |
| `_CalibrateDensity` | not called |  |  |  |   |
| `CalibrateDocument` | not called |  |  |  |   |
| `GetCalibrationViewUnit` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_CalibrationAngleMatrix` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_CurrentCalibration` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ImageCalibration` | needs arguments | error: Bad number of parameters |  |  |   |
| `SaveImageCalibration` | not called |  |  |  |   |
| `SetCalibrationViewPrecision` | not called |  |  |  |   |
| `SetCalibrationViewUnit` | not called |  |  |  |   |
| `Uncalibrate` | not called |  |  |  |   |
| `_CalibrateEx` | not called |  |  |  |   |
| `_CalibrateExObjLine` | not called |  |  |  |   |
| `_Uncalibrate` | not called |  |  |  |   |

## Device

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `_Stg_CalibrateAnalogInput` | not called |  |  |  |   |
| `Stg_CalibratedAnalogOutputWrite` | not called |  |  |  |   |
| `_Stg_CalibrateAnalogOutput` | not called |  |  |  |   |
| `Stg_AnalogInputRead` | not called |  |  |  |   |
| `Stg_AnalogOutputRead` | not called |  |  |  |   |
| `Stg_AnalogOutputWrite` | not called |  |  |  |   |
| `Stg_GetAnalyzerState` | ran | 0 |  |  |   |
| `Stg_IsAnalyzerPresent` | ran | 0 |  |  |   |
| `Stg_SetAnalyzerState` | not called |  |  |  |   |
| `Stg_GetAperturePosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetApertureStepPosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetApertureSteps` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_IsAperturePresent` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_SetAperturePosition` | not called |  |  |  |   |
| `Stg_GetLastBarCode` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetCSUShutterState` | ran | 0 |  |  |   |
| `Stg_GetDiskSpeed` | ran | 7298712 |  |  |   |
| `Stg_GetRelayLensPosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_SetCSUShutterState` | not called |  |  |  |   |
| `Stg_SetDiskSpeed` | not called |  |  |  |   |
| `Stg_SetRelayLensPosition` | not called |  |  |  |   |
| `Stg_SyncDiskSpeed` | not called |  |  |  |   |
| `Stg_GetCondenserPosition` | ran | 0 |  |  |   |
| `Stg_GetCondenserPositions` | ran | 0 |  |  |   |
| `Stg_IsCondenserPresent` | ran | 0 |  |  |   |
| `Stg_SetCondenserPosition` | not called |  |  |  |   |
| `A1ApplyStimulationSettings` | not called |  |  |  |   |
| `A1AutoGain` | not called |  |  |  |   |
| `A1AutoGainSimple` | not called |  |  |  |   |
| `A1AutoOffset` | not called |  |  |  |   |
| `A1Capture1DZ` | not called |  |  |  |   |
| `A1Capture1DZ_IntensityCorr` | not called |  |  |  |   |
| `A1EnableIRLaserCOMPortConnection` | not called |  |  |  |   |
| `A1IRLaserAutoAlign` | not called |  |  |  |   |
| `A1Live1DZ` | not called |  |  |  |   |
| `A1Live1DZ_IntensityCorr` | not called |  |  |  |   |
| `A1SetOutputPort` | not called |  |  |  |   |
| `A1ShowSetupGUI` | not called |  |  |  |   |
| `A1TestSWTrigger` | not called |  |  |  |   |
| `A1VAASGetParams` | not called |  |  |  |   |
| `A1VAASSetParams` | not called |  |  |  |   |
| `C2SwitchLever` | not called |  |  |  |   |
| `LineChannelSeriesSetup` | not called |  |  |  |   |
| `LiveUnmixingToggle` | not called |  |  |  |   |
| `Live_Unmixing` | not called |  |  |  |   |
| `Live_Unmixing_EnabledChecked` | not called |  |  |  |   |
| `_A1AutoGain` | not called |  |  |  |   |
| `_A1AutoGain_Setup` | not called |  |  |  |   |
| `AxNSPARC_CheckNSPARCAlignment` | not called |  |  |  |   |
| `AxNSPARC_RunNSPARCAlignment` | not called |  |  |  |   |
| `ConfocalAX_MeasureCurrentIlluminationPower` | not called |  |  |  |   |
| `ConfocalAX_MeasureIlluminationPower` | not called |  |  |  |   |
| `Stg_CorrectionCollar_GetDescription` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_CorrectionCollar_GetPosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_CorrectionCollar_SetPosition` | not called |  |  |  |   |
| `Crest_DeepSIM__AdjustReconstructionParameters` | not called |  |  |  |   |
| `Crest_DeepSIM_CreateReconstructedImage` | not called |  |  |  |   |
| `Crest_DeepSIM_CreateReconstructedImageND` | not called |  |  |  |   |
| `Crest_DeepSIM_CreateRollingReconstructedImageND` | not called |  |  |  |   |
| `Crest_DeepSIM_ExportRawChannels` | not called |  |  |  |   |
| `Stg_SetDisk_On_Off` | not called |  |  |  |   |
| `VCS_SetFocusLens` | not called |  |  |  |   |
| `VCS_GetFocusLens` | not called |  |  |  |   |
| `Stg_DMD_AppendRoiAsPattern` | not called |  |  |  |   |
| `Stg_GetDMDActivePatternId` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetDMDAssociatedLightId` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetDMDAssociatedShutterCount` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetDMDAssociatedShutterId` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetDMDAssociatedShuttersOpenState` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetDMDAssociatedSwitcherId` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetDMDAssociatedSwitcherId' |  |  |   |
| `Stg_GetDMDAssociatedSwitcherPosition` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetDMDAssociatedSwitcherPosition' |  |  |   |
| `Stg_GetDMDCalibrated` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetDMDDeviceCount` | ran | 0 |  |  |   |
| `Stg_GetDMDDeviceName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetDMDPatternCount` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetDMDPatternId` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetDMDPatternIdByName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetDMDPatternName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_SetDMDActivePatternId` | not called |  |  |  |   |
| `Stg_SetDMDAssociatedShuttersOpenState` | not called |  |  |  |   |
| `Stg_Filter_GetCount` | ran | 0 |  |  |   |
| `Stg_Filter_GetName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Filter_GetPosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Filter_GetPositionCount` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Filter_GetPositionName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Filter_GetSpeed` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_Filter_GetSpeed' |  |  |   |
| `Stg_Filter_GetSpeedSteps` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_Filter_GetSpeedSteps' |  |  |   |
| `Stg_Filter_GetStepSpeed` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_Filter_GetStepSpeed' |  |  |   |
| `Stg_Filter_SetPosition` | not called |  |  |  |   |
| `Stg_Filter_SetPositionName` | not called |  |  |  |   |
| `Stg_Filter_SetSpeed` | not called |  |  |  |   |
| `Stg_GetFilterName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetFilterPosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetFilterPositions` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetFilterSpeed` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetFilterSpeed' |  |  |   |
| `Stg_GetFilterSpeedSteps` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetFilterSpeedSteps' |  |  |   |
| `Stg_GetFilterStepSpeed` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetFilterStepSpeed' |  |  |   |
| `Stg_IsFilterPresent` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_SetFilterName` | not called |  |  |  |   |
| `Stg_SetFilterPosition` | not called |  |  |  |   |
| `Stg_SetFilterSpeed` | not called |  |  |  |   |
| `Stg_HTIRF_GetAngle` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_GetAngle' |  |  |   |
| `Stg_HTIRF_SetAlignmentName` | not called |  |  |  |   |
| `Stg_HTIRF_SetAngle` | not called |  |  |  |   |
| `Stg_HTIRF_GetDirection` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_GetDirection' |  |  |   |
| `Stg_HTIRF_SetDirection` | not called |  |  |  |   |
| `Stg_HTIRF_GetFocus` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_GetFocus' |  |  |   |
| `Stg_HTIRF_SetFocus` | not called |  |  |  |   |
| `Stg_HTIRF_GetX` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_GetX' |  |  |   |
| `Stg_HTIRF_SetX` | not called |  |  |  |   |
| `Stg_HTIRF_GetY` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_GetY' |  |  |   |
| `Stg_HTIRF_SetY` | not called |  |  |  |   |
| `Stg_HTIRF_IsGradationND` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_IsGradationND' |  |  |   |
| `Stg_HTIRF_IsLambdaQP` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_HTIRF_IsLambdaQP' |  |  |   |
| `Stg_HTIRF_SetXYFocus` | not called |  |  |  |   |
| `Stg_HTIRF_SetXY` | not called |  |  |  |   |
| `Stg_NSTORM_GetZoom` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_NSTORM_GetZoom' |  |  |   |
| `Stg_NSTORM_SetZoom` | not called |  |  |  |   |
| `Stg_HeatStageContinueCooling` | not called |  |  |  |   |
| `Stg_HeatStageContinueHeating` | not called |  |  |  |   |
| `Stg_HeatStageGetCurrentTemperature` | not called |  |  |  |   |
| `Stg_HeatStageGetStatus` | not called |  |  |  |   |
| `Stg_HeatStageHoldCurrentTemperature` | not called |  |  |  |   |
| `Stg_HeatStageIsPresent` | not called |  |  |  |   |
| `Stg_HeatStageSetTemperature` | not called |  |  |  |   |
| `Stg_HeatStageSetTemperatureRate` | not called |  |  |  |   |
| `Stg_HeatStageStartHeatingCooling` | not called |  |  |  |   |
| `Stg_HeatStageStopHeatingCooling` | not called |  |  |  |   |
| `Stg_HeatStage_ContinueCooling` | not called |  |  |  |   |
| `Stg_HeatStage_ContinueHeating` | not called |  |  |  |   |
| `Stg_HeatStage_GetCount` | ran | 0 |  |  |   |
| `Stg_HeatStage_GetCurrentTemperature` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_HeatStage_GetName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_HeatStage_GetStatus` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_HeatStage_HoldCurrentTemperature` | not called |  |  |  |   |
| `Stg_HeatStage_SetTemperature` | not called |  |  |  |   |
| `Stg_HeatStage_SetTemperatureRate` | not called |  |  |  |   |
| `Stg_HeatStage_StartHeatingCooling` | not called |  |  |  |   |
| `Stg_HeatStage_StopHeatingCooling` | not called |  |  |  |   |
| `Stg_Incubator_GetCurrentGas` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Incubator_GetCurrentHumidity` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Incubator_GetCurrentPressure` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Incubator_GetPressureRange` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Incubator_GetTargetGas` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Incubator_GetTargetHumidity` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Incubator_GetTargetPressure` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Incubator_SetAtmosphericPressure` | not called |  |  |  |   |
| `Stg_Incubator_SetTargetGas` | not called |  |  |  |   |
| `Stg_Incubator_SetTargetHumidity` | not called |  |  |  |   |
| `Stg_Incubator_SetTargetPressure` | not called |  |  |  |   |
| `Stg_Incubator_SetVacuumPressure` | not called |  |  |  |   |
| `Stg_LUNB_GetCylindricalLensMounted` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_LUNB_GetCylindricalLensMounted' |  |  |   |
| `Stg_LUNB_GetCylindricalLensPosition` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_LUNB_GetCylindricalLensPosition' |  |  |   |
| `Stg_LUNB_GetRelayLensMounted` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_LUNB_GetRelayLensMounted' |  |  |   |
| `Stg_LUNB_GetRelayLensPosition` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_LUNB_GetRelayLensPosition' |  |  |   |
| `Stg_LUNB_SetCylindricalLensPosition` | not called |  |  |  |   |
| `Stg_LUNB_SetRelayLensPosition` | not called |  |  |  |   |
| `Stg_GetLaserOutputModality` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetLaserOutputModality' |  |  |   |
| `Stg_GetLaserOutputNumPorts` | ran | 0 |  |  |   |
| `Stg_GetLaserOutputPortUsed` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetLaserOutputPortUsedEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_SetLaserOutputPortUsed` | not called |  |  |  |   |
| `Stg_SetLaserOutputPortUsedEx` | not called |  |  |  |   |
| `Stg_GetLightIrisIntensity` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetLightIrisIntensitySteps` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetLightIrisSteps` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetLightState` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetLightStepVoltage` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetLightVoltage` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetLightVoltageSteps` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_IsLightPresent` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_GetCount` | ran | 0 |  |  |   |
| `Stg_Light_GetIrisIntensity` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_GetIrisSteps` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_GetNDFilterControllable` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_GetNDFilterPosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_GetNDFilterStepPosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_GetNDFilterSteps` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_GetName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_GetRemoteSwitch` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_GetState` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_GetStepIrisIntensity` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_GetStepVoltage` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_GetVoltage` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_GetVoltageSteps` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_IsIrisControllable` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_IsVoltageControllable` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_Light_SetIrisIntensity` | not called |  |  |  |   |
| `Stg_Light_SetNDFilterPosition` | not called |  |  |  |   |
| `Stg_Light_SetRemoteSwitch` | not called |  |  |  |   |
| `Stg_Light_SetState` | not called |  |  |  |   |
| `Stg_Light_SetVoltage` | not called |  |  |  |   |
| `Stg_SetLightIrisIntensity` | not called |  |  |  |   |
| `Stg_SetLightState` | not called |  |  |  |   |
| `Stg_SetLightVoltage` | not called |  |  |  |   |
| `Stg_GetLightPathPosition` | ran | 0 |  |  |   |
| `Stg_GetLightPathPositions` | ran | 0 |  |  |   |
| `Stg_IsLightPathPresent` | ran | 0 |  |  |   |
| `Stg_SetLightPathPosition` | not called |  |  |  |   |
| `Stg_Bioluminescence_Mode` | not called |  |  |  |   |
| `Stg_CaptureSlidePreview` | not called |  |  |  |   |
| `Stg_CloseMicroscopeDoor` | not called |  |  |  |   |
| `Stg_DisplayLED` | not called |  |  |  |   |
| `Stg_EnableMicControlPad` | not called |  |  |  |   |
| `Stg_GetMicroscopeSleep` | ran | 0 |  |  |   |
| `Stg_GetPinConfiguredForTTLOutput` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPinConfiguredForTTLOutput' |  |  |   |
| `Stg_GetPinConfiguredForTTLOutputPulse` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPinConfiguredForTTLOutputPulse' |  |  |   |
| `Stg_GetPinTTLOutputState` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPinTTLOutputState' |  |  |   |
| `Stg_IsMicroscopePresent` | ran | 0 |  |  |   |
| `Stg_MicroscopeMuteSound` | not called |  |  |  |   |
| `Stg_MicroscopeOperationSound` | not called |  |  |  |   |
| `Stg_MicroscopeSleep` | not called |  |  |  |   |
| `Stg_OpenMicroscopeDoor` | not called |  |  |  |   |
| `Stg_SetBlockMicroscopeAccessories` | not called |  |  |  |   |
| `Stg_SetPinTTLOutputPulse` | not called |  |  |  |   |
| `Stg_SetPinTTLOutputState` | not called |  |  |  |   |
| `Stg_ShutdownMicroscope` | not called |  |  |  |   |
| `Stg_ToggleMicControlPad` | not called |  |  |  |   |
| `Stg_TriggerInternalCamera` | not called |  |  |  |   |
| `Stg_GetMultiLaserCount` | ran | 0 |  |  |   |
| `Stg_GetMultiLaserLineNDFilter` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetMultiLaserLineName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetMultiLaserLineUsed` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetMultiLaserModality` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetMultiLaserModality' |  |  |   |
| `Stg_GetMultiLaserName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetMultiLaserNumLines` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetMultiLaserOpMode` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetMultiLaserPower` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetMultiLaserPowerSteps` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetMultiLaserStepPower` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetMultiLaserWavelength` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_RemoveInterlock` | not called |  |  |  |   |
| `Stg_SetMultiLaserLineAltSeq` | not called |  |  |  |   |
| `Stg_SetMultiLaserLineNDFilter` | not called |  |  |  |   |
| `Stg_SetMultiLaserLineName` | not called |  |  |  |   |
| `Stg_SetMultiLaserLineUsed` | not called |  |  |  |   |
| `Stg_SetMultiLaserOpMode` | not called |  |  |  |   |
| `Stg_SetMultiLaserPower` | not called |  |  |  |   |
| `Stg_SetMultiLaserWavelength` | not called |  |  |  |   |
| `Stg_StartMultiLaserAdvancedAltSeq` | not called |  |  |  |   |
| `Stg_StartMultiLaserAdvancedAltSeqEx` | not called |  |  |  |   |
| `Stg_StopMultiLaserAdvancedAltSeq` | not called |  |  |  |   |
| `_Stg_CalibrateMultiLaserLine` | not called |  |  |  |   |
| `Stg_GetNDFilterPosition` | ran | 0.0 |  |  |   |
| `Stg_GetNDFilterStepPosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetNDFilterSteps` | ran | 0 |  |  |   |
| `Stg_IsNDFilterPresent` | ran | 0 |  |  |   |
| `Stg_SetNDFilterPosition` | not called |  |  |  |   |
| `Stg_GetObjectiveNameFromCode` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetNosepieceObjectiveCode` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetNosepieceObjectiveName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetNosepieceObjectiveRefractiveIndex` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetNosepiecePosition` | ran | 0 |  |  |   |
| `Stg_GetNosepiecePositions` | ran | 0 |  |  |   |
| `Stg_IsNosepiecePresent` | ran | 0 |  |  |   |
| `Stg_Nosepiece_EnableRotation` | not called |  |  |  |   |
| `Stg_SetNosepieceObjective` | not called |  |  |  |   |
| `Stg_SetNosepieceObjectiveName` | not called |  |  |  |   |
| `Stg_SetNosepiecePosition` | not called |  |  |  |   |
| `_Stg_NosepieceSetup` | not called |  |  |  |   |
| `Stg_DropOil` | not called |  |  |  |   |
| `StgFocusPFS` | not called |  |  |  |   |
| `StgGetPFSPlanePoints` | ran | 0 |  |  |   |
| `StgIsPFSPlaneValid` | ran | 0 |  |  |   |
| `StgResetPFSPlane` | not called |  |  |  |   |
| `StgUsePFSPlane` | not called |  |  |  |   |
| `Stg_GetPFSLEDSwitch` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPFSLEDSwitch' |  |  |   |
| `Stg_GetPFSLensOffsetPosition` | ran | 0 |  |  |   |
| `Stg_GetPFSStatus` | ran | 0 |  |  |   |
| `Stg_IsPFSPresent` | ran | 0 |  |  |   |
| `Stg_PFSEnableSignalOutput` | not called |  |  |  |   |
| `Stg_PFSFindOffset` | not called |  |  |  |   |
| `Stg_PFSGetDishType` | not called |  |  |  |   |
| `Stg_PFSGetDishTypeChangeable` | not called |  |  |  |   |
| `Stg_PFSInsertExtractDM` | not called |  |  |  |   |
| `Stg_PFSIsDMInserted` | not called |  |  |  |   |
| `Stg_PFSIsDMMotorized` | not called |  |  |  |   |
| `Stg_PFSIsSignalOutputEnabled` | not called |  |  |  |   |
| `Stg_PFSSetDishType` | not called |  |  |  |   |
| `Stg_PFSSetLEDPower` | not called |  |  |  |   |
| `Stg_PFSSignalOutputTest` | not called |  |  |  |   |
| `Stg_SetPFSFocus` | not called |  |  |  |   |
| `Stg_SetPFSLEDSwitch` | not called |  |  |  |   |
| `Stg_SetPFSLensOffsetPosition` | not called |  |  |  |   |
| `Stg_SetPFSStatus` | not called |  |  |  |   |
| `Stg_WaitForPFS` | not called |  |  |  |   |
| `_StgSetupPFSFocus` | not called |  |  |  |   |
| `Stg_GetPatternDeviceName` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPatternDeviceName' |  |  |   |
| `Stg_GetPatternId` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPatternId' |  |  |   |
| `Stg_GetPatternIdByName` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPatternIdByName' |  |  |   |
| `Stg_GetPatternName` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPatternName' |  |  |   |
| `Stg_GetPatternState` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetPatternState' |  |  |   |
| `Stg_Perfusion_Clean` | not called |  |  |  |   |
| `Stg_Perfusion_Dispence_mL` | not called |  |  |  |   |
| `Stg_Perfusion_GetState` | ran | 0 |  |  |   |
| `Stg_Perfusion_LoadCalibrationFromXML` | not called |  |  |  |   |
| `Stg_Perfusion_Purge_mL` | not called |  |  |  |   |
| `Stg_Perfusion_SetSolvent` | not called |  |  |  |   |
| `PiezoXYGetPosition` | not called |  |  |  |   |
| `PiezoXYMoveToHomePosition` | not called |  |  |  |   |
| `PiezoXYMoveToXYPosition` | not called |  |  |  |   |
| `Stg_CloseFirstShutter` | not called |  |  |  |   |
| `Stg_GetShutterAperture` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetShutterApertureSteps` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetShutterCount` | ran | 0 |  |  |   |
| `Stg_GetShutterName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetShutterSpeed` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetShutterSpeed' |  |  |   |
| `Stg_GetShutterSpeedSteps` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetShutterSpeedSteps' |  |  |   |
| `Stg_GetShutterState` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetShutterStateEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetShutterStepAperture` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetShutterStepSpeed` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_GetShutterStepSpeed' |  |  |   |
| `Stg_IsShutterPresent` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_OpenFirstShutter` | not called |  |  |  |   |
| `Stg_SetShutterAperture` | not called |  |  |  |   |
| `Stg_SetShutterSpeed` | not called |  |  |  |   |
| `Stg_SetShutterState` | not called |  |  |  |   |
| `Stg_SetShutterStateEx` | not called |  |  |  |   |
| `Stg_ToggleFirstShutter` | not called |  |  |  |   |
| `_Stg_FiltersShutters` | not called |  |  |  |   |
| `_Stg_RenameShutter` | not called |  |  |  |   |
| `Stg_AllowSlideLoaderCassetteManipulation` | not called |  |  |  |   |
| `Stg_GetBarCode` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetBarCodeEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetCassetteCount` | ran | 0 |  |  |   |
| `Stg_GetLoadedSlide` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetSlideCount` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetSlideLoaderHolderCapacity` | ran | 0 |  |  |   |
| `Stg_InitializeSlideLoader` | not called |  |  |  |   |
| `Stg_IsBarCodeScanned` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_IsCassettePresent` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_IsCassetteScanned` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_IsSlideLoaded` | ran | 0 |  |  |   |
| `Stg_IsSlideLoaderCassetteManipulationAllowed` | ran | 0 |  |  |   |
| `Stg_IsSlideLoaderInitialized` | ran | 0 |  |  |   |
| `Stg_IsSlidePresent` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_IsSlidePresentEx` | ran | 0 |  |  |   |
| `Stg_LoadSlideFrom` | not called |  |  |  |   |
| `Stg_LoadSlideToPreparationPosition` | not called |  |  |  |   |
| `Stg_PreScanBarCode` | not called |  |  |  |   |
| `Stg_ScanCassette` | not called |  |  |  |   |
| `Stg_ScanPosition` | not called |  |  |  |   |
| `Stg_SetSlidePresent` | not called |  |  |  |   |
| `Stg_SlideLoaderGetHwStatus` | not called |  |  |  |   |
| `Stg_SlideloaderCheckStageEmpty` | not called |  |  |  |   |
| `Stg_SlideLoaderMoveAtVelocity` | not called |  |  |  |   |
| `Stg_SlideLoaderShowError` | not called |  |  |  |   |
| `Stg_SlideLoaderWarmInitAvailable` | not called |  |  |  |   |
| `Stg_StopSlideLoader` | not called |  |  |  |   |
| `Stg_TransferSlide` | not called |  |  |  |   |
| `Stg_UnloadSlide` | not called |  |  |  |   |
| `Stg_UnloadSlideTo` | not called |  |  |  |   |
| `_Stg_InitializeSlideLoader` | not called |  |  |  |   |
| `Stg_StimDev_AddPatternFromImage` | not called |  |  |  |   |
| `Stg_GetTIRFMirror` | ran | 0 |  |  |   |
| `Stg_SetTIRFMirror` | not called |  |  |  |   |
| `Stg_SetTIRFMouseWheel` | not called |  |  |  |   |
| `Stg_GetTIRFAngleEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetTIRFDirectionEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetTIRFFocusEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetTIRFPosition` | ran | 0.0 |  |  |   |
| `Stg_GetTIRFPositionEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_SetTIRFAngleEx` | not called |  |  |  |   |
| `Stg_SetTIRFDirectionEx` | not called |  |  |  |   |
| `Stg_SetTIRFFocusEx` | not called |  |  |  |   |
| `Stg_SetTIRFPosition` | not called |  |  |  |   |
| `Stg_SetTIRFPositionEx` | not called |  |  |  |   |
| `Stg_DIOReadInputs` | not called |  |  |  |   |
| `Stg_GetLineIndex` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetTTLStatus` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_TTLInputRead` | not called |  |  |  |   |
| `Stg_PulseTTL` | not called |  |  |  |   |
| `Stg_TTLOutputDoAction` | not called |  |  |  |   |
| `Stg_TTLOutputDoActionAsync` | not called |  |  |  |   |
| `Stg_TTLOutputGetControlMode` | not called |  |  |  |   |
| `Stg_TTLOutputGetControlModePulses` | not called |  |  |  |   |
| `Stg_TTLOutputGetPulseActiveState` | not called |  |  |  |   |
| `Stg_TTLOutputGetPulseTime` | not called |  |  |  |   |
| `Stg_TTLOutputPulse` | not called |  |  |  |   |
| `Stg_TTLOutputPulseAsync` | not called |  |  |  |   |
| `Stg_TTLOutputPulsesTrain` | not called |  |  |  |   |
| `Stg_TTLOutputPulsesTrainAbort` | not called |  |  |  |   |
| `Stg_TTLOutputPulsesTrainAsync` | not called |  |  |  |   |
| `Stg_TTLOutputPulsesTrainFinished` | not called |  |  |  |   |
| `Stg_TTLOutputSetControlMode` | not called |  |  |  |   |
| `Stg_TTLOutputSetPulseActiveState` | not called |  |  |  |   |
| `Stg_TTLOutputSetPulseTime` | not called |  |  |  |   |
| `Stg_TTLOutputWrite` | not called |  |  |  |   |
| `Stg_WriteTTL` | not called |  |  |  |   |
| `Stg_WID_Abort` | not called |  |  |  |   |
| `Stg_WID_AllowAutomaticReplenishment` | not called |  |  |  |   |
| `Stg_WID_Discharge` | not called |  |  |  |   |
| `Stg_WID_GetLastReplenishmentTime` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_WID_GetLastReplenishmentTime' |  |  |   |
| `Stg_WID_GetObjectiveWet` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_WID_GetObjectiveWet' |  |  |   |
| `Stg_WID_GetReplenishmentRemainingTimeInSeconds` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_WID_GetReplenishmentRemainingTimeInSeconds' |  |  |   |
| `Stg_WID_GetReplenishmentTimePeriodInSeconds` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_WID_GetReplenishmentTimePeriodInSeconds' |  |  |   |
| `Stg_WID_GetWaterInitiated` | not reachable | AttributeError: 'Macro' object has no attribute 'Stg_WID_GetWaterInitiated' |  |  |   |
| `Stg_WID_Initiate` | not called |  |  |  |   |
| `Stg_WID_Replenish` | not called |  |  |  |   |
| `Stg_WID_WaitForFinish` | not called |  |  |  |   |
| `PI_GcsCommand` | not called |  |  |  |   |
| `StgGeneratePointsForXYOverview` | not called |  |  |  |   |
| `FindPointInPairedDocument` | not called |  |  |  |   |
| `StgCalibrateXYAutomatic` | not called |  |  |  |   |
| `StgEnableJoystickXY` | not called |  |  |  |   |
| `StgGetInitValuesXY` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgGetPosXY` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgGetRelativeMovements` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgInitiateXY` | not called |  |  |  |   |
| `StgMoveXY` | not called |  |  |  |   |
| `StgMoveXYScan` | not called |  |  |  |   |
| `StgMoveXYToRoi` | not called |  |  |  |   |
| `StgSetRelativeMovements` | not called |  |  |  |   |
| `StgSetTrigger` | not called |  |  |  |   |
| `StgToggleJoystickXY` | not called |  |  |  |   |
| `StgXY_DrawCircleAsync_Start` | not called |  |  |  |   |
| `StgXY_DrawCircleAsync_Stop` | not called |  |  |  |   |
| `StgXY_DrawCircleAsync_WaitAngle` | not called |  |  |  |   |
| `StgXY_GetBlockAxis` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgXY_GetBlockAxisSupported` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgXY_GetJoystickSpeed` | ran | -4.0 |  |  |   |
| `StgXY_GetJoystickSpeedSteps` | ran | -4 |  |  |   |
| `StgXY_GetLimits` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgXY_GetMotorSpeed` | ran | -4.0 |  |  |   |
| `StgXY_GetMotorSpeedSteps` | ran | -4 |  |  |   |
| `StgXY_GetPrecision` | ran | -4.0 |  |  |   |
| `StgXY_GetSettleTime` | ran | -4.0 |  |  |   |
| `StgXY_GetSpeedRamp` | ran | -4 |  |  |   |
| `StgXY_GetSpeedRampSteps` | ran | -4 |  |  |   |
| `StgXY_GetSpeedVector` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgXY_GetStepJoystickSpeed` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgXY_GetStepMotorSpeed` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgXY_IsJoystickSpeedControllable` | ran | 0 |  |  |   |
| `StgXY_IsMotorSpeedControllable` | ran | 0 |  |  |   |
| `StgXY_IsPrecisionControllable` | ran | 0 |  |  |   |
| `StgXY_IsPresent` | ran | 0 |  |  |   |
| `StgXY_IsSettleTimeControllable` | ran | 0 |  |  |   |
| `StgXY_IsSpeedRampControllable` | ran | 0 |  |  |   |
| `StgXY_IsSpeedVectorControllable` | ran | 0 |  |  |   |
| `StgXY_IsVirtualJoystickSupported` | ran | 0 |  |  |   |
| `StgXY_MoveVirtualJoystickAtSpeed` | not called |  |  |  |   |
| `StgXY_SetBlockAxis` | not called |  |  |  |   |
| `StgXY_IsInLoadingPosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgXY_SetJoystickSpeed` | not called |  |  |  |   |
| `StgXY_MoveToAcquisitionPosition` | not called |  |  |  |   |
| `StgXY_MoveToLoadingPosition` | not called |  |  |  |   |
| `StgXY_SetLimits` | not called |  |  |  |   |
| `StgXY_SetMotorSpeed` | not called |  |  |  |   |
| `StgXY_SetPrecision` | not called |  |  |  |   |
| `StgXY_SetSettleTime` | not called |  |  |  |   |
| `StgXY_SetSpeedRamp` | not called |  |  |  |   |
| `StgXY_SetSpeedVector` | not called |  |  |  |   |
| `_StgCalibrateXY4Points` | not called |  |  |  |   |
| `_StgCalibrateXYAutomatic` | not called |  |  |  |   |
| `_StgConfigXY` | not called |  |  |  |   |
| `StgEnableJoystick` | not called |  |  |  |   |
| `StgGetList` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgGetListEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgGetPos` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgInitiate` | not called |  |  |  |   |
| `StgJoystickOff` | not called |  |  |  |   |
| `StgJoystickOn` | not called |  |  |  |   |
| `StgMove` | not called |  |  |  |   |
| `StgMoveXYZScan` | not called |  |  |  |   |
| `StgScan` | not called |  |  |  |   |
| `StgScanCaptureOnEachScan` | not called |  |  |  |   |
| `StgScanDir` | not called |  |  |  |   |
| `StgScanEllipse` | not called |  |  |  |   |
| `StgScanEx` | not called |  |  |  |   |
| `StgScanFocus` | not called |  |  |  |   |
| `StgScanMacro` | not called |  |  |  |   |
| `StgScanOrigin` | not called |  |  |  |   |
| `StgScanRange` | not called |  |  |  |   |
| `StgScanReturn` | not called |  |  |  |   |
| `StgScanStatus` | not called |  |  |  |   |
| `StgScanSystem` | not called |  |  |  |   |
| `StgStopScan` | not called |  |  |  |   |
| `StgToggleJoystick` | not called |  |  |  |   |
| `Stg_LargeImageScan` | not called |  |  |  |   |
| `Stg_LargeImageScanArea` | not called |  |  |  |   |
| `Stg_LargeImageStageScanWithName` | not called |  |  |  |   |
| `Stg_LinearActuator_GetDescription` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_LinearActuator_GetPosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_LinearActuator_SetPosition` | not called |  |  |  |   |
| `Stg_LoadLastFocusSurfacePoints` | not called |  |  |  |   |
| `Stg_RemoveFocusSurfacePoints` | not called |  |  |  |   |
| `Stg_SetLargeImageQuietMode` | not called |  |  |  |   |
| `Stg_SetLargeImageStageScanningMacro` | not called |  |  |  |   |
| `Stg_SetLargeImageStageZParams` | not called |  |  |  |   |
| `_StgConfig` | not called |  |  |  |   |
| `_StgInitiate` | not called |  |  |  |   |
| `_StgSetupScan` | not called |  |  |  |   |
| `_Stg_LargeImageScanning` | not called |  |  |  |   |
| `_Stg_LargeImageStageScanning` | not called |  |  |  |   |
| `_Stg_LargeImageStageScanningWMacro` | not called |  |  |  |   |
| `_Stg_LargeImageStageScanningWithZ` | not called |  |  |  |   |
| `RunAutoFocusLong` | not called |  |  |  |   |
| `RunAutoFocusShort` | not called |  |  |  |   |
| `RunAutoFocusSmartRange` | not called |  |  |  |   |
| `RunFastAutoFocus` | not called |  |  |  |   |
| `StgEnableJoystickZ` | not called |  |  |  |   |
| `StgFocus` | not called |  |  |  |   |
| `StgFocusAdaptive` | not called |  |  |  |   |
| `StgFocusAdaptiveTwoPasses` | not called |  |  |  |   |
| `StgFocusCriteria` | not called |  |  |  |   |
| `StgFocusInRange` | not called |  |  |  |   |
| `StgFocusInRangeEx` | not called |  |  |  |   |
| `StgFocusInRangeExTwoPasses` | not called |  |  |  |   |
| `StgFocusInRangeTwoPasses` | not called |  |  |  |   |
| `StgFocusPlane` | not called |  |  |  |   |
| `StgFocusSetCriterion` | not called |  |  |  |   |
| `StgFocusSetCriterionDialog` | not called |  |  |  |   |
| `StgGetAbsPosZ` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgGetFocusPlanePosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgGetFocusPlaneType` | ran | 0 |  |  |   |
| `StgGetPosZ` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgInitiateZ` | not called |  |  |  |   |
| `StgIsFocusPlaneValid` | ran | 0 |  |  |   |
| `StgMoveMainZ` | not called |  |  |  |   |
| `StgMovePiezoZ` | not called |  |  |  |   |
| `StgMovePiezoZToHomeKeepZ` | not called |  |  |  |   |
| `StgMovePiezoZToHomePosition` | not called |  |  |  |   |
| `StgMoveZ` | not called |  |  |  |   |
| `StgMoveZNamed` | not called |  |  |  |   |
| `StgSetFocusPlane` | not called |  |  |  |   |
| `StgSetupFocus` | not called |  |  |  |   |
| `StgSetupFocusAdaptiveTwoPasses` | not called |  |  |  |   |
| `StgSetupFocusContinuousTwoPasses` | not called |  |  |  |   |
| `StgSetupFocusEx` | not called |  |  |  |   |
| `StgSetupFocusOffset` | not called |  |  |  |   |
| `StgSetupFocusTwoPasses` | not called |  |  |  |   |
| `StgToggleJoystickZ` | not called |  |  |  |   |
| `StgZ_AutoFocus` | not called |  |  |  |   |
| `StgZ_Escape` | not called |  |  |  |   |
| `StgZ_GetActiveZ` | ran | 0 |  |  |   |
| `StgZ_GetEscape` | ran | 0 |  |  |   |
| `StgZ_GetJoystickSpeed` | ran | -3.0 |  |  |   |
| `StgZ_GetJoystickSpeedSteps` | ran | -3 |  |  |   |
| `StgZ_GetJoystickZStep` | ran | 5.0 |  |  |   |
| `StgZ_GetLimits` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgZ_GetLimitsMultiple` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgZ_GetMotorSpeed` | ran | -3.0 |  |  |   |
| `StgZ_GetMotorSpeedSteps` | ran | -3 |  |  |   |
| `StgZ_GetPiezoDevice` | ran | 0 |  |  |   |
| `StgZ_GetReferencePosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgZ_GetSpeedRamp` | ran | -3 |  |  |   |
| `StgZ_GetSpeedRampSteps` | ran | -3 |  |  |   |
| `StgZ_GetStepJoystickSpeed` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgZ_GetStepMotorSpeed` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgZ_IsJoystickSpeedControllable` | ran | -1 |  |  |   |
| `StgZ_IsMotorSpeedControllable` | ran | -1 |  |  |   |
| `StgZ_IsPresent` | needs arguments | error: Bad number of parameters |  |  |   |
| `StgZ_IsSpeedRampControllable` | ran | -1 |  |  |   |
| `StgZ_IsVirtualJoystickSupported` | ran | -1 |  |  |   |
| `StgZ_MoveVirtualJoystickAtSpeed` | not called |  |  |  |   |
| `StgZ_Refocus` | not called |  |  |  |   |
| `StgZ_SetActiveZ` | not called |  |  |  |   |
| `StgZ_SetJoystickSpeed` | not called |  |  |  |   |
| `StgZ_SetJoystickZStep` | not called |  |  |  |   |
| `StgZ_SetKeepPosition` | not called |  |  |  |   |
| `StgZ_SetLimits` | not called |  |  |  |   |
| `StgZ_SetMotorSpeed` | not called |  |  |  |   |
| `StgZ_SetSpeedRamp` | not called |  |  |  |   |
| `Stg_EnableMouseJoystickZ` | not called |  |  |  |   |
| `Stg_IsMouseJoystickZ` | ran | 1 |  |  |   |
| `Stg_ToggleMouseJoystickZ` | not called |  |  |  |   |
| `_SetupFastAutoFocus` | not called |  |  |  |   |
| `_StgCalibrateZ` | not called |  |  |  |   |
| `_StgConfigZ` | not called |  |  |  |   |
| `_StgInitiateZ` | not called |  |  |  |   |
| `_StgSetupFocus` | not called |  |  |  |   |
| `_StgSetupFocusPlane` | not called |  |  |  |   |
| `_Stg_SetupMouseJoystickZ` | not called |  |  |  |   |
| `Stg_GetZoomPosition` | ran | 1.0 |  |  |   |
| `Stg_GetZoomStepPosition` | needs arguments | error: Bad number of parameters |  |  |   |
| `Stg_GetZoomSteps` | ran | 0 |  |  |   |
| `Stg_IsZoomManual` | ran | 1 |  |  |   |
| `Stg_IsZoomPresent` | ran | 0 |  |  |   |
| `Stg_LoadZoomCorrection` | not called |  |  |  |   |
| `Stg_SetZoomPosition` | not called |  |  |  |   |
| `Stg_ShowZoomConfig` | not called |  |  |  |   |
| `_Stg_ShowZoomConfig` | not called |  |  |  |   |
| `A1ACCGetCollectParams` | not called |  |  |  |   |
| `A1ACCSetCollectParams` | not called |  |  |  |   |
| `A1ACCGetLaserParams` | not called |  |  |  |   |
| `A1ACCSetLaserParams` | not called |  |  |  |   |
| `ACC_AdjustForCurrentZPosition` | not called |  |  |  |   |
| `ACC_GetCorrectedStack` | not called |  |  |  |   |
| `ACC_MoveDevices` | not called |  |  |  |   |
| `_ACC_AutoCorrection` | not called |  |  |  |   |
| `_ACC_Settings` | not called |  |  |  |   |
| `ACC_ValidateZStackAvailability` | not called |  |  |  |   |
| `_ObjectiveClearance` | not called |  |  |  |   |
| `_ObjectivesXYOffset` | not called |  |  |  |   |
| `AddObjective` | not called |  |  |  |   |
| `ApplyObjectivesXYOffset` | not called |  |  |  |   |
| `AddObjectiveEx` | not called |  |  |  |   |
| `BackupObjectives` | not called |  |  |  |   |
| `ChangeObjective` | not called |  |  |  |   |
| `DeleteObjective` | not called |  |  |  |   |
| `DeleteObjectives` | not called |  |  |  |   |
| `GetCurrentObjMagnification` | ran | 0.0 |  |  |   |
| `GetCurrentObjName` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetObjMagnification` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetObjType` | needs arguments | error: Bad number of parameters |  |  |   |
| `RestoreObjectives` | not called |  |  |  |   |
| `RestoreObjectivesEx` | not called |  |  |  |   |
| `_BackupObjectives` | not called |  |  |  |   |
| `_CalibrateObjective` | not called |  |  |  |   |
| `_CalibrateObjective2` | not called |  |  |  |   |
| `_CalibrateObjective3` | not called |  |  |  |   |
| `_ExploreObjectives` | not called |  |  |  |   |
| `_QuickCalibration` | not called |  |  |  |   |
| `_RestoreObjectives` | not called |  |  |  |   |

## ExportResults

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `CopyExternalMetadata` | not called |  |  |  |   |
| `Export` | not called |  |  |  |   |
| `ImageExportAllAvailableInfo` | not called |  |  |  |   |
| `ExportLoadSetting` | not called |  |  |  |   |
| `ExportSaveAndCloseExcelFile` | not called |  |  |  |   |
| `ExportSaveSetting` | not called |  |  |  |   |
| `ExportSetExcelPos` | not called |  |  |  |   |
| `ExportSetName` | not called |  |  |  |   |
| `ExportSettings` | not called |  |  |  |   |
| `SetAlignmentPoints` | not called |  |  |  |   |
| `_ShowExportSettings` | not called |  |  |  |   |
| `CopyTextToClipboard` | not called |  |  |  |   |
| `Excel_Close` | not called |  |  |  |   |
| `Excel_GetValue` | not called |  |  |  |   |
| `Excel_GetValueEx` | not called |  |  |  |   |
| `Excel_Open` | not called |  |  |  |   |
| `Excel_Paste` | not called |  |  |  |   |
| `Excel_PasteEx` | not called |  |  |  |   |
| `Excel_Save` | not called |  |  |  |   |
| `Excel_SetValue` | not called |  |  |  |   |
| `Excel_SetValueEx` | not called |  |  |  |   |
| `RG_CloseWindow` | not called |  |  |  |   |
| `RG_CopyCurrentImage` | not called |  |  |  |   |
| `RG_ExportToImage` | not called |  |  |  |   |
| `RG_ExportToPDF` | not called |  |  |  |   |
| `RG_GetROIDByCustomID` | not called |  |  |  |   |
| `RG_GetROIDs` | not called |  |  |  |   |
| `RG_InitUndoManager` | not called |  |  |  |   |
| `RG_MeasExport` | not called |  |  |  |   |
| `RG_NewReportFromTemplate` | not called |  |  |  |   |
| `RG_Open` | not called |  |  |  |   |
| `RG_OpenFromBinBuffer` | not called |  |  |  |   |
| `RG_OpenReportReadOnly` | not called |  |  |  |   |
| `RG_Print` | not called |  |  |  |   |
| `RG_SaveToFile` | not called |  |  |  |   |
| `RG_ScriptDS_SetROAttribute_Double` | not called |  |  |  |   |
| `RG_ScriptDS_SetROAttribute_RGBA` | not called |  |  |  |   |
| `RG_ScriptDS_SetROAttribute_String` | not called |  |  |  |   |
| `RG_ScriptDS_SetROAttribute_Uint` | not called |  |  |  |   |
| `RG_SetGraphData` | not called |  |  |  |   |
| `RG_SetROAttribute_Double` | not called |  |  |  |   |
| `RG_SetROAttribute_ISize` | not called |  |  |  |   |
| `RG_SetROAttribute_RGBA` | not called |  |  |  |   |
| `RG_SetROAttribute_String` | not called |  |  |  |   |
| `RG_SetROAttribute_Uint` | not called |  |  |  |   |
| `RG_SetTableCellROAttribute_Double` | not called |  |  |  |   |
| `RG_SetTableCellROAttribute_RGBA` | not called |  |  |  |   |
| `RG_SetTableCellROAttribute_String` | not called |  |  |  |   |
| `RG_SetTableCellROAttribute_Uint` | not called |  |  |  |   |
| `_RG_DBReport` | not called |  |  |  |   |
| `_RG_ManageSharedReports` | not called |  |  |  |   |
| `_RG_NewBlankReport` | not called |  |  |  |   |
| `_RG_NewReportFromTemplate` | not called |  |  |  |   |
| `_RG_NewTemplate` | not called |  |  |  |   |
| `_RG_Open` | not called |  |  |  |   |
| `_RG_OpenReportReadOnly` | not called |  |  |  |   |
| `_RG_Print` | not called |  |  |  |   |

## Image

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `AdjustColorsRGB` | not called |  |  |  |   |
| `ApplyOneShotHDR` | not called |  |  |  |   |
| `AutoContrastEx` | not called |  |  |  |   |
| `AutoContrastExND` | not called |  |  |  |   |
| `AutoWhiteEx` | not called |  |  |  |   |
| `AutoWhiteExND` | not called |  |  |  |   |
| `AutoshadeDirect` | not called |  |  |  |   |
| `ChangeSaturation` | not called |  |  |  |   |
| `CLAHE` | not called |  |  |  |   |
| `ColorToGray` | not called |  |  |  |   |
| `ColorToGrayND` | not called |  |  |  |   |
| `ColorToGrayVSL` | not called |  |  |  |   |
| `ComplementColor` | not called |  |  |  |   |
| `ComponentContrast` | not called |  |  |  |   |
| `ComponentContrastMCh` | not called |  |  |  |   |
| `Contrast` | not called |  |  |  |   |
| `ConvertTo8bitRGB` | not called |  |  |  |   |
| `CRE_EnhanceResonant` | not called |  |  |  |   |
| `DetectModalityBatch` | not called |  |  |  |   |
| `FourierTransformation` | not called |  |  |  |   |
| `GaussLaplaceSharpen` | not called |  |  |  |   |
| `GLPDetails` | not called |  |  |  |   |
| `GuidedSharpen` | not called |  |  |  |   |
| `IntensityTransformation` | not called |  |  |  |   |
| `LocalContrast` | not called |  |  |  |   |
| `RescaleUD_LSkip` | not called |  |  |  |   |
| `TripleQuadInterleave` | not called |  |  |  |   |
| `UnsharpMask` | not called |  |  |  |   |
| `WhiteBalance` | not called |  |  |  |   |
| `_AdjustColorsRGB` | not called |  |  |  |   |
| `_ApplyOneShotHDR` | not called |  |  |  |   |
| `_AutoshadeDirect` | not called |  |  |  |   |
| `_CalibrateInspektis` | not called |  |  |  |   |
| `_CLAHE` | not called |  |  |  |   |
| `_CRE_EnhanceResonant` | not called |  |  |  |   |
| `_ChangeSaturation` | not called |  |  |  |   |
| `_ColorToGray` | not called |  |  |  |   |
| `_ComplementColor` | not called |  |  |  |   |
| `_ComponentContrast` | not called |  |  |  |   |
| `_DetectModality` | not called |  |  |  |   |
| `_FourierTransformation` | not called |  |  |  |   |
| `_GaussLaplaceSharpen` | not called |  |  |  |   |
| `_GLPDetails` | not called |  |  |  |   |
| `_GuidedSharpen` | not called |  |  |  |   |
| `_IntensityTransformation` | not called |  |  |  |   |
| `_LocalContrast` | not called |  |  |  |   |
| `_TripleQuadInterleave` | not called |  |  |  |   |
| `_UnsharpMask` | not called |  |  |  |   |
| `_WhiteBalance` | not called |  |  |  |   |
| `AddLabelToVectorObjects` | not called |  |  |  |   |
| `BringVectorObjectsToFront` | not called |  |  |  |   |
| `CopyVectorObjectsToClipboard` | not called |  |  |  |   |
| `DeselectVectorObjects` | not called |  |  |  |   |
| `EnableVectorObjectsTimeChange` | not called |  |  |  |   |
| `ExportSelectedLineCoordinates` | not called |  |  |  |   |
| `InsertArrow` | not called |  |  |  |   |
| `InsertArrowEx` | not called |  |  |  |   |
| `InsertText` | not called |  |  |  |   |
| `InsertTextEx` | not called |  |  |  |   |
| `LockVectorObjects` | not called |  |  |  |   |
| `PasteVectorObjectsFromClipboard` | not called |  |  |  |   |
| `RemoveSelectedVectorObjects` | not called |  |  |  |   |
| `RemoveVectorObjects` | not called |  |  |  |   |
| `SelectVectorObjects` | not called |  |  |  |   |
| `SendVectorObjectsToBack` | not called |  |  |  |   |
| `SetVectorObjectFramesMethod` | not called |  |  |  |   |
| `SetVectorObjectsCurrentMP` | not called |  |  |  |   |
| `SetVectorObjectsInterpolationMethod` | not called |  |  |  |   |
| `SetVectorObjectsTimeVisEnd` | not called |  |  |  |   |
| `SetVectorObjectsTimeVisStart` | not called |  |  |  |   |
| `ShowVectorObjectProperties` | not called |  |  |  |   |
| `ShowVectorObjectVisibilityProperties` | not called |  |  |  |   |
| `ShowVectorObjectVisibilityPropertiesEx` | not called |  |  |  |   |
| `ToggleAnnotations` | not called |  |  |  |   |
| `VectorObjectContextCommand` | not called |  |  |  |   |
| `_InsertArrow` | not called |  |  |  |   |
| `_InsertText` | not called |  |  |  |   |
| `CreatePictureEx` | not called |  |  |  |   |
| `StretchBlt` | not called |  |  |  |   |
| `StretchBltRGB` | not called |  |  |  |   |
| `BurnScale` | not called |  |  |  |   |
| `BurnScaleND` | not called |  |  |  |   |
| `BurnVectorObjects` | not called |  |  |  |   |
| `CreateDocumentAsSliceViewProjection` | not called |  |  |  |   |
| `CreateDocumentAsSliceViewProjectionUnscaled` | not called |  |  |  |   |
| `CreateViewSnapshot` | not called |  |  |  |   |
| `CreateViewSnapshotFull` | not called |  |  |  |   |
| `CreateViewSnapshotFullND` | not called |  |  |  |   |
| `CreateViewSnapshotND` | not called |  |  |  |   |
| `InsertOverlay` | not called |  |  |  |   |
| `InsertOverlayND` | not called |  |  |  |   |
| `InsertScale` | not called |  |  |  |   |
| `InsertScaleEx` | not called |  |  |  |   |
| `_BurnScale` | not called |  |  |  |   |
| `_BurnScaleND` | not called |  |  |  |   |
| `_BurnSpectralBar` | not called |  |  |  |   |
| `_CreateMontageView` | not called |  |  |  |   |
| `_CreateViewSnapshotFullND` | not called |  |  |  |   |
| `_CreateViewSnapshotInRect` | not called |  |  |  |   |
| `_CreateViewSnapshotND` | not called |  |  |  |   |
| `_InsertOverlayND` | not called |  |  |  |   |
| `BlindUnmixing` | not called |  |  |  |   |
| `ChangeChannelColor` | not called |  |  |  |   |
| `ChangeChannelDescription` | not called |  |  |  |   |
| `ExtractComponents` | not called |  |  |  |   |
| `ExtractSelectedComponents` | not called |  |  |  |   |
| `ExtractSelectedComponentsAsFloat` | not called |  |  |  |   |
| `GetChannelName` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetChannelPropertiesEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetViewComponents` | needs arguments | error: Bad number of parameters |  |  |   |
| `KeepSelectedChannels` | not called |  |  |  |   |
| `MergeImagePlanes` | not called |  |  |  |   |
| `PasteIntoChannel` | not called |  |  |  |   |
| `PasteIntoSelectedChannel` | not called |  |  |  |   |
| `ProcessBlue` | not called |  |  |  |   |
| `ProcessGreen` | not called |  |  |  |   |
| `ProcessRGB` | not called |  |  |  |   |
| `ProcessRed` | not called |  |  |  |   |
| `ProcessViewComponent` | not called |  |  |  |   |
| `RemoveChannel` | not called |  |  |  |   |
| `ReorderChannels` | not called |  |  |  |   |
| `SetChannelProperties` | not called |  |  |  |   |
| `SetChannelPropertiesEx` | not called |  |  |  |   |
| `SetSelectedChannelsAsCustom` | not called |  |  |  |   |
| `SpectralImageRepresentation` | not called |  |  |  |   |
| `ToggleChannelInColor` | not called |  |  |  |   |
| `ToggleSpectralImageRepresentation` | not called |  |  |  |   |
| `UnMix` | not called |  |  |  |   |
| `UnMixND` | not called |  |  |  |   |
| `VAASImageRepresentation` | not called |  |  |  |   |
| `ViewAllComponents` | not called |  |  |  |   |
| `ViewBlue` | not called |  |  |  |   |
| `ViewChannel` | not called |  |  |  |   |
| `ViewChannelInColor` | not called |  |  |  |   |
| `ViewComponentText` | not called |  |  |  |   |
| `ViewComponents` | not called |  |  |  |   |
| `ViewCustomChannel` | not called |  |  |  |   |
| `ViewGreen` | not called |  |  |  |   |
| `ViewHDR` | not called |  |  |  |   |
| `ViewRGB` | not called |  |  |  |   |
| `ViewRed` | not called |  |  |  |   |
| `XViewComponent` | not called |  |  |  |   |
| `_BlindUnmixing` | not called |  |  |  |   |
| `_ChangeChannelColor` | not called |  |  |  |   |
| `_ChangeChannelDescription` | not called |  |  |  |   |
| `_ChannelProperties` | not called |  |  |  |   |
| `_CustomChannelProperties` | not called |  |  |  |   |
| `_ManageStoredSpectra` | not called |  |  |  |   |
| `_MergeImagePlanes` | not called |  |  |  |   |
| `_ReorderChannels` | not called |  |  |  |   |
| `_UnMix` | not called |  |  |  |   |
| `_UnMixND` | not called |  |  |  |   |
| `Copy` | not called |  |  |  |   |
| `CopyBinary` | not called |  |  |  |   |
| `CopySelect` | not called |  |  |  |   |
| `CopySelectEx` | not called |  |  |  |   |
| `Paste` | not called |  |  |  |   |
| `PasteBinary` | not called |  |  |  |   |
| `PasteBrightfield` | not called |  |  |  |   |
| `PasteChannels` | not called |  |  |  |   |
| `PasteRectangle` | not called |  |  |  |   |
| `PasteWithName` | not called |  |  |  |   |
| `_CopySelect` | not called |  |  |  |   |
| `_CopySelectEx` | not called |  |  |  |   |
| `_Paste` | not called |  |  |  |   |
| `_PasteBrightfield` | not called |  |  |  |   |
| `_PasteChannels` | not called |  |  |  |   |
| `_PasteKeepAspect` | not called |  |  |  |   |
| `_PasteRectangle` | not called |  |  |  |   |
| `_PasteSelect` | not called |  |  |  |   |
| `AddNewComponent` | not called |  |  |  |   |
| `AdjustImage` | not called |  |  |  |   |
| `AdjustImageForSave` | not called |  |  |  |   |
| `ChangeColorDepth` | not called |  |  |  |   |
| `ChangeColorDepthND` | not called |  |  |  |   |
| `ChangeColorDepthVSL` | not called |  |  |  |   |
| `ConvertBinaryToColorComponent` | not called |  |  |  |   |
| `ConvertFloatToPic` | not called |  |  |  |   |
| `ConvertIHStoRGB` | not called |  |  |  |   |
| `ConvertRGBtoIHS` | not called |  |  |  |   |
| `ConvertRGBtoLab` | not called |  |  |  |   |
| `ConvertRGBtoXYZ` | not called |  |  |  |   |
| `ConvertTo8bitRGBVSL` | not called |  |  |  |   |
| `ConvertToFloatPic` | not called |  |  |  |   |
| `ConvertToMCH` | not called |  |  |  |   |
| `ConvertToMCHND` | not called |  |  |  |   |
| `ConvertToRGB` | not called |  |  |  |   |
| `ConvertToRGBND` | not called |  |  |  |   |
| `ConvertToRGBVSL` | not called |  |  |  |   |
| `CopyChannels` | not called |  |  |  |   |
| `Extract` | not called |  |  |  |   |
| `ExtractComponent` | not called |  |  |  |   |
| `VAASOffline` | not called |  |  |  |   |
| `_AddNewComponent` | not called |  |  |  |   |
| `_AdjustImageForSave` | not called |  |  |  |   |
| `_ChangeColorDepth` | not called |  |  |  |   |
| `_ConvertFloatToPic` | not called |  |  |  |   |
| `_ConvertToMCH` | not called |  |  |  |   |
| `_ConvertToRGB` | not called |  |  |  |   |
| `_Extract` | not called |  |  |  |   |
| `_VAASOffline` | not called |  |  |  |   |
| `_VAASOnline` | not called |  |  |  |   |
| `ClearAllOverlays` | not called |  |  |  |   |
| `ClearAnnotations` | not called |  |  |  |   |
| `ClearColor` | not called |  |  |  |   |
| `ClearColorND` | not called |  |  |  |   |
| `_ClearColor` | not called |  |  |  |   |
| `ExportAscii` | not called |  |  |  |   |
| `ExportImageProperties` | not called |  |  |  |   |
| `_ExportAscii` | not called |  |  |  |   |
| `FlipHorizontally` | not called |  |  |  |   |
| `FlipHorizontallyND` | not called |  |  |  |   |
| `FlipVertically` | not called |  |  |  |   |
| `FlipVerticallyND` | not called |  |  |  |   |
| `_FlipHorizontally` | not called |  |  |  |   |
| `_FlipVertically` | not called |  |  |  |   |
| `LinCloseColor` | not called |  |  |  |   |
| `LinCloseColorGa3` | not called |  |  |  |   |
| `LinDilateColor` | not called |  |  |  |   |
| `LinDilateColorGa3` | not called |  |  |  |   |
| `LinErodeColor` | not called |  |  |  |   |
| `LinErodeColorGa3` | not called |  |  |  |   |
| `LinOpenColor` | not called |  |  |  |   |
| `LinOpenColorGa3` | not called |  |  |  |   |
| `_LinCloseColor` | not called |  |  |  |   |
| `_LinCloseColorGa3` | not called |  |  |  |   |
| `_LinDilateColor` | not called |  |  |  |   |
| `_LinDilateColorGa3` | not called |  |  |  |   |
| `_LinErodeColor` | not called |  |  |  |   |
| `_LinErodeColorGa3` | not called |  |  |  |   |
| `_LinOpenColor` | not called |  |  |  |   |
| `_LinOpenColorGa3` | not called |  |  |  |   |
| `CloseColor` | not called |  |  |  |   |
| `CloseColorGa3` | not called |  |  |  |   |
| `DetectDICObjects` | not called |  |  |  |   |
| `DetectDICObjectsGa3` | not called |  |  |  |   |
| `DetectPeaks` | not called |  |  |  |   |
| `DetectValleys` | not called |  |  |  |   |
| `MorphoGradientEx` | not called |  |  |  |   |
| `MorphoGradientExGa3` | not called |  |  |  |   |
| `OpenColor` | not called |  |  |  |   |
| `OpenColorGa3` | not called |  |  |  |   |
| `_CloseColor` | not called |  |  |  |   |
| `_CloseColorGa3` | not called |  |  |  |   |
| `_DetectDICObjects` | not called |  |  |  |   |
| `_DetectDICObjectsGa3` | not called |  |  |  |   |
| `_DetectPeaks` | not called |  |  |  |   |
| `_DetectValleys` | not called |  |  |  |   |
| `_ChangeProcessParameters` | not called |  |  |  |   |
| `_MorphoGradientEx` | not called |  |  |  |   |
| `_MorphoGradientExGa3` | not called |  |  |  |   |
| `_OpenColor` | not called |  |  |  |   |
| `_OpenColorGa3` | not called |  |  |  |   |
| `Convert_ai` | not called |  |  |  |   |
| `Convert3d_ai` | not called |  |  |  |   |
| `CreateTrainedFileDBRecord` | not called |  |  |  |   |
| `Denoise_ai` | not called |  |  |  |   |
| `Enhance_ai` | not called |  |  |  |   |
| `Enhance3d_ai` | not called |  |  |  |   |
| `Restore_ai` | not called |  |  |  |   |
| `NDDenoise_ai` | not called |  |  |  |   |
| `RunDistributedItem` | not called |  |  |  |   |
| `RunDistributedItems` | not called |  |  |  |   |
| `RunQueuedItem` | not called |  |  |  |   |
| `RunQueuedItems` | not called |  |  |  |   |
| `Segment_ai` | not called |  |  |  |   |
| `Segment3d_ai` | not called |  |  |  |   |
| `SegmentObjects_ai` | not called |  |  |  |   |
| `SegmentObjects3d_ai` | not called |  |  |  |   |
| `StartMxExecutor` | not called |  |  |  |   |
| `Train_Convert_ai` | not called |  |  |  |   |
| `Train_Convert3d_ai` | not called |  |  |  |   |
| `Train_Enhance_ai` | not called |  |  |  |   |
| `Train_Enhance3d_ai` | not called |  |  |  |   |
| `Train_Segment_ai` | not called |  |  |  |   |
| `Train_Segment3d_ai` | not called |  |  |  |   |
| `Train_SegmentObjects_ai` | not called |  |  |  |   |
| `Train_SegmentObjects3d_ai` | not called |  |  |  |   |
| `_Clarify_ai` | not called |  |  |  |   |
| `_Convert3d_ai` | not called |  |  |  |   |
| `_Convert_ai` | not called |  |  |  |   |
| `_Denoise_ai` | not called |  |  |  |   |
| `_Enhance3d_ai` | not called |  |  |  |   |
| `_Enhance_ai` | not called |  |  |  |   |
| `_Explorer_ai` | not called |  |  |  |   |
| `_NDDenoise_ai` | not called |  |  |  |   |
| `_Restore_ai` | not called |  |  |  |   |
| `_Segment3d_ai` | not called |  |  |  |   |
| `_Segment_ai` | not called |  |  |  |   |
| `_SegmentObjects3d_ai` | not called |  |  |  |   |
| `_SegmentObjects_ai` | not called |  |  |  |   |
| `_Train_Convert3d_ai` | not called |  |  |  |   |
| `_Train_Convert_ai` | not called |  |  |  |   |
| `_Train_Enhance3d_ai` | not called |  |  |  |   |
| `_Train_Enhance_ai` | not called |  |  |  |   |
| `_Train_Segment3d_ai` | not called |  |  |  |   |
| `_Train_Segment_ai` | not called |  |  |  |   |
| `_Train_SegmentObjects3d_ai` | not called |  |  |  |   |
| `_Train_SegmentObjects_ai` | not called |  |  |  |   |
| `AdvancedDenoising` | not called |  |  |  |   |
| `AdvancedDenoisingSimple` | not called |  |  |  |   |
| `AdvancedDenoisingSimpleEx` | not called |  |  |  |   |
| `AXShadingCorrectionGa3` | not called |  |  |  |   |
| `BackgroundSubtraction` | not called |  |  |  |   |
| `CannyDetector` | not called |  |  |  |   |
| `ChangeHue` | not called |  |  |  |   |
| `ContrastGa3` | not called |  |  |  |   |
| `Correlation` | not called |  |  |  |   |
| `CorrelationND` | not called |  |  |  |   |
| `Delineate` | not called |  |  |  |   |
| `DenoiseAnisotrophic` | not called |  |  |  |   |
| `DestripeGa3` | not called |  |  |  |   |
| `DetectPeaksGa3` | not called |  |  |  |   |
| `DetectValleysGa3` | not called |  |  |  |   |
| `DifSubsequentFramesTime` | not called |  |  |  |   |
| `DifSubsequentFramesZ` | not called |  |  |  |   |
| `DilateColor` | not called |  |  |  |   |
| `DilateColorGa3` | not called |  |  |  |   |
| `DivideComponents` | not called |  |  |  |   |
| `EdgesDetect` | not called |  |  |  |   |
| `EdgesDetectGa3` | not called |  |  |  |   |
| `EqualizeIntensity` | not called |  |  |  |   |
| `EqualizeIntensityTime` | not called |  |  |  |   |
| `EqualizeIntensityTimeEx` | not called |  |  |  |   |
| `EqualizeIntensityXY` | not called |  |  |  |   |
| `EqualizeIntensityXYEx` | not called |  |  |  |   |
| `EqualizeIntensityZ` | not called |  |  |  |   |
| `EqualizeIntensityZEx` | not called |  |  |  |   |
| `ErodeColor` | not called |  |  |  |   |
| `ErodeColorGa3` | not called |  |  |  |   |
| `FastDenoising` | not called |  |  |  |   |
| `FluorescenceUnmixingGa3` | not called |  |  |  |   |
| `GaborResponse` | not called |  |  |  |   |
| `GaborResponseGa3` | not called |  |  |  |   |
| `GaussLaplaceSharpenGa3` | not called |  |  |  |   |
| `GeneralConvolution` | not called |  |  |  |   |
| `GolayFilter` | not called |  |  |  |   |
| `GolayFilterGa3` | not called |  |  |  |   |
| `Homogenization` | not called |  |  |  |   |
| `HorizontalEdges` | not called |  |  |  |   |
| `Laplace4` | not called |  |  |  |   |
| `Laplace4Ga3` | not called |  |  |  |   |
| `Laplace8` | not called |  |  |  |   |
| `Laplace8Ga3` | not called |  |  |  |   |
| `LocalContrastGa3` | not called |  |  |  |   |
| `LowPassFilterFFT` | not called |  |  |  |   |
| `LowPassFilterFFTGa3` | not called |  |  |  |   |
| `Median` | not called |  |  |  |   |
| `MedianGa3` | not called |  |  |  |   |
| `MergeOpenedDocuments` | not called |  |  |  |   |
| `MexicanHat` | not called |  |  |  |   |
| `MexicanHatGa3` | not called |  |  |  |   |
| `MexicanHatEx` | not called |  |  |  |   |
| `MixComponents` | not called |  |  |  |   |
| `ND_AutoShadingCorrectionGa3` | not called |  |  |  |   |
| `NDAverage` | not called |  |  |  |   |
| `ProcessChannel` | not called |  |  |  |   |
| `ProcessChannelGa3` | not called |  |  |  |   |
| `RGBTransformation` | not called |  |  |  |   |
| `ReduceLowResData` | not called |  |  |  |   |
| `RegionalMaxima` | not called |  |  |  |   |
| `RegionalMaximaGa3` | not called |  |  |  |   |
| `RegionalMinima` | not called |  |  |  |   |
| `RegionalMinimaGa3` | not called |  |  |  |   |
| `Relief` | not called |  |  |  |   |
| `RollingBallCorrection` | not called |  |  |  |   |
| `RollingBallCorrectionGa3` | not called |  |  |  |   |
| `SetPreprocessOnRGB` | not called |  |  |  |   |
| `ShadingCorrection` | not called |  |  |  |   |
| `ShadingCorrectionGa3` | not called |  |  |  |   |
| `ShadingCorrectionUnderROI` | not called |  |  |  |   |
| `Sharpen` | not called |  |  |  |   |
| `SharpenGa3` | not called |  |  |  |   |
| `SharpenMore` | not called |  |  |  |   |
| `SharpenMoreGa3` | not called |  |  |  |   |
| `SharpenSlightly` | not called |  |  |  |   |
| `SharpenSlightlyGa3` | not called |  |  |  |   |
| `Smooth` | not called |  |  |  |   |
| `SmoothGa3` | not called |  |  |  |   |
| `SubtractAvgTime` | not called |  |  |  |   |
| `SubtractAvgZ` | not called |  |  |  |   |
| `SubtractBackgroundUsingConstantGa3` | not called |  |  |  |   |
| `SubtractMaxIntensityTime` | not called |  |  |  |   |
| `SubtractMaxIntensityZ` | not called |  |  |  |   |
| `SubtractMinIntensityTime` | not called |  |  |  |   |
| `SubtractMinIntensityZ` | not called |  |  |  |   |
| `SubtractSubsequentFramesTime` | not called |  |  |  |   |
| `SubtractSubsequentFramesZ` | not called |  |  |  |   |
| `SubtractWhite` | not called |  |  |  |   |
| `SubtractWhiteND` | not called |  |  |  |   |
| `TogglePreprocessOnRGB` | not called |  |  |  |   |
| `UnsharpMaskGa3` | not called |  |  |  |   |
| `VerticalEdges` | not called |  |  |  |   |
| `_AdvancedDenoising` | not called |  |  |  |   |
| `_AXShadingCorrectionGa3` | not called |  |  |  |   |
| `_BackgroundSubtraction` | not called |  |  |  |   |
| `_CannyDetector` | not called |  |  |  |   |
| `_ContrastGa3` | not called |  |  |  |   |
| `_ChangeHue` | not called |  |  |  |   |
| `_Delineate` | not called |  |  |  |   |
| `_Destripe` | not called |  |  |  |   |
| `_DestripeGa3` | not called |  |  |  |   |
| `_DetectPeaksGa3` | not called |  |  |  |   |
| `_DetectValleysGa3` | not called |  |  |  |   |
| `_DilateColor` | not called |  |  |  |   |
| `_DilateColorGa3` | not called |  |  |  |   |
| `_DivideComponents` | not called |  |  |  |   |
| `_EdgesDetect` | not called |  |  |  |   |
| `_EdgesDetectGa3` | not called |  |  |  |   |
| `_EqualizeIntensityTime` | not called |  |  |  |   |
| `_EqualizeIntensityXY` | not called |  |  |  |   |
| `_EqualizeIntensityZ` | not called |  |  |  |   |
| `_ErodeColor` | not called |  |  |  |   |
| `_ErodeColorGa3` | not called |  |  |  |   |
| `_FastDenoising` | not called |  |  |  |   |
| `_FluorescenceUnmixingGa3` | not called |  |  |  |   |
| `_GaborResponse` | not called |  |  |  |   |
| `_GaborResponseGa3` | not called |  |  |  |   |
| `_GaussLaplaceSharpenGa3` | not called |  |  |  |   |
| `_GeneralConvolution` | not called |  |  |  |   |
| `_GolayFilter` | not called |  |  |  |   |
| `_GolayFilterGa3` | not called |  |  |  |   |
| `_Homogenization` | not called |  |  |  |   |
| `_HorizontalEdges` | not called |  |  |  |   |
| `_Laplace4` | not called |  |  |  |   |
| `_Laplace4Ga3` | not called |  |  |  |   |
| `_Laplace8` | not called |  |  |  |   |
| `_Laplace8Ga3` | not called |  |  |  |   |
| `_LocalContrastGa3` | not called |  |  |  |   |
| `_LowPassFilterFFT` | not called |  |  |  |   |
| `_LowPassFilterFFTGa3` | not called |  |  |  |   |
| `_Median` | not called |  |  |  |   |
| `_MedianGa3` | not called |  |  |  |   |
| `_MexicanHat` | not called |  |  |  |   |
| `_MexicanHatGa3` | not called |  |  |  |   |
| `_MixComponents` | not called |  |  |  |   |
| `_ND_AutoShadingCorrectionGa3` | not called |  |  |  |   |
| `_NDAverage` | not called |  |  |  |   |
| `_ND_ConvertExperiment` | not called |  |  |  |   |
| `_NDImagesArithmetics` | not called |  |  |  |   |
| `_PatchDenoising3D` | not called |  |  |  |   |
| `_ReduceLowResData` | not called |  |  |  |   |
| `_RGBTransformation` | not called |  |  |  |   |
| `_RegionalMaxima` | not called |  |  |  |   |
| `_RegionalMaximaGa3` | not called |  |  |  |   |
| `_RegionalMinima` | not called |  |  |  |   |
| `_RegionalMinimaGa3` | not called |  |  |  |   |
| `_RegistrationWizard` | not called |  |  |  |   |
| `_Relief` | not called |  |  |  |   |
| `_RollingBallCorrection` | not called |  |  |  |   |
| `_RollingBallCorrectionGa3` | not called |  |  |  |   |
| `_ShadingCorrection` | not called |  |  |  |   |
| `_ShadingCorrectionGa3` | not called |  |  |  |   |
| `_ShadingCorrectionUnderROI` | not called |  |  |  |   |
| `_SharpenGa3` | not called |  |  |  |   |
| `_SharpenMore` | not called |  |  |  |   |
| `_SharpenMoreGa3` | not called |  |  |  |   |
| `_SharpenSlightly` | not called |  |  |  |   |
| `_SharpenSlightlyGa3` | not called |  |  |  |   |
| `_Smooth` | not called |  |  |  |   |
| `_SmoothGa3` | not called |  |  |  |   |
| `_SubtractBackgroundUsingConstantGa3` | not called |  |  |  |   |
| `_SubtractWhite` | not called |  |  |  |   |
| `_UnsharpMaskGa3` | not called |  |  |  |   |
| `_VerticalEdges` | not called |  |  |  |   |
| `Region_Accepted_Binary` | not called |  |  |  |   |
| `Region_Copy` | not called |  |  |  |   |
| `Region_Cut` | not called |  |  |  |   |
| `Region_Cut_RGB` | not called |  |  |  |   |
| `Region_Info` | not called |  |  |  |   |
| `Region_Paste` | not called |  |  |  |   |
| `Region_Settings` | not called |  |  |  |   |
| `Region_Settings_RGB` | not called |  |  |  |   |
| `_AutoDetect_Copy` | not called |  |  |  |   |
| `_AutoDetect_Cut` | not called |  |  |  |   |
| `_Circle_Copy` | not called |  |  |  |   |
| `_Circle_Cut` | not called |  |  |  |   |
| `_Region_Accepted` | not called |  |  |  |   |
| `_Region_Accepted_Binary` | not called |  |  |  |   |
| `_Region_Copy` | not called |  |  |  |   |
| `_Region_Cut` | not called |  |  |  |   |
| `_Region_Paste` | not called |  |  |  |   |
| `_Region_Settings` | not called |  |  |  |   |
| `ImageRegistration` | not called |  |  |  |   |
| `_ImageRegistration` | not called |  |  |  |   |
| `Rotate` | not called |  |  |  |   |
| `RotateGrow` | not called |  |  |  |   |
| `RotateGrowND` | not called |  |  |  |   |
| `RotateInCenter` | not called |  |  |  |   |
| `RotateLeft` | not called |  |  |  |   |
| `RotateLeftND` | not called |  |  |  |   |
| `RotateLevelHor` | not called |  |  |  |   |
| `RotateLevelVer` | not called |  |  |  |   |
| `RotateND` | not called |  |  |  |   |
| `RotateRect` | not called |  |  |  |   |
| `RotateRectND` | not called |  |  |  |   |
| `RotateRight` | not called |  |  |  |   |
| `RotateRightND` | not called |  |  |  |   |
| `_Rotate` | not called |  |  |  |   |
| `_RotateLeft` | not called |  |  |  |   |
| `_RotateRect` | not called |  |  |  |   |
| `_RotateRight` | not called |  |  |  |   |
| `GetScalePos` | needs arguments | error: Bad number of parameters |  |  |   |
| `SetScalePos` | not called |  |  |  |   |
| `Sequences` | not called |  |  |  |   |
| `SequencesEx` | not called |  |  |  |   |
| `_Sequences` | not called |  |  |  |   |
| `AlignChannels` | not called |  |  |  |   |
| `AlignChannelsLow` | not called |  |  |  |   |
| `AlignChannelsOnBeads` | not called |  |  |  |   |
| `ShiftDown` | not called |  |  |  |   |
| `ShiftDownND` | not called |  |  |  |   |
| `ShiftImage` | not called |  |  |  |   |
| `ShiftImageND` | not called |  |  |  |   |
| `ShiftLeft` | not called |  |  |  |   |
| `ShiftLeftND` | not called |  |  |  |   |
| `ShiftRight` | not called |  |  |  |   |
| `ShiftRightND` | not called |  |  |  |   |
| `ShiftSubPixel` | not called |  |  |  |   |
| `ShiftSubPixelND` | not called |  |  |  |   |
| `ShiftSubPixelZ` | not called |  |  |  |   |
| `ShiftUp` | not called |  |  |  |   |
| `ShiftUpND` | not called |  |  |  |   |
| `_AlignChannels` | not called |  |  |  |   |
| `_AlignChannelsOnBeads` | not called |  |  |  |   |
| `_ShiftDown` | not called |  |  |  |   |
| `_ShiftLeft` | not called |  |  |  |   |
| `_ShiftRight` | not called |  |  |  |   |
| `_ShiftSubPixel` | not called |  |  |  |   |
| `_ShiftSubPixelZ` | not called |  |  |  |   |
| `_ShiftUp` | not called |  |  |  |   |
| `AddImageBorders` | not called |  |  |  |   |
| `AddImageBordersND` | not called |  |  |  |   |
| `CanvasSize` | not called |  |  |  |   |
| `CanvasSizeND` | not called |  |  |  |   |
| `ImageBinning` | not called |  |  |  |   |
| `ImageBinningND` | not called |  |  |  |   |
| `ImageCrop` | not called |  |  |  |   |
| `ImageCropND` | not called |  |  |  |   |
| `ImageCropVSL` | not called |  |  |  |   |
| `ImageResize` | not called |  |  |  |   |
| `ImageResizeForExport` | not called |  |  |  |   |
| `ImageResizeND` | not called |  |  |  |   |
| `ImageResizeVSL` | not called |  |  |  |   |
| `RadonTransform` | not called |  |  |  |   |
| `RadonTransformND` | not called |  |  |  |   |
| `SetRescalingMethod` | not called |  |  |  |   |
| `_AddImageBorders` | not called |  |  |  |   |
| `_CanvasSize` | not called |  |  |  |   |
| `_ImageBinning` | not called |  |  |  |   |
| `_ImageCrop` | not called |  |  |  |   |
| `_ImageCropEx` | not called |  |  |  |   |
| `_ImageCropProj` | not called |  |  |  |   |
| `_ImageResize` | not called |  |  |  |   |
| `_ImageResizeForExport` | not called |  |  |  |   |
| `_RadonTransform` | not called |  |  |  |   |
| `RestoreColorToOrigin` | not called |  |  |  |   |
| `UndoColor` | not called |  |  |  |   |
| `UndoNext` | not called |  |  |  |   |
| `UndoPrev` | not called |  |  |  |   |
| `UndoPurge` | not called |  |  |  |   |
| `UndoSelect` | not called |  |  |  |   |
| `UndoSwap` | not called |  |  |  |   |
| `_UndoHistory` | not called |  |  |  |   |
| `ColorBinCombine` | not called |  |  |  |   |
| `ColorBinCombineND` | not called |  |  |  |   |
| `ColorCombine` | not called |  |  |  |   |
| `ColorCombineND` | not called |  |  |  |   |
| `ColorFromReference` | not called |  |  |  |   |
| `ColorOperations` | not called |  |  |  |   |
| `ColorOperationsND` | not called |  |  |  |   |
| `ColorSwapReference` | not called |  |  |  |   |
| `ColorToReference` | not called |  |  |  |   |
| `StretchToReference` | not called |  |  |  |   |
| `WeightedAddition` | not called |  |  |  |   |
| `WeightedAdditionND` | not called |  |  |  |   |
| `_ColorBinCombine` | not called |  |  |  |   |
| `_ColorCombine` | not called |  |  |  |   |
| `_ColorOperations` | not called |  |  |  |   |
| `_WeightedAddition` | not called |  |  |  |   |
| `GetYeastFocusCtiterion` | crashed or hung | NIS crashed or hung in this call; the run was started again after it |  |  |   |
| `ImageOperations` | not called |  |  |  |   |
| `_HighLightImage` | not called |  |  |  |   |
| `_ImageOperations` | not called |  |  |  |   |
| `_PolarImage` | not called |  |  |  |   |

## ImageDocument

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `ActivateDocument` | not called |  |  |  |   |
| `GetOpenedDocumentList` | needs arguments | error: Bad number of parameters |  |  |   |
| `NextOpenedDocument` | not called |  |  |  |   |
| `PrevOpenedDocument` | not called |  |  |  |   |
| `ShowOpenedDocument` | not called |  |  |  |   |
| `ImageAttachmentRemove` | not called |  |  |  |   |
| `_ImageAttachmentAdd` | not called |  |  |  |   |
| `_ImageAttachmentOpen` | not called |  |  |  |   |
| `_ImageAttachmentSaveAs` | not called |  |  |  |   |
| `CloseAllDocuments` | not called |  |  |  |   |
| `CloseAllDocumentsButCurrent` | not called |  |  |  |   |
| `CloseCurrentDocument` | not called |  |  |  |   |
| `_CloseAllDocuments` | not called |  |  |  |   |
| `_CloseAllDocumentsButCurrent` | not called |  |  |  |   |
| `_CloseCurrentDocument` | not called |  |  |  |   |
| `DeleteCurrentImage` | not called |  |  |  |   |
| `_DeleteCurrentImage` | not called |  |  |  |   |
| `AddImageTag` | not called |  |  |  |   |
| `Get_ImageInfo` | needs arguments | error: Bad number of parameters |  |  |   |
| `LoadImageDescription` | not called |  |  |  |   |
| `LoadImageFullDescription` | not called |  |  |  |   |
| `SaveImageDescription` | not called |  |  |  |   |
| `SaveImageFullDescription` | not called |  |  |  |   |
| `_ImageDescription` | not called |  |  |  |   |
| `DigitalSigning_SetSigningThumbprint` | not called |  |  |  |   |
| `_DigitalSigning_CaptureImageToPdf` | not called |  |  |  |   |
| `_DigitalSigning_SelectSigningCertificate` | not called |  |  |  |   |
| `DuplicateDocument` | not called |  |  |  |   |
| `_DuplicateDocument` | not called |  |  |  |   |
| `NewDocumentBin` | not called |  |  |  |   |
| `NewDocumentMono` | not called |  |  |  |   |
| `NewDocumentRGB` | not called |  |  |  |   |
| `_BinaryNew` | not called |  |  |  |   |
| `_ImageNew` | not called |  |  |  |   |
| `_ReopenProgressiveAsDownsampled` | not called |  |  |  |   |
| `EnableDetectSequence` | not called |  |  |  |   |
| `ImageOpen` | not called |  |  |  |   |
| `OpenDocument` | not called |  |  |  |   |
| `OpenDocument2` | not called |  |  |  |   |
| `OpenDocument2_SetParams_Downsample` | not called |  |  |  |   |
| `OpenDocument2_SetParams_Exp` | not called |  |  |  |   |
| `OpenDocumentSerie` | not called |  |  |  |   |
| `OpenDownsampledLargeImage` | not called |  |  |  |   |
| `OpenDownsampledLargeImageEx` | not called |  |  |  |   |
| `OpenLargeImage` | not called |  |  |  |   |
| `SnippingTool` | not called |  |  |  |   |
| `_ImageOpen` | not called |  |  |  |   |
| `_OpenLargeImageProgVsSplit` | not called |  |  |  |   |
| `_OpenLargeImageSplit` | not called |  |  |  |   |
| `ImageOpenFirst` | not called |  |  |  |   |
| `ImageOpenLast` | not called |  |  |  |   |
| `ImageOpenNext` | not called |  |  |  |   |
| `ImageOpenPrevious` | not called |  |  |  |   |
| `OpenNext_LimitDocuments` | not called |  |  |  |   |
| `OpenNext_SetNum` | not called |  |  |  |   |
| `OpenNext_Sort` | not called |  |  |  |   |
| `OpenNext_SourceImages` | not called |  |  |  |   |
| `_ImageOpenFirst` | not called |  |  |  |   |
| `_ImageOpenLast` | not called |  |  |  |   |
| `_ImageOpenNext` | not called |  |  |  |   |
| `_ImageOpenPrevious` | not called |  |  |  |   |
| `_ImageOpenSettings` | not called |  |  |  |   |
| `_OpenNext_SetNum` | not called |  |  |  |   |
| `ImagePrint` | not called |  |  |  |   |
| `PrintPage` | not called |  |  |  |   |
| `AddUndoImage` | not called |  |  |  |   |
| `DisplayCurrentPicture` | not called |  |  |  |   |
| `GetPixelValue` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetPixelValueEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `SetPixelValue` | not called |  |  |  |   |
| `SetPixelValueEx` | not called |  |  |  |   |
| `ImageReload` | not called |  |  |  |   |
| `RestoreCurrentDocument` | not called |  |  |  |   |
| `_ImageReload` | not called |  |  |  |   |
| `ImageExportToAVI` | not called |  |  |  |   |
| `ImageSave` | not called |  |  |  |   |
| `ImageSaveAs` | not called |  |  |  |   |
| `ImageSaveAsEx` | not called |  |  |  |   |
| `SaveAll` | not called |  |  |  |   |
| `SaveCurrentDocument` | not called |  |  |  |   |
| `ShowImageInfoBeforeSaveAs` | not called |  |  |  |   |
| `_ImageSave` | not called |  |  |  |   |
| `_ImageSaveAs` | not called |  |  |  |   |
| `ImageSaveNext` | not called |  |  |  |   |
| `ImageSaveNextSuppressDialog` | not called |  |  |  |   |
| `SaveNext_ImageInfo` | not called |  |  |  |   |
| `SaveNext_Images` | not called |  |  |  |   |
| `SaveNext_SetNumber` | not called |  |  |  |   |
| `UndoSaveNext` | not called |  |  |  |   |
| `_ImageSaveNextSettings` | not called |  |  |  |   |
| `SendMail` | not called |  |  |  |   |
| `_SendMail` | not called |  |  |  |   |
| `ReduceNumberOfDocuments` | not called |  |  |  |   |
| `SetCaptureCreatesNewDoc` | not called |  |  |  |   |
| `SetMaxMemoryImageSize` | not called |  |  |  |   |
| `SetShowMappingDlg` | not called |  |  |  |   |
| `SetUseAutoLUTs` | not called |  |  |  |   |
| `SetUseLastLUTs` | not called |  |  |  |   |
| `SetUsedFixPathForFiles` | not called |  |  |  |   |
| `SetUsedFixPathForMacros` | not called |  |  |  |   |
| `UseSingleUndo` | not called |  |  |  |   |
| `CascadeAllWindows` | not called |  |  |  |   |
| `MaximizeCurrentDocument` | not called |  |  |  |   |
| `MinimizeCurrentDocument` | not called |  |  |  |   |
| `SetSingleWindow` | not called |  |  |  |   |
| `TileHorWindows` | not called |  |  |  |   |
| `TileVertWindows` | not called |  |  |  |   |
| `AppendFile` | not called |  |  |  |   |
| `Convert_Files` | not called |  |  |  |   |
| `CopyFile` | not called |  |  |  |   |
| `DeleteFile` | not called |  |  |  |   |
| `DeleteFileQuery` | not called |  |  |  |   |
| `EditFile` | not called |  |  |  |   |
| `ExistFile` | not called |  |  |  |   |
| `FindFiles` | not called |  |  |  |   |
| `GetFreeDiskSpace` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetOpenSaveFileName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_FileSize` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_FileTitle` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_Filename` | needs arguments | error: Bad number of parameters |  |  |   |
| `MakeDirectory` | not called |  |  |  |   |
| `OpenAsciiFile` | not called |  |  |  |   |
| `ReadFile` | not called |  |  |  |   |
| `ReadFileEx` | not called |  |  |  |   |
| `RenameFile` | not called |  |  |  |   |
| `SaveImageTextInfo` | not called |  |  |  |   |
| `SelectFile` | not called |  |  |  |   |
| `SelectImage` | not called |  |  |  |   |
| `TraceToLogFile` | not called |  |  |  |   |
| `WriteFile` | not called |  |  |  |   |
| `_Convert_Files` | not called |  |  |  |   |
| `_MakeDirectory` | not called |  |  |  |   |
| `_SendFile` | not called |  |  |  |   |
| `GetFileAbsTime` | ran | -1.0 |  |  |   |
| `ImageReuseCameraROI` | not called |  |  |  |   |
| `ImageReuseCameraSettings` | not called |  |  |  |   |
| `ImageReuseDeviceSettings` | not called |  |  |  |   |
| `ImageReuseExperiment` | not called |  |  |  |   |
| `ImageReuseOptConf` | not called |  |  |  |   |
| `ImageReuseStimulationSettings` | not called |  |  |  |   |
| `ND_MoveStageToSelectedPoint` | not called |  |  |  |   |
| `OpenFileInFolder` | not called |  |  |  |   |
| `SetFileAbsTime` | not called |  |  |  |   |
| `XYZOverview_PreviewClear` | not called |  |  |  |   |
| `XYZOverview_PreviewFromCurrentDocument` | not called |  |  |  |   |
| `XYZOverview_PreviewFromCurrentDocumentAllXY` | not called |  |  |  |   |
| `XYZOverview_SetAdjustToPoints` | not called |  |  |  |   |

## Macro

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `GetVariableValue` | needs arguments | error: Bad number of parameters |  |  |   |
| `SetVariableValue` | not called |  |  |  |   |
| `AbortMacro` | not called |  |  |  |   |
| `AssignMacro` | not called |  |  |  |   |
| `BackupMacroPanel` | not called |  |  |  |   |
| `BrowseMacro` | not called |  |  |  |   |
| `Command` | not called |  |  |  |   |
| `CommandHistory` | not called |  |  |  |   |
| `ECMAScript` | not called |  |  |  |   |
| `EditMacro` | not called |  |  |  |   |
| `ExecuteAddon` | not called |  |  |  |   |
| `GA3_Execute` | not called |  |  |  |   |
| `GA3_ImportResults` | not called |  |  |  |   |
| `GA3_ImportResultsEx` | not called |  |  |  |   |
| `GA3_RecipeFromUndoSteps` | not called |  |  |  |   |
| `GA3_RunAnalysis` | not called |  |  |  |   |
| `GA3_RunAnalysisEx` | not called |  |  |  |   |
| `GA3_SettingsClose` | not called |  |  |  |   |
| `GA3_SettingsOpen` | not called |  |  |  |   |
| `GA3_SettingsSave` | not called |  |  |  |   |
| `GA3_SettingsSetParamNumber` | not called |  |  |  |   |
| `GA3_SettingsSetParamText` | not called |  |  |  |   |
| `GetHistory` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_RunningMacroDir` | not called |  |  |  |   |
| `History` | not called |  |  |  |   |
| `IJ_Execute` | not called |  |  |  |   |
| `IJ_FileOpen` | not called |  |  |  |   |
| `IJ_FileSaveCurrent` | not called |  |  |  |   |
| `IJ_SaveSettings` | not called |  |  |  |   |
| `LoadMacro` | not called |  |  |  |   |
| `MacroPreferences` | not called |  |  |  |   |
| `NewMacro` | not called |  |  |  |   |
| `OpenMacro` | not called |  |  |  |   |
| `Paste_Command` | not called |  |  |  |   |
| `PauseMacro` | not called |  |  |  |   |
| `QML_ClearComponentCache` | not called |  |  |  |   |
| `QML_ListDeviceAPIProperties` | not called |  |  |  |   |
| `RecordMacro` | not called |  |  |  |   |
| `RepeatLast` | not called |  |  |  |   |
| `RestoreMacroPanel` | not called |  |  |  |   |
| `RunCurrentMacro` | not called |  |  |  |   |
| `RunMacro` | not called |  |  |  |   |
| `RunMacroOnEvent` | not called |  |  |  |   |
| `RunMacroOnFileList` | not called |  |  |  |   |
| `RunMacroOnFilesInFolder` | not called |  |  |  |   |
| `RunMacroOnND` | not called |  |  |  |   |
| `RunMacroOnOpenedDocuments` | not called |  |  |  |   |
| `SaveAsMacro` | not called |  |  |  |   |
| `SaveCurrrentMacroAsShared` | not called |  |  |  |   |
| `SaveMacroAsShared` | not called |  |  |  |   |
| `ShortcutsCreateNewPad` | not called |  |  |  |   |
| `_IJ_ProcessCurrentImage` | not called |  |  |  |   |
| `_IJ_Settings` | not called |  |  |  |   |
| `_ManageSharedMacros` | not called |  |  |  |   |
| `_RecordMacro` | not called |  |  |  |   |
| `_RunMacro` | not called |  |  |  |   |
| `_RunMacroOnEvents` | not called |  |  |  |   |
| `_StartSearchMenu` | not called |  |  |  |   |
| `_RunMacroOnFileList` | not called |  |  |  |   |
| `_RunMacroOnFilesInFolder` | not called |  |  |  |   |
| `_RunMacroOnND` | not called |  |  |  |   |
| `_RunMacroOnOpenedDocuments` | not called |  |  |  |   |

## Measure

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `SetNumClasses` | not called |  |  |  |   |
| `MeasAddCustomFeature` | not called |  |  |  |   |
| `MeasLoadCustomFeatures` | not called |  |  |  |   |
| `MeasResetCustomFeatures` | not called |  |  |  |   |
| `MeasSaveCustomFeatures` | not called |  |  |  |   |
| `MeasSetCustomFeatureExpression` | not called |  |  |  |   |
| `_MeasDefineCustomFeatures` | not called |  |  |  |   |
| `Get_3DObjectFeatureDataDbl` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_3DObjectFeatureDataStr` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_3DObjectFeatureName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_3DObjectFeatureValueDbl` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_3DObjectFeatureValueStr` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_3DObjectFeaturesCount` | ran | 0 |  |  |   |
| `Get_3DObjectRecordsCount` | ran | 0 |  |  |   |
| `Get_BinaryInRoiFeatureData` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_BinaryInRoiFeatureStats` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_BinaryInRoiFeatureStatsInLocation` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_BinaryInRoiFeatureValue` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_BinaryInRoiFeatureValueString` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_FeatureRestriction` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_FieldFeatureData` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_FieldFeatureDataInBinary` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_FieldFeatureName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_FieldFeatureStats` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_FieldFeatureStatsInBinary` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_FieldFeatureStatsInBinaryAndLocation` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_FieldFeatureStatus` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_FieldFeatureValue` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_FieldFeatureValueInBinary` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_FieldFeatureValueString` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_Histo` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_IFeatureData` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_IFeatureSData` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_IFeatureSValueString` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_IFeatureValueString` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_NumFeatures` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_NumFields` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_NumIFeatureRecords` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_NumIFeatureSRecords` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_NumObjects` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_NumObjectsInBinary` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_NumObjectsInBinaryAndRoi` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureData` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureDataInBinary` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureDataInBinaryAndRoi` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureStats` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureStatsInBinary` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureStatsInBinaryAndRoi` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureStatsInBinaryAndRoiAndLocation` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureStatus` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureValue` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureValueInBinary` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureValueInBinaryAndRoi` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureValueString` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ObjectFeatureValueStringInBinaryAndRoi` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ROIFeatureData` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ROIFeatureStats` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ROIFeatureStatsInLocation` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ROIFeatureValue` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ROIFeatureValueString` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_ROINumObjects` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_TableFeatureData` | needs arguments | error: Bad number of parameters |  |  |   |
| `ResetAutoMeasData` | not called |  |  |  |   |
| `ExportFieldData` | not called |  |  |  |   |
| `ExportObjectData` | not called |  |  |  |   |
| `ExportObjectStats` | not called |  |  |  |   |
| `ExportROIData` | not called |  |  |  |   |
| `Measure3DVolume` | not called |  |  |  |   |
| `MeasureField` | not called |  |  |  |   |
| `MeasureFieldND` | not called |  |  |  |   |
| `ResetFieldFeatures` | not called |  |  |  |   |
| `SelectFieldFeature` | not called |  |  |  |   |
| `_FieldMeasSetup` | not called |  |  |  |   |
| `_MeasureFieldND` | not called |  |  |  |   |
| `HistogramAutoMeas_RotateAxisYCaption` | not called |  |  |  |   |
| `HistogramAutoMeas_SetAutoBinWidth` | not called |  |  |  |   |
| `HistogramAutoMeas_SetAutoMax` | not called |  |  |  |   |
| `HistogramAutoMeas_SetAutoMin` | not called |  |  |  |   |
| `HistogramAutoMeas_SetAxisXCaption` | not called |  |  |  |   |
| `HistogramAutoMeas_SetAxisYCaption` | not called |  |  |  |   |
| `HistogramAutoMeas_SetEqBins` | not called |  |  |  |   |
| `HistogramAutoMeas_SetEquidistant` | not called |  |  |  |   |
| `HistogramAutoMeas_SetNonEqBins` | not called |  |  |  |   |
| `HistogramAutoMeas_SetTopCaption` | not called |  |  |  |   |
| `HistogramAutoMeas_ShowAxisXCaption` | not called |  |  |  |   |
| `HistogramAutoMeas_ShowAxisYCaption` | not called |  |  |  |   |
| `HistogramAutoMeas_ShowTopCaption` | not called |  |  |  |   |
| `HistogramManMeas_RotateAxisYCaption` | not called |  |  |  |   |
| `HistogramManMeas_SetAutoBinWidth` | not called |  |  |  |   |
| `HistogramManMeas_SetAutoMax` | not called |  |  |  |   |
| `HistogramManMeas_SetAutoMin` | not called |  |  |  |   |
| `HistogramManMeas_SetAxisXCaption` | not called |  |  |  |   |
| `HistogramManMeas_SetAxisYCaption` | not called |  |  |  |   |
| `HistogramManMeas_SetEqBins` | not called |  |  |  |   |
| `HistogramManMeas_SetEquidistant` | not called |  |  |  |   |
| `HistogramManMeas_SetNonEqBins` | not called |  |  |  |   |
| `HistogramManMeas_SetTopCaption` | not called |  |  |  |   |
| `HistogramManMeas_ShowAxisXCaption` | not called |  |  |  |   |
| `HistogramManMeas_ShowAxisYCaption` | not called |  |  |  |   |
| `HistogramManMeas_ShowTopCaption` | not called |  |  |  |   |
| `Histogram_FieldDataEx` | not called |  |  |  |   |
| `Histogram_ObjectDataEx` | not called |  |  |  |   |
| `ManualMeasure` | not called |  |  |  |   |
| `ManualMeasureClear` | not called |  |  |  |   |
| `ManualMeasureReset` | not called |  |  |  |   |
| `Measure3DAngle` | not called |  |  |  |   |
| `Measure3DLength` | not called |  |  |  |   |
| `Measure3DPolyline` | not called |  |  |  |   |
| `MeasureAngle` | not called |  |  |  |   |
| `MeasureArea` | not called |  |  |  |   |
| `MeasureCounts` | not called |  |  |  |   |
| `MeasureLength` | not called |  |  |  |   |
| `MeasureNumbers` | not called |  |  |  |   |
| `MeasureRadius` | not called |  |  |  |   |
| `MeasureSemiaxes` | not called |  |  |  |   |
| `_MeasureLengthAdv` | not called |  |  |  |   |
| `ClearCurrentMeasurement` | not called |  |  |  |   |
| `GenerateBinary` | not called |  |  |  |   |
| `GenerateBinaryEx` | not called |  |  |  |   |
| `GenerateBinaryExND` | not called |  |  |  |   |
| `GenerateBinaryND` | not called |  |  |  |   |
| `MeasureObjects` | not called |  |  |  |   |
| `MeasureObjectsND` | not called |  |  |  |   |
| `ResetObjectFeatures` | not called |  |  |  |   |
| `ResetRestrictions` | not called |  |  |  |   |
| `Restrictions` | not called |  |  |  |   |
| `ScanObjects` | not called |  |  |  |   |
| `ScanObjectsND` | not called |  |  |  |   |
| `SelectObjectFeature` | not called |  |  |  |   |
| `UpdateCurrentMeasurement` | not called |  |  |  |   |
| `_GenerateBinaryND` | not called |  |  |  |   |
| `_InspectObjects` | not called |  |  |  |   |
| `_MeasureObjectsND` | not called |  |  |  |   |
| `_ObjectData` | not called |  |  |  |   |
| `_ObjectMeasSetup` | not called |  |  |  |   |
| `_Restrictions` | not called |  |  |  |   |
| `_ScanObjects` | not called |  |  |  |   |
| `DataDelimiter` | not called |  |  |  |   |
| `SetCopyMeasFromLive` | not called |  |  |  |   |
| `_DataDelimiter` | not called |  |  |  |   |
| `_MeasurementOptions` | not called |  |  |  |   |
| `_TaxonomyOptions` | not called |  |  |  |   |
| `BestFitGetCircle` | not called |  |  |  |   |
| `InsertProfileLine` | not called |  |  |  |   |
| `InsertZProfileLine` | not called |  |  |  |   |
| `MeasureProfile` | not called |  |  |  |   |
| `ProfileFullSize` | not called |  |  |  |   |
| `ProfileMeasureComponent` | not called |  |  |  |   |
| `ProfileProperties` | not called |  |  |  |   |
| `ProfileReverse` | not called |  |  |  |   |
| `PSF_MeasureFWHM` | not called |  |  |  |   |
| `RemoveProfileLine` | not called |  |  |  |   |
| `RemoveZProfileLine` | not called |  |  |  |   |
| `ShowProfile` | not called |  |  |  |   |
| `ToggleProfile` | not called |  |  |  |   |
| `_ProfileLineSettings` | not called |  |  |  |   |
| `_ProfileProperties` | not called |  |  |  |   |
| `_ProfilePropertiesBasic` | not called |  |  |  |   |
| `_ZProfileLineSettings` | not called |  |  |  |   |
| `_ZProfileProperties` | not called |  |  |  |   |
| `_ZProfile_Options` | not called |  |  |  |   |
| `ManualMeasLoadSettings` | not called |  |  |  |   |
| `ManualMeasSaveSettings` | not called |  |  |  |   |
| `MeasObjectExclusion` | not called |  |  |  |   |
| `MeasurementLoadSettings` | not called |  |  |  |   |
| `MeasurementSaveSettings` | not called |  |  |  |   |
| `_FeatureGraph` | not called |  |  |  |   |
| `_ManualMeasLoadSettings` | not called |  |  |  |   |
| `_ManualMeasSaveSettings` | not called |  |  |  |   |
| `_MeasurementLoadSettings` | not called |  |  |  |   |
| `_MeasurementSaveSettings` | not called |  |  |  |   |
| `ShowIntensitySurfacePlot` | not called |  |  |  |   |

## Misc

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `EnableProfile` | not called |  |  |  |   |
| `ResetProfile` | not called |  |  |  |   |
| `ViewProfileResults` | not called |  |  |  |   |
| `Python_RunFile` | not called |  |  |  |   |
| `Python_RunString` | not called |  |  |  |   |
| `Heart_Analyze` | not called |  |  |  |   |
| `PSNR` | not called |  |  |  |   |

## ND

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `ExportImagesToTIFF` | not called |  |  |  |   |
| `GetSuggestedZStep` | ran | 0.0 |  |  |   |
| `ModifyZStep` | not called |  |  |  |   |
| `ND_BioStationNex_Import` | not called |  |  |  |   |
| `ND_ConvertAddWaveLength` | not called |  |  |  |   |
| `ND_ConvertAddWaveLength2` | not called |  |  |  |   |
| `ND_ConvertAllocXYCoors` | not called |  |  |  |   |
| `ND_ConvertFinish` | not called |  |  |  |   |
| `ND_ConvertFreeXYCoors` | not called |  |  |  |   |
| `ND_ConvertInit` | not called |  |  |  |   |
| `ND_ConvertSequenceToSpectral` | not called |  |  |  |   |
| `ND_ConvertSetMicSettings` | not called |  |  |  |   |
| `ND_ConvertSetTimeLoop` | not called |  |  |  |   |
| `ND_ConvertSetXYLoop` | not called |  |  |  |   |
| `ND_ConvertSetZStackLoop` | not called |  |  |  |   |
| `ND_CropAllocMask` | not called |  |  |  |   |
| `ND_CropFinish` | not called |  |  |  |   |
| `ND_CropFreeMask` | not called |  |  |  |   |
| `ND_CropInit` | not called |  |  |  |   |
| `ND_CropSetBinary` | not called |  |  |  |   |
| `ND_CropSetChannelCropXYZ` | not called |  |  |  |   |
| `ND_CropSetChannelCropXYZArb` | not called |  |  |  |   |
| `ND_CropSetProjections` | not called |  |  |  |   |
| `ND_CropSpectLoop` | not called |  |  |  |   |
| `ND_CropTimeLoop` | not called |  |  |  |   |
| `ND_CropXYLoop` | not called |  |  |  |   |
| `ND_CropZStackLoop` | not called |  |  |  |   |
| `ND_DefineExperiment` | not called |  |  |  |   |
| `ND_ExchangeDimensions` | not called |  |  |  |   |
| `ND_Export` | not called |  |  |  |   |
| `ND_ExportToTIFF` | not called |  |  |  |   |
| `ND_FinishExperiment` | not called |  |  |  |   |
| `ND_GetCurrentPosIndexes` | not called |  |  |  |   |
| `ND_GetExperimentLoopSize` | not called |  |  |  |   |
| `ND_GetPictureMetadata` | not called |  |  |  |   |
| `ND_GetPositionInExperiment` | not called |  |  |  |   |
| `ND_GetRecordingDataDouble` | not called |  |  |  |   |
| `ND_GetRecordingDataInt` | not called |  |  |  |   |
| `ND_GetRecordingDataString` | not called |  |  |  |   |
| `ND_GetSelectionRange` | not called |  |  |  |   |
| `ND_InsertEvent` | not called |  |  |  |   |
| `ND_LoadExperiment` | not called |  |  |  |   |
| `ND_LoadMultipointSet` | not called |  |  |  |   |
| `ND_LoadNDAdvanced` | not called |  |  |  |   |
| `ND_LoadSequence` | not called |  |  |  |   |
| `ND_MergeFiles` | not called |  |  |  |   |
| `ND_MoveExperimentBackward` | not called |  |  |  |   |
| `ND_MoveExperimentForward` | not called |  |  |  |   |
| `ND_MoveInExperiment` | not called |  |  |  |   |
| `ND_MoveInExperimentSeq` | not called |  |  |  |   |
| `ND_MoveRangeBackward` | not called |  |  |  |   |
| `ND_MoveRangeForward` | not called |  |  |  |   |
| `ND_MoveToNextEvent` | not called |  |  |  |   |
| `ND_MoveToPreviousEvent` | not called |  |  |  |   |
| `ND_PauseExperiment` | not called |  |  |  |   |
| `ND_RecordedDataDefault` | not called |  |  |  |   |
| `ND_RedefineAbsZ` | not called |  |  |  |   |
| `ND_RemoveEvent` | not called |  |  |  |   |
| `ND_RemoveExperiment` | not called |  |  |  |   |
| `ND_RemoveRecordingData` | not called |  |  |  |   |
| `ND_ResumeExperiment` | not called |  |  |  |   |
| `ND_ReuseExperiment` | not called |  |  |  |   |
| `ND_ReuseZIntensityCorr` | not called |  |  |  |   |
| `ND_RunExperiment` | not called |  |  |  |   |
| `ND_RunExperimentNoProgressBar` | not called |  |  |  |   |
| `ND_RunExperimentWithZIntensityCorrection` | not called |  |  |  |   |
| `ND_RunMultipointSet` | not called |  |  |  |   |
| `ND_RunNDAdvanced` | not called |  |  |  |   |
| `ND_SaveExperiment` | not called |  |  |  |   |
| `ND_SetRecordingDataDouble` | not called |  |  |  |   |
| `ND_SetRecordingDataInt` | not called |  |  |  |   |
| `ND_SetRecordingDataString` | not called |  |  |  |   |
| `ND_SetSelectionMode` | not called |  |  |  |   |
| `ND_SetSelectionRange` | not called |  |  |  |   |
| `ND_SplitMultipoints` | not called |  |  |  |   |
| `OpenStackedTiff` | not called |  |  |  |   |
| `_ExportImagesToTIFF` | not called |  |  |  |   |
| `_ND_BatchExport` | not called |  |  |  |   |
| `_ND_BioStationNex_Import` | not called |  |  |  |   |
| `_ND_Convert` | not called |  |  |  |   |
| `_ND_CreateJsonSequence` | not called |  |  |  |   |
| `_ND_CreateNDAdvanced` | not called |  |  |  |   |
| `_ND_Crop` | not called |  |  |  |   |
| `_ND_Dicom_Import` | not called |  |  |  |   |
| `_ND_ExchangeDimensions` | not called |  |  |  |   |
| `_ND_Export` | not called |  |  |  |   |
| `_ND_ExportToTIFF` | not called |  |  |  |   |
| `_ND_SplitMultipoints` | not called |  |  |  |   |
| `_OpenSequence` | not called |  |  |  |   |
| `ND_CreateKymographBySelectedLine` | not called |  |  |  |   |
| `ND_KymographLineSettings` | not called |  |  |  |   |
| `_ND_CreateKymographByLine` | not called |  |  |  |   |
| `_ND_KymographLineSettings` | not called |  |  |  |   |
| `ND_AppendLambdaChannel` | not called |  |  |  |   |
| `ND_GetLambdaChannel` | not called |  |  |  |   |
| `ND_IsInExperimentCapture` | not called |  |  |  |   |
| `ND_ResetLambdaExp` | not called |  |  |  |   |
| `ND_RunLambdaExp` | not called |  |  |  |   |
| `ND_SetLambdaExp` | not called |  |  |  |   |
| `ND_SetLambdaRepresentation` | not called |  |  |  |   |
| `_ND_CreateLambdaExp` | not called |  |  |  |   |
| `ND_AppendMultipointPoint` | not called |  |  |  |   |
| `ND_AppendMultipointPointPFS` | not called |  |  |  |   |
| `ND_GetMultipointEnabled` | not called |  |  |  |   |
| `ND_GetMultipointName` | not called |  |  |  |   |
| `ND_KeepPFSOnDuringStageMove` | not called |  |  |  |   |
| `ND_LoadMultipoint` | not called |  |  |  |   |
| `ND_MP_GetCount` | not called |  |  |  |   |
| `ND_MP_MoveToIndex` | not called |  |  |  |   |
| `ND_OffsetAllMultipoints` | not called |  |  |  |   |
| `ND_RedefineAbsZAfterPFS` | not called |  |  |  |   |
| `ND_ResetMultipointExp` | not called |  |  |  |   |
| `ND_RunMultipointExp` | not called |  |  |  |   |
| `ND_SaveMultipoint` | not called |  |  |  |   |
| `ND_SetLambdaEnabled` | not called |  |  |  |   |
| `ND_SetLargeImageEnabled` | not called |  |  |  |   |
| `ND_SetMultipointEnabled` | not called |  |  |  |   |
| `ND_SetMultiPoints` | not called |  |  |  |   |
| `ND_SetPictureMetadata` | not called |  |  |  |   |
| `ND_SetMultiPointsEx` | not called |  |  |  |   |
| `ND_SetMultipointExp` | not called |  |  |  |   |
| `ND_SetTimeEnabled` | not called |  |  |  |   |
| `ND_SetXYEnabled` | not called |  |  |  |   |
| `ND_SetZStackEnabled` | not called |  |  |  |   |
| `_ND_CaptureMultipointManually` | not called |  |  |  |   |
| `_ND_CreateMultipointExp` | not called |  |  |  |   |
| `ND_CreateMaxIntProjectionImageT` | not called |  |  |  |   |
| `ND_CreateMaxIntProjectionImageZ` | not called |  |  |  |   |
| `ND_CreateMinIntProjectionImageT` | not called |  |  |  |   |
| `ND_CreateMinIntProjectionImageZ` | not called |  |  |  |   |
| `ND_ShowMaxIntProjectionImage` | not called |  |  |  |   |
| `ND_ShowMinIntProjectionImage` | not called |  |  |  |   |
| `EnableTapToFrap` | not called |  |  |  |   |
| `ND_RunSequentialStimulationExp` | not called |  |  |  |   |
| `ND_RunSimultaneousStimulationExp` | not called |  |  |  |   |
| `ND_StimulationAppendPhase` | not called |  |  |  |   |
| `ND_StimulationCommand` | not called |  |  |  |   |
| `ND_StimulationPoint` | not called |  |  |  |   |
| `ND_StimulationResetPhases` | not called |  |  |  |   |
| `ND_StimulationSimultaneousAcquisition` | not called |  |  |  |   |
| `ND_StimulationSimultaneousStimulation` | not called |  |  |  |   |
| `ND_TriggerManualStimPhase` | not called |  |  |  |   |
| `ND_AppendTimePhase` | not called |  |  |  |   |
| `ND_AppendTimePhaseEx` | not called |  |  |  |   |
| `ND_Concatenate1DT` | not called |  |  |  |   |
| `ND_FastTimelapse` | not called |  |  |  |   |
| `ND_FastTimelapsePrepare` | not called |  |  |  |   |
| `ND_FastTimelapsePrepare_EX` | not called |  |  |  |   |
| `ND_GetTimeExp` | not called |  |  |  |   |
| `ND_GetTimeExpPhase` | not called |  |  |  |   |
| `ND_GetTimeLapsePhaseCount` | not called |  |  |  |   |
| `ND_GetTimePhase` | not called |  |  |  |   |
| `ND_GetTimePhaseSchedule` | not called |  |  |  |   |
| `ND_ResetTimeExp` | not called |  |  |  |   |
| `ND_ReverseTimelapseDirection` | not called |  |  |  |   |
| `ND_RunTimeExp` | not called |  |  |  |   |
| `ND_SetTimeExp` | not called |  |  |  |   |
| `ND_SetTimeExpPhase` | not called |  |  |  |   |
| `ND_StartTimePhase` | not called |  |  |  |   |
| `_ND_CaptureTimelapseManually` | not called |  |  |  |   |
| `_ND_CreateTimeExp` | not called |  |  |  |   |
| `_ND_FastTimelapse` | not called |  |  |  |   |
| `ND_CreateZStackFile` | not called |  |  |  |   |
| `ND_GetZSeriesExp` | not called |  |  |  |   |
| `ND_GetZSeriesType` | not called |  |  |  |   |
| `ND_ResetZSeriesExp` | not called |  |  |  |   |
| `ND_ReverseZStackDirection` | not called |  |  |  |   |
| `ND_RunZSeriesExp` | not called |  |  |  |   |
| `ND_SetZSeriesExp` | not called |  |  |  |   |
| `ND_RunZSeriesExpWithZIntensityCorrection` | not called |  |  |  |   |
| `ND_SetZSeriesType` | not called |  |  |  |   |
| `ND_ShowEDFFocusedView` | not called |  |  |  |   |
| `ND_ShowEDFToolbar` | not called |  |  |  |   |
| `ND_ShowMainView` | not called |  |  |  |   |
| `ND_ShowSlicesView` | not called |  |  |  |   |
| `ND_ShowVolumeViewVTK` | not called |  |  |  |   |
| `ND_ToggleOrigFocImage` | not called |  |  |  |   |
| `ND_VV_CreatePyramidFile` | not called |  |  |  |   |
| `ND_VV_ManagePyramidFiles` | not called |  |  |  |   |
| `ND_ShowTiledView` | not called |  |  |  |   |
| `ND_ShowVolumeView` | not called |  |  |  |   |
| `ND_ShowVolumeViewDX11` | not called |  |  |  |   |
| `ND_VV_Reset` | not called |  |  |  |   |
| `ND_ZIntensityControlIsDataReady` | not called |  |  |  |   |
| `ND_ZIntensityControlLoad` | not called |  |  |  |   |
| `ND_ZIntensityControlSave` | not called |  |  |  |   |
| `_ND_CaptureZManually` | not called |  |  |  |   |
| `_ND_CreateZSeriesExp` | not called |  |  |  |   |
| `_ND_ZIntensityControl` | not called |  |  |  |   |
| `IncubationInterfaceSetActive` | not called |  |  |  |   |
| `NDEnableSaveToTIFF` | not called |  |  |  |   |
| `ND_AddCustomMetadataDefinition` | not called |  |  |  |   |
| `ND_AddCustomMetadataField` | not called |  |  |  |   |
| `ND_CreateViewProjection` | not called |  |  |  |   |
| `ND_CustomCapture` | not called |  |  |  |   |
| `ND_CustomFinish` | not called |  |  |  |   |
| `ND_CustomSequenceConvertToMultipoint` | not called |  |  |  |   |
| `ND_CustomSequenceConvertToTime` | not called |  |  |  |   |
| `ND_CustomSequenceConvertToZStack` | not called |  |  |  |   |
| `ND_CustomSetSettings` | not called |  |  |  |   |
| `ND_GetCustomMetadataDefinition` | not called |  |  |  |   |
| `ND_GetCustomMetadataDefinitionCount` | not called |  |  |  |   |
| `ND_GetCustomMetadataFieldCount` | not called |  |  |  |   |
| `ND_GetCustomMetadataFieldInfo` | not called |  |  |  |   |
| `ND_GetCustomMetadataFieldName` | not called |  |  |  |   |
| `ND_GetCustomMetadataFieldText` | not called |  |  |  |   |
| `ND_GetCustomMetadataFieldValue` | not called |  |  |  |   |
| `ND_RefreshView` | not called |  |  |  |   |
| `ND_RemoveCustomMetadataDefinition` | not called |  |  |  |   |
| `ND_RemoveCustomMetadataField` | not called |  |  |  |   |
| `ND_SelectViewProjection` | not called |  |  |  |   |
| `ND_SelectViewProjectionEx` | not called |  |  |  |   |
| `ND_SetAuthentication` | not called |  |  |  |   |
| `ND_SetCustomMetadataFieldText` | not called |  |  |  |   |
| `ND_SetCustomMetadataFieldValue` | not called |  |  |  |   |
| `ND_SetOpenViewsToNewWindow` | not called |  |  |  |   |
| `ND_SetPlateLabeling` | not called |  |  |  |   |
| `ND_SetZeroBasedTime` | not called |  |  |  |   |
| `Stimulate` | not called |  |  |  |   |
| `_MergeNDDocuments` | not called |  |  |  |   |

## Organizer

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `_Org_Copy` | not called |  |  |  |   |
| `_Org_Cut` | not called |  |  |  |   |
| `_Org_Delete` | not called |  |  |  |   |
| `_Org_GenerateReport` | not called |  |  |  |   |
| `_Org_InvertSelection` | not called |  |  |  |   |
| `_Org_NextPane` | not called |  |  |  |   |
| `_Org_OpenImage` | not called |  |  |  |   |
| `_Org_Paste` | not called |  |  |  |   |
| `_Org_Properties` | not called |  |  |  |   |
| `_Org_RefreshFolders` | not called |  |  |  |   |
| `_Org_RemoveFilterAndSort` | not called |  |  |  |   |
| `_Org_RemoveSort` | not called |  |  |  |   |
| `_Org_Rotate180` | not called |  |  |  |   |
| `_Org_RotateLeft` | not called |  |  |  |   |
| `_Org_RotateRight` | not called |  |  |  |   |
| `_Org_SelectAll` | not called |  |  |  |   |
| `_Org_SetDirectory` | not called |  |  |  |   |
| `_Org_SetPanesSameSize` | not called |  |  |  |   |
| `_Org_SortByColumn` | not called |  |  |  |   |
| `_Org_SwitchLeftPaneSize` | not called |  |  |  |   |
| `_Org_SwitchNavigationView` | not called |  |  |  |   |
| `_Org_SwitchRightPaneSize` | not called |  |  |  |   |
| `_Org_ViewType` | not called |  |  |  |   |
| `_PrecacheThumbnails` | not called |  |  |  |   |
| `Org_GetActiveDataSource` | ran | 0 |  |  |   |
| `Org_GetColumnName` | needs arguments | error: Bad number of parameters |  |  |   |
| `Org_GetColumnNameEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Org_GetExtension` | needs arguments | error: Bad number of parameters |  |  |   |
| `Org_GetExtensionEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Org_GetFieldValue` | needs arguments | error: Bad number of parameters |  |  |   |
| `Org_GetFieldValueEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Org_GetFileFolder` | needs arguments | error: Bad number of parameters |  |  |   |
| `Org_GetFileFolderEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Org_GetRecordCount` | ran | 6 |  |  |   |
| `Org_GetRecordCountEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Org_GetRecursive` | ran | 0 |  |  |   |
| `Org_GetRecursiveEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Org_SetExtension` | not called |  |  |  |   |
| `Org_SetExtensionEx` | not called |  |  |  |   |
| `Org_SetFileFolder` | not called |  |  |  |   |
| `Org_SetFileFolderEx` | not called |  |  |  |   |
| `Org_SetRecursive` | not called |  |  |  |   |
| `Org_SetRecursiveEx` | not called |  |  |  |   |
| `Org_SortTablesByNames` | not called |  |  |  |   |
| `Org_EnableFilter` | not called |  |  |  |   |
| `Org_ExtentFilter` | not called |  |  |  |   |
| `Org_SetFilter` | not called |  |  |  |   |
| `_Org_ShowFilter` | not called |  |  |  |   |
| `Org_OpenImage` | not called |  |  |  |   |
| `Org_OpenImageEx` | not called |  |  |  |   |
| `Org_GetPaneFocus` | ran | 0 |  |  |   |
| `Org_IsPaneVisible` | not called |  |  |  |   |
| `Org_KillPaneFocus` | not called |  |  |  |   |
| `Org_SetPaneFocus` | not called |  |  |  |   |
| `Org_ShowPane` | not called |  |  |  |   |
| `Org_CurrSel_GetFieldValue` | not called |  |  |  |   |
| `Org_CurrSel_GetFieldValueEx` | not called |  |  |  |   |
| `Org_CurrSel_GetRecordCount` | not called |  |  |  |   |
| `Org_CurrSel_GetRecordCountEx` | not called |  |  |  |   |
| `Org_CurrSel_OpenImage` | not called |  |  |  |   |
| `Org_CurrSel_OpenImageEx` | not called |  |  |  |   |
| `Org_InvertSelection` | not called |  |  |  |   |
| `Org_InvertSelectionEx` | not called |  |  |  |   |
| `Org_SelectAll` | not called |  |  |  |   |
| `Org_SelectAllEx` | not called |  |  |  |   |
| `Org_SelectRange` | not called |  |  |  |   |
| `Org_SelectRangeEx` | not called |  |  |  |   |
| `Org_SelectRecord` | not called |  |  |  |   |
| `Org_SelectRecordEx` | not called |  |  |  |   |
| `_Org_CurrSel_Presentation` | not called |  |  |  |   |
| `_Org_CurrSel_PresentationEx` | not called |  |  |  |   |
| `Org_GetSort` | needs arguments | error: Bad number of parameters |  |  |   |
| `Org_GetSortEx` | needs arguments | error: Bad number of parameters |  |  |   |
| `Org_SetSort` | not called |  |  |  |   |
| `Org_SetSortEx` | not called |  |  |  |   |

## System

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `GetXYFromDWord` | needs arguments | error: Bad number of parameters |  |  |   |
| `HIBYTE` | not called |  |  |  |   |
| `HIWORD` | not called |  |  |  |   |
| `LOBYTE` | not called |  |  |  |   |
| `LOWORD` | not called |  |  |  |   |
| `_GeneralOptions` | not called |  |  |  |   |
| `_Options` | not called |  |  |  |   |
| `_SetTempFilesPathForNextSession` | not called |  |  |  |   |
| `Exit` | not called |  |  |  |   |
| `ExitEx` | not called |  |  |  |   |
| `Get_ClipboardText` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_Info` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_InfoStr` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_Language` | ran | 0 |  |  |   |
| `Get_Size` | needs arguments | error: Bad number of parameters |  |  |   |
| `Get_UserTime` | needs arguments | error: Bad number of parameters |  |  |   |
| `DeleteVariable` | not called |  |  |  |   |
| `DeleteVariables` | not called |  |  |  |   |
| `Enable_Interrupt_InScript` | not called |  |  |  |   |
| `ExistConst` | not called |  |  |  |   |
| `ExistProc` | not called |  |  |  |   |
| `ExistVariable` | not called |  |  |  |   |
| `RegisterConst` | not called |  |  |  |   |
| `RegisterProc` | not called |  |  |  |   |
| `ShowVars` | not called |  |  |  |   |
| `UnregisterProc` | not called |  |  |  |   |
| `VariablesUpdate` | not called |  |  |  |   |
| `Wait` | not called |  |  |  |   |
| `WaitText` | not called |  |  |  |   |
| `BatchAnalysis` | not called |  |  |  |   |
| `Beep` | not called |  |  |  |   |
| `Convert_ms_To_Time` | not called |  |  |  |   |
| `EnableContextMenu` | not called |  |  |  |   |
| `Enable_Special_Actions` | not called |  |  |  |   |
| `Load_Settings` | not called |  |  |  |   |
| `RemoveInputMessages` | not called |  |  |  |   |
| `RunApplicationConventional` | not called |  |  |  |   |
| `RunGeneralAnalysis` | not called |  |  |  |   |
| `RunGeneralAnalysisDB` | not called |  |  |  |   |
| `SMSSend` | not called |  |  |  |   |
| `SMTPConfig` | not called |  |  |  |   |
| `SMTPSendEmail` | not called |  |  |  |   |
| `Save_Configuration` | not called |  |  |  |   |
| `Save_Settings` | not called |  |  |  |   |
| `SetReferenceTime` | not called |  |  |  |   |
| `_ShowUserManager` | not called |  |  |  |   |
| `_BatchAnalysis` | not called |  |  |  |   |
| `_BatchGeneralAnalysis` | not called |  |  |  |   |
| `_BatchSPT` | not called |  |  |  |   |
| `_CreateNewRecipe` | not called |  |  |  |   |
| `_EditExistingAnalysis` | not called |  |  |  |   |
| `_Load_Settings` | not called |  |  |  |   |
| `_NewGeneralAnalysis` | not called |  |  |  |   |
| `_OpenExistingAnalysis` | not called |  |  |  |   |
| `_OpenExistingRecipe` | not called |  |  |  |   |
| `_RunApplication` | not called |  |  |  |   |
| `_RunApplicationConventional` | not called |  |  |  |   |
| `_ShowAnalysisRunResults` | not called |  |  |  |   |
| `_ShowAnalysisSumResults` | not called |  |  |  |   |
| `_RunGeneralAnalysis` | not called |  |  |  |   |
| `_RunGeneralAnalysis3` | not called |  |  |  |   |
| `_RunGeneralAnalysisInWizard` | not called |  |  |  |   |
| `_RunGeneralAnalysisRGBInWizard` | not called |  |  |  |   |
| `_SMTPConfig` | not called |  |  |  |   |
| `_ShowAnalysisRunResultsGraph` | not called |  |  |  |   |
| `_ShowAnalysisRunResultsReport` | not called |  |  |  |   |
| `_ShowAnalysisRunResultsTable` | not called |  |  |  |   |
| `_ShowAnalysisSumResultsGraph` | not called |  |  |  |   |
| `_ShowAnalysisSumResultsReport` | not called |  |  |  |   |
| `_ShowAnalysisSumResultsTable` | not called |  |  |  |   |
| `About` | not called |  |  |  |   |
| `ClearLog` | not called |  |  |  |   |
| `DeviceCommunicationLog` | not called |  |  |  |   |
| `EnableLogging` | not called |  |  |  |   |
| `GetDeviceCommunicationLog` | ran | 1 |  |  |   |
| `HelpContents` | not called |  |  |  |   |
| `HelpCursor` | not called |  |  |  |   |
| `HelpFolder` | not called |  |  |  |   |
| `HelpHotkeys` | not called |  |  |  |   |
| `HelpOpenGitHub` | not called |  |  |  |   |
| `HelpSearch` | not called |  |  |  |   |
| `LogPerSession` | not called |  |  |  |   |
| `OpenLogFile` | not called |  |  |  |   |
| `OpenLogFolder` | not called |  |  |  |   |
| `VersionUpdateAvailability` | not called |  |  |  |   |
| `_HASPInformation` | not called |  |  |  |   |
| `_SendSystemInfo` | not called |  |  |  |   |
| `S3_Close` | not called |  |  |  |   |
| `S3_DownloadFile` | not called |  |  |  |   |
| `S3_ListFilesToClipboard` | not called |  |  |  |   |
| `S3_LoadFile` | not called |  |  |  |   |
| `S3_Logout` | not called |  |  |  |   |
| `S3_Open` | not called |  |  |  |   |
| `S3_RemoveFile` | not called |  |  |  |   |
| `S3_SaveFile` | not called |  |  |  |   |
| `S3_SetPrefix` | not called |  |  |  |   |
| `S3_UploadFile` | not called |  |  |  |   |
| `Streaming_Toggle` | not called |  |  |  |   |
| `Streaming_start` | not called |  |  |  |   |
| `Streaming_stop` | not called |  |  |  |   |
| `_StreamingTool` | not called |  |  |  |   |
| `Get_Date` | ran | None |  |  |   |
| `Get_Time` | ran | None |  |  |   |
| `Timer` | not called |  |  |  |   |
| `GetFocusCriterium` | ran | 0.0 |  |  |   |
| `Get_Calibration` | needs arguments | error: Bad number of parameters |  |  |   |
| `Measure` | not called |  |  |  |   |
| `SetDrive` | not called |  |  |  |   |
| `SetProfileProp` | not called |  |  |  |   |
| `SetRelativePath` | not called |  |  |  |   |
| `_SetDrive` | not called |  |  |  |   |

## UserInterface

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `AssignButton` | not called |  |  |  |   |
| `AssignButtonEx` | not called |  |  |  |   |
| `ChangeTools` | not called |  |  |  |   |
| `DefaultToolbar` | not called |  |  |  |   |
| `EnlargeToolbars` | not called |  |  |  |   |
| `Set_ToolTipText` | not called |  |  |  |   |
| `SetupTools` | not called |  |  |  |   |
| `Toolbar_Next` | not called |  |  |  |   |
| `Toolbar_Prev` | not called |  |  |  |   |
| `EndLayout` | not called |  |  |  |   |
| `SetDockingViewContent` | not called |  |  |  |   |
| `SetDockingViewFlags` | not called |  |  |  |   |
| `SetImageLayout` | not called |  |  |  |   |
| `SetImageLayoutEx` | not called |  |  |  |   |
| `SetLayout` | not called |  |  |  |   |
| `SetOrganizerLayout` | not called |  |  |  |   |
| `ShowDockingView` | not called |  |  |  |   |
| `ShowOrganizerWindow` | not called |  |  |  |   |
| `StartLayout` | not called |  |  |  |   |
| `ToggleDockingView` | not called |  |  |  |   |
| `_LayoutManager` | not called |  |  |  |   |
| `_ShowWindows` | not called |  |  |  |   |
| `_ViewLayoutSetup` | not called |  |  |  |   |
| `AppMaximize` | not called |  |  |  |   |
| `AppMinimize` | not called |  |  |  |   |
| `AppRestore` | not called |  |  |  |   |

## View

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `BackProbeKeepUpdate` | not called |  |  |  |   |
| `BackProbeReset` | not called |  |  |  |   |
| `SetBackOffset` | not called |  |  |  |   |
| `ShowBackProbe` | not called |  |  |  |   |
| `SubtractBackgroundUsingConstant` | not called |  |  |  |   |
| `SubtractBackgroundUsingConstantND` | not called |  |  |  |   |
| `SubtractBackgroundUsingProbe` | not called |  |  |  |   |
| `SubtractBackgroundUsingProbeND` | not called |  |  |  |   |
| `SubtractBackgroundUsingReference` | not called |  |  |  |   |
| `ToggleBackProbe` | not called |  |  |  |   |
| `_BackProbeProperties` | not called |  |  |  |   |
| `_DrawBackProbe` | not called |  |  |  |   |
| `_SetBackOffsetLive` | not called |  |  |  |   |
| `_SubtractBackgroundUsingConstant` | not called |  |  |  |   |
| `_SubtractBackgroundUsingProbe` | not called |  |  |  |   |
| `EnableGUI` | not called |  |  |  |   |
| `ShowControl` | not called |  |  |  |   |
| `ToggleControl` | not called |  |  |  |   |
| `SetFullScreen` | not called |  |  |  |   |
| `ToggleFullScreen` | not called |  |  |  |   |
| `ViewFull` | not called |  |  |  |   |
| `AddBinaryToGraticuleMask` | not called |  |  |  |   |
| `CreateSpecialGraticuleMask` | not called |  |  |  |   |
| `DefaultGridPosition` | not called |  |  |  |   |
| `DefaultGridPositionEx` | not called |  |  |  |   |
| `DefineGraticuleMask` | not called |  |  |  |   |
| `GetGraticuleXPosition` | ran | -9 |  |  |   |
| `GetGraticuleYPosition` | ran | -9 |  |  |   |
| `Get_GraticuleOptions` | needs arguments | error: Bad number of parameters |  |  |   |
| `Graticules3DProperties` | not called |  |  |  |   |
| `GraticulesProperties` | not called |  |  |  |   |
| `LoadGraticuleMask` | not called |  |  |  |   |
| `MoveGraticuleToCenter` | not called |  |  |  |   |
| `SaveGraticuleMask` | not called |  |  |  |   |
| `SetGraticuleMaskOpacity` | not called |  |  |  |   |
| `SetGraticulePosition` | not called |  |  |  |   |
| `ShowGraticule` | not called |  |  |  |   |
| `ToggleGraticule` | not called |  |  |  |   |
| `_Graticules3DProperties` | not called |  |  |  |   |
| `_GraticulesProperties` | not called |  |  |  |   |
| `_LoadGraticuleMask` | not called |  |  |  |   |
| `_SaveGraticuleMask` | not called |  |  |  |   |
| `SetLUTFullIntensityRange` | not called |  |  |  |   |
| `ShowLUTIntensity` | not called |  |  |  |   |
| `ShowLUTIntensityText` | not called |  |  |  |   |
| `ToggleLUTFullIntensityRange` | not called |  |  |  |   |
| `ToggleLUTIntensity` | not called |  |  |  |   |
| `ToggleLUTIntensityText` | not called |  |  |  |   |
| `InsertMagnifierGlass` | not called |  |  |  |   |
| `ToggleMagnifierGamma` | not called |  |  |  |   |
| `ToggleMagnifierGlass` | not called |  |  |  |   |
| `_MagnifierOptions` | not called |  |  |  |   |
| `MeasFrame` | not called |  |  |  |   |
| `MeasFrameColor` | not called |  |  |  |   |
| `MeasFrameProperties` | not called |  |  |  |   |
| `ShowFrame` | not called |  |  |  |   |
| `ToggleFrame` | not called |  |  |  |   |
| `_MeasFrameProperties` | not called |  |  |  |   |
| `AddNDInformation` | not called |  |  |  |   |
| `RemoveNDInformation` | not called |  |  |  |   |
| `ShowNDInformation` | not called |  |  |  |   |
| `ToggleNDInformation` | not called |  |  |  |   |
| `_NDInformationProperties` | not called |  |  |  |   |
| `AddEquationViewOnLive` | not called |  |  |  |   |
| `AddNewEquationView` | not called |  |  |  |   |
| `AllowZoomUnderBestFit` | not called |  |  |  |   |
| `AutoZoomInMeasurement` | not called |  |  |  |   |
| `BackupLayouts` | not called |  |  |  |   |
| `DisplayColorSpace` | not called |  |  |  |   |
| `DisplayOptions` | not called |  |  |  |   |
| `EnableButtons` | not called |  |  |  |   |
| `EnableLayouts` | not called |  |  |  |   |
| `EnableZIntensityControl` | not called |  |  |  |   |
| `EquationViewSetup` | not called |  |  |  |   |
| `KeepPicWndAspect` | not called |  |  |  |   |
| `KeepTextZoom` | not called |  |  |  |   |
| `LoadTitration` | not called |  |  |  |   |
| `LoadTitrationFromFile` | not called |  |  |  |   |
| `MeasColors` | not called |  |  |  |   |
| `ND_CloseAcqAfterRun` | not called |  |  |  |   |
| `PearsonViewEnable` | not called |  |  |  |   |
| `RatioViewAutoScale` | not called |  |  |  |   |
| `RatioViewEnable` | not called |  |  |  |   |
| `RatioViewSetup` | not called |  |  |  |   |
| `Redraw` | not called |  |  |  |   |
| `ReloadCurrentLayout` | not called |  |  |  |   |
| `ReloadDefaultLayout` | not called |  |  |  |   |
| `RemoveEquationView` | not called |  |  |  |   |
| `RemoveEquationViewOnLive` | not called |  |  |  |   |
| `ResetAutoScale` | not called |  |  |  |   |
| `RestoreLayouts` | not called |  |  |  |   |
| `RestoreLayoutsEx` | not called |  |  |  |   |
| `SaveCurrentLayout` | not called |  |  |  |   |
| `SaveCurrentLayoutAs` | not called |  |  |  |   |
| `SaveCurrentLayoutAsDefault` | not called |  |  |  |   |
| `SetBackground` | not called |  |  |  |   |
| `SetColorScale` | not called |  |  |  |   |
| `SetCommandText` | not called |  |  |  |   |
| `SetDarkColorScheme` | not called |  |  |  |   |
| `SetDefaultVDockerSide` | not called |  |  |  |   |
| `SetInitialZoom` | not called |  |  |  |   |
| `SetLayoutGuiZoom` | not called |  |  |  |   |
| `SetLineThicknessEx` | not called |  |  |  |   |
| `SetMultiWindowLiveZoom100` | not called |  |  |  |   |
| `SetPhysicalZoom` | not called |  |  |  |   |
| `SetSaveDialogPrompt` | not called |  |  |  |   |
| `SetScreenTextEx` | not called |  |  |  |   |
| `SetStatusBarZIndex` | not called |  |  |  |   |
| `SetTitrationModulatedChannel` | not called |  |  |  |   |
| `SetToolbarsPlacement` | not called |  |  |  |   |
| `ShowComponentTabs` | not called |  |  |  |   |
| `ShowGUI` | not called |  |  |  |   |
| `ShowPhysicalZoom` | not called |  |  |  |   |
| `ShowRatioScale` | not called |  |  |  |   |
| `ShowScrollbars` | not called |  |  |  |   |
| `ShowSplitCompAllChannels` | not called |  |  |  |   |
| `ShowSplitCompCustomChannels` | not called |  |  |  |   |
| `ShowSplitCompPerCamera` | not called |  |  |  |   |
| `ShowTaskbar` | not called |  |  |  |   |
| `ShowThumbsInProc` | not called |  |  |  |   |
| `SplitCompVAASSync` | not called |  |  |  |   |
| `StretchAppWindow` | not called |  |  |  |   |
| `SuppressDisplay` | not called |  |  |  |   |
| `SuppressLMDisplay` | not called |  |  |  |   |
| `TitrationViewEnable` | not called |  |  |  |   |
| `Toggle4KLayoutGuiZoom` | not called |  |  |  |   |
| `ToggleColorScheme` | not called |  |  |  |   |
| `ToggleShowPhysicalZoom` | not called |  |  |  |   |
| `ToggleShowScrollbars` | not called |  |  |  |   |
| `ToggleTaskbar` | not called |  |  |  |   |
| `TransformEquationView` | not called |  |  |  |   |
| `UseAdvacedButtons` | not called |  |  |  |   |
| `ViewEquation` | not called |  |  |  |   |
| `ViewPearson` | not called |  |  |  |   |
| `ViewRatio` | not called |  |  |  |   |
| `ViewSplitComponents` | not called |  |  |  |   |
| `ViewTitration` | not called |  |  |  |   |
| `_AddEquationViewOnLive` | not called |  |  |  |   |
| `_AddNewEquationView` | not called |  |  |  |   |
| `_BackupLayouts` | not called |  |  |  |   |
| `_EditScale` | not called |  |  |  |   |
| `_EquationViewSetup` | not called |  |  |  |   |
| `_PearsonViewSetup` | not called |  |  |  |   |
| `_PhysicalZoomProperties` | not called |  |  |  |   |
| `_PhysicalZoomPropertiesCursor` | not called |  |  |  |   |
| `_RatioViewSetup` | not called |  |  |  |   |
| `_RestoreLayouts` | not called |  |  |  |   |
| `_TitrationCalibration` | not called |  |  |  |   |
| `ChangeOverlayCol` | not called |  |  |  |   |
| `DecOverlayTransparency` | not called |  |  |  |   |
| `DecTransparency` | not called |  |  |  |   |
| `HideBinary` | not called |  |  |  |   |
| `HideColor` | not called |  |  |  |   |
| `IncOverlayTransparency` | not called |  |  |  |   |
| `IncTransparency` | not called |  |  |  |   |
| `OverlayColor` | not called |  |  |  |   |
| `OverlayTransparency` | not called |  |  |  |   |
| `ViewBinary` | not called |  |  |  |   |
| `ViewColor` | not called |  |  |  |   |
| `ViewColor_Overlay` | not called |  |  |  |   |
| `ViewMolecules` | not called |  |  |  |   |
| `ViewOverlay` | not called |  |  |  |   |
| `ViewUserDef` | not called |  |  |  |   |
| `MoveProbeToCenter` | not called |  |  |  |   |
| `ProbeOptions` | not called |  |  |  |   |
| `ProbeProperties` | not called |  |  |  |   |
| `ShowMoleculeProbe` | not called |  |  |  |   |
| `ShowProbe` | not called |  |  |  |   |
| `ToggleMoleculeProbe` | not called |  |  |  |   |
| `ToggleProbe` | not called |  |  |  |   |
| `_MoleculeProbeProperties` | not called |  |  |  |   |
| `_ProbeProperties` | not called |  |  |  |   |
| `ShowAUXPoints` | not called |  |  |  |   |
| `ShowAnnotations` | not called |  |  |  |   |
| `DefaultScalePosition` | not called |  |  |  |   |
| `LockScale` | not called |  |  |  |   |
| `ScaleProperties` | not called |  |  |  |   |
| `ShowScale` | not called |  |  |  |   |
| `ToggleScale` | not called |  |  |  |   |
| `_ScaleProperties` | not called |  |  |  |   |
| `ShowUserEventInfo` | not called |  |  |  |   |
| `ToggleUserEventInfo` | not called |  |  |  |   |
| `_UserEventInfoProperties` | not called |  |  |  |   |
| `GetZoom` | ran | 1.0 |  |  |   |
| `SetZoomViewPoint` | not called |  |  |  |   |
| `Zoom` | not called |  |  |  |   |
| `ZoomAndCenter` | not called |  |  |  |   |
| `ZoomBestFit` | not called |  |  |  |   |
| `ZoomFitToScreen` | not called |  |  |  |   |
| `ZoomIn` | not called |  |  |  |   |
| `ZoomInAtCursor` | not called |  |  |  |   |
| `ZoomOut` | not called |  |  |  |   |
| `ZoomOutAtCursor` | not called |  |  |  |   |
| `_Create3DMovie` | not called |  |  |  |   |
| `GetCurrentViewIndex` | ran | -1 |  |  |   |
| `GetCurrentViewProjection` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetImageOriginalStatus` | needs arguments | error: Bad number of parameters |  |  |   |
| `GetOpenedViewList` | needs arguments | error: Bad number of parameters |  |  |   |
| `PictureMouseOperation` | not called |  |  |  |   |
| `SyncLocus` | not called |  |  |  |   |
| `Thumbnails` | not called |  |  |  |   |
| `TranslateOriginalStatusToText` | not called |  |  |  |   |

## Visualization

| Function | Result | Answer | Dialog | Changed | Put back |
|---|---|---|---|---|---|
| `ProcessZLUTs` | not called |  |  |  |   |
| `ProcessZLUTsND` | not called |  |  |  |   |
| `ShowZLUTsWindow` | not called |  |  |  |   |
| `ZLUTsOn` | not called |  |  |  |   |
| `ConvertSpectralGroupsToChannels` | not called |  |  |  |   |
| `CreateLUTs` | not called |  |  |  |   |
| `EnableLUTs` | not called |  |  |  |   |
| `Inmap` | not called |  |  |  |   |
| `LUTsLoadSettings` | not called |  |  |  |   |
| `LUTsSaveSettings` | not called |  |  |  |   |
| `LUTs_AutoScale` | not called |  |  |  |   |
| `LUTs_AutoScaleOneComp` | not called |  |  |  |   |
| `LUTs_Copy` | not called |  |  |  |   |
| `LUTs_GetGradient` | not called |  |  |  |   |
| `LUTs_GetLowHighGamma` | not called |  |  |  |   |
| `LUTs_GetLowHighGammaEx` | not called |  |  |  |   |
| `LUTs_GetOverSaturationColor` | not called |  |  |  |   |
| `LUTs_GetPercentil` | not called |  |  |  |   |
| `LUTs_GetSpectCustomColor` | not called |  |  |  |   |
| `LUTs_GetSpectGainOffsetGamma` | not called |  |  |  |   |
| `LUTs_GetSpectGroupColor` | not called |  |  |  |   |
| `LUTs_GetUnderSaturationColor` | not called |  |  |  |   |
| `LUTs_KeepAutoScale` | not called |  |  |  |   |
| `LUTs_Paste` | not called |  |  |  |   |
| `LUTs_Reset` | not called |  |  |  |   |
| `LUTs_ResetOneComp` | not called |  |  |  |   |
| `LUTs_SetGradient` | not called |  |  |  |   |
| `LUTs_SetLowHighGamma` | not called |  |  |  |   |
| `LUTs_SetLowHighGammaEx` | not called |  |  |  |   |
| `LUTs_SetOverSaturationColor` | not called |  |  |  |   |
| `LUTs_SetPercentil` | not called |  |  |  |   |
| `LUTs_SetSaveOversaturationState` | not called |  |  |  |   |
| `LUTs_SetSpectCustomColor` | not called |  |  |  |   |
| `LUTs_SetSpectGainOffsetGamma` | not called |  |  |  |   |
| `LUTs_SetSpectGroupColor` | not called |  |  |  |   |
| `LUTs_SetSpectGroups` | not called |  |  |  |   |
| `LUTs_SetUnderSaturationColor` | not called |  |  |  |   |
| `ProcessLUTs` | not called |  |  |  |   |
| `ProcessLUTsND` | not called |  |  |  |   |
| `SetSpectralColorMode` | not called |  |  |  |   |
| `ShowLUTsWindow` | not called |  |  |  |   |
| `ToggleKeepAutoScaleLUTs` | not called |  |  |  |   |
| `ToggleLUTs` | not called |  |  |  |   |
| `ToggleLUTsWnd` | not called |  |  |  |   |
| `TogglePixelSaturationIndication` | not called |  |  |  |   |
| `_LUTsLoadSettings` | not called |  |  |  |   |
| `_LUTsSaveSettings` | not called |  |  |  |   |
| `_LUTs_CreateCustom` | not called |  |  |  |   |
| `_LUTs_SetBrightfieldOpacity` | not called |  |  |  |   |
