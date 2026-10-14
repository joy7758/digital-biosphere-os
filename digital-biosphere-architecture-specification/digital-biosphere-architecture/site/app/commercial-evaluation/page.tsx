import type { Metadata } from "next";
import { CommercialEvaluationPage } from "../commercial-evaluation-page";

export const metadata: Metadata = {
  title: "第一版商业评估包 v0.1",
  description: "TITMAS 商业评估包的十分钟入口、验证边界和完整同源资料。",
  alternates: {
    canonical: "/commercial-evaluation/",
    languages: { "zh-CN": "/commercial-evaluation/", en: "/en/commercial-evaluation/" },
  },
};

export default function ChineseCommercialEvaluation() {
  return <CommercialEvaluationPage locale="zh" />;
}
