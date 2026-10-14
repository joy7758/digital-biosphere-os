import type { Locale } from "./site-content";

export type CommercialPageKey =
  | "gate"
  | "receipt"
  | "audit"
  | "health"
  | "design-partner"
  | "private-evaluation"
  | "monitor-pilot"
  | "enforce-pilot"
  | "request-access"
  | "security"
  | "trust-center"
  | "privacy"
  | "terms";

type Section = {
  title: string;
  body: string;
  items?: readonly string[];
};

type PageCopy = {
  eyebrow: string;
  title: string;
  lead: string;
  status: string;
  statusDetail: string;
  sections: readonly Section[];
  primaryLabel: string;
  primaryHref: string;
  secondaryLabel: string;
  secondaryHref: string;
};

export const productKeys = ["gate", "receipt", "audit", "health"] as const;
export const commercialSlugs = [
  "design-partner",
  "private-evaluation",
  "monitor-pilot",
  "enforce-pilot",
  "request-access",
  "security",
  "trust-center",
  "privacy",
  "terms",
] as const;

export function isProductKey(value: string): value is (typeof productKeys)[number] {
  return productKeys.includes(value as (typeof productKeys)[number]);
}

export function isCommercialSlug(value: string): value is (typeof commercialSlugs)[number] {
  return commercialSlugs.includes(value as (typeof commercialSlugs)[number]);
}

const shared = {
  zh: {
    boundary: "当前为私有商业试点候选与公开说明面，不是生产服务、客户采用、认证或法律结论。",
    request: "申请私有评估",
    proof: "查看合成效果证明",
  },
  en: {
    boundary: "This is a private commercial-pilot candidate and public information surface, not a production service, customer adoption, certification, or legal conclusion.",
    request: "Request a private evaluation",
    proof: "View synthetic proof",
  },
} as const;

