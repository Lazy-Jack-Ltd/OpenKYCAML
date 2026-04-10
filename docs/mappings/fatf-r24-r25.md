# FATF Recommendations R.24 and R.25 — Beneficial Ownership Mapping

This document provides a detailed field-level mapping of **FATF Recommendation 24** (Transparency and Beneficial Ownership of Legal Persons) and **FATF Recommendation 25** (Transparency and Beneficial Ownership of Legal Arrangements) as revised in the **March 2022 updates** to OpenKYCAML v1.7.0. It is a companion to `fatf-r24-r25.yaml`.

**Key regulatory changes addressed:**
- FATF 2022 R.24 revision: multiple-mechanism approach (registries + alternative mechanisms); nominee identification; bearer share prohibition
- FATF 2022 R.25 revision: trustee identification; class-of-beneficiary disclosure; protector/enforcer identification

---

## 1. FATF R.24 — Beneficial Ownership of Legal Persons

### 1.1 Core Information Requirements (R.24 para. 1)

| FATF R.24 Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|
| Name of the legal person | `ivms101.originator.originatorPersons[].legalPerson.name.nameIdentifiers[]` (LEGL) | Legal/official name |
| Legal form and proof of existence | `legalPerson.entityType` + `legalPerson.legalFormCode` (ISO 20275 ELF) | `entityType` enum: COMPANY, TRUST, FOUNDATION, PARTNERSHIP, OTHER |
| Powers that regulate and bind the legal person | `legalPerson.lpid.mandates[]` | Representatives with `roleOrPower`, `validFrom`/`validUntil` |
| Address of registered office or place of business | `ivms101.originator.originatorPersons[].legalPerson.*address` | Via IVMS 101 GeographicAddress |
| List of directors | `legalPerson.lpid.mandates[]` where `roleOrPower` = "DIRECTOR" | Mandate array used for director disclosure |
| **Basic beneficial ownership information** | `kycProfile.beneficialOwnership[]` | `ownershipPercentage`, `ownershipType`, `controlMechanism` |
| UBO name, nationality, DoB, country of residence | `kycProfile.beneficialOwnership[].person.naturalPerson.*` | Full NaturalPerson $def with IVMS 101 fields |
| Nature and extent of interest | `kycProfile.beneficialOwnership[].controlMechanism` + `ownershipType` | SHAREHOLDING, VOTING_RIGHTS, CONTRACTUAL, DE_FACTO_CONTROL |

### 1.2 Bearer Shares (R.24 Interpretive Note para. 6)

| FATF Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|
| Identify and record bearer share issuance | `kycProfile.beneficialOwnership[].nomineeFlags.bearerShareFlag` | New in v1.7.0; true = bearer shares in issue; triggers EDD |
| Immobilisation or conversion status | `kycProfile.dueDiligenceType` = `EDD` when `bearerShareFlag` = true | Validator warning generated |

### 1.3 Nominee Shareholders and Directors (R.24 Interpretive Note paras. 7–9)

| FATF Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|
| Identify nominee acting on behalf of UBO | `kycProfile.beneficialOwnership[].nomineeFlags.isNominee` | New in v1.7.0; true = nominee arrangement |
| Verify identity of actual owner (nominator) | `kycProfile.beneficialOwnership[].nomineeFlags.nominatorIdentified` | Confirms nominator has been identified and verified |
| Role in arrangement | `kycProfile.beneficialOwnership[].roleInArrangement` | NOMINEE value available in enum |

### 1.4 Multi-Tier Ownership Chains (R.24 Interpretive Note paras. 10–12)

| FATF Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|
| Penetrate ownership chain to UBO level | `kycProfile.beneficialOwnership[].ownershipChainDepth` | Integer depth (1 = direct; 2+ = via intermediaries) |
| Intermediate entity details | `kycProfile.beneficialOwnership[].intermediateEntities[]` | Full `LegalPerson` $def per tier; jurisdiction, ownership %, control mechanism |
| UBO threshold (25% or lower) | `kycProfile.beneficialOwnership[].ownershipPercentage` | Standard threshold; jurisdictions may apply lower thresholds |

