from __future__ import annotations

import json
import hashlib
import inspect
import io
import re
import subprocess
import tempfile
import unittest
import zipfile
from html.parser import HTMLParser
from http.client import IncompleteRead
from pathlib import Path
from unittest import mock
from urllib.request import Request

from jsonschema import Draft202012Validator

from cockpit.weekly.cells.evidence_admission import EvidenceAdmissionCell
from cockpit.weekly.cells.drift import DriftCell
from cockpit.weekly.cells.environment_discovery import EnvironmentDiscoveryCell
from cockpit.weekly.cells.handoff import HandoffCell
from cockpit.weekly.cells.human_view import HumanViewCell
from cockpit.weekly.cells.project_discovery import ProjectDiscoveryCell
from cockpit.weekly.cells.security import SecurityCell
from cockpit.weekly.cells.memory import MemoryCell
from cockpit.weekly.coordinator import WeeklyCoordinator
from cockpit.weekly.run_weekly import (
    _apply_live_result_projection,
    _build_pilot_boundary,
    load_demo_context,
    load_live_context,
)
from cockpit.weekly.sources.artifact_memory import ArtifactMemory
from cockpit.weekly.sources.dependency_readonly import DependencyReadOnlyAdapter
from cockpit.weekly.sources.github_readonly import (
    ALLOWLIST,
    GithubApi,
    GithubReadOnlyAdapter,
    ReadOnlyRedirectHandler,
)
from cockpit.weekly.sources.public_http_readonly import ALLOWED_ENDPOINTS, PublicHttpReadOnlyAdapter
from cockpit.weekly.sources.source_result import SourceResult


WEEKLY = Path(__file__).resolve().parents[1]
DBA = WEEKLY.parents[1]
DEMO = WEEKLY / "demo"


