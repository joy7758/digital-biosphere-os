import { CommercialCollectionPage, commercialCollectionMetadata } from "../commercial-collection-page";

export const metadata = commercialCollectionMetadata("zh", "platform");

export default function PlatformPage() {
  return <CommercialCollectionPage locale="zh" collection="platform" />;
}
