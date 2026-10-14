# TITMAS Asset Classification v0.1

Observed at: `2026-08-03`

Status: `SOURCE_PINNED_WHERE_AVAILABLE_OTHERWISE_NOT_ASSESSED`

This register classifies portfolio role. It does not change repository
visibility, ownership, maturity, Authority or implementation truth.

| repository or asset | canonical role / truth owner | private domain | public mapping | solution | type | visibility | maturity | disposition | duplicate risk / limitations |
|---|---|---|---|---|---|---|---|---|---|
| `joy7758/digital-biosphere-architecture-specification` | DBA governance and architecture | none | governance reference | all | normative governance | private | active cockpit | retain | not Runtime or product core |
| `joy7758/agent-evidence` | execution-evidence semantics / repository | Evidence and Provenance | Receipt, Audit input | all | implementation | private | candidate | retain | unique evidence semantic source; Evidence is not Truth |
| `joy7758/titmas-sandbox-gateway` | bounded Gateway candidate / repository | Gate and shared controls | no public engine source | software delivery | implementation | private | P0 candidate with retained failures | freeze | no production access; D04 and P0-10 remain closed |
| `joy7758/titmac-scout` | discovery and bounded evolution / repository | supporting discovery | none | all | implementation candidate | private | D27 merged negative evidence | retain | not executor authority; one real ER-1, zero real self-evolution |
| `joy7758/titmas-agent-safety-signal-relay` | auxiliary safety-signal reference / repository | Health reference | Health reference only | all | non-normative pilot | private | frozen | freeze | branch `ecb8000…`; tag resolves to older `6bcebcd…` and is not an exact head attestation |
| `joy7758/aro-audit` | accountability and audit candidate / repository | Audit and Replay | Audit | all | implementation candidate | private | not assessed | retain | possible overlap with DBOS Verification and Agent Evidence |
| local `execution_audit_sdk` | execution-audit SDK material / unknown | Audit and Replay | Audit reference | software delivery | local asset | local only | not assessed | defer | no canonical Git source observed |
| local `pra-server` | research pulse server material / local repository | none | none | research | application | local only | not assessed | defer | no remote observed; not a product core |
| `joy7758/persona-object-protocol` | portable persona projection / repository | Identity adjacent | none | all | draft protocol | public | draft | retain | not canonical DBOS identity authority |
| `joy7758/agent-object-protocol` | portable agent object draft / repository | Adapter adjacent | none | all | draft protocol | public | draft | defer | Agent Object is not Entity Identity or Permission |
| `joy7758/verifiable-agent-demo` | execution-evidence walkthrough / repository | none | proof reference | software delivery | demo | public | demo | retain | Demo is not production proof |
| `joy7758/verifiable-tool-invocation-flow` | signed tool-call flow / repository | Gate, Receipt adjacent | proof reference | software delivery | reference implementation | private | candidate | retain | not a production Gateway or Authority |
| `joy7758/agent-health` and local variants | health probe/normalizer candidate / repository | Health and Evaluation | Health reference | all | implementation candidate | private | not assessed | freeze | not a repository fixer, control plane or certification system |
| `joy7758/titmas-media-guard` | media evidence application profile / repository | shared evidence reference | Receipt, Audit, Health configuration | media evidence | private reference implementation | private | admitted adjacent candidate | retain | not standard, legal evidence or DBOS Evidence authority |
| `udi-dicom-evidence-validator` family | medical imaging evidence validation reference / repository family | Evidence and Audit mapping | Receipt, Audit | medical imaging | application/reference | mixed | not assessed | defer | no clinical decision, certification or production claim |
| precision-mold and robotics FDO assets | manufacturing data-object research / source repositories | Adapter mapping only | none | smart manufacturing | research/specification | public/mixed | not assessed | defer | no production equipment action or TITMAS core adoption |
| Space Agent Evidence materials under `agent-evidence` | space evidence profile / `agent-evidence` | Evidence and Audit mapping | Receipt, Audit, Health | autonomous space research | application profile | mixed | candidate | defer | no mission authority or external adoption |
| `joy7758/SAEE` | evolution evaluation / repository | Health and Evaluation input | Health reference | all | evolution engine | private | canonical project | retain | recommendation is not decision or execution |
| `joy7758/digital-biosphere-os` | existence governance / repository | Identity, lifecycle and evidence integration | shared private platform | all | infrastructure implementation | private | canonical project | retain | not Agent framework or public core |

Research documents, Demos, industry directions and auxiliary pilots remain in
their recorded categories and are not promoted to products by this table.
