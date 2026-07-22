# Offline OpenTelemetry Reference Profiles

This directory contains immutable, byte-digest-bound inputs for the bounded
DQ-018 Telemetry Admission Foundation. It is package data, not generated
runtime state.

| file | role | exact SHA-256 |
|---|---|---|
| `opentelemetry-semantic-mapping.v0.1.json` | DBA-adopted 47-field mapping | `b81213505b1a7c3841ba298545b642b127af1a96ec906536be27caab351de706` |
| `opentelemetry-semantic-conformance-cases.v0.1.json` | 46-case semantic catalog; current offline scope executes 32 | `18b84edf6e8b618991c2dfd669d21794c3a3032188e198b7fd53899205b66c6e` |
| `opentelemetry-schema-resource-conformance-cases.v0.1.json` | 45-case Schema/Resource catalog; current offline scope executes 36 | `805374a196f533d8b2c56492faeb566e05dd744edd0e519155442fcc50f8f452` |
| `opentelemetry-semantic-conformance-result-set.schema.v0.1.json` | semantic result-set validation contract | `33fa128aa8063d8f4861f8abda23d9b48151f1a6529752848adaef3ea49f6f15` |
| `opentelemetry-schema-resource-conformance-result-set.schema.v0.1.json` | Schema/Resource result-set validation contract | `11a744b089bfab132f96825e5f10ce613d8d0b7ff145919fdff4bdb06c5112ee` |
| `opentelemetry-schema-1.43.0.yaml` | official published OTel schema artifact | `6ac5dd367ff707dbcdcb1e5b459d4ac2fd676fb44eb17a21f9494a9fee4233df` |

`references.py` verifies each digest before parsing. Unknown filenames,
missing resources, parse failures, or byte drift fail closed. Runtime network
fetch is intentionally absent.

These files do not authorize or create a Collector, listener, deployment,
Agent, Runtime, Entity, Capability, Permission, Evidence, Verification, SAEE
output, or production gate result. The 14 semantic and 9 Schema/Resource cases
outside the DQ-018/PR-G2 offline scope remain `BLOCKED_NOT_AUTHORIZED` in the
machine-readable test bindings.