class ElementCounter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class WeeklyCockpitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        snapshots = sorted(DEMO.glob("weekly-snapshot-*.json"))
        if not snapshots:
            raise AssertionError("demo snapshot must be generated before tests")
        cls.snapshot = json.loads(snapshots[-1].read_text(encoding="utf-8"))
        cls.html = (DEMO / "dashboard.html").read_text(encoding="utf-8")
        cls.markdown = (DEMO / "latest.md").read_text(encoding="utf-8")
        cls.workflow = (DBA.parent / ".github" / "workflows" / "dba-weekly-cockpit.yml").read_text(encoding="utf-8")

    def test_01_all_twelve_manifests_validate(self):
        schema = json.loads((WEEKLY / "schemas" / "cell-manifest.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        manifests = sorted((WEEKLY / "manifests").glob("*.json"))
        self.assertEqual(12, len(manifests))
        for path in manifests:
            errors = list(validator.iter_errors(json.loads(path.read_text(encoding="utf-8"))))
            self.assertEqual([], errors, path.name)

    def test_02_manifests_deny_all_write_authorities(self):
        for path in (WEEKLY / "manifests").glob("*.json"):
            bounds = json.loads(path.read_text(encoding="utf-8"))["authority_boundaries"]
            self.assertTrue(all(value is False for value in bounds.values()))

    def test_03_discovered_candidate_is_not_auto_monitored(self):
        result = ProjectDiscoveryCell().run({"as_of": "2026-08-29T00:30:00+08:00", "project_check_registry": {"projects": []}})
        candidates = getattr(result, "discoveries", getattr(result, "observations", []))
        external = next(item for item in candidates if item["project_id"] == "openbao-adjacent-signal")
        self.assertEqual("DISCOVERED", external["current_state"])

    def test_04_unauthorized_candidate_does_not_scan_private_content(self):
        result = ProjectDiscoveryCell().run({"as_of": "2026-08-29T00:30:00+08:00", "project_check_registry": {"projects": []}})
        candidates = getattr(result, "discoveries", getattr(result, "observations", []))
        external = next(item for item in candidates if item["project_id"] == "openbao-adjacent-signal")
        self.assertFalse(external["scan_authorized"])
        self.assertFalse(external["private_content_scanned"])

    def test_05_evidence_without_source_or_time_is_rejected(self):
        decision = EvidenceAdmissionCell.admit({"freshness": "CURRENT"})
        self.assertEqual("REJECTED", decision["status"])
        self.assertEqual("MISSING_SOURCE_OR_TIME", decision["reason"])

    def test_06_stale_evidence_is_rejected(self):
        decision = EvidenceAdmissionCell.admit({"source_reference": "x", "observed_at": "2026-01-01", "freshness": "STALE"})
        self.assertEqual("REJECTED", decision["status"])
        self.assertEqual("STALE_OR_UNKNOWN", decision["reason"])

    def test_07_unknown_project_is_not_rendered_as_green(self):
        for project in self.snapshot["projects"]:
            if project.get("status") in {"UNKNOWN", "NOT_ASSESSED"}:
                self.assertNotIn(project.get("status"), {"PASS", "NORMAL", "STABLE"})

    def test_08_cell_failure_isolation_contract_is_present(self):
        coordinator = (WEEKLY / "coordinator.py").read_text(encoding="utf-8")
        self.assertIn("NOT_ASSESSED", coordinator)
        self.assertRegex(coordinator, r"except\s+Exception")

    def test_09_discovery_unavailable_fail_closed_contract_is_present(self):
        coordinator = (WEEKLY / "coordinator.py").read_text(encoding="utf-8")
        self.assertIn("DISCOVERY_UNAVAILABLE", coordinator)

    def test_10_handoff_contains_no_execution_commands(self):
        result = HandoffCell().run({"as_of": "2026-08-29T00:30:00+08:00"})
        packets = getattr(result, "handoffs", getattr(result, "handoff_packets", []))
        self.assertTrue(packets)
        self.assertTrue(all(item["execution_commands"] == [] for item in packets))

    def test_11_human_view_declares_snapshot_only(self):
        self.assertIn("固定问题仅查询当前快照", self.html)
        self.assertNotIn("fetch(", self.html)

    def test_12_no_composite_project_score(self):
        flattened = json.dumps(self.snapshot, ensure_ascii=False).lower()
        self.assertNotIn("composite_score", flattened)
        self.assertNotIn("health_score", flattened)

    def test_13_technical_evidence_is_collapsed_by_default(self):
        self.assertIn("<details>", self.html)
        self.assertNotIn("<details open", self.html)

    def test_14_dashboard_is_standalone(self):
        self.assertNotRegex(self.html, r"<(script|link)[^>]+(?:src|href)=['\"]https?://")
        self.assertIn("id=\"weekly-snapshot\"", self.html)

    def test_15_query_answers_come_from_snapshot(self):
        self.assertIn("snapshot.preset_queries", self.html)
        self.assertNotIn("XMLHttpRequest", self.html)

    def test_16_workflow_has_read_only_permissions(self):
        self.assertIn("contents: read", self.workflow)
        self.assertNotRegex(self.workflow, r"contents:\s*write")
        self.assertNotRegex(self.workflow, r"pull-requests:\s*write")

    def test_17_daily_schedule_requires_explicit_repository_variable(self):
        self.assertIn('cron: "0 1 * * *"', self.workflow)
        self.assertIn("DBA_WEEKLY_COCKPIT_SCHEDULE_ENABLED", self.workflow)
        self.assertIn("'true'", self.workflow)

    def test_18_registered_projects_are_read_only(self):
        registry = json.loads((WEEKLY / "project-check-registry.json").read_text(encoding="utf-8"))
        projects = registry.get("projects", registry.get("entries", []))
        self.assertTrue(projects)
        for project in projects:
            self.assertTrue(
                project.get("read_only", False)
                or project.get("access") == "READ_ONLY"
                or project.get("source_access_mode", "").endswith("READ_ONLY")
                or project.get("source_access_mode") == "EXISTING_READ_ONLY_STATUS_ADAPTER"
            )

    def test_19_history_policy_forbids_overwrite(self):
        policy = (WEEKLY / "history" / "README.md").read_text(encoding="utf-8")
        self.assertIn("MUST NOT be overwritten", policy)

    def test_20_old_titmas_snapshots_do_not_gain_current_authority(self):
        flattened = json.dumps(self.snapshot, ensure_ascii=False)
        self.assertIn("view_not_truth", flattened)
        self.assertNotIn('"authority": "CURRENT_TRUTH"', flattened)

    def test_21_exactly_twelve_logical_cells(self):
        registry = json.loads((WEEKLY / "cell-registry.json").read_text(encoding="utf-8"))
        cells = registry.get("cells", registry.get("entries", []))
        self.assertEqual(12, len(cells))
        self.assertEqual(12, len(self.snapshot["cell_runs"]))

    def test_22_dashboard_has_no_more_than_six_main_sections(self):
        parser = ElementCounter()
        parser.feed(self.html)
        sections = [attrs for tag, attrs in parser.tags if tag == "section"]
        self.assertLessEqual(len(sections), 6)
        self.assertTrue(any(tag == "main" for tag, _ in parser.tags))
        self.assertTrue(any(tag == "nav" for tag, _ in parser.tags))
        self.assertTrue(any(tag == "button" for tag, _ in parser.tags))

    def test_23_weekly_snapshot_contract_validates(self):
        schema = json.loads((WEEKLY / "schemas" / "weekly-snapshot.schema.json").read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema).iter_errors(self.snapshot))
        self.assertEqual([], errors)

    def test_24_dashboard_has_chinese_language_and_title(self):
        self.assertIn('lang="zh-CN"', self.html)
        self.assertIn("<title>DBA Weekly Cockpit", self.html)

    def test_25_markdown_uses_observed_at_without_false_unknown(self):
        self.assertIn(self.snapshot["observed_at"], self.markdown)
        self.assertNotIn("As of: UNKNOWN", self.markdown)
        self.assertNotIn("观察时间：`UNKNOWN`", self.markdown)

    def test_26_markdown_contains_both_human_decisions(self):
        self.assertIn("是否启动依赖安全专项复核", self.markdown)
        self.assertIn("是否授权刷新 TITMAC Scout 的只读状态", self.markdown)

    def test_27_markdown_contains_all_five_projects(self):
        for name in ("红岩公文", "DBA 驾驶舱", "数字细胞演示", "TITMAS 支撑层", "TITMAC 侦察"):
            self.assertIn(name, self.markdown)

    def test_28_markdown_has_no_false_placeholder_copy(self):
        self.assertNotIn("未命名", self.markdown)
        self.assertNotIn("无说明", self.markdown)

    def test_29_html_and_markdown_share_snapshot_identity(self):
        snapshot_id = self.snapshot["snapshot_id"]
        self.assertIn(snapshot_id, self.html)
        self.assertIn(snapshot_id, self.markdown)

    def test_30_not_assessed_is_not_translated_as_normal(self):
        line = next(line for line in self.markdown.splitlines() if "依赖漏洞的远端运行绑定未观察" in line)
        self.assertIn("NOT_ASSESSED", line)
        self.assertNotIn("正常", line)

    def test_31_markdown_semantics_match_snapshot(self):
        self.assertIn(self.snapshot["weekly_sentence_zh"], self.markdown)
        for item in self.snapshot["discoveries"]:
            self.assertIn(item["title_zh"], self.markdown)
        for item in self.snapshot["blind_spots"]:
            self.assertIn(item["title_zh"], self.markdown)

    def test_32_coordinator_contains_no_project_specific_constants(self):
        source = (WEEKLY / "coordinator.py").read_text(encoding="utf-8")
        for token in ("RED_YAN", "OpenBao", "postcss", "nanoid", "TITMAC_SCOUT"):
            self.assertNotIn(token, source)

    def test_33_coordinator_contains_no_concrete_human_decisions(self):
        source = (WEEKLY / "coordinator.py").read_text(encoding="utf-8")
        self.assertNotIn("是否启动依赖安全专项复核", source)
        self.assertNotIn("是否授权刷新 TITMAC Scout 的只读状态", source)

    def test_34_all_snapshot_decisions_come_from_handoff_cell(self):
        self.assertEqual("HANDOFF_CELL", self.snapshot["decisions_source"])
        self.assertTrue(self.snapshot["decisions"])
        self.assertTrue(all(item["source_cell_id"] == "HANDOFF_CELL" for item in self.snapshot["decisions"]))

    def test_35_security_consumes_only_admitted_observations(self):
        result = SecurityCell().run(
            {
                "admitted_observations": [
                    {"signal_id": "accepted", "kind": "DEPENDENCY_SECURITY_CONFLICT_CANDIDATE"}
                ],
                "rejected_observations": [
                    {"observation": {"signal_id": "rejected", "kind": "DEPENDENCY_SECURITY_CONFLICT_CANDIDATE"}}
                ],
            }
        )
        self.assertEqual(["accepted"], result.outputs["security_consumed_signal_ids"])

    def test_36_rejected_observations_are_not_rendered_as_admitted(self):
        rejected = [item for item in self.snapshot["discoveries"] if item["admission_status"] == "REJECTED"]
        self.assertTrue(rejected)
        self.assertTrue(all(item["admission_label_zh"] == "未通过准入或来源过期" for item in rejected))

    def test_37_openbao_remains_discovered_not_admitted_or_monitored(self):
        item = next(item for item in self.snapshot["discoveries"] if item.get("project_id") == "openbao-adjacent-signal")
        self.assertEqual("DISCOVERED", item["current_state"])
        self.assertEqual("NOT_ADMITTED", item["admission_status"])
        self.assertEqual("NOT_MONITORED", item["monitoring_status"])
        self.assertFalse(item["scan_authorized"])

    def test_38_openbao_is_not_a_human_decision(self):
        decisions = json.dumps(self.snapshot["decisions"], ensure_ascii=False)
        self.assertNotIn("OpenBao", decisions)

    def test_39_dependency_audit_conflict_preserves_both_counts(self):
        finding = next(item for item in self.snapshot["findings"] if item.get("finding_type") == "DEPENDENCY_AUDIT_STATE_CONFLICT")
        self.assertEqual(2, finding["canonical_high_count"])
        self.assertEqual(4, finding["live_candidate_high_count"])
        self.assertEqual("NOT_ASSESSED", finding["exploitability"])

    def test_40_all_live_high_packages_are_visible(self):
        for package in ("image-size", "js-yaml", "nanoid", "vinext"):
            self.assertIn(package, self.html)
            self.assertIn(package, self.markdown)

    def test_41_dashboard_does_not_claim_remote_exploitability(self):
        self.assertNotIn("远端可利用", self.html)
        self.assertNotIn("远端可利用", self.markdown)

    def test_42_first_snapshot_does_not_claim_six_new_signals(self):
        self.assertNotIn("新增6", self.html)
        self.assertNotIn("新增 6", self.markdown)
        self.assertIn("首次快照，尚不能判断这些信号是否相对于上周新增", self.markdown)

    def test_43_machine_status_code_is_hidden_from_hero(self):
        app = (WEEKLY / "ui" / "app.js").read_text(encoding="utf-8")
        hero_line = next(line for line in app.splitlines() if 'el("overall-signal")' in line)
        self.assertNotIn("snapshot.overall_status", hero_line)
        self.assertIn("部分检查尚未完成", hero_line)

    def test_44_human_view_uses_chinese_high_risk_wording(self):
        self.assertIn("高危", self.html)
        self.assertIn("高危", self.markdown)
        self.assertNotRegex(self.html, r"\d+\s*个\s*high")
        self.assertNotRegex(self.markdown, r"\d+\s*个\s*high")

    def test_45_handoff_allows_one_decision_without_forced_symmetry(self):
        result = HandoffCell().run(
            {
                "findings": [
                    {
                        "finding_type": "DEPENDENCY_AUDIT_STATE_CONFLICT",
                        "finding_id": "f1",
                        "project_id": "p1",
                        "canonical_high_count": 2,
                        "live_candidate_high_count": 4,
                    }
                ],
                "blind_spots": [],
            }
        )
        self.assertEqual(1, len(result.outputs["decisions"]))

    def test_46_cell_failure_isolation_remains_fail_closed(self):
        source = (WEEKLY / "coordinator.py").read_text(encoding="utf-8")
        self.assertRegex(source, r"except\s+Exception")
        self.assertIn('status="NOT_ASSESSED"', source)
        self.assertIn("DISCOVERY_UNAVAILABLE", source)

    def test_47_logical_cell_count_remains_twelve(self):
        self.assertEqual(12, len(self.snapshot["logical_cells"]))
        self.assertEqual(12, len(self.snapshot["cell_runs"]))

    def test_48_discovery_admission_counts_are_explicit(self):
        counts = self.snapshot["counts"]
        self.assertEqual(6, counts["discovered_count"])
        self.assertEqual(1, counts["admitted_count"])
        self.assertEqual(5, counts["rejected_or_pending_count"])


class FakeResponse:
    def __init__(self, body: bytes = b"ok", status: int = 200):
        self.body = body
        self.status = status
        self.headers = {"Content-Type": "text/plain", "Content-Length": str(len(body))}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, size: int = -1):
        return self.body if size < 0 else self.body[:size]

    def getcode(self):
        return self.status


