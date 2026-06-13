# Automation Triggers

ToolKit v78 exposes automation trigger metadata for OS 27. This reference is packaged as static data so agents can inspect trigger identifiers, Apple Shortpy-style Python names, parameter keys, and output types without reading a user's live Shortcuts databases.

This is **research metadata only**. Shortcuts Playground currently builds and validates workflow action plists. It does not create or import Personal Automation records, inline automation headers, or Shortcuts database rows such as `ZUNIFIEDTRIGGER`. Do not author automations from this table until an exported shortcut/automation payload proves the top-level plist or database serialization.

Use the lookup helper for targeted searches:

```bash
python3 scripts/lookup_action_grounding.py --identifier com.apple.shortcuts.WFTimeOfDayTrigger.at_time_on_recurring_day --target-macos 27
python3 scripts/lookup_action_grounding.py --python-name when_app_opened --json
python3 scripts/lookup_action_grounding.py --query "wi-fi trigger" --json
```

## Packaged Metadata

- Source catalog: `data/toolkit-v78-trigger-parameter-keys.json`
- Trigger count: 42
- Platforms observed: macOS 27 ToolKit v78 and iOS 27 Simulator ToolKit v78
- Parameter descriptions are intentionally omitted. Display names and key/type metadata are included.

## Trigger Catalog

