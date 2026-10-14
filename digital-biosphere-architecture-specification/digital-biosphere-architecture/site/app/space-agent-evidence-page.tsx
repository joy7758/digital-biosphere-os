import type { Locale } from "./site-content";
import { Footer, Header } from "./site-shell";
import styles from "./industry/space-agent-evidence/space-agent-evidence.module.css";

const GITHUB_URL = "https://github.com/joy7758/agent-evidence/tree/main/extensions/space";
const DOI_URL = "https://doi.org/10.5281/zenodo.21393369";
const CONCEPT_DOI = "10.5281/zenodo.19334061";

const copy = {
  zh: {
    home: "TITMAS 首页",
    applications: "行业应用",
    title: "自主航天智能体可信执行",
    englishTitle: "Space Agent Evidence Profile (SAEP)",
    lead: "SAEP 是 TITMAS 面向自主航天系统的行业应用剖面，用于验证数字生物圈架构在高风险自主环境中的可信执行能力。",
    relation: "TITMAS 提供跨行业的可信基础设施；SAEP 将 EEOAP 执行证据结构应用到卫星、空间机器人与未来深空自主系统的研究场景。",
    contextTitle: "高风险自主任务不能只留下运行日志",
    contextLead: "随着更多任务由人工智能智能体自主完成，系统需要保留可独立检查的身份、权限上下文、决策依据、执行过程与责任分析线索。",
    questions: [
      "哪个智能体执行了操作？",
      "它是否拥有相应权限？",
      "它依据什么信息做出决策？",
      "执行过程是否可以被验证？",
      "事后如何进行责任分析？",
    ],
    capabilityTitle: "SAEP 为完成后的操作形成可核验对象",
    capabilityLead: "SAEP 扩展 EEOAP 的证据模型，描述自主航天智能体如何留下有边界、可引用、可离线检查的执行证据。",
    capabilities: [
      ["Identity & Role Context", "身份与角色上下文", "关联空间对象、智能体角色与声明的授权引用。"],
      ["Decision Evidence", "决策过程证据", "保留决策输入、约束与结果之间的可检查关系。"],
      ["Execution Records", "执行记录", "记录已经完成的操作及其输入、输出和过程回执。"],
      ["Verifiable Evidence Objects", "可验证证据对象", "把证据、来源、完整性摘要和验证结果组织为结构化对象。"],
      ["Offline Verification", "离线验证能力", "允许审查者在原始 Runtime 之外复核证据包。"],
    ],
    architectureTitle: "从数字生物圈到航天应用剖面",
    architectureLead: "SAEP 不是另一个航天控制平台。它位于行业 Agent 与 EEOAP 证据层之间，用一个有界研究案例说明 TITMAS 如何支撑高风险行业。",
    healthcare: "医疗",
    healthcareProfile: "UDI-DICOM",
    space: "航天",
    spaceProfile: "SAEP",
    evidenceLayer: "EEOAP Evidence Layer",
    runtime: "Runtime Verification",
    statusTitle: "SAEP v0.1 公开状态",
    statusLead: "这些状态只描述已归档的研究快照。合成验证结果不等于外部验证、飞行性能或航天认证。",
    statuses: [
      ["RESEARCH_PROTOTYPE", "Research prototype", "开放研究原型，不是任务运行系统。"],
      ["OPEN_RESEARCH_ARTIFACT", "Open research artifact", "规范、Schema、Validator、示例与研究材料公开可查。"],
      ["SYNTHETIC_VALIDATION_COMPLETED", "Synthetic validation completed", "本地确定性基准使用单一合成 fixture；不是外部验证。"],
      ["DOI_ARCHIVED", "DOI archived", "SAEP v0.1 研究快照已通过版本 DOI 归档。"],
    ],
    resourcesTitle: "公开资源与引用",
    resourcesLead: "代码与研究入口位于 agent-evidence；引用 SAEP v0.1 时使用版本 DOI。",
    github: "查看 GitHub 研究入口",
    zenodo: "打开 Zenodo DOI",
    citationLabel: "建议引用",
    citation: "Zhang, B. (2026). Space Agent Evidence Profile (SAEP) v0.1 (Version saep-v0.1-research). Zenodo. https://doi.org/10.5281/zenodo.21393369",
    conceptDoiLabel: "项目 concept DOI",
    boundaryTitle: "行业应用剖面，不是航天认证",
    boundaryLead: "SAEP 的目标不是替代航天任务系统，而是在未来自主航天生态中研究可信执行证据基础设施。",
    boundaries: [
      "NASA_ADOPTION_CLAIM=false",
      "ESA_ADOPTION_CLAIM=false",
      "FDO_ADOPTION_CLAIM=false",
      "FLIGHT_CERTIFICATION_CLAIM=false",
      "SPACE_QUALIFICATION_CLAIM=false",
      "INDUSTRIAL_DEPLOYMENT_CLAIM=false",
      "MISSION_SAFETY_GUARANTEE=false",
      "PRODUCTION_READY=false",
    ],
  },
  en: {
    home: "TITMAS home",
    applications: "Applications",
    title: "Trusted execution for autonomous space agents",
    englishTitle: "Space Agent Evidence Profile (SAEP)",
    lead: "SAEP is a vertical application profile of TITMAS for autonomous space systems, used to examine trusted execution in high-risk autonomous environments.",
    relation: "TITMAS provides cross-industry trust infrastructure. SAEP applies the EEOAP execution-evidence structure to research scenarios involving satellites, space robotics, and future deep-space autonomy.",
    contextTitle: "High-risk autonomous missions need more than runtime logs",
    contextLead: "As AI agents perform more tasks autonomously, systems need independently inspectable identity, authorization context, decision grounds, execution history, and accountability clues.",
    questions: [
      "Which agent performed the operation?",
      "Did it have the declared authorization?",
      "What information informed its decision?",
      "Can the execution process be verified?",
      "How can the operation be reviewed afterward?",
    ],
    capabilityTitle: "SAEP forms verifiable objects for completed operations",
    capabilityLead: "SAEP extends the EEOAP evidence model to describe bounded, referencable, and offline-verifiable execution evidence for autonomous space agents.",
    capabilities: [
      ["Identity & Role Context", "Identity and role context", "Relate the space object, agent role, and declared authorization references."],
      ["Decision Evidence", "Decision-process evidence", "Retain inspectable relationships among decision inputs, constraints, and outcomes."],
      ["Execution Records", "Execution records", "Record completed operations with their inputs, outputs, and process receipts."],
      ["Verifiable Evidence Objects", "Verifiable evidence objects", "Package evidence, provenance, integrity summaries, and validation results."],
      ["Offline Verification", "Offline verification", "Let reviewers inspect an evidence bundle outside the originating runtime."],
    ],
    architectureTitle: "From Digital Biosphere to a space application profile",
    architectureLead: "SAEP is not another spacecraft-control platform. It sits between industry agents and the EEOAP evidence layer as a bounded research case for high-risk industries.",
    healthcare: "Healthcare",
    healthcareProfile: "UDI-DICOM",
    space: "Space",
    spaceProfile: "SAEP",
    evidenceLayer: "EEOAP Evidence Layer",
    runtime: "Runtime Verification",
    statusTitle: "Public status of SAEP v0.1",
    statusLead: "These labels describe an archived research snapshot only. Synthetic validation is not external validation, flight performance, or space certification.",
    statuses: [
      ["RESEARCH_PROTOTYPE", "Research prototype", "An open research prototype, not a mission operations system."],
      ["OPEN_RESEARCH_ARTIFACT", "Open research artifact", "The specification, schema, validator, example, and research material are publicly inspectable."],
      ["SYNTHETIC_VALIDATION_COMPLETED", "Synthetic validation completed", "The local deterministic benchmark uses one synthetic fixture; it is not external validation."],
      ["DOI_ARCHIVED", "DOI archived", "The SAEP v0.1 research snapshot has a version DOI."],
    ],
    resourcesTitle: "Public resources and citation",
    resourcesLead: "The code and research entry live in agent-evidence. Cite the version DOI when referring specifically to SAEP v0.1.",
    github: "Open the GitHub research entry",
    zenodo: "Open the Zenodo DOI",
    citationLabel: "Suggested citation",
    citation: "Zhang, B. (2026). Space Agent Evidence Profile (SAEP) v0.1 (Version saep-v0.1-research). Zenodo. https://doi.org/10.5281/zenodo.21393369",
    conceptDoiLabel: "Project concept DOI",
    boundaryTitle: "An industry application profile, not space certification",
    boundaryLead: "SAEP does not replace a space mission system. It researches trusted execution evidence infrastructure for future autonomous space ecosystems.",
    boundaries: [
      "NASA_ADOPTION_CLAIM=false",
      "ESA_ADOPTION_CLAIM=false",
      "FDO_ADOPTION_CLAIM=false",
      "FLIGHT_CERTIFICATION_CLAIM=false",
      "SPACE_QUALIFICATION_CLAIM=false",
      "INDUSTRIAL_DEPLOYMENT_CLAIM=false",
      "MISSION_SAFETY_GUARANTEE=false",
      "PRODUCTION_READY=false",
    ],
  },
} as const;

