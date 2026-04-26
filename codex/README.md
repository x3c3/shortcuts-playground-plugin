# Shortcuts Playground for Codex

Codex plugin for building, remixing, validating, archiving, and signing Apple Shortcuts.

## Structure

```text
codex/
├── .codex-plugin/plugin.json
├── assets/
│   ├── icon.png
│   ├── icon-small.png
│   └── logo.png
└── skills/
    └── shortcuts-playground/
```

This package follows the Codex plugin structure: the manifest lives at `.codex-plugin/plugin.json`, skills live under `skills/`, and visual assets live under `assets/`.

## Runtime Differences from Claude

The Codex package intentionally omits Claude-only plugin features:

- Slash commands
- Specialized Claude agents
- PostToolUse hooks
- PATH wrapper commands under `bin/`
- Claude `userConfig`

The bundled skill uses direct script paths instead:

```bash
SKILL_DIR=/path/to/codex/skills/shortcuts-playground
python3 "$SKILL_DIR/scripts/select_shortcut_icon_color.py" --prompt "weather shortcut"
python3 "$SKILL_DIR/scripts/validate_shortcut.py" /path/to/Shortcut.xml
"$SKILL_DIR/scripts/sign_shortcut.sh" /path/to/Shortcut.xml --name "Shortcut Name"
```

Set `SHORTCUTS_PLAYGROUND_OUTPUT_DIR` and `SHORTCUTS_PLAYGROUND_SIGNING_MODE` to customize signing output.
