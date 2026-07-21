"""A visible Tool remains a Tool reference and never becomes Capability."""

from __future__ import annotations

import unittest

from adapters.mcp import MappingStatus, adapt_tool_call
from fixtures import synthetic_tool_call


def _all_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key).lower())
            keys.update(_all_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_all_keys(child))
    return keys


class CapabilityInferenceBlockTests(unittest.TestCase):
    def test_capability_claim_fields_are_rejected(self) -> None:
        for field in ("capability", "capabilities", "capability_grant"):
            with self.subTest(field=field):
                result = adapt_tool_call(synthetic_tool_call(**{field: "claimed"}))
                self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
                self.assertIsNone(result.candidate)

    def test_tool_name_never_adds_capability_or_permission_fields(self) -> None:
        result = adapt_tool_call(
            synthetic_tool_call(tool_name="capability-looking-tool-name")
        )
        serialized = result.to_dict()
        keys = _all_keys(serialized["candidate"])

        self.assertEqual(result.mapping_status, MappingStatus.MAPPED)
        self.assertNotIn("capability", keys)
        self.assertNotIn("capability_grant", keys)
        self.assertNotIn("permission", keys)
        self.assertNotIn("evidence", keys)

    def test_unknown_top_level_field_is_rejected_fail_closed(self) -> None:
        result = adapt_tool_call(synthetic_tool_call(unregistered_extension="value"))

        self.assertEqual(result.mapping_status, MappingStatus.REJECTED)
        self.assertIsNone(result.candidate)


if __name__ == "__main__":
    unittest.main()
