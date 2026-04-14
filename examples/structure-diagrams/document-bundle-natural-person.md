# document-bundle-natural-person.json — Structure Diagram

**Scenario:** Verification Document Bundle — Natural Person (v1.6.0).  
Andreas Schmidt (DE) has a complete CDD document bundle: German national ID, proof of address, and an eIDAS PID credential. The bundle is marked `COMPLETE` and was validated by the VASP's automated KYC engine. Document IDs use the `urn:openkycaml:doc:` URN convention (v1.6.0+).

```mermaid
flowchart TD
    subgraph Person["Natural Person — Subject"]
        NP["👤 Andreas Schmidt\nNaturalPerson · DE"]
    end

    subgraph Bundle["identityDocuments — VerificationDocumentBundle (v1.6.0)"]
        STATUS["✅ bundleCompleteness: COMPLETE\nValidated by: AutoKYC v3.2\n(Example VASP GmbH Compliance Engine)"]

        subgraph NP_DOCS["Natural Person Documents"]
            DOC1["🪪 NATIONAL_ID_CARD · DE\nurn:openkycaml:doc:de:national-id:sha256-421149:2021-03\nExtracted: familyName · givenName · dateOfBirth"]
            DOC2["🏠 PROOF_OF_ADDRESS · DE\nurn:openkycaml:doc:de:proof-of-address:...\nExtracted: streetName · buildingNumber · postCode"]
            DOC3["📲 EIDAS_PID_CREDENTIAL · DE\nurn:openkycaml:doc:de:eidas-pid:sha256-4...\nExtracted: family_name · given_name · birth_date\n(EUDI Wallet PID — eIDAS 2.0)"]
        end
    end

    NP -.-> Bundle

    style NP fill:#dbeafe,stroke:#3b82f6
    style STATUS fill:#dcfce7,stroke:#16a34a
    style DOC1 fill:#f0fdf4,stroke:#16a34a
    style DOC2 fill:#f0fdf4,stroke:#16a34a
    style DOC3 fill:#e0e7ff,stroke:#6366f1
```

## Document Bundle Summary

| # | Document type | Country | URN (truncated) | Extracted attributes |
|---|---|---|---|---|
| 1 | `NATIONAL_ID_CARD` | DE | `urn:openkycaml:doc:de:national-id:sha256-421149:2021-03` | familyName, givenName, dateOfBirth |
| 2 | `PROOF_OF_ADDRESS` | DE | `urn:openkycaml:doc:de:proof-of-address:...` | streetName, buildingNumber, postCode |
| 3 | `EIDAS_PID_CREDENTIAL` | DE | `urn:openkycaml:doc:de:eidas-pid:sha256-4...` | family_name, given_name, birth_date |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.6.0 |
| Subject | Andreas Schmidt (DE) |
| Bundle status | `COMPLETE` |
| Documents | 3 (NID + proof of address + eIDAS PID) |
| Validated by | AutoKYC v3.2 |
| Document ID format | `urn:openkycaml:doc:[country]:[type]:[hash]:[date]` (v1.6.0 convention) |
| Regulatory basis | AMLR Art. 22 CDD; eIDAS 2.0 PID verification |
