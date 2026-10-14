import type { Metadata } from "next";
import { MediaEvidenceDemoPage } from "../../../media-evidence-demo-page";

export const metadata: Metadata = {
  title: "TITMAS Media Evidence demo",
  description: "A frontend-only synthetic demo of AI-media lifecycle, evidence conflict, and tamper detection.",
  alternates: { canonical: "/en/demo/media-evidence/", languages: { "zh-CN": "/demo/media-evidence/", en: "/en/demo/media-evidence/" } },
  openGraph: { title: "TITMAS Media Evidence demo", description: "Three synthetic scenarios: lifecycle, conflict, and tamper detection.", url: "/en/demo/media-evidence/", locale: "en_US", type: "article", images: ["/og-media-evidence.png"] },
};

export default function MediaEvidenceDemoEn() { return <MediaEvidenceDemoPage locale="en" />; }
