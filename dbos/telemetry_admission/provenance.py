"""Offline OpenTelemetry Schema, Resource, and Entity provenance controls.

The implementation is deliberately metadata-only and network-free.  It binds
the exact OTel 1.43 schema artifact, records deterministic transformation and
Resource merge lineage, and quarantines Development OTel Entity material.
Nothing in this module creates a DBOS Identity, Entity, Evidence,
Verification, Capability, Permission, lifecycle change, or gate decision.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Sequence
from urllib.parse import unquote

from .contracts import (
    CORE_SEMCONV_REFERENCE,
    OTEL_SCHEMA_ARTIFACT_DIGEST,
    OTEL_SCHEMA_FILE_FORMAT,
    OTEL_SPEC_REFERENCE,
    OPAQUE_REFERENCE_PATTERN,
    SCHEMA_RESOURCE_CONFORMANCE_CATALOG_DIGEST,
    SCHEMA_RESOURCE_CONFORMANCE_CATALOG_ID,
    SCHEMA_RESOURCE_PR_G2_CASE_COUNT,
    SEMANTIC_CONVENTION_SCHEMA_URL,
)
from .references import (
    OTEL_SCHEMA_FILENAME,
    SCHEMA_RESOURCE_CONFORMANCE_FILENAME,
    ReferenceIntegrityError,
    read_pinned_json,
    read_pinned_yaml,
)


_SCHEMA_URL_PREFIX = "https://opentelemetry.io/schemas/"
_VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
_MAX_ATTRIBUTES = 256
_MAX_VALUE_BYTES = 16_384
_MAX_ENTITY_INPUT_BYTES = 65_536
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
_HEX_PAIR_PATTERN = re.compile(r"%[0-9A-Fa-f]{2}")
_ZERO_EFFECTS = MappingProxyType(
    {
        "identity_created": False,
        "entity_created": False,
        "entity_registered": False,
        "lifecycle_changed": False,
        "execution_created": False,
        "capability_created": False,
        "permission_created": False,
        "evidence_created": False,
        "verification_created": False,
        "federation_created": False,
        "gate_state_changed": False,
    }
)


class ProvenanceError(RuntimeError):
    """Fail-closed provenance error without untrusted value echo."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True, slots=True)
class SchemaArtifactInfo:
    schema_url: str
    digest: str
    file_format: str
    version_count: int
    runtime_network_fetch_enabled: bool = False


@dataclass(frozen=True, slots=True)
class SchemaPrecedenceResult:
    status: str
    resource_schema_url_original: str | None
    scope_schema_url_original: str | None
    effective_schema_url: str | None
    precedence_reason: str
    reason_codes: tuple[str, ...]
    effects: Mapping[str, bool] = _ZERO_EFFECTS


@dataclass(frozen=True, slots=True)
class TransformerBinding:
    transformer_id: str
    transformer_version: str
    artifact_digest: str
    environment_digest: str

    def valid(self) -> bool:
        return (
            bool(self.transformer_id)
            and bool(self.transformer_version)
            and _is_digest(self.artifact_digest)
            and _is_digest(self.environment_digest)
        )


@dataclass(frozen=True, slots=True)
class TransformationResult:
    status: str
    source_schema_url: str
    target_schema_url: str
    input_projection_digest: str
    output_projection_digest: str | None
    output_field_digests: Mapping[str, str]
    operations_applied: tuple[str, ...]
    unsupported_or_lossy_operations: tuple[str, ...]
    reason_codes: tuple[str, ...]
    transformer_reference_digest: str
    effects: Mapping[str, bool] = _ZERO_EFFECTS

    def __post_init__(self) -> None:
        if not isinstance(self.output_field_digests, MappingProxyType):
            object.__setattr__(
                self,
                "output_field_digests",
                MappingProxyType(dict(self.output_field_digests)),
            )

    @property
    def transformation_reference(self) -> str:
        """Return a deterministic reference distinct from either projection."""

        material = "|".join(
            (
                self.input_projection_digest,
                self.target_schema_url,
                self.transformer_reference_digest,
            )
        ).encode("utf-8")
        return f"ta:transform:{hashlib.sha256(material).hexdigest()}"


@dataclass(frozen=True, slots=True)
class DetectorBinding:
    detector_name: str
    detector_version: str
    detector_artifact_digest: str
    detector_config_digest: str
    detector_order: int
    source_class: str
    source_reference: str

    def valid(self) -> bool:
        return (
            bool(self.detector_name)
            and bool(self.detector_version)
            and _is_digest(self.detector_artifact_digest)
            and _is_digest(self.detector_config_digest)
            and isinstance(self.detector_order, int)
            and not isinstance(self.detector_order, bool)
            and self.detector_order >= 0
            and self.source_class
            in {
                "USER_RESOURCE",
                "ENVIRONMENT",
                "SDK_DEFAULT",
                "PLATFORM_DETECTOR",
                "COLLECTOR_TRANSFORM",
            }
            and bool(self.source_reference)
        )


