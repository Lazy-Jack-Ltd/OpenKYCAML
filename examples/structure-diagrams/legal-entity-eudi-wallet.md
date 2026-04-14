# legal-entity-eudi-wallet.json — Structure Diagram

**Scenario:** EUDI Wallet KYC — Legal Entity with LPID and Director Mandate.  
Global Trade Solutions GmbH (DE) onboards at Deutsche Krypto Bank AG by presenting its eIDAS 2.0 LPID from the German company EUDI Wallet, issued by Bundesanzeiger. Director Hans Bauer presents a QEAA mandate confirming his power of representation. UBO: Hans Friedrich Bauer (75% direct).

```mermaid
flowchart TD
    subgraph Identity_Chain["Identity & Trust Chain — EUDI Wallet"]
        LPID_ISSUER["🏛️ Bundesanzeiger\n(German Commercial Register)\nDID #2: did:web:lpid-provider\n.bundesanzeiger.example.de\nIssues LPID + QEAA Mandate"]

        COMPANY_WALLET["🏢 Global Trade Solutions GmbH\nCompany EUDI Wallet\nDID #1: did:ebsi:z2JJFoq4joyXKABBGe7mJmN5\nLEI: 5299002E54U7O0MHZL76\nEUID: DE-FFM-HRB-12345"]

        DIRECTOR_WALLET["👤 Hans Friedrich Bauer\n(Managing Director)\nPersonal EUDI Wallet\nDID #3: did:web:pid-provider.bsi\nDE National ID: DE-IDCARD-T880012456\nDOB: 1972-03-14, Stuttgart"]

        UBO["👤 Hans Friedrich Bauer\nUBO · DE · 75% direct shareholding\nVerified via EUDI Wallet PID\nControl: SHAREHOLDING · DIRECT"]

        LPID_ISSUER -- "Issues LPID VC\n(Company identity)" --> COMPANY_WALLET
        LPID_ISSUER -- "Issues QEAA Mandate VC\n(Power of representation)" --> DIRECTOR_WALLET
        DIRECTOR_WALLET -- "Also serves as UBO" --> UBO
    end

    subgraph Transfer["Travel Rule Transfer — DE → SG"]
        OVASP["🏦 Deutsche Krypto Bank AG\nOriginating VASP · DE\nDID #4: did:web:deutsche-krypto-bank.example.de\nLEI: 724500TEHJJ2L5MWSK89\nIssues LegalEntityKYCAttestation\nRisk: MEDIUM · CDD · EUDI_WALLET"]
        BVASP["🏦 MAS-Licensed Digital Assets Exchange\nBeneficiary VASP · SG\nLEI: 529900T8BM49AAMSDO55"]
        B["🏢 Pacific Rim Investments Pte Ltd · SG\nLEI: 335800ZETG7B8I3S5X35\nAccount: SG29DBSS0000000012345678"]
    end

    COMPANY_WALLET -- "Presents LPID via OpenID4VP" --> OVASP
    DIRECTOR_WALLET -- "Presents QEAA Mandate + PID\nvia OpenID4VP" --> OVASP
    OVASP -- "Issues VC + IVMS 101\n250,000 EUR" --> BVASP
    BVASP -- "Credits account" --> B

    style LPID_ISSUER fill:#dcfce7,stroke:#16a34a
    style COMPANY_WALLET fill:#ede9fe,stroke:#7c3aed
    style DIRECTOR_WALLET fill:#dbeafe,stroke:#3b82f6
    style UBO fill:#dbeafe,stroke:#3b82f6
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
    style B fill:#ede9fe,stroke:#7c3aed
```

## Beneficial Ownership

```mermaid
flowchart TD
    UBO["👤 Hans Friedrich Bauer · DE\nUBO · 75% direct\nDOB: 1972-03-14"]
    SUBJECT["🏢 Global Trade Solutions GmbH · DE\nSubject VASP\nLEI: 5299002E54U7O0MHZL76"]

    UBO -- "75% direct shareholding\n(SHAREHOLDING · DIRECT · depth 1)" --> SUBJECT
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Onboarding | EUDI_WALLET |
| Originator | Global Trade Solutions GmbH (DE) — LPID + QEAA Mandate |
| UBO | Hans Friedrich Bauer (75% direct) |
| Beneficiary | Pacific Rim Investments Pte Ltd (SG) |
| Asset / Amount | 250,000 EUR |
| Risk | MEDIUM · CDD |
| Evidence | LPID (Bundesanzeiger), QEAA Mandate, Director PID |
| VC type | LegalEntityKYCAttestation |
