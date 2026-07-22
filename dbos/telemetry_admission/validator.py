"""Deterministic closed-schema validator for telemetry observation metadata.

Validation is offline. Schema URLs are compared with an exact local allowlist
and are never fetched. The validator neither persists input nor grants any
governance effect.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from .contracts import (
    CLOCK_SOURCES,
    CONTENT_CAPTURE_STATES,
    CONTEXT_FIELDS,
    DELIVERY_STATES,
    DIGEST_PATTERN,
    ENVELOPE_FIELDS,
    ENVELOPE_OBJECT_KIND,
    ENVELOPE_SCHEMA_VERSION,
    GENAI_SEMCONV_PIN,
    INSTRUMENTATION_SCOPE_FIELDS,
    MAX_ATTRIBUTE_COUNT,
    MAX_ENVELOPE_BYTES,
    MAX_LIMITATIONS,
    MAX_LIST_ITEMS,
    MAX_NESTING_DEPTH,
    MAX_SOURCE_SIZE_BYTES,
    OPAQUE_REFERENCE_PATTERN,
    OTEL_SPEC_VERSION,
    OTLP_VERSION,
    PARENT_STATES,
    PROFILE_ID,
    PROHIBITED_KEYS,
    REDACTION_FIELDS,
    REDACTION_RESULTS,
    RESOURCE_FIELDS,
    SAMPLING_DECISIONS,
    SAMPLING_FIELDS,
    SEMANTIC_CONVENTION_SCHEMA_URL,
    SEMANTIC_CONVENTION_VERSION,
    SIGNAL_TYPES,
    SPAN_ID_PATTERN,
    TRACE_FLAGS_PATTERN,
    TRACE_ID_PATTERN,
    order_reason_codes,
)
from .models import ValidationDecision


_HARD_REJECTION_CODES = frozenset(
    {
        "TA_SCHEMA_UNSUPPORTED",
        "TA_PROFILE_UNSUPPORTED",
        "TA_SIGNAL_UNSUPPORTED",
        "TA_SHAPE_INVALID",
        "TA_SIZE_LIMIT_EXCEEDED",
        "TA_RESOURCE_MISSING",
        "TA_INSTRUMENTATION_SCOPE_MISSING",
        "TA_CONTEXT_INVALID",
        "TA_GENAI_SEMCONV_UNPINNED",
        "TA_CONTENT_CAPTURE_PROHIBITED",
        "TA_SENSITIVE_KEY_DETECTED",
        "TA_DIGEST_INVALID",
        "TA_PROVENANCE_INCOMPLETE",
    }
)
_UNKNOWN_CODES = frozenset(
    {"TA_SCHEMA_URL_UNKNOWN", "TA_SEMCONV_UNSUPPORTED", "TA_INTERNAL_UNKNOWN"}
)
_SENSITIVE_VALUE_MARKERS = (
    "api-key",
    "apikey",
    "bearer",
    "credential",
    "password",
    "secret",
    "session-cookie",
    "token",
)
_ALLOWED_DECISION_PATH = "$.sampling_state.decision"


def _is_mapping(value: object) -> bool:
    return isinstance(value, Mapping)


def _has_exact_fields(value: object, fields: Sequence[str]) -> bool:
    return _is_mapping(value) and set(value) == set(fields)


def _is_non_negative_int(value: object, maximum: int | None = None) -> bool:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        return False
    return maximum is None or value <= maximum


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (
        parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
    )


def _is_timestamp(value: object) -> bool:
    return _parse_timestamp(value) is not None


def _is_reference(value: object, *, allow_unknown: bool = False) -> bool:
    if allow_unknown and value == "UNKNOWN":
        return True
    return (
        isinstance(value, str) and OPAQUE_REFERENCE_PATTERN.fullmatch(value) is not None
    )


def _is_digest(value: object) -> bool:
    return isinstance(value, str) and DIGEST_PATTERN.fullmatch(value) is not None


def _json_size(value: object) -> int | None:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError):
        return None
    return len(encoded)


def _walk_shape(
    value: object,
    *,
    path: str = "$",
    depth: int = 0,
) -> tuple[bool, bool]:
    """Return ``(within_limits, sensitive_key_or_value_seen)``."""

    if depth > MAX_NESTING_DEPTH:
        return False, False
    within_limits = True
    sensitive = False
    if isinstance(value, Mapping):
        if len(value) > MAX_LIST_ITEMS:
            within_limits = False
        for key, child in value.items():
            if not isinstance(key, str):
                within_limits = False
                continue
            child_path = f"{path}.{key}"
            normalized_key = key.strip().lower()
            if (
                normalized_key in PROHIBITED_KEYS
                and child_path != _ALLOWED_DECISION_PATH
            ):
                sensitive = True
            child_limits, child_sensitive = _walk_shape(
                child,
                path=child_path,
                depth=depth + 1,
            )
            within_limits = within_limits and child_limits
            sensitive = sensitive or child_sensitive
    elif isinstance(value, (list, tuple)):
        if len(value) > MAX_LIST_ITEMS:
            within_limits = False
        for index, child in enumerate(value):
            child_limits, child_sensitive = _walk_shape(
                child,
                path=f"{path}[{index}]",
                depth=depth + 1,
            )
            within_limits = within_limits and child_limits
            sensitive = sensitive or child_sensitive
    elif isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in _SENSITIVE_VALUE_MARKERS):
            sensitive = True
    return within_limits, sensitive


def _context_valid(context: object, signal_type: object) -> bool:
    if not _has_exact_fields(context, CONTEXT_FIELDS):
        return False
    if not isinstance(context, Mapping):
        return False
    trace_id = context.get("trace_id")
    span_id = context.get("span_id")
    flags = context.get("trace_flags")
    parent_state = context.get("parent_state")
    if parent_state not in PARENT_STATES:
        return False
    all_not_applicable = (
        trace_id == "NOT_APPLICABLE"
        and span_id == "NOT_APPLICABLE"
        and flags == "NOT_APPLICABLE"
        and parent_state == "NOT_APPLICABLE"
    )
    if all_not_applicable:
        return signal_type in {"METRIC", "LOG"}
    if not (
        isinstance(trace_id, str)
        and TRACE_ID_PATTERN.fullmatch(trace_id)
        and trace_id != "0" * 32
        and isinstance(span_id, str)
        and SPAN_ID_PATTERN.fullmatch(span_id)
        and span_id != "0" * 16
        and isinstance(flags, str)
        and TRACE_FLAGS_PATTERN.fullmatch(flags)
        and parent_state in {"ROOT", "CHILD", "UNKNOWN"}
    ):
        return False
    return True


def _closed_nested_shape_errors(envelope: Mapping[str, Any]) -> set[str]:
    errors: set[str] = set()
    resource = envelope.get("resource")
    scope = envelope.get("instrumentation_scope")
    if resource is None:
        errors.add("TA_RESOURCE_MISSING")
    elif not _has_exact_fields(resource, RESOURCE_FIELDS):
        errors.add("TA_SHAPE_INVALID")
    if scope is None:
        errors.add("TA_INSTRUMENTATION_SCOPE_MISSING")
    elif not _has_exact_fields(scope, INSTRUMENTATION_SCOPE_FIELDS):
        errors.add("TA_SHAPE_INVALID")
    if not _has_exact_fields(envelope.get("context"), CONTEXT_FIELDS):
        errors.add("TA_SHAPE_INVALID")
    if not _has_exact_fields(envelope.get("sampling_state"), SAMPLING_FIELDS):
        errors.add("TA_SHAPE_INVALID")
    if not _has_exact_fields(envelope.get("redaction_state"), REDACTION_FIELDS):
        errors.add("TA_SHAPE_INVALID")
    return errors


class TelemetryEnvelopeValidator:
    """Validate an untrusted mapping into a safe metadata-only projection."""

    def validate(self, value: object) -> ValidationDecision:
        reasons: set[str] = set()
        limitations: set[str] = set()
        safe_observation_reference: str | None = None
        safe_source_digest: str | None = None

        encoded_size = _json_size(value)
        if encoded_size is None:
            reasons.add("TA_SHAPE_INVALID")
        elif encoded_size > MAX_ENVELOPE_BYTES:
            reasons.add("TA_SIZE_LIMIT_EXCEEDED")

        within_limits, sensitive = _walk_shape(value)
        if not within_limits:
            reasons.add("TA_SIZE_LIMIT_EXCEEDED")
        if sensitive:
            reasons.add("TA_SENSITIVE_KEY_DETECTED")

        if not isinstance(value, Mapping):
            reasons.add("TA_SHAPE_INVALID")
            return self._decision(reasons, limitations, None, None, None)

        if set(value) != set(ENVELOPE_FIELDS):
            reasons.add("TA_SHAPE_INVALID")
        reasons.update(_closed_nested_shape_errors(value))

        observation_id = value.get("observation_id")
        if _is_reference(observation_id):
            safe_observation_reference = str(observation_id)
        else:
            reasons.add("TA_PROVENANCE_INCOMPLETE")

        source_digest = value.get("source_digest")
        if _is_digest(source_digest):
            safe_source_digest = str(source_digest)
        else:
            reasons.add("TA_DIGEST_INVALID")

        if value.get("object_kind") != ENVELOPE_OBJECT_KIND:
            reasons.add("TA_SCHEMA_UNSUPPORTED")
        if value.get("schema_version") != ENVELOPE_SCHEMA_VERSION:
            reasons.add("TA_SCHEMA_UNSUPPORTED")
        if value.get("profile_id") != PROFILE_ID:
            reasons.add("TA_PROFILE_UNSUPPORTED")
        if value.get("otel_spec_version") != OTEL_SPEC_VERSION:
            reasons.add("TA_SCHEMA_UNSUPPORTED")
        if value.get("otlp_version") not in {OTLP_VERSION, "NOT_OTLP"}:
            reasons.add("TA_SCHEMA_UNSUPPORTED")

        semconv_version = value.get("semantic_convention_version")
        schema_url = value.get("semantic_convention_schema_url")
        if semconv_version != SEMANTIC_CONVENTION_VERSION:
            reasons.add("TA_SEMCONV_UNSUPPORTED")
        if schema_url != SEMANTIC_CONVENTION_SCHEMA_URL:
            reasons.add("TA_SCHEMA_URL_UNKNOWN")
        if value.get("genai_semconv_ref") not in {"NOT_USED", GENAI_SEMCONV_PIN}:
            reasons.add("TA_GENAI_SEMCONV_UNPINNED")

        signal_type = value.get("signal_type")
        if signal_type not in SIGNAL_TYPES:
            reasons.add("TA_SIGNAL_UNSUPPORTED")
        if not _is_reference(value.get("producer_reference")):
            reasons.add("TA_PROVENANCE_INCOMPLETE")
        if not _is_reference(value.get("transport_source_reference")):
            reasons.add("TA_PROVENANCE_INCOMPLETE")
        if not _is_reference(value.get("signal_reference")):
            reasons.add("TA_PROVENANCE_INCOMPLETE")
        if not _is_timestamp(value.get("observed_at")) or not _is_timestamp(
            value.get("received_at")
        ):
            reasons.add("TA_SHAPE_INVALID")
        else:
            observed_at = _parse_timestamp(value.get("observed_at"))
            received_at = _parse_timestamp(value.get("received_at"))
            if (
                observed_at is not None
                and received_at is not None
                and observed_at > received_at
            ):
                reasons.add("TA_CLOCK_UNCERTAIN")
                limitations.add("TA_CLOCK_UNCERTAIN")
        if value.get("clock_source") not in CLOCK_SOURCES:
            reasons.add("TA_SHAPE_INVALID")
        elif value.get("clock_source") == "UNKNOWN":
            reasons.add("TA_CLOCK_UNCERTAIN")
            limitations.add("TA_CLOCK_UNCERTAIN")

        if not _context_valid(value.get("context"), signal_type):
            reasons.add("TA_CONTEXT_INVALID")
        elif isinstance(value.get("context"), Mapping):
            trace_id = value["context"].get("trace_id")
            if (
                observation_id == trace_id
                or value.get("idempotency_reference") == trace_id
            ):
                reasons.add("TA_CONTEXT_INVALID")

        resource = value.get("resource")
        if isinstance(resource, Mapping):
            if not _is_reference(resource.get("reference")):
                reasons.add("TA_PROVENANCE_INCOMPLETE")
            if resource.get("schema_url") != SEMANTIC_CONVENTION_SCHEMA_URL:
                reasons.add("TA_SCHEMA_URL_UNKNOWN")
            if not _is_digest(resource.get("attribute_set_digest")):
                reasons.add("TA_DIGEST_INVALID")
            if not _is_non_negative_int(
                resource.get("attribute_count"), MAX_ATTRIBUTE_COUNT
            ):
                reasons.add("TA_SIZE_LIMIT_EXCEEDED")

        scope = value.get("instrumentation_scope")
        if isinstance(scope, Mapping):
            if not _is_reference(scope.get("name")) or not _is_reference(
                scope.get("version"), allow_unknown=True
            ):
                reasons.add("TA_INSTRUMENTATION_SCOPE_MISSING")
            if scope.get("schema_url") != SEMANTIC_CONVENTION_SCHEMA_URL:
                reasons.add("TA_SCHEMA_URL_UNKNOWN")
            if not _is_digest(scope.get("attribute_set_digest")):
                reasons.add("TA_DIGEST_INVALID")

        sampling = value.get("sampling_state")
        if isinstance(sampling, Mapping):
            if sampling.get("decision") not in SAMPLING_DECISIONS:
                reasons.add("TA_SHAPE_INVALID")
            if not _is_reference(sampling.get("rule_reference"), allow_unknown=True):
                reasons.add("TA_SHAPE_INVALID")
            if not isinstance(sampling.get("known_loss"), bool):
                reasons.add("TA_SHAPE_INVALID")
            elif sampling.get("known_loss") or sampling.get("decision") == "DROP":
                reasons.add("TA_SAMPLING_LIMITATION")
                limitations.add("TA_SAMPLING_LIMITATION")

        redaction = value.get("redaction_state")
        if isinstance(redaction, Mapping):
            if not _is_reference(redaction.get("policy_reference"), allow_unknown=True):
                reasons.add("TA_SHAPE_INVALID")
            if redaction.get("result") not in REDACTION_RESULTS:
                reasons.add("TA_SHAPE_INVALID")
            for count_field in ("removed_count", "hashed_count"):
                if not _is_non_negative_int(
                    redaction.get(count_field), MAX_ATTRIBUTE_COUNT
                ):
                    reasons.add("TA_SIZE_LIMIT_EXCEEDED")

        if value.get("content_capture_state") not in CONTENT_CAPTURE_STATES:
            reasons.add("TA_CONTENT_CAPTURE_PROHIBITED")
        delivery_state = value.get("delivery_state")
        if delivery_state not in DELIVERY_STATES:
            reasons.add("TA_SHAPE_INVALID")
        elif delivery_state in {"PARTIAL", "RETRYING", "DROPPED"}:
            reasons.add("TA_PARTIAL_INPUT")
            limitations.add("TA_PARTIAL_INPUT")
        elif delivery_state == "UNKNOWN":
            reasons.add("TA_INTERNAL_UNKNOWN")
            limitations.add("TA_INTERNAL_UNKNOWN")

        if not _is_non_negative_int(
            value.get("source_size_bytes"), MAX_SOURCE_SIZE_BYTES
        ):
            reasons.add("TA_SIZE_LIMIT_EXCEEDED")
        if not _is_reference(value.get("idempotency_reference"), allow_unknown=True):
            reasons.add("TA_SHAPE_INVALID")

        supplied_limitations = value.get("limitations")
        if not isinstance(supplied_limitations, list):
            reasons.add("TA_SHAPE_INVALID")
        elif (
            len(supplied_limitations) > MAX_LIMITATIONS
            or len(set(map(str, supplied_limitations))) != len(supplied_limitations)
            or any(not _is_reference(item) for item in supplied_limitations)
        ):
            reasons.add("TA_SHAPE_INVALID")
        else:
            limitations.update(str(item) for item in supplied_limitations)

        normalized: dict[str, Any] | None = None
        ordered_reasons = order_reason_codes(reasons)
        if not any(code in _HARD_REJECTION_CODES for code in ordered_reasons):
            # Exact field allowlist: never persist the caller mapping, extras,
            # custom objects, or ``__dict__`` wholesale.
            normalized = {
                field: copy.deepcopy(value[field]) for field in ENVELOPE_FIELDS
            }
        return self._decision(
            set(ordered_reasons),
            limitations,
            normalized,
            safe_observation_reference,
            safe_source_digest,
        )

    @staticmethod
    def _decision(
        reasons: set[str],
        limitations: set[str],
        normalized: Mapping[str, Any] | None,
        safe_observation_reference: str | None,
        safe_source_digest: str | None,
    ) -> ValidationDecision:
        ordered = order_reason_codes(reasons)
        if any(code in _HARD_REJECTION_CODES for code in ordered):
            state = "REJECTED"
            normalized = None
        elif any(code in _UNKNOWN_CODES for code in ordered):
            state = "UNKNOWN"
        elif any(
            code in {"TA_PARTIAL_INPUT", "TA_SAMPLING_LIMITATION", "TA_CLOCK_UNCERTAIN"}
            for code in ordered
        ):
            state = "PARTIAL"
        else:
            state = "ACCEPTED_AS_MATERIAL"
        return ValidationDecision(
            state=state,
            reason_codes=ordered,
            limitations=tuple(sorted(limitations)),
            normalized_envelope=normalized,
            safe_observation_reference=safe_observation_reference,
            safe_source_digest=safe_source_digest,
        )


__all__ = ["TelemetryEnvelopeValidator"]