@dataclass(frozen=True, slots=True)
class ResourceMergeResult:
    status: str
    schema_url: str | None
    attribute_value_digests: Mapping[str, str]
    attribute_source_classes: Mapping[str, str]
    reason_codes: tuple[str, ...]
    conflict_state: str
    effects: Mapping[str, bool] = _ZERO_EFFECTS

    def __post_init__(self) -> None:
        for field_name in ("attribute_value_digests", "attribute_source_classes"):
            value = getattr(self, field_name)
            if not isinstance(value, MappingProxyType):
                object.__setattr__(self, field_name, MappingProxyType(dict(value)))


@dataclass(frozen=True, slots=True)
class EnvironmentParseResult:
    status: str
    attributes: Mapping[str, str]
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.attributes, MappingProxyType):
            object.__setattr__(
                self, "attributes", MappingProxyType(dict(self.attributes))
            )


@dataclass(frozen=True, slots=True)
class DataGovernanceBinding:
    tenant_scope_reference: str
    purpose_reference: str
    retention_policy_reference: str
    access_policy_reference: str
    encryption_policy_reference: str
    classification_status: str
    redaction_status: str
    isolation_status: str
    retention_status: str

    def valid(self) -> bool:
        references = (
            self.tenant_scope_reference,
            self.purpose_reference,
            self.retention_policy_reference,
            self.access_policy_reference,
            self.encryption_policy_reference,
        )
        statuses = (
            self.classification_status,
            self.redaction_status,
            self.isolation_status,
            self.retention_status,
        )
        return all(references) and all(status == "PASS" for status in statuses)

    def digest(self) -> str:
        return _json_digest(
            {
                "tenant_scope_reference": self.tenant_scope_reference,
                "purpose_reference": self.purpose_reference,
                "retention_policy_reference": self.retention_policy_reference,
                "access_policy_reference": self.access_policy_reference,
                "encryption_policy_reference": self.encryption_policy_reference,
                "classification_status": self.classification_status,
                "redaction_status": self.redaction_status,
                "isolation_status": self.isolation_status,
                "retention_status": self.retention_status,
            }
        )


@dataclass(frozen=True, slots=True)
class QuarantineRecord:
    status: str
    quarantine_record_schema_version: str
    source_reference: str
    payload_digest: str
    schema_url: str | None
    source_artifact_digest: str
    stability: str
    accepted_segment_count: int
    skipped_segment_count: int
    duplicate_count: int
    diagnostic_codes: tuple[str, ...]
    data_governance_binding_digest: str | None
    trusted_projection_created: bool = False
    effects: Mapping[str, bool] = _ZERO_EFFECTS


@dataclass(frozen=True, slots=True)
class ProvenanceResultClaimDecision:
    status: str
    reason_codes: tuple[str, ...]
    effects: Mapping[str, bool] = _ZERO_EFFECTS


def _is_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST_PATTERN.fullmatch(value) is not None


def _json_bytes(value: object) -> bytes:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ProvenanceError("OSR_VALUE_UNSUPPORTED") from exc
    if len(encoded) > _MAX_VALUE_BYTES:
        raise ProvenanceError("OSR_VALUE_SIZE_EXCEEDED")
    return encoded


def _json_digest(value: object) -> str:
    return f"sha256:{hashlib.sha256(_json_bytes(value)).hexdigest()}"


def _has_authority_name(field: str) -> bool:
    normalized = field.strip().lower()
    return normalized.startswith(_AUTHORITY_PREFIXES) or normalized in _AUTHORITY_FIELDS


def _version_tuple(value: str) -> tuple[int, int, int] | None:
    match = _VERSION_PATTERN.fullmatch(value)
    if match is None:
        return None
    return tuple(int(item) for item in match.groups())  # type: ignore[return-value]


def _schema_version(schema_url: str) -> str | None:
    if not schema_url.startswith(_SCHEMA_URL_PREFIX):
        return None
    version = schema_url[len(_SCHEMA_URL_PREFIX) :]
    return version if _version_tuple(version) is not None else None


