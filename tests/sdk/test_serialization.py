"""Detached dict and deterministic JSON serialization tests."""

from __future__ import annotations

import json
import unittest

from fixtures import all_objects, capability_object, entity_object
from sdk.serialization import object_to_dict, object_to_json
from sdk.serialization.serializer import _json_value


class SerializationTests(unittest.TestCase):
    def test_serializes_all_five_objects_to_dict(self) -> None:
        for target in all_objects():
            with self.subTest(object_type=target.object_type):
                self.assertEqual(object_to_dict(target)["object_type"], target.object_type)

    def test_preserves_version_source_and_limitations(self) -> None:
        serialized = object_to_dict(entity_object())
        self.assertEqual(serialized["version"], "v0.1")
        self.assertEqual(serialized["source"]["namespace"], "dbio")
        self.assertEqual(
            serialized["limitations"],
            ["Synthetic in-memory SDK test fixture only."],
        )

    def test_object_to_dict_exact_output_format(self) -> None:
        target = entity_object()
        expected = {
            "object_id": "dbio://repository/synthetic-sdk-fixture/v0.1",
            "source": {
                "namespace": "dbio",
                "source_id": "registry/entities.yaml",
                "version": "v0.1",
                "status": "DECLARED"
            },
            "status": "DECLARED",
            "limitations": [
                "Synthetic in-memory SDK test fixture only."
            ],
            "version": "v0.1",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "object_type": "ENTITY",
            "entity_id": "dbio://repository/synthetic-sdk-fixture/v0.1",
            "entity_type": "repository",
            "owner_reference": {
                "reference_id": "dbio://entity/synthetic-owner/v0.1",
                "reference_type": "ENTITY",
                "namespace": "dbio",
                "version": "v0.1",
                "source": "registry/entities.yaml",
                "status": "DECLARED"
            },
            "lifecycle_state": "PROPOSED",
            "source_reference": {
                "reference_id": "dbio://repository/synthetic-sdk-fixture/v0.1",
                "reference_type": "ENTITY",
                "namespace": "dbio",
                "version": "v0.1",
                "source": "registry/entities.yaml",
                "status": "DECLARED"
            }
        }
        self.assertEqual(object_to_dict(target), expected)

    def test_json_round_trip_preserves_serialized_object(self) -> None:
        target = capability_object()
        self.assertEqual(json.loads(object_to_json(target)), object_to_dict(target))

    def test_serialized_copy_cannot_mutate_original(self) -> None:
        target = entity_object()
        serialized = object_to_dict(target)
        serialized["source"]["status"] = "REVOKED"
        self.assertEqual(target.source["status"], "DECLARED")

    def test_serialization_does_not_validate_or_add_results(self) -> None:
        serialized = object_to_dict(entity_object(entity_id="conflicting-id"))
        self.assertNotIn("validation_result", serialized)
        self.assertEqual(serialized["entity_id"], "conflicting-id")

    def test_rejects_non_sdk_input(self) -> None:
        with self.assertRaises(TypeError):
            object_to_dict({"object_type": "ENTITY"})  # type: ignore[arg-type]

    def test_json_value_parses_lists_and_tuples(self) -> None:
        self.assertEqual(_json_value((1, 2, 3)), [1, 2, 3])
        self.assertEqual(_json_value([1, 2, 3]), [1, 2, 3])
        self.assertEqual(_json_value({1, 2, 3}), [1, 2, 3])

    def test_json_value_parses_enums(self) -> None:
        from enum import Enum

        class TestEnum(Enum):
            A = "a"
            B = "b"

        self.assertEqual(_json_value(TestEnum.A), "a")

    def test_object_to_json_default_indent(self) -> None:
        target = entity_object()
        json_str = object_to_json(target)
        self.assertTrue(json_str.startswith("{\n  \""))
        self.assertEqual(json.loads(json_str), object_to_dict(target))

    def test_object_to_json_no_indent(self) -> None:
        target = entity_object()
        json_str = object_to_json(target, indent=None)
        self.assertNotIn("\n", json_str)
        self.assertEqual(json.loads(json_str), object_to_dict(target))

    def test_object_to_json_custom_indent(self) -> None:
        target = entity_object()
        json_str = object_to_json(target, indent=4)
        self.assertTrue(json_str.startswith("{\n    \""))
        self.assertEqual(json.loads(json_str), object_to_dict(target))


if __name__ == "__main__":
    unittest.main()
