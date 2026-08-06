"""Read-only DBOS Object Schema Validator v0.1.

The validator performs offline JSON Schema Draft 2020-12 validation followed
by local DBOS governance and reference-consistency checks. It never repairs,
registers, authorizes, executes, activates, or verifies the supplied object.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Iterator, Mapping
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError
from referencing import Registry, Resource

from validator.governance_constraint_validator import (
    validate_governance_constraints,
    validate_schema_boundaries,
)
from validator.reference_consistency_validator import validate_reference_consistency
from validator.validation_result_model import (
    VALIDATOR_VERSION,
    SchemaReference,
    ValidationIssue,
    ValidationResult,
    ValidationStatus,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_DIRECTORY = REPOSITORY_ROOT / "schemas"
SUPPORTED_OBJECT_VERSION = "v0.1"

SCHEMA_FILES = (
    "common-object-schema.yaml",
    "entity-object-schema.yaml",
    "capability-object-schema.yaml",
    "execution-object-schema.yaml",
    "evidence-reference-object-schema.yaml",
    "verification-object-schema.yaml",
)

SCHEMA_ID_BY_OBJECT_TYPE = {
    "ENTITY": "dbio://schema/entity-object/v0.1",
    "CAPABILITY": "dbio://schema/capability-object/v0.1",
    "EXECUTION": "dbio://schema/execution-object/v0.1",
    "EVIDENCE_REFERENCE": "dbio://schema/evidence-reference-object/v0.1",
    "VERIFICATION": "dbio://schema/verification-object/v0.1",
}

TYPE_SPECIFIC_ID = {
    "ENTITY": "entity_id",
    "CAPABILITY": "capability_id",
    "EXECUTION": "execution_id",
    "EVIDENCE_REFERENCE": "evidence_id",
    "VERIFICATION": "verification_id",
}

UNKNOWN_VALUE_FIELDS = frozenset(
    {
        "entity_type",
        "integrity_status",
        "lifecycle_state",
        "status",
        "verification_status",
        "verification_type",
    }
)


class SchemaRegistryError(RuntimeError):
    """Raised when the local schema set cannot be loaded safely."""


def _safe_target_reference(target: Any) -> str | None:
    if not isinstance(target, Mapping):
        return None
    value = target.get("object_id")
    return value if isinstance(value, str) and value else None


def _issue_sort_key(issue: ValidationIssue) -> tuple[str, str, str]:
    return issue.path, issue.code, issue.rule


def _json_path(error: ValidationError) -> str:
    path = "$"
    for component in error.absolute_path:
        if isinstance(component, int):
            path += f"[{component}]"
        else:
            path += f".{component}"
    return path


def _schema_error_to_issue(error: ValidationError) -> ValidationIssue:
    path = _json_path(error)
    code = (
        "VERSION_MISMATCH"
        if path == "$.version" and error.validator == "const"
        else "INVALID"
    )
    return ValidationIssue(
        code=code,
        path=path,
        message=f"JSON Schema constraint failed: {error.validator}.",
        rule=f"json_schema_{error.validator}",
    )


def _allowed_top_level_fields(
    schema: Mapping[str, Any], common_schema: Mapping[str, Any]
) -> frozenset[str]:
    common_properties = common_schema.get("properties", {})
    common_keys = common_properties if isinstance(common_properties, Mapping) else {}
    type_properties: Mapping[str, Any] = {}
    all_of = schema.get("allOf")
    if isinstance(all_of, list) and len(all_of) > 1 and isinstance(all_of[1], Mapping):
        candidate = all_of[1].get("properties", {})
        if isinstance(candidate, Mapping):
            type_properties = candidate
    return frozenset(
        {
            *(str(key) for key in common_keys),
            *(str(key) for key in type_properties),
        }
    )


def _is_redundant_unevaluated_error(
    error: ValidationError,
    target: Mapping[str, Any],
    schema: Mapping[str, Any],
    common_schema: Mapping[str, Any],
) -> bool:
    """Suppress composition fallout while retaining genuine unknown fields."""

    if error.validator != "unevaluatedProperties" or error.absolute_path:
        return False
    return set(target).issubset(_allowed_top_level_fields(schema, common_schema))


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _check_id_consistency(
    target: Mapping[str, Any], object_type: Any
) -> Iterator[ValidationIssue]:
    id_field = TYPE_SPECIFIC_ID.get(str(object_type))
    if (
        id_field
        and id_field in target
        and target.get("object_id") != target.get(id_field)
    ):
        yield ValidationIssue(
            code="CONFLICT",
            path=f"$.{id_field}",
            message="The type-specific identifier conflicts with object_id.",
            rule="object_id_equals_type_specific_id",
        )


def _check_timestamp_ordering(target: Mapping[str, Any]) -> Iterator[ValidationIssue]:
    created_at = _parse_timestamp(target.get("created_at"))
    updated_at = _parse_timestamp(target.get("updated_at"))
    if created_at is not None and updated_at is not None and updated_at < created_at:
        yield ValidationIssue(
            code="INVALID",
            path="$.updated_at",
            message="updated_at cannot be earlier than created_at.",
            rule="updated_at_not_before_created_at",
        )


def _check_limitations(target: Mapping[str, Any]) -> Iterator[ValidationIssue]:
    limitations = target.get("limitations")
    if isinstance(limitations, list) and not limitations:
        yield ValidationIssue(
            code="UNKNOWN",
            path="$.limitations",
            message="An empty limitations list lacks attributable support in local validation.",
            rule="empty_limitations_require_attributed_source_assertion",
        )


def _check_entity_lifecycle_state(
    target: Mapping[str, Any], object_type: Any
) -> Iterator[ValidationIssue]:
    if object_type == "ENTITY" and target.get("lifecycle_state") in {
        "ACTIVE",
        "VERIFIED",
        "EVALUATED",
        "ADAPTED",
    }:
        yield ValidationIssue(
            code="UNKNOWN",
            path="$.lifecycle_state",
            message="An elevated lifecycle claim requires external lifecycle evidence.",
            rule="active_is_source_assertion_only",
        )


def _check_verification_invariants(
    target: Mapping[str, Any], object_type: Any
) -> Iterator[ValidationIssue]:
    if object_type == "VERIFICATION" and target.get("verification_status") in {
        "PASS",
        "FAIL",
        "INCONCLUSIVE",
        "REVOKED",
    }:
        yield ValidationIssue(
            code="UNKNOWN",
            path="$.verification_status",
            message="A non-pending result requires an external verification record.",
            rule="non_pending_results_require_resolvable_verification_record",
        )
    if (
        object_type == "VERIFICATION"
        and target.get("verification_type") == "INDEPENDENT_VERIFICATION"
    ):
        yield ValidationIssue(
            code="UNKNOWN",
            path="$.verification_type",
            message="Independent verification requires external independence evidence.",
            rule="independent_type_requires_independence_evidence",
        )


def _semantic_invariant_issues(
    target: Mapping[str, Any],
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    object_type = target.get("object_type")

    issues.extend(_check_id_consistency(target, object_type))
    issues.extend(_check_timestamp_ordering(target))
    issues.extend(_check_limitations(target))
    issues.extend(_check_entity_lifecycle_state(target, object_type))
    issues.extend(_check_verification_invariants(target, object_type))

    return tuple(issues)


def _unknown_value_issues(value: Any, path: str = "$") -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in UNKNOWN_VALUE_FIELDS and child == "UNKNOWN":
                issues.append(
                    ValidationIssue(
                        code="UNKNOWN",
                        path=child_path,
                        message="The controlled value remains explicitly unknown.",
                        rule="unknown_remains_unknown",
                    )
                )
            if key == "limitations" and isinstance(child, list) and "UNKNOWN" in child:
                issues.append(
                    ValidationIssue(
                        code="UNKNOWN",
                        path=child_path,
                        message="The limitations surface declares unresolved information.",
                        rule="unknown_limitation_remains_unknown",
                    )
                )
            issues.extend(_unknown_value_issues(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            issues.extend(_unknown_value_issues(child, f"{path}[{index}]"))
    return tuple(issues)


def _classify(issues: tuple[ValidationIssue, ...]) -> ValidationStatus:
    codes = {issue.code for issue in issues}
    if "INVALID" in codes:
        return ValidationStatus.FAIL
    if "VERSION_MISMATCH" in codes:
        return ValidationStatus.VERSION_MISMATCH
    if "CONFLICT" in codes:
        return ValidationStatus.CONFLICT
    if codes:
        return ValidationStatus.UNKNOWN
    return ValidationStatus.PASS


class ObjectSchemaValidator:
    """Offline, deterministic validator for the five DBOS v0.1 object types."""

    def __init__(self, schema_directory: Path | str = DEFAULT_SCHEMA_DIRECTORY) -> None:
        self.schema_directory = Path(schema_directory)
        self._schemas, self._schema_digests = self._load_schemas()
        resources = [
            (schema_id, Resource.from_contents(schema))
            for schema_id, schema in self._schemas.items()
        ]
        self._registry = Registry().with_resources(resources)
        self._validators = {
            schema_id: Draft202012Validator(
                schema,
                registry=self._registry,
                format_checker=FormatChecker(),
            )
            for schema_id, schema in self._schemas.items()
            if schema_id != "dbio://schema/common-object/v0.1"
        }

    def _load_schemas(self) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
        schemas: dict[str, dict[str, Any]] = {}
        digests: dict[str, str] = {}
        for filename in SCHEMA_FILES:
            path = self.schema_directory / filename
            try:
                raw_schema = path.read_bytes()
                schema = json.loads(raw_schema.decode("utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise SchemaRegistryError(
                    f"Cannot load local schema: {filename}"
                ) from exc
            if not isinstance(schema, dict) or not isinstance(schema.get("$id"), str):
                raise SchemaRegistryError(f"Schema has no stable $id: {filename}")
            schema_id = schema["$id"]
            if schema_id in schemas:
                raise SchemaRegistryError(f"Duplicate local schema $id: {schema_id}")
            try:
                Draft202012Validator.check_schema(schema)
            except SchemaError as exc:
                raise SchemaRegistryError(f"Invalid local schema: {filename}") from exc
            boundary_issues = validate_schema_boundaries(schema)
            if boundary_issues:
                raise SchemaRegistryError(f"Unsafe local schema boundaries: {filename}")
            schemas[schema_id] = schema
            digests[schema_id] = f"sha256:{hashlib.sha256(raw_schema).hexdigest()}"

        expected_ids = {
            "dbio://schema/common-object/v0.1",
            *SCHEMA_ID_BY_OBJECT_TYPE.values(),
        }
        if set(schemas) != expected_ids:
            raise SchemaRegistryError(
                "The local DBOS v0.1 schema set is incomplete or unexpected."
            )
        return schemas, digests

    def validate(
        self, target: Mapping[str, Any] | Any, *, schema_id: str | None = None
    ) -> ValidationResult:
        """Validate without mutating the target or resolving any external source."""

        target_reference = _safe_target_reference(target)
        if not isinstance(target, Mapping):
            issue = ValidationIssue(
                code="INVALID",
                path="$",
                message="The validation target must be a JSON object.",
                rule="target_is_object",
            )
            return ValidationResult(
                validator_version=VALIDATOR_VERSION,
                target_reference=target_reference,
                result=ValidationStatus.FAIL,
                errors=(issue,),
            )

        object_type = target.get("object_type")
        expected_schema_id = SCHEMA_ID_BY_OBJECT_TYPE.get(str(object_type))
        if expected_schema_id is None:
            issue = ValidationIssue(
                code="INVALID",
                path="$.object_type",
                message="The object_type does not select a DBOS v0.1 core object schema.",
                rule="core_object_type_allowlist",
            )
            return ValidationResult(
                validator_version=VALIDATOR_VERSION,
                target_reference=target_reference,
                result=ValidationStatus.FAIL,
                errors=(issue,),
            )

        selected_schema_id = schema_id or expected_schema_id
        if selected_schema_id not in self._validators:
            issue = ValidationIssue(
                code="UNKNOWN",
                path="$schema",
                message="The explicitly selected schema is not present in the offline registry.",
                rule="offline_schema_registry",
            )
            return ValidationResult(
                validator_version=VALIDATOR_VERSION,
                target_reference=target_reference,
                result=ValidationStatus.UNKNOWN,
                errors=(issue,),
                schema_reference=SchemaReference(selected_schema_id, None),
            )
        if selected_schema_id != expected_schema_id:
            issue = ValidationIssue(
                code="CONFLICT",
                path="$schema",
                message="The selected schema conflicts with object_type.",
                rule="schema_object_type_consistency",
            )
            return ValidationResult(
                validator_version=VALIDATOR_VERSION,
                target_reference=target_reference,
                result=ValidationStatus.CONFLICT,
                errors=(issue,),
                schema_reference=SchemaReference(
                    selected_schema_id,
                    self._schema_digests[selected_schema_id],
                ),
            )

        schema = self._schemas[selected_schema_id]
        common_schema = self._schemas["dbio://schema/common-object/v0.1"]
        issues: list[ValidationIssue] = []
        for error in self._validators[selected_schema_id].iter_errors(target):
            if _is_redundant_unevaluated_error(error, target, schema, common_schema):
                continue
            issues.append(_schema_error_to_issue(error))
        issues.extend(validate_governance_constraints(target, schema))
        issues.extend(validate_reference_consistency(target))
        issues.extend(_semantic_invariant_issues(target))
        issues.extend(_unknown_value_issues(target))

        if "version" in target and target.get("version") != SUPPORTED_OBJECT_VERSION:
            issues.append(
                ValidationIssue(
                    code="VERSION_MISMATCH",
                    path="$.version",
                    message="The object representation version is not supported by this validator.",
                    rule="object_contract_version_v0_1",
                )
            )

        deduplicated = {(issue.code, issue.path, issue.rule): issue for issue in issues}
        ordered = tuple(sorted(deduplicated.values(), key=_issue_sort_key))
        return ValidationResult(
            validator_version=VALIDATOR_VERSION,
            target_reference=target_reference,
            result=_classify(ordered),
            errors=ordered,
            schema_reference=SchemaReference(
                selected_schema_id,
                self._schema_digests[selected_schema_id],
            ),
        )


@lru_cache(maxsize=1)
def _default_validator() -> ObjectSchemaValidator:
    return ObjectSchemaValidator()


def validate_object(
    target: Mapping[str, Any] | Any, *, schema_id: str | None = None
) -> ValidationResult:
    """Convenience entry point for deterministic local validation."""

    return _default_validator().validate(target, schema_id=schema_id)


def main(argv: list[str] | None = None) -> int:
    """Read one JSON file, print a diagnostic envelope, and never rewrite it."""

    parser = argparse.ArgumentParser(
        description="Validate one DBOS v0.1 object JSON file."
    )
    parser.add_argument("object_file", type=Path)
    parser.add_argument("--schema-id", default=None)
    args = parser.parse_args(argv)

    try:
        target = json.loads(args.object_file.read_text(encoding="utf-8"))
        result = validate_object(target, schema_id=args.schema_id)
    except (OSError, UnicodeError, json.JSONDecodeError):
        issue = ValidationIssue(
            code="INVALID",
            path="$",
            message="The input file could not be read as JSON.",
            rule="input_json_parse",
        )
        result = ValidationResult(
            validator_version=VALIDATOR_VERSION,
            target_reference=None,
            result=ValidationStatus.FAIL,
            errors=(issue,),
        )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
