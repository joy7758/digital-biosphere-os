---
document_id: DBA-CLEAN-CLONE-VALIDATION-2026-07-21-02
title: Trusted Multi-Agent Infrastructure Developer Preview v0.1 Clean Clone Validation Report
title_zh: 可信多智能体基础设施开发者预览版 v0.1 干净检出验证报告
status: pass-frozen-remote-sources
validation_result: PASS
release_authorized: false
trial_conditionally_authorized: true
trial_execution_authorized: false
validated_at: 2026-07-21T23:17:11+08:00
---

# Clean Clone Validation Report v0.1（干净检出验证报告 v0.1）

## 1. Outcome（结论）

三个最终远端 `main` commit 已在全新隔离目录完成 Clean Clone（干净检出）、依赖准备、
本地测试、Validator（验证器）、Demo（演示）和跨仓库只读评价验证。

```text
DBA_CLEAN_CLONE_PASS=true
DBOS_CLEAN_CLONE_PASS=true
DBOS_TESTS_PASS=true
DBOS_VALIDATORS_PASS=true
DBOS_MULTI_AGENT_DEMO_PASS=true
DBOS_MCP_DEMO_PASS=true
SAEE_PUBLIC_CLEAN_CLONE_PASS=true
SAEE_DBOS_ADAPTER_PASS=true
CROSS_PROJECT_CLEAN_CLONE_PASS=true
DQ_010_TECHNICAL_GATE_PASS=true
TRIAL_EXECUTION_AUTHORIZED=false
DEVELOPER_PREVIEW_RELEASED=false
```

该 `PASS` 证明冻结源码可以从远端重新获得并在限定环境中复验。它不证明匿名 DBOS
访问、外部开发者完成、客户验证、Evidence Truth（证据真值）、生产就绪或正式发布。

## 2. Frozen Remote Sources（冻结远端来源）

| 项目 | 远端引用 | 验证 commit | Clone 边界 |
|---|---|---|---|
| DBA | `joy7758/digital-biosphere-architecture-specification:main` | `91928e3b1096566aad5568124707e3a6cb3a40ca` | public HTTPS clone |
| DBOS | `joy7758/digital-biosphere-os:main` | `0caa2c45e511a82d0dcab778b0ffc3163aac0029` | authenticated clone；repository 保持 private |
| SAEE public layer | `joy7758/SAEE:main` | `2173c258f91aed03fc02c0097d4250a87be703aa` | public HTTPS clone |

三个 clone 初始和验证后 Git worktree（工作树）均为 0 个变更。隔离验证目录是本地可删除
材料，不是 release artifact（发布工件）或 trial package（试用包）。

## 3. Validation Results（验证结果）

| 项目 | 检查 | 结果 | 直接证据边界 |
|---|---|---|---|
| DBA | Markdown links | `PASS` | 99 个 Markdown 文件；317 个本地链接；0 个断链 |
| DBA / DBOS / SAEE | `Apache-2.0` text | `PASS` | 三个根 `LICENSE` 与 Apache 官方 `LICENSE-2.0.txt` 逐字节一致 |
| DBOS | Fresh editable install | `PASS` | 新 venv；安装 `digital-biosphere-os-preview==0.1.0.dev0` |
| DBOS | Test suite | `PASS` | 15 个目录；331/331 tests |
| DBOS | Validator suite | `PASS` | 34/34 validators |
| DBOS | Multi-Agent Trust Demo | `PASS` | 3 个角色、3 个 Execution Record、0 external side effect |
| DBOS | MCP Reference Demo | `PASS` | `demo_contract_satisfied=true`；`real_mcp_connected=false` |
| SAEE | Dependency environment | `PASS` | 新 venv；`jsonschema==4.26.0`、`referencing==0.37.0` |
| SAEE | Public consolidation smoke | `PASS` | 11/11 module mapping；19 negative cases；5/5 deterministic runs |
| SAEE | Minimal public demo | `PASS` | `SAEE_PUBLIC_ABSTRACTION_DEMO: PASS` |
| SAEE | DBOS Adapter tests | `PASS` | 8/8 tests |
| SAEE | Exact public-safe extraction | `PASS` | `2173c25` 中冻结 19 个 Git blob 全部 19/19 匹配 |
| DBOS → SAEE | Read-only evaluation pipeline | `PASS` | `NOT_ASSESSED` / `NOT_ASSESSED` / `HOLD`；`advisory_only=true`；无 authority |

所有 Demo 只使用仓库内 synthetic inputs（合成输入）。未创建真实 Agent、Runtime、
Permission、Entity Instance、Execution Fact、Canonical Evidence 或外部网络服务。

## 4. Command-entry Finding（命令入口发现）

验证中保留了一个具体 onboarding（上手）风险：

- `python3 examples/multi_agent_trust_demo/run_demo.py` 从任意工作目录执行时不能解析顶层
  `examples` package；
- 仓库文档给出的规范入口 `python3 -m examples.multi_agent_trust_demo.run_demo` 从 DBOS
  根目录执行可以通过；
- DBOS → SAEE 管道也必须从 DBOS 根目录生成 Demo，或显式设置 DBOS `PYTHONPATH`。

这不是 Demo 逻辑或契约失败，但外部试用必须以规范模块命令为唯一入口，并收集开发者
是否仍误用直接文件路径的反馈。不得把后续失败静默归为“用户错误”。

## 5. SAEE Boundary Verification（SAEE 边界验证）

精确 19 文件来自审查候选 `2da5b00655f5dfef5506f20490a4d03119fb3d8c`，并在公共
`main@2173c25` 保持相同 blob identity（内容身份）。公共边界只增加：

- DBOS synthetic envelope 的只读 Adapter；
- 已列明 evaluator closure（评价器闭包）；
- Schema、Profile、CLI 和负向测试；
- 公共边界说明与 Apache-2.0。

没有复制 kernel、selection、mutation、lineage、private backend，且 SAEE 输出没有
DBOS writeback（写回）、Decision、Authorization 或 Execution 效果。

## 6. Previous Failed Attempt Preserved（保留前次失败）

本报告的前一版本验证了 DBA 和 DBOS，但 SAEE public `main@e503c22` 缺少 Adapter，结果
为 `FAIL_REQUIRED_SAEE_ADAPTER_MISSING`。该失败没有被解释为通过；`ADR-020` 批准精确
公共安全提取后，才使用新的远端 commits 完成这次后继复验。

```text
PREVIOUS_VALIDATION_RESULT=FAIL
PREVIOUS_FAILURE_REASON=SAEE_PUBLIC_ADAPTER_MISSING
CURRENT_VALIDATION_RESULT=PASS
FAILURE_RECORD_DELETED=false
```

## 7. Remaining Trial Gate（剩余试用闸门）

Clean Clone 技术条件已经满足，但 `DQ-010` 仍不能自动生效。开始外部联系前还必须：

1. 冻结并引用 exact `trial_package_id`；
2. 把 `participant_source` 占位符替换为真实 3–5 名开发者或明确招募渠道；
3. 由协调者确认隐私说明、帮助等级、反馈用途和停止规则随包交付；
4. 对每名参与者单独记录 DBOS private collaborator access（私有协作者访问）。

本报告不授权 external contact（外部联系）、添加协作者、试用执行、tag、正式 GitHub
Release、百度正式发布或客户验证。
