import assert from "node:assert/strict";
import test from "node:test";
import { serializeJsonLd } from "../app/json-ld.ts";

test("serializes JSON-LD without a script-closing sequence", () => {
  const serialized = serializeJsonLd({
    description: "</script><script>alert('xss')</script>",
  });

  assert.doesNotMatch(serialized, /</);
  assert.match(serialized, /\\u003c\/script>/);
  assert.deepEqual(JSON.parse(serialized), {
    description: "</script><script>alert('xss')</script>",
  });
});
