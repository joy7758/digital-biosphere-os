import rawCatalog from "../public/updates.json";
import {
  selectActiveAnnouncement,
  validateUpdatesCatalog,
} from "../scripts/update-contract.mjs";
import type { Locale } from "./site-content";

export type UpdateCategory =
  | "RELEASE_NOTE"
  | "RESEARCH_UPDATE"
  | "DEMO_UPDATE"
  | "GOVERNANCE_NOTICE"
  | "MAINTENANCE_NOTICE";

export type UpdateItem = {
  slug: string;
  category: UpdateCategory;
  status: "PUBLISHED" | "SUPERSEDED" | "WITHDRAWN";
  audience: string[];
  effective_date: string;
  expires_at: string | null;
  is_announcement: boolean;
  severity: "critical" | "high" | "medium" | "informational" | null;
  source_commit: string;
  source_url: string;
  supersedes: string | null;
  title: Record<Locale, string>;
  summary: Record<Locale, string>;
  href: Record<Locale, string>;
  changes: Record<Locale, string[]>;
  truth_boundaries: Array<{
    scope: string;
    limitation: string;
  }>;
};

type UpdatesCatalog = {
  schema_version: string;
  catalog_id: string;
  observed_at: string;
  route_template: string;
  categories: UpdateCategory[];
  items: UpdateItem[];
};

export const updatesCatalog = rawCatalog as unknown as UpdatesCatalog;
validateUpdatesCatalog(updatesCatalog);

export const publishedUpdates = [...updatesCatalog.items]
  .filter((item) => item.status === "PUBLISHED")
  .sort((left, right) => Date.parse(right.effective_date) - Date.parse(left.effective_date));

export function getActiveAnnouncement(at = new Date()) {
  return selectActiveAnnouncement(updatesCatalog.items, at) as UpdateItem | null;
}

export function formatUpdateDate(locale: Locale, value: string) {
  return new Intl.DateTimeFormat(locale === "zh" ? "zh-CN" : "en", {
    year: "numeric",
    month: locale === "zh" ? "long" : "short",
    day: "numeric",
    timeZone: "Asia/Shanghai",
  }).format(new Date(value));
}

export const updateCategoryLabels: Record<UpdateCategory, Record<Locale, string>> = {
  RELEASE_NOTE: { zh: "版本说明", en: "Release note" },
  RESEARCH_UPDATE: { zh: "研究更新", en: "Research update" },
  DEMO_UPDATE: { zh: "Demo 更新", en: "Demo update" },
  GOVERNANCE_NOTICE: { zh: "治理公告", en: "Governance notice" },
  MAINTENANCE_NOTICE: { zh: "维护公告", en: "Maintenance notice" },
};
