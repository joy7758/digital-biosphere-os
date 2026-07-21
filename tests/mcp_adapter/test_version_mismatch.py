"""Synthetic version allowlist tests; no real MCP revision is supported."""

from __future__ import annotations

import unittest

from adapters.mcp import AdapterErrorCode, MappingStatus, adapt_tool_call
from fixtures import synthetic_tool_call
from validator import ValidationStatus


class VersionMismatchTests(unittest.TestCase):
    def test_unknown_protocol_revision_is_not_auto_accepted(self) -> None:
        for revision in ("latest", "2026-07-21", "real-mcp-version-placeholder"):
            with self.subTest(revision=revision):
                result = adapt_tool_call(
                    synthetic_tool_call(protocol_revision=revision)
                )
                self.assertEqual(result.mapping_status, MappingStatus.VERSION_MISMATCH)
                self.assertEqual(
                    result.validation_result.result,
                    ValidationStatus.VERSION_MISMATCH,
                )
                self.assertEqual(
                    result.adapter_errors[0].code,
                    AdapterErrorCode.VERSION_MISMATCH,
                )
                self.assertIsNone(result.candidate)

    def test_unknown_mapping_profile_is_not_auto_accepted(self) -> None:
        result = adapt_tool_call(
            synthetic_tool_call(mapping_profile_version="latest")
        )

        self.assertEqual(result.mapping_status, MappingStatus.VERSION_MISMATCH)
        self.assertFalse(result.validator_invoked)
        self.assertIsNone(result.candidate)

    def test_missing_protocol_is_unknown_not_defaulted(self) -> None:
        fixture = synthetic_tool_call()
        fixture.pop("protocol_revision")

        result = adapt_tool_call(fixture)

        self.assertEqual(result.mapping_status, MappingStatus.UNKNOWN)
        self.assertEqual(result.validation_result.result, ValidationStatus.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
