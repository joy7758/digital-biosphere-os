import type { Metadata } from "next";
import { IndustryPage } from "../../industry-page";

export const metadata: Metadata = {
  title: "Manufacturing AI Agent Ecosystem",
  description: "Manufacturing as a high-value application example of TITMAS trust infrastructure.",
  alternates: {
    canonical: "/en/industries/",
    languages: { "zh-CN": "/industries/", en: "/en/industries/" },
  },
};

export default function EnglishIndustries() {
  return <IndustryPage locale="en" />;
}
