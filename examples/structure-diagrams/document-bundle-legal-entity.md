# document-bundle-legal-entity.json — Structure Diagram

**Scenario:** Verification Document Bundle — Legal Entity (v1.6.0).  
Acme Global Trading PLC (GB) has a complete KYB document bundle: certificate of incorporation, articles of association, Companies House registry extract, LEI registration, UBO declaration, and a beneficial ownership register extract (6 documents total). Validated by the VASP's KYB compliance officer. Document IDs use the `urn:openkycaml:doc:` URN convention (v1.6.0+).

```mermaid
flowchart TD
    subgraph Entity["Legal Entity — Subject"]
        LP["🏢 Acme Global Trading PLC\nLegalPerson · GB"]
    end

    subgraph Bundle["identityDocuments — VerificationDocumentBundle (v1.6.0)"]
        STATUS["✅ bundleCompleteness: COMPLETE\nValidated by: UK Digital Assets Exchange Ltd\nKYB Compliance Officer — Jane Smith"]

        subgraph LE_DOCS["Legal Entity Documents (6)"]
            DOC1["📜 CERTIFICATE_OF_INCORPORATION · GB\nurn:openkycaml:doc:gb:cert-incorp:529900..."]
            DOC2["📋 ARTICLES_OF_ASSOCIATION · GB\nurn:openkycaml:doc:gb:articles:529900w18..."]
            DOC3["🏛️ REGISTRY_EXTRACT · GB\nurn:openkycaml:doc:gb:registry-extract:5...\n(Companies House)"]
            DOC4["🔖 LEI_REGISTRATION · GB\nurn:openkycaml:doc:gb:lei:529900w18lqjjn...\n(LEI: 529900W18LQJJNF6SJ37)"]
            DOC5["👥 UBO_DECLARATION · GB\nurn:openkycaml:doc:gb:ubo-declaration:...\n(AMLR Art. 26 — beneficial ownership)"]
            DOC6["📊 BENEFICIAL_OWNERSHIP_REGISTER · GB\nurn:openkycaml:doc:gb:psc-register:...\n(UK PSC register extract)"]
        end
    end

    LP -.-> Bundle

    style LP fill:#ede9fe,stroke:#7c3aed
    style STATUS fill:#dcfce7,stroke:#16a34a
    style DOC1 fill:#f0fdf4,stroke:#16a34a
    style DOC2 fill:#f0fdf4,stroke:#16a34a
    style DOC3 fill:#f0fdf4,stroke:#16a34a
    style DOC4 fill:#dbeafe,stroke:#3b82f6
    style DOC5 fill:#fff7ed,stroke:#f97316
    style DOC6 fill:#fff7ed,stroke:#f97316
```

## Document Bundle Summary

| # | Document type | Country | Purpose |
|---|---|---|---|
| 1 | `CERTIFICATE_OF_INCORPORATION` | GB | Legal existence proof |
| 2 | `ARTICLES_OF_ASSOCIATION` | GB | Corporate constitution |
| 3 | `REGISTRY_EXTRACT` | GB | Current Companies House filing |
| 4 | `LEI_REGISTRATION` | GB | LEI 529900W18LQJJNF6SJ37 verification |
| 5 | `UBO_DECLARATION` | GB | AMLR Art. 26 self-declaration |
| 6 | `BENEFICIAL_OWNERSHIP_REGISTER` | GB | UK PSC register extract |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.6.0 |
| Subject | Acme Global Trading PLC (GB) |
| Bundle status | `COMPLETE` |
| Documents | 6 (incorporation + governance + LEI + UBO) |
| Validated by | Jane Smith — KYB Compliance Officer |
| Document ID format | `urn:openkycaml:doc:[country]:[type]:[ref]:[date]` |
| Regulatory basis | AMLR Art. 22/26 CDD + UBO disclosure; UK MLR 2017 |
