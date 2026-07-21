# ADR-022: DBOS Validation Result Contract v0.1（DBOS 验证结果契约 v0.1）

状态：`ACCEPTED_FOR_SPECIFICATION`

实施范围：`LOCAL_RESULT_MODEL_ALIGNMENT_ONLY`

## 1. Context（背景）

DBOS 已有 Object Contract（对象契约）、Object Schema（对象模式）和本地 Object Schema Validator（对象模式验证器）。验证器已经稳定产生五种结果，但 v0.1 契约冻结前的临时输出使用 `target_object`、独立 `schema_id/schema_digest`，且没有统一的 `warnings`、`validation_id` 和 `timestamp` 字段。

如果不同 Adapter 或未来 SDK 继续自行命名，将出现 `status/result`、`FAIL/FAILED`、字符串错误/结构化错误等不可互操作表达。

## 2. Decision（决策）

冻结 9 字段 ValidationResult Object（验证结果对象）：

```text
validation_id
validator_version
target_reference
schema_reference
result
errors
warnings
limitations
timestamp
```

冻结五种主状态：

```text
PASS
FAIL
UNKNOWN
CONFLICT
VERSION_MISMATCH
```

错误和警告统一使用 5 字段 Validation Error Object（验证错误对象）。本地代码只做结果封装对齐，不改变 Schema、验证顺序、错误优先级或任何对象状态。

## 3. Null and Provenance Decision（空值与来源决策）

当前 Validator 没有持久化 Validation Registry（验证登记表），也没有获准用系统时钟形成审计时间。因此本地瞬时结果必须输出：

```text
validation_id=null
timestamp=null
```

这避免生成不可追溯 ID 和伪造时间。未来持久化层必须单独授权，并提供 ID、时钟来源、追加式存储和撤销策略。

## 4. Compatibility Decision（兼容决策）

v0.1 契约以本 ADR 为首次冻结点。冻结前的本地临时字段不视为已发布公共 API：

| 临时字段 | v0.1 契约字段 |
|---|---|
| `target_object` | `target_reference` |
| `schema_id` + `schema_digest` | `schema_reference` |
| 不存在 | `validation_id=null` |
| 不存在 | `warnings=[]` |
| 不存在 | `timestamp=null` |

未来再次改名必须进入新的契约版本和兼容性审查。

## 5. Pre-development Agent Consultation（开发前智能体咨询）

问题：如果潜在客户需要多个开发工具统一解释 DBOS 本地验证结果，智能体是否会推荐当前工作？

结论：

```text
RECOMMEND_RESULT_CONTRACT_SPECIFICATION=true
RECOMMEND_LOCAL_VALIDATOR_OUTPUT=true
RECOMMEND_AS_FACT_VERIFICATION=false
RECOMMEND_AS_AUTHORIZATION_SYSTEM=false
RECOMMEND_AS_PRODUCTION_SDK=false
```

推荐原因是字段、状态、错误和禁止效果可以统一并自动测试。不推荐为事实验证、授权系统或生产 SDK，因为外部 Reference resolution、Validation Registry、独立 Verification、跨语言兼容和真实集成证据尚不存在。

## 6. Alternatives Considered（备选方案）

### A. 允许每个开发者自行设计结果

拒绝。状态和错误语义将分裂，无法建立稳定 SDK。

### B. 直接复用 API Error Object（接口错误对象）

拒绝。API 操作错误与对象结构验证属于不同层，且 API 尚未实现。

### C. 自动生成 Validation ID 和当前时间

拒绝。没有持久化、时钟来源和审计边界时会制造不可追溯记录。

### D. 冻结统一结果对象并保留 `null`

接受。它统一开发者语言，同时保持未知、来源和无权力边界。

## 7. Consequences（影响）

正向影响：

- 五种状态具有统一机器语义；
- 错误、警告与限制可以跨工具稳定消费；
- Schema 身份与摘要成为一个明确引用；
- 未来 SDK 可以复用结果契约而不重命名；
- 负向测试可证明结果不产生权限、实体或执行。

限制：

- 当前没有 Validation Registry；
- `validation_id` 与 `timestamp` 仍为 `null`；
- 当前没有跨语言类型或发布包；
- Reference consistency（引用一致性）仍不是外部解析；
- `PASS` 仍不是事实验证或授权。

## 8. Current State（当前状态）

```text
VALIDATION_RESULT_CONTRACT=FROZEN_V0.1
LOCAL_RESULT_MODEL_ALIGNED=true
RESULT_STATUS_COUNT=5
RESULT_FIELD_COUNT=9
ERROR_FIELD_COUNT=5
AUTO_REPAIR=false
PERMISSION_GRANTED=false
ENTITY_CREATED=false
EXECUTION_TRIGGERED=false
SAEE_CALLED=false
SDK_CREATED=false
API_CREATED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
```

本 ADR 不修改 SAEE 或 DBA，不创建 SDK、API、Agent、Runtime、Entity、Permission 或真实 Validation Record。
