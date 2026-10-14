import type { Metadata } from "next";
import { DirectoryPage } from "../../directory-page";

export const metadata: Metadata = {
  title: "研究索引",
  description: "TITMAS 已发布研究基础、研究方向与基础设施研究索引。",
  alternates: {
    canonical: "/research/index/",
    languages: { "zh-CN": "/research/index/", en: "/en/research/index/" },
  },
};

export default function ResearchIndex() {
  return <DirectoryPage locale="zh" section="research" indexOnly />;
}
