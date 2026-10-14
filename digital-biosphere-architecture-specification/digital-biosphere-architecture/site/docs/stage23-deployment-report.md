# Stage 23 Media Evidence RC2 Deployment Report

Observed: 2026-08-01 (Asia/Shanghai)

Scope: authorized push, immutable deployment, live verification, real rollback drill, and RC2 restoration for `https://redcrag.cn`.

## Authorization and source

```text
AUTHORIZED_BY=zhangbin
AUTHORIZED_ACTIONS=PUSH_AND_DEPLOY_RC2
AUTHORIZED_SOURCE_REVISION=800a3523eab8f3f35295207f4df636dbadf347bf
AUTHORIZED_TAG=redcrag-media-evidence-rc2
PUBLIC_GITHUB_RELEASE_AUTHORIZED=false
DNS_CHANGE_AUTHORIZED=false
NGINX_CONFIG_CHANGE_AUTHORIZED=false
SERVER_PATCH_AUTHORIZED=false
```

- Local deployment source: `800a3523eab8f3f35295207f4df636dbadf347bf`
- Remote `main` after source push: `800a3523eab8f3f35295207f4df636dbadf347bf`
- Remote RC1 peeled commit: `61b3cc93e00b664eb93b5cccc5bcf52656ae2c08`
- Remote RC2 peeled commit: `800a3523eab8f3f35295207f4df636dbadf347bf`
- The source push was a normal fast-forward. No force push, merge, rebase, or reset was used.
- The GitHub release-by-tag API returned HTTP 404 for `redcrag-media-evidence-rc2` after deployment; no public GitHub Release exists for the tag.
- GitHub HTTPS transport failed during the preflight. Existing authenticated GitHub SSH transport on port 443 was used without changing the repository remote configuration.

## Formal build evidence

```text
LINT_ERRORS=0
PRE_EXISTING_DIGITAL_CELL_WARNINGS=3
TESTS_TOTAL=54
TESTS_PASS=54
STATIC_EXPORT_PASS=true
ZH_EN_CONTENT_PARITY_PASS=true
TRUTH_BOUNDARY_VALIDATION_PASS=true
LOCAL_LINKS_CHECKED=1648
LOCAL_LINKS=PASS
PUBLIC_OUTPUT_DISCLOSURE_SCAN=PASS
SOURCE_REVISION=800a3523eab8f3f35295207f4df636dbadf347bf
OUT_FILE_COUNT=149
MANIFEST_FILES=148
```

Release Manifest:

- schema version: `0.1`
- generated at: `2026-08-01T03:52:46.871Z`
- source revision: `800a3523eab8f3f35295207f4df636dbadf347bf`
- file entries: `148`

Local deterministic release digest:

```text
OUT_DIRECTORY_SHA256=d2e3468064d5702aa08082fbfca9bc0e81530a1324947c7f1139c2808838355a
```

Key artifact hashes:

```text
79dc71880074df1445538f01e04a03e2ae7cbfc62050a2bc640d9aa7ce0a627c  release-manifest.json
6217d713a3f8df7adfe9f3b6d1621a0ef36e15b331557e7313520f5069bd9b60  media-evidence-profile.json
b03de8f76eba9fd60d891a95aa1e3635e296c0f21b53b6ab007fa58f51965e77  agent-index.json
554c0aff8da9545d7a1e861ed80d732e0e658d5d774444639fcb95ea8959df35  site-catalog.json
1bfe7c55cdf6f8495a99f6ea0aec2dc9b5dfd05660c81d2d2431dcd2c2c3b6c8  updates.json
53a78f699a3aeda4588757882241c7710dcb554e0361a5eda4b920178c9e94d0  llms.txt
1889715202d540f357e260032ee9590212902f70fc27f94c932ac1e579f16177  sitemap.xml
```

The remote immutable directory contained 149 regular files, no symlinks, no special files, and no group- or world-writable files. Its deterministic digest and all listed artifact hashes matched the local output before activation. All JSON files parsed successfully. No file in the immutable release directory was edited on the server.

## Release layout and activation

- Previous release: `/srv/tmai/releases/ca0c634f781f977b8637a6f47031dadb986d6a7b--c2d1e160f84e06982ccb218d95e6423bdc37a1b9558fa79112e028399b2f0961`
- Previous source revision: `ca0c634f781f977b8637a6f47031dadb986d6a7b`
- RC2 release: `/srv/tmai/releases/800a3523eab8f3f35295207f4df636dbadf347bf`
- Initial RC2 switch: `2026-08-01T11:55:50+08:00`
- Final `current` target: `/srv/tmai/releases/800a3523eab8f3f35295207f4df636dbadf347bf`

