import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { dirname, extname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const outputRoot = join(siteRoot, "out");
const textExtensions = new Set([".css", ".html", ".js", ".json", ".map", ".svg", ".txt", ".xml"]);

async function listTextFiles(current = outputRoot) {
  const files = [];
  for (const entry of await readdir(current, { withFileTypes: true })) {
    const absolute = join(current, entry.name);
    if (entry.isDirectory()) files.push(...(await listTextFiles(absolute)));
    else if (entry.isFile() && textExtensions.has(extname(entry.name))) files.push(absolute);
  }
  return files;
}

const rules = {
  PRIVATE_REPOSITORY_URL_FINDINGS: [
    /github\.com\/joy7758\/digital-biosphere-architecture-specification/i,
    /github\.com\/joy7758\/digital-biosphere-os/i,
    /github\.com\/joy7758\/SAEE/i,
    /github\.com\/joy7758\/titmas-private-developer-trial/i,
  ],
  SERVER_INFRASTRUCTURE_DISCLOSURE_FINDINGS: [
    /\b180\.76\.115\.193\b/,
    /\bhongyan-4cj\b/i,
    /\/srv\/tmai\//,
    /\bssh\s+(?:root@|hongyan)/i,
  ],
  SECRET_FINDINGS: [
    /\b(?:sk|ghp|github_pat|AKIA)[-_A-Za-z0-9.]{16,}\b/,
    /-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----/,
    /(?:api[_-]?key|access[_-]?token|client[_-]?secret)\s*[:=]\s*["'][^"']{8,}["']/i,
  ],
  PRIVATE_PATH_FINDINGS: [
    /\/Users\/[^/\s]+/,
    /\/home\/[^/\s]+/,
    /[A-Za-z]:\\Users\\[^\\\s]+/,
  ],
  CORE_SOURCE_DISCLOSURE_FINDINGS: [
    /\bentity_support\//,
    /\bTITMAS\/private-governance\//,
    /\bTITMAS\/private-stage5/i,
    /\bDBOS-EXP-0001\b/,
    /\bexpected_answer\b/i,
  ],
  CUSTOMER_DATA_FINDINGS: [
    /\bcustomer[_ -]?(?:name|email|phone|identifier)\s*[:=]/i,
    /\b(?:id_card|identity_card|national_id)\s*[:=]/i,
  ],
};

const findings = Object.fromEntries(Object.keys(rules).map((name) => [name, []]));
for (const absolute of await listTextFiles()) {
  const text = await readFile(absolute, "utf8");
  for (const [name, patterns] of Object.entries(rules)) {
    for (const pattern of patterns) {
      if (pattern.test(text)) {
        findings[name].push({ path: relative(outputRoot, absolute), pattern: String(pattern) });
      }
    }
  }
}

for (const [name, matches] of Object.entries(findings)) {
  console.log(`${name}=${matches.length}`);
  assert.equal(matches.length, 0, `${name}: ${JSON.stringify(matches)}`);
}
console.log("PUBLIC_OUTPUT_DISCLOSURE_SCAN=PASS");
