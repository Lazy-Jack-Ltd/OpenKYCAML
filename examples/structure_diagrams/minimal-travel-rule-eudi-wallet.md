# minimal-travel-rule-eudi-wallet.json — Structure Diagram

**Scenario:** EUDI Wallet Travel Rule — Minimal. Hiroshi Tanaka (JP) sends 0.05 BTC to Marie Dubois (FR). Marie presents her French eIDAS 2.0 PID at the beneficiary VASP via EUDI Wallet. Originator is a non-EU Japanese customer identified by standard IVMS 101.

```mermaid
flowchart TD
    subgraph JP_Side["Originating Side — Japan"]
        O["👤 Hiroshi Tanaka\nNaturalPerson · JP\nMyNumber: JP-MYNUMBER-1234-5678-9012\nWallet: bc1qar0srrr7..."]
        OVASP["🏦 Tokyo Digital Assets Co., Ltd.\nOriginating VASP · JP\nLEI: 3538003FPHWP7EM5C773\n(Non-EU — standard IVMS 101)"]
    end

    subgraph FR_EUDI["Beneficiary Side — France (EUDI Wallet)"]
        PID_ISSUER["🏛️ French PID Provider (ANSSI)\nDID #2: did:web:pid-provider\n.anssi.example.fr\nIssues FR eIDAS 2.0 PID"]
        WALLET["📱 Marie Dubois — EUDI Wallet\nDID #1: did:ebsi:z3KpWqR8mTvXnYbZhFjLcGaE\nFR National ID: FR-CNI-1234567890123\nDOB withheld · Rue de Rivoli, Paris"]
        BVASP["🏦 CryptoFrance SAS\nBeneficiary VASP · FR\nDID #3: did:web:cryptofrance.example.fr\nLEI: 969500T6EEF8MJKQ5541\nIssues Travel Rule VC after PID verification"]
        B["👤 Marie Élise Dubois\nNaturalPerson · FR · Wallet: bc1p0xlxvlh..."]
        PID_ISSUER -- "Issues eIDAS 2.0 PID VC\n(FR National ID Card CNIe)" --> WALLET
        WALLET -- "Presents PID via OpenID4VP" --> BVASP
        BVASP -- "Credits account" --> B
    end

    O -- "Initiates 0.05 BTC transfer" --> OVASP
    OVASP -- "IVMS 101 Travel Rule message\n0.05 BTC" --> BVASP

    style O fill:#dbeafe,stroke:#3b82f6
    style OVASP fill:#fef9c3,stroke:#eab308
    style PID_ISSUER fill:#dcfce7,stroke:#16a34a
    style WALLET fill:#dbeafe,stroke:#3b82f6
    style BVASP fill:#fef9c3,stroke:#eab308
    style B fill:#dbeafe,stroke:#3b82f6
```

## DID Triangulation (Beneficiary Side)

```mermaid
flowchart LR
    D1["DID #1\nMarie's EUDI Wallet\ndid:ebsi:z3KpWqR8..."]
    D2["DID #2\nFrench PID Provider\ndid:web:pid-provider\n.anssi.example.fr"]
    D3["DID #3\nCryptoFrance SAS\ndid:web:cryptofrance\n.example.fr"]

    D2 -- "Issued PID to" --> D1
    D1 -- "Presented PID via OpenID4VP" --> D3
    D3 -- "Issues Travel Rule VC\n(credentialSubject = DID #1)" --> D1
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Originator | Hiroshi Tanaka (JP) — standard IVMS 101, non-EU |
| Beneficiary | Marie Élise Dubois (FR) — eIDAS 2.0 PID via EUDI Wallet |
| Asset / Amount | 0.05 BTC |
| Originating VASP | Tokyo Digital Assets Co., Ltd. (JP) |
| Beneficiary VASP | CryptoFrance SAS (FR) |
| Beneficiary onboarding | EUDI_WALLET (OpenID4VP) |
| VC type | TravelRuleAttestation |
