import type { Metadata } from "next";
import { IndustryPage } from "../industry-page";

export const metadata: Metadata = {
  title: "智能制造智能体生态",
  description: "制造业作为 TITMAS 可信智能体基础设施的高价值应用示例。",
  alternates: {
    canonical: "/industries/",
    languages: { "zh-CN": "/industries/", en: "/en/industries/" },
  },
};

export default function Industries() {
  return <IndustryPage locale="zh" />;
}
