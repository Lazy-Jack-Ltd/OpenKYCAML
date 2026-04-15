# predictive/predictive-delta.json — Structure Diagram

**Scenario:** Predictive AML Score with Risk Evolution History (Delta Monitoring) (v1.7.0).  
A KYC record carries a `network-risk-model-v2` score snapshot from the Fenergo Dynamic Risk Engine. Two scores are returned: `network_risk` (45.0) and `velocity_fraud` (38.5). Crucially, `riskEvolutionHistory[]` captures 3 monthly snapshots showing a steadily rising score (30 → 36 → 41.5) over Jan–Mar 2026. The record is correlated with TM case `ACTIMIZE-CASE-2026-00441`. Customer is currently rated MEDIUM, under STANDARD monitoring.

```mermaid
flowchart TD
    subgraph Customer["Customer — Subject"]
        CUST["📋 KYC Record (standalone)\noverallRisk: MEDIUM · ddt: SDD/CDD\nalertCorrelationId: ACTIMIZE-CASE-2026-00441"]
    end

    subgraph Model["predictiveAML — Network Risk Model"]
        MM["🤖 network-risk-model-v2\nProvider: Fenergo Dynamic Risk Engine\neuAiActClassification: limited-risk"]
    end

    subgraph Scores["predictiveScores (Current Snapshot — 2026-04-07)"]
        S1["📊 network_risk: 45.0 / 100\nconfidence: 0.78 · horizon: 60d"]
        S2["📊 velocity_fraud: 38.5 / 100\nconfidence: 0.83 · horizon: 14d"]
    end

    subgraph Evolution["riskEvolutionHistory — Rising Trend ⚠️"]
        E1["Jan 2026: score 30.0\nbaseline · delta: 0.0"]
        E2["Feb 2026: score 36.0\ndelta: +6.0 ↑"]
        E3["Mar 2026: score 41.5\ndelta: +5.5 ↑"]
        CURR["Apr 2026: 45.0 (current)\n(still rising — MEDIUM but trending HIGH)"]

        E1 --> E2 --> E3 --> CURR
    end

    subgraph Monitor["Monitoring"]
        MON["🔍 STANDARD monitoring · ACTIVE\nTM case: ACTIMIZE-CASE-2026-00441\n(rising trend — escalation candidate)"]
    end

    CUST --> Model
    Model --> Scores
    CUST --> Evolution
    CUST -.-> Monitor

    style CUST fill:#fef9c3,stroke:#eab308
    style MM fill:#f3e8ff,stroke:#9333ea
    style S1 fill:#fff7ed,stroke:#f97316
    style S2 fill:#fff7ed,stroke:#f97316
    style E1 fill:#dcfce7,stroke:#16a34a
    style E2 fill:#fff7ed,stroke:#f97316
    style E3 fill:#fff7ed,stroke:#f97316
    style CURR fill:#fef2f2,stroke:#ef4444
    style MON fill:#fef9c3,stroke:#eab308
```

## Risk Evolution Trend

| Month | Score | Delta | Signal |
|---|---|---|---|
| Jan 2026 | 30.0 | 0.0 | Baseline |
| Feb 2026 | 36.0 | +6.0 ↑ | Rising |
| Mar 2026 | 41.5 | +5.5 ↑ | Rising |
| Apr 2026 | 45.0 (current) | +3.5 ↑ | ⚠️ Escalation candidate |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.7.0 |
| Predictive model | network-risk-model-v2 (delta monitoring) |
| Provider | Fenergo Dynamic Risk Engine |
| Current scores | network_risk: 45.0 · velocity_fraud: 38.5 |
| Risk evolution | 4-month rising trend (30 → 45, +15 points) |
| Alert correlation | `ACTIMIZE-CASE-2026-00441` |
| Overall risk | MEDIUM (trending towards HIGH) |
| Monitoring | STANDARD · ACTIVE |
| Regulatory basis | AMLR Art. 21 ongoing monitoring; FATF Rec. 10/11; BCBS 239 |
