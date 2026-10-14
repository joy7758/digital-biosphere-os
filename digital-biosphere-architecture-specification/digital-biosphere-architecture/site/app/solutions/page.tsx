import { CommercialCollectionPage, commercialCollectionMetadata } from "../commercial-collection-page";

export const metadata = commercialCollectionMetadata("zh", "solutions");

export default function SolutionsPage() {
  return <CommercialCollectionPage locale="zh" collection="solutions" />;
}
