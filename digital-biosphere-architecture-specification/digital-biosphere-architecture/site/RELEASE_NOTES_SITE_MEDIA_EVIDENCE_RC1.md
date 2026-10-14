# redcrag.cn Media Evidence Demo RC1

中文名称：redcrag.cn 媒体证据演示发布候选版 1

Type: static-site release candidate with local synthetic reference surfaces.

## Added and revised

- a three-entry homepage carousel for TITMAS infrastructure, Media Evidence, and Medical Evidence;
- homepage primary sections reduced from approximately 16 to 5 while retaining governance and status entry points;
- bilingual Media Evidence industry pages;
- bilingual frontend-only Media Evidence demonstration pages;
- normal lifecycle, evidence conflict, and tamper-detection synthetic scenarios;
- a machine-readable Media Evidence profile and synchronized agent/site catalogs;
- static export, route, disclosure, machine-boundary, reduced-motion, and no-JavaScript checks;
- ten release-candidate screenshots;
- Chinese-first labels for Stage 21 headings and technical terms.

## Verification snapshot

```text
LINT_ERRORS=0
LINT_PRE_EXISTING_WARNINGS=3
TESTS=53
TESTS_PASS=53
STATIC_FILES=149
STATIC_MANIFEST_FILES=148
LOCAL_LINKS_CHECKED=1648
LOCAL_LINKS=PASS
PUBLIC_OUTPUT_DISCLOSURE_SCAN=PASS
SCREENSHOTS=10
```

## Explicit boundaries

- not a production service;
- does not receive media uploads;
- does not run a real detector or real C2PA validation;
- does not authenticate content truth or subject identity;
- does not provide legal evidence;
- does not claim regulatory recognition, competition endorsement, customer adoption, investment return, external-standard compatibility, or guaranteed security.

## Known limitations

See `docs/stage22-known-limitations.md` and `docs/stage22-accessibility-review.md`.

```text
INDEPENDENT_WCAG_AUDIT_COMPLETED=false
DEPLOYED=false
PUSHED=false
PUBLIC_GITHUB_RELEASE_CREATED=false
```
