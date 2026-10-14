import { CommercialCollectionPage, commercialCollectionMetadata } from "../../commercial-collection-page";

export const metadata = commercialCollectionMetadata("en", "products");

export default function ProductsPage() {
  return <CommercialCollectionPage locale="en" collection="products" />;
}
