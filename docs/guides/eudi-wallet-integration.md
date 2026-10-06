# EUDI Wallet Integration Guide

This document specifies how OpenKYCAML credentials are stored in and retrieved from
an EU Digital Identity Wallet (EUDIW) as defined by the eIDAS 2.0 Architecture and
Reference Framework (ARF) v1.4+ and the OpenID for Verifiable Credentials
specifications.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Credential Format Selection: VC-JWT vs JSON-LD](#2-credential-format-selection-vc-jwt-vs-json-ld)
3. [EUDIW Storage Profile](#3-eudiw-storage-profile)
4. [Wallet API Mapping](#4-wallet-api-mapping)
5. [Issuance Flow (OpenID4VCI)](#5-issuance-flow-openid4vci)
6. [Presentation Flow (OpenID4VP)](#6-presentation-flow-openid4vp)
   - [6.1 Constructing the Authorization Request (Travel Rule Minimum)](#61-constructing-the-authorization-request-travel-rule-minimum)
7. [Credential Metadata](#7-credential-metadata)
8. [Selective Disclosure (SD-JWT VC)](#8-selective-disclosure-sd-jwt-vc)
9. [Revocation and Status](#9-revocation-and-status)
10. [Trusted Issuer Validation](#10-trusted-issuer-validation)
11. [Examples](#11-examples)
12. [Handling Restricted Data in EUDIW Presentations](#12-handling-restricted-data-in-eudiw-presentations)

---

## 1. Overview

An OpenKYCAML credential is a W3C Verifiable Credential (VC) that embeds:
- an **IVMS 101** Travel Rule payload (Travel Rule use-cases), and/or
- a **KYC Profile** (CDD reliance / identity portability use-cases).

When issued to an EUDI Wallet the credential is stored as a
**SD-JWT VC** (recommended) or as a **VC-JWT** (interoperability fallback).
JSON-LD presentation is reserved for verifiers that explicitly require Linked-Data
Proofs (e.g. EBSI conformant services).

```
┌─────────────────────────────────────────────────────────────────┐
│  OpenKYCAML Credential                                          │
│  ─────────────────────                                          │
│  Envelope     verifiableCredential { … }                        │
│  Subject      credentialSubject.ivms101  +  .kycProfile         │
│  Proof        Ed25519Signature2020  |  ES256  |  ES256K         │
│  SD-JWT       selectiveDisclosure { _sd_alg, decodedDisclosures }│
└─────────────────────────────────────────────────────────────────┘
         │  issued via OpenID4VCI          │  presented via OpenID4VP
         ▼                                 ▼
   EUDI Wallet storage               Relying Party (VASP / Bank)
```

---

## 2. Credential Format Selection: VC-JWT vs JSON-LD

| Criterion | VC-JWT (`jwt_vc_json`) | SD-JWT VC (`dc+sd-jwt`) | JSON-LD (`ldp_vc`) |
|-----------|------------------------|-------------------------|--------------------|
| **EUDIW ARF mandate** | Conformant (fallback) | **Primary format** (ARF §6.3.2) | Allowed where EBSI conformance required |
| **Selective disclosure** | ❌ Not supported | ✅ Native (`_sd` arrays) | ⚠ Partial (ZKP only with BBS+) |
| **EUDI Wallet storage** | ✅ Supported | ✅ Preferred | ✅ Supported |
| **FATF Travel Rule interop** | ✅ Widely supported | ✅ Supported | ⚠ Limited ecosystem support |
| **Signature algorithm** | ES256 / ES256K / EdDSA | ES256 / ES256K / EdDSA | Ed25519Signature2020 / JsonWebSignature2020 |
| **Holder binding** | `sub` claim (DID) | `cnf.jwk` or `sub` | `credentialSubject.id` (DID) |
| **Compact serialisation** | Yes — Base64url JWT | Yes — JWT `~` disclosures | No — JSON object |

### Recommendation

- **New implementations**: use `dc+sd-jwt` (SD-JWT VC) for all EUDI Wallet flows.
  This format is required by the eIDAS 2.0 ARF for PID and QEAA credentials and
  provides native GDPR data-minimisation through selective disclosure.
- **Interoperability with legacy verifiers**: fall back to `jwt_vc_json` (VC-JWT).
- **EBSI / Linked-Data Proof verifiers**: use `ldp_vc` (JSON-LD) only when required
  by the specific verifier's conformance profile.

---

## 3. EUDIW Storage Profile

### 3.1 Credential Type Identifier

When stored in an EUDI Wallet the OpenKYCAML credential uses the following
`vct` (Verifiable Credential Type) URI:

```
https://openkycaml.org/credentials/v1/OpenKYCAMLCredential
```

### 3.2 SD-JWT VC Storage Metadata

| Metadata field | Value |
|---|---|
| `format` | `dc+sd-jwt` |
| `vct` | `https://openkycaml.org/credentials/v1/OpenKYCAMLCredential` |
| `cryptographic_binding_methods_supported` | `["did:ebsi", "did:web", "jwk"]` |
| `credential_signing_alg_values_supported` | `["ES256", "ES256K", "EdDSA"]` |
| `display[].name` | `"OpenKYCAML KYC Attestation"` |
| `display[].locale` | `"en-US"` |
| `display[].logo.uri` | `"https://openkycaml.org/assets/logo.png"` |

### 3.3 VC-JWT Storage Metadata (fallback)

| Metadata field | Value |
|---|---|
| `format` | `jwt_vc_json` |
| `types` | `["VerifiableCredential", "OpenKYCAMLCredential", "KYCAttestation"]` |
| `cryptographic_binding_methods_supported` | `["did:ebsi", "did:web", "did:key"]` |
| `credential_signing_alg_values_supported` | `["ES256", "ES256K", "EdDSA"]` |

### 3.4 JSON-LD Storage Metadata

| Metadata field | Value |
|---|---|
| `format` | `ldp_vc` |
| `types` | `["VerifiableCredential", "OpenKYCAMLCredential", "KYCAttestation"]` |
| `cryptographic_binding_methods_supported` | `["did:ebsi", "did:key"]` |
| `proof_types_supported` | `["Ed25519Signature2020", "JsonWebSignature2020"]` |
| `@context` | `["https://www.w3.org/ns/credentials/v2", "https://openkycaml.org/contexts/v1", "https://europa.eu/2018/credentials/eudi/v1"]` |

### 3.5 Claim Path Mapping (SD-JWT VC)

The following table maps OpenKYCAML JSON paths to SD-JWT VC claim names as they
appear in the wallet's credential display and in OpenID4VP presentation requests.

| OpenKYCAML JSON path | SD-JWT VC claim name | Disclosable | Notes |
|---|---|---|---|
| `credentialSubject.ivms101.originator.originatorPersons[0].naturalPerson.name.nameIdentifier[0].primaryIdentifier` | `family_name` | Recommended disclose | FATF Rec 16 minimum |
| `credentialSubject.ivms101.originator.originatorPersons[0].naturalPerson.name.nameIdentifier[0].secondaryIdentifier` | `given_name` | Recommended disclose | FATF Rec 16 minimum |
| `credentialSubject.ivms101.originator.originatorPersons[0].naturalPerson.dateAndPlaceOfBirth.dateOfBirth` | `birthdate` | Optional | GDPR minimisation |
| `credentialSubject.ivms101.originator.originatorPersons[0].naturalPerson.geographicAddress[0]` | `address` | Optional | GDPR minimisation |
| `credentialSubject.ivms101.originator.originatorPersons[0].naturalPerson.nationalIdentification.nationalIdentifier` | `personal_administrative_number` | Optional | High-sensitivity |
| `credentialSubject.kycProfile.customerRiskRating` | `customer_risk_rating` | Optional | Internal classification |
| `credentialSubject.kycProfile.pepStatus.isPEP` | `is_pep` | Optional | Regulatory purpose |
| `credentialSubject.kycProfile.sanctionsScreening.screeningStatus` | `sanctions_status` | Optional | Regulatory purpose |
| `credentialSubject.kycProfile.onboardingChannel` | `onboarding_channel` | Optional | Audit trail |

---

## 4. Wallet API Mapping

### 4.1 OpenID for Verifiable Credential Issuance (OpenID4VCI)

The issuer (VASP or KYC Utility) advertises OpenKYCAML credential support via its
**Credential Issuer Metadata** endpoint:

```
GET /.well-known/openid-credential-issuer
```

Relevant metadata fields:

```json
{
  "credential_issuer": "https://vasp.example.com",
  "credential_endpoint": "https://vasp.example.com/credentials",
  "credentials_supported": {
    "OpenKYCAMLCredential": {
      "format": "dc+sd-jwt",
      "vct": "https://openkycaml.org/credentials/v1/OpenKYCAMLCredential",
      "cryptographic_binding_methods_supported": ["did:ebsi", "did:web", "jwk"],
      "credential_signing_alg_values_supported": ["ES256", "EdDSA"],
      "claims": {
        "family_name":    { "mandatory": true,  "display": [{"name": "Family name",  "locale": "en-US"}] },
        "given_name":     { "mandatory": true,  "display": [{"name": "Given name",   "locale": "en-US"}] },
        "birthdate":      { "mandatory": false, "display": [{"name": "Date of birth","locale": "en-US"}] },
        "address":        { "mandatory": false, "display": [{"name": "Address",       "locale": "en-US"}] },
        "customer_risk_rating": { "mandatory": false, "display": [{"name": "Risk Rating", "locale": "en-US"}] }
      }
    }
  }
}
```

**Authorization flow** (Pre-Authorised Code — recommended for EUDI Wallet):

```
Issuer                          Wallet                   User
  |── credential_offer_uri ────▶|                          |
  |                             |── User approves ────────▶|
  |                             |◀──────────────────────── |
  |◀── token_request (pre-auth) |                          |
  |─── access_token ───────────▶|                          |
  |◀── credential_request      |                          |
  |─── credential (SD-JWT VC) ─▶|                          |
  |                             |── stored in wallet       |
```

### 4.2 OpenID for Verifiable Presentations (OpenID4VP)

The relying party (counterparty VASP, bank) sends a **Presentation Definition**
(DIF PE v2) requesting specific OpenKYCAML claims:

```json
{
  "id": "openkycaml-travel-rule-request",
  "input_descriptors": [
    {
      "id": "kyc_attestation",
      "format": { "dc+sd-jwt": { "alg": ["ES256", "EdDSA"] } },
      "constraints": {
        "fields": [
          {
            "path": ["$.vct"],
            "filter": { "type": "string", "const": "https://openkycaml.org/credentials/v1/OpenKYCAMLCredential" }
          },
          { "path": ["$.family_name"] },
          { "path": ["$.given_name"] },
          { "path": ["$.customer_risk_rating"], "optional": true }
        ]
      }
    }
  ]
}
```

The wallet user selects which disclosures to release (data-minimisation). The
compact SD-JWT VP token returned to the relying party includes only the chosen
`~disclosure` objects appended after the issuer-signed JWT.

### 4.3 DID Resolution

OpenKYCAML issuers and subjects use the following DID methods:

| DID method | Use-case |
|---|---|
| `did:web` | VASP / bank issuers (simple, corporate domain) |
| `did:ebsi` | EUDI Wallet subjects (EU member-state issued) |
| `did:key` | Development / testing only |
| `did:jwk` | Ephemeral holder keys in wallet |

---

## 5. Issuance Flow (OpenID4VCI)

Complete step-by-step for issuing an OpenKYCAML SD-JWT VC to a user's EUDI Wallet
after completing KYC onboarding:

1. **KYC completion**: the obliged entity performs CDD / eIDAS PID verification.
2. **Build OpenKYCAML payload**: construct the full JSON payload per the
   [schema](../../schema/kyc-aml-hybrid-extended.json) with `verifiableCredential`
   block and `selectiveDisclosure` descriptor.
3. **Sign JWT**: issue a signed SD-JWT:
   - Header: `{"alg": "ES256", "typ": "dc+sd-jwt"}`
   - Payload: JWT claims derived from the `verifiableCredential` block plus
     `_sd` digest arrays for disclosable claims.
   - Append `~<base64url-disclosure>` segments for each selectively-disclosable claim.
4. **Deliver via OpenID4VCI**: send `credential_offer` to the wallet via deep-link
   (`openid-credential-offer://`) or QR code.
5. **Wallet storage**: the wallet stores the SD-JWT VC under the `vct` URI and
   displays it using the `display` metadata.

---

## 6. Presentation Flow (OpenID4VP)

1. **RP sends Authorization Request**: includes `presentation_definition` (see §4.2 and the canonical definition below).
2. **Wallet evaluates**: matches request against stored credentials by `vct`.
3. **User approves**: selects claims to disclose (selective disclosure).
4. **Wallet builds VP Token**: constructs compact SD-JWT:
   ```
   <issuer-JWT>~<disclosure-1>~<disclosure-2>~<kb-JWT>
   ```
   where `<kb-JWT>` is the Key Binding JWT proving holder authentication.
5. **RP verifies**: validates issuer JWT signature, disclosure hashes, and key binding.
6. **RP stores OpenKYCAML record**: reconstructs full credential from disclosed claims
   for CDD reliance and audit records.

### 6.1 Constructing the Authorization Request (Travel Rule Minimum)

A VASP acting as a Relying Party (RP) for Travel Rule verification constructs an OpenID4VP
Authorization Request using the canonical Presentation Definition from
[`examples/presentation-definitions/travel-rule-minimum.json`](../../examples/presentation-definitions/travel-rule-minimum.json).
This definition requests exactly the FATF Recommendation 16 minimum claims.

**Example Authorization Request (JAR — JWT-secured):**

```
GET /authorize?
  response_type=vp_token
  &client_id=https%3A%2F%2Fvasp.example.nl
  &response_uri=https%3A%2F%2Fvasp.example.nl%2Fcallback
  &response_mode=direct_post
  &nonce=n-0S6_WzA2Mj
  &presentation_definition_uri=https%3A%2F%2Fvasp.example.nl%2Fpd%2Ftravel-rule-minimum.json
```

Or inline with the definition embedded:

```json
{
  "response_type": "vp_token",
  "client_id": "https://vasp.example.nl",
  "response_uri": "https://vasp.example.nl/callback",
  "response_mode": "direct_post",
  "nonce": "n-0S6_WzA2Mj",
  "presentation_definition": {
    "id": "openkycaml-travel-rule-minimum-v1",
    "name": "OpenKYCAML Travel Rule Minimum (FATF Rec 16 / TFR 2023/1113 Art. 14)",
    "purpose": "Verify the FATF Recommendation 16 minimum identity data for a natural person originator or beneficiary.",
    "format": {
      "dc+sd-jwt": {
        "sd-jwt_alg_values": ["ES256", "ES384"],
        "kb-jwt_alg_values": ["ES256", "ES384"]
      }
    },
    "input_descriptors": [
      {
        "id": "openkycaml-natural-person-identity",
        "name": "OpenKYCAML KYC Identity Attestation — Natural Person",
        "constraints": {
          "limit_disclosure": "required",
          "fields": [
            {
              "path": ["$.vct"],
              "filter": { "type": "string", "const": "https://openkycaml.org/credentials/v1/OpenKYCAMLCredential" }
            },
            {
              "path": ["$.credentialSubject.ivms101.originator.originatorPersons[0].naturalPerson.name.nameIdentifier[0].primaryIdentifier"],
              "purpose": "Family name (FATF Rec 16 mandatory)"
            },
            {
              "path": ["$.credentialSubject.ivms101.originator.originatorPersons[0].naturalPerson.name.nameIdentifier[0].secondaryIdentifier"],
              "purpose": "Given name(s) (FATF Rec 16 mandatory)"
            },
            {
              "path": ["$.credentialSubject.ivms101.originator.originatorPersons[0].naturalPerson.nationalIdentification.nationalIdentifier"],
              "purpose": "National identifier (FATF Rec 16 / TFR 2023/1113 Art. 14)"
            },
            {
              "path": ["$.credentialSubject.ivms101.originator.accountNumber[0]"],
              "purpose": "Originator account number (crypto address or IBAN)"
            }
          ]
        }
      }
    ]
  }
}
```

> **`limit_disclosure: required`** instructs the wallet to apply selective disclosure and only
> reveal the fields listed above — GDPR data-minimisation is enforced at the protocol layer.
> The wallet holder must explicitly approve each disclosure before the VP Token is sent.

The full canonical Presentation Definition (including optional DoB / address alternative fields
and format constraints) is at [`examples/presentation-definitions/travel-rule-minimum.json`](../../examples/presentation-definitions/travel-rule-minimum.json).

---

## 7. Credential Metadata

### 7.1 Credential Display Configuration

Configure wallet display via the Credential Issuer Metadata `display` array:

```json
{
  "display": [
    {
      "name": "OpenKYCAML KYC Attestation",
      "locale": "en-US",
      "logo": {
        "uri": "https://openkycaml.org/assets/logo.png",
        "alt_text": "OpenKYCAML Logo"
      },
      "background_color": "#003366",
      "text_color": "#FFFFFF",
      "description": "EU AML/KYC Verifiable Credential — FATF Travel Rule and AMLR 2027 compliant"
    }
  ]
}
```

### 7.2 Validity and Refresh

| Field | Recommended value | Notes |
|---|---|---|
| `validFrom` | Date of KYC completion | ISO 8601 with timezone (W3C VC DM 2.0) |
| `validUntil` | `validFrom + 12 months` | Periodic re-verification per AMLR (W3C VC DM 2.0) |
| `credentialStatus.type` | `StatusList2021Entry` | Supports instant revocation |
| Refresh interval | Every 12 months or on risk event | AMLR Art. 22 periodic review |

---

## 8. Selective Disclosure (SD-JWT VC)

OpenKYCAML credentials support SD-JWT selective disclosure as defined in
[IETF draft-ietf-oauth-sd-jwt-vc](https://datatracker.ietf.org/doc/draft-ietf-oauth-sd-jwt-vc/).

The `selectiveDisclosure` block in the OpenKYCAML JSON schema (`schema/versions/v1.2.0.json`)
documents the decoded form of the SD-JWT payload.

### Disclosure construction

Each disclosable claim is represented as a three-element JSON array:

```json
["<salt>", "<claim-name>", <claim-value>]
```

The SHA-256 digest of the base64url-encoded disclosure replaces the claim value in
the issuer-signed JWT:

```json
{ "_sd": ["xG2wRdTCIjDnxJz-fPFq...", "yH3xSdUDJeEoyKa-gQGr..."] }
```

The full `selectiveDisclosure.decodedDisclosures` array in the OpenKYCAML JSON
payload shows the plaintext `(salt, claim, value)` tuples before encoding — useful
for audit records and developer tooling.

### Minimum required disclosures for Travel Rule

Per FATF Recommendation 16 and EU TFR Article 4(1), the following claims **must
always be disclosed** to the beneficiary VASP:

- `family_name`
- `given_name`
- originator account number (`$.ivms101.originator.accountNumber`)

All other claims (date of birth, address, national identifier, risk rating) **may
be withheld** under GDPR data-minimisation when not required by the specific
Travel Rule message context.

---

## 9. Revocation and Status

OpenKYCAML credentials use **StatusList2021** (W3C Verifiable Credentials Status
List v2021) for revocation:

```json
"credentialStatus": {
  "id": "https://issuer.example.com/status/v1#4821",
  "type": "StatusList2021Entry",
  "statusPurpose": "revocation",
  "statusListIndex": "4821",
  "statusListCredential": "https://issuer.example.com/status/v1"
}
```

The EUDI Wallet checks the status list periodically (recommended: every 24 hours)
and marks the credential as revoked in the wallet UI when `statusPurpose: revocation`
is set and the bit at `statusListIndex` is `1`.

---

## 10. Trusted Issuer Validation

Relying parties **should** validate that the credential issuer appears on a
recognised trust list before accepting an OpenKYCAML credential for CDD reliance.

The optional `trustedIssuers` array in the OpenKYCAML schema allows obliged entities
to publish their issuer allowlist inline with the credential configuration:

```json
{
  "trustedIssuers": [
    {
      "issuerId": "did:web:pid-provider.bsi.example.de",
      "issuerName": "Bundesamt für Sicherheit in der Informationstechnik (BSI) — PID Provider",
      "countryCode": "DE",
      "trustFramework": "eIDAS_2.0",
      "eIDASAssuranceLevel": "high",
      "qtspServiceType": "QCertESig",
      "tspServiceUri": "https://www.bundesnetzagentur.de/DE/Sachgebiete/QES/tsp/trusted-list.xml",
      "validFrom": "2025-01-01",
      "validUntil": "2027-12-31"
    }
  ]
}
```

### Validation algorithm

When a relying party receives an OpenKYCAML credential:

1. Extract the `issuer.id` DID from `verifiableCredential.issuer`.
2. Resolve the DID document and retrieve the verification key.
3. Verify the credential signature.
4. **Trust list check** (if `trustedIssuers` is configured):
   a. Check that `issuer.id` appears in `trustedIssuers[*].issuerId`.
   b. If `trustFramework` is `eIDAS_2.0`, additionally verify that the issuer
      appears on the applicable Member State **Trusted List** (TSL) at the URI
      in `tspServiceUri` with a `ServiceStatus` of
      `http://uri.etsi.org/TrstSvc/TrustedList/Svcstatus/granted`.
5. Reject the credential if trust validation fails.

The EU Commission publishes the authoritative List of Trusted Lists (LOTL) at:
`https://ec.europa.eu/tools/lotl/eu-lotl.xml`

---

## 11. Examples

| File | Description |
|---|---|
| [`examples/natural-person-eudi-wallet.json`](../../examples/natural-person-eudi-wallet.json) | Full natural-person EUDI Wallet credential (VC-JWT form) |
| [`examples/natural-person-sd-jwt-eudi-wallet.json`](../../examples/natural-person-sd-jwt-eudi-wallet.json) | Natural-person credential with SD-JWT selective disclosure |
| [`examples/legal-entity-eudi-wallet.json`](../../examples/legal-entity-eudi-wallet.json) | Legal entity (LPID) EUDI Wallet credential |
| [`examples/legal-entity-sd-jwt-eudi-wallet.json`](../../examples/legal-entity-sd-jwt-eudi-wallet.json) | Legal entity SD-JWT credential |
| [`examples/sd-jwt-compact-token.json`](../../examples/sd-jwt-compact-token.json) | Annotated SD-JWT compact-token format — shows encoded `_sd` digests and `~disclosure` structure |
| [`examples/full-kyc-profile-eudi-wallet.json`](../../examples/full-kyc-profile-eudi-wallet.json) | Full KYC profile with EUDI Wallet evidence |
| [`examples/hybrid-with-sar-restriction.json`](../../examples/hybrid-with-sar-restriction.json) | SAR-restricted VC with `gdprSensitivityMetadata`, `tippingOffProtected: true`, and SD-JWT withholding of SAR fields |

---

## 12. Handling Restricted Data in EUDIW Presentations

### 12.1 The Tipping-Off Problem

When an OpenKYCAML credential is issued to a user's EUDI Wallet, there is a
fundamental tension between:

- **Portability** — the user controls their credential and may present it to any
  relying party.
- **Tipping-off prohibition** — AMLR Art. 73 and FATF Recommendation 21 make it a
  criminal offence in most jurisdictions to disclose the *existence* of a SAR/STR
  or internal suspicion flag to the data subject or to parties outside the AML
  compliance chain.

Without explicit sensitivity metadata, a user's wallet app could inadvertently
display SAR-related fields in the credential viewer, or a relying party could
inadvertently request and receive them via an OpenID4VP presentation.

### 12.2 The `gdprSensitivityMetadata` Block

OpenKYCAML v1.3.0 introduces the optional **`gdprSensitivityMetadata`** top-level
object. It provides a machine-readable classification that wallets, issuers, and
relying parties can consume to enforce the correct data-handling policy
automatically.

```json
"gdprSensitivityMetadata": {
  "classification": "sar_restricted",
  "restrictedFields": [
    "/kycProfile/adverseMedia",
    "/kycProfile/sarFilingReference",
    "/kycProfile/internalSuspicionFlag"
  ],
  "tippingOffProtected": true,
  "legalBasis": "AMLR-Art73",
  "retentionPeriod": "P5Y",
  "consentRecord": {
    "consentGiven": false,
    "withdrawalPossible": false
  },
  "disclosurePolicy": {
    "allowedRecipients": ["fiu_only", "law_enforcement_authority"],
    "prohibitedRecipients": ["data_subject", "counterparty_vasp"],
    "requiresExplicitConsent": false
  },
  "auditReference": "sar-case-ref:sha256:c7f3e2a1b9d8f45e..."
}
```

#### Classification values

| Value | Meaning | Applicable regulation |
|---|---|---|
| `standard` | Ordinary personal data | GDPR Art. 6 |
| `sensitive_personal` | Special-category data (biometrics, health) | GDPR Art. 9 |
| `criminal_offence` | Data on criminal convictions or offences | GDPR Art. 10 |
| `sar_restricted` | SAR/STR material — tipping-off protected | AMLR Art. 73 / FATF Rec. 21 |
| `internal_suspicion` | Internal AML suspicion not yet formalised as SAR | AMLR Art. 73 |
| `confidential_aml` | AML/CFT investigation data | AMLR Art. 55 |

#### Enforcement rule

When `tippingOffProtected` is `true`:

1. **Issuer**: MUST NOT include SAR field values in the SD-JWT `decodedDisclosures`
   array. The fields appear only as SHA-256 digests in the `_sd` array of the
   Issuer-JWT and are never appended to a presentation token.
2. **Wallet software**: MUST NOT render `restrictedFields` in the credential
   viewer UI. The wallet MAY display a generic "Restricted — regulatory compliance"
   placeholder.
3. **Relying party**: MUST NOT include `restrictedFields` in `input_descriptors`
   of an OpenID4VP `presentation_definition`. Any presentation token containing
   a disclosure for a restricted field MUST be rejected.
4. **Audit log**: The issuer MUST record the `auditReference` in its DPO/AML
   compliance register. The `auditReference` value MUST be an opaque identifier —
   it MUST NOT contain the SAR narrative or case details.

### 12.3 Cryptographic Enforcement with SD-JWT

The `gdprSensitivityMetadata.restrictedFields` declaration is a policy hint.
**Cryptographic enforcement** is achieved by never generating SD-JWT disclosures
for the restricted fields:

```
Compact SD-JWT token = <Issuer-JWT>~<disclosure-name>~<disclosure-address>~<kb-JWT>
```

SAR-restricted claims (`adverseMedia`, `sarFilingReference`, `internalSuspicionFlag`)
have SHA-256 digests in the Issuer-JWT `_sd` array but no corresponding
`~disclosure` appended. A relying party that receives this token cannot reconstruct
the restricted values even if they attempt to brute-force the salt (the salt is
cryptographically random and at least 128 bits).

This two-layer approach (policy metadata + cryptographic withholding) is the
recommended pattern:

```
┌─────────────────────────────────────────────────────────────────┐
│  gdprSensitivityMetadata  (policy layer)                        │
│  ─────────────────────────────────────────────────────────────  │
│  classification:         sar_restricted                         │
│  tippingOffProtected:    true                                    │
│  disclosurePolicy:       allowedRecipients: [fiu_only]          │
│                          prohibitedRecipients: [data_subject]   │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼  enforced by
┌─────────────────────────────────────────────────────────────────┐
│  SD-JWT cryptographic layer                                     │
│  ─────────────────────────────────────────────────────────────  │
│  SAR fields: digest only in _sd[]  ← NO disclosure appended    │
│  Other fields: normal disclosures appended after ~              │
└─────────────────────────────────────────────────────────────────┘
```

### 12.4 Issuer Guidance: When to Set `tippingOffProtected`

Issuers MUST set `gdprSensitivityMetadata` with `classification: "sar_restricted"`
and `tippingOffProtected: true` in any OpenKYCAML credential that:

- Contains a `kycProfile.adverseMedia` entry linked to a filed SAR/STR.
- Contains an internal suspicion flag or AML case reference.
- Is issued after the obliged entity has filed or is considering filing a SAR.

Issuers SHOULD also:

- Populate `disclosurePolicy.prohibitedRecipients` with at minimum `"data_subject"`.
- Set `legalBasis: "AMLR-Art73"` and `retentionPeriod: "P5Y"` (or longer per
  national law).
- Use a cryptographic hash or UUID for `auditReference` — never embed the SAR
  narrative.
- Instruct the wallet delivery system to suppress the credential from the wallet's
  credential viewer if the wallet supports sensitivity-aware display.

### 12.5 GDPR Art. 9 / Art. 10 Data

For credentials containing biometric data, health data, or data relating to
criminal convictions or offences (GDPR Art. 9 / Art. 10):

- Use `classification: "sensitive_personal"` or `"criminal_offence"` respectively.
- Set `legalBasis` to `"GDPR-Art9-2g"` (substantial public interest) or
  `"GDPR-Art10"` (official authority).
- `tippingOffProtected` is not required for Art. 9/10 data unless it also
  relates to a SAR. Set `disclosurePolicy.requiresExplicitConsent: true` where
  national law requires documented consent.

### 12.6 Python Helper

Using the `GdprSensitivityMetadata` Pydantic model from `tools/python/models.py`:

```python
from tools.python.models import (
    OpenKYCAMLVC, KYCProfileModel, GdprSensitivityMetadata,
    GdprConsentRecord, DisclosurePolicy,
)

vc = OpenKYCAMLVC(
    credential_subject_did="did:ebsi:z5KMnPq9rLtUvWxYz3NjRsT",
    issuer_did="did:web:acme-crypto.example.nl",
    issuer_name="Acme Crypto Exchange BV",
    kyc_profile=KYCProfileModel(customerRiskRating="HIGH", dueDiligenceType="EDD"),
    gdpr_sensitivity=GdprSensitivityMetadata(
        classification="sar_restricted",
        tippingOffProtected=True,          # enforced by model validator
        legalBasis="AMLR-Art73",
        retentionPeriod="P5Y",
        restrictedFields=[
            "/kycProfile/adverseMedia",
            "/kycProfile/sarFilingReference",
        ],
        consentRecord=GdprConsentRecord(consentGiven=False, withdrawalPossible=False),
        disclosurePolicy=DisclosurePolicy(
            allowedRecipients=["fiu_only"],
            prohibitedRecipients=["data_subject"],
        ),
        auditReference="sar-case-ref:sha256:c7f3e2a1b9d8f45e6c09...",
    ),
)
envelope = vc.issue()
```

The model validator raises a `ValueError` at construction time if
`tippingOffProtected` is missing or `False` for `sar_restricted` or
`internal_suspicion` classifications, preventing accidental omission of the
tipping-off flag.

---

*This document is part of the [OpenKYCAML](https://openkycaml.org) specification.*
*For schema details see [`schema/versions/v1.7.0.json`](../../schema/versions/v1.7.0.json).*

---

## W3C VC Data Model Version Support

**Current position (v1.18.0+):** OpenKYCAML uses the **W3C VC Data Model 2.0** `@context` URL (W3C Recommendation, May 2024):

```
https://www.w3.org/ns/credentials/v2
```

This is enforced via a `contains` constraint in the schema at `verifiableCredential.@context`. The VC DM 2.0 upgrade was completed in OpenKYCAML v1.18.0. Credential date fields use the v2 names: `validFrom` (required, replaces v1.1 `issuanceDate`) and `validUntil` (optional, replaces v1.1 `expirationDate`).

**EUDI Wallet context URL:** The second context URL used in EUDI Wallet examples (`https://europa.eu/2018/credentials/eudi/v1`) is a **placeholder** pending the European Commission's official ARF VC JSON-LD context publication. Adopters should monitor the EU Commission's ARF releases and update this URL when the official context is published.

For the historical v1.1 → v2.0 migration reference, see [`vc-data-model-migration.md`](../reference/vc-data-model-migration.md).
