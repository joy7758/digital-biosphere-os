import { content, type Locale } from "./site-content";
import { Footer, Header } from "./site-shell";
import { StructuredPageData } from "./structured-page-data";

const industryCopy = {
  zh: {
    eyebrow: "INDUSTRY APPLICATION / 行业应用示例",
    title: "智能制造智能体生态",
    lead: "制造业展示的是 TITMAS 可信基础设施如何被行业 Agent 使用，而不是一套由 TITMAS 销售或运行的制造软件。",
    home: "TITMAS 首页",
    current: "行业应用",
    rolesTitle: "行业 Agent 由企业与开发者构建",
    rolesLead: "生产、质量、设备与供应链 Agent 可以来自不同团队和技术栈。TITMAS 不接管它们的业务逻辑，只定义共同的可信运行关注面。",
    manufacturingAgents: [
      ["Production Planning Agent", "生产调度智能体"],
      ["Quality Inspection Agent", "质量检测智能体"],
      ["Maintenance Agent", "设备维护智能体"],
      ["Supply Chain Agent", "供应链智能体"],
    ],
    trustTitle: "同一套可信基础，连接不同工业 Agent",
    trustLead: "六个可组合能力用于表达身份、边界、执行记录与长期状态；它们不自动产生权限、业务决策或生产认证。",
    infrastructureCapabilities: [
      ["Identity", "身份", "确认 Agent 是谁、属于谁，以及声明了什么能力。"],
      ["Boundary", "边界", "表达 Agent 可以做什么、不能做什么。"],
      ["Evidence", "证据", "保留任务、过程与结果的可追溯记录。"],
      ["Health", "健康", "评价长期运行中的可靠性、风险与稳定性。"],
      ["Memory", "记忆", "组织可引用的执行历史与经验。"],
      ["Reputation", "声誉", "形成长期、可审查的可信表现。"],
    ],
    stackAria: "TITMAS 支撑的行业生态",
    stackLabels: ["Industry Applications", "Industrial AI Agents", "TITMAS Trust Infrastructure", "Agent Framework / MCP", "Models + Data + Devices"],
    flowTitle: "一个工业任务如何进入可信执行路径",
    flowLead: "以下流程展示基础设施作用，不模拟工厂控制系统。",
    steps: [
      ["01", "注册身份", "记录 Agent、版本、所属主体与能力声明。"],
      ["02", "接受任务", "把任务目标与允许的操作边界关联起来。"],
      ["03", "执行操作", "行业 Agent 在自己的 Runtime 与业务系统中运行。"],
      ["04", "生成 Evidence", "保留意图、过程、结果与完整性摘要。"],
      ["05", "输出执行证明", "形成可引用、可重放的执行记录。"],
      ["06", "健康评估", "基于已有记录观察可靠性与风险状态。"],
    ],
    boundaryTitle: "TITMAS 在这里做什么，也不做什么",
    provides: "TITMAS 提供",
    providesItems: ["可信对象与开放规范", "Adapter contract 与符合性边界", "执行证据、健康与历史的可引用结构"],
    excludes: "TITMAS 不提供",
    excludesItems: ["MES 或生产调度系统", "工业 AI 平台或设备控制", "行业解决方案销售、生产认证或安全保证"],
    demoTitle: "查看可运行的参考演示",
    demoLead: "Digital Cell Demo 展示最小可信执行对象、确定性重放和健康视图；它不是制造系统本身。",
    demoCta: "进入 Digital Cell Demo",
    medicalCta: "医疗证据基础设施",
    spaceCta: "自主航天 SAEP",
    profilesTitle: "从一个制造示例进入更多行业剖面",
    profilesLead: "行业剖面把共同的 TITMAS 可信结构翻译为领域问题；领域系统、业务规则与 Agent 仍由行业团队负责。",
    profileOpen: "查看行业剖面",
    profileCards: [
      ["HEALTHCARE", "医疗证据基础设施", "UDI-DICOM 从设备身份与影像证据出发，说明医疗方向如何复用 TITMAS。"],
      ["AUTONOMOUS SPACE", "Space Agent Evidence Profile (SAEP)", "SAEP 基于 EEOAP，研究高风险自主航天 Agent 的可核验执行证据。"],
    ],
    statusCta: "查看状态与边界",
  },
  en: {
    eyebrow: "INDUSTRY APPLICATION EXAMPLE",
    title: "Manufacturing AI Agent Ecosystem",
    lead: "Manufacturing shows how industry agents can use TITMAS trust infrastructure. It is not manufacturing software sold or operated by TITMAS.",
    home: "TITMAS home",
    current: "Industry applications",
    rolesTitle: "Enterprises and developers build the industry agents",
    rolesLead: "Production, quality, maintenance, and supply-chain agents may come from different teams and technology stacks. TITMAS does not take over their business logic; it defines shared trust concerns.",
    manufacturingAgents: [
      ["Production Planning Agent", "Production planning"],
      ["Quality Inspection Agent", "Quality inspection"],
      ["Maintenance Agent", "Equipment maintenance"],
      ["Supply Chain Agent", "Supply chain"],
    ],
    trustTitle: "One trust foundation across different industrial agents",
    trustLead: "Six composable capabilities express identity, boundaries, execution records, and long-term state. They create no automatic permission, business decision, or production certification.",
    infrastructureCapabilities: [
      ["Identity", "Identity", "Establish who an agent is, who it belongs to, and what capabilities it claims."],
      ["Boundary", "Boundary", "Express what an agent may and may not do."],
      ["Evidence", "Evidence", "Retain traceable records of tasks, process, and outcomes."],
      ["Health", "Health", "Assess reliability, risk, and stability over long-running operation."],
      ["Memory", "Memory", "Organize referencable execution history and experience."],
      ["Reputation", "Reputation", "Build a long-term, reviewable record of trustworthy performance."],
    ],
    stackAria: "TITMAS Across Industries",
    stackLabels: ["Industry Applications", "Industrial AI Agents", "TITMAS Trust Infrastructure", "Agent Framework / MCP", "Models + Data + Devices"],
    flowTitle: "How an industrial task enters a trusted execution path",
    flowLead: "This flow explains the infrastructure role. It does not simulate a factory-control system.",
    steps: [
      ["01", "Register identity", "Record the agent, version, owner, and capability claims."],
      ["02", "Accept a task", "Associate the task objective with permitted operational boundaries."],
      ["03", "Execute", "The industry agent runs in its own runtime and business system."],
      ["04", "Generate Evidence", "Retain intent, process, outcome, and integrity summaries."],
      ["05", "Issue an execution record", "Produce a referencable and replayable execution record."],
      ["06", "Evaluate health", "Observe reliability and risk from existing records."],
    ],
    boundaryTitle: "What TITMAS does here—and what it does not",
    provides: "TITMAS provides",
    providesItems: ["Trust objects and open specifications", "Adapter contracts and conformance boundaries", "Referencable structures for evidence, health, and history"],
    excludes: "TITMAS does not provide",
    excludesItems: ["MES or production-planning systems", "Industrial AI platforms or device control", "Industry-solution sales, production certification, or safety guarantees"],
    demoTitle: "Explore the runnable reference demo",
    demoLead: "The Digital Cell Demo shows minimal trust objects, deterministic replay, and a health view. It is not a manufacturing system.",
    demoCta: "Open the Digital Cell Demo",
    medicalCta: "Medical Evidence Infrastructure",
    spaceCta: "Autonomous Space SAEP",
    profilesTitle: "From one manufacturing example to more industry profiles",
    profilesLead: "Industry profiles translate shared TITMAS trust structures into domain questions. Industry teams still own their systems, rules, and agents.",
    profileOpen: "Open the industry profile",
    profileCards: [
      ["HEALTHCARE", "Medical Evidence Infrastructure", "UDI-DICOM starts from device identity and imaging evidence to show how healthcare can reuse TITMAS."],
      ["AUTONOMOUS SPACE", "Space Agent Evidence Profile (SAEP)", "SAEP uses EEOAP to research verifiable execution evidence for high-risk autonomous space agents."],
    ],
    statusCta: "Review status and boundaries",
  },
} as const;

