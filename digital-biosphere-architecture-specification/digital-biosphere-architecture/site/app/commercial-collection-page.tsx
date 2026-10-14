import type { Metadata } from "next";
import productCatalog from "../public/product-catalog.json";
import proofCatalog from "../public/proof-catalog.json";
import solutionCatalog from "../public/solution-catalog.json";
import type { Locale } from "./site-content";
import { Footer, Header } from "./site-shell";
import { StructuredPageData } from "./structured-page-data";

export type CommercialCollectionKey = "platform" | "products" | "solutions" | "proof";

type CollectionItem = {
  id: string;
  name: string;
  role: string;
  status: string;
  href: string;
};

const collectionCopy = {
  zh: {
    platform: {
      eyebrow: "PLATFORM / 平台",
      title: "一个私有平台，四个公开产品入口",
      lead: "TITMAS 将行动闸门、可验证执行回执、证据审计和智能体健康快照组合为同一商业基础设施候选。公开页面只提供发现、理解和合成证明。",
      marker: "TITMAS_PLATFORM_COLLECTION",
    },
    products: {
      eyebrow: "PRODUCTS / 产品",
      title: "四个边界明确的产品入口",
      lead: "从低摩擦 Health Snapshot 开始，经 Monitor 理解价值；任何 Enforce、Credential、合同或部署仍需独立人类决策。",
      marker: "TITMAS_PRODUCTS_COLLECTION",
    },
    solutions: {
      eyebrow: "SOLUTIONS / 解决方案",
      title: "从关键行动控制开始验证",
      lead: "首个候选场景聚焦软件交付行动控制；行业方向只复用可信基础设施，不扩张为新的行业平台。",
      marker: "TITMAS_SOLUTIONS_COLLECTION",
    },
    proof: {
      eyebrow: "PROOF / 效果证明",
      title: "检查合成证明，也检查它不能证明什么",
      lead: "公开 Proof 保留来源、版本、结果和限制。合成测试通过不等于客户采用、生产就绪、认证或结果正确。",
      marker: "TITMAS_PROOF_COLLECTION",
    },
  },
  en: {
    platform: {
      eyebrow: "PLATFORM",
      title: "One private platform, four public product entries",
      lead: "TITMAS composes an action gate, verifiable execution receipts, evidence audit, and agent health snapshots. Public pages provide discovery, understanding, and bounded synthetic proof only.",
      marker: "TITMAS_PLATFORM_COLLECTION",
    },
    products: {
      eyebrow: "PRODUCTS",
      title: "Four products with explicit boundaries",
      lead: "Start with a low-friction Health Snapshot and understand value in Monitor. Enforce, credentials, contracts, and deployment each require a separate Human Decision.",
      marker: "TITMAS_PRODUCTS_COLLECTION",
    },
    solutions: {
      eyebrow: "SOLUTIONS",
      title: "Validate critical-action control first",
      lead: "The first candidate scenario focuses on software-delivery action control. Industry directions reuse trust infrastructure without becoming new industry platforms.",
      marker: "TITMAS_SOLUTIONS_COLLECTION",
    },
    proof: {
      eyebrow: "PROOF",
      title: "Inspect synthetic proof and what it cannot establish",
      lead: "Public Proof retains provenance, version, result, and limitations. A passing synthetic test is not customer adoption, production readiness, certification, or result correctness.",
      marker: "TITMAS_PROOF_COLLECTION",
    },
  },
} as const;

function productItems(locale: Locale): CollectionItem[] {
  return productCatalog.products.map((product) => ({
    id: product.product_id,
    name: locale === "zh" ? product.name_zh : product.name,
    role: product.role,
    status: product.current_status,
    href: locale === "zh" ? product.human_entry : product.human_entry_en,
  }));
}

function solutionItems(locale: Locale): CollectionItem[] {
  return solutionCatalog.solutions.map((solution) => ({
    id: solution.solution_id,
    name: locale === "zh" ? solution.name_zh : solution.name,
    role: solution.priority,
    status: "monitor_status" in solution ? solution.monitor_status : solution.current_status,
    href: locale === "zh" ? solution.entry : solution.entry_en,
  }));
}

