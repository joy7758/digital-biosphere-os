# China Legal Applicability Matrix

Status: `HUMAN_LEGAL_REVIEW_REQUIRED`

```text
DRAFT_NOT_LEGAL_ADVICE=true
LEGAL_COMPLIANCE_PASS=false
LICENSE_NOT_REQUIRED=NOT_ASSESSED
FILING_NOT_REQUIRED=NOT_ASSESSED
```

This matrix classifies questions for qualified Chinese legal, cybersecurity,
telecommunications and cryptography review. It does not provide a compliance
opinion or certification.

| Instrument | Official source | Candidate status | Trigger considered | Required next evidence |
|---|---|---|---|---|
| Cybersecurity Law of the PRC, 2025 revision effective 2026-01-01 | https://flk.npc.gov.cn/detail?fileId=&id=021e7d7684474107b8f3febbb1c4f8b5&title=%E4%B8%AD%E5%8D%8E%E4%BA%BA%E6%B0%91%E5%85%B1%E5%92%8C%E5%9B%BD%E7%BD%91%E7%BB%9C%E5%AE%89%E5%85%A8%E6%B3%95&type= | `LIKELY_APPLICABLE` | operating a network service and protecting systems/data | counsel and security-owner review of operator duties and classification |
| Data Security Law | https://www.npc.gov.cn/npc/c2/c30834/202106/t20210610_311888.html | `LIKELY_APPLICABLE` | processing operational, customer and security data | data catalog, classification owner and important-data assessment |
| Personal Information Protection Law | https://www.npc.gov.cn/npc/c2/c30834/202108/t20210820_313088.html | `CONDITIONALLY_APPLICABLE` | business email, contacts, user/account logs or customer-provided PI | lawful-basis analysis, notice, processor/controller roles, retention and rights workflow |
| Regulations on Network Data Security Management, effective 2025-01-01 | https://app.www.gov.cn/govdata/gov/202409/30/520076/article.html | `LIKELY_APPLICABLE` | network-data processing in managed service or website | accountable roles, data inventory, incident and deletion controls |
| Interim Measures for Generative AI Services | https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm | `CONDITIONALLY_APPLICABLE` | providing generative-AI service to the public in China | service-path analysis; model filing/application-registration evidence if triggered |
| Measures for Labeling AI-Generated Synthetic Content, effective 2025-09-01 | https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm | `CONDITIONALLY_APPLICABLE` | TITMAS itself generating and publishing covered content | interface/content-flow analysis and explicit/implicit label design if triggered |
| Algorithmic Recommendation Provisions | https://www.cac.gov.cn/2022-01/04/c_1642894606364259.htm | `LIKELY_NOT_APPLICABLE` to current bounded private pilot; `HUMAN_LEGAL_REVIEW_REQUIRED` | public recommendation/distribution or personalized ranking | product feature review before any public recommendation function |
| Deep Synthesis Provisions | https://www.cac.gov.cn/2022-12/11/c_1672221949354811.htm | `CONDITIONALLY_APPLICABLE` | public deep-synthesis generation service | content-generation and provider-role assessment |
| Provisions on Promoting and Regulating Cross-Border Data Flows | https://www.gov.cn/gongbao/2024/issue_11366/202405/content_6954192.html | `CONDITIONALLY_APPLICABLE` | sending China customer or personal data to a foreign model/provider or foreign control plane | per-flow data category, volume, recipient, purpose and mechanism review |
| Personal Information Protection Compliance Audit Measures, effective 2025-05-01 | https://www.cac.gov.cn/2025-02/14/c_1741233507681519.htm | `CONDITIONALLY_APPLICABLE` | PI processor duties, thresholds or regulator requirements | PI count, processing role and qualified audit advice |
| Internet Information Service Measures | https://cqca.miit.gov.cn/zwgk/zcwj/flfg/art/2026/art_3aa3d50dbe1648fda74aeab4f39b2db1.html | `LIKELY_APPLICABLE` to public web service | operation of redcrag.cn and any online service | hosting, business model, service description and counsel review |
| Measures for the Administration of Non-commercial Internet Information Services Filing | https://www.miit.gov.cn/gyhxxhb/jgsj/cyzcyfgs/bmgz/xxtxl/art/2024/art_84a0cfa0ebd049bbbe751dca9a008e56.html | `LIKELY_APPLICABLE` to the current informational site | non-commercial public website hosted in mainland China | authoritative ICP record, entity/domain/host consistency and change process |
| Telecommunications Services Classification Catalogue (2015), as amended | https://www.miit.gov.cn/zwgk/zcwj/wjfb/tg/art/2020/art_b6a54a60f9c6471cb3a996106fc09cd5.html and https://wap.miit.gov.cn/zwgk/zcwj/wjfb/tg/art/2020/art_e98406cd89844f7e92ea1bcf3b5301e0.html | `HUMAN_LEGAL_REVIEW_REQUIRED` | paid online processing, platform publication, transaction or SaaS delivery characteristics | telecom counsel classification of actual product and delivery contract |
| Electronic Signature Law | https://www.npc.gov.cn/zgrdw/npc/xinwen/2019-05/07/content_2086835.htm | `CONDITIONALLY_APPLICABLE` | electronic contracts/signatures or presenting Receipt as a signature service | preserve Receipt as technical record; counsel review for contract-signature use |
| Cryptography Law | https://wb.flk.npc.gov.cn/flfg/PDF/ae21d83445074060a3228ae9c4ee528f.pdf | `CONDITIONALLY_APPLICABLE` | use or provision of cryptography products/services and sector requirements | qualified cryptography review of product, deployment and key roles |
| Commercial Cryptography Regulations | https://www.mee.gov.cn/zcwj/gwywj/202305/t20230529_1031579.shtml | `CONDITIONALLY_APPLICABLE` | commercial cryptography products/services, regulated deployment or required assessments | qualified review of Ed25519 and optional SM profile |
| GB/T 22239-2019 Network Security Classified Protection Baseline | https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=BAFB47E8874764186BDB7865E8344DAF | `HUMAN_LEGAL_REVIEW_REQUIRED` | network operator/system classification and security-protection obligations | system boundary, deployment topology, grading consultation and evidence plan |

## Frozen interpretation boundaries

```text
COMPLIANCE_MATRIX_NE_CERTIFICATION=true
LEGAL_REVIEW_NE_CODEX_CONCLUSION=true
CUSTOMER_DATA_TO_FOREIGN_MODEL_DEFAULT=false
CUSTOMER_PERSONAL_INFORMATION_TO_FOREIGN_MODEL_DEFAULT=false
PUBLIC_SELF_SERVICE_SALES=false
OFFLINE_B2B_CONTRACTED_PRIVATE_PILOT=AWAITING_HUMAN_LEGAL_REVIEW
```
