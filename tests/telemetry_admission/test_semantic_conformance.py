"""Execute the exact 32 DQ-018/PR-G2 semantic conformance cases."""

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from dbos.telemetry_admission.contracts import (
    SEMANTIC_CONFORMANCE_CATALOG_DIGEST,
    SEMANTIC_MAPPING_CATALOG_DIGEST,
    SEMANTIC_PR_G2_CASE_COUNT,
)
from dbos.telemetry_admission.semantic import (
    SemanticMappingError,
    SemanticMetadataMapper,
    SemanticSourceBinding,
)


ROOT = Path(__file__).resolve().parents[2]
CATALOG = (
    ROOT
    / "dbos"
    / "telemetry_admission"
    / "profiles"
    / "opentelemetry-semantic-conformance-cases.v0.1.json"
)


def _catalog() -> dict[str, object]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def _required_case_ids() -> frozenset[str]:
    return frozenset(
        case["case_id"] for case in _catalog()["cases"] if "PR-G2" in case["gate_refs"]
    )


def _fields(start: int, end: int) -> dict[str, object]:
    catalog = json.loads(
        (
            ROOT
            / "dbos"
            / "telemetry_admission"
            / "profiles"
            / "opentelemetry-semantic-mapping.v0.1.json"
        ).read_text(encoding="utf-8")
    )
    by_id = {item["mapping_id"]: item["upstream_field"] for item in catalog["mappings"]}
    return {by_id[f"OTEL-SM-{index:03d}"]: index for index in range(start, end + 1)}


