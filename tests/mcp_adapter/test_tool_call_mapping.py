"""Positive synthetic Tool Call mapping tests with no external effects."""

from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from adapters.mcp import MappingStatus, adapt_tool_call
from adapters.mcp import tool_call_adapter
from fixtures import SYNTHETIC_NAMESPACE, synthetic_tool_call
from validator import ValidationStatus


class ToolCallMappingTests(unittest.TestCase):
    def test_maps_to_inert_execution_candidate(self) -> None:
        fixture = synthetic_tool_call()
        result = adapt_tool_call(fixture)

        self.assertEqual(result.mapping_status, MappingStatus.MAPPED)
        self.assertIsNotNone(result.candidate)
        self.assertTrue(result.validator_invoked)
        self.assertTrue(
            result.execution_candidate_id.startswith(
                "extension:dbos-mcp-tool-call-candidate:"
            )
        )
        self.assertEqual(result.candidate.object_type, "EXECUTION")
        self.assertEqual(result.candidate.status, "UNKNOWN")
        self.assertIsNone(result.candidate.output_reference)

    def test_preserves_context_source_entity_and_arguments_references(self) -> None:
        fixture = synthetic_tool_call()
        result = adapt_tool_call(fixture)
        candidate = result.candidate
        self.assertIsNotNone(candidate)

        self.assertEqual(dict(candidate.source), fixture["source_reference"])
        self.assertEqual(dict(candidate.context_reference), fixture["context_reference"])
        self.assertEqual(dict(candidate.entity_reference), fixture["entity_reference"])
        self.assertEqual(dict(candidate.input_reference), fixture["arguments_reference"])

    def test_tool_name_maps_only_to_external_task_reference(self) -> None:
        result = adapt_tool_call(synthetic_tool_call(tool_name="synthetic.tool/name"))
        candidate = result.candidate
        self.assertIsNotNone(candidate)

        self.assertEqual(candidate.task_reference["reference_type"], "TOOL")
        self.assertEqual(candidate.task_reference["namespace"], SYNTHETIC_NAMESPACE)
        self.assertIn("synthetic.tool%2Fname", candidate.task_reference["reference_id"])

    def test_existing_validator_is_invoked_and_unknown_remains_unknown(self) -> None:
        result = adapt_tool_call(synthetic_tool_call())

        self.assertEqual(result.validation_result.result, ValidationStatus.UNKNOWN)
        self.assertEqual(result.validation_result.validator_version, "v0.1")
        self.assertTrue(
            any(
                issue.rule == "unknown_remains_unknown"
                for issue in result.validation_result.errors
            )
        )

    def test_mapping_is_deterministic_and_does_not_mutate_input(self) -> None:
        fixture = synthetic_tool_call()
        original = copy.deepcopy(fixture)

        first = adapt_tool_call(fixture)
        second = adapt_tool_call(fixture)

        self.assertEqual(first.execution_candidate_id, second.execution_candidate_id)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(fixture, original)

    def test_result_is_json_compatible_data(self) -> None:
        result = adapt_tool_call(synthetic_tool_call()).to_dict()
        self.assertEqual(result["mapping_status"], "MAPPED")
        self.assertEqual(result["candidate"]["object_type"], "EXECUTION")
        self.assertEqual(result["validation_result"]["result"], "UNKNOWN")
        self.assertEqual(result["adapter_errors"], [])

    def test_canonical_validator_is_actually_called_once(self) -> None:
        with patch.object(
            tool_call_adapter,
            "validate_object",
            wraps=tool_call_adapter.validate_object,
        ) as validator_call:
            result = adapt_tool_call(synthetic_tool_call())

        validator_call.assert_called_once_with(result.candidate)
        self.assertTrue(result.validator_invoked)


if __name__ == "__main__":
    unittest.main()
