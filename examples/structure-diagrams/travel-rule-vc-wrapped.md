# travel-rule-vc-wrapped.json — Structure Diagram

**Scenario:** Travel Rule VC-Wrapped with Transaction Monitoring.  
Pieter Jan Van Dijk (NL) sends 0.5 BTC to Thomas James Hargreaves (GB). The full IVMS 101 payload is wrapped inside a W3C Verifiable Credential, signed by the originating VASP and transmitted to the beneficiary VASP. Transaction monitoring evaluates three rules.

```mermaid
flowchart TD
    subgraph Originator_Side["Originating Side — Netherlands"]
        O["👤 Pieter Jan Van Dijk\nNaturalPerson · NL\nPassport: NL-PASSPORT-AB123456\nDOB: 1985-04-05, Amsterdam\nWallet: bc1qxy2kgdygjr..."]
        OVASP["🏦 Acme Crypto Exchange BV\nOriginating VASP · NL\nDID: did:web:acme-crypto.example.nl\nLEI: 724500VNNHZHYDLFMO70"]
    end

    subgraph VC_Envelope["VC Wrapper (TravelRuleAttestation)"]
        VC["📜 OpenKYCAML Verifiable Credential\n─────────────────────────────\nType: TravelRuleAttestation\nIssuer: did:web:acme-crypto.example.nl\nSubject: did:example:customer:CUST-NL-0000042\nProof: Ed25519Signature2020\n─────────────────────────────\ncredentialSubject.ivms101\n  (full originator + beneficiary data)"]
    end

    subgraph TM["Transaction Monitoring"]
        TM_ENGINE["⚙️ Acme TM Suite v2.3\n─────────────────────────────\n✅ RULE-VEL-001 PASS: 0.5 BTC < 5 BTC/7d limit\n✅ RULE-TR-001 PASS: ~14,750 EUR > 1,000 EUR threshold\n   Travel Rule applicable — IVMS 101 transmitted\n✅ RULE-GEO-001 PASS: NL + GB low-risk jurisdictions\n─────────────────────────────\nOverall: CLEAR · COMPLIANT"]
    end

    subgraph Beneficiary_Side["Beneficiary Side — United Kingdom"]
        BVASP["🏦 FinTech Exchange Ltd\nBeneficiary VASP · GB\nLEI: 213800WSGIIZCXF1P572\nVerifies VC signature via TRP"]
        B["👤 Thomas James Hargreaves\nNaturalPerson · GB\nPassport: GB-PASSPORT-HF987654\nWallet: 3J98t1WpEZ73CN..."]
    end

    O -- "0.5 BTC" --> OVASP
    OVASP -- "Signs VC" --> VC_Envelope
    OVASP -- "Evaluates" --> TM
    VC_Envelope -- "Transmits VC via TRP\n(IVMS 101 payload embedded)" --> BVASP
    BVASP -- "Credits account" --> B

    style O fill:#dbeafe,stroke:#3b82f6
    style OVASP fill:#fef9c3,stroke:#eab308
    style VC fill:#f3e8ff,stroke:#9333ea
    style TM_ENGINE fill:#ecfdf5,stroke:#059669
    style BVASP fill:#fef9c3,stroke:#eab308
    style B fill:#dbeafe,stroke:#3b82f6
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Message type | VC-wrapped IVMS 101 |
| VC type | TravelRuleAttestation |
| Originator | Pieter Jan Van Dijk, NL |
| Beneficiary | Thomas James Hargreaves, GB |
| Asset / Amount | 0.5 BTC (~14,750 EUR) |
| Travel Rule threshold | 1,000 EUR (NL jurisdiction) |
| Compliance status | COMPLIANT |
| TM outcome | CLEAR (3 rules PASS) |
| Transmission protocol | TRP (Travel Rule Protocol) |
