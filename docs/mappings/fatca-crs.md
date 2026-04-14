# FATCA & CRS Mapping (v1.9.1)

> **Standards:** US FATCA (Chapter 4, IRC §1471–1474) | OECD Common Reporting Standard (CRS) | OECD CARF
> **OpenKYCAML version:** 1.9.1
> **Status:** Production-Ready
> **Last updated:** April 2026

---

## §1 Introduction & Scope

This document describes the mapping of US FATCA and OECD CRS/CARF requirements to the OpenKYCAML v1.9.1 `taxStatus` block. While FATCA and CRS share broadly aligned due-diligence and self-certification data requirements, production KYC/AML platforms surface FATCA-specific artifacts (GIIN, Chapter 4 classification, withholding agent references) that the generic `tinIdentifiers[]` block does not make fully machine-readable. OpenKYCAML v1.9.1 adds two first-class sub-objects to `taxStatus`:

| New field (v1.9.1) | Purpose |
|---|---|
| `taxStatus.crsTaxResidencies[]` | Enhanced per-jurisdiction CRS data: TIN + verification + self-certification date + controlling-person flag |
| `taxStatus.fatcaStatus` | FATCA GIIN, Chapter 4 classification, US TIN flag, IRS Notice 2024-78 relief, FFI List verification |

Both additions are **fully backward-compatible** — existing v1.9.0 and v1.8.0 payloads require no changes.

### 1.1 Relationship to tinIdentifiers[]

`taxStatus.tinIdentifiers[]` (added in v1.9.0) remains the canonical multi-purpose TIN array and continues to satisfy ~95% of FATCA/CRS KYC/AML data needs. The new first-class fields are **additive enrichment** for institutions that need to expose FATCA GIIN validation and CRS controlling-person flags as distinct, queryable data points.

| Scenario | Recommended fields |
|---|---|
| Simple TIN exchange (CRS, CARF, IVMS 101 migration) | `tinIdentifiers[]` only |
| Full CRS self-certification with multi-residency | `crsTaxResidencies[]` (plus `tinIdentifiers[]` for IVMS 101 backward compat) |
| FATCA FFI due-diligence and withholding compliance | `fatcaStatus` (plus `tinIdentifiers[tinType=EIN]` for US TIN) |
| Full AEOI compliance (FATCA + CRS + CARF) | All three |

---

## §2 OECD CRS — crsTaxResidencies[]

### 2.1 Standard Overview

The OECD Common Reporting Standard (CRS) requires Reporting Financial Institutions (RFIs) to:
1. Obtain a self-certification from each account holder declaring all jurisdictions of tax residency.
2. Collect and validate the TIN issued by each jurisdiction of residency.
3. Separately identify and report Controlling Persons of Passive NFEs.
4. Exchange account information via OECD CRS XML Schema v2.0 under bilateral Competent Authority Agreements.

### 2.2 Field Mapping

| OECD CRS XML / Self-Cert Field | OpenKYCAML v1.9.1 Field | Notes |
|---|---|---|
| AccountHolder/TIN + TINCountry | `taxStatus.crsTaxResidencies[].tinValue` + `jurisdiction` | ISO 3166-1 alpha-2 |
| TIN verification status | `taxStatus.crsTaxResidencies[].tinVerificationStatus` | `verified / unverified / relief-applied / not-required` |
| Self-certification date | `taxStatus.crsTaxResidencies[].selfCertificationDate` | ISO 8601 date-time |
| ControllingPerson indicator | `taxStatus.crsTaxResidencies[].controllingPersonFlag` | `true` for Passive NFE controlling persons |
| Multiple tax residencies | `taxStatus.crsTaxResidencies[]` (array) | One entry per jurisdiction |
| CRS self-cert reason codes | `tinVerificationStatus = "not-required"` or `"relief-applied"` | Maps to CRS reason codes A/B/C |

### 2.3 TIN Verification Status Mapping to CRS Reason Codes

| CRS Reason Code | Meaning | `tinVerificationStatus` |
|---|---|---|
| No reason code (TIN present) | TIN obtained and validated | `verified` |
| No reason code (TIN present, not yet validated) | TIN obtained but not validated | `unverified` |
| Reason A | Jurisdiction does not issue TINs | `not-required` |
| Reason B | TIN not yet obtained (new account / in process) | `unverified` |
| Reason C | Temporary exemption / grace period applies | `relief-applied` |

### 2.4 Controlling Person (Passive NFE)

For Passive NFE accounts, a separate `CrsTaxResidency` entry with `controllingPersonFlag: true` must be included for each controlling person. This maps to the OECD CRS XML `ControllingPerson` element with its own TIN and residency jurisdiction.

---

## §3 US FATCA — fatcaStatus

### 3.1 Standard Overview

The US Foreign Account Tax Compliance Act (FATCA, IRC §§1471–1474) requires:
- Foreign Financial Institutions (FFIs) to register with the IRS and obtain a GIIN.
- Withholding agents to verify GIIN validity against the IRS FFI List (published monthly).
- Chapter 4 entity classification to determine withholding and reporting obligations.
- US TIN collection for US-reportable accounts (subject to IRS Notice 2024-78 temporary relief for pre-existing accounts in Model 1 IGA jurisdictions through 2027).

