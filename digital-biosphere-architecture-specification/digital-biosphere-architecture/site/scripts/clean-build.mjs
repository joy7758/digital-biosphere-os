import { rm } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");

for (const generatedDirectory of ["dist", ".vinext"]) {
  await rm(join(siteRoot, generatedDirectory), { recursive: true, force: true });
}

console.log("Generated build directories cleared.");
