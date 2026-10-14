# TITMAS 一页简介

## 一句话

TITMAS 是面向多智能体关键行动的控制与可验证执行基础设施候选：在动作发生前绑定身份、能力、授权、策略和证据，在动作后生成可验证技术回执与审计材料。

## 解决什么

当 Coding Agent、自动化 Agent 或多 Agent 团队准备合并代码、发布版本、写入数据或对外发送时，团队需要回答：谁提出、谁授权、依据什么、实际发生了什么、结果能否独立复核。

## 四个产品表面

- **Gate**：在 Monitor 中给出 `WOULD_*`，在客户特定 Enforce 中给出有界决定；
- **Receipt**：记录行动、版本、引用和限制的技术执行回执；
- **Audit**：串联主体、授权、决定、执行和核验时间线；
- **Health**：显示身份、边界、证据和回执覆盖，不输出虚假综合分数。

## 首个候选 Offering

Monitor Pilot：一个工作流、1–3 个 Agent、最长 30 天，先用合成数据，不阻断、不执行、不自动批准。当前仍受安全、法律、主体、开票、定价和支持责任人闸门阻塞，尚不可售。

```text
RECEIPT_NE_TRUTH=true
MONITOR_EFFECT=NONE
PRODUCTION_READY=false
```
