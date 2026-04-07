# Enforcement Tiers for OpenKYCAML Compliance

This document defines the **enforcement tiers** that govern which OpenKYCAML fields are mandatory, strongly recommended, or optional for different obliged entity types and regulatory regimes. It supports AMLR 2027 compliance programme gap analysis and helps implementers prioritise their adoption roadmap.

---

## 1. Tier Overview

| Tier | Label | Enforcement Standard | Use Cases |
|---|---|---|---|
| **Tier 0** | Absolute minimum | JSON schema `required` constraints — payload is invalid without these | Any OpenKYCAML envelope regardless of use case |
| **Tier 1** | FATF Core | Required for FATF-compliant Travel Rule and CDD | VASPs, banks under FATF R.10/16 |
| **Tier 2** | AMLR 2027 | Required for EU obliged entities from 1 July 2027 | EU banks, fintechs, crypto-asset service providers under AMLR |
| **Tier 3** | EDD / High-Risk | Required when `dueDiligenceType` = `EDD` or `customerRiskRating` = `VERY_HIGH` | PEP, high-risk country, complex ownership |
| **Tier 4** | PredictiveAML | Required when using AI-based AML scoring under EU AI Act | Obliged entities deploying high-risk AI for AML |
| **Tier 5** | XRPL / Blockchain | Required for on-chain VASP Travel Rule and XRPL credential-gated tokens | XRPL-based VASPs, MPT issuers, permissioned domain operators |

---

## 2. Tier 0 — Absolute Minimum (Schema Required)

These fields are enforced by JSON Schema `required` constraints. A payload without them fails validation.

| Field | Constraint |
|---|---|
| `predictiveAML.modelMetadata.modelId` | Required when `predictiveAML` is present |
| `predictiveAML.modelMetadata.modelVersion` | Required when `predictiveAML` is present |
| `predictiveAML.modelMetadata.euAiActClassification` | Required when `predictiveAML` is present |
| `predictiveAML.predictiveScores[]` (minItems: 1) | Required when `predictiveAML` is present |
| `predictiveAML.predictiveScores[].scoreType` | Required per score |
| `predictiveAML.predictiveScores[].value` | Required per score |
| `predictiveAML.predictiveScores[].confidence` | Required per score |

---

## 3. Tier 1 — FATF Core

| Field | Regulatory Basis | Applicability |
|---|---|---|
| `ivms101.originator` | FATF R.16 Travel Rule | All VASPs |
| `ivms101.beneficiary` | FATF R.16 Travel Rule | All VASPs |
| `kycProfile.customerRiskRating` | FATF R.1 (RBA) | All obliged entities |
| `kycProfile.dueDiligenceType` | FATF R.10 (CDD) | All obliged entities |
| `kycProfile.sanctionsScreening` | FATF R.6 | All obliged entities |
| `kycProfile.beneficialOwnership[]` | FATF R.24/R.25 | Legal persons and arrangements |
| `kycProfile.monitoringInfo` | FATF R.10 (ongoing monitoring) | All obliged entities |

---

## 4. Tier 2 — AMLR 2027

| Field | AMLR Article | Deadline |
|---|---|---|
| `kycProfile.pepStatus` | Art. 28–31 | 1 July 2027 |
| `kycProfile.sourceOfFundsWealth` | Art. 29 (EDD) | 1 July 2027 |
| `kycProfile.thirdPartyCDDReliance` | Art. 48 | 1 July 2027 |
| `kycProfile.auditMetadata.dataRetentionDate` | Art. 56 (5-year retention) | 1 July 2027 |
| `gdprSensitivityMetadata.tippingOffProtected` | Art. 73 | 1 July 2027 |
| `kycProfile.beneficialOwnership[].intermediateEntities[]` | Art. 26 (full chain) | 1 July 2027 |

---

## 5. Tier 3 — EDD / High-Risk

Required when `kycProfile.dueDiligenceType` = `EDD` or `kycProfile.customerRiskRating` = `VERY_HIGH`:

| Field | EDD Trigger | Notes |
|---|---|---|
| `kycProfile.sourceOfFundsWealth` | PEP, high-risk country, complex structure | Mandatory source of funds narrative |
| `kycProfile.beneficialOwnership[].nomineeFlags` | Nominee arrangements identified | FATF R.24 (2022 rev.) |
| `kycProfile.beneficialOwnership[].trustInstrumentReference` | Trust/foundation structures | FATF R.25 (2022 rev.) |
| `kycProfile.monitoringInfo.alertFrequency` | EDD = REAL_TIME or DAILY recommended | Ongoing monitoring intensity |
| `kycProfile.monitoringInfo.ruleTriggerHistory[]` | All EDD customers | Audit trail for SAR/STR decisions |

---

## 6. Tier 4 — PredictiveAML (EU AI Act)

Required when deploying AI-based AML scoring:

| Field | EU AI Act Article | Notes |
|---|---|---|
| `predictiveAML.modelMetadata.euAiActClassification` | Art. 6(2) + Annex III | Mandatory classification |
| `predictiveAML.modelMetadata.conformityAssessmentReference` | Art. 43 | Required for `high-risk-aml` classification |
| `predictiveAML.predictiveScores[].confidence` | Art. 13(3)(b)(ii) | Per-score confidence mandatory |
| `predictiveAML.explainability` | Art. 13(3)(b)(iii) | Output interpretation mandatory |
| `predictiveAML.dataAggregationMetadata.bcbs239ComplianceLevel` | BCBS 239 / supervisory expectation | Mandatory for G-SIBs and D-SIBs |

---

## 7. Tier 5 — XRPL / Blockchain

Required for XRPL-based VASPs and token issuers:

| Field | Standard | When Required |
|---|---|---|
| `kycProfile.blockchainAccountIds[].xrplCredentialType` | XLS-70 (formerly XLS-40d) | XRPL Credential-gated operations |
| `kycProfile.blockchainAccountIds[].mptIssuanceId` | XLS-33d (MPT) | MPT holder authorisation |
| `kycProfile.blockchainAccountIds[].xrplPermissionedDomainId` | XLS-80d | Permissioned domain participation |
| `kycProfile.blockchainAccountIds[].xrplAuthorizedCredentialTypes[]` | XLS-80d | Domain-level credential acceptance |
| `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer` | XLS-96d | Confidential transaction compliance |
| `kycProfile.blockchainAccountIds[].xrplFreezeType` | XRPL freeze mechanism | Sanctions enforcement status |
| `kycProfile.blockchainAccountIds[].xrplClawbackEnabled` | XRPL clawback | Regulatory seizure capability |
| `kycProfile.blockchainAccountIds[].lightningNodePubkey` | Lightning Network / FATF R.16 | Lightning VASP Travel Rule |
| `kycProfile.blockchainAccountIds[].bitcoinScriptType` | Bitcoin UTXO analytics | Chain analytics integration |

---

## 8. Gap Analysis Summary by Entity Type

| Entity Type | Minimum Tier | Recommended Tier |
|---|---|---|
| Non-EU VASP (Travel Rule only) | Tier 1 | Tier 1 |
| EU CASP / VASP (MiCA + AMLR) | Tier 2 | Tier 3 |
| EU Bank (AMLR 2027) | Tier 2 | Tier 3–4 |
| G-SIB / D-SIB | Tier 2 | Tier 4 (BCBS 239) |
| XRPL VASP / MPT issuer | Tier 1 + Tier 5 | Tier 2 + Tier 5 |
| AI-driven AML platform | Tier 4 | Tier 4 (mandatory) |

---

*Last updated: April 2026 — OpenKYCAML v1.7.0*
