# full-kyc-profile-eudi-wallet.json — Structure Diagram

**Scenario:** EUDI Wallet — Full KYC Profile, EDD, Foreign PEP Case.  
Fatima Noor Al-Rashidi (AE), Former UAE Minister of Finance (2015–2020), is a Foreign PEP onboarding at DIFC Digital Asset Exchange LLC via Austrian EUDI Wallet PID (she has EU residency). **Note: EUDI Wallet PID does NOT reduce PEP risk — EDD is always mandatory per AMLR Art. 28.**

```mermaid
flowchart TD
    subgraph Identity_Chain["Identity Chain — EUDI Wallet (Austrian Residency PID)"]
        PID_AT["🏛️ Austrian PID Provider\nBundesministerium für Inneres (BMI)\nDID #2: did:web:pid-provider.bmi.example.at\nIssues Austrian Residence-based PID\n(eIDAS 2.0 — Regulation EU 2024/1183)"]
        WALLET["📱 Fatima Al-Rashidi — Austrian EUDI Wallet\nDID #1: did:ebsi:z4MrTwQ9nVyXkBFaLdZhGpJ8\nUAE Emirates ID cross-reference maintained\nAE national with AT EU residency"]
        PID_AT -- "Issues Austrian Residence PID VC\n(enables EU remote CDD — AMLR Art. 22(5))" --> WALLET
    end

    subgraph UAE_ID["UAE Cross-Reference"]
        UAE_ICP["🏛️ UAE ICP\ndid:web:icp.example.ae\nIssues Emirates ID cross-reference"]
        UAE_ICP -- "Emirates ID verification\n(AE-EMIRATESID-784-1978-1234567-8)" --> WALLET
    end

    subgraph EDD_Process["EDD Process"]
        EDD_PROVIDER["🔍 Dow Jones Risk & Compliance\nThird-party EDD Provider\nDID #4: did:web:dj-risk-compliance.example.com\nEDD Report: PEP confirmed (FOREIGN_PEP)\nSanctions: CLEAR · Adverse Media: CLEAR"]
    end

    subgraph Transfer["Transfer — AE → CH (PEP EDD VC)"]
        OVASP["🏦 DIFC Digital Asset Exchange LLC\nOriginating VASP · AE (DIFC)\nDID #3: did:web:difc-dax.example.ae\nLEI: 529900T8BM49AAMSDO55\nOnboarding: EUDI_WALLET + EDD\nRisk: HIGH (720) · EDD · ENHANCED monitoring\nVC types: EDDAttestation + PEPAttestation"]
        BVASP["🏦 Swiss Digital Finance AG · CH\nLEI: 549300FJPOIUJ7U9LV82"]
        B["🏢 Geneva Capital Management SA · CH\nAccount: CH5604835012345678009"]
    end

    WALLET -- "Presents Austrian PID via OpenID4VP\n(AMLR Art. 22(5) remote CDD)" --> OVASP
    UAE_ID -- "Cross-reference verification" --> OVASP
    EDD_PROVIDER -- "EDD Report — PEP confirmed\n(AMLR Art. 28 mandatory EDD)" --> OVASP
    OVASP -- "Issues EDDAttestation + PEPAttestation VC\n125,000 USDC" --> BVASP
    BVASP -- "Credits" --> B

    style PID_AT fill:#dcfce7,stroke:#16a34a
    style WALLET fill:#fee2e2,stroke:#ef4444
    style UAE_ICP fill:#dcfce7,stroke:#16a34a
    style EDD_PROVIDER fill:#dcfce7,stroke:#16a34a
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
    style B fill:#ede9fe,stroke:#7c3aed
```

## DID Triangulation (4 DIDs)

```mermaid
flowchart LR
    D1["DID #1\nFatima's Austrian EUDI Wallet\ndid:ebsi:z4MrTwQ9..."]
    D2["DID #2\nAustrian PID Provider (BMI)\ndid:web:pid-provider\n.bmi.example.at"]
    D3["DID #3\nDIFC DAX (VASP)\ndid:web:difc-dax\n.example.ae"]
    D4["DID #4\nDow Jones Risk & Compliance\n(3rd party EDD provider)\ndid:web:dj-risk-compliance\n.example.com"]

    D2 -- "Issued Austrian PID to" --> D1
    D1 -- "Presented PID (OpenID4VP)" --> D3
    D4 -- "EDD Report evidence" --> D3
    D3 -- "Issues VC (credentialSubject = DID #1)" --> D1
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Onboarding | EUDI_WALLET (Austrian residency PID) |
| Customer | Fatima Noor Al-Rashidi (AE) — FOREIGN_PEP |
| PEP role | Former UAE Minister of Finance (2015–2020) |
| Risk | HIGH (720) — EUDI Wallet does **not** reduce PEP risk |
| Due diligence | EDD mandatory (AMLR Art. 28) |
| Monitoring | ENHANCED, semi-annual |
| Asset / Amount | 125,000 USDC |
| VC types | EDDAttestation, PEPAttestation |
