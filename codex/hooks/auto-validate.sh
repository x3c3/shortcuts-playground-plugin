#!/usr/bin/env bash
# Shortcuts Playground - Codex PostToolUse auto-validator.
#
# Codex reports file edits through apply_patch, whose hook payload contains the
# patch text rather than a direct file_path. This hook extracts touched XML-ish
# files, sniffs for Shortcuts workflow plists, and feeds validator failures back
# into Codex as PostToolUse feedback.

set -u

PLUGIN_ROOT="${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-}}"
if [ -z "$PLUGIN_ROOT" ]; then
  PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fi

VALIDATOR="$PLUGIN_ROOT/skills/shortcuts-playground/scripts/validate_shortcut.py"
if [ ! -f "$VALIDATOR" ]; then
  exit 0
fi

PY="${SHORTCUTS_PLAYGROUND_PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  exit 0
fi
if ! "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
  exit 0
fi

INPUT="$(cat)"
FILE_PATHS="$(printf '%s' "$INPUT" | "$PY" -c '
import json
import os
import re
import sys

try:
    data = json.loads(sys.stdin.read() or "{}")
except Exception:
    sys.exit(0)

cwd = data.get("cwd") or os.getcwd()
tool_input = data.get("tool_input") or {}
paths = []

def add(path):
    if not isinstance(path, str) or not path:
        return
    if path == "/dev/null":
        return
    if not os.path.isabs(path):
        path = os.path.abspath(os.path.join(cwd, path))
    if path not in paths:
        paths.append(path)

for key in ("file_path", "path"):
    add(tool_input.get(key))

command = tool_input.get("command")
if isinstance(command, str):
    for match in re.finditer(r"^\*\*\* (?:Add|Update) File: (.+)$", command, re.MULTILINE):
        add(match.group(1).strip())
    for match in re.finditer(r"^\*\*\* Move to: (.+)$", command, re.MULTILINE):
        add(match.group(1).strip())

for path in paths:
    print(path)
' 2>/dev/null || true)"

if [ -z "$FILE_PATHS" ]; then
  exit 0
fi

FAILURES=""
while IFS= read -r FILE_PATH; do
  if [ -z "$FILE_PATH" ]; then
    continue
  fi

  if [ ! -f "$FILE_PATH" ]; then
    continue
  fi

  case "$FILE_PATH" in
    *.xml|*.shortcut) : ;;
    *) continue ;;
  esac

  if ! /usr/bin/grep -q 'WFWorkflowActions' "$FILE_PATH" 2>/dev/null; then
    continue
  fi

  if VALIDATOR_OUT="$("$PY" "$VALIDATOR" "$FILE_PATH" 2>&1)"; then
    continue
  fi

  FAILURE="shortcuts-playground validator failed for $FILE_PATH

$VALIDATOR_OUT"
  if [ -z "$FAILURES" ]; then
    FAILURES="$FAILURE"
  else
    FAILURES="$FAILURES

$FAILURE"
  fi
done <<EOF
$FILE_PATHS
EOF

if [ -z "$FAILURES" ]; then
  exit 0
fi

printf '%s' "$FAILURES" | "$PY" -c '
import json
import sys

reason = sys.stdin.read()
print(json.dumps({
    "decision": "block",
    "reason": reason,
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": reason,
    },
}))
'
