import type { Metadata } from "next";
import { MediaEvidenceIndustryPage } from "../../media-evidence-industry-page";

export const metadata: Metadata = {
  title: "面向人工智能生成内容安全的智能审核证据链",
  description: "TITMAS 证据架构在广播电视和网络视听场景中的本地合成参考实现。",
  alternates: { canonical: "/industry/media-evidence/", languages: { "zh-CN": "/industry/media-evidence/", en: "/en/industry/media-evidence/" } },
  openGraph: { title: "TITMAS 媒体证据", description: "通过证据对象支持人工智能生成内容审核过程可追溯、可复核。", url: "/industry/media-evidence/", locale: "zh_CN", type: "article", images: ["/og-media-evidence.png"] },
};

export default function MediaEvidenceIndustry() { return <MediaEvidenceIndustryPage locale="zh" />; }
