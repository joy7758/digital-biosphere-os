"""UNKNOWN result format tests."""

from __future__ import annotations

import unittest

from validator import ValidationStatus, validate_object

from assertions import assert_result_contract
from fixtures import synthetic_entity


class UnknownFormatTests(unittest.TestCase):
    def test_unknown_uses_frozen_result_format(self) -> None:
        target = synthetic_entity()
        target["lifecycle_state"] = "ACTIVE"
        payload = assert_result_contract(self, validate_object(target), "UNKNOWN")
        self.assertTrue(payload["errors"])

    def test_unknown_never_defaults_to_pass(self) -> None:
        target = synthetic_entity()
        target["status"] = "UNKNOWN"
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.UNKNOWN)
        self.assertFalse(result.passed)


if __name__ == "__main__":
    unittest.main()
