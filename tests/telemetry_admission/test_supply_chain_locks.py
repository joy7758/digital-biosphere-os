"""Executable, agent-readable controls for DQ-018 supply-chain locks."""

from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path

from tools.telemetry_admission_otel_conformance import _source_manifest


ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = ROOT / "requirements"
MACOS_RUNTIME_LOCK = REQUIREMENTS / "telemetry-admission-runtime-py312-macos-arm64.lock"
LINUX_RUNTIME_LOCK = REQUIREMENTS / "telemetry-admission-runtime-py312-linux-arm64.lock"
BUILD_LOCK = REQUIREMENTS / "telemetry-admission-build.lock"
ENTRY_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)==([^ ]+) \\$", re.ASCII)
HASH_PATTERN = re.compile(r"^    --hash=sha256:([0-9a-f]{64})$", re.ASCII)

EXPECTED_RUNTIME_MACOS = {
    "attrs": (
        "26.1.0",
        "c647aa4a12dfbad9333ca4e71fe62ddc36f4e63b2d260a37a8b83d2f043ac309",
    ),
    "jsonschema": (
        "4.26.0",
        "d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce",
    ),
    "jsonschema-specifications": (
        "2025.9.1",
        "98802fee3a11ee76ecaca44429fda8a41bff98b00a0f2838151b113f210cc6fe",
    ),
    "pyyaml": (
        "6.0.3",
        "fc09d0aa354569bc501d4e787133afc08552722d3ab34836a80547331bb5d4a0",
    ),
    "referencing": (
        "0.37.0",
        "381329a9f99628c9069361716891d34ad94af76e461dcb0335825aecc7692231",
    ),
    "rpds-py": (
        "2026.6.3",
        "538949e262e46caa31ac01bdb3c1e8f642622922cacbabbae6a8445d9dc33eaf",
    ),
    "typing-extensions": (
        "4.16.0",
        "481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8",
    ),
}
EXPECTED_RUNTIME_LINUX = {
    **EXPECTED_RUNTIME_MACOS,
    "pyyaml": (
        "6.0.3",
        "9149cad251584d5fb4981be1ecde53a1ca46c891a79788c0df828d2f166bda28",
    ),
    "rpds-py": (
        "2026.6.3",
        "55927d532399c2c646100ff7feb48eaa940ad70f42cd68e1328f3ded9f81ca24",
    ),
}
EXPECTED_BUILD = {
    "build": (
        "1.5.0",
        "13f3eecb844759ab66efec90ca17639bbf14dc06cb2fdf37a9010322d9c50a6f",
    ),
    "packaging": (
        "26.2",
        "5fc45236b9446107ff2415ce77c807cee2862cb6fac22b8a73826d0693b0980e",
    ),
    "pyproject-hooks": (
        "1.2.0",
        "9e5c6bfa8dcc30091c74b0cf803c81fdd29d94f01992a7707bc97babb1141913",
    ),
    "setuptools": (
        "83.0.0",
        "29b23c360f22f414dc7336bb39178cc7bcbf6021ed2733cde173f09dba19abb3",
    ),
    "wheel": (
        "0.47.0",
        "212281cab4dff978f6cedd499cd893e1f620791ca6ff7107cf270781e587eced",
    ),
}


def _normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _parse_lock(path: Path) -> dict[str, tuple[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    entries: dict[str, tuple[str, str]] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line or line.startswith("#"):
            index += 1
            continue
        entry = ENTRY_PATTERN.fullmatch(line)
        if entry is None or index + 1 >= len(lines):
            raise AssertionError(f"invalid lock entry at {path.name}:{index + 1}")
        digest = HASH_PATTERN.fullmatch(lines[index + 1])
        if digest is None:
            raise AssertionError(f"missing exact hash at {path.name}:{index + 2}")
        name = _normalize(entry.group(1))
        if name in entries:
            raise AssertionError(f"duplicate package in {path.name}: {name}")
        entries[name] = (entry.group(2), digest.group(1))
        index += 2
    return entries


class SupplyChainLockTests(unittest.TestCase):
    def test_macos_runtime_lock_is_exact_platform_scoped_transitive_closure(
        self,
    ) -> None:
        self.assertEqual(_parse_lock(MACOS_RUNTIME_LOCK), EXPECTED_RUNTIME_MACOS)
        header = MACOS_RUNTIME_LOCK.read_text(encoding="utf-8")
        self.assertIn("environment=CPython-3.12 macOS-11+-arm64", header)
        self.assertIn("cross_platform_claim=false", header)

    def test_linux_runtime_lock_is_exact_platform_scoped_transitive_closure(
        self,
    ) -> None:
        self.assertEqual(_parse_lock(LINUX_RUNTIME_LOCK), EXPECTED_RUNTIME_LINUX)
        header = LINUX_RUNTIME_LOCK.read_text(encoding="utf-8")
        self.assertIn("environment=CPython-3.12 Linux-glibc-arm64", header)
        self.assertIn(
            "base_image=python:3.12.13-slim-bookworm@sha256:"
            "d50fb7611f86d04a3b0471b46d7557818d88983fc3136726336b2a4c657aa30b",
            header,
        )
        self.assertIn("cross_platform_claim=false", header)

    def test_build_toolchain_is_exact_hash_locked(self) -> None:
        self.assertEqual(_parse_lock(BUILD_LOCK), EXPECTED_BUILD)

    def test_pyproject_pins_backend_and_runtime_roots_match_lock(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["build-system"]["requires"], ["setuptools==83.0.0"])
        dependencies = pyproject["project"]["dependencies"]
        self.assertEqual(set(dependencies), {"jsonschema>=4.18,<5", "PyYAML>=6.0,<7"})
        for runtime_lock in (MACOS_RUNTIME_LOCK, LINUX_RUNTIME_LOCK):
            locked = _parse_lock(runtime_lock)
            self.assertIn("jsonschema", locked)
            self.assertIn("pyyaml", locked)

    def test_documented_install_and_build_paths_fail_closed(self) -> None:
        readme = (REQUIREMENTS / "README.md").read_text(encoding="utf-8")
        self.assertIn("--require-hashes", readme)
        self.assertIn("--only-binary=:all:", readme)
        self.assertIn("--no-deps", readme)
        self.assertIn("SOURCE_DATE_EPOCH=1784678400", readme)
        self.assertIn("--no-isolation", readme)
        self.assertIn("cross-platform equivalence", readme)
        self.assertIn("telemetry-admission-runtime-py312-linux-arm64.lock", readme)
        self.assertIn(
            "python:3.12.13-slim-bookworm@sha256:"
            "d50fb7611f86d04a3b0471b46d7557818d88983fc3136726336b2a4c657aa30b",
            readme,
        )

    def test_source_manifest_binds_platform_locks_and_instructions(self) -> None:
        paths = {entry["path"] for entry in _source_manifest()["entries"]}
        self.assertTrue(
            {
                "requirements/telemetry-admission-build.lock",
                "requirements/telemetry-admission-runtime-py312-linux-arm64.lock",
                "requirements/telemetry-admission-runtime-py312-macos-arm64.lock",
                "requirements/README.md",
            }.issubset(paths)
        )


if __name__ == "__main__":
    unittest.main()
