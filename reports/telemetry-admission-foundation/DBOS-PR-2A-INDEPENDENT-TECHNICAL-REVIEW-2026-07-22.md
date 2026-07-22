# DBOS PR-2A Independent Technical Review

```text
decision_reference=DQ-018
review_target=PR-G2A
exact_source_commit=5c52c1c2f44767c0b13b4ac9670425721b9ea0dd
implementation_manifest=sha256:fdda745c3907e35ac92769740f07afc81483be674568879a3c0314c2a09baa51
verdict=RECOMMENDED_FOR_PR_G2A_HUMAN_REVIEW
human_approval=false
full_pr_g2_ready=false
production_ready=false
```

## Review Outcome（审查结果）

独立于原实现路径的对抗性复核发现七类可复现问题，均已在精确源码提交 `5c52c1c2…`
修复并增加负向或恢复测试。修复后，在 DQ-018 授权的离线 metadata-only（仅元数据）
切片内，没有未关闭的 Critical/High 发现。

这是一份 Agent Recommendation（智能体建议），不是 Architecture Authority、Human
Approval、merge、release、deployment 或 production authorization。

## Findings and Closure（发现与关闭）

| ID | finding | closure |
|---|---|---|
| `IR-01` | compatible store backup 把迁移 lineage 错标为 direct `0001` | manifest 改为绑定实际 applied migration checksums，并增加兼容迁移备份／恢复测试 |
| `IR-02` | 仅拒绝最终 symlink，祖先目录 symlink 可逃逸显式 store root | 逐层检查祖先 symlink，并增加负例 |
| `IR-03` | 已存在的非普通 store path 没有显式 fail closed | 仅接受普通文件，并增加负例 |
| `IR-04` | metrics 保存全部 duration tuple，长期运行内存无界增长 | 改为常量空间 observation counter，10,000 次观测测试 |
| `IR-05` | public `ValidationDecision` 可被伪造为 accepted 并绕过 validator | store 将 decision 视为非 authority token，重新验证 normalized envelope |
| `IR-06` | state 与 item counts 可矛盾，且 Python bool 被当作 int | 严格状态／计数一致性与 bool 拒绝测试 |
| `IR-07` | 畸形 restore manifest 可能泄漏原生异常 | 固化 schema/type 检查和稳定 fail-closed 错误 |

## Post-fix Evidence（修复后证据）

- full tests：`531/531 PASS`；focused telemetry：`197/197 PASS`；
- validators：`35/35 PASS`；telemetry validator：`25/25 PASS`，effects `0`；
- focused coverage：`86%`；
- Bandit `1.9.4`：生产切片 5,352 LOC，0 findings；
- `pip-audit 2.10.0`：7 个锁定运行依赖，0 个已知漏洞；
- OTel authorized cases：Semantic `32/32` + Schema/Resource `36/36`；23 个
  DQ-020 cases 保持 `BLOCKED`；
- 两个 clean clone wheel：SHA-256 均为 `24082849…e41`；
- wheel 安装、`pip check`、源码树外导入、migration/profile package data 读取：`PASS`；
- rollback：25/25 acknowledgements，failed source retained，distinct restore，mismatch `0`，
  automatic switch `false`，next gate `HUMAN_SWITCH_REQUIRED`；
- `TA-P001`—`TA-P004` 在新清单上完成；`TA-P005` 一小时画像没有重跑。

## Remaining Production Risks（剩余生产风险）

1. `DQ-019 / PR-G2B` production persistence 尚未实施；
2. `PR-G2T` telemetry deployment integration、`PR-G2I` identity integration、
   `DQ-021 / PR-G2C` federation/durability 均未关闭；
3. DQ-020 的 23 个真实部署用例未授权、未执行；
4. 独立人工安全审查、跨平台锁、Human rollback switch 未完成；
5. 当前性能数据只属于 macOS arm64、CPython 3.12.13、单机 SQLite reference backend，
   不产生 SLO、高可用、容量或生产持久性声明。

## Recommendation（建议）

推荐把精确切片提交给 `PR-G2A Human Review`；不推荐把它称为完整 `PR-G2` 或生产服务。
