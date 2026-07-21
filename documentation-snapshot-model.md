# DBOS Documentation Snapshot Model v0.1（DBOS 文档快照模型 v0.1）

状态：`SPECIFICATION_ONLY`

实现状态：`NOT_STARTED`

## 1. Purpose（目的）

Documentation Snapshot（文档快照）把一组明确文档版本固定到可验证的时间边界。它用于回答“哪个版本参与了哪次实验或决定”，而不是把当前工作树重写成历史状态。

```text
PREVIOUS_SNAPSHOT_IMMUTABLE=true
CURRENT_SNAPSHOT_IS_NEW_RECORD=true
CHANGE_EVIDENCE_APPEND_ONLY=true
SNAPSHOT_NE_TRUTH=true
```

## 2. Snapshot Concepts（快照概念）

### 2.1 Previous Snapshot（前一快照）

Previous Snapshot 是变化前已经保留的文档集合。它必须继续保存：

- snapshot identity（快照身份）；
- scope（范围）和 manifest（清单）；
- 每个文档的 `document_id`、版本、路径、摘要和来源；
- capture time（捕获时间）与 capture evidence（捕获证据）；
- 原始验证结果，包括 `FAIL`。

Previous Snapshot 一旦被引用为历史证据，不得因后继文档出现而修改。

### 2.2 Current Snapshot（当前快照）

Current Snapshot 是在新的捕获动作中形成的新记录。`current` 只表示特定比较上下文中的较新版本，不表示全局最新、正确、权威或正式发布。

Current Snapshot 必须：

- 使用新的 `snapshot_id`；
- 重新计算自身 manifest 和摘要；
- 明确捕获范围和排除项；
- 引用所含 Documentation Object；
- 不复用 Previous Snapshot 的 ID 或写入位置；
- 不覆盖 Previous Snapshot 的文件、清单、摘要或时间。

### 2.3 Change Evidence（变化证据）

Change Evidence 由追加式 Change Record 和关系验证材料组成。它解释 Previous Snapshot 与 Current Snapshot 之间已观察到的差异，但不证明变化合理、内容正确或已获授权。

最小关系：

```text
Previous Snapshot
        |
        | preserves previous bytes and hashes
        | （保留前一字节与摘要）
        v
Change Evidence
        |
        | references previous_hash and new_hash
        | （引用前后摘要）
        v
Current Snapshot
```

这个关系是有向追加关系，不是原地替换。

## 3. Conceptual Snapshot Record（概念快照记录）

未来快照记录至少应表达：

| 概念字段 | 语义 |
|---|---|
| `snapshot_id` | 唯一且不可复用的快照 ID |
| `scope` | 被捕获的文档路径与排除规则 |
| `manifest_reference` | 文档对象、版本、大小和摘要清单 |
| `previous_snapshot_reference` | 可选的前一快照引用；不能形成循环 |
| `captured_at` | 含时区的捕获时间 |
| `collector_reference` | 捕获来源的可归因引用 |
| `snapshot_digest` | 快照清单或固定打包内容的摘要 |
| `status` | `CAPTURED`、`SUPERSEDED`、`ARCHIVED` 或 `UNKNOWN` |

这是模型说明，不是已发布 schema、Registry（登记表）或 API。

## 4. Relationship Rules（关系规则）

1. Previous Snapshot 与 Current Snapshot 必须是两个不同记录；
2. Current Snapshot 必须显式引用 Previous Snapshot，不能依赖文件名相同来推断；
3. Change Evidence 必须引用前后 Documentation Object 和摘要；
4. 同一 Previous Snapshot 可以有多个后继；存在分叉时必须保持全部分支并报告歧义；
5. 关系链不能有循环；
6. 删除、移动或归档 Current Snapshot 不能修改 Previous Snapshot；
7. 新实验必须显式选择输入快照，不能隐式使用当前工作树；
8. Snapshot match（快照匹配）只证明被检查字节与所引用摘要一致，不证明内容真实。

## 5. Scope and Retention（范围与保留）

- Full Snapshot（完整快照）覆盖声明范围内全部文档；
- Scoped Snapshot（限定范围快照）只覆盖显式列出的文档；
- 未包含路径必须表达为 `OUT_OF_SCOPE`，不能解释为“未变化”；
- 被排除路径必须保留排除规则和原因；
- `ARCHIVED` 表示长期保留，不表示可以删除；
- 保留期限到期时仍需新的治理决定，不能由验证器自动清理。

## 6. Existing DBOS Snapshot Boundary（既有 DBOS 快照边界）

`evidence/experiments/DBOS-EXP-0001/freeze/` 是已有实验冻结材料，不是本规范新建的文档演化台账。该目录中的 archive（归档包）、manifest、validator manifest（验证器清单）、capture result（捕获结果）和 certificate（证书）必须保持历史字节不变。

当前工作树中的新规范文档与 `README.md` 更新不属于该历史快照。把历史验证器指向当前工作树时出现摘要不匹配，应继续按历史验证边界报告，直到未来另行授权并捕获新的 Current Snapshot 与 Change Evidence。

## 7. Forbidden Operations（禁止操作）

- 以新快照覆盖旧快照路径；
- 修改旧 manifest 中的 `hash` 或文件大小；
- 删除旧快照以消除验证差异；
- 将 symlink（符号链接）、重命名或复制自动声明为版本连续性；
- 把 Current Snapshot 自动设为规范事实真源；
- 由快照创建 Agent、Runtime、Capability 或 Permission。
