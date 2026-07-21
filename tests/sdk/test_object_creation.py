"""Pure data-object construction tests for the local SDK skeleton."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from fixtures import all_objects, entity_object
from sdk.objects import EntityObject
from sdk.serialization import object_to_dict


class ObjectCreationTests(unittest.TestCase):
    def test_creates_exactly_five_contract_object_types(self) -> None:
        self.assertEqual(
            tuple(item.object_type for item in all_objects()),
            ("ENTITY", "CAPABILITY", "EXECUTION", "EVIDENCE_REFERENCE", "VERIFICATION"),
        )

    def test_preserves_caller_supplied_identifiers(self) -> None:
        target = entity_object()
        self.assertEqual(target.object_id, target.entity_id)

    def test_does_not_generate_timestamps(self) -> None:
        target = entity_object(created_at=None, updated_at=None)
        self.assertIsNone(target.created_at)
        self.assertIsNone(target.updated_at)

    def test_common_fields_are_required_from_caller(self) -> None:
        values = object_to_dict(entity_object())
        values.pop("object_type")
        values.pop("source")
        with self.assertRaises(TypeError):
            EntityObject(**values)

    def test_object_is_frozen(self) -> None:
        target = entity_object()
        with self.assertRaises(FrozenInstanceError):
            target.status = "REVOKED"  # type: ignore[misc]

    def test_nested_declarations_are_frozen(self) -> None:
        target = entity_object()
        with self.assertRaises(TypeError):
            target.source["status"] = "REVOKED"  # type: ignore[index]


if __name__ == "__main__":
    unittest.main()
