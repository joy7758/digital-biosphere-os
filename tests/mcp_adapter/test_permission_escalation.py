"""Permission and evidence escalation attempts are rejected before mapping."""

from __future__ import annotations

import unittest

from adapters.mcp import AdapterErrorCode, MappingStatus, adapt_tool_call
from fixtures import synthetic_tool_call
from validator import ValidationStatus


class PermissionEscalationTests(unittest.TestCase):
    def test_permission_fields_are_rejected(self) -> None:
        for field in ("tool_permission", "permission", "permissions", "permission_grant"):
            with self.subTest(field=field):
                result = adapt_tool_call(synthetic_tool_call(**{field: "ALLOW"}))
                self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
                self.assertEqual(result.validation_result.result, ValidationStatus.FAIL)
                self.assertEqual(
                    result.adapter_errors[0].code,
                    AdapterErrorCode.INVALID_TOOL_REFERENCE,
                )
                self.assertIsNone(result.candidate)

    def test_nested_permission_field_is_rejected(self) -> None:
        fixture = synthetic_tool_call()
        fixture["arguments_reference"]["permission"] = "ALLOW"

        result = adapt_tool_call(fixture)

        self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
        self.assertIn("permission", result.adapter_errors[0].field_reference)

    def test_tool_result_cannot_become_evidence(self) -> None:
        for field in ("tool_result", "evidence", "evidence_truth"):
            with self.subTest(field=field):
                result = adapt_tool_call(
                    synthetic_tool_call(**{field: "synthetic-value"})
                )
                self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
                self.assertIsNone(result.candidate)
                self.assertFalse(result.validator_invoked)


if __name__ == "__main__":
    unittest.main()
