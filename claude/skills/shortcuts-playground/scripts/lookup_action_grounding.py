#!/usr/bin/env python3
"""Look up reviewed Apple-derived Shortcuts grounding metadata.

This helper reads the packaged static macOS 27 Shortpy catalog and a compact
ToolKit v78 first-party parameter-key snapshot. It never reads the user's live
Shortcuts databases and never calls private Apple frameworks. Use it as an
authoring aid when a macOS 27 action or Apple Shortpy function name needs
additional grounding beyond the markdown references.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Any


TARGET_MACOS_ENV_VARS = (
    "SHORTCUTS_PLAYGROUND_TARGET_MACOS",
    "CLAUDE_PLUGIN_OPTION_TARGET_MACOS",
)
TOOLKIT_SNAPSHOT_MIN_MACOS_MAJOR = {
    "toolkit-v78": 27,
    "toolkit-v78-ios27": 27,
}


def toolkit_snapshot_min_macos_major(version: str | None) -> int | None:
    if not isinstance(version, str) or not version:
        return None
    if version in TOOLKIT_SNAPSHOT_MIN_MACOS_MAJOR:
        return TOOLKIT_SNAPSHOT_MIN_MACOS_MAJOR[version]
    import re

    match = re.search(r"v(\d+)", version)
    if match and int(match.group(1)) >= 78:
        return 27
    return None


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def catalog_path(base: Path | None = None) -> Path:
    return (base or skill_dir()) / "data/macos27-shortpy-grounding.json"


def parameter_catalog_path(base: Path | None = None) -> Path:
    return (base or skill_dir()) / "data/toolkit-v78-first-party-parameter-keys.json"


def load_catalog(base: Path | None = None) -> dict[str, Any]:
    path = catalog_path(base)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_parameter_catalog(base: Path | None = None) -> dict[str, Any]:
    path = parameter_catalog_path(base)
    if not path.exists():
        return {"tools": {}}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_identifier_min_macos(base: Path | None = None) -> dict[str, int | None]:
    """Return the earliest packaged snapshot availability for each identifier."""

    data_dir = (base or skill_dir()) / "data"
    availability: dict[str, int | None] = {}
    for path in sorted(data_dir.glob("toolkit-v*-tool-ids.json")):
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        version = payload.get("version") or path.stem.replace("-tool-ids", "")
        min_macos = toolkit_snapshot_min_macos_major(version)
        ids = set(payload.get("ids") or [])
        ids.update(payload.get("control_flow_exceptions_missing_from_tools_table") or [])
        for identifier in ids:
            if identifier not in availability:
                availability[identifier] = min_macos
            elif availability[identifier] is not None and (
                min_macos is None or min_macos < availability[identifier]
            ):
                availability[identifier] = min_macos
    return availability


def host_macos_major() -> int | None:
    if platform.system() != "Darwin":
        return None
    try:
        result = subprocess.run(
            ["sw_vers", "-productVersion"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    major = result.stdout.strip().split(".", 1)[0]
    return int(major) if major.isdigit() else None


def resolve_target_macos(value: str | None) -> int | None:
    raw = value
    if raw is None:
        for env_name in TARGET_MACOS_ENV_VARS:
            raw = os.environ.get(env_name)
            if raw:
                break
    if raw is None or raw == "" or raw.lower() == "auto":
        return host_macos_major()
    if raw.lower() in {"latest", "all"}:
        return None
    if raw.isdigit():
        return int(raw)
    raise ValueError(f"Invalid macOS target: {raw!r}")


def normalized_identifier(value: str) -> str:
    if value.startswith("is.workflow.actions."):
        return value
    return f"is.workflow.actions.{value}"


def find_by_identifier(catalog: dict[str, Any], value: str) -> tuple[str, dict[str, Any]] | None:
    tools = catalog.get("tools") or {}
    structural = catalog.get("structuralActions") or {}
    candidates = {**tools, **structural}
    for key in (value, normalized_identifier(value)):
        if key in candidates:
            return key, candidates[key]
    suffix = value.removeprefix("is.workflow.actions.")
    matches = [
        (identifier, entry)
        for identifier, entry in candidates.items()
        if identifier.endswith(f".{suffix}") or identifier.rsplit(".", 1)[-1] == suffix
    ]
    return matches[0] if len(matches) == 1 else None


def find_by_python_name(catalog: dict[str, Any], value: str) -> tuple[str, dict[str, Any]] | None:
    lookup = catalog.get("pythonLookup") or {}
    if value in lookup:
        entry = lookup[value]
        identifier = entry.get("wfIdentifier")
        if identifier:
            found = find_by_identifier(catalog, identifier)
            return found or (identifier, entry)
    for identifier, entry in (catalog.get("tools") or {}).items():
        if entry.get("pythonName") == value:
            return identifier, entry
    return None


def parameter_entry_to_grounding(identifier: str, entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "toolkit-parameter-summary",
        "name": entry.get("displayName") or identifier,
        "pythonName": entry.get("pythonName"),
        "summary": (
            "ToolKit v78 parameter-key summary. This proves the action exists "
            "and names its parameters, but it is not a full authored shortcut sample."
        ),
        "toolkitPlatforms": entry.get("platforms") or [],
        "toolkitToolType": entry.get("toolType"),
        "toolkitParameterSummary": {
            "parameterCount": entry.get("parameterCount"),
            "parameters": entry.get("parameters") or [],
        },
        "parameters": [],
        "sourceFunctions": {},
        "sampleShortcuts": [],
    }


def augment_with_parameter_summary(
    identifier: str,
    entry: dict[str, Any],
    parameter_catalog: dict[str, Any],
) -> dict[str, Any]:
    toolkit_entry = (parameter_catalog.get("tools") or {}).get(identifier)
    if not isinstance(toolkit_entry, dict):
        return entry
    out = dict(entry)
    out["toolkitPlatforms"] = toolkit_entry.get("platforms") or []
    out["toolkitToolType"] = toolkit_entry.get("toolType")
    out["toolkitParameterSummary"] = {
        "parameterCount": toolkit_entry.get("parameterCount"),
        "parameters": toolkit_entry.get("parameters") or [],
    }
    return out


def find_parameter_by_identifier(
    parameter_catalog: dict[str, Any],
    value: str,
) -> tuple[str, dict[str, Any]] | None:
    tools = parameter_catalog.get("tools") or {}
    for key in (value, normalized_identifier(value)):
        entry = tools.get(key)
        if isinstance(entry, dict):
            return key, parameter_entry_to_grounding(key, entry)
    suffix = value.removeprefix("is.workflow.actions.")
    matches = [
        (identifier, parameter_entry_to_grounding(identifier, entry))
        for identifier, entry in tools.items()
        if identifier.endswith(f".{suffix}") or identifier.rsplit(".", 1)[-1] == suffix
    ]
    return matches[0] if len(matches) == 1 else None


def find_parameter_by_python_name(
    parameter_catalog: dict[str, Any],
    value: str,
) -> tuple[str, dict[str, Any]] | None:
    tools = parameter_catalog.get("tools") or {}
    matches = [
        (identifier, parameter_entry_to_grounding(identifier, entry))
        for identifier, entry in tools.items()
        if entry.get("pythonName") == value
    ]
    return matches[0] if len(matches) == 1 else None


def entry_search_text(identifier: str, entry: dict[str, Any]) -> str:
    parts: list[str] = [
        identifier,
        entry.get("status") or "",
        entry.get("name") or "",
        entry.get("pythonName") or "",
        entry.get("summary") or "",
        " ".join(entry.get("keywords") or []),
        " ".join(entry.get("sourceFunctions") or {}),
    ]
    for parameter in entry.get("parameters") or []:
        parts.extend(
            [
                parameter.get("wfKey") or "",
                parameter.get("pythonKeyword") or "",
                parameter.get("label") or "",
                parameter.get("description") or "",
            ]
        )
    toolkit_summary = entry.get("toolkitParameterSummary") or {}
    if isinstance(toolkit_summary, dict):
        for parameter in toolkit_summary.get("parameters") or []:
            if isinstance(parameter, dict):
                parts.extend(
                    [
                        parameter.get("key") or "",
                        parameter.get("typePythonName") or "",
                    ]
                )
    return "\n".join(parts).lower()


def search_entries(catalog: dict[str, Any], query: str, limit: int) -> list[tuple[str, dict[str, Any]]]:
    terms = [term.lower() for term in query.split() if term]
    tools = catalog.get("tools") or {}
    structural = catalog.get("structuralActions") or {}
    entries = sorted({**tools, **structural}.items())
    if not terms:
        return entries[:limit]
    matches = [
        (identifier, entry)
        for identifier, entry in entries
        if all(term in entry_search_text(identifier, entry) for term in terms)
    ]
    return matches[:limit]


def search_parameter_entries(
    parameter_catalog: dict[str, Any],
    query: str,
    limit: int,
) -> list[tuple[str, dict[str, Any]]]:
    terms = [term.lower() for term in query.split() if term]
    entries = sorted((parameter_catalog.get("tools") or {}).items())
    converted = [
        (identifier, parameter_entry_to_grounding(identifier, entry))
        for identifier, entry in entries
    ]
    if not terms:
        return converted[:limit]
    return [
        (identifier, entry)
        for identifier, entry in converted
        if all(term in entry_search_text(identifier, entry) for term in terms)
    ][:limit]


def target_note(minimum: int | None, target_macos: int | None) -> str | None:
    if target_macos is not None and minimum is not None and target_macos < minimum:
        return f"Requires macOS {minimum}+; target macOS is {target_macos}."
    return None


def entry_min_macos(identifier: str, availability: dict[str, int | None]) -> int | None:
    return availability.get(identifier)


def compact_entry(
    identifier: str,
    entry: dict[str, Any],
    availability: dict[str, int | None],
    target_macos: int | None,
) -> dict[str, Any]:
    minimum = entry_min_macos(identifier, availability)
    return {
        "identifier": identifier,
        "status": entry.get("status"),
        "minimumMacOSMajor": minimum,
        "availabilityNote": target_note(minimum, target_macos),
        "name": entry.get("name"),
        "pythonName": entry.get("pythonName"),
        "toolRendererEmbedded": entry.get("toolRendererEmbedded"),
        "toolRendererScriptingUtility": entry.get("toolRendererScriptingUtility"),
        "summary": entry.get("summary"),
        "parameters": entry.get("parameters") or [],
        "toolkitPlatforms": entry.get("toolkitPlatforms") or [],
        "toolkitToolType": entry.get("toolkitToolType"),
        "toolkitParameterSummary": entry.get("toolkitParameterSummary") or {},
        "sourceFunctions": entry.get("sourceFunctions") or {},
        "sampleShortcuts": entry.get("sampleShortcuts") or [],
    }


def print_markdown_entry(
    identifier: str,
    entry: dict[str, Any],
    availability: dict[str, int | None],
    target_macos: int | None,
) -> None:
    print(f"## {entry.get('name') or identifier}")
    print()
    print(f"- Identifier: `{identifier}`")
    if entry.get("pythonName"):
        print(f"- Apple Shortpy name: `{entry['pythonName']}`")
    print(f"- Status: `{entry.get('status')}`")
    minimum = entry_min_macos(identifier, availability)
    if minimum is not None:
        print(f"- Minimum target: macOS {minimum}+")
    note = target_note(minimum, target_macos)
    if note:
        print(f"- Availability: {note}")
    if entry.get("toolRendererEmbedded"):
        flag = "ToolRenderer embedded"
        if entry.get("toolRendererScriptingUtility"):
            flag += ", scripting utility"
        print(f"- Apple surface: {flag}")
    if entry.get("summary"):
        print(f"- Summary: {entry['summary']}")
    samples = entry.get("sampleShortcuts") or []
    if samples:
        print(f"- Observed samples: {', '.join(samples)}")
    parameters = entry.get("parameters") or []
    if parameters:
        print()
        print("| WF key | Apple keyword | Required | Label |")
        print("|--------|---------------|----------|-------|")
        for parameter in parameters:
            print(
                "| `{}` | `{}` | {} | {} |".format(
                    parameter.get("wfKey") or "",
                    parameter.get("pythonKeyword") or "",
                    "yes" if parameter.get("required") else "no",
                    parameter.get("label") or "",
                )
            )
    toolkit_summary = entry.get("toolkitParameterSummary") or {}
    toolkit_parameters = toolkit_summary.get("parameters") if isinstance(toolkit_summary, dict) else None
    if toolkit_parameters:
        print()
        print("| ToolKit key | Type |")
        print("|-------------|------|")
        for parameter in toolkit_parameters:
            print(
                "| `{}` | `{}` |".format(
                    parameter.get("key") or "",
                    parameter.get("typePythonName") or "",
                )
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--identifier", help="WF action identifier or short suffix, e.g. additemtolist")
    group.add_argument("--python-name", help="Apple Shortpy function name, e.g. com_apple_shortcuts_add_item_to_list")
    group.add_argument("--query", help="Search names, summaries, keywords, parameters, and Python names")
    parser.add_argument("--target-macos", default=None, help="Target macOS major version, auto, latest, or all")
    parser.add_argument("--limit", type=int, default=10, help="Maximum search/list results")
    parser.add_argument("--list", action="store_true", help="List catalog entries")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args()

    try:
        target_macos = resolve_target_macos(args.target_macos)
    except ValueError as exc:
        print(str(exc))
        return 2
    catalog = load_catalog()
    parameter_catalog = load_parameter_catalog()
    availability = load_identifier_min_macos()

    results: list[tuple[str, dict[str, Any]]]
    if args.identifier:
        found = find_by_identifier(catalog, args.identifier)
        if found:
            found = (
                found[0],
                augment_with_parameter_summary(found[0], found[1], parameter_catalog),
            )
        else:
            found = find_parameter_by_identifier(parameter_catalog, args.identifier)
        results = [found] if found else []
    elif args.python_name:
        found = find_by_python_name(catalog, args.python_name)
        if found:
            found = (
                found[0],
                augment_with_parameter_summary(found[0], found[1], parameter_catalog),
            )
        else:
            found = find_parameter_by_python_name(parameter_catalog, args.python_name)
        results = [found] if found else []
    elif args.query:
        results = [
            (identifier, augment_with_parameter_summary(identifier, entry, parameter_catalog))
            for identifier, entry in search_entries(catalog, args.query, args.limit)
        ]
        seen = {identifier for identifier, _ in results}
        if len(results) < args.limit:
            for identifier, entry in search_parameter_entries(
                parameter_catalog,
                args.query,
                args.limit - len(results),
            ):
                if identifier not in seen:
                    results.append((identifier, entry))
                    seen.add(identifier)
    else:
        results = (
            [
                (identifier, augment_with_parameter_summary(identifier, entry, parameter_catalog))
                for identifier, entry in search_entries(catalog, "", args.limit)
            ]
            if args.list
            else []
        )

    if args.json:
        result_notes = [
            target_note(entry_min_macos(identifier, availability), target_macos)
            for identifier, _ in results
        ]
        unique_notes = sorted({note for note in result_notes if note})
        payload = {
            "catalog": {
                "schemaVersion": catalog.get("schemaVersion"),
                "minimumMacOSMajor": catalog.get("minimumMacOSMajor"),
                "summary": catalog.get("summary"),
                "runtimePolicy": catalog.get("runtimePolicy"),
            },
            "targetMacOSMajor": target_macos,
            "availabilityNote": unique_notes[0] if len(unique_notes) == 1 else None,
            "results": [
                compact_entry(identifier, entry, availability, target_macos)
                for identifier, entry in results
            ],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if results else 1

    if not results:
        print("No Apple-derived grounding entry found.")
        return 1
    for index, (identifier, entry) in enumerate(results):
        if index:
            print()
        print_markdown_entry(identifier, entry, availability, target_macos)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
