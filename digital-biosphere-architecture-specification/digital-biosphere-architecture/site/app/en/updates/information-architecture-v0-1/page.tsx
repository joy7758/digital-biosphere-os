import type { Metadata } from "next";
import { UpdateDetailPage } from "../../../update-detail-page";

export const metadata: Metadata = {
  title: "Site Information Architecture v0.1 Update",
  description: "Update note for the Research, Applications, Demos, and product-entry gate information architecture.",
  alternates: {
    canonical: "/en/updates/information-architecture-v0-1/",
    languages: {
      "zh-CN": "/updates/information-architecture-v0-1/",
      en: "/en/updates/information-architecture-v0-1/",
    },
  },
};

export default function EnglishInformationArchitectureUpdate() {
  return <UpdateDetailPage locale="en" slug="information-architecture-v0-1" />;
}
