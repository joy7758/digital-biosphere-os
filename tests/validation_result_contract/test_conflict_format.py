"""CONFLICT result format tests."""

from __future__ import annotations

import unittest

from validator import validate_object

from assertions import assert_result_contract
from fixtures import synthetic_entity


class ConflictFormatTests(unittest.TestCase):
    def test_conflict_uses_frozen_result_format(self) -> None:
        target = synthetic_entity()
        target["entity_id"] = "dbio://repository/conflicting-result-contract-fixture/v0.1"
        payload = assert_result_contract(self, validate_object(target), "CONFLICT")
        self.assertTrue(payload["errors"])

    def test_conflict_diagnostic_identifies_field_without_merging(self) -> None:
        target = synthetic_entity()
        target["entity_id"] = "dbio://repository/conflicting-result-contract-fixture/v0.1"
        payload = validate_object(target).to_dict()
        self.assertTrue(
            any(item["field_reference"] == "$.entity_id" for item in payload["errors"])
        )


if __name__ == "__main__":
    unittest.main()
