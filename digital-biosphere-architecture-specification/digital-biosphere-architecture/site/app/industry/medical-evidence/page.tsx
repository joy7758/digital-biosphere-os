import type { Metadata } from "next";
import { MedicalEvidenceIndustryPage } from "../../medical-evidence-industry-page";

export const metadata: Metadata = {
  title: "医疗证据基础设施 | TITMAS Healthcare Evidence Infrastructure",
  description: "基于 TITMAS 基础设施构建的医疗设备身份、操作过程和 AI 智能体证据验证方向。",
  keywords: ["TITMAS", "Medical Evidence Infrastructure", "UDI-DICOM", "Healthcare AI Governance", "Medical Device Evidence"],
  alternates: {
    canonical: "/industry/medical-evidence/",
    languages: { "zh-CN": "/industry/medical-evidence/", en: "/en/industry/medical-evidence/" },
  },
};

export default function MedicalEvidenceIndustry() {
  return <MedicalEvidenceIndustryPage locale="zh" />;
}
