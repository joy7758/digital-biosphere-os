"""Offline OpenTelemetry semantic mapping with zero authority effect.

This module consumes an allowlisted mapping catalog adopted by DBA.  It emits
metadata projections containing field names and value digests only.  It never
stores raw telemetry and cannot create Identity, Entity, Capability,
Permission, Evidence, Verification, SAEE output, or a governance decision.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from .contracts import (
    CORE_SEMCONV_REFERENCE,
    GENAI_SEMCONV_COMMIT,
    OTEL_SPEC_REFERENCE,
    OTLP_REFERENCE,
    SEMANTIC_CONFORMANCE_CATALOG_DIGEST,
    SEMANTIC_CONFORMANCE_CATALOG_ID,
    SEMANTIC_MAPPING_CATALOG_DIGEST,
    SEMANTIC_MAPPING_CATALOG_ID,
    SEMANTIC_PR_G2_CASE_COUNT,
    SEMANTIC_CONVENTION_SCHEMA_URL,
)
from .references import (
    SEMANTIC_CONFORMANCE_FILENAME,
    SEMANTIC_MAPPING_FILENAME,
    ReferenceIntegrityError,
    read_pinned_json,
)


_MAX_ATTRIBUTE_COUNT = 64
_MAX_VALUE_BYTES = 16_384
_AUTHORITY_PREFIXES = ("tmai.", "dbos.", "saee.")
_AUTHORITY_FIELDS = frozenset(
    {
        "active",
        "authorization",
        "capability",
        "decision",
        "entity_id",
        "evidence",
        "fitness",
        "lifecycle_state",
        "permission",
        "recommendation",
        "truth",
        "verification",
    }
)
_SENSITIVE_BINDINGS = frozenset(
    {
        "decision_reference",
        "policy_digest",
        "field_allowlist",
        "retention_reference",
        "residency_reference",
        "access_policy_reference",
        "redaction_policy_reference",
    }
)
_ZERO_EFFECTS = MappingProxyType(
    {
        "identity_created": False,
        "entity_created": False,
        "execution_created": False,
        "capability_created": False,
        "permission_created": False,
        "evidence_created": False,
        "verification_created": False,
        "saee_output_created": False,
        "governance_decision_created": False,
        "gate_state_changed": False,
    }
)


class SemanticMappingError(RuntimeError):
    """Fail-closed semantic mapping error without untrusted value echo."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True, slots=True)
class SemanticSourceBinding:
    """Exact upstream versions required for a mapping execution."""

    otel_spec_reference: str = OTEL_SPEC_REFERENCE
    core_semconv_reference: str = CORE_SEMCONV_REFERENCE
    genai_semconv_commit: str = GENAI_SEMCONV_COMMIT
    otlp_reference: str = OTLP_REFERENCE
    resource_schema_url: str | None = SEMANTIC_CONVENTION_SCHEMA_URL
    instrumentation_scope_schema_url: str | None = SEMANTIC_CONVENTION_SCHEMA_URL


@dataclass(frozen=True, slots=True)
class SemanticProjection:
    """Digest-only projection of one allowlisted upstream attribute."""

    mapping_id: str
    upstream_field: str
    source: str
    stability: str
    capture_class: str
    target: str
    target_field: str
    authority_rule: str
    value_digest: str

    def as_dict(self) -> dict[str, str]:
        return {
            "mapping_id": self.mapping_id,
            "upstream_field": self.upstream_field,
            "source": self.source,
            "stability": self.stability,
            "capture_class": self.capture_class,
            "target": self.target,
            "target_field": self.target_field,
            "authority_rule": self.authority_rule,
            "value_digest": self.value_digest,
        }


