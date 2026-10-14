import type { Metadata } from "next";
import { WebsiteUpdateConstitutionPage } from "../../update-constitution-page";

export const metadata: Metadata = {
  title: "网站更新宪法",
  description: "TITMAS 网站更新的 OpenAI 与 OpenTelemetry 参考决策基准。",
  alternates: {
    canonical: "/updates/constitution/",
    languages: { "zh-CN": "/updates/constitution/", en: "/en/updates/constitution/" },
  },
};

export default function WebsiteUpdateConstitution() {
  return <WebsiteUpdateConstitutionPage locale="zh" />;
}
