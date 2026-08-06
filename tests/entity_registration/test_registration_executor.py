"""Tests for timestamp validation in registration executor."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from entity_support.registration.registration_executor import _event_timestamp

class EventTimestampTests(unittest.TestCase):
    def test_none_returns_current_utc(self) -> None:
        val, errors = _event_timestamp(None)
        self.assertEqual(errors, [])
        # Ensure the returned string is a valid timezone-aware isoformat
        parsed = datetime.fromisoformat(val.replace("Z", "+00:00"))
        self.assertIsNotNone(parsed.tzinfo)

    def test_valid_timezone_aware(self) -> None:
        val, errors = _event_timestamp("2026-07-20T12:00:00+08:00")
        self.assertEqual(errors, [])
        self.assertEqual(val, "2026-07-20T12:00:00+08:00")

    def test_valid_zulu_timezone(self) -> None:
        val, errors = _event_timestamp("2026-07-20T12:00:00Z")
        self.assertEqual(errors, [])
        self.assertEqual(val, "2026-07-20T12:00:00Z")

    def test_naive_datetime_returns_error(self) -> None:
        val, errors = _event_timestamp("2026-07-20T12:00:00")
        self.assertEqual(errors, ["registered_at must be a timezone-aware ISO 8601 string"])
        self.assertNotEqual(val, "2026-07-20T12:00:00")
        parsed = datetime.fromisoformat(val.replace("Z", "+00:00"))
        self.assertIsNotNone(parsed.tzinfo)

    def test_invalid_string_returns_error(self) -> None:
        val, errors = _event_timestamp("invalid-date-format")
        self.assertEqual(errors, ["registered_at must be a timezone-aware ISO 8601 string"])
        parsed = datetime.fromisoformat(val.replace("Z", "+00:00"))
        self.assertIsNotNone(parsed.tzinfo)

    def test_invalid_type_returns_error(self) -> None:
        val, errors = _event_timestamp(1234567890)  # type: ignore
        self.assertEqual(errors, ["registered_at must be a timezone-aware ISO 8601 string"])
        parsed = datetime.fromisoformat(val.replace("Z", "+00:00"))
        self.assertIsNotNone(parsed.tzinfo)

if __name__ == "__main__":
    unittest.main()
