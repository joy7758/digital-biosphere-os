import type { Metadata } from "next";
import { PortalPage } from "../portal-page";

export const metadata: Metadata = {
  title: { absolute: "山西游骑兵电子商务有限公司" },
  description:
    "TITMAS Agent Action Control and Verifiable Accountability Platform. Closed private core with public discovery and bounded synthetic proof.",
  alternates: {
    canonical: "/en/",
    languages: { "zh-CN": "/", en: "/en/" },
  },
};

export default function EnglishHome() {
  return <PortalPage locale="en" />;
}
