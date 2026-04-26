# Action ID Snapshot

This skill bundles a precomputed action-ID allowlist so it can be shared without requiring any extra setup on the user's machine.

## Bundled file

- `data/toolkit-v63-tool-ids.json` — flat list of 1,794 action/intent identifiers used by the validator as the primary allowlist.

Only the identifiers needed for validation are bundled. This keeps the plugin lightweight (~98 KB vs. several megabytes for the full metadata set).

## Validator behavior

`scripts/validate_shortcut.py` uses `data/toolkit-v63-tool-ids.json` as the primary allowlist source, then augments it with the markdown references (`ACTIONS.md`, `APPINTENTS.md`, `THIRD_PARTY_ACTIONS.md`).

This keeps validation portable and self-contained.
