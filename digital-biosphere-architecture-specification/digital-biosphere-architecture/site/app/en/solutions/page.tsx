import { CommercialCollectionPage, commercialCollectionMetadata } from "../../commercial-collection-page";

export const metadata = commercialCollectionMetadata("en", "solutions");

export default function SolutionsPage() {
  return <CommercialCollectionPage locale="en" collection="solutions" />;
}
