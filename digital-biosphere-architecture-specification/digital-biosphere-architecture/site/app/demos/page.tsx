import type { Metadata } from "next";
import { DirectoryPage } from "../directory-page";

export const metadata: Metadata = {
  title: "参考 Demo",
  description: "TITMAS 媒体证据、Digital Cell 与 UDI-DICOM 医疗证据参考 Demo 索引。",
  alternates: {
    canonical: "/demos/",
    languages: { "zh-CN": "/demos/", en: "/en/demos/" },
  },
};

export default function Demos() {
  return <DirectoryPage locale="zh" section="demos" />;
}
