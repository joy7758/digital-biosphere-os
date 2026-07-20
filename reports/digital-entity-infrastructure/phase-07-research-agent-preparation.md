# Phase 7 — Research Agent Preparation Layer

Stage: `PHASE_7_PASS`

## Files Added

- `entity_support/research_agent_preparation.py`

## Tests Added

- `tests/entity_support/test_research_agent_preparation.py`
- Test cases：7

## Validation Result

- Phase tests：`7/7 PASS`
- Validators：`30/30 PASS`

## Security Boundary

- `OPERATIONAL_ENTITY` 只是 architecture role classification，不写入 canonical entity type taxonomy。
- `RESEARCH_AGENT` 只是 role metadata，不创建 Agent。
- Capability Profile 仅含五个 declaration template（声明模板），没有 `capability_id`。
- 模板禁止 `entity_id/agent_id/runtime_id/capability_id/permission*` 实例字段。
- Human oversight 固定为必需；发表与研究结论 authority 固定为 `NONE`。

## Created

```text
Agent=false
ResearchAgent=false
Runtime=false
EntityInstance=false
CapabilityInstance=false
Permission=false
ResearchTaskExecution=false
```
