#!/usr/bin/env python3
"""Authorized DBOS-EXP-0001 Runner with digest-locked auxiliary evidence.

The frozen archive contains constitution, registry, validation, and execution
inputs. Phase-aware validation also needs the separately retained subject and
environment evidence that those registries reference. This wrapper mounts only
the exact allowlisted evidence files into the temporary extracted validation
root, records their real digests, and delegates the experiment procedure to the
deterministic base implementation.

It does not modify the frozen archive, create an Agent or Runtime, grant a
permission, access an external repository, or select any unregistered step.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import dbos_exp_0001 as base

AUXILIARY_INPUTS = (
    "README.md",
    "reports/DBOS-EXP-0001-CURRENT_STATE_REPORT.md",
    "evidence/experiments/DBOS-EXP-0001/identity/subject-identity-evidence.json",
    "evidence/experiments/DBOS-EXP-0001/environment/environment-observation.json",
    "evidence/experiments/DBOS-EXP-0001/environment/environment-observation.receipt.json",
    "evolution/evolution-ledger.yaml",
    "schemas/project-manifest.schema.yaml",
)
VALIDATOR_OVERRIDES = (
    "validation/capture_readiness_validator.py",
    "validation/environment_validator.py",
    "validation/snapshot_capture_validator.py",
)


def auxiliary_manifest(root: Path) -> dict[str, Any]:
    artifacts = []
    for relative in AUXILIARY_INPUTS:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"required auxiliary input missing or unsafe: {relative}")
        artifacts.append({"path": relative, "digest": base.sha256_file(path), "size": path.stat().st_size})
    overrides = []
    for relative in VALIDATOR_OVERRIDES:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"required validator override missing or unsafe: {relative}")
        overrides.append({"path": relative, "digest": base.sha256_file(path), "size": path.stat().st_size, "reason": "relocation-safe successor for frozen absolute-root baseline check"})
    return {
        "schema_version": "0.1",
        "kind": "DBOSExperimentAuxiliaryInputManifest",
        "experiment_id": base.EXPERIMENT_ID,
        "mount_mode": "temporary_read_only_validation_input",
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "validator_overrides": overrides,
        "validator_override_count": len(overrides),
        "frozen_archive_modified": False,
        "external_repository_access": False,
        "sensitive_data_access": False,
        "authority_effect": "none",
    }


def prepare_validator_manifest(root: Path, source: Path, output: Path) -> dict[str, Any]:
    manifest = base.load_json(source)
    replacements = {item["path"]: item for item in auxiliary_manifest(root)["validator_overrides"]}
    validators = manifest.get("validators")
    if not isinstance(validators, list) or not validators:
        raise ValueError("source validator manifest is empty")
    replaced = 0
    for item in validators:
        replacement = replacements.get(item.get("path"))
        if replacement:
            item["digest"] = replacement["digest"]
            item["size"] = replacement["size"]
            item["successor_reason"] = replacement["reason"]
            replaced += 1
    if replaced != len(replacements):
        raise ValueError("validator override is not present in source manifest")
    manifest["kind"] = "DBOSExperimentValidatorManifestSuccessor"
    manifest["supersedes"] = str(source)
    manifest["prepared_at"] = base.timestamp_now()
    manifest["validator_override_count"] = replaced
    base.write_json(output, manifest)
    return {"status": "PASS", "output": str(output), "digest": base.sha256_file(output), "validator_count": manifest.get("validator_count"), "validator_override_count": replaced}


def install_mounts(root: Path, extraction_root: Path, manifest: dict[str, Any], validator_manifest: dict[str, Any]) -> None:
    for item in manifest["artifacts"] + manifest["validator_overrides"]:
        source = root / item["path"]
        target = extraction_root / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if base.sha256_file(target) != item["digest"] or target.stat().st_size != item["size"]:
            raise ValueError(f"auxiliary mount mismatch: {item['path']}")
    expected = {item["path"]: item["digest"] for item in validator_manifest.get("validators", [])}
    for relative in validator_manifest.get("execution_order", []):
        path = extraction_root / relative
        if relative not in expected or not path.is_file() or base.sha256_file(path) != expected[relative]:
            raise ValueError(f"validator manifest digest mismatch after mount: {relative}")


def preflight(root: Path, snapshot_dir: Path, output_dir: Path) -> dict[str, Any]:
    root = root.resolve()
    manifest = auxiliary_manifest(root)
    base.write_json(output_dir / "auxiliary-input-manifest.json", manifest)
    with tempfile.TemporaryDirectory(prefix="dbos-exp-0001-preflight-") as temporary:
        extraction_root = Path(temporary) / "frozen-dbos"
        extraction_root.mkdir()
        _, validator_manifest = base.verify_frozen_snapshot(snapshot_dir, extraction_root)
        install_mounts(root, extraction_root, manifest, validator_manifest)
        results = base.run_validators(extraction_root, validator_manifest)
    result = {
        "schema_version": "0.1",
        "kind": "DBOSExperimentRunnerPreflight",
        "experiment_id": base.EXPERIMENT_ID,
        "timestamp": base.timestamp_now(),
        "validator_count_expected": validator_manifest["validator_count"],
        "validator_count_executed": len(results),
        "pass_count": sum(item["status"] == "PASS" for item in results),
        "fail_count": sum(item["status"] == "FAIL" for item in results),
        "results": results,
    }
    result["status"] = "PASS" if result["fail_count"] == 0 and result["validator_count_executed"] == result["validator_count_expected"] else "FAIL"
    base.write_json(output_dir / "preflight-results.json", result)
    return result


def run(root: Path, snapshot_dir: Path, authorization: Path, output_dir: Path) -> dict[str, Any]:
    root = root.resolve()
    manifest = auxiliary_manifest(root)
    base.write_json(output_dir / "auxiliary-input-manifest.json", manifest)
    original_verify = base.verify_frozen_snapshot
    original_execution_id = base.EXECUTION_ID
    original_authorization_id = base.AUTHORIZATION_ID
    original_executor_authorization_id = base.EXECUTOR_AUTHORIZATION_ID
    base.EXECUTION_ID = "dbio:runner-execution:dbos-self-validation:DBOS-EXP-0001:0002"
    base.AUTHORIZATION_ID = "DBOS-EXP-0001-AUTH-0002"
    base.EXECUTOR_AUTHORIZATION_ID = "DBOS-EXP-0001-EXECUTOR-AUTH-0002"

    def verify_with_auxiliary_mount(snapshot: Path, extraction_root: Path):
        result = original_verify(snapshot, extraction_root)
        install_mounts(root, extraction_root, manifest, result[1])
        return result

    base.verify_frozen_snapshot = verify_with_auxiliary_mount
    try:
        return base.run_experiment(root, snapshot_dir, authorization, output_dir)
    finally:
        base.verify_frozen_snapshot = original_verify
        base.EXECUTION_ID = original_execution_id
        base.AUTHORIZATION_ID = original_authorization_id
        base.EXECUTOR_AUTHORIZATION_ID = original_executor_authorization_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare-validator-manifest")
    prepare.add_argument("--source", type=Path, required=True)
    prepare.add_argument("--output", type=Path, required=True)
    preflight_parser = commands.add_parser("preflight")
    preflight_parser.add_argument("--snapshot-dir", type=Path, required=True)
    preflight_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--snapshot-dir", type=Path, required=True)
    run_parser.add_argument("--authorization", type=Path, required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare-validator-manifest":
            result = prepare_validator_manifest(args.root.resolve(), args.source, args.output)
        elif args.command == "preflight":
            result = preflight(args.root, args.snapshot_dir, args.output_dir)
        else:
            result = run(args.root, args.snapshot_dir, args.authorization, args.output_dir)
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED", "error_type": type(exc).__name__, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
