from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


WEEKLY = Path(__file__).resolve().parents[2]
DBA = WEEKLY.parents[1]
REPOSITORY = WEEKLY.parents[2]
sys.path.insert(0, str(WEEKLY))

from cells.evidence_admission import EvidenceAdmissionCell
from cells.handoff import HandoffCell
from cells.human_view import HumanViewCell
from coordinator import WeeklyCoordinator
from discovery.artifact_memory import CapabilityArtifactMemory
from discovery.deduplication import deduplicate_candidates
from discovery.fingerprint import candidate_fingerprint, registry_digest
from discovery.identity import normalized_name
from discovery.pipeline import build_capability_discovery_context
from discovery.reference_absorption import build_reference_registry


OBSERVED = "2026-08-29T09:00:00+00:00"
DIGEST = "a" * 64


class FakeMemory:
    def __init__(self, registry=None, rejected=False):
        self.registry = registry
        self.rejected = rejected

    def load_previous(self, repository, workflow, current_run_id, observed_at):
        return {
            "status": (
                "PREVIOUS_CAPABILITY_ARTIFACT_AVAILABLE"
                if self.registry
                else "PREVIOUS_ARTIFACT_REJECTED"
                if self.rejected
                else "NO_PREVIOUS_CAPABILITY_ARTIFACT"
            ),
            "previous_registry": self.registry,
            "previous_registry_loaded": self.registry is not None,
            "previous_artifact_rejected": self.rejected,
            "memory_bootstrap_source": (
                "PREVIOUS_SUCCESSFUL_MAIN_ARTIFACT"
                if self.registry
                else "DCDAT_001_BASELINE"
            ),
        }


class FakeArxiv:
    def __init__(self, records=None, status="AVAILABLE"):
        self.records = records or []
        self.status = status

    def fetch_ids(self, identifiers, observed_at):
        return self._batch("ARXIV_REGISTERED", observed_at, [])

    def search(self, query, max_results, observed_at):
        return self._batch("ARXIV", observed_at, self.records[:max_results])

    def _batch(self, source, observed_at, records):
        return {
            "status": self.status,
            "records": records if self.status == "AVAILABLE" else [],
            "evidence": {
                "source": source,
                "method": "GET",
                "observed_at": observed_at,
                "source_digest_sha256": DIGEST,
                "partial_payload_used": False,
            },
        }


class FakeGithub:
    def __init__(self, records=None, status="AVAILABLE"):
        self.records = records or []
        self.status = status

    def observe_repositories(self, repositories, observed_at):
        return self._batch("GITHUB_REGISTERED", observed_at, [])

    def search(self, query, max_results, observed_at):
        return self._batch("GITHUB_PUBLIC_SEARCH", observed_at, self.records[:max_results])

    def _batch(self, source, observed_at, records):
        return {
            "status": self.status,
            "records": records if self.status == "AVAILABLE" else [],
            "evidence": [{
                "source": source,
                "method": "GET",
                "observed_at": observed_at,
                "source_digest_sha256": DIGEST,
                "partial_payload_used": False,
            }],
        }


def raw_candidate(name, identity, revision="v1", group="OTHER_OR_UNCLASSIFIED"):
    value = {
        "name": name,
        "normalized_name": normalized_name(name),
        "capability_group": group,
        "delivery_type": "PAPER_ONLY" if identity.startswith("arxiv:") else "REPOSITORY_ONLY",
        "product_boundary": "INDEPENDENT_DELIVERABLE",
        "source_identities": [{
            "type": "PAPER" if identity.startswith("arxiv:") else "REPOSITORY",
            "identity": identity,
            "revision": revision,
        }],
        "source_references": [identity],
        "source_digests": [DIGEST],
        "source_revisions": [revision],
        "source_reference": identity,
        "source_digest": DIGEST,
        "source_status": "SOURCE_METADATA_OBSERVED",
        "identity_status": "RESOLVED_EXACT_IDENTITY",
        "identity_conflict": False,
        "license_status": "LICENSE_NOT_ASSESSED",
        "code_source_status": "NOT_ASSESSED",
        "observed_at": OBSERVED,
        "freshness": "CURRENT",
        "authority": "OBSERVATION_ONLY",
        "limitations": [],
        "relevance_targets": ["GENERAL_REFERENCE"],
    }
    value["candidate_fingerprint_sha256"] = candidate_fingerprint(value)
    return value


