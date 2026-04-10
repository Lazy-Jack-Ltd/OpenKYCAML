# BCBS 239 Risk Data Aggregation Mapping

This document maps the **Basel Committee on Banking Supervision Principles for Effective Risk Data Aggregation and Risk Reporting (BCBS 239)** (January 2013, revised guidance 2020) to OpenKYCAML v1.7.0 fields. It is a companion to the machine-readable YAML version (`bcbs239.yaml`).

BCBS 239 is primarily directed at Globally Systemically Important Banks (G-SIBs) and Domestically Systemically Important Banks (D-SIBs) but constitutes best practice for any AML data infrastructure subject to supervisory review.

---

## 1. BCBS 239 Principles and OpenKYCAML Mapping

### Pillar 1 — Overarching Governance and Infrastructure (Principles 1–2)

| BCBS 239 Principle | Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|---|
| **P1 — Governance** | Board-approved data architecture; senior accountability for data quality | `kycProfile.auditMetadata.dataProvider` + `dataSourceSystem` | Audit trail for data origin and responsible system |
| **P2 — Data Architecture and IT Infrastructure** | Single authoritative source; automated aggregation; lineage traceability | `predictiveAML.dataAggregationMetadata.dataLineageReference` + `bcbs239ComplianceLevel` | `dataLineageReference` captures the ETL job/catalogue reference; `lastAggregationTimestamp` records when the aggregate was last produced |

### Pillar 2 — Risk Data Aggregation Capabilities (Principles 3–6)

| BCBS 239 Principle | Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|---|
| **P3 — Accuracy and Integrity** | Data reconciled and validated; error rates monitored | `predictiveAML.modelMetadata.modelVersion` + `predictiveAML.predictiveScores[].confidence` | Confidence score quantifies model data quality; version ensures reproducibility |
| **P4 — Completeness** | All material risk positions captured | `kycProfile.beneficialOwnership[]` + `identityDocuments.*` | Full UBO chain and document verification status captured |
| **P5 — Timeliness** | Data aggregated to meet regulatory reporting deadlines | `predictiveAML.dataAggregationMetadata.lastAggregationTimestamp` | ISO 8601 timestamp of last aggregation run; supports SLA monitoring |
| **P6 — Adaptability** | Aggregation adaptable to stress scenarios and ad hoc requests | `predictiveAML.predictiveScores[].horizonDays` + `riskEvolutionHistory[]` | Variable horizon scores and delta history support scenario modelling |

### Pillar 3 — Risk Reporting Practices (Principles 7–11)

| BCBS 239 Principle | Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|---|
| **P7 — Accuracy** | Reports accurate and reliable; reconciliation to source data | `predictiveAML.explainability` (SHAP/LIME values) | Explainability output provides audit trail linking score to source features |
| **P8 — Comprehensiveness** | All material risk aggregated across entities, geographies, products | `kycProfile.beneficialOwnership[].intermediateEntities[]` | Multi-tier ownership chain enables group-level risk consolidation |
| **P9 — Clarity and Usefulness** | Reports clear; appropriate for recipient | `predictiveAML.explainability.method` + `values` | Counterfactual and SHAP outputs designed for compliance officer consumption |
| **P10 — Frequency** | Reporting frequency commensurate with risk | `kycProfile.monitoringInfo.reviewFrequency` + `alertFrequency` | REAL_TIME through ANNUAL; RISK_TRIGGERED for event-driven refresh |
| **P11 — Distribution** | Reports distributed to appropriate recipients; access controls | `gdprSensitivityMetadata.disclosurePolicy` | `allowedRecipients` / `prohibitedRecipients` machine-readable access controls |

### Pillar 4 — Supervisory Review, Tools, and Cooperation (Principles 12–14)

| BCBS 239 Principle | Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|---|
| **P12 — Review** | Supervisors review BCBS 239 adherence annually | `predictiveAML.dataAggregationMetadata.bcbs239ComplianceLevel` | Self-reported compliance level: `full`, `partial`, `gap-analysis` |
| **P13 — Remediation** | Banks address deficiencies in agreed timeframes | `kycProfile.auditMetadata.recordUpdatedAt` + `recordVersion` | Tracks remediation events via version increments |
| **P14 — Home/Host Cooperation** | Cross-border data sharing between supervisors | `kycProfile.thirdPartyCDDReliance` + `informationSharingFlags` | Structured third-party CDD reliance and FinCEN 314(a)/(b) sharing records |

---

## 2. DataAggregationMetadata Block Reference

The `predictiveAML.dataAggregationMetadata` object is the primary BCBS 239 vehicle in OpenKYCAML:

```json
{
  "dataAggregationMetadata": {
    "bcbs239ComplianceLevel": "full",
    "lastAggregationTimestamp": "2026-04-07T08:00:00Z",
    "dataLineageReference": "urn:lineage:acme:aml:job:20260407-080000"
  }
}
```

| Field | BCBS 239 Principle | Description |
|---|---|---|
| `bcbs239ComplianceLevel` | P1, P12 | Self-assessed compliance level (`full` / `partial` / `gap-analysis`) |
| `lastAggregationTimestamp` | P5 (Timeliness) | When the risk data aggregation was last run |
| `dataLineageReference` | P2 (Data Architecture), P3 (Accuracy) | Pointer to ETL job, data catalogue entry, or audit log |

---

## 3. Coverage Assessment

| BCBS 239 Principle | Coverage | Notes |
|---|---|---|
| P1 — Governance | ✅ | `auditMetadata` provides data origin and accountability |
| P2 — Data Architecture | ✅ | `dataLineageReference` + `lastAggregationTimestamp` |
| P3 — Accuracy and Integrity | ✅ | Model `confidence` + `modelVersion` |
| P4 — Completeness | 🟡 | UBO/docs coverage strong; product portfolio partial |
| P5 — Timeliness | ✅ | `lastAggregationTimestamp` + `alertFrequency` |
| P6 — Adaptability | ✅ | `horizonDays` + `riskEvolutionHistory[]` |
| P7 — Accuracy (reporting) | ✅ | SHAP/LIME/counterfactual explainability |
| P8 — Comprehensiveness | ✅ | Multi-tier UBO chain; group-level aggregation |
| P9 — Clarity | ✅ | Explainability values designed for human consumption |
| P10 — Frequency | ✅ | `reviewFrequency` + `alertFrequency` |
| P11 — Distribution | ✅ | `gdprSensitivityMetadata.disclosurePolicy` |
| P12 — Supervisory Review | ✅ | `bcbs239ComplianceLevel` self-assessment |
| P13 — Remediation | 🟡 | `recordVersion` increments; no formal remediation plan field |
| P14 — Home/Host Cooperation | ✅ | `thirdPartyCDDReliance` + `informationSharingFlags` |

---

*Last updated: April 2026 — OpenKYCAML v1.12.0*
