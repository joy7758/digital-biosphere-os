# China Electronic Signature Boundary

Status: `HUMAN_LEGAL_REVIEW_REQUIRED`

Primary source: https://www.npc.gov.cn/zgrdw/npc/xinwen/2019-05/07/content_2086835.htm

TITMAS Receipt is a `技术执行回执` or `可验证执行回执`. It records bounded
technical execution material and verification limitations.

```text
RECEIPT_IS_TECHNICAL_EVIDENCE_RECORD=true
RECEIPT_NE_LEGAL_CERTIFICATE=true
RECEIPT_NE_ELECTRONIC_CERTIFICATION_SERVICE=true
RECEIPT_NE_FACT_TRUTH=true
RECEIPT_NE_LEGALITY=true
AUTOMATIC_CONTRACT_SIGNATURE=false
```

TITMAS does not issue legal-person identity certificates, operate a CA,
authenticate legal signatures, sign contracts for a party, or claim judicial
or administrative evidentiary status. If a customer later uses a Receipt in an
electronic-signature or electronic-contract workflow, qualified counsel and
the customer's chosen signature/certification provider must define that
separate boundary.
