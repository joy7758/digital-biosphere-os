import type { Locale } from "./site-content";
import { Footer, Header } from "./site-shell";
import styles from "./industry/medical-evidence/medical-evidence-industry.module.css";

const copy = {
  zh: {
    home: "TITMAS 首页",
    industries: "行业应用",
    title: "医疗证据基础设施",
    englishTitle: "Medical Evidence Infrastructure",
    lead: "基于 TITMAS 的医疗设备、医疗流程和医疗智能体可信证据基础设施。",
    contextTitle: "为什么需要医疗证据基础设施？",
    contextLead: "未来医疗系统不是缺少数据，而是缺少能够被独立检查、持续引用和明确解释的可信证据链。",
    questions: ["数据来自哪个设备？", "哪个主体执行了操作？", "操作过程是否可验证？", "AI 决策是否具有过程证据？"],
    architectureTitle: "基于 TITMAS 的证据架构",
    architectureLead: "医疗证据不是另起一套封闭平台，而是在 Digital Biosphere 与 TITMAS 基础设施之上形成的有界行业应用方向。",
    titmasProvides: "TITMAS 提供",
    titmasItems: ["Identity", "Boundary", "Evidence", "Verification", "Memory", "Governance"],
    medicalProvides: "医疗方向扩展",
    medicalItems: ["UDI 映射", "DICOM 证据", "医疗设备规则", "临床工作流扩展"],
    roadmapTitle: "医疗证据三阶段路线",
    roadmapLead: "从设备身份一致性开始，再扩展到操作过程与医疗智能体过程证据。后两个阶段是方向，不是本站已实现能力。",
    stages: [
      {
        number: "01",
        name: "UDI-DICOM Evidence Profile",
        question: "设备是谁？",
        body: "表达医疗设备身份、影像对象、注册信息和外部证据之间的一致性验证关系。",
        details: ["设备身份", "影像对象", "登记引用", "证据 Manifest"],
        state: "REFERENCE_DEMO",
      },
      {
        number: "02",
        name: "Medical Device Operation Evidence",
        question: "设备做了什么？",
        body: "面向软件版本、操作会话、设备状态、人工干预和异常事件的可引用记录。",
        details: ["软件版本", "操作会话", "设备状态", "人工干预", "异常事件"],
        state: "DIRECTION_ONLY",
      },
      {
        number: "03",
        name: "Medical Agent Evidence",
        question: "AI 为什么这样决策？",
        body: "面向模型身份、工具调用、输入证据、策略约束和输出过程的证据表达。",
        details: ["模型身份", "工具调用", "输入证据", "策略约束", "输出过程"],
        state: "DIRECTION_ONLY",
      },
    ],
    demoTitle: "从第一个有界参考 Demo 开始",
    demoBody: "UDI-DICOM Evidence Validator Demo 使用模拟输入解释 Identity → Imaging → Evidence 的引用关系。它不查询真实登记库，也不执行医疗、临床或监管验证。",
    demoCta: "查看医疗证据 Demo",
    boundaryTitle: "行业应用，不是医疗软件",
    boundaries: ["不是医疗诊断系统", "不是临床安全验证", "不是医疗认证系统", "不使用患者、医院或真实登记库数据"],
  },
  en: {
    home: "TITMAS home",
    industries: "Industry applications",
    title: "Medical Evidence Infrastructure",
    englishTitle: "A TITMAS Industry Application",
    lead: "Trustworthy evidence infrastructure for medical devices, medical operations, and medical agents, built on TITMAS.",
    contextTitle: "Why does healthcare need evidence infrastructure?",
    contextLead: "Future medical systems will not lack data. They will lack trustworthy evidence chains that can be independently inspected, continuously referenced, and clearly interpreted.",
    questions: ["Which device produced the data?", "Which subject performed the operation?", "Can the process be verified?", "Does an AI decision retain process evidence?"],
    architectureTitle: "Evidence architecture built on TITMAS",
    architectureLead: "Medical evidence is not a separate closed platform. It is a bounded industry direction built above Digital Biosphere and TITMAS infrastructure.",
    titmasProvides: "TITMAS provides",
    titmasItems: ["Identity", "Boundary", "Evidence", "Verification", "Memory", "Governance"],
    medicalProvides: "Medical direction extends",
    medicalItems: ["UDI mapping", "DICOM evidence", "Medical-device rules", "Clinical-workflow extensions"],
    roadmapTitle: "Three-stage medical evidence roadmap",
    roadmapLead: "Start with device identity consistency, then extend toward operation evidence and medical-agent process evidence. The latter two stages are directions, not implemented site capabilities.",
    stages: [
      {
        number: "01",
        name: "UDI-DICOM Evidence Profile",
        question: "Which device is it?",
        body: "Express consistency relationships across medical-device identity, imaging objects, registry references, and external evidence.",
        details: ["Device identity", "Imaging object", "Registry reference", "Evidence Manifest"],
        state: "REFERENCE_DEMO",
      },
      {
        number: "02",
        name: "Medical Device Operation Evidence",
        question: "What did the device do?",
        body: "Referencable records for software versions, operation sessions, device state, human intervention, and exception events.",
        details: ["Software version", "Operation session", "Device state", "Human intervention", "Exception event"],
        state: "DIRECTION_ONLY",
      },
      {
        number: "03",
        name: "Medical Agent Evidence",
        question: "Why did the AI decide this?",
        body: "Evidence expressions for model identity, tool calls, input evidence, policy constraints, and output process.",
        details: ["Model identity", "Tool calls", "Input evidence", "Policy constraints", "Output process"],
        state: "DIRECTION_ONLY",
      },
    ],
    demoTitle: "Start with the first bounded reference demo",
    demoBody: "The UDI-DICOM Evidence Validator Demo uses synthetic input to explain Identity → Imaging → Evidence references. It performs no real registry, medical, clinical, or regulatory validation.",
    demoCta: "Open the medical evidence demo",
    boundaryTitle: "An industry application, not medical software",
    boundaries: ["Not a medical diagnosis system", "Not clinical-safety validation", "Not a medical certification system", "No patient, hospital, or real registry data"],
  },
} as const;

