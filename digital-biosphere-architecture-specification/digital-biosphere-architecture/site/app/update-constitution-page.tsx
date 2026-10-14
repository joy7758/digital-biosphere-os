import { content, type Locale } from "./site-content";
import { Footer, Header } from "./site-shell";
import { StructuredPageData } from "./structured-page-data";

const constitutionCopy = {
  zh: {
    eyebrow: "WEBSITE UPDATE CONSTITUTION v0.1",
    title: "TITMAS 网站更新宪法",
    lead: "以后遇到网站更新抉择，默认先核对 OpenAI 与 OpenTelemetry 官方模式；参考风格不能覆盖 TITMAS 已验证事实或治理边界。",
    back: "全部更新",
    decisionTitle: "两类参考，各自解决不同问题",
    openaiTitle: "OpenAI：面向受众的信息架构",
    openaiItems: ["顶层导航与内容分层", "Research Overview / Index", "Newsroom 分类与 Release Notes", "开发者更新与渐进披露", "简短、单一、可追溯的公告"],
    otelTitle: "OpenTelemetry：开放规范的生命周期",
    otelItems: ["公告 date、expiryDate 与确定性排序", "文档级成熟度，不传播为项目成熟度", "Specification / Implementation / Contrib 分离", "版本、稳定、弃用与移除", "来源 commit、最后修改与贡献流程"],
    sequenceTitle: "默认决策顺序",
    sequence: ["分类网站变化", "核验 TITMAS 当前事实", "检查 OpenAI 信息架构模式", "检查 OpenTelemetry 成熟度与公告规则", "保留权力和非等价边界", "记录来源、日期、状态与限制", "验证中英文和机器入口"],
    conflictTitle: "发生冲突时",
    conflictBody: "TITMAS 已验证事实与治理边界优先。参考不能创建产品、实现、权限、权力、发布、认证、客户或生产状态。",
    gateTitle: "仍需人工 gate 的事项",
    gates: ["新的产品或商业服务声明", "生产、认证或安全保证", "Authority / Permission / Execution 变化", "破坏稳定公共接口的变更", "法律、安全或隐私承诺"],
    nonAffiliation: "参考不等于采纳、官方关联或认可。TITMAS 不声称获得 OpenAI、OpenTelemetry 或 CNCF 的背书。",
    sources: "官方参考",
  },
  en: {
    eyebrow: "WEBSITE UPDATE CONSTITUTION v0.1",
    title: "TITMAS Website Update Constitution",
    lead: "When a website update requires a choice, check official OpenAI and OpenTelemetry patterns first. Reference style cannot override verified TITMAS truth or governance boundaries.",
    back: "All updates",
    decisionTitle: "Two references with different responsibilities",
    openaiTitle: "OpenAI: audience-facing information architecture",
    openaiItems: ["Top-level navigation and content hierarchy", "Research Overview / Index", "Newsroom categories and Release Notes", "Developer updates and progressive disclosure", "Short, singular, traceable announcements"],
    otelTitle: "OpenTelemetry: open-specification lifecycle",
    otelItems: ["Announcement date, expiryDate, and deterministic ordering", "Document-level maturity without project-wide propagation", "Specification / Implementation / Contrib separation", "Versioning, stability, deprecation, and removal", "Source commit, last modified, and contribution workflow"],
    sequenceTitle: "Default decision sequence",
    sequence: ["Classify the website change", "Verify current TITMAS truth", "Check the OpenAI information-architecture pattern", "Check OpenTelemetry maturity and announcement rules", "Preserve authority and non-equivalence boundaries", "Record source, date, status, and limitations", "Validate Chinese, English, and machine entries"],
    conflictTitle: "When references conflict",
    conflictBody: "Verified TITMAS truth and governance boundaries win. A reference cannot create a product, implementation, permission, authority, release, certification, customer, or production status.",
    gateTitle: "Changes that still require a human gate",
    gates: ["New product or commercial-offering claims", "Production, certification, or safety guarantees", "Authority / Permission / Execution changes", "Breaking stable public interfaces", "Legal, security, or privacy commitments"],
    nonAffiliation: "Reference does not mean adoption, affiliation, or endorsement. TITMAS claims no endorsement by OpenAI, OpenTelemetry, or CNCF.",
    sources: "Official references",
  },
} as const;

