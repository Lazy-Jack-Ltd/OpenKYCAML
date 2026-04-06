# hybrid-vc-wrapped.json — Structure Diagram

**Scenario:** Hybrid VC-Wrapped — IVMS 101 + KYC Profile + Transaction Monitoring.  
Anna Müller (DE) sends 2.75 ETH to Marco Rossi (IT) via BerlinDeFi GmbH and MilanoChain S.p.A. The full IVMS 101 Travel Rule payload and KYC profile are wrapped in a W3C Verifiable Credential, signed by the originating VASP.

```mermaid
flowchart TD
    subgraph Originator_Side["Originating Side — Germany"]
        O["👤 Anna Katharina Müller\nNaturalPerson · DE\nTax ID: DE-TAXID-77834455891\nDOB: 1990-11-20, Munich\nWallet: 0x71C7656E..."]
        OVASP["🏦 BerlinDeFi GmbH\nOriginating VASP · DE\nDID: did:web:berlindefi.example.com\nLEI: 724500TEHJJ2L5MWSK89"]
    end

    subgraph VC_Envelope["VC Wrapper (TravelRuleAttestation)"]
        VC["📜 OpenKYCAML Verifiable Credential\n─────────────────────────────\nType: TravelRuleAttestation\nIssuer: did:web:berlindefi.example.com\nSubject: did:example:customer:CUST-DE-0009823\nProof: Ed25519Signature2020\n─────────────────────────────\ncredentialSubject.ivms101 (full payload)\ncredentialSubject.kycProfile\n  Risk: LOW · SDD\n  PEP: Not PEP\n  Sanctions: CLEAR"]
    end

    subgraph Beneficiary_Side["Beneficiary Side — Italy"]
        BVASP["🏦 MilanoChain S.p.A.\nBeneficiary VASP · IT\nLEI: 815600E86C0C8A1F1804"]
        B["👤 Marco Rossi\nNaturalPerson · IT\nFiscal Code: RSSMRC85T10F205F\nWallet: 0xAb5801a7..."]
    end

    O -- "2.75 ETH" --> OVASP
    OVASP -- "Signs VC (IVMS 101 + kycProfile embedded)" --> VC_Envelope
    VC_Envelope -- "Transmits VC via TRP\n2.75 ETH" --> BVASP
    BVASP -- "Credits account" --> B

    style O fill:#dbeafe,stroke:#3b82f6
    style OVASP fill:#fef9c3,stroke:#eab308
    style VC fill:#f3e8ff,stroke:#9333ea
    style BVASP fill:#fef9c3,stroke:#eab308
    style B fill:#dbeafe,stroke:#3b82f6
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Message type | Hybrid VC-wrapped (IVMS 101 + kycProfile) |
| VC type | TravelRuleAttestation |
| Originator | Anna Katharina Müller (DE) |
| Beneficiary | Marco Rossi (IT) |
| Asset / Amount | 2.75 ETH |
| Risk | LOW · SDD |
| Originating VASP | BerlinDeFi GmbH (DE) |
| Beneficiary VASP | MilanoChain S.p.A. (IT) |
