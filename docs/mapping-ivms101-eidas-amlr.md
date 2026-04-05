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

OpenKYCAML v1.3.0 ships a complete ISO 20022 bridge layer in [`iso20022-integration/`](../iso20022-integration/). The table below maps key OpenKYCAML fields to their ISO 20022 counterparts; for the full bidirectional mapping and gap analysis see [`iso20022-integration/mapping/`](../iso20022-integration/mapping/).

### 7.1 Standard Field Mapping (ISO 20022 native elements)

| OpenKYCAML Field | ISO 20022 Message / Element | Notes |
|---|---|---|
| `ivms101.originator.originatorPersons[].naturalPerson.name` | `pacs.008`/`pain.001` `Dbtr/Nm` | Natural person display name |
| `ivms101.originator.originatorPersons[].legalPerson.nationalIdentification` (LEIX) | `pacs.008`/`pain.001` `Dbtr/Id/OrgId/LEI` | Legal Entity Identifier |
| `ivms101.originator.originatorPersons[].naturalPerson.dateAndPlaceOfBirth` | `pain.001` `Dbtr/Id/PrvtId/DtAndPlcOfBirth` | Debtor date/place of birth |
| `ivms101.originator.originatorPersons[].naturalPerson.geographicAddresses[]` | `pacs.008`/`pain.001` `Dbtr/PstlAdr` | Postal address (structured or unstructured lines) |
| `ivms101.originator.accountNumber[]` | `pacs.008`/`pain.001` `DbtrAcct/Id/IBAN` (or `Othr/Id`) | IBAN detected automatically; non-IBAN → `<Othr>` |
| `ivms101.transferredAmount.amount` | `pacs.008` `IntrBkSttlmAmt` / `pain.001` `Amt/InstdAmt` | Transfer amount |
| `ivms101.transferredAmount.assetType` | `@Ccy` attribute (ISO 4217); non-fiat → `XXX` | Fiat mapped directly; crypto assets use `XXX` |
| `ivms101.originatingVASP.lei` | `pacs.008` `GrpHdr/InstgAgt/FinInstnId/LEI` | Originating VASP identified by LEI |
| `ivms101.beneficiaryVASP.lei` | `pacs.008` `GrpHdr/InstdAgt/FinInstnId/LEI` | Beneficiary VASP identified by LEI |
| `ivms101.originator.originatorPersons[].naturalPerson.nationalIdentification` | `Dbtr/Id/PrvtId/Othr` with `SchmeNm/Prtry` | National ID type preserved in proprietary scheme name |
| `ivms101.beneficiary.beneficiaryPersons[].naturalPerson.name` | `Cdtr/Nm` | Beneficiary display name |
| `ivms101.beneficiary.accountNumber[]` | `CdtrAcct/Id/IBAN` (or `Othr/Id`) | Same IBAN/non-IBAN logic as debtor |

### 7.2 Fields Carried in `<SplmtryData>` (KYCAMLEnvelope)

The following OpenKYCAML fields have no ISO 20022 native counterpart and are embedded in the `<SplmtryData><Envlp>` extension using the `OpenKYCAML/KYCAMLEnvelope/1.0` discriminator:

| OpenKYCAML Field | Reason No Native ISO 20022 Equivalent | KYCAMLEnvelope Key |
|---|---|---|
| `kycProfile.customerRiskRating` | ISO 20022 carries no risk ratings | `kycProfile.customerRiskRating` |
| `kycProfile.sanctionsScreening` | Screening results are out of scope for ISO 20022 payment messages | `screeningResults.sanctionsScreening` |
| `kycProfile.pepStatus` | No PEP flag in ISO 20022 | `screeningResults.pepScreening` |
| `kycProfile.adverseMedia` | No adverse media field in ISO 20022 | `screeningResults.adverseMediaScreening` |
| `kycProfile.thirdPartyCDDReliance` | CDD reliance is application-layer data | `kycProfile.thirdPartyCDDReliance` |
| `kycProfile.auditMetadata` | Audit trail not carried in ISO 20022 | `kycProfile.auditMetadata` |
| `gdprSensitivityMetadata` | GDPR sensitivity data outside ISO 20022 scope | `gdprSensitivityMetadata` |
| `verifiableCredential.proof` | VC proofs are not ISO 20022 native | `vcProofs[]` |
| `gdprSensitivityMetadata.consentRecord` | Consent records outside ISO 20022 scope | `consentRecord` |

### 7.3 ISO 20022 Integration Module