`nginx -t` passed before release finalization, before every symlink switch, and before every reload. No DNS record, Nginx configuration, server package, source file, or immutable release file was modified.

## Live health verification

The following 15 live resources returned HTTP 200 with no redirect loop after initial activation and again after RC2 restoration:

- `/`
- `/en/`
- `/applications/`
- `/demos/`
- `/industry/media-evidence/`
- `/en/industry/media-evidence/`
- `/demo/media-evidence/`
- `/en/demo/media-evidence/`
- `/media-evidence-profile.json`
- `/agent-index.json`
- `/site-catalog.json`
- `/updates.json`
- `/llms.txt`
- `/sitemap.xml`
- `/release-manifest.json`

Checks passed:

- Chinese and English pages were reachable.
- The homepage contained all three carousel records and kept the TITMAS overview as the first record.
- The media-evidence industry and demo pages were reachable.
- Normal lifecycle, evidence conflict, and tamper-detection scenarios were independently selectable.
- Machine-readable JSON parsed successfully.
- `truth_verification`, `identity_authentication`, `legal_evidence`, and `production_ready` remained `false`.
- The live Release Manifest reported the authorized RC2 source revision and 148 file entries.
- Canonical links and Open Graph metadata were present on the checked HTML pages.
- No private local path, private-key marker, configured API-key name, customer data, or release-boundary drift was detected.

## Machine discovery

The restored RC2 was discoverable through:

- `/llms.txt`
- `/agent-index.json`
- `/site-catalog.json`
- `/updates.json`
- `/media-evidence-profile.json`

Together these resources expose the project name, industry, current reference status, application page, demo page, synthetic-data policy, and the explicit boundaries for truth verification, identity authentication, legal evidence, and production readiness.

## Security response headers

All 15 checked resources retained:

- `Strict-Transport-Security`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Referrer-Policy`
- `Permissions-Policy`
- `Content-Security-Policy`

This check records header presence and release continuity. It is not a security certification or a guarantee against all attacks.

## Browser verification

Real-browser checks were run after initial activation and repeated after the rollback restoration.

| Check | Result |
|---|---|
| Desktop 1440 × 1000 | PASS; no horizontal overflow; five homepage sections; carousel controls at least 44 × 44 CSS pixels. |
| Tablet 768 × 1024 | PASS; no horizontal overflow or control overlap; arrows 44 × 44 and selectors 58 × 44. |
| Mobile 390 × 844 | PASS; no horizontal overflow or control overlap; all five controls 44 × 44. |
| No JavaScript | PASS; one complete first slide remained visible. |
| Reduced motion | PASS; the first slide remained active after 8.5 seconds. |
| Normal automatic advance | PASS; the second slide was active after 8.5 seconds. |
| Keyboard left/right | PASS. |
| Pause after user action | PASS. |
| Pause on focus and hover | PASS. |
| Focus visibility | PASS; a 3-pixel outline remained visible. |
| Demo scenario switching | PASS for all three synthetic scenarios. |
| Browser console | 0 errors in the checked contexts. |

## Real rollback drill

- Rollback switch to previous release: `2026-08-01T11:59:12+08:00`
- Previous-version health verification: `2026-08-01T11:59:12+08:00`, PASS
- Restore switch to RC2: `2026-08-01T11:59:12+08:00`
- Restored RC2 health verification: `2026-08-01T11:59:12+08:00`, PASS
- Historical release directories were preserved.
- RC2 remained immutable during the drill.
- Complete HTTP and browser checks were rerun after restoration.

## Known limitations and claim boundary

- `INDEPENDENT_WCAG_AUDIT_COMPLETED=false`
- No independent multi-screen-reader or instrumented contrast audit was performed.
- Three established `digital-cell-page.tsx` image lint warnings remain outside this release scope.
- Media-evidence surfaces remain local synthetic reference surfaces. They do not prove content truth, authenticate identity, constitute legal evidence, demonstrate external-standard certification, guarantee security, or establish production-review capability.
- Deployment health does not upgrade these capability boundaries.

## Recorded status

```text
PUSHED=true
DEPLOYED=true
HEALTH_CHECK_PASS=true
ROLLBACK_VALIDATED=true
PUBLIC_GITHUB_RELEASE_CREATED=false
DNS_CHANGED=false
NGINX_CONFIG_CHANGED=false
SERVER_PATCHED=false
FINAL_STATUS=DEPLOYED_AND_ROLLBACK_VALIDATED
```
