import type { Metadata } from "next";
import { DirectoryPage } from "../../../directory-page";

export const metadata: Metadata = {
  title: "Research Index",
  description: "Index of published TITMAS research foundations, directions, and infrastructure research.",
  alternates: {
    canonical: "/en/research/index/",
    languages: { "zh-CN": "/research/index/", en: "/en/research/index/" },
  },
};

export default function EnglishResearchIndex() {
  return <DirectoryPage locale="en" section="research" indexOnly />;
}
