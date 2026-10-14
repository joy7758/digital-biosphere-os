---
document_id: TITMAS-STAGE-5-1-EXTERNAL-DEVELOPER-INVITATION-DECISION-PACKET-1.0
title: TITMAS Stage 5.1 External Developer Invitation Decision Packet v1.0
title_zh: TITMAS Stage 5.1 外部开发者邀请决策包 v1.0
status: prepared-no-invitation-authorized
maturity: Development
normative: false
owner_ref: zhangbin
decision_reference: TITMAS-STAGE-5-1-PRIVATE-EXTERNAL-DEVELOPER-TRIAL-CHANNEL-D01
---

# External Developer Invitation Decision Packet

This packet is a future Human Owner decision input. It is not an invitation,
access grant, participant record, contract, standard adoption or commercial
activation.

## Participant-specific record

Create one copy of this record per real participant. No placeholder username
may be used to send an invitation.

```yaml
participant_id: PENDING_REAL_INPUT
participant_github_username: PENDING_REAL_INPUT
participant_source: PENDING_REAL_INPUT
participant_affiliation: PENDING_REAL_INPUT
selected_trial_task: PENDING_REAL_INPUT

access_repository: joy7758/titmas-private-developer-trial
access_requested_at: null
access_expires_at: null
access_revoked_at: null

trial_acknowledgement_status: PENDING
data_scope:
  - NONCONFIDENTIAL_SYNTHETIC_STANDARD_CONTRIBUTION
allowed_operations:
  - standards:read
  - tasks:read
  - examples:read
  - sdk:use
  - proposal:prepare
  - adapter:prepare
  - test-vector:prepare
  - pull-request:create
  - feedback:submit
prohibited_operations:
  - core-source:read
  - private-governance:read
  - internal-test:read
  - secret:read
  - main:direct-push
  - standard:adopt
  - release:create
  - deployment:create
  - admin

invitation_decision: NOT_AUTHORIZED
decided_by_ref: null
```

GitHub repository permissions and Sandbox Key scopes are independent controls.
Neither implies the other.

## Required entry gates

- a real GitHub username and source are provided;
- the Human Owner approves this exact participant;
- the participant accepts
  `trial/TRIAL-PARTICIPATION-ACKNOWLEDGEMENT-v0.1.md`;
- branch protection is verified live;
- trial repository scans and the clean-clone trial remain passing;
- access expiry is set before the invitation;
- only the separate trial repository is selected.

## Suggested access cycle

```text
MAX_ACTIVE_EXTERNAL_PARTICIPANTS=1
DEFAULT_ACCESS_DURATION_HOURS=72
MAX_ACCESS_DURATION_DAYS=7
```

Human approval is followed by acknowledgement, trial-repository-only access,
one selected task, Pull Request, automated Conformance, Human Maintainer review,
access removal and participant confirmation of local clone deletion. Removing
GitHub access cannot technically delete a copy already retained by the
participant.

## Current decision state

```text
PARTICIPANT_GITHUB_USERNAME=PENDING_REAL_INPUT
EXTERNAL_PARTICIPANT_INVITATION_AUTHORIZED=false
INVITATION_SENT=false
EXTERNAL_DEVELOPER_TRIAL_EXECUTED=false
```
