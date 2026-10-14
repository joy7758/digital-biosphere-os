---
document_id: TITMAS-STAGE-5-1-PRIVATE-EXTERNAL-DEVELOPER-TRIAL-CHANNEL-REPORT-1.0
title: TITMAS Stage 5.1 Private External Developer Trial Channel Report v1.0
title_zh: TITMAS Stage 5.1 私有外部开发者试用通道报告 v1.0
status: complete-with-recorded-limitations
maturity: Development
normative: false
owner_ref: zhangbin
decision_reference: TITMAS-STAGE-5-1-PRIVATE-EXTERNAL-DEVELOPER-TRIAL-CHANNEL-D01
---

# TITMAS Stage 5.1 Private Trial Channel Report

## Repository facts

```text
CORE_REPOSITORY=joy7758/digital-biosphere-architecture-specification
CORE_REPOSITORY_VISIBILITY=PRIVATE
PRIVATE_CORE_IS_CANONICAL=true

TRIAL_REPOSITORY=joy7758/titmas-private-developer-trial
TRIAL_REPOSITORY_VISIBILITY=PRIVATE
TRIAL_REPOSITORY_DEFAULT_BRANCH=main
TRIAL_REPOSITORY_IS_FORK=false
TRIAL_REPOSITORY_ROOT_COMMIT=cb824621189262c4e4bc9f12840f1de08d615cb9
TRIAL_REPOSITORY_SOURCE_COMMIT=6ff89d355205fb19ace46dc9b7d706bb562af87b
GIT_HISTORY_COPIED=false
PUBLICATION_BY_RECONSTRUCTION=true
ALLOWLIST_ONLY_EXPORT=true
```

The separate trial repository contains 30 files, including the
`trial-source-manifest.json` self record. Each file is bound to a source
repository, source commit, source path, source blob, classification, trial
path, output SHA-256 and review status. No unmanifested file is allowed.

## Programmatic clean-clone trial

The internal controller clean-cloned the actual private trial repository,
created a new virtual environment, installed the generated dependency-free
wheel without network package resolution, read the machine entry, discovered
three tasks and selected `TRIAL-01-NEGATIVE-TEST-VECTOR`.

It submitted one schema-valid negative Test Vector to the existing loopback
Stage 5 Sandbox. Canonical Conformance returned `CONFORMANCE_PASS` and required
Human disposition. A second vector removed the required negative failure
classification and failed closed with HTTP 422. One uncommitted, unpushed Pull
Request fixture was prepared and deleted with the temporary directory.

```text
PRIVATE_TRIAL_CLEAN_CLONE=PASS
TRIAL_SDK_INSTALL=PASS
TRIAL_TASK_DISCOVERY=PASS
TRIAL_CONTRIBUTION_PREFLIGHT=PASS
TRIAL_SANDBOX_SUBMISSION=PASS
TRIAL_CONFORMANCE_RESULT=PASS
INVALID_TEST_VECTOR=CONFORMANCE_FAIL
CORE_ACCESS_COUNT=0
REAL_MODEL_CALL_COUNT=0
REAL_PROVIDER_CALL_COUNT=0
```

Evidence:
`TITMAS/private-stage5-1-trial/programmatic-clean-clone-report.json`.

## Security and export findings

```text
TRIAL_REPOSITORY_CORE_SOURCE_FINDINGS=0
TRIAL_REPOSITORY_SECRET_FINDINGS=0
TRIAL_REPOSITORY_PRIVATE_PATH_FINDINGS=0
TRIAL_REPOSITORY_PROVIDER_CONFIGURATION_FINDINGS=0
TRIAL_REPOSITORY_GIT_HISTORY_FINDINGS=0
TRIAL_REPOSITORY_SYMLINK_FINDINGS=0
UNAUTHORIZED_EXPORT_COUNT=0
```

No core implementation, internal test, private governance, customer data,
production Evidence, Provider configuration, credential, hidden answer,
response-capture implementation or semantic-checkpoint implementation was
exported. The formal Specification Registry was not changed.

The website production dependency audit returned zero vulnerabilities. The
full development-toolchain audit reported nine high-severity transitive
findings in the ESLint/minimatch/brace-expansion chain. Available automatic
remediation requires major-version changes and is outside this bounded Goal.
No Release or Deployment is authorized; the finding remains recorded rather
than silently rewritten as zero.

```text
PRODUCTION_DEPENDENCY_AUDIT=0_VULNERABILITIES
DEVELOPMENT_TOOLCHAIN_AUDIT=9_HIGH
DEVELOPMENT_TOOLCHAIN_REMEDIATION=DEFERRED_MAJOR_VERSION_REVIEW_REQUIRED
```

## Local validation summary

