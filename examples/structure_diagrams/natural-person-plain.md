# natural-person-plain.json — Structure Diagram

**Scenario:** Minimal IVMS 101 Travel Rule — Natural Person to Natural Person (plain JSON, no VC wrapper).  
Satoshi Nakamoto (NL) sends 0.5 BTC to Harold Finney (GB) via two VASPs.

```mermaid
flowchart TD
    subgraph Originator_Side["Originating Side — Netherlands"]
        O["👤 Satoshi Nakamoto\nNaturalPerson · NL\nPassport: NL-PASSPORT-AB123456\nDOB: 1985-04-05, Amsterdam\nWallet: bc1qxy2kgdygjr..."]
        OVASP["🏦 Acme Crypto Exchange BV\nOriginating VASP · NL\nLEI: 724500VNNHZHYDLFMO70"]
    end

    subgraph Beneficiary_Side["Beneficiary Side — United Kingdom"]
        BVASP["🏦 FinTech Exchange Ltd\nBeneficiary VASP · GB\nLEI: 213800WSGIIZCXF1P572"]
        B["👤 Harold Thomas Finney\nNaturalPerson · GB\nPassport: GB-PASSPORT-HF987654\nWallet: 3J98t1WpEZ73CN..."]
    end

    O -- "Initiates transfer\n0.5 BTC" --> OVASP
    OVASP -- "IVMS 101 Travel Rule message\n(OpenKYCAML v1.3.0)\n0.5 BTC" --> BVASP
    BVASP -- "Credits account" --> B

    style O fill:#dbeafe,stroke:#3b82f6
    style B fill:#dbeafe,stroke:#3b82f6
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Message type | IVMS 101 (plain — no VC wrapper) |
| Originator | Satoshi Nakamoto, NL natural person |
| Beneficiary | Harold Thomas Finney, GB natural person |
| Asset / Amount | 0.5 BTC |
| Originating VASP | Acme Crypto Exchange BV (NL) |
| Beneficiary VASP | FinTech Exchange Ltd (GB) |
| Due diligence | Standard IVMS 101 — no kycProfile attached |