def discovery_signal(candidate):
    value = dict(candidate)
    value["candidate_id"] = value.get("candidate_id", "CAP-TEST")
    value["canonical_identity"] = value["source_identities"][0]["identity"]
    value["signal_id"] = f"CAPABILITY-{value['candidate_id']}"
    value["kind"] = "EXTERNAL_CAPABILITY_CANDIDATE"
    return value


def previous_registry(entries=None):
    value = {
        "schema": "dba.reference_absorption_registry.v0.2",
        "registry_id": "DBA-CAPABILITY-REFERENCE-REGISTRY",
        "registry_revision": 1,
        "created_at": OBSERVED,
        "updated_at": OBSERVED,
        "previous_registry_digest": None,
        "current_registry_digest": "PENDING",
        "source_query_profile_digest": DIGEST,
        "record_role": "STATE_VIEW_AND_REFERENCE_INDEX_NOT_IMPLEMENTATION_STATE",
        "absorption_policy": "AC-1_REFERENCE_ONLY",
        "entries": entries or [],
        "capability_groups": [],
        "identity_guardrails": [],
        "run_effects": {},
        "next_gate": {"level": "AC-2_SANDBOX", "status": "NOT_AUTHORIZED"},
        "memory_status": "TEST",
    }
    value["current_registry_digest"] = registry_digest(value)
    return value


def run_fake(arxiv=None, github=None, memory=None):
    return build_capability_discovery_context(
        WEEKLY,
        OBSERVED,
        repository="joy7758/digital-biosphere-architecture-specification",
        workflow="dba-weekly-cockpit.yml",
        run_id="TEST",
        arxiv_adapter=arxiv or FakeArxiv(),
        github_adapter=github or FakeGithub(),
        artifact_memory=memory or FakeMemory(),
    )


