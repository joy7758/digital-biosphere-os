import assert from "node:assert/strict";
import { mkdir, writeFile, rm, access } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import test from "node:test";
import { sites } from "../build/sites-vite-plugin.ts";

async function fileExists(path) {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

test("sites vite plugin", async (t) => {
  await t.test("plugin definition", () => {
    const plugin = sites();
    assert.equal(plugin.name, "vinext-sites");
    assert.equal(plugin.enforce, "pre");
    assert.equal(plugin.apply, "build");
  });

  await t.test("resolveId returns null for unhandled source", () => {
    const plugin = sites();
    assert.equal(plugin.resolveId("other"), null);
  });

  await t.test("resolveId resolves vinext/server/image-optimization", () => {
    const plugin = sites();
    assert.equal(plugin.resolveId("vinext/server/image-optimization"), "\0vinext/server/image-optimization");
  });

  await t.test("load returns mock code for resolved image-optimization", () => {
    const plugin = sites();
    const code = plugin.load("\0vinext/server/image-optimization");
    assert.match(code, /export const DEFAULT_DEVICE_SIZES/);
    assert.match(code, /export const DEFAULT_IMAGE_SIZES/);
    assert.match(code, /export function handleImageOptimization/);
  });

  await t.test("load returns null for unhandled id", () => {
    const plugin = sites();
    assert.equal(plugin.load("other"), null);
  });

  await t.test("copies hosting.json and drizzle directory if they exist", async () => {
    const plugin = sites();
    const root = join(tmpdir(), `sites-plugin-test-1-${Date.now()}`);
    try {
      await mkdir(join(root, ".openai"), { recursive: true });
      await mkdir(join(root, "drizzle"), { recursive: true });

      await writeFile(join(root, ".openai", "hosting.json"), '{"test":true}');
      await writeFile(join(root, "drizzle", "schema.ts"), 'export const schema = {}');

      // plugin configResolved hook
      if (plugin.configResolved) {
          plugin.configResolved({ root });
      }

      // plugin closeBundle hook
      if (plugin.closeBundle) {
          await plugin.closeBundle();
      }

      const distOpenai = join(root, "dist", ".openai");
      assert.equal(await fileExists(join(distOpenai, "hosting.json")), true);
      assert.equal(await fileExists(join(distOpenai, "drizzle", "schema.ts")), true);
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });

  await t.test("works when source files do not exist", async () => {
    const plugin = sites();
    const root = join(tmpdir(), `sites-plugin-test-2-${Date.now()}`);
    try {
      await mkdir(root, { recursive: true });

      if (plugin.configResolved) {
          plugin.configResolved({ root });
      }

      if (plugin.closeBundle) {
          await plugin.closeBundle();
      }

      const distOpenai = join(root, "dist", ".openai");
      assert.equal(await fileExists(distOpenai), true);
      assert.equal(await fileExists(join(distOpenai, "hosting.json")), false);
      assert.equal(await fileExists(join(distOpenai, "drizzle")), false);
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });

  await t.test("cleans up existing dist directory before copying", async () => {
    const plugin = sites();
    const root = join(tmpdir(), `sites-plugin-test-3-${Date.now()}`);
    try {
      const distOpenai = join(root, "dist", ".openai");
      await mkdir(distOpenai, { recursive: true });

      // Create an old file that should be deleted
      await writeFile(join(distOpenai, "old-file.txt"), "old content");

      await mkdir(join(root, ".openai"), { recursive: true });
      await writeFile(join(root, ".openai", "hosting.json"), '{"test":true}');

      if (plugin.configResolved) {
          plugin.configResolved({ root });
      }

      if (plugin.closeBundle) {
          await plugin.closeBundle();
      }

      assert.equal(await fileExists(join(distOpenai, "hosting.json")), true);
      assert.equal(await fileExists(join(distOpenai, "old-file.txt")), false);
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });
});
