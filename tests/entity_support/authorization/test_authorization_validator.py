import unittest
from datetime import datetime, timedelta, timezone

from entity_support.authorization.authorization_validator import (
    validate_authorization_for_registration,
    REQUIRED_REGISTRATION_SCOPE,
)
from entity_support.authorization.authorization_record import build_authorization_record

class AuthorizationValidatorTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)
        self.future = (self.now + timedelta(days=1)).isoformat()
        self.past = (self.now - timedelta(days=1)).isoformat()

        # Valid AUTHORIZED record
        self.valid_record = build_authorization_record(
            authorization_id="auth-1",
            candidate_id="cand-1",
            target_entity_type="agent",  # Must be in SUPPORTED_ENTITY_TYPES
            status="AUTHORIZED",
            created_at=self.now.isoformat(),
            decision_reference="dec-1",
            scope=REQUIRED_REGISTRATION_SCOPE,
            issuer_reference="issuer-1",
            expires_at=self.future,
        )

    def test_happy_path_is_effective(self):
        errors = validate_authorization_for_registration(self.valid_record, at_time=self.now.isoformat())
        self.assertEqual(errors, [])

    def test_requires_authorized_status(self):
        record = dict(self.valid_record)
        record["status"] = "PENDING"
        # We manually modify the dict to bypass `build_authorization_record` strictness which might fail
        errors = validate_authorization_for_registration(record)
        self.assertIn("registration requires status=AUTHORIZED", errors)

        record["status"] = "REJECTED"
        errors = validate_authorization_for_registration(record)
        self.assertIn("registration requires status=AUTHORIZED", errors)

    def test_requires_no_revocation_reference(self):
        record = dict(self.valid_record)
        record["revocation_reference"] = "rev-1"
        errors = validate_authorization_for_registration(record)
        self.assertIn("revoked authorization cannot be used", errors)

    def test_requires_mapping_scope(self):
        record = dict(self.valid_record)
        record["scope"] = "not_a_mapping"
        errors = validate_authorization_for_registration(record)
        self.assertIn("registration authorization requires scope mapping", errors)

    def test_requires_correct_scope_keys(self):
        record = dict(self.valid_record)
        record["scope"] = {"operation": "wrong_operation", "lifecycle_target": "REGISTERED"}
        errors = validate_authorization_for_registration(record)
        self.assertIn("scope.operation must be entity_registration", errors)

        record["scope"] = {"operation": "entity_registration", "lifecycle_target": "WRONG_TARGET"}
        errors = validate_authorization_for_registration(record)
        self.assertIn("scope.lifecycle_target must be REGISTERED", errors)

        # Missing key
        record["scope"] = {"operation": "entity_registration"}
        errors = validate_authorization_for_registration(record)
        self.assertIn("scope.lifecycle_target must be REGISTERED", errors)

    def test_invalid_at_time(self):
        errors = validate_authorization_for_registration(self.valid_record, at_time="invalid-time")
        self.assertIn("at_time must be a timezone-aware ISO 8601 string", errors)

        errors = validate_authorization_for_registration(self.valid_record, at_time="2024-08-04T12:00:00") # missing tz
        self.assertIn("at_time must be a timezone-aware ISO 8601 string", errors)

    def test_authorization_is_expired(self):
        # The record expires in the future, if we check it in the further future, it should be expired
        further_future = (self.now + timedelta(days=2)).isoformat()
        errors = validate_authorization_for_registration(self.valid_record, at_time=further_future)
        self.assertIn("authorization is expired", errors)

        # Test exact expiration time edge case (should be expired if at_time >= expires_at)
        errors = validate_authorization_for_registration(self.valid_record, at_time=self.future)
        self.assertIn("authorization is expired", errors)

    def test_underlying_record_validation_errors_propagate(self):
        # Make the record structurally invalid according to `validate_authorization_record`
        record = dict(self.valid_record)
        del record["authorization_id"]
        errors = validate_authorization_for_registration(record)
        self.assertTrue(any("missing fields" in err for err in errors))

if __name__ == '__main__':
    unittest.main()
