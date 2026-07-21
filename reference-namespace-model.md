# DBOS Reference Namespace Model v0.1（DBOS 引用命名空间模型 v0.1）

状态：`SPECIFICATION_ONLY`

当前 Namespace Registry（命名空间登记表）：`NONE`

## 1. Purpose（目的）

Namespace（命名空间）声明一个 Reference（引用）的语义所有者、语法边界和允许 Source（来源）。它防止 DBOS、外部平台和第三方 Extension（扩展）使用相同字符串却表达不同对象，或由外部系统覆盖 DBOS 规范含义。

Namespace 不是身份、信任、验证、Permission（权限）或 Architecture Authority（架构权力）。Namespace 被登记只表示其语义边界可识别。

## 2. Namespace Classes（命名空间类别）

v0.1 定义三类 Namespace：

```text
DBOS namespace
External namespace
Extension namespace
```

### 2.1 DBOS Namespace（DBOS 命名空间）

Namespace identifier（命名空间标识符）：

```text
dbio
```

`dbio` 是 DBOS 规范引用保留命名空间。只有 DBOS 受治理的规范 Source 和明确版本化决策可以定义其含义。

当前已存在两种语法轮廓：

1. Entity canonical identifier（实体规范标识符）：

   ```text
   dbio://<entity_type>/<name>/<version>
   ```

2. Opaque record identifier（不透明记录标识符）：

   ```text
   dbio:<record_type>:<opaque-id>
   ```

两种语法不能互相转换或推断：`dbio:entity:registration:<digest>` 是登记链产生的不透明 Entity record ID，不自动等于 `dbio://<entity_type>/<name>/<version>` 规范实体 ID。只有明确的 Registration 与 Canonical Registry 写入关系才能连接二者。

DBOS Namespace 不允许第三方：

- 自行 mint（铸造）规范 `dbio` ID；
- 覆盖既有 `dbio` 含义；
- 用 Adapter 输出冒充 DBOS Source；
- 把外部对象自动升级为 DBOS Entity；
- 修改规范 Source 中的历史记录。

### 2.2 External Namespace（外部命名空间）

推荐 Namespace identifier 形式：

```text
external:<authority>
```

`<authority>` 应是稳定、可归因、ASCII 小写的组织、域名或协议标识符。例如仅作语法说明：`external:<domain-or-owner>`。

External Namespace 的 Owner 保留其 ID 语义。DBOS Resolver 只能通过显式 Adapter 或 Source descriptor（来源描述符）查找，不得把外部 ID 重新签发为 `dbio` ID。

External Namespace 可以表达：

- Git hosting（Git 托管）Repository ID；
- LangChain、CrewAI 或其他框架的 Run/Agent/Task ID；
- MCP（Model Context Protocol，模型上下文协议）Server/Tool/Resource ID；
- 云 Runtime、Artifact Registry（工件登记表）或外部 Evidence Store（证据存储）ID；
- 组织内部的既有对象 ID。

External Namespace 的成功解析只证明外部 Source 返回唯一记录，不证明 DBOS 身份、Capability（能力）、Permission、Evidence 等级或 Verification（验证）。

### 2.3 Extension Namespace（扩展命名空间）

推荐 Namespace identifier 形式：

```text
extension:<extension-id>
```

Extension Namespace 用于第三方 Adapter、Validator（验证器）、Tooling（工具）或 Industry Extension（行业扩展）产生的中间引用和映射记录。

Extension 必须声明：

- `extension-id`；
- Owner reference（所有者引用）；
- Version；
- Source repository；
- Reference Types；
- External dependencies；
- Collision policy（冲突策略）；
- Security and privacy boundary（安全与隐私边界）；
- Revocation path（撤销路径）。

Extension Namespace 不能：

- 使用 `dbio` 前缀；
- 定义 DBOS Canonical Entity meaning（规范实体含义）；
- 产生 Permission、Capability Grant（能力授予）或 Entity Activation（实体激活）；
- 覆盖外部 Namespace Owner 的原始 ID；
- 因 Validator `PASS` 获得 Architecture Authority。

## 3. Namespace Descriptor（命名空间描述符）

未来 Namespace registration（命名空间登记）应使用以下概念字段。该字段集合不是当前 schema 或 API：

```text
namespace_id
namespace_class
owner_ref
authority_source
syntax_profile
allowed_reference_types
source_allowlist
case_policy
version_policy
collision_policy
alias_policy
privacy_policy
status
```

安全默认值：

