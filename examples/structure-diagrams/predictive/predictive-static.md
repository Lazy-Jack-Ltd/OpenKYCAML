# predictive/predictive-static.json — Structure Diagram

**Scenario:** Static Predictive AML Score Snapshot (v1.7.0).  
A KYC record carries a static predictive risk snapshot from the `txn-risk-model-v3` (EU AI Act high-risk classification, Conformity Assessment EU-AIACT-2026-NB001-TXN-00342). Two scores are present: `transaction_anomaly` (72.5/100, conf 0.87, 30d horizon) and `customer_lifetime_risk` (65.0/100, conf 0.91, 90d horizon). SHAP explainability values identify `cross_border_ratio` and `velocity_30d` as the top drivers. Customer is rated HIGH risk, under ENHANCED monitoring.

```mermaid
flowchart TD
    subgraph Customer["Customer — Subject"]
        CUST["📋 KYC Record\n(no IVMS101 payload — standalone risk record)\nmessageId: a1b2c3d4-e5f6-7890-abcd-ef1234567890\nkycCompletionDate: 2026-01-15\noverallRisk: HIGH · ddt: EDD"]
    end

    subgraph Model["predictiveAML — Model Metadata"]
        MM["🤖 txn-risk-model-v3 v3.0.0\nProvider: Acme AML Analytics Ltd\ntraining: 2026-01-01\neuAiActClassification: high-risk-aml\nConformity Assessment:\nEU-AIACT-2026-NB001-TXN-00342"]
    end

    subgraph Scores["predictiveScores (Static Snapshot)"]
        S1["⚠️ transaction_anomaly: 72.5 / 100\nconfidence: 0.87 · horizon: 30d\ntimestamp: 2026-04-07T08:45:00Z"]
        S2["⚠️ customer_lifetime_risk: 65.0 / 100\nconfidence: 0.91 · horizon: 90d\ntimestamp: 2026-04-07T08:45:00Z"]
    end

    subgraph SHAP["Explainability — SHAP Values (top drivers)"]
        E1["cross_border_ratio: 0.31 (top driver)"]
        E2["velocity_30d_txn_count_hash: 0.24"]
        E3["cash_intensive: 0.18"]
        E4["avg_txn_value_usd_bucket: 0.15"]
    end

    subgraph Monitor["Monitoring"]
        MON["🔍 ENHANCED monitoring · ACTIVE\nreviews: QUARTERLY\nalerts: REAL_TIME\nnextReview: 2026-06-01\nTM model: actimize-sam-9.2.1"]
    end

    CUST --> Model
    Model --> Scores
    Scores --> SHAP
    CUST -.-> Monitor

    style CUST fill:#fef3c7,stroke:#f59e0b
    style MM fill:#f3e8ff,stroke:#9333ea
    style S1 fill:#fef2f2,stroke:#ef4444
    style S2 fill:#fff7ed,stroke:#f97316
    style E1 fill:#e0e7ff,stroke:#6366f1
    style E2 fill:#e0e7ff,stroke:#6366f1
    style E3 fill:#e0e7ff,stroke:#6366f1
    style E4 fill:#e0e7ff,stroke:#6366f1
    style MON fill:#fef2f2,stroke:#ef4444
```

## Score Details

| Score type | Value | Confidence | Horizon | Status |
|---|---|---|---|---|
| `transaction_anomaly` | 72.5 / 100 | 0.87 | 30 days | ⚠️ ELEVATED |
| `customer_lifetime_risk` | 65.0 / 100 | 0.91 | 90 days | ⚠️ ELEVATED |

## SHAP Feature Contributions

| Feature | SHAP value | Interpretation |
|---|---|---|
| `cross_border_ratio` | 0.31 | High cross-border transaction rate |
| `velocity_30d_txn_count_hash` | 0.24 | Elevated 30-day transaction velocity |
| `cash_intensive` | 0.18 | Cash-intensive business flag |
| `avg_txn_value_usd_bucket` | 0.15 | High average transaction value bucket |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.7.0 |
| Predictive model | txn-risk-model-v3 v3.0.0 (static snapshot) |
| EU AI Act | `high-risk-aml` — Conformity Assessment EU-AIACT-2026-NB001-TXN-00342 |
| Overall risk | HIGH |
| Monitoring | ENHANCED · REAL_TIME alerts |
| BCBS 239 | Compliant (data aggregation metadata present) |
| Regulatory basis | EU AI Act Art. 6 (high-risk); AMLR Art. 21 monitoring; BCBS 239 |
