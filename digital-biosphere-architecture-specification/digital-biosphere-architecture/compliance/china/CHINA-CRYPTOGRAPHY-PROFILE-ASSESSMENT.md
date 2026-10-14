# China Cryptography Profile Assessment

Status: `HUMAN_CRYPTOGRAPHY_REVIEW_REQUIRED`

Primary sources:

- Cryptography Law: https://wb.flk.npc.gov.cn/flfg/PDF/ae21d83445074060a3228ae9c4ee528f.pdf
- Commercial Cryptography Regulations: https://www.mee.gov.cn/zcwj/gwywj/202305/t20230529_1031579.shtml

## Candidate profiles

| Profile | Candidate use | Status |
|---|---|---|
| Ed25519 + SHA-256 | current technical receipt candidate and public verifier | `IMPLEMENTATION_CANDIDATE_NOT_LEGAL_CONCLUSION` |
| Customer-managed KMS/HSM | private deployment signing boundary | `PREFERRED_ENTERPRISE_OPTION` |
| SM2/SM3/SM4 | optional China cryptography profile | `ARCHITECTURE_RESERVED_NOT_IMPLEMENTED` |
| qualified third-party timestamp/signature | customer-selected evidentiary requirement | `EXTERNAL_SERVICE_IF_REQUIRED` |

TITMAS must not create a CA or electronic certification service. Before a paid
pilot, a qualified reviewer must determine whether the actual deployment,
product classification, sector or customer security scheme triggers commercial
cryptography testing, certification, import/export, MLPS cryptography or other
requirements.

Key generation, storage, rotation, revocation, compromise handling, backup and
public-key distribution remain required technical controls regardless of the
legal classification.