```text
status=PROPOSED
authority_effect=NONE
permission_effect=NONE
trust_effect=NONE
default_namespace=false
network_access=false
```

## 4. Namespace Syntax Rules（命名空间语法规则）

### 4.1 Namespace identifier

- 使用 ASCII 小写字母、数字、点和连字符；
- 类别与标识符之间使用单个冒号；
- 禁止空白、路径分隔符、控制字符和百分号混淆；
- `dbio` 是保留单段 Namespace；
- `external:` 与 `extension:` 后必须有非空 authority/extension ID；
- 不执行 Unicode 相似字符归一化来猜测等价项；可疑输入返回 `INVALID`。

### 4.2 Reference identifier

Resource ID（资源标识符）由 Namespace Owner 定义。Resolver 必须保留其字节语义和大小写策略，禁止未经声明的 lowercasing（转小写）、URL decoding（URL 解码）或路径规范化。

### 4.3 Version

- 每个 Reference Object 必须携带显式 `version`；
- 未解析版本使用 `unresolved`；
- 已知无版本源使用 `unversioned`；
- `latest`、`current`、`main` 或目录修改时间不能替代精确版本；
- `unresolved` 或 `unversioned` 记录可以被唯一定位，但 Resolution Result 必须保留版本限制；
- Resolver 不自动选择 successor 或最高语义版本。

## 5. No Implicit Default（禁止隐式默认）

裸 ID 不得自动归入 `dbio`。调用方必须提供 Namespace，或者由一个显式、版本化的输入 contract（契约）指定 Namespace。

以下均不是 Namespace 证据：

- 当前工作目录；
- Repository 名称；
- Python module（模块）路径；
- 类名或函数名；
- Agent Framework 名称；
- URL host 的外观相似性；
- 文件中出现 `dbio` 字符串。

缺少 Namespace 时，结构完整性检查返回 `INVALID`；如果上层旧契约允许未命名引用，则适配阶段必须显式包装为 `unknown` Namespace 并返回 `UNKNOWN`，不能默认提升。

## 6. Canonical Meaning Protection（规范含义保护）

External 和 Extension Namespace 不能覆盖 DBOS canonical meaning（规范含义）：

```text
external:*  --X--> dbio ownership
extension:* --X--> dbio ownership
```

保护规则：

1. 只有 `registry/entities.yaml` 或明确 successor 能为当前 DBOS Entity Reference 提供规范身份 Source；
2. `registry/agents.yaml` 是兼容视图，不能单独成为规范 Source；
3. 外部或扩展对象与 DBOS Entity 相似时仍是不同对象；
4. External/Extension Source 不得返回 `namespace=dbio`；
5. Resolver 必须把 Source 声明和 Resolution Result 一起返回；
6. Namespace registration 不创建 Entity 或 Canonical ID；
7. Namespace Owner 变更需要追加式治理记录，不能静默替换。

## 7. Alias Model（别名模型）

Alias（别名）是两个引用之间有来源、可撤销的映射关系，不是字符串等价规则。

未来 alias relation 概念字段：

```text
alias_ref
target_ref
relation_type
evidence_ref
declared_by
version
status
revocation_ref
```

允许的关系类型：

- `same_external_object`：两个外部引用声明同一外部对象；
- `maps_to_dbos_entity`：外部对象有证据映射到一个 DBOS Entity；
- `supersedes`：新引用替代旧引用；
- `mirrors`：Source 镜像关系，不改变 Owner。

Alias 规则：

- 默认不跟随 alias；
- 只有调用方显式允许且 alias 已登记时才跟随；
- External → DBOS 映射不把外部 Owner 变成 DBOS Owner；
- 一个 alias 指向多个目标时返回 `AMBIGUOUS`；
- alias 链必须限制深度并检测循环；
- 撤销 alias 后保留历史；
- 路径相同、名称相同或内容摘要相同不能自动生成 alias。

## 8. Collision Model（冲突模型）

### 8.1 Cross-namespace collision（跨命名空间冲突）

相同 `reference_id` 在不同 Namespace 中是不同引用，不构成冲突：

```text
external:<authority-a> / object-1
extension:<adapter-b>  / object-1
```

### 8.2 Same-namespace collision（同命名空间冲突）

同 Namespace、Reference Type、Version 和 `reference_id` 命中多个不同目标时返回 `AMBIGUOUS`。Resolver 不能按文件顺序、更新时间或 Source 距离选一个。

### 8.3 Type collision（类型冲突）