### 3.2 GIIN Structure and Validation

The GIIN follows the IRS format `XXXXXX.XXXXX.XX.XXX`:

| Segment | Length | Description |
|---|---|---|
| FATCA ID | 6 chars | Unique entity identifier assigned by IRS |
| GIIN suffix | 5 chars | Branch / sponsored-entity suffix (or `00000` for lead FFI) |
| Category code | 2 chars | Entity type code (e.g. `LE` = lead FFI, `SL` = sponsored direct reporting NFFE) |
| Country code | 3 chars | OECD 3-character numeric country code |

OpenKYCAML validates the GIIN against the regex `^[0-9A-Z]{6}\.[0-9A-Z]{5}\.[0-9A-Z]{2}\.[0-9A-Z]{3}$`.

### 3.3 Field Mapping

| FATCA / IRS Field | OpenKYCAML v1.9.1 Field | Notes |
|---|---|---|
| GIIN (IRS FFI List) | `taxStatus.fatcaStatus.giin` | 19-char regex-validated; must be verified monthly |
| Chapter 4 classification | `taxStatus.fatcaStatus.chapter4Classification` | 8-value enum; see §3.4 |
| US TIN required flag | `taxStatus.fatcaStatus.usTinRequired` | Boolean — false for exempt beneficial owners |
| IRS Notice 2024-78 relief | `taxStatus.fatcaStatus.temporaryReliefApplied` | True = Model 1 IGA pre-existing account relief (2025–2027) |
| FFI List verification date | `taxStatus.fatcaStatus.ffiListVerificationTimestamp` | ISO 8601; refresh every 35 days |
| Withholding agent / sponsor | `taxStatus.fatcaStatus.withholdingAgentReference` | For sponsored entities and Model 2 IGA |

### 3.4 Chapter 4 Classification Values

| `chapter4Classification` | Treasury Reg Reference | Description |
|---|---|---|
| `participatingFFI` | §1.1471-5(e)(1)(i) | FFI with IRS FFI Agreement; full FATCA reporting |
| `registeredDeemedCompliantFFI` | §1.1471-5(e)(1)(ii) | IRS-registered, deemed-compliant — reduced reporting obligations |
| `certifiedDeemedCompliantFFI` | §1.1471-5(e)(2) | Self-certified deemed-compliant — no IRS registration required |
| `sponsoredDirectReportingNFFE` | §1.1472-1(c)(3) | NFFE reporting directly to IRS via US sponsoring entity |
| `exemptBeneficialOwner` | §1.1471-6 | Government entity, central bank, retirement fund, international org |
| `nonFinancialNonReportingEntity` | §1.1472-1(c)(1)–(2) | Active NFFE, start-up NFFE, non-profit NFFE |
| `nonParticipatingFFI` | §1.1471-4 (absent) | FFI not registered and not deemed-compliant; 30% withholding applies |
| `other` | — | Classification not covered by the above |

### 3.5 FATCA + CRS Interoperability

Under Model 1 IGAs, FATCA reporting for accounts in IGA jurisdictions is routed through the local CRS/AEOI infrastructure (local competent authority → IRS). This means:
- `taxStatus.crsTaxResidencies[]` covers the CRS self-certification data also used for FATCA due-diligence.
- `taxStatus.fatcaStatus` adds FATCA-only artifacts (GIIN, Chapter 4, withholding agent) not covered by CRS.
- `taxStatus.tinIdentifiers[tinType=EIN]` or `[tinType=TIN]` with `jurisdiction=US` carries the US TIN value for both Chapter 3 and Chapter 4 withholding.

---

## §4 PredictiveAML Synergy

`taxStatus.fatcaStatus` feeds directly into the `predictiveAML` extension (added in v1.7.0):

| fatcaStatus condition | predictiveAML risk signal |
|---|---|
| `chapter4Classification = "nonParticipatingFFI"` | HIGH risk — 30% withholding indicator; possible sanctions linkage |
| `giin` absent + `usTinRequired = true` | MEDIUM risk — FATCA registration gap; EDD recommended |
| `ffiListVerificationTimestamp` > 35 days old | LOW/MEDIUM — stale FFI List check; refresh required |
| `temporaryReliefApplied = true` + pre-existing account | Informational — document relief basis in audit trail |

---

## §5 Compliance Notes

### 5.1 Backward Compatibility

| Version | Impact |
|---|---|
| v1.9.0 and earlier | Zero breaking changes. `crsTaxResidencies` and `fatcaStatus` are independently optional. |
| v1.9.1 | Both new sub-objects available. Existing v1.9.0 payloads validate green against v1.9.1 schema. |

### 5.2 IRS Notice 2024-78

IRS Notice 2024-78 extends the temporary relief for FFIs in Model 1 IGA jurisdictions from collecting US TINs for pre-existing accounts from 2023 through 2027 (subject to annual confirmation). Set `temporaryReliefApplied: true` during this period and `usTinRequired: true` to ensure the TIN collection obligation is documented for post-relief-period compliance.

---

*Maintained by the OpenKYCAML Technical Working Group. For corrections or additions, please open an issue or pull request.*
