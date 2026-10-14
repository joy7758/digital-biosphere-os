import type { Locale } from "./site-content";
import { Footer, Header } from "./site-shell";
import { StructuredPageData } from "./structured-page-data";
import styles from "./industry/media-evidence/media-evidence-industry.module.css";

const REFERENCE_COMMIT = "7eac452f66a2b7de525543f80b9a7cf1465ef9a1";

const copy = {
  zh: {
    title: "面向人工智能生成内容安全的智能审核证据链",
    subtitle: "TITMAS 证据架构（TITMAS Evidence Architecture）在广播电视和网络视听场景中的参考实现。",
    boundary: "本页面介绍本地合成参考实现，不提供内容真实性认证、身份认证、法律证据、生产审核、外部标准认证或安全保证。",
    problemTitle: "行业问题：审核标签无法回答责任链",
    problemBody: "人工智能生成内容（AIGC）进入节目策划、制作、审核和播出流程后，单一的“通过/拒绝”结果无法说明请求来自哪里、谁被记录为执行主体、使用了哪些判断材料，以及争议如何复核。",
    labelTitle: "为什么最终审核标签不足",
    labelItems: ["标签不保留生成请求和授权记录", "标签不解释检测结果来自哪个工具和版本", "标签容易覆盖冲突、未知和人工暂缓", "标签难以独立复制完整性检查"],
    lifecycleTitle: "生成前、生成中、生成后",
    lifecycle: [
      ["生成前", "请求与授权状态", "记录希望生成什么、授权记录如何关联；APPROVED 仅是合成记录状态。"],
      ["生成中", "智能体执行与来源关联", "记录智能体、模型、工具和输出引用；不据此认证主体身份。"],
      ["生成后", "多来源证据、异议与审核决定", "保留冲突、补充材料和人工决定；不自动裁决内容真假。"],
    ],
    ecosystemTitle: "连接已有工具，不替代已有工具",
    ecosystemBody: "适配器（Adapter）将不同来源的观察结果规范化为证据对象（Evidence Object），使其进入责任链、异议记录和审核决定。",
    ecosystem: [
      ["内容来源与真实性联盟规范（C2PA）", "记录来源声明是否可用；本站不执行真实 C2PA 验证。"],
      ["人工智能生成内容检测", "记录模型、分数和方法；不超越底层检测模型能力。"],
      ["数字水印", "记录水印观察结果；不把存在或缺失升级为真实性结论。"],
      ["人工审核", "记录复核意见和业务决定；审核决定不等于事实判断。"],
    ],
    broadcastTitle: "广播电视节目策划、制作、审核和播出",
    broadcastBody: "在策划请求、生成授权状态、生产智能体执行、编辑修改、技术审核、人工复核和播出决定之间建立可引用记录，便于事后说明“谁、何时、基于什么材料做了什么”。",
    onlineTitle: "网络视听内容生产、申诉和争议复核",
    onlineBody: "把平台检测、来源声明、水印观察、人工反馈和申诉补充材料保留为并列证据；冲突可以进入异议记录（Challenge）而不是被静默覆盖。",
    routeTitle: "增量接入路线",
    route: ["先接入一个现有审核工具的模拟输出", "转换为最小证据对象", "加入引用链和负例", "由人工决定是否扩大接入范围"],
    statusTitle: "当前实现状态",
    statusBody: "v0.1.0 是本地合成参考实现（Reference Implementation）。当前公开页面只复现结构、引用、生命周期和文件完整性检查；不连接真实媒体、模型、身份系统或审核平台。",
    boundaryTitle: "能力边界",
    boundaries: ["不认证内容真实性", "不认证主体身份", "不构成法律证据", "不表示生产部署", "不声明外部标准兼容或认证", "不声明客户采用、投资回报或保证安全"],
    demoTitle: "进入在线演示",
    demoBody: "使用三个纯前端合成场景查看正常生命周期、证据冲突和篡改检测。页面不上传内容，也不作在线审核决定。",
    demoCta: "运行媒体证据演示",
  },
  en: {
    title: "Review evidence chains for AI-generated-content safety",
    subtitle: "A reference implementation of the TITMAS Evidence Architecture for broadcasting and online audiovisual workflows.",
    boundary: "This page describes a local synthetic reference implementation. It provides no content-truth, identity, legal-evidence, production-review, external-certification, or security-guarantee claim.",
    problemTitle: "Industry problem: a final label is not an accountability chain",
    problemBody: "When AI-generated content enters planning, production, review, and publication workflows, a single pass/reject label cannot explain the request, the recorded actor, the observations used, or how a dispute can be reviewed.",
    labelTitle: "Why a final review label is insufficient",
    labelItems: ["It does not retain the request and authorization record", "It does not identify the tool and version behind a result", "It can hide conflicts, unknowns, and human holds", "It cannot reproduce package-integrity checks by itself"],
    lifecycleTitle: "Before, during, and after generation",
    lifecycle: [
      ["Before", "Request and authorization state", "Record the requested task and linked authorization record; APPROVED is a synthetic record state only."],
      ["During", "Agent execution and source association", "Record agent, model, tool, and output references without authenticating identity."],
      ["After", "Multi-source evidence, challenge, and decision", "Retain conflict, additional material, and human decisions without automatic truth adjudication."],
    ],
    ecosystemTitle: "Connect existing tools without replacing them",
    ecosystemBody: "Adapters normalize observations into Evidence Objects so they can enter accountability chains, Challenge records, and review Decisions.",
    ecosystem: [
      ["Coalition for Content Provenance and Authenticity (C2PA)", "Record whether a provenance statement is available; no real C2PA validation runs here."],
      ["AIGC detector", "Record model, score, and method without exceeding the underlying detector."],
      ["Digital watermark", "Record a watermark observation without elevating presence or absence into truth."],
      ["Human review", "Record review opinions and business decisions; a decision is not a factual judgment."],
    ],
    broadcastTitle: "Broadcast planning, production, review, and publication",
    broadcastBody: "Create referencable records across planning requests, authorization state, production-agent execution, editing, technical review, human review, and publication decisions.",
    onlineTitle: "Online audiovisual production, appeals, and dispute review",
    onlineBody: "Retain platform detections, provenance statements, watermark observations, human feedback, and appeal material as parallel evidence; conflict can enter a Challenge instead of being overwritten.",
    routeTitle: "Incremental integration route",
    route: ["Start with one simulated tool output", "Convert it into a minimal Evidence Object", "Add references and negative cases", "Let humans decide whether to expand scope"],
    statusTitle: "Current implementation state",
    statusBody: "v0.1.0 is a local synthetic Reference Implementation. The public page reproduces structures, references, lifecycle, and file-integrity checks only; it connects no real media, model, identity system, or review platform.",
    boundaryTitle: "Capability boundaries",
    boundaries: ["No content-truth certification", "No identity authentication", "No legal-evidence claim", "No production-deployment claim", "No external-standard compatibility or certification claim", "No customer-adoption, return, or guaranteed-security claim"],
    demoTitle: "Open the online demo",
    demoBody: "Inspect normal lifecycle, evidence conflict, and tamper detection with three frontend-only synthetic scenarios. Nothing is uploaded and no online review decision is made.",
    demoCta: "Run the media evidence demo",
  },
} as const;

