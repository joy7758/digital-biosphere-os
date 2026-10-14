import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { CommercialPublicPage, commercialMetadata } from "../../commercial-public-page";
import { commercialSlugs, isCommercialSlug } from "../../commercial-public-content";

export function generateStaticParams() {
  return commercialSlugs.map((commercial) => ({ commercial }));
}

export async function generateMetadata({ params }: { params: Promise<{ commercial: string }> }): Promise<Metadata> {
  const { commercial } = await params;
  if (!isCommercialSlug(commercial)) return {};
  return commercialMetadata("en", commercial);
}

export default async function CommercialPage({ params }: { params: Promise<{ commercial: string }> }) {
  const { commercial } = await params;
  if (!isCommercialSlug(commercial)) notFound();
  return <CommercialPublicPage locale="en" pageKey={commercial} />;
}
