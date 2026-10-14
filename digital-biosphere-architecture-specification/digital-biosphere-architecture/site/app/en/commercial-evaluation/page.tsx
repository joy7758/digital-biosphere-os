import type { Metadata } from "next";
import { CommercialEvaluationPage } from "../../commercial-evaluation-page";

export const metadata: Metadata = {
  title: "Commercial Evaluation Pack v0.1",
  description: "The ten-minute TITMAS commercial evaluation entry, validation boundaries, and complete same-origin materials.",
  alternates: {
    canonical: "/en/commercial-evaluation/",
    languages: { "zh-CN": "/commercial-evaluation/", en: "/en/commercial-evaluation/" },
  },
};

export default function EnglishCommercialEvaluation() {
  return <CommercialEvaluationPage locale="en" />;
}
