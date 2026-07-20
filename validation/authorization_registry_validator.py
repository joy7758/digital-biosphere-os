#!/usr/bin/env python3
"""Validate Authorization Registry and Registration Persistence boundaries.

Agent-readable contract:
- All persistence occurs inside an automatically removed temporary directory.
- PASS proves immutable records, authorization lookup, receipt linkage, replay
  rejection, and persisted identity continuity.
- PASS creates no live Authorization, Registration, Entity, Agent, Runtime,
  Permission, task Execution, Evidence, or SAEE result.
- Exit 0: PASS
- Exit 1: FAIL
No third-party Python packages are required.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from entity_support.authorization.authorization_record import (
    build_authorization_record,
)
from entity_support.authorization.authorization_registry import AuthorizationRegistry
from entity_support.registration.registration_validator import derive_entity_id
from entity_support.registration_store.receipt_store import (
    ReceiptStore,
    build_stored_receipt,
)
from entity_support.registration_store.registration_persistence_validator import (
    validate_persistence_stores,
)
from entity_support.registration_store.registration_store import (
    RegistrationStore,
    build_registration_record,
)

CREATED_AT = "2026-07-20T12:00:00+08:00"
EXPIRES_AT = "2027-07-20T12:00:00+08:00"
EXPECTED_NEGATIVE_CASES = (
    "missing_issuer",
    "missing_decision_reference",
    "authorized_without_scope",
    "revoked_authorization_use",
    "duplicate_success_registration",
    "registration_without_authorization",
)


def _authorized_record(
    *,
    authorization_id: str = "fixture-authorization",
    candidate_id: str = "fixture-candidate",
) -> dict[str, Any]:
    return build_authorization_record(
        authorization_id=authorization_id,
        decision_reference="fixture-admission-decision",
        candidate_id=candidate_id,
        target_entity_type="service",
        scope={
            "operation": "entity_registration",
            "lifecycle_target": "REGISTERED",
        },
        issuer_reference="fixture-issuer",
        status="AUTHORIZED",
        created_at=CREATED_AT,
        expires_at=EXPIRES_AT,
    )


def _success_registration(
    *,
    registration_id: str = "fixture-registration",
    authorization_id: str = "fixture-authorization",
    candidate_id: str = "fixture-candidate",
) -> dict[str, str | None]:
    return build_registration_record(
        registration_id=registration_id,
        entity_id=derive_entity_id(candidate_id, authorization_id),
        candidate_reference=candidate_id,
        authorization_reference=authorization_id,
        registered_at=CREATED_AT,
        status="SUCCESS",
    )


def _must_reject(name: str, action: Callable[[], object], errors: list[str]) -> bool:
    try:
        action()
    except ValueError:
        return True
    except Exception as exc:  # pragma: no cover - defensive diagnostics
        errors.append(f"{name}: unexpected {type(exc).__name__}: {exc}")
        return False
    errors.append(f"{name}: prohibited operation was accepted")
    return False


def validate() -> dict[str, Any]:
    errors: list[str] = []
    rejected: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="dbos-registration-validator-") as temp:
        root = Path(temp)
        authorizations = AuthorizationRegistry(root / "authorizations.json")
        registrations = RegistrationStore(root / "registrations.json")
        receipts = ReceiptStore(root / "receipts.json")
        authorizations.initialize()
        registrations.initialize()
        receipts.initialize()

        authorization = authorizations.append(_authorized_record())
        registration = registrations.append(
            _success_registration(),
            authorization_registry=authorizations,
        )
        receipt = receipts.append(
            build_stored_receipt(
                registration_id=registration["registration_id"],
                receipt_id="fixture-receipt",
                status="SUCCESS",
                timestamp=CREATED_AT,
            ),
            registration_store=registrations,
        )
        errors.extend(
            validate_persistence_stores(
                authorization_registry=authorizations,
                registration_store=registrations,
                receipt_store=receipts,
            )
        )

        invalid = _authorized_record()
        invalid["issuer_reference"] = None
        rejected["missing_issuer"] = _must_reject(
            "missing_issuer", lambda: build_authorization_record(**invalid), errors
        )
        invalid = _authorized_record()
        invalid["decision_reference"] = None
        rejected["missing_decision_reference"] = _must_reject(
            "missing_decision_reference",
            lambda: build_authorization_record(**invalid),
            errors,
        )
        invalid = _authorized_record()
        invalid["scope"] = None
        rejected["authorized_without_scope"] = _must_reject(
            "authorized_without_scope",
            lambda: build_authorization_record(**invalid),
            errors,
        )

        revocable = _authorized_record(
            authorization_id="fixture-revoked-authorization",
            candidate_id="fixture-revoked-candidate",
        )
        revocable["decision_reference"] = "fixture-revoked-decision"
        authorizations.append(revocable)
        revoked = build_authorization_record(
            authorization_id="fixture-revoked-authorization",
            decision_reference="fixture-revoked-decision",
            candidate_id="fixture-revoked-candidate",
            target_entity_type="service",
            scope={
                "operation": "entity_registration",
                "lifecycle_target": "REGISTERED",
            },
            issuer_reference="fixture-issuer",
            status="REVOKED",
            created_at="2026-07-20T12:00:01+08:00",
            expires_at=EXPIRES_AT,
            revocation_reference="fixture-revocation",
        )
        authorizations.append(revoked)
        rejected["revoked_authorization_use"] = _must_reject(
            "revoked_authorization_use",
            lambda: registrations.append(
                _success_registration(
                    registration_id="fixture-revoked-registration",
                    authorization_id="fixture-revoked-authorization",
                    candidate_id="fixture-revoked-candidate",
                ),
                authorization_registry=authorizations,
            ),
            errors,
        )
        rejected["duplicate_success_registration"] = _must_reject(
            "duplicate_success_registration",
            lambda: registrations.append(
                _success_registration(registration_id="fixture-registration-replay"),
                authorization_registry=authorizations,
            ),
            errors,
        )
        rejected["registration_without_authorization"] = _must_reject(
            "registration_without_authorization",
            lambda: registrations.append(
                _success_registration(
                    registration_id="fixture-orphan-registration",
                    authorization_id="missing-authorization",
                ),
                authorization_registry=authorizations,
            ),
            errors,
        )

        fixture_counts = {
            "authorization_record": authorizations.authorization_count(),
            "authorization_state_record": authorizations.count(),
            "registration_record": registrations.count(),
            "receipt_record": receipts.count(),
        }
        if authorization["status"] != "AUTHORIZED":
            errors.append("fixture Authorization Record was not persisted")
        if registration["status"] != "SUCCESS":
            errors.append("fixture Registration Record was not persisted")
        if receipt["status"] != "SUCCESS":
            errors.append("fixture Receipt Record was not persisted")

    for name in EXPECTED_NEGATIVE_CASES:
        if name not in rejected:
            errors.append(f"missing negative case: {name}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "fixture_persisted_counts": fixture_counts,
        "temporary_store_removed": not Path(temp).exists(),
        "negative_case_count": len(EXPECTED_NEGATIVE_CASES),
        "rejected_negative_case_count": sum(rejected.values()),
        "negative_case_results": rejected,
        "live_record_counts": {
            "authorization_record": 0,
            "registration_record": 0,
            "entity": 0,
            "agent": 0,
            "runtime": 0,
            "permission": 0,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()
    result = validate()
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"authorization_registry_validator: {result['status']}")
        print(
            "negative cases rejected: "
            f"{result['rejected_negative_case_count']}/{result['negative_case_count']}"
        )
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