@dataclass(frozen=True, slots=True)
class SemanticMappingResult:
    """Immutable mapping result; never a conformance or governance decision."""

    status: str
    projections: tuple[SemanticProjection, ...]
    reason_codes: tuple[str, ...]
    limitations: tuple[str, ...]
    unknown_field_digests: tuple[str, ...]
    mapping_catalog_digest: str = SEMANTIC_MAPPING_CATALOG_DIGEST
    conformance_catalog_digest: str = SEMANTIC_CONFORMANCE_CATALOG_DIGEST
    effects: Mapping[str, bool] = _ZERO_EFFECTS

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "projections": [item.as_dict() for item in self.projections],
            "reason_codes": list(self.reason_codes),
            "limitations": list(self.limitations),
            "unknown_field_digests": list(self.unknown_field_digests),
            "mapping_catalog_digest": self.mapping_catalog_digest,
            "conformance_catalog_digest": self.conformance_catalog_digest,
            "effects": dict(self.effects),
            "raw_values_present": False,
            "gate_effect": False,
        }


@dataclass(frozen=True, slots=True)
class ResultClaimDecision:
    """Validation result for a claimed semantic conformance result set."""

    status: str
    reason_codes: tuple[str, ...]
    effects: Mapping[str, bool] = _ZERO_EFFECTS


def _json_digest(value: object) -> str:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise SemanticMappingError("SEM_VALUE_UNSUPPORTED") from exc
    if len(encoded) > _MAX_VALUE_BYTES:
        raise SemanticMappingError("SEM_VALUE_SIZE_EXCEEDED")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _field_digest(field: str) -> str:
    return f"sha256:{hashlib.sha256(field.encode('utf-8')).hexdigest()}"


def _has_authority_name(field: str) -> bool:
    normalized = field.strip().lower()
    return normalized.startswith(_AUTHORITY_PREFIXES) or normalized in _AUTHORITY_FIELDS


