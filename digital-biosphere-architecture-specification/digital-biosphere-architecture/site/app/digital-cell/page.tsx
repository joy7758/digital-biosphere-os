import type { Metadata } from "next";
import { DigitalCellPage } from "../digital-cell-page";

export const metadata: Metadata = {
  title: "TITMAS Digital Cell Demo v0.1",
  description: "一个展示 AI Agent 如何具备身份、边界、执行证据和健康状态的最小参考实现。",
  alternates: {
    canonical: "/digital-cell/",
    languages: { "zh-CN": "/digital-cell/", en: "/en/digital-cell/" },
  },
  openGraph: {
    title: "TITMAS Digital Cell Demo v0.1",
    description: "A minimal reference implementation of an observable, verifiable, and health-assessable digital agent.",
    images: ["/digital-cell/digital-cell-architecture.png"],
  },
};

export default function DigitalCell() {
  return <DigitalCellPage locale="zh" />;
}
