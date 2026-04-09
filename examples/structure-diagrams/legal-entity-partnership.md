# legal-entity-partnership.json — Structure Diagram

**Scenario:** UK Limited Liability Partnership (LLP) — Cairn Digital Ventures LLP (GB) sends 120,000 BTC to Northstar Digital Exchange Ltd (GB). The record captures the LLP partnership structure with two natural-person members (Designated Members) and one corporate member, under AMLR Art. 26 CDD requirements for partnerships.

```mermaid
flowchart TD
    subgraph Members["LLP Members — Cairn Digital Ventures LLP"]
        NP1["👤 Fiona Jean MacAlister\nDesignated Member · GB\nPassport ID presented\nKYC verified"]
        NP2["👤 Robert Alistair Drummond\nDesignated Member · GB\nPassport ID presented\nKYC verified"]
        LP1["🏢 Cairn Capital Management Ltd\nCorporate Member\nRegistered in GB"]
    end

    subgraph Subject["Subject VASP — LLP"]
        LLP["🏢 Cairn Digital Ventures LLP\nentityType: PARTNERSHIP / LLP\nReg: SO300447 (CH-RA, GB)\nKYC/AML: AMLR Art. 26 — all managing\nmembers/partners identified"]
    end

    subgraph KYC["KYC Profile — EDD"]
        KYCP["📋 KYC Level: EDD\nriskRating: MEDIUM\nddt: EDD\nCustomer type: LLP\nBO: Fiona MacAlister (40%)\nBO: Robert Drummond (35%)\nSanctions: CLEAR"]
    end

    subgraph Transfer["Travel Rule Transfer — GB → GB"]
        OVASP["🏦 Cairn Digital Ventures LLP\nOriginating VASP · GB"]
        BVASP["🏦 Northstar Digital Exchange Ltd\nBeneficiary VASP · GB"]
    end

    NP1 -- "Designated Member\n(management rights)" --> LLP
    NP2 -- "Designated Member\n(management rights)" --> LLP
    LP1 -- "Corporate Member" --> LLP

    LLP -- "120,000 BTC" --> OVASP
    OVASP -- "IVMS 101 Travel Rule\n120,000 BTC" --> BVASP
    LLP -.-> KYC

    style NP1 fill:#dbeafe,stroke:#3b82f6
    style NP2 fill:#dbeafe,stroke:#3b82f6
    style LP1 fill:#ede9fe,stroke:#7c3aed
    style LLP fill:#fef9c3,stroke:#eab308
    style KYCP fill:#f0fdf4,stroke:#16a34a
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
```

## Partnership Structure Summary

| Role | Name | Type | Notes |
|---|---|---|---|
| Designated Member | Fiona Jean MacAlister (GB) | Natural person | 40% ownership — UBO above FATF 25% threshold |
| Designated Member | Robert Alistair Drummond (GB) | Natural person | 35% ownership — UBO above FATF 25% threshold |
| Corporate Member | Cairn Capital Management Ltd (GB) | Legal person | 25% — CDD applied to legal person |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.4.0 |
| Structure | UK Limited Liability Partnership |
| Entity | Cairn Digital Ventures LLP (GB) |
| Members | 2 natural persons + 1 corporate member |
| Designated members | MacAlister + Drummond (management control) |
| Asset / Amount | 120,000 BTC |
| KYC level | EDD |
| Risk | MEDIUM |
| Beneficiary VASP | Northstar Digital Exchange Ltd (GB) |
| Regulatory basis | FATF Rec. 24; AMLR Art. 26; Companies Act 2006 (LLP Regs 2001) |