| Display Name | Identifier | Python Name | Parameters | Output Types |
|--------------|------------|-------------|------------|--------------|
| Airplane Mode | `com.apple.shortcuts.WFAirplaneModeTrigger.changes` | `when_airplane_mode_changes` | `WFAirplaneModeType` | `none` |
| Alarm | `com.apple.shortcuts.WFAlarmTrigger.any_alarm` | `when_alarm_any_alarm` | `WFAlarmState` | `none` |
| Alarm | `com.apple.shortcuts.WFAlarmTrigger.specific_alarm` | `when_alarm_specific_alarm` | `WFAlarms`, `WFAlarmState` | `none` |
| App | `com.apple.shortcuts.WFAppInFocusTrigger.opened` | `when_app_opened` | `WFSelectedApps`, `WFAppState` | `none` |
| Arrive | `com.apple.shortcuts.WFArriveLocationTrigger.enter_location` | `when_arrive_enter_location` | `WFArriveLocation` | `none` |
| Arrive | `com.apple.shortcuts.WFArriveLocationTrigger.enter_location_between` | `when_arrive_enter_location_between` | `WFArriveLocation`, `WFArriveStartTime`, `WFArriveEndTime` | `none` |
| Battery Level | `com.apple.shortcuts.WFBatteryLevelTrigger.equal` | `when_battery_level_equal` | `WFBatteryLevel`, `WFBatteryLevelComparison` | `none` |
| Bluetooth | `com.apple.shortcuts.WFBluetoothTrigger.any_connection_changes` | `when_bluetooth_any_connection_changes` | `WFBluetoothConnectionType` | `none` |
| Bluetooth | `com.apple.shortcuts.WFBluetoothTrigger.selected_connection_changes` | `when_bluetooth_selected_connection_changes` | `WFBluetoothConnectionType`, `WFSelectedDevices` | `none` |
| CarPlay | `com.apple.shortcuts.WFCarPlayConnectionTrigger.changes` | `when_car_play_changes` | `WFCarPlayConnectionType` | `none` |
| External Drive | `com.apple.shortcuts.WFDiskMountTrigger.external_drive` | `when_external_drive_external_drive` | none | `file` |
| Email | `com.apple.shortcuts.WFEmailTrigger.senders_are` | `when_email_senders_are` | `WFEmailSender`, `WFEmailAccount`, `WFEmailRecipient` | `com.apple.shortcuts.WFEmailContentItem` |
| Email | `com.apple.shortcuts.WFEmailTrigger.senders_are_and_subject_contains` | `when_email_senders_are_and_subject_contains` | `WFEmailSender`, `WFEmailSubjectContains`, `WFEmailAccount`, `WFEmailRecipient` | `com.apple.shortcuts.WFEmailContentItem` |
| Email | `com.apple.shortcuts.WFEmailTrigger.subject_contains` | `when_email_subject_contains` | `WFEmailSubjectContains`, `WFEmailAccount`, `WFEmailRecipient` | `com.apple.shortcuts.WFEmailContentItem` |
| Display | `com.apple.shortcuts.WFExternalDisplayTrigger.` | `when_display_wfexternaldisplaytrigger` | `WFConnectionType` | `com.apple.shortcuts.WFDisplayContentItem` |
| File | `com.apple.shortcuts.WFFileTrigger.file_modified` | `when_file_file_modified` | none | `file` |
| Folder | `com.apple.shortcuts.WFFolderTrigger.folder_changed` | `when_folder_folder_changed` | none | `none` |
| Keyboard | `com.apple.shortcuts.WFKeyboardTrigger.connection_changes` | `when_keyboard_connection_changes` | `WFConnectionType` | `bool` |
| Leave | `com.apple.shortcuts.WFLeaveLocationTrigger.leave_location` | `when_leave_leave_location` | `WFLeaveLocation` | `none` |
| Leave | `com.apple.shortcuts.WFLeaveLocationTrigger.leave_location_between` | `when_leave_leave_location_between` | `WFLeaveLocation`, `WFLeaveStartTime`, `WFLeaveEndTime` | `none` |
| Low Power Mode | `com.apple.shortcuts.WFLowPowerModeTrigger.changes` | `when_low_power_mode_changes` | `WFLowPowerModeType` | `none` |
| Message | `com.apple.shortcuts.WFMessageTrigger.contains` | `when_message_contains` | `WFMessageContains` | `com.apple.shortcuts.WFMessageContentItem` |
| Message | `com.apple.shortcuts.WFMessageTrigger.senders_are` | `when_message_senders_are` | `WFMessageSender` | `com.apple.shortcuts.WFMessageContentItem` |
| Message | `com.apple.shortcuts.WFMessageTrigger.senders_are_and_contains` | `when_message_senders_are_and_contains` | `WFMessageSender`, `WFMessageContains` | `com.apple.shortcuts.WFMessageContentItem` |
| NFC | `com.apple.shortcuts.WFNFCTrigger.scan_tag` | `when_nfc_scan_tag` | `WFNFCTag` | `none` |
| Notification | `com.apple.shortcuts.WFNotificationTrigger.received` | `when_notification_received` | `SelectedApps` | `com.apple.shortcuts.WFNotificationContentItem` |
| Charger | `com.apple.shortcuts.WFPlugInTrigger.changes` | `when_charger_changes` | `WFConnectionType` | `none` |
| Screenshot | `com.apple.shortcuts.WFScreenshotTrigger.saved` | `when_screenshot_saved` | `ScreenshotLocations` | `file` |
| Sleep | `com.apple.shortcuts.WFSleepTrigger.` | `when_sleep_wfsleeptrigger` | `WFSleepMode` | `none` |
| Sound Recognition | `com.apple.shortcuts.WFSoundRecognitionTrigger.sound_recognition` | `when_sound_recognition_sound_recognition` | `WFSounds` | `none` |
| Stage Manager | `com.apple.shortcuts.WFStageManagerTrigger.on` | `when_stage_manager_on` | `WFStageManagerType` | `none` |
| Time of Day | `com.apple.shortcuts.WFTimeOfDayTrigger.around_sunrise_on_recurring_day` | `when_time_of_day_around_sunrise_on_recurring_day` | `WFTimeOffset`, `WFRecurrence` | `none` |
| Time of Day | `com.apple.shortcuts.WFTimeOfDayTrigger.around_sunset_on_recurring_day` | `when_time_of_day_around_sunset_on_recurring_day` | `WFTimeOffset`, `WFRecurrence` | `none` |
| Time of Day | `com.apple.shortcuts.WFTimeOfDayTrigger.at_time_on_recurring_day` | `when_time_of_day_at_time_on_recurring_day` | `WFTime`, `WFRecurrence` | `none` |
| Focus | `com.apple.shortcuts.WFUserFocusActivityTrigger.enable` | `when_focus_enable` | `WFFocusMode`, `WFFocusEvent` | `none` |
| Wallet | `com.apple.shortcuts.WFWalletTransactionTrigger.tap` | `when_wallet_tap` | `WFWalletCards`, `WFWalletMerchantTypes`, `WFWalletMerchants` | `com.apple.shortcuts.WFWalletTransactionContentItem` |
| Wi-Fi | `com.apple.shortcuts.WFWifiTrigger.connect_to_any` | `when_wi_fi_connect_to_any` | `WFRunAfterConnectionInterruption` | `none` |
| Wi-Fi | `com.apple.shortcuts.WFWifiTrigger.connect_to_selected` | `when_wi_fi_connect_to_selected` | `WFNetworks`, `WFRunAfterConnectionInterruption` | `none` |
| Wi-Fi | `com.apple.shortcuts.WFWifiTrigger.disconnect_from_any` | `when_wi_fi_disconnect_from_any` | none | `none` |
| Wi-Fi | `com.apple.shortcuts.WFWifiTrigger.disconnect_from_selected` | `when_wi_fi_disconnect_from_selected` | `WFNetworks` | `none` |
| Apple Watch Workout | `com.apple.shortcuts.WFWorkoutTrigger.any` | `when_apple_watch_workout_any` | `WFWorkoutEvent` | `none` |
| Apple Watch Workout | `com.apple.shortcuts.WFWorkoutTrigger.specific` | `when_apple_watch_workout_specific` | `WFWorkoutEvent`, `WFWorkoutTypes` | `none` |

## Current Authoring Boundary

- Treat trigger identifiers and parameter keys as discovery aids only.
- Use this catalog to understand Apple's Shortpy trigger mapping and to request precise exported samples.
- Do not claim trigger creation support until we can validate importable workflow/automation serialization end to end.
