"""Tests for the freeze_value recursive function."""

import unittest
from types import MappingProxyType

from sdk.objects.base import freeze_value


class FreezeValueTests(unittest.TestCase):
    def test_primitive_types(self) -> None:
        self.assertEqual(freeze_value(1), 1)
        self.assertEqual(freeze_value("hello"), "hello")
        self.assertEqual(freeze_value(True), True)
        self.assertIsNone(freeze_value(None))

    def test_empty_collections(self) -> None:
        self.assertEqual(freeze_value([]), ())
        self.assertEqual(freeze_value(()), ())
        self.assertEqual(freeze_value(set()), ())
        frozen_dict = freeze_value({})
        self.assertIsInstance(frozen_dict, MappingProxyType)
        self.assertEqual(dict(frozen_dict), {})

    def test_list_becomes_tuple(self) -> None:
        self.assertEqual(freeze_value([1, 2, 3]), (1, 2, 3))

    def test_tuple_is_preserved(self) -> None:
        self.assertEqual(freeze_value((1, 2, 3)), (1, 2, 3))

    def test_set_becomes_sorted_tuple(self) -> None:
        # repr(1) -> '1', repr(2) -> '2', repr('10') -> "'10'"
        # '1' < '2', but for repr string sorting we should just check an obvious case
        self.assertEqual(freeze_value({"b", "a", "c"}), ("a", "b", "c"))

        # Test with ints
        self.assertEqual(freeze_value({3, 1, 2}), (1, 2, 3))

    def test_dict_becomes_mapping_proxy(self) -> None:
        frozen_dict = freeze_value({"a": 1, "b": 2})
        self.assertIsInstance(frozen_dict, MappingProxyType)
        self.assertEqual(frozen_dict["a"], 1)
        self.assertEqual(frozen_dict["b"], 2)

    def test_nested_structures(self) -> None:
        nested = {
            "list": [1, [2, 3]],
            "dict": {"inner": {"key": "value"}},
            "set": {3, 1, 2},
            "tuple": (1, (2, 3)),
        }
        frozen = freeze_value(nested)

        self.assertIsInstance(frozen, MappingProxyType)
        self.assertEqual(frozen["list"], (1, (2, 3)))

        self.assertIsInstance(frozen["dict"], MappingProxyType)
        self.assertIsInstance(frozen["dict"]["inner"], MappingProxyType)
        self.assertEqual(frozen["dict"]["inner"]["key"], "value")

        self.assertEqual(frozen["set"], (1, 2, 3))
        self.assertEqual(frozen["tuple"], (1, (2, 3)))

    def test_mutation_attempt_raises_error(self) -> None:
        frozen = freeze_value({"a": [1, 2], "b": {"c": 3}})

        with self.assertRaises(TypeError):
            frozen["a"] = (1, 2, 3) # type: ignore

        with self.assertRaises(TypeError):
            frozen["b"]["c"] = 4 # type: ignore

        # Tuple doesn't support item assignment
        with self.assertRaises(TypeError):
            frozen["a"][0] = 5 # type: ignore

if __name__ == "__main__":
    unittest.main()
