import { CommercialCollectionPage, commercialCollectionMetadata } from "../commercial-collection-page";

export const metadata = commercialCollectionMetadata("zh", "products");

export default function ProductsPage() {
  return <CommercialCollectionPage locale="zh" collection="products" />;
}
