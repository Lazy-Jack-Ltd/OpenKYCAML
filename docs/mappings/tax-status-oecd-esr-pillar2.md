# Tax Status, TIN, ESR & Pillar 2 GloBE Mapping (v1.9.0)

> **Standard:** OECD CRS/CARF TIN | EU VAT / National GST-PST | Economic Substance Regulations (ESR) | OECD Pillar 2 GloBE (BEPS 2.0)
> **OpenKYCAML version:** 1.9.0
> **Status:** Production-Ready
> **Last updated:** April 2026

---

## §1 Introduction & Scope

This document maps the `taxStatus` top-level block (added in OpenKYCAML v1.9.0) to four global tax and economic substance regimes that are directly relevant to KYC/AML obligations:

| Regime | Governing Body | AML/KYC Relevance |
|---|---|---|
| TIN / OECD CRS / CARF / FATCA | OECD; IRS (FATCA); national revenue authorities | Mandatory for automatic exchange of financial account information; AMLR Art. 22 tax-residency verification; FATF R.16 Travel Rule originator/beneficiary data |
| VAT / GST / PST / HST | EU (VIES); national tax authorities (India, Australia, Canada, Singapore, etc.) | Entity legitimacy checks; source-of-wealth verification; onboarding due diligence |
| Economic Substance Regulations (ESR) | EU/OECD (BVI, Cayman, UAE, Jersey, Guernsey, Isle of Man, etc.) | Shell-company red-flag prevention under AMLR Art. 26 and EBA ML/TF risk-factor guidelines |
| OECD Pillar 2 GloBE (BEPS 2.0) | OECD Inclusive Framework | Base-erosion and profit-shifting (BEPS) risk scoring; GloBE Information Return (GIR) linkage for predictive AML |

The `taxStatus` block is **optional** at the root level of every OpenKYCAML v1.9.0 payload. All four sub-properties (`tinIdentifiers`, `indirectTaxRegistrations`, `economicSubstance`, `pillarTwo`) are independently optional. Adding `taxStatus` to a v1.9.0 payload introduces **zero breaking changes** for implementers of v1.8.0 or earlier.

---

## §2 OECD CRS / CARF — TIN Identifiers

### 2.1 Standard Overview

The OECD Common Reporting Standard (CRS) and Crypto-Asset Reporting Framework (CARF), together with FATCA, require Reporting Financial Institutions and Crypto-Asset Service Providers to collect and exchange **Taxpayer Identification Numbers (TINs)** for account holders and controlling persons across all jurisdictions of tax residency.

IVMS 101 v1.0 addresses TINs partially via `nationalIdentification.nationalIdentifierType = TXID` (one entry per person, no verification metadata, no multi-jurisdiction array). OpenKYCAML v1.9.0 replaces this with the structured `taxStatus.tinIdentifiers[]` array.

### 2.2 Field Mapping

| OECD CRS / CARF / FATCA Field | OpenKYCAML v1.9.0 Field | Notes |
|---|---|---|
| TIN (account holder) | `taxStatus.tinIdentifiers[].tinValue` | Matches IVMS 101 `nationalIdentification.TXID` for single-jurisdiction cases |
| TIN issuing jurisdiction | `taxStatus.tinIdentifiers[].jurisdiction` | ISO 3166-1 alpha-2 |
| TIN type | `taxStatus.tinIdentifiers[].tinType` | `TIN`, `EIN`, `functionalEquivalent`, `other` |
| TIN verification status | `taxStatus.tinIdentifiers[].verificationStatus` | `verified` / `unverified` / `revoked` / `suspended` |
| TIN verification source | `taxStatus.tinIdentifiers[].verificationSource` | e.g. `OECD-TIN-list`, `HMRC-API`, `IRS-TIN-Matching`, `Revenue-IE` |
| Issuance / confirmation date | `taxStatus.tinIdentifiers[].issuanceDate` | ISO 8601 date-time |

### 2.3 IVMS 101 TXID Migration Path

For Travel Rule payloads where a single TIN is sufficient:

