import type { Metadata } from "next";
import { DirectoryPage } from "../../directory-page";

export const metadata: Metadata = {
  title: "Research",
  description: "Research entry for Digital Biosphere, Evidence Governance, and TITMAS trust infrastructure.",
  alternates: {
    canonical: "/en/research/",
    languages: { "zh-CN": "/research/", en: "/en/research/" },
  },
};

export default function EnglishResearch() {
  return <DirectoryPage locale="en" section="research" />;
}
