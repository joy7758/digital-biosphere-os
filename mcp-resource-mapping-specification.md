# DBOS MCP Resource Mapping Specification v0.1（DBOS MCP 资源映射规范 v0.1）

状态：`FROZEN_FOR_SPECIFICATION_V0.1`

映射实例：`0`

## 1. Purpose（目的）

本规范定义未来 Adapter 如何把调用方提供的 MCP Resource（MCP 资源）引用转换为 Evidence Reference Candidate（证据引用候选）。它不读取 Resource 正文、不创建 Evidence，也不判断 Evidence Truth（证据真相）。

```text
RESOURCE_NE_EVIDENCE_OBJECT=true
RESOURCE_NE_EVIDENCE_TRUTH=true
RESOURCE_ACCESS_NE_SOURCE_AUTHENTICITY=true
```

## 2. Required Input Fields（必需输入字段）

| 字段 | 语义 | 约束 |
|---|---|---|
| `resource_reference` | 稳定 Resource ID 或 URI 引用 | 不因可访问而成为 Evidence |
| `source` | Resource 声明来源 | 必须可归属，不能默认为 Server Owner |
| `version` | Resource 自身或声明版本 | 与 MCP 修订和 DBOS 对象版本分离 |
| `origin` | Resource 最初生成或持有方引用 | 重定向、镜像或缓存不能覆盖 Origin |
| `server_reference` | 暴露 Resource 的 Server 引用 | 不自动等于 Source 或 Origin |
| `execution_reference` | 既有 Execution Reference（执行引用） | 缺失时不能形成 Evidence Reference Candidate |
| `integrity_status` | Source 声明的完整性状态 | v0.1 只允许 `UNKNOWN/PENDING` |
| `mcp_protocol_revision` | 精确 MCP 修订 | 禁止默认最新 |
| `mapping_profile_version` | 精确 Resource 映射配置版本 | 必须与修订和字段形状匹配 |
| `limitations` | 未验证真实性、相关性和范围 | 至少一项 |

`source`、`version` 和 `origin` 必须分别保留。三者不能从 URI host（统一资源标识符主机）、Server 名称、网络凭据或缓存位置自动推导。

## 3. Eligibility Rules（候选资格规则）

必须同时满足：

- Resource 引用在声明 Namespace 中稳定且类型明确；
- Source、Origin、Version 和 Server 引用完整且无冲突；
- 存在既有 `EXECUTION` 类型 Reference Object；
- 调用方显式声明 Resource 与该 Execution 的关系；
- `integrity_status` 未超过现有 Source 证据；
- Mapping Profile 支持该 MCP 修订和 Resource 形状；
- 不需要读取、复制、哈希、签名或解释 Resource 内容即可映射。

没有 `execution_reference` 时，输出只能保留外部 `RESOURCE` 引用并返回 `UNKNOWN_RESOURCE`；不能为了满足对象契约而补建 Execution。

## 4. Field Mapping Rules（字段映射规则）

| MCP Resource 输入 | Evidence Reference Candidate 字段 | 规则 |
|---|---|---|
| Resource + Source + Origin + Mapping Profile | `object_id/evidence_id` 的候选来源 | 未来只能使用 Adapter `extension:` Namespace；不是 Canonical Evidence ID |
| 固定目标类型 | `object_type=EVIDENCE_REFERENCE` | 只是引用候选 |
| DBOS 对象契约版本 | `version` | Resource 版本另存于 Source binding |
| `source` | 公共 `source` | 必须和 `source_reference` Owner/Namespace 一致 |
| 固定安全值 | `status=UNKNOWN` | 不自动使用 `DECLARED/VERIFIED` |
| Source 明确提供的时间引用 | `created_at/updated_at` | 缺失保持 `null` |
| 输入与映射限制 | `limitations` | 必须包含“Resource 不等于 Evidence Truth” |
| `execution_reference` | `execution_reference` | 解析不证明 Execution 发生 |
| Resource + Source + Origin 引用 | `source_reference` | 保留 Resource 的外部定位和归属 |
| `integrity_status` | `integrity_status` | 只允许 `UNKNOWN/PENDING`，不提升 E 等级 |

Resource 的外部 `version` 不能覆盖 Evidence Reference Object 的公共 `version`。两个版本轴必须同时记录并可区分。

## 5. Content and Change Boundary（内容与变化边界）

- Adapter 不读取 Resource contents（资源内容）、Embedded Resource（嵌入资源）或 Resource Link（资源链接）的正文；
- URI、MIME type（媒体类型）、size（大小）、digest（摘要）和签名只有 Source 明确提供时才可作为未验证元数据引用；
- Adapter 不生成缺失 digest、timestamp（时间戳）或 signature（签名）；
- Resource 更新必须形成新的外部版本引用，不能覆盖旧候选或历史 Evidence；
- `RESOLVED` 只表示引用唯一可定位，不证明内容真实、完整、相关或充分；
- Resource 不自动获得 E 等级、Verification、Capability 或 Permission。

## 6. Error Mapping（错误映射）

| 条件 | Adapter 错误 |
|---|---|
| Resource、Source、Origin 或 Execution 引用缺失/不可唯一解析 | `UNKNOWN_RESOURCE` |
| Resource ID 在不同 Source、类型或版本中冲突 | `CONFLICTING_REFERENCE` |
| MCP 修订或 Mapping Profile 不支持该 Resource 形状 | `VERSION_MISMATCH` |
| 关联 Context 必需但不可解析 | `UNRESOLVED_CONTEXT` |

## 7. Explicit Non-effects（明确无效果）

```text
RESOURCE_MAPPING_INSTANCE_COUNT=0
EVIDENCE_REFERENCE_OBJECT_CREATED=false
CANONICAL_EVIDENCE_CREATED=false
CANONICAL_EVIDENCE_MODIFIED=false
RESOURCE_CONTENT_READ=false
RESOURCE_HASH_GENERATED=false
EVIDENCE_LEVEL_CHANGED=false
VERIFICATION_CREATED=false
PERMISSION_GRANTED=false
```
