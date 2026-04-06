# legal-entity-plain.json — Structure Diagram

**Scenario:** Legal Entity IVMS 101 Travel Rule — Plain (no VC wrapper).  
Global Trade Solutions GmbH (DE) sends 500,000 USD to Pacific Rim Investments Pte Ltd (SG) via two VASPs.

```mermaid
flowchart TD
    subgraph Originator_Side["Originating Side — Germany"]
        O["🏢 Global Trade Solutions GmbH\nLegalPerson · DE\nLEI: 5299002E54U7O0MHZL76 (LEIX)\nShort name: GTS\nFrankfurter Allee 100, Frankfurt\nCustomer: CORP-DE-0001234\nAccounts: DE89370400440532013000\n          0xd8dA6BF..."]
        OVASP["🏦 Deutsche Krypto Bank AG\nOriginating VASP · DE"]
    end

    subgraph Beneficiary_Side["Beneficiary Side — Singapore"]
        BVASP["🏦 MAS-Licensed Digital Assets Exchange\nBeneficiary VASP · SG"]
        B["🏢 Pacific Rim Investments Pte Ltd\nLegalPerson · SG\nLEI: 335800ZETG7B8I3S5X35 (LEIX)\nShort names: PRI / Pacific Rim\n1 Raffles Place, Singapore\nAccount: SG29DBSS0000000012345678"]
    end

    O -- "Initiates transfer\n500,000 USD" --> OVASP
    OVASP -- "IVMS 101 Travel Rule message\n(plain — no VC wrapper)\n500,000 USD" --> BVASP
    BVASP -- "Credits account" --> B

    style O fill:#ede9fe,stroke:#7c3aed
    style B fill:#ede9fe,stroke:#7c3aed
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Message type | IVMS 101 plain (no VC wrapper) |
| Originator | Global Trade Solutions GmbH, DE legal entity |
| Beneficiary | Pacific Rim Investments Pte Ltd, SG legal entity |
| Asset / Amount | 500,000 USD |
| Originating VASP | Deutsche Krypto Bank AG (DE) |
| Beneficiary VASP | MAS-Licensed Digital Assets Exchange (SG) |
| ID type | LEI (LEIX) for both entities |
