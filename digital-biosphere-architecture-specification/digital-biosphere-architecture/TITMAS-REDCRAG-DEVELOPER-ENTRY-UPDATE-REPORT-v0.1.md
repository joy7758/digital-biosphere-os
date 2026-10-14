---
report_id: TITMAS-REDCRAG-DEVELOPER-ENTRY-UPDATE-v0.1
status: PASS_DEPLOYED_WITH_RECORDED_LIMITATIONS
observed_at: 2026-07-29T23:00:00+08:00
public_site: https://redcrag.cn/
---

# TITMAS redcrag.cn Developer Entry and Machine Truth Update Report v0.1

## Outcome

The bilingual TITMAS developer entry and the machine-readable current-state
surfaces were updated on the existing `redcrag.cn` static site. The change used
the existing Git repository, existing Baidu Cloud host, existing immutable
release layout, and existing Nginx configuration.

```text
REDCRAG_TITMAS_DEVELOPER_ENTRY_CURRENT=true
REDCRAG_MACHINE_TRUTH_CURRENT=true
REDCRAG_PUBLIC_TRIAL_INTEREST_ENTRY_ACTIVE=true
REDCRAG_EXISTING_BAIDU_DEPLOYMENT_UPDATED=true

CHATGPT_SITES_USED=false
NEW_HOSTING_PROVIDER_USED=false
DNS_CHANGED=false
CERTIFICATE_CHANGED=false
```

No secret, private key, server password, GitHub token, cloud credential, SSH
alias, server address, or private absolute path is recorded in this report.

## Source and review binding

| Field | Value |
|---|---|
| `source_repository` | `joy7758/digital-biosphere-architecture-specification` |
| `source_main_before` | `95aaf27aebb331c169c5d287d61b5de237c2cc5b` |
| `feature_branch` | `codex/redcrag-titmas-developer-entry-update-v0-1` |
| `pull_request` | `#55` |
| `reviewed_head` | `82567592811170c554988af17e4ee3bf6d6bc54a` |
| `merge_commit` | `3cb3599123d79f56d879c474f40dcb3816b765bf` |
| `exact_reviewed_head` | `true` |
| `ci` | `PASS` |
| `unresolved_review_threads` | `0` |

The merge was guarded by the exact reviewed head SHA. No Release, Tag, DNS,
certificate, hosting-provider, Runtime, production API, commercial-access,
certification, standard-adoption, or community-establishment action was
created.

## Developer entry

The Chinese and English entry points now provide:

- one explicit non-binding private-trial interest CTA;
- `Invite-only`, `Non-binding interest`, and `No automatic repository access`
  boundaries;
- a seven-step developer path from discovery through Human Maintainer
  disposition;
- a clear separation between public-safe resources and scoped-trial resources;
- a five-minute local validation path;
- an exact public-safe wheel, seven schema files, and one inert synthetic
  example;
- explicit non-equivalence rules for Conformance, Evidence, Evaluation,
  Recommendation, Decision, and Execution.

The public-safe wheel is byte-for-byte identical to the previously approved
artifact:

```text
wheel_sha256=edf92e548860384b1416a612a7e319e0d994bb324f8621847d0d154624ae8f09
wheel_bytes=45115
schema_count=7
synthetic_example_count=1
synthetic_example_validation=PASS
```

This mirror and schema projection do not create a public protocol release,
formal standard change, Entity, Agent, Runtime, Permission, or production
authority.

## Machine truth

The homepage, English homepage, Chinese and English status pages, `llms.txt`,
`agent-index.json`, `status.json`, and `agent-customer-package.json` agree on:

```text
CURRENT_CORE_REPOSITORY_VISIBILITY=PRIVATE
PUBLIC_CORE_CLONE_AVAILABLE=false
CURRENT_STAGE=TITMAS_STAGE_5_2_EXTERNAL_DEVELOPER_TRIAL

E01_STATUS=IN_PROGRESS_WAITING_FOR_PARTICIPANT_ACTION
E01_PARTICIPANT_ACCESS_AUTHORIZED=true
E01_PARTICIPANT_ACCESS_ACTIVE=true
E01_CORE_REPOSITORY_ACCESS=false
E01_CONTRIBUTION_PATH=PRIVATE_FORK_PULL_REQUEST
FIRST_EXTERNAL_HUMAN_DEVELOPER_TRIAL_COMPLETE=false

PUBLIC_TRIAL_INTEREST_ENTRY_ACTIVE=true
NEW_EXTERNAL_PARTICIPANT_INVITATION_AUTHORIZED=false
NEXT_TRIAL_SLOT_AUTHORIZED=false

PUBLIC_PROTOCOL_RELEASED=false
FORMAL_STANDARD_CHANGE_AUTHORIZED=false
COMMERCIAL_ACCESS_GRANTED=false
TITMAS_COMMUNITY_ESTABLISHED=false
COMMERCIAL_ECOSYSTEM_ESTABLISHED=false
PRODUCTION_READY=false
```

```text
MACHINE_TRUTH_CONSISTENCY_TESTS=10/10_PASS
```

## Validation

| Check | Result |
|---|---|
| Site test suite | `40/40 PASS` |
| Machine truth consistency | `10/10 PASS` |
| Formal static export | `PASS` |
| Lint | `PASS` |
| Local links | `132 PASS` |
| JSON parsing | `PASS` |
| Nginx security-header contract | `PASS` |
| Unknown-route fail-closed check | `PASS` |
| Production dependency audit | `0 vulnerabilities` |
| Development dependency audit | `9 high findings` |
| Qwen developer recommendation after remediation | `YES` (advisory only) |

The development dependency findings are retained. They are not rewritten as
zero and do not affect the production static dependency audit result.

