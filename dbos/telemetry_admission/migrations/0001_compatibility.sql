-- Explicit additive migration from synthetic prior-compatible 0000.
CREATE INDEX idx_observation_fingerprint
    ON observation_envelopes(comparison_fingerprint, fingerprint_version);
