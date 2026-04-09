# cell-company/pcc-cell-predictive-aml.json — Structure Diagram

**Scenario:** Protected Cell Company with Cell-Level Predictive AML Scores (v1.11.2).  
Guernsey Re PCC — Cell 7 (`CELL-007`) transfer record is enriched with predictive AML scores at both the entity level and the cell level. The `cellLevelPredictiveScores[]` array (added in v1.11.2) carries cell-specific transaction anomaly and network risk scores. A `cellRiskProfileOverride` reflects an elevated score (72) compared to the previous run (delta +8), indicating a short-window alert for the cell's counterparty network.

```mermaid
flowchart TD
    subgraph PCC["PCC Cell — Guernsey"]
        PARENT_PCC["🏢 Guernsey Re PCC\nParent PCC · GG\nLEI: 549300ABCDEF12345678"]
        CELL7["🏢 Cell 7 — Property Catastrophe Series 2026\ncellIdentifier: CELL-007\ncellCompanyType: PCC_CELL\nhasIndependentLegalPersonality: false"]
        PARENT_PCC -- "cell of" --> CELL7
    end

    subgraph PredictiveAML["predictiveAML Block — Cell-Level Scores 🆕 v1.11.2"]
        MODEL["🤖 Model: amlr2027-edd-risk-model-v2 · v2.1.0\nmodelType: gradient_boosted_tree\nEU AI Act: HIGH_RISK\nBCBS 239 compliant"]

        CELL_SCORES["📊 cellLevelPredictiveScores[CELL-007]:\n  transaction_anomaly: 72 (conf 0.85, 30d)\n  network_risk: 65 (conf 0.78, 60d)\n\n⚠️ Both above MEDIUM threshold"]

        OVERRIDE["⚡ cellRiskProfileOverride:\n  overallRiskScore: 72\n  deltaFromPrevious: +8\n  timestamp: 2026-04-09T10:00:00Z\n\n(score escalation — EDD review triggered)"]
    end

    subgraph Transfer["Transfer — GG → KY"]
        OVASP["🏦 Guernsey Trust & Custody Ltd · GG"]
        BVASP["🏦 Cayman Digital Finance Ltd · KY"]
    end

    CELL7 -.-> PredictiveAML
    CELL7 -- "5,000,000 USD" --> OVASP
    OVASP -- "IVMS 101 Travel Rule" --> BVASP

    style PARENT_PCC fill:#ede9fe,stroke:#7c3aed
    style CELL7 fill:#dbeafe,stroke:#3b82f6
    style MODEL fill:#f3e8ff,stroke:#9333ea
    style CELL_SCORES fill:#fff7ed,stroke:#f97316
    style OVERRIDE fill:#fef2f2,stroke:#ef4444
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
```

## Cell-Level Predictive Score Breakdown

```mermaid
xychart-beta
    title "CELL-007 Predictive Risk Scores"
    x-axis ["transaction_anomaly (30d)", "network_risk (60d)"]
    y-axis "Score (0-100)" 0 --> 100
    bar [72, 65]
```

## Cell-Level vs Entity-Level Scores

| Scope | Score type | Value | Confidence | Horizon |
|---|---|---|---|---|
| CELL-007 (cell) | `transaction_anomaly` | 72 | 0.85 | 30 days |
| CELL-007 (cell) | `network_risk` | 65 | 0.78 | 60 days |
| Override | `overallRiskScore` (delta) | 72 (+8 from prev.) | — | — |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.11.2 |
| Cell | Guernsey Re PCC · Cell 7 (CELL-007) |
| Predictive model | amlr2027-edd-risk-model-v2 v2.1.0 |
| Cell `transaction_anomaly` | 72 / 100 (conf 0.85, 30d) |
| Cell `network_risk` | 65 / 100 (conf 0.78, 60d) |
| `cellRiskProfileOverride` | Score 72, delta +8 (escalation alert) |
| Asset / Amount | 5,000,000 USD |
| Regulatory basis | FATF Rec. 24; EU AI Act Art. 6 (High-Risk AI); BCBS 239; AMLR Art. 26 |
