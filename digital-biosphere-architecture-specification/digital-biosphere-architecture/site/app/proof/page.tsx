import { CommercialCollectionPage, commercialCollectionMetadata } from "../commercial-collection-page";

export const metadata = commercialCollectionMetadata("zh", "proof");

export default function ProofPage() {
  return <CommercialCollectionPage locale="zh" collection="proof" />;
}
