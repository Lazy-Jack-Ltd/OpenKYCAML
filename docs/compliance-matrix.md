# OpenKYCAML Compliance Matrix

This matrix documents the alignment of the OpenKYCAML v1.0.0 schema with major regulatory and technical standards.

**Legend:**
- ✅ Full alignment — the standard is directly addressed.
- 🟡 Partial alignment — the standard is partially addressed; notes explain scope.
- ⬜ Not in scope — explicitly out of scope or addressed by the transport layer.

---

## 1. FATF Recommendations

| FATF Recommendation | Coverage in OpenKYCAML | Relevant Schema Fields |
|---|---|---|
| **Rec 1** — Risk-based approach | ✅ | `kycProfile.customerRiskRating`, `kycProfile.dueDiligenceType` |
| **Rec 6** — Targeted financial sanctions | ✅ | `kycProfile.sanctionsScreening` |
| **Rec 10** — Customer due diligence | ✅ | `ivms101.originator`, `kycProfile.customerClassification`, `kycProfile.dueDiligenceType`, `kycProfile.beneficialOwnership` |
| **Rec 11** — Record keeping | ✅ | `kycProfile.auditMetadata` |
| **Rec 12** — Politically Exposed Persons | ✅ | `kycProfile.pepStatus`, `kycProfile.sourceOfFundsWealth` |
| **Rec 15** — New technologies (VASPs) | ✅ | Full IVMS 101 support; `kycProfile.customerClassification` = `VASP` |
| **Rec 16** — Wire transfers / Travel Rule | ✅ | `ivms101` block (IVMS 101 v1.0 superset), `ivms101.transferredAmount`, originating/beneficiary VASP fields |
| **Rec 20** — Reporting of suspicious transactions | 🟡 | `kycProfile.monitoringInfo.alerts` (SAR trigger fields) — SAR submission itself is out of scope |
| **Rec 24** — Beneficial ownership of legal persons | ✅ | `kycProfile.beneficialOwnership[]` |
| **Rec 25** — Beneficial ownership of legal arrangements | 🟡 | Covered by `kycProfile.beneficialOwnership` for trusts; specific trust-deed fields planned for v1.1 |

---

## 2. EU Anti-Money Laundering Regulation (AMLR 2024)

> _Regulation (EU) 2024/1624 — applicable from 1 July 2027_

| AMLR Article | Topic | Coverage | Relevant Schema Fields |
|---|---|---|---|
| **Art. 15** — Risk-based approach | RBA framework | ✅ | `kycProfile.customerRiskRating` |
| **Art. 20** — Risk assessment | Risk factors | ✅ | `kycProfile.customerRiskRating.riskFactors` |
| **Art. 21** — Ongoing monitoring | Transaction and relationship monitoring | ✅ | `kycProfile.monitoringInfo` |
| **Art. 22(1)** — CDD measures | SDD / CDD / EDD | ✅ | `kycProfile.dueDiligenceType` |
| **Art. 22(2)** — CDD data required | Name, DoB, address, ID | ✅ | `ivms101.originator.originatorPersons[].naturalPerson.*` |
| **Art. 22(5)** — Remote / third-party CDD | Reliable electronic means; third-party reliance | ✅ | `verifiableCredential` wrapper; `kycProfile.onboardingChannel` |
| **Art. 24** — Targeted financial sanctions | Sanctions screening | ✅ | `kycProfile.sanctionsScreening` |
| **Art. 26** — Beneficial owners | UBOs of legal entities | ✅ | `kycProfile.beneficialOwnership[]` |
| **Art. 28–31** — PEP provisions | PEP identification and EDD | ✅ | `kycProfile.pepStatus` |
| **Art. 29** — EDD measures | Enhanced due diligence | ✅ | `kycProfile.dueDiligenceType` = `EDD`, `kycProfile.sourceOfFundsWealth` |
| **Art. 56** — Record keeping | 5-year minimum retention | ✅ | `kycProfile.auditMetadata.dataRetentionDate`, `changeLog` |
| **Art. 83** — Transfer of funds (Travel Rule) | VASP Travel Rule obligations | ✅ | `ivms101` block |

---

## 3. EU Markets in Crypto Assets (MiCA) Regulation

| MiCA Article / Provision | Coverage | Notes |
|---|---|---|
| **Art. 83** — Transfer of crypto-assets | ✅ | `ivms101` block supports full VASP Travel Rule payload per IVMS 101 |
| **Art. 68** — VASP authorisation | ⬜ | Out of scope — operational, not data model |
| **Art. 82** — Customer onboarding | 🟡 | `kycProfile.onboardingChannel`, `kycProfile.kycCompletionDate` |

---

## 4. IVMS 101 (InterVASP Messaging Standard v1.0)

