# Field Mapping: IVMS 101 × eIDAS 2.0 ARF × EU AMLR

This document maps every significant field in the OpenKYCAML schema to its counterpart in IVMS 101, the eIDAS 2.0 Architecture and Reference Framework (ARF), and the EU Anti-Money Laundering Regulation (AMLR 2024).

---

## 1. Overview

OpenKYCAML is designed to be a **superset** of IVMS 101 while adding:

1. An optional **Verifiable Credential (VC) wrapper** aligned with the W3C VC Data Model v2 and the eIDAS 2.0 ARF (EU Digital Identity Wallet).
2. A **`kycProfile` section** covering the full lifecycle of KYC/AML data required by AMLR Articles 22 and 26, FATF Recommendations 10 and 16, and EBA Risk Factor Guidelines.

All IVMS 101 fields map 1:1 into the `ivms101` block. No IVMS 101 fields are renamed or removed.

---

## 2. Natural Person Fields

| OpenKYCAML Field | IVMS 101 Field | eIDAS ARF Attribute | AMLR Reference |
|---|---|---|---|
| `ivms101.originator.originatorPersons[].naturalPerson.name.nameIdentifiers[].primaryIdentifier` | `Originator.naturalPerson.name.nameIdentifiers[].primaryIdentifier` | `family_name` (ISO/IEC 5218) | Art. 22(2)(a) |
| `ivms101.originator.originatorPersons[].naturalPerson.name.nameIdentifiers[].secondaryIdentifier` | `Originator.naturalPerson.name.nameIdentifiers[].secondaryIdentifier` | `given_name` | Art. 22(2)(a) |
| `ivms101.originator.originatorPersons[].naturalPerson.name.nameIdentifiers[].nameIdentifierType` | `Originator.naturalPerson.name.nameIdentifiers[].nameIdentifierType` | — | — |
| `ivms101.originator.originatorPersons[].naturalPerson.dateAndPlaceOfBirth.dateOfBirth` | `Originator.naturalPerson.dateAndPlaceOfBirth.dateOfBirth` | `birth_date` (ISO 8601) | Art. 22(2)(b) |
| `ivms101.originator.originatorPersons[].naturalPerson.dateAndPlaceOfBirth.placeOfBirth` | `Originator.naturalPerson.dateAndPlaceOfBirth.placeOfBirth` | `birth_place` | Art. 22(2)(b) |
| `ivms101.originator.originatorPersons[].naturalPerson.geographicAddresses[].streetName` | `Originator.naturalPerson.geographicAddresses[].streetName` | `address.street_address` | Art. 22(2)(c) |
| `ivms101.originator.originatorPersons[].naturalPerson.geographicAddresses[].country` | `Originator.naturalPerson.geographicAddresses[].country` | `address.country` (ISO 3166-1) | Art. 22(2)(c) |
| `ivms101.originator.originatorPersons[].naturalPerson.nationalIdentification.nationalIdentifier` | `Originator.naturalPerson.nationalIdentification.nationalIdentifier` | `document_number` | Art. 22(2)(d) |
| `ivms101.originator.originatorPersons[].naturalPerson.nationalIdentification.nationalIdentifierType` | `Originator.naturalPerson.nationalIdentification.nationalIdentifierType` | `document_type` | Art. 22(2)(d) |
| `ivms101.originator.originatorPersons[].naturalPerson.countryOfResidence` | `Originator.naturalPerson.countryOfResidence` | `resident_address.country` | Art. 22(2)(c) |

---

## 3. Legal Entity Fields

| OpenKYCAML Field | IVMS 101 Field | eIDAS ARF Attribute | AMLR Reference |
|---|---|---|---|
| `ivms101.originator.originatorPersons[].legalPerson.name.nameIdentifiers[].legalPersonName` | `Originator.legalPerson.name.nameIdentifiers[].legalPersonName` | `organization_name` | Art. 26(1)(a) |
| `ivms101.originator.originatorPersons[].legalPerson.name.nameIdentifiers[].legalPersonNameIdentifierType` | `Originator.legalPerson.name.nameIdentifiers[].legalPersonNameIdentifierType` | — | — |
| `ivms101.originator.originatorPersons[].legalPerson.nationalIdentification.nationalIdentifier` (LEIX) | `Originator.legalPerson.nationalIdentification.nationalIdentifier` | `legal_entity_identifier` (GLEIF) | Art. 26(1)(b) |
| `ivms101.originator.originatorPersons[].legalPerson.countryOfRegistration` | `Originator.legalPerson.countryOfRegistration` | `established_in` | Art. 26(1)(a) |
| `ivms101.originator.originatorPersons[].legalPerson.geographicAddresses[].streetName` | `Originator.legalPerson.geographicAddresses[].streetName` | `registered_address` | Art. 26(1)(c) |