For the complete Python and TypeScript converters, XML examples, and pre-validated profiles, see:

- **Full integration module**: [`iso20022-integration/`](../iso20022-integration/)
- **Bidirectional field mapping**: [`iso20022-integration/mapping/openkycaml-to-iso20022-mapping.yaml`](../iso20022-integration/mapping/openkycaml-to-iso20022-mapping.yaml)
- **Gap analysis**: [`iso20022-integration/mapping/field-level-gap-analysis.md`](../iso20022-integration/mapping/field-level-gap-analysis.md)
- **KYCAMLEnvelope JSON Schema**: [`iso20022-integration/supplementary-data/kyc-aml-envelope-schema.json`](../iso20022-integration/supplementary-data/kyc-aml-envelope-schema.json)
- **Profiles**: pacs.008 CBPR+ Travel Rule, pain.001 CDD reliance, camt.053 audit trail

---

## 8. eIDAS 2.0 LPID (Legal Person Identification Data) Mapping

The `legalPerson.lpid` block provides a native mapping to the **Legal Person Identification Data (LPID)** credential defined in the eIDAS 2.0 Architecture and Reference Framework (ARF). LPID is issued by Member State-appointed PID Providers and accepted under AMLR Articles 22 and 26 as high-assurance electronic identification for legal entities.

### 8.1 IVMS 101 → LPID Attribute Mapping

| IVMS 101 Field (Legal Person) | eIDAS 2.0 LPID Attribute | Mandatory / Optional | OpenKYCAML Field |
|---|---|---|---|
| `legalPerson.name.nameIdentifier[0].legalPersonName` (LEGL) | `current_legal_name` | **M** | `legalPerson.lpid.currentLegalName` |
| `legalPerson.nationalIdentification.nationalIdentifier` | `unique_identifier` | **M** | `legalPerson.lpid.uniqueIdentifier` |
| `legalPerson.geographicAddress[]` | `current_address` | O | `legalPerson.lpid.currentAddress` (`Address`) |
| `legalPerson.customerNumber` (VAT prefix) | `vat_registration_number` | O | `legalPerson.lpid.vatRegistrationNumber` |
| `legalPerson.customerNumber` (TAX prefix) | `tax_reference_number` | O | `legalPerson.lpid.taxReferenceNumber` |
| _(EUID — no IVMS 101 equivalent)_ | `european_unique_identifier` | O | `legalPerson.lpid.europeanUniqueIdentifier` |
| `legalPerson.nationalIdentification.nationalIdentifier` (LEIX) / `legalPerson.lei` | `lei` | O | `legalPerson.lpid.lei` |
| `legalPerson.customerNumber` (EORI prefix) | `eori_number` | O | `legalPerson.lpid.eoriNumber` |
| `legalPerson.countryOfRegistration` | Registration country (derived from `unique_identifier`) | O | `legalPerson.countryOfRegistration` |

### 8.2 Representation & Mandates (QEAA)

Under eIDAS 2.0 and AMLR, authorised representatives and beneficial owners of legal entities may present Qualified Electronic Attestations of Attributes (QEAAs) for their powers of representation. The `legalPerson.lpid.mandates[]` array supports this:

| OpenKYCAML Field | Description | AMLR Reference |
|---|---|---|
| `legalPerson.lpid.mandates[].naturalPerson` | Natural person holding the mandate (full `NaturalPerson` block, including PID-mapped name, DOB, address) | Art. 26 — beneficial owner / authorised representative |
| `legalPerson.lpid.mandates[].roleOrPower` | Description of authority (e.g. `"Director"`, `"Authorised Signatory"`, `"Power of Attorney"`) | Art. 26(1) |
| `legalPerson.lpid.mandates[].validFrom` | Effective date of the mandate (ISO 8601) | — |
| `legalPerson.lpid.mandates[].validUntil` | Expiry date of the mandate (ISO 8601); omit if open-ended | — |

### 8.3 Standalone LPID Verifiable Credential

For EUDI Wallet flows where a full IVMS 101 Travel Rule payload is not required, the `verifiableCredential.credentialSubject.lpid` field allows a standalone LPID VC to be issued and verified:

```json
{
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "type": ["VerifiableCredential", "LegalPersonIdentificationCredential"],
  "issuer": "did:example:pidprovider",
  "issuanceDate": "2025-01-15T00:00:00Z",
  "credentialSubject": {
    "id": "did:example:acmecorp",
    "lpid": {
      "currentLegalName": "Acme Corporation S.A.",
      "uniqueIdentifier": "BE-BCE-0123456789",
      "lei": "ABCDEFGHIJKLMNOPQRST",
      "vatRegistrationNumber": "BE0123456789",
      "mandates": [
        {
          "naturalPerson": {
            "name": {
              "nameIdentifier": [
                { "primaryIdentifier": "Smith", "secondaryIdentifier": "Jane", "nameIdentifierType": "LEGL" }
              ]
            }
          },
          "roleOrPower": "Director",
          "validFrom": "2024-01-01"
        }
      ]
    }
  }
}
```

---

## 9. GDPR Sensitivity Metadata — `gdprSensitivityMetadata` (v1.3.0)

The `gdprSensitivityMetadata` block provides a machine-readable sensitivity classification that travels with the OpenKYCAML payload and is enforced by EUDI Wallets, relying parties, and automated processing systems.

### 9.1 Regulatory Mapping

| `gdprSensitivityMetadata` Field | GDPR / AMLR Reference | Description |
|---|---|---|
| `classification: "standard"` | GDPR Art. 6 | Ordinary personal data — standard processing basis |
| `classification: "sensitive_personal"` | GDPR Art. 9 | Special-category data (biometrics, health, racial/ethnic origin) — requires Art. 9(2) safeguards |
| `classification: "criminal_offence"` | GDPR Art. 10 | Data on criminal convictions or offences — requires official authority or equivalent safeguards |
| `classification: "sar_restricted"` | AMLR Art. 73 / FATF Rec. 21 | SAR/STR material — tipping-off prohibition applies |
| `classification: "internal_suspicion"` | AMLR Art. 73 / FATF Rec. 21 | Pre-SAR internal AML suspicion flag — same prohibition applies |
| `classification: "confidential_aml"` | AMLR Art. 55 | AML/CFT investigation data protected from broader disclosure |
| `tippingOffProtected: true` | AMLR Art. 73 | Mandatory for `sar_restricted` and `internal_suspicion`; prohibits disclosure to data subject or unauthorised parties |
| `legalBasis: "GDPR-Art6-1c"` | GDPR Art. 6(1)(c) | Legal obligation (AML/KYC) |
| `legalBasis: "GDPR-Art9-2g"` | GDPR Art. 9(2)(g) | Substantial public interest |
| `legalBasis: "GDPR-Art10"` | GDPR Art. 10 | Criminal-offence data under official authority |
| `legalBasis: "AMLR-Art55"` | AMLR Art. 55 | AML data-sharing obligation |
| `legalBasis: "AMLR-Art73"` | AMLR Art. 73 | Tipping-off prohibition compliance |
| `retentionPeriod` | AMLR Art. 56 | ISO 8601 duration — minimum `"P5Y"` per AMLR |
| `disclosurePolicy.prohibitedRecipients: ["data_subject"]` | AMLR Art. 73 | SAR non-disclosure to subject |
| `disclosurePolicy.allowedRecipients: ["fiu_only"]` | AMLR Art. 73 | Restricted to Financial Intelligence Unit |
| `auditReference` | AMLR Art. 56 / GDPR Art. 5(2) accountability | Opaque reference to DPO record or SAR case ID |

### 9.2 OpenKYCAML Field → GDPR / AMLR Cross-Reference

| OpenKYCAML Field | GDPR Article | AMLR Article |
|---|---|---|
| `gdprSensitivityMetadata.classification` | Art. 5(1)(f), Art. 9, Art. 10 | Art. 55, Art. 73 |
| `gdprSensitivityMetadata.tippingOffProtected` | — | Art. 73 |
| `gdprSensitivityMetadata.legalBasis` | Art. 6, Art. 9(2), Art. 10 | Art. 55 |
| `gdprSensitivityMetadata.retentionPeriod` | Art. 5(1)(e) storage limitation | Art. 56 (5-year minimum) |
| `gdprSensitivityMetadata.consentRecord` | Art. 7 | — |
| `gdprSensitivityMetadata.disclosurePolicy` | Art. 5(1)(b) purpose limitation | Art. 73 |
| `gdprSensitivityMetadata.auditReference` | Art. 5(2) accountability | Art. 56 |
| `kycProfile.consentRecord` | Art. 7 | — |
| `kycProfile.auditMetadata.dataRetentionDate` | Art. 5(1)(e) | Art. 56 |
| `verifiableCredential.selectiveDisclosure` | Art. 5(1)(c) data minimisation | — |

---

*Maintained by the OpenKYCAML Technical Working Group. For corrections or additions, please open an issue or pull request.*