def _strict_unquote(value: str) -> str:
    """Decode percent escapes only when every escape is complete and valid."""

    index = 0
    while index < len(value):
        if value[index] == "%":
            if _HEX_PAIR_PATTERN.fullmatch(value[index : index + 3]) is None:
                raise ValueError
            index += 3
        else:
            index += 1
    return unquote(value, errors="strict")


class SchemaResourceProvenanceValidator:
    """Validate exact schema bytes and perform bounded offline provenance work."""

    def __init__(
        self,
        *,
        expected_schema_digest: str = OTEL_SCHEMA_ARTIFACT_DIGEST,
        expected_catalog_digest: str = SCHEMA_RESOURCE_CONFORMANCE_CATALOG_DIGEST,
    ) -> None:
        try:
            schema = read_pinned_yaml(
                OTEL_SCHEMA_FILENAME,
                expected_digest=expected_schema_digest,
            )
            catalog = read_pinned_json(
                SCHEMA_RESOURCE_CONFORMANCE_FILENAME,
                expected_digest=expected_catalog_digest,
            )
        except ReferenceIntegrityError as exc:
            raise ProvenanceError(exc.reason_code) from exc
        self._schema = schema
        self._catalog = catalog
        self._validate_contracts()
        self._pr_g2_case_ids = frozenset(
            case["case_id"] for case in catalog["cases"] if "PR-G2" in case["gate_refs"]
        )
        self._blocked_case_ids = frozenset(
            case["case_id"]
            for case in catalog["cases"]
            if "PR-G2" not in case["gate_refs"]
        )

    def _validate_contracts(self) -> None:
        if self._schema.get("file_format") != OTEL_SCHEMA_FILE_FORMAT:
            raise ProvenanceError("OSR_SCHEMA_FILE_FORMAT_MISMATCH")
        if self._schema.get("schema_url") != SEMANTIC_CONVENTION_SCHEMA_URL:
            raise ProvenanceError("OSR_SCHEMA_URL_MISMATCH")
        versions = self._schema.get("versions")
        if not isinstance(versions, Mapping) or "1.43.0" not in versions:
            raise ProvenanceError("OSR_SCHEMA_VERSION_INVENTORY_INVALID")
        if self._catalog.get("catalog_id") != SCHEMA_RESOURCE_CONFORMANCE_CATALOG_ID:
            raise ProvenanceError("OSR_CASE_CATALOG_ID_MISMATCH")
        binding = self._catalog.get("contract_binding")
        if not isinstance(binding, Mapping):
            raise ProvenanceError("OSR_CONTRACT_BINDING_INVALID")
        if (
            binding.get("otel_specification") != OTEL_SPEC_REFERENCE
            or binding.get("core_semconv") != CORE_SEMCONV_REFERENCE
            or binding.get("core_schema_url") != SEMANTIC_CONVENTION_SCHEMA_URL
            or binding.get("core_schema_observed_digest") != OTEL_SCHEMA_ARTIFACT_DIGEST
        ):
            raise ProvenanceError("OSR_CONTRACT_BINDING_INVALID")
        source_registry = self._catalog.get("source_registry")
        if not isinstance(source_registry, list) or len(source_registry) != 6:
            raise ProvenanceError("OSR_SOURCE_REGISTRY_INVALID")
        source_ids = {source.get("source_id") for source in source_registry}
        if len(source_ids) != 6:
            raise ProvenanceError("OSR_SOURCE_REGISTRY_INVALID")
        cases = self._catalog.get("cases")
        if not isinstance(cases, list) or len(cases) != 45:
            raise ProvenanceError("OSR_CASE_INVENTORY_INVALID")
        if len({case.get("case_id") for case in cases}) != 45:
            raise ProvenanceError("OSR_CASE_INVENTORY_INVALID")
        if (
            len([case for case in cases if "PR-G2" in case.get("gate_refs", [])])
            != SCHEMA_RESOURCE_PR_G2_CASE_COUNT
        ):
            raise ProvenanceError("OSR_PR_G2_CASE_INVENTORY_INVALID")
        effects = self._catalog.get("effects")
        if not isinstance(effects, Mapping) or any(effects.values()):
            raise ProvenanceError("OSR_CASE_AUTHORITY_EFFECT_INVALID")

    @property
    def pr_g2_case_ids(self) -> frozenset[str]:
        return self._pr_g2_case_ids

    @property
    def blocked_case_ids(self) -> frozenset[str]:
        return self._blocked_case_ids

    def artifact_info(self) -> SchemaArtifactInfo:
        return SchemaArtifactInfo(
            schema_url=SEMANTIC_CONVENTION_SCHEMA_URL,
            digest=OTEL_SCHEMA_ARTIFACT_DIGEST,
            file_format=OTEL_SCHEMA_FILE_FORMAT,
            version_count=len(self._schema["versions"]),
        )

    @staticmethod
    def resolve_schema_precedence(
        resource_schema_url: str | None,
        scope_schema_url: str | None,
    ) -> SchemaPrecedenceResult:
        """Preserve both URLs and apply contained-scope precedence."""

        resource = resource_schema_url or None
        scope = scope_schema_url or None
        reasons: set[str] = set()
        if scope is not None:
            if _schema_version(scope) is None:
                reasons.add("OSR_SCOPE_SCHEMA_FAMILY_UNKNOWN")
            if resource is not None and _schema_version(resource) is None:
                reasons.add("OSR_RESOURCE_SCHEMA_FAMILY_UNKNOWN")
            if reasons:
                status = "BLOCKED"
                effective = None
                precedence = "CROSS_FAMILY_OR_UNKNOWN_BLOCKED"
            else:
                status = "RESOLVED"
                effective = scope
                precedence = "INSTRUMENTATION_SCOPE_CONTAINED_SIGNAL_PRECEDENCE"
        elif resource is not None:
            if _schema_version(resource) is None:
                status = "BLOCKED"
                effective = None
                precedence = "RESOURCE_SCHEMA_FAMILY_UNKNOWN"
                reasons.add("OSR_RESOURCE_SCHEMA_FAMILY_UNKNOWN")
            else:
                status = "RESOLVED"
                effective = resource
                precedence = "RESOURCE_SCHEMA_USED_SCOPE_EMPTY"
        else:
            status = "UNKNOWN"
            effective = None
            precedence = "NO_SCHEMA_URL_DECLARED"
            reasons.add("OSR_SCHEMA_URL_UNKNOWN")
        return SchemaPrecedenceResult(
            status=status,
            resource_schema_url_original=resource_schema_url,
            scope_schema_url_original=scope_schema_url,
            effective_schema_url=effective,
            precedence_reason=precedence,
            reason_codes=tuple(sorted(reasons)),
        )

    def transform_attributes(
        self,
        attributes: Mapping[str, object],
        *,
        source_schema_url: str,
        target_schema_url: str = SEMANTIC_CONVENTION_SCHEMA_URL,
        binding: TransformerBinding,
        signal_type: str = "TRACE",
        metric_name: str | None = None,
        requested_operation_types: Sequence[str] = ("rename_attributes",),
    ) -> TransformationResult:
        """Apply only pinned attribute rename operations with full lineage."""

        try:
            input_digest = _json_digest(attributes)
        except ProvenanceError as exc:
            return self._transformation_rejected(
                source_schema_url,
                target_schema_url,
                f"sha256:{'0' * 64}",
                binding,
                {exc.reason_code},
            )
        if (
            not isinstance(attributes, Mapping)
            or len(attributes) > _MAX_ATTRIBUTES
            or any(not isinstance(field, str) for field in attributes)
        ):
            return self._transformation_rejected(
                source_schema_url,
                target_schema_url,
                input_digest,
                binding,
                {"OSR_ATTRIBUTE_SET_INVALID"},
            )
        if not binding.valid():
            return self._transformation_rejected(
                source_schema_url,
                target_schema_url,
                input_digest,
                binding,
                {"OSR_TRANSFORMER_BINDING_INCOMPLETE"},
            )
        if set(requested_operation_types) != {"rename_attributes"}:
            return TransformationResult(
                status="BLOCKED",
                source_schema_url=source_schema_url,
                target_schema_url=target_schema_url,
                input_projection_digest=input_digest,
                output_projection_digest=None,
                output_field_digests={},
                operations_applied=(),
                unsupported_or_lossy_operations=tuple(
                    sorted(str(item) for item in requested_operation_types)
                ),
                reason_codes=("OSR_TRANSFORMATION_TYPE_UNSUPPORTED",),
                transformer_reference_digest=self._binding_digest(binding),
            )
        if signal_type not in {"TRACE", "METRIC", "LOG"}:
            return self._transformation_rejected(
                source_schema_url,
                target_schema_url,
                input_digest,
                binding,
                {"OSR_SIGNAL_TYPE_UNSUPPORTED"},
            )
        if any(_has_authority_name(field) for field in attributes):
            return self._transformation_rejected(
                source_schema_url,
                target_schema_url,
                input_digest,
                binding,
                {"OSR_AUTHORITY_FIELD_REJECTED"},
            )
        source_version = _schema_version(source_schema_url)
        target_version = _schema_version(target_schema_url)
        versions = self._schema["versions"]
        if (
            source_version is None
            or target_version is None
            or source_version not in versions
            or target_version not in versions
        ):
            return self._transformation_rejected(
                source_schema_url,
                target_schema_url,
                input_digest,
                binding,
                {"OSR_SCHEMA_VERSION_UNSUPPORTED"},
            )
        source_tuple = _version_tuple(source_version)
        target_tuple = _version_tuple(target_version)
        if source_tuple is None or target_tuple is None or source_tuple > target_tuple:
            return self._transformation_rejected(
                source_schema_url,
                target_schema_url,
                input_digest,
                binding,
                {"OSR_BREAKING_OR_REVERSE_TRANSFORM_BLOCKED"},
            )

        projected = dict(attributes)
        operations: list[str] = []
        unsupported: list[str] = []
        relevant_versions = sorted(
            (
                version
                for version in versions
                if _version_tuple(str(version)) is not None
                and source_tuple < _version_tuple(str(version)) <= target_tuple  # type: ignore[operator]
            ),
            key=lambda version: _version_tuple(str(version)),
        )
        signal_section = {"TRACE": "spans", "METRIC": "metrics", "LOG": "logs"}.get(
            signal_type
        )
        for version in relevant_versions:
            version_rules = versions[version] or {}
            if not isinstance(version_rules, Mapping):
                unsupported.append(f"INVALID_VERSION_RULE:{version}")
                continue
            sections = ["all"]
            if signal_section is not None:
                sections.append(signal_section)
            for section_name in sections:
                section = version_rules.get(section_name) or {}
                if not isinstance(section, Mapping):
                    unsupported.append(f"INVALID_SECTION:{version}:{section_name}")
                    continue
                changes = section.get("changes") or []
                if not isinstance(changes, list):
                    unsupported.append(f"INVALID_CHANGES:{version}:{section_name}")
                    continue
                for change in changes:
                    if not isinstance(change, Mapping):
                        unsupported.append(f"INVALID_CHANGE:{version}:{section_name}")
                        continue
                    for change_type, detail in change.items():
                        if change_type == "rename_attributes":
                            if not isinstance(detail, Mapping):
                                unsupported.append(
                                    f"INVALID_RENAME:{version}:{section_name}"
                                )
                                continue
                            attribute_map = detail.get("attribute_map")
                            if not isinstance(attribute_map, Mapping):
                                unsupported.append(
                                    f"INVALID_ATTRIBUTE_MAP:{version}:{section_name}"
                                )
                                continue
                            apply_to_metrics = detail.get("apply_to_metrics")
                            if apply_to_metrics is not None:
                                if signal_type != "METRIC":
                                    continue
                                if (
                                    not isinstance(apply_to_metrics, list)
                                    or metric_name is None
                                    or metric_name not in apply_to_metrics
                                ):
                                    if any(old in projected for old in attribute_map):
                                        unsupported.append(
                                            f"METRIC_SCOPE_REQUIRED:{version}:{section_name}"
                                        )
                                    continue
                            for old, new in attribute_map.items():
                                if not isinstance(old, str) or not isinstance(new, str):
                                    unsupported.append(
                                        f"INVALID_ATTRIBUTE_NAME:{version}:{section_name}"
                                    )
                                    continue
                                if old not in projected:
                                    continue
                                if new in projected or _has_authority_name(new):
                                    unsupported.append(
                                        f"RENAME_COLLISION_OR_AUTHORITY:{version}:{old}"
                                    )
                                    continue
                                projected[new] = projected.pop(old)
                                operations.append(f"{version}:rename:{old}->{new}")
                        elif change_type == "rename_metrics":
                            # This method transforms attributes only. Metric-name
                            # changes are retained as out-of-scope, not executed.
                            continue
                        else:
                            unsupported.append(
                                f"UNSUPPORTED:{version}:{section_name}:{change_type}"
                            )
        if unsupported:
            return TransformationResult(
                status="BLOCKED",
                source_schema_url=source_schema_url,
                target_schema_url=target_schema_url,
                input_projection_digest=input_digest,
                output_projection_digest=None,
                output_field_digests={},
                operations_applied=tuple(operations),
                unsupported_or_lossy_operations=tuple(sorted(unsupported)),
                reason_codes=("OSR_TRANSFORMATION_UNSUPPORTED",),
                transformer_reference_digest=self._binding_digest(binding),
            )
        if any(_has_authority_name(field) for field in projected):
            return self._transformation_rejected(
                source_schema_url,
                target_schema_url,
                input_digest,
                binding,
                {"OSR_AUTHORITY_FIELD_REJECTED"},
            )
        output_digest = _json_digest(projected)
        output_fields = {
            field: _json_digest(value) for field, value in projected.items()
        }
        return TransformationResult(
            status="UNCHANGED" if not operations else "TRANSFORMED",
            source_schema_url=source_schema_url,
            target_schema_url=target_schema_url,
            input_projection_digest=input_digest,
            output_projection_digest=output_digest,
            output_field_digests=output_fields,
            operations_applied=tuple(operations),
            unsupported_or_lossy_operations=(),
            reason_codes=(),
            transformer_reference_digest=self._binding_digest(binding),
        )

    @staticmethod
    def _binding_digest(binding: TransformerBinding) -> str:
        return _json_digest(
            {
                "transformer_id": binding.transformer_id,
                "transformer_version": binding.transformer_version,
                "artifact_digest": binding.artifact_digest,
                "environment_digest": binding.environment_digest,
            }
        )

    def _transformation_rejected(
        self,
        source_schema_url: str,
        target_schema_url: str,
        input_digest: str,
        binding: TransformerBinding,
        reasons: set[str],
    ) -> TransformationResult:
        return TransformationResult(
            status="BLOCKED",
            source_schema_url=source_schema_url,
            target_schema_url=target_schema_url,
            input_projection_digest=input_digest,
            output_projection_digest=None,
            output_field_digests={},
            operations_applied=(),
            unsupported_or_lossy_operations=(),
            reason_codes=tuple(sorted(reasons)),
            transformer_reference_digest=self._binding_digest(binding),
        )

    @staticmethod
    def parse_resource_environment(value: object) -> EnvironmentParseResult:
        """Parse OTEL_RESOURCE_ATTRIBUTES atomically; any error discards all."""

        if not isinstance(value, str) or not value:
            return EnvironmentParseResult(
                status="DISCARDED",
                attributes={},
                reason_codes=("OSR_ENV_RESOURCE_MALFORMED",),
            )
        result: dict[str, str] = {}
        try:
            for segment in value.split(","):
                if "=" not in segment:
                    raise ValueError
                raw_key, raw_value = segment.split("=", 1)
                key = _strict_unquote(raw_key).strip()
                decoded_value = _strict_unquote(raw_value).strip()
                if not key or key in result or _has_authority_name(key):
                    raise ValueError
                result[key] = decoded_value
        except (ValueError, UnicodeError):
            return EnvironmentParseResult(
                status="DISCARDED",
                attributes={},
                reason_codes=("OSR_ENV_RESOURCE_MALFORMED",),
            )
        return EnvironmentParseResult(
            status="PARSED", attributes=result, reason_codes=()
        )

    @staticmethod
    def merge_resources(
        old_attributes: Mapping[str, object],
        updating_attributes: Mapping[str, object],
        *,
        old_schema_url: str | None,
        updating_schema_url: str | None,
        old_detector: DetectorBinding,
        updating_detector: DetectorBinding,
    ) -> ResourceMergeResult:
        """Apply OTel Resource merge precedence while retaining source class."""

        reasons: set[str] = set()
        if not old_detector.valid() or not updating_detector.valid():
            reasons.add("OSR_DETECTOR_BINDING_INCOMPLETE")
        if old_detector.detector_name == updating_detector.detector_name:
            reasons.add("OSR_DETECTOR_NAME_DUPLICATE")
        if updating_detector.detector_order <= old_detector.detector_order:
            reasons.add("OSR_DETECTOR_ORDER_CONFLICT")
        if (
            not isinstance(old_attributes, Mapping)
            or not isinstance(updating_attributes, Mapping)
            or len(old_attributes) + len(updating_attributes) > _MAX_ATTRIBUTES
            or any(not isinstance(field, str) for field in old_attributes)
            or any(not isinstance(field, str) for field in updating_attributes)
        ):
            reasons.add("OSR_RESOURCE_SHAPE_INVALID")
        if any(
            _has_authority_name(field)
            for field in list(old_attributes) + list(updating_attributes)
            if isinstance(field, str)
        ):
            reasons.add("OSR_AUTHORITY_FIELD_REJECTED")

        old_url = old_schema_url or None
        updating_url = updating_schema_url or None
        if old_url and updating_url and old_url != updating_url:
            reasons.add("OSR_RESOURCE_SCHEMA_CONFLICT")
            schema_url = None
        else:
            schema_url = updating_url or old_url
        if reasons:
            return ResourceMergeResult(
                status="REJECTED",
                schema_url=schema_url,
                attribute_value_digests={},
                attribute_source_classes={},
                reason_codes=tuple(sorted(reasons)),
                conflict_state="CONFLICT",
            )
        merged = dict(old_attributes)
        source_classes = {field: old_detector.source_class for field in old_attributes}
        for field, value in updating_attributes.items():
            if (
                field in merged
                and old_detector.source_class == "USER_RESOURCE"
                and updating_detector.source_class == "ENVIRONMENT"
            ):
                continue
            merged[field] = value
            source_classes[field] = updating_detector.source_class
        try:
            digests = {field: _json_digest(value) for field, value in merged.items()}
        except ProvenanceError as exc:
            return ResourceMergeResult(
                status="REJECTED",
                schema_url=schema_url,
                attribute_value_digests={},
                attribute_source_classes={},
                reason_codes=(exc.reason_code,),
                conflict_state="VALUE_INVALID",
            )
        return ResourceMergeResult(
            status="MERGED",
            schema_url=schema_url,
            attribute_value_digests=digests,
            attribute_source_classes=source_classes,
            reason_codes=(),
            conflict_state="NONE",
        )

    @staticmethod
    def quarantine_otel_entities(
        value: object,
        *,
        source_reference: str,
        schema_url: str | None,
        governance: DataGovernanceBinding,
    ) -> QuarantineRecord:
        """Parse bounded OTEL_ENTITIES material into a digest-only quarantine record.

        The accepted bounded syntax is ``type:key=value[,key=value][;...]``.
        It is an observation parser, not a DBOS Entity adapter.
        """

        if isinstance(value, str):
            encoded = value.encode("utf-8", errors="strict")
        else:
            try:
                encoded = _json_bytes(value)
            except ProvenanceError:
                encoded = b""
        payload_digest = f"sha256:{hashlib.sha256(encoded).hexdigest()}"
        diagnostics: set[str] = set()
        accepted = 0
        skipped = 0
        duplicates = 0
        safe_source_reference = (
            source_reference
            if isinstance(source_reference, str)
            and OPAQUE_REFERENCE_PATTERN.fullmatch(source_reference)
            else "UNKNOWN"
        )
        if safe_source_reference == "UNKNOWN":
            diagnostics.add("OSR_ENTITY_SOURCE_REFERENCE_MISSING")
        if len(encoded) > _MAX_ENTITY_INPUT_BYTES or not encoded:
            diagnostics.add("OSR_ENTITY_INPUT_INVALID")
        if not governance.valid():
            diagnostics.add("OSR_DATA_GOVERNANCE_INCOMPLETE")
        if schema_url is not None and _schema_version(schema_url) is None:
            diagnostics.add("OSR_ENTITY_SCHEMA_FAMILY_UNKNOWN")

        if (
            isinstance(value, str)
            and encoded
            and len(encoded) <= _MAX_ENTITY_INPUT_BYTES
        ):
            seen: set[tuple[str, str]] = set()
            for segment in value.split(";"):
                try:
                    entity_type, raw_attributes = segment.split(":", 1)
                    if not entity_type.strip() or not raw_attributes:
                        raise ValueError
                    local_keys: set[str] = set()
                    for item in raw_attributes.split(","):
                        key, _raw_value = item.split("=", 1)
                        key = _strict_unquote(key).strip()
                        if not key or _has_authority_name(key):
                            raise ValueError
                        marker = (entity_type.strip(), key)
                        if key in local_keys or marker in seen:
                            duplicates += 1
                        local_keys.add(key)
                        seen.add(marker)
                    accepted += 1
                except (ValueError, UnicodeError):
                    skipped += 1
                    diagnostics.add("OSR_ENTITY_SEGMENT_SKIPPED")
        elif not isinstance(value, str):
            # Structured inputs are digest-retained but not interpreted by the
            # environment parser.
            diagnostics.add("OSR_ENTITY_STRUCTURED_INPUT_NOT_PARSED")
        if duplicates:
            diagnostics.add("OSR_ENTITY_DUPLICATE_LAST_OCCURRENCE_OBSERVED")
        if skipped:
            diagnostics.add("OSR_ENTITY_PARTIAL_PARSE")
        status = "QUARANTINED"
        if "OSR_DATA_GOVERNANCE_INCOMPLETE" in diagnostics:
            status = "BLOCKED"
        elif "OSR_ENTITY_INPUT_INVALID" in diagnostics:
            status = "REJECTED"
        return QuarantineRecord(
            status=status,
            quarantine_record_schema_version="0.1",
            source_reference=safe_source_reference,
            payload_digest=payload_digest,
            schema_url=schema_url,
            source_artifact_digest=(
                "sha256:5b3ec810c707b7816643a3efcac08d5c17f8fb0a36540f1bbd84715cbb1f5102"
            ),
            stability="DEVELOPMENT",
            accepted_segment_count=accepted,
            skipped_segment_count=skipped,
            duplicate_count=duplicates,
            diagnostic_codes=tuple(sorted(diagnostics)),
            data_governance_binding_digest=(
                governance.digest() if governance.valid() else None
            ),
        )

    @staticmethod
    def entity_merge_allowed(
        left_schema_url: str | None,
        right_schema_url: str | None,
    ) -> bool:
        """Return OTel observation-merge compatibility, never DBOS identity."""

        return bool(left_schema_url and left_schema_url == right_schema_url)

    def validate_result_claim(self, claim: object) -> ProvenanceResultClaimDecision:
        """Reject synthetic, incomplete, or self-authorizing result claims."""

        reasons: set[str] = set()
        if not isinstance(claim, Mapping):
            reasons.add("OSR_RESULT_SHAPE_INVALID")
        else:
            if claim.get("synthetic") is not False:
                reasons.add("OSR_SYNTHETIC_RESULT_CANNOT_PASS")
            if (
                claim.get("catalog_digest")
                != SCHEMA_RESOURCE_CONFORMANCE_CATALOG_DIGEST
            ):
                reasons.add("OSR_RESULT_CATALOG_DIGEST_MISMATCH")
            if claim.get("schema_artifact_digest") != OTEL_SCHEMA_ARTIFACT_DIGEST:
                reasons.add("OSR_RESULT_SCHEMA_DIGEST_MISMATCH")
            case_ids = claim.get("case_ids")
            if not isinstance(case_ids, list) or set(case_ids) != self._pr_g2_case_ids:
                reasons.add("OSR_RESULT_CASE_SET_INCOMPLETE")
            blocked_case_ids = claim.get("blocked_case_ids")
            if (
                not isinstance(blocked_case_ids, list)
                or set(blocked_case_ids) != self._blocked_case_ids
            ):
                reasons.add("OSR_RESULT_BLOCKED_CASE_SET_INVALID")
            if claim.get("full_catalog_result") != "BLOCKED":
                reasons.add("OSR_RESULT_FULL_CATALOG_PASS_REJECTED")
            effects = claim.get("effects")
            if not isinstance(effects, Mapping) or set(effects) != set(_ZERO_EFFECTS):
                reasons.add("OSR_RESULT_EFFECTS_INVALID")
            elif any(effects.values()):
                reasons.add("OSR_RESULT_SELF_AUTHORIZATION_REJECTED")
            if claim.get("gate_state_change") is not False:
                reasons.add("OSR_RESULT_GATE_EFFECT_REJECTED")
            if not claim.get("reviewed_by_ref"):
                reasons.add("OSR_RESULT_REVIEW_BINDING_MISSING")
            governance = claim.get("data_governance_binding")
            if not isinstance(governance, Mapping) or any(
                governance.get(key) != "PASS"
                for key in (
                    "classification_status",
                    "redaction_status",
                    "isolation_status",
                    "retention_status",
                )
            ):
                reasons.add("OSR_RESULT_DATA_GOVERNANCE_INCOMPLETE")
        return ProvenanceResultClaimDecision(
            status="VALIDATED_INPUT" if not reasons else "REJECTED",
            reason_codes=tuple(sorted(reasons)),
        )

    def valid_result_claim(self) -> dict[str, Any]:
        return {
            "synthetic": False,
            "catalog_digest": SCHEMA_RESOURCE_CONFORMANCE_CATALOG_DIGEST,
            "schema_artifact_digest": OTEL_SCHEMA_ARTIFACT_DIGEST,
            "case_ids": sorted(self._pr_g2_case_ids),
            "blocked_case_ids": sorted(self._blocked_case_ids),
            "full_catalog_result": "BLOCKED",
            "effects": dict(_ZERO_EFFECTS),
            "gate_state_change": False,
            "reviewed_by_ref": "independent-review-required",
            "data_governance_binding": {
                "classification_status": "PASS",
                "redaction_status": "PASS",
                "isolation_status": "PASS",
                "retention_status": "PASS",
            },
        }


__all__ = [
    "DataGovernanceBinding",
    "DetectorBinding",
    "EnvironmentParseResult",
    "ProvenanceError",
    "ProvenanceResultClaimDecision",
    "QuarantineRecord",
    "ResourceMergeResult",
    "SchemaArtifactInfo",
    "SchemaPrecedenceResult",
    "SchemaResourceProvenanceValidator",
    "TransformationResult",
    "TransformerBinding",
]