const pages: Record<Locale, Record<CommercialPageKey, PageCopy>> = {
  zh: {
    gate: {
      eyebrow: "TITMAS GATE / 行动闸门",
      title: "在关键动作发生前，先验证上下文与授权边界",
      lead: "TITMAS Gate 面向代码合并、发布、配置修改、数据写入和外部发送等关键动作，提供 Monitor 与客户特定 Enforce 两种有界路径。",
      status: "SYNTHETIC_REFERENCE_IMPLEMENTED_NOT_DEPLOYED",
      statusDetail: shared.zh.boundary,
      sections: [
        { title: "Monitor Mode", body: "只计算 Shadow Decision，不阻断客户动作。", items: ["WOULD_ALLOW", "WOULD_BLOCK", "WOULD_NEED_APPROVAL", "NOT_ASSESSED"] },
        { title: "Enforce Mode", body: "只在客户书面授权、动作范围、策略、回滚和审批路径全部明确后进入试点。", items: ["ALLOW", "BLOCK", "NEEDS_APPROVAL", "NOT_ASSESSED → BLOCK_OR_HOLD"] },
        { title: "边界", body: "Gate 不是通用授权平台、Agent Runtime、AI 防火墙或结果正确性证明。" },
      ],
      primaryLabel: shared.zh.request,
      primaryHref: "/private-evaluation/",
      secondaryLabel: shared.zh.proof,
      secondaryHref: "/commercial-evaluation/",
    },
    receipt: {
      eyebrow: "TITMAS RECEIPT / 可验证执行回执",
      title: "把行动、来源、决定和限制绑定为可携带技术回执",
      lead: "TITMAS Receipt 记录发生了什么、依据什么、由谁授权以及如何验证，并保留失败、撤销、替代和密钥不可用状态。",
      status: "PRIVATE_REFERENCE_IMPLEMENTED_NOT_AVAILABLE_OFFERING",
      statusDetail: shared.zh.boundary,
      sections: [
        { title: "公开视图", body: "提供不含客户机密的状态、摘要、验证结果和限制说明。" },
        { title: "验证语义", body: "验证只说明声明范围内的结构、完整性和签名状态。", items: ["PASS", "FAIL", "NOT_ASSESSED", "UNVERIFIABLE_KEY_UNAVAILABLE"] },
        { title: "永久边界", body: "Receipt 是技术执行证据记录，不是事实真相、法律证书、合规认证或电子认证服务。" },
      ],
      primaryLabel: "查看验证入口",
      primaryHref: "/commercial-evaluation/",
      secondaryLabel: "阅读 Trust Center",
      secondaryHref: "/trust-center/",
    },
    audit: {
      eyebrow: "TITMAS AUDIT / 证据审计",
      title: "沿时间线复核主体、授权、决定、回执和执行结果",
      lead: "TITMAS Audit 将 Gate、审批、Receipt、执行结果、重放结果和已知限制组织为可导出的审计视图。",
      status: "PRIVATE_REFERENCE_IMPLEMENTED_NOT_DEPLOYED",
      statusDetail: shared.zh.boundary,
      sections: [
        { title: "时间线", body: "按关联标识连接主体、任务、策略版本、授权、决定和结果。" },
        { title: "离线复核", body: "审计包目标是可离线检查；当前公开面仅提供合成材料。" },
        { title: "边界", body: "Audit 不捕获 Chain of Thought，不把记录提升为事实真相，也不替代客户法务或审计意见。" },
      ],
      primaryLabel: shared.zh.proof,
      primaryHref: "/commercial-evaluation/",
      secondaryLabel: shared.zh.request,
      secondaryHref: "/private-evaluation/",
    },
    health: {
      eyebrow: "TITMAS HEALTH / 智能体健康快照",
      title: "先识别身份、边界、证据、闸门和审计缺口",
      lead: "TITMAS Health Snapshot 是进入 Monitor Pilot 前的低门槛评估，用可解释覆盖项替代未经校准的综合分数。",
      status: "EVALUATION_PROFILE_NOT_AVAILABLE_OFFERING",
      statusDetail: shared.zh.boundary,
      sections: [
        { title: "检查范围", body: "首版关注结构完整性和覆盖情况。", items: ["Identity completeness", "Boundary completeness", "Evidence completeness", "Gate coverage", "Receipt verification coverage", "Audit replay coverage"] },
        { title: "允许状态", body: "只输出可解释的离散状态。", items: ["COMPLETE", "PARTIAL", "MISSING", "NOT_ASSESSED"] },
        { title: "边界", body: "Health 不输出信用评分、安全认证等级或未经校准的总健康分。" },
      ],
      primaryLabel: shared.zh.request,
      primaryHref: "/private-evaluation/",
      secondaryLabel: "查看四产品目录",
      secondaryHref: "/product-catalog.json",
    },
    "design-partner": {
      eyebrow: "DESIGN PARTNER / 设计伙伴",
      title: "用一个真实工作流共同验证 Monitor-first 产品路径",
      lead: "设计伙伴计划面向使用 Coding Agent、内部自动化或 Agent 平台的研发团队。登记不等于接受、授权、合同或仓库访问。",
      status: "PROGRAM_DEFINED_OUTREACH_NOT_AUTHORIZED",
      statusDetail: shared.zh.boundary,
      sections: [
        { title: "适合对象", body: "软件研发团队、AI SaaS 团队、内部自动化平台和 Agent 平台开发团队。" },
        { title: "候选范围", body: "一个关键工作流、一至三个 Agent、合成或经授权元数据、人工审查。" },
        { title: "不会自动发生", body: "不自动联系、不自动签约、不自动开通 Key、不公开案例。" },
      ],
      primaryLabel: "查看申请边界",
      primaryHref: "/request-access/",
      secondaryLabel: "查看 Monitor Pilot",
      secondaryHref: "/monitor-pilot/",
    },
    "private-evaluation": {
      eyebrow: "PRIVATE EVALUATION / 私有评估",
      title: "先用零客户数据和合成场景验证第一价值",
      lead: "私有评估从 Agent Overview、Shadow Gate、Receipt 验证和 Audit 时间线开始，不要求生产权限或客户原始 Trace。",
      status: "SYNTHETIC_REFERENCE_IMPLEMENTED_NOT_PUBLICLY_AVAILABLE",
      statusDetail: shared.zh.boundary,
      sections: [
        { title: "第一价值", body: "未知 Agent 能发现入口、理解边界并完成合成 Observer → Gate → Receipt → Audit。" },
        { title: "数据边界", body: "默认零客户数据；原始客户内容不上传，管理面只接收必要元数据。" },
        { title: "退出", body: "任何阶段可停止；申请不会创建 Tenant、Workspace、Credential 或商业承诺。" },
      ],
      primaryLabel: "查看访问请求",
      primaryHref: "/request-access/",
      secondaryLabel: shared.zh.proof,
      secondaryHref: "/commercial-evaluation/",
    },
    "monitor-pilot": {
      eyebrow: "MONITOR PILOT / 监测试点",
      title: "先观察本应被阻断或需要审批的动作，不影响真实系统",
      lead: "Monitor Pilot 生成 Shadow Decision、技术 Receipt 和 Audit Bundle，但不改变、不阻断、不执行客户动作。",
      status: "SYNTHETIC_REFERENCE_PROOF_ONLY_NOT_AVAILABLE_OFFERING",
      statusDetail: shared.zh.boundary,
      sections: [
        { title: "明确非阻断", body: "MODE=MONITOR；ENFORCEMENT_EFFECT=NONE。" },
        { title: "候选交付", body: "一个关键工作流、一至三个 Agent、有限事件量、周报和最终差距报告。" },
        { title: "当前限制", body: "尚无批准价格、法律审查、客户合同或已开通付费 Pilot。" },
      ],
      primaryLabel: "申请私有评估",
      primaryHref: "/request-access/",
      secondaryLabel: "查看 Gate",
      secondaryHref: "/products/gate/",
    },
    "enforce-pilot": {
      eyebrow: "ENFORCE PILOT / 执行控制试点",
      title: "只有客户特定授权后，才评估真实阻断与审批",
      lead: "Enforce Pilot 是未来客户特定路径，不是当前可用产品。它要求明确动作范围、书面授权、策略、回滚、紧急停机和验收。",
      status: "SYNTHETIC_REFERENCE_ONLY_CUSTOMER_AUTHORIZATION_COUNT_0",
      statusDetail: shared.zh.boundary,
      sections: [
        { title: "额外闸门", body: "客户书面授权、策略批准、回滚批准、Human Approval Path 和 Emergency Stop 缺一不可。" },
        { title: "失败关闭", body: "NOT_ASSESSED 不得升级为 ALLOW；应进入 BLOCK_OR_HOLD。" },
        { title: "当前事实", body: "真实客户授权数量为 0；没有自动 Enforce、生产 Key 或生产部署。" },
      ],
      primaryLabel: "先评估 Monitor",
      primaryHref: "/monitor-pilot/",
      secondaryLabel: "安全边界",
      secondaryHref: "/security/",
    },
    "request-access": {
      eyebrow: "REQUEST ACCESS / 申请访问",
      title: "所有商业访问均由人工、逐范围审查",
      lead: "当前页面不收集表单、不创建客户记录、不签发 Key，也不触发自动联系。正式申请渠道需在隐私、法务和支持责任确认后另行启用。",
      status: "INFORMATION_ONLY_INTAKE_NOT_ACTIVE",
      statusDetail: shared.zh.boundary,
      sections: [
        { title: "未来最小字段", body: "姓名、组织、商务邮箱、非保密用例、Agent Framework、目标动作、部署偏好、数据敏感度和联系偏好。" },
        { title: "不要提交", body: "API Key、个人敏感信息、客户数据、生产数据、私有仓库信息或公司机密。" },
        { title: "人工决定", body: "每个 Evaluation、Pilot、Credential、部署和 Enforce 范围均需单独 Human Decision。" },
      ],
      primaryLabel: "阅读隐私边界",
      primaryHref: "/privacy/",
      secondaryLabel: "查看当前状态",
      secondaryHref: "/status/",
    },
    security: {
      eyebrow: "SECURITY / 安全",
      title: "闭源核心、最小元数据和失败关闭是当前默认边界",
      lead: "公开网站仅提供静态信息与公开安全材料；不暴露私有核心、攻击语料、Credential、客户数据或内部安全配置。",
      status: "SECURITY_REVIEW_REQUIRED_BEFORE_COMMERCIAL_AVAILABILITY",
      statusDetail: shared.zh.boundary,
      sections: [
        { title: "数据平面", body: "客户原始数据默认留在客户环境；管理面只接收必要元数据。" },
        { title: "访问", body: "Scoped Key 必须绑定主体、Agent、Workspace、Scope、额度、到期和撤销状态。" },
        { title: "未完成", body: "独立安全评价、全部商业安全闸门和客户特定部署审查尚未完成。" },
      ],
      primaryLabel: "打开 Trust Center",
      primaryHref: "/trust-center/",
      secondaryLabel: "查看状态",
      secondaryHref: "/status/",
    },
    "trust-center": {
      eyebrow: "TRUST CENTER / 信任中心",
      title: "把证据、验证、授权和执行保持为不同事实",
      lead: "TITMAS 的可信来自明确分离和可复核来源，而不是把 PASS、Receipt 或 Gate Decision 说成事实真相或法律结论。",
      status: "PUBLIC_TRUST_INFORMATION_NOT_CERTIFICATION",
      statusDetail: shared.zh.boundary,
      sections: [
        { title: "核心非等价", body: "Evidence ≠ Truth；Verification ≠ Authorization；Recommendation ≠ Decision；Decision ≠ Execution。" },
        { title: "公开证明", body: "公开 Proof 仅使用合成或公共安全材料，并明确来源、版本、结果和限制。" },
        { title: "不作声明", body: "不声明认证、绝对安全、不可绕过、生产就绪或客户采用。" },
      ],
      primaryLabel: "查看 Proof Catalog",
      primaryHref: "/proof-catalog.json",
      secondaryLabel: "安全说明",
      secondaryHref: "/security/",
    },
    privacy: {
      eyebrow: "PRIVACY / 隐私",
      title: "默认不收集客户原始内容，不把客户数据交给境外模型",
      lead: "当前商业入口是静态说明页，不包含申请表后端。未来任何数据处理必须遵循最小必要、目的限定、地域、保留、删除和审计边界。",
      status: "HUMAN_LEGAL_REVIEW_REQUIRED",
      statusDetail: shared.zh.boundary,
      sections: [
        { title: "默认值", body: "CUSTOMER_TRACE_RAW_UPLOAD_DEFAULT=false；CUSTOMER_DATA_TO_FOREIGN_MODEL=false。" },
        { title: "允许测试数据", body: "公开数据、合成数据、经授权匿名化数据或明确批准的非客户测试数据。" },
        { title: "法律边界", body: "适用性矩阵不是法律意见；个人信息、跨境和保留方案需中国法律专业审查。" },
      ],
      primaryLabel: "阅读 Trust Center",
      primaryHref: "/trust-center/",
      secondaryLabel: "返回申请边界",
      secondaryHref: "/request-access/",
    },
    terms: {
      eyebrow: "TERMS / 条款边界",
      title: "当前公开页面不构成报价、合同、SLA 或服务承诺",
      lead: "所有价格、SOW、部署、支持、数据处理和 Enforce 授权均需经 Human Owner、合同及适用专业审查单独确认。",
      status: "DRAFT_INFORMATION_NOT_CONTRACT",
      statusDetail: shared.zh.boundary,
      sections: [
        { title: "当前不是", body: "不是在线购买、自动订阅、自动开票、自动 Key 签发或正式 SLA。" },
        { title: "未来合同", body: "应明确服务范围、数据边界、Receipt 限制、支持、验收、终止和数据返还。" },
        { title: "人工控制", body: "Codex 或其他 Agent 不能签字、盖章、收款、开票或替代法律意见。" },
      ],
      primaryLabel: "查看当前状态",
      primaryHref: "/status/",
      secondaryLabel: "隐私边界",
      secondaryHref: "/privacy/",
    },
  },
  en: {} as Record<CommercialPageKey, PageCopy>,
};

