import type { Metadata } from "next";
import { WebsiteUpdateConstitutionPage } from "../../../update-constitution-page";

export const metadata: Metadata = {
  title: "Website Update Constitution",
  description: "The OpenAI and OpenTelemetry reference decision baseline for TITMAS website updates.",
  alternates: {
    canonical: "/en/updates/constitution/",
    languages: { "zh-CN": "/updates/constitution/", en: "/en/updates/constitution/" },
  },
};

export default function EnglishWebsiteUpdateConstitution() {
  return <WebsiteUpdateConstitutionPage locale="en" />;
}
