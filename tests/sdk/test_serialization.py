"""Detached dict and deterministic JSON serialization tests."""

from __future__ import annotations

import json
import unittest
from enum import Enum

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

    def test_object_to_dict_with_enums_and_sets(self) -> None:
        class Color(Enum):
            RED = "red"
            BLUE = "blue"

        # Create a mock BaseObject subclass to test complex types
        from sdk.objects.base import BaseObject
        from dataclasses import dataclass

        # We need a proper frozen dataclass that inherits from BaseObject
        @dataclass(frozen=True, slots=True, kw_only=True)
        class ComplexObject(BaseObject):
            colors: set[str]
            color_enum: Color
            nested_dict: dict[str, dict[str, int]]
            object_type: str = "COMPLEX"

        target = ComplexObject(
            object_id="test-id",
            source={"namespace": "test", "version": "v1"},
            status="TESTING",
            limitations=[],
            colors={"b", "a"},
            color_enum=Color.RED,
            nested_dict={"level1": {"level2": 42}},
        )

        result = object_to_dict(target)

        self.assertEqual(result["object_type"], "COMPLEX")
        self.assertEqual(result["colors"], ["a", "b"])  # Sorted list
        self.assertEqual(result["color_enum"], "red")   # Enum value
        self.assertEqual(result["nested_dict"], {"level1": {"level2": 42}})

if __name__ == "__main__":
    unittest.main()