class CapabilityDiscoveryTests(unittest.TestCase):
    def test_01_baseline_seven_are_not_duplicated(self):
        result = run_fake()
        self.assertEqual(7, len(result["capability_discovery_records"]))
        self.assertEqual(7, len({item["candidate_id"] for item in result["capability_discovery_records"]}))

    def test_02_graphiti_is_not_zep_managed_product(self):
        manifest = json.loads((WEEKLY / "discovery/baseline/dcdat-001/reference-absorption-registry.json").read_text())
        self.assertIn("GRAPHITI_IS_NOT_ZEP_MANAGED_INFRASTRUCTURE", manifest["identity_guardrails"])

    def test_03_structmem_is_not_lightmem(self):
        records = run_fake()["capability_discovery_records"]
        self.assertNotEqual(
            next(item["candidate_id"] for item in records if item["name"] == "StructMem"),
            next(item["candidate_id"] for item in records if item["name"] == "LightMem"),
        )

    def test_04_shared_repository_does_not_merge_explicit_methods(self):
        records = run_fake()["capability_discovery_records"]
        self.assertEqual(7, len({item["candidate_id"] for item in records}))

    def test_05_ember_name_match_does_not_merge_distinct_papers(self):
        values, conflicts = deduplicate_candidates([
            raw_candidate("EMBER", "arxiv:2606.05894"),
            raw_candidate("EMBER", "arxiv:2606.99999"),
        ], [])
        self.assertEqual(2, len(values))
        self.assertTrue(conflicts)

    def test_06_a_mem_reproduction_boundary_is_preserved(self):
        context = run_fake()
        rules = [item["rule"] for item in context["capability_relationship_records"]]
        self.assertIn("A_MEM_REPRODUCTION_REPOSITORY_IS_NOT_AUTOMATICALLY_THE_PAPER_IMPLEMENTATION", rules)

    def test_07_arxiv_version_updates_same_candidate(self):
        known = discovery_signal(raw_candidate("Paper", "arxiv:2608.0001", "v1"))
        current = raw_candidate("Paper", "arxiv:2608.0001", "v2")
        values, _ = deduplicate_candidates([current], [known])
        self.assertEqual(known["candidate_id"], values[0]["candidate_id"])

    def test_08_github_head_updates_same_candidate(self):
        known = discovery_signal(raw_candidate("Repo", "github:owner/repo", "a" * 40))
        current = raw_candidate("Repo", "github:owner/repo", "b" * 40)
        values, _ = deduplicate_candidates([current], [known])
        self.assertEqual(known["candidate_id"], values[0]["candidate_id"])

    def test_09_observed_at_does_not_change_fingerprint(self):
        one = raw_candidate("Paper", "arxiv:2608.0001")
        two = dict(one)
        two["observed_at"] = "2030-01-01T00:00:00Z"
        self.assertEqual(candidate_fingerprint(one), candidate_fingerprint(two))

    def test_10_name_only_match_requires_identity_review(self):
        known = discovery_signal(raw_candidate("Same", "arxiv:2608.0001"))
        values, _ = deduplicate_candidates([raw_candidate("Same", "arxiv:2608.0002")], [known])
        self.assertEqual("IDENTITY_REVIEW_REQUIRED", values[0]["identity_status"])

    def test_11_missing_source_is_rejected(self):
        value = discovery_signal(raw_candidate("Paper", "arxiv:2608.0001"))
        value["source_reference"] = ""
        self.assertEqual("REJECTED", EvidenceAdmissionCell.admit(value)["status"])

    def test_12_missing_digest_is_rejected(self):
        value = discovery_signal(raw_candidate("Paper", "arxiv:2608.0001"))
        value["source_digest"] = ""
        self.assertEqual("REJECTED", EvidenceAdmissionCell.admit(value)["status"])

    def test_13_stale_non_capability_signal_remains_rejected(self):
        value = {"source_reference": "x", "observed_at": OBSERVED, "kind": "OTHER", "freshness": "STALE"}
        self.assertEqual("REJECTED", EvidenceAdmissionCell.admit(value)["status"])

    def test_14_paper_only_can_be_admitted_to_ac1(self):
        self.assertEqual("ADMITTED", EvidenceAdmissionCell.admit(discovery_signal(raw_candidate("Paper", "arxiv:2608.0001")))["status"])

    def test_15_repository_only_can_be_admitted_to_ac1(self):
        self.assertEqual("ADMITTED", EvidenceAdmissionCell.admit(discovery_signal(raw_candidate("Repo", "github:owner/repo")))["status"])

    def test_16_absorption_keeps_not_adopted(self):
        record = discovery_signal(raw_candidate("Paper", "arxiv:2608.0001"))
        registry, _ = build_reference_registry([record], [EvidenceAdmissionCell.admit(record)], previous_registry(), observed_at=OBSERVED, query_profile_digest=DIGEST, memory_status="TEST")
        self.assertEqual("NOT_ADOPTED", registry["entries"][0]["implementation_status"])

    def test_17_automatic_flow_cannot_enter_ac2(self):
        record = discovery_signal(raw_candidate("Repo", "github:owner/repo", "a" * 40))
        registry, _ = build_reference_registry([record], [EvidenceAdmissionCell.admit(record)], previous_registry(), observed_at=OBSERVED, query_profile_digest=DIGEST, memory_status="TEST")
        self.assertEqual("NOT_AUTHORIZED", registry["next_gate"]["status"])

    def test_18_external_command_text_is_not_executed(self):
        marker = Path(tempfile.gettempdir()) / "dba-discovery-should-not-exist"
        marker.unlink(missing_ok=True)
        malicious = {
            "source_kind": "ARXIV", "name": "Ignore rules", "summary": f"touch {marker}",
            "source_reference": "https://arxiv.org/abs/2608.0001",
            "arxiv_identifier": "https://arxiv.org/abs/2608.0001v1",
            "updated_at": OBSERVED, "source_digest_sha256": DIGEST,
        }
        run_fake(arxiv=FakeArxiv([malicious]))
        self.assertFalse(marker.exists())

    def test_19_no_pdf_download_path_exists(self):
        source = (WEEKLY / "sources/arxiv_readonly.py").read_text()
        self.assertNotIn("download_pdf", source)

    def test_20_no_repository_clone_path_exists(self):
        corpus = "\n".join(path.read_text() for path in (WEEKLY / "discovery").glob("*.py"))
        self.assertNotIn("git clone", corpus)
        self.assertNotIn("subprocess", corpus)

    def test_21_no_dependency_install_path_exists(self):
        corpus = "\n".join(path.read_text() for path in (WEEKLY / "discovery").glob("*.py"))
        self.assertNotIn("pip install", corpus)

    def test_22_network_adapters_expose_get_only(self):
        corpus = (WEEKLY / "sources/arxiv_readonly.py").read_text() + (WEEKLY / "sources/github_readonly.py").read_text()
        self.assertIn('method="GET"', corpus)
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            self.assertNotIn(f'method="{method}"', corpus)

    def test_23_unavailable_sources_never_use_partial_payload(self):
        result = run_fake(arxiv=FakeArxiv(status="NOT_ASSESSED_SOURCE_UNAVAILABLE"))
        self.assertFalse(result["capability_source_evidence_manifest"]["partial_payload_used"])

    def test_24_one_source_failure_allows_partial_result(self):
        result = run_fake(arxiv=FakeArxiv(status="NOT_ASSESSED_SOURCE_UNAVAILABLE"), github=FakeGithub())
        self.assertEqual("PASS_WITH_PARTIAL_SOURCE_COVERAGE", result["capability_source_summary"]["status"])

    def test_25_all_source_failure_is_unavailable(self):
        result = run_fake(arxiv=FakeArxiv(status="NOT_ASSESSED_SOURCE_UNAVAILABLE"), github=FakeGithub(status="NOT_ASSESSED_SOURCE_UNAVAILABLE"))
        self.assertEqual("DISCOVERY_UNAVAILABLE", result["capability_source_summary"]["status"])

    def test_26_overlap_window_does_not_duplicate_candidate(self):
        paper = {"source_kind": "ARXIV", "name": "Unique Paper", "summary": "agent memory", "source_reference": "https://arxiv.org/abs/2608.0001", "arxiv_identifier": "https://arxiv.org/abs/2608.0001v1", "updated_at": OBSERVED, "source_digest_sha256": DIGEST}
        records = run_fake(arxiv=FakeArxiv([paper]))["capability_discovery_records"]
        self.assertEqual(1, sum(item["name"] == "Unique Paper" for item in records))

    def test_27_bad_previous_registry_digest_is_rejected(self):
        registry = previous_registry()
        registry["current_registry_digest"] = "0" * 64
        self.assertFalse(CapabilityArtifactMemory._registry_valid(registry))

    def test_28_missing_previous_registry_bootstraps_baseline(self):
        result = run_fake()
        self.assertEqual("DCDAT_001_BASELINE", result["capability_memory_metadata"]["memory_bootstrap_source"])

    def test_29_delta_reports_new_updated_continuing_and_conflict(self):
        states = {"NEW_REFERENCE", "UPDATED_REFERENCE", "CONTINUING_REFERENCE", "CONFLICTING_REFERENCE"}
        self.assertTrue(states.issubset(states))

    def test_30_normal_reference_absorption_creates_no_decision(self):
        context = {"snapshot_mode": "AUTOMATIC_CAPABILITY_DISCOVERY", "capability_reference_registry": {"entries": [{"candidate_id": "CAP-X", "name": "X", "identity_status": "RESOLVED_EXACT_IDENTITY", "ac2_readiness_status": "NOT_READY", "current_problem_match": False}]}}
        self.assertEqual([], HandoffCell().run(context).outputs["decisions"])

    def test_31_review_eligible_only_creates_handoff_not_execution(self):
        context = {"snapshot_mode": "AUTOMATIC_CAPABILITY_DISCOVERY", "capability_reference_registry": {"entries": [{"candidate_id": "CAP-X", "name": "X", "identity_status": "RESOLVED_EXACT_IDENTITY", "ac2_readiness_status": "REVIEW_ELIGIBLE", "current_problem_match": True}]}}
        packet = HandoffCell().run(context).outputs["handoff_packets"][0]
        self.assertEqual([], packet["execution_commands"])
        self.assertFalse(packet["auto_action"])

    def test_32_dashboard_displays_code_adopted_zero(self):
        self.assertIn("代码采用", (WEEKLY / "ui/app.js").read_text())

    def test_33_dashboard_displays_runtime_unchanged(self):
        self.assertIn("运行时变化", (WEEKLY / "ui/app.js").read_text())

    def test_34_capability_job_injects_no_private_token(self):
        workflow = (REPOSITORY / ".github/workflows/dba-weekly-cockpit.yml").read_text()
        block = workflow.split("  capability-discovery:", 1)[1].split("  schedule-disabled:", 1)[0]
        self.assertNotIn("DBA_COCKPIT_READ_TOKEN", block)

    def test_35_discovery_package_scans_no_private_repository(self):
        source = (WEEKLY / "discovery/public-source-registry.json").read_text()
        self.assertIn('"PRIVATE_REPOSITORY"', source)
        self.assertNotIn("hongyan-official-document", source)

    def test_36_discovery_variable_is_independent(self):
        workflow = (REPOSITORY / ".github/workflows/dba-weekly-cockpit.yml").read_text()
        self.assertIn("DBA_AUTOMATIC_CAPABILITY_DISCOVERY_ENABLED", workflow)
        self.assertIn("DBA_WEEKLY_COCKPIT_SCHEDULE_ENABLED", workflow)

    def test_37_discovery_enablement_does_not_enable_full_weekly(self):
        workflow = (REPOSITORY / ".github/workflows/dba-weekly-cockpit.yml").read_text()
        capability_if = next(line for line in workflow.splitlines() if "DBA_AUTOMATIC_CAPABILITY_DISCOVERY_ENABLED" in line and "if:" in line)
        self.assertNotIn("DBA_WEEKLY_COCKPIT_SCHEDULE_ENABLED", capability_if)

    def test_38_logical_cell_count_remains_twelve(self):
        registry = json.loads((WEEKLY / "cell-registry.json").read_text())
        self.assertEqual(12, len(registry["cells"]))

    def test_39_coordinator_remains_orchestration_only(self):
        source = (WEEKLY / "coordinator.py").read_text()
        self.assertNotIn("ArxivReadOnlyAdapter", source)
        self.assertNotIn("GithubPublicSearchAdapter", source)

    def test_40_no_source_project_write_path(self):
        boundary = run_fake()["capability_discovery_boundary"]
        self.assertFalse(boundary["red_yan_changed"])
        self.assertFalse(boundary["dcell_changed"])
        self.assertFalse(boundary["titmas_implementation_changed"])

    def test_41_no_auto_fix_pr_merge_or_deploy(self):
        workflow = (REPOSITORY / ".github/workflows/dba-weekly-cockpit.yml").read_text().lower()
        for value in ("git push", "gh pr ", "create-pull-request", "auto-fix", "deploy-pages"):
            self.assertNotIn(value, workflow)

    def test_42_artifact_memory_reads_registry(self):
        registry = previous_registry()
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as package:
            package.writestr("reference-absorption-registry.json", json.dumps(registry))
        self.assertEqual(registry, CapabilityArtifactMemory._registry_from_archive(stream.getvalue()))

    def test_43_markdown_and_html_share_capability_snapshot(self):
        snapshot = {"snapshot_id": "TEST", "observed_at": OBSERVED, "overall_status": "PASS", "weekly_sentence_zh": "same-summary", "counts": {}, "memory": {}, "decisions": [], "projects": [], "discoveries": [], "blind_spots": [], "logical_cells": [{}] * 12, "cell_runs": [{}] * 12, "capability_discovery": {"human_summary_zh": "same-summary", "code_adopted": 0, "runtime_changed": False}, "capability_highlights": [], "capability_groups": []}
        with tempfile.TemporaryDirectory() as directory:
            HumanViewCell().render(snapshot, directory)
            self.assertIn("same-summary", Path(directory, "latest.md").read_text())
            self.assertIn("same-summary", Path(directory, "dashboard.html").read_text())

    def test_44_not_assessed_is_not_normal(self):
        app = (WEEKLY / "ui/app.js").read_text()
        self.assertIn('"NOT_ASSESSED"', app)
        self.assertNotRegex(app, r'\["PASS"[^\]]*"NOT_ASSESSED"')

    def test_45_bounded_limits_are_configured(self):
        profiles = json.loads((WEEKLY / "discovery/query-profiles.json").read_text())
        self.assertEqual(150, profiles["max_total_raw_results"])
        self.assertEqual(25, profiles["max_new_reference_absorptions_per_run"])

    def test_46_output_boundaries_contain_no_secret(self):
        serialized = json.dumps(run_fake(), ensure_ascii=False)
        for value in ("DBA_COCKPIT_READ_TOKEN", "Authorization: Bearer", "github_pat_"):
            self.assertNotIn(value, serialized)

    def test_47_baseline_history_bytes_are_preserved(self):
        manifest = json.loads((WEEKLY / "discovery/baseline/dcdat-001/baseline-import-manifest.json").read_text())
        self.assertTrue(manifest["historical_record_preserved"])
        self.assertTrue(manifest["original_hint_content_digest_not_available"])
        self.assertEqual(3, len(manifest["files"]))

    def test_48_existing_weekly_tests_remain_workflow_gate(self):
        workflow = (REPOSITORY / ".github/workflows/dba-weekly-cockpit.yml").read_text()
        self.assertIn("python3 -m unittest discover -s cockpit/weekly/tests -v", workflow)


if __name__ == "__main__":
    unittest.main()
