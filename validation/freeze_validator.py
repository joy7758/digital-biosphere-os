#!/usr/bin/env python3
"""Validate DBOS-EXP-0001 freeze contracts without freezing or executing it.

Agent-readable contract:
- One pending freeze manifest references the registered experiment, its pending
  snapshot, pending validator manifest, defined environment, pending environment
  lock, and pending unissued certificate.
- A pending reference chain is not an immutable freeze.
- Frozen status requires complete digests, retained material, timestamps, and an
  attributable certificate; the current v0.1 baseline claims none of them.
- Freeze records cannot authorize execution, create events or runtimes, grant
  capability or permission, or upgrade C/E/V.
- Exit 0 means local structural PASS only; exit 1 fails closed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "DBOS-EXP-0001"
FREEZE_ID = "DBOS-EXP-0001-FREEZE-0001"
SNAPSHOT_ID = "DBOS-EXP-0001-SNAPSHOT-0001"
VALIDATOR_MANIFEST_ID = "DBOS-EXP-0001-VALIDATOR-MANIFEST-0001"
ENVIRONMENT_ID = "dbio://environment/local-governance-workspace/v0.1"
ENVIRONMENT_LOCK_ID = "DBOS-EXP-0001-ENV-LOCK-0001"
CERTIFICATE_ID = "DBOS-EXP-0001-FREEZE-CERT-0001"
CAPTURE_ID = "DBOS-EXP-0001-CAPTURE-0001"
AUTHORIZATION_ID = "DBOS-EXP-0001-AUTH-0001"
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
FREEZE_STATUSES = {"pending", "frozen", "thawed", "invalid", "revoked"}
LOCK_STATUSES = {"pending", "frozen", "thawed", "invalid", "revoked"}
CERTIFICATE_STATUSES = {"pending", "issued", "invalid", "revoked", "superseded"}
SNAPSHOT_HASH_FIELDS = (
    "file_tree_hash",
    "config_hash",
    "dependency_hash",
    "environment_hash",
)
FORBIDDEN_EFFECT_KEYS = {
    "capability_id",
    "capability_assignment",
    "capability_assignment_status",
    "permission",
    "permission_grant",
    "permission_status",
    "execution_result",
    "event_id",
    "runtime_id",
    "agent_id",
    "organism_id",
    "maturity_level",
    "evidence_level",
    "verification_level",
}


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load one JSON-compatible YAML mapping without third-party packages."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one mapping")
    return value


def index_records(
    records: Any, key: str, label: str, errors: list[str]
) -> dict[str, dict[str, Any]]:
    """Index mapping records and reject missing or duplicate identifiers."""
    if not isinstance(records, list):
        errors.append(f"{label} must be a list")
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        where = f"{label}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{where} must be a mapping")
            continue
        identifier = record.get(key)
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"{where}.{key} must be a non-empty string")
            continue
        if identifier in indexed:
            errors.append(f"duplicate {key}: {identifier}")
            continue
        indexed[identifier] = record
    return indexed


def valid_timestamp(value: Any) -> bool:
    """Return true only for ISO 8601 timestamps with an explicit timezone."""
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def valid_digest(value: Any) -> bool:
    return isinstance(value, str) and DIGEST_RE.fullmatch(value) is not None


def reject_effect_fields(record: Any, label: str, errors: list[str]) -> None:
    """Reject authority, result, and level fields anywhere in freeze registries."""
    if isinstance(record, dict):
        present = sorted(FORBIDDEN_EFFECT_KEYS.intersection(record))
        if present:
            errors.append(f"{label}: freeze cannot contain authority or result fields {present}")
        for key, value in record.items():
            reject_effect_fields(value, f"{label}.{key}", errors)
    elif isinstance(record, list):
        for index, value in enumerate(record):
            reject_effect_fields(value, f"{label}[{index}]", errors)


def require_zero(metadata: Any, fields: tuple[str, ...], label: str, errors: list[str]) -> None:
    """Require zero-effect metadata for this non-executing layer."""
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in fields:
        if metadata.get(field) != 0:
            errors.append(f"{label} metadata {field} must remain zero")


def validate(
    experiment_doc: dict[str, Any],
    snapshot_doc: dict[str, Any],
    validator_manifest_doc: dict[str, Any],
    environment_doc: dict[str, Any],
    freeze_manifest_doc: dict[str, Any],
    environment_lock_doc: dict[str, Any],
    certificate_doc: dict[str, Any],
    readiness_doc: dict[str, Any],
    authorization_doc: dict[str, Any],
    event_doc: dict[str, Any],
    context_doc: dict[str, Any],
    runtime_doc: dict[str, Any],
    candidate_doc: dict[str, Any],
    ecological_doc: dict[str, Any],
    entity_doc: dict[str, Any],
    capability_doc: dict[str, Any],
    claim_doc: dict[str, Any],
    evidence_doc: dict[str, Any],
    verification_doc: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    """Validate the pending freeze baseline and its no-effect boundaries."""
    errors: list[str] = []

    experiments = index_records(
        experiment_doc.get("experiments"), "experiment_id", "experiments", errors
    )
    if tuple(experiments) != (EXPERIMENT_ID,):
        errors.append("freeze layer requires exactly DBOS-EXP-0001")
    experiment = experiments.get(EXPERIMENT_ID, {})
    if experiment.get("status") != "registered":
        errors.append("freeze cannot change the experiment from registered status")
    if experiment.get("execution_status") != "not_executed":
        errors.append("freeze cannot execute the experiment")
    if experiment.get("execution_context_ref") is not None or experiment.get("runtime_ref") is not None or experiment.get("run_ref") is not None:
        errors.append("freeze cannot attach execution context, runtime, or run references")

    snapshots = index_records(
        snapshot_doc.get("experiment_snapshots"), "snapshot_id", "experiment_snapshots", errors
    )
    validator_manifests = index_records(
        validator_manifest_doc.get("validator_manifests"),
        "manifest_id",
        "validator_manifests",
        errors,
    )
    environments = index_records(
        environment_doc.get("environments"), "environment_id", "environments", errors
    )
    freeze_manifests = index_records(
        freeze_manifest_doc.get("freeze_manifests"), "freeze_id", "freeze_manifests", errors
    )
    environment_locks = index_records(
        environment_lock_doc.get("environment_locks"), "lock_id", "environment_locks", errors
    )
    certificates = index_records(
        certificate_doc.get("freeze_certificates"), "certificate_id", "freeze_certificates", errors
    )

    if tuple(freeze_manifests) != (FREEZE_ID,):
        errors.append("freeze manifest registry must contain exactly DBOS-EXP-0001-FREEZE-0001")
    freeze_manifest = freeze_manifests.get(FREEZE_ID, {})
    expected_freeze_refs = {
        "experiment_id": EXPERIMENT_ID,
        "snapshot_refs": [SNAPSHOT_ID],
        "validator_manifest_ref": VALIDATOR_MANIFEST_ID,
        "environment_ref": ENVIRONMENT_ID,
        "environment_lock_ref": ENVIRONMENT_LOCK_ID,
        "certificate_ref": CERTIFICATE_ID,
        "snapshot_capture_requirement": {
            "capture_ref": CAPTURE_ID,
            "required_status": "captured",
            "minimum_artifact_digest_count": 1,
            "capture_evidence_required": True,
            "current_status": "pending",
        },
        "authority_effect": "none",
    }
    for field, expected in expected_freeze_refs.items():
        if freeze_manifest.get(field) != expected:
            errors.append(f"{FREEZE_ID}: {field} must remain {expected!r}")
    if freeze_manifest.get("experiment_id") not in experiments:
        errors.append(f"{FREEZE_ID}: freeze must reference an existing experiment")
    for snapshot_ref in freeze_manifest.get("snapshot_refs", []):
        if snapshot_ref not in snapshots:
            errors.append(f"{FREEZE_ID}: missing snapshot reference {snapshot_ref}")
    if freeze_manifest.get("validator_manifest_ref") not in validator_manifests:
        errors.append(f"{FREEZE_ID}: validator manifest reference does not exist")
    if freeze_manifest.get("environment_ref") not in environments:
        errors.append(f"{FREEZE_ID}: environment reference does not exist")
    if freeze_manifest.get("environment_lock_ref") not in environment_locks:
        errors.append(f"{FREEZE_ID}: environment lock reference does not exist")
    if freeze_manifest.get("certificate_ref") not in certificates:
        errors.append(f"{FREEZE_ID}: certificate reference does not exist")
    freeze_status = freeze_manifest.get("status")
    if freeze_status not in FREEZE_STATUSES:
        errors.append(f"{FREEZE_ID}: invalid freeze status {freeze_status!r}")
    if freeze_status == "pending":
        if freeze_manifest.get("frozen_at") is not None:
            errors.append(f"{FREEZE_ID}: pending freeze requires frozen_at=null")
        if freeze_manifest.get("thaw_ref") is not None or freeze_manifest.get("revocation_ref") is not None:
            errors.append(f"{FREEZE_ID}: pending freeze cannot claim thaw or revocation")
    if freeze_status == "frozen" and not valid_timestamp(freeze_manifest.get("frozen_at")):
        errors.append(f"{FREEZE_ID}: frozen status requires timezone-aware frozen_at")
    if freeze_status != "pending":
        errors.append("v0.1 freeze manifest must remain pending and cannot claim completion")

    snapshot = snapshots.get(SNAPSHOT_ID)
    if snapshot is None:
        errors.append("freeze requires the registered experiment snapshot")
        snapshot = {}
    if snapshot.get("experiment_id") != EXPERIMENT_ID:
        errors.append(f"{SNAPSHOT_ID}: snapshot must reference DBOS-EXP-0001")
    if snapshot.get("freeze_reference") != FREEZE_ID:
        errors.append(f"{SNAPSHOT_ID}: freeze_reference must bind the pending freeze manifest")
    if snapshot.get("capture_reference") != CAPTURE_ID:
        errors.append(f"{SNAPSHOT_ID}: capture_reference must bind the pending snapshot capture")
    if snapshot.get("status") != "pending":
        errors.append(f"{SNAPSHOT_ID}: current snapshot must remain pending and unfrozen")
    for field in SNAPSHOT_HASH_FIELDS:
        if snapshot.get(field) is not None:
            errors.append(f"{SNAPSHOT_ID}: pending snapshot requires {field}=null")

    validator_manifest = validator_manifests.get(VALIDATOR_MANIFEST_ID)
    if validator_manifest is None:
        errors.append("freeze requires the registered validator manifest")
        validator_manifest = {}
    if validator_manifest.get("experiment_id") != EXPERIMENT_ID:
        errors.append(f"{VALIDATOR_MANIFEST_ID}: validator manifest must reference DBOS-EXP-0001")
    expected_validators = sorted(
        str(path.relative_to(root)) for path in (root / "validation").glob("*_validator.py")
    )
    if validator_manifest.get("validators") != expected_validators:
        errors.append(f"{VALIDATOR_MANIFEST_ID}: validator paths must match the current suite")
    if validator_manifest.get("status") != "pending":
        errors.append(f"{VALIDATOR_MANIFEST_ID}: current validator manifest must remain pending")
    if validator_manifest.get("digest") is not None or validator_manifest.get("locked_digest") is not None:
        errors.append(f"{VALIDATOR_MANIFEST_ID}: pending validator manifest requires digest=null and locked_digest=null")
    if validator_manifest.get("status") in {"frozen", "ready"}:
        if not valid_digest(validator_manifest.get("digest")):
            errors.append(f"{VALIDATOR_MANIFEST_ID}: frozen validator manifest requires valid digest")
        if validator_manifest.get("locked_digest") != validator_manifest.get("digest"):
            errors.append(f"{VALIDATOR_MANIFEST_ID}: locked_digest must equal digest")

    environment = environments.get(ENVIRONMENT_ID)
    if environment is None:
        errors.append("freeze requires the registered local governance environment")
        environment = {}
    if environment.get("status") != "defined" or environment.get("activation_status") != "not_active":
        errors.append("freeze cannot activate or change the current environment")

    if tuple(environment_locks) != (ENVIRONMENT_LOCK_ID,):
        errors.append("environment lock registry must contain exactly DBOS-EXP-0001-ENV-LOCK-0001")
    environment_lock = environment_locks.get(ENVIRONMENT_LOCK_ID, {})
    expected_lock_refs = {"experiment_id": EXPERIMENT_ID, "environment_id": ENVIRONMENT_ID, "authority_effect": "none"}
    for field, expected in expected_lock_refs.items():
        if environment_lock.get(field) != expected:
            errors.append(f"{ENVIRONMENT_LOCK_ID}: {field} must remain {expected!r}")
    lock_status = environment_lock.get("status")
    if lock_status not in LOCK_STATUSES:
        errors.append(f"{ENVIRONMENT_LOCK_ID}: invalid lock status {lock_status!r}")
    if lock_status == "pending":
        for field in ("os_version", "runtime_version", "dependency_hash", "locked_at"):
            if environment_lock.get(field) is not None:
                errors.append(f"{ENVIRONMENT_LOCK_ID}: pending lock requires {field}=null")
        if environment_lock.get("evidence_refs") != []:
            errors.append(f"{ENVIRONMENT_LOCK_ID}: pending lock requires empty evidence_refs")
    if lock_status == "frozen":
        for field in ("os_version", "runtime_version"):
            if not isinstance(environment_lock.get(field), str) or not environment_lock.get(field):
                errors.append(f"{ENVIRONMENT_LOCK_ID}: frozen lock requires {field}")
        if not valid_digest(environment_lock.get("dependency_hash")):
            errors.append(f"{ENVIRONMENT_LOCK_ID}: frozen lock requires valid dependency_hash")
        if not valid_timestamp(environment_lock.get("locked_at")):
            errors.append(f"{ENVIRONMENT_LOCK_ID}: frozen lock requires timezone-aware locked_at")
        if not isinstance(environment_lock.get("evidence_refs"), list) or not environment_lock.get("evidence_refs"):
            errors.append(f"{ENVIRONMENT_LOCK_ID}: frozen lock requires evidence_refs")
    if lock_status != "pending":
        errors.append("v0.1 environment lock must remain pending and cannot claim completion")

    if tuple(certificates) != (CERTIFICATE_ID,):
        errors.append("freeze certificate registry must contain exactly DBOS-EXP-0001-FREEZE-CERT-0001")
    certificate = certificates.get(CERTIFICATE_ID, {})
    expected_certificate_refs = {
        "experiment_id": EXPERIMENT_ID,
        "freeze_manifest": FREEZE_ID,
        "authority_effect": "none",
    }
    for field, expected in expected_certificate_refs.items():
        if certificate.get(field) != expected:
            errors.append(f"{CERTIFICATE_ID}: {field} must remain {expected!r}")
    certificate_status = certificate.get("status")
    if certificate_status not in CERTIFICATE_STATUSES:
        errors.append(f"{CERTIFICATE_ID}: invalid certificate status {certificate_status!r}")
    if certificate_status == "pending":
        if certificate.get("created_at") is not None or certificate.get("issuer") is not None:
            errors.append(f"{CERTIFICATE_ID}: pending certificate requires created_at=null and issuer=null")
    if certificate_status == "issued":
        if freeze_status != "frozen":
            errors.append(f"{CERTIFICATE_ID}: issued certificate requires frozen manifest")
        if not valid_timestamp(certificate.get("created_at")):
            errors.append(f"{CERTIFICATE_ID}: issued certificate requires timezone-aware created_at")
        if not isinstance(certificate.get("issuer"), str) or not certificate.get("issuer"):
            errors.append(f"{CERTIFICATE_ID}: issued certificate requires attributable issuer")
    if certificate_status != "pending":
        errors.append("v0.1 freeze certificate must remain pending and unissued")

    if freeze_status == "frozen":
        if snapshot.get("status") not in {"frozen", "ready"}:
            errors.append("frozen manifest requires a frozen snapshot")
        if validator_manifest.get("status") not in {"frozen", "ready"}:
            errors.append("frozen manifest requires a frozen validator manifest")
        if lock_status != "frozen":
            errors.append("frozen manifest requires a frozen environment lock")
        if certificate_status != "issued":
            errors.append("frozen manifest requires an issued freeze certificate")

    freeze_meta = freeze_manifest_doc.get("metadata", {})
    lock_meta = environment_lock_doc.get("metadata", {})
    certificate_meta = certificate_doc.get("metadata", {})
    if freeze_meta.get("freeze_manifest_count") != 1 or freeze_meta.get("freeze_status_distribution", {}).get("pending") != 1:
        errors.append("freeze manifest metadata must report one pending record")
    if lock_meta.get("environment_lock_count") != 1 or lock_meta.get("lock_status_distribution", {}).get("pending") != 1:
        errors.append("environment lock metadata must report one pending record")
    if certificate_meta.get("freeze_certificate_count") != 1 or certificate_meta.get("certificate_status_distribution", {}).get("pending") != 1:
        errors.append("freeze certificate metadata must report one pending record")
    require_zero(
        freeze_meta,
        ("frozen_manifest_count", "execution_authority_count", "event_created_count", "runtime_created_count", "agent_created_count", "organism_created_count", "capability_effect_count", "permission_grant_count", "c_e_v_level_change_count"),
        "freeze manifest",
        errors,
    )
    require_zero(
        lock_meta,
        ("frozen_environment_lock_count", "execution_authority_count", "runtime_created_count", "event_created_count", "permission_grant_count"),
        "environment lock",
        errors,
    )
    require_zero(
        certificate_meta,
        ("issued_certificate_count", "execution_authority_count", "event_created_count", "trust_grant_count", "permission_grant_count"),
        "freeze certificate",
        errors,
    )

    reviews = index_records(
        readiness_doc.get("readiness_reviews"), "review_id", "readiness_reviews", errors
    )
    if len(reviews) != 5 or any(review.get("status") != "pending" for review in reviews.values()):
        errors.append("freeze layer must preserve all five readiness reviews as pending")
    if readiness_doc.get("metadata", {}).get("readiness_status") != "pending":
        errors.append("freeze layer cannot promote aggregate readiness")

    authorizations = index_records(
        authorization_doc.get("experiment_authorizations"),
        "authorization_id",
        "experiment_authorizations",
        errors,
    )
    authorization = authorizations.get(AUTHORIZATION_ID)
    if authorization is None:
        errors.append("freeze layer requires the existing genesis authorization record")
        authorization = {}
    if authorization.get("status") != "pending" or authorization.get("authorized_by") is not None or authorization.get("decision_at") is not None:
        errors.append("freeze cannot grant or fabricate experiment authorization")
    if authorization.get("scope", {}).get("current_effect") != "none":
        errors.append("freeze cannot create authorization effect")

    if event_doc.get("events") != []:
        errors.append("freeze cannot generate an event")
    if context_doc.get("execution_contexts") != []:
        errors.append("freeze cannot create an execution context")
    if runtime_doc.get("runtime_instances") != []:
        errors.append("freeze cannot create a runtime")
    if candidate_doc.get("organism_candidates") != []:
        errors.append("freeze cannot create an organism candidate")
    if capability_doc.get("capabilities") != []:
        errors.append("freeze cannot create a capability")

    entities = index_records(entity_doc.get("entities"), "entity_id", "entities", errors)
    if any(entity.get("entity_type") == "agent" for entity in entities.values()):
        errors.append("freeze cannot create an Agent entity")
    ecological_entities = ecological_doc.get("ecological_entities")
    if not isinstance(ecological_entities, list):
        errors.append("ecological_entities must be a list")
        ecological_entities = []
    for record in ecological_entities:
        if not isinstance(record, dict):
            errors.append("ecological entity records must be mappings")
            continue
        if record.get("ecological_type") in {"Runtime", "Candidate Organism", "Digital Organism"}:
            errors.append("freeze cannot promote an ecological entity")
        if record.get("evolution_stage") != "pre-organism":
            errors.append("freeze cannot change evolution stage")

    claims = index_records(claim_doc.get("claims"), "claim_id", "claims", errors)
    evidence_records = index_records(evidence_doc.get("evidence"), "evidence_id", "evidence", errors)
    verifications = index_records(
        verification_doc.get("verification_records"),
        "verification_id",
        "verification_records",
        errors,
    )
    for claim_id, claim in claims.items():
        if claim.get("status") != "pending" or claim.get("maturity_level") != "C1":
            errors.append(f"{claim_id}: freeze must preserve capability claims at pending/C1")
            break
    for evidence_id, record in evidence_records.items():
        if record.get("status") != "pending" or record.get("evidence_type") != "E1":
            errors.append(f"{evidence_id}: freeze must preserve evidence at pending/E1")
            break
    for verification_id, record in verifications.items():
        if record.get("status") != "pending" or record.get("decision") != "pending" or record.get("verification_level") != "V0":
            errors.append(f"{verification_id}: freeze must preserve verification at pending/V0")
            break

    reject_effect_fields(freeze_manifest_doc, "freeze manifest registry", errors)
    reject_effect_fields(environment_lock_doc, "environment lock registry", errors)
    reject_effect_fields(certificate_doc, "freeze certificate registry", errors)

    freeze_constitution = root / "constitution" / "experiment-freeze-constitution.yaml"
    readiness_constitution = root / "constitution" / "experiment-readiness-constitution.yaml"
    for path, tokens in (
        (
            freeze_constitution,
            (
                'freeze_definition:',
                'freeze_scope:',
                'immutable_artifacts:',
                'freeze_certificate:',
                'thaw_procedure:',
            ),
        ),
        (
            readiness_constitution,
            (
                'freeze_reference: "experiment-freeze-constitution.yaml"',
                'freeze_manifest_registry: "../registry/freeze-manifests.yaml"',
                'environment_lock_registry: "../registry/environment-locks.yaml"',
                'freeze_certificate_registry: "../registry/freeze-certificates.yaml"',
            ),
        ),
    ):
        if not path.is_file():
            errors.append(f"required constitution is missing: {path.relative_to(root)}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                errors.append(f"{path.name}: missing freeze integration token {token}")

    remaining_gaps = [
        "experiment snapshot has four null hashes and is not frozen",
        "validator manifest digest and locked_digest are null and the manifest is not frozen",
        "environment lock has null OS, runtime, dependency hash, locked_at, and no evidence",
        "freeze manifest is pending with frozen_at=null",
        "freeze certificate is pending with issuer=null and created_at=null",
        "all five readiness reviews remain pending",
        "experiment authorization remains pending",
        "DBOS root has no Git repository identity for a commit-bound snapshot",
    ]
    return {
        "status": "FAIL" if errors else "PASS",
        "experiment_id": EXPERIMENT_ID,
        "freeze_manifest_count": len(freeze_manifests),
        "freeze_status": freeze_status,
        "environment_lock_count": len(environment_locks),
        "environment_lock_status": lock_status,
        "freeze_certificate_count": len(certificates),
        "freeze_certificate_status": certificate_status,
        "validator_count": len(expected_validators),
        "readiness_status": readiness_doc.get("metadata", {}).get("readiness_status"),
        "authorization_status": authorization.get("status"),
        "execution_status": experiment.get("execution_status"),
        "event_count": len(event_doc.get("events", [])) if isinstance(event_doc.get("events"), list) else None,
        "runtime_count": len(runtime_doc.get("runtime_instances", [])) if isinstance(runtime_doc.get("runtime_instances"), list) else None,
        "remaining_pre_execution_gaps": remaining_gaps,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiments", type=Path, default=root / "registry" / "experiments.yaml")
    parser.add_argument("--snapshots", type=Path, default=root / "registry" / "experiment-snapshots.yaml")
    parser.add_argument("--validator-manifests", type=Path, default=root / "registry" / "validator-manifests.yaml")
    parser.add_argument("--environments", type=Path, default=root / "registry" / "environments.yaml")
    parser.add_argument("--freeze-manifests", type=Path, default=root / "registry" / "freeze-manifests.yaml")
    parser.add_argument("--environment-locks", type=Path, default=root / "registry" / "environment-locks.yaml")
    parser.add_argument("--certificates", type=Path, default=root / "registry" / "freeze-certificates.yaml")
    parser.add_argument("--readiness", type=Path, default=root / "registry" / "readiness-reviews.yaml")
    parser.add_argument("--authorizations", type=Path, default=root / "registry" / "experiment-authorizations.yaml")
    parser.add_argument("--events", type=Path, default=root / "registry" / "events.yaml")
    parser.add_argument("--contexts", type=Path, default=root / "registry" / "execution-contexts.yaml")
    parser.add_argument("--runtimes", type=Path, default=root / "registry" / "runtime-instances.yaml")
    parser.add_argument("--candidates", type=Path, default=root / "registry" / "organism-candidates.yaml")
    parser.add_argument("--ecological", type=Path, default=root / "registry" / "ecological-entities.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--capabilities", type=Path, default=root / "registry" / "capabilities.yaml")
    parser.add_argument("--claims", type=Path, default=root / "registry" / "capability-claims.yaml")
    parser.add_argument("--evidence", type=Path, default=root / "registry" / "capability-evidence.yaml")
    parser.add_argument("--verification", type=Path, default=root / "registry" / "verification-records.yaml")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    from execution_chain_compat import delegate_if_advanced
    delegated = delegate_if_advanced(root, args.format)
    if delegated is not None:
        return delegated
    try:
        result = validate(
            load_json_yaml(args.experiments),
            load_json_yaml(args.snapshots),
            load_json_yaml(args.validator_manifests),
            load_json_yaml(args.environments),
            load_json_yaml(args.freeze_manifests),
            load_json_yaml(args.environment_locks),
            load_json_yaml(args.certificates),
            load_json_yaml(args.readiness),
            load_json_yaml(args.authorizations),
            load_json_yaml(args.events),
            load_json_yaml(args.contexts),
            load_json_yaml(args.runtimes),
            load_json_yaml(args.candidates),
            load_json_yaml(args.ecological),
            load_json_yaml(args.entities),
            load_json_yaml(args.capabilities),
            load_json_yaml(args.claims),
            load_json_yaml(args.evidence),
            load_json_yaml(args.verification),
            root,
        )
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"EXPERIMENT_FREEZE_VALIDATION: {result.get('status', 'FAIL')}")
        print(f"freeze_manifests={result.get('freeze_manifest_count', 0)}")
        print(f"environment_locks={result.get('environment_lock_count', 0)}")
        print(f"freeze_certificates={result.get('freeze_certificate_count', 0)}")
        print(f"freeze_status={result.get('freeze_status')}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
