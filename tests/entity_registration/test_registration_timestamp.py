"""Tests for registration timestamp parsing and validation."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
import re

from entity_support.registration.registration_executor import _event_timestamp

class RegistrationTimestampTests(unittest.TestCase):
    def test_valid_timezone_aware_timestamp(self) -> None:
        timestamp = "2026-07-20T12:00:00+08:00"
        value, errors = _event_timestamp(timestamp)
        self.assertEqual(value, timestamp)
        self.assertEqual(errors, [])

    def test_valid_utc_timestamp_with_z(self) -> None:
        timestamp = "2026-07-20T12:00:00Z"
        value, errors = _event_timestamp(timestamp)
        self.assertEqual(value, timestamp)
        self.assertEqual(errors, [])

    def test_none_timestamp_returns_current_time_and_no_errors(self) -> None:
        before = datetime.now(timezone.utc)
        value, errors = _event_timestamp(None)
        after = datetime.now(timezone.utc)
        self.assertEqual(errors, [])
        # Verify the returned value is a valid ISO 8601 string between before and after
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        self.assertLessEqual(before, parsed)
        self.assertGreaterEqual(after, parsed)
        self.assertIsNotNone(parsed.tzinfo)

    def test_missing_timezone_returns_error(self) -> None:
        timestamp = "2026-07-20T12:00:00"
        value, errors = _event_timestamp(timestamp)
        self.assertTrue(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?\+00:00$", value.replace("Z", "+00:00")))
        self.assertEqual(errors, ["registered_at must be a timezone-aware ISO 8601 string"])

    def test_invalid_string_format_returns_error(self) -> None:
        timestamp = "not-a-timestamp"
        value, errors = _event_timestamp(timestamp)
        self.assertTrue(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?\+00:00$", value.replace("Z", "+00:00")))
        self.assertEqual(errors, ["registered_at must be a timezone-aware ISO 8601 string"])

    def test_invalid_type_returns_error(self) -> None:
        timestamp = 123
        value, errors = _event_timestamp(timestamp) # type: ignore
        self.assertTrue(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?\+00:00$", value.replace("Z", "+00:00")))
        self.assertEqual(errors, ["registered_at must be a timezone-aware ISO 8601 string"])

if __name__ == "__main__":
    unittest.main()
