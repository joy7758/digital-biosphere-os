"""Tests for entity ID derivation."""

import unittest
from entity_support.registration.registration_validator import derive_entity_id


class DeriveEntityIdTests(unittest.TestCase):
    def test_derive_entity_id_deterministic(self) -> None:
        """Test that same inputs produce the same identity."""
        id1 = derive_entity_id("candidate-123", "auth-456")
        id2 = derive_entity_id("candidate-123", "auth-456")
        self.assertEqual(id1, id2)
        self.assertTrue(id1.startswith("dbio:entity:registration:"))

    def test_derive_entity_id_different_inputs(self) -> None:
        """Test that different inputs produce different identities."""
        id1 = derive_entity_id("candidate-123", "auth-456")
        id2 = derive_entity_id("candidate-999", "auth-456")
        id3 = derive_entity_id("candidate-123", "auth-999")
        self.assertNotEqual(id1, id2)
        self.assertNotEqual(id1, id3)
        self.assertNotEqual(id2, id3)

    def test_derive_entity_id_strips_whitespace(self) -> None:
        """Test that inputs are stripped of whitespace before derivation."""
        id1 = derive_entity_id("candidate-123", "auth-456")
        id2 = derive_entity_id("  candidate-123  ", " auth-456\n")
        self.assertEqual(id1, id2)

    def test_derive_entity_id_rejects_empty_candidate(self) -> None:
        """Test that empty or whitespace-only candidate ID is rejected."""
        with self.assertRaisesRegex(ValueError, "candidate_id must be a non-empty string"):
            derive_entity_id("", "auth-456")

        with self.assertRaisesRegex(ValueError, "candidate_id must be a non-empty string"):
            derive_entity_id("   ", "auth-456")

    def test_derive_entity_id_rejects_empty_authorization(self) -> None:
        """Test that empty or whitespace-only authorization ID is rejected."""
        with self.assertRaisesRegex(ValueError, "authorization_id must be a non-empty string"):
            derive_entity_id("candidate-123", "")

        with self.assertRaisesRegex(ValueError, "authorization_id must be a non-empty string"):
            derive_entity_id("candidate-123", "   ")

    def test_derive_entity_id_rejects_non_string_inputs(self) -> None:
        """Test that non-string inputs are rejected."""
        with self.assertRaisesRegex(ValueError, "candidate_id must be a non-empty string"):
            derive_entity_id(None, "auth-456")  # type: ignore

        with self.assertRaisesRegex(ValueError, "authorization_id must be a non-empty string"):
            derive_entity_id("candidate-123", 123)  # type: ignore


if __name__ == "__main__":
    unittest.main()
