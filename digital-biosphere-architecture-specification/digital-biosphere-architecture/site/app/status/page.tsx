import type { Metadata } from "next";
import { StatusPage } from "../status-page";

export const metadata: Metadata = {
  title: "当前状态",
  description: "可信多智能体基础设施当前可验证状态与发布闸门。",
  alternates: {
    canonical: "/status/",
    languages: { "zh-CN": "/status/", en: "/en/status/" },
  },
};

export default function ChineseStatus() {
  return <StatusPage locale="zh" />;
}
