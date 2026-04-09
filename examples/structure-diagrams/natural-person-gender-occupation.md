# natural-person-gender-occupation.json — Structure Diagram

**Scenario:** KYC Natural Person with Gender and Structured Occupation (v1.12.0).  
Anna Maria Müller (DE, self-employed UX designer) sends 1,500 EUR to a digital payments provider. The record includes the new v1.12.0 `gender` and structured `occupation` fields, plus a full `reviewLifecycle` state history from ONBOARDING through to PERIODIC_REVIEW (AMLR Art. 21).

```mermaid
flowchart TD
    subgraph Person["Natural Person — Originator"]
        NP["👤 Anna Maria Müller\nNaturalPerson · DE\nID: DE123456789 (IDCD)\nDOB: 1985-07-14, Munich\nAddress: Hauptstraße 42, Berlin 10115\ngender: FEMALE 🆕 v1.12.0\noccupationCode: SELF_EMPLOYED 🆕 v1.12.0\noccupationDescription: Freelance UX designer\nAccount: DE89370400440532013000\nEmail: anna.mueller@example.de"]
    end

    subgraph KYC["KYC Profile — Standard CDD"]
        KYCP["📋 KYC Profile\nkycLevel: STANDARD\nkycStatus: VERIFIED\nkycCompletionDate: 2026-01-15\nriskRating: LOW (score 12)\nddt: CDD\noccupationOrPurpose: Freelance UX designer\n(kycProfile field — unchanged)"]
    end

    subgraph Lifecycle["Review Lifecycle State Machine 🆕 v1.12.0"]
        S1["🟦 ONBOARDING\n2026-01-10 → 2026-01-12\ntriggeredBy: CUSTOMER_PORTAL\nCustomer initiated via web portal"]
        S2["🟦 INITIAL_REVIEW\n2026-01-12 → 2026-01-15\ntriggeredBy: COMPLIANCE_OFFICER_JM\nDocuments verified; screens clear"]
        S3["🟩 PERIODIC_REVIEW ← currentState\n2026-01-15 →\ntriggeredBy: COMPLIANCE_OFFICER_JM\nAnnual review schedule initiated"]

        S1 --> S2 --> S3
    end

    subgraph Transfer["Transfer"]
        OVASP["🏦 Example Payments GmbH\nOriginating VASP · DE"]
        BVASP["🏦 Digital Payments GmbH\nBeneficiary VASP · DE"]
    end

    NP -- "1,500 EUR (FIAT)" --> OVASP
    OVASP -- "IVMS 101 Travel Rule\n1,500 EUR" --> BVASP
    NP -.-> KYC
    KYC -.-> Lifecycle

    style NP fill:#dbeafe,stroke:#3b82f6
    style KYCP fill:#f0fdf4,stroke:#16a34a
    style S1 fill:#e0e7ff,stroke:#6366f1
    style S2 fill:#e0e7ff,stroke:#6366f1
    style S3 fill:#dcfce7,stroke:#16a34a
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
```

## v1.12.0 Fields Highlighted

| Field | Path | Value |
|---|---|---|
| `gender` 🆕 | `naturalPerson.gender` | `FEMALE` (eIDAS 2.0 PID / ISO IEC 5218) |
| `occupationCode` 🆕 | `naturalPerson.occupation.occupationCode` | `SELF_EMPLOYED` (ILO/ISCO-08) |
| `occupationDescription` 🆕 | `naturalPerson.occupation.occupationDescription` | `"Freelance UX designer and digital product consultant"` |
| `reviewLifecycle.currentState` 🆕 | `kycProfile.monitoringInfo.reviewLifecycle.currentState` | `PERIODIC_REVIEW` |
| `stateHistory` 🆕 | `kycProfile.monitoringInfo.reviewLifecycle.stateHistory` | 3 transitions with timestamps and notes |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.12.0 |
| Message type | KYC_NATURAL_PERSON |
| Subject | Anna Maria Müller (DE) |
| Gender | FEMALE (eIDAS 2.0 PID `gender`) |
| Occupation | SELF_EMPLOYED — Freelance UX designer |
| Amount | 1,500 EUR |
| KYC level | STANDARD · CDD |
| Risk | LOW (score 12) |
| Lifecycle state | PERIODIC_REVIEW (3rd state after ONBOARDING → INITIAL_REVIEW) |
| Regulatory basis | AMLR Art. 22 CDD data; AMLR Art. 21 ongoing monitoring; IVMS 101 extended CDD; eIDAS 2.0 PID |
| GDPR note | `gender` is GDPR Art. 9 special-category data — lawful basis required |
