const categories = new Set([
  "RELEASE_NOTE",
  "RESEARCH_UPDATE",
  "DEMO_UPDATE",
  "GOVERNANCE_NOTICE",
  "MAINTENANCE_NOTICE",
]);

const severityCategories = new Set([
  "GOVERNANCE_NOTICE",
  "MAINTENANCE_NOTICE",
]);

const severityRank = {
  critical: 4,
  high: 3,
  medium: 2,
  informational: 1,
  none: 0,
};

const commitPattern = /^(?:[0-9a-f]{40}|[0-9a-f]{64})$/;
const slugPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

export function validateUpdatesCatalog(catalog) {
  if (!catalog || !Array.isArray(catalog.items)) {
    throw new Error("UPDATES_ITEMS_REQUIRED");
  }

  const seen = new Set();
  for (const item of catalog.items) {
    if (!slugPattern.test(item.slug || "")) throw new Error(`INVALID_UPDATE_SLUG:${item.slug}`);
    if (seen.has(item.slug)) throw new Error(`DUPLICATE_UPDATE_SLUG:${item.slug}`);
    seen.add(item.slug);
    if (!categories.has(item.category)) throw new Error(`INVALID_UPDATE_CATEGORY:${item.slug}`);
    if (!commitPattern.test(item.source_commit || "")) throw new Error(`INVALID_SOURCE_COMMIT:${item.slug}`);
    if (!["PUBLISHED", "SUPERSEDED", "WITHDRAWN"].includes(item.status)) {
      throw new Error(`INVALID_UPDATE_STATUS:${item.slug}`);
    }
    if (!Array.isArray(item.audience) || item.audience.length === 0) {
      throw new Error(`UPDATE_AUDIENCE_REQUIRED:${item.slug}`);
    }
    if (!item.effective_date || Number.isNaN(Date.parse(item.effective_date))) {
      throw new Error(`INVALID_EFFECTIVE_DATE:${item.slug}`);
    }
    if (item.expires_at !== null && Number.isNaN(Date.parse(item.expires_at))) {
      throw new Error(`INVALID_EXPIRES_AT:${item.slug}`);
    }
    if (item.severity !== null && !severityCategories.has(item.category)) {
      throw new Error(`SEVERITY_NOT_ALLOWED:${item.slug}`);
    }
    if (item.severity !== null && !(item.severity in severityRank)) {
      throw new Error(`INVALID_SEVERITY:${item.slug}`);
    }
    if (!item.title?.zh || !item.title?.en || !item.summary?.zh || !item.summary?.en) {
      throw new Error(`BILINGUAL_UPDATE_CONTENT_REQUIRED:${item.slug}`);
    }
    if (!item.href?.zh || !item.href?.en) throw new Error(`BILINGUAL_UPDATE_ROUTE_REQUIRED:${item.slug}`);
    if (!Array.isArray(item.truth_boundaries) || item.truth_boundaries.length === 0) {
      throw new Error(`TRUTH_BOUNDARIES_REQUIRED:${item.slug}`);
    }
    for (const boundary of item.truth_boundaries) {
      if (!boundary.scope || !boundary.limitation) {
        throw new Error(`INVALID_TRUTH_BOUNDARY:${item.slug}`);
      }
    }
  }

  for (const item of catalog.items) {
    if (item.supersedes === null) continue;
    const replaced = catalog.items.find((candidate) => candidate.slug === item.supersedes);
    if (!replaced) throw new Error(`SUPERSEDES_TARGET_NOT_FOUND:${item.slug}`);
    if (replaced.status !== "SUPERSEDED") {
      throw new Error(`SUPERSEDES_TARGET_NOT_MARKED:${item.slug}`);
    }
  }

  return true;
}

export function selectActiveAnnouncement(items, at = new Date()) {
  const now = at instanceof Date ? at.getTime() : new Date(at).getTime();
  const active = items.filter((item) => {
    if (!item.is_announcement || item.status !== "PUBLISHED") return false;
    const effective = Date.parse(item.effective_date);
    const expires = item.expires_at === null ? Number.POSITIVE_INFINITY : Date.parse(item.expires_at);
    return effective <= now && now < expires;
  });

  return active.sort((left, right) => {
    const severityDelta =
      (severityRank[right.severity || "none"] || 0) -
      (severityRank[left.severity || "none"] || 0);
    if (severityDelta !== 0) return severityDelta;

    const leftExpiry = left.expires_at === null ? Number.POSITIVE_INFINITY : Date.parse(left.expires_at);
    const rightExpiry = right.expires_at === null ? Number.POSITIVE_INFINITY : Date.parse(right.expires_at);
    if (leftExpiry !== rightExpiry) return leftExpiry - rightExpiry;

    return Date.parse(right.effective_date) - Date.parse(left.effective_date);
  })[0] || null;
}

export const updateContract = {
  categories,
  severityCategories,
  severityRank,
};
