"""Tests for governance constraints and boundaries validation logic."""

from __future__ import annotations

import unittest

from validator.governance_constraint_validator import _walk_keys


class TestWalkKeys(unittest.TestCase):
    def test_flat_dict(self) -> None:
        data = {"a": 1, "B": 2}
        result = list(_walk_keys(data))
        self.assertEqual(result, [("$.a", "a"), ("$.B", "b")])

    def test_nested_dict(self) -> None:
        data = {"a": {"b": {"C": 3}}}
        result = list(_walk_keys(data))
        self.assertEqual(result, [("$.a", "a"), ("$.a.b", "b"), ("$.a.b.C", "c")])

    def test_list_in_dict(self) -> None:
        data = {"a": [1, {"b": 2}]}
        result = list(_walk_keys(data))
        self.assertEqual(result, [("$.a", "a"), ("$.a[1].b", "b")])

    def test_dict_in_list(self) -> None:
        data = [{"A": 1}, {"B": 2}]
        result = list(_walk_keys(data))
        self.assertEqual(result, [("$[0].A", "a"), ("$[1].B", "b")])

    def test_empty_collections(self) -> None:
        self.assertEqual(list(_walk_keys({})), [])
        self.assertEqual(list(_walk_keys([])), [])
        self.assertEqual(list(_walk_keys({"a": [], "b": {}})), [("$.a", "a"), ("$.b", "b")])

    def test_non_string_keys(self) -> None:
        data = {1: "a", None: "b"}
        result = list(_walk_keys(data))
        self.assertEqual(result, [("$.1", "1"), ("$.None", "none")])

    def test_deep_nesting(self) -> None:
        data = {"a": {"b": [{"c": [{"D": 4}]}]}}
        result = list(_walk_keys(data))
        self.assertEqual(
            result,
            [("$.a", "a"), ("$.a.b", "b"), ("$.a.b[0].c", "c"), ("$.a.b[0].c[0].D", "d")]
        )

    def test_non_collection_input(self) -> None:
        self.assertEqual(list(_walk_keys("string")), [])
        self.assertEqual(list(_walk_keys(123)), [])
        self.assertEqual(list(_walk_keys(None)), [])


if __name__ == '__main__':
    unittest.main()
