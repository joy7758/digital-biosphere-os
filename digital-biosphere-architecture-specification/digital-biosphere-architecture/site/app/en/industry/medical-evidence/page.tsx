import type { Metadata } from "next";
import { MedicalEvidenceIndustryPage } from "../../../medical-evidence-industry-page";

export const metadata: Metadata = {
  title: "Medical Evidence Infrastructure | TITMAS",
  description: "A TITMAS industry direction for evidence across medical-device identity, operation processes, and medical AI agents.",
  keywords: ["TITMAS", "Medical Evidence Infrastructure", "UDI-DICOM", "Healthcare AI Governance", "Medical Device Evidence"],
  alternates: {
    canonical: "/en/industry/medical-evidence/",
    languages: { "zh-CN": "/industry/medical-evidence/", en: "/en/industry/medical-evidence/" },
  },
};

export default function EnglishMedicalEvidenceIndustry() {
  return <MedicalEvidenceIndustryPage locale="en" />;
}
