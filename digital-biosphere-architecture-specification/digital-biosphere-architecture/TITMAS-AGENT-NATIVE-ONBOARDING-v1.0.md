# TITMAS Agent-Native Onboarding v1.0

## Status

```text
ONBOARDING_CONTRACT_DEFINED=true
ONBOARDING_IMPLEMENTED=false
PUBLIC_REGISTRATION_ENABLED=false
EXTERNAL_CREDENTIAL_ISSUANCE_ENABLED=false
HTML_UI_REQUIRED=false
```

## Intended machine flow

```text
discover
-> inspect service status
-> inspect capabilities and plans
-> obtain a delegated scoped credential
-> inspect schemas
-> execute preflight
-> verify receipt
-> inspect quota
-> reuse in a second task
```

The current phase uses only internally authorized synthetic tenants. Public
Agent self-registration and public credential issuance are not authorized.

## Discovery contract

An Agent starts with the origin and reads, in order:

1. `/.well-known/titmas.json`;
2. `/api/v1/status`;
3. `/api/v1/capabilities`;
4. `/api/v1/plans`;
5. `/api/v1/openapi.json`.

The documents must expose:

- service and API identity;
- exact maturity state;
- authentication and scope method;
- schema catalog;
- limits and unsupported operations;
- receipt verification profile;
- SDK and adapter locations;
- explicit authority non-claims.

HTML must not contain a capability unavailable to machine clients, except a
Human safety stop or irreversible commercial decision.

## Credential handoff

The Contracting Principal or a separately scoped management Agent creates a
credential through an offline or protected control-plane process. The
operational Agent receives:

```text
base_url
credential_id
one-time plaintext credential
tenant_id
agent_id
scopes
expires_at
```

The plaintext is never emitted into Git, issue trackers, logs, receipts,
provider prompts or public documentation.

## First call

The client generates:

```text
request_id
idempotency_key
schema_id
schema_version
object
```

The server derives tenant, Agent and credential identity from authenticated
state. It rejects any contradictory client identity fields.

The response preserves one of:

```text
PASS
FAIL
NOT_ASSESSED
```

and returns a receipt reference. `FAIL` and `NOT_ASSESSED` are valid bounded
outcomes and must not be rewritten to success.

## Receipt verification

The Agent obtains the public verification key from a versioned machine entry,
verifies the canonicalized receipt and checks:

- expected service identity and receipt version;
- request and response digests;
- tenant and Agent binding;
- signature;
- optional chain link;
- explicit `formal_conformance=false`, `certification=false`,
  `truth_claim=false` and `authorization_effect=false`.

Verification does not prove the customer's source object or scientific claim
is true.

## Repeat-use event

A second task must create a new request and idempotency key. Adoption is not
recorded until one independent Agent:

1. discovered through a machine entry;
2. used a delegated scoped credential;
3. completed a protected call;
4. verified the receipt;
5. reused TITMAS in another task;
6. used it at three separate timestamps.

## SDK behavior

Python, TypeScript, MCP and framework adapters must:

- use bounded timeouts;
- retry only safe/idempotent operations;
- reuse the same idempotency key for a protected retry;
- surface scope and quota failures;
- preserve `NOT_ASSESSED`;
- support offline receipt verification;
- never label a receipt as certification.

## Current limitation

A bounded `/api/v1` implementation and internal synthetic credential workflow
exist. Public self-registration, externally delegated commercial credentials,
validated public-safe commercial SDK/Adapters and external Agent Beta do not
exist. CR-01 is also blocked on restored historical Receipt integrity, so the
implemented candidate is not Commercial Technical Ready or Production Ready.
