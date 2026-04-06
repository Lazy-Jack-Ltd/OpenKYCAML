# full-kyc-profile.json — Structure Diagram

**Scenario:** Full KYC Profile — Foreign PEP with EDD (plain JSON, no VC wrapper).  
Fatima Noor Al-Rashidi (AE), Former UAE Minister of Finance (2015–2020), is a Foreign PEP onboarded at DIFC Digital Asset Exchange LLC (AE) under Enhanced Due Diligence. HIGH risk rating (score 720). Sends 125,000 USDC to Geneva Capital Management SA (CH).

```mermaid
flowchart TD
    subgraph Customer["Customer — Enhanced Due Diligence"]
        CUST["👤 Fatima Noor Al-Rashidi\nFOREIGN_PEP · AE\nEmirates ID: 784-1990-1234567-8\nDOB: 1978-03-12, Abu Dhabi\nResident: Dubai · HNW\nFormer Minister of Finance (2015–2020)"]

        RISK["⚠️ Risk Profile\n─────────────────────────\nOverall: HIGH (score 720)\nGeographic: HIGH\nProduct: HIGH / Channel: MEDIUM\nCustomer type: HIGH / Transaction: HIGH\nDue Diligence: EDD\nMonitoring: ENHANCED (semi-annual)"]

        SOW["💰 Source of Wealth / Funds\n─────────────────────────\n✅ FULLY_VERIFIED\nInvestment Returns + Business Income\nSupporting docs:\n• Tax Return (AE-TAX-2023)\n• Audited Accounts (3 UAE/BVI holdcos)\n• Bank Statement (ADIB Q1 2024)"]

        SCREENING["🔍 Screening Results\n─────────────────────────\n✅ Sanctions: CLEAR\n   (OFAC_SDN, OFAC_NON_SDN, EU, UN,\n    HMT, AUSTRAC)\n✅ Adverse Media: CLEAR\n   (ComplyAdvantage — 100,000+ sources)"]
    end

    subgraph Transfer["Travel Rule Transfer — AE → CH"]
        OVASP["🏦 DIFC Digital Asset Exchange LLC\nOriginating VASP · AE (DIFC)\nLEI: 529900T8BM49AAMSDO55\nOnboarding: IN_PERSON\nReview: Semi-annual EDD"]
        BVASP["🏦 Swiss Digital Finance AG\nBeneficiary VASP · CH\nLEI: 549300FJPOIUJ7U9LV82"]
        B["🏢 Geneva Capital Management SA\nLegalPerson · CH\nLEI: 54930084UKLVMY22DS16\nAccount: CH5604835012345678009"]
    end

    CUST -- "Onboards under EDD" --> OVASP
    CUST -.-> RISK
    CUST -.-> SOW
    CUST -.-> SCREENING
    OVASP -- "IVMS 101 (plain)\n125,000 USDC" --> BVASP
    BVASP -- "Credits account" --> B

    style CUST fill:#fee2e2,stroke:#ef4444
    style RISK fill:#fef3c7,stroke:#f59e0b
    style SOW fill:#ecfdf5,stroke:#059669
    style SCREENING fill:#ecfdf5,stroke:#059669
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
    style B fill:#ede9fe,stroke:#7c3aed
```

## KYC Timeline

```mermaid
timeline
    title KYC Review Timeline
    2024-01-10 : Initial onboarding (EDD) created
    2024-05-28 : Alert ALT-2024-003921 — Velocity breach\n3 cross-border transfers > USD 50k in 7 days\nClosed — no action (consistent with profile)
    2024-06-01 : Annual EDD review completed\nRisk: HIGH maintained\nMonitoring: ENHANCED confirmed
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Customer | Fatima Noor Al-Rashidi (AE), Foreign PEP |
| PEP role | Former Minister of Finance UAE (2015–2020) |
| Risk rating | HIGH (720/1000) |
| Due diligence | EDD |
| Monitoring | ENHANCED, semi-annual |
| Asset / Amount | 125,000 USDC |
| Originating VASP | DIFC Digital Asset Exchange LLC (AE) |
| Beneficiary | Geneva Capital Management SA (CH) |