| IVMS 101 (legacy) | OpenKYCAML v1.9.0 (structured) |
|---|---|
| `nationalIdentification.nationalIdentifier` (TXID) | `taxStatus.tinIdentifiers[0].tinValue` |
| `nationalIdentification.countryOfIssue` | `taxStatus.tinIdentifiers[0].jurisdiction` |
| _(no type field)_ | `taxStatus.tinIdentifiers[0].tinType = "TIN"` |
| _(no verification metadata)_ | `taxStatus.tinIdentifiers[0].verificationStatus` + `verificationSource` |

Dual-residency and multi-jurisdiction MNE scenarios require the full `tinIdentifiers[n]` array and cannot be represented in IVMS 101 without proprietary extension.

### 2.4 Jurisdiction-Specific TIN Formats (Selected)

| Jurisdiction | TIN Name | `tinType` | Format Example |
|---|---|---|---|
| US | EIN (entities) | `EIN` | `12-3456789` |
| US | SSN / ITIN (individuals) | `TIN` | `123-45-6789` |
| GB | UTR (Unique Taxpayer Reference) | `functionalEquivalent` | `1234567890` |
| DE | Steueridentifikationsnummer | `TIN` | `86095742719` |
| IE | Tax Registration Number | `TIN` | `IE6336214T` |
| IN | PAN (Permanent Account Number) | `TIN` | `AAPFU0939F` |
| AU | TFN (Tax File Number) | `functionalEquivalent` | `123 456 789` |
| CL | RUT (Rol Unico Tributario) | `functionalEquivalent` | `12.345.678-9` |

---

## §3 EU VAT / National GST-PST — Indirect Tax Registrations

### 3.1 Standard Overview

Value Added Tax (VAT), Goods and Services Tax (GST), Provincial Sales Tax (PST), and Harmonised Sales Tax (HST) registration numbers are **indirect tax identifiers** issued by national revenue authorities. They are distinct from income-tax TINs but frequently serve as the primary entity identifier in corporate onboarding, source-of-wealth verification, and entity legitimacy screening.

Key validation sources:

- **EU VIES** (VAT Information Exchange System) — real-time VAT number validation for all EU member states.
- **India GST Portal** (`https://www.gst.gov.in`) — GSTIN verification by business name or PAN.
- **Australia ABN Lookup** (`https://abr.business.gov.au`) — ABN/GST registration verification.
- **Canada CRA Business Number** registry — HST/PST cross-reference via provincial returns.

### 3.2 Field Mapping

| Standard / Source | OpenKYCAML v1.9.0 Field | Coverage |
|---|---|---|
| EU VAT number (VIES) | `taxStatus.indirectTaxRegistrations[taxType="VAT"]` | Full — jurisdiction + registrationNumber + status |
| India GSTIN | `taxStatus.indirectTaxRegistrations[taxType="GST"]` | Full |
| Australia ABN/GST | `taxStatus.indirectTaxRegistrations[taxType="GST"]` | Full |
| Canada HST | `taxStatus.indirectTaxRegistrations[taxType="HST"]` | Full |
| Canada PST | `taxStatus.indirectTaxRegistrations[taxType="PST"]` | Full |
| US state sales tax | `taxStatus.indirectTaxRegistrations[taxType="salesTax"]` | Full |

### 3.3 Status Values and AML Significance

| `status` | Meaning | AML Action |
|---|---|---|
| `active` | Valid and in good standing | Standard CDD |
| `suspended` | Temporarily inactive by tax authority | Enhanced scrutiny; request explanation |
| `revoked` | Registration cancelled | EDD trigger; escalate to compliance |
| `exempt` | Registered but exempt from charging tax | Document exemption basis |

---

## §4 Economic Substance Regulations — ESR Block

### 4.1 Standard Overview

Following the 2019 EU listing of non-cooperative jurisdictions, BVI, Cayman Islands, UAE, Jersey, Guernsey, and Isle of Man each enacted Economic Substance Regulations (ESR) requiring entities carrying out "relevant activities" (banking, insurance, IP, holding, fund management, shipping, financing/leasing, distribution/service centres, headquarters) to demonstrate adequate economic substance in the jurisdiction.