export function MediaEvidenceIndustryPage({ locale }: { locale: Locale }) {
  const c = copy[locale];
  const root = locale === "zh" ? "/" : "/en/";
  const applications = locale === "zh" ? "/applications/" : "/en/applications/";
  const demo = locale === "zh" ? "/demo/media-evidence/" : "/en/demo/media-evidence/";
  const path = locale === "zh" ? "/industry/media-evidence/" : "/en/industry/media-evidence/";

  return (
    <div className="site" lang={locale === "zh" ? "zh-CN" : "en"}>
      <Header locale={locale} section="mediaIndustry" />
      <StructuredPageData locale={locale} path={path} title={c.title} description={c.subtitle} type="TechArticle" dateModified="2026-08-01" />
      <main className={styles.page} id="main-content">
        <section className={styles.hero}>
          <div className={styles.shell}>
            <nav className={styles.breadcrumb} aria-label={locale === "zh" ? "面包屑导航" : "Breadcrumb"}><a href={root}>TITMAS</a><span>/</span><a href={applications}>{locale === "zh" ? "行业应用" : "Applications"}</a><span>/</span><span aria-current="page">{locale === "zh" ? "媒体证据" : "Media evidence"}</span></nav>
            <p className={styles.kicker}>{locale === "zh" ? "媒体证据场景配置（MEDIA EVIDENCE PROFILE）/ v0.1.0" : "MEDIA EVIDENCE PROFILE / v0.1.0"}</p>
            <h1>{c.title}</h1>
            <p className={styles.subtitle}>{c.subtitle}</p>
            <p className={styles.boundary} role="note">{c.boundary}</p>
            <div className={styles.truth}><code>LOCAL_SYNTHETIC_REFERENCE_IMPLEMENTATION</code><code>PRODUCTION_READY=false</code><code>TRUTH_VERIFICATION=false</code></div>
          </div>
        </section>

        <section className={styles.section}><div className={styles.shell}><p className={styles.kicker}>{locale === "zh" ? "01 / 行业问题（INDUSTRY PROBLEM）" : "01 / INDUSTRY PROBLEM"}</p><div className={styles.twoColumn}><div><h2>{c.problemTitle}</h2><p>{c.problemBody}</p></div><article><h3>{c.labelTitle}</h3><ul>{c.labelItems.map((item) => <li key={item}>{item}</li>)}</ul></article></div></div></section>

        <section className={`${styles.section} ${styles.tint}`}><div className={styles.shell}><p className={styles.kicker}>{locale === "zh" ? "02 / 治理生命周期（GOVERNANCE LIFECYCLE）" : "02 / GOVERNANCE LIFECYCLE"}</p><h2>{c.lifecycleTitle}</h2><div className={styles.threeGrid}>{c.lifecycle.map(([phase, title, body], index) => <article key={phase}><span>0{index + 1}</span><h3>{phase} · {title}</h3><p>{body}</p></article>)}</div></div></section>

        <section className={styles.section}><div className={styles.shell}><p className={styles.kicker}>{locale === "zh" ? "03 / 证据生态（EVIDENCE ECOSYSTEM）" : "03 / EVIDENCE ECOSYSTEM"}</p><h2>{c.ecosystemTitle}</h2><p className={styles.lead}>{c.ecosystemBody}</p><div className={styles.ecosystemGrid}>{c.ecosystem.map(([title, body]) => <article key={title}><h3>{title}</h3><p>{body}</p></article>)}</div></div></section>

        <section className={`${styles.section} ${styles.scenarios}`}><div className={styles.shell}><p className={styles.kicker}>{locale === "zh" ? "04 / 广播电视与网络视听（BROADCAST + ONLINE AUDIOVISUAL）" : "04 / BROADCAST + ONLINE AUDIOVISUAL"}</p><div className={styles.twoColumn}><article><h2>{c.broadcastTitle}</h2><p>{c.broadcastBody}</p></article><article><h2>{c.onlineTitle}</h2><p>{c.onlineBody}</p></article></div></div></section>

        <section className={styles.section}><div className={styles.shell}><p className={styles.kicker}>{locale === "zh" ? "05 / 增量接入（INCREMENTAL ADOPTION）" : "05 / INCREMENTAL ADOPTION"}</p><h2>{c.routeTitle}</h2><ol className={styles.route}>{c.route.map((item, index) => <li key={item}><span>{String(index + 1).padStart(2, "0")}</span><strong>{item}</strong></li>)}</ol></div></section>

        <section className={`${styles.section} ${styles.status}`} id="capability-boundaries"><div className={styles.shell}><div className={styles.twoColumn}><div><p className={styles.kicker}>{locale === "zh" ? "06 / 当前状态（CURRENT STATUS）" : "06 / CURRENT STATUS"}</p><h2>{c.statusTitle}</h2><p>{c.statusBody}</p><dl><div><dt>{locale === "zh" ? "版本（VERSION）" : "VERSION"}</dt><dd>v0.1.0</dd></div><div><dt>{locale === "zh" ? "参考提交（REFERENCE COMMIT）" : "REFERENCE COMMIT"}</dt><dd><code>{REFERENCE_COMMIT}</code></dd></div><div><dt>{locale === "zh" ? "数据政策（DATA POLICY）" : "DATA POLICY"}</dt><dd>SYNTHETIC_DATA_ONLY</dd></div></dl></div><article><h3>{c.boundaryTitle}</h3><ul>{c.boundaries.map((item) => <li key={item}>{item}</li>)}</ul></article></div></div></section>

        <section className={styles.cta}><div className={styles.shell}><div><p className={styles.kicker}>{locale === "zh" ? "07 / 参考演示（REFERENCE DEMO）" : "07 / REFERENCE DEMO"}</p><h2>{c.demoTitle}</h2><p>{c.demoBody}</p></div><a className="button button-primary" href={demo}>{c.demoCta}</a></div></section>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
