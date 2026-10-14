import type { Metadata } from "next";
import { DirectoryPage } from "../directory-page";

export const metadata: Metadata = {
  title: "行业应用",
  description: "TITMAS 媒体证据、医疗证据、智能制造与自主航天 SAEP 行业应用方向索引。",
  alternates: {
    canonical: "/applications/",
    languages: { "zh-CN": "/applications/", en: "/en/applications/" },
  },
};

export default function Applications() {
  return <DirectoryPage locale="zh" section="applications" />;
}
