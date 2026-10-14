import type { Metadata } from "next";
import { StatusPage } from "../../status-page";

export const metadata: Metadata = {
  title: "Current status",
  description:
    "Current verifiable status and release gates for Trusted Multi-Agent Infrastructure.",
  alternates: {
    canonical: "/en/status/",
    languages: { "zh-CN": "/status/", en: "/en/status/" },
  },
};

export default function EnglishStatus() {
  return <StatusPage locale="en" />;
}