```text
CANONICAL_CONFORMANCE=PASS
PYTHON_TEST_DOMAINS=8
PYTHON_TESTS=167/167_PASS
SITE_BUILD=PASS
SITE_TESTS=22/22_PASS
SITE_LINT=PASS
JSON_ASSETS_PARSED=104
YAML_ASSETS_PARSED=14
LICENSE_SCAN=PASS
GIT_DIFF_CHECK=PASS
PRODUCTION_DEPENDENCY_AUDIT=0_VULNERABILITIES
```

## Pull Request review remediation

Three P1 findings from the automated PR review were reproduced and closed:

1. directory symlinks are now counted and rejected before file filtering;
2. reconstruction now requires an existing 40-character Git commit and verifies
   every copied source plus the Builder itself against the blob at that commit;
3. each sanitized Stage 5 checkpoint now carries a recomputable payload hash,
   the audit binds all three hashes, and payload tampering fails closed.

The remediation added three Stage 5.1 negative tests and one Stage 5 audit
tamper test. It did not execute another Agent or Provider call.

```text
P1_REVIEW_FINDINGS=3
P1_REVIEW_REMEDIATIONS=3
STAGE5_1_TESTS=8/8_PASS
STAGE5_PILOT_TESTS=7/7_PASS
REAL_MODEL_CALL_COUNT=0
REAL_PROVIDER_CALL_COUNT=0
```

## Branch protection

After the GitHub Pro entitlement became active, the required protection was
configured and read back from the live repository:

```text
BRANCH_PROTECTION_VERIFIED=true
DEFAULT_BRANCH_DIRECT_PUSH_BLOCKED=true
FORCE_PUSH_BLOCKED=true
BRANCH_DELETION_BLOCKED=true
PULL_REQUEST_REQUIRED=true
OWNER_REVIEW_REQUIRED=true
REQUIRED_APPROVING_REVIEW_COUNT=1
REQUIRE_LAST_PUSH_APPROVAL=true
DISMISS_STALE_REVIEWS=true
REQUIRED_CONVERSATION_RESOLUTION=true
REQUIRED_LINEAR_HISTORY=true
STATUS_CHECKS_REQUIRED=true
REQUIRED_STATUS_CHECK=trial-conformance
TRIAL_REPOSITORY_INVITATION_READY=true
BLOCK_REASON=NONE
```

The initial root commit has one successful `trial-conformance` status. Technical
invitation readiness does not authorize or send an invitation. The Human Owner
must still approve a real participant-specific packet.

## Current gates

`TITMAS_STAGE_5_1_PRIVATE_TRIAL_CHANNEL_READY=true` means the separate private
package, machine entry, local client, existing Sandbox integration and internal
clean-clone validation are ready. It does not mean that an external invitation
is safe or authorized.

```text
TITMAS_STAGE_5_1_PRIVATE_TRIAL_CHANNEL_READY=true
TITMAS_PRIVATE_TRIAL_REPOSITORY_READY=true
TITMAS_EXTERNAL_DEVELOPER_TRIAL_PACKAGE_READY=true
TITMAS_EXTERNAL_INVITATION_DECISION_PACKET_READY=true

TRIAL_REPOSITORY_INVITATION_READY=true
EXTERNAL_PARTICIPANT_INVITATION_AUTHORIZED=false
EXTERNAL_DEVELOPER_TRIAL_EXECUTED=false
PUBLIC_EXPORT_AUTHORIZED=false
PUBLIC_PROTOCOL_RELEASED=false
FORMAL_STANDARD_CHANGE_AUTHORIZED=false
COMMERCIAL_ACCESS_GRANTED=false
TITMAS_COMMUNITY_ESTABLISHED=false
COMMERCIAL_ECOSYSTEM_ESTABLISHED=false
```

## Drift Check

```text
PRIVATE_CORE_IS_CANONICAL=true
EXTERNAL_DEVELOPER_CORE_ACCESS=false
TRIAL_REPOSITORY_IS_SEPARATE=true
TRIAL_REPOSITORY_IS_PRIVATE=true
TRIAL_REPOSITORY_RECONSTRUCTED_FROM_ALLOWLIST=true
DEVELOPER_RECEIVES_STANDARD_SDK_EXAMPLES_AND_TASKS=true
DEVELOPER_RECEIVES_CORE_SOURCE=false
TRIAL_ACCESS_NE_SOURCE_LICENSE=true
TRIAL_CONTRIBUTION_NE_STANDARD_ADOPTION=true
PUBLIC_EXPORT_EXECUTED=false
REAL_MODEL_CALLED=false
NEW_CONTROL_AUTHORITY_CREATED=false
NEW_TRUTH_SOURCE_CREATED=false
NEW_RUNTIME_CREATED=false
COMMUNITY_ESTABLISHED_OVERCLAIMED=false
COMMERCIAL_ECOSYSTEM_OVERCLAIMED=false
TITMAS_DRIFT_CHECK_RESULT=PASS_WITH_RECORDED_LIMITATIONS
```
