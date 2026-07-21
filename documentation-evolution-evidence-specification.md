# DBOS Documentation Evolution Evidence Specification v0.1（DBOS 文档演化证据规范 v0.1）

状态：`SPECIFICATION_ONLY`

实现状态：`NOT_STARTED`

证据台账状态：`NOT_CREATED`

规范角色：Governance Evidence Specification（治理证据规范）

## 1. Purpose（目的）

Documentation Evolution Evidence（文档演化证据）用于解释 DBOS 文档从一个可引用版本变化到另一个可引用版本的过程，同时保持已有实验快照、摘要、报告和验证结果不变。

本规范解决以下问题：

- 当前文档可能晚于某个冻结实验快照；
- 同一路径的内容摘要可能随新版本变化；
- 历史验证器可能继续针对旧快照报告 `FAIL`；
- 开发者和智能体需要区分“旧证据被破坏”与“新版本尚未登记”；
- 文档演化需要可归因、可追踪、可追加的解释，而不能覆盖旧记录。

本规范只定义对象、记录、快照关系和验证语义，不创建实现、Schema（模式）、SDK（软件开发工具包）、API（应用程序接口）或运行时服务。

```text
DOCUMENTATION_CHANGE_NE_HISTORICAL_REWRITE=true
NEW_VERSION_NE_OLD_EVIDENCE_REPLACEMENT=true
HASH_DIFFERENCE_NE_ERROR=true
EVIDENCE_RECORDS_APPEND_ONLY=true
EVIDENCE_NE_TRUTH=true
DBOS_NE_SAEE=true
```

## 2. Scope（范围）

v0.1 适用于 DBOS 仓库内需要版本化解释的治理文档，例如：

- 根目录规范和 ADR（架构决策记录）；
- `README.md`；
- `reports/` 中的报告；
- `evidence/` 中用于说明证据边界的文档；
- `validation/` 中说明验证语义的文档。

本规范不把任意文件变化自动变成证据，不修改 `DBOS-EXP-0001` 的冻结材料，也不声称当前工作树已经具有 Documentation Evolution Ledger（文档演化台账）。

## 3. Normative Principles（规范原则）

### 3.1 Documentation Change ≠ Historical Rewrite（文档变化不等于历史改写）

新文本只能形成新版本或新快照。旧版本的字节、摘要、时间、来源和验证结果必须继续按原始状态保留。

### 3.2 New Documentation Version ≠ Old Evidence Replacement（新文档版本不等于旧证据替换）

新版本可以成为后续工作的当前参考，但不能替换旧实验所引用的文档对象。历史实验仍必须解析到它执行时冻结的版本。

### 3.3 Hash Difference ≠ Error（摘要差异不等于错误）

摘要不同只证明字节不同。它可能表示合法更新、未登记漂移、错误修改或损坏；必须结合来源、变化原因、快照关系和验证结果解释。

### 3.4 Evidence records are append-only（证据记录只追加）

每次变化生成新的 Change Record（变化记录）。纠正错误也必须追加 correction（更正）或 successor（后继）记录，不能编辑或删除旧记录。

### 3.5 Evidence ≠ Truth（证据不等于真相）

记录存在、摘要匹配或作者可归因，都不自动证明文档内容正确、完整、权威或被独立验证。

### 3.6 DBOS ≠ SAEE（DBOS 不等于 SAEE）

DBOS 在本层治理文档对象、版本和证据关系。它不实现 SAEE 的适应度、选择或演化算法，也不把文档更新解释为生态演化。

## 4. Documentation Object（文档对象）

Documentation Object 是某一文档在明确版本上的可引用声明。它不是 Identity Provider（身份提供者），也不创建新的 Digital Entity（数字实体）。

| 字段 | 类型 | 语义 | 约束 |
|---|---|---|---|
| `document_id` | non-empty string（非空字符串） | 文档跨版本的稳定逻辑标识符 | 不能从路径静默推断；不能因重命名自动变化 |
| `path` | repository-relative path（仓库相对路径） | 该版本内容的定位路径 | 禁止绝对路径和越界路径；路径不是身份事实 |
| `version` | explicit version（显式版本） | 被引用的文档版本 | 必须与快照或来源绑定；不能使用“最新”替代 |
| `hash` | digest（摘要） | 该版本字节的内容摘要 | v0.1 格式为 `sha256:<64 lowercase hexadecimal>`；摘要不是真实性结论 |
| `created_at` | timezone-aware timestamp（含时区时间戳） | 该版本记录的形成时间 | 不能回填为未知历史时间；未知必须保持未知 |
| `source_reference` | attributable reference（可归因引用） | 产生或保存该版本的来源 | 来源存在不表示独立验证或权威 |
| `status` | controlled status（受控状态） | 该版本记录的声明状态 | 只能使用下列值；不产生 Permission 或 Lifecycle 晋级 |

`status` 值：

```text
DECLARED
SUPERSEDED
DEPRECATED
ARCHIVED
UNKNOWN
```

- `DECLARED`：版本已声明，未表达内容正确或正式发布；
- `SUPERSEDED`：存在明确后继版本，旧版本仍保留；
- `DEPRECATED`：不建议用于新工作，历史引用仍有效；
- `ARCHIVED`：已转入保留状态，不能被删除；
- `UNKNOWN`：状态证据不足，不得自动推断。

### 4.1 Object invariants（对象不变量）