class SemanticMetadataMapper:
    """Map exact OTel fields to non-authoritative digest-only projections."""

    def __init__(
        self,
        *,
        expected_mapping_digest: str = SEMANTIC_MAPPING_CATALOG_DIGEST,
        expected_conformance_digest: str = SEMANTIC_CONFORMANCE_CATALOG_DIGEST,
    ) -> None:
        try:
            mapping = read_pinned_json(
                SEMANTIC_MAPPING_FILENAME,
                expected_digest=expected_mapping_digest,
            )
            conformance = read_pinned_json(
                SEMANTIC_CONFORMANCE_FILENAME,
                expected_digest=expected_conformance_digest,
            )
        except ReferenceIntegrityError as exc:
            raise SemanticMappingError(exc.reason_code) from exc
        self._mapping_catalog = mapping
        self._conformance_catalog = conformance
        self._by_field = self._validate_catalogs(mapping, conformance)
        self._pr_g2_case_ids = frozenset(
            case["case_id"]
            for case in conformance["cases"]
            if "PR-G2" in case["gate_refs"]
        )
        self._blocked_case_ids = frozenset(
            case["case_id"]
            for case in conformance["cases"]
            if "PR-G2" not in case["gate_refs"]
        )

    @staticmethod
    def _validate_catalogs(
        mapping: Mapping[str, Any],
        conformance: Mapping[str, Any],
    ) -> dict[str, Mapping[str, Any]]:
        if mapping.get("catalog_id") != SEMANTIC_MAPPING_CATALOG_ID:
            raise SemanticMappingError("SEM_MAPPING_CATALOG_ID_MISMATCH")
        if conformance.get("catalog_id") != SEMANTIC_CONFORMANCE_CATALOG_ID:
            raise SemanticMappingError("SEM_CASE_CATALOG_ID_MISMATCH")
        mappings = mapping.get("mappings")
        if not isinstance(mappings, list) or len(mappings) != 47:
            raise SemanticMappingError("SEM_MAPPING_INVENTORY_INVALID")
        expected_ids = {f"OTEL-SM-{index:03d}" for index in range(1, 48)}
        observed_ids = {item.get("mapping_id") for item in mappings}
        if observed_ids != expected_ids:
            raise SemanticMappingError("SEM_MAPPING_INVENTORY_INVALID")
        fields = [item.get("upstream_field") for item in mappings]
        if len(set(fields)) != 47 or any(not isinstance(item, str) for item in fields):
            raise SemanticMappingError("SEM_MAPPING_FIELD_AMBIGUOUS")
        if any(
            item.get("canonical_effect") != "NONE"
            or not isinstance(item.get("authority_rule"), str)
            for item in mappings
        ):
            raise SemanticMappingError("SEM_AUTHORITY_EFFECT_INVALID")

        source_registry = mapping.get("stability_source_registry")
        if not isinstance(source_registry, list) or len(source_registry) != 9:
            raise SemanticMappingError("SEM_SOURCE_REGISTRY_INVALID")
        source_coverage: list[str] = []
        for source in source_registry:
            source_coverage.extend(source.get("applicable_mapping_ids", []))
        if len(source_coverage) != 47 or set(source_coverage) != expected_ids:
            raise SemanticMappingError("SEM_SOURCE_REGISTRY_INVALID")

        cases = conformance.get("cases")
        if not isinstance(cases, list) or len(cases) != 46:
            raise SemanticMappingError("SEM_CASE_INVENTORY_INVALID")
        case_ids = [case.get("case_id") for case in cases]
        if len(set(case_ids)) != 46:
            raise SemanticMappingError("SEM_CASE_INVENTORY_INVALID")
        pr_g2 = [case for case in cases if "PR-G2" in case.get("gate_refs", [])]
        if len(pr_g2) != SEMANTIC_PR_G2_CASE_COUNT:
            raise SemanticMappingError("SEM_PR_G2_CASE_INVENTORY_INVALID")
        effects = conformance.get("effects")
        if not isinstance(effects, Mapping) or any(effects.values()):
            raise SemanticMappingError("SEM_CASE_AUTHORITY_EFFECT_INVALID")
        return {
            item["upstream_field"]: MappingProxyType(dict(item)) for item in mappings
        }

    @property
    def mapping_count(self) -> int:
        return len(self._by_field)

    @property
    def pr_g2_case_ids(self) -> frozenset[str]:
        return self._pr_g2_case_ids

    @property
    def blocked_case_ids(self) -> frozenset[str]:
        return self._blocked_case_ids

    def map_attributes(
        self,
        attributes: Mapping[str, object],
        *,
        source_binding: SemanticSourceBinding | None = None,
        sensitive_governance: Mapping[str, object] | None = None,
        stability_overrides: Mapping[str, str] | None = None,
    ) -> SemanticMappingResult:
        """Map one in-memory attribute set without retaining raw values."""

        if (
            not isinstance(attributes, Mapping)
            or len(attributes) > _MAX_ATTRIBUTE_COUNT
        ):
            return self._result("REJECTED", (), {"SEM_ATTRIBUTE_SET_INVALID"}, (), ())
        binding = source_binding or SemanticSourceBinding()
        source_reasons = self._validate_source_binding(binding, attributes)
        if source_reasons:
            return self._result("REJECTED", (), source_reasons, (), ())

        projections: list[SemanticProjection] = []
        reasons: set[str] = set()
        limitations: set[str] = set()
        unknown_digests: list[str] = []
        if binding.instrumentation_scope_schema_url is None:
            limitations.add("SEM_SCOPE_SCHEMA_URL_UNKNOWN")
        elif binding.instrumentation_scope_schema_url != SEMANTIC_CONVENTION_SCHEMA_URL:
            reasons.add("SEM_SCOPE_SCHEMA_URL_UNSUPPORTED")
        if binding.resource_schema_url is None:
            limitations.add("SEM_RESOURCE_SCHEMA_URL_UNKNOWN")
        elif binding.resource_schema_url != SEMANTIC_CONVENTION_SCHEMA_URL:
            reasons.add("SEM_RESOURCE_SCHEMA_URL_UNSUPPORTED")

        overrides = stability_overrides or {}
        for field in sorted(attributes):
            if not isinstance(field, str):
                reasons.add("SEM_FIELD_NAME_INVALID")
                continue
            if _has_authority_name(field):
                reasons.add("SEM_AUTHORITY_FIELD_REJECTED")
                unknown_digests.append(_field_digest(field))
                continue
            entry = self._by_field.get(field)
            if entry is None:
                reasons.add("SEM_UNKNOWN_FIELD_REJECTED")
                unknown_digests.append(_field_digest(field))
                continue
            if (
                overrides.get(entry["mapping_id"], entry["stability"])
                != entry["stability"]
            ):
                reasons.add("SEM_STABILITY_DRIFT")
                continue
            if entry["stability"] == "DEPRECATED":
                reasons.add("SEM_DEPRECATED_FIELD_REJECTED")
                limitations.add(f"SEM_MIGRATION_REQUIRED_{entry['mapping_id']}")
                continue
            if entry["source"] == "GENAI_SEMCONV":
                limitations.add("SEM_GENAI_DEVELOPMENT_LANE")
                limitations.add("GENAI_SCHEMA_URL_UNAVAILABLE")
            if entry["capture_class"] == "OPT_IN_SENSITIVE_DISABLED_BY_DEFAULT":
                if not self._sensitive_allowed(field, sensitive_governance):
                    reasons.add("SEM_SENSITIVE_CONTENT_DISABLED")
                    continue
                limitations.add("SEM_SENSITIVE_VALUE_DIGEST_ONLY")
            try:
                value_digest = _json_digest(attributes[field])
            except SemanticMappingError as exc:
                reasons.add(exc.reason_code)
                continue
            projections.append(
                SemanticProjection(
                    mapping_id=entry["mapping_id"],
                    upstream_field=field,
                    source=entry["source"],
                    stability=entry["stability"],
                    capture_class=entry["capture_class"],
                    target=entry["target"],
                    target_field=entry["target_field"],
                    authority_rule=entry["authority_rule"],
                    value_digest=value_digest,
                )
            )
        if reasons:
            status = "REJECTED"
            projections = []
        elif limitations:
            status = "PARTIAL"
        else:
            status = "MAPPED"
        return self._result(
            status,
            projections,
            reasons,
            limitations,
            unknown_digests,
        )

    @staticmethod
    def _validate_source_binding(
        binding: SemanticSourceBinding,
        attributes: Mapping[str, object],
    ) -> set[str]:
        reasons: set[str] = set()
        if binding.otel_spec_reference != OTEL_SPEC_REFERENCE:
            reasons.add("SEM_OTEL_SPEC_REFERENCE_MISMATCH")
        if binding.core_semconv_reference != CORE_SEMCONV_REFERENCE:
            reasons.add("SEM_CORE_SEMCONV_REFERENCE_MISMATCH")
        if binding.otlp_reference != OTLP_REFERENCE:
            reasons.add("SEM_OTLP_REFERENCE_MISMATCH")
        if any(str(field).startswith("gen_ai.") for field in attributes) and (
            binding.genai_semconv_commit != GENAI_SEMCONV_COMMIT
        ):
            reasons.add("SEM_GENAI_COMMIT_MISMATCH")
        return reasons

    @staticmethod
    def _sensitive_allowed(
        field: str,
        governance: Mapping[str, object] | None,
    ) -> bool:
        if (
            not isinstance(governance, Mapping)
            or set(governance) != _SENSITIVE_BINDINGS
        ):
            return False
        if any(
            value is None
            or (isinstance(value, str) and value in {"", "UNKNOWN", "NOT_ASSESSED"})
            for value in governance.values()
        ):
            return False
        allowlist = governance.get("field_allowlist")
        return isinstance(allowlist, (list, tuple, frozenset)) and field in allowlist

    @staticmethod
    def _result(
        status: str,
        projections: list[SemanticProjection] | tuple[SemanticProjection, ...],
        reasons: set[str],
        limitations: set[str] | tuple[str, ...],
        unknown_digests: list[str] | tuple[str, ...],
    ) -> SemanticMappingResult:
        return SemanticMappingResult(
            status=status,
            projections=tuple(sorted(projections, key=lambda item: item.mapping_id)),
            reason_codes=tuple(sorted(reasons)),
            limitations=tuple(sorted(limitations)),
            unknown_field_digests=tuple(sorted(unknown_digests)),
        )

    def validate_result_claim(self, claim: object) -> ResultClaimDecision:
        """Reject incomplete or self-authorizing semantic result claims."""

        reasons: set[str] = set()
        if not isinstance(claim, Mapping):
            reasons.add("SEM_RESULT_SHAPE_INVALID")
        else:
            if claim.get("synthetic") is not False:
                reasons.add("SEM_SYNTHETIC_RESULT_CANNOT_PASS")
            if claim.get("mapping_catalog_digest") != SEMANTIC_MAPPING_CATALOG_DIGEST:
                reasons.add("SEM_RESULT_MAPPING_DIGEST_MISMATCH")
            if (
                claim.get("conformance_catalog_digest")
                != SEMANTIC_CONFORMANCE_CATALOG_DIGEST
            ):
                reasons.add("SEM_RESULT_CASE_DIGEST_MISMATCH")
            case_ids = claim.get("case_ids")
            if not isinstance(case_ids, list) or set(case_ids) != self._pr_g2_case_ids:
                reasons.add("SEM_RESULT_CASE_SET_INCOMPLETE")
            blocked_case_ids = claim.get("blocked_case_ids")
            if (
                not isinstance(blocked_case_ids, list)
                or set(blocked_case_ids) != self._blocked_case_ids
            ):
                reasons.add("SEM_RESULT_BLOCKED_CASE_SET_INVALID")
            if claim.get("full_catalog_result") != "BLOCKED":
                reasons.add("SEM_RESULT_FULL_CATALOG_PASS_REJECTED")
            effects = claim.get("effects")
            if not isinstance(effects, Mapping) or set(effects) != set(_ZERO_EFFECTS):
                reasons.add("SEM_RESULT_EFFECTS_INVALID")
            elif any(effects.values()):
                reasons.add("SEM_RESULT_SELF_AUTHORIZATION_REJECTED")
            if claim.get("gate_state_change") is not False:
                reasons.add("SEM_RESULT_GATE_EFFECT_REJECTED")
            if not claim.get("reviewed_by_ref"):
                reasons.add("SEM_RESULT_REVIEW_BINDING_MISSING")
        return ResultClaimDecision(
            status="VALIDATED_INPUT" if not reasons else "REJECTED",
            reason_codes=tuple(sorted(reasons)),
        )

    def valid_result_claim(self) -> dict[str, Any]:
        """Create a no-effect fixture shape for external result producers."""

        return {
            "synthetic": False,
            "mapping_catalog_digest": SEMANTIC_MAPPING_CATALOG_DIGEST,
            "conformance_catalog_digest": SEMANTIC_CONFORMANCE_CATALOG_DIGEST,
            "case_ids": sorted(self._pr_g2_case_ids),
            "blocked_case_ids": sorted(self._blocked_case_ids),
            "full_catalog_result": "BLOCKED",
            "effects": dict(_ZERO_EFFECTS),
            "gate_state_change": False,
            "reviewed_by_ref": "independent-review-required",
        }


__all__ = [
    "ResultClaimDecision",
    "SemanticMappingError",
    "SemanticMappingResult",
    "SemanticMetadataMapper",
    "SemanticProjection",
    "SemanticSourceBinding",
]
