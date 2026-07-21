# DBOS Documentation Validation Boundary v0.1（DBOS 文档验证边界 v0.1）

状态：`SPECIFICATION_ONLY`

实现状态：`NOT_STARTED`

## 1. Purpose（目的）

本文定义文档版本、快照和变化证据的验证结果语义。验证只回答限定输入、方法和范围内的结构或一致性问题，不产生真实性、权限、发布或治理结论。

```text
VALIDATION_NE_TRUTH=true
VALIDATION_NE_VERIFICATION_AUTHORITY=true
EXPECTED_CHANGE_NE_HISTORICAL_PASS=true
NO_AUTOMATIC_HISTORY_REPAIR=true
```

## 2. Result Semantics（结果语义）

### 2.1 `PASS`

`PASS` 表示：在声明的验证目标、版本、快照、算法和范围内，所检查字节、摘要、引用及结构满足相应不变量。

`PASS` 不表示：

- 文档内容真实或正确；
- 作者身份已认证；
- 文档获批准、发布或采用；
- 后继版本与历史版本相同；
- Capability、Permission 或 Verification 等级已产生。

### 2.2 `FAIL`

`FAIL` 表示至少一项声明的不变量未满足，例如：

- 引用的文档、快照或变化记录不存在；
- 实际字节与所引用版本的摘要不同；
- 历史 snapshot、hash 或 report 被修改或删除；
- Change Record 不连续、字段缺失或形成循环；
- 摘要发生变化但没有满足最小证据包；
- 试图覆盖旧记录或自动修复历史结果。

`FAIL` 必须保留其原始输入、范围、时间和错误信息。后续修复只能形成新的验证运行，不能编辑旧结果。

### 2.3 `EXPECTED_CHANGE`

`EXPECTED_CHANGE` 表示：相对于 Previous Snapshot，Current Snapshot 的差异已由完整、追加式 Change Evidence 明确声明，并通过关系完整性检查。

它只适用于“版本之间的变化关系”，不是历史快照自身的 `PASS`。必须同时满足：

1. Previous Snapshot 和 Previous Documentation Object 仍可解析且字节未变；
2. Current Snapshot 和 Current Documentation Object 已由新捕获动作形成；
3. `previous_hash` 与 `new_hash` 分别匹配两个快照；
4. Change Record 含变化类型、原因、作者引用和时间；
5. 所有记录均追加形成，没有覆盖历史；
6. 对同一路径或版本的冲突、分叉和未知项已显式报告。

任一条件缺失时，不得仅凭 hash difference（摘要差异）返回 `EXPECTED_CHANGE`。

## 3. Historical Validation Boundary（历史验证边界）

历史验证必须固定其原始：

- Snapshot ID（快照 ID）；
- Documentation Object 版本；
- expected hash（预期摘要）；
- validation method（验证方法）和版本；
- scope（范围）；
- input and output evidence（输入和输出证据）。

当历史验证器拿旧摘要检查当前工作树时，摘要不匹配仍应报告 `FAIL`。新的 Documentation Object 或 `EXPECTED_CHANGE` 记录不能把该历史结果回写为 `PASS`。

未来 version-aware validation（版本感知验证）可以分别表达：

```text
historical_snapshot_integrity=PASS
current_tree_matches_historical_snapshot=FAIL
document_transition=EXPECTED_CHANGE
```

这三个结论可以同时成立，不能合并为一个笼统的成功状态。

## 4. Current DBOS Interpretation（当前 DBOS 解释）

当前 `validation/execution_chain_validator.py` 对 `DBOS-EXP-0001` 身份证据中的文件大小和 SHA-256（安全哈希算法 256 位）做精确比较。`README.md` 在实验冻结后增加新的规范入口，因此：

- 旧实验身份材料继续引用旧 `README.md` 字节；
- 当前工作树不匹配旧身份材料时，现有验证器应继续 `FAIL`；
- 本规范不修改验证器、不更新旧摘要，也不自动创建 `EXPECTED_CHANGE`；
- 只有未来新快照和追加式变化证据完成后，新的版本感知验证运行才能单独报告文档转换状态。

因此，当前历史 `FAIL` 是一个保留的 truth surface（事实状态表面），不是由本规范修复的错误。

## 5. No Automatic Repair（禁止自动修复）

验证器和维护者不得为了得到 `PASS`：

- 把当前摘要写入旧 evidence（证据）；
- 改写旧 snapshot manifest（快照清单）；
- 删除或覆盖旧 report（报告）；
- 重跑后覆盖原验证结果；
- 把所有摘要差异静默归类为 `EXPECTED_CHANGE`；
- 恢复旧文件并声称后继文档从未存在；
- 修改历史时间、作者或来源字段。

正确做法是保留旧结果，追加新版本、快照、变化记录和新验证运行。

## 6. Fail-closed Decision Table（失败关闭决策表）

| 条件 | 结果 | 说明 |
|---|---|---|
| 指定版本字节与摘要匹配，引用完整 | `PASS` | 只对该版本和范围成立 |
| 旧快照自身字节被修改或缺失 | `FAIL` | 历史完整性破坏 |
| 当前字节与旧摘要不同，且无完整变化证据 | `FAIL` | 不得猜测变化原因 |
| 前后快照均保留，变化证据完整且关系检查通过 | `EXPECTED_CHANGE` | 不替代旧版本的 `PASS/FAIL` |
| Source、author 或 timestamp 未知 | `FAIL` 或保持 `UNKNOWN` | 由具体不变量决定，不得补造 |
| 变化证据试图产生 Permission、Capability 或 truth claim（真相声明） | `FAIL` | 超出本层权力边界 |

## 7. Validation Is Not Implementation（验证不等于实现）

本文没有创建验证代码、测试框架、Schema、SDK 或 API。未来实现必须在新的明确授权下冻结输入输出契约、追加式存储和负向测试，并证明不会改写已有 DBOS 证据。
