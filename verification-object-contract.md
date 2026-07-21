# DBOS Verification Object Contract v0.1（DBOS 验证对象契约 v0.1）

状态：`FROZEN_FOR_SPECIFICATION`

对象实例状态：`NOT_CREATED`

## 1. Definition（定义）

Verification Object（验证对象）是对既有 Verification Record（验证记录）或 Verification Run（验证运行）的受范围投影。它表达验证类型、状态、目标和限制，不执行验证、不伪造结果，也不产生 Permission。

```text
VERIFICATION_OBJECT_NE_VERIFICATION_RUN=true
VERIFICATION_NE_REVIEW_APPROVAL=true
VERIFICATION_NE_PERMISSION=true
```

## 2. Complete Field Set（完整字段集合）

Verification Object 必须包含公共字段：

`object_id`、`object_type`、`version`、`source`、`status`、`created_at`、`updated_at`、`limitations`

以及以下专属字段：

`verification_id`、`target_reference`、`verification_type`、`verification_status`

用户要求的 `limitations` 使用统一公共字段，不重复定义。

## 3. Field Semantics（字段语义）

| 字段 | 语义 | 约束 |
|---|---|---|
| `object_id` | 对象标识 | 必须等于 `verification_id` |
| `object_type` | 核心对象类型 | 必须为 `VERIFICATION` |
| `verification_id` | Verification Record 或 Run 的稳定引用 ID | 不表示验证已运行 |
| `target_reference` | 被验证对象、Claim 或 Evidence 引用 | 不创建或批准目标 |
| `verification_type` | 验证方法类别 | 只能使用受控词表或 `UNKNOWN` |
| `verification_status` | Source 声明的验证状态 | 不由 API 请求自动产生 |
| `status` | Verification Object 记录状态 | `UNKNOWN/DECLARED/SUPERSEDED/REVOKED` |
| `limitations` | 方法、环境、证据和独立性限制 | 必须存在；不能因 `PASS` 省略 |

## 4. Controlled Vocabulary（受控词表）

`verification_type`：

```text
UNKNOWN
SELF_CHECK
AUTOMATED_VALIDATION
REPRODUCIBLE_VERIFICATION
INDEPENDENT_VERIFICATION
CONTINUOUS_VERIFICATION
```

`verification_status`：

```text
UNKNOWN
PENDING
PASS
FAIL
INCONCLUSIVE
REVOKED
```

当前 `entity_support/verification_reference.py` 的安全上限仍为 `PENDING/V0`。本契约列出未来可投影词表，不升级任何现有 Verification Record。

## 5. Result Boundary（结果边界）

`PASS` 只有在公共 `source` 能解析到完整 Verification Record，并且该 Source 记录了 Evidence、Verifier、Method、Scope、Timestamp 和 Limitations 时才可投影。

即使 `verification_status=PASS`，也只表示该方法、输入和范围内的验证结论，不表示：

- Review Approval（复核批准）；
- Certification（认证）；
- Capability Assignment；
- Authorization；
- Permission；
- Production readiness（生产就绪）；
- SAEE Fitness 或 Evolution 结果。

## 6. Validation Rules（验证规则）

必须返回错误的情况：

- `object_id != verification_id`；
- `object_type != VERIFICATION`；
- Target 或 Source 引用缺失；
- `verification_type` 或 `verification_status` 不在受控词表；
- `PENDING` 对象伪造完成时间或已完成结果；
- `PASS` 缺少可解析的 Evidence、Verifier、Method、Scope 或 Limitations；
- `INDEPENDENT_VERIFICATION` 缺少独立性来源；
- 对象包含 Permission、Capability Grant、Entity activation 或 SAEE 决定字段。

## 7. Explicit Non-effects（明确无效果）

```text
VERIFICATION_EXECUTION_EFFECT=NONE
REVIEW_APPROVAL_EFFECT=NONE
CAPABILITY_GRANT_EFFECT=NONE
AUTHORIZATION_EFFECT=NONE
PERMISSION_EFFECT=NONE
SAEE_EVOLUTION_EFFECT=NONE
```
