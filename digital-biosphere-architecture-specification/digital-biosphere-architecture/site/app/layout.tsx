import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://redcrag.cn"),
  icons: {
    icon: [{ url: "/titmas-logo.png", type: "image/png", sizes: "1024x1024" }],
    apple: [{ url: "/titmas-logo.png", type: "image/png", sizes: "1024x1024" }],
  },
  title: {
    default: "山西游骑兵电子商务有限公司",
    template: "%s · 山西游骑兵电子商务有限公司",
  },
  description:
    "TITMAS智能体行动控制与可验证执行平台：闭源私有核心、公开发现与合成证明。",
  openGraph: {
    type: "website",
    siteName: "山西游骑兵电子商务有限公司",
    title: "山西游骑兵电子商务有限公司",
    description:
      "TITMAS Agent Action Control and Verifiable Accountability Platform.",
    images: [
      {
        url: "/titmas-logo.png",
        width: 1024,
        height: 1024,
        alt: "夏日之海 / titmas",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "山西游骑兵电子商务有限公司",
    description:
      "Closed-core commercial agent infrastructure with public discovery and bounded synthetic proof.",
    images: ["/titmas-logo.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
