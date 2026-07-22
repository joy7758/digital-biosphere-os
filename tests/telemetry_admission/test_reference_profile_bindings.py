"""Agent-readable integrity and executable-node checks for OTel profiles."""

from __future__ import annotations

import importlib
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from dbos.telemetry_admission.references import (
    OTEL_SCHEMA_FILENAME,
    REFERENCE_ARTIFACT_DIGESTS,
    SCHEMA_RESOURCE_CONFORMANCE_FILENAME,
    SCHEMA_RESOURCE_RESULT_SCHEMA_FILENAME,
    SEMANTIC_CONFORMANCE_FILENAME,
    SEMANTIC_MAPPING_FILENAME,
    SEMANTIC_RESULT_SCHEMA_FILENAME,
    read_pinned_bytes,
    read_pinned_json,
    read_pinned_yaml,
    sha256_digest,
)


ROOT = Path(__file__).resolve().parent
SEMANTIC_BINDING = ROOT / "semantic_pr_g2_bindings.v0.1.json"
SCHEMA_RESOURCE_BINDING = ROOT / "schema_resource_pr_g2_bindings.v0.1.json"


class ReferenceProfileBindingTests(unittest.TestCase):
    def test_all_vendored_artifacts_match_exact_human_adopted_digests(self) -> None:
        self.assertEqual(
            set(REFERENCE_ARTIFACT_DIGESTS),
            {
                SEMANTIC_MAPPING_FILENAME,
                SEMANTIC_CONFORMANCE_FILENAME,
                SCHEMA_RESOURCE_CONFORMANCE_FILENAME,
                SEMANTIC_RESULT_SCHEMA_FILENAME,
                SCHEMA_RESOURCE_RESULT_SCHEMA_FILENAME,
                OTEL_SCHEMA_FILENAME,
            },
        )
        for filename, expected in REFERENCE_ARTIFACT_DIGESTS.items():
            self.assertEqual(sha256_digest(read_pinned_bytes(filename)), expected)
        self.assertEqual(
            read_pinned_json(SEMANTIC_MAPPING_FILENAME)["catalog_id"],
            "TMAI-OTEL-SEMANTIC-MAPPING-0.1",
        )
        self.assertEqual(read_pinned_yaml(OTEL_SCHEMA_FILENAME)["file_format"], "1.1.0")
        for filename in (
            SEMANTIC_RESULT_SCHEMA_FILENAME,
            SCHEMA_RESOURCE_RESULT_SCHEMA_FILENAME,
        ):
            schema = read_pinned_json(filename)
            self.assertEqual(schema["type"], "object")
            Draft202012Validator.check_schema(schema)

    def test_authorized_case_bindings_resolve_to_executable_test_nodes(self) -> None:
        for path in (SEMANTIC_BINDING, SCHEMA_RESOURCE_BINDING):
            binding = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(
                binding["authorized_case_count"], len(binding["authorized_cases"])
            )
            for case in binding["authorized_cases"]:
                module_name, class_name, method_name = case["test_node"].split(".")
                module = importlib.import_module(
                    f"tests.telemetry_admission.{module_name}"
                )
                test_class = getattr(module, class_name)
                self.assertTrue(callable(getattr(test_class, method_name, None)))
                self.assertEqual(case["status"], "BOUND_TO_EXECUTABLE_TEST")

    def test_unauthorized_deployment_cases_remain_explicitly_blocked(self) -> None:
        expected = {
            SEMANTIC_BINDING: (32, 14),
            SCHEMA_RESOURCE_BINDING: (36, 9),
        }
        for path, counts in expected.items():
            binding = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(
                (
                    binding["authorized_case_count"],
                    binding["blocked_not_authorized_case_count"],
                ),
                counts,
            )
            self.assertTrue(
                all(
                    case["status"] == "BLOCKED_NOT_AUTHORIZED"
                    for case in binding["blocked_not_authorized_cases"]
                )
            )
            self.assertFalse(any(binding["effects"].values()))


if __name__ == "__main__":
    unittest.main()
