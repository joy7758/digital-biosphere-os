import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../public/sdk/v0.1/", import.meta.url);
const publicRoot = new URL("../public/", import.meta.url);
const manifest = JSON.parse(await readFile(new URL("manifest.json", root), "utf8"));

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

test("publishes the exact public-safe wheel digest without changing release authority", async () => {
  const wheel = await readFile(
    new URL("downloads/digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl", publicRoot),
  );
  assert.equal(sha256(wheel), manifest.package.sha256);
  assert.equal(manifest.package.sha256, "edf92e548860384b1416a612a7e319e0d994bb324f8621847d0d154624ae8f09");
  assert.equal(manifest.public_protocol_release, false);
  assert.equal(manifest.formal_standard_change, false);
});

test("publishes seven schema files whose digests match the SDK surface manifest", async () => {
  assert.equal(manifest.schemas.length, 7);
  for (const entry of manifest.schemas) {
    const bytes = await readFile(new URL(entry.path, root));
    assert.equal(sha256(bytes), entry.sha256, entry.path);
    const schema = JSON.parse(bytes.toString("utf8"));
    if (entry.path.endsWith("project-manifest.schema.yaml")) {
      assert.match(schema.$schema, /json-schema\.org/, entry.path);
    } else {
      assert.equal(schema["x-dbios-schema-version"], "v0.1", entry.path);
    }
  }
});

test("publishes one inert synthetic example with fail-closed boundary declarations", async () => {
  const example = JSON.parse(
    await readFile(new URL("examples/synthetic-entity.json", root), "utf8"),
  );
  assert.equal(example.object_type, "ENTITY");
  assert.equal(example.entity_type, "repository");
  assert.equal(example.lifecycle_state, "PROPOSED");
  assert.equal(example.object_id, example.entity_id);
  assert.match(example.limitations.join(" "), /No real entity/);
  assert.equal(manifest.synthetic_examples[0].creates_entity, false);
  assert.equal(manifest.synthetic_examples[0].grants_permission, false);
});
