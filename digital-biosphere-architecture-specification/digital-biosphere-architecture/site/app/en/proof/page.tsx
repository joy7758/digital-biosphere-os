import { CommercialCollectionPage, commercialCollectionMetadata } from "../../commercial-collection-page";

export const metadata = commercialCollectionMetadata("en", "proof");

export default function ProofPage() {
  return <CommercialCollectionPage locale="en" collection="proof" />;
}
