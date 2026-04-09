# Contact Fields and Financial Identifiers — Mapping and Validation Reference

This document describes the contact and financial identifier fields added in **OpenKYCAML v1.10.0**, their JSON Schema `format` and `pattern` constraints, regulatory rationale, and alignment with IVMS 101, FATF Recommendations, eIDAS 2.0, ISO 13616 (IBAN), and ISO 9362 (BIC/SWIFT).

---

## Table of Contents

1. [Overview — Why These Fields Were Added](#1-overview)
2. [Contact Fields — Email and Phone](#2-contact-fields)
3. [BankingDetails — IBAN, BIC, and Account Data](#3-bankingdetails)
4. [Regulatory Identifier Pattern Additions](#4-regulatory-identifier-patterns)
5. [Document Number Patterns](#5-document-number-patterns)
6. [Miscellaneous Field Tightening](#6-miscellaneous)
7. [Validator Business Warnings](#7-validator-warnings)
8. [Backward Compatibility Notes](#8-backward-compatibility)

---

## 1. Overview

Prior to v1.10.0, the OpenKYCAML schema did not include email address or telephone number fields on `NaturalPerson` or `LegalPerson`, and many regulatory identifier fields (VAT registration number, EORI, TIN value, IBAN, BIC) had only `maxLength` constraints with no machine-enforceable format validation.

This meant that while the schema correctly prevented invalid dates, country codes, and URIs, it could not guarantee consistent validation of high-value contact and financial data across multi-party environments (ERP, CRM, VASP, bank correspondent systems).

**v1.10.0 adds:**
- `emailAddress`, `phoneNumber`, and `mobileNumber` to `NaturalPerson` and `LegalPerson`.
- A new reusable `BankingDetails` $def with IBAN, BIC, currency, and account type — wired as `bankingDetails[]` on both person types.
- Anchored regex patterns on EU VAT, EORI, EUID, TIN, IBAN, BIC, and document number fields.
- ISO 4217 patterns on currency and asset type fields.
- Structural patterns on address postal codes and IVMS 101 account numbers.

All additions are strictly backward-compatible (no existing required fields changed; no existing patterns modified).

---

## 2. Contact Fields

### 2.1 `emailAddress`

| Property | Value |
|---|---|
| **$defs** | `NaturalPerson`, `LegalPerson` |
| **type** | `string` |
| **format** | `"email"` (JSON Schema format keyword; RFC 5321 / RFC 5322) |
| **maxLength** | 254 (RFC 5321 maximum total path length) |
| **Optional** | Yes |

**Regulatory basis:**
- FATF Recommendation 16 (wire transfers / Travel Rule): counterparty contact data requirements.
- AMLR 2024 Art. 22: CDD measures include verified contact information for the customer relationship.
- eIDAS 2.0 / EUDI Wallet onboarding: email used as notification channel for wallet attestation delivery.

**B2B data exchange note:** `format: "email"` is enforced by JSON Schema validators that implement the `format` vocabulary (e.g. ajv with `ajv-formats`, Python `jsonschema` with `format_checker`). This guarantees that any party consuming the schema rejects malformed email addresses at parse time, eliminating reconciliation errors when exchanging KYC dossiers with suppliers or correspondent banks.

### 2.2 `phoneNumber`

| Property | Value |
|---|---|
| **$defs** | `NaturalPerson`, `LegalPerson` |
| **type** | `string` |
| **pattern** | `^\+[1-9]\d{1,14}$` (ITU-T E.164 international format) |
| **maxLength** | 16 |
| **Optional** | Yes |

**Pattern explanation:** E.164 requires a `+` prefix, followed by a country calling code (1–3 digits starting with 1–9), followed by a subscriber number, with the total number of digits not exceeding 15 (hence the pattern allows 1 to 14 digits after the country code digit). Examples: `+447911123456` (UK), `+14155552671` (US), `+4930123456` (DE).

### 2.3 `mobileNumber`

| Property | Value |
|---|---|
| **$defs** | `NaturalPerson`, `LegalPerson` |
| **type** | `string` |
| **pattern** | `^\+[1-9]\d{1,14}$` (ITU-T E.164) |
| **maxLength** | 16 |
| **Optional** | Yes |

Separate from `phoneNumber` to support workflows that distinguish voice lines from mobile numbers (mTAN/OTP delivery in AMLR Art. 22(5) remote CDD, EUDI Wallet push notifications, SMS verification).

---

## 3. BankingDetails

The `BankingDetails` $def is a new reusable object capturing validated banking account data. It is wired as `bankingDetails[]` on both `NaturalPerson` and `LegalPerson`.

### 3.1 Field Reference

| Field | type | Format / Pattern | maxLength | Notes |
|---|---|---|---|---|
| `iban` | string | `^[A-Z]{2}[0-9]{2}[A-Z0-9]{4,30}$` | 34 | ISO 13616:2020 structural validation |
| `bic` | string | `^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$` | 11 | ISO 9362:2022; 8-char or 11-char BIC |
| `bankName` | string | — | 140 | Legal name of financial institution |
| `accountCurrency` | string | `^[A-Z]{3}$` | 3 | ISO 4217 currency code |
| `accountType` | string (enum) | CURRENT \| SAVINGS \| CORRESPONDENT \| CRYPTO_FIAT_GATEWAY \| OTHER | — | Account classification |
| `bankingCountry` | string | `^[A-Z]{2}$` | — | ISO 3166-1 alpha-2 |

### 3.2 IBAN Pattern Rationale

Pattern: `^[A-Z]{2}[0-9]{2}[A-Z0-9]{4,30}$`

ISO 13616:2020 defines the IBAN structure as:
- 2-character ISO 3166-1 alpha-2 country code
- 2-digit check digits (modulo-97 Luhn-style checksum — computed at runtime)
- Basic Bank Account Number (BBAN): 4–30 alphanumeric characters (country-specific format)

Maximum total length: 34 characters (as per ISO 13616 Annex A, maximum BBAN length of 30 chars across all countries). The pattern enforces the structural envelope; full modulo-97 checksum verification is left to runtime validators to avoid regex complexity.

Example valid IBANs: `GB29NWBK60161331926819`, `DE89370400440532013000`, `FR7630006000011234567890189`.

### 3.3 BIC Pattern Rationale

Pattern: `^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$`

ISO 9362:2022 defines the BIC structure as:
- 4-character institution code (alphabetic)
- 2-character ISO 3166-1 alpha-2 country code
- 2-character location code (alphanumeric)
- Optional 3-character branch code (alphanumeric; omitted = primary office / `XXX`)

The pattern accepts both the 8-character abbreviated form and the full 11-character form.

Example valid BICs: `NWBKGB2L` (NatWest, 8-char), `NWBKGB2LXXX` (NatWest primary, 11-char), `DEUTDEDB` (Deutsche Bank).

### 3.4 Regulatory Alignment

| Standard | Alignment |
|---|---|
| FATF Rec. 16 — Wire transfers / Travel Rule | Correspondent banking account identification requires validated IBAN/BIC for cross-border transfers |
| AMLR 2024 Art. 22 | Financial relationship verification — source of funds and account ownership |
| ISO 20022 (pain.001, camt.053) | IBAN and BIC are mandatory for SEPA credit transfers and account statement reconciliation |
| EU Funds Transfer Regulation 2023/1113 Art. 14 | Account number of originator required in Travel Rule payload |
| SWIFT / SEPA | BIC-based correspondent bank identification |

---

## 4. Regulatory Identifier Patterns

### 4.1 VAT Registration Number — `LegalPersonIdentificationData.vatRegistrationNumber`

Pattern: `^[A-Z]{2}[A-Z0-9]{2,12}$`

Structural form: 2-char ISO 3166-1 country prefix + 2–12 alphanumeric characters. This covers all EU Member State VAT formats (e.g. `GB123456789`, `DE123456789`, `FR12345678901`, `ATU12345678`). Country-specific checksum validation is a runtime concern.

**Standard:** EU VAT Directive 2006/112/EC; eIDAS 2.0 LPID optional attribute.

### 4.2 EORI Number — `LegalPersonIdentificationData.eoriNumber`

Pattern: `^[A-Z]{2}[A-Z0-9]{1,15}$`

Economic Operators Registration and Identification (EORI): 2-char country prefix + 1–15 alphanumeric characters. Examples: `GB123456789000` (UK), `DE1234567890` (EU).

**Standard:** EU Regulation 952/2013 (Union Customs Code); eIDAS 2.0 LPID optional attribute.

### 4.3 European Unique Identifier (EUID) — `LegalPersonIdentificationData.europeanUniqueIdentifier`

Pattern: `^[A-Z]{2}-[A-Za-z0-9.\-]{6,40}$`

Format: `CC-RegistrationAuthority-RegistrationNumber`. The country code is always 2 uppercase letters; the registration authority and registration number components can include alphanumerics, dots, and hyphens. Example: `GB-COH-12345678` (UK Companies House).

**Standard:** Directive (EU) 2017/1132 Art. 16 — Cross-border company register identifiers; eIDAS 2.0 EUID.

### 4.4 TIN Value — `TinIdentifier.tinValue`

Pattern: `^[A-Z0-9\-\/]{5,20}$`

Intentionally loose to cover the wide variation in global TIN formats (US EIN `12-3456789`, UK UTR `1234567890`, DE TIN `86095742719`, AU TFN `123456789`). Enforces uppercase and prevents control characters / injection strings. Jurisdiction-specific validation is a runtime concern.

**Standard:** OECD CRS §IV.C; FATCA; AMLR Art. 22.

### 4.5 Indirect Tax Registration Number — `IndirectTaxRegistration.registrationNumber`

Pattern: `^[A-Z0-9\-\/]{2,30}$`

Generic: 2–30 uppercase alphanumeric with hyphens and slashes. Covers EU VAT (`DE123456789`), India GSTIN (`27AAPFU0939F1ZV`), Australia ABN (`12345678901`), Canada HST/PST.

### 4.6 FATCA Withholding Agent Reference — `FatcaStatus.withholdingAgentReference`

Pattern: `^[A-Z0-9\-]{1,30}$`

IRS-assigned or internal reference for the withholding agent responsible for FATCA reporting obligations.

---

## 5. Document Number Patterns

Document numbers are intentionally validated with generic patterns because passport and national ID formats vary widely by country and document type. The patterns enforce:
- Uppercase alphanumeric characters (standard document printing convention)
- Hyphens, slashes, and spaces (common separators in document numbers)
- No control characters, injection strings, or non-printing characters

| Field | $def | Pattern |
|---|---|---|
| `documentNumber` | `NaturalPersonDocument` | `^[A-Z0-9\-\/ ]{1,50}$` |
| `documentNumber` | `LegalEntityDocument` | `^[A-Z0-9\-\/ ]{1,100}$` |
| `registrationNumber` | `LegalEntityDocument` | `^[A-Z0-9\-\/ ]{1,100}$` |

---

## 6. Miscellaneous Field Tightening

### 6.1 Account Numbers — `Originator.accountNumber`, `Beneficiary.accountNumber`

Pattern: `^[A-Za-z0-9\-\/.]{1,100}$`

Mixed case to support:
- Ethereum addresses (`0x` prefix with mixed-case hex)
- Bitcoin bech32 addresses (lowercase `bc1q...`)
- IBANs (uppercase)
- Proprietary account identifiers

**Standard:** IVMS 101 §4 account number sanitisation.

### 6.2 Registration Authority — `NationalIdentification.registrationAuthority`

Pattern: `^RA[0-9]{6}$`

Aligns with `RegistrationAuthorityDetail.ralCode` which already carried this pattern since v1.5.0. The GLEIF Registration Authority List (RAL) code format is `RA` followed by 6 digits (e.g. `RA000585` = UK Companies House, `RA000394` = French INPI). Required when `nationalIdentifierType` is `LEIX`.

### 6.3 Currency Codes — `TransactionMonitoring` threshold fields

Pattern: `^[A-Z]{3}$`

Applied to `jurisdictionThreshold.currency` and `reportingThreshold.currency`. Enforces ISO 4217 three-letter currency code format.

### 6.4 Asset Type — `IVMS101Payload.transferredAmount.assetType`

Pattern: `^[A-Z]{3,10}$`

Covers ISO 4217 fiat currency codes (3 chars, e.g. `EUR`, `USD`) and crypto-asset tickers (3–10 uppercase chars, e.g. `BTC`, `ETH`, `USDT`, `MATIC`). Does not restrict to a fixed enum to accommodate new assets.

### 6.5 Postal Code — `Address.postCode`

Pattern: `^[A-Z0-9\- ]{2,10}$`

Generic structural validation: 2–10 uppercase alphanumeric characters with hyphens and spaces. Covers UK (`SW1A 2AA`), US (`10001`), DE (`10115`), NL (`1234 AB`), CA (`K1A 0A6`). Full country-specific postcode validation is a runtime concern.

**Standard:** IVMS 101 §3.5 structured address.

---

## 7. Validator Business Warnings

The Python and JavaScript validators emit advisory warnings (not schema errors) for the following v1.10.0 additions:

### 7.1 Missing contact fields for EDD customers

```
kycProfile.dueDiligenceType is 'ENHANCED' but naturalPerson[i] has no emailAddress or phoneNumber —
FATF Rec. 16 / AMLR Art. 22 require verified contact data for Enhanced Due Diligence customers.
```

Triggered when `kycProfile.dueDiligenceType == "ENHANCED"` and a natural person in `ivms101.originator.originatorPersons` has neither `emailAddress` nor `phoneNumber`.

### 7.2 IBAN without BIC

```
bankingDetails[i].iban is present but bic is absent — BIC is required for SEPA credit transfers and
correspondent banking identification (ISO 9362 / FATF Rec. 16).
```

Triggered for each `bankingDetails` entry on `NaturalPerson` or `LegalPerson` where `iban` is set but `bic` is absent.

---

## 8. Backward Compatibility Notes

All additions in v1.10.0 are **strictly additive**:

- No existing required fields were changed.
- No existing `format`, `pattern`, or `enum` constraints were modified.
- Payloads valid under v1.9.x remain valid under v1.10.0.
- The `BankingDetails` $def and all new contact fields are optional.
- The new `pattern` additions on existing fields (`registrationAuthority`, `accountNumber`, `currency`, `assetType`, `postCode`) are applied to fields that were previously unconstrained (only `maxLength`). Any payload that was previously valid will continue to be valid if the values already conform to the expected formats. Values that would fail the new patterns were already non-conforming with the underlying standards.

For consuming systems that need to remain compatible with both v1.9.x and v1.10.0 schemas, no changes are required unless the consuming system is generating or accepting values in non-standard formats for the newly patterned fields.

---

*Added in OpenKYCAML v1.10.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*
