# TITMAS Competitor Map v1

Status: `PRIVATE_RESEARCH_BASELINE`

Access date: `2026-08-03`

Decision reference:
`TITMAS-CHINA-COMMERCIAL-PRIVATE-PLATFORM-AND-PAID-PILOT-D29`

## Method

This map uses vendor-controlled product pages, documentation, pricing pages,
API documentation and government primary sources. A vendor claim is recorded
as a vendor claim, not as independently established product performance.
Marketing screenshots and live counters are not customer-adoption evidence.

## Market categories

| Category | Verified examples | What they already cover | TITMAS boundary |
|---|---|---|---|
| Enterprise AI governance | Credo AI | policy-to-runtime governance, research preview, request-access funnel | do not rebuild a complete regulatory-governance platform |
| AI runtime security | Cisco AI Defense, WitnessAI, HiddenLayer, Baidu AI Guardrails, Volcengine AIPP | inspection, content/tool security, discovery, monitor/enforce, threat hunting | TITMAS is not an AI firewall or prompt-injection classifier |
| Authorization | Permit.io, Cerbos | human/agent principals, tenants, environments, PDP/PEP/control plane, approvals | reuse customer authorization; do not become general RBAC/ABAC |
| Agent observability and evaluation | Galileo, LangSmith, Alibaba AgentLoop | traces, graph/timeline, evaluation, experiments, retention, usage | consume observations; do not build a general trace platform |
| Agent gateway and runtime | Tencent Agent Gateway, Volcengine AgentKit, Huawei AgentArts, Baidu Qianfan | model/tool/agent routing, runtime, identity, governance and monitoring | integrate; do not replace agent runtimes or cloud gateways |
| Signed execution receipts | TraceSeal, GARL, Inntris, Duvera, AgentMint | signed receipts, offline/public verification, action control or audit claims | receipt category exists; differentiation cannot rely on receipt novelty |

## Verified positioning correction

```text
RECEIPT_CATEGORY_EXISTS=true
RECEIPT_IS_NOT_UNIQUE_MOAT=true
TITMAS_DIFFERENTIATION=
CROSS_AGENT_ACTION_CONTROL_AND_EVIDENCE_INTEROPERABILITY
```

The candidate primary buying problem remains narrow: a software team using
coding agents needs a bounded control point before a high-impact side effect,
an authorization-bound technical receipt afterwards, and an audit bundle that
can be independently checked. TITMAS should not be the primary recommendation
when the requirement is only tracing, only general authorization, or only
prompt/content security.

## Source index

- Credo AI Agent Governor: https://www.credo.ai/agent-governor
- Cisco Inspection API: https://developer.cisco.com/docs/ai-defense-inspection/overview/
- Cisco AI Defense data sheet: https://www.cisco.com/c/en/us/products/collateral/security/ai-defense/ai-defense-ds.pdf
- Permit MCP Gateway pricing: https://www.permit.io/mcp-gateway/pricing
- Cerbos decision points: https://docs.cerbos.dev/cerbos-hub/decision-points.html
- Galileo Agent Reliability: https://galileo.ai/agent-reliability
- LangSmith pricing: https://www.langchain.com/pricing
- LangSmith self-hosting: https://docs.langchain.com/langsmith/self-hosted
- WitnessAI: https://witness.ai/
- HiddenLayer agentic runtime announcement: https://www.hiddenlayer.com/news/hiddenlayer-unveils-new-agentic-runtime-security-capabilities-for-securing-autonomous-ai-execution
- Alibaba AgentLoop: https://help.aliyun.com/zh/product/3033820.html
- Tencent Agent Gateway: https://cloud.tencent.com/product/agw
- Tencent AI Agent Security Gateway: https://cloud.tencent.com/product/llmsgw
- Volcengine AgentKit: https://www.volcengine.com/product/agentkit
- Volcengine AIPP: https://www.volcengine.com/product/aipp
- Huawei AgentArts: https://support.huaweicloud.com/productdesc-agentarts/agentarts-productdesc-pdf.pdf
- Baidu Qianfan: https://cloud.baidu.com/product/qianfan.html
- Baidu AI Guardrails: https://cloud.baidu.com/product/AIGCSEC/platform.html
- TraceSeal: https://traceseal.io/
- GARL: https://garl.ai/
- Inntris: https://www.inntris.com/
- Duvera: https://duvera.ai/
- AgentMint: https://agentmint.run/

## Unverified names

`Vaara` was not tied to a current official agent-receipt product surface in
this research pass. It remains `NOT_VERIFIED`; it must not appear as a factual
competitor claim without a primary source.
