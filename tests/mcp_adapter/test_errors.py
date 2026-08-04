"""Tests for MCP Adapter error handling and conversion."""

from __future__ import annotations

import unittest

from adapters.mcp.errors import AdapterError, AdapterErrorCode
from validator import ValidationIssue


class AdapterErrorTests(unittest.TestCase):
    def test_post_init_validation(self) -> None:
        """Test that invalid fields raise ValueError during initialization."""

        with self.assertRaisesRegex(ValueError, "message must be a non-empty string"):
            AdapterError(
                code=AdapterErrorCode.UNKNOWN_RESOURCE,
                message="",
                field_reference="$.test",
                resolution_hint="Fix it",
            )

        with self.assertRaisesRegex(ValueError, "field_reference must be a non-empty string"):
            AdapterError(
                code=AdapterErrorCode.UNKNOWN_RESOURCE,
                message="Error",
                field_reference="",
                resolution_hint="Fix it",
            )

        with self.assertRaisesRegex(ValueError, "resolution_hint must be a non-empty string"):
            AdapterError(
                code=AdapterErrorCode.UNKNOWN_RESOURCE,
                message="Error",
                field_reference="$.test",
                resolution_hint="",
            )

    def test_to_validation_issue_conversion(self) -> None:
        """Test conversion to ValidationIssue with default result_code."""
        error = AdapterError(
            code=AdapterErrorCode.INVALID_TOOL_REFERENCE,
            message="Tool not found",
            field_reference="$.tool_name",
            resolution_hint="Check tool name",
        )

        issue = error.to_validation_issue()

        self.assertIsInstance(issue, ValidationIssue)
        self.assertEqual(issue.code, "INVALID_TOOL_REFERENCE")
        self.assertEqual(issue.path, "$.tool_name")
        self.assertEqual(issue.message, "Tool not found")
        self.assertEqual(issue.rule, "mcp_adapter_invalid_tool_reference")
        self.assertEqual(issue.resolution_hint, "Check tool name")

    def test_to_validation_issue_with_custom_result_code(self) -> None:
        """Test conversion to ValidationIssue with explicit result_code."""
        error = AdapterError(
            code=AdapterErrorCode.VERSION_MISMATCH,
            message="Wrong version",
            field_reference="$.version",
            resolution_hint="Update version",
        )

        issue = error.to_validation_issue(result_code="CUSTOM_CODE")

        self.assertEqual(issue.code, "CUSTOM_CODE")
        self.assertEqual(issue.rule, "mcp_adapter_version_mismatch")


if __name__ == "__main__":
    unittest.main()
