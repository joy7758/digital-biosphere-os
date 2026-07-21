"""Required negative cases for DBOS v0.1 governance non-effects."""

from __future__ import annotations

import unittest

from validator import ValidationStatus, validate_object

from fixtures import synthetic_capability, synthetic_entity, synthetic_verification


class NegativeGovernanceTests(unittest.TestCase):
    def assert_rejected(self, target: dict[str, object]) -> None:
        self.assertIsNot(validate_object(target).result, ValidationStatus.PASS)

    def test_rejects_capability_permission_field(self) -> None:
        target = synthetic_capability()
        target["scope"]["permission"] = "READ"
        self.assert_rejected(target)

    def test_rejects_verification_authorization_field(self) -> None:
        target = synthetic_verification()
        target["authorization"] = "GRANTED"
        self.assert_rejected(target)

    def test_rejects_object_authority_field(self) -> None:
        target = synthetic_capability()
        target["constraints"]["authority"] = "SELF"
        self.assert_rejected(target)

    def test_rejects_unknown_top_level_field(self) -> None:
        target = synthetic_entity()
        target["unexpected_field"] = "must not be accepted"
        self.assert_rejected(target)

    def test_rejects_unknown_status_auto_upgrade(self) -> None:
        target = synthetic_entity()
        target["status"] = "UNKNOWN"
        target["lifecycle_state"] = "ACTIVE"
        self.assertEqual(validate_object(target).result, ValidationStatus.UNKNOWN)

    def test_rejects_schema_execution_trigger(self) -> None:
        target = synthetic_capability()
        target["scope"]["execution_trigger"] = True
        self.assert_rejected(target)

    def test_rejects_reference_truth_claim(self) -> None:
        target = synthetic_verification()
        target["target_reference"]["truth_confirmed"] = True
        self.assert_rejected(target)


if __name__ == "__main__":
    unittest.main()
