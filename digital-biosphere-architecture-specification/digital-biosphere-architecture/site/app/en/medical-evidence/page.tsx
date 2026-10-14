import type { Metadata } from "next";
import { MedicalEvidencePage } from "../../medical-evidence-page";

export const metadata: Metadata = {
  title: "UDI-DICOM Evidence Validator Demo | TITMAS",
  description: "Compatibility entry for the TITMAS synthetic UDI-DICOM evidence reference demo.",
  alternates: {
    canonical: "/en/demo/medical-evidence/",
    languages: { "zh-CN": "/demo/medical-evidence/", en: "/en/demo/medical-evidence/" },
  },
};

export default function EnglishMedicalEvidence() {
  return <MedicalEvidencePage locale="en" />;
}
