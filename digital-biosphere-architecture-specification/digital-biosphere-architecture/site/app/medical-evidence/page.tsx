import type { Metadata } from "next";
import { MedicalEvidencePage } from "../medical-evidence-page";

export const metadata: Metadata = {
  title: "UDI-DICOM Evidence Validator Demo | TITMAS",
  description: "兼容入口：TITMAS 医疗证据方向的模拟 UDI-DICOM 引用关系参考 Demo。",
  alternates: {
    canonical: "/demo/medical-evidence/",
    languages: { "zh-CN": "/demo/medical-evidence/", en: "/en/demo/medical-evidence/" },
  },
};

export default function MedicalEvidence() {
  return <MedicalEvidencePage locale="zh" />;
}
