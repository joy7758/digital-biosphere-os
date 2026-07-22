-- Synthetic prior-compatible fixture derived from a current empty store.
-- The test harness replaces {{PRIOR_CHECKSUM}} with this file's SHA-256.
DROP INDEX idx_observation_fingerprint;
DROP TRIGGER schema_migrations_no_update;
DROP TRIGGER schema_migrations_no_delete;
DELETE FROM schema_migrations;
INSERT INTO schema_migrations(version, checksum, applied_at)
VALUES ('0000', '{{PRIOR_CHECKSUM}}', '2026-07-22T00:00:00Z');
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
PRAGMA user_version=0;
