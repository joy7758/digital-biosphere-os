"""Tests for malformed synthetic Tool Call fixtures."""

import unittest

from adapters.mcp import MappingStatus, adapt_tool_call
from fixtures import synthetic_tool_call
from validator import ValidationStatus


class MalformedToolCallTests(unittest.TestCase):
    def test_non_mapping_fixture_is_rejected(self) -> None:
        result = adapt_tool_call("not a mapping")
        self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
        self.assertEqual(result.validation_result.result, ValidationStatus.FAIL)
        self.assertEqual(result.validation_result.errors[0].path, "$")

    def test_missing_or_empty_tool_call_id_or_name_is_rejected(self) -> None:
        for field in ("tool_call_id", "tool_name"):
            fixture = synthetic_tool_call()
            fixture[field] = ""
            result = adapt_tool_call(fixture)
            self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
            self.assertEqual(result.validation_result.errors[0].path, f"$.{field}")

            fixture[field] = 123
            result = adapt_tool_call(fixture)
            self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
            self.assertEqual(result.validation_result.errors[0].path, f"$.{field}")

    def test_non_mapping_reference_is_rejected(self) -> None:
        for field in (
            "arguments_reference",
            "context_reference",
            "source_reference",
            "entity_reference",
        ):
            fixture = synthetic_tool_call()
            fixture[field] = "not a mapping"
            result = adapt_tool_call(fixture)
            self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
            self.assertEqual(result.validation_result.errors[0].path, f"$.{field}")

    def test_extra_source_reference_fields_are_rejected(self) -> None:
        fixture = synthetic_tool_call()
        fixture["source_reference"]["extra"] = "value"
        result = adapt_tool_call(fixture)
        self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
        self.assertEqual(result.validation_result.errors[0].path, "$.source_reference.extra")

    def test_empty_or_non_string_source_reference_fields_are_rejected(self) -> None:
        fixture = synthetic_tool_call()
        fixture["source_reference"]["version"] = ""
        result = adapt_tool_call(fixture)
        self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
        self.assertEqual(result.validation_result.errors[0].path, "$.source_reference")

        fixture["source_reference"]["version"] = 123
        result = adapt_tool_call(fixture)
        self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
        self.assertEqual(result.validation_result.errors[0].path, "$.source_reference")

    def test_wrong_source_namespace_is_rejected(self) -> None:
        fixture = synthetic_tool_call()
        fixture["source_reference"]["namespace"] = "wrong:namespace"
        result = adapt_tool_call(fixture)
        self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
        self.assertEqual(result.validation_result.errors[0].path, "$.source_reference.namespace")

    def test_empty_source_id_is_rejected(self) -> None:
        fixture = synthetic_tool_call()
        fixture["source_reference"]["source_id"] = ""
        result = adapt_tool_call(fixture)
        self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
        self.assertEqual(result.validation_result.errors[0].path, "$.source_reference") # it hits the all fields check first!

    def test_empty_or_non_string_reference_fields_are_rejected(self) -> None:
        for field in ("arguments_reference", "context_reference", "entity_reference"):
            fixture = synthetic_tool_call()
            fixture[field]["version"] = ""
            result = adapt_tool_call(fixture)
            self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
            self.assertEqual(result.validation_result.errors[0].path, f"$.{field}")

            fixture[field]["version"] = 123
            result = adapt_tool_call(fixture)
            self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
            self.assertEqual(result.validation_result.errors[0].path, f"$.{field}")

    def test_wrong_reference_namespace_is_rejected(self) -> None:
        for field in ("arguments_reference", "context_reference", "entity_reference"):
            fixture = synthetic_tool_call()
            fixture[field]["namespace"] = "wrong:namespace"
            result = adapt_tool_call(fixture)
            self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
            self.assertEqual(result.validation_result.errors[0].path, f"$.{field}.namespace")

    def test_wrong_reference_type_is_rejected(self) -> None:
        for field in ("arguments_reference", "context_reference", "entity_reference"):
            fixture = synthetic_tool_call()
            fixture[field]["reference_type"] = "WRONG"
            result = adapt_tool_call(fixture)
            self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
            self.assertEqual(result.validation_result.errors[0].path, f"$.{field}.reference_type")

if __name__ == "__main__":
    unittest.main()