const sources = {
  openai: [
    ["OpenAI Research", "https://openai.com/research/"],
    ["OpenAI Newsroom", "https://openai.com/news/company-announcements/"],
    ["ChatGPT Release Notes", "https://help.openai.com/en/articles/6825453-chatgpt-release-notes"],
    ["OpenAI Developers", "https://developers.openai.com/"],
  ],
  otel: [
    ["OpenTelemetry Homepage Announcements", "https://opentelemetry.io/site/build/announcements/"],
    ["OpenTelemetry Document Status", "https://opentelemetry.io/docs/specs/otel/document-status/"],
    ["OpenTelemetry Versioning and Stability", "https://opentelemetry.io/docs/specs/otel/versioning-and-stability/"],
    ["OpenTelemetry Contributing", "https://opentelemetry.io/docs/contributing/"],
  ],
} as const;

export function WebsiteUpdateConstitutionPage({ locale }: { locale: Locale }) {
  const c = content[locale];
  const t = constitutionCopy[locale];
  const updates = locale === "zh" ? "/updates/" : "/en/updates/";

  return (
    <div className="site constitution-page" lang={c.lang}>
      <Header locale={locale} section="constitution" />
      <StructuredPageData
        locale={locale}
        path={locale === "zh" ? "/updates/constitution/" : "/en/updates/constitution/"}
        title={t.title}
        description={t.lead}
        type="TechArticle"
      />
      <main id="main-content">
        <section className="constitution-hero">
          <div className="section-shell">
            <a className="update-back" href={updates}>← {t.back}</a>
            <p className="section-kicker">{t.eyebrow}</p>
            <h1>{t.title}</h1>
            <p>{t.lead}</p>
            <div className="constitution-status">
              <code>SITE_GOVERNANCE_BASELINE</code>
              <code>REFERENCE_NE_ADOPTION</code>
              <code>REFERENCE_NE_ENDORSEMENT</code>
            </div>
          </div>
        </section>

        <section className="section constitution-references">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">REFERENCE RESPONSIBILITIES</p>
              <h2>{t.decisionTitle}</h2>
            </div>
            <div className="constitution-reference-grid">
              <article>
                <span>01 / OPENAI</span>
                <h3>{t.openaiTitle}</h3>
                <ul>{t.openaiItems.map((item) => <li key={item}>{item}</li>)}</ul>
                <div>{sources.openai.map(([label, href]) => <a href={href} key={href}>{label} ↗</a>)}</div>
              </article>
              <article>
                <span>02 / OPENTELEMETRY</span>
                <h3>{t.otelTitle}</h3>
                <ul>{t.otelItems.map((item) => <li key={item}>{item}</li>)}</ul>
                <div>{sources.otel.map(([label, href]) => <a href={href} key={href}>{label} ↗</a>)}</div>
              </article>
            </div>
          </div>
        </section>

        <section className="section constitution-sequence">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">DECISION PROCEDURE</p>
              <h2>{t.sequenceTitle}</h2>
            </div>
            <ol>{t.sequence.map((step, index) => <li key={step}><span>{String(index + 1).padStart(2, "0")}</span><strong>{step}</strong></li>)}</ol>
          </div>
        </section>

        <section className="section constitution-boundaries">
          <div className="section-shell constitution-boundary-grid">
            <article>
              <p className="section-kicker">CONFLICT RULE</p>
              <h2>{t.conflictTitle}</h2>
              <p>{t.conflictBody}</p>
            </article>
            <article>
              <p className="section-kicker">HUMAN GATE</p>
              <h2>{t.gateTitle}</h2>
              <ul>{t.gates.map((gate) => <li key={gate}>{gate}</li>)}</ul>
            </article>
          </div>
        </section>

        <section className="constitution-non-affiliation">
          <div className="section-shell">
            <code>NO AFFILIATION / NO ENDORSEMENT</code>
            <p>{t.nonAffiliation}</p>
            <div>
              <a href="/WEBSITE-UPDATE-CONSTITUTION-v0.1.json">JSON ↗</a>
              <a href="/WEBSITE-UPDATE-CONSTITUTION-v0.1.md">Markdown ↗</a>
            </div>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
