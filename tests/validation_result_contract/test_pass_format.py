"""PASS result format tests."""

from __future__ import annotations

import unittest

from validator import validate_object

from assertions import assert_result_contract
from fixtures import synthetic_entity


class PassFormatTests(unittest.TestCase):
    def test_pass_uses_frozen_result_format(self) -> None:
        payload = assert_result_contract(self, validate_object(synthetic_entity()), "PASS")
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["warnings"], [])

    def test_pass_preserves_schema_identity_without_authority(self) -> None:
        payload = validate_object(synthetic_entity()).to_dict()
        self.assertEqual(
            payload["schema_reference"]["schema_id"],
            "dbio://schema/entity-object/v0.1",
        )
        self.assertTrue(payload["schema_reference"]["schema_digest"].startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
