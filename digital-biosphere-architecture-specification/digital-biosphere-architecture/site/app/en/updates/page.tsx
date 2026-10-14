import type { Metadata } from "next";
import { UpdatesPage } from "../../updates-page";

export const metadata: Metadata = {
  title: "Updates & Announcements",
  description: "Traceable updates to the TITMAS site, research, demos, and governance information.",
  alternates: {
    canonical: "/en/updates/",
    languages: { "zh-CN": "/updates/", en: "/en/updates/" },
  },
};

export default function EnglishUpdates() {
  return <UpdatesPage locale="en" />;
}
