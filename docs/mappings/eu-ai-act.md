# EU AI Act — High-Risk AML System Mapping

This document maps the **EU Artificial Intelligence Act** (Regulation (EU) 2024/1689, in force 1 August 2024, AML provisions applicable from 2 August 2026) obligations for high-risk AI systems used in AML/CFT to OpenKYCAML v1.7.0 fields. It is a companion to `eu-ai-act.yaml`.

**Primary legal basis:**
- EU AI Act Regulation (EU) 2024/1689
- Annex III — High-risk AI systems (point 5(b): AI systems used in AML, credit scoring, insurance risk assessment)
- Art. 6(2) — Classification as high-risk based on Annex III
- Art. 13 — Transparency and provision of information to users
- Art. 14 — Human oversight
- Art. 15 — Accuracy, robustness, and cybersecurity
- Art. 43 — Conformity assessment
- Art. 50 — Transparency obligations for certain AI systems

---

## 1. Classification: AML Systems as High-Risk AI

Under **EU AI Act Annex III, point 5(b)**, AI systems used in the context of critical digital infrastructure and AML — specifically systems that assess creditworthiness, perform customer risk scoring, or detect suspicious activity — are classified as **high-risk AI systems**. This classification applies to:

- Transaction monitoring models (anomaly detection)
- Customer risk scoring engines (static and dynamic)
- UBO graph risk analysis tools
- Sanctions screening AI (where AI decision-making is involved)
- Predictive fraud detection models

OpenKYCAML's `predictiveAML.modelMetadata.euAiActClassification` = `"high-risk-aml"` captures this classification explicitly.

---

## 2. AI Act Obligations and OpenKYCAML Mapping

### Art. 13 — Transparency and Provision of Information to Deployers

| AI Act Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|
| **Art. 13(3)(a)** — Identity and contact details of provider | `predictiveAML.modelMetadata.provider` | Model provider name or DID |
| **Art. 13(3)(b)(i)** — Purpose and intended use | `predictiveAML.predictiveScores[].scoreType` | Score type documents the specific AML use case |
| **Art. 13(3)(b)(ii)** — Level of accuracy, robustness, and cybersecurity | `predictiveAML.predictiveScores[].confidence` | Confidence score per-prediction; linked to model version |
| **Art. 13(3)(b)(iii)** — Expected output and output interpretation | `predictiveAML.explainability.values` | SHAP/LIME/counterfactual values for output interpretation |
| **Art. 13(3)(b)(iv)** — Performance metrics on which the system was tested | `predictiveAML.modelMetadata.trainingDate` + `modelVersion` | Version + training date enable traceability to published model cards |
| **Art. 13(3)(c)** — Changes to the system that have been pre-determined by the provider | `predictiveAML.modelMetadata.modelVersion` | Version increments track approved model changes |

### Art. 14 — Human Oversight

| AI Act Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|
| Human review of model outputs | `kycProfile.monitoringInfo.alerts[].alertStatus` (UNDER_REVIEW, ESCALATED) | Alert lifecycle tracks human review steps |
| Ability to override model decisions | `kycProfile.monitoringInfo.alerts[].alertStatus` = `CLOSED_NO_ACTION` | Manual override outcome captured |
| Competent persons assigned | `kycProfile.monitoringInfo.alerts[].assignedTo` | Person/team responsible for oversight |

### Art. 15 — Accuracy, Robustness, and Cybersecurity

| AI Act Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|
| Model accuracy documentation | `predictiveAML.predictiveScores[].confidence` | Per-score confidence bounds |
| Robustness against adversarial inputs | `predictiveAML.explainability.method` (SHAP/LIME stability) | SHAP stability metrics indicate robustness |
| Version control and reproducibility | `predictiveAML.modelMetadata.modelVersion` + `trainingDate` | Enables full reproducibility audit |

### Art. 43 — Conformity Assessment

| AI Act Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|
| Conformity assessment for high-risk AI | `predictiveAML.modelMetadata.conformityAssessmentReference` | Notified body certificate number or self-assessment reference |
| Classification as high-risk | `predictiveAML.modelMetadata.euAiActClassification` = `"high-risk-aml"` | Explicit Annex III point 5(b) classification |

---

## 3. Model Card Template (predictiveAML.modelMetadata)

The `modelMetadata` object constitutes a machine-readable partial model card aligned to EU AI Act Art. 13 obligations:

```json
{
  "modelMetadata": {
    "modelId": "txn-risk-model-v3",
    "modelVersion": "3.0.0",
    "provider": "Acme AML Analytics Ltd",
    "trainingDate": "2026-01-01T00:00:00Z",
    "euAiActClassification": "high-risk-aml",
    "conformityAssessmentReference": "EU-AIACT-2026-NB001-TXN-00342"
  }
}
```

For full AI Act compliance, providers should supplement with an external model card covering:
- Training data sources and data governance
- Performance benchmarks (precision, recall, F1 on held-out AML test sets)
- Known limitations and out-of-distribution behaviour
- Bias and fairness assessments

---

## 4. Coverage Summary

| EU AI Act Obligation | Coverage | OpenKYCAML Field |
|---|---|---|
| Art. 13(3)(a) — Provider identity | ✅ | `modelMetadata.provider` |
| Art. 13(3)(b)(i) — Intended use | ✅ | `predictiveScores[].scoreType` |
| Art. 13(3)(b)(ii) — Accuracy / confidence | ✅ | `predictiveScores[].confidence` |
| Art. 13(3)(b)(iii) — Output interpretation | ✅ | `explainability.values` |
| Art. 13(3)(b)(iv) — Performance metrics | 🟡 | `modelVersion` + `trainingDate` (full metrics in external model card) |
| Art. 13(3)(c) — System changes | ✅ | `modelVersion` |
| Art. 14 — Human oversight | ✅ | `alerts[].alertStatus` + `assignedTo` |
| Art. 15 — Accuracy and robustness | ✅ | `confidence` + `explainability` |
| Art. 43 — Conformity assessment | ✅ | `conformityAssessmentReference` |
| Annex III classification | ✅ | `euAiActClassification` = `"high-risk-aml"` |

---

*Last updated: April 2026 — OpenKYCAML v1.12.0*
