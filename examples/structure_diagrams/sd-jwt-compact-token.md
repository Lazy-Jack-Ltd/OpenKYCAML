# sd-jwt-compact-token.json — Structure Diagram

**Scenario:** SD-JWT Compact Token — Annotated Reference Example.  
This file documents the complete structure of an OpenKYCAML SD-JWT VC in its compact serialisation as it travels between an issuer, an EUDI Wallet, and a relying party. Anna Müller selectively discloses only the FATF Travel Rule minimum (name + address) and withholds date of birth, national identifier, and nationality.

```mermaid
flowchart TD
    subgraph Issuance["1. Issuance — VASP issues SD-JWT VC"]
        ISSUER["🏦 Acme Crypto Exchange BV\ndid:web:acme-crypto.example.nl\nSigns Issuer-JWT (ES256)\nOnboarding: EUDI_WALLET\nRisk: LOW · SDD"]
        ISSUER_JWT["📄 Issuer-JWT\n─────────────────────────────\niss: did:web:acme-crypto.example.nl\nsub: did:ebsi:z2LSzT7...\nvct: OpenKYCAMLCredential\n_sd_alg: sha-256\n_sd: [sha256(family_name),\n       sha256(given_name),\n       sha256(address),\n       sha256(birthdate),\n       sha256(national_id),\n       sha256(nationalities)]\nonboarding_channel: EUDI_WALLET\nsanctions_status: CLEAR\ncustomer_risk_rating: LOW\ndue_diligence_type: SDD\ncnf: {jwk: {holder public key}}"]
        ISSUER -- "Signs" --> ISSUER_JWT
    end

    subgraph Wallet["2. Holder — EUDI Wallet stores and presents"]
        HOLDER["📱 Anna Müller's EUDI Wallet\ndid:ebsi:z2LSzT7LiUNMxKKyGCnNjNT\nHolds full SD-JWT including\nall 6 disclosure objects"]

        subgraph Selected_Disclosures["Selected for presentation (FATF min.)"]
            D1["~Disclosure 1\nsalt: 2GLC42sK...\nfamily_name: Müller"]
            D2["~Disclosure 2\nsalt: eluV5Og3...\ngiven_name: Anna Katharina"]
            D3["~Disclosure 3\nsalt: 6Ij7tM-a5...\naddress: {Unter den Linden 77,\n  Berlin 10117, DE}"]
        end

        subgraph Withheld_Disclosures["Withheld (not appended — GDPR)"]
            W1["~~birthdate: 1990-11-20"]
            W2["~~national_identifier: DE-IDCARD-T220001293"]
            W3["~~nationalities: [DE]"]
        end

        HOLDER -- "Selects 3 of 6 disclosures" --> Selected_Disclosures
        HOLDER -- "Withholds (GDPR minimisation)" --> Withheld_Disclosures
    end

    subgraph Presentation["3. Presentation — OpenID4VP to Relying Party"]
        KB_JWT["🔑 Key Binding JWT (KB-JWT)\nnonce: 942b1b52-fd58-4b3f-8e2a...\naud: did:web:beneficiary-vasp\niat: timestamp\nSigned by holder's private key"]
        RP["🏦 Beneficiary VASP\ndid:web:beneficiary-vasp.example.com\nVerifies:\n✅ Issuer-JWT signature\n✅ Disclosed claim hashes match _sd\n✅ KB-JWT nonce + binding\n❌ Cannot see withheld claims"]
    end

    subgraph Token_Format["Compact Token Structure"]
        FORMAT["<Issuer-JWT>~<Disc1>~<Disc2>~<Disc3>~<KB-JWT>\n(single ASCII string, base64url-encoded parts)"]
    end

    ISSUER_JWT --> HOLDER
    Selected_Disclosures --> KB_JWT
    KB_JWT --> RP
    Token_Format -. "format: dc+sd-jwt" .-> RP

    style ISSUER fill:#fef9c3,stroke:#eab308
    style ISSUER_JWT fill:#f3e8ff,stroke:#9333ea
    style HOLDER fill:#dbeafe,stroke:#3b82f6
    style D1 fill:#dcfce7,stroke:#16a34a
    style D2 fill:#dcfce7,stroke:#16a34a
    style D3 fill:#dcfce7,stroke:#16a34a
    style W1 fill:#fee2e2,stroke:#ef4444
    style W2 fill:#fee2e2,stroke:#ef4444
    style W3 fill:#fee2e2,stroke:#ef4444
    style KB_JWT fill:#fef9c3,stroke:#eab308
    style RP fill:#fef9c3,stroke:#eab308
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Format | `dc+sd-jwt` compact token |
| Subject | Anna Katharina Müller (DE) |
| Issuer | Acme Crypto Exchange BV (did:web:acme-crypto.example.nl) |
| Disclosed at presentation | family_name, given_name, address |
| Withheld | birthdate, national_identifier, nationalities |
| Key Binding | KB-JWT (holder-bound, nonce-protected) |
| SD alg | sha-256 |
| Risk | LOW · SDD |
| **Important** | Signature values in this example are PLACEHOLDER stubs — not cryptographically valid |