class SemanticConformanceTests(unittest.TestCase):
    """Each generated method is bound one-to-one to a frozen DBA case ID."""

    maxDiff = None

    def run_case(self, case_id: str) -> None:
        mapper = SemanticMetadataMapper()

        if case_id == "SEM-CF-VSN-001":
            result = mapper.map_attributes({"service.name": "service-a"})
            self.assertEqual(result.status, "MAPPED")
            self.assertEqual(mapper.mapping_count, 47)
            self.assertFalse(any(result.effects.values()))
        elif case_id == "SEM-CF-VSN-002":
            result = mapper.map_attributes(
                {"service.name": "service-a"},
                source_binding=SemanticSourceBinding(core_semconv_reference="latest"),
            )
            self.assertEqual(result.status, "REJECTED")
            self.assertIn("SEM_CORE_SEMCONV_REFERENCE_MISMATCH", result.reason_codes)
        elif case_id == "SEM-CF-VSN-003":
            with self.assertRaisesRegex(
                SemanticMappingError, "TA_REFERENCE_DIGEST_MISMATCH"
            ):
                SemanticMetadataMapper(expected_mapping_digest=f"sha256:{'0' * 64}")
        elif case_id == "SEM-CF-VSN-004":
            result = mapper.map_attributes(
                {"gen_ai.operation.name": "chat"},
                source_binding=SemanticSourceBinding(genai_semconv_commit="unknown"),
            )
            self.assertEqual(result.status, "REJECTED")
            self.assertIn("SEM_GENAI_COMMIT_MISMATCH", result.reason_codes)
        elif case_id == "SEM-CF-VSN-005":
            result = mapper.map_attributes(
                {"service.name": "service-a"},
                source_binding=SemanticSourceBinding(
                    instrumentation_scope_schema_url=None
                ),
            )
            self.assertEqual(result.status, "PARTIAL")
            self.assertEqual(len(result.projections), 1)
            self.assertIn("SEM_SCOPE_SCHEMA_URL_UNKNOWN", result.limitations)
        elif case_id.startswith("SEM-CF-CORE-"):
            ranges = {
                "SEM-CF-CORE-001": (1, 5),
                "SEM-CF-CORE-002": (6, 10),
                "SEM-CF-CORE-003": (11, 13),
                "SEM-CF-CORE-004": (14, 16),
                "SEM-CF-CORE-005": (17, 20),
            }
            start, end = ranges[case_id]
            result = mapper.map_attributes(_fields(start, end))
            self.assertEqual(result.status, "MAPPED")
            self.assertEqual(
                {item.mapping_id for item in result.projections},
                {f"OTEL-SM-{index:03d}" for index in range(start, end + 1)},
            )
            self.assertTrue(
                all(item.stability == "STABLE" for item in result.projections)
            )
            self.assertFalse(any(result.effects.values()))
        elif case_id.startswith("SEM-CF-GENAI-"):
            ranges = {
                "SEM-CF-GENAI-001": (21, 22),
                "SEM-CF-GENAI-002": (23, 25),
                "SEM-CF-GENAI-003": (26, 27),
                "SEM-CF-GENAI-004": (28, 29),
                "SEM-CF-GENAI-005": (30, 31),
                "SEM-CF-GENAI-006": (32, 36),
            }
            start, end = ranges[case_id]
            result = mapper.map_attributes(_fields(start, end))
            self.assertEqual(result.status, "PARTIAL")
            self.assertEqual(len(result.projections), end - start + 1)
            self.assertTrue(
                all(item.stability == "DEVELOPMENT" for item in result.projections)
            )
            self.assertIn("SEM_GENAI_DEVELOPMENT_LANE", result.limitations)
            self.assertFalse(any(result.effects.values()))
        elif case_id.startswith("SEM-CF-DRIFT-"):
            if case_id in {
                "SEM-CF-DRIFT-001",
                "SEM-CF-DRIFT-002",
                "SEM-CF-DRIFT-003",
            }:
                index = 44 + int(case_id[-1])
                result = mapper.map_attributes(_fields(index, index))
                self.assertIn("SEM_DEPRECATED_FIELD_REJECTED", result.reason_codes)
                self.assertTrue(
                    any(
                        item.startswith("SEM_MIGRATION_REQUIRED_")
                        for item in result.limitations
                    )
                )
            elif case_id == "SEM-CF-DRIFT-004":
                result = mapper.map_attributes({"future.unknown.field": "value"})
                self.assertIn("SEM_UNKNOWN_FIELD_REJECTED", result.reason_codes)
                self.assertEqual(len(result.unknown_field_digests), 1)
            else:
                result = mapper.map_attributes(
                    {"service.name": "service-a"},
                    stability_overrides={"OTEL-SM-001": "DEVELOPMENT"},
                )
                self.assertIn("SEM_STABILITY_DRIFT", result.reason_codes)
            self.assertEqual(result.status, "REJECTED")
            self.assertEqual(result.projections, ())
        elif case_id == "SEM-CF-AUTH-001":
            for field in ("tmai.permission", "dbos.entity_id", "saee.fitness"):
                result = mapper.map_attributes({field: "injected"})
                self.assertIn("SEM_AUTHORITY_FIELD_REJECTED", result.reason_codes)
                self.assertFalse(any(result.effects.values()))
        elif case_id == "SEM-CF-AUTH-002":
            for field in ("permission", "authorization", "decision", "evidence"):
                result = mapper.map_attributes({field: "injected"})
                self.assertIn("SEM_AUTHORITY_FIELD_REJECTED", result.reason_codes)
                self.assertFalse(any(result.effects.values()))
        elif case_id in {
            "SEM-CF-AUTH-003",
            "SEM-CF-AUTH-004",
            "SEM-CF-AUTH-005",
            "SEM-CF-AUTH-006",
            "SEM-CF-AUTH-007",
        }:
            fields = {
                "SEM-CF-AUTH-003": _fields(3, 3) | _fields(23, 25),
                "SEM-CF-AUTH-004": _fields(14, 16),
                "SEM-CF-AUTH-005": _fields(32, 34),
                "SEM-CF-AUTH-006": _fields(35, 36),
                "SEM-CF-AUTH-007": {"service.name": "service-a"},
            }[case_id]
            result = mapper.map_attributes(fields)
            self.assertIn(result.status, {"MAPPED", "PARTIAL"})
            self.assertFalse(any(result.effects.values()))
            self.assertNotIn("entity_id", result.as_dict())
            self.assertNotIn("permission", result.as_dict())
            self.assertNotIn("evidence", result.as_dict())
        elif case_id.startswith("SEM-CF-RESULT-"):
            claim = mapper.valid_result_claim()
            if case_id == "SEM-CF-RESULT-001":
                claim["synthetic"] = True
                expected = "SEM_SYNTHETIC_RESULT_CANNOT_PASS"
            elif case_id == "SEM-CF-RESULT-002":
                claim["case_ids"] = claim["case_ids"][:-1]
                expected = "SEM_RESULT_CASE_SET_INCOMPLETE"
            elif case_id == "SEM-CF-RESULT-003":
                claim["mapping_catalog_digest"] = f"sha256:{'0' * 64}"
                expected = "SEM_RESULT_MAPPING_DIGEST_MISMATCH"
            else:
                changed = deepcopy(claim["effects"])
                changed["gate_state_changed"] = True
                claim["effects"] = changed
                claim["gate_state_change"] = True
                expected = "SEM_RESULT_SELF_AUTHORIZATION_REJECTED"
            decision = mapper.validate_result_claim(claim)
            self.assertEqual(decision.status, "REJECTED")
            self.assertIn(expected, decision.reason_codes)
            self.assertFalse(any(decision.effects.values()))
        else:  # pragma: no cover - catalog expansion must fail loudly
            self.fail(f"unimplemented semantic conformance case: {case_id}")

    def test_catalog_binding_is_exact_and_deployment_cases_are_not_executed(
        self,
    ) -> None:
        required = _required_case_ids()
        self.assertEqual(len(required), SEMANTIC_PR_G2_CASE_COUNT)
        self.assertEqual(required, SemanticMetadataMapper().pr_g2_case_ids)
        all_cases = {case["case_id"] for case in _catalog()["cases"]}
        blocked = all_cases - required
        self.assertEqual(len(all_cases), 46)
        self.assertEqual(len(blocked), 14)
        self.assertTrue(
            all(
                "DQ-020" in case["gate_refs"]
                or "PR-G3" in case["gate_refs"]
                or "PR-G5" in case["gate_refs"]
                for case in _catalog()["cases"]
                if case["case_id"] in blocked
            )
        )
        self.assertEqual(
            SemanticMetadataMapper().valid_result_claim()["mapping_catalog_digest"],
            SEMANTIC_MAPPING_CATALOG_DIGEST,
        )
        self.assertEqual(
            SemanticMetadataMapper().valid_result_claim()["conformance_catalog_digest"],
            SEMANTIC_CONFORMANCE_CATALOG_DIGEST,
        )
        self.assertEqual(
            SemanticMetadataMapper().valid_result_claim()["full_catalog_result"],
            "BLOCKED",
        )


def _install_case_tests() -> None:
    for case_id in sorted(_required_case_ids()):
        method_name = f"test_{case_id.lower().replace('-', '_')}"

        def test_method(
            self: SemanticConformanceTests, bound_case: str = case_id
        ) -> None:
            self.run_case(bound_case)

        test_method.__name__ = method_name
        test_method.__doc__ = f"Execute frozen case {case_id}."
        setattr(SemanticConformanceTests, method_name, test_method)


_install_case_tests()


if __name__ == "__main__":
    unittest.main()
