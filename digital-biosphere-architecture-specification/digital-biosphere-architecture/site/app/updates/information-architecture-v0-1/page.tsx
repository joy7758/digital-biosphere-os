import type { Metadata } from "next";
import { UpdateDetailPage } from "../../update-detail-page";

export const metadata: Metadata = {
  title: "网站信息架构 v0.1 更新",
  description: "Research、Applications、Demos 与产品入口门控的信息架构更新说明。",
  alternates: {
    canonical: "/updates/information-architecture-v0-1/",
    languages: {
      "zh-CN": "/updates/information-architecture-v0-1/",
      en: "/en/updates/information-architecture-v0-1/",
    },
  },
};

export default function InformationArchitectureUpdate() {
  return <UpdateDetailPage locale="zh" slug="information-architecture-v0-1" />;
}
