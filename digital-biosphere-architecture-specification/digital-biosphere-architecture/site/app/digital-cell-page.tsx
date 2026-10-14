import type { CSSProperties } from "react";
import type { Locale } from "./site-content";
import { Footer, Header } from "./site-shell";
import { StructuredPageData } from "./structured-page-data";
import styles from "./digital-cell/digital-cell.module.css";

const pageCopy = {
  zh: {
    breadcrumb: ["TITMAS 首页", "行业应用", "Digital Cell Demo"],
    eyebrow: "REFERENCE DEMO · v0.1.0",
    title: <>让 Agent 的执行<br />变得可观察。</>,
    lead: "TITMAS Digital Cell Demo 是一个最小参考实现，展示 AI Agent 如何具备身份、边界、执行证据和健康状态。",
    release: "查看公开 Release",
    understand: "理解 Digital Cell",
    whyTitle: "能执行，不等于能被理解。",
    whyLead: "未来 Agent 系统需要回答四个基础问题：它是谁、允许做什么、实际做了什么、发生异常后处于什么状态。",
    questions: [["Who?", "可追溯身份"], ["Within what boundary?", "明确行为边界"], ["What happened?", "执行证据"], ["What state now?", "健康观察"]],
    architectureTitle: "六个简单、受限、可组合的对象",
    architectureLead: "Digital Cell 不创造无限自治中心。每个对象只有明确职责，Evidence 不等于 Permission，Health 不等于 Certification，Reputation 不等于 Authority。",
    objects: [
      ["Identity", "身份", "标识主体、版本、用途与来源。"],
      ["Boundary", "边界", "声明允许行为、禁止行为与能力限制。"],
      ["Evidence", "证据", "记录意图、执行、结果与完整性摘要。"],
      ["Health", "健康", "从已有记录派生可观察状态，不构成认证。"],
      ["Memory", "记忆", "保留执行、失败、恢复与演化历史。"],
      ["Reputation", "声誉", "汇总可靠性和证据质量历史。"],
    ],
    architectureCaption: "Digital Cell v0.1 Architecture · 最小参考模型，不是生产架构。",
    lifecycleTitle: "一次执行，成为一段可追溯历史。",
    lifecycle: [["Birth", "出生"], ["Execution", "执行"], ["Evidence", "证据"], ["Health", "健康评估"], ["Recovery", "恢复"], ["Evolution", "演化状态"]],
    lifecycleCaption: "Lifecycle view · 状态变化有记录，但不产生认证或自治治理权力。",
    evidenceTitle: "可复现，不被过度解释。",
    evidenceLead: "冻结的参考运行通过 7 项测试，生成 12 条证据记录，并通过确定性重放和 SHA-256 完整性检查。",
    runTitle: "一个实现，一个入口，零第三方依赖。",
    runLead: "需要 Python 3。Release 和源码均位于公开 GitHub 仓库。",
    repo: "打开 GitHub 仓库",
    boundaryTitle: "这个 Demo 明确不证明什么",
    boundaryLead: "它只展示一个 Agent 如何变得可观察、可验证并可进行健康状态评估。健康视图不是安全保证，证据完整不等于智能正确。",
  },
  en: {
    breadcrumb: ["TITMAS home", "Applications", "Digital Cell Demo"],
    eyebrow: "REFERENCE DEMO · v0.1.0",
    title: <>Make agent execution<br />observable.</>,
    lead: "The TITMAS Digital Cell Demo is a minimal reference implementation showing how an AI agent can carry identity, boundaries, execution evidence, and health state.",
    release: "View public release",
    understand: "Understand Digital Cell",
    whyTitle: "Being executable does not make an agent understandable.",
    whyLead: "Future agent systems need to answer four basic questions: who it is, what it may do, what actually happened, and what state it is in after an anomaly.",
    questions: [["Who?", "Traceable identity"], ["Within what boundary?", "Explicit behavior boundary"], ["What happened?", "Execution evidence"], ["What state now?", "Health observation"]],
    architectureTitle: "Six simple, bounded, composable objects",
    architectureLead: "A Digital Cell does not create an unlimited autonomy center. Each object has one explicit responsibility: Evidence is not Permission, Health is not Certification, and Reputation is not Authority.",
    objects: [
      ["Identity", "Identity", "Identify the subject, version, purpose, and source."],
      ["Boundary", "Boundary", "Declare permitted behavior, prohibited behavior, and capability limits."],
      ["Evidence", "Evidence", "Record intent, execution, result, and integrity summaries."],
      ["Health", "Health", "Derive observable state from existing records; this is not certification."],
      ["Memory", "Memory", "Retain execution, failure, recovery, and evolution history."],
      ["Reputation", "Reputation", "Summarize reliability and evidence-quality history."],
    ],
    architectureCaption: "Digital Cell v0.1 Architecture · Minimal reference model, not a production architecture.",
    lifecycleTitle: "One execution becomes traceable history.",
    lifecycle: [["Birth", "Identity"], ["Execution", "Operation"], ["Evidence", "Record"], ["Health", "Evaluation"], ["Recovery", "Recovery"], ["Evolution", "State"]],
    lifecycleCaption: "Lifecycle view · State changes are recorded but create no certification or autonomous governance authority.",
    evidenceTitle: "Reproducible, without over-interpretation.",
    evidenceLead: "The frozen reference run passes 7 tests, produces 12 evidence records, and passes deterministic replay and SHA-256 integrity checks.",
    runTitle: "One implementation, one entry point, zero third-party dependencies.",
    runLead: "Python 3 is required. The release and source are available in the public GitHub repository.",
    repo: "Open the GitHub repository",
    boundaryTitle: "What this demo explicitly does not prove",
    boundaryLead: "It only shows how an agent can become observable, verifiable, and health-assessable. A health view is not a safety guarantee, and evidence integrity does not make an agent correct.",
  },
} as const;

