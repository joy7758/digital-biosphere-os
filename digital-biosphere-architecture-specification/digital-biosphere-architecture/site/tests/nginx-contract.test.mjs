import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const config = await readFile(
  new URL("../deploy/nginx/redcrag.cn.conf", import.meta.url),
  "utf8",
);

test("keeps the existing static-root and TLS deployment boundary", () => {
  assert.match(config, /root \/srv\/tmai\/current;/);
  assert.match(config, /ssl_certificate \/etc\/letsencrypt\/live\/redcrag\.cn\/fullchain\.pem;/);
  assert.match(config, /ssl_certificate_key \/etc\/letsencrypt\/live\/redcrag\.cn\/privkey\.pem;/);
  assert.match(config, /try_files \$uri \$uri\/ \$uri\/index\.html =404;/);
});

test("keeps all required security headers at server scope", () => {
  for (const header of [
    "Strict-Transport-Security",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "Content-Security-Policy",
  ]) {
    assert.match(config, new RegExp(`add_header ${header.replaceAll("-", "\\-")} `));
  }
});
