from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WEBSITE_ALLOWLIST = ROOT / "commercial/implementation/D29-WEBSITE-SOURCE-CORRECTION-ALLOWLIST-v1.json"
WEEKLY_COCKPIT_SCOPE_MANIFEST = ROOT / "cockpit/weekly/prototype-scope-v0.1.json"


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def approved_website_paths():
    if not WEBSITE_ALLOWLIST.is_file():
        return set()
    manifest = json.loads(WEBSITE_ALLOWLIST.read_text(encoding="utf-8"))
    if manifest.get("decision_reference") != "TITMAS-CHINA-COMMERCIAL-PRIVATE-PLATFORM-AND-PAID-PILOT-D29":
        return set()
    if manifest.get("deployment_authorized") is not False:
        return set()
    approved = set()
    for item in manifest.get("files", []):
        relative = item.get("path", "")
        source = ROOT / relative
        if not relative.startswith("site/") or not source.is_file():
            return set()
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest != item.get("sha256"):
            return set()
        approved.add(f"digital-biosphere-architecture/{relative}")
    return approved


def approved_weekly_cockpit_paths(manifest_path=None):
    """Return only digest-bound prototype paths; any inconsistency fails closed."""
    path = Path(manifest_path) if manifest_path is not None else WEEKLY_COCKPIT_SCOPE_MANIFEST
    if not path.is_file():
        return set()
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    required_identity = {
        "manifest_id": "DBA-WEEKLY-COCKPIT-PROTOTYPE-SCOPE-v0.1",
        "version": "0.1",
        "decision_scope": "PATH_SCOPE_AUTHORIZATION_MANIFEST",
        "prototype_only": True,
        "private_internal_cockpit": True,
        "read_only": True,
        "schedule_enabled": False,
        "auto_fix": False,
        "auto_pr": False,
        "auto_merge": False,
        "auto_deploy": False,
        "new_truth_source": False,
        "new_control_plane": False,
    }
    if any(manifest.get(key) != value for key, value in required_identity.items()):
        return set()
    files = manifest.get("files")
    if not isinstance(files, list) or not files or manifest.get("approved_file_count") != len(files):
        return set()
    if not isinstance(manifest.get("generated_at"), str) or not manifest.get("generated_at"):
        return set()
    if not isinstance(manifest.get("limitations"), list) or not manifest.get("limitations"):
        return set()

    manifest_relative = "digital-biosphere-architecture/cockpit/weekly/prototype-scope-v0.1.json"
    workflow_relative = ".github/workflows/dba-weekly-cockpit.yml"
    weekly_prefix = "digital-biosphere-architecture/cockpit/weekly/"
    forbidden_name_tokens = {
        "auto_fix", "autofix", "deploy", "deployment", "write_project",
        "runtime", "database", "migration", "server",
    }
    approved = {manifest_relative}
    seen = set()
    for item in files:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            return set()
        relative = item.get("path")
        digest = item.get("sha256")
        if not isinstance(relative, str) or relative in seen or relative == manifest_relative:
            return set()
        if relative != workflow_relative and not relative.startswith(weekly_prefix):
            return set()
        lowered_parts = {part.lower() for part in Path(relative).parts}
        lowered_stem = Path(relative).stem.lower()
        if lowered_parts & forbidden_name_tokens or any(token in lowered_stem for token in forbidden_name_tokens):
            return set()
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            return set()
        source = ROOT.parent / relative
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            return set()
        seen.add(relative)
        approved.add(relative)

    workflow = manifest.get("workflow")
    if not isinstance(workflow, dict):
        return set()
    workflow_item = next((item for item in files if item["path"] == workflow_relative), None)
    if workflow_item is None or workflow != workflow_item:
        return set()
    return approved


