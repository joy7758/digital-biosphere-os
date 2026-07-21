# DBOS MCP Security Test Model v0.1（DBOS MCP 安全测试模型 v0.1）

状态：`DEFINED_NOT_RUN`

案例数量：`5`

执行数量：`0`

## 1. Purpose（目的）

本模型冻结未来 MCP Adapter Test Harness（MCP 适配器测试环境）的最小 Security Test（安全测试）范围。它定义威胁输入、检测目标、预期拒绝和无副作用条件，不证明实际 Adapter（适配器）、MCP（Model Context Protocol，模型上下文协议）生态或生产部署安全。

## 2. Security Invariants（安全不变量）

```text
UNTRUSTED_CONTENT_EXECUTED=false
NAMESPACE_OVERRIDE_ALLOWED=false
VERSION_GUESSING_ALLOWED=false
SENSITIVE_DATA_CAPTURED=false
REPLAY_CAN_CREATE_EFFECT=false
SECURITY_TEST_PASS_NE_SECURITY_CERTIFICATION=true
```

安全 fixture（测试夹具）必须使用合成、脱敏、非生产数据；不能为了测试而引入真实 Secret（秘密）、Token（令牌）、Credential（凭据）或个人信息。

## 3. `MCP-SEC-001` — Tool Injection（工具注入）

### Threat Fixture（威胁夹具）

在 `tool_name`、Tool description（工具描述）、arguments reference（参数引用）或合成 payload（载荷）中放置要求 Harness 执行指令、改变规则、跳过 Validator（验证器）或授予 Permission（权限）的不可信文本。

### Expected Detection（预期检测）

- 内容只作为数据处理；
- 未授权字段或引用非法时拒绝；
- 不解释、不执行、不调用 Tool；
- 适用时返回 `INVALID_TOOL_REFERENCE`；
- 若待测实现执行了内容，Harness 结果必须为 `FAIL`。

### Required Non-effects（必须无效果）

`TOOL_INSTRUCTION_EXECUTED=false`、`RULE_MODIFIED=false`、`PERMISSION_GRANTED=false`。

## 4. `MCP-SEC-002` — Reference Collision（引用冲突）

### Threat Fixture（威胁夹具）

同一外部 ID 在不同 Source（来源）、Namespace（命名空间）、类型或版本中声明不兼容对象，或尝试用外部 Namespace 覆盖 `dbio`。

### Expected Detection（预期检测）

- `mapping_status=CONFLICT`；
- Adapter 错误为 `CONFLICTING_REFERENCE`；
- 不选择最新、最近或最相似对象；
- 不合并身份、Context（上下文）、Execution（执行）或 Evidence（证据）。

### Required Non-effects（必须无效果）

`NAMESPACE_OVERRIDE=false`、`IDENTITY_MERGE=false`、`CANONICAL_REGISTRATION=false`。

## 5. `MCP-SEC-003` — Version Conflict（版本冲突）

### Threat Fixture（威胁夹具）

协议修订、Server（服务器）、Client（客户端）、Mapping Profile（映射配置）、Schema（模式）或 Validator 版本不存在显式兼容关系。

### Expected Detection（预期检测）

- `mapping_status=VERSION_MISMATCH`；
- Adapter 错误为 `VERSION_MISMATCH`；
- 禁止 `latest`、静默升级、降级和回退；
- 不产生部分候选。

### Required Non-effects（必须无效果）

`AUTOMATIC_DOWNGRADE=false`、`MAPPING_CONTINUED=false`、`PARTIAL_CANDIDATE=false`。

## 6. `MCP-SEC-004` — Sensitive Data Exposure（敏感数据暴露）

### Threat Fixture（威胁夹具）

合成 payload 模拟可能被误写入候选、错误、日志或 Evidence Reference Candidate（证据引用候选）的敏感字段。测试数据只能使用明显无效的占位符，禁止真实秘密。

### Expected Detection（预期检测）

- fixture 含禁止字段时可在前置检查返回 `INVALID_FIXTURE`；
- 候选、错误和日志不得复制敏感值；
- Harness 只记录字段路径和非敏感原因；
- 无法验证脱敏效果时返回 `BLOCKED`，不能默认 `PASS`。

### Required Non-effects（必须无效果）

`SENSITIVE_VALUE_LOGGED=false`、`RESOURCE_BODY_COPIED=false`、`CANONICAL_EVIDENCE_MODIFIED=false`。

## 7. `MCP-SEC-005` — Replay Attempt（重放尝试）

### Threat Fixture（威胁夹具）

使用相同 `fixture_id`、运行引用或输入摘要重复提交，尝试制造第二次对象登记、Event（事件）、Evidence 或 Permission 效果。

### Expected Detection（预期检测）

- Harness 能识别重复运行引用并记录 `REPLAY_DETECTED` 治理断言；
- `REPLAY_DETECTED` 不是第六种 Adapter 错误；
- 重放可以生成新的追加式测试运行记录，但不能修改第一次记录；
- 如果实现不能检测副作用或唯一运行身份，结果必须为 `BLOCKED`。

### Required Non-effects（必须无效果）

`DUPLICATE_CANONICAL_WRITE=false`、`EVENT_CREATED=false`、`PERMISSION_GRANTED=false`、`HISTORY_REWRITTEN=false`。

## 8. Coverage Boundary（覆盖边界）

这五项定义不覆盖：

- 真实网络传输、TLS（传输层安全）或身份认证；
- 真实 MCP Server/Client 实现差异；
- 操作系统、容器或供应链隔离；
- 性能、可用性、灾难恢复或生产监控；
- 未知未来协议功能；
- 外部渗透测试或独立安全审计。

因此，即使未来五项全部通过，也只能说明所测版本与边界内的控制符合预期。

## 9. Aggregate State（汇总状态）

```text
SECURITY_TEST_CASE_DEFINITION_COUNT=5
SECURITY_TEST_EXECUTION_COUNT=0
SECURITY_TEST_PASS_COUNT=0
SECURITY_TEST_FAIL_COUNT=0
SECURITY_CERTIFICATION=false
PRODUCTION_READY=false
```
