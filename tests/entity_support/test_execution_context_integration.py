"""Tests for read-only links to existing DBOS Execution Context records."""

from __future__ import annotations

import unittest

from entity_support.execution_context_integration import build_execution_context_link
from entity_support.execution_registry import build_execution_record


class ExecutionContextIntegrationTests(unittest.TestCase):
    def _execution(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "execution_id": "fixture-execution",
            "entity_id": "fixture-entity",
            "task_reference": "fixture-task",
            "input_reference": "fixture-input",
            "context_reference": "fixture-context",
        }
        values.update(overrides)
        return build_execution_record(**values)

    def _context(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "context_id": "fixture-context",
            "status": "validated",
        }
        values.update(overrides)
        return values

    def test_link_preserves_execution_references(self) -> None:
        link = build_execution_context_link(
            self._execution(), context_record=self._context()
        )
        self.assertEqual(link["execution_id"], "fixture-execution")
        self.assertEqual(link["context_reference"], "fixture-context")

    def test_link_keeps_execution_created(self) -> None:
        link = build_execution_context_link(
            self._execution(), context_record=self._context()
        )
        self.assertEqual(link["execution_status"], "CREATED")

    def test_link_has_no_runtime_effect(self) -> None:
        link = build_execution_context_link(
            self._execution(), context_record=self._context()
        )
        self.assertEqual(link["runtime_effect"], "NONE")
        self.assertNotIn("runtime_id", link)

    def test_context_id_must_match_reference(self) -> None:
        with self.assertRaises(ValueError):
            build_execution_context_link(
                self._execution(),
                context_record=self._context(context_id="different-context"),
            )

    def test_revoked_context_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_execution_context_link(
                self._execution(), context_record=self._context(status="revoked")
            )

    def test_success_execution_record_is_rejected_before_linking(self) -> None:
        execution = self._execution()
        execution["status"] = "SUCCESS"
        with self.assertRaises(ValueError):
            build_execution_context_link(execution, context_record=self._context())

    def test_null_output_reference_remains_not_a_result(self) -> None:
        link = build_execution_context_link(
            self._execution(), context_record=self._context()
        )
        self.assertIsNone(link["output_reference"])


if __name__ == "__main__":
    unittest.main()
