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
    back: "全部更新",
    changes: "本次变化",
    boundaries: "事实边界",
    provenance: "来源与生效信息",
    effective: "生效日期",
    source: "来源 commit",
    status: "状态",
  },
  en: {
    back: "All updates",
    changes: "What changed",
    boundaries: "Truth boundaries",
    provenance: "Source and effective information",
    effective: "Effective date",
    source: "Source commit",
    status: "Status",
  },
} as const;

export function UpdateDetailPage({ locale, slug }: { locale: Locale; slug: string }) {
  const c = content[locale];
  const t = copy[locale];
  const item = publishedUpdates.find((candidate) => candidate.slug === slug);
  if (!item) return null;
  const updates = locale === "zh" ? "/updates/" : "/en/updates/";

  return (
    <div className="site update-detail-page" lang={c.lang}>
      <Header locale={locale} section="updates" />
      <StructuredPageData
        locale={locale}
        path={item.href[locale]}
        title={item.title[locale]}
        description={item.summary[locale]}
        type="Article"
        datePublished={item.effective_date}
        dateModified={item.effective_date}
      />
      <main id="main-content">
        <article>
          <header className="update-detail-hero">
            <div className="section-shell">
              <a className="update-back" href={updates}>← {t.back}</a>
              <div className="update-meta">
                <span>{updateCategoryLabels[item.category][locale]}</span>
                <code>{item.category}</code>
              </div>
              <h1>{item.title[locale]}</h1>
              <p>{item.summary[locale]}</p>
              <time dateTime={item.effective_date}>{formatUpdateDate(locale, item.effective_date)}</time>
            </div>
          </header>

          <section className="section update-detail-body">
            <div className="section-shell update-detail-grid">
              <div>
                <p className="section-kicker">CHANGESET</p>
                <h2>{t.changes}</h2>
                <ul>{item.changes[locale].map((change) => <li key={change}>{change}</li>)}</ul>
              </div>
              <aside>
                <p className="section-kicker">PROVENANCE</p>
                <h2>{t.provenance}</h2>
                <dl>
                  <div><dt>{t.effective}</dt><dd>{formatUpdateDate(locale, item.effective_date)}</dd></div>
                  <div><dt>{t.source}</dt><dd><code>{item.source_commit}</code></dd></div>
                  <div><dt>{t.status}</dt><dd><code>{item.status}</code></dd></div>
                </dl>
              </aside>
            </div>
          </section>

          <section className="section update-boundaries">
            <div className="section-shell">
              <div className="section-heading">
                <p className="section-kicker">TRUTH BOUNDARIES</p>
                <h2>{t.boundaries}</h2>
              </div>
              <div className="update-boundary-grid">
                {item.truth_boundaries.map((boundary) => (
                  <article key={boundary.scope}>
                    <code>{boundary.scope}</code>
                    <p>{boundary.limitation}</p>
                  </article>
                ))}
              </div>
            </div>
          </section>
        </article>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
