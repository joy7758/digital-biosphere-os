import type { Metadata } from "next";
import { UpdatesPage } from "../updates-page";

export const metadata: Metadata = {
  title: "更新与公告",
  description: "TITMAS 网站、研究、Demo 与治理信息的可追溯更新记录。",
  alternates: {
    canonical: "/updates/",
    languages: { "zh-CN": "/updates/", en: "/en/updates/" },
  },
};

export default function Updates() {
  return <UpdatesPage locale="zh" />;
}
