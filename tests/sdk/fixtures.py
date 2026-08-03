"""Synthetic in-memory SDK objects with no registry or execution effects."""

from __future__ import annotations

from typing import Any

from sdk.objects import CapabilityObject
from sdk import (
    EntityObject,
    EvidenceReferenceObject,
    ExecutionObject,
)
from sdk.objects.verification import VerificationObject


def source(source_id: str) -> dict[str, str]:
    return {
        "namespace": "dbio",
        "source_id": source_id,
        "version": "v0.1",
        "status": "DECLARED",
    }


def reference(
    reference_id: str, reference_type: str, *, source_id: str
) -> dict[str, str]:
    return {
        "reference_id": reference_id,
        "reference_type": reference_type,
        "namespace": "dbio",
        "version": "v0.1",
        "source": source_id,
        "status": "DECLARED",
    }


def common(object_id: str, source_id: str) -> dict[str, Any]:
    return {
        "object_id": object_id,
        "source": source(source_id),
        "status": "DECLARED",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "limitations": ["Synthetic in-memory SDK test fixture only."],
    }


def entity_object(**overrides: Any) -> EntityObject:
    entity_id = "dbio://repository/synthetic-sdk-fixture/v0.1"
    source_id = "registry/entities.yaml"
    values = {
        **common(entity_id, source_id),
        "entity_id": entity_id,
        "entity_type": "repository",
        "owner_reference": reference(
            "dbio://entity/synthetic-owner/v0.1", "ENTITY", source_id=source_id
        ),
        "lifecycle_state": "PROPOSED",
        "source_reference": reference(entity_id, "ENTITY", source_id=source_id),
    }
    values.update(overrides)
    return EntityObject(**values)


def capability_object(**overrides: Any) -> CapabilityObject:
    capability_id = "dbio://capability/synthetic-sdk-read-boundary/v0.1"
    source_id = "registry/capabilities.yaml"
    values = {
        **common(capability_id, source_id),
        "capability_id": capability_id,
        "entity_reference": reference(
            "dbio://repository/synthetic-sdk-fixture/v0.1",
            "ENTITY",
            source_id="registry/entities.yaml",
        ),
        "capability_name": "synthetic_read_boundary",
        "scope": {"operation": "local validation"},
        "constraints": {"external_action": "forbidden"},
        "verification_status": "PENDING",
    }
    values.update(overrides)
    return CapabilityObject(**values)


def execution_object(**overrides: Any) -> ExecutionObject:
    execution_id = "dbio://execution/synthetic-sdk-record/v0.1"
    source_id = "registry/executions.yaml"
    values = {
        **common(execution_id, source_id),
        "status": "CREATED",
        "execution_id": execution_id,
        "entity_reference": reference(
            "dbio://repository/synthetic-sdk-fixture/v0.1",
            "ENTITY",
            source_id="registry/entities.yaml",
        ),
        "task_reference": reference(
            "dbio://registration/synthetic-sdk-task/v0.1",
            "REGISTRATION",
            source_id="registry/experiments.yaml",
        ),
        "context_reference": reference(
            "dbio://execution/synthetic-sdk-context/v0.1",
            "EXECUTION",
            source_id="registry/execution-contexts.yaml",
        ),
        "input_reference": reference(
            "dbio://evidence/synthetic-sdk-input/v0.1",
            "EVIDENCE",
            source_id="registry/capability-evidence.yaml",
        ),
        "output_reference": None,
    }
    values.update(overrides)
    return ExecutionObject(**values)


def evidence_reference_object(**overrides: Any) -> EvidenceReferenceObject:
    evidence_id = "dbio://evidence/synthetic-sdk-reference/v0.1"
    source_id = "registry/capability-evidence.yaml"
    values = {
        **common(evidence_id, source_id),
        "evidence_id": evidence_id,
        "execution_reference": reference(
            "dbio://execution/synthetic-sdk-record/v0.1",
            "EXECUTION",
            source_id="registry/executions.yaml",
        ),
        "source_reference": reference(
            evidence_id, "EVIDENCE", source_id=source_id
        ),
        "integrity_status": "PENDING",
    }
    values.update(overrides)
    return EvidenceReferenceObject(**values)


def verification_object(**overrides: Any) -> VerificationObject:
    verification_id = "dbio://verification/synthetic-sdk-record/v0.1"
    source_id = "registry/verification-records.yaml"
    values = {
        **common(verification_id, source_id),
        "verification_id": verification_id,
        "target_reference": reference(
            "dbio://evidence/synthetic-sdk-reference/v0.1",
            "EVIDENCE",
            source_id="registry/capability-evidence.yaml",
        ),
        "verification_type": "AUTOMATED_VALIDATION",
        "verification_status": "PENDING",
    }
    values.update(overrides)
    return VerificationObject(**values)


def all_objects() -> tuple[
    EntityObject,
    CapabilityObject,
    ExecutionObject,
    EvidenceReferenceObject,
    VerificationObject,
]:
    return (
        entity_object(),
        capability_object(),
        execution_object(),
        evidence_reference_object(),
        verification_object(),
    )
