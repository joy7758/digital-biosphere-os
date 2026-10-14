import type { Metadata } from "next";
import { PortalPage } from "./portal-page";

export const metadata: Metadata = {
  title: { absolute: "山西游骑兵电子商务有限公司" },
  description:
    "TITMAS智能体行动控制与可验证执行平台。闭源私有核心，公开发现与合成证明。",
  alternates: {
    canonical: "/",
    languages: { "zh-CN": "/", en: "/en/" },
  },
};

export default function Home() {
  return <PortalPage locale="zh" />;
}
