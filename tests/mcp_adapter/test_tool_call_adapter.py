"""Tests for MCPToolCallAdapter and its internal traversal logic."""

import unittest

from adapters.mcp.tool_call_adapter import MCPToolCallAdapter, _walk_keys
from adapters.mcp import MappingStatus, adapt_tool_call
from fixtures import synthetic_tool_call


class ToolCallAdapterTests(unittest.TestCase):
    def test_walk_keys_with_lists_and_tuples(self) -> None:
        """Test that _walk_keys correctly traverses lists and tuples."""
        data = {
            "a": [
                {"b": 1},
                {"c": 2}
            ],
            "d": (
                {"e": 3},
            )
        }
        keys = list(_walk_keys(data))
        self.assertEqual(
            keys,
            [
                ("$.a", "a"),
                ("$.a[0].b", "b"),
                ("$.a[1].c", "c"),
                ("$.d", "d"),
                ("$.d[0].e", "e")
            ]
        )

    def test_prohibited_field_in_list_is_rejected(self) -> None:
        """Test that a prohibited field inside a list is detected and rejected."""
        fixture = synthetic_tool_call()
        # Nesting a prohibited field ('permission') inside a list.
        # This will be caught by _validate_basic_structure before reference validation.
        fixture["arguments_reference"] = {
            "reference_id": "fixture:input",
            "reference_type": "INPUT",
            "namespace": "extension:dbos-mcp-synthetic",
            "version": "v0.1",
            "source": "fixture:mcp-tool-call-adapter-v0.1",
            "status": "DECLARED",
            "some_list": [{"permission": "ALLOW"}]
        }

        result = adapt_tool_call(fixture)

        self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
        self.assertIsNotNone(result.adapter_errors)
        self.assertTrue(len(result.adapter_errors) > 0)
        self.assertIn("permission", result.adapter_errors[0].field_reference)

    def test_prohibited_field_in_tuple_is_rejected(self) -> None:
        """Test that a prohibited field inside a tuple is detected and rejected."""
        fixture = synthetic_tool_call()
        # Nesting a prohibited field ('evidence') inside a tuple.
        fixture["context_reference"] = {
            "reference_id": "fixture:context",
            "reference_type": "CONTEXT",
            "namespace": "extension:dbos-mcp-synthetic",
            "version": "v0.1",
            "source": "fixture:mcp-tool-call-adapter-v0.1",
            "status": "DECLARED",
            "some_tuple": ({"evidence": "truth"},)
        }

        result = adapt_tool_call(fixture)

        self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
        self.assertIsNotNone(result.adapter_errors)
        self.assertTrue(len(result.adapter_errors) > 0)
        self.assertIn("evidence", result.adapter_errors[0].field_reference)

    def test_direct_instantiation(self) -> None:
        """Test direct instantiation of MCPToolCallAdapter."""
        adapter = MCPToolCallAdapter()
        fixture = synthetic_tool_call()
        result = adapter.adapt(fixture)
        self.assertEqual(result.mapping_status, MappingStatus.MAPPED)


if __name__ == "__main__":
    unittest.main()
