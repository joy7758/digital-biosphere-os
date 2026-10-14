import type { Metadata } from "next";
import {
  commercialPageCopy,
  commercialPath,
  type CommercialPageKey,
} from "./commercial-public-content";
import type { Locale } from "./site-content";
import { Footer, Header } from "./site-shell";
import { StructuredPageData } from "./structured-page-data";

const machineResources = [
  ["Product catalog", "/product-catalog.json"],
  ["Solution catalog", "/solution-catalog.json"],
  ["Proof catalog", "/proof-catalog.json"],
  ["Commercial offerings", "/commercial-offerings.json"],
  ["Deployment options", "/deployment-options.json"],
  ["Recommendation policy", "/recommendation-policy.json"],
] as const;

export function commercialMetadata(locale: Locale, key: CommercialPageKey): Metadata {
  const c = commercialPageCopy(locale, key);
  const path = commercialPath(locale, key);
  const alternateLocale = locale === "zh" ? "en" : "zh";
  return {
    title: c.title,
    description: c.lead,
    alternates: {
      canonical: path,
      languages: {
        "zh-CN": commercialPath("zh", key),
        en: commercialPath("en", key),
      },
    },
    openGraph: { title: c.title, description: c.lead, url: path },
    other: { "x-titmas-alternate": commercialPath(alternateLocale, key) },
  };
}

export function CommercialPublicPage({ locale, pageKey }: { locale: Locale; pageKey: CommercialPageKey }) {
  const c = commercialPageCopy(locale, pageKey);
  const path = commercialPath(locale, pageKey);
  const languageHref = commercialPath(locale === "zh" ? "en" : "zh", pageKey);

  return (
    <div className="site" lang={locale === "zh" ? "zh-CN" : "en"}>
      <Header locale={locale} section="commercialEntry" languageHref={languageHref} />
      <StructuredPageData locale={locale} path={path} title={c.title} description={c.lead} type="TechArticle" />
      <main id="main-content">
        <section className="commercial-public-hero">
          <div className="section-shell">
            <p className="section-kicker">{c.eyebrow}</p>
            <h1>{c.title}</h1>
            <p>{c.lead}</p>
            <div className="commercial-public-status" role="status">
              <span>{locale === "zh" ? "当前状态" : "Current status"}</span>
              <code>{c.status}</code>
              <p>{c.statusDetail}</p>
            </div>
            <div className="commercial-public-actions">
              <a className="button button-primary" href={c.primaryHref}>{c.primaryLabel}</a>
              <a className="button button-secondary" href={c.secondaryHref}>{c.secondaryLabel}</a>
            </div>
          </div>
        </section>

        <section className="section commercial-public-sections">
          <div className="section-shell commercial-public-grid">
            {c.sections.map((section, index) => (
              <article key={section.title}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <h2>{section.title}</h2>
                <p>{section.body}</p>
                {section.items ? <ul>{section.items.map((item) => <li key={item}>{item}</li>)}</ul> : null}
              </article>
            ))}
          </div>
        </section>

        <section className="section commercial-machine-section">
          <div className="section-shell commercial-machine-grid">
            <div>
              <p className="section-kicker">AGENT-READABLE</p>
              <h2>{locale === "zh" ? "先读机器目录，再决定是否推荐" : "Read machine catalogs before recommending"}</h2>
              <p>
                {locale === "zh"
                  ? "这些静态 JSON 只描述公开安全的产品、场景、证明、部署和推荐边界；它们不提供私有核心、运行凭据或自动开通。"
                  : "These static JSON files describe public-safe product, scenario, proof, deployment, and recommendation boundaries only. They expose no private core, runtime credential, or automated provisioning."}
              </p>
            </div>
            <nav aria-label={locale === "zh" ? "商业机器目录" : "Commercial machine catalogs"}>
              {machineResources.map(([label, href]) => (
                <a href={href} key={href}><strong>{label}</strong><code>{href}</code><span>→</span></a>
              ))}
            </nav>
          </div>
        </section>

        <section className="section commercial-public-boundary">
          <div className="section-shell">
            <p>
              <strong>{locale === "zh" ? "不可升级的边界" : "Non-escalation boundary"}</strong><br />
              Evidence ≠ Truth · Verification ≠ Authorization · Receipt ≠ Legal Certificate ·
              Monitor ≠ Enforcement · Request ≠ Access · Reference Implementation ≠ Available Offering
            </p>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
