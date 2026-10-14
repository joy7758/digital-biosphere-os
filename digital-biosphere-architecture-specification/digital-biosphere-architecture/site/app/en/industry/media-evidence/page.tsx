import type { Metadata } from "next";
import { MediaEvidenceIndustryPage } from "../../../media-evidence-industry-page";

export const metadata: Metadata = {
  title: "AI-generated content review evidence chains",
  description: "A local synthetic TITMAS Evidence Architecture reference implementation for broadcasting and online audiovisual workflows.",
  alternates: { canonical: "/en/industry/media-evidence/", languages: { "zh-CN": "/industry/media-evidence/", en: "/en/industry/media-evidence/" } },
  openGraph: { title: "TITMAS Media Evidence", description: "A reviewable accountability-chain reference for AI-generated media workflows.", url: "/en/industry/media-evidence/", locale: "en_US", type: "article", images: ["/og-media-evidence.png"] },
};

export default function MediaEvidenceIndustryEn() { return <MediaEvidenceIndustryPage locale="en" />; }
