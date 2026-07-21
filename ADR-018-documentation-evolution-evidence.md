# ADR-018: Documentation Evolution Evidence v0.1（文档演化证据 v0.1）

ADR（Architecture Decision Record，架构决策记录）状态：`ACCEPTED_FOR_SPECIFICATION`

实现授权：`NOT_AUTHORIZED`

日期：`2026-07-20`

决策范围：DBOS 文档版本、快照、摘要差异和验证语义

## 1. Context（背景）

DBOS 已使用 `DBOS-EXP-0001` 形成冻结输入、验证器清单、环境锁、事件、证明、证据包和最终报告。实验材料固定了执行时的仓库状态。

实验完成后，DBOS 继续增加 Developer Kit Specification（开发者工具包规范）和 Canonical Reference Resolver Specification（规范引用解析规范），并更新 `README.md` 入口。当前文档因此可能与历史实验身份材料中的大小和摘要不同。

这是文档正常演化和历史证据不可变之间的真实边界问题：如果更新旧摘要，会改写历史；如果永久禁止文档变化，DBOS 无法继续形成公开基础设施规范；如果忽略不匹配，又会损害验证结果的可解释性。

## 2. Problem（问题）

DBOS 需要同时表达：

1. 历史实验使用的文档版本保持不变；
2. 当前文档可以形成新的明确版本；
3. 摘要差异需要证据解释，但不自动表示错误；
4. 新版本不能替代旧证据；
5. 历史 `FAIL` 不能被新文档自动修复；
6. 智能体和开发者必须能确定性地区分版本匹配、历史破坏和预期变化。

## 3. Pre-development Agent Consultation（开发前智能体咨询）

问题：如果潜在客户需要长期维护可审计的治理文档和实验快照，智能体是否会推荐 DBOS 的 Documentation Evolution Evidence Layer（文档演化证据层）？

结论：**推荐规范，暂不推荐实现或生产使用。**

推荐规范的原因：

- 它解决了当前 `README.md` 后续演化与 `DBOS-EXP-0001` 冻结证据之间的真实差异；
- 它使用 agent-readable（智能体可读）的对象、变化类型和三态验证语义；
- 它保持 evidence-bound（证据约束）和 fail-closed（失败关闭）；
- 它避免把摘要差异、文件存在或新版本自动升级为真实性结论；
- 它可以被未来开发者工具、Reference Resolver（引用解析器）和审计流程复用。

暂不推荐实现或生产使用的原因：

- Documentation Object、Change Record 和 Snapshot schema 尚未冻结；
- 还没有 append-only store（只追加存储）、并发分叉处理和保留策略；
- 现有 `execution_chain_validator.py` 是历史精确字节检查，不是版本感知验证器；
- 当前工作树尚未捕获新的文档快照或登记真实 Change Record；
- 没有独立验证、外部采用或生产证据。

## 4. Decision（决策）

DBOS 接受 Documentation Evolution Evidence v0.1 作为纯规范层，包含：

1. 七字段 Documentation Object：`document_id`、`path`、`version`、`hash`、`created_at`、`source_reference`、`status`；
2. 追加式 Change Record：`change_id`、`document_reference`、`previous_hash`、`new_hash`、`change_reason`、`author_reference`、`timestamp`；
3. `CREATED`、`UPDATED`、`DEPRECATED`、`ARCHIVED` 四种 Change Type；
4. Previous Snapshot → Change Evidence → Current Snapshot 的有向关系；
5. `PASS`、`FAIL`、`EXPECTED_CHANGE` 三种验证语义；
6. `EXPECTED_CHANGE` 需要完整前后快照和变化证据，不能从摘要差异自动推断；
7. 历史 evidence、snapshot、hash、report 和 `FAIL` 保持不可变；
8. Evidence、Truth、Authority、Permission 和 SAEE 演化职责严格分离。

本决策不创建当前台账、不登记真实文档对象、不捕获新快照，也不改变任何既有验证结果。

## 5. Alternatives Considered（备选方案）

### A. 更新 `DBOS-EXP-0001` 中的旧摘要

拒绝。它会把后续文档版本写入历史实验输入，构成 Historical Rewrite（历史改写）。

### B. 永久冻结根目录文档，不允许继续更新

拒绝。历史快照应冻结其自身，而不是阻止仓库形成后继版本。

### C. 忽略所有摘要不匹配

拒绝。它会掩盖真实损坏、越权修改和未登记漂移。

### D. 把所有摘要差异自动标记为 `EXPECTED_CHANGE`

拒绝。摘要只证明字节不同，不能说明原因、授权、来源或版本连续性。

### E. 保留旧快照并追加新版本、变化记录和验证运行

接受。这种方式同时保持历史完整性、当前可演化性和可审计解释。

## 6. Consequences（影响）

正向影响：

- 历史实验可以继续复现其原始输入；
- 文档可以形成新版本而不覆盖过去；
- 智能体能区分 `PASS`、`FAIL` 和 `EXPECTED_CHANGE`；
- 摘要差异具有明确的 fail-closed 处理方式；
- 未来开发者生态可引用稳定文档对象和快照关系。

成本与限制：

- 每次受治理变化需要新对象、快照和变化记录；
- 同一路径不再足以表示文档身份和版本；
- 未登记的合法更新仍会在旧验证边界中表现为 `FAIL`；
- 分叉、并发更新、归档和纠正需要额外治理；
- 当前规范不会让历史验证器恢复 `PASS`。

## 7. Relationship to Current Repository（与当前仓库的关系）

本次规范工作：

- 新增四份规范性文档；
- 仅在当前 `README.md` 增加入口和边界说明；
- 不修改 `evidence/`、`reports/`、`validation/` 中的历史材料或代码；
- 不修改 `DBOS-EXP-0001` 的摘要、快照、证书或结果；
- 不创建新的 Agent、Runtime、Capability、Permission 或 Digital Organism；
- 不修改 DBA 或 SAEE 仓库。

因此，旧实验对当前 `README.md` 的精确摘要检查仍可报告 `FAIL`。该结果是被明确保留的历史验证语义。

## 8. Implementation Gates（实现闸门）

未来实现需要新的明确授权，并至少完成：

1. schema 和 ID/Namespace（命名空间）规则冻结；
2. 只追加存储、冲突和更正模型；
3. 快照捕获、保留和隐私边界；
4. 版本感知验证器设计；
5. 历史 `PASS/FAIL` 不变性的负向测试；
6. Canonical Reference Resolver 集成边界；
7. 人工复核、风险评估和实现决定。

在独立授权前：

```text
IMPLEMENTATION_STATUS=NOT_STARTED
DOCUMENTATION_LEDGER_STATUS=NOT_CREATED
HISTORICAL_EVIDENCE_MUTATION=FORBIDDEN
AUTOMATIC_FAIL_REPAIR=FORBIDDEN
```
