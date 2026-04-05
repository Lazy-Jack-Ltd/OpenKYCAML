# natural-person-eudi-wallet.json — Structure Diagram

**Scenario:** EUDI Wallet KYC Onboarding — Natural Person.  
Anna Müller (DE) onboards at Acme Crypto Exchange BV (NL) by presenting her German eIDAS 2.0 PID from her EU Digital Identity Wallet via OpenID4VP. Three DIDs triangulate the identity chain.

```mermaid
flowchart TD
    subgraph Identity_Chain["Identity & Trust Chain"]
        direction TB
        PID_ISSUER["🏛️ German PID Provider\nBundesamt für Sicherheit\nin der Informationstechnik\nDID #2: did:web:pid-provider.bsi.example.de"]
        WALLET["📱 Anna Müller's EUDI Wallet\nDID #1: did:ebsi:z2LSzT7LiUNMxKKyGCnNjNT\nDE National ID: DE-IDCARD-T220001293\nDOB: 1990-11-20, Munich"]
        PID_ISSUER -- "Issues eIDAS 2.0 PID VC\n(German National ID Card)" --> WALLET
    end

    subgraph Transfer["Travel Rule Transfer"]
        direction LR
        OVASP["🏦 Acme Crypto Exchange BV\nOriginating + Beneficiary VASP · NL\nDID #3: did:web:acme-crypto.example.nl\nLEI: 724500VNNHZHYDLFMO70\nOnboarding: EUDI_WALLET\nRisk: LOW · SDD"]
        B["👤 Pieter Van der Berg\nNaturalPerson · NL\nBSN: NL-BSN-987654321\nWallet: 0xd8dA6BF..."]
    end

    WALLET -- "Presents PID via OpenID4VP\n(evidence recorded in VC)" --> OVASP
    OVASP -- "Issues OpenKYCAML VC\n(KYCAttestation)\nIVMS101 + kycProfile embedded\n0.15 ETH (intra-VASP)" --> B

    style PID_ISSUER fill:#dcfce7,stroke:#16a34a
    style WALLET fill:#dbeafe,stroke:#3b82f6
    style OVASP fill:#fef9c3,stroke:#eab308
    style B fill:#dbeafe,stroke:#3b82f6
```

## DID Triangulation

```mermaid
flowchart LR
    D1["DID #1\nSubject Wallet\ndid:ebsi:z2LSzT7..."]
    D2["DID #2\nPID Issuer\ndid:web:pid-provider\n.bsi.example.de"]
    D3["DID #3\nVASP Issuer\ndid:web:acme-crypto\n.example.nl"]

    D2 -- "Issued PID to" --> D1
    D1 -- "Presented PID to (OpenID4VP)" --> D3
    D3 -- "Issues OpenKYCAML VC\nwith credentialSubject = DID #1" --> D1
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Onboarding channel | EUDI_WALLET |
| Originator | Anna Katharina Müller (DE), EUDI Wallet |
| Beneficiary | Pieter Van der Berg (NL) |
| Asset / Amount | 0.15 ETH (intra-VASP transfer) |
| Risk rating | LOW · SDD |
| PEP | No |
| Evidence | German National ID Card (eIDAS 2.0 PID, OpenID4VP) |
| VC type | KYCAttestation |
