#!/usr/bin/env python3
"""Exercise the installed ``dbos`` facade with one inert object representation.

Run this only after ``python3 -m pip install -e .`` from the repository root.
No path injection, network access, Agent, Runtime, Permission, or governed state
is created.
"""

from __future__ import annotations

import json

from dbos import EntityObject, object_to_dict
from validator import validate_object


ENTITY_ID = "dbio://repository/installed-editable-preview/v0.1"
SOURCE_ID = "examples/basic_object/installed_editable_quickstart.py"


def reference(reference_id: str) -> dict[str, str]:
    return {
        "reference_id": reference_id,
        "reference_type": "ENTITY",
        "namespace": "dbio",
        "version": "v0.1",
        "source": SOURCE_ID,
        "status": "DECLARED",
    }


def build_object() -> EntityObject:
    """Build a synthetic in-memory representation, not a registered Entity."""
    return EntityObject(
        object_id=ENTITY_ID,
        entity_id=ENTITY_ID,
        entity_type="repository",
        owner_reference=reference("dbio://entity/installed-preview-owner/v0.1"),
        lifecycle_state="PROPOSED",
        source_reference=reference(ENTITY_ID),
        source={
            "namespace": "dbio",
            "source_id": SOURCE_ID,
            "version": "v0.1",
            "status": "DECLARED",
        },
        status="DECLARED",
        limitations=(
            "Local editable-install preview representation only.",
            "No identity verification, registration, activation, or permission is created.",
        ),
    )


def main() -> int:
    target = build_object()
    result = validate_object(target)
    output = {
        "object": object_to_dict(target),
        "validation": result.to_dict(),
        "non_effects": {
            "agent_created": False,
            "runtime_created": False,
            "entity_registered": False,
            "permission_granted": False,
            "canonical_evidence_created": False,
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