export function MedicalEvidenceIndustryPage({ locale }: { locale: Locale }) {
  const c = copy[locale];
  const root = locale === "zh" ? "/" : "/en/";
  const industries = locale === "zh" ? "/industries/" : "/en/industries/";
  const demo = locale === "zh" ? "/demo/medical-evidence/" : "/en/demo/medical-evidence/";

  const structuredData = {
    "@context": "https://schema.org",
    "@type": "TechArticle",
    headline: c.title,
    alternativeHeadline: c.englishTitle,
    description: c.lead,
    inLanguage: locale === "zh" ? "zh-CN" : "en",
    url: `https://redcrag.cn${locale === "zh" ? "/industry/medical-evidence/" : "/en/industry/medical-evidence/"}`,
    about: ["TITMAS", "Medical Evidence Infrastructure", "UDI-DICOM", "Healthcare AI Governance"],
  };

  return (
    <div className="site" lang={locale === "zh" ? "zh-CN" : "en"}>
      <Header locale={locale} section="medicalIndustry" />
      <main className={styles.page} id="main-content">
        <section className={styles.hero}>
          <div className={styles.heroGrid} aria-hidden="true" />
          <div className={styles.shell}>
            <nav className={styles.breadcrumb} aria-label={locale === "zh" ? "面包屑导航" : "Breadcrumb"}>
              <a href={root}>{c.home}</a><span>/</span>
              <a href={industries}>{c.industries}</a><span>/</span>
              <span aria-current="page">{c.title}</span>
            </nav>
            <p className={styles.kicker}>INDUSTRY APPLICATION / MEDICAL EVIDENCE</p>
            <h1>{c.title}</h1>
            <p className={styles.englishTitle}>{c.englishTitle}</p>
            <p className={styles.lead}>{c.lead}</p>
            <div className={styles.truth}>
              <code>BUILT_ON_TITMAS=true</code>
              <code>INDEPENDENT_MEDICAL_PLATFORM=false</code>
              <code>PRODUCTION_READY=false</code>
            </div>
          </div>
        </section>

        <section className={styles.problem}>
          <div className={styles.shell}>
            <p className={styles.kicker}>WHY / PROBLEM CONTEXT</p>
            <div className={styles.problemGrid}>
              <div><h2>{c.contextTitle}</h2><p>{c.contextLead}</p></div>
              <ol>{c.questions.map((question, index) => <li key={question}><span>0{index + 1}</span><strong>{question}</strong></li>)}</ol>
            </div>
          </div>
        </section>

        <section className={styles.architecture}>
          <div className={styles.shell}>
            <p className={styles.kicker}>EVIDENCE LAYER / TRUST NETWORK</p>
            <h2>{c.architectureTitle}</h2>
            <p className={styles.sectionLead}>{c.architectureLead}</p>
            <div className={styles.architectureGrid}>
              <div className={styles.stack} role="img" aria-label={c.architectureTitle}>
                {["Digital Biosphere", "TITMAS Infrastructure", "Evidence Object", "Medical Evidence Direction"].map((label, index) => (
                  <div key={label} className={index === 1 ? styles.stackCore : ""}>
                    <span>0{index + 1}</span><strong>{label}</strong>{index < 3 && <i>↓</i>}
                  </div>
                ))}
                <div className={styles.directions}>
                  <span>UDI-DICOM Evidence</span>
                  <span>Medical Operation Evidence</span>
                  <span>Medical Agent Evidence</span>
                </div>
              </div>
              <div className={styles.capabilities}>
                <article><span>{c.titmasProvides}</span><ul>{c.titmasItems.map((item) => <li key={item}>{item}</li>)}</ul></article>
                <article><span>{c.medicalProvides}</span><ul>{c.medicalItems.map((item) => <li key={item}>{item}</li>)}</ul></article>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.roadmap}>
          <div className={styles.shell}>
            <p className={styles.kicker}>ROADMAP / THREE STAGES</p>
            <h2>{c.roadmapTitle}</h2>
            <p className={styles.sectionLead}>{c.roadmapLead}</p>
            <div className={styles.stageGrid}>
              {c.stages.map((stage) => (
                <article key={stage.number}>
                  <div><span>{stage.number}</span><code>{stage.state}</code></div>
                  <h3>{stage.name}</h3>
                  <strong>{stage.question}</strong>
                  <p>{stage.body}</p>
                  <ul>{stage.details.map((detail) => <li key={detail}>{detail}</li>)}</ul>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className={styles.demoCta}>
          <div className={styles.shell}>
            <div>
              <p className={styles.kicker}>REFERENCE DEMO</p>
              <h2>{c.demoTitle}</h2>
              <p>{c.demoBody}</p>
              <a className="button button-primary" href={demo}>{c.demoCta}</a>
            </div>
            <aside>
              <span>{c.boundaryTitle}</span>
              {c.boundaries.map((boundary) => <p key={boundary}>{boundary}</p>)}
            </aside>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }} />
    </div>
  );
}