function proofItems(locale: Locale): CollectionItem[] {
  return proofCatalog.proofs.map((proof) => ({
    id: proof.proof_id,
    name: proof.proof_id.replaceAll("_", " "),
    role: proof.proof_type,
    status: proof.result,
    href: locale === "zh" ? proof.public_detail : `/en${proof.public_detail}`,
  }));
}

function itemsFor(locale: Locale, collection: CommercialCollectionKey): CollectionItem[] {
  if (collection === "solutions") return solutionItems(locale);
  if (collection === "proof") return proofItems(locale);
  return productItems(locale);
}

const machineCatalog: Record<CommercialCollectionKey, string> = {
  platform: "/product-catalog.json",
  products: "/product-catalog.json",
  solutions: "/solution-catalog.json",
  proof: "/proof-catalog.json",
};

export function commercialCollectionPath(locale: Locale, collection: CommercialCollectionKey) {
  const base = `/${collection}/`;
  return locale === "zh" ? base : `/en${base}`;
}

export function commercialCollectionMetadata(locale: Locale, collection: CommercialCollectionKey): Metadata {
  const copy = collectionCopy[locale][collection];
  return {
    title: copy.title,
    description: copy.lead,
    alternates: {
      canonical: commercialCollectionPath(locale, collection),
      languages: {
        "zh-CN": commercialCollectionPath("zh", collection),
        en: commercialCollectionPath("en", collection),
      },
    },
  };
}

export function CommercialCollectionPage({
  locale,
  collection,
}: {
  locale: Locale;
  collection: CommercialCollectionKey;
}) {
  const copy = collectionCopy[locale][collection];
  const items = itemsFor(locale, collection);
  const path = commercialCollectionPath(locale, collection);
  const languageHref = commercialCollectionPath(locale === "zh" ? "en" : "zh", collection);
  const section = collection === "proof" ? "proofCollection" : collection === "solutions" ? "solutionsCollection" : "productsCollection";

  return (
    <div className="site" lang={locale === "zh" ? "zh-CN" : "en"}>
      <Header locale={locale} section={section} languageHref={languageHref} />
      <StructuredPageData locale={locale} path={path} title={copy.title} description={copy.lead} type="CollectionPage" />
      <main id="main-content">
        <section className="commercial-public-hero">
          <div className="section-shell">
            <p className="section-kicker">{copy.eyebrow}</p>
            <h1>{copy.title}</h1>
            <p>{copy.lead}</p>
            <div className="commercial-public-status" role="status">
              <span>{locale === "zh" ? "机器集合标识" : "Machine collection marker"}</span>
              <code>{copy.marker}</code>
              <p>AVAILABLE_OFFERINGS=0 · PRODUCTION_READY=false</p>
            </div>
            <div className="commercial-public-actions">
              <a className="button button-primary" href={machineCatalog[collection]}>
                {locale === "zh" ? "读取机器目录" : "Read machine catalog"}
              </a>
              <a className="button button-secondary" href={locale === "zh" ? "/request-access/" : "/en/request-access/"}>
                {locale === "zh" ? "查看申请边界" : "Read request boundaries"}
              </a>
            </div>
          </div>
        </section>

        <section className="section commercial-public-sections">
          <div className="section-shell commercial-public-grid">
            {items.map((item, index) => (
              <article key={item.id}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <h2>{item.name}</h2>
                <p><code>{item.role}</code></p>
                <p>{item.status}</p>
                <a href={item.href}>{locale === "zh" ? "查看明确边界" : "Inspect explicit boundaries"} →</a>
              </article>
            ))}
          </div>
        </section>

        <section className="section commercial-public-boundary">
          <div className="section-shell">
            <p>
              <strong>{locale === "zh" ? "不可升级的边界" : "Non-escalation boundary"}</strong><br />
              Catalog ≠ Available Offering · Proof ≠ Adoption · Receipt ≠ Truth ·
              Verification ≠ Authorization · Request ≠ Access · Reference ≠ Production
            </p>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
