# OpenKYCAML Schema Reference

This document provides a field-by-field reference for the
[OpenKYCAML Hybrid Extended Schema](../schema/kyc-aml-hybrid-extended.json)
(version **1.0.0**).

---

## Top-Level Structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schemaVersion` | `string` | ✅ | Must be `"1.0.0"`. |
| `profileType` | `string` | ✅ | One of `naturalPerson`, `legalEntity`, or `hybrid`. |
| `naturalPerson` | object | — | Identity data for an individual. |
| `legalEntity` | object | — | Identity data for a company or organization. |
| `travelRule` | object | — | FATF Travel Rule (IVMS 101) transfer data. |
| `verifiableCredential` | object | — | W3C Verifiable Credential wrapper. |
| `riskAssessment` | object | — | AML/CFT risk scoring and screening results. |
| `metadata` | object | — | Record-keeping metadata. |

---

## Natural Person

Describes an individual's identity.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name.firstName` | `string` | ✅ | |
| `name.lastName` | `string` | ✅ | |
| `name.middleName` | `string` | — | |
| `name.nameLocal` | `string` | — | Name in local script. |
| `dateOfBirth` | `date` | ✅ | ISO 8601. |
| `placeOfBirth` | `string` | — | |
| `nationality` | `string[]` | — | ISO 3166-1 alpha-2 codes. |
| `address` | Address | — | See [Address](#address). |
| `identificationDocuments` | Document[] | — | See [Identification Document](#identification-document). |
| `contactDetails` | Contact | — | See [Contact Details](#contact-details). |
| `politicallyExposedPerson` | `boolean` | — | PEP flag. |
| `sourceOfFunds` | `string` | — | |
| `sourceOfWealth` | `string` | — | |
| `occupation` | `string` | — | |

---

## Legal Entity

Describes a company, trust, or other organization.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `legalName` | `string` | ✅ | Official registered name. |
| `tradingName` | `string` | — | Business/trading name. |
| `registrationNumber` | `string` | — | |
| `leiCode` | `string` | — | 20-character LEI. |
| `incorporationDate` | `date` | — | |
| `incorporationCountry` | `string` | ✅ | ISO 3166-1 alpha-2. |
| `entityType` | `string` | — | `corporation`, `partnership`, `sole_proprietorship`, `trust`, `foundation`, `government`, `ngo`, `other`. |
| `registeredAddress` | Address | — | |
| `beneficialOwners` | Owner[] | — | See [Beneficial Owner](#beneficial-owner). |
| `directors` | object[] | — | Each requires `name`. |
| `contactDetails` | Contact | — | |

---

## Travel Rule (IVMS 101)

Carries FATF Travel Rule data for virtual asset transfers.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `originator` | Party | ✅ | See [Travel Rule Party](#travel-rule-party). |
| `beneficiary` | Party | ✅ | |
| `originatingVASP` | VASP | ✅ | See [VASP](#vasp). |
| `beneficiaryVASP` | VASP | ✅ | |
| `transactionReference` | `string` | — | Unique TX ID. |
| `transferAmount.amount` | `string` | ✅ | Numeric string. |
| `transferAmount.currency` | `string` | ✅ | ISO 4217 or asset code. |
| `transferDate` | `date-time` | — | |

### Travel Rule Party

| Field | Type | Required |
|-------|------|----------|
| `name` | `string` | ✅ |
| `accountNumber` | `string` | ✅ |
| `address` | Address | — |
| `dateOfBirth` | `date` | — |
| `placeOfBirth` | `string` | — |
| `nationalIdentification` | `string` | — |

### VASP

| Field | Type | Required |
|-------|------|----------|
| `name` | `string` | ✅ |
| `leiCode` | `string` | — |
| `registrationCountry` | `string` | — |
| `address` | Address | — |

---

## Verifiable Credential

W3C VC wrapper enabling decentralized identity interoperability.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `@context` | `string[]` | ✅ | JSON-LD contexts. |
| `type` | `string[]` | ✅ | Credential types. |
| `issuer` | `string` (URI) | ✅ | DID or URI. |
| `issuanceDate` | `date-time` | ✅ | |
| `expirationDate` | `date-time` | — | |
| `credentialSubject` | object | ✅ | The KYC payload. |
| `proof` | object | — | Digital signature. |

---

## Risk Assessment

AML/CFT risk evaluation results.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `riskLevel` | `string` | ✅ | `low`, `medium`, `high`, `prohibited`. |
| `riskScore` | `number` | — | 0–100. |
| `assessmentDate` | `date-time` | ✅ | |
| `nextReviewDate` | `date` | — | |
| `sanctions.screened` | `boolean` | — | |
| `sanctions.matched` | `boolean` | — | |
| `sanctions.lists` | `string[]` | — | Lists checked. |
| `pepStatus.screened` | `boolean` | — | |
| `pepStatus.matched` | `boolean` | — | |
| `adverseMedia.screened` | `boolean` | — | |
| `adverseMedia.matched` | `boolean` | — | |

---

## Shared Types

### Address

| Field | Type | Required |
|-------|------|----------|
| `streetAddress` | `string` | — |
| `city` | `string` | — |
| `stateProvince` | `string` | — |
| `postalCode` | `string` | — |
| `country` | `string` | ✅ |

### Identification Document

| Field | Type | Required |
|-------|------|----------|
| `documentType` | `string` | ✅ |
| `documentNumber` | `string` | ✅ |
| `issuingCountry` | `string` | ✅ |
| `issueDate` | `date` | — |
| `expiryDate` | `date` | — |

Document types: `passport`, `national_id`, `drivers_license`,
`residence_permit`, `other`.

### Contact Details

| Field | Type | Required |
|-------|------|----------|
| `email` | `string` (email) | — |
| `phone` | `string` | — |
| `website` | `string` (URI) | — |

### Beneficial Owner

| Field | Type | Required |
|-------|------|----------|
| `name` | `string` | ✅ |
| `dateOfBirth` | `date` | — |
| `nationality` | `string` | — |
| `ownershipPercentage` | `number` | ✅ |
| `controlType` | `string` | — |

### Metadata

| Field | Type | Required |
|-------|------|----------|
| `createdAt` | `date-time` | — |
| `updatedAt` | `date-time` | — |
| `createdBy` | `string` | — |
| `source` | `string` | — |
| `jurisdiction` | `string` | — |
| `dataClassification` | `string` | — |