1. 同一 `document_id` 可以有多个版本，但每个版本必须唯一；
2. 相同 `document_id + version` 不得对应两个不同摘要；
3. 同一路径可以承载后继版本，但路径重用不能覆盖旧快照中的内容；
4. 摘要变化必须由新的 Documentation Object 和 Change Record 表达；
5. `source_reference` 和 `created_at` 缺失时必须保留 `UNKNOWN`，不得根据文件元数据伪造。

## 5. Change Record（变化记录）

Change Record 连接同一文档的两个版本或声明一个新文档。记录是追加式证据，不是修改命令。

| 字段 | 类型 | 语义 | 约束 |
|---|---|---|---|
| `change_id` | unique string（唯一字符串） | 单次变化记录的唯一标识 | 不得复用、覆盖或重新编号 |
| `document_reference` | Documentation Object reference（文档对象引用） | 被创建或变化的文档版本 | 必须可解析；解析不等于验证 |
| `previous_hash` | digest or null（摘要或空值） | 前一版本摘要 | `CREATED` 必须为 `null`；其他类型必须引用已保留版本 |
| `new_hash` | digest（摘要） | 新版本或状态记录所绑定的摘要 | 必须与 Current Snapshot（当前快照）中的字节匹配后才能声明已捕获 |
| `change_reason` | non-empty text（非空文本） | 变化的可解释原因 | 不能只写“hash changed（摘要变化）”作为充分理由 |
| `author_reference` | attributable reference（可归因引用） | 变化声明的责任来源 | 归因不等于认证、授权或内容正确 |
| `timestamp` | timezone-aware timestamp（含时区时间戳） | 记录形成时间 | 不能覆盖原版本时间；未知不得伪造 |

Change Record 还必须明确 `change_type`，取值如下：

```text
CREATED
UPDATED
DEPRECATED
ARCHIVED
```

### 5.1 Change Type（变化类型）语义

- `CREATED`：首次登记文档；`previous_hash=null`；
- `UPDATED`：形成内容不同的后继版本；前后摘要均必须保留；
- `DEPRECATED`：旧版本仍可解析，但不再推荐用于新工作；不得删除内容；
- `ARCHIVED`：版本进入长期保留；不得把归档解释为删除或不可验证。

### 5.2 Change chain（变化链）规则

1. `previous_hash` 必须指向同一 `document_id` 的已存在版本；
2. `new_hash` 必须指向新 Documentation Object；
3. 后一记录必须追加，不能修改前一记录；
4. 分叉必须显式报告为 branch（分支）或 `AMBIGUOUS`，不得任意选择一个“当前”版本；
5. 撤销或纠正必须追加新记录，并用 `source_reference` 指向被纠正记录；
6. Change Record 不授予 Authority（权力）、Capability（能力）、Permission（权限）或发布状态。

## 6. Minimum Evidence Package（最小证据包）

把摘要变化分类为 `EXPECTED_CHANGE` 前，至少需要：

1. 可解析的 Previous Documentation Object（前一文档对象）；
2. 不可变的 Previous Snapshot（前一快照）；
3. 可解析的 Current Documentation Object（当前文档对象）；
4. 新 Current Snapshot（当前快照）及其 manifest（清单）；
5. 追加式 Change Record；
6. 前后摘要、变化原因、作者引用和时间；
7. 对关系完整性进行的验证结果。

缺少任一项时，系统不得从摘要差异自动推断 `EXPECTED_CHANGE`。

## 7. Relationship to Existing DBOS Evidence（与既有 DBOS 证据的关系）

`DBOS-EXP-0001` 的冻结快照和身份材料记录了实验形成时的文档字节。后续 `README.md` 或其他文档变化：

- 不改变该实验的输入；
- 不更新旧 snapshot digest（快照摘要）；
- 不修复旧验证器针对当前工作树产生的 mismatch（不匹配）；
- 不修改 Final Report（最终报告）中已记录的事实；
- 只能在未来授权的文档演化台账中作为新版本追加。

当前规范文件本身是工作树中新建的规范，并不构成已登记的 Documentation Object、Change Record 或新冻结快照。

## 8. Prohibited Effects（禁止效果）

Documentation Evolution Evidence 不得：

- 删除或改写旧 snapshot；
- 修改历史 hash；
- 覆盖旧 report（报告）；
- 自动修复历史 `FAIL`；
- 把任何摘要匹配声明为事实真理；
- 创建 Entity、Agent、Runtime 或 Digital Organism（数字生命体）；
- 授予 Capability、Permission、Authorization 或 Verification 等级；
- 实现 SAEE 适应度、选择或演化逻辑。

## 9. Future Implementation Gates（未来实现闸门）

任何实现都需要新的明确授权，并至少依次完成：

1. 冻结 Documentation Object 和 Change Record schema；
2. 定义 append-only ledger（只追加台账）与并发冲突规则；
3. 定义新快照捕获和保留策略；
4. 建立版本感知验证器及负向测试；
5. 证明旧 `DBOS-EXP-0001` 证据、报告和摘要字节未变；
6. 明确 Canonical Reference Resolver（规范引用解析器）的引用边界；
7. 经人工复核后再决定是否进入实现。

在这些闸门完成前：

```text
CURRENT_DOCUMENTATION_LEDGER=false
CURRENT_VERSION_AWARE_VALIDATOR=false
CURRENT_AUTO_MIGRATION=false
CURRENT_HISTORY_REWRITE=false
```