ESR non-compliance is a **direct AML red flag** under:
- AMLR Art. 26 (legal entity CDD — establishment verification)
- EBA Guidelines on ML/TF risk factors (section on shell companies)
- FATF Recommendation 24 (transparency of legal persons)

### 4.2 Field Mapping

| ESR Requirement | OpenKYCAML v1.9.0 Field | Notes |
|---|---|---|
| Jurisdiction of ESR assessment | `taxStatus.economicSubstance.jurisdiction` | ISO 3166-1 alpha-2 (e.g. `KY`, `VG`, `AE`, `JE`) |
| Entity classification | `taxStatus.economicSubstance.status` | See §4.3 |
| Relevant activities carried out | `taxStatus.economicSubstance.relevantActivities[]` | String array; see §4.4 |
| CIGAs performed in jurisdiction | `taxStatus.economicSubstance.coreIncomeGeneratingActivitiesPerformed` | Boolean — must be `true` for substance test |
| Date of last annual notification | `taxStatus.economicSubstance.lastNotificationDate` | ISO 8601 date |
| Reference of last ESR report | `taxStatus.economicSubstance.lastReportReference` | Opaque reference number or URI |

### 4.3 ESR Status Values

| `status` | Definition | Risk Implication |
|---|---|---|
| `inScope-RelevantEntity` | Entity carries out a relevant activity and is subject to substance tests | Include CIGAs flag and notification date |
| `exempt-TaxResidentElsewhere` | Entity is tax resident in a non-EU-blacklisted jurisdiction — ESR exempt | Document tax residency evidence |
| `exempt-PureEquityHolding` | Pure equity holding entity — only permissible activities allowed | Must confirm no other activities |
| `compliant` | Passed most recent annual substance assessment | No additional action required |
| `nonCompliant` | Failed substance test — CIGAs not adequately performed in jurisdiction | **EDD mandatory; consider SAR** |

### 4.4 Relevant Activity Strings

Standard values for `relevantActivities[]`:

| Activity | ESR Law Reference |
|---|---|
| `holdingCompany` | All ESR jurisdictions |
| `bankingBusiness` | All ESR jurisdictions |
| `insuranceBusiness` | All ESR jurisdictions |
| `fundManagement` | All ESR jurisdictions |
| `financingLeasing` | All ESR jurisdictions |
| `headquartersBusiness` | All ESR jurisdictions |
| `shippingBusiness` | All ESR jurisdictions |
| `distributionServiceCentre` | All ESR jurisdictions |
| `intellectualProperty` | All ESR jurisdictions (enhanced substance test) |

---

## §5 OECD Pillar 2 GloBE — Pillar Two Block

### 5.1 Standard Overview

OECD Pillar 2 (GloBE — Global Anti-Base Erosion rules, BEPS 2.0) imposes a **15% global minimum effective tax rate** on MNE groups with annual consolidated revenue exceeding EUR 750 million. Jurisdictions implementing Pillar 2 require constituent entities to file a **GloBE Information Return (GIR)** with the lead filing jurisdiction.

From an AML perspective, Pillar 2 data enables:
- Detection of base-erosion / profit-shifting red flags (ETR < 15% in low-tax jurisdictions).
- Linkage of GIR references to predictive AML risk scores (`predictiveAML.riskEvolutionHistory`).
- Identification of QDMTT jurisdictions (domestic top-up tax — may signal aggressive tax planning).

### 5.2 Field Mapping

