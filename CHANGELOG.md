# Changelog

All notable changes to the Shortcuts Playground plugin are documented in this file. The skill-level changelog lives at `skills/shortcuts-playground/CHANGELOG.md`.

## [1.2.0] — 2026-04-13

### Fixed (important behavior)
- **Agent reconnaissance failure mode.** The `shortcut-builder` agent could go into unbounded exploration when an action identifier was allowlisted but lacked a documented parameter schema — it would query the user's local `~/Library/Shortcuts/Shortcuts.sqlite`, the ToolKit database, Google Drive backups, and system binaries looking for examples. Reproduced with the prompt *"Build a shortcut that gets my reminders due today and lets me select multiple ones to reschedule them"* against `is.workflow.actions.setters.reminders`. The agent now stops and escalates to the user with three clean options (best-effort guess, simpler alternative, user-provided example) and never touches local databases during authoring.

### Removed
- **All references to `Shortcuts.sqlite` / `ZSHORTCUTACTIONS` / ToolKit sqlite from user-facing skill docs.** Purged from `SKILL.md` (rule #54 rewritten), `PARAMETER_TYPES.md` (verification section replaced with character ordinal table), `BEST_PRACTICES.md` (batch install verification bullet), `TOOLKIT_SNAPSHOT.md` (rewritten), and the skill's internal `README.md` (installed-batch-verification section deleted).
- **`scripts/install_and_verify_shortcuts.py`** — deleted. The script was only referenced from the now-removed docs.
- **Optional local ToolKit sqlite expansion in `validate_shortcut.py`** — removed. The bundled `data/toolkit-v63-tool-ids.json` (1,794 identifiers) is now the only allowlist source, making the validator deterministic and sqlite-free.
- **`import sqlite3`** — no longer present anywhere in the plugin's runtime code.

### Added (agent system prompt)
- **Hard rules against reconnaissance** in `agents/shortcut-builder.md`:
  - Never inspect `~/Library/Shortcuts/Shortcuts.sqlite` for authoring discovery (post-runtime debugging use is also removed from the docs entirely).
  - Never inspect `~/Library/Shortcuts/ToolKit/*.sqlite` or any ToolKit database.
  - Never search `~/Library/CloudStorage`, `~/Library/Mobile Documents`, `/System/Applications/Shortcuts.app`, or `/Applications/Shortcuts.app` for template shortcuts.
  - Never write inline Python that imports `sqlite3` or `objc`.
  - When an allowlisted action has no documented parameter schema, **stop and ask the user** with three concrete options.
- **Bounded research budget** — the agent may use up to 8 total Read/Grep/Glob calls before authoring or escalating. Prevents the unbounded-exploration failure mode even when no single rule fires.

### Changed
- **Rule #54 in `SKILL.md`** rewritten from "Verify installed shortcut behavior against Shortcuts.sqlite" to "Never inspect the user's local system for authoring discovery" — the old rule was the specific trigger that the agent was misapplying.
- **`TOOLKIT_SNAPSHOT.md`** retitled and rewritten to remove the "to avoid extracting ToolKit sqlite" framing. The snapshot just exists; no sqlite backstory.

### Verified
- Self-test passes.
- Hello World regression produces signed `.shortcut`.
- Federico's exact failing reminders prompt now triggers the escalation path: the agent stops, presents three options, makes zero tool calls to Shortcuts.sqlite / ToolKit / Google Drive / system paths.

## [1.1.0] — 2026-04-13

### Added
- `bin/shortcuts-playground-selftest` — post-install smoke test that verifies Python 3.10+, the macOS `shortcuts` CLI, plugin root resolution, bundled data files, a validator pass on an embedded golden XML, and a full `sign-shortcut` archive + sign round trip to a temp dir. Exits with specific error messages on any failure. Supports `SHORTCUTS_PLAYGROUND_SELFTEST_SKIP_SIGN=1` for CI environments without the `shortcuts` CLI.
- `commands/build.md` — `/shortcuts-playground:build <brief>` slash command. Explicit entry point that delegates to the `shortcut-builder` agent with the brief as `$ARGUMENTS`. Complements natural-language auto-invocation.
- `.claude-plugin/marketplace.json` — single-plugin marketplace manifest so the plugin directory can be added via `claude plugin marketplace add /path/to/shortcuts-playground-plugin`.

### Changed
- **README.md** — rewrote the Requirements section to clearly state the Python 3.10+ requirement (`/usr/bin/python3` on older macOS is 3.9.6 and will fail). Added a Health Check section that walks readers through post-install verification in four commands. Added a Configuration section documenting the three ways to set `userConfig` values: interactive `/plugin` TUI, manual `settings.json` edit under `pluginConfigs`, or direct `CLAUDE_PLUGIN_OPTION_*` env var override. Added a Development section explaining the directory-vs-git marketplace cache behavior (directory installs read from source; git installs read from cache and require `claude plugin update`). Added the slash command to the Usage section.
- **Plugin version bumped from 1.0.0 → 1.1.0** (minor — additive features, no breaking changes).

### Verified
- Full test matrix on v1.1.0 (8 checks, all green):
  - T1: `claude plugin validate` on plugin.json and marketplace.json.
  - T2: `shortcuts-playground-selftest` from plugin root — all 6 sub-checks pass.
  - T3: `shortcuts-playground-selftest` from `/tmp` without `CLAUDE_PLUGIN_ROOT` — fallback path resolution works.
  - T4: negative self-test (`CLAUDE_PLUGIN_ROOT=/tmp/nonexistent`) exits 1 with 6 specific error messages.
  - T5: `/shortcuts-playground:build` slash command via headless `claude -p` produces a signed `.shortcut`.
  - T6: natural-language auto-invocation (no slash command) produces a signed `.shortcut`.
  - T7: validator hook blocks a write with an unknown action identifier in headless mode.
  - T8: re-validation of every archive XML produced in the matrix — all pass.

## [1.0.0] — 2026-04-13

### Added
- Initial plugin conversion from the standalone `generate-shortcuts-skill` Claude Code skill.
- `skills/shortcuts-playground/` — full knowledge base carried over verbatim, with `SKILL.md` adapted to invoke the new bin wrappers instead of `python3 scripts/*.py` calls. Includes `BEST_PRACTICES.md`, `ACTIONS.md`, `APPINTENTS.md`, `PARAMETER_TYPES.md`, `VARIABLES.md`, `CONTROL_FLOW.md`, `FILTERS.md`, `EXAMPLES.md`, `THIRD_PARTY_ACTIONS.md`, `TOOLKIT_SNAPSHOT.md`, `ICONS_AND_COLORS.md`, `PLIST_FORMAT.md`, the golden-shortcuts reference library, and the ToolKit v63 metadata bundle.
- `agents/shortcut-builder.md` — specialized agent that owns the full design → build → validate → sign → archive loop, keeping the main thread free of the 1.2 MB knowledge base.
- `hooks/hooks.json` + `hooks/auto-validate.sh` — `PostToolUse` hook that auto-runs the Craig Loop validator on every `Write`/`Edit` that produces a Shortcuts plist file. Exits with code 2 + stderr on failure so validator output is injected back into Claude's context for the next iteration.
- `bin/validate-shortcut` — wrapper around `validate_shortcut.py`.
- `bin/resolve-icon` — wrapper around `select_shortcut_icon_color.py`.
- `bin/sign-shortcut` — combines archive + `shortcuts sign` into one command; respects `output_dir` and `signing_mode` userConfig values.
- `userConfig.output_dir` and `userConfig.signing_mode` — prompted at install time; falls back to `~/Documents/Shortcuts Playground` and `anyone` respectively.

### Migration notes from the standalone skill
- The Craig Loop is now **automatic**. Previously the model had to remember to invoke `validate_shortcut.py` after every `Write`; now the hook runs it unconditionally.
- All paths in `SKILL.md` that referenced `python3 scripts/<name>.py` now use the bin wrappers (`validate-shortcut`, `resolve-icon`, `sign-shortcut`) or `${CLAUDE_PLUGIN_ROOT}`-prefixed paths for the dev-only regression scripts.
- The archive directory is configurable via `userConfig.output_dir` instead of the hardcoded `~/Agent/Shortcuts Playground/` path.
- The skill name namespace is now `shortcuts-playground:shortcuts-playground`; the original `shortcuts-generator` name remains available via the parallel `~/.claude/skills/generate-shortcuts-skill/` installation until it is explicitly removed.
