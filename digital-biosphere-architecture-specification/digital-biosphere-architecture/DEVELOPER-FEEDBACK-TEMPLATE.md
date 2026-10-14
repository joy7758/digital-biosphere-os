---
document_id: DBA-DEVELOPER-FEEDBACK-TEMPLATE-0.1
title: Trusted Multi-Agent Infrastructure Developer Preview Feedback Template v0.1
status: prepared-session-record-template-trial-not-authorized
trial_execution_authorized: false
---

# Developer Preview Feedback Template v0.1（开发者预览反馈模板 v0.1）

本模板同时是单次 session record（会话记录）。评分规则和 cohort success criteria（批次成功条件）以 [`EXTERNAL-DEVELOPER-TRIAL-PLAN.md`](EXTERNAL-DEVELOPER-TRIAL-PLAN.md) 为准。

## A. Session and source（会话与来源）

```text
trial_id=
trial_package_id=
trial_date=
tester_reference=pseudonymous-id-only
participant_profile=AGENT_DEVELOPER|MCP_DEVELOPER|MULTI_AGENT_FRAMEWORK_USER
prior_internal_project_involvement=false
trial_coordinator_ref=

dba_source_version=
dbos_source_version=
saee_source_version=
clean_clone_validation_reference=
operating_system=
python_version=
uv_version=
```

## B. Workflow result（流程结果）

```text
session_start_timestamp=
demo_success_timestamp=
session_end_timestamp=
time_to_demo_minutes=

installation_result=PASS|FAIL|NOT_RUN
quick_start_result=PASS|FAIL|NOT_RUN
dbos_test_result=PASS|FAIL|NOT_RUN
demo_result=PASS|FAIL|NOT_RUN
saee_evaluation_result=PASS|FAIL|NOT_RUN

intervention_level=0|1|2|3
intervention_count=
intervention_notes=
```

`intervention_level`：`0=none`、`1=clarification`、`2=command_hint`、`3=hands_on_fix`。原始失败必须保留。

## C. Participant comprehension answers（参与者理解原始回答）

以下字段由参与者在 debrief（复盘）前填写：

```text
q1_what_is_dbos=
q2_why_dbos_is_not_agent_framework=
q3_dbos_mcp_relationship=
q4_validation_pass_meaning_and_limits=
q5_saee_hold_stop_and_decision_authority=
```

## D. Reviewer rubric（复核评分）

以下字段由 reviewer 在原始答案冻结后填写：

```text
q1_score=CORRECT|PARTIAL|INCORRECT
q2_score=CORRECT|PARTIAL|INCORRECT
q3_score=CORRECT|PARTIAL|INCORRECT
q4_score=CORRECT|PARTIAL|INCORRECT
q5_score=CORRECT|PARTIAL|INCORRECT
reviewer_reference=
scoring_conflict=false
scoring_conflict_notes=
```

关键语义不是关键词匹配：DBOS 是可信存在／记录基础设施；MCP 是可选接口或传输而非 Authority；Validation `PASS` 不是 Truth；SAEE Recommendation 不是 Decision 或 Execution。

## E. Value signal（价值信号）

```text
current_agent_workflow_problem=
problem_relevance=HIGH|MEDIUM|LOW|NONE
relevance_reason=
concrete_followup_use_case=
next_intent=TRY_AGAIN|TRY_IF_IMPROVED|NOT_RELEVANT
```

这些字段只表示参与者的 problem relevance signal（问题相关性信号），不表示购买、采用或客户验证。

## F. Feedback and failure（反馈与失败）

```text
feedback_category=DOCUMENTATION|INSTALLATION|CONCEPT_MISUNDERSTANDING|EVALUATION_INTERPRETATION|FEATURE_REQUEST|SECURITY_PRIVACY
severity=RELEASE_BLOCKING|HIGH|MEDIUM|LOW
first_failure_command=
first_failure_output_reference=
expected_behavior=
observed_behavior=
suspected_owner=DBA|DBOS|SAEE|UNKNOWN
possible_duplicate_capability=
security_or_privacy_concern=
suggested_minimal_improvement=
```

多个问题使用多个记录，不得把不同 owner 或 severity 合并成一个成功／失败结论。

## G. Safety and truth boundary（安全与事实边界）

```text
agent_created=false
runtime_created=false
permission_granted=false
customer_data_used=false
secret_used=false
historical_evidence_modified=false
external_side_effect_observed=false
participant_is_customer=false
customer_validation_claimed=false
release_authorized=false
```

若任何 `false` 边界实际变为 `true`，立即停止试用并保留失败输出。不要附加 secret（秘密）、客户数据、个人数据或未公开研究材料。

提交反馈不表示采用、认可、认证、购买意向或客户验证。功能建议必须进入 DBA Test-to-Feature Governance（测试到功能治理），不能由反馈直接授权实现。当前模板存在不表示试用已经授权、招募或执行。
