# Stage 22 Visual Release QA

Observed: 2026-08-01 (Asia/Shanghai)

Candidate: `redcrag.cn Media Evidence Demo RC2`

Source: local formal-mode static export generated from the Stage 22 working tree. These images are release-candidate evidence, not proof of deployment.

## Common checks

- no horizontal overflow at 1440, 768, or 390 CSS pixels;
- no clipped headings, overlapping text, hidden primary actions, or missing carousel controls;
- the three demo scenarios remain distinguishable by selected tab, heading, written state, and result text;
- the media-evidence boundary appears at the top of both the industry and demo surfaces;
- no private local path, key, customer data, debug notice, or unapproved third-party mark is visible;
- the carousel stage keeps a stable layout while slides change;
- at 390 CSS pixels, all five carousel controls measure 44 × 44 CSS pixels, do not overlap, and fit within the viewport;
- at 768 CSS pixels, arrows measure 44 × 44 and page selectors measure 58 × 44 CSS pixels without overlap.

## Screenshot review

| Screenshot | Page and state | Viewport | Result | Known limitation |
|---|---|---:|---|---|
| `01-home-desktop.png` | `/`, overall infrastructure slide | 1440 × 1000 | PASS | Full-page capture is taller than the viewport by design. |
| `02-home-tablet.png` | `/`, selected medical-evidence slide | 768 × 1024 | PASS | Third slide is selected to expose the complete tablet carousel state. |
| `03-home-mobile.png` | `/`, overall infrastructure slide | 390 × 844 | PASS | Mobile touch-target limitation is `RESOLVED`; all five controls are 44 × 44 CSS pixels. |
| `04-media-industry-desktop.png` | `/industry/media-evidence/` | 1440 × 1000 | PASS | Long page captured in full; individual text appears smaller in the overview image. |
| `05-media-industry-mobile.png` | `/industry/media-evidence/` | 390 × 844 | PASS | Full-page evidence is intended for QA, not presentation use. |
| `06-media-demo-lifecycle.png` | `/demo/media-evidence/`, normal lifecycle | 1440 × 1000 | PASS | All states are local synthetic records. |
| `07-media-demo-conflict.png` | `/demo/media-evidence/`, evidence conflict | 1440 × 1000 | PASS | Conflict state is governance data, not a truth decision. |
| `08-media-demo-tamper.png` | `/demo/media-evidence/`, tamper detection | 1440 × 1000 | PASS | Hash mismatch only demonstrates byte inconsistency. |
| `09-home-no-javascript.png` | `/`, JavaScript disabled | 1440 × 1000 | PASS | Interactive slide changes are unavailable by design; the complete first slide remains visible. |
| `10-home-reduced-motion.png` | `/`, reduced motion, after 8.5 seconds | 1440 × 1000 | PASS | Static image alone cannot prove elapsed time; the browser assertion is recorded in the accessibility review. |

## SHA-256

```text
adc322c2e8b44216509be2092ab2f5a6cd1dfad6aacd3c6ed574b67bb45216b0  01-home-desktop.png
da1495cd8cbc265b587c10790ac668b3404aa7ff7bc0354b42ab05a63a2055cd  02-home-tablet.png
914616ceace37976b2119ab8315a6d115f27262bcf85c5478e1a07764dc3b8eb  03-home-mobile.png
eadadcafeceff03c9f1fdbd3275bb041e9f7209d2413b3bac550fe093fb27e7b  04-media-industry-desktop.png
95b8ca967cf74830c662863d41e875a21f301d603a6e78e68348163c222719f3  05-media-industry-mobile.png
9e0cf58d93e89cdb9f7af74fa3f3dddd39021670fc3e0a0624c4a37dd9dc21ad  06-media-demo-lifecycle.png
7c4b857f8c92b506b6b3d865815b96834a39975a04b781ccc8138268365028ad  07-media-demo-conflict.png
708f9e0226d6cc86715ed67cfd049ee68cbcf8917263c911232d8b989fcac759  08-media-demo-tamper.png
adc322c2e8b44216509be2092ab2f5a6cd1dfad6aacd3c6ed574b67bb45216b0  09-home-no-javascript.png
8ea6c322bd1e265ae14023800e577cf4524f7a2070e2c48abf069a5ade87e687  10-home-reduced-motion.png
```

```text
VISUAL_RELEASE_BLOCKER=false
SCREENSHOT_COUNT=10
```