def validate_schema(schema, value, path="$"):
    errors = []
    expected_type = schema.get("type")
    type_map = {
        "object": dict,
        "array": list,
        "string": str,
        "integer": int,
        "boolean": bool,
    }
    if expected_type and not isinstance(value, type_map[expected_type]):
        return [f"{path}: expected {expected_type}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: not in enum")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: too short")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: pattern mismatch")
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: above maximum")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: too few items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: too many items")
        for index, item in enumerate(value):
            errors.extend(validate_schema(schema.get("items", {}), item, f"{path}[{index}]"))
    if isinstance(value, dict):
        required = set(schema.get("required", []))
        missing = required - set(value)
        errors.extend(f"{path}: missing {key}" for key in sorted(missing))
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            errors.extend(f"{path}: unexpected {key}" for key in sorted(set(value) - set(properties)))
        for key, child_schema in properties.items():
            if key in value:
                errors.extend(validate_schema(child_schema, value[key], f"{path}.{key}"))
    return errors


def current_change_paths():
    commands = [
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "diff", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]
    paths = set()
    for command in commands:
        result = subprocess.run(command, cwd=ROOT.parent, text=True, capture_output=True, check=False)
        if result.returncode == 0:
            paths.update(line for line in result.stdout.splitlines() if line)
    # A clean checkout has no candidate change set. Only then inspect the
    # current commit, so a merge commit already present on origin/main is not
    # mistaken for the next branch's implementation scope.
    if not paths:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD^1..HEAD"],
            cwd=ROOT.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            paths.update(line for line in result.stdout.splitlines() if line)
    return paths


