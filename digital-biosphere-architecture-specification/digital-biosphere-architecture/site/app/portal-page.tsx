import { HeroCarousel } from "./components/hero-carousel";
import { content, type Locale } from "./site-content";
import { Footer, Header } from "./site-shell";
import { serializeJsonLd } from "./json-ld";

export function PortalPage({ locale }: { locale: Locale }) {
  const c = content[locale];
  const local = (path: string) => locale === "zh" ? path : `/en${path}`;

  const products = [
    ["TITMAS Gate", locale === "zh" ? "行动闸门" : "Action gate", local("/products/gate/"), "MONITOR_FIRST"],
    ["TITMAS Receipt", locale === "zh" ? "可验证执行回执" : "Verifiable execution receipt", local("/products/receipt/"), "PORTABLE_PROOF"],
    ["TITMAS Audit", locale === "zh" ? "证据审计" : "Evidence audit", local("/products/audit/"), "REVIEW_AND_REPLAY"],
    ["TITMAS Health", locale === "zh" ? "智能体健康快照" : "Agent health snapshot", local("/products/health/"), "LOW_FRICTION_ENTRY"],
  ] as const;

  const humanEntries = [
    [locale === "zh" ? "私有评估" : "Private evaluation", locale === "zh" ? "零客户数据的合成第一价值" : "Synthetic first value with zero customer data", local("/private-evaluation/")],
    ["Monitor Pilot", locale === "zh" ? "只观察，不阻断" : "Observe without blocking", local("/monitor-pilot/")],
    [locale === "zh" ? "设计伙伴" : "Design partner", locale === "zh" ? "人工、逐范围审查" : "Human-reviewed and scope-bounded", local("/design-partner/")],
    ["Trust Center", locale === "zh" ? "证据、验证与非声明" : "Evidence, verification, and non-claims", local("/trust-center/")],
  ] as const;

  const machineEntries = [
    ["product-catalog.json", locale === "zh" ? "四产品与当前可用性" : "Four products and availability", "/product-catalog.json"],
    ["solution-catalog.json", locale === "zh" ? "软件交付与行业边界" : "Software delivery and industry boundaries", "/solution-catalog.json"],
    ["proof-catalog.json", locale === "zh" ? "合成证明、来源与限制" : "Synthetic proof, provenance, and limits", "/proof-catalog.json"],
    ["recommendation-policy.json", locale === "zh" ? "何时推荐与何时放弃" : "When to recommend or abstain", "/recommendation-policy.json"],
    ["commercial-offerings.json", locale === "zh" ? "Offering 状态与非声明" : "Offering status and non-claims", "/commercial-offerings.json"],
    ["deployment-options.json", locale === "zh" ? "部署候选与授权状态" : "Deployment candidates and authority", "/deployment-options.json"],
  ] as const;

  const structuredData = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "@id": "https://redcrag.cn/#organization",
        name: "山西游骑兵电子商务有限公司",
        legalName: "山西游骑兵电子商务有限公司",
        alternateName: ["夏日之海", "titmas", "TITMAS"],
        url: "https://redcrag.cn/",
        logo: "https://redcrag.cn/titmas-logo.png",
      },
      {
        "@type": "WebSite",
        "@id": "https://redcrag.cn/#website",
        name: locale === "zh" ? "夏日之海 · TITMAS" : "titmas · TITMAS",
        url: "https://redcrag.cn/",
        inLanguage: ["zh-CN", "en"],
        description: locale === "zh"
          ? "TITMAS 智能体行动控制与可验证执行平台。"
          : "TITMAS Agent Action Control and Verifiable Accountability Platform.",
        image: "https://redcrag.cn/titmas-logo.png",
        publisher: { "@id": "https://redcrag.cn/#organization" },
        hasPart: [
          ...humanEntries.map(([name, , href]) => ({ "@type": "WebPage", name, url: `https://redcrag.cn${href}` })),
          ...machineEntries.map(([name, , href]) => ({ "@type": "DigitalDocument", name, url: `https://redcrag.cn${href}` })),
        ],
      },
    ],
  };

  return (
    <div className="site" lang={c.lang}>
      <Header locale={locale} />
      <main id="main-content">
        <HeroCarousel locale={locale} />

        <section className="section home-overview" id="about" data-section-id="platform-and-products">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">{locale === "zh" ? "一个私有平台，四个对外产品" : "ONE PRIVATE PLATFORM, FOUR PUBLIC PRODUCTS"}</p>
              <h2>{locale === "zh" ? "关键行动控制与可验证追责，共用同一套私有核心" : "Critical-action control and verifiable accountability on one private core"}</h2>
              <p>{locale === "zh" ? "公开入口负责发现、理解和独立检查；私有核心保持闭源。产品页描述边界和试点候选，不代表服务已经开放。" : "Public surfaces support discovery, understanding, and independent inspection while the core remains closed. Product pages describe boundaries and pilot candidates, not generally available services."}</p>
            </div>
            <div className="home-product-grid">
              {products.map(([name, role, href, tag], index) => (
                <a href={href} key={name}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <code>{tag}</code>
                  <h3>{name}</h3>
                  <p>{role}</p>
                  <b>→</b>
                </a>
              ))}
            </div>
          </div>
        </section>

        <section className="section home-showcase" data-section-id="monitor-first-path">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">MONITOR BEFORE ENFORCE</p>
              <h2>{locale === "zh" ? "从低风险评估进入客户特定控制" : "Move from low-risk evaluation to customer-specific control"}</h2>
              <p>{locale === "zh" ? "当前只证明合成参考路径；任何付费、Credential、部署或 Enforce 都必须经过独立 Human Decision。" : "Only synthetic reference paths are currently evidenced. Payment, credentials, deployment, and Enforce each require a separate Human Decision."}</p>
            </div>
            <ol className="commercial-path">
              {[
                ["01", "Health Snapshot", locale === "zh" ? "识别接入缺口" : "Identify onboarding gaps", local("/products/health/")],
                ["02", "Monitor Pilot", locale === "zh" ? "产生 Shadow Decision，不阻断" : "Create Shadow Decisions without blocking", local("/monitor-pilot/")],
                ["03", "Enforce Pilot", locale === "zh" ? "仅客户特定授权后评估" : "Evaluate only after customer-specific authorization", local("/enforce-pilot/")],
                ["04", locale === "zh" ? "企业私有部署" : "Enterprise private deployment", locale === "zh" ? "未来合同与部署闸门" : "Future contract and deployment gate", local("/request-access/")],
              ].map(([index, title, body, href]) => (
                <li key={index}><span>{index}</span><h3>{title}</h3><p>{body}</p><a href={href}>→</a></li>
              ))}
            </ol>
          </div>
        </section>

        <section className="section home-developer" id="agent-start" data-section-id="human-and-agent-entry">
          <div className="section-shell home-developer-grid">
            <div>
              <p className="section-kicker">{locale === "zh" ? "人类与智能体双入口" : "HUMAN AND AGENT ENTRY"}</p>
              <h2>{locale === "zh" ? "人类审查商业范围，智能体读取精确机器契约" : "Humans review commercial scope; agents read precise machine contracts"}</h2>
              <p>{locale === "zh" ? "入口不会自动创建客户、Workspace、Key、Permission、合同或生产部署。" : "No entry automatically creates a customer, workspace, key, permission, contract, or production deployment."}</p>
              <div className="home-entry-list">
                {humanEntries.map(([title, description, href]) => <a href={href} key={href}><strong>{title}</strong><span>{description}</span><i>→</i></a>)}
              </div>
            </div>
            <aside className="home-machine-entry">
              <div><span>{locale === "zh" ? "机器商业目录" : "Machine commercial catalogs"}</span><code>STATIC · PUBLIC-SAFE</code></div>
              {machineEntries.map(([title, description, href]) => <a href={href} key={href}><strong>{title}</strong><small>{description}</small></a>)}
            </aside>
          </div>
        </section>

        <section className="section home-status" id="status" data-section-id="current-commercial-boundary">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">{locale === "zh" ? "当前商业事实" : "CURRENT COMMERCIAL TRUTH"}</p>
              <h2>{locale === "zh" ? "参考实现已形成，可用 Offering 尚未成立" : "Reference implementation exists; no available offering is established"}</h2>
            </div>
            <div className="home-status-grid">
              <article><span>PRIVATE CORE</span><strong>CLOSED</strong><p>{locale === "zh" ? "公开接口不等于私有实现。" : "Public interface is not private implementation."}</p></article>
              <article><span>MONITOR</span><strong>REFERENCE IMPLEMENTED</strong><p>{locale === "zh" ? "合成、未部署、不会阻断。" : "Synthetic, not deployed, and non-blocking."}</p></article>
              <article><span>AVAILABLE OFFERINGS</span><strong>0</strong><p>{locale === "zh" ? "没有自动销售、支付或 Key。" : "No automated sales, payment, or keys."}</p></article>
              <article><span>PRODUCTION READY</span><strong>false</strong><p>{locale === "zh" ? "没有客户采用、认证或法律通过声明。" : "No customer adoption, certification, or legal-pass claim."}</p></article>
            </div>
            <div className="home-boundary-row">
              <p><code>Evidence ≠ Truth · Verification ≠ Authorization · Request ≠ Access</code><br />{locale === "zh" ? "所有结果保持来源、范围、失败与限制。" : "Every result retains provenance, scope, failure, and limits."}</p>
              <nav><a href={local("/status/")}>{locale === "zh" ? "完整状态" : "Full status"}<span>→</span></a><a href={local("/request-access/")}>{locale === "zh" ? "申请边界" : "Request boundary"}<span>→</span></a></nav>
            </div>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: serializeJsonLd(structuredData) }} />
    </div>
  );
}