## Disclosure scan

The exact generated static output passed:

```text
PRIVATE_REPOSITORY_URL_FINDINGS=0
SERVER_INFRASTRUCTURE_DISCLOSURE_FINDINGS=0
SECRET_FINDINGS=0
PRIVATE_PATH_FINDINGS=0
CORE_SOURCE_DISCLOSURE_FINDINGS=0
CUSTOMER_DATA_FINDINGS=0
```

The same private-repository and infrastructure patterns were absent in two
post-deployment online-content scans.

## Deployment

| Field | Value |
|---|---|
| `deployment_source_commit` | `3cb3599123d79f56d879c474f40dcb3816b765bf` |
| `release_manifest_sha256` | `195563e852d4791054f7a08c09eff9e1a5cd8e04c834997718d8d2f4ed969326` |
| `release_manifest_files` | `32` |
| `archive_sha256` | `335015036930b3b6d3a248306280f47bd558a05aec10e178cb6e59ef7d321400` |
| `previous_release` | `3b002fe37ba4c456baab8f6bf52f1576d243a1cb--818821a95974d463c1decd31aaace0d2e13463b915978cf0b9f85e775b521183` |
| `new_release` | `3cb3599123d79f56d879c474f40dcb3816b765bf` |
| `rollback_target` | previous release retained |
| `on_host_manifest` | `32/32 PASS` |
| `nginx_validation` | `PASS` |
| `nginx_active` | `true` |
| `deployment_result` | `PASS` |
| `rollback_executed` | `false` |

The new release was uploaded to a new immutable directory. The existing
`current` pointer changed only after manifest verification and `nginx -t`
passed. The previous release remains available as the rollback target.

## Online verification

Every route below returned final HTTP `200`, the expected Content-Type, and a
SHA-256 matching the deployed release manifest:

| Route | SHA-256 |
|---|---|
| `/` | `1f38ec50ac250f7d6b5d2a59e948cbeaec70e95b0bfd1dbed87e966ecf56ede5` |
| `/en` | `4bdba6c96f1e35e64e933fce93b64037d2754ed644fe51dc1c9d5dc6a44fb38e` |
| `/status` | `706b3266cde001deb3d5e18c1e7987b68eea3ce1d9ea059acfc74b0ce94760c9` |
| `/en/status` | `1fcbef2ab2b9796a3fc9979b00e99d0974bfaa35a9d83c3e42b1564bb083b587` |
| `/llms.txt` | `51e244759a7455d62effb0a5ad4a02dfb48da77bbd11f9bfd7ad7aa71119872c` |
| `/agent-index.json` | `67e8fcce83a790730cc242104a0a3f46e462ef9ad4e99dd42ba7d54a782c3ee1` |
| `/status.json` | `472a4130b8735d8a8cd2b2fab345e64cccbf099c9c34d1ccd5ef0c06d51a064a` |
| `/agent-customer-package.json` | `eb5f67f4ea946efa21c678377f8651675974d63fa91e13c0a87d9659a59a3af9` |
| `/sdk/v0.1/manifest.json` | `f52fcad6b4382aef297f19dacea26149a74f438145ba9a23a871165a2f8576a8` |
| `/sdk/v0.1/examples/synthetic-entity.json` | `01ff215ec90e48c8ce720a8c7c0fb54614ce11190803bf91d7cf35d15fd9578f` |
| public-safe wheel | `edf92e548860384b1416a612a7e319e0d994bb324f8621847d0d154624ae8f09` |

```text
HTTP_STATUS=200
HTTPS_VALID=true
CONTENT_TYPE_CORRECT=true
SECURITY_HEADERS_PRESENT=true
MACHINE_RESOURCES_PARSE=true
TRIAL_APPLICATION_LINK_WORKS=true
ONLINE_CONTENT_HASH_MATCH=PASS
CACHE_RECHECK_COMPLETE=true
```

One transient TLS connection error occurred during the second pass. The bounded
retry succeeded with identical content hashes. This observation is retained and
was not treated as a content failure or a reason to redeploy.

## Limitations and next decision

- E01 remains in progress and has not produced a participant Fork, Pull
  Request, Conformance result, Human Disposition, or completed trial.
- The public-safe surface validates bounded object contracts; it is not a
  public Runtime or complex multi-agent execution environment.
- Sandbox and broader specification access remain scoped-trial resources.
- Developer Preview schemas may evolve; no stability or production
  compatibility promise is created.
- Core implementation remains private; the public surface is auditable only
  within its declared contracts and digests.
- The next decision is to observe E01 participant action. It does not authorize
  a second active trial slot.

## TITMAS Drift Check

```text
TITMAS_DRIFT_CHECK

CANONICAL_WEBSITE=redcrag.cn
CANONICAL_WEBSITE_SOURCE=existing_Git_repository
CANONICAL_HOSTING=existing_Baidu_Cloud

CHATGPT_SITES_USED=false
DUPLICATE_WEBSITE_CREATED=false
NEW_DEPLOYMENT_AUTHORITY_CREATED=false

PUBLIC_WEBSITE_UPDATE_NE_PUBLIC_PROTOCOL_RELEASE=true
TRIAL_INTEREST_NE_TRIAL_AUTHORIZATION=true
E01_IN_PROGRESS_NE_E01_SUCCESS=true
RECRUITMENT_SUBMITTED_NE_DEVELOPER_HIRED=true

CORE_REPOSITORIES_PRIVATE=true
PUBLIC_EXPORT_LIMITED_TO_APPROVED_WEBSITE_CONTENT=true

TITMAS_DRIFT_CHECK_RESULT=PASS_WITH_RECORDED_LIMITATIONS
```
