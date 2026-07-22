"""Bounded DBOS telemetry admission foundation.

Agent-readable boundary:

* This package validates and records metadata-only observation material.
* ``ACCEPTED_AS_MATERIAL`` is not Evidence, Verification, Permission, Identity,
  Entity registration, execution, or truth.
* The package has no network listener, OTLP decoder, Collector integration,
  Agent, Runtime, SAEE call, or lifecycle activation path.
* SQLite is a single-host reference conformance backend, not a selected
  production persistence service.

The package is intentionally not re-exported from :mod:`dbos`. Callers must
opt into the versioned, pre-production surface explicitly.
"""

from .contracts import (
    ADMISSION_POLICY_VERSION,
    ENVELOPE_SCHEMA_VERSION,
    FINGERPRINT_VERSION,
    PROFILE_ID,
    RECORD_SCHEMA_VERSION,
    VALIDATOR_VERSION,
)
from .metrics import AdmissionMetrics
from .models import AdmissionResult, ValidationDecision
from .provenance import (
    DataGovernanceBinding,
    DetectorBinding,
    SchemaResourceProvenanceValidator,
    TransformerBinding,
)
from .semantic import SemanticMetadataMapper, SemanticSourceBinding
from .service import TelemetryAdmissionService
from .store import SQLiteTelemetryAdmissionStore
from .validator import TelemetryEnvelopeValidator

__all__ = [
    "ADMISSION_POLICY_VERSION",
    "AdmissionMetrics",
    "AdmissionResult",
    "DataGovernanceBinding",
    "DetectorBinding",
    "ENVELOPE_SCHEMA_VERSION",
    "FINGERPRINT_VERSION",
    "PROFILE_ID",
    "RECORD_SCHEMA_VERSION",
    "SQLiteTelemetryAdmissionStore",
    "SchemaResourceProvenanceValidator",
    "SemanticMetadataMapper",
    "SemanticSourceBinding",
    "TelemetryAdmissionService",
    "TelemetryEnvelopeValidator",
    "TransformerBinding",
    "VALIDATOR_VERSION",
    "ValidationDecision",
]
