# TITMAS Receipt Key Management v1.0

## Status

```text
KEY_MANAGEMENT_CONTRACT_DEFINED=true
SIGNING_KEY_GENERATED=false
PUBLIC_KEY_PUBLISHED=false
KEY_ROTATION_DRILL_PASS=false
KEY_COMPROMISE_DRILL_PASS=false
COMMERCIAL_TECHNICAL_READY=false
```

This profile governs service Receipt keys only. It is not a general identity
provider, certificate authority or customer-key custody service.

## Key profile

- algorithm candidate: Ed25519, RFC 8032;
- one `ACTIVE` signing key per service environment;
- prior public keys may remain `VERIFY_ONLY`;
- key identifier: opaque, versioned and non-secret;
- private key: never stored in Git, PostgreSQL, logs, backups in plaintext or
  model Provider input.

## Generation ceremony

1. run an offline, reviewed key-management command on the target host;
2. use the operating-system cryptographic random source through the reviewed
   cryptographic library;
3. set `umask 077`;
4. write the private key once to a root-owned file outside every release;
5. set owner to the commercial service account and mode `0600`;
6. derive the public key and fingerprint;
7. record only key ID, algorithm, public key, fingerprint, creation time and
   status in the audit record;
8. verify a sign/verify test vector before activation.

Command output must never include private key bytes.

## Storage

Initial technical candidate:

```text
PRIVATE_KEY_BACKEND=ROOT_OWNED_FILE
PRIVATE_KEY_IN_DATABASE=false
PRIVATE_KEY_IN_RELEASE=false
PRIVATE_KEY_IN_LOGS=false
PRIVATE_KEY_IN_MODEL_PROVIDER=false
```

A managed KMS or HSM is a future option requiring a new provider/cost
decision. It is not falsely claimed at this stage.

## Public-key distribution and trust

The service publishes:

```text
/.well-known/titmas-keys.json
```

Each entry contains:

```text
key_id
algorithm
public_key_encoding
public_key
fingerprint_sha256
status
not_before
not_after
```

The current HTTPS origin is the distribution trust anchor; no DNS or
certificate change is authorized. Public-safe SDK releases also pin the
expected key fingerprint for their release observation while allowing an
explicit refresh from the same origin.

## Rotation

1. generate and validate a new key;
2. publish its public key as `PENDING`;
3. atomically make it the only `ACTIVE` signer;
4. move the prior key to `VERIFY_ONLY`;
5. retain prior public keys for at least the published Receipt verification
   period;
6. securely remove the retired private key after rollback and incident needs
   have expired;
7. record the transition without changing historical Receipts.

The exact verification period is plan/data-retention input and must be frozen
before external Beta. Rotation cannot shorten an already promised period.

## Backup and recovery

The private key backup is separately encrypted, access-controlled and excluded
from normal database backup. Restoration occurs only into a restricted
environment and must prove that:

- existing Receipts verify;
- no second active signer remains;
- audit and key status are continuous.

If loss occurs without recoverable private material, create a new key and
preserve old public verification keys. Never recreate or rewrite old
signatures.

## Compromise response

1. stop signing;
2. mark the key `REVOKED_COMPROMISED`;
3. preserve the affected interval and audit evidence;
4. publish the revocation state;
5. activate a new key only after bounded review;
6. return `SIGNATURE_KEY_COMPROMISED` for affected Receipt verification;
7. do not relabel affected Receipts as trusted or re-sign them.

Compromise does not prove every historical Receipt is forged, and a valid
signature does not prove truth.

## Readiness gates

Commercial technical readiness requires:

- file ownership/mode verification;
- no-secret scan;
- sign/verify and tamper tests;
- public-key discovery test;
- rotation drill;
- loss/recovery drill;
- compromise/revocation drill;
- rollback test with no dual-active signer.

## References

- <https://www.rfc-editor.org/info/rfc8032>
- <https://www.rfc-editor.org/info/rfc8785>
