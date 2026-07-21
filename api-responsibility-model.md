# DBOS API Responsibility Model v0.1（DBOS 应用程序接口职责模型 v0.1）

状态：`SPECIFICATION_ONLY`

实现状态：`NOT_STARTED`

## 1. Purpose（目的）

本模型把未来 DBOS API 的责任限定为 Data Access（数据访问）、Reference Resolution（引用解析）、State Observation（状态观察）和 Evidence Linking（证据连接）。这些责任不包含智能、执行或治理决定。

## 2. Responsibility Matrix（职责矩阵）

| 责任 | API 可以做什么 | API 必须保留什么 | API 不得做什么 |
|---|---|---|---|
| Data Access（数据访问） | 读取显式允许的规范 Source；返回限定字段 | Source、Version、Scope、观察时间、限制 | 建立第二套事实源；修改历史；绕过访问边界 |
| Reference Resolution（引用解析） | 精确匹配 Type、Namespace、Version 和 Source | `RESOLVED/AMBIGUOUS/UNKNOWN/INVALID` 与诊断 | 从解析推导真实性、授权、Permission 或激活 |
| State Observation（状态观察） | 读取 Lifecycle、Claim、Evidence、Verification 的已记录状态 | 状态来源、版本、时间和冲突 | 应用状态转换；把观察值写成治理决定 |
| Evidence Linking（证据连接） | 追加对象之间的引用关系 | 原始 Evidence Owner、provenance、完整性状态 | 创建事实、覆盖证据、提升 E/V/C 等级 |

## 3. Data Access Boundary（数据访问边界）

Data Access 必须是 source-aware（来源感知）和 scope-bounded（范围受限）的：

- 调用方显式提供或选择允许的 Source；
- 返回值保留 Source 与 Version；
- 缺少 Source 时保持 `UNKNOWN`；
- Cache 和 Index（索引）只是投影，不是规范事实源；
- 数据访问成功不表示内容真实、当前有效或适用于调用方目的；
- API 不得通过扫描整个工作区补造记录。

## 4. Reference Resolution Boundary（引用解析边界）

Reference Resolution 只回答“在指定语义和来源中是否能唯一定位记录”。它不回答：

- 身份是否真实；
- Capability 是否存在或可用；
- Authorization 是否对当前动作有效；
- Evidence 是否充分；
- Verification 是否可信；
- Permission 是否已授予。

解析结果必须继续受 `canonical-reference-resolver-specification.md` 约束。

## 5. State Observation Boundary（状态观察边界）

State Observation 返回 observation（观察），不是 transition（转换）。

允许：

- 查询当前可见状态；
- 返回状态的 Source、Version 和 observed_at（观察时间）；
- 返回 predecessor/successor/revocation references（前序、后继、撤销引用）；
- 报告并存状态为 `CONFLICT`。

禁止：

- 查询即触发状态变化；
- 根据代码、目录或调用频率推导状态；
- 把缓存状态覆盖到规范 Registry；
- 自动解决冲突或选择“最新”记录。

## 6. Evidence Linking Boundary（证据连接边界）

Evidence Linking 可以追加：

- Entity → Evidence Reference；
- Execution → Evidence Reference；
- Claim → Evidence Reference；
- Verification → Evidence Reference；
- Documentation Change → Snapshot Evidence。

它只能形成 relation record（关系记录），不能创建被引用 Evidence、修改其摘要、删除其历史或提升 Evidence Level（证据等级）。

## 7. Request, Decision, and Effect Separation（请求、决定与效果分离）

```text
API Request（接口请求）
  ↓
Validated Record or Reference（已验证结构的记录或引用）
  ↓
Independent Governance Decision（独立治理决定）
  ↓
Separately Applied State Effect（独立应用的状态效果）
```

API Request 的技术接收成功最多表示结构被接受或记录被追加。它不跨越后两个阶段。

| 表面状态 | 允许含义 | 禁止推导 |
|---|---|---|
| `ACCEPTED` | 请求结构被接收 | 已登记、已批准、已授权 |
| `DECLARED` | 调用方声明已记录 | Capability 已验证或可执行 |
| `CREATED` | 惰性记录已形成 | Runtime 已启动或任务已执行 |
| `PENDING` | 等待独立处理 | 将来必然通过 |
| `RESOLVED` | 唯一记录可定位 | 真实、可信、授权或有权限 |

## 8. Ownership Model（职责所有权模型）

| 层 | 负责 | 不负责 |
|---|---|---|
| External Agent Framework（外部智能体框架） | 推理、规划、记忆、工具编排 | DBOS 规范身份和证据历史 |
| External Runtime（外部运行时） | 模型、工具、任务和进程执行 | DBOS 治理决定 |
| DBOS API | 身份引用、状态观察、上下文引用、证据和验证连接 | 推理、执行、Permission、Fitness |
| Governance Authority（治理权力主体） | 明确范围内的决定与授权记录 | 模型推理或证据伪造 |
| SAEE | 演化解释、适应和选择理论 | DBOS 身份、Permission 或 API 运行 |

## 9. Explicit Non-responsibilities（明确非职责）

DBOS API 不负责：

- Agent reasoning（智能体推理）；
- Model inference（模型推理）；
- Autonomous decision（自主决定）；
- Tool calling（工具调用）；
- Chat session（聊天会话）；
- Runtime provisioning（运行时供应）；
- Task scheduling（任务调度）；
- Permission creation（权限创建）；
- Authentication、Credential 或 Token 签发；
- Fitness、Selection 或 Evolution Algorithm；
- 商业价格、合同或生产 SLA。

## 10. Decision Rules（决策规则）

如果一个未来 API 提案满足以下任一条件，必须拒绝进入 DBOS 核心或提交新的架构决策：

- 需要 DBOS 选择模型、规划步骤或调用工具；
- 让一次 API 调用直接激活 Entity；
- 把 Capability Claim 变成 Permission；
- 把 Evidence Reference 变成 Truth；
- 把 Verification 变成独立认证；
- 把 SAEE 的适应度或演化算法放入 DBOS；
- 隐藏 Source、Version、Scope 或失败原因。

```text
RESPONSIBILITY_SCOPE=DATA_ACCESS_REFERENCE_RESOLUTION_STATE_OBSERVATION_EVIDENCE_LINKING
DECISION_EFFECT=NONE
EXECUTION_EFFECT=NONE
PERMISSION_EFFECT=NONE
```
