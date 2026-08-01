#!/usr/bin/env python3
"""Public facade tests for the installable DBOS Developer Preview candidate."""

from __future__ import annotations

import unittest

import dbos


class PublicFacadeTests(unittest.TestCase):
    def test_facade_exports_only_bounded_object_and_validation_symbols(self) -> None:
        expected = {
            "CapabilityObject",
            "EntityObject",
            "EvidenceReferenceObject",
            "ExecutionObject",
            "SchemaReference",
            "ValidationIssue",
            "ValidationResult",
            "ValidationStatus",
            "VerificationObject",
            "object_to_dict",
            "object_to_json",
            "validate_object",
        }
        self.assertEqual(set(dbos.__all__), expected)

    def test_facade_exports_no_agent_runtime_permission_or_authority(self) -> None:
        forbidden_tokens = ("agent", "runtime", "permission", "authority", "execute")
        exported = {name.lower() for name in dbos.__all__}
        for token in forbidden_tokens:
            self.assertFalse(any(token in name for name in exported))

    def test_preview_version_is_explicitly_developmental(self) -> None:
        self.assertEqual(dbos.__version__, "0.1.0.dev0")


if __name__ == "__main__":
    unittest.main()
