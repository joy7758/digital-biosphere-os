"""Validate persisted authorization, registration, receipt, and identity links.

Agent-readable contract:
- The continuity chain is candidate → authorization → registration → entity.
- Receipt references the registration outcome but is not Evidence Truth.
- Successful registration does not imply activation, Agent, Runtime, or Permission.
- Validation is read-only and never repairs or deletes persisted history.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from entity_support.authorization.authorization_record import (
    validate_authorization_record,
)
from entity_support.authorization.authorization_registry import AuthorizationRegistry
from entity_support.registration.registration_validator import derive_entity_id
from entity_support.registration_store.receipt_store import (
    ReceiptStore,
    validate_stored_receipt,
)
from entity_support.registration_store.registration_store import (
    RegistrationStore,
    validate_registration_record,
)


def validate_identity_continuity_persistence(
    *,
    authorization: Mapping[str, Any],
    registration: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> list[str]:
    """Return errors for broken candidate/authorization/registration/entity links."""

    errors = [
        *(f"authorization: {error}" for error in validate_authorization_record(authorization)),
        *(f"registration: {error}" for error in validate_registration_record(registration)),
        *(f"receipt: {error}" for error in validate_stored_receipt(receipt)),
    ]
    if registration.get("authorization_reference") != authorization.get(
        "authorization_id"
    ):
        errors.append("registration authorization_reference must match authorization_id")
    if registration.get("candidate_reference") != authorization.get("candidate_id"):
        errors.append("registration candidate_reference must match authorization candidate_id")
    if receipt.get("registration_id") != registration.get("registration_id"):
        errors.append("receipt registration_id must match Registration Record")
    if receipt.get("status") != registration.get("status"):
        errors.append("receipt status must match Registration Record")

    if registration.get("status") == "SUCCESS":
        candidate_id = authorization.get("candidate_id")
        authorization_id = authorization.get("authorization_id")
        if isinstance(candidate_id, str) and isinstance(authorization_id, str):
            expected_entity_id = derive_entity_id(candidate_id, authorization_id)
            if registration.get("entity_id") != expected_entity_id:
                errors.append("entity_id lacks persisted identity continuity")
        else:
            errors.append("successful continuity requires candidate_id and authorization_id")
    if registration.get("status") == "FAILED" and registration.get("entity_id") is not None:
        errors.append("failed registration cannot persist entity_id")
    return errors


def validate_persistence_stores(
    *,
    authorization_registry: AuthorizationRegistry,
    registration_store: RegistrationStore,
    receipt_store: ReceiptStore,
) -> list[str]:
    """Validate all persisted references without mutating any store."""

    errors: list[str] = []
    receipts = {
        item["registration_id"]: item for item in receipt_store.list_records()
    }
    for registration in registration_store.list_records():
        registration_id = registration["registration_id"]
        authorization = authorization_registry.get(
            registration["authorization_reference"]
        )
        if authorization is None:
            errors.append(f"{registration_id}: missing Authorization Record")
            continue
        receipt = receipts.get(registration_id)
        if receipt is None:
            errors.append(f"{registration_id}: missing Receipt Record")
            continue
        errors.extend(
            f"{registration_id}: {error}"
            for error in validate_identity_continuity_persistence(
                authorization=authorization,
                registration=registration,
                receipt=receipt,
            )
        )
    registration_ids = {
        item["registration_id"] for item in registration_store.list_records()
    }
    for receipt in receipt_store.list_records():
        if receipt["registration_id"] not in registration_ids:
            errors.append(
                f"{receipt['receipt_id']}: orphan receipt without Registration Record"
            )
    return errors


__all__ = [
    "validate_identity_continuity_persistence",
    "validate_persistence_stores",
]
