# DBOS MCP Test Fixture Model v0.1（DBOS MCP 测试夹具模型 v0.1）

状态：`FROZEN_FOR_SPECIFICATION_V0.1`

实例状态：`EMPTY`

## 1. Purpose（目的）

本模型定义未来 MCP Adapter Test Harness（MCP 适配器测试环境）可读取的 Synthetic Fixture（合成夹具）语义。它不提供实际数据文件，不复刻真实 MCP（Model Context Protocol，模型上下文协议）流量，也不构成 Evidence（证据）。

## 2. Common Fixture Envelope（公共夹具封装）

| 字段 | 类型 | 必填 | 规则 |
|---|---|---:|---|
| `fixture_id` | string | 是 | 测试命名空间内唯一；不能用作 Entity ID |
| `fixture_type` | enum | 是 | `TOOL_CALL_FIXTURE/RESOURCE_FIXTURE/CONTEXT_FIXTURE` |
| `synthetic` | boolean | 是 | 固定为 `true` |
| `fixture_version` | string | 是 | 精确、不可变、禁止 `latest` |
| `mcp_protocol_revision` | string | 是 | 必须匹配未来支持矩阵 |
| `mapping_profile_version` | string | 是 | 必须匹配未来获批 Mapping Profile（映射配置） |
| `source_namespace` | string | 是 | 使用隔离测试命名空间，不得冒充 `dbio` |
| `source_reference` | string | 是 | 合成引用，不认证 Source（来源） |
| `server_reference` | string | 是 | 合成 Server（服务器）引用，不创建 Entity |
| `input_payload` | object | 是 | 只包含类型允许字段 |
| `expected_mapping` | object | 是 | 预期候选、引用或拒绝 |
| `expected_validation` | object | 是 | 预期结构验证状态 |
| `expected_failure` | object/null | 是 | 无预期失败时显式 `null` |
| `limitations` | array[string] | 是 | 至少一项 |

未来实现还必须对未知字段失败关闭；本文件本身不是机器可读 Schema（模式）。

## 3. Tool Call Fixture（工具调用夹具）

用户要求的核心字段：

```text
tool_call_id
tool_name
arguments_reference
source_reference
```

为了形成合规正向测试，未来 fixture 还必须显式提供：

| 字段 | 语义 | 限制 |
|---|---|---|
| `entity_reference` | 既有外部主体引用 | 不创建或认证 Entity（实体） |
| `task_reference` | 既有任务引用 | 不表示任务获授权 |
| `context_reference` | 类型化上下文引用 | 未解析时必须拒绝 |
| `tool_version` | Tool（工具）版本 | 缺失保持未知 |
| `argument_integrity_reference` | 参数完整性引用 | Adapter 不读取参数正文 |

预期输出只能是 Execution Object Candidate（执行对象候选）或拒绝结果，不能是 Execution Result（执行结果）、Capability（能力）或 Permission（权限）。

## 4. Resource Fixture（资源夹具）

用户要求的核心字段：

```text
resource_id
source
version
origin
```

为了形成合规正向测试，未来 fixture 还必须显式提供：

| 字段 | 语义 | 限制 |
|---|---|---|
| `execution_reference` | 既有执行引用 | 不证明执行发生或成功 |
| `integrity_status` | 外部声明的完整性状态 | 不升级为 DBOS Integrity（完整性）结论 |
| `media_type` | 资源类型声明 | Adapter 不读取正文 |
| `access_boundary` | 不访问或披露的边界 | 必须禁止凭据和真实敏感内容 |

预期输出只能是 Evidence Reference Candidate（证据引用候选）或拒绝结果，不能是 Evidence Truth（证据真相）、Canonical Evidence（规范证据）或 Verification（事实验证）。

## 5. Context Fixture（上下文夹具）

用户要求的核心字段：

```text
context_id
namespace
version
source
```

未来 fixture 还必须显式提供：

| 字段 | 语义 | 限制 |
|---|---|---|
| `context_kind` | 上下文的调用方声明类型 | 不宣称 MCP 存在统一顶层 Context 对象 |
| `scope_reference` | 上下文适用范围 | 不产生 Permission |
| `owner_reference` | 外部所有者引用 | 不认证所有者身份 |
| `content_reference` | 内容的惰性引用 | Harness（测试环境）不得读取内容 |

预期输出只能是 DBOS Context Reference（DBOS 上下文引用）或拒绝结果，不能创建 Execution Context（执行上下文）实例。

## 6. Expected Objects（预期对象）

`expected_mapping` 必须包含：

```text
mapping_status
candidate_type
required_preserved_fields
forbidden_fields
authority_effect
permission_effect
limitations
```

其中 `authority_effect=NONE`、`permission_effect=NONE`。`expected_validation` 必须包含 `result`、`required_error_codes`、`validator_required=true` 和限制。

这些是 Assertion Oracle（断言判定基准），不是对象实例、登记记录、真实 Validation Result（验证结果）或 Evidence。

## 7. Namespace and Data Rules（命名空间与数据规则）

- 所有 fixture 使用专用测试 Namespace（命名空间），不得使用 `dbio`；
- 禁止真实 Credential（凭据）、Token（令牌）、Secret（秘密）、个人信息和客户数据；
- 禁止真实可调用 Tool 地址、生产 Resource URI（统一资源标识符）或真实会话标识；
- ID 只在测试套件内稳定，不得解析为 Canonical Reference（规范引用）；
- `origin`、`source` 和 `version` 必须保持原字段身份，不能互相替代；
- 字段缺失、冲突或不支持时必须成为负向 fixture，不能由 Harness 补全。

## 8. Fixture Lifecycle（夹具生命周期）

未来 fixture 状态只允许：

```text
DEFINED
REVIEWED
FROZEN
RETIRED
INVALID
```

`FROZEN` 后内容改变必须生成新 `fixture_id` 或新 `fixture_version` 并保留旧版本。`RETIRED` 不删除历史。当前实例数量为 `0`。

## 9. Non-effects（无效果）

```text
FIXTURE_INSTANCE_COUNT=0
SYNTHETIC_ONLY=true
REAL_MCP_EVENT_COUNT=0
ENTITY_CREATED=false
PERMISSION_GRANTED=false
EXECUTION_TRIGGERED=false
EVENT_CREATED=false
CANONICAL_EVIDENCE_CREATED=false
TRUTH_CLAIM_CREATED=false
```
