import type { Metadata } from "next";
import { DigitalCellPage } from "../../digital-cell-page";

export const metadata: Metadata = {
  title: "TITMAS Digital Cell Demo v0.1",
  description: "A minimal reference implementation showing agent identity, boundaries, execution evidence, and health state.",
  alternates: {
    canonical: "/en/digital-cell/",
    languages: { "zh-CN": "/digital-cell/", en: "/en/digital-cell/" },
  },
  openGraph: {
    title: "TITMAS Digital Cell Demo v0.1",
    description: "A minimal reference implementation of an observable, verifiable, and health-assessable digital agent.",
    images: ["/digital-cell/digital-cell-architecture.png"],
  },
};

export default function EnglishDigitalCell() {
  return <DigitalCellPage locale="en" />;
}
