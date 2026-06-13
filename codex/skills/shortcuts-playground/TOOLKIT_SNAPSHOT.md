# Action ID Snapshots

This skill bundles precomputed action-ID allowlists so it can be shared without requiring any extra setup on the user's machine.

## Bundled files

- `data/toolkit-v63-tool-ids.json` - flat list of 1,794 action/intent identifiers from the original ToolKit snapshot.
- `data/toolkit-v78-tool-ids.json` - flat list of 2,731 action/intent identifiers from macOS 27 Golden Gate build 26A5353q.
- `data/toolkit-v78-ios27-tool-ids.json` - flat list of 1,206 action/intent identifiers from an iOS 27.0 Simulator ToolKit v78 database.
- `data/toolkit-v78-first-party-parameter-keys.json` - compact first-party ToolKit v78 parameter-key catalog used by `lookup_action_grounding.py` for broad AppIntent/schema discovery.
- `data/toolkit-v78-trigger-parameter-keys.json` - compact ToolKit v78 automation trigger catalog with trigger IDs, Python names, parameter keys, and output type identifiers.
- `data/macos27-shortpy-grounding.json` - reviewed static Apple-derived macOS 27 grounding catalog with ToolKit `pythonName`, Apple Shortpy keyword, ToolRenderer utility, and ShortcutsLanguage syntax evidence.

Only the identifiers needed for validation are bundled. This keeps the plugin lightweight compared with the full ToolKit SQLite metadata.

## Validator behavior

`scripts/validate_shortcut.py` loads packaged `data/toolkit-v*-tool-ids.json` files according to the target OS version and target platform, then augments those snapshots with the markdown references (`ACTIONS.md`, `APPINTENTS.md`, `THIRD_PARTY_ACTIONS.md`). OS 27 snapshots include both macOS 27 and iOS 27 Simulator ToolKit evidence, but iOS-only snapshot rows are rejected for the default macOS platform target. It also target-gates the reviewed Automators OS 26 to 27 parameter deltas, so OS 27-only parameter keys are rejected on macOS 26 targets even when the action identifier itself predates OS 27.

The default OS target is `auto`: on macOS it reads `sw_vers -productVersion`; when the host cannot be detected it falls back to macOS 26 rather than latest. Override with `--target-macos 26`, `--target-macos 27`, or `--target-macos latest`. The same override is available via `SHORTCUTS_PLAYGROUND_TARGET_MACOS`.

The default platform target is `macos`. Override with `--target-platform ios` / `SHORTCUTS_PLAYGROUND_TARGET_PLATFORM=ios` for iPhone/iPad authoring, or `--target-platform all` only when intentionally validating every packaged platform.

This keeps validation portable and self-contained while avoiding false compatibility on machines that do not have macOS 27 installed.

## macOS 27 scope

The v78 snapshot expands validation coverage for shortcuts created on macOS 27. It is only active when the target is macOS 27+ or `latest`. It is an identifier allowlist, not a complete authoring schema. If a v78-only action identifier is present but its parameter serialization is not documented in the reference files or a golden XML, do not guess the payload. Ask for an exported XML sample or use a documented fallback.

OS 27-era parameter keys are also target-gated. Examples include `WFAllowWebSearch` on Use Model, `interpretAsMarkdown` on Notes actions, `WFAvoidTolls`/`WFAvoidHighways` on Maps route actions, `WFAppsExcept` on Hide/Quit App, `imageFile` on Scan QR or Barcode / Extract from Image, and `contents` on Safari Create Tab Group.

## iOS 27 simulator scope

The iOS 27 Simulator v78 snapshot adds iOS-only AppIntents that are not present in the macOS ToolKit database, such as `com.apple.HearingApp.MuteVolumeIntent` and iOS Settings/Wallet/Health/Fitness identifiers. These identifiers are included for iOS/iPadOS shortcut authoring and are also target-gated to OS 27+. They do not validate for the default macOS target; use `--target-platform ios` only when authoring for iPhone/iPad. Do not use them for macOS shortcuts unless a macOS ToolKit snapshot or exported shortcut confirms runtime support.

## Apple-derived grounding catalog

`data/macos27-shortpy-grounding.json` is a portable metadata catalog generated from local macOS 27 Shortcuts ToolKit, ToolRenderer, WorkflowKit source-export, and installed sample evidence. It is static package data: normal validation does not read the user's live Shortcuts database and does not load private frameworks.

Use `scripts/lookup_action_grounding.py` to inspect it:

```bash
python3 scripts/lookup_action_grounding.py --identifier additemtolist --target-macos 27
python3 scripts/lookup_action_grounding.py --python-name com_apple_shortcuts_add_item_to_list --json
```

The grounding catalog can improve authoring confidence, but it does not override target availability. If `validate_shortcut.py --target-macos 26` rejects a v78-only identifier or parameter key, the static grounding entry is only a note that the action or parameter exists in OS 27-era ToolKit metadata.

`lookup_action_grounding.py` computes per-action availability from the packaged ToolKit snapshots, not from the grounding catalog's source OS. Older actions that appear in the macOS 27 grounding catalog still remain available to older targets when they are present in `toolkit-v63`.

## Automation trigger metadata

`data/toolkit-v78-trigger-parameter-keys.json` packages the 42 automation triggers exposed in local macOS 27 and iOS 27 Simulator ToolKit v78 databases. This includes identifiers such as `com.apple.shortcuts.WFTimeOfDayTrigger.at_time_on_recurring_day`, Apple Shortpy-style names such as `when_app_opened`, trigger parameter keys, and raw output type identifiers.

This catalog is discovery metadata only. It does not prove importable Personal Automation or inline trigger serialization, and the validator does not validate top-level automation trigger payloads. Use [AUTOMATION_TRIGGERS.md](AUTOMATION_TRIGGERS.md) and `lookup_action_grounding.py` to request precise exported samples or to enrich future authoring work, not to emit automation database rows.
