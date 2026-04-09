# predictive/predictive-ai-high-risk.json — Structure Diagram

**Scenario:** EU AI Act High-Risk — UBO Graph Predictive AML Model (v1.7.0).  
A KYC record carries three predictive scores from `ubo-graph-risk-model-v1` (EU AI Act `high-risk-aml` classification): `ubo_graph_risk` (89.0), `network_risk` (84.5), and `transaction_anomaly` (77.0). The risk evolution history shows a steep escalation from 60 (Nov 2025) to 88 (Mar 2026). Customer is rated VERY_HIGH with full EDD and REAL_TIME monitoring. The conformity assessment record is required under EU AI Act Art. 6.

```mermaid
flowchart TD
    subgraph Customer["Customer — Subject"]
        CUST["📋 KYC Record (standalone)\noverallRisk: VERY_HIGH · ddt: EDD\nEDD required — all three scores above HIGH threshold"]
    end

    subgraph Model["predictiveAML — UBO Graph Risk Model"]
        MM["🤖 ubo-graph-risk-model-v1 v1.4.0\nProvider: FinSentinel AI Ltd\neuAiActClassification: high-risk-aml ⛔\nEU AI Act Art. 6 — mandatory conformity assessment"]
    end

    subgraph Scores["predictiveScores (VERY_HIGH — 2026-04-07)"]
        S1["🔴 ubo_graph_risk: 89.0 / 100\nconfidence: 0.93 · horizon: 30d\n(top score — complex UBO chain)"]
        S2["🔴 network_risk: 84.5 / 100\nconfidence: 0.88 · horizon: 30d"]
        S3["🔴 transaction_anomaly: 77.0 / 100\nconfidence: 0.85 · horizon: 14d"]
    end

    subgraph Evolution["riskEvolutionHistory — Steep Escalation ⛔"]
        E1["Nov 2025: 60.0 (initial)"]
        E2["Jan 2026: 68.0 (+8.0 ↑)"]
        E3["Mar 2026: 88.0 (+20.0 ↑↑)"]
        CURR["Apr 2026: 89.0 (current) VERY_HIGH"]

        E1 --> E2 --> E3 --> CURR
    end

    subgraph Monitor["Monitoring — REAL_TIME"]
        MON["🔍 ENHANCED monitoring · ACTIVE\nalerts: REAL_TIME\nEDD triggered\n(all 3 scores exceed HIGH threshold)"]
    end

    CUST --> Model
    Model --> Scores
    CUST --> Evolution
    CUST -.-> Monitor

    style CUST fill:#fef2f2,stroke:#ef4444
    style MM fill:#fef2f2,stroke:#ef4444
    style S1 fill:#fef2f2,stroke:#ef4444
    style S2 fill:#fef2f2,stroke:#ef4444
    style S3 fill:#fef2f2,stroke:#ef4444
    style E1 fill:#fff7ed,stroke:#f97316
    style E2 fill:#fef2f2,stroke:#ef4444
    style E3 fill:#fef2f2,stroke:#ef4444
    style CURR fill:#fef2f2,stroke:#ef4444
    style MON fill:#fef2f2,stroke:#ef4444
```

## Score Summary (All VERY_HIGH)

| Score type | Value | Confidence | Horizon | Risk level |
|---|---|---|---|---|
| `ubo_graph_risk` | 89.0 / 100 | 0.93 | 30 days | 🔴 VERY_HIGH |
| `network_risk` | 84.5 / 100 | 0.88 | 30 days | 🔴 VERY_HIGH |
| `transaction_anomaly` | 77.0 / 100 | 0.85 | 14 days | 🔴 HIGH |

## Risk Escalation Timeline

| Date | Score | Delta | Trigger |
|---|---|---|---|
| Nov 2025 | 60.0 | baseline | Initial |
| Jan 2026 | 68.0 | +8.0 | UBO graph complexity increased |
| Mar 2026 | 88.0 | +20.0 ↑↑ | Rapid escalation — EDD triggered |
| Apr 2026 | 89.0 (current) | +1.0 | VERY_HIGH sustained |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.7.0 |
| Predictive model | ubo-graph-risk-model-v1 v1.4.0 |
| Provider | FinSentinel AI Ltd |
| EU AI Act | `high-risk-aml` — conformity assessment required (Art. 6) |
| Overall risk | VERY_HIGH |
| Risk escalation | +29 points over 5 months |
| Monitoring | ENHANCED · REAL_TIME |
| Action | EDD initiated — all scores > HIGH threshold |
| Regulatory basis | EU AI Act Art. 6/9/13; AMLR Art. 21; FATF Rec. 10/11; BCBS 239 |
