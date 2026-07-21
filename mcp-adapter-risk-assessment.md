# DBOS MCP Adapter Risk Assessment v0.1（DBOS MCP 适配器风险评估 v0.1）

状态：`DESIGN_RISK_REGISTER_ONLY`

真实实现风险评分：`NOT_ASSESSED`

## 1. Assessment Boundary（评估边界）

本文件分析未来 MCP Adapter（MCP 适配器）的已知风险场景，不评估任何现有实现、Server（服务器）、Client（客户端）或部署。当前没有代码、测试流量、供应链清单或生产数据，因此不计算发生概率或剩余风险分数。

## 2. Primary Risks（主要风险）

| 风险 | 典型场景 | 潜在后果 | 必需控制 | 当前状态 |
|---|---|---|---|---|
| Tool Injection（工具注入） | Tool 描述或结果包含要求 Adapter 改规则、读凭据或调用其他工具的指令 | 未授权动作、数据泄露、映射污染 | 所有内容按数据处理；禁止执行；配置与内容隔离；负向测试 | `UNMITIGATED_NO_IMPLEMENTATION` |
| False Capability Mapping（错误能力映射） | Tool 可见、名称相似或一次调用成功被映射为已验证 Capability | 虚假能力、越权或错误治理结论 | `Tool != Capability`；默认禁止 Capability Mapping；单独声明/证据/复核 | `CONTROL_SPECIFIED_NOT_TESTED` |
| Evidence Contamination（证据污染） | Resource 或 Tool result 被复制进规范证据并覆盖来源、摘要或限制 | 历史污染、不可追溯事实、错误验证 | 只产生引用候选；Canonical Evidence 只读；追加版本；独立复核 | `CONTROL_SPECIFIED_NOT_TESTED` |
| Permission Escalation（权限升级） | MCP access token、Server allowlist 或会话授权被转换成 DBOS Permission | 隐式权限、跨边界执行 | 权限系统隔离；凭据不进入对象；Adapter 权力为零 | `CONTROL_SPECIFIED_NOT_TESTED` |

## 3. Additional Risks（其他风险）

| 风险 | 边界要求 |
|---|---|
| Source Spoofing（来源冒充） | Server 自报名称或端点不等于来源认证；需独立 Source evidence |
| Reference Collision（引用冲突） | Tool/Resource/Context 类型和 Namespace 不可合并；冲突返回 `CONFLICT` |
| Version Drift（版本漂移） | 固定七个版本轴；禁止 `latest`；破坏性变化使用新 Mapping Profile |
| Replay or Duplication（重放或重复） | invocation 引用、Source 与序列材料必须可去重；不得重复生成规范事实 |
| Context Confusion（上下文混淆） | session/request/environment 引用必须分离；禁止跨上下文继承权限或来源 |
| Sensitive Data Leakage（敏感数据泄露） | 默认不采集正文、凭据或个人信息；最小元数据与显式授权 |
| Validator Bypass（绕过验证器） | 所有候选必须使用核心 Validator；禁止弱化包装、旧结果缓存或伪造 `PASS` |
| Partial Mapping（部分映射） | 部分成功不得形成部分登记、证据或权限；保留失败报告 |
| Availability Coupling（可用性耦合） | Adapter 或 MCP 不可用不能阻断 DBOS 规范身份与历史证据访问 |

## 4. Risk Acceptance Boundary（风险接受边界）

以下风险不能由 Adapter 维护者自行接受：

- 任何创建 Entity、Agent、Capability Grant 或 Permission 的隐式行为；
- 任何 Canonical Evidence 修改、覆盖或删除；
- 任何 Validator 弱化或 `PASS` 伪造；
- 任何未授权网络、凭据、文件或敏感数据访问；
- 任何把 Tool result 解释为事实验证或认证；
- 任何触发 Runtime、Evolution 或 C/E/V 升级的行为。

这些情况必须阻止实现或运行，而不是仅写入 `limitations`。

## 5. Evidence Required Before Implementation（实现前所需证据）

未来实现提案至少需要：

- 脱敏 MCP input fixture（MCP 输入夹具）与来源许可；
- 精确协议、Server、Client、Adapter 和 DBOS 版本矩阵；
- Tool/Resource/Context 字段映射与未映射字段清单；
- 四项主要风险及其他风险的可复现负向测试设计；
- 凭据、网络、文件和隐私数据流图；
- Canonical Evidence 只读证明；
- 核心 Validator conformance（验证器一致性）计划；
- 供应链 manifest（清单）、License（许可证）、Owner 与安全联系人；
- 撤销、升级、回滚和事件响应流程；
- 独立安全复核与人工授权。

## 6. Stop Rules（停止规则）

出现以下任一情况，未来工作必须停止：

```text
SOURCE_FIXTURE_MISSING=true
VERSION_MATRIX_INCOMPLETE=true
CREDENTIAL_BOUNDARY_UNKNOWN=true
CANONICAL_EVIDENCE_WRITE_PATH_PRESENT=true
VALIDATOR_BYPASS_PRESENT=true
IMPLICIT_PERMISSION_PRESENT=true
IMPLICIT_CAPABILITY_PRESENT=true
UNAUTHORIZED_NETWORK_ACCESS_PRESENT=true
```

当前状态满足多个实现前缺口，因此结论保持：

```text
MCP_ADAPTER_IMPLEMENTATION_READY=false
MCP_ADAPTER_EXECUTION_AUTHORIZED=false
```
