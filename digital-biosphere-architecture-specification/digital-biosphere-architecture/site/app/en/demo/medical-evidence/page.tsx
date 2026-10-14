import type { Metadata } from "next";
import { MedicalEvidencePage } from "../../../medical-evidence-page";

export const metadata: Metadata = {
  title: "UDI-DICOM Evidence Validator Demo | TITMAS",
  description: "A synthetic reference demo for UDI-DICOM evidence relationships; no diagnosis, clinical safety, certification, or production claim.",
  keywords: ["TITMAS", "UDI-DICOM", "Medical Device Evidence", "Evidence Validator Demo"],
  alternates: {
    canonical: "/en/demo/medical-evidence/",
    languages: { "zh-CN": "/demo/medical-evidence/", en: "/en/demo/medical-evidence/" },
  },
};

export default function EnglishMedicalEvidenceDemo() {
  return <MedicalEvidencePage locale="en" />;
}
