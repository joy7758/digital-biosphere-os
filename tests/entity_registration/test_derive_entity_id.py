"""Tests for deriving deterministic entity identities from registration sources."""

from __future__ import annotations

import unittest

from entity_support.registration.registration_validator import derive_entity_id


class DeriveEntityIdTests(unittest.TestCase):
    def test_derive_entity_id_produces_deterministic_opaque_identifier(self) -> None:
        result = derive_entity_id("candidate-1", "auth-1")
        self.assertTrue(result.startswith("dbio:entity:registration:"))
        # Digest should be 24 hex characters
        digest = result.split(":")[-1]
        self.assertEqual(len(digest), 24)

        # Same inputs should produce exactly the same output
        self.assertEqual(result, derive_entity_id("candidate-1", "auth-1"))

        # Different inputs must produce different outputs
        self.assertNotEqual(result, derive_entity_id("candidate-2", "auth-1"))
        self.assertNotEqual(result, derive_entity_id("candidate-1", "auth-2"))

    def test_derive_entity_id_strips_whitespace_from_inputs(self) -> None:
        base_result = derive_entity_id("candidate-1", "auth-1")

        # Should strip whitespace from candidate_id
        self.assertEqual(base_result, derive_entity_id("  candidate-1  ", "auth-1"))
        self.assertEqual(base_result, derive_entity_id("\ncandidate-1\t", "auth-1"))

        # Should strip whitespace from authorization_id
        self.assertEqual(base_result, derive_entity_id("candidate-1", "  auth-1  "))
        self.assertEqual(base_result, derive_entity_id("candidate-1", "\nauth-1\t"))

        # Should strip whitespace from both
        self.assertEqual(base_result, derive_entity_id("  candidate-1  ", "  auth-1  "))

    def test_derive_entity_id_rejects_empty_candidate_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "candidate_id must be a non-empty string"):
            derive_entity_id("", "auth-1")
        with self.assertRaisesRegex(ValueError, "candidate_id must be a non-empty string"):
            derive_entity_id("   ", "auth-1")

    def test_derive_entity_id_rejects_invalid_type_candidate_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "candidate_id must be a non-empty string"):
            derive_entity_id(None, "auth-1") # type: ignore
        with self.assertRaisesRegex(ValueError, "candidate_id must be a non-empty string"):
            derive_entity_id(123, "auth-1") # type: ignore

    def test_derive_entity_id_rejects_empty_authorization_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "authorization_id must be a non-empty string"):
            derive_entity_id("candidate-1", "")
        with self.assertRaisesRegex(ValueError, "authorization_id must be a non-empty string"):
            derive_entity_id("candidate-1", "   ")

    def test_derive_entity_id_rejects_invalid_type_authorization_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "authorization_id must be a non-empty string"):
            derive_entity_id("candidate-1", None) # type: ignore
        with self.assertRaisesRegex(ValueError, "authorization_id must be a non-empty string"):
            derive_entity_id("candidate-1", 123) # type: ignore


if __name__ == "__main__":
    unittest.main()
