import { CommercialCollectionPage, commercialCollectionMetadata } from "../../commercial-collection-page";

export const metadata = commercialCollectionMetadata("en", "platform");

export default function PlatformPage() {
  return <CommercialCollectionPage locale="en" collection="platform" />;
}
