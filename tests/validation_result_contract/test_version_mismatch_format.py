"""VERSION_MISMATCH result format tests."""

from __future__ import annotations

import unittest

from validator import validate_object

from assertions import assert_result_contract
from fixtures import synthetic_entity


class VersionMismatchFormatTests(unittest.TestCase):
    def test_version_mismatch_uses_frozen_result_format(self) -> None:
        target = synthetic_entity()
        target["version"] = "v9.9"
        payload = assert_result_contract(
            self,
            validate_object(target),
            "VERSION_MISMATCH",
        )
        self.assertTrue(payload["errors"])

    def test_version_mismatch_preserves_observed_target(self) -> None:
        target = synthetic_entity()
        target["version"] = "v9.9"
        payload = validate_object(target).to_dict()
        self.assertEqual(payload["target_reference"], target["object_id"])
        self.assertTrue(
            any(item["field_reference"] == "$.version" for item in payload["errors"])
        )


if __name__ == "__main__":
    unittest.main()
