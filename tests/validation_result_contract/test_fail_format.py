"""FAIL result format tests."""

from __future__ import annotations

import unittest

from validator import validate_object

from assertions import assert_result_contract
from fixtures import synthetic_entity


class FailFormatTests(unittest.TestCase):
    def test_fail_uses_frozen_result_format(self) -> None:
        target = synthetic_entity()
        del target["owner_reference"]
        payload = assert_result_contract(self, validate_object(target), "FAIL")
        self.assertTrue(payload["errors"])
        self.assertTrue(any(item["error_code"] == "INVALID" for item in payload["errors"]))

    def test_fail_errors_use_five_field_error_object(self) -> None:
        target = synthetic_entity()
        target["unexpected_field"] = True
        payload = validate_object(target).to_dict()
        self.assertTrue(all(item["severity"] == "ERROR" for item in payload["errors"]))
        self.assertTrue(all(item["resolution_hint"] for item in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
