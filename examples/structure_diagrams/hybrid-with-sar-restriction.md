# hybrid-with-sar-restriction.json — Structure Diagram

**Scenario:** SAR Restriction + Tipping-Off Protection.  
Acme Crypto Exchange BV (NL) has filed a Suspicious Activity Report (SAR) on customer Pieter Van Houten after detecting anomalous transaction patterns. SAR-restricted fields are cryptographically withheld via SD-JWT and protected by tipping-off rules (AMLR Art. 73). The data subject and counterparty VASP must never learn of the SAR.

```mermaid
flowchart TD
    subgraph Customer["Customer — SAR Subject"]
        O["👤 Pieter Jan Van Houten\nNaturalPerson · NL\nBSN: NL-BSN-012345678\nDOB: 1985-03-22, Rotterdam\nWallet: 0x9F8e7D6c..."]
        RISK["⚠️ Risk Profile\n─────────────────────────\nOverall: HIGH (score 740)\nProduct: HIGH / Customer type: HIGH\nTransaction: HIGH\nDue Diligence: EDD\nAnomaly: 3 large cross-border\ntransfers detected"]
    end

    subgraph SAR_Section["🔴 SAR RESTRICTED — Tipping-Off Protected\n(AMLR Art. 73 — MUST NOT be disclosed to subject or counterparty)"]
        SAR_FIELDS["🔒 SAR-Restricted Fields\n─────────────────────────\n• adverseMedia (suspicious patterns)\n• sarFilingReference (internal SAR ID)\n• internalSuspicionFlag (true)\n─────────────────────────────\nSDJWT: SHA-256 digests in _sd array\nNO plaintext disclosures appended\nClassification: sar_restricted\ntippingOffProtected: true"]
        RECIPIENTS["Allowed Recipients:\n• FIU only\n• Law enforcement\n• Internal AML compliance team\n─────────────────────────────\nProhibited Recipients:\n• Data subject (Pieter)\n• Counterparty VASP\n• Third parties without supervisory approval"]
    end

    subgraph Transfer["Suspicious Transfer"]
        OVASP["🏦 Acme Crypto Exchange BV · NL\nOriginating VASP\nDID: did:web:acme-crypto.example.nl\nLEI: 724500VNNHZHYDLFMO70\nOnboarding: IN_PERSON\nVC issuer — SAR-restricted fields withheld"]
        B["⚠️ Unknown External Wallet\nBeneficiary: UNKNOWN\nWallet: 0x1A2b3C4d..."]
        BVASP["⚠️ Unknown External Wallet\nBeneficiary VASP: UNKNOWN"]
    end

    O -- "Suspicious transfer pattern" --> OVASP
    O -.-> RISK
    RISK -- "Triggers SAR filing" --> SAR_FIELDS
    SAR_FIELDS -.-> RECIPIENTS
    OVASP -- "Transfer (flagged internally)\nSD-JWT VC — SAR fields\nnever disclosed in presentation" --> BVASP
    BVASP --> B

    style O fill:#fee2e2,stroke:#ef4444
    style RISK fill:#fef3c7,stroke:#f59e0b
    style SAR_FIELDS fill:#fee2e2,stroke:#ef4444
    style RECIPIENTS fill:#fee2e2,stroke:#ef4444
    style OVASP fill:#fef9c3,stroke:#eab308
    style B fill:#e5e7eb,stroke:#6b7280
    style BVASP fill:#e5e7eb,stroke:#6b7280
```

## SD-JWT SAR Protection Mechanism

```mermaid
flowchart LR
    JWT["Issuer-JWT\n_sd: [sha256(adverseMedia),\n       sha256(sarFilingReference),\n       sha256(internalSuspicionFlag)]\nOther claims: plaintext"]
    DISCLOSED["~Disclosed to RP\nname, address,\nsanctions_status"]
    WITHHELD["SAR fields:\nNO disclosures appended\nDigests only in _sd\n(cryptographically hidden)"]

    JWT -- "Shared" --> DISCLOSED
    JWT -. "Never appended" .-> WITHHELD
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Subject | Pieter Jan Van Houten (NL) |
| Risk | HIGH (740) · EDD |
| SAR status | FILED — tipping-off protected |
| Legal basis | AMLR Art. 73 (tipping-off prohibition) |
| GDPR classification | `sar_restricted` |
| SD-JWT mechanism | SAR fields: digests only, no disclosures |
| Allowed recipients | FIU, Law Enforcement, Internal AML only |
| VASP | Acme Crypto Exchange BV (NL) |
