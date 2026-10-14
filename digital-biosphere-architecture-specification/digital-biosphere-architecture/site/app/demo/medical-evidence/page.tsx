import type { Metadata } from "next";
import { MedicalEvidencePage } from "../../medical-evidence-page";

export const metadata: Metadata = {
  title: "UDI-DICOM Evidence Validator Demo | TITMAS",
  description: "TITMAS 医疗证据方向的模拟 UDI-DICOM 引用关系参考 Demo；不构成诊断、临床安全、认证或生产声明。",
  keywords: ["TITMAS", "UDI-DICOM", "Medical Device Evidence", "Evidence Validator Demo"],
  alternates: {
    canonical: "/demo/medical-evidence/",
    languages: { "zh-CN": "/demo/medical-evidence/", en: "/en/demo/medical-evidence/" },
  },
};

export default function MedicalEvidenceDemo() {
  return <MedicalEvidencePage locale="zh" />;
}
