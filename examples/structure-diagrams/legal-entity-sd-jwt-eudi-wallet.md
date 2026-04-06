# legal-entity-sd-jwt-eudi-wallet.json — Structure Diagram

**Scenario:** SD-JWT Selective Disclosure — Legal Entity (EUDI Wallet LPID).  
Acme Digital Trading SL (ES) onboards at Swiss Digital Finance AG (CH) by presenting a Spanish LPID credential via SD-JWT VC / OpenID4VP. The entity discloses its legal name, LEI, and country of registration but withholds its VAT number and registered address.

```mermaid
flowchart TD
    subgraph LPID_Layer["LPID Credential Layer"]
        LPID_ISSUER["🏛️ Agencia Tributaria (ES)\nDID: did:web:lpid-provider\n.agencia-tributaria.example.es\nIssues SD-JWT LPID VC\n(OpenID4VP+SD-JWT)"]
        ENTITY_WALLET["🏢 Acme Digital Trading SL\nDID: did:web:acme-digital-trading.example.es\nES CIF: B87654321\nHolds SD-JWT LPID VC"]
        LPID_ISSUER -- "Issues Spanish LPID\n(eIDAS 2.0 Legal Person ID — SD-JWT VC)" --> ENTITY_WALLET
    end

    subgraph Disclosure["Selective Disclosure at Presentation"]
        direction LR
        REVEALED["✅ DISCLOSED to VASP\n─────────────────\n• legal_name: Acme Digital Trading SL\n• legal_person_identifier: ES-CIF-B87654321\n• country_of_registration: ES\n• lei: 549300XY1234ABCD5678"]
        WITHHELD["🔒 WITHHELD (GDPR minimisation)\n─────────────────\n• registered_address:\n  Calle Gran Via 28, Madrid 28013\n• vat_number: ESB87654321\n(SHA-256 digests only in _sd array)"]
    end

    subgraph VASP_Layer["VASP Layer — CH"]
        BVASP["🏦 Swiss Digital Finance AG\nVASP · CH\nDID: did:web:swiss-digital-finance.example.ch\nLEI: 549300FJPOIUJ7U9LV82\nVerifies SD-JWT LPID signature\nRisk: MEDIUM · CDD · EUDI_WALLET"]
        B["🏢 Swiss Digital Finance AG\nAccount: CH5604835012345678009\n(Beneficiary of intra-chain transfer)"]
    end

    ENTITY_WALLET -- "Presents SD-JWT LPID\n(selective disclosures appended after ~)" --> BVASP
    REVEALED -- "Appended as disclosures" --> BVASP
    WITHHELD -- "SHA-256 digests only\n(not revealed in this presentation)" --> BVASP
    BVASP -- "Issues OpenKYCAML KYCAttestation VC\n25,000 USDC" --> B

    style LPID_ISSUER fill:#dcfce7,stroke:#16a34a
    style ENTITY_WALLET fill:#ede9fe,stroke:#7c3aed
    style REVEALED fill:#dcfce7,stroke:#16a34a
    style WITHHELD fill:#fee2e2,stroke:#ef4444
    style BVASP fill:#fef9c3,stroke:#eab308
    style B fill:#fef9c3,stroke:#eab308
```

## SD-JWT Disclosure Summary

```mermaid
flowchart LR
    LPID["Spanish LPID\n(SD-JWT VC, full payload)"]
    D1["legal_name\n✅ disclosed"]
    D2["legal_person_identifier\n✅ disclosed"]
    D3["country_of_registration\n✅ disclosed"]
    D4["lei\n✅ disclosed"]
    D5["registered_address\n🔒 withheld"]
    D6["vat_number\n🔒 withheld"]

    LPID --> D1 & D2 & D3 & D4 & D5 & D6
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Format | SD-JWT VC via OpenID4VP+SD-JWT |
| Originator | Acme Digital Trading SL (ES) |
| Beneficiary VASP | Swiss Digital Finance AG (CH) |
| Disclosed claims | legal_name, identifier, country, LEI |
| Withheld claims | registered_address, vat_number |
| Asset / Amount | 25,000 USDC |
| Risk | MEDIUM · CDD |
| Privacy basis | GDPR data-minimisation (Art. 5(1)(c)) |
