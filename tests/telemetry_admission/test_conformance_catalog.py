"""Machine-readable coverage binding for all preregistered C/N/D/S/F/M/R cases."""

from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "conformance_catalog.v0.1.json"
CASE_COUNTS = {"C": 12, "N": 7, "D": 12, "S": 11, "F": 14, "M": 12, "R": 10}


class ConformanceCatalogTests(unittest.TestCase):
    def test_catalog_has_exact_78_case_inventory_and_resolvable_nodes(self) -> None:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        cases = catalog["cases"]
        self.assertEqual(catalog["case_count"], 78)
        self.assertEqual(len(cases), 78)
        self.assertEqual(len({case["case_id"] for case in cases}), 78)

        expected = {
            f"TA-{group}{index:03d}"
            for group, count in CASE_COUNTS.items()
            for index in range(1, count + 1)
        }
        self.assertEqual({case["case_id"] for case in cases}, expected)

        test_nodes: set[str] = set()
        for path in ROOT.glob("test_*.py"):
            module = path.stem
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for class_node in (
                node for node in tree.body if isinstance(node, ast.ClassDef)
            ):
                for method in (
                    node
                    for node in class_node.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name.startswith("test_")
                ):
                    test_nodes.add(f"{module}.{class_node.name}.{method.name}")
        unresolved = sorted(
            case["test_node"] for case in cases if case["test_node"] not in test_nodes
        )
        self.assertEqual(unresolved, [])
        self.assertTrue(
            all(re.fullmatch(r"TA-[CNDSFMR]\d{3}", case["case_id"]) for case in cases)
        )


if __name__ == "__main__":
    unittest.main()
