import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import { dirname, extname, join, normalize, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const outputRoot = join(siteRoot, "out");
let checked = 0;

function targetFor(pathname) {
  const clean = decodeURIComponent(pathname);
  if (clean === "/") return "index.html";
  if (clean.endsWith("/")) return `${clean.slice(1)}index.html`;
  if (extname(clean)) return clean.slice(1);
  return `${clean.slice(1)}/index.html`;
}

const release = await readFile(join(outputRoot, "release.json"), "utf8").then(JSON.parse);
const pages = release.routes.map((route) => [
  targetFor(route),
  new URL(route.endsWith("/") ? route : `${route}/`, "https://redcrag.cn/").href,
]);

for (const [page, base] of pages) {
  const html = await readFile(join(outputRoot, page), "utf8");
  for (const match of html.matchAll(/\bhref="([^"]+)"/g)) {
    const href = match[1];
    if (/^(?:https?:|mailto:|tel:)/.test(href)) continue;
    const url = new URL(href, base);
    const relativeTarget = normalize(targetFor(url.pathname));
    const absoluteTarget = join(outputRoot, relativeTarget);
    assert.ok(
      absoluteTarget === outputRoot || absoluteTarget.startsWith(`${outputRoot}/`),
      `link escapes output root: ${href}`,
    );
    await access(absoluteTarget);
    if (url.hash && absoluteTarget.endsWith(".html")) {
      const targetHtml = await readFile(absoluteTarget, "utf8");
      const id = decodeURIComponent(url.hash.slice(1)).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      assert.match(targetHtml, new RegExp(`\\bid="${id}"`), `missing fragment target: ${href}`);
    }
    checked += 1;
  }
}

console.log(`LOCAL_LINKS_CHECKED=${checked}`);
console.log("LOCAL_LINKS=PASS");