| IVMS 101 Section | Coverage | Notes |
|---|---|---|
| §3.2 — NaturalPersonName | ✅ | `NaturalPersonNameIdentifier` — all name identifier types supported (ALIA, BIRT, MAID, LEGL, MISC) |
| §3.3 — DateAndPlaceOfBirth | ✅ | `DateAndPlaceOfBirth` |
| §3.4 — NaturalPersonNationalIdentification | ✅ | `NationalIdentification` — all types (ARNU, CCPT, RAID, DRLC, FIIN, TXID, SOCS, IDCD, LEIX, MISC) |
| §3.5 — Address | ✅ | `Address` — all 14 structured fields + unstructured `addressLine[]` |
| §3.6 — CountryOfResidence | ✅ | `NaturalPerson.countryOfResidence` |
| §3.7 — CustomerIdentification | ✅ | `customerIdentification` on both `NaturalPerson` and `LegalPerson` |
| §3.8 — LegalPersonName | ✅ | `LegalPersonNameIdentifier` — LEGL, SHRT, TRAD |
| §3.9 — LegalPersonNationalIdentification | ✅ | `NationalIdentification` with LEIX type and `registrationAuthority` |
| §3.10 — CountryOfRegistration | ✅ | `LegalPerson.countryOfRegistration` |
| §4 — TransferredAmount | ✅ | `transferredAmount.amount`, `transferredAmount.assetType` |
| §5 — OriginatingVASP / BeneficiaryVASP | ✅ | `originatingVASP`, `beneficiaryVASP` |

**Backward compatibility:** A validator accepting IVMS 101 JSON payloads will also accept the `ivms101` block of any OpenKYCAML payload.

---

## 5. eIDAS 2.0 / EU Digital Identity Architecture and Reference Framework (ARF)

| ARF Component | Coverage | Relevant Schema Fields |
|---|---|---|
| W3C VC Data Model v2 | ✅ | `verifiableCredential` block |
| VC Issuer (PID Issuer) | ✅ | `verifiableCredential.issuer` (DID URL) |
| VC Subject (User DID) | ✅ | `verifiableCredential.credentialSubject.id` |
| Credential Status / Revocation | ✅ | `verifiableCredential.credentialStatus` (StatusList2021) |
| Proof suites (Ed25519, JWS, DataIntegrity) | ✅ | `verifiableCredential.proof.type` |
| PID (Person Identification Data) — natural persons | ✅ | `NaturalPerson.*` fields with eIDAS attribute annotations (`family_name`, `given_name`, `birth_date`, `resident_address`, etc.) |
| **LPID (Legal Person Identification Data)** — legal entities | ✅ | `legalPerson.lpid` — `LegalPersonIdentificationData` definition; covers mandatory (`currentLegalName`, `uniqueIdentifier`) and optional attributes (`lei`, `vatRegistrationNumber`, `taxReferenceNumber`, `eoriNumber`, `europeanUniqueIdentifier`, `currentAddress`) |
| **QEAA / Representation & Mandates** | ✅ | `legalPerson.lpid.mandates[]` — natural person representatives with `roleOrPower`, `validFrom`/`validUntil`; supports AMLR authorised representative and UBO verification |
| LPID in VC credentialSubject | ✅ | `verifiableCredential.credentialSubject.lpid` — standalone LPID VC for EUDI Wallet issuance flows |
| OpenID4VCI (issuance) | ⬜ | Transport protocol — out of schema scope |
| OpenID4VP (presentation) | ⬜ | Transport protocol — out of schema scope |
| SD-JWT selective disclosure | 🟡 | Schema is compatible; SD-JWT framing not part of schema definition |

---

## 6. ISO 20022

| ISO 20022 Element | Coverage | Notes |
|---|---|---|
| `pain.001` — Credit Transfer | 🟡 | Key fields (name, LEI, IBAN, amount, currency) are present; full ISO 20022 XML not generated |
| `pacs.008` — FI Credit Transfer | 🟡 | Same as above |
| LEI (`LEIX` type) | ✅ | `nationalIdentification.nationalIdentifierType` = `"LEIX"`, `registrationAuthority` per GLEIF |
| BIC/SWIFT (RAID type) | ✅ | `nationalIdentification.nationalIdentifierType` = `"RAID"` |
| IBAN | 🟡 | Supported as an `accountNumber` string value; format validation planned for v1.1 |

---

## 7. GLEIF / Legal Entity Identifier (LEI)

| LEI Requirement | Coverage | Notes |
|---|---|---|
| LEI code (20-char ISO 17442) | ✅ | `nationalIdentification.nationalIdentifier` with type `LEIX` |
| Registration Authority code | ✅ | `nationalIdentification.registrationAuthority` |
| Level 2 data (UBOs) | ✅ | `kycProfile.beneficialOwnership[]` — maps to GLEIF Level 2 / Relationship Records |

---

## 8. General Data Protection Regulation (GDPR)

| GDPR Requirement | Coverage | Notes |
|---|---|---|
| Lawful basis for processing (Art. 6) | 🟡 | `kycProfile.consentRecord.consentPurpose` for consent-based processing; other legal bases (Art. 6(1)(c) legal obligation) implicit |
| Consent record (Art. 7) | ✅ | `kycProfile.consentRecord` |
| Right to erasure (Art. 17) | 🟡 | `kycProfile.auditMetadata.dataRetentionDate` supports scheduled deletion; erasure workflow is operational |
| Data minimisation (Art. 5(1)(c)) | ✅ | All fields optional except those required for compliance; schema supports minimal payloads |
| Special categories (Art. 9) | ⬜ | Biometric and health data not collected in schema |

---

*Last updated: v1.0.0 — June 2024. Maintained by the OpenKYCAML Technical Working Group.*
