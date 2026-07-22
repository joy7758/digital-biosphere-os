"""Frozen constants for DBOS Telemetry Admission Foundation v0.1.

The constants are protocol constraints, not runtime configuration. Unknown or
unsupported versions fail closed; this package performs no runtime schema
fetch and never treats a digest or declared producer reference as identity.
"""

from __future__ import annotations

import re


ENVELOPE_OBJECT_KIND = "TelemetryObservationEnvelope"
ENVELOPE_SCHEMA_VERSION = "0.1.0"
RECORD_SCHEMA_VERSION = "0.1.0"
PROFILE_ID = "TMAI-OTEL-OBSERVABILITY-PROFILE-0.1"
ADMISSION_POLICY_VERSION = "TMAI-DBOS-TELEMETRY-ADMISSION-POLICY-0.1.0"
VALIDATOR_VERSION = "TMAI-DBOS-TELEMETRY-ADMISSION-VALIDATOR-0.1.0"
FINGERPRINT_VERSION = "TMAI-TA-FINGERPRINT-SHA256-0.1.0"
STORE_SCHEMA_VERSION = "0.1.0"

OTEL_SPEC_REFERENCE = "v1.59.0@a824fb4eba795c5c65dd397b3d22e7c28e934de3"
CORE_SEMCONV_REFERENCE = "v1.43.0@89aae438b3b3b0a8dd33003c9d70592baf7dbd0d"
GENAI_SEMCONV_COMMIT = "2e994c6d59a93bb4fc1752c5378eedb9b8e14d6b"
OTLP_REFERENCE = "v1.11.0@790608c4d51e6ffc12210b541e8514cbed9e91a4"

SEMANTIC_MAPPING_CATALOG_ID = "TMAI-OTEL-SEMANTIC-MAPPING-0.1"
SEMANTIC_MAPPING_CATALOG_DIGEST = (
    "sha256:b81213505b1a7c3841ba298545b642b127af1a96ec906536be27caab351de706"
)
SEMANTIC_CONFORMANCE_CATALOG_ID = "TMAI-OTEL-SEMANTIC-CONFORMANCE-0.1"
SEMANTIC_CONFORMANCE_CATALOG_DIGEST = (
    "sha256:18b84edf6e8b618991c2dfd669d21794c3a3032188e198b7fd53899205b66c6e"
)
SEMANTIC_RESULT_SCHEMA_DIGEST = (
    "sha256:33fa128aa8063d8f4861f8abda23d9b48151f1a6529752848adaef3ea49f6f15"
)
SCHEMA_RESOURCE_CONFORMANCE_CATALOG_ID = "TMAI-OTEL-SCHEMA-RESOURCE-CONFORMANCE-0.1"
SCHEMA_RESOURCE_CONFORMANCE_CATALOG_DIGEST = (
    "sha256:805374a196f533d8b2c56492faeb566e05dd744edd0e519155442fcc50f8f452"
)
SCHEMA_RESOURCE_RESULT_SCHEMA_DIGEST = (
    "sha256:11a744b089bfab132f96825e5f10ce613d8d0b7ff145919fdff4bdb06c5112ee"
)
OTEL_SCHEMA_ARTIFACT_DIGEST = (
    "sha256:6ac5dd367ff707dbcdcb1e5b459d4ac2fd676fb44eb17a21f9494a9fee4233df"
)
OTEL_SCHEMA_FILE_FORMAT = "1.1.0"

SEMANTIC_PR_G2_CASE_COUNT = 32
SCHEMA_RESOURCE_PR_G2_CASE_COUNT = 36

OTEL_SPEC_VERSION = "1.59.0"
OTLP_VERSION = "1.11.0"
SEMANTIC_CONVENTION_VERSION = "1.43.0"
SEMANTIC_CONVENTION_SCHEMA_URL = "https://opentelemetry.io/schemas/1.43.0"
GENAI_SEMCONV_PIN = (
    "semantic-conventions-genai@2e994c6d59a93bb4fc1752c5378eedb9b8e14d6b"
)

SIGNAL_TYPES = frozenset({"TRACE", "METRIC", "LOG"})
DELIVERY_STATES = frozenset({"RECEIVED", "PARTIAL", "RETRYING", "DROPPED", "UNKNOWN"})
CONTENT_CAPTURE_STATES = frozenset({"DISABLED", "METADATA_ONLY"})
CLOCK_SOURCES = frozenset({"SOURCE_DECLARED", "INTAKE_CLOCK", "UNKNOWN"})
SAMPLING_DECISIONS = frozenset(
    {"RECORD_AND_SAMPLE", "RECORD_ONLY", "DROP", "UNKNOWN", "NOT_APPLICABLE"}
)
REDACTION_RESULTS = frozenset(
    {"NOT_REQUIRED", "APPLIED", "PARTIAL", "FAILED", "UNKNOWN"}
)
PARENT_STATES = frozenset({"ROOT", "CHILD", "UNKNOWN", "NOT_APPLICABLE"})

ADMISSION_STATES = frozenset(
    {
        "RECEIVED",
        "VALIDATING",
        "ACCEPTED_AS_MATERIAL",
        "PARTIAL",
        "REJECTED",
        "DUPLICATE_CONFIRMED",
        "DUPLICATE_SUSPECTED",
        "UNKNOWN",
    }
)
TERMINAL_STATES = ADMISSION_STATES - {"RECEIVED", "VALIDATING"}

