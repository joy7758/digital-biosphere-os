import unittest
from datetime import datetime, timezone
from validator.object_schema_validator import _parse_timestamp

class TestObjectSchemaValidator(unittest.TestCase):
    def test_parse_timestamp_valid(self):
        """Test parsing a valid ISO timestamp."""
        ts = "2023-01-01T12:00:00Z"
        result = _parse_timestamp(ts)
        self.assertIsNotNone(result)
        self.assertEqual(result, datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc))

    def test_parse_timestamp_invalid_string(self):
        """Test parsing an invalid string that raises ValueError."""
        ts = "invalid-date"
        result = _parse_timestamp(ts)
        self.assertIsNone(result)

    def test_parse_timestamp_non_string(self):
        """Test parsing a non-string value."""
        ts = 12345
        result = _parse_timestamp(ts)
        self.assertIsNone(result)

    def test_parse_timestamp_missing_timezone(self):
        """Test parsing a valid ISO timestamp missing timezone info."""
        ts = "2023-01-01T12:00:00"
        result = _parse_timestamp(ts)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
