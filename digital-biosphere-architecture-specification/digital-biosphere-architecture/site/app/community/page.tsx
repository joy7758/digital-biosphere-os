import type { Metadata } from "next";
import { CommunityPage } from "../community-page";

export const metadata: Metadata = {
  title: "开发者入口",
  description: "TITMAS 的完整中文开发者入口、贡献边界与当前状态。",
  alternates: {
    canonical: "/community/",
    languages: { "zh-CN": "/community/", en: "/en/community/" },
  },
};

export default function ChineseCommunity() {
  return <CommunityPage locale="zh" />;
}
