# amlr2027-fatca-ai-act.json — Structure Diagram

**Scenario:** AMLR 2027 + FATCA + EU AI Act — Full-Stack Compliance Record (v1.9.1).  
Nexus Capital Management Ltd (IE) is a comprehensive EDD showcase combining: three-jurisdiction TINs + FATCA GIIN + CRS residencies + Pillar Two (all in `taxStatus`), a QSeal X.509 certificate (`pkiEvidence`), three predictive AML scores from an EU AI Act high-risk model, FinCEN 314(b) safe-harbour flag, and two beneficial owners (Nexus Global Holdings 80% + Jonathan Harrington 20%). This is the widest-coverage example in the repository.

```mermaid
flowchart TD
    subgraph BOs["Beneficial Ownership"]
        BO1["🏢 Nexus Global Holdings PLC\nBO #1 · 80% SHAREHOLDING"]
        BO2["👤 Jonathan P. Harrington\nBO #2 · 20% SHAREHOLDING"]
    end

    subgraph Entity["Subject Entity"]
        LP["🏢 Nexus Capital Management Ltd\nLegalPerson · IE\nLEI: 213800NEXUSCAPITAL001\nRisk: HIGH · EDD\nX.500 DN present (QSEAL)"]
    end

    subgraph PKI["pkiEvidence + legacyIdentifiers (v1.8.0)"]
        X509["🔐 X.509 QSeal · Serial: 0A1B2C3D...\nIssuer: IE-QTSP-ROOT-CA\nx500DN: CN=Nexus Capital Management Ltd\nOIDs: QCStatements + organizationIdentifier + PDS"]
    end

    subgraph TaxBlock["taxStatus — 5 Tax Modules (v1.9.1)"]
        TINS["TINs:\n  IE: IE6336214T ✅\n  US: 98-7654321 ✅\n  DE: 86095742719 ✅"]
        VAT_REG["Indirect Tax:\n  IE VAT: IE6336214T ✅\n  DE VAT: DE123456789 ✅"]
        CRS_BLOCK["CRS Residencies:\n  IE · US · DE (all verified ✅)"]
        FATCA_BLOCK["FATCA:\n  classification: registeredDeemedCompliantFFI\n  GIIN: XYZ123.DEF45.LE.372 ✅\n  WA ref: WA-NEXUS-IE-2026-001"]
        P2_BLOCK["Pillar Two:\n  inScopeMNE · revenue €920M\n  IE ETR 12.5% ⚠️ · US 21% ✅ · DE 29.8% ✅\n  GIR: GIR-NEXUS-IE-2025-001"]
    end

    subgraph PredAML["predictiveAML — EU AI Act High-Risk (v1.7.0)"]
        PAML["🤖 amlr2027-edd-risk-model-v2\neuAiActClassification: high-risk-aml\nubo_graph_risk: 76.0 (conf 0.91)\nnetwork_risk: 68.5 (conf 0.85)\ntransaction_anomaly: 62.0 (conf 0.79)"]
    end

    subgraph ISF["informationSharingFlags (v1.7.0)"]
        ISF_NODE["🇺🇸 FinCEN 314(b) Safe-Harbour: true ✅\nsharingConsentTimestamp: 2026-04-08T09:00:00Z\n(USA PATRIOT Act § 314(b), 31 CFR 1010.540)"]
    end

    BO1 --> LP
    BO2 --> LP
    LP --> PKI
    LP --> TaxBlock
    LP --> PredAML
    LP --> ISF

    style BO1 fill:#ede9fe,stroke:#7c3aed
    style BO2 fill:#dbeafe,stroke:#3b82f6
    style LP fill:#fef2f2,stroke:#ef4444
    style X509 fill:#f0fdf4,stroke:#16a34a
    style TINS fill:#dcfce7,stroke:#16a34a
    style VAT_REG fill:#dbeafe,stroke:#3b82f6
    style CRS_BLOCK fill:#dbeafe,stroke:#3b82f6
    style FATCA_BLOCK fill:#fef3c7,stroke:#f59e0b
    style P2_BLOCK fill:#fef3c7,stroke:#f59e0b
    style PAML fill:#fef2f2,stroke:#ef4444
    style ISF_NODE fill:#e0e7ff,stroke:#6366f1
```

## Feature Matrix — All Extensions Active

| Extension | Fields present | Version added |
|---|---|---|
| Tax / TIN | `taxStatus.tinIdentifiers[]` × 3 | v1.9.0 |
| Indirect tax | `taxStatus.indirectTaxRegistrations[]` × 2 | v1.9.0 |
| FATCA | `taxStatus.fatcaStatus` (GIIN + chapter4) | v1.9.1 |
| CRS | `taxStatus.crsTaxResidencies[]` × 3 | v1.9.1 |
| Pillar Two | `taxStatus.pillarTwo` (ETRs + GIR) | v1.9.0 |
| X.509 PKI | `pkiEvidence` + `legacyIdentifiers` | v1.8.0 |
| Predictive AML | `predictiveAML` (3 scores, EU AI Act) | v1.7.0 |
| FinCEN 314(b) | `informationSharingFlags.section314bSafeHarbor` | v1.7.0 |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.9.1 |
| Subject | Nexus Capital Management Ltd (IE) |
| Risk | HIGH · EDD |
| UBOs | Nexus Global Holdings PLC (80%) + Jonathan Harrington (20%) |
| FATCA GIIN | `XYZ123.DEF45.LE.372` |
| Pillar Two IE ETR | 12.5% — ⚠️ below GloBE 15% minimum |
| Predictive AML | 3 scores (max: `ubo_graph_risk` 76.0) |
| 314(b) | Safe-harbour active (FinCEN § 314(b)) |
| Regulatory basis | AMLR 2027; FATCA; OECD CRS + Pillar Two; eIDAS 2.0; EU AI Act; USA PATRIOT Act § 314(b) |