export function IndustryPage({ locale }: { locale: Locale }) {
  const c = content[locale];
  const copy = industryCopy[locale];
  const root = locale === "zh" ? "/" : "/en/";
  const demo = locale === "zh" ? "/digital-cell/" : "/en/digital-cell/";
  const medical = locale === "zh" ? "/industry/medical-evidence/" : "/en/industry/medical-evidence/";
  const space = locale === "zh" ? "/industry/space-agent-evidence/" : "/en/industry/space-agent-evidence/";
  const status = locale === "zh" ? "/status/" : "/en/status/";

  return (
    <div className="site industry-page" lang={c.lang}>
      <Header locale={locale} section="industries" />
      <StructuredPageData
        locale={locale}
        path={locale === "zh" ? "/industries/" : "/en/industries/"}
        title={copy.title}
        description={copy.lead}
        type="TechArticle"
      />
      <main id="main-content">
        <section className="industry-hero">
          <div className="industry-hero-shell">
            <nav className="breadcrumb" aria-label={locale === "zh" ? "面包屑导航" : "Breadcrumb"}>
              <a href={root}>{copy.home}</a><span>/</span><span aria-current="page">{copy.current}</span>
            </nav>
            <p className="section-kicker">{copy.eyebrow}</p>
            <h1>{copy.title}</h1>
            <p>{copy.lead}</p>
            <div className="industry-hero-actions">
              <a className="button button-primary" href="#ecosystem">
                {locale === "zh" ? "查看生态结构" : "View the ecosystem"}
              </a>
              <a className="button button-secondary" href={demo}>{copy.demoCta}</a>
              <a className="button button-secondary" href={medical}>{copy.medicalCta}</a>
              <a className="button button-secondary" href={space}>{copy.spaceCta}</a>
            </div>
          </div>
        </section>

        <section className="section industry-roles" id="ecosystem">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">INDUSTRY AGENTS</p>
              <h2>{copy.rolesTitle}</h2>
              <p>{copy.rolesLead}</p>
            </div>
            <div className="industry-role-grid">
              {copy.manufacturingAgents.map(([name, description], index) => (
                <article key={name}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <code>{name}</code>
                  <h3>{description}</h3>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="section industry-trust">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">TITMAS TRUST INFRASTRUCTURE</p>
              <h2>{copy.trustTitle}</h2>
              <p>{copy.trustLead}</p>
            </div>
            <div className="industry-trust-layout">
              <div className="industry-capabilities">
                {copy.infrastructureCapabilities.map(([name, title, description]) => (
                  <article key={name}>
                    <code>{name}</code>
                    <div><h3>{title}</h3><p>{description}</p></div>
                  </article>
                ))}
              </div>
              <div className="ecosystem-stack industry-stack" role="img" aria-label={copy.stackAria}>
                {copy.stackLabels.map((label, index) => (
                  <div className={index === 2 ? "stack-core" : ""} key={label}>
                    <span>{String(index + 1).padStart(2, "0")}</span>
                    <strong>{label}</strong>
                    {index < copy.stackLabels.length - 1 && <i aria-hidden="true">↓</i>}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="section industry-flow">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">TRUSTED EXECUTION PATH</p>
              <h2>{copy.flowTitle}</h2>
              <p>{copy.flowLead}</p>
            </div>
            <ol>
              {copy.steps.map(([number, title, description]) => (
                <li key={number}>
                  <span>{number}</span><div><h3>{title}</h3><p>{description}</p></div>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="section industry-boundary">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">EXPLICIT BOUNDARY</p>
              <h2>{copy.boundaryTitle}</h2>
            </div>
            <div className="industry-boundary-grid">
              <article>
                <strong>{copy.provides}</strong>
                <ul>{copy.providesItems.map((item) => <li key={item}>{item}</li>)}</ul>
              </article>
              <article className="industry-boundary-excludes">
                <strong>{copy.excludes}</strong>
                <ul>{copy.excludesItems.map((item) => <li key={item}>{item}</li>)}</ul>
              </article>
            </div>
          </div>
        </section>

        <section className="section industry-profiles">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">INDUSTRY APPLICATION PROFILES</p>
              <h2>{copy.profilesTitle}</h2>
              <p>{copy.profilesLead}</p>
            </div>
            <div className="industry-profile-grid">
              {copy.profileCards.map(([label, title, description], index) => (
                <a href={index === 0 ? medical : space} key={label}>
                  <code>{label}</code>
                  <h3>{title}</h3>
                  <p>{description}</p>
                  <strong>{copy.profileOpen} <span>↗</span></strong>
                </a>
              ))}
            </div>
          </div>
        </section>

        <section className="industry-demo-cta">
          <div>
            <p className="section-kicker">REFERENCE DEMO</p>
            <h2>{copy.demoTitle}</h2>
            <p>{copy.demoLead}</p>
          </div>
          <div>
            <a className="button button-secondary" href={demo}>{copy.demoCta}</a>
            <a href={status}>{copy.statusCta} <span>↗</span></a>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
