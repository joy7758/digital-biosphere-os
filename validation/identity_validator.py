#!/usr/bin/env python3
"""Validate the Digital Biosphere canonical identity registry.

Agent-readable contract:
- Input: registry/entities.yaml (JSON-compatible YAML 1.2)
- Compatibility input: registry/agents.yaml identity view
- Output: a deterministic JSON or text verdict
- Exit 0: PASS
- Exit 1: FAIL
No third-party Python packages are required.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

VALID_ENTITY_TYPES = {
    "agent",
    "protocol",
    "repository",
    "service",
    "artifact",
    "governance_system",
}
VALID_LIFECYCLE_STATES = {"proposed", "active", "verified", "deprecated", "retired"}
VALID_PATH_STATUSES = {"duplicate", "mirror", "temporary", "unknown"}
VALID_OWNER_STATUSES = {"unknown", "repository_namespace_only", "verified"}
CANONICAL_ID_RE = re.compile(
    r"^dbio://(?P<entity_type>agent|protocol|repository|service|artifact|governance_system)/"
    r"(?P<name>[a-z0-9][a-z0-9.-]*)/"
    r"(?P<version>v[a-zA-Z0-9][a-zA-Z0-9._-]*|unversioned|unresolved)$"
)
QUOTED_FIELD_RE = re.compile(
    r'^    (?P<key>id|entity_id|canonical_id|entity_type|version|status): "(?P<value>.*)"$'
)
LIFECYCLE_STATE_RE = re.compile(r'^      state: "(?P<value>.*)"$')
ENTRY_RE = re.compile(r'^  - id: "(?P<value>.*)"$')


def load_registry(path: Path) -> dict[str, Any]:
    """Load JSON-compatible YAML using the Python standard library."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain one mapping")
    return data


def parse_agent_identity_view(path: Path) -> dict[str, dict[str, str]]:
    """Read only the identity fields from the block-YAML compatibility view."""
    records: dict[str, dict[str, str]] = {}
    current: dict[str, str] | None = None
    in_lifecycle = False
    for line in path.read_text(encoding="utf-8").splitlines():
        entry_match = ENTRY_RE.match(line)
        if entry_match:
            current = {"id": entry_match.group("value")}
            records[current["id"]] = current
            in_lifecycle = False
            continue
        if current is None:
            continue
        if line == "    lifecycle:":
            in_lifecycle = True
            continue
        if in_lifecycle:
            lifecycle_match = LIFECYCLE_STATE_RE.match(line)
            if lifecycle_match:
                current["lifecycle_state"] = lifecycle_match.group("value")
                continue
            if line.startswith("    ") and not line.startswith("      "):
                in_lifecycle = False
        field_match = QUOTED_FIELD_RE.match(line)
        if field_match:
            current[field_match.group("key")] = field_match.group("value")
    return records


