import { content, type Locale } from "./site-content";
import { directoryItems, type PublicDirectory } from "./site-directory";
import { Footer, Header } from "./site-shell";
import { StructuredPageData } from "./structured-page-data";

const copy = {
  zh: {
    research: {
      eyebrow: "RESEARCH / 研究",
      title: "从研究框架到可验证基础设施",
      lead: "研究解释为什么这个方向重要、哪些边界必须长期保留，以及架构如何演进；它不把研究方向包装成已经交付的产品。",
      current: "研究",
      indexLabel: "研究索引",
    },
    applications: {
      eyebrow: "APPLICATIONS / 行业应用",
      title: "可信基础设施如何进入行业",
      lead: "行业应用说明 TITMAS 解决哪些问题、由谁实现业务逻辑，以及基础设施与行业软件之间的边界。",
      current: "行业应用",
      indexLabel: "已发布应用方向",
    },
    demos: {
      eyebrow: "DEMOS / 参考演示",
      title: "用可检查的演示理解基础设施",
      lead: "Demo 展示可运行或可交互的参考路径，并显式标注数据、验证、生产与权力边界。",
      current: "Demo",
      indexLabel: "已发布 Demo",
    },
    home: "TITMAS 首页",
    overview: "Overview",
    index: "Index",
    open: "打开",
    machine: "机器目录",
    researchPillars: [
      ["01", "Research Foundation", "Digital Biosphere 提供长期问题框架。"],
      ["02", "Evidence Governance", "证据记录与权力、真相和决策保持分离。"],
      ["03", "Industry Translation", "行业方向验证基础设施是否可被复用，而不是宣布产品成熟。"],
    ],
    evidenceTitle: "证据治理是跨行业的共同研究主线",
    evidenceBody: "医疗证据、工业执行证据与智能体行为证据可以使用不同领域规则，但都需要来源、过程、完整性、验证与边界。TITMAS 研究的是这些共同结构。",
    evidenceRules: ["Evidence ≠ Truth", "Evaluation ≠ Authority", "Recommendation ≠ Decision", "Decision ≠ Execution"],
  },
  en: {
    research: {
      eyebrow: "RESEARCH",
      title: "From research frames to verifiable infrastructure",
      lead: "Research explains why the direction matters, which boundaries must persist, and how the architecture can evolve. It does not present a research direction as a delivered product.",
      current: "Research",
      indexLabel: "Research index",
    },
    applications: {
      eyebrow: "APPLICATIONS",
      title: "How trust infrastructure enters industries",
      lead: "Applications explain the problem, who owns the business logic, and the boundary between infrastructure and industry software.",
      current: "Applications",
      indexLabel: "Published application directions",
    },
    demos: {
      eyebrow: "DEMOS",
      title: "Understand the infrastructure through inspectable demos",
      lead: "Demos expose runnable or interactive reference paths with explicit data, validation, production, and authority boundaries.",
      current: "Demos",
      indexLabel: "Published demos",
    },
    home: "TITMAS home",
    overview: "Overview",
    index: "Index",
    open: "Open",
    machine: "Machine catalog",
    researchPillars: [
      ["01", "Research Foundation", "Digital Biosphere provides the long-term problem frame."],
      ["02", "Evidence Governance", "Evidence remains separate from authority, truth, and decisions."],
      ["03", "Industry Translation", "Industry directions test reuse without claiming product maturity."],
    ],
    evidenceTitle: "Evidence governance is the shared cross-industry research track",
    evidenceBody: "Medical evidence, industrial execution evidence, and agent-behavior evidence use different domain rules, but all need provenance, process, integrity, verification, and explicit boundaries. TITMAS researches those shared structures.",
    evidenceRules: ["Evidence ≠ Truth", "Evaluation ≠ Authority", "Recommendation ≠ Decision", "Decision ≠ Execution"],
  },
} as const;

function sectionName(section: PublicDirectory) {
  return section === "research" ? "research" : section;
}

export function DirectoryPage({
  locale,
  section,
  indexOnly = false,
}: {
  locale: Locale;
  section: PublicDirectory;
  indexOnly?: boolean;
}) {
  const c = content[locale];
  const t = copy[locale];
  const sectionCopy = t[section];
  const root = locale === "zh" ? "/" : "/en/";
  const overview = locale === "zh" ? `/${section}/` : `/en/${section}/`;
  const index = section === "research"
    ? (locale === "zh" ? "/research/index/" : "/en/research/index/")
    : `${overview}#index`;
  const pagePath = indexOnly ? index : overview;
  const pageTitle = indexOnly ? sectionCopy.indexLabel : sectionCopy.title;

  return (
    <div className="site directory-page" lang={c.lang}>
      <Header locale={locale} section={section === "research" && indexOnly ? "researchIndex" : sectionName(section)} />
      <StructuredPageData
        locale={locale}
        path={pagePath}
        title={pageTitle}
        description={sectionCopy.lead}
        type="CollectionPage"
      />
      <main id="main-content">
        <section className="directory-hero">
          <div className="section-shell">
            <nav className="breadcrumb" aria-label={locale === "zh" ? "面包屑导航" : "Breadcrumb"}>
              <a href={root}>{t.home}</a><span>/</span><span aria-current="page">{sectionCopy.current}</span>
            </nav>
            <p className="section-kicker">{sectionCopy.eyebrow}</p>
            <h1>{indexOnly ? sectionCopy.indexLabel : sectionCopy.title}</h1>
            <p>{sectionCopy.lead}</p>
            <nav className="directory-tabs" aria-label={locale === "zh" ? "页面分区" : "Page sections"}>
              <a href={overview} aria-current={!indexOnly ? "page" : undefined}>{t.overview}</a>
              <a href={index} aria-current={indexOnly ? "page" : undefined}>{t.index}</a>
              <a href="/site-catalog.json">{t.machine}</a>
            </nav>
          </div>
        </section>

        {section === "research" && !indexOnly && (
          <>
            <section className="section directory-pillars">
              <div className="section-shell">
                <div className="directory-pillar-grid">
                  {t.researchPillars.map(([number, title, description]) => (
                    <article key={number}>
                      <span>{number}</span><h2>{title}</h2><p>{description}</p>
                    </article>
                  ))}
                </div>
              </div>
            </section>
            <section className="section evidence-governance" id="evidence-governance">
              <div className="section-shell evidence-governance-grid">
                <div>
                  <p className="section-kicker">EVIDENCE GOVERNANCE</p>
                  <h2>{t.evidenceTitle}</h2>
                  <p>{t.evidenceBody}</p>
                </div>
                <div className="evidence-rule-list">
                  {t.evidenceRules.map((rule) => <code key={rule}>{rule}</code>)}
                </div>
              </div>
            </section>
          </>
        )}

        <section className="section directory-index" id="index">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">PUBLISHED INDEX</p>
              <h2>{sectionCopy.indexLabel}</h2>
            </div>
            <div className="directory-list">
              {directoryItems[section].map((item, itemIndex) => (
                <a id={item.id} href={item.href[locale]} key={item.id}>
                  <span>{String(itemIndex + 1).padStart(2, "0")}</span>
                  <div>
                    <div className="directory-item-meta">
                      <code>{item.type}</code><b>{item.status}</b>
                    </div>
                    <h3>{item.title[locale]}</h3>
                    <p>{item.description[locale]}</p>
                    <small>{item.metadata.join(" · ")}</small>
                  </div>
                  <strong>{t.open} ↗</strong>
                </a>
              ))}
            </div>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
