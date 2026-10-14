import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { CommercialPublicPage, commercialMetadata } from "../../../commercial-public-page";
import { isProductKey, productKeys } from "../../../commercial-public-content";

export function generateStaticParams() {
  return productKeys.map((product) => ({ product }));
}

export async function generateMetadata({ params }: { params: Promise<{ product: string }> }): Promise<Metadata> {
  const { product } = await params;
  if (!isProductKey(product)) return {};
  return commercialMetadata("en", product);
}

export default async function ProductPage({ params }: { params: Promise<{ product: string }> }) {
  const { product } = await params;
  if (!isProductKey(product)) notFound();
  return <CommercialPublicPage locale="en" pageKey={product} />;
}
