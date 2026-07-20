"""Tests for immutable Registration Receipt persistence."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from test_authorization_record import CREATED_AT, build_authorized
from test_registration_store import build_success
from entity_support.authorization.authorization_registry import AuthorizationRegistry
from entity_support.registration_store.receipt_store import (
    STORED_RECEIPT_FIELDS,
    ReceiptStore,
    build_stored_receipt,
)
from entity_support.registration_store.registration_store import (
    RegistrationStore,
    build_registration_record,
)


class ReceiptStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="dbos-receipt-test-")
        root = Path(self.temp.name)
        self.authorizations = AuthorizationRegistry(root / "authorizations.json")
        self.registrations = RegistrationStore(root / "registrations.json")
        self.receipts = ReceiptStore(root / "receipts.json")
        self.authorizations.append(build_authorized())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_success_receipt_is_persisted(self) -> None:
        self.registrations.append(
            build_success(),
            authorization_registry=self.authorizations,
        )
        receipt = self.receipts.append(
            build_stored_receipt(
                registration_id="fixture-registration",
                receipt_id="fixture-receipt",
                status="SUCCESS",
                timestamp=CREATED_AT,
            ),
            registration_store=self.registrations,
        )
        self.assertEqual(tuple(receipt), STORED_RECEIPT_FIELDS)

    def test_failed_receipt_requires_error_reference(self) -> None:
        with self.assertRaises(ValueError):
            build_stored_receipt(
                registration_id="fixture-failure",
                receipt_id="fixture-failure-receipt",
                status="FAILED",
                timestamp=CREATED_AT,
            )

    def test_failed_receipt_is_persisted(self) -> None:
        failed = build_registration_record(
            registration_id="fixture-failure",
            entity_id=None,
            candidate_reference="fixture-candidate",
            authorization_reference="fixture-authorization",
            registered_at=CREATED_AT,
            status="FAILED",
        )
        self.registrations.append(
            failed,
            authorization_registry=self.authorizations,
        )
        receipt = self.receipts.append(
            build_stored_receipt(
                registration_id="fixture-failure",
                receipt_id="fixture-failure-receipt",
                status="FAILED",
                timestamp=CREATED_AT,
                error_reference="error:fixture-failure",
            ),
            registration_store=self.registrations,
        )
        self.assertEqual(receipt["error_reference"], "error:fixture-failure")

    def test_receipt_requires_registration_record(self) -> None:
        with self.assertRaises(ValueError):
            self.receipts.append(
                build_stored_receipt(
                    registration_id="missing-registration",
                    receipt_id="fixture-orphan-receipt",
                    status="FAILED",
                    timestamp=CREATED_AT,
                    error_reference="error:missing-registration",
                ),
                registration_store=self.registrations,
            )

    def test_receipt_status_must_match_registration(self) -> None:
        self.registrations.append(
            build_success(),
            authorization_registry=self.authorizations,
        )
        with self.assertRaises(ValueError):
            self.receipts.append(
                build_stored_receipt(
                    registration_id="fixture-registration",
                    receipt_id="fixture-mismatch-receipt",
                    status="FAILED",
                    timestamp=CREATED_AT,
                    error_reference="error:mismatch",
                ),
                registration_store=self.registrations,
            )

    def test_existing_failed_receipt_cannot_be_overwritten(self) -> None:
        failed = build_registration_record(
            registration_id="fixture-failure",
            entity_id=None,
            candidate_reference="fixture-candidate",
            authorization_reference="fixture-authorization",
            registered_at=CREATED_AT,
            status="FAILED",
        )
        self.registrations.append(
            failed,
            authorization_registry=self.authorizations,
        )
        receipt = build_stored_receipt(
            registration_id="fixture-failure",
            receipt_id="fixture-failure-receipt",
            status="FAILED",
            timestamp=CREATED_AT,
            error_reference="error:first",
        )
        self.receipts.append(receipt, registration_store=self.registrations)
        replacement = dict(receipt)
        replacement["receipt_id"] = "fixture-replacement-receipt"
        replacement["error_reference"] = "error:replacement"
        with self.assertRaises(ValueError):
            self.receipts.append(replacement, registration_store=self.registrations)


if __name__ == "__main__":
    unittest.main()