---

## 2. FATF R.25 — Beneficial Ownership of Legal Arrangements

### 2.1 Trust Information Requirements (R.25 para. 1)

| FATF R.25 Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|
| Name of the trust | `ivms101.originator.originatorPersons[].legalPerson.name.nameIdentifiers[]` | Trust name as LEGL |
| Country of administration | `legalPerson.countryOfRegistration` | ISO 3166-1 alpha-2 |
| **Settlor** | `kycProfile.beneficialOwnership[].roleInArrangement` = `SETTLOR` | New in v1.7.0; also `legalPerson.trustDetails.settlors[]` (v1.4.0) |
| **Trustee(s)** | `kycProfile.beneficialOwnership[].roleInArrangement` = `TRUSTEE` | Also `legalPerson.trustDetails.trustees[]` |
| **Protector(s)** | `kycProfile.beneficialOwnership[].roleInArrangement` = `PROTECTOR` | Also `legalPerson.trustDetails.protectors[]` |
| **Beneficiaries or class of beneficiaries** | `kycProfile.beneficialOwnership[].roleInArrangement` = `BENEFICIARY_CLASS` | Also `legalPerson.trustDetails.beneficiaryClass` (free text class description) |
| **Enforcer** | `kycProfile.beneficialOwnership[].roleInArrangement` = `ENFORCER` | Foundation/STAR trust enforcer |
| Trust deed reference | `kycProfile.beneficialOwnership[].trustInstrumentReference` | New in v1.7.0; URI/documentId of trust instrument |

### 2.2 Other Legal Arrangements (Foundations, Partnerships)

| FATF R.25 Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|
| Foundation founders | `legalPerson.foundationDetails.founders[]` + `roleInArrangement` = `FOUNDER` | v1.4.0 typed sub-object |
| Foundation council | `legalPerson.foundationDetails.councilMembers[]` + `roleInArrangement` = `COUNCIL_MEMBER` | |
| Partnership general/limited partners | `legalPerson.partnershipDetails.generalPartners[]` / `limitedPartners[]` + `roleInArrangement` = `PARTNER` | |
| Charter/instrument reference | `kycProfile.beneficialOwnership[].trustInstrumentReference` | Reused for foundation charter, partnership deed |

### 2.3 Document Evidence (R.25 para. 4)

| FATF Requirement | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|
| Trust deed / instrument on file | `identityDocuments.legalEntityDocuments[]` type `TRUST_DEED` | With `kycProfile.beneficialOwnership[].verifyingDocumentRefs[]` |
| Beneficiary class description document | `identityDocuments.legalEntityDocuments[]` type `CONSTITUTIONAL_DOCUMENT` | |

---

## 3. Coverage Summary

| FATF Requirement | Coverage | Schema Field |
|---|---|---|
| R.24 — Basic BO information | ✅ Full | `kycProfile.beneficialOwnership[]` |
| R.24 — Multi-tier chain | ✅ Full | `intermediateEntities[]` + `ownershipChainDepth` |
| R.24 — Bearer share flag | ✅ Full (v1.7.0) | `nomineeFlags.bearerShareFlag` |
| R.24 — Nominee identification | ✅ Full (v1.7.0) | `nomineeFlags.isNominee` + `nominatorIdentified` |
| R.25 — Trust parties (settlor/trustee/protector/class) | ✅ Full (v1.4.0 + v1.7.0) | `trustDetails.*` + `roleInArrangement` |
| R.25 — Trust instrument reference | ✅ Full (v1.7.0) | `trustInstrumentReference` |
| R.25 — Foundation and partnership | ✅ Full (v1.4.0) | `foundationDetails.*` + `partnershipDetails.*` |

---

*Last updated: April 2026 — OpenKYCAML v1.12.0*
