"""Pure synthetic fixtures for DBOS Object Schema Validator tests.

These dictionaries are never written to a registry and do not represent real
entities, capabilities, executions, evidence, verifications, or permissions.
"""

from __future__ import annotations

from typing import Any


def synthetic_source(source_id: str) -> dict[str, str]:
    return {
        "namespace": "dbio",
        "source_id": source_id,
        "version": "v0.1",
        "status": "DECLARED",
    }


def synthetic_reference(
    reference_id: str,
    reference_type: str,
    *,
    source: str,
) -> dict[str, str]:
    return {
        "reference_id": reference_id,
        "reference_type": reference_type,
        "namespace": "dbio",
        "version": "v0.1",
        "source": source,
        "status": "DECLARED",
    }


def synthetic_common(object_id: str, object_type: str, source_id: str) -> dict[str, Any]:
    return {
        "object_id": object_id,
        "object_type": object_type,
        "version": "v0.1",
        "source": synthetic_source(source_id),
        "status": "DECLARED",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "limitations": ["Synthetic local structure-validation fixture only."],
    }


def synthetic_entity() -> dict[str, Any]:
    entity_id = "dbio://repository/synthetic-schema-fixture/v0.1"
    source_id = "registry/entities.yaml"
    value = synthetic_common(entity_id, "ENTITY", source_id)
    value.update(
        {
            "entity_id": entity_id,
            "entity_type": "repository",
            "owner_reference": synthetic_reference(
                "dbio://entity/synthetic-owner/v0.1",
                "ENTITY",
                source=source_id,
            ),
            "lifecycle_state": "PROPOSED",
            "source_reference": synthetic_reference(
                entity_id,
                "ENTITY",
                source=source_id,
            ),
        }
    )
    return value


def synthetic_capability() -> dict[str, Any]:
    capability_id = "dbio://capability/synthetic-read-boundary/v0.1"
    value = synthetic_common(capability_id, "CAPABILITY", "registry/capabilities.yaml")
    value.update(
        {
            "capability_id": capability_id,
            "entity_reference": synthetic_reference(
                "dbio://repository/synthetic-schema-fixture/v0.1",
                "ENTITY",
                source="registry/entities.yaml",
            ),
            "capability_name": "synthetic_read_boundary",
            "scope": {"operation": "read-only validation"},
            "constraints": {"external_action": "forbidden"},
            "verification_status": "PENDING",
        }
    )
    return value


def synthetic_execution() -> dict[str, Any]:
    execution_id = "dbio://execution/synthetic-validation-record/v0.1"
    value = synthetic_common(execution_id, "EXECUTION", "registry/executions.yaml")
    value.update(
        {
            "execution_id": execution_id,
            "entity_reference": synthetic_reference(
                "dbio://repository/synthetic-schema-fixture/v0.1",
                "ENTITY",
                source="registry/entities.yaml",
            ),
            "task_reference": synthetic_reference(
                "dbio://registration/synthetic-task/v0.1",
                "REGISTRATION",
                source="registry/experiments.yaml",
            ),
            "context_reference": synthetic_reference(
                "dbio://execution/synthetic-context/v0.1",
                "EXECUTION",
                source="registry/execution-contexts.yaml",
            ),
            "input_reference": synthetic_reference(
                "dbio://evidence/synthetic-input/v0.1",
                "EVIDENCE",
                source="registry/capability-evidence.yaml",
            ),
            "output_reference": None,
        }
    )
    value["status"] = "CREATED"
    return value


def synthetic_evidence_reference() -> dict[str, Any]:
    evidence_id = "dbio://evidence/synthetic-validation-evidence/v0.1"
    source_id = "registry/capability-evidence.yaml"
    value = synthetic_common(evidence_id, "EVIDENCE_REFERENCE", source_id)
    value.update(
        {
            "evidence_id": evidence_id,
            "execution_reference": synthetic_reference(
                "dbio://execution/synthetic-validation-record/v0.1",
                "EXECUTION",
                source="registry/executions.yaml",
            ),
            "source_reference": synthetic_reference(
                evidence_id,
                "EVIDENCE",
                source=source_id,
            ),
            "integrity_status": "PENDING",
        }
    )
    return value


def synthetic_verification() -> dict[str, Any]:
    verification_id = "dbio://verification/synthetic-structural-check/v0.1"
    value = synthetic_common(
        verification_id,
        "VERIFICATION",
        "registry/verification-records.yaml",
    )
    value.update(
        {
            "verification_id": verification_id,
            "target_reference": synthetic_reference(
                "dbio://repository/synthetic-schema-fixture/v0.1",
                "ENTITY",
                source="registry/entities.yaml",
            ),
            "verification_type": "AUTOMATED_VALIDATION",
            "verification_status": "PENDING",
        }
    )
    return value
