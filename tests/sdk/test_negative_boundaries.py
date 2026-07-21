"""Negative SDK boundaries: no Agent, Runtime, execution, permission, or truth effect."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import inspect
from pathlib import Path
import unittest

import sdk
from fixtures import capability_object, entity_object, evidence_reference_object, execution_object
from sdk.objects import CapabilityObject
from sdk.serialization import object_to_dict
from sdk.validation import validate_object
from validator import ValidationStatus


SDK_ROOT = Path(__file__).resolve().parents[2] / "sdk"


class NegativeBoundaryTests(unittest.TestCase):
    def test_sdk_cannot_construct_permission_field(self) -> None:
        values = object_to_dict(capability_object())
        values.pop("object_type")
        values["permission"] = "GRANTED"
        with self.assertRaises(TypeError):
            CapabilityObject(**values)

    def test_sdk_exports_no_agent_type(self) -> None:
        self.assertFalse(hasattr(sdk, "Agent"))
        self.assertFalse((SDK_ROOT / "objects" / "agent.py").exists())

    def test_sdk_exports_no_runtime_or_api_server(self) -> None:
        self.assertFalse(hasattr(sdk, "Runtime"))
        self.assertFalse(hasattr(sdk, "APIServer"))

    def test_execution_object_has_no_behavioral_entrypoint(self) -> None:
        target = execution_object()
        for method in ("execute", "run", "start", "invoke"):
            self.assertFalse(hasattr(target, method))

    def test_evidence_reference_cannot_be_changed_to_truth(self) -> None:
        target = evidence_reference_object()
        self.assertFalse(hasattr(target, "truth"))
        with self.assertRaises(FrozenInstanceError):
            target.integrity_status = "VERIFIED"  # type: ignore[misc]

    def test_invalid_object_cannot_bypass_validator(self) -> None:
        result = validate_object(entity_object(entity_id="conflicting-id"))
        self.assertEqual(result.result, ValidationStatus.CONFLICT)

    def test_serialization_does_not_claim_validation(self) -> None:
        serialized = object_to_dict(entity_object())
        self.assertNotIn("validated", serialized)
        self.assertNotIn("permission", serialized)

    def test_sdk_source_has_no_network_or_process_execution_imports(self) -> None:
        source_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in SDK_ROOT.rglob("*.py")
        )
        for forbidden in ("import socket", "import subprocess", "import requests"):
            self.assertNotIn(forbidden, source_text)

    def test_object_types_are_data_classes_only(self) -> None:
        target = entity_object()
        public_methods = {
            name
            for name, member in inspect.getmembers(type(target), inspect.isfunction)
            if not name.startswith("__")
        }
        self.assertEqual(public_methods, set())


if __name__ == "__main__":
    unittest.main()
