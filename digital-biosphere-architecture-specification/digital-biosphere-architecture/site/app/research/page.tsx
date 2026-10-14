import type { Metadata } from "next";
import { DirectoryPage } from "../directory-page";

export const metadata: Metadata = {
  title: "研究",
  description: "Digital Biosphere、Evidence Governance 与 TITMAS 可信基础设施研究入口。",
  alternates: {
    canonical: "/research/",
    languages: { "zh-CN": "/research/", en: "/en/research/" },
  },
};

export default function Research() {
  return <DirectoryPage locale="zh" section="research" />;
}
