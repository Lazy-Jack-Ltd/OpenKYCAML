# OpenKYCAML ↔ ISO 20022 Field-Level Gap Analysis

This document analyses the alignment between OpenKYCAML v1.3.0 and ISO 20022, identifying:

1. Fields that map 1:1 cleanly
2. Fields that require transformation
3. Fields that have no counterpart and must be carried in `<SplmtryData>`
4. Fields that are in ISO 20022 but outside the scope of KYC/AML data

---

## 1. Clean 1:1 Mappings

These fields require no format conversion. The data type and semantics are identical or directly compatible.

| OpenKYCAML Path | ISO 20022 Element | Notes |
|---|---|---|
| `messageId` | `GrpHdr/MsgId` | Both are free-text identifiers. UUIDv4 satisfies Max35Text. |
| `messageDateTime` | `GrpHdr/CreDtTm` | Both use ISO 8601 datetime format. |
| `ivms101.originatingVASP.lei` | `InstgAgt/FinInstnId/LEI` | ISO 17442 LEI — identical type. |
| `ivms101.beneficiaryVASP.lei` | `InstdAgt/FinInstnId/LEI` | ISO 17442 LEI — identical type. |
| `ivms101.originator.originatorPersons[0].naturalPerson.geographicAddresses[0].country` | `Dbtr/PstlAdr/Ctry` | ISO 3166-1 alpha-2 — used by both. |
| `ivms101.originator.originatorPersons[0].naturalPerson.geographicAddresses[0].postCode` | `Dbtr/PstlAdr/PstCd` | Free text in both. |
| `ivms101.originator.originatorPersons[0].naturalPerson.geographicAddresses[0].townName` | `Dbtr/PstlAdr/TwnNm` | Free text in both. |
| `ivms101.originator.originatorPersons[0].naturalPerson.geographicAddresses[0].streetName` | `Dbtr/PstlAdr/StrtNm` | Free text in both. |
| `ivms101.originator.originatorPersons[0].naturalPerson.dateAndPlaceOfBirth.dateOfBirth` | `Dbtr/Id/PrvtId/DtAndPlcOfBirth/BirthDt` | ISO 8601 date. |
| `ivms101.originator.originatorPersons[0].naturalPerson.dateAndPlaceOfBirth.countryOfBirth` | `Dbtr/Id/PrvtId/DtAndPlcOfBirth/CtryOfBirth` | ISO 3166-1 alpha-2. |
| `ivms101.originator.originatorPersons[0].legalPerson.nationalIdentification.nationalIdentifier` (LEIX) | `Dbtr/Id/OrgId/LEI` | When `nationalIdentifierType = LEIX`. |
| `ivms101.beneficiary.beneficiaryPersons[0].legalPerson.nationalIdentification.nationalIdentifier` (LEIX) | `Cdtr/Id/OrgId/LEI` | When `nationalIdentifierType = LEIX`. |
| `ivms101.originator.accountNumber[0]` (IBAN pattern) | `DbtrAcct/Id/IBAN` | When value matches IBAN pattern `[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}`. |
| `ivms101.beneficiary.accountNumber[0]` (IBAN pattern) | `CdtrAcct/Id/IBAN` | When value matches IBAN pattern. |

**Coverage: 14 fields map cleanly without transformation.**

---

## 2. Fields Requiring Transformation

These fields have a logical counterpart but require format conversion, code-list mapping, or structural adaptation.

### 2.1 Name Fields

**Problem:** ISO 20022 uses a single `Nm` string (Max140Text) for party names. OpenKYCAML (IVMS 101) uses a structured `nameIdentifier` array with separate `primaryIdentifier` (family name), `secondaryIdentifier` (given name), and `nameIdentifierType` fields.

**OpenKYCAML → ISO 20022:**
```
Nm = secondaryIdentifier + " " + primaryIdentifier
     (e.g. "Hiroshi Tanaka")
```

**ISO 20022 → OpenKYCAML:**
```
Split at last space boundary:
  primaryIdentifier   = last token
  secondaryIdentifier = everything before the last token
  nameIdentifierType  = "LEGL"
```

**Risk:** Name-splitting heuristics can fail for names with multiple family-name components (e.g. "Van Der Berg"). For legal entities, the full `Nm` string maps to `legalPersonName` with type `LEGL`.

---

### 2.2 Date Formats

**Problem:** Both OpenKYCAML and ISO 20022 use ISO 8601, but ISO 20022 distinguishes between `ISODate` (YYYY-MM-DD) and `ISODateTime` (YYYY-MM-DDThh:mm:ssZ). OpenKYCAML uses string fields without strict format enforcement in all cases.

