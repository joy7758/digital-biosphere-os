import { content, type Locale } from "./site-content";
import {
  formatUpdateDate,
  publishedUpdates,
  updateCategoryLabels,
} from "./update-content";
import { Footer, Header } from "./site-shell";
import { StructuredPageData } from "./structured-page-data";

const copy = {
  zh: {
    eyebrow: "UPDATES / 更新与公告",
    title: "每次变化，都要说明发生了什么",
    lead: "这里按时间记录网站、研究、Demo 与治理信息的真实变化。更新记录不自动产生产品、发布、权力或生产状态。",
    home: "TITMAS 首页",
    current: "更新",
    latest: "最新更新",
    open: "阅读更新",
    machine: "机器可读更新流",
    constitutionTitle: "网站更新宪法",
    constitutionBody: "以后遇到网站结构、公告、成熟度或版本表达的抉择，默认先核对 OpenAI 与 OpenTelemetry 官方模式，同时保留 TITMAS 自身事实与治理边界。",
    constitutionCta: "查看决策基准",
  },
  en: {
    eyebrow: "UPDATES & ANNOUNCEMENTS",
    title: "Every change should explain what changed",
    lead: "A chronological record of real changes to the site, research, demos, and governance information. An update record creates no product, release, authority, or production status.",
    home: "TITMAS home",
    current: "Updates",
    latest: "Latest updates",
    open: "Read update",
    machine: "Machine-readable updates",
    constitutionTitle: "Website Update Constitution",
    constitutionBody: "When website structure, announcements, maturity, or version language requires a choice, check official OpenAI and OpenTelemetry patterns first while preserving TITMAS truth and governance boundaries.",
    constitutionCta: "Review the decision baseline",
  },
} as const;

export function UpdatesPage({ locale }: { locale: Locale }) {
  const c = content[locale];
  const t = copy[locale];
  const root = locale === "zh" ? "/" : "/en/";
  const constitution = locale === "zh" ? "/updates/constitution/" : "/en/updates/constitution/";

  return (
    <div className="site updates-page" lang={c.lang}>
      <Header locale={locale} section="updates" />
      <StructuredPageData
        locale={locale}
        path={locale === "zh" ? "/updates/" : "/en/updates/"}
        title={t.title}
        description={t.lead}
        type="CollectionPage"
      />
      <main id="main-content">
        <section className="updates-hero">
          <div className="section-shell">
            <nav className="breadcrumb" aria-label={locale === "zh" ? "面包屑导航" : "Breadcrumb"}>
              <a href={root}>{t.home}</a><span>/</span><span aria-current="page">{t.current}</span>
            </nav>
            <p className="section-kicker">{t.eyebrow}</p>
            <h1>{t.title}</h1>
            <p>{t.lead}</p>
            <div className="updates-machine-links">
              <a href="/updates.json">{t.machine} ↗</a>
              <a href="/WEBSITE-UPDATE-CONSTITUTION-v0.1.json">Constitution JSON ↗</a>
            </div>
          </div>
        </section>

        <section className="section updates-index">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">CHRONOLOGICAL INDEX</p>
              <h2>{t.latest}</h2>
            </div>
            <div className="updates-list">
              {publishedUpdates.map((item) => (
                <a href={item.href[locale]} key={item.slug}>
                  <time dateTime={item.effective_date}>{formatUpdateDate(locale, item.effective_date)}</time>
                  <div>
                    <div className="update-meta">
                      <span>{updateCategoryLabels[item.category][locale]}</span>
                      <code>{item.category}</code>
                    </div>
                    <h3>{item.title[locale]}</h3>
                    <p>{item.summary[locale]}</p>
                  </div>
                  <strong>{t.open} ↗</strong>
                </a>
              ))}
            </div>
          </div>
        </section>

        <section className="section update-constitution-entry">
          <div className="section-shell update-constitution-card">
            <div>
              <p className="section-kicker">DECISION BASELINE</p>
              <h2>{t.constitutionTitle}</h2>
              <p>{t.constitutionBody}</p>
            </div>
            <a className="button button-secondary" href={constitution}>{t.constitutionCta}</a>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
