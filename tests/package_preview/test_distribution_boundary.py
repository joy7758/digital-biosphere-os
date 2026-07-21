#!/usr/bin/env python3
"""Distribution metadata tests for the bounded DBOS Developer Preview."""

from __future__ import annotations

from pathlib import Path
import tomllib
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPOSITORY_ROOT / "pyproject.toml"
SCHEMA_FILES = {
    "common-object-schema.yaml",
    "entity-object-schema.yaml",
    "capability-object-schema.yaml",
    "execution-object-schema.yaml",
    "evidence-reference-object-schema.yaml",
    "verification-object-schema.yaml",
}


class DistributionBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.metadata = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

    def test_installed_validator_has_all_canonical_object_schemas(self) -> None:
        schemas = REPOSITORY_ROOT / "schemas"
        self.assertTrue((schemas / "__init__.py").is_file())
        self.assertTrue(SCHEMA_FILES.issubset({path.name for path in schemas.glob("*.yaml")}))

        package_data = self.metadata["tool"]["setuptools"]["package-data"]
        self.assertEqual(package_data["schemas"], ["*.yaml"])
        included = self.metadata["tool"]["setuptools"]["packages"]["find"]["include"]
        self.assertIn("schemas*", included)

    def test_repository_test_runner_is_not_an_installed_console_script(self) -> None:
        scripts = self.metadata["project"]["scripts"]
        self.assertEqual(
            scripts,
            {"dbos-validate": "validator.object_schema_validator:main"},
        )
        self.assertNotIn("dbos-tests", scripts)

    def test_distribution_boundary_excludes_governed_state_packages(self) -> None:
        included = self.metadata["tool"]["setuptools"]["packages"]["find"]["include"]
        for governed_package in (
            "constitution*",
            "entity_support*",
            "evidence*",
            "evolution*",
            "registry*",
            "tests*",
            "tools*",
        ):
            self.assertNotIn(governed_package, included)


if __name__ == "__main__":
    unittest.main()
