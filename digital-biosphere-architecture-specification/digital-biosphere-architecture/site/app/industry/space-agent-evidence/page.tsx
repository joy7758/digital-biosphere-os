import type { Metadata } from "next";
import { SpaceAgentEvidencePage } from "../../space-agent-evidence-page";

export const metadata: Metadata = {
  title: "自主航天智能体可信执行（SAEP）",
  description: "SAEP 是 TITMAS 面向自主航天系统的行业应用剖面，基于 EEOAP 展示合成、可核验、可离线检查的执行证据路径。",
  keywords: [
    "自主航天智能体",
    "AI Agent可信执行",
    "智能体治理",
    "数字生物圈",
    "执行证据",
    "航天人工智能",
    "Space Agent Evidence Profile",
    "Autonomous Space Systems",
    "AI Agent Governance",
    "Execution Evidence",
    "Digital Biosphere",
  ],
  alternates: {
    canonical: "/industry/space-agent-evidence/",
    languages: { "zh-CN": "/industry/space-agent-evidence/", en: "/en/industry/space-agent-evidence/" },
  },
};

export default function SpaceAgentEvidenceIndustry() {
  return <SpaceAgentEvidencePage locale="zh" />;
}
