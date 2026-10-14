import type { Metadata } from "next";
import { SpaceAgentEvidencePage } from "../../../space-agent-evidence-page";

export const metadata: Metadata = {
  title: "Space Agent Evidence Profile (SAEP)",
  description: "Space Agent Evidence Profile (SAEP) is a TITMAS vertical profile using EEOAP to examine synthetic, verifiable, and offline-reviewable execution evidence for autonomous space systems.",
  keywords: [
    "Space Agent Evidence Profile",
    "Autonomous Space Systems",
    "AI Agent Governance",
    "Execution Evidence",
    "Digital Biosphere",
    "Trusted Agent Execution",
  ],
  alternates: {
    canonical: "/en/industry/space-agent-evidence/",
    languages: { "zh-CN": "/industry/space-agent-evidence/", en: "/en/industry/space-agent-evidence/" },
  },
};

export default function EnglishSpaceAgentEvidenceIndustry() {
  return <SpaceAgentEvidencePage locale="en" />;
}