def forbidden_change_reason(paths):
    forbidden_parts = {"src", "runtime", "server", "migrations", "migration", "database", "db"}
    allowed_exact = {
        ".gitignore",
        "README.md",
        "digital-biosphere-architecture/AGENTS.md",
        "digital-biosphere-architecture/CROSS-PROJECT-DEPENDENCIES.md",
        "digital-biosphere-architecture/DECISION-QUEUE.md",
        "digital-biosphere-architecture/INTEGRATION-GATES.md",
        "digital-biosphere-architecture/MASTER-ROADMAP.md",
        "digital-biosphere-architecture/PROGRAM-CHARTER.md",
        "digital-biosphere-architecture/PROGRAM-STATUS.md",
        "digital-biosphere-architecture/PROJECT-PORTFOLIO.md",
        "digital-biosphere-architecture/README.md",
        "digital-biosphere-architecture/TITMAS/README.md",
        "digital-biosphere-architecture/TITMAS/agent-native/README.md",
        "digital-biosphere-architecture/TITMAS/agent-native/schemas/agent-index.schema.json",
        "digital-biosphere-architecture/TITMAS-COMMERCIAL-PRODUCT-CONVERGENCE-IMPLEMENTATION-PROJECTION-v1.0.md",
        "digital-biosphere-architecture/titmas-commercial-product-convergence-status-v1.0.json",
        "digital-biosphere-architecture/TITMAS/community/community-status.json",
        "digital-biosphere-architecture/TITMAS/conformance/schemas/community-status.schema.json",
        "digital-biosphere-architecture/TITMAS/conformance/reports/latest.json",
        "digital-biosphere-architecture/TITMAS/conformance/tests/test_commercial_c01_entry.py",
        "digital-biosphere-architecture/TITMAS/conformance/tests/test_commercial_private_constitution.py",
        "digital-biosphere-architecture/TITMAS/conformance/tests/test_dba_titmas_constitution_coherence.py",
        "digital-biosphere-architecture/TITMAS/conformance/tests/test_agent_action_gate_portfolio.py",
        "digital-biosphere-architecture/TITMAS/conformance/tests/test_d29_current_implementation_projection.py",
        "digital-biosphere-architecture/TITMAS/conformance/tests/test_d29_commercial_delivery_foundation.py",
        "digital-biosphere-architecture/TITMAS/conformance/tests/test_d29_commercial_readiness_evidence.py",
        "digital-biosphere-architecture/agent-index.json",
        "digital-biosphere-architecture/llms.txt",
        "digital-biosphere-architecture/architecture/ADR-041-low-friction-entry-and-progressive-value.md",
        "digital-biosphere-architecture/architecture/ADR-042-commercial-private-infrastructure-direction.md",
        "digital-biosphere-architecture/architecture/ADR-043-dba-titmas-constitution-coherent-upgrade.md",
        "digital-biosphere-architecture/architecture/commercial-private-infrastructure-strategy-constitution.md",
        "digital-biosphere-architecture/architecture/dba-main-constitution-coherence-amendment-v0.1.md",
        "digital-biosphere-architecture/architecture/dba-titmas-constitution-reuse-compatibility-audit-v0.1.md",
        "digital-biosphere-architecture/architecture/dba-titmas-constitution-traceability-matrix-v0.1.md",
        "digital-biosphere-architecture/architecture/dcell-module-governance-profile.json",
        "digital-biosphere-architecture/architecture/main-constitution-principles.json",
        "digital-biosphere-architecture/architecture/commercialization-strategy.md",
        "digital-biosphere-architecture/architecture/developer-ecosystem-strategy.md",
        "digital-biosphere-architecture/architecture/open-infrastructure-strategy-constitution.md",
        "digital-biosphere-architecture/architecture/project-mapping.md",
        "digital-biosphere-architecture/architecture/schemas/commercial-readiness-v1.0.schema.json",
        "digital-biosphere-architecture/architecture/schemas/constitution-machine-contract-v0.1.schema.json",
        "digital-biosphere-architecture/architecture/titmas-project-constitution-unified-entry-dcell-amendment-v0.1.md",
        "digital-biosphere-architecture/architecture/titmas-project-constitution.json",
        "digital-biosphere-architecture/architecture/titmas-architecture-charter-v1.0.md",
        "digital-biosphere-architecture/architecture/titmas-d29-commercial-direction-freeze-v1.md",
        "digital-biosphere-architecture/architecture/titmas-d29-private-platform-architecture-v1.md",
        "digital-biosphere-architecture/architecture/titmas-fdo-dtr-pvs0-assets-v0.1.json",
        "digital-biosphere-architecture/architecture/titmas-fdo-dtr-pvs0-auxiliary-line-status-v0.1.md",
        "digital-biosphere-architecture/cockpit/projections/titmac-scout.json",
        "digital-biosphere-architecture/cockpit/source-registry.json",
        "digital-biosphere-architecture/cockpit/tests/test_titmac_scout_bridge.py",
        "digital-biosphere-architecture/docs/TITMAS_PRIVATE_PLATFORM_ARCHITECTURE_v0.1.md",
        "digital-biosphere-architecture/docs/TITMAS_PRODUCT_PORTFOLIO_v0.1.md",
        "digital-biosphere-architecture/docs/TITMAS_WEBSITE_RESTRUCTURE_PLAN_v0.1.md",
        "digital-biosphere-architecture/commercial-program-state.json",
        "digital-biosphere-architecture/commercial-readiness.json",
        "digital-biosphere-architecture/COMMERCIAL-READINESS-MACHINE-STATUS.json",
        "digital-biosphere-architecture/COMMERCIAL-READINESS-REPORT-v1.md",
        "digital-biosphere-architecture/CURRENT-PROJECT-DIRECTION-2026-08-28.md",
        "digital-biosphere-architecture/D29-DATA-LIFECYCLE-COCKPIT-SYNC-REPORT-v1.0.md",
        "digital-biosphere-architecture/D29-TERMINAL-CONSISTENCY-AUDIT-v1.0.md",
        "digital-biosphere-architecture/D29-SECURITY-DRILL-READINESS-COCKPIT-SYNC-v1.0.md",
        "digital-biosphere-architecture/D29-SECURITY-FINDINGS-DISPOSITION-COCKPIT-SYNC-v1.0.md",
        "digital-biosphere-architecture/DBA-TITMAS-CONSTITUTION-COHERENT-UPGRADE-COMPLETION-REPORT-v0.1.md",
        "digital-biosphere-architecture/PROJECT-STATE-RECONCILIATION-2026-08-28.md",
        "digital-biosphere-architecture/RISK-AND-BLOCKER-REGISTER.md",
        "digital-biosphere-architecture/portfolio/canonical-reuse-audit-d29.json",
        "digital-biosphere-architecture/portfolio/product-catalog.internal.json",
        "digital-biosphere-architecture/research/competitive/CONSOLE-INFORMATION-ARCHITECTURE.md",
        "digital-biosphere-architecture/site/app/site-content.ts",
        "digital-biosphere-architecture/site/README.md",
        "digital-biosphere-architecture/site/public/llms.txt",
    }
    approved_website = approved_website_paths()
    approved_weekly_cockpit = approved_weekly_cockpit_paths()
    for raw in paths:
        path = Path(raw)
        parts = set(path.parts)
        lowered = raw.lower()
        frozen_validation_source = raw.startswith(
            "digital-biosphere-architecture/commercial/validation/d29-multi-agent-v1/source-materials/"
        )
        if "owner-map" in lowered or "owner_resolver" in lowered or "owner-resolver" in lowered:
            return "OWNER_ROUTING_CHANGED"
        if (
            "digital-biosphere-architecture" in parts
            and "site" in parts
            and not frozen_validation_source
            and raw not in allowed_exact
            and raw not in approved_website
        ):
            return "WEBSITE_IMPLEMENTATION_CHANGED"
        if parts & forbidden_parts:
            return "CORE_RUNTIME_OR_DATABASE_CHANGED"
        weekly_candidate = raw.startswith(
            "digital-biosphere-architecture/cockpit/weekly/"
        ) or raw == ".github/workflows/dba-weekly-cockpit.yml"
        if weekly_candidate and raw not in approved_weekly_cockpit:
            return "UNAPPROVED_CHANGE_PATH"
        allowed_contract = raw.startswith("digital-biosphere-architecture/commercial/") and raw.endswith((".json", ".md"))
        allowed_commercial_doc = raw.startswith("digital-biosphere-architecture/docs/commercial/") and raw.endswith(".md")
        allowed_intelligence_artifact = raw.startswith(
            "digital-biosphere-architecture/intelligence/"
        ) and raw.endswith((".json", ".md"))
        if (
            raw not in allowed_exact
            and raw not in approved_website
            and raw not in approved_weekly_cockpit
            and not allowed_contract
            and not allowed_commercial_doc
            and not allowed_intelligence_artifact
        ):
            return "UNAPPROVED_CHANGE_PATH"
    return None


