"""Tests for the freeze_value utility."""

from __future__ import annotations

from types import MappingProxyType
import unittest

from sdk.objects.base import freeze_value


class FreezeValueTests(unittest.TestCase):
    def test_freeze_scalar(self) -> None:
        self.assertEqual(freeze_value(42), 42)
        self.assertEqual(freeze_value("hello"), "hello")
        self.assertIsNone(freeze_value(None))

    def test_freeze_list_to_tuple(self) -> None:
        self.assertEqual(freeze_value([1, 2, 3]), (1, 2, 3))
        self.assertIsInstance(freeze_value([1, 2, 3]), tuple)

    def test_freeze_tuple(self) -> None:
        self.assertEqual(freeze_value((1, 2, 3)), (1, 2, 3))

    def test_freeze_set_to_sorted_tuple(self) -> None:
        s = {2, 1, 3}
        self.assertEqual(freeze_value(s), (1, 2, 3))

        s2 = {"b", "a"}
        self.assertEqual(freeze_value(s2), ("a", "b"))

        s3 = {1, "a"}
        expected_s3 = tuple(sorted((1, "a"), key=repr))
        self.assertEqual(freeze_value(s3), expected_s3)

    def test_freeze_mapping(self) -> None:
        m = {"a": 1, "b": 2}
        frozen = freeze_value(m)
        self.assertIsInstance(frozen, MappingProxyType)
        self.assertEqual(frozen["a"], 1)
        self.assertEqual(frozen["b"], 2)

        with self.assertRaises(TypeError):
            frozen["a"] = 3 # type: ignore[index]

    def test_freeze_nested_structures(self) -> None:
        nested = {
            "list": [1, {"a": 2}],
            "tuple": (3, [4, 5]),
            "set": {6, 7},
            "dict": {"b": [8, 9]}
        }

        frozen = freeze_value(nested)

        self.assertIsInstance(frozen, MappingProxyType)
        self.assertIsInstance(frozen["list"], tuple)
        self.assertIsInstance(frozen["list"][1], MappingProxyType)
        self.assertEqual(frozen["list"][1]["a"], 2)

        self.assertIsInstance(frozen["tuple"], tuple)
        self.assertIsInstance(frozen["tuple"][1], tuple)
        self.assertEqual(frozen["tuple"][1], (4, 5))

        self.assertIsInstance(frozen["set"], tuple)
        self.assertEqual(freeze_value({6, 7}), frozen["set"])

        self.assertIsInstance(frozen["dict"], MappingProxyType)
        self.assertIsInstance(frozen["dict"]["b"], tuple)
        self.assertEqual(frozen["dict"]["b"], (8, 9))


    def test_freeze_frozenset(self) -> None:
        fs = frozenset({1, 2, 3})
        self.assertEqual(freeze_value(fs), frozenset({1, 2, 3}))

    def test_freeze_bytes(self) -> None:
        b = b"hello"
        self.assertEqual(freeze_value(b), b"hello")


    def test_freeze_custom_object(self) -> None:
        class CustomObj:
            def __init__(self, val: int) -> None:
                self.val = val

        obj = CustomObj(42)
        self.assertEqual(freeze_value(obj), obj)

if __name__ == "__main__":
    unittest.main()
