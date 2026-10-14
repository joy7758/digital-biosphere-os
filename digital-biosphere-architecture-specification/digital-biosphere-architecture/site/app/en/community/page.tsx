import type { Metadata } from "next";
import { CommunityPage } from "../../community-page";

export const metadata: Metadata = {
  title: "Developer entry",
  description: "The complete English developer entry, contribution boundaries, and current status for titmas.",
  alternates: {
    canonical: "/en/community/",
    languages: { "zh-CN": "/community/", en: "/en/community/" },
  },
};

export default function EnglishCommunity() {
  return <CommunityPage locale="en" />;
}
