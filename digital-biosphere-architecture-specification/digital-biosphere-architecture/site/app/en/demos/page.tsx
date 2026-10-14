import type { Metadata } from "next";
import { DirectoryPage } from "../../directory-page";

export const metadata: Metadata = {
  title: "Reference Demos",
  description: "Index of the TITMAS Digital Cell and UDI-DICOM medical-evidence reference demos.",
  alternates: {
    canonical: "/en/demos/",
    languages: { "zh-CN": "/demos/", en: "/en/demos/" },
  },
};

export default function EnglishDemos() {
  return <DirectoryPage locale="en" section="demos" />;
}