export function DigitalCellPage({ locale }: { locale: Locale }) {
  const copy = pageCopy[locale];
  const root = locale === "zh" ? "/" : "/en/";
  const industries = locale === "zh" ? "/industries/" : "/en/industries/";

  return (
    <div className="site" lang={locale === "zh" ? "zh-CN" : "en"}>
      <Header locale={locale} section="demo" />
      <StructuredPageData
        locale={locale}
        path={locale === "zh" ? "/digital-cell/" : "/en/digital-cell/"}
        title={locale === "zh" ? "TITMAS Digital Cell Demo v0.1" : "TITMAS Digital Cell Demo v0.1"}
        description={copy.lead}
        type="TechArticle"
      />
      <main className={styles.page} id="main-content">
        <section className={styles.hero}>
          <div>
            <nav className={styles.breadcrumb} aria-label={locale === "zh" ? "面包屑导航" : "Breadcrumb"}>
              <a href={root}>{copy.breadcrumb[0]}</a><span>/</span>
              <a href={industries}>{copy.breadcrumb[1]}</a><span>/</span>
              <span aria-current="page">{copy.breadcrumb[2]}</span>
            </nav>
            <p className={styles.eyebrow}>{copy.eyebrow}</p>
            <h1>{copy.title}</h1>
            <p className={styles.lead}>{copy.lead}</p>
            <div className={styles.actions}>
              <a className={styles.primary} href="https://github.com/joy7758/titmas-demo/releases/tag/v0.1.0">{copy.release}</a>
              <a className={styles.secondary} href="#architecture">{copy.understand}</a>
            </div>
            <div className={styles.statusRow} aria-label="Release status">
              <code>REFERENCE_COMPLETE</code><code>REPLAY_PASS</code><code>APACHE-2.0</code>
            </div>
          </div>
          <div className={styles.cellVisual} aria-label="Six Digital Cell objects">
            <div className={styles.core}>Digital<br />Cell</div>
            {copy.objects.map(([name], index) => (
              <span key={name} className={styles.orbitItem} style={{ "--index": index } as CSSProperties}>{name}</span>
            ))}
          </div>
        </section>

        <section className={styles.problem}>
          <p className={styles.sectionTag}>WHY DIGITAL CELL</p>
          <div className={styles.problemLead}><h2>{copy.whyTitle}</h2><p>{copy.whyLead}</p></div>
          <div className={styles.questionGrid}>
            {copy.questions.map(([question, answer], index) => (
              <article key={question}><span>0{index + 1}</span><strong>{question}</strong><p>{answer}</p></article>
            ))}
          </div>
        </section>

        <section className={styles.architecture} id="architecture">
          <div className={styles.sectionHeading}>
            <p className={styles.sectionTag}>DIGITAL CELL ARCHITECTURE</p>
            <h2>{copy.architectureTitle}</h2><p>{copy.architectureLead}</p>
          </div>
          <div className={styles.objectGrid}>
            {copy.objects.map(([name, label, description], index) => (
              <article key={name}><span>0{index + 1}</span><h3>{name}</h3><strong>{label}</strong><p>{description}</p></article>
            ))}
          </div>
          <figure className={styles.figure}>
            <img src="/digital-cell/digital-cell-architecture.png" alt="Digital Cell v0.1 architecture" />
            <figcaption>{copy.architectureCaption}</figcaption>
          </figure>
        </section>

        <section className={styles.lifecycle}>
          <div className={styles.sectionHeading}><p className={styles.sectionTag}>BOUNDED LIFECYCLE</p><h2>{copy.lifecycleTitle}</h2></div>
          <div className={styles.lifecycleFlow}>
            {copy.lifecycle.map(([name, label], index) => <div key={name}><span>0{index + 1}</span><strong>{name}</strong><small>{label}</small></div>)}
          </div>
          <figure className={styles.figure}>
            <img src="/digital-cell/digital-cell-lifecycle.png" alt="Digital Cell bounded lifecycle" />
            <figcaption>{copy.lifecycleCaption}</figcaption>
          </figure>
        </section>

        <section className={styles.evidence} id="evidence">
          <div>
            <p className={styles.sectionTag}>VERIFIED REFERENCE RUN</p><h2>{copy.evidenceTitle}</h2><p>{copy.evidenceLead}</p>
            <div className={styles.metrics}>
              <div><strong>7/7</strong><span>Tests passed</span></div>
              <div><strong>12</strong><span>Evidence records</span></div>
              <div><strong>PASS</strong><span>Deterministic replay</span></div>
            </div>
          </div>
          <figure className={styles.reportFigure}><img src="/digital-cell/digital-cell-report.png" alt="Digital Cell reference execution report" /></figure>
        </section>

        <section className={styles.run} id="run">
          <div><p className={styles.sectionTag}>RUN LOCALLY</p><h2>{copy.runTitle}</h2><p>{copy.runLead}</p></div>
          <pre><code>{`git clone https://github.com/joy7758/titmas-demo.git
cd titmas-demo/examples/digital-cell
python3 -m unittest discover -s tests -v
python3 run.py`}</code></pre>
          <a href="https://github.com/joy7758/titmas-demo">{copy.repo} →</a>
        </section>

        <section className={styles.boundary}>
          <p className={styles.sectionTag}>INTERPRETATION BOUNDARY</p><h2>{copy.boundaryTitle}</h2>
          <div><span>NO DIGITAL LIFE CLAIM</span><span>NO AI CONSCIOUSNESS CLAIM</span><span>NO PRODUCTION CERTIFICATION</span><span>NO UNIVERSAL SAFETY CLAIM</span></div>
          <p>{copy.boundaryLead}</p>
        </section>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
