# llp-complex-ubo.json — Structure Diagram

**Scenario:** Limited Liability Partnership — UK LLP with Corporate General Partner and Multiple Limited Partners.  
Meridian Capital LLP (UK) is the subject VASP sending 2,000,000 USDT to Singapore Digital Securities Pte Ltd. Control flows exclusively through the General Partner (Meridian Capital GP Ltd). The UBO is Priya Sharma — sole director and 100% shareholder of the GP. Limited Partners have no management rights under the LPA.

```mermaid
flowchart TD
    subgraph UBO["Ultimate Beneficial Owner"]
        UBO1["👤 Priya Anita Sharma\nUBO · GB / Indian national\nPassport: GB-PASS-PD7788990\nDOB: 1976-02-28, Mumbai\n8A Kensington Palace Gardens, London\n⚡ Control via GP:\n   Sole Director + 100% Shareholder\n   of Meridian Capital GP Ltd\nControl: DE_FACTO_CONTROL\n(FATF LP Guidance June 2023)"]
    end

    subgraph GP_Layer["General Partner (100% management control)"]
        GP["🏢 Meridian Capital GP Ltd · UK\nCH: GB-CH-14112233\nBishopsgate 100, London EC2N 4AG\n0% economic / 100% management authority\nunder LPA Clause 5\n📋 Directors (LPID mandates):\n→ Priya Sharma — Sole Director + 100% Shareholder\n→ Robert James Ashworth — NED (no ownership)"]
    end

    subgraph LLP["Meridian Capital LLP — Subject VASP"]
        SUBJECT["🏢 Meridian Capital LLP\nSubject VASP · UK · OC445678\nLEI: 213800MCLLPGB000GB00\nFCA-regulated · Risk: HIGH · EDD\nAll management vested in GP (LPA Clause 5)\nLP management rights: NONE (LPA Clause 7)"]
    end

    subgraph LPs["Limited Partners (economic interest only — no management rights)"]
        LP1["🏢 Priya Sharma Investments Ltd · Mauritius\nLP #1 · 45% economic interest\nMU ROC: MU-ROC-C200234567\n100% owned by Priya Sharma (UBO)\n📋 Director: Priya Sharma (sole)"]
        LP2["🏢 Ashworth Pension Fund Ltd · UK\nLP #2 · 35% economic interest\nCH: GB-CH-07112345\nNo individual controller >25%\n⚠️ Robert Ashworth (NED of GP)\n   also a trustee here — conflict noted"]
        LP3["👤 Dr. Arjun Dev Sharma · GB / Indian national\nLP #3 · 10% direct\nPassport: GB-PASS-PF3344556\nBrother of UBO Priya Sharma"]
        LP4["👤 Sita Rani Patel · GB\nLP #4 · 10% direct\nPassport: GB-PASS-PG5566778\nIndependent investor"]
    end

    subgraph Transfer["Travel Rule Transfer — GB → SG"]
        BVASP["🏦 Singapore Digital Securities Pte Ltd · SG\nBeneficiary VASP\nDID: did:web:singapore-digital-securities.example.sg\nLEI: 335800SDSSG000001SG0\nIssues KYCAttestation VC"]
    end

    UBO1 -- "Sole director + 100% shareholder" --> GP
    GP -- "General Partner\n(all management + voting rights\nunder LPA Clause 5)" --> SUBJECT
    LP1 -- "45% LP interest\n(no management rights)" --> SUBJECT
    LP2 -- "35% LP interest\n(no management rights)" --> SUBJECT
    LP3 -- "10% LP interest\n(no management rights)" --> SUBJECT
    LP4 -- "10% LP interest\n(no management rights)" --> SUBJECT
    UBO1 -.-> LP1
    SUBJECT -- "2,000,000 USDT\nOpenKYCAML VC" --> BVASP

    style UBO1 fill:#dbeafe,stroke:#3b82f6
    style GP fill:#fef3c7,stroke:#f59e0b
    style SUBJECT fill:#fef9c3,stroke:#eab308
    style LP1 fill:#ede9fe,stroke:#7c3aed
    style LP2 fill:#e5e7eb,stroke:#6b7280
    style LP3 fill:#dbeafe,stroke:#3b82f6
    style LP4 fill:#dbeafe,stroke:#3b82f6
    style BVASP fill:#fef9c3,stroke:#eab308
```

## Partnership Interest Summary

```mermaid
pie title Meridian Capital LLP — Economic Interest Split
    "Priya Sharma Investments Ltd (MU) — LP 45%" : 45
    "Ashworth Pension Fund Ltd (UK) — LP 35%" : 35
    "Dr. Arjun Sharma (UK individual) — LP 10%" : 10
    "Sita Patel (UK individual) — LP 10%" : 10
```

## UBO Determination Logic

```mermaid
flowchart LR
    PRIYA["Priya Sharma (UBO)"]
    GP_CO["Meridian Capital\nGP Ltd\n(100% management)"]
    MV_CO["Priya Sharma\nInvestments Ltd (MU)\n(45% LP economic)"]
    LLP["Meridian Capital LLP\n(subject VASP)"]

    PRIYA -- "100% owns + sole director" --> GP_CO
    PRIYA -- "100% owns + sole director" --> MV_CO
    GP_CO -- "GP = complete management control\n(0% economic / 100% voting)" --> LLP
    MV_CO -- "45% LP economic interest\n(no management rights)" --> LLP
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Structure | UK LLP with corporate GP and 4 LPs |
| Subject VASP | Meridian Capital LLP (UK, FCA-regulated) |
| UBO | Priya Anita Sharma (GB/IN) — via GP control |
| UBO control basis | Sole director + 100% shareholder of General Partner |
| GP economic interest | 0% (management fee only) |
| LP partners | 2 corporate + 2 individual |
| Notable conflict | Robert Ashworth — NED of GP and trustee of LP #2 pension fund |
| Asset / Amount | 2,000,000 USDT |
| Beneficiary VASP | Singapore Digital Securities Pte Ltd (SG) |
| Risk | HIGH · EDD |
| Regulatory basis | AMLR Art. 26(1), FATF LP Transparency Guidance (June 2023) |
