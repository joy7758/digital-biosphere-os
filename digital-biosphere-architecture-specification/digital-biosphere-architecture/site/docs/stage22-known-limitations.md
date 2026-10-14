# Stage 22 Known Limitations

Observed: 2026-08-01 (Asia/Shanghai)

## Existing image lint warnings

- Path: `app/digital-cell-page.tsx`
- Rule: `@next/next/no-img-element`
- Count: 3
- Lines observed: 137, 148, and 162

These warnings predate the Media Evidence and homepage-carousel change, do not block the build, do not affect the new pages, and are not a security finding. Stage 22 does not modify that established Digital Cell surface because the release-freeze scope permits only defects introduced by Stage 21.

Recommended follow-up: assess image loading and static-export behavior in a separate Digital Cell change, then either adopt the project image abstraction or record why the existing static `<img>` elements remain appropriate.

## Accessibility boundary

- `INDEPENDENT_WCAG_AUDIT_COMPLETED=false`
- Visual contrast and semantic behavior received local browser review only.
- Screen-reader behavior has not received an independent multi-product audit.

## Resolved in RC2

- `MOBILE_CAROUSEL_TOUCH_TARGET_LIMITATION=RESOLVED`
- At 390 CSS pixels, previous, next, and all three page selectors each measure 44 × 44 CSS pixels, with no pairwise overlap or horizontal overflow in local real-browser QA.

## Demonstration boundary

- The media-evidence scenarios are frontend-only synthetic records.
- No media upload, detector, C2PA validator, identity service, database, external API, or online review service is present.
- Local integrity and reference checks do not establish content truth, identity, legal evidence, regulatory recognition, or production readiness.

## Release boundary

- The candidate is committed and tagged only if every Stage 22 gate passes.
- Push, deployment, DNS, Nginx, cloud-server changes, and a public GitHub Release remain outside this stage.