def validate(
    registry: dict[str, Any],
    agent_view: dict[str, dict[str, str]],
) -> dict[str, Any]:
    errors: list[str] = []
    entities = registry.get("entities")
    observations = registry.get("path_observations", [])
    if not isinstance(entities, list):
        return {"status": "FAIL", "errors": ["entities must be a list"]}

    entity_ids: set[str] = set()
    canonical_ids: set[str] = set()
    entity_by_id: dict[str, dict[str, Any]] = {}
    type_counts: Counter[str] = Counter()

    for index, entity in enumerate(entities):
        where = f"entities[{index}]"
        if not isinstance(entity, dict):
            errors.append(f"{where} must be a mapping")
            continue
        entity_id = entity.get("entity_id")
        canonical_id = entity.get("canonical_id")
        entity_type = entity.get("entity_type")
        version = entity.get("version")

        if not isinstance(entity_id, str) or not entity_id:
            errors.append(f"{where}.entity_id must be a non-empty string")
            continue
        if entity_id in entity_ids:
            errors.append(f"duplicate entity_id: {entity_id}")
        entity_ids.add(entity_id)
        entity_by_id[entity_id] = entity

        if entity_type not in VALID_ENTITY_TYPES:
            errors.append(f"{entity_id}: invalid entity_type {entity_type!r}")
        else:
            type_counts[entity_type] += 1

        if not isinstance(canonical_id, str):
            errors.append(f"{entity_id}: canonical_id must be a string")
        else:
            if canonical_id in canonical_ids:
                errors.append(f"duplicate canonical_id: {canonical_id}")
            canonical_ids.add(canonical_id)
            match = CANONICAL_ID_RE.match(canonical_id)
            if not match:
                errors.append(f"{entity_id}: malformed canonical_id {canonical_id!r}")
            else:
                if match.group("entity_type") != entity_type:
                    errors.append(f"{entity_id}: canonical_id type does not match entity_type")
                if match.group("version") != version:
                    errors.append(f"{entity_id}: canonical_id version does not match version")

        lifecycle = entity.get("lifecycle")
        if not isinstance(lifecycle, dict):
            errors.append(f"{entity_id}: lifecycle must be a mapping")
        else:
            for required_key in ("state", "created", "last_verified", "successor"):
                if required_key not in lifecycle:
                    errors.append(f"{entity_id}: lifecycle missing {required_key}")
            state = lifecycle.get("state")
            if state not in VALID_LIFECYCLE_STATES:
                errors.append(f"{entity_id}: invalid lifecycle state {state!r}")
            if version in {"unversioned", "unresolved"} and state != "proposed":
                errors.append(f"{entity_id}: provisional version requires proposed lifecycle")
            if state == "retired" and not lifecycle.get("retirement_record"):
                errors.append(f"{entity_id}: retired entity requires retirement_record")

        owner = entity.get("owner")
        if not isinstance(owner, dict) or owner.get("status") not in VALID_OWNER_STATUSES:
            errors.append(f"{entity_id}: invalid owner status")
        else:
            owner_status = owner.get("status")
            owner_value = owner.get("value")
            if owner_status in {"repository_namespace_only", "verified"} and not owner_value:
                errors.append(f"{entity_id}: owner status {owner_status} requires value")
            for source in owner.get("evidence_source", []):
                if not Path(source).exists():
                    errors.append(f"{entity_id}: missing owner evidence source {source}")

        verification = entity.get("verification")
        if not isinstance(verification, dict):
            errors.append(f"{entity_id}: verification must be a mapping")
        else:
            for source in verification.get("evidence_source", []):
                if not Path(source).exists():
                    errors.append(f"{entity_id}: missing evidence source {source}")

    for entity_id, entity in entity_by_id.items():
        parent = entity.get("parent_entity")
        if parent is not None and parent not in entity_by_id:
            errors.append(f"{entity_id}: parent_entity does not exist: {parent}")
        if entity.get("entity_type") == "artifact" and parent is None:
            errors.append(f"{entity_id}: artifact requires parent_entity")
        for child in entity.get("child_entities", []):
            if child not in entity_by_id:
                errors.append(f"{entity_id}: child entity does not exist: {child}")
        lifecycle = entity.get("lifecycle", {})
        successor = lifecycle.get("successor") if isinstance(lifecycle, dict) else None
        if successor is not None and successor not in entity_by_id:
            errors.append(f"{entity_id}: successor does not exist: {successor}")

        source_id = entity.get("source_registry_id")
        view = agent_view.get(source_id)
        if view is None:
            errors.append(f"{entity_id}: missing agents.yaml compatibility record {source_id}")
        else:
            for key in ("entity_id", "canonical_id", "entity_type", "version", "status"):
                if view.get(key) != entity.get(key):
                    errors.append(
                        f"{entity_id}: agents.yaml {key} mismatch "
                        f"({view.get(key)!r} != {entity.get(key)!r})"
                    )
            if view.get("lifecycle_state") != entity.get("lifecycle", {}).get("state"):
                errors.append(f"{entity_id}: agents.yaml lifecycle state mismatch")

    if len(agent_view) != len(entities):
        errors.append(
            f"agents.yaml record count {len(agent_view)} does not match entity count {len(entities)}"
        )

    observation_paths: set[str] = set()
    observation_counts: Counter[str] = Counter()
    for index, observation in enumerate(observations):
        where = f"path_observations[{index}]"
        if not isinstance(observation, dict):
            errors.append(f"{where} must be a mapping")
            continue
        path = observation.get("path")
        status = observation.get("identity_status")
        if not isinstance(path, str) or not path:
            errors.append(f"{where}.path must be a non-empty string")
        elif path in observation_paths:
            errors.append(f"duplicate path observation: {path}")
        else:
            observation_paths.add(path)
        if status not in VALID_PATH_STATUSES:
            errors.append(f"{where}: invalid identity_status {status!r}")
        else:
            observation_counts[status] += 1
        if "entity_id" in observation or "canonical_id" in observation:
            errors.append(f"{where}: path observation must not create an entity identity")

    metadata = registry.get("metadata", {})
    expected_counts = metadata.get("classification_counts", {})
    for entity_type in VALID_ENTITY_TYPES:
        if expected_counts.get(entity_type, 0) != type_counts.get(entity_type, 0):
            errors.append(f"classification count mismatch for {entity_type}")
    expected_path_counts = metadata.get("path_identity_counts", {})
    for status in VALID_PATH_STATUSES:
        if expected_path_counts.get(status, 0) != observation_counts.get(status, 0):
            errors.append(f"path identity count mismatch for {status}")
    if metadata.get("entity_count") != len(entities):
        errors.append("metadata.entity_count mismatch")
    if metadata.get("path_observation_count") != len(observations):
        errors.append("metadata.path_observation_count mismatch")

    return {
        "status": "FAIL" if errors else "PASS",
        "entity_count": len(entities),
        "classification_counts": {
            key: type_counts.get(key, 0)
            for key in (
                "protocol",
                "agent",
                "repository",
                "artifact",
                "service",
                "governance_system",
            )
        },
        "path_observation_count": len(observations),
        "path_identity_counts": {
            key: observation_counts.get(key, 0)
            for key in ("duplicate", "mirror", "temporary", "unknown")
        },
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--entities",
        type=Path,
        default=root / "registry" / "entities.yaml",
        help="JSON-compatible YAML identity registry",
    )
    parser.add_argument(
        "--agents",
        type=Path,
        default=root / "registry" / "agents.yaml",
        help="block-YAML compatibility view",
    )
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()

    try:
        registry = load_registry(args.entities)
        agent_view = parse_agent_identity_view(args.agents)
        result = validate(registry, agent_view)
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"IDENTITY_VALIDATION: {result['status']}")
        print(f"entities={result.get('entity_count', 0)}")
        print(f"classification_counts={result.get('classification_counts', {})}")
        print(f"path_identity_counts={result.get('path_identity_counts', {})}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