相同 ID 同时作为 Candidate 和 Entity 时仍是两个不同 Reference Object。必须用显式 relation 连接，不能因字符串相同合并身份。

### 8.4 Version collision（版本冲突）

请求版本与目标版本不同且没有显式 alias/successor relation 时：

- 精确版本不存在：`UNKNOWN`；
- Source 对同一版本返回多个目标：`AMBIGUOUS`；
- 版本语法不合法：`INVALID`。

## 9. Source Registration Boundary（来源登记边界）

Namespace Descriptor 可以包含 Source allowlist，但 Source 登记只说明 Resolver 可以查询，不表示 Source 内容真实或独立验证。

未来 Source descriptor 至少需要：

- Source ID；
- Owner reference；
- Namespace；
- supported Reference Types；
- version；
- access mode；
- integrity metadata；
- privacy classification；
- status；
- revocation reference。

任意本地路径、URL、Database 或 MCP Resource 不能因可访问而自动成为规范 Source。

## 10. Framework and Adapter Namespaces（框架与适配器命名空间）

### LangChain

LangChain 外部 Run、Agent、Chain 或 Tool ID 应保留在其 External Namespace。DBOS Adapter 的转换记录使用独立 Extension Namespace；两者都不能生成 `dbio` Entity ID。

### CrewAI

Crew、Agent role（角色）、Task 和 Process ID 保留在 External Namespace。CrewAI Agent 名称不自动建立 DBOS Agent identity（身份）。

### MCP

MCP Server、Tool、Resource 和 Prompt ID 保留在 External Namespace。MCP Adapter 只提供显式映射；Tool 暴露不等于 Capability，Tool 调用不等于 Permission。

## 11. Namespace Lifecycle（命名空间生命周期）

未来 Namespace registration 采用追加式状态：

```text
PROPOSED
  ↓ governance review
REGISTERED
  ↓ source and compatibility evidence
VERIFIED_FOR_DECLARED_SCOPE
  ↓ suspension / replacement
SUSPENDED / SUPERSEDED / RETIRED
```

Namespace 生命周期不改变其引用对象的 Lifecycle，也不自动升级 Entity、Capability、Evidence 或 Verification。

当前没有 Namespace Registry、登记记录或已验证外部 Namespace。本模型不创建它们。

## 12. Security and Privacy（安全与隐私）

- Namespace 不得内嵌 Token、密码、私钥或个人敏感数据；
- Source descriptor 应使用受控引用，不公开凭据；
- External/Extension Adapter 必须拒绝任意 URL、路径穿越和未授权网络访问；
- Namespace collision 诊断应隐藏敏感 Source 内容；
- Cache 不得因 Namespace 注册复制 Evidence 正文；
- Namespace Owner 撤销时应停止新解析，但保留历史结果；
- Namespace 名称的品牌、域名或组织相似性不证明 Owner 身份。

## 13. Developer Rules（开发者规则）

开发者必须：

1. 显式选择 DBOS、External 或 Extension Namespace；
2. 保留外部原始 ID；
3. 为转换创建独立映射关系，不覆盖原 ID；
4. 声明 Version、Source 和 Reference Type；
5. 对 collision、unknown 和 revocation 编写失败关闭处理；
6. 不把 Namespace registration 表述为 DBOS adoption（采用）、身份验证或认证；
7. 不把 Extension Namespace 提升为 DBOS 核心权威。

## 14. Invariants（不变量）

```text
DBOS_NAMESPACE=dbio
DBOS_NAMESPACE_RESERVED=true
EXTERNAL_NAMESPACE_NE_DBOS=true
EXTENSION_NAMESPACE_NE_DBOS=true
NAMESPACE_NE_IDENTITY=true
NAMESPACE_NE_TRUST=true
NAMESPACE_NE_PERMISSION=true
ALIAS_NE_IDENTITY_MERGE=true
NO_IMPLICIT_DEFAULT_NAMESPACE=true
EXTERNAL_CANNOT_OVERRIDE_DBOS_MEANING=true
CURRENT_NAMESPACE_REGISTRY=false
```

## 15. Related Documents（关联文档）

- `canonical-reference-resolver-specification.md`
- `reference-resolution-boundary-rules.md`
- `ADR-017-canonical-reference-resolver.md`
- `developer-extension-model.md`
- `registry/entities.yaml`
- `validation/identity_validator.py`

本模型只定义 Namespace 语义，不创建 Source、Registry、Entity、Agent、Runtime、Capability、Permission、API 或 SDK。
