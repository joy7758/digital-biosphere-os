"""Missing attribution inputs stay UNKNOWN and create no candidate."""

from __future__ import annotations

import unittest

from adapters.mcp import AdapterErrorCode, MappingStatus, adapt_tool_call
from fixtures import synthetic_tool_call
from validator import ValidationStatus


class MissingAttributionTests(unittest.TestCase):
    def test_missing_source_context_or_protocol_is_unknown(self) -> None:
        for field in ("source_reference", "context_reference", "protocol_revision"):
            fixture = synthetic_tool_call()
            fixture.pop(field)
            with self.subTest(field=field):
                result = adapt_tool_call(fixture)
                self.assertEqual(result.mapping_status, MappingStatus.UNKNOWN)
                self.assertEqual(result.validation_result.result, ValidationStatus.UNKNOWN)
                self.assertIsNone(result.candidate)
                self.assertFalse(result.validator_invoked)

    def test_missing_entity_reference_is_unknown_not_inferred(self) -> None:
        fixture = synthetic_tool_call()
        fixture.pop("entity_reference")

        result = adapt_tool_call(fixture)

        self.assertEqual(result.mapping_status, MappingStatus.UNKNOWN)
        self.assertIsNone(result.candidate)
        self.assertEqual(
            result.adapter_errors[0].code,
            AdapterErrorCode.UNRESOLVED_CONTEXT,
        )

    def test_missing_source_has_no_invented_adapter_error_code(self) -> None:
        fixture = synthetic_tool_call()
        fixture.pop("source_reference")

        result = adapt_tool_call(fixture)

        self.assertEqual(result.adapter_errors, ())
        self.assertEqual(result.validation_result.errors[0].code, "UNKNOWN")

    def test_incomplete_source_descriptor_fails_closed(self) -> None:
        fixture = synthetic_tool_call(source_reference={"namespace": "extension:dbos-mcp-synthetic"})

        result = adapt_tool_call(fixture)

        self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
        self.assertEqual(result.validation_result.result, ValidationStatus.FAIL)
        self.assertIsNone(result.candidate)

    def test_malformed_reference_cannot_create_partial_candidate(self) -> None:
        cases = (
            ("arguments_reference", {"reference_id": "fixture:input"}),
            ("context_reference", {"reference_type": "CONTEXT"}),
            ("entity_reference", {"reference_type": "TOOL"}),
            (
                "arguments_reference",
                {
                    **synthetic_tool_call()["arguments_reference"],
                    "unexpected": "value",
                },
            ),
        )
        for field, value in cases:
            with self.subTest(field=field):
                result = adapt_tool_call(synthetic_tool_call(**{field: value}))
                self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
                self.assertEqual(result.validation_result.result, ValidationStatus.FAIL)
                self.assertIsNone(result.candidate)
                self.assertFalse(result.validator_invoked)


if __name__ == "__main__":
    unittest.main()