const englishSections: Record<CommercialPageKey, readonly Section[]> = {
  gate: [
    { title: "Monitor Mode", body: "Computes a Shadow Decision without blocking customer actions.", items: ["WOULD_ALLOW", "WOULD_BLOCK", "WOULD_NEED_APPROVAL", "NOT_ASSESSED"] },
    { title: "Enforce Mode", body: "Enters a pilot only after written customer scope, policy, rollback, and approval paths are explicit.", items: ["ALLOW", "BLOCK", "NEEDS_APPROVAL", "NOT_ASSESSED → BLOCK_OR_HOLD"] },
    { title: "Boundary", body: "Gate is not a general authorization platform, agent runtime, AI firewall, or proof of result correctness." },
  ],
  receipt: [
    { title: "Public view", body: "Provides a customer-safe status, summary, verification result, and limitation view." },
    { title: "Verification semantics", body: "Verification establishes only in-scope structure, integrity, and signature state.", items: ["PASS", "FAIL", "NOT_ASSESSED", "UNVERIFIABLE_KEY_UNAVAILABLE"] },
    { title: "Permanent boundary", body: "A Receipt is a technical execution evidence record, not truth, a legal certificate, compliance certification, or electronic certification service." },
  ],
  audit: [
    { title: "Timeline", body: "Uses correlation references to connect the principal, task, policy revision, authority, decision, and outcome." },
    { title: "Offline review", body: "Audit bundles are designed for offline inspection; the current public surface contains synthetic material only." },
    { title: "Boundary", body: "Audit captures no chain of thought, does not promote records into truth, and does not replace legal or professional audit opinion." },
  ],
  health: [
    { title: "Coverage", body: "The first profile focuses on structural completeness and coverage.", items: ["Identity completeness", "Boundary completeness", "Evidence completeness", "Gate coverage", "Receipt verification coverage", "Audit replay coverage"] },
    { title: "Allowed states", body: "Only explainable discrete states are used.", items: ["COMPLETE", "PARTIAL", "MISSING", "NOT_ASSESSED"] },
    { title: "Boundary", body: "Health produces no credit score, security certification level, or uncalibrated aggregate health score." },
  ],
  "design-partner": [
    { title: "Intended teams", body: "Software engineering, AI SaaS, internal automation, and agent-platform teams." },
    { title: "Candidate scope", body: "One critical workflow, one to three agents, synthetic or authorized metadata, and human review." },
    { title: "No automatic effects", body: "No automated outreach, contracting, key provisioning, or public case study." },
  ],
  "private-evaluation": [
    { title: "First value", body: "An unknown agent discovers the entry, understands boundaries, and completes a synthetic Observer → Gate → Receipt → Audit path." },
    { title: "Data boundary", body: "Zero customer data by default; raw customer content stays out and the management plane receives minimum metadata only." },
    { title: "Exit", body: "The process may stop at any step. A request creates no tenant, workspace, credential, or commercial commitment." },
  ],
  "monitor-pilot": [
    { title: "Explicitly non-blocking", body: "MODE=MONITOR; ENFORCEMENT_EFFECT=NONE." },
    { title: "Candidate delivery", body: "One critical workflow, one to three agents, bounded events, weekly review, and a final gap report." },
    { title: "Current limits", body: "There is no approved price, legal review, customer contract, or activated paid pilot." },
  ],
  "enforce-pilot": [
    { title: "Additional gates", body: "Written customer authority, approved policy and rollback, a human approval path, and emergency stop are all required." },
    { title: "Fail closed", body: "NOT_ASSESSED must not become ALLOW; it enters BLOCK_OR_HOLD." },
    { title: "Current fact", body: "Customer authorization count is zero. There is no automatic Enforce, production key, or production deployment." },
  ],
  "request-access": [
    { title: "Future minimum fields", body: "Name, organization, business email, non-confidential use case, agent framework, target action, deployment preference, data sensitivity, and contact preference." },
    { title: "Do not submit", body: "API keys, sensitive personal information, customer or production data, private-repository information, or company secrets." },
    { title: "Human decision", body: "Every evaluation, pilot, credential, deployment, and Enforce scope requires a separate Human Decision." },
  ],
  security: [
    { title: "Data plane", body: "Raw customer data stays in the customer environment by default; the management plane receives minimum metadata only." },
    { title: "Access", body: "A scoped key must bind principal, agent, workspace, scope, quota, expiry, and revocation state." },
    { title: "Incomplete work", body: "Independent security evaluation, all commercial security gates, and customer-specific deployment review remain incomplete." },
  ],
  "trust-center": [
    { title: "Core non-equivalence", body: "Evidence ≠ Truth; Verification ≠ Authorization; Recommendation ≠ Decision; Decision ≠ Execution." },
    { title: "Public proof", body: "Public proof uses synthetic or public-safe material and declares provenance, version, result, and limitations." },
    { title: "Non-claims", body: "No certification, absolute safety, unbypassability, production readiness, or customer adoption is claimed." },
  ],
  privacy: [
    { title: "Defaults", body: "CUSTOMER_TRACE_RAW_UPLOAD_DEFAULT=false; CUSTOMER_DATA_TO_FOREIGN_MODEL=false." },
    { title: "Allowed test data", body: "Public data, synthetic data, authorized anonymized data, or explicitly approved non-customer test data." },
    { title: "Legal boundary", body: "An applicability matrix is not legal advice. Personal-information, cross-border, and retention plans require qualified China legal review." },
  ],
  terms: [
    { title: "Not currently", body: "No online purchase, automated subscription, invoice, key provisioning, or formal SLA." },
    { title: "Future contract", body: "Contracts should define service scope, data boundaries, Receipt limits, support, acceptance, termination, and data return." },
    { title: "Human control", body: "Codex or any other agent cannot sign, seal, collect payment, issue invoices, or replace legal advice." },
  ],
};

