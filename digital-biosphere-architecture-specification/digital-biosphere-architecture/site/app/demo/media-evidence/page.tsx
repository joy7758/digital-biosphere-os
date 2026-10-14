import type { Metadata } from "next";
import { MediaEvidenceDemoPage } from "../../media-evidence-demo-page";

export const metadata: Metadata = {
  title: "TITMAS 媒体证据在线演示",
  description: "使用本地合成数据展示人工智能生成内容治理生命周期、证据冲突和篡改检测。",
  alternates: { canonical: "/demo/media-evidence/", languages: { "zh-CN": "/demo/media-evidence/", en: "/en/demo/media-evidence/" } },
  openGraph: { title: "TITMAS 媒体证据在线演示", description: "三个纯前端合成场景：正常生命周期、证据冲突和篡改检测。", url: "/demo/media-evidence/", locale: "zh_CN", type: "article", images: ["/og-media-evidence.png"] },
};

export default function MediaEvidenceDemo() { return <MediaEvidenceDemoPage locale="zh" />; }