---

## 4. Travel Rule Fields (IVMS 101)

| OpenKYCAML Field | IVMS 101 Field | FATF Rec 16 Element | AMLR Reference |
|---|---|---|---|
| `ivms101.transferredAmount.amount` | `transferredAmount.amount` | Transfer value | Art. 83(1) |
| `ivms101.transferredAmount.assetType` | `transferredAmount.assetType` | Virtual asset type | Art. 83(1) |
| `ivms101.originatingVASP.originatingVASP.name` | `originatingVASP.name` | Originating VASP name | Art. 83(2)(a) |
| `ivms101.beneficiaryVASP.beneficiaryVASP.name` | `beneficiaryVASP.name` | Beneficiary VASP name | Art. 83(2)(b) |
| `ivms101.originator.accountNumber[]` | `Originator.accountNumber[]` | Virtual asset account / wallet address | FATF Rec 16, Interpretive Note §7 |

---

## 5. Verifiable Credential Wrapper

| OpenKYCAML Field | W3C VC Data Model v2 | eIDAS ARF §6.3 | AMLR Reference |
|---|---|---|---|
| `verifiableCredential.@context` | `@context` | EUDIW Context | — |
| `verifiableCredential.id` | `id` | Credential URI | — |
| `verifiableCredential.type[]` | `type` | `VerifiableAttestation` sub-types | — |
| `verifiableCredential.issuer` | `issuer` | PID Issuer DID | Art. 22(5)(b) — remote onboarding provider |
| `verifiableCredential.issuanceDate` | `issuanceDate` | `validFrom` | — |
| `verifiableCredential.expirationDate` | `expirationDate` | `validUntil` | — |
| `verifiableCredential.credentialSubject.id` | `credentialSubject.id` | User's EUDIW DID | — |
| `verifiableCredential.credentialStatus` | `credentialStatus` | Revocation endpoint | — |
| `verifiableCredential.proof` | `proof` | Signature Suite | Art. 22(5)(b) |

---

## 6. KYC Profile → AMLR / EBA Mapping

| OpenKYCAML Field | AMLR Article | EBA RFG Section | FATF Recommendation |
|---|---|---|---|
| `kycProfile.customerRiskRating.overallRiskRating` | Art. 20(1) — risk-based approach | Chapter 4 | Rec 1, Rec 10 |
| `kycProfile.customerRiskRating.riskFactors` | Art. 20(2) — risk factors | §4.2 Customer risk factors | Rec 10 |
| `kycProfile.dueDiligenceType` | Art. 22 (SDD/CDD/EDD) | Chapter 4 | Rec 10, 12 |
| `kycProfile.customerClassification` | Art. 22(1) | §4.1 | Rec 10 |
| `kycProfile.pepStatus` | Art. 28–31 (PEP provisions) | Chapter 5 | Rec 12 |
| `kycProfile.sanctionsScreening` | Art. 24 (targeted financial sanctions) | — | Rec 6 |
| `kycProfile.adverseMedia` | Art. 20(2)(b) | §4.2.3 | Rec 10 |
| `kycProfile.sourceOfFundsWealth` | Art. 29 (EDD measures) | §5.3 | Rec 12 |
| `kycProfile.beneficialOwnership` | Art. 26 (beneficial owners) | Chapter 6 | Rec 10, 24 |
| `kycProfile.monitoringInfo` | Art. 21 (ongoing monitoring) | Chapter 7 | Rec 10 |
| `kycProfile.onboardingChannel` | Art. 22(5) (non-face-to-face) | §4.3 | Rec 10 |
| `kycProfile.auditMetadata` | Art. 56 (record keeping) | — | Rec 11 |
| `kycProfile.consentRecord` | GDPR Art. 6/9 | — | — |

---

## 7. ISO 20022 Cross-Reference

| OpenKYCAML Field | ISO 20022 Message / Element | Notes |
|---|---|---|
| `ivms101.originator.originatorPersons[].naturalPerson.name` | `pain.001` `Dbtr/Nm` | Natural person name |
| `ivms101.originator.originatorPersons[].legalPerson.nationalIdentification` (LEIX) | `pain.001` `Dbtr/Id/OrgId/LEI` | Legal Entity Identifier |
| `ivms101.originator.accountNumber[]` | `pain.001` `DbtrAcct/Id/IBAN` or `VirtualAccountNo` | Account or wallet |
| `ivms101.transferredAmount.amount` | `pain.001` `Amt/InstdAmt` | Transfer amount |
| `ivms101.transferredAmount.assetType` | `pain.001` `Amt/InstdAmt@Ccy` | Asset/currency |

---

*Maintained by the OpenKYCAML Technical Working Group. For corrections or additions, please open an issue or pull request.*
