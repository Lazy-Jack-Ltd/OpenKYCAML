# travel-rule-vc-eudi-wallet.json — Structure Diagram

**Scenario:** EUDI Wallet Travel Rule VC — Full VC wrapper with EUDI PID, transaction monitoring and multi-DID triangulation.  
Pieter Jan Van Dijk (NL) sends 0.5 BTC to Thomas James Hargreaves (GB). Pieter Jan presents his Dutch EUDI Wallet PID at Acme Crypto. The IVMS 101 payload is VC-wrapped, signed by the originating VASP, and acknowledged by the beneficiary VASP via TRP.

```mermaid
flowchart TD
    subgraph NL_Identity["Identity Chain — Netherlands (Originator)"]
        PID_NL["🏛️ Dutch PID Provider (RVO)\nDID #2: did:web:pid-provider.rvo.example.nl\nIssues NL eIDAS 2.0 PID"]
        WALLET_S["📱 Pieter Jan Van Dijk — EUDI Wallet (NL)\nDID #1: did:ebsi:zABkFm2PRPvLxNksMqJdVHK7\nNL Passport: NL-PASSPORT-AB123456"]
        PID_NL -- "Issues eIDAS 2.0 PID VC\n(Dutch National PID via DigiD)" --> WALLET_S
    end

    subgraph VASPs["VASP Layer"]
        OVASP["🏦 Acme Crypto Exchange BV · NL\nDID #3: did:web:acme-crypto.example.nl\nLEI: 724500VNNHZHYDLFMO70\nIssues Travel Rule VC after PID verification"]
        BVASP["🏦 FinTech Exchange Ltd · GB\nDID #4: did:web:fintech-exchange.example.gb\nLEI: 213800WSGIIZCXF1P572\nAccepts VC via TRP"]
    end

    subgraph TM["Transaction Monitoring — Acme TM Suite v3.1"]
        TM_RESULT["⚙️ Overall: CLEAR · COMPLIANT\n─────────────────────────\n✅ RULE-VEL-001 PASS: 0.5 BTC < 5 BTC/7d\n✅ RULE-TR-001 PASS: ~46,500 EUR > 1,000 EUR\n✅ RULE-GEO-001 PASS: NL low-risk EU / GB equiv.\n✅ RULE-EUDI-001 PASS: eIDAS 2.0 LoA High\n   Identity assurance reduces AMLR Art. 22(5) risk"]
    end

    subgraph UK_Side["Beneficiary Side — United Kingdom"]
        B["👤 Thomas James Hargreaves · GB\nPassport: GB-PASSPORT-HF987654\nWallet: 3J98t1WpEZ73CN..."]
    end

    WALLET_S -- "Presents PID via OpenID4VP" --> OVASP
    OVASP -- "Signs VC (TravelRuleAttestation)\nembeds full IVMS 101 payload" --> VASPs
    OVASP -- "Evaluates 4 rules" --> TM
    BVASP -- "Acknowledges via TRP" --> VASPs
    BVASP -- "Credits account" --> B

    style PID_NL fill:#dcfce7,stroke:#16a34a
    style WALLET_S fill:#dbeafe,stroke:#3b82f6
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
    style TM_RESULT fill:#ecfdf5,stroke:#059669
    style B fill:#dbeafe,stroke:#3b82f6
```

## Multi-DID Triangulation

```mermaid
flowchart LR
    D1["DID #1\nPieter Jan's EUDI Wallet\ndid:ebsi:zABkFm2PRPv..."]
    D2["DID #2\nDutch PID Provider (RVO)\ndid:web:pid-provider\n.rvo.example.nl"]
    D3["DID #3\nAcme Crypto (Orig. VASP)\ndid:web:acme-crypto\n.example.nl"]
    D4["DID #4\nFinTech Exchange (Ben. VASP)\ndid:web:fintech-exchange\n.example.gb"]

    D2 -- "Issued PID to" --> D1
    D1 -- "Presented PID (OpenID4VP)" --> D3
    D3 -- "Issues VC + transmits via TRP" --> D4
    D3 -- "VC credentialSubject = DID #1" --> D1
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| VC type | TravelRuleAttestation (EUDI Wallet) |
| Originator | Pieter Jan Van Dijk (NL) — Dutch EUDI Wallet PID |
| Beneficiary | Thomas James Hargreaves (GB) |
| Asset / Amount | 0.5 BTC (~46,500 EUR) |
| Travel Rule | COMPLIANT, threshold 1,000 EUR (NL) |
| Identity assurance | eIDAS 2.0 LoA High — AMLR Art. 22(5) |
| TM rules | 4 PASS — CLEAR |
| Transmission | TRP (Travel Rule Protocol) |