**Transformation:** Strip the time component when mapping `messageDateTime` to date-only ISO 20022 fields (e.g. `IntrBkSttlmDt`). Append `T00:00:00Z` when promoting a date to datetime.

---

### 2.3 National Identifier Type Codes

**Problem:** IVMS 101 uses its own code list for `nationalIdentifierType` (CCPT, TXID, DRLC, ARNU, SOCS, IDCD, LEIX, RAID, FIIN, MISC). ISO 20022 uses `ExternalOrganisationIdentification1Code` and `ExternalPersonIdentification1Code`.

**Mapping Table:**

| IVMS 101 Code | ISO 20022 Scheme Name | Notes |
|---|---|---|
| `CCPT` | `CCPT` | Passport — identical code |
| `TXID` | `TXID` | Tax identification number — identical code |
| `DRLC` | `DRLC` | Driver's licence — identical code |
| `ARNU` | `ARNU` | Alien registration — identical code |
| `SOCS` | `SOCS` | Social security — identical code |
| `IDCD` | `IDCD` | Identity card — identical code |
| `LEIX` | `LEI` | Legal Entity Identifier — maps to dedicated `LEI` element |
| `RAID` | `BIC` or `BICFI` | BIC/SWIFT identifier |
| `FIIN` | `FIIN` | Financial institution identification — identical code |
| `MISC` | `MISC` | Miscellaneous — use proprietary scheme name |

---

### 2.4 Account Numbers: IBAN vs Non-IBAN

**Problem:** OpenKYCAML stores all account numbers as strings in `accountNumber[]`. ISO 20022 has a dedicated `IBAN` element for International Bank Account Numbers and an `Othr` element for everything else.

**Transformation Logic:**
```python
IBAN_PATTERN = re.compile(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$')
if IBAN_PATTERN.match(account_number):
    # → DbtrAcct/Id/IBAN
else:
    # → DbtrAcct/Id/Othr/Id (with SchmeNm describing the account type)
```

**Cryptocurrency addresses** (Bitcoin, Ethereum, etc.) always go into `Othr/Id`. The scheme name (`Prtry`) should be the asset type (e.g. `BTC`, `ETH`). The `transferredAmount.assetType` field informs this classification.

---

### 2.5 Unstructured vs Structured Address

**Problem:** OpenKYCAML supports both structured address fields (`streetName`, `buildingNumber`, `postCode`, `townName`, `country`) and an unstructured `addressLine[]` array. ISO 20022 accepts both in `PostalAddress24`, but most market infrastructures (CBPR+, TARGET2) mandate structured addresses.

**Transformation:**
- If structured fields are populated → use `StrtNm`, `BldgNb`, `PstCd`, `TwnNm`, `Ctry`.
- If only `addressLine[]` is available → use `AdrLine` elements (max 7 lines).
- If both are present → prefer structured (more precise).

---

### 2.6 Transfer Amount: Fiat vs Cryptocurrency

**Problem:** ISO 20022 `InstdAmt` requires an ISO 4217 currency code. Cryptocurrency asset types (BTC, ETH, USDT, etc.) are not valid ISO 4217 codes.

**Transformation:**
- If `assetType` is a valid ISO 4217 code → map to `InstdAmt/@Ccy`.
- If `assetType` is a cryptocurrency ticker → set `InstdAmt/@Ccy = "XXX"` (ISO 4217 undefined currency) and carry the full `transferredAmount` object in the `KYCAMLEnvelope` inside `<SplmtryData>`.

---

## 3. Fields with No ISO 20022 Counterpart — Carried in `<SplmtryData>`

The following OpenKYCAML fields have no semantic equivalent in the ISO 20022 data dictionary and **must** be carried in the `<SplmtryData>` element using the `KYCAMLEnvelope` schema.

### 3.1 Risk Classification
| OpenKYCAML Field | Disposition |
|---|---|
| `kycProfile.customerRiskRating.overallRiskRating` | `SplmtryData` — no ISO 20022 risk-rating element |
| `kycProfile.customerRiskRating.riskScore` | `SplmtryData` |
| `kycProfile.riskRatingDetail.riskFactors` | `SplmtryData` |
| `kycProfile.dueDiligenceType` | `SplmtryData` |
| `kycProfile.customerClassification` | `SplmtryData` |

### 3.2 Sanctions and Screening Results
| OpenKYCAML Field | Disposition |
|---|---|
| `kycProfile.sanctionsScreening` | `SplmtryData → KYCAMLEnvelope.screeningResults` |
| `kycProfile.adverseMedia` | `SplmtryData → KYCAMLEnvelope.screeningResults` |
| `kycProfile.pepStatus` | `SplmtryData → KYCAMLEnvelope.screeningResults` |