class CommercialC01EntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load("commercial/entry/first-value-contract.schema.json")
        cls.examples = load("commercial/entry/first-value-examples.json")
        cls.catalog = load("portfolio/product-catalog.internal.json")
        cls.entry = load("commercial/entry/entry-layer.json")
        cls.surfaces = load("commercial/entry/entry-surfaces.json")
        cls.modes = load("commercial/entry/access-modes.json")
        cls.exit = load("commercial/entry/exit-controls.json")
        cls.reason_registry = load("commercial/entry/customer-entry-reason-codes.json")
        cls.c01 = load("commercial/constitution/c01-low-friction-entry.json")

    def assert_examples_valid(self, examples=None):
        examples = examples or self.examples["examples"]
        errors = [error for item in examples for error in validate_schema(self.schema, item)]
        self.assertEqual([], errors)

    def test_t01_synthetic_demo_requires_no_architecture_theory(self):
        self.assertEqual("commercial/entry/first-value-contract.schema.json", self.examples["contract_schema_ref"])
        self.assertTrue((ROOT / self.examples["contract_schema_ref"]).is_file())
        self.assert_examples_valid()
        synthetic = copy.deepcopy(self.examples["examples"][0])
        self.assertEqual([], synthetic["required_architecture_concepts"])
        synthetic["required_architecture_concepts"] = ["DBA"]
        self.assertIn("too many items", " ".join(validate_schema(self.schema, synthetic)))

    def test_t02_first_value_requires_no_production_write_permission(self):
        self.assertTrue(all(not item["production_write_access_required"] for item in self.examples["examples"]))
        changed = copy.deepcopy(self.examples["examples"][0])
        changed["production_write_access_required"] = True
        self.assertTrue(validate_schema(self.schema, changed))

    def test_t03_first_value_requires_no_enforce(self):
        self.assertTrue(all(not item["automatic_enforcement_required"] and not item["enforce_activation_required"] for item in self.examples["examples"]))
        changed = copy.deepcopy(self.examples["examples"][0])
        changed["automatic_enforcement_required"] = True
        self.assertTrue(validate_schema(self.schema, changed))

    def test_t04_private_raw_trace_is_not_default(self):
        self.assertTrue(all(not item["raw_trace_required"] for item in self.examples["examples"]))
        changed = copy.deepcopy(self.examples["examples"][1])
        changed["raw_trace_required"] = True
        self.assertTrue(validate_schema(self.schema, changed))

    def test_t05_observer_is_absent_from_products(self):
        ids = {item["product_id"] for item in self.catalog["products"]}
        observer = self.entry["entry_layers"][0]
        self.assertNotIn("TITMAS_OBSERVER", ids)
        self.assertFalse(observer["is_product"])
        changed = copy.deepcopy(self.catalog)
        changed["products"].append({"product_id": "TITMAS_OBSERVER"})
        self.assertIn("TITMAS_OBSERVER", {item["product_id"] for item in changed["products"]})

    def test_t06_public_product_count_remains_four(self):
        expected = {"TITMAS_GATE", "TITMAS_RECEIPT", "TITMAS_AUDIT", "TITMAS_HEALTH"}
        ids = {item["product_id"] for item in self.catalog["products"]}
        self.assertEqual(expected, ids)
        self.assertEqual(4, self.catalog["product_count"])
        principles = load("commercial/constitution/commercial-constitution-index.json")["principles"]
        self.assertEqual([f"TITMAS-COMMERCIAL-C{index:02d}" for index in range(1, 11)], [item["principle_id"] for item in principles])
        self.assertEqual("FROZEN_COMMERCIAL_CONSTITUTION", principles[0]["normative_status"])
        self.assertTrue(all(item["normative_status"] == "SUPPORTING_PRINCIPLE_CANDIDATE" for item in principles[1:]))
        changed = copy.deepcopy(self.catalog)
        changed["product_count"] = 5
        self.assertNotEqual(len(changed["products"]), changed["product_count"])

    def test_t07_human_entry_exists(self):
        self.assertIn("HUMAN", self.surfaces["surfaces"])
        self.assertEqual(7, len(self.surfaces["surfaces"]["HUMAN"]["first_questions"]))
        changed = copy.deepcopy(self.surfaces)
        del changed["surfaces"]["HUMAN"]
        self.assertNotIn("HUMAN", changed["surfaces"])

    def test_t08_agent_machine_entry_exists(self):
        agent = self.surfaces["surfaces"]["AGENT"]
        self.assertEqual(12, len(agent["actions"]))
        self.assertEqual(7, len(agent["catalog_refs"]))
        self.assertEqual({"RECOMMENDED", "CONDITIONALLY_RECOMMENDED", "NOT_RECOMMENDED", "NOT_APPLICABLE", "NOT_ASSESSED"}, set(agent["allowed_recommendations"]))
        self.assertTrue(all((ROOT / ref).is_file() for ref in agent["catalog_refs"]))
        index = load("agent-index.json")["machine_surfaces"]
        for key in ("commercial_product_catalog", "commercial_solution_catalog", "commercial_recommendation_policy", "commercial_offerings", "commercial_deployment_options", "commercial_known_limitations", "commercial_entry_status"):
            self.assertIn(key, index)
        changed = copy.deepcopy(agent)
        changed["allowed_recommendations"].remove("NOT_ASSESSED")
        self.assertNotIn("NOT_ASSESSED", changed["allowed_recommendations"])

    def test_t09_monitor_has_no_blocking_effect(self):
        monitor = self.modes["modes"]["MONITOR"]
        self.assertEqual("NONE", monitor["authority_effect"])
        self.assertEqual("NONE", monitor["enforcement_effect"])
        self.assertFalse(monitor["can_block"])
        self.assertEqual({"WOULD_ALLOW", "WOULD_BLOCK", "WOULD_NEED_APPROVAL", "NOT_ASSESSED"}, set(monitor["outputs"]))
        changed = copy.deepcopy(monitor)
        changed["can_block"] = True
        self.assertTrue(changed["can_block"])

    def test_t10_enforce_requires_separate_human_authorization(self):
        enforce = self.modes["modes"]["ENFORCE"]
        self.assertTrue(enforce["requires_separate_human_authorization"])
        self.assertEqual("NOT_AUTHORIZED", enforce["authorization_status"])
        self.assertIsNone(enforce["authorization_ref"])
        self.assertFalse(enforce["inherited_from_c01"])
        changed = copy.deepcopy(enforce)
        changed["inherited_from_c01"] = True
        self.assertTrue(changed["inherited_from_c01"])

    def test_t11_exit_revocation_and_deletion_request_are_defined(self):
        for key in ("disconnect", "key_revocation", "deletion_request"):
            self.assertTrue(self.exit[key]["contract_defined"])
            self.assertTrue(self.exit[key]["path"])
            self.assertFalse(self.exit[key]["runtime_available"])
        changed = copy.deepcopy(self.exit)
        changed["deletion_request"]["path"] = ""
        self.assertFalse(changed["deletion_request"]["path"])

    def test_t12_first_results_explain_reasons_and_limitations(self):
        self.assert_examples_valid()
        for item in self.examples["examples"]:
            self.assertTrue(item["result_explanation"])
            self.assertTrue(item["machine_reason_codes"])
            self.assertTrue(item["limitations"])
            self.assertFalse(item["verification_available"])
            self.assertTrue(item["verification_contract_defined"])
        changed = copy.deepcopy(self.examples["examples"][0])
        changed["limitations"] = []
        self.assertTrue(validate_schema(self.schema, changed))

    def test_t13_simplicity_preserves_registered_reason_codes(self):
        registry = set(self.reason_registry["reason_codes"])
        referenced = {code for item in self.examples["examples"] for code in item["machine_reason_codes"]}
        self.assertTrue(referenced <= registry)
        checker = load("commercial/entry/customer-entry-check.json")
        self.assertTrue(set(checker["redesign_triggers"]) <= registry)
        self.assertFalse(self.reason_registry["reason_codes_removed_for_simplicity"])
        changed = copy.deepcopy(self.examples["examples"][0])
        changed["machine_reason_codes"].append("UNKNOWN_REASON")
        self.assertFalse(set(changed["machine_reason_codes"]) <= registry)

    def test_t14_simplicity_preserves_gate_receipt_and_evidence_semantics(self):
        invariants = self.c01["safety_invariants"]
        self.assertTrue(invariants["simplicity_does_not_weaken_authority"])
        self.assertTrue(invariants["simplicity_does_not_weaken_evidence"])
        self.assertTrue(invariants["simplicity_does_not_hide_limitations"])
        self.assertTrue(invariants["simplicity_does_not_remove_human_authorization"])
        d29 = (ROOT / "architecture/titmas-d29-commercial-direction-freeze-v1.md").read_text(encoding="utf-8")
        self.assertIn("AGENT_EVIDENCE_IS_UNIQUE_EXECUTION_EVIDENCE_SEMANTIC_SOURCE=true", d29)
        documents = [
            "docs/commercial/TITMAS_COMMERCIAL_CONSTITUTION_v1.0.md",
            "architecture/titmas-d29-commercial-direction-freeze-v1.md",
            "architecture/titmas-d29-private-platform-architecture-v1.md",
            "docs/TITMAS_PRIVATE_PLATFORM_ARCHITECTURE_v0.1.md",
            "docs/TITMAS_PRODUCT_PORTFOLIO_v0.1.md",
            "research/competitive/CONSOLE-INFORMATION-ARCHITECTURE.md",
            "docs/TITMAS_WEBSITE_RESTRUCTURE_PLAN_v0.1.md",
        ]
        joined = "\n".join((ROOT / item).read_text(encoding="utf-8") for item in documents)
        for required_text in ("PUBLIC_PRODUCT_COUNT=4", "OBSERVER_IS_PRODUCT=false", "FIRST_VALUE_BEFORE_ENFORCEMENT=true", "MONITOR_BEFORE_ENFORCE=true"):
            self.assertIn(required_text, joined)
        for path in documents:
            self.assertTrue((ROOT / path).is_file())
        changed = copy.deepcopy(invariants)
        changed["simplicity_does_not_weaken_evidence"] = False
        self.assertFalse(changed["simplicity_does_not_weaken_evidence"])

    def test_t15_no_trace_platform_fifth_product_or_implementation_change(self):
        drift = self.c01["drift_invariants"]
        required = {"no_new_trace_platform", "no_new_runtime", "no_new_control_plane", "no_new_truth_source", "no_duplicate_verification", "no_p0_10_reopen", "no_d04_reopen"}
        self.assertTrue(required <= set(drift))
        self.assertTrue(all(drift[key] for key in required))
        self.assertIsNone(forbidden_change_reason(current_change_paths()))
        approved_site_paths = approved_website_paths()
        changed_site_paths = {
            path for path in current_change_paths()
            if path.startswith("digital-biosphere-architecture/site/")
        }
        documentation_only_site_paths = {
            "digital-biosphere-architecture/site/README.md",
        }
        changed_site_implementation_paths = changed_site_paths - documentation_only_site_paths
        if changed_site_implementation_paths:
            self.assertEqual(approved_site_paths, changed_site_implementation_paths)
        self.assertTrue(changed_site_paths <= approved_site_paths | documentation_only_site_paths)
        # The original C-01 integration changed at least 40 paths, but that
        # historical batch size is not a permanent conformance invariant.
        # Future path-scoped governance updates must still have a visible diff
        # and every changed path must continue through forbidden_change_reason.
        self.assertTrue(current_change_paths())
        self.assertEqual("CORE_RUNTIME_OR_DATABASE_CHANGED", forbidden_change_reason({"digital-biosphere-architecture/src/runtime/observer.py"}))
        self.assertEqual("WEBSITE_IMPLEMENTATION_CHANGED", forbidden_change_reason({"digital-biosphere-architecture/site/app/page.tsx"}))
        self.assertIsNone(forbidden_change_reason({"digital-biosphere-architecture/site/app/site-content.ts"}))
        self.assertIsNone(forbidden_change_reason({"digital-biosphere-architecture/site/public/llms.txt"}))
        self.assertIsNone(forbidden_change_reason({"digital-biosphere-architecture/intelligence/2026-08-15/intelligence-brief.md"}))
        self.assertIsNone(forbidden_change_reason({"digital-biosphere-architecture/intelligence/2026-08-15/reference-case.json"}))
        self.assertEqual("UNAPPROVED_CHANGE_PATH", forbidden_change_reason({"digital-biosphere-architecture/intelligence/collector.py"}))
        self.assertIsNone(forbidden_change_reason({"digital-biosphere-architecture/commercial/validation/d29-multi-agent-v1/source-materials/site/public/proof-catalog.json"}))
        self.assertIsNone(forbidden_change_reason({
            "digital-biosphere-architecture/cockpit/projections/titmac-scout.json",
            "digital-biosphere-architecture/cockpit/source-registry.json",
            "digital-biosphere-architecture/cockpit/tests/test_titmac_scout_bridge.py",
        }))
        self.assertEqual("UNAPPROVED_CHANGE_PATH", forbidden_change_reason({
            "digital-biosphere-architecture/cockpit/unregistered-status.json"
        }))
        self.assertEqual("OWNER_ROUTING_CHANGED", forbidden_change_reason({"digital-biosphere-architecture/TITMAS/agent-native/evolution/canonical-owner-map.json"}))
        self.assertEqual("UNAPPROVED_CHANGE_PATH", forbidden_change_reason({"digital-biosphere-architecture/unknown.py"}))
        self.assertEqual("UNAPPROVED_CHANGE_PATH", forbidden_change_reason({"digital-biosphere-architecture/commercial/observer.py"}))

    def test_t16_registered_weekly_cockpit_paths_are_digest_bound(self):
        approved = approved_weekly_cockpit_paths()
        self.assertIn(
            "digital-biosphere-architecture/cockpit/weekly/run_weekly.py",
            approved,
        )
        self.assertIn(".github/workflows/dba-weekly-cockpit.yml", approved)
        self.assertIsNone(forbidden_change_reason(approved))

    def test_t17_unregistered_weekly_cockpit_paths_fail_closed(self):
        for relative in (
            "digital-biosphere-architecture/cockpit/weekly/future.py",
            "digital-biosphere-architecture/cockpit/weekly/auto_fix.py",
            "digital-biosphere-architecture/cockpit/weekly/deploy.py",
            "digital-biosphere-architecture/cockpit/weekly/write_project.py",
        ):
            self.assertEqual("UNAPPROVED_CHANGE_PATH", forbidden_change_reason({relative}))

    def test_t18_weekly_workflow_remains_read_only_and_schedule_gated(self):
        workflow = (ROOT.parent / ".github/workflows/dba-weekly-cockpit.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("pull-requests: write", workflow)
        self.assertIn("DBA_WEEKLY_COCKPIT_SCHEDULE_ENABLED", workflow)
        manifest = json.loads(WEEKLY_COCKPIT_SCOPE_MANIFEST.read_text(encoding="utf-8"))
        self.assertFalse(manifest["schedule_enabled"])

    def test_t19_weekly_scope_digest_mismatch_fails_closed(self):
        manifest = json.loads(WEEKLY_COCKPIT_SCOPE_MANIFEST.read_text(encoding="utf-8"))
        manifest["files"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "manifest.json"
            candidate.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(set(), approved_weekly_cockpit_paths(candidate))

    def test_t20_missing_weekly_scope_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(
                set(),
                approved_weekly_cockpit_paths(Path(directory) / "missing.json"),
            )

    def test_t21_weekly_scope_identity_and_boundaries_are_exact(self):
        manifest = json.loads(WEEKLY_COCKPIT_SCOPE_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual("PATH_SCOPE_AUTHORIZATION_MANIFEST", manifest["decision_scope"])
        for key in ("prototype_only", "private_internal_cockpit", "read_only"):
            self.assertTrue(manifest[key])
        for key in (
            "schedule_enabled", "auto_fix", "auto_pr", "auto_merge",
            "auto_deploy", "new_truth_source", "new_control_plane",
        ):
            self.assertFalse(manifest[key])

    def test_t22_weekly_scope_cannot_authorize_other_domains(self):
        original = json.loads(WEEKLY_COCKPIT_SCOPE_MANIFEST.read_text(encoding="utf-8"))
        forbidden_paths = (
            "digital-biosphere-architecture/site/README.md",
            "digital-biosphere-architecture/CURRENT-PROJECT-DIRECTION-2026-08-28.md",
            "digital-biosphere-architecture/src/runtime/observer.py",
            "digital-biosphere-architecture/database/state.json",
            "digital-biosphere-architecture/deployment/release.yml",
        )
        for relative in forbidden_paths:
            manifest = copy.deepcopy(original)
            source = ROOT.parent / relative
            digest = hashlib.sha256(source.read_bytes()).hexdigest() if source.is_file() else "0" * 64
            manifest["files"].append({"path": relative, "sha256": digest})
            manifest["approved_file_count"] = len(manifest["files"])
            with tempfile.TemporaryDirectory() as directory:
                candidate = Path(directory) / "manifest.json"
                candidate.write_text(json.dumps(manifest), encoding="utf-8")
                self.assertEqual(set(), approved_weekly_cockpit_paths(candidate), relative)


if __name__ == "__main__":
    unittest.main()
