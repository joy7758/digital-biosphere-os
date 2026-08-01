"""Show three fail-closed DBOS validation cases using synthetic data only.

The prohibited permission field is an intentionally malformed in-memory test
declaration. It is not a Permission object, grant, authorization, or registry
record and is never persisted.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
BASIC_EXAMPLE_ROOT = Path(__file__).resolve().parents[1]
for path in (REPOSITORY_ROOT, BASIC_EXAMPLE_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from create_entity_object import build_synthetic_entity_object  # noqa: E402
from sdk import CapabilityObject  # noqa: E402
from sdk.serialization import object_to_dict  # noqa: E402
from validator import ValidationStatus, validate_object  # noqa: E402


def _source(source_id: str) -> dict[str, str]:
    return {
        "namespace": "dbio",
        "source_id": source_id,
        "version": "v0.1",
        "status": "DECLARED",
    }


def _entity_reference() -> dict[str, str]:
    return {
        "reference_id": "dbio://repository/quickstart-synthetic-example/v0.1",
        "reference_type": "ENTITY",
        "namespace": "dbio",
        "version": "v0.1",
        "source": "examples/basic_object/create_entity_object.py",
        "status": "DECLARED",
    }


def _synthetic_capability() -> CapabilityObject:
    capability_id = "dbio://capability/quickstart-negative-example/v0.1"
    return CapabilityObject(
        object_id=capability_id,
        capability_id=capability_id,
        entity_reference=_entity_reference(),
        capability_name="synthetic_local_read",
        scope={"operation": "read synthetic input"},
        constraints={"external_action": "forbidden"},
        verification_status="PENDING",
        source=_source("examples/basic_object/negative/validate_negative_cases.py"),
        status="DECLARED",
        limitations=("Synthetic negative validation fixture only.",),
    )


def build_negative_cases() -> tuple[tuple[str, dict[str, Any], ValidationStatus], ...]:
    capability_with_permission = object_to_dict(_synthetic_capability())
    capability_with_permission["permission"] = "GRANTED"

    entity_with_unknown_field = object_to_dict(build_synthetic_entity_object())
    entity_with_unknown_field["unexpected_field"] = "must be rejected"

    entity_with_wrong_version = object_to_dict(build_synthetic_entity_object())
    entity_with_wrong_version["version"] = "v9.9"

    return (
        ("capability_with_permission", capability_with_permission, ValidationStatus.FAIL),
        ("unknown_field", entity_with_unknown_field, ValidationStatus.FAIL),
        (
            "version_mismatch",
            entity_with_wrong_version,
            ValidationStatus.VERSION_MISMATCH,
        ),
    )


def main() -> int:
    all_rejected_as_expected = True
    for case_name, target, expected in build_negative_cases():
        result = validate_object(target)
        all_rejected_as_expected = all_rejected_as_expected and result.result is expected
        print(
            json.dumps(
                {"case": case_name, "validation_result": result.to_dict()},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    return 0 if all_rejected_as_expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
