# Shortcuts Playground Plugins

This repository ships Shortcuts Playground for two agent runtimes:

| Folder | Runtime | Contents |
|--------|---------|----------|
| [`claude/`](claude/) | Claude Code | Full Claude plugin with skill, slash commands, specialized agents, PostToolUse validation hook, and PATH wrapper commands. |
| [`codex/`](codex/) | Codex | Codex plugin with `.codex-plugin/plugin.json`, bundled skill, validator/signing scripts, and Codex icon assets. |

The root `.claude-plugin/marketplace.json` is a Claude marketplace that installs the Claude plugin from `./claude`.

The root `.agents/plugins/marketplace.json` is a Codex marketplace that installs the Codex plugin from `./codex`.

## Codex Install

Codex can read the repo marketplace at `.agents/plugins/marketplace.json`. For manual local testing, install or cache the `codex/` plugin as a local Codex plugin and enable `shortcuts-playground@shortcuts-playground-local`.

The Codex package intentionally omits Claude-only features: slash commands, specialized agents, PostToolUse hooks, and PATH wrapper bins. The Codex skill calls its bundled scripts directly.

## Claude Install

Add this repository as a Claude marketplace. Its marketplace entry points to `./claude`, where the Claude Code plugin lives.

## Icon

The Codex plugin icon in `codex/assets/` is a PNG conversion of the supplied `Shortcuts Playground.icon` package.