### 3.3 Ongoing Monitoring
| OpenKYCAML Field | Disposition |
|---|---|
| `kycProfile.monitoringInfo` | `SplmtryData` |
| `kycProfile.monitoringInfo.alerts` | `SplmtryData` — SAR trigger candidates |

### 3.4 Beneficial Ownership (UBOs)
| OpenKYCAML Field | Disposition |
|---|---|
| `kycProfile.beneficialOwnership[]` | `SplmtryData` — ISO 20022 has no UBO chain structure |

### 3.5 eIDAS 2.0 Verifiable Credentials
| OpenKYCAML Field | Disposition |
|---|---|
| `verifiableCredential.issuer` | `SplmtryData → KYCAMLEnvelope.vcProofs[].issuerDid` |
| `verifiableCredential.credentialSubject.id` | `SplmtryData → KYCAMLEnvelope.vcProofs[].subjectDid` |
| `verifiableCredential.evidence[]` | `SplmtryData → KYCAMLEnvelope.vcProofs[]` |
| `verifiableCredential.proof` | `SplmtryData → KYCAMLEnvelope.vcProofs[].proofValue` |
| `verifiableCredential.selectiveDisclosure` | `SplmtryData` — no ISO 20022 SD-JWT concept |
| `verifiableCredential.credentialStatus` | `SplmtryData` — no ISO 20022 revocation concept |

### 3.6 GDPR and Data Protection
| OpenKYCAML Field | Disposition |
|---|---|
| `gdprSensitivityMetadata.classification` | `SplmtryData` — no ISO 20022 GDPR field |
| `gdprSensitivityMetadata.tippingOffProtected` | `SplmtryData` — critical: intermediaries MUST NOT log |
| `gdprSensitivityMetadata.disclosurePolicy` | `SplmtryData` |
| `gdprSensitivityMetadata.legalBasis` | `SplmtryData` |
| `gdprSensitivityMetadata.retentionPeriod` | `SplmtryData` |
| `kycProfile.consentRecord` | `SplmtryData → KYCAMLEnvelope.consentRecord` |

### 3.7 Audit Trail
| OpenKYCAML Field | Disposition |
|---|---|
| `kycProfile.auditMetadata` | `SplmtryData` |
| `kycProfile.auditMetadata.dataRetentionDate` | `SplmtryData` — retention enforcement is operational |
| `kycProfile.auditMetadata.changeLog[]` | `SplmtryData` |

### 3.8 Third-Party CDD Reliance
| OpenKYCAML Field | Disposition |
|---|---|
| `kycProfile.thirdPartyCDDReliance` | `SplmtryData` — AMLR Art. 48 reliance record |

---

## 4. ISO 20022 Fields Outside KYC/AML Scope

These ISO 20022 fields are operational/financial and have no place in a KYC/AML data model. They should not be mapped to or from OpenKYCAML.

| ISO 20022 Element | Reason Out of Scope |
|---|---|
| `GrpHdr/NbOfTxs` | Batch processing counter — not KYC data |
| `GrpHdr/CtrlSum` | Batch control sum — not KYC data |
| `GrpHdr/SttlmInf/SttlmMtd` | Settlement method code — clearing infrastructure |
| `CdtTrfTxInf/IntrBkSttlmDt` | Value date — payment scheduling |
| `CdtTrfTxInf/ChrgBr` | Charge bearer (who pays fees) — commercial |
| `CdtTrfTxInf/RmtInf/Ustrd` | Remittance information — commercial |
| `CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId` | Clearing system membership — infrastructure |
| `CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId` | Clearing system membership — infrastructure |

---

## 5. Summary

| Category | Field Count |
|---|---|
| Clean 1:1 mappings | 14 |
| Fields requiring transformation | ~12 (name, dates, codes, amounts, addresses) |
| OpenKYCAML fields with no ISO 20022 equivalent → `SplmtryData` | ~30+ |
| ISO 20022 fields outside KYC scope | 8 |

The `<SplmtryData>` mechanism is essential: roughly 60% of the OpenKYCAML data model has no direct ISO 20022 counterpart and must be carried in the `KYCAMLEnvelope` extension. This is by design — ISO 20022 is a payment messaging standard, not a KYC data standard. The `SplmtryData` extension is the ISO-approved, non-breaking mechanism for carrying enriched compliance data alongside payment messages.

---

*Last updated: v1.7.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*
