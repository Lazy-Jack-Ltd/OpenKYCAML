# legal-entity-deep-ubo.json — Structure Diagram

**Scenario:** Enhanced Beneficial Ownership — 4-Tier Corporate Chain (AMLR Art. 26).  
Meridian Digital Assets Ltd (KY) is the subject VASP sending 500,000 USDT to Prime Digital Exchange Ltd (GB). Full AMLR Art. 26 chain disclosure for two UBOs: Fatima Al-Rashidi (75% indirect, 4-tier chain) and Sheikh Omar Al-Farsi (20% direct).

```mermaid
flowchart TD
    subgraph UBO1_Chain["UBO 1 Chain — 75% Indirect (4 tiers)"]
        UBO1["👤 Fatima Noor Al-Rashidi\nUBO #1 · AE\nEmirates ID: 784-1978-1234567-0\nDOB: 1978-03-12, Abu Dhabi\n75% ultimate indirect control\nControl: SHAREHOLDING · INDIRECT · depth 4"]

        T3["🏢 Al-Rashidi Family Office Holding Ltd\nTier 3 (closest to UBO) · BVI\nReg: VG-BC-2015-000311\n100% owned by UBO"]
        T2["🏢 Meridian Holdings SA\nTier 2 · Luxembourg\nReg: LU-RCS-B247891\n88% owned by Family Office"]
        T1["🏢 Meridian Ventures Ltd\nTier 1 (closest to subject) · Cayman Islands\nReg: KY-CI-MV-2018-000077\n75% owned by Holdings SA"]

        UBO1 -- "100% owns" --> T3
        T3 -- "100%" --> T2
        T2 -- "88%" --> T1
        T1 -- "75%" --> SUBJECT
    end

    subgraph UBO2["UBO 2 — 20% Direct"]
        UBO2_NODE["👤 Sheikh Omar Khalid Al-Farsi\nUBO #2 · AE\nEmirates ID: 784-1972-1234567-9\nDOB: 1972-07-04, Dubai\n20% direct shareholding (disclosed per EDD policy)\nControl: SHAREHOLDING · DIRECT · depth 1"]
        UBO2_NODE -- "20% direct" --> SUBJECT
    end

    SUBJECT["🏢 Meridian Digital Assets Ltd\n**Subject VASP** · Cayman Islands\nReg: KY-CI-MC-2020-000142\nLEI: 213800DZWM2ULYSJRN63\nRisk: HIGH · EDD"]

    subgraph Transfer["Travel Rule Transfer"]
        BVASP["🏦 Prime Digital Exchange Ltd\nBeneficiary VASP · GB\nDID: did:web:prime-digital-exchange.example.co.uk\nLEI: 213800PFGH1KDXSYA174"]
    end

    SUBJECT -- "500,000 USDT\nOpenKYCAML VC (KYCAttestation)" --> BVASP

    style UBO1 fill:#dbeafe,stroke:#3b82f6
    style T3 fill:#ede9fe,stroke:#7c3aed
    style T2 fill:#ede9fe,stroke:#7c3aed
    style T1 fill:#ede9fe,stroke:#7c3aed
    style SUBJECT fill:#fef9c3,stroke:#eab308
    style UBO2_NODE fill:#dbeafe,stroke:#3b82f6
    style BVASP fill:#fef9c3,stroke:#eab308
```

## Ownership Summary

| UBO | Ownership | Depth | Mechanism | Chain |
|---|---|---|---|---|
| Fatima Al-Rashidi (AE) | 75% indirect | 4 | SHAREHOLDING | Family Office BVI → Holdings SA LU → Ventures KY → Subject |
| Sheikh Omar Al-Farsi (AE) | 20% direct | 1 | SHAREHOLDING | Direct |
| Others (not reported) | 5% | — | — | Below FATF 25% threshold |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Subject VASP | Meridian Digital Assets Ltd (KY) |
| Risk | HIGH · EDD (offshore chain, complex UBO) |
| Primary UBO | Fatima Noor Al-Rashidi (AE) — 75%, 4-tier |
| Secondary UBO | Sheikh Omar Al-Farsi (AE) — 20%, direct |
| Beneficiary VASP | Prime Digital Exchange Ltd (GB) |
| Asset / Amount | 500,000 USDT |
| Regulatory basis | AMLR Art. 26 full chain disclosure |
