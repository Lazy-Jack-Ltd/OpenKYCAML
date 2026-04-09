# Cell Company Structures — PCC and ICC KYC/AML Mapping

This document describes the cell company support added in **OpenKYCAML v1.11.0** and updated in **v1.11.1**, covering Protected Cell Companies (PCC) and Incorporated Cell Companies (ICC). It explains the legal structures, field-level schema design, regulatory rationale, and alignment with FATF, AMLR 2024, IVMS 101, and eIDAS.

---

## Table of Contents

1. [Overview — PCC and ICC Structures](#1-overview)
2. [CellCompanyType Classification](#2-cellcompanytype)
3. [CellCompanyDetails Field Reference](#3-cellcompanydetails)
4. [ParentCellCompanyReference](#4-parentcellcompanyreference)
5. [LegalPerson Cell Extensions](#5-legalperson-extensions)
6. [Schema-Enforced Constraints](#6-schema-enforced-constraints)
7. [Regulatory Alignment](#7-regulatory-alignment)
8. [Backward Compatibility](#8-backward-compatibility)

---

## 1. Overview

A **Protected Cell Company (PCC)** is a single legal entity (the PCC Core) with any number of non-incorporated cells. Cells share the PCC's legal personality — they transact through the PCC — but statute provides ring-fenced asset/liability segregation between cells and the Core.

An **Incorporated Cell Company (ICC)** grants each cell its own independent legal personality. Each ICC cell is a separate registered company (with its own registration number, LEI eligibility, and full contracting capacity) while remaining within the ICC structure.

Cell companies are widely used in:
- **Insurance-linked securities (ILS)** and catastrophe bonds (Guernsey, Jersey, Cayman Islands)
- **Securitisation vehicles** (Malta, Isle of Man)
- **Regulated investment funds** (Gibraltar, Vermont, South Carolina insurance captives)

Without explicit schema support, cells are often described using ad-hoc fields, making beneficial-ownership tracing ambiguous and increasing reconciliation friction in FATF/AMLR/IVMS 101 flows.

---

## 2. CellCompanyType

| Value | Meaning | Legal Personality |
|---|---|---|
| `NONE` | Ordinary non-cell company | Yes |
| `PCC_CORE` | Overarching PCC entity | Yes (single entity for all cells) |
| `PCC_CELL` | Cell within a PCC | No — transacts through PCC Core |
| `ICC_CORE` | ICC coordinating core | Yes |
| `ICC_CELL` | Incorporated cell (own company) | Yes — own registration, LEI, filing |

---

## 3. CellCompanyDetails

| Field | Type | Pattern / Format | Required | Notes |
|---|---|---|---|---|
| `cellCompanyType` | string (enum) | `CellCompanyType` | Yes | Core classification field |
| `cellIdentifier` | string | `^[A-Za-z0-9 \-]{1,64}$` | No | Unique cell number/designator. **This is the sole cell identifier field; do not use `cellCompanyIdentifier` (historical draft name, never adopted).** |
| `cellName` | string | — | No | Human-readable cell name, max 128 chars |
| `cellRegistrationNumber` | string | `^[A-Z0-9]{1,35}$` | No | ICC cells only — registration number issued by authority |
| `hasIndependentLegalPersonality` | boolean | — | No | `true` for ICC cells, `false` for PCC cells |
| `isCellCompanyIssuer` | boolean | — | No | `true` when cell is a securities issuer vehicle |
| `issuancePurpose` | string (enum) | 5 values | No | Required when `isCellCompanyIssuer: true` |
| `cellSpecificInstrumentReference` | string | `format: "uri"` | No | Link to prospectus / term sheet |

### Issuance Purpose Values

| Value | Description |
|---|---|
| `INSURANCE_LINKED_SECURITY` | ILS (catastrophe bonds, sidecars, etc.) |
| `CATASTROPHE_BOND` | Cat bond specifically |
| `STRUCTURED_NOTE` | Structured credit/equity notes |
| `DEBT_INSTRUMENT` | Bonds, notes, sukuk |
| `OTHER` | Other issuance purpose |

---

## 4. ParentCellCompanyReference

Mandatory for any cell (`PCC_CELL` or `ICC_CELL`). Provides the link required for FATF beneficial-ownership chain tracing and AMLR Art. 26 legal entity verification.

> **Recursion-depth guidance (v1.11.2):** Use `legalEntityIdentifier` + `jurisdiction` as the primary reference link. For performance-critical or deeply-nested cell-of-cell payloads, avoid embedding full parent objects — reference by identifier only.

| Field | Type | Pattern | Required | Notes |
|---|---|---|---|---|
| `legalEntityIdentifier` | string | `^[A-Z0-9]{1,35}$` | Yes | LEI (20-char) preferred; registration number also accepted |
| `jurisdiction` | string | `^[A-Z]{2}$` | Yes | ISO 3166-1 alpha-2 of parent Core's jurisdiction |
| `parentName` | string | — | No | Registered name of parent Core, max 128 chars |

---

## 5. LegalPerson Cell Extensions

All optional. Absent for ordinary non-cell companies.

| Field | $ref | Purpose |
|---|---|---|
| `cellCompanyDetails` | `CellCompanyDetails` | Cell classification and metadata |
| `parentCellCompanyReference` | `ParentCellCompanyReference` | Parent Core link — FATF / AMLR Art. 26 |
| `cellRiskProfileOverride` | `RiskSnapshot` | Cell-level risk where cell risk differs from Core |
| `cellSourceOfFundsWealth` | `SourceOfFundsWealth` | Cell-specific SoF/SoW for AMLR Art. 29 / FATF Rec. 12 EDD |
| `cellAuditMetadata` | `AuditMetadata` | Per-cell audit trail — AMLR Art. 56 5-year retention |

### 5.1 Predictive AML — Cell-Level Scores (v1.11.2)

The optional `predictiveAML.cellLevelPredictiveScores[]` array inside the `PredictiveAML` block allows per-cell predictive risk scoring for PCC/ICC structures. Each entry references a cell by its `cellIdentifier` and carries one or more scores.

Use this in conjunction with `cellRiskProfileOverride` (a `RiskSnapshot` on `LegalPerson`) when individual cells exhibit materially different risk profiles from the parent Core.

| Field | Type | Required | Notes |
|---|---|---|---|
| `cellIdentifier` | string | Yes | References `CellCompanyDetails.cellIdentifier` on the target `LegalPerson` record |
| `scores[].scoreType` | enum | Yes | `transaction_anomaly`, `network_risk`, `velocity_fraud`, `ubo_graph_risk`, `customer_lifetime_risk` |
| `scores[].value` | number 0–100 | Yes | Risk score (0 = lowest, 100 = highest) |
| `scores[].confidence` | number 0–1 | Yes | Model confidence (EU AI Act Art. 13(3)(b)(iv)) |
| `scores[].horizonDays` | integer | No | Forward-looking prediction window (days) |
| `scores[].timestamp` | date-time | No | When this score was computed |

**Example:** See `examples/cell-company/pcc-cell-predictive-aml.json` for a PCC cell with both `cellRiskProfileOverride` and a `predictiveAML.cellLevelPredictiveScores` entry.

---

## 6. Schema-Enforced Constraints (v1.11.1)

The following conditions are enforced as hard JSON Schema `if`/`then` rules. Payloads that violate them **fail schema validation** — they do not produce soft warnings.

| Condition | Schema mechanism | Regulatory basis |
|---|---|---|
| `cellCompanyType` is `PCC_CELL` or `ICC_CELL` → `parentCellCompanyReference` **required** | `LegalPerson` `allOf` `if`/`then` | FATF Rec. 24; AMLR Art. 26(2)(b) — beneficial-ownership chain tracing requires an explicit parent link |
| `isCellCompanyIssuer: true` → `issuancePurpose` **required** | `CellCompanyDetails` `if`/`then` | AML/CFT risk classification; instrument-type disclosure for EDD |

> **Note (v1.11.0 → v1.11.1):** Both of these were originally implemented as soft validator advisories in v1.11.0. They were promoted to hard schema constraints in v1.11.1 because both conditions represent genuine regulatory requirements that must be enforced at the data level, not merely advised upon. The validator business-warning code blocks were removed in the same patch.

---

## 7. Regulatory Alignment

| Requirement | Standard | How Cell Company Fields Address It |
|---|---|---|
| Legal entity transparency | FATF Rec. 24 | `cellCompanyType` + `parentCellCompanyReference` expose the full PCC/ICC hierarchy for beneficial-ownership mapping |
| Legal arrangement disclosure | FATF Rec. 25 | `CellCompanyDetails` describes the cell's legal form and position within the structure |
| Entity verification | AMLR 2024 Art. 26(2)(b) | `parentCellCompanyReference.legalEntityIdentifier` provides the authoritative parent link |
| Source of funds / EDD | AMLR 2024 Art. 29; FATF Rec. 12 | `cellSourceOfFundsWealth` enables cell-level SoF declaration where cell assets differ from Core |
| Record retention | AMLR 2024 Art. 56 | `cellAuditMetadata` provides a per-cell audit trail with `recordCreatedAt` and `recordVersion` |
| Travel Rule counterparty identification | FATF Rec. 16; IVMS 101 | `cellIdentifier` + `cellRegistrationNumber` provide unambiguous cell-level VASP identification |
| eIDAS LPID cross-border registration | eIDAS 2.0 LPID | `cellRegistrationNumber` (for ICC cells with independent legal personality) supports EUID construction |

---

## 8. Backward Compatibility

All additions in v1.11.0 are strictly additive:
- `cellCompanyDetails`, `parentCellCompanyReference`, and the three cell-level $ref fields are all optional on `LegalPerson`.
- Existing LegalPerson records without `cellCompanyDetails` (or with `cellCompanyType: "NONE"`) remain 100% valid.
- No existing required fields, enums, or patterns were modified.

---

*Added in OpenKYCAML v1.11.0 — April 2026. Updated v1.11.1 (hard constraints), v1.11.2 (cellIdentifier disambiguation, recursion-depth guidance, cellLevelPredictiveScores). Maintained by the OpenKYCAML Technical Working Group.*
