import type { Locale } from "./site-content";

export type PublicDirectory = "research" | "applications" | "demos";

type DirectoryItem = {
  id: string;
  type: string;
  status: string;
  title: Record<Locale, string>;
  description: Record<Locale, string>;
  href: Record<Locale, string>;
  metadata: string[];
};

export const directoryItems: Record<PublicDirectory, DirectoryItem[]> = {
  research: [
    {
      id: "digital-biosphere",
      type: "RESEARCH_FOUNDATION",
      status: "PUBLISHED_ARCHITECTURE_BASELINE",
      title: {
        zh: "Digital Biosphere",
        en: "Digital Biosphere",
      },
      description: {
        zh: "把自治数字实体、可信运行基础设施与长期生态治理放在同一研究框架中。",
        en: "A research frame connecting autonomous digital entities, trust infrastructure, and long-term ecosystem governance.",
      },
      href: {
        zh: "/research/index/#digital-biosphere",
        en: "/en/research/index/#digital-biosphere",
      },
      metadata: ["ARCHITECTURE", "LONG_TERM_DIRECTION"],
    },
    {
      id: "evidence-governance",
      type: "RESEARCH_TRACK",
      status: "PUBLISHED_RESEARCH_DIRECTION",
      title: {
        zh: "Evidence Governance",
        en: "Evidence Governance",
      },
      description: {
        zh: "研究 Evidence 如何保留来源、过程、边界与验证记录，同时坚持 Evidence ≠ Truth。",
        en: "Research into provenance, process, boundaries, and verification records while preserving Evidence ≠ Truth.",
      },
      href: {
        zh: "/research/index/#evidence-governance",
        en: "/en/research/index/#evidence-governance",
      },
      metadata: ["EVIDENCE", "AUDITABILITY", "NO_AUTHORITY_EFFECT"],
    },
    {
      id: "titmas-trust-infrastructure",
      type: "INFRASTRUCTURE_RESEARCH",
      status: "DEVELOPER_PREVIEW_RELEASED",
      title: {
        zh: "TITMAS Trust Infrastructure",
        en: "TITMAS Trust Infrastructure",
      },
      description: {
        zh: "围绕 Identity、Boundary、Evidence、Health、Memory 与 Reputation 的可组合可信关注面。",
        en: "Composable trust concerns across Identity, Boundary, Evidence, Health, Memory, and Reputation.",
      },
      href: {
        zh: "/research/index/#titmas-trust-infrastructure",
        en: "/en/research/index/#titmas-trust-infrastructure",
      },
      metadata: ["SPECIFICATION", "ADAPTER_CONTRACT", "CONFORMANCE"],
    },
  ],
  applications: [
    {
      id: "media-evidence",
      type: "INDUSTRY_APPLICATION_PROFILE",
      status: "LOCAL_SYNTHETIC_REFERENCE_IMPLEMENTATION",
      title: {
        zh: "TITMAS 媒体证据",
        en: "TITMAS Media Evidence",
      },
      description: {
        zh: "面向人工智能生成内容安全的智能审核证据链参考实现；覆盖生成前、生成中和生成后。",
        en: "A review-evidence-chain reference implementation for AI-generated-content safety across pre-, during-, and post-generation stages.",
      },
      href: {
        zh: "/industry/media-evidence/",
        en: "/en/industry/media-evidence/",
      },
      metadata: ["SYNTHETIC_DATA_ONLY", "TRUTH_VERIFICATION=false", "PRODUCTION_READY=false"],
    },
    {
      id: "medical-evidence",
      type: "INDUSTRY_APPLICATION_DIRECTION",
      status: "PUBLISHED_DIRECTION",
      title: {
        zh: "医疗证据基础设施",
        en: "Medical Evidence Infrastructure",
      },
      description: {
        zh: "TITMAS 在医疗设备、操作过程与医疗智能体证据方向上的行业应用；不是独立医疗软件。",
        en: "A TITMAS application direction for medical-device, operational, and agent evidence; not standalone medical software.",
      },
      href: {
        zh: "/industry/medical-evidence/",
        en: "/en/industry/medical-evidence/",
      },
      metadata: ["DIRECTION_ONLY", "INDEPENDENT_MEDICAL_PLATFORM=false"],
    },
    {
      id: "manufacturing-agent-ecosystem",
      type: "INDUSTRY_APPLICATION_EXAMPLE",
      status: "PUBLISHED_EXAMPLE",
      title: {
        zh: "智能制造智能体生态",
        en: "Manufacturing AI Agent Ecosystem",
      },
      description: {
        zh: "展示行业 Agent 如何使用共同可信基础；TITMAS 不提供 MES、设备控制或制造解决方案。",
        en: "Shows how industry agents use a shared trust foundation; TITMAS provides no MES, device control, or manufacturing solution.",
      },
      href: {
        zh: "/industries/",
        en: "/en/industries/",
      },
      metadata: ["APPLICATION_EXAMPLE", "NO_PRODUCTION_CERTIFICATION"],
    },
    {
      id: "space-agent-evidence",
      type: "INDUSTRY_APPLICATION_PROFILE",
      status: "PUBLISHED_RESEARCH_PROFILE",
      title: {
        zh: "自主航天智能体可信执行（SAEP）",
        en: "Space Agent Evidence Profile (SAEP)",
      },
      description: {
        zh: "TITMAS 面向自主航天系统的垂直应用剖面；基于 EEOAP 研究合成、可核验、可离线检查的执行证据。",
        en: "A TITMAS vertical profile using EEOAP to research synthetic, verifiable, and offline-reviewable execution evidence for autonomous space systems.",
      },
      href: {
        zh: "/industry/space-agent-evidence/",
        en: "/en/industry/space-agent-evidence/",
      },
      metadata: ["RESEARCH_PROTOTYPE", "EVIDENCE_ORIGIN=SYNTHETIC", "FLIGHT_CERTIFIED=false"],
    },
  ],
  demos: [
    {
      id: "media-evidence",
      type: "SYNTHETIC_REFERENCE_DEMO",
      status: "FRONTEND_ONLY_LOCAL_DEMO",
      title: {
        zh: "TITMAS 媒体证据在线演示",
        en: "TITMAS Media Evidence demo",
      },
      description: {
        zh: "使用三个合成场景展示治理生命周期、证据冲突和篡改检测；不上传媒体或连接外部服务。",
        en: "Three synthetic scenarios show lifecycle, evidence conflict, and tamper detection without uploads or external services.",
      },
      href: {
        zh: "/demo/media-evidence/",
        en: "/en/demo/media-evidence/",
      },
      metadata: ["SYNTHETIC_DATA=true", "NO_UPLOAD", "NO_EXTERNAL_API"],
    },
    {
      id: "digital-cell",
      type: "REFERENCE_DEMO",
      status: "REFERENCE_COMPLETE",
      title: {
        zh: "TITMAS Digital Cell Demo",
        en: "TITMAS Digital Cell Demo",
      },
      description: {
        zh: "展示最小可信执行对象、确定性重放、证据记录与健康视图。",
        en: "Shows minimal trusted execution objects, deterministic replay, evidence records, and a health view.",
      },
      href: {
        zh: "/digital-cell/",
        en: "/en/digital-cell/",
      },
      metadata: ["RUNNABLE_REFERENCE", "PRODUCTION_CLAIM=false"],
    },
    {
      id: "udi-dicom-evidence",
      type: "SYNTHETIC_REFERENCE_DEMO",
      status: "STATIC_SYNTHETIC_UI_DEMO",
      title: {
        zh: "UDI-DICOM Evidence Validator",
        en: "UDI-DICOM Evidence Validator",
      },
      description: {
        zh: "使用模拟输入说明 Identity → Imaging → Evidence 的结构关系；不执行真实登记库查询或临床验证。",
        en: "Uses synthetic input to explain Identity → Imaging → Evidence; no real registry query or clinical validation.",
      },
      href: {
        zh: "/demo/medical-evidence/",
        en: "/en/demo/medical-evidence/",
      },
      metadata: ["SYNTHETIC_DATA=true", "CLINICAL_VALIDATION=false"],
    },
  ],
};

export const productSurfaceGate = {
  routeTemplate: "/products/{slug}/",
  registryInterface: "site-catalog.json#/extension_interfaces/products",
  publicNavigation: false,
  sitemapVisible: false,
  availableProducts: 0,
  activationGate: "AVAILABLE_PRODUCTS_GT_0",
} as const;