const englishActions: Record<CommercialPageKey, [string, string]> = {
  gate: [shared.en.request, shared.en.proof],
  receipt: ["Open verification entry", "Read the Trust Center"],
  audit: [shared.en.proof, shared.en.request],
  health: [shared.en.request, "Open the four-product catalog"],
  "design-partner": ["Read request boundaries", "View Monitor Pilot"],
  "private-evaluation": ["View request access", shared.en.proof],
  "monitor-pilot": ["Request a private evaluation", "View Gate"],
  "enforce-pilot": ["Evaluate Monitor first", "Security boundary"],
  "request-access": ["Read privacy boundaries", "View current status"],
  security: ["Open Trust Center", "View status"],
  "trust-center": ["View Proof Catalog", "Security information"],
  privacy: ["Read Trust Center", "Back to request boundary"],
  terms: ["View current status", "Privacy boundary"],
};

// English copy stays claim-equivalent to the Chinese commercial surface.
pages.en = Object.fromEntries(
  Object.entries(pages.zh).map(([key, value]) => [
    key,
    {
      ...value,
      eyebrow: value.eyebrow.split(" / ")[0],
      title: ({
        gate: "Verify context and authority before a critical action occurs",
        receipt: "Bind action, provenance, decision, and limits into a portable technical receipt",
        audit: "Review principals, authority, decisions, receipts, and outcomes on one timeline",
        health: "Identify identity, boundary, evidence, gate, and audit gaps first",
        "design-partner": "Validate a Monitor-first product path with one real workflow",
        "private-evaluation": "Validate first value with zero customer data and synthetic scenarios",
        "monitor-pilot": "Observe actions that would be blocked or require approval without affecting the real system",
        "enforce-pilot": "Evaluate real blocking only after customer-specific authorization",
        "request-access": "Every commercial access path is reviewed by a human and bounded by scope",
        security: "Closed core, minimum metadata, and fail-closed behavior are the defaults",
        "trust-center": "Keep evidence, verification, authorization, and execution as separate facts",
        privacy: "No raw customer content by default and no customer data sent to foreign models",
        terms: "This public surface is not a quote, contract, SLA, or service commitment",
      } as Record<string, string>)[key],
      lead: ({
        gate: "TITMAS Gate supports bounded Monitor and future customer-specific Enforce paths for merges, releases, configuration changes, data writes, and external sends.",
        receipt: "TITMAS Receipt records what happened, its provenance, who authorized it, how it verifies, and retained failure or revocation states.",
        audit: "TITMAS Audit organizes Gate, approval, Receipt, outcome, replay, and limitation records into an exportable review view.",
        health: "TITMAS Health Snapshot is a low-friction pre-Monitor assessment based on explainable coverage, not an uncalibrated aggregate score.",
        "design-partner": "The design-partner path is for coding-agent, internal-automation, and agent-platform teams. Interest is not acceptance, authorization, contract, or repository access.",
        "private-evaluation": "A private evaluation starts with Agent Overview, Shadow Gate, Receipt verification, and Audit timeline without production access or raw customer traces.",
        "monitor-pilot": "Monitor Pilot creates Shadow Decisions, technical Receipts, and Audit Bundles but does not change, block, or execute customer actions.",
        "enforce-pilot": "Enforce Pilot is a future customer-specific path, not a currently available product. It requires written scope, policy, rollback, emergency stop, and acceptance.",
        "request-access": "This page collects no form data, creates no customer record, issues no key, and triggers no automated contact. A formal intake channel requires separate privacy, legal, and support approval.",
        security: "The public website contains static information and public-safe material only. It does not expose the private core, attack corpus, credentials, customer data, or internal security configuration.",
        "trust-center": "TITMAS trust comes from explicit separation and reviewable provenance, not from treating PASS, a Receipt, or a Gate Decision as truth or legal conclusion.",
        privacy: "The current commercial entry is static and has no intake backend. Any future processing must follow necessity, purpose, locality, retention, deletion, and audit boundaries.",
        terms: "Pricing, SOW, deployment, support, data processing, and Enforce authority each require separate Human Owner, contract, and applicable professional review.",
      } as Record<string, string>)[key],
      statusDetail: shared.en.boundary,
      sections: englishSections[key as CommercialPageKey],
      primaryLabel: englishActions[key as CommercialPageKey][0],
      secondaryLabel: englishActions[key as CommercialPageKey][1],
    },
  ]),
) as Record<CommercialPageKey, PageCopy>;

export function commercialPageCopy(locale: Locale, key: CommercialPageKey): PageCopy {
  return pages[locale][key];
}

export function commercialPath(locale: Locale, key: CommercialPageKey): string {
  const base = productKeys.includes(key as (typeof productKeys)[number]) ? `/products/${key}/` : `/${key}/`;
  return locale === "zh" ? base : `/en${base}`;
}
