# DBOS Autonomy Mode Comparison v0.1（DBOS 自主模式比较 v0.1）

状态：`PROPOSED_FOR_REVIEW`

真实模式绑定：`0`

## 1. Comparison Table（比较表）

| 维度 | `APPROVAL_REQUIRED`（请求批准） | `DELEGATED_AUTONOMY`（委托自主） | `FULL_AUTONOMY_WITHIN_SCOPE`（范围内完全自主） |
|---|---|---|---|
| 用户体验 | 每个动作先确认，可见控制最强，交互成本最高 | 用户预先定义规则，常规动作减少打断，例外升级 | 范围内无需逐动作确认，体验最流畅，但前置治理最严格 |
| 风险姿态 | 适合高风险、不可逆、敏感或最终发布动作 | 适合边界稳定、可监测、可撤销的中风险流程 | 只适合精确白名单、资源受限、可撤销且不被其他规则强制逐动作批准的范围 |
| 人工介入 | 每个动作执行前 | 策略批准、阈值/例外/未知/冲突时 | 策略批准、定期复核、异常/撤销/范围变化时 |
| Capability 要求 | 已验证；批准不能替代 | 已验证且范围稳定 | 已验证、固定版本且不能包含强制逐动作批准的危险能力 |
| Permission 要求 | 每个动作均需独立有效 Permission | Policy 和每次动作均不能超出 Permission | 精确 Permission 范围；不能因模式而扩大 |
| Approval（批准）要求 | 事前逐动作批准 | 策略级批准；受限动作逐动作批准 | 策略级批准；其他规则要求时仍逐动作批准 |
| Evidence 要求 | 动作提案、批准、Context、Execution 和结果引用 | Policy 评估、每次动作、例外升级和执行证据 | 每次动作、资源、异常、撤销传播和定期复核证据 |
| 失败处理 | 缺批准即阻断 | 超范围、阈值、未知或冲突即阻断并升级 | 任一边界变化、撤销或 Evidence 缺失即阻断 |
| 撤销响应 | 后续批准停止 | 后续范围内动作停止 | 必须快速传播并停止全部后续范围内动作 |
| 当前实现 | 不存在 | 不存在 | 不存在 |

## 2. User Experience Trade-off（用户体验权衡）

三个模式不是“低级到高级”的能力成熟度，也不是信任分数。它们表达不同的监督成本和风险承担方式：

- `APPROVAL_REQUIRED` 优先保证每次决定可见；
- `DELEGATED_AUTONOMY` 优先减少常规动作中的重复确认；
- `FULL_AUTONOMY_WITHIN_SCOPE` 优先减少严格白名单内的逐动作干预，但需要最强的范围、Evidence、撤销和复核基础。

任何模式都不改变 Agent 的模型、推理、Capability 或 Permission。

## 3. Evidence Minimums（最低证据要求）

### `APPROVAL_REQUIRED`

- action proposal reference（动作提案引用）；
- scoped approval reference（有范围的批准引用）；
- Policy、Capability、Permission 和 Context 引用；
- 执行前后时间关系；
- 结果、失败和限制引用。

### `DELEGATED_AUTONOMY`

- 已批准 Policy 版本和范围；
- 每次 action-to-policy evaluation（动作到策略判定）；
- 阈值、资源和环境状态；
- 例外、升级、批准或阻断记录；
- 外部 Execution 和 Evidence 引用。

### `FULL_AUTONOMY_WITHIN_SCOPE`

- 已批准且未撤销的精确 Policy、Capability 和 Permission；
- 固定环境和资源范围；
- 每次动作、判定、Context、输出、资源与失败引用；
- 撤销传播、漂移检测和定期人工复核材料；
- 任何其他治理层仍要求的逐动作批准。

这些是未来要求，不表示当前 Evidence 存在或达到特定等级。

## 4. Example Application Matrix（示例应用矩阵）

| 动作示例 | 推荐起始模式 | 原因 | 边界 |
|---|---|---|---|
| 本地文献元数据整理 | `DELEGATED_AUTONOMY` | 可白名单、低副作用、可复核 | 数据来源和文件写入仍需 Permission |
| 科研草稿格式检查 | `DELEGATED_AUTONOMY` | 规则明确、结果可人工复核 | 不能自动提交或改作者身份 |
| 论文最终发布 | `APPROVAL_REQUIRED` | 外部、不可轻易撤回、作者责任明确 | 用户批准不能修改历史 Evidence |
| 医疗或金融决定 | `APPROVAL_REQUIRED` | 高风险且可能受额外规则约束 | 本表不是法律或合规判断 |
| 固定测试夹具上的只读检查 | 可评估 `FULL_AUTONOMY_WITHIN_SCOPE` | 精确输入、无外部副作用、资源可控 | 必须具有独立 Permission、停止规则和 Evidence |

示例只说明模式选择方向，不创建 Policy、Agent、Runtime、Permission 或实际授权。

## 5. Mode Transition（模式转换）

模式不能因使用频率、成功次数、Validator `PASS`、用户沉默或 Evidence 数量自动升级。

未来转换必须：

1. 创建新的 Policy 版本；
2. 比较旧/新 Scope、Constraint、Approval 和 Evidence 要求；
3. 记录风险评估和迁移理由；
4. 获得独立人工批准；
5. 明确生效、过期、撤销和回滚路径；
6. 保留旧 Policy 和全部历史决定；
7. 在 Capability、Permission、环境或风险变化时重新评估。

从更严格模式转向更宽模式不能继承旧批准；从更宽模式转向更严格模式不能删除旧执行记录。

## 6. Current State（当前状态）

```text
AUTONOMY_MODE_COUNT=3
AUTONOMY_POLICY_BINDING_COUNT=0
AUTONOMY_MODE_TRANSITION_COUNT=0
AUTONOMY_POLICY_EVIDENCE_COUNT=0
AUTONOMY_POLICY_IMPLEMENTATION=false
AGENT_CREATED=false
RUNTIME_CREATED=false
PERMISSION_GRANTED=false
EXECUTION_CREATED=false
```