REASON_CODES = (
    "TA_SCHEMA_UNSUPPORTED",
    "TA_PROFILE_UNSUPPORTED",
    "TA_SIGNAL_UNSUPPORTED",
    "TA_SHAPE_INVALID",
    "TA_SIZE_LIMIT_EXCEEDED",
    "TA_RESOURCE_MISSING",
    "TA_INSTRUMENTATION_SCOPE_MISSING",
    "TA_CONTEXT_INVALID",
    "TA_SCHEMA_URL_UNKNOWN",
    "TA_SEMCONV_UNSUPPORTED",
    "TA_GENAI_SEMCONV_UNPINNED",
    "TA_CONTENT_CAPTURE_PROHIBITED",
    "TA_SENSITIVE_KEY_DETECTED",
    "TA_DIGEST_INVALID",
    "TA_PROVENANCE_INCOMPLETE",
    "TA_IDEMPOTENCY_UNKNOWN",
    "TA_INTAKE_RECEIPT_INVALID",
    "TA_DUPLICATE_CONFIRMED",
    "TA_DUPLICATE_SUSPECTED",
    "TA_FINGERPRINT_POLICY_UNSUPPORTED",
    "TA_FINGERPRINT_COLLISION_OR_LEGITIMATE_DUPLICATE",
    "TA_IDEMPOTENCY_CONFLICT",
    "TA_PARTIAL_INPUT",
    "TA_SAMPLING_LIMITATION",
    "TA_CLOCK_UNCERTAIN",
    "TA_STORAGE_UNAVAILABLE",
    "TA_STORAGE_INTEGRITY_FAILURE",
    "TA_INTERNAL_UNKNOWN",
)
REASON_CODE_SET = frozenset(REASON_CODES)
REASON_ORDER = {code: index for index, code in enumerate(REASON_CODES)}

ENVELOPE_FIELDS = (
    "observation_id",
    "object_kind",
    "schema_version",
    "profile_id",
    "otel_spec_version",
    "otlp_version",
    "semantic_convention_version",
    "semantic_convention_schema_url",
    "genai_semconv_ref",
    "producer_reference",
    "transport_source_reference",
    "resource",
    "instrumentation_scope",
    "signal_type",
    "signal_reference",
    "context",
    "observed_at",
    "received_at",
    "clock_source",
    "sampling_state",
    "redaction_state",
    "content_capture_state",
    "delivery_state",
    "source_digest",
    "source_size_bytes",
    "idempotency_reference",
    "limitations",
)
RESOURCE_FIELDS = (
    "reference",
    "schema_url",
    "attribute_set_digest",
    "attribute_count",
)
INSTRUMENTATION_SCOPE_FIELDS = (
    "name",
    "version",
    "schema_url",
    "attribute_set_digest",
)
CONTEXT_FIELDS = ("trace_id", "span_id", "trace_flags", "parent_state")
SAMPLING_FIELDS = ("decision", "rule_reference", "known_loss")
REDACTION_FIELDS = (
    "policy_reference",
    "result",
    "removed_count",
    "hashed_count",
)

ADMISSION_RECORD_FIELDS = (
    "admission_record_id",
    "admission_id",
    "observation_reference",
    "sequence",
    "previous_record_reference",
    "state",
    "policy_version",
    "validator_version",
    "source_digest",
    "idempotency_reference",
    "intake_receipt_reference",
    "duplicate_reference",
    "comparison_fingerprint",
    "fingerprint_version",
    "accepted_item_count",
    "rejected_item_count",
    "reason_codes",
    "limitations",
    "recorded_at",
    "actor_reference",
)

OPAQUE_REFERENCE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
TRACE_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
SPAN_ID_PATTERN = re.compile(r"^[0-9a-f]{16}$")
TRACE_FLAGS_PATTERN = re.compile(r"^[0-9a-f]{2}$")

MAX_ENVELOPE_BYTES = 65_536
MAX_SOURCE_SIZE_BYTES = 16_777_216
MAX_NESTING_DEPTH = 6
MAX_LIST_ITEMS = 32
MAX_LIMITATIONS = 16
MAX_REASON_CODES = 16
MAX_ATTRIBUTE_COUNT = 1024
MAX_ERROR_DETAIL_LENGTH = 160
BUSY_TIMEOUT_MILLISECONDS = 5_000

# The closed schema is the primary boundary. This set is a defense-in-depth
# denylist and intentionally includes governance and sensitive-content names.
PROHIBITED_KEYS = frozenset(
    {
        "agent_id",
        "api_key",
        "authorization",
        "authorization_status",
        "baggage",
        "capability",
        "capability_grant",
        "cookie",
        "credential",
        "decision",
        "email",
        "entity_id",
        "evidence_id",
        "evidence_status",
        "fitness",
        "input_text",
        "output_text",
        "password",
        "permission",
        "permission_grant",
        "prompt",
        "recommendation",
        "response",
        "risk",
        "session_cookie",
        "ssn",
        "token",
        "tool_arguments",
        "tool_results",
        "truth",
        "verified",
        "verification_status",
    }
)

METRIC_NAMESPACE = "tmai.dbos.telemetry_admission"
METRIC_OUTCOMES = frozenset(
    {
        "accepted_as_material",
        "partial",
        "rejected",
        "duplicate_confirmed",
        "duplicate_suspected",
        "unknown",
        "storage_failure",
    }
)


def order_reason_codes(
    codes: set[str] | list[str] | tuple[str, ...],
) -> tuple[str, ...]:
    """Return unique stable reason codes in protocol order."""

    unique = {code for code in codes if code in REASON_CODE_SET}
    return tuple(sorted(unique, key=REASON_ORDER.__getitem__))


__all__ = [name for name in globals() if name.isupper()] + ["order_reason_codes"]
