# hybrid-vc-eudi-wallet.json — Structure Diagram

**Scenario:** EUDI Wallet Hybrid VC — Natural Person, full IVMS 101 + kycProfile.  
Anna Müller (DE) sends 2.75 ETH to Marco Rossi (IT) via BerlinDeFi GmbH → MilanoChain S.p.A. Anna is identified via German EUDI Wallet PID. This is the EUDI Wallet companion to hybrid-vc-wrapped.json, adding a 4-DID trust triangle.

```mermaid
flowchart TD
    subgraph Identity_Chain["Identity Chain — Germany (EUDI Wallet)"]
        PID_DE["🏛️ German PID Provider (BSI)\nDID #2: did:web:pid-provider.bsi.example.de\nIssues DE eIDAS 2.0 PID"]
        WALLET["📱 Anna Müller — EUDI Wallet (DE)\nDID #1: did:ebsi:z2LSzT7LiUNMxKKyGCnNjNT\nDE National ID: DE-IDCARD-T220001293\nDOB: 1990-11-20, Munich"]
        PID_DE -- "Issues German PID VC" --> WALLET
    end

    subgraph Transfer["Travel Rule Transfer — DE → IT"]
        OVASP["🏦 BerlinDeFi GmbH · DE\nDID #3: did:web:berlindefi.example.com\nLEI: 724500TEHJJ2L5MWSK89\nOnboarding: EUDI_WALLET\nRisk: LOW · SDD\nIssues TravelRuleAttestation VC"]
        BVASP["🏦 MilanoChain S.p.A. · IT\nDID #4: referenced in proof\nLEI: 815600E86C0C8A1F1804"]
        B["👤 Marco Rossi · IT\nFiscal Code: RSSMRC85T10F205F\nWallet: 0xAb5801a7..."]
    end

    WALLET -- "Presents PID via OpenID4VP\n(evidence recorded in VC)" --> OVASP
    OVASP -- "Signs TravelRuleAttestation VC\nIVMS 101 + kycProfile embedded\n2.75 ETH" --> BVASP
    BVASP -- "Credits account" --> B

    style PID_DE fill:#dcfce7,stroke:#16a34a
    style WALLET fill:#dbeafe,stroke:#3b82f6
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
    style B fill:#dbeafe,stroke:#3b82f6
```

## DID Triangulation (4 DIDs)

```mermaid
flowchart LR
    D1["DID #1\nAnna's EUDI Wallet\ndid:ebsi:z2LSzT7..."]
    D2["DID #2\nGerman PID Provider (BSI)\ndid:web:pid-provider\n.bsi.example.de"]
    D3["DID #3\nBerlinDeFi GmbH\n(Orig. VASP)\ndid:web:berlindefi\n.example.com"]
    D4["DID #4\nMilanoChain S.p.A.\n(Ben. VASP)\nReferenced in proof"]

    D2 -- "Issued PID to" --> D1
    D1 -- "Presented PID (OpenID4VP)" --> D3
    D3 -- "Issues VC + transmits to" --> D4
    D3 -- "VC credentialSubject = DID #1" --> D1
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Onboarding | EUDI_WALLET (German PID, OpenID4VP) |
| VC type | TravelRuleAttestation |
| Originator | Anna Katharina Müller (DE) — EUDI Wallet |
| Beneficiary | Marco Rossi (IT) |
| Asset / Amount | 2.75 ETH |
| Risk | LOW · SDD |
| Originating VASP | BerlinDeFi GmbH (DE) |
| Beneficiary VASP | MilanoChain S.p.A. (IT) |
