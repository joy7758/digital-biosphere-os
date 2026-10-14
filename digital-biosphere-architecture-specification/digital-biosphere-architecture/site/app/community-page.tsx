import type { Locale } from "./site-content";
import { Footer, Header } from "./site-shell";
import { StructuredPageData } from "./structured-page-data";

const copy = {
  zh: {
    lang: "zh-CN",
    eyebrow: "HISTORICAL MATERIAL / 历史资料",
    title: "历史开发者社区设计资料",
    lead:
      "该页面保留 TITMAS 早期开发者社区设计，供历史追溯。它不是当前商业入口，不表示开放贡献、开放核心或已经建立社区。",
    status: "当前阶段",
    statusValue: "HISTORICAL_NON_CURRENT · 社区从未建立",
    definitionTitle: "TITMAS 是什么",
    definition:
      "TITMAS 是面向可信多智能体基础设施的开发者入口。开发者继续使用自己选择的 Agent Framework 和 Runtime；TITMAS 关注跨实现的身份、能力、执行、证据、验证和评价接口。",
    nonGoalsTitle: "TITMAS 不是什么",
    nonGoals: [
      "不是创建、编排或托管 Agent 的平台",
      "不是 DBOS、SAEE 或 Digital Biosphere 的替代品",
      "不是 Foundation、认证计划或 Marketplace",
      "不把 Observation、Evidence、Verification 或 Evaluation 自动升级为 Truth 或 Authority",
    ],
    surfacesTitle: "可以共同建设的四类基础设施表面",
    surfaces: [
      ["Specification", "规范", "定义对象、字段、版本、所有权和非等价边界。"],
      ["Adapter Contract", "适配契约", "把外部 Agent Runtime 的观察材料映射到 TITMAS 边界。"],
      ["Conformance", "符合性", "用正例、负例、失败关闭和结果合同验证实现声明。"],
      ["Reference Implementation", "参考实现", "提供可替换、可复现的学习路径，不成为唯一 Runtime。"],
    ],
    flowTitle: "贡献如何流动",
    flow: ["发现入口", "选择边界", "声明来源", "准备 Proposal", "领域审查", "架构决定", "独立实现授权", "符合性验证"],
    rolesTitle: "谁可以参与",
    roles: [
      ["Human Developer", "可以准备规范、mapping、Adapter contract、测试和文档，并承担来源与结果责任。"],
      ["Governed AI Agent", "可以辅助编码、检索、测试和引用；必须披露工具、来源、验证和人工责任方。"],
      ["Reviewer Candidate", "可以指出边界、兼容、安全和失败问题；Review 不等于 Decision。"],
    ],
    readyTitle: "现在可以做什么",
    ready: [
      "阅读中英文架构和机器状态",
      "用 TITMAS 对自己的 Agent Runtime 做概念 mapping",
      "审查 Technical Validation Pilot 的最小闭环",
      "准备本地 Proposal candidate，不创建外部 Issue 或 PR",
    ],
    blockedTitle: "现在还不能做什么",
    blocked: [
      "不能向未创建的 GitHub Organization 提交贡献",
      "不能把 contributor entry 写成已开放社区",
      "不能创建 Agent、Runtime、Permission 或自动 Authority",
      "不能宣称外部采用、生产就绪、认证或 Foundation",
    ],
    domainTitle: "公开入口迁移状态",
    domainItems: [
      ["当前在线", "https://redcrag.cn/"],
      ["未来主域名", "titmas.cn · 备案中 · 尚未上线"],
      ["GitHub slug", "titmas-cn · 已选择 · Organization 未创建"],
      ["仓库迁移", "0 · 需要逐仓独立决定"],
    ],
    resourcesTitle: "不依赖 GitHub 的公开资源",
    resources: [
      ["/llms.txt", "LLM-readable 项目与边界入口"],
      ["/agent-index.json", "智能体发现索引"],
      ["/status.json", "机器可读当前状态"],
      ["/titmas-community.json", "TITMAS 社区机器对象"],
      ["/agent-customer-package.json", "适用／不适用与推荐边界"],
    ],
    back: "返回首页",
  },
  en: {
    lang: "en",
    eyebrow: "HISTORICAL MATERIAL",
    title: "Historical developer-community design material",
    lead:
      "This page preserves an earlier TITMAS developer-community design for historical traceability. It is not the current commercial entry and does not mean open contribution, open core, or an established community.",
    status: "Current stage",
    statusValue: "HISTORICAL_NON_CURRENT · community was never established",
    definitionTitle: "What TITMAS is",
    definition:
      "titmas is the public developer entry for trusted multi-agent infrastructure; TITMAS remains its technical project identifier. Developers keep their chosen agent frameworks and runtimes; TITMAS focuses on portable identity, capability, execution, evidence, verification, and evaluation interfaces.",
    nonGoalsTitle: "What TITMAS is not",
    nonGoals: [
      "Not a platform that creates, orchestrates, or hosts agents",
      "Not a replacement for DBOS, SAEE, or Digital Biosphere",
      "Not a foundation, certification program, or marketplace",
      "Does not promote observations, evidence, verification, or evaluation into truth or authority",
    ],
    surfacesTitle: "Four infrastructure surfaces to build together",
    surfaces: [
      ["Specification", "Rules", "Define objects, fields, versions, ownership, and non-equivalence boundaries."],
      ["Adapter Contract", "Mappings", "Map observations from external agent runtimes into TITMAS boundaries."],
      ["Conformance", "Claims", "Test implementation claims with positive, negative, fail-closed, and result contracts."],
      ["Reference Implementation", "Examples", "Provide replaceable, reproducible learning paths without becoming the only runtime."],
    ],
    flowTitle: "How a contribution moves",
    flow: ["Discover", "Choose a boundary", "Declare sources", "Prepare proposal", "Domain review", "Architecture decision", "Separate implementation authorization", "Conformance"],
    rolesTitle: "Who can participate",
    roles: [
      ["Human Developer", "May prepare specifications, mappings, adapter contracts, tests, and documentation while owning source and result accountability."],
      ["Governed AI Agent", "May assist with code, retrieval, tests, and citations; tools, sources, verification, and human accountability must be disclosed."],
      ["Reviewer Candidate", "May identify boundary, compatibility, security, and failure issues. Review is not decision."],
    ],
    readyTitle: "What you can do now",
    ready: [
      "Read bilingual architecture and machine status",
      "Conceptually map your agent runtime to TITMAS",
      "Review the minimum loop in the Technical Validation Pilot",
      "Prepare a local proposal candidate without creating an external issue or PR",
    ],
    blockedTitle: "What you cannot do yet",
    blocked: [
      "Contribute to a GitHub organization that does not exist",
      "Describe the contributor entry as an open community",
      "Create agents, runtimes, permissions, or automatic authority",
      "Claim external adoption, production readiness, certification, or a foundation",
    ],
    domainTitle: "Public-entry migration status",
    domainItems: [
      ["Live now", "https://redcrag.cn/"],
      ["Future primary domain", "titmas.cn · filing · not live"],
      ["GitHub slug", "titmas-cn · selected · organization not created"],
      ["Repositories moved", "0 · each requires a separate decision"],
    ],
    resourcesTitle: "Public resources that do not depend on GitHub",
    resources: [
      ["/llms.txt", "LLM-readable project and boundary entry"],
      ["/agent-index.json", "Agent discovery index"],
      ["/status.json", "Machine-readable current status"],
      ["/titmas-community.json", "TITMAS community machine object"],
      ["/agent-customer-package.json", "Fit, non-fit, and recommendation boundaries"],
    ],
    back: "Back to home",
  },
} as const;

