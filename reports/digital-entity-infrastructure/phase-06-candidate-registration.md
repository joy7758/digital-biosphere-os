# Phase 6 — Digital Entity Registration Prototype

Stage: `PHASE_6_PASS`

## Files Added

- `entity_support/candidate_registration.py`

## Tests Added

- `tests/entity_support/test_candidate_registration.py`
- Test cases：8

## Validation Result

- Phase tests：`8/8 PASS`
- Validators：`30/30 PASS`

## Security Boundary

- Candidate 使用 `candidate_reference`，不分配 `entity_id` 或 canonical identity（规范身份）。
- Entity Proposal、Review Status、Registration Request 保持分离。
- Registration Request 仅支持 `NOT_SUBMITTED/PENDING/REJECTED`；不能在原型中批准并落地 Entity。
- 请求目标只能是 `REGISTERED`，不能请求或生成 `ACTIVE`。
- 所有候选记录固定 `current_effect=NONE`。

## Created

```text
Agent=false
Runtime=false
EntityInstance=false
EntityIdentity=false
CapabilityInstance=false
Permission=false
ActiveEntity=false
```
