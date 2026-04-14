# legal-entity-governance.json — Structure Diagram

**Scenario:** Legal Entity with Full EntityGovernance Block (v1.12.0).  
Acme Financial Services GmbH (DE) is a dual-regulated (BaFin + FCA), exchange-listed subsidiary of Acme Group AG, sending 50,000 EUR to European Clearing House SA (LU). The record showcases the new v1.12.0 `entityGovernance` block with regulators array, listedStatus, parent company linkage, and `reviewLifecycle` state history.

```mermaid
flowchart TD
    subgraph Group["Corporate Group Structure"]
        PARENT["🏢 Acme Group AG\nParent Company · DE\nLEI: 529900T8BM49AURSDO55\nparentRegulated: true ✅\nparentListed: true ✅"]
    end

    subgraph Entity["Originating Entity — Acme Financial Services GmbH"]
        LP["🏢 Acme Financial Services GmbH\nLegalPerson · DE\nLEI: 529900HNOAA1KXQJUQ27\nlegalFormCode: UF1W (GmbH)\nentityType: COMPANY\nBockenheimer Landstraße 10, Frankfurt"]

        subgraph EG["entityGovernance 🆕 v1.12.0"]
            REG["📜 regulatoryStatus: REGULATED\n\nregulators[0]:\n  BaFin · DE\n  BAFIN-I-2024-001234\n\nregulators[1]:\n  Financial Conduct Authority · GB\n  FCA-789012"]
            LISTED["📈 listedStatus:\n  isListed: true\n  marketIdentifier: XETR (Deutsche Börse)\n  recognisedMarket: true (MiFID II)"]
            FLAGS["🔖 majorityOwnedSubsidiary: true\nparentRegulated: true\nparentListed: true\nstateOwned: false"]
        end
    end

    subgraph KYC["KYC Profile — Enhanced CDD"]
        KYCP["📋 kycLevel: ENHANCED · status: VERIFIED\nriskRating: LOW\nddt: CDD\ncustomerType: FINANCIAL_INSTITUTION\nBeneficialOwner: Acme Group AG (100%)"]
    end

    subgraph Lifecycle["Review Lifecycle 🆕 v1.12.0"]
        L1["ONBOARDING 2026-01-20→25"]
        L2["INITIAL_REVIEW 2026-01-25→Feb 01\nLEI verified; BaFin + FCA confirmed"]
        L3["🟩 PERIODIC_REVIEW ← currentState\n2026-02-01→"]
        L1 --> L2 --> L3
    end

    subgraph Transfer["Transfer"]
        OVASP["🏦 Acme Financial Services GmbH\nOriginating VASP · DE"]
        BVASP["🏦 European Clearing House SA\nBeneficiary VASP · LU\nLEI: 969500T8IBXIJNAXYS11"]
    end

    PARENT -. "100% owns (majorityOwnedSubsidiary)" .-> LP
    LP --> EG
    LP -- "50,000 EUR (FIAT)" --> OVASP
    OVASP -- "IVMS 101 Travel Rule" --> BVASP
    LP -.-> KYC
    KYC -.-> Lifecycle

    style PARENT fill:#ede9fe,stroke:#7c3aed
    style LP fill:#ede9fe,stroke:#7c3aed
    style REG fill:#dbeafe,stroke:#3b82f6
    style LISTED fill:#dcfce7,stroke:#16a34a
    style FLAGS fill:#f0fdf4,stroke:#16a34a
    style KYCP fill:#f0fdf4,stroke:#16a34a
    style L1 fill:#e0e7ff,stroke:#6366f1
    style L2 fill:#e0e7ff,stroke:#6366f1
    style L3 fill:#dcfce7,stroke:#16a34a
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
```

## EntityGovernance Field Summary

| Field | Value | Regulatory basis |
|---|---|---|
| `regulatoryStatus` | `REGULATED` | AMLR Art. 48 CDD reliance |
| `regulators[0]` | BaFin (DE) · BAFIN-I-2024-001234 | AMLR Art. 48; Wolfsberg CBDDQ §3 |
| `regulators[1]` | FCA (GB) · FCA-789012 | Multi-jurisdiction dual-regulation |
| `listedStatus.isListed` | `true` | AMLR Art. 22 SDD eligibility |
| `listedStatus.marketIdentifier` | `XETR` (Deutsche Börse, MiFID II) | MAR insider-dealing risk |
| `listedStatus.recognisedMarket` | `true` | AMLR Art. 22 simplified CDD |
| `majorityOwnedSubsidiary` | `true` | FATF Rec. 24; AMLR Art. 26 |
| `parentRegulated` | `true` | AMLR Art. 48 intra-group reliance |
| `parentListed` | `true` | AMLR Art. 22 SDD; MAR |
| `stateOwned` | `false` | FATF PEP Guidance — no SOE risk |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.12.0 |
| Message type | KYC_LEGAL_ENTITY |
| Subject | Acme Financial Services GmbH (DE) |
| Regulatory status | REGULATED — dual-licensed (BaFin + FCA) |
| Listed | XETR (Deutsche Börse) — recognised market |
| Parent | Acme Group AG (regulated + listed) |
| Amount | 50,000 EUR |
| KYC level | ENHANCED · CDD |
| Risk | LOW |
| Lifecycle state | PERIODIC_REVIEW |
| Regulatory basis | FATF Rec. 24/25; AMLR Art. 22/26/48; MiFID II; MAR |
