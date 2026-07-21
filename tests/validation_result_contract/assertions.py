"""Shared assertions for the frozen nine-field ValidationResult contract."""

from __future__ import annotations

import unittest

from validator.validation_result_model import ValidationResult


RESULT_FIELDS = {
    "validation_id",
    "validator_version",
    "target_reference",
    "schema_reference",
    "result",
    "errors",
    "warnings",
    "limitations",
    "timestamp",
}

ERROR_FIELDS = {
    "error_code",
    "message",
    "field_reference",
    "severity",
    "resolution_hint",
}

SCHEMA_REFERENCE_FIELDS = {"schema_id", "schema_digest"}


def assert_result_contract(
    testcase: unittest.TestCase,
    result: ValidationResult,
    expected_status: str,
) -> dict[str, object]:
    payload = result.to_dict()
    testcase.assertEqual(set(payload), RESULT_FIELDS)
    testcase.assertEqual(payload["result"], expected_status)
    testcase.assertEqual(payload["validator_version"], "v0.1")
    testcase.assertIsInstance(payload["errors"], list)
    testcase.assertIsInstance(payload["warnings"], list)
    testcase.assertIsInstance(payload["limitations"], list)
    testcase.assertTrue(payload["limitations"])
    testcase.assertIsNone(payload["validation_id"])
    testcase.assertIsNone(payload["timestamp"])
    if payload["schema_reference"] is not None:
        testcase.assertEqual(
            set(payload["schema_reference"]),
            SCHEMA_REFERENCE_FIELDS,
        )
    for issue in [*payload["errors"], *payload["warnings"]]:
        testcase.assertEqual(set(issue), ERROR_FIELDS)
    return payload
