"""Capability Object structural and governance-boundary tests."""

from __future__ import annotations

from copy import deepcopy
import unittest

from validator import ValidationStatus, validate_object

from fixtures import synthetic_capability


class CapabilitySchemaValidationTests(unittest.TestCase):
    def test_accepts_structurally_valid_synthetic_capability(self) -> None:
        self.assertEqual(validate_object(synthetic_capability()).result, ValidationStatus.PASS)

    def test_rejects_missing_scope(self) -> None:
        target = synthetic_capability()
        del target["scope"]
        self.assertEqual(validate_object(target).result, ValidationStatus.FAIL)

    def test_rejects_empty_scope(self) -> None:
        target = synthetic_capability()
        target["scope"] = {}
        self.assertEqual(validate_object(target).result, ValidationStatus.FAIL)

    def test_rejects_inconsistent_entity_reference_type(self) -> None:
        target = synthetic_capability()
        target["entity_reference"]["reference_type"] = "EVIDENCE"
        self.assertEqual(validate_object(target).result, ValidationStatus.FAIL)

    def test_rejects_unverified_capability_upgrade(self) -> None:
        target = synthetic_capability()
        target["verification_status"] = "VERIFIED"
        self.assertEqual(validate_object(target).result, ValidationStatus.FAIL)

    def test_does_not_mutate_input(self) -> None:
        target = synthetic_capability()
        before = deepcopy(target)
        validate_object(target)
        self.assertEqual(target, before)


if __name__ == "__main__":
    unittest.main()
