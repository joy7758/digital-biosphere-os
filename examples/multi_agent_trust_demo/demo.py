"""Build a deterministic three-role DBOS trust-chain teaching fixture.

The role functions are pure, fixed transformations over synthetic text. Role
names describe collaboration semantics; no Agent class, model, planner, tool,
network call, Runtime, identity registration, Permission, or canonical Evidence
is created. DBOS objects are inert in-memory representations and all validation
results are local structural results only.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from dbos import (
    EntityObject,
    EvidenceReferenceObject,
    ExecutionObject,
    object_to_dict,
    validate_object,
)

DEMO_ID = "DBOS-MULTI-AGENT-TRUST-DEMO-V0.1"
SOURCE_ID = "examples/multi_agent_trust_demo/demo.py"
NAMESPACE = "extension:dbos-multi-agent-trust-demo"
SCENARIO_QUESTION = (
    "How should a governed multi-agent research workflow separate evidence "
    "from analysis and human conclusions?"
)
ROLE_ORDER = ("research_agent", "analysis_agent", "review_agent")
ROLE_TITLES = {
    "research_agent": "Research Agent",
    "analysis_agent": "Analysis Agent",
    "review_agent": "Review Agent",
}


def source_descriptor() -> dict[str, str]:
    return {
        "namespace": NAMESPACE,
        "source_id": SOURCE_ID,
        "version": "v0.1",
        "status": "DECLARED",
    }


def reference(reference_id: str, reference_type: str) -> dict[str, str]:
    return {
        "reference_id": reference_id,
        "reference_type": reference_type,
        "namespace": NAMESPACE,
        "version": "v0.1",
        "source": SOURCE_ID,
        "status": "DECLARED",
    }


def role_entity_id(role_id: str) -> str:
    return f"{NAMESPACE}:role:{role_id}:v0.1"


def build_role_entity(role_id: str) -> EntityObject:
    entity_id = role_entity_id(role_id)
    return EntityObject(
        object_id=entity_id,
        entity_id=entity_id,
        entity_type="agent",
        owner_reference=reference(
            f"{NAMESPACE}:owner:human-demo-reviewer:v0.1",
            "ENTITY",
        ),
        lifecycle_state="PROPOSED",
        source_reference=reference(entity_id, "ENTITY"),
        source=source_descriptor(),
        status="DECLARED",
        limitations=(
            "Synthetic role identity representation only; no Agent instance exists.",
            "PROPOSED does not mean registered, verified, active, authorized, or permitted.",
        ),
    )


def research_role(question: str) -> dict[str, Any]:
    """Return fixed synthetic research notes without external retrieval."""
    return {
        "question": question,
        "material_type": "SYNTHETIC_TEACHING_NOTES",
        "notes": [
            "Identity, execution, evidence reference, and validation are separate records.",
            "Evidence completeness does not establish scientific truth.",
            "Recommendations require review before any adoption decision.",
        ],
        "external_sources_retrieved": False,
    }


def analysis_role(research_output: Mapping[str, Any]) -> dict[str, Any]:
    """Derive fixed analytical observations from the synthetic notes."""
    notes = research_output.get("notes", [])
    return {
        "input_note_count": len(notes) if isinstance(notes, list) else 0,
        "observations": [
            "A shared reference chain can preserve role attribution.",
            "Fail-closed validation prevents missing context from becoming success.",
            "Human review remains necessary for conclusions and release decisions.",
        ],
        "risk_flags": ["SYNTHETIC_INPUT_ONLY", "NO_EXTERNAL_FACT_VERIFICATION"],
        "scientific_conclusion_created": False,
    }


def review_role(analysis_output: Mapping[str, Any]) -> dict[str, Any]:
    """Review boundaries without certifying truth or approving execution."""
    risk_flags = analysis_output.get("risk_flags", [])
    return {
        "review_result": "HUMAN_REVIEW_REQUIRED",
        "checks": {
            "role_attribution_present": True,
            "evidence_truth_separated": True,
            "automatic_permission_absent": True,
            "risk_flags_present": bool(risk_flags),
        },
        "scientific_truth_claimed": False,
        "publication_approved": False,
        "execution_authorized": False,
    }


def build_step_objects(role_id: str, step_number: int) -> tuple[ExecutionObject, EvidenceReferenceObject]:
    execution_id = f"{NAMESPACE}:execution:{step_number:02d}:{role_id}:v0.1"
    evidence_id = f"{NAMESPACE}:evidence-reference:{step_number:02d}:{role_id}:v0.1"
    execution = ExecutionObject(
        object_id=execution_id,
        execution_id=execution_id,
        entity_reference=reference(role_entity_id(role_id), "ENTITY"),
        task_reference=reference(f"{NAMESPACE}:task:{role_id}:v0.1", "TASK"),
        context_reference=reference(f"{NAMESPACE}:context:shared:v0.1", "CONTEXT"),
        input_reference=reference(f"{NAMESPACE}:input:{step_number:02d}:v0.1", "INPUT"),
        output_reference=reference(evidence_id, "EVIDENCE"),
        source=source_descriptor(),
        status="CREATED",
        limitations=(
            "In-memory record of a deterministic role simulation, not a DBOS execution engine result.",
            "Output reference does not establish evidence integrity, truth, or verification.",
        ),
    )
    evidence_reference = EvidenceReferenceObject(
        object_id=evidence_id,
        evidence_id=evidence_id,
        execution_reference=reference(execution_id, "EXECUTION"),
        source_reference=reference(
            f"{NAMESPACE}:synthetic-output:{step_number:02d}:{role_id}:v0.1",
            "EVIDENCE",
        ),
        integrity_status="PENDING",
        source=source_descriptor(),
        status="DECLARED",
        limitations=(
            "Reference to an in-memory synthetic output only; no canonical Evidence Object is created.",
            "PENDING integrity does not prove completeness, correctness, or truth.",
        ),
    )
    return execution, evidence_reference


def validation_record(target: Any) -> dict[str, Any]:
    result = validate_object(target)
    return result.to_dict()


def build_demo() -> dict[str, Any]:
    """Return the complete deterministic demo and DBOS-to-SAEE envelope."""
    role_entities = {role_id: build_role_entity(role_id) for role_id in ROLE_ORDER}
    role_outputs: dict[str, dict[str, Any]] = {}
    role_outputs["research_agent"] = research_role(SCENARIO_QUESTION)
    role_outputs["analysis_agent"] = analysis_role(role_outputs["research_agent"])
    role_outputs["review_agent"] = review_role(role_outputs["analysis_agent"])

    steps: list[dict[str, Any]] = []
    execution_history: list[dict[str, Any]] = []
    evidence_references: list[dict[str, Any]] = []
    validation_results: list[dict[str, Any]] = []

    for step_number, role_id in enumerate(ROLE_ORDER, start=1):
        entity = role_entities[role_id]
        execution, evidence_reference = build_step_objects(role_id, step_number)
        entity_validation = validation_record(entity)
        execution_validation = validation_record(execution)
        evidence_validation = validation_record(evidence_reference)
        validation_results.extend(
            [entity_validation, execution_validation, evidence_validation]
        )
        execution_record = object_to_dict(execution)
        evidence_record = object_to_dict(evidence_reference)
        execution_history.append(execution_record)
        evidence_references.append(evidence_record)
        steps.append(
            {
                "step_number": step_number,
                "role_id": role_id,
                "role_title": ROLE_TITLES[role_id],
                "entity": object_to_dict(entity),
                "role_output": role_outputs[role_id],
                "execution": execution_record,
                "evidence_reference": evidence_record,
                "validation_results": {
                    "entity": entity_validation,
                    "execution": execution_validation,
                    "evidence_reference": evidence_validation,
                },
            }
        )

    all_validations_pass = all(
        result.get("result") == "PASS" for result in validation_results
    )
    return {
        "demo_id": DEMO_ID,
        "demo_status": "LOCAL_DETERMINISTIC_MULTI_ROLE_TRUST_DEMO",
        "scenario": {"question": SCENARIO_QUESTION, "synthetic": True},
        "role_order": list(ROLE_ORDER),
        "steps": steps,
        "dbos_to_saee_envelope": {
            "contract_version": "dba.dbos-saee-developer-preview/v0.1",
            "source_demo_id": DEMO_ID,
            "execution_history": execution_history,
            "validation_results": validation_results,
            "evidence_references": evidence_references,
            "resource_information": {
                "measurement_status": "OBSERVED_LOCAL_SYNTHETIC",
                "role_step_count": 3,
                "model_call_count": 0,
                "network_call_count": 0,
                "tool_call_count": 0,
                "external_side_effect_count": 0,
            },
            "limitations": [
                "Prepared local envelope; SAEE has not been called by DBOS.",
                "Validation PASS is structural and does not establish Evidence truth.",
            ],
        },
        "demo_contract_satisfied": all_validations_pass,
        "non_effects": {
            "agent_instance_created": False,
            "runtime_created": False,
            "entity_registered": False,
            "entity_activated": False,
            "capability_granted": False,
            "permission_granted": False,
            "canonical_evidence_created": False,
            "saee_called": False,
            "evolution_decision_created": False,
            "dbos_state_modified": False,
        },
    }
