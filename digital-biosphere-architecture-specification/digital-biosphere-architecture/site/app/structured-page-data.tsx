import type { Locale } from "./site-content";

type StructuredPageType = "WebPage" | "CollectionPage" | "TechArticle" | "Article";

type StructuredPageDataProps = {
  locale: Locale;
  path: string;
  title: string;
  description: string;
  type?: StructuredPageType;
  datePublished?: string;
  dateModified?: string;
};

export function StructuredPageData({
  locale,
  path,
  title,
  description,
  type = "WebPage",
  datePublished,
  dateModified,
}: StructuredPageDataProps) {
  const url = new URL(path, "https://redcrag.cn").toString();
  const data = {
    "@context": "https://schema.org",
    "@type": type,
    "@id": `${url}#webpage`,
    url,
    name: title,
    headline: type === "Article" || type === "TechArticle" ? title : undefined,
    description,
    inLanguage: locale === "zh" ? "zh-CN" : "en",
    isPartOf: {
      "@id": "https://redcrag.cn/#website",
    },
    publisher: {
      "@id": "https://redcrag.cn/#organization",
    },
    datePublished,
    dateModified,
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
