# DBOS Multi-Agent Trust Demo v0.1（DBOS 多智能体可信演示 v0.1）

状态：`LOCAL_DETERMINISTIC_MULTI_ROLE_TRUST_DEMO`（本地确定性多角色可信演示）

运行：

```bash
python3 -m examples.multi_agent_trust_demo.run_demo
```

流程：

```text
Research Agent role simulation（研究智能体角色模拟）
  -> Analysis Agent role simulation（分析智能体角色模拟）
  -> Review Agent role simulation（审查智能体角色模拟）
  -> DBOS Entity / Execution / Evidence Reference representations
  -> DBOS local Validation Results
  -> prepared DBOS-to-SAEE envelope（准备好的 DBOS 到 SAEE 信封）
```

三个角色是固定、纯本地的字符串／映射转换，不是 Agent 实例。Demo 不调用模型、网络、工具或 SAEE，不创建 Runtime、注册 Entity、授予 Capability/Permission，也不产生 canonical Evidence（规范证据）。

每个角色都有一个 `PROPOSED` Entity Object representation（实体对象表示）、一个 `CREATED` Execution Object representation（执行对象表示）和一个 `PENDING` Evidence Reference（证据引用）。这些对象通过本地结构 validator，只表示格式与治理边界成立。

输出中的 `dbos_to_saee_envelope` 是后续 SAEE conformance test（符合性测试）的唯一输入夹具，避免 Demo 与 SAEE 各自创建一份事实。`saee_called=false`；在 SAEE 评价层通过独立审计前，DBOS 不解释或生成 Fitness、Risk 或 Evolution Recommendation。

## Optional SAEE conformance（可选 SAEE 符合性测试）

如果本地同时有包含 Developer Preview adapter（开发者预览适配器）的 SAEE checkout，可以执行只读跨仓库测试：

```bash
python3 -m examples.multi_agent_trust_demo.run_demo \
  > /tmp/dbos-multi-agent-trust-demo-v0.1.json

SAEE_PREVIEW_REPO=/path/to/SAEE
python3 "$SAEE_PREVIEW_REPO/scripts/saee_evaluate_dbos_preview.py" \
  --input /tmp/dbos-multi-agent-trust-demo-v0.1.json
```

预期 SAEE 结果为 fail closed（失败关闭），而不是乐观评分：

```text
Reliability=NOT_ASSESSED
Stability=NOT_ASSESSED
Risk=RISKS_IDENTIFIED
EvolutionRecommendation=HOLD
```

原因是本 Demo 只有 `CREATED` records（记录）和 `PENDING` references（引用），没有完成的 Agent execution（智能体执行）或 verified canonical Evidence（已验证规范证据）。SAEE 命令读取 JSON 并输出评价，不写回 DBOS。

```text
ROLE_SIMULATION_NE_AGENT_INSTANCE=true
OBJECT_REPRESENTATION_NE_ENTITY_REGISTRATION=true
EXECUTION_RECORD_NE_EXECUTION_ENGINE=true
EVIDENCE_REFERENCE_NE_TRUTH=true
VALIDATION_NE_VERIFICATION=true
SAEE_CALLED=false
PERMISSION_GRANTED=false
```
