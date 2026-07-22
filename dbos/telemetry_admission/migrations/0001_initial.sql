CREATE TABLE schema_migrations (
    version TEXT PRIMARY KEY,
    checksum TEXT NOT NULL,
    applied_at TEXT NOT NULL
);

CREATE TABLE observation_envelopes (
    observation_id TEXT PRIMARY KEY,
    envelope_json TEXT,
    source_digest TEXT NOT NULL,
    persistence_class TEXT NOT NULL CHECK (
        persistence_class IN ('VALIDATED_METADATA', 'REJECTION_STUB')
    ),
    comparison_fingerprint TEXT,
    fingerprint_version TEXT NOT NULL,
    payload_digest TEXT NOT NULL,
    received_at TEXT NOT NULL
);

CREATE TABLE admission_lifecycles (
    admission_id TEXT PRIMARY KEY,
    observation_reference TEXT NOT NULL REFERENCES observation_envelopes(observation_id),
    source_digest TEXT NOT NULL,
    idempotency_reference TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE admission_records (
    admission_record_id TEXT PRIMARY KEY,
    admission_id TEXT NOT NULL REFERENCES admission_lifecycles(admission_id),
    observation_reference TEXT NOT NULL REFERENCES observation_envelopes(observation_id),
    sequence INTEGER NOT NULL CHECK (sequence >= 1),
    previous_record_reference TEXT REFERENCES admission_records(admission_record_id),
    state TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    validator_version TEXT NOT NULL,
    source_digest TEXT NOT NULL,
    idempotency_reference TEXT NOT NULL,
    intake_receipt_reference TEXT NOT NULL,
    duplicate_reference TEXT,
    comparison_fingerprint TEXT,
    fingerprint_version TEXT NOT NULL,
    accepted_item_count INTEGER NOT NULL CHECK (accepted_item_count >= 0),
    rejected_item_count INTEGER NOT NULL CHECK (rejected_item_count >= 0),
    reason_codes_json TEXT NOT NULL,
    limitations_json TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    actor_reference TEXT NOT NULL,
    record_digest TEXT NOT NULL,
    UNIQUE(admission_id, sequence)
);

CREATE TABLE intake_receipts (
    intake_receipt_reference TEXT PRIMARY KEY,
    admission_id TEXT NOT NULL UNIQUE REFERENCES admission_lifecycles(admission_id),
    source_digest TEXT NOT NULL,
    issued_at TEXT NOT NULL
);

CREATE TABLE untrusted_idempotency_hints (
    idempotency_reference TEXT NOT NULL,
    admission_id TEXT NOT NULL REFERENCES admission_lifecycles(admission_id),
    comparison_fingerprint TEXT,
    recorded_at TEXT NOT NULL,
    PRIMARY KEY(idempotency_reference, admission_id)
);

CREATE TABLE backup_manifests (
    backup_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    database_sha256 TEXT NOT NULL,
    record_chain_digest TEXT NOT NULL,
    manifest_digest TEXT NOT NULL,
    counts_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX idx_observation_fingerprint
    ON observation_envelopes(comparison_fingerprint, fingerprint_version);
CREATE INDEX idx_admission_records_lifecycle
    ON admission_records(admission_id, sequence);
CREATE INDEX idx_idempotency_hint
    ON untrusted_idempotency_hints(idempotency_reference);

CREATE TRIGGER schema_migrations_no_update
BEFORE UPDATE ON schema_migrations
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;
CREATE TRIGGER schema_migrations_no_delete
BEFORE DELETE ON schema_migrations
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;

CREATE TRIGGER observation_envelopes_no_update
BEFORE UPDATE ON observation_envelopes
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;
CREATE TRIGGER observation_envelopes_no_delete
BEFORE DELETE ON observation_envelopes
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;

CREATE TRIGGER admission_lifecycles_no_update
BEFORE UPDATE ON admission_lifecycles
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;
CREATE TRIGGER admission_lifecycles_no_delete
BEFORE DELETE ON admission_lifecycles
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;

CREATE TRIGGER admission_records_no_update
BEFORE UPDATE ON admission_records
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;
CREATE TRIGGER admission_records_no_delete
BEFORE DELETE ON admission_records
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;

CREATE TRIGGER intake_receipts_no_update
BEFORE UPDATE ON intake_receipts
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;
CREATE TRIGGER intake_receipts_no_delete
BEFORE DELETE ON intake_receipts
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;

CREATE TRIGGER untrusted_idempotency_hints_no_update
BEFORE UPDATE ON untrusted_idempotency_hints
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;
CREATE TRIGGER untrusted_idempotency_hints_no_delete
BEFORE DELETE ON untrusted_idempotency_hints
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;

CREATE TRIGGER backup_manifests_no_update
BEFORE UPDATE ON backup_manifests
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;
CREATE TRIGGER backup_manifests_no_delete
BEFORE DELETE ON backup_manifests
BEGIN
    SELECT RAISE(ABORT, 'TA_APPEND_ONLY');
END;
