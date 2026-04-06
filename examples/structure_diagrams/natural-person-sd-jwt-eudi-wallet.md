# natural-person-sd-jwt-eudi-wallet.json — Structure Diagram

**Scenario:** SD-JWT Selective Disclosure — Natural Person (EUDI Wallet).  
Anna Müller (DE) presents a German eIDAS 2.0 PID via SD-JWT VC in OpenID4VP. She discloses only her legal name and residential address (FATF Travel Rule minimum) and withholds date of birth, place of birth, and nationality under GDPR data-minimisation.

```mermaid
flowchart TD
    subgraph PID_Layer["PID Credential Layer"]
        PID_ISSUER["🏛️ German PID Provider (BSI)\nDID: did:web:pid-provider.bsi.example.de\nIssues SD-JWT VC (OpenID4VP+SD-JWT)"]
        WALLET["📱 Anna Müller — EUDI Wallet\nDID: did:ebsi:z2LSzT7LiUNMxKKyGCnNjNT\nHolds SD-JWT PID VC"]
        PID_ISSUER -- "Issues SD-JWT PID VC\n_sd digests for all claims" --> WALLET
    end

    subgraph Disclosure["Selective Disclosure at Presentation"]
        direction LR
        REVEALED["✅ DISCLOSED to VASP\n─────────────────\n• family_name: Müller\n• given_name: Anna Katharina\n• address: Unter den Linden 77,\n  Berlin 10117, DE"]
        WITHHELD["🔒 WITHHELD (GDPR minimisation)\n─────────────────\n• birthdate: 1990-11-20\n• place_of_birth: Munich, DE\n• nationalities: [DE]\n(SHA-256 digests only in _sd array)"]
    end

    subgraph VASP_Layer["VASP Layer"]
        OVASP["🏦 Acme Crypto Exchange BV · NL\nDID: did:web:acme-crypto.example.nl\nVerifies SD-JWT signature WITHOUT\nseeing withheld claim values\nRisk: LOW · SDD · EUDI_WALLET"]
        B["👤 Pieter Van der Berg · NL\nWallet: 0xd8dA6BF...\nBeneficiary"]
    end

    WALLET -- "Presents SD-JWT VC\n(selective disclosures appended after ~)" --> OVASP
    REVEALED -- "Appended as disclosure objects\nafter ~ separator" --> OVASP
    WITHHELD -- "SHA-256 digests only\n(never revealed in this presentation)" --> OVASP
    OVASP -- "Issues OpenKYCAML VC\n0.15 ETH" --> B

    style PID_ISSUER fill:#dcfce7,stroke:#16a34a
    style WALLET fill:#dbeafe,stroke:#3b82f6
    style REVEALED fill:#dcfce7,stroke:#16a34a
    style WITHHELD fill:#fee2e2,stroke:#ef4444
    style OVASP fill:#fef9c3,stroke:#eab308
    style B fill:#dbeafe,stroke:#3b82f6
```

## SD-JWT Token Structure

```mermaid
flowchart LR
    JWT["Issuer-JWT\nheader.payload.signature\n─────────────────\n_sd: [digest1, digest2, digest3]\nonboarding_channel: EUDI_WALLET\nsanctions_status: CLEAR\ncustomer_risk_rating: LOW"]
    D1["~Disclosure 1\nfamily_name: Müller"]
    D2["~Disclosure 2\ngiven_name: Anna Katharina"]
    D3["~Disclosure 3\naddress: {Berlin...}"]
    KB["~KB-JWT\nKey Binding JWT\n(nonce + audience)"]

    JWT --> D1 --> D2 --> D3 --> KB
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Format | SD-JWT VC (dc+sd-jwt) via OpenID4VP+SD-JWT |
| Disclosed claims | family_name, given_name, address |
| Withheld claims | birthdate, place_of_birth, nationalities |
| Privacy basis | GDPR data-minimisation (Art. 5(1)(c)) |
| Asset / Amount | 0.15 ETH (intra-VASP) |
| Risk | LOW · SDD |
