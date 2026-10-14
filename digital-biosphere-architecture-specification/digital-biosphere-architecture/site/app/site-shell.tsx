import type { Locale } from "./site-content";
import { content } from "./site-content";

export function Brand({ locale }: { locale: Locale }) {
  const brandName = locale === "zh" ? "夏日之海" : "titmas";
  const brandDescriptor = locale === "zh" ? "可信多智能体基础设施" : "Trusted Multi-Agent Infrastructure";

  return (
    <span className="brand" aria-label={`${brandName} · ${brandDescriptor}`}>
      <span className="brand-mark" aria-hidden="true">
        {/* Static export uses the authorized public brand asset without an image-optimization runtime. */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/titmas-logo.png" alt="" width="1024" height="1024" />
      </span>
      <span className="brand-name">
        <strong>{brandName}</strong>
        <small>{brandDescriptor}</small>
      </span>
    </span>
  );
}

type SiteSection =
  | "home"
  | "research"
  | "researchIndex"
  | "applications"
  | "demos"
  | "industries"
  | "medicalIndustry"
  | "mediaIndustry"
  | "spaceIndustry"
  | "medical"
  | "mediaDemo"
  | "demo"
  | "updates"
  | "constitution"
  | "status"
  | "community"
  | "commercial"
  | "commercialEntry"
  | "productsCollection"
  | "solutionsCollection"
  | "proofCollection";

export function Header({ locale, section = "home", languageHref }: { locale: Locale; section?: SiteSection; languageHref?: string }) {
  const c = content[locale];
  const root = locale === "zh" ? "/" : "/en/";
  const research = locale === "zh" ? "/research/" : "/en/research/";
  const products = locale === "zh" ? "/products/" : "/en/products/";
  const solutions = locale === "zh" ? "/solutions/" : "/en/solutions/";
  const proof = locale === "zh" ? "/proof/" : "/en/proof/";
  const designPartner = locale === "zh" ? "/design-partner/" : "/en/design-partner/";
  const requestAccess = locale === "zh" ? "/request-access/" : "/en/request-access/";
  const languageRoutes: Record<SiteSection, [string, string]> = {
    home: ["/en/", "/"],
    research: ["/en/research/", "/research/"],
    researchIndex: ["/en/research/index/", "/research/index/"],
    applications: ["/en/applications/", "/applications/"],
    demos: ["/en/demos/", "/demos/"],
    industries: ["/en/industries/", "/industries/"],
    medicalIndustry: ["/en/industry/medical-evidence/", "/industry/medical-evidence/"],
    mediaIndustry: ["/en/industry/media-evidence/", "/industry/media-evidence/"],
    spaceIndustry: ["/en/industry/space-agent-evidence/", "/industry/space-agent-evidence/"],
    medical: ["/en/demo/medical-evidence/", "/demo/medical-evidence/"],
    mediaDemo: ["/en/demo/media-evidence/", "/demo/media-evidence/"],
    demo: ["/en/digital-cell/", "/digital-cell/"],
    updates: ["/en/updates/", "/updates/"],
    constitution: ["/en/updates/constitution/", "/updates/constitution/"],
    status: ["/en/status/", "/status/"],
    community: ["/en/community/", "/community/"],
    commercial: ["/en/commercial-evaluation/", "/commercial-evaluation/"],
    commercialEntry: ["/en/products/gate/", "/products/gate/"],
    productsCollection: ["/en/products/", "/products/"],
    solutionsCollection: ["/en/solutions/", "/solutions/"],
    proofCollection: ["/en/proof/", "/proof/"],
  };
  const language = languageHref ?? (locale === "zh" ? languageRoutes[section][0] : languageRoutes[section][1]);

  const nav = (
    <>
      <a href={products} aria-current={section === "commercialEntry" || section === "productsCollection" ? "page" : undefined}>{locale === "zh" ? "产品" : "Products"}</a>
      <a href={solutions} aria-current={section === "solutionsCollection" ? "page" : undefined}>{locale === "zh" ? "解决方案" : "Solutions"}</a>
      <a href={proof} aria-current={section === "commercial" || section === "proofCollection" ? "page" : undefined}>{locale === "zh" ? "效果证明" : "Proof"}</a>
      <a href={designPartner}>{locale === "zh" ? "设计伙伴" : "Design partners"}</a>
      <a href={research} aria-current={section === "research" || section === "researchIndex" ? "page" : undefined}>{locale === "zh" ? "研究" : "Research"}</a>
      <a href={requestAccess}>{locale === "zh" ? "申请访问" : "Request access"}</a>
      <a className="language-link" href={language} hrefLang={locale === "zh" ? "en" : "zh-CN"}>
        {c.nav.language}
      </a>
    </>
  );

  return (
    <>
      <a className="skip-link" href="#main-content">
        {locale === "zh" ? "跳到主要内容" : "Skip to main content"}
      </a>
      <header className="site-header">
        <div className="nav-shell">
          <a className="brand-link" href={root}>
            <Brand locale={locale} />
          </a>
          <nav className="desktop-nav" aria-label={locale === "zh" ? "主导航" : "Primary navigation"}>
            {nav}
          </nav>
          <details className="mobile-nav">
            <summary aria-label={locale === "zh" ? "打开导航" : "Open navigation"}>
              <span />
              <span />
              <span />
            </summary>
            <nav aria-label={locale === "zh" ? "移动导航" : "Mobile navigation"}>{nav}</nav>
          </details>
        </div>
      </header>
    </>
  );
}

export function Footer({ locale }: { locale: Locale }) {
  const c = content[locale];
  return (
    <footer className="site-footer">
      <div className="footer-grid">
        <div>
          <Brand locale={locale} />
          <p>{c.footer}</p>
        </div>
        <div>
          <strong>{locale === "zh" ? "产品与试点" : "Products and pilots"}</strong>
          <a href={locale === "zh" ? "/products/gate/" : "/en/products/gate/"}>TITMAS Gate</a>
          <a href={locale === "zh" ? "/products/receipt/" : "/en/products/receipt/"}>TITMAS Receipt</a>
          <a href={locale === "zh" ? "/products/audit/" : "/en/products/audit/"}>TITMAS Audit</a>
          <a href={locale === "zh" ? "/products/health/" : "/en/products/health/"}>TITMAS Health</a>
          <a href={locale === "zh" ? "/monitor-pilot/" : "/en/monitor-pilot/"}>Monitor Pilot</a>
        </div>
        <div>
          <strong>{locale === "zh" ? "机器可读" : "Machine-readable"}</strong>
          <a href="/llms.txt">llms.txt</a>
          <a href="/agent-index.json">agent-index.json</a>
          <a href="/product-catalog.json">product-catalog.json</a>
          <a href="/solution-catalog.json">solution-catalog.json</a>
          <a href="/proof-catalog.json">proof-catalog.json</a>
          <a href="/recommendation-policy.json">recommendation-policy.json</a>
          <a href="/status.json">status.json</a>
        </div>
        <div>
          <strong>{locale === "zh" ? "信任与公司" : "Trust and company"}</strong>
          <a href={locale === "zh" ? "/security/" : "/en/security/"}>{locale === "zh" ? "安全" : "Security"}</a>
          <a href={locale === "zh" ? "/trust-center/" : "/en/trust-center/"}>Trust Center</a>
          <a href={locale === "zh" ? "/status/" : "/en/status/"}>{locale === "zh" ? "当前状态" : "Current status"}</a>
          <a href={locale === "zh" ? "/privacy/" : "/en/privacy/"}>{locale === "zh" ? "隐私" : "Privacy"}</a>
          <a href={locale === "zh" ? "/terms/" : "/en/terms/"}>{locale === "zh" ? "条款边界" : "Terms boundary"}</a>
          <a href={locale === "zh" ? "/community/" : "/en/community/"}>{locale === "zh" ? "历史社区资料" : "Historical community material"}</a>
          <a href="https://github.com/joy7758">{locale === "zh" ? "公开 GitHub Profile" : "Public GitHub profile"}</a>
        </div>
      </div>
      <div className="footer-legal">
        <span>© 2026 山西游骑兵电子商务有限公司</span>
        <span>{c.legal}</span>
      </div>
      <div className="footer-filing">
        <span>{locale === "zh" ? "网站运营主体" : "Website operator"}：山西游骑兵电子商务有限公司</span>
        <strong>晋ICP备2026006409号-1</strong>
        <a href="https://beian.miit.gov.cn" target="_blank" rel="noreferrer">
          工业和信息化部备案管理系统
        </a>
      </div>
    </footer>
  );
}
