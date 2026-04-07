# complex-group-multi-tier.json — Structure Diagram

**Scenario:** Complex Multi-Tier Corporate Group — 4-Layer Holding Structure with Natural Person Directors.  
Nexus Global Ventures Ltd (KY VASP) is controlled by one UBO (Marcus Van Den Berg, NL, 75%) through a four-tier chain. Natural person directors are documented at every tier via LPID mandates. A secondary shareholder (Ingrid Van Den Berg, 5%) is also disclosed under EDD policy.

```mermaid
flowchart TD
    subgraph UBO["Ultimate Beneficial Owner"]
        UBO1["👤 Marcus Pieter Van Den Berg\nUBO · NL\nBSN: NL-BSN-112233445\nDOB: 1969-08-22, Rotterdam\nAddress: Herengracht 418, Amsterdam\n75% ultimate indirect control\nControl: SHAREHOLDING · INDIRECT · depth 4"]
        UBO2["👤 Ingrid Maria Van Den Berg\nSecondary Shareholder · NL\nBSN: NL-BSN-998877665\nDOB: 1972-05-10, Amsterdam\n(spouse of UBO)\n5% direct — below FATF 25% threshold\ndisclosed under EDD policy"]
    end

    subgraph Tier3["Tier 3 — Closest to UBO (NL)"]
        T3["🏢 MVB Family Office BV · Netherlands\nKvK: NL-KVK-80112233\n📋 Directors (LPID mandates):\n→ Marcus Van Den Berg\n   Managing Director + Sole Shareholder\n→ Hendrik Bauer\n   Director (family advisor, no ownership)"]
    end

    subgraph Tier2["Tier 2 (LU)"]
        T2["🏢 Nexus Capital SA · Luxembourg\nRCS: LU-RCS-B312456\n📋 Directors (LPID mandates):\n→ Jean-Pierre Luc Moreau (LU)\n   Director\n→ Sophia Miriam Bernstein (CH)\n   Director (also on BVI board ⚠️)"]
    end

    subgraph Tier1["Tier 1 — Closest to Subject (BVI)"]
        T1["🏢 Nexus Holdings Ltd · British Virgin Islands\nReg: VG-BC-2017-000422\n📋 Directors (LPID mandates):\n→ Sophia Miriam Bernstein (CH)\n   Director (cross-board with LU ⚠️)\n→ Elena Dmitrievna Volkov (CH)\n   Director"]
    end

    subgraph Subject["Subject Entity (VASP)"]
        SUBJECT["🏢 Nexus Global Ventures Ltd\nSubject VASP · Cayman Islands\nReg: KY-CI-NV-2019-000381\nLEI: 549300NXGVKY00001KY0\nRisk: HIGH · EDD\nVASP — CIMA regulated"]
    end

    subgraph Transfer["Travel Rule Transfer — KY → IE"]
        BVASP["🏦 Atlantic Digital Exchange Ltd · Ireland\nBeneficiary VASP · IE\nDID: did:web:atlantic-digital-exchange.example.ie\nLEI: 635400ADXIRL00001IE0\nIssues KYCAttestation VC"]
        TXNOTE["Transfer: 750,000 ETH\nOpenKYCAML VC"]
    end

    UBO1 -- "100% owns" --> T3
    UBO2 -- "5% direct" --> SUBJECT
    T3 -- "100%" --> T2
    T2 -- "88%" --> T1
    T1 -- "100%" --> SUBJECT
    UBO1 -- "75% effective indirect" -.-> SUBJECT

    SUBJECT --> BVASP
    SUBJECT -.-> TXNOTE
    TXNOTE -.-> BVASP

    style UBO1 fill:#dbeafe,stroke:#3b82f6
    style UBO2 fill:#dbeafe,stroke:#3b82f6
    style T3 fill:#ede9fe,stroke:#7c3aed
    style T2 fill:#ede9fe,stroke:#7c3aed
    style T1 fill:#ede9fe,stroke:#7c3aed
    style SUBJECT fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
    style TXNOTE fill:#f8fafc,stroke:#64748b,stroke-dasharray: 4 2
```

## Directors at Each Tier

```mermaid
flowchart LR
    subgraph Directors["Natural Person Directors (LPID Mandates)"]
        MvdB["Marcus Van Den Berg\nMD + Shareholder\n📍 MVB Family Office BV (NL)"]
        HB["Hendrik Bauer\nDirector (advisor)\n📍 MVB Family Office BV (NL)"]
        JPM["Jean-Pierre Moreau\nDirector\n📍 Nexus Capital SA (LU)"]
        SB["Sophia Bernstein\nDirector\n📍 Nexus Capital SA (LU)\n📍 Nexus Holdings Ltd (BVI) ⚠️ Cross-board"]
        EV["Elena Volkov\nDirector\n📍 Nexus Holdings Ltd (BVI)"]
    end
```

## Key Data Points

| Field | Value |
| --- | --- |
| Schema | OpenKYCAML v1.3.0 |
| Subject VASP | Nexus Global Ventures Ltd (KY) |
| UBO | Marcus Pieter Van Den Berg (NL) — 75%, 4-tier |
| Secondary shareholder | Ingrid Van Den Berg (NL) — 5% direct |
| Holding chain | NL → LU → BVI → KY (4 tiers) |
| Directors documented | 5 natural persons across 3 tiers (LPID mandates) |
| Notable | Sophia Bernstein holds directorships on both LU and BVI boards (cross-appointment flagged as EDD indicator) |
| Beneficiary VASP | Atlantic Digital Exchange Ltd (IE) |
| Asset / Amount | 750,000 ETH |
| Risk | HIGH · EDD |
| Regulatory basis | AMLR Art. 26 — full chain disclosure |
