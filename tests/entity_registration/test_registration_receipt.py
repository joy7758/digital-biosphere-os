"""Tests for SUCCESS/FAILED Registration Receipt mappings."""

from __future__ import annotations

import unittest

from entity_support.registration.registration_receipt import (
    REGISTRATION_RECEIPT_FIELDS,
    build_registration_receipt,
    retain_registration_receipt,
)

TIMESTAMP = "2026-07-20T12:00:00+08:00"


class RegistrationReceiptTests(unittest.TestCase):
    def test_success_receipt_has_exact_fields(self) -> None:
        receipt = build_registration_receipt(
            registration_id="fixture-registration",
            entity_id="fixture-entity",
            authorization_reference="fixture-authorization",
            timestamp=TIMESTAMP,
            status="SUCCESS",
        )
        self.assertEqual(tuple(receipt), REGISTRATION_RECEIPT_FIELDS)

    def test_failed_receipt_preserves_failure_without_entity_id(self) -> None:
        receipt = build_registration_receipt(
            registration_id="fixture-failed-registration",
            entity_id=None,
            authorization_reference="fixture-authorization",
            timestamp=TIMESTAMP,
            status="FAILED",
        )
        self.assertEqual(receipt["status"], "FAILED")
        self.assertIsNone(receipt["entity_id"])

    def test_success_requires_entity_id(self) -> None:
        with self.assertRaises(ValueError):
            build_registration_receipt(
                registration_id="fixture-registration",
                entity_id=None,
                authorization_reference="fixture-authorization",
                timestamp=TIMESTAMP,
                status="SUCCESS",
            )

    def test_failed_receipt_cannot_claim_entity_id(self) -> None:
        with self.assertRaises(ValueError):
            build_registration_receipt(
                registration_id="fixture-registration",
                entity_id="forbidden-entity",
                authorization_reference="fixture-authorization",
                timestamp=TIMESTAMP,
                status="FAILED",
            )

    def test_receipt_rejects_unknown_status(self) -> None:
        with self.assertRaises(ValueError):
            build_registration_receipt(
                registration_id="fixture-registration",
                entity_id=None,
                authorization_reference="fixture-authorization",
                timestamp=TIMESTAMP,
                status="PENDING",
            )

    def test_retention_appends_a_copy(self) -> None:
        receipt = build_registration_receipt(
            registration_id="fixture-registration",
            entity_id="fixture-entity",
            authorization_reference="fixture-authorization",
            timestamp=TIMESTAMP,
            status="SUCCESS",
        )
        log: list[dict[str, str | None]] = []
        retain_registration_receipt(receipt, log)
        receipt["status"] = "FAILED"
        self.assertEqual(log[0]["status"], "SUCCESS")


if __name__ == "__main__":
    unittest.main()