| Pillar 2 / GIR Field | OpenKYCAML v1.9.0 Field | Notes |
|---|---|---|
| In-scope MNE flag | `taxStatus.pillarTwo.inScopeMNE` | Boolean — true if group revenue >= EUR 750 m |
| Consolidated group revenue (EUR) | `taxStatus.pillarTwo.consolidatedRevenueEUR` | Most recent fiscal year; from GIR or consolidated accounts |
| Constituent entity status | `taxStatus.pillarTwo.constituentEntityStatus` | `inScope` / `excluded` / `QDMTT` |
| ETR per jurisdiction | `taxStatus.pillarTwo.etrJurisdictions[]` | Array of `{jurisdiction, etr}` — ETR as decimal (0.15 = 15%) |
| Safe harbour election | `taxStatus.pillarTwo.safeHarbourApplied` | `SimplifiedETR` / `SubstanceBased` / `DeMinimis` / `none` |
| GIR filing reference | `taxStatus.pillarTwo.girFilingReference` | Reference number or URI of most recent GIR |
| GIR filing date | `taxStatus.pillarTwo.lastGIRDate` | ISO 8601 date-time |

### 5.3 ETR Threshold and AML Risk Scoring

| ETR Range | Risk Implication | Recommended Action |
|---|---|---|
| `etr >= 0.15` | GloBE minimum met — no top-up tax | Standard CDD |
| `0.10 <= etr < 0.15` | Below global minimum — top-up tax may apply | Enhanced CDD; verify GIR filing |
| `etr < 0.10` | Significant low-tax position | EDD trigger; BEPS risk flag in `predictiveAML` |
| No ETR data + `inScopeMNE = true` | Missing GIR — compliance gap | Request GIR reference; flag for EDD |

### 5.4 Safe Harbour Types

| `safeHarbourApplied` | Description |
|---|---|
| `SimplifiedETR` | Transitional CbCR Safe Harbour — simplified ETR test using Country-by-Country Report data |
| `SubstanceBased` | Substance-Based Income Exclusion — payroll and tangible assets carve-out reduces top-up tax |
| `DeMinimis` | De Minimis Exclusion — jurisdiction revenue < EUR 10 m and income < EUR 1 m |
| `none` | No safe harbour elected; full GloBE top-up tax calculation applies |

### 5.5 Predictive AML Linkage

`taxStatus.pillarTwo` feeds directly into the `predictiveAML` extension:
- Low ETR jurisdictions (`etr < 0.10`) should trigger a `HIGH` risk flag in `predictiveAML.predictiveScores`.
- `girFilingReference` should be recorded in `predictiveAML.dataAggregationMetadata.dataSourcesUsed[]`.
- ESR `nonCompliant` status compounds the BEPS risk signal.

---

## §6 Compliance Notes & Backward Compatibility

### 6.1 Backward Compatibility

| Version | Impact |
|---|---|
| v1.8.0 and earlier | **Zero breaking changes.** The `taxStatus` root property is fully optional. All existing v1.8.0 payloads remain valid against the v1.9.0 schema. |
| v1.9.0 | New `taxStatus` property available at root level. All four sub-properties independently optional. |

### 6.2 FATF R.16 / IVMS 101 Alignment

- For Travel Rule compliance, `taxStatus.tinIdentifiers[]` **supersedes** IVMS 101 `nationalIdentification.TXID` for structured TIN data. Implementers MAY include both for backward compatibility with pure-IVMS 101 counterparties.
- `tinIdentifiers[0].tinValue` with `tinType = "TIN"` maps 1:1 to the IVMS 101 TXID field.

### 6.3 AMLR Art. 22 Third-Party CDD Reliance

When relying on third-party CDD under AMLR Art. 22, the `taxStatus` block should be included in the shared CDD payload to satisfy tax-residency verification requirements. The `verificationSource` field provides the provenance chain required for AMLR audit trails.

### 6.4 ESR Shell Company Red-Flag Protocol

When `taxStatus.economicSubstance.status = "nonCompliant"`:
1. Escalate customer risk rating to `HIGH`.
2. Require `dueDiligenceType = "EDD"`.
3. Document the ESR non-compliance in `kycProfile.adverseMedia` or the compliance notes field.
4. Consider filing a Suspicious Activity Report (SAR) if combined with other risk indicators.

---

*Maintained by the OpenKYCAML Technical Working Group. For corrections or additions, please open an issue or pull request.*
