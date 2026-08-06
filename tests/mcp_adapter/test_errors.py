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


if __name__ == "__main__":
    unittest.main()