export function SpaceAgentEvidencePage({ locale }: { locale: Locale }) {
  const c = copy[locale];
  const root = locale === "zh" ? "/" : "/en/";
  const applications = locale === "zh" ? "/applications/" : "/en/applications/";
  const medical = locale === "zh" ? "/industry/medical-evidence/" : "/en/industry/medical-evidence/";
  const route = locale === "zh" ? "/industry/space-agent-evidence/" : "/en/industry/space-agent-evidence/";

  const structuredData = {
    "@context": "https://schema.org",
    "@type": "TechArticle",
    headline: c.englishTitle,
    alternativeHeadline: c.title,
    description: c.lead,
    inLanguage: locale === "zh" ? "zh-CN" : "en",
    url: `https://redcrag.cn${route}`,
    isBasedOn: [GITHUB_URL, DOI_URL],
    about: [
      "Space Agent Evidence Profile",
      "Autonomous Space Systems",
      "AI Agent Governance",
      "Execution Evidence",
      "Digital Biosphere",
    ],
    citation: c.citation,
  };

  return (
    <div className="site" lang={locale === "zh" ? "zh-CN" : "en"}>
      <Header locale={locale} section="spaceIndustry" />
      <main className={styles.page} id="main-content">
        <section className={styles.hero}>
          <div className={styles.orbit} aria-hidden="true"><i /><i /><i /></div>
          <div className={styles.shell}>
            <nav className={styles.breadcrumb} aria-label={locale === "zh" ? "面包屑导航" : "Breadcrumb"}>
              <a href={root}>{c.home}</a><span>/</span>
              <a href={applications}>{c.applications}</a><span>/</span>
              <span aria-current="page">SAEP</span>
            </nav>
            <p className={styles.kicker}>INDUSTRY APPLICATION PROFILE / AUTONOMOUS SPACE</p>
            <h1>{c.title}</h1>
            <p className={styles.englishTitle}>{c.englishTitle}</p>
            <p className={styles.lead}>{c.lead}</p>
            <blockquote>{c.relation}</blockquote>
            <div className={styles.truth}>
              <code>SAEP_VERSION=v0.1</code>
              <code>SAEP_STATUS=RESEARCH_PROTOTYPE</code>
              <code>VERTICAL_APPLICATION_PROFILE=true</code>
              <code>BASE_PROFILE=EEOAP@0.1</code>
              <code>EVIDENCE_ORIGIN=SYNTHETIC</code>
            </div>
          </div>
        </section>

        <section className={styles.problem}>
          <div className={styles.shell}>
            <p className={styles.kicker}>WHY / ACCOUNTABILITY QUESTIONS</p>
            <div className={styles.problemGrid}>
              <div><h2>{c.contextTitle}</h2><p>{c.contextLead}</p></div>
              <ol>
                {c.questions.map((question, index) => (
                  <li key={question}><span>{String(index + 1).padStart(2, "0")}</span><strong>{question}</strong></li>
                ))}
              </ol>
            </div>
          </div>
        </section>

        <section className={styles.capability}>
          <div className={styles.shell}>
            <p className={styles.kicker}>SAEP / EVIDENCE SURFACES</p>
            <h2>{c.capabilityTitle}</h2>
            <p className={styles.sectionLead}>{c.capabilityLead}</p>
            <div className={styles.capabilityGrid}>
              {c.capabilities.map(([code, title, description], index) => (
                <article key={code}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <code>{code}</code>
                  <h3>{title}</h3>
                  <p>{description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className={styles.architecture}>
          <div className={styles.shell}>
            <p className={styles.kicker}>ARCHITECTURE RELATIONSHIP</p>
            <h2>{c.architectureTitle}</h2>
            <p className={styles.sectionLead}>{c.architectureLead}</p>
            <div className={styles.architectureMap} role="img" aria-label={c.architectureTitle}>
              <div className={`${styles.architectureNode} ${styles.architectureCore}`}>
                <small>STRATEGIC FRAME + TRUST INFRASTRUCTURE</small>
                <strong>Digital Biosphere / TITMAS</strong>
              </div>
              <i aria-hidden="true">↓</i>
              <div className={styles.architectureNode}>
                <small>TRANSLATION LAYER</small>
                <strong>Industry Application Profiles</strong>
              </div>
              <i aria-hidden="true">↓</i>
              <div className={styles.profileBranches}>
                <a href={medical}>
                  <small>{c.healthcare}</small>
                  <strong>{c.healthcareProfile}</strong>
                </a>
                <div>
                  <small>{c.space}</small>
                  <strong>{c.spaceProfile}</strong>
                </div>
              </div>
              <i aria-hidden="true">↓</i>
              <div className={`${styles.architectureNode} ${styles.evidenceNode}`}>
                <small>EXECUTION EVIDENCE</small>
                <strong>{c.evidenceLayer}</strong>
              </div>
              <i aria-hidden="true">↓</i>
              <div className={styles.architectureNode}>
                <small>OFFLINE / REVIEWABLE</small>
                <strong>{c.runtime}</strong>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.status}>
          <div className={styles.shell}>
            <p className={styles.kicker}>PUBLIC RESEARCH STATUS</p>
            <h2>{c.statusTitle}</h2>
            <p className={styles.sectionLead}>{c.statusLead}</p>
            <div className={styles.statusGrid}>
              {c.statuses.map(([code, title, description]) => (
                <article key={code}>
                  <code>{`${code}=true`}</code>
                  <h3>{title}</h3>
                  <p>{description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className={styles.resources}>
          <div className={styles.shell}>
            <div>
              <p className={styles.kicker}>OPEN RESEARCH ARTIFACT</p>
              <h2>{c.resourcesTitle}</h2>
              <p>{c.resourcesLead}</p>
              <div className={styles.resourceLinks}>
                <a className="button button-primary" href={GITHUB_URL} target="_blank" rel="noreferrer">{c.github}</a>
                <a className="button button-secondary" href={DOI_URL} target="_blank" rel="noreferrer">{c.zenodo}</a>
              </div>
            </div>
            <aside>
              <span>{c.citationLabel}</span>
              <cite>{c.citation}</cite>
              <cite><strong>{c.conceptDoiLabel}:</strong> {CONCEPT_DOI}</cite>
            </aside>
          </div>
        </section>

        <section className={styles.boundary}>
          <div className={styles.shell}>
            <div>
              <p className={styles.kicker}>EXPLICIT NON-CLAIMS</p>
              <h2>{c.boundaryTitle}</h2>
              <p>{c.boundaryLead}</p>
            </div>
            <div className={styles.boundaryCodes}>
              {c.boundaries.map((boundary) => <code key={boundary}>{boundary}</code>)}
            </div>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }} />
    </div>
  );
}
