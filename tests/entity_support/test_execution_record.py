"""Tests for inert execution-record declarations."""

from __future__ import annotations

import unittest

from entity_support.execution_registry import (
    EXECUTION_RECORD_FIELDS,
    build_execution_record,
    validate_execution_record,
)


class ExecutionRecordTests(unittest.TestCase):
    def _build(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "execution_id": "fixture-execution",
            "entity_id": "fixture-entity",
            "task_reference": "fixture-task",
            "input_reference": "fixture-input",
            "context_reference": "fixture-context",
        }
        values.update(overrides)
        return build_execution_record(**values)

    def test_execution_defaults_to_created(self) -> None:
        record = self._build()
        self.assertEqual(record["status"], "CREATED")
        self.assertEqual(tuple(record), EXECUTION_RECORD_FIELDS)

    def test_execution_has_no_output_by_default(self) -> None:
        record = self._build()
        self.assertIsNone(record["output_reference"])

    def test_execution_rejects_success(self) -> None:
        with self.assertRaises(ValueError):
            self._build(status="SUCCESS")

    def test_execution_requires_context_reference(self) -> None:
        record = self._build()
        record.pop("context_reference")
        errors = validate_execution_record(record)
        self.assertTrue(any("missing fields" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