class FakeArtifactApi:
    def __init__(self, runs=None, artifacts=None, archive=b""):
        self.runs = runs or []
        self.artifacts = artifacts or {}
        self.archive = archive

    def request_json(self, reference, **_kwargs):
        if "/runs?" in reference:
            return {"workflow_runs": self.runs}
        if "/artifacts?" in reference:
            run_id = reference.split("/runs/")[1].split("/")[0]
            return {"artifacts": self.artifacts.get(run_id, [])}
        raise AssertionError(reference)

    def request_bytes(self, _reference):
        return self.archive


def live_snapshot_bytes(observed_at="2026-08-29T03:00:00+08:00"):
    snapshot = {
        "schema_version": "0.1",
        "snapshot_id": "DBA-WEEKLY-2026-W35-RUN-1",
        "observed_at": observed_at,
        "mode": "LIVE_READ_ONLY_OBSERVATION_PILOT",
        "boundaries": {"pilot_only": True},
        "findings": [],
    }
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as package:
        package.writestr("latest.json", json.dumps(snapshot))
    return stream.getvalue()


class LiveReadOnlyPilotTests(unittest.TestCase):
    def test_49_live_context_does_not_load_fixed_audit_candidate(self):
        self.assertNotIn("live-dependency-audit-candidate", inspect.getsource(load_live_context))

    def test_50_demo_replay_is_deterministic(self):
        context_a = load_demo_context("2026-08-29T00:30:00+08:00")
        context_b = load_demo_context("2026-08-29T00:30:00+08:00")
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            a = WeeklyCoordinator().run(context_a, Path(first), "latest.json")
            b = WeeklyCoordinator().run(context_b, Path(second), "latest.json")
        self.assertEqual(a, b)

    def test_51_public_http_adapter_uses_get(self):
        methods = []

        def opener(request, timeout):
            methods.append((request.get_method(), timeout))
            return FakeResponse()

        result = PublicHttpReadOnlyAdapter(opener).observe(ALLOWED_ENDPOINTS[0], "2026-08-29T00:00:00Z")
        self.assertEqual("AVAILABLE", result.status)
        self.assertEqual([("GET", 20)], methods)

    def test_52_public_http_adapter_rejects_mutating_method(self):
        with self.assertRaisesRegex(ValueError, "READ_ONLY_HTTP_METHOD_REQUIRED"):
            PublicHttpReadOnlyAdapter().observe(ALLOWED_ENDPOINTS[0], "2026-08-29T00:00:00Z", "POST")

    def test_53_source_result_does_not_expose_token_field(self):
        flattened = json.dumps(SourceResult.unavailable(
            source_id="x", project_id="p", source_reference="r",
            observed_at="2026-08-29T00:00:00Z", reason="credential unavailable"
        ).to_dict())
        self.assertNotIn("token", flattened.lower())

    def test_54_github_repository_allowlist_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "REPOSITORY_NOT_ALLOWLISTED"):
            GithubReadOnlyAdapter._assert_allowlisted("DBA_COCKPIT", "joy7758/other")

    def test_55_private_repository_missing_credential_is_not_assessed(self):
        project = {
            "project_id": "TITMAC_SCOUT", "repository": "joy7758/titmac-scout",
            "cross_repo_credential_required": True,
        }
        with mock.patch.dict("os.environ", {}, clear=True):
            result = GithubReadOnlyAdapter().observe_project(project, "2026-08-29T00:00:00Z")
        self.assertEqual("NOT_ASSESSED_CREDENTIAL_UNAVAILABLE", result.status)

    @staticmethod
    def dependency_runner(command, _cwd):
        if command[:2] == ["git", "status"]:
            return subprocess.CompletedProcess(command, 0, "", "")
        if command == ["npm", "--version"]:
            return subprocess.CompletedProcess(command, 0, "10.0.0\n", "")
        if command[:2] == ["npm", "audit"]:
            payload = {
                "metadata": {"vulnerabilities": {"high": 4, "critical": 0}},
                "vulnerabilities": {"sample": {"isDirect": True, "fixAvailable": True}},
            }
            return subprocess.CompletedProcess(command, 1, json.dumps(payload), "")
        return subprocess.CompletedProcess(command, 2, "", "outdated unavailable")

    def test_56_nonzero_npm_audit_is_retained_and_cells_continue(self):
        result = DependencyReadOnlyAdapter(self.dependency_runner).observe(
            Path("/site"), Path("/repo"), "2026-08-29T00:00:00Z"
        )
        self.assertEqual("AVAILABLE", result.status)
        self.assertEqual(1, result.payload["audit_exit_code"])
        self.assertEqual(4, result.payload["observed_result"]["high_count"])

    def test_57_dependency_observation_proves_git_unchanged(self):
        result = DependencyReadOnlyAdapter(self.dependency_runner).observe(
            Path("/site"), Path("/repo"), "2026-08-29T00:00:00Z"
        )
        self.assertTrue(result.payload["git_status_unchanged"])

    def test_58_outdated_failure_is_not_assessed(self):
        result = DependencyReadOnlyAdapter(self.dependency_runner).observe(
            Path("/site"), Path("/repo"), "2026-08-29T00:00:00Z"
        )
        self.assertEqual("NOT_ASSESSED", result.payload["outdated_status"])

    def test_59_scout_existing_adapter_fails_closed_without_credential(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            result = GithubReadOnlyAdapter().observe_scout("2026-08-29T00:00:00+00:00")
        self.assertEqual("NOT_ASSESSED_CREDENTIAL_UNAVAILABLE", result.status)

    def test_60_zero_discovery_failures_is_available(self):
        self.assertEqual("AVAILABLE", WeeklyCoordinator.classify_discovery_failures(0))

    def test_61_one_discovery_failure_is_partial(self):
        self.assertEqual("PARTIAL_DISCOVERY_NOT_ASSESSED", WeeklyCoordinator.classify_discovery_failures(1))

    def test_62_two_discovery_failures_are_partial(self):
        self.assertEqual("PARTIAL_DISCOVERY_NOT_ASSESSED", WeeklyCoordinator.classify_discovery_failures(2))

    def test_63_three_discovery_failures_are_unavailable(self):
        self.assertEqual("DISCOVERY_UNAVAILABLE", WeeklyCoordinator.classify_discovery_failures(3))

    def test_64_first_run_records_no_previous_live_artifact(self):
        result = ArtifactMemory(FakeArtifactApi()).load_previous(
            repository="joy7758/repo", workflow="workflow.yml", branch="main",
            current_run_id="1", observed_at="2026-08-29T00:00:00Z"
        )
        self.assertEqual("NO_PREVIOUS_LIVE_ARTIFACT", result.payload["memory_status"])

    def test_65_second_run_loads_first_run_artifact(self):
        archive = live_snapshot_bytes()
        api = FakeArtifactApi(
            runs=[{"id": 1, "head_branch": "main", "status": "completed", "conclusion": "success"}],
            artifacts={"1": [{
                "id": 10, "name": "dba-weekly-cockpit-live-pilot-1", "expired": False,
                "archive_download_url": "https://api.github.test/archive",
                "digest": f"sha256:{hashlib.sha256(archive).hexdigest()}",
            }]}, archive=archive,
        )
        result = ArtifactMemory(api).load_previous(
            repository="joy7758/repo", workflow="workflow.yml", branch="main",
            current_run_id="2", observed_at="2026-08-29T00:00:00Z"
        )
        self.assertTrue(result.payload["PREVIOUS_LIVE_ARTIFACT_LOADED"])
        self.assertEqual("PASS", result.payload["artifact_digest_verification"])

    def test_66_current_run_artifact_is_rejected(self):
        api = FakeArtifactApi(runs=[
            {"id": 2, "head_branch": "main", "status": "completed", "conclusion": "success"}
        ])
        result = ArtifactMemory(api).load_previous(
            repository="joy7758/repo", workflow="workflow.yml", branch="main",
            current_run_id="2", observed_at="2026-08-29T00:00:00Z"
        )
        self.assertFalse(result.payload["PREVIOUS_LIVE_ARTIFACT_LOADED"])
        self.assertTrue(result.payload["ARTIFACT_FROM_CURRENT_RUN_REJECTED"])

    def test_67_failed_and_expired_artifacts_are_rejected(self):
        api = FakeArtifactApi(
            runs=[
                {"id": 3, "head_branch": "main", "status": "completed", "conclusion": "failure"},
                {"id": 1, "head_branch": "main", "status": "completed", "conclusion": "success"},
            ],
            artifacts={"1": [{"id": 10, "name": "dba-weekly-cockpit-live-pilot-1", "expired": True}]},
        )
        result = ArtifactMemory(api).load_previous(
            repository="joy7758/repo", workflow="workflow.yml", branch="main",
            current_run_id="4", observed_at="2026-08-29T00:00:00Z"
        )
        self.assertFalse(result.payload["PREVIOUS_LIVE_ARTIFACT_LOADED"])
        self.assertTrue(result.payload["FAILED_OR_EXPIRED_ARTIFACT_REJECTED"])

    def test_68_observed_at_change_does_not_create_false_new_finding(self):
        base = {
            "finding_id": "f", "project_id": "p", "finding_type": "t",
            "observed_at": "2026-08-28T00:00:00Z",
        }
        current = {**base, "observed_at": "2026-08-29T00:00:00Z"}
        comparison = MemoryCell.compare_findings([base], [current])
        self.assertEqual([], comparison["NEW"])
        self.assertEqual(["f | p | t"], comparison["CONTINUING"])

    def test_69_every_external_action_is_full_sha_pinned(self):
        uses = re.findall(r"^\s*uses:\s*([^\s]+)", self._workflow(), re.MULTILINE)
        self.assertTrue(uses)
        for reference in uses:
            if reference.startswith("./"):
                continue
            self.assertRegex(reference, r"@[0-9a-f]{40}$")

    def test_70_workflow_contains_no_write_permission(self):
        self.assertNotRegex(self._workflow(), r":\s*write\b")

    def test_71_schedule_remains_explicitly_disabled_by_default(self):
        workflow = self._workflow()
        self.assertIn("DBA_WEEKLY_COCKPIT_SCHEDULE_ENABLED", workflow)
        self.assertIn("schedule-disabled", workflow)

    def test_72_red_yan_runtime_access_is_forbidden(self):
        source = (WEEKLY / "run_weekly.py").read_text(encoding="utf-8")
        self.assertNotIn("ssh ", source.lower())
        self.assertIn('"red_yan_runtime_access": False', source)

    def test_73_ui_has_small_live_pilot_indicator(self):
        self.assertIn('id="pilot-indicator"', (WEEKLY / "ui" / "template.html").read_text(encoding="utf-8"))

    def test_74_ui_renders_required_source_labels(self):
        app = (WEEKLY / "ui" / "app.js").read_text(encoding="utf-8")
        self.assertIn("source_label", app)
        self.assertIn("RETAINED_SNAPSHOT", app)

    def test_75_live_pilot_preserves_exactly_twelve_cells(self):
        registry = json.loads((WEEKLY / "cell-registry.json").read_text(encoding="utf-8"))
        self.assertEqual(12, len(registry["cells"]))

    def test_76_coordinator_remains_source_adapter_free(self):
        source = (WEEKLY / "coordinator.py").read_text(encoding="utf-8")
        self.assertNotIn("GithubReadOnlyAdapter", source)
        self.assertNotIn("DependencyReadOnlyAdapter", source)

    def test_77_handoff_still_emits_no_commands(self):
        result = HandoffCell().run({})
        self.assertTrue(all(item["execution_commands"] == [] for item in result.outputs["handoff_packets"]))

    def test_78_no_automatic_dependency_fix_exists(self):
        corpus = self._workflow() + (WEEKLY / "sources" / "dependency_readonly.py").read_text(encoding="utf-8")
        self.assertNotIn("npm audit fix", corpus)
        self.assertNotIn("npm update", corpus)

    def test_79_workflow_uploads_all_six_live_outputs(self):
        workflow = self._workflow()
        for name in (
            "latest.json", "latest.md", "dashboard.html", "cell-run-summary.json",
            "source-observation-summary.json", "pilot-boundary-report.json",
        ):
            self.assertIn(name, workflow)

    def test_80_live_mode_schema_and_boundaries_are_explicit(self):
        schema = json.loads((WEEKLY / "schemas" / "weekly-snapshot.schema.json").read_text(encoding="utf-8"))
        self.assertIn("LIVE_READ_ONLY_OBSERVATION_PILOT", schema["properties"]["mode"]["enum"])
        source = (WEEKLY / "run_weekly.py").read_text(encoding="utf-8")
        for boundary in ("pilot_only", "schedule_enabled", "source_mutation"):
            self.assertIn(boundary, source)

    def test_81_source_adapters_have_observation_only_authority(self):
        result = SourceResult(
            source_id="s", project_id="p", status="AVAILABLE", source_reference="r",
            observed_at="2026-08-29T00:00:00Z", retrieved_at="2026-08-29T00:00:00Z",
        )
        self.assertEqual("OBSERVATION_ONLY", result.authority)

    def test_82_public_endpoint_allowlist_is_exact(self):
        self.assertEqual(4, len(ALLOWED_ENDPOINTS))
        self.assertEqual("https://dcell.net/", ALLOWED_ENDPOINTS[0])

    def test_83_incomplete_github_response_fails_closed_without_partial_payload(self):
        partial = b'{"private":"SUPER_SECRET", "apparently_valid":true'

        class IncompleteResponse(FakeResponse):
            def read(self, _size=-1):
                raise IncompleteRead(partial=partial, expected=20)

        def opener(_request, timeout):
            self.assertEqual(20, timeout)
            return IncompleteResponse()

        project = {
            "project_id": "DIGITAL_CELL_DEMO",
            "repository": "joy7758/titmas-demo",
            "branch": "main",
        }
        from cockpit.weekly.sources.github_readonly import GithubApi

        failed = GithubReadOnlyAdapter(GithubApi(token="TOKEN_MUST_NOT_LEAK", opener=opener)).observe_project(
            project, "2026-08-29T00:00:00Z"
        )
        unrelated = SourceResult(
            source_id="http:https://dcell.net/", project_id="PUBLIC_DCELL_ENDPOINTS",
            status="AVAILABLE", source_reference="https://dcell.net/",
            observed_at="2026-08-29T00:00:00Z", retrieved_at="2026-08-29T00:00:00Z",
        )
        serialized = json.dumps(failed.to_dict(), ensure_ascii=False)
        self.assertEqual("NOT_ASSESSED", failed.status)
        self.assertEqual("NOT_ASSESSED_SOURCE_UNAVAILABLE", failed.payload["reason_code"])
        self.assertFalse(failed.payload["source_available"])
        self.assertFalse(failed.payload["evidence_admitted"])
        self.assertFalse(failed.payload["partial_payload_used"])
        self.assertEqual("OBSERVATION_ONLY", failed.authority)
        self.assertNotIn(failed.status, {"PASS", "NORMAL", "STABLE"})
        self.assertEqual("AVAILABLE", unrelated.status)
        self.assertEqual(
            "PARTIAL_DISCOVERY_NOT_ASSESSED",
            WeeklyCoordinator.classify_discovery_failures(1),
        )
        self.assertNotIn("SUPER_SECRET", serialized)
        self.assertNotIn("TOKEN_MUST_NOT_LEAK", serialized)
        self.assertNotIn("apparently_valid", serialized)
        self.assertNotIn("findings", failed.payload)

    def test_84_cross_origin_artifact_redirect_drops_sensitive_headers(self):
        request = Request(
            "https://api.github.com/repos/joy7758/repo/actions/artifacts/1/zip",
            headers={
                "Authorization": "Bearer MUST_NOT_LEAK",
                "Proxy-Authorization": "Basic MUST_NOT_LEAK",
                "Cookie": "session=MUST_NOT_LEAK",
                "Accept": "application/vnd.github+json",
            },
            method="GET",
        )
        redirected = ReadOnlyRedirectHandler().redirect_request(
            request,
            None,
            302,
            "Found",
            {},
            "https://productionresults.example.invalid/signed-artifact",
        )
        self.assertIsNotNone(redirected)
        headers = {name.lower(): value for name, value in redirected.header_items()}
        self.assertNotIn("authorization", headers)
        self.assertNotIn("proxy-authorization", headers)
        self.assertNotIn("cookie", headers)
        self.assertEqual("application/vnd.github+json", headers["accept"])
        self.assertEqual("GET", redirected.get_method())

    def test_85_same_origin_redirect_preserves_authorization(self):
        request = Request(
            "https://api.github.com/repos/joy7758/repo/actions/artifacts/1/zip",
            headers={"Authorization": "Bearer SAME_ORIGIN_ONLY"},
            method="GET",
        )
        redirected = ReadOnlyRedirectHandler().redirect_request(
            request,
            None,
            302,
            "Found",
            {},
            "https://api.github.com/repos/joy7758/repo/actions/artifacts/1/archive",
        )
        self.assertEqual("Bearer SAME_ORIGIN_ONLY", redirected.get_header("Authorization"))

    def test_86_non_https_redirect_fails_closed(self):
        request = Request(
            "https://api.github.com/repos/joy7758/repo/actions/artifacts/1/zip",
            headers={"Authorization": "Bearer MUST_NOT_LEAK"},
            method="GET",
        )
        with self.assertRaisesRegex(ValueError, "GITHUB_REDIRECT_HTTPS_REQUIRED"):
            ReadOnlyRedirectHandler().redirect_request(
                request,
                None,
                302,
                "Found",
                {},
                "http://artifact.example.invalid/signed-artifact",
            )

    def test_87_dispatch_live_resolves_to_live_mode(self):
        resolved = self._resolve_execution("workflow_dispatch", "live-read-only-pilot", "first")
        self.assertEqual("live-read-only-pilot", resolved["resolved_mode"])

    def test_88_dispatch_demo_resolves_to_demo_mode(self):
        resolved = self._resolve_execution("workflow_dispatch", "demo", "first")
        self.assertEqual("demo", resolved["resolved_mode"])
        self.assertEqual("demo", resolved["resolved_artifact_kind"])

    def test_89_schedule_resolves_to_live_mode(self):
        resolved = self._resolve_execution("schedule")
        self.assertEqual("live-read-only-pilot", resolved["resolved_mode"])

    def test_90_schedule_resolves_to_second_sequence(self):
        resolved = self._resolve_execution("schedule")
        self.assertEqual("second", resolved["resolved_sequence"])

    def test_91_schedule_selects_live_artifact(self):
        resolved = self._resolve_execution("schedule")
        self.assertEqual("live", resolved["resolved_artifact_kind"])

    def test_92_schedule_does_not_select_demo_artifact(self):
        resolved = self._resolve_execution("schedule")
        self.assertNotEqual("demo", resolved["resolved_artifact_kind"])

    def test_93_downstream_steps_do_not_read_inputs_mode(self):
        downstream = self._workflow().split("      - name: Run weekly cockpit tests\n", 1)[1]
        self.assertNotIn("inputs.mode", downstream)

    def test_94_downstream_steps_do_not_read_inputs_sequence(self):
        downstream = self._workflow().split("      - name: Run weekly cockpit tests\n", 1)[1]
        self.assertNotIn("inputs.pilot_sequence", downstream)

    def test_95_candidate_schedule_requires_enablement_variable(self):
        workflow = self._workflow()
        self.assertIn(
            "if: github.event_name == 'workflow_dispatch' || (github.event_name == 'schedule' && vars.DBA_WEEKLY_COCKPIT_SCHEDULE_ENABLED == 'true')",
            workflow,
        )

    def test_96_schedule_disabled_notice_remains(self):
        workflow = self._workflow()
        self.assertIn("schedule-disabled:", workflow)
        self.assertIn(
            "if: github.event_name == 'schedule' && vars.DBA_WEEKLY_COCKPIT_SCHEDULE_ENABLED != 'true'",
            workflow,
        )

    def test_97_live_upload_uses_resolved_artifact_kind(self):
        self.assertIn(
            "if: steps.resolve.outputs.resolved_artifact_kind == 'live'",
            self._workflow(),
        )

    def test_98_demo_upload_uses_resolved_artifact_kind(self):
        self.assertIn(
            "if: steps.resolve.outputs.resolved_artifact_kind == 'demo'",
            self._workflow(),
        )

    def test_99_resolver_fails_closed_for_unsupported_event(self):
        with tempfile.NamedTemporaryFile(mode="r+", encoding="utf-8") as output:
            result = subprocess.run(
                ["/bin/bash", "-euo", "pipefail", "-c", self._resolver_script()],
                env={
                    "GITHUB_OUTPUT": output.name,
                    "EVENT_NAME": "push",
                    "DISPATCH_MODE": "",
                    "DISPATCH_SEQUENCE": "",
                },
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Unsupported event", result.stderr)

    def test_100_workflow_permissions_remain_read_only(self):
        permissions = self._workflow().split("permissions:\n", 1)[1].split("\njobs:\n", 1)[0]
        self.assertNotIn("write", permissions)
        for permission in ("contents", "actions", "issues", "pull-requests", "security-events"):
            self.assertIn(f"  {permission}: read", permissions)

    def test_101_all_workflow_actions_remain_pinned_to_full_sha(self):
        references = re.findall(r"^\s*uses:\s*\S+@([0-9a-f]+)\s*$", self._workflow(), re.MULTILINE)
        self.assertGreaterEqual(len(references), 2)
        for reference in references:
            self.assertRegex(reference, r"^[0-9a-f]{40}$")

    def test_102_workflow_contains_no_mutating_or_deployment_command(self):
        workflow = self._workflow().lower()
        for forbidden in (
            "git commit",
            "git push",
            "gh issue",
            "gh pr ",
            "create-pull-request",
            "create-release",
            "deploy-pages",
        ):
            self.assertNotIn(forbidden, workflow)

    def test_103_manual_first_and_second_sequences_remain_supported(self):
        first = self._resolve_execution("workflow_dispatch", "live-read-only-pilot", "first")
        second = self._resolve_execution("workflow_dispatch", "live-read-only-pilot", "second")
        self.assertEqual("first", first["resolved_sequence"])
        self.assertEqual("second", second["resolved_sequence"])

    def test_104_existing_memory_matching_regressions_remain_registered(self):
        test_source = Path(__file__).read_text(encoding="utf-8")
        for test_number in range(64, 69):
            self.assertRegex(test_source, rf"def test_{test_number}_")

    def test_105_current_repository_client_uses_github_token(self):
        with mock.patch.dict(
            "os.environ",
            {"GITHUB_TOKEN": "CURRENT_FAKE_TOKEN", "DBA_COCKPIT_READ_TOKEN": "PRIVATE_FAKE_TOKEN"},
            clear=True,
        ):
            adapter = GithubReadOnlyAdapter()
        request = adapter.current_repository_api._request("repos/joy7758/digital-biosphere-architecture-specification")
        self.assertEqual("Bearer CURRENT_FAKE_TOKEN", request.get_header("Authorization"))

    def test_106_private_client_uses_dedicated_cross_repository_token(self):
        with mock.patch.dict(
            "os.environ",
            {"GITHUB_TOKEN": "CURRENT_FAKE_TOKEN", "DBA_COCKPIT_READ_TOKEN": "PRIVATE_FAKE_TOKEN"},
            clear=True,
        ):
            adapter = GithubReadOnlyAdapter()
        request = adapter.private_cross_repository_api._request("repos/joy7758/titmas")
        self.assertEqual("Bearer PRIVATE_FAKE_TOKEN", request.get_header("Authorization"))

    def test_107_private_client_does_not_use_current_repository_token(self):
        with mock.patch.dict(
            "os.environ",
            {"GH_TOKEN": "CURRENT_FAKE_TOKEN", "DBA_COCKPIT_READ_TOKEN": "PRIVATE_FAKE_TOKEN"},
            clear=True,
        ):
            adapter = GithubReadOnlyAdapter()
        request = adapter.private_cross_repository_api._request("repos/joy7758/hongyan-official-document")
        self.assertNotEqual("Bearer CURRENT_FAKE_TOKEN", request.get_header("Authorization"))

    def test_108_public_client_carries_no_private_or_current_token(self):
        with mock.patch.dict(
            "os.environ",
            {"GH_TOKEN": "CURRENT_FAKE_TOKEN", "DBA_COCKPIT_READ_TOKEN": "PRIVATE_FAKE_TOKEN"},
            clear=True,
        ):
            adapter = GithubReadOnlyAdapter()
        request = adapter.public_repository_api._request("repos/joy7758/titmas-demo")
        self.assertIsNone(request.get_header("Authorization"))

    def test_109_red_yan_repository_is_configured(self):
        project = self._registry_project("RED_YAN_OFFICIAL_DOCUMENT")
        self.assertIsNotNone(project["repository"])
        self.assertEqual("joy7758/hongyan-official-document", project["repository"])

    def test_110_red_yan_uses_private_credential_gated_read_only_mode(self):
        project = self._registry_project("RED_YAN_OFFICIAL_DOCUMENT")
        self.assertTrue(project["cross_repo_credential_required"])
        self.assertTrue(project["scan_authorized"])
        self.assertEqual("CROSS_REPOSITORY_CREDENTIAL_GATED_READ_ONLY", project["source_access_mode"])

    def test_111_titmas_is_classified_as_private_credential_gated(self):
        project = self._registry_project("TITMAS_SUPPORTING_LAYER")
        self.assertEqual("joy7758/titmas", project["repository"])
        self.assertTrue(project["cross_repo_credential_required"])
        self.assertEqual("PRIVATE_REPOSITORY_METADATA", project["data_classification"])
        self.assertEqual("CROSS_REPOSITORY_CREDENTIAL_GATED_READ_ONLY", project["source_access_mode"])

    def test_112_scout_keeps_dedicated_read_only_status_adapter(self):
        project = self._registry_project("TITMAC_SCOUT")
        self.assertEqual("joy7758/titmac-scout", project["repository"])
        self.assertTrue(project["cross_repo_credential_required"])
        self.assertEqual("EXISTING_READ_ONLY_STATUS_ADAPTER", project["source_access_mode"])

    def test_113_all_private_sources_fail_closed_without_dedicated_token(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            adapter = GithubReadOnlyAdapter()
            results = [
                adapter.observe_project(self._registry_project("RED_YAN_OFFICIAL_DOCUMENT"), "2026-08-29T00:00:00Z"),
                adapter.observe_project(self._registry_project("TITMAS_SUPPORTING_LAYER"), "2026-08-29T00:00:00Z"),
                adapter.observe_scout("2026-08-29T00:00:00Z"),
            ]
        for result in results:
            self.assertEqual("NOT_ASSESSED_CREDENTIAL_UNAVAILABLE", result.status)
            self.assertEqual(
                "CROSS_REPO_READ_CREDENTIAL_UNAVAILABLE",
                result.payload.get("reason_code", result.payload.get("reason")),
            )

    def test_114_private_observation_uses_private_client_not_current_client(self):
        current_api = mock.Mock()
        current_api.request_json.side_effect = AssertionError("current repository client used")
        private_api = self._successful_repository_api()
        adapter = GithubReadOnlyAdapter(
            current_repository_api=current_api,
            public_repository_api=self._successful_repository_api(),
            private_cross_repository_api=private_api,
        )
        result = adapter.observe_project(
            self._registry_project("RED_YAN_OFFICIAL_DOCUMENT"),
            "2026-08-29T00:00:00Z",
        )
        self.assertEqual("AVAILABLE", result.status)
        self.assertTrue(private_api.references)
        current_api.request_json.assert_not_called()

    def test_115_public_observation_uses_anonymous_public_client(self):
        public_api = self._successful_repository_api()
        private_api = self._successful_repository_api()
        adapter = GithubReadOnlyAdapter(
            current_repository_api=self._successful_repository_api(),
            public_repository_api=public_api,
            private_cross_repository_api=private_api,
        )
        result = adapter.observe_project(
            self._registry_project("DIGITAL_CELL_DEMO"),
            "2026-08-29T00:00:00Z",
        )
        self.assertEqual("AVAILABLE", result.status)
        self.assertTrue(public_api.references)
        self.assertEqual([], private_api.references)

    def test_116_current_observation_uses_current_repository_client(self):
        current_api = self._successful_repository_api()
        public_api = self._successful_repository_api()
        adapter = GithubReadOnlyAdapter(
            current_repository_api=current_api,
            public_repository_api=public_api,
            private_cross_repository_api=self._successful_repository_api(),
        )
        result = adapter.observe_project(
            self._registry_project("DBA_COCKPIT"),
            "2026-08-29T00:00:00Z",
        )
        self.assertEqual("AVAILABLE", result.status)
        self.assertTrue(current_api.references)
        self.assertEqual([], public_api.references)

    def test_117_repository_allowlist_is_exact(self):
        self.assertEqual(
            {
                "DBA_COCKPIT": "joy7758/digital-biosphere-architecture-specification",
                "RED_YAN_OFFICIAL_DOCUMENT": "joy7758/hongyan-official-document",
                "TITMAS_SUPPORTING_LAYER": "joy7758/titmas",
                "DIGITAL_CELL_DEMO": "joy7758/titmas-demo",
                "TITMAC_SCOUT": "joy7758/titmac-scout",
            },
            ALLOWLIST,
        )

    def test_118_github_api_exposes_get_only(self):
        source = inspect.getsource(GithubApi)
        self.assertIn('method="GET"', source)
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            self.assertNotIn(f'method="{method}"', source)

    def test_119_incomplete_read_fail_closed_regression_remains_registered(self):
        self.assertRegex(Path(__file__).read_text(encoding="utf-8"), r"def test_83_")

    def test_120_redirect_credential_stripping_regressions_remain_registered(self):
        source = Path(__file__).read_text(encoding="utf-8")
        for test_number in range(84, 87):
            self.assertRegex(source, rf"def test_{test_number}_")

    def test_121_tokens_do_not_enter_private_observation_result(self):
        private_api = self._successful_repository_api()
        result = GithubReadOnlyAdapter(
            current_repository_api=self._successful_repository_api(),
            public_repository_api=self._successful_repository_api(),
            private_cross_repository_api=private_api,
        ).observe_project(
            self._registry_project("TITMAS_SUPPORTING_LAYER"),
            "2026-08-29T00:00:00Z",
        )
        serialized = json.dumps(result.to_dict(), ensure_ascii=False)
        self.assertNotIn("CURRENT_FAKE_TOKEN", serialized)
        self.assertNotIn("PRIVATE_FAKE_TOKEN", serialized)
        self.assertNotIn("DBA_COCKPIT_READ_TOKEN", serialized)

    def test_122_credential_routing_preserves_twelve_cells(self):
        registry = json.loads((WEEKLY / "cell-registry.json").read_text(encoding="utf-8"))
        self.assertEqual(12, len(registry["cells"]))

    def test_123_coordinator_remains_orchestration_only(self):
        source = (WEEKLY / "coordinator.py").read_text(encoding="utf-8")
        self.assertNotIn("GithubReadOnlyAdapter", source)
        self.assertNotIn("DBA_COCKPIT_READ_TOKEN", source)

    def test_124_schedule_remains_disabled_by_repository_variable(self):
        workflow = self._workflow()
        self.assertIn("DBA_WEEKLY_COCKPIT_SCHEDULE_ENABLED", workflow)
        self.assertIn("schedule-disabled:", workflow)

    def test_125_no_automatic_fix_pr_merge_or_deploy_is_added(self):
        workflow = self._workflow().lower()
        for forbidden in ("git push", "gh pr ", "create-pull-request", "auto-fix", "deploy-pages"):
            self.assertNotIn(forbidden, workflow)

    def test_126_source_repository_observation_has_no_write_method(self):
        source = inspect.getsource(GithubReadOnlyAdapter)
        for forbidden in ("git push", "git commit", 'method="POST"', 'method="PUT"', 'method="PATCH"', 'method="DELETE"'):
            self.assertNotIn(forbidden, source)

    def test_127_partial_source_coverage_overrides_available_credential_channel(self):
        boundary = _build_pilot_boundary(
            self._synthetic_snapshot(), self._projection_context(not_assessed=1)
        )
        self.assertEqual("PARTIAL", boundary["source_coverage_status"])
        self.assertEqual("LIVE_READ_ONLY_PILOT_PASS_WITH_PARTIAL_COVERAGE", boundary["pilot_status"])

    def test_128_full_pass_requires_all_sources_available(self):
        snapshot = self._synthetic_snapshot(overall_status="PASS")
        boundary = _build_pilot_boundary(snapshot, self._projection_context(not_assessed=0))
        self.assertEqual("COMPLETE", boundary["source_coverage_status"])
        self.assertEqual("LIVE_READ_ONLY_PILOT_PASS", boundary["pilot_status"])

    def test_129_second_run_without_previous_artifact_fails(self):
        snapshot = self._synthetic_snapshot(previous_loaded=False)
        self.assertEqual(
            "LIVE_READ_ONLY_PILOT_FAILED",
            _build_pilot_boundary(snapshot, self._projection_context(not_assessed=1))["pilot_status"],
        )

    def test_130_second_run_without_memory_comparison_fails(self):
        snapshot = self._synthetic_snapshot(memory_compared=False)
        self.assertEqual(
            "LIVE_READ_ONLY_PILOT_FAILED",
            _build_pilot_boundary(snapshot, self._projection_context(not_assessed=1))["pilot_status"],
        )

    def test_131_source_mutation_fails_pilot(self):
        context = self._projection_context(not_assessed=0)
        context["source_mutation"] = True
        self.assertEqual(
            "LIVE_READ_ONLY_PILOT_FAILED",
            _build_pilot_boundary(self._synthetic_snapshot(overall_status="PASS"), context)["pilot_status"],
        )

    def test_132_red_yan_available_is_observed_not_credential_unavailable(self):
        redyan = self._redyan_projection("AVAILABLE")
        self.assertEqual("OBSERVED", redyan["status"])
        self.assertNotIn("凭据不可用", redyan["status_zh"])

    def test_133_red_yan_available_source_label_is_live(self):
        self.assertEqual("LIVE", self._redyan_projection("AVAILABLE")["source_label"])

    def test_134_red_yan_repository_observation_is_not_stable(self):
        self.assertNotEqual("STABLE", self._redyan_projection("AVAILABLE")["status"])

    def test_135_scout_stale_reason_is_not_mapped_to_credential_failure(self):
        scout, blind_spot = self._scout_projection(
            "NOT_ASSESSED_SOURCE_UNAVAILABLE", "SOURCE_STALE"
        )
        self.assertNotIn("CREDENTIAL", scout["reason_code"])
        self.assertEqual("SCOUT_SOURCE_STALE", blind_spot["blind_spot_id"])

    def test_136_scout_stale_human_status_preserves_source_age(self):
        scout, _ = self._scout_projection("NOT_ASSESSED_SOURCE_UNAVAILABLE", "SOURCE_STALE")
        self.assertIn("来源过期", scout["status_zh"])

    def test_137_scout_credential_failure_remains_explicit(self):
        scout, blind_spot = self._scout_projection("NOT_ASSESSED_CREDENTIAL_UNAVAILABLE")
        self.assertIn("凭据不可用", scout["status_zh"])
        self.assertEqual("SCOUT_CREDENTIAL_UNAVAILABLE", blind_spot["blind_spot_id"])

    def test_138_scout_source_drift_preserves_drift_reason(self):
        scout, blind_spot = self._scout_projection("SOURCE_DRIFT")
        self.assertEqual("SOURCE_DRIFT", scout["reason_code"])
        self.assertEqual("SCOUT_SOURCE_DRIFT", blind_spot["blind_spot_id"])

    def test_139_project_category_counts_close_to_total(self):
        snapshot = self._counted_snapshot()
        counts = snapshot["counts"]
        total = sum(counts[key] for key in ("stable", "observed", "attention", "blind_spot", "not_assessed", "other"))
        self.assertEqual(counts["projects"], total)
        self.assertTrue(counts["project_count_sum_match"])

    def test_140_observed_projects_are_counted(self):
        self.assertEqual(3, self._counted_snapshot()["counts"]["observed"])

    def test_141_json_markdown_html_and_boundary_share_partial_coverage(self):
        snapshot = self._synthetic_snapshot()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            boundary = _apply_live_result_projection(
                snapshot, self._projection_context(not_assessed=1), output, "latest.json"
            )
            latest = json.loads((output / "latest.json").read_text(encoding="utf-8"))
            markdown = (output / "latest.md").read_text(encoding="utf-8")
            html = (output / "dashboard.html").read_text(encoding="utf-8")
        expected = "LIVE_READ_ONLY_PILOT_PASS_WITH_PARTIAL_COVERAGE"
        self.assertEqual(expected, boundary["pilot_status"])
        self.assertEqual(expected, latest["pilot_status"])
        self.assertIn(expected, markdown)
        self.assertIn(expected, html)

    def test_142_partial_boundary_cannot_claim_full_pilot_pass(self):
        boundary = _build_pilot_boundary(
            self._synthetic_snapshot(), self._projection_context(not_assessed=1)
        )
        self.assertNotEqual("LIVE_READ_ONLY_PILOT_PASS", boundary["pilot_status"])
        self.assertTrue(boundary["result_projection_consistent"])

    def test_143_not_assessed_ui_status_is_not_normal(self):
        app = (WEEKLY / "ui" / "app.js").read_text(encoding="utf-8")
        self.assertIn('"NOT_ASSESSED"', app)
        self.assertNotRegex(app, r'\["PASS"[^\]]*"NOT_ASSESSED"')

    def test_144_repository_observation_does_not_claim_runtime_acceptance(self):
        redyan = self._redyan_projection("AVAILABLE")
        self.assertIn("不构成红岩运行时验收", redyan["why_zh"])
        self.assertNotEqual("RUNTIME_VERIFIED", redyan["status"])

    def test_145_result_projection_preserves_twelve_cells(self):
        registry = json.loads((WEEKLY / "cell-registry.json").read_text(encoding="utf-8"))
        self.assertEqual(12, len(registry["cells"]))

    def test_146_coordinator_remains_project_agnostic(self):
        source = (WEEKLY / "coordinator.py").read_text(encoding="utf-8")
        for project_id in ("RED_YAN_OFFICIAL_DOCUMENT", "TITMAC_SCOUT"):
            self.assertNotIn(project_id, source)

    def test_147_projection_boundaries_remain_non_mutating(self):
        boundary = _build_pilot_boundary(
            self._synthetic_snapshot(), self._projection_context(not_assessed=1)
        )
        for key in ("auto_fix", "auto_pr", "auto_merge", "auto_deploy", "source_mutation"):
            self.assertFalse(boundary[key])
        self.assertFalse(boundary["schedule_enabled"])
        self.assertFalse(boundary["red_yan_runtime_access"])

    def test_148_synthetic_outputs_contain_no_secret_material(self):
        snapshot = self._synthetic_snapshot()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            _apply_live_result_projection(
                snapshot, self._projection_context(not_assessed=1), output, "latest.json"
            )
            corpus = "\n".join(path.read_text(encoding="utf-8") for path in output.iterdir())
        for forbidden in ("DBA_COCKPIT_READ_TOKEN", "PRIVATE_FAKE_TOKEN", "CURRENT_FAKE_TOKEN"):
            self.assertNotIn(forbidden, corpus)

    def _redyan_projection(self, source_status):
        context = self._cell_context()
        context["source_observations"]["RED_YAN_OFFICIAL_DOCUMENT"] = {
            "status": source_status,
            "source_reference": "https://github.test/redyan/tree/abc",
            "observed_at": "2026-08-29T00:00:00Z",
            "payload": {"revision": "abc"},
        }
        result = DriftCell().run(context)
        return next(item for item in result.outputs["project_updates"] if item["project_id"] == "RED_YAN_OFFICIAL_DOCUMENT")

    def _scout_projection(self, source_status, reason=None):
        context = self._cell_context()
        context["source_observations"]["TITMAC_SCOUT"] = {
            "status": source_status,
            "source_reference": "https://github.test/scout",
            "payload": {"reason": reason} if reason else {},
        }
        result = EnvironmentDiscoveryCell().run(context)
        project = result.outputs["project_updates"][0]
        blind_spot = result.outputs["blind_spots"][0] if result.outputs["blind_spots"] else None
        return project, blind_spot

    @staticmethod
    def _cell_context():
        return {
            "snapshot_mode": "LIVE_READ_ONLY_OBSERVATION_PILOT",
            "as_of": "2026-08-29T00:00:00Z",
            "live_dependency_audit": {
                "audit_status": "AVAILABLE",
                "canonical_retained": {"high_count": 2},
                "observed_result": {"high_count": 1, "high_packages": ["nanoid"]},
            },
            "source_paths": {"live_dependency_audit": "site/package-lock.json"},
            "source_observations": {
                "DBA_COCKPIT": {"status": "AVAILABLE", "source_reference": "dba"},
                "TITMAS_SUPPORTING_LAYER": {"status": "AVAILABLE", "source_reference": "titmas"},
            },
            "public_http_observations": [],
        }

    @staticmethod
    def _projection_context(not_assessed):
        return {
            "pilot_sequence": "second",
            "source_mutation": False,
            "source_observation_summary": {
                "source_mode": "LIVE_READ_ONLY",
                "live_source_success_count": 11 - not_assessed,
                "not_assessed_count": not_assessed,
                "partial_coverage": not_assessed > 0,
                "cross_repo_read_credential": "AVAILABLE",
            },
            "source_observation_records": [],
        }

    @staticmethod
    def _synthetic_snapshot(overall_status="PASS_WITH_NOT_ASSESSED", previous_loaded=True, memory_compared=True):
        projects = [
            {"project_id": "DBA_COCKPIT", "status": "ATTENTION", "status_zh": "需关注"},
            {"project_id": "RED_YAN_OFFICIAL_DOCUMENT", "status": "OBSERVED", "status_zh": "已实时观察仓库状态", "source_label": "LIVE"},
            {"project_id": "TITMAS_SUPPORTING_LAYER", "status": "OBSERVED", "status_zh": "已实时观察", "source_label": "LIVE"},
            {"project_id": "DIGITAL_CELL_DEMO", "status": "OBSERVED", "status_zh": "已实时观察", "source_label": "LIVE"},
            {"project_id": "TITMAC_SCOUT", "status": "NOT_ASSESSED", "status_zh": "来源过期，未评估", "source_label": "STALE"},
        ]
        return {
            "schema_version": "0.1",
            "snapshot_id": "DBA-WEEKLY-SYNTHETIC",
            "observed_at": "2026-08-29T00:00:00Z",
            "overall_status": overall_status,
            "mode": "LIVE_READ_ONLY_OBSERVATION_PILOT",
            "discovery_state": "AVAILABLE",
            "weekly_sentence_zh": "本周共纳入5个项目视图：3个已观察，1个需关注，1个尚未评估。",
            "counts": {"projects": 5, "observed": 3, "attention": 1, "not_assessed": 1, "live_source_success": 10, "source_not_assessed": 1},
            "projects": projects,
            "discoveries": [],
            "decisions": [],
            "blind_spots": [],
            "cell_runs": [{"cell_id": f"CELL_{index}", "status": "PASS"} for index in range(12)],
            "logical_cells": [{"cell_id": f"CELL_{index}", "status": "PASS"} for index in range(12)],
            "dependency_audit_state": {"status": "CONFLICT_REQUIRES_REVIEW"},
            "source_observation_summary": {"source_mode": "LIVE_READ_ONLY", "partial_coverage": True},
            "memory": {
                "status": "COMPARISON_AVAILABLE",
                "PREVIOUS_LIVE_ARTIFACT_LOADED": previous_loaded,
                "MEMORY_COMPARISON_EXECUTED": memory_compared,
            },
        }

    def _counted_snapshot(self):
        context = {
            "as_of": "2026-08-29T00:00:00Z",
            "project_records": self._synthetic_snapshot()["projects"],
            "source_observation_summary": {"live_source_success_count": 10, "not_assessed_count": 1},
        }
        return WeeklyCoordinator(cell_types=[])._snapshot(context, [], 0)

    @staticmethod
    def _registry_project(project_id):
        registry = json.loads((WEEKLY / "project-check-registry.json").read_text(encoding="utf-8"))
        return next(project for project in registry["projects"] if project["project_id"] == project_id)

    @staticmethod
    def _successful_repository_api():
        api = mock.Mock()
        api.references = []

        def request_json(reference, *, allow_404=False):
            api.references.append(reference)
            if "/actions/runs?" in reference:
                return {"workflow_runs": []}
            if "/pulls?" in reference or "/issues?" in reference:
                return []
            if reference.endswith("/releases/latest"):
                return None
            if "/contents/" in reference:
                return {"sha": "blob-sha", "size": 1}
            if "/commits?path=" in reference:
                return []
            if "/commits/" in reference:
                return {
                    "sha": "head-sha",
                    "commit": {
                        "tree": {"sha": "tree-sha"},
                        "committer": {"date": "2026-08-29T00:00:00Z"},
                    },
                }
            if reference.startswith("repos/") and reference.count("/") == 2:
                return {"default_branch": "main"}
            raise AssertionError((reference, allow_404))

        api.request_json.side_effect = request_json
        return api

    @classmethod
    def _resolver_script(cls):
        workflow = cls._workflow()
        step_marker = "      - name: Resolve execution mode\n"
        step_start = workflow.index(step_marker)
        run_marker = "        run: |\n"
        script_start = workflow.index(run_marker, step_start) + len(run_marker)
        lines = []
        for line in workflow[script_start:].splitlines():
            if not line.startswith("          "):
                break
            lines.append(line[10:])
        return "\n".join(lines)

    @classmethod
    def _resolve_execution(cls, event_name, mode="", sequence=""):
        with tempfile.NamedTemporaryFile(mode="r+", encoding="utf-8") as output:
            result = subprocess.run(
                ["/bin/bash", "-euo", "pipefail", "-c", cls._resolver_script()],
                env={
                    "GITHUB_OUTPUT": output.name,
                    "EVENT_NAME": event_name,
                    "DISPATCH_MODE": mode,
                    "DISPATCH_SEQUENCE": sequence,
                },
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                raise AssertionError(result.stderr)
            output.seek(0)
            return dict(line.rstrip("\n").split("=", 1) for line in output if "=" in line)

    @staticmethod
    def _workflow():
        return (DBA.parent / ".github" / "workflows" / "dba-weekly-cockpit.yml").read_text(encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