export function CommunityPage({ locale }: { locale: Locale }) {
  const c = copy[locale];
  const home = locale === "zh" ? "/" : "/en/";

  return (
    <div className="site community-page" lang={c.lang}>
      <Header locale={locale} section="community" />
      <StructuredPageData
        locale={locale}
        path={locale === "zh" ? "/community/" : "/en/community/"}
        title={c.title}
        description={c.lead}
      />
      <main id="main-content">
        <section className="status-hero community-hero">
          <div className="section-shell">
            <p className="section-kicker">{c.eyebrow}</p>
            <h1>{c.title}</h1>
            <p>{c.lead}</p>
            <div className="observed-chip">
              <span>{c.status}</span>
              <strong>{c.statusValue}</strong>
            </div>
            <p className="historical-surface-notice">
              {locale === "zh"
                ? "当前方向：闭源私有核心 + 公开发现与有界证明。商业入口请从产品、Monitor Pilot 或申请访问页面进入。"
                : "Current direction: closed private core with public discovery and bounded proof. Use Products, Monitor Pilot, or Request Access as the commercial entry."}
            </p>
          </div>
        </section>

        <section className="section community-definition">
          <div className="section-shell community-two-column">
            <article>
              <p className="section-kicker">DEFINITION</p>
              <h2>{c.definitionTitle}</h2>
              <p>{c.definition}</p>
            </article>
            <aside className="governance-card">
              <span className="governance-label">NON-GOALS</span>
              <h3>{c.nonGoalsTitle}</h3>
              <ul>{c.nonGoals.map((item) => <li key={item}>{item}</li>)}</ul>
            </aside>
          </div>
        </section>

        <section className="section signals-section">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">CONTRIBUTION SURFACES</p>
              <h2>{c.surfacesTitle}</h2>
            </div>
            <div className="signal-grid">
              {c.surfaces.map(([name, title, description], index) => (
                <article className="signal-card" key={name}>
                  <div className={`signal-symbol signal-${index + 1}`} aria-hidden="true"><i /><i /><i /></div>
                  <span>{name}</span>
                  <h3>{title}</h3>
                  <p>{description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="section workflow-section">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">PROCESS</p>
              <h2>{c.flowTitle}</h2>
            </div>
            <ol className="community-flow">
              {c.flow.map((step, index) => (
                <li key={step}><span>{String(index + 1).padStart(2, "0")}</span><strong>{step}</strong></li>
              ))}
            </ol>
          </div>
        </section>

        <section className="section community-roles">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">PARTICIPATION</p>
              <h2>{c.rolesTitle}</h2>
            </div>
            <div className="role-grid">
              {c.roles.map(([title, description]) => (
                <article key={title}><h3>{title}</h3><p>{description}</p></article>
              ))}
            </div>
          </div>
        </section>

        <section className="section trust-section">
          <div className="section-shell community-two-column">
            <article className="boundary-list">
              <p className="section-kicker">READY</p>
              <h2>{c.readyTitle}</h2>
              <ul>{c.ready.map((item) => <li key={item}>{item}</li>)}</ul>
            </article>
            <article className="boundary-list boundary-list-blocked">
              <p className="section-kicker">NOT YET</p>
              <h2>{c.blockedTitle}</h2>
              <ul>{c.blocked.map((item) => <li key={item}>{item}</li>)}</ul>
            </article>
          </div>
        </section>

        <section className="section status-detail-section alt">
          <div className="section-shell">
            <h2>{c.domainTitle}</h2>
            <div className="baseline-table">
              {c.domainItems.map(([label, value]) => (
                <div className="front-door-row" key={label}><strong>{label}</strong><code>{value}</code></div>
              ))}
            </div>
          </div>
        </section>

        <section className="section community-resources">
          <div className="section-shell community-two-column">
            <div>
              <p className="section-kicker">MACHINE-READABLE</p>
              <h2>{c.resourcesTitle}</h2>
              <div className="developer-links">
                {c.resources.map(([href, label]) => (
                  <a href={href} key={href}><code>{href}</code><span>{label} →</span></a>
                ))}
              </div>
            </div>
            <aside className="community-terminal" aria-label="TITMAS current machine status">
              <code>TITMAS_DOMAIN=titmas.cn</code>
              <code>DOMAIN_LIVE=false</code>
              <code>GITHUB_SLUG=titmas-cn</code>
              <code>ORGANIZATION_CREATED=false</code>
              <code>COMMUNITY_ESTABLISHED=false</code>
              <code>PUBLIC_CONTRIBUTION_ENABLED=false</code>
            </aside>
          </div>
          <div className="section-shell community-back">
            <a className="button button-primary" href={home}>{c.back}</a>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
