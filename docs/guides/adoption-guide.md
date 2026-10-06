# OpenKYCAML Adoption Guide

This guide walks you through integrating OpenKYCAML into your product or infrastructure. It targets three main adopter profiles:

1. **VASPs / Crypto Exchanges** — Travel Rule compliance under FATF Rec 16 / MiCA / TFR.
2. **Banks and Payment Institutions** — AMLR 2027 CDD reliance and cross-system data sharing.
3. **KYC Utilities / Identity Providers** — Portable KYC attestations using eIDAS 2.0 Verifiable Credentials.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Use Case 1: Travel Rule (VASP)](#2-use-case-1-travel-rule-vasp)
3. [Use Case 2: Third-Party CDD Reliance (Bank)](#3-use-case-2-third-party-cdd-reliance-bank)
4. [Use Case 3: Portable KYC with eIDAS 2.0 VC](#4-use-case-3-portable-kyc-with-eidas-20-vc)
5. [Use Case 4: Full KYC Profile Sharing](#5-use-case-4-full-kyc-profile-sharing)
6. [Use Case 5: Integrating with Legacy Payment Rails via ISO 20022](#6-use-case-5-integrating-with-legacy-payment-rails-via-iso-20022)
7. [Validation](#7-validation)
8. [Building a Compliant Document Bundle](#8-building-a-compliant-document-bundle)
9. [Versioning and Upgrades](#9-versioning-and-upgrades)
10. [FAQ](#10-faq)

---

## 1. Prerequisites

- **New to JSON?** Read [JSON 101 for AML](json-101-for-aml.md) — a plain-English introduction to JSON and the most common AML data-sync failure patterns.
- **Want to understand JSON Schema as a data contract?** Read [JSON 102 for AML](json-102-for-aml.md) — covers `required`, `enum`, `format`, `pattern`, `$defs`, `if/then/else`, and `additionalProperties`.
- An understanding of [IVMS 101](https://intervasp.org/) for the Travel Rule payload.
- JSON Schema draft 2020-12 compatible validator (see [tools/](../../tools/)).
- Optional: familiarity with [W3C Verifiable Credentials Data Model v2](https://www.w3.org/TR/vc-data-model-2.0/) for VC wrapping.

---

## 2. Use Case 1: Travel Rule (VASP)

### Goal
Transmit compliant Travel Rule messages between VASPs under FATF Recommendation 16, MiCA Article 83, and the EU Funds Transfer Regulation (TFR) 2023.

### Minimum Required Fields
For a FATF-compliant Travel Rule message, the `ivms101` block must include:

**Originator (natural person):**
- `name.nameIdentifier[0].primaryIdentifier` — family name
- `name.nameIdentifier[0].secondaryIdentifier` — given name
- `name.nameIdentifier[0].nameIdentifierType` = `"LEGL"`
- `nationalIdentification.nationalIdentifier`
- `nationalIdentification.nationalIdentifierType`
- `dateAndPlaceOfBirth.dateOfBirth` *(or address)*
- `countryOfResidence` *(or address)*

**Originator account number:**
- `originator.accountNumber[]` — blockchain address or account

**Transfer amount and asset type:**
- `transferredAmount.amount`
- `transferredAmount.assetType`

**Originating VASP:**
- `originatingVASP.name.nameIdentifier[0].legalPersonName`
- `originatingVASP.nationalIdentification.nationalIdentifier` (LEI preferred)

### Example
See [`examples/minimal-travel-rule.json`](../../examples/minimal-travel-rule.json).

### Integration Checklist
- [ ] Generate a unique `messageId` (UUID v4) per message.
- [ ] Set `messageDateTime` to the current UTC timestamp.
- [ ] Set `version` to `"1.7.0"` (or the current schema version).
- [ ] Validate the payload against the OpenKYCAML schema before sending.
- [ ] Ensure your Travel Rule protocol (OpenVASP, TRP, TRISA, Notabene) transmits the `ivms101` block in its data payload.

---

## 3. Use Case 2: Third-Party CDD Reliance (Bank)

### Goal
Accept KYC data from a third-party CDD provider and store/forward it in a standardised format, as permitted under AMLR 2027 Article 22(5).

### Steps

1. **Request a KYC record** from the third-party provider in OpenKYCAML format.
2. **Validate** the received record against the schema.
3. **Store the full `kycProfile`** in your customer master data system.
4. **Map the `auditMetadata`** to your own record-keeping system for regulatory compliance (AMLR Art. 56 — 5-year retention).
5. **Record your own `changeLog` entry** showing that you received and accepted the CDD.

### Key Fields to Check

| Field | Your Obligation |
|---|---|
| `kycProfile.dueDiligenceType` | Verify it meets your risk rating requirement (SDD/CDD/EDD). |
| `kycProfile.customerRiskRating.overallRiskRating` | Must be ≤ your threshold for reliance. |
| `kycProfile.auditMetadata.dataRetentionDate` | Extend if your retention policy is longer. |
| `kycProfile.sanctionsScreening.screeningDate` | Must be ≤ 30 days old (or re-screen). |
| `kycProfile.pepStatus.isPEP` | If `true`, apply your own EDD before relying. |

### Example
See [`examples/full-kyc-profile.json`](../../examples/full-kyc-profile.json).

---

## 4. Use Case 3: Portable KYC with eIDAS 2.0 VC

### Goal
Issue a Verifiable Credential (VC) that encapsulates a customer's KYC/AML status and can be presented to any relying party via a European Digital Identity Wallet (EUDIW) or compatible wallet.

### Steps

1. **Complete KYC** on your platform and populate the `kycProfile`.
2. **Wrap the record** in a `verifiableCredential` block:
   - Set `issuer` to your institution's DID (e.g., `did:web:bank.example.com`).
   - Set `credentialSubject.id` to the customer's DID or a pseudonymous identifier.
   - Include `credentialStatus` pointing to your status list endpoint.
3. **Sign the credential** using an appropriate proof suite (Ed25519Signature2020, JsonWebSignature2020).
4. **Deliver to the customer's wallet** via OpenID4VCI.
5. The customer can then **present the VC** to another institution via OpenID4VP, avoiding repeat KYC.

### Supported Proof Suites
- `Ed25519Signature2020` — recommended for new deployments.
- `JsonWebSignature2020` — for systems already using JWT infrastructure.
- `DataIntegrityProof` — for advanced cryptographic suites (BBS+, etc.).

### Example
See [`examples/hybrid-vc-wrapped.json`](../../examples/hybrid-vc-wrapped.json).

---

## 5. Use Case 4: Full KYC Profile Sharing

### Goal
Share a complete risk-rated KYC/AML profile between institutions for correspondent banking, VASP onboarding, or cross-border data sharing under data-sharing agreements.

### Recommended Profile for Corporate Customers

When sharing a legal entity record, always include:

```json
{
  "ivms101": { /* legal person block */ },
  "kycProfile": {
    "customerRiskRating": { /* ... */ },
    "customerClassification": "CORPORATE",
    "dueDiligenceType": "CDD",
    "pepStatus": { /* ... */ },
    "sanctionsScreening": { /* ... */ },
    "adverseMedia": { /* ... */ },
    "sourceOfFundsWealth": { /* ... */ },
    "beneficialOwnership": [ /* UBOs */ ],
    "monitoringInfo": { /* ... */ },
    "auditMetadata": { /* ... */ }
  }
}
```

### Beneficial Ownership Requirement
Per AMLR Article 26, you **must** include the `beneficialOwnership` array for all legal entities, listing all UBOs with ≥ 25% ownership or effective control.

### Example
See [`examples/legal-entity-plain.json`](../../examples/legal-entity-plain.json) and [`examples/full-kyc-profile.json`](../../examples/full-kyc-profile.json).

---

## 6. Use Case 5: Integrating with Legacy Payment Rails via ISO 20022

### Goal
Embed a full OpenKYCAML KYC/AML payload inside an ISO 20022 `pacs.008` (interbank credit transfer) or `pain.001` (customer credit transfer initiation) message for Travel Rule, CDD reliance, or audit-trail purposes — without modifying the ISO 20022 schema or breaking existing parsers.

### The `<SplmtryData>` Mechanism

ISO 20022 provides a standards-approved extension point called `<SplmtryData>`. OpenKYCAML uses this to embed the full KYC/AML dataset — risk scores, screening results, eIDAS 2.0 VC proofs, consent records, GDPR metadata — alongside the standard payment fields.

The `<PlcAndNm>` discriminator `OpenKYCAML/KYCAMLEnvelope/1.0` identifies the envelope. All conforming parsers check this value before attempting to decode the `<Envlp>` content.

### Supported Profiles

| Profile | File | Use Case |
|---|---|---|
| Travel Rule (CBPR+) | [`travel-rule-pacs.008-profile.json`](../../iso20022-integration/profiles/travel-rule-pacs.008-profile.json) | FATF Rec 16 / MiCA Art. 83 VASP-to-VASP transfer |
| CDD Reliance | [`pain.001-kyc-envelope-profile.json`](../../iso20022-integration/profiles/pain.001-kyc-envelope-profile.json) | AMLR Art. 48 third-party CDD reliance |
| Audit Trail | [`camt.053-kyc-audit-profile.json`](../../iso20022-integration/profiles/camt.053-kyc-audit-profile.json) | AMLR Art. 56 five-year record-keeping |

### Quick Start (Python)

```python
import json
import sys

sys.path.insert(0, "iso20022-integration/libraries/python")
from converter import openkycaml_to_pacs008, iso20022_to_openkycaml

# Convert OpenKYCAML payload → pacs.008 XML
with open("examples/minimal-travel-rule.json") as f:
    payload = json.load(f)

xml = openkycaml_to_pacs008(payload)
print(xml)          # Full pacs.008 with <SplmtryData> KYCAMLEnvelope

# Parse pacs.008 XML back → OpenKYCAML dict
recovered = iso20022_to_openkycaml(xml)
print(recovered["ivms101"]["originator"])
```

### XML Examples

- [`pacs.008-with-openkycaml-supplementarydata.xml`](../../iso20022-integration/examples/pacs.008-with-openkycaml-supplementarydata.xml) — Full CBPR+ Travel Rule message
- [`pain.001-with-kyc-envelope.xml`](../../iso20022-integration/examples/pain.001-with-kyc-envelope.xml) — Corporate CDD reliance message
- [`minimal-travel-rule-pacs008-snippet.xml`](../../iso20022-integration/examples/minimal-travel-rule-pacs008-snippet.xml) — Copy-paste `<SplmtryData>` block

See [`iso20022-integration/`](../../iso20022-integration/) for the complete module, including TypeScript support, bidirectional field mapping, and the `KYCAMLEnvelope` JSON Schema.

---

## 7. Validation

### Online Validator
Use the online validator at [https://openkycaml.org/validate](https://openkycaml.org/validate) to check any payload instantly.

### Python CLI

```bash
pip install -r tools/python/requirements.txt
python tools/python/validator.py examples/full-kyc-profile.json
```

### JavaScript / Node.js

```bash
cd tools/javascript
npm install
node validator.js ../../examples/full-kyc-profile.json
```

### Programmatic (Python)

```python
from validator import OpenKYCAMLValidator

v = OpenKYCAMLValidator()
result = v.validate(payload_dict)
if result.is_valid:
    print("Valid OpenKYCAML payload")
else:
    for error in result.errors:
        print(f"  {error.path}: {error.message}")
```

### Using examples as test fixtures

The [`examples/`](../../examples/) directory contains 25 schema-valid payloads covering the full range of compliance scenarios.  They are automatically validated by the CI workflow on every push — adding a new file to `examples/` enrolls it in CI with no workflow changes needed.

See **[`examples/EXAMPLES.md`](../../examples/EXAMPLES.md)** for:
- A full per-file catalogue table (scenario, subject type, schema version, data blocks present)
- Copy-paste pytest parametrize patterns for integration test suites
- Notes on special files (`sd-jwt-compact-token.json`, `travel-rule-vc-wrapped.json`, document bundle examples)

---

## 8. Building a Compliant Document Bundle

OpenKYCAML v1.5.0 introduces the `identityDocuments` block — a typed, structured bundle of verification documents that satisfies the documentary evidence requirements of **ISO 17442**, **GLEIF LOUs**, **FATF Rec. 10/24/25**, and **AMLR Art. 22 and 26**.

### Why a document bundle?

The `kycProfile.dueDiligenceRequirements.verificationMethods[]` block records *how* each attribute was verified. The `identityDocuments` block records *what documents* were examined to produce that verification. Together they provide end-to-end auditability from raw evidence → extracted attribute → verified identity claim.

### 8.1 GLEIF RAL Lookup Workflow

When onboarding a legal entity, the correct registration authority must be identified using the **GLEIF Registration Authorities List (RAL)**. The RAL maps every jurisdiction to its official national business registry.

**Steps:**

1. Determine the entity's `countryOfRegistration` (ISO 3166-1 alpha-2).
2. Look up the RAL at [https://www.gleif.org/en/about-lei/code-lists/gleif-registration-authorities-list](https://www.gleif.org/en/about-lei/code-lists/gleif-registration-authorities-list).
3. Find the matching `ralCode` (format: `RA######`).
4. Populate `nationalIdentification.registrationAuthorityDetail` with the structured RAL reference.

**Common RAL codes:**

| Jurisdiction | Registry | RAL Code |
|---|---|---|
| United Kingdom | Companies House | `RA000585` |
| Germany | Handelsregister | `RA000602` |
| United States (Federal) | SEC / IRS EIN | `RA000543` |
| France | INSEE / RCS | `RA000518` |
| Netherlands | Kamer van Koophandel | `RA000440` |
| Japan | Ministry of Justice | `RA000397` |
| Ireland | Companies Registration Office | `RA000190` |

When the registry is digitally accessible (`digitalAccessible: true`), the live registry record is the primary evidence source per GLEIF LOU practice. A `registryUrl` should always be included so the record can be re-verified in future.

### 8.2 Required Documents by Entity Type

#### Natural Persons (CDD)

| Required | Document Type | Notes |
|---|---|---|
| Yes (one of) | `PASSPORT`, `NATIONAL_ID_CARD`, `RESIDENCE_PERMIT` | Primary photo-ID |
| Yes | `PROOF_OF_ADDRESS` | Utility bill or bank statement, not older than 3 months |
| EDD only | `TAX_IDENTIFICATION` or `SOCIAL_SECURITY` | Secondary identifier |
| EDD / Remote | `EIDAS_PID_CREDENTIAL` | Fulfils AMLR Art. 22(5)(b) for non-face-to-face |

#### Legal Entities — Company (COMPANY)

| Required | Document Type | Notes |
|---|---|---|
| Yes | `CERTIFICATE_OF_INCORPORATION` | Evidences legal name, date of formation, ELF code |
| Yes | `ARTICLES_OF_ASSOCIATION` | Evidences legal sub-type (private/public) |
| Yes | `REGISTRY_EXTRACT` | Current extract from RAL-designated registry; validity ≤ 6 months |
| Recommended | `LEI_REGISTRATION` | Confirms LEI via ISO 17442 |
| Recommended | `ULTIMATE_BENEFICIAL_OWNER_REGISTER` | e.g. UK PSC register, EU UBO register |
| EDD | `ANNUAL_REPORT_ACCOUNTS` | Source of funds verification |
| EDD | `AUTHORISED_SIGNATORY_LIST` | Mandate and representative verification |

#### Legal Entities — Trust (TRUST)

| Required | Document Type |
|---|---|
| Yes | `TRUST_DEED` |
| Yes | `ULTIMATE_BENEFICIAL_OWNER_REGISTER` |
| Recommended | `REGISTRY_EXTRACT` (if registered) |
| Recommended | `AUTHORISED_SIGNATORY_LIST` |

#### Legal Entities — Foundation (FOUNDATION)

| Required | Document Type |
|---|---|
| Yes | `FOUNDATION_CHARTER` |
| Yes | `REGISTRY_EXTRACT` |
| Recommended | `ULTIMATE_BENEFICIAL_OWNER_REGISTER` |

#### Legal Entities — Partnership (PARTNERSHIP)

| Required | Document Type |
|---|---|
| Yes | `PARTNERSHIP_AGREEMENT` |
| Yes | `REGISTRY_EXTRACT` |
| Recommended | `ULTIMATE_BENEFICIAL_OWNER_REGISTER` |

### 8.3 The GLEIF vLEI Credential Hierarchy

For legal entities that have a GLEIF vLEI credential, include a `VLEI_CREDENTIAL` record and set the `vLEICredentialType`:

| Type | Full Name | Purpose |
|---|---|---|
| `QVI` | Qualified vLEI Issuer credential | Issued by GLEIF to authorised QVI issuers; confirms issuer authority |
| `OOR` | Official Organisational Role credential | Issued to legal representatives (Directors, Authorised Signatories); maps to `lpid.mandates[]` |
| `ECR` | Engagement Context Role credential | Issued to employees for specific business contexts |

**Example vLEI chain:** GLEIF → QVI (e.g. LuxTrust SA) → OOR for Director of Acme PLC.

The `credentialIssuer` field should be the DID of the QVI, and `credentialId` the URI of the specific credential.

### 8.4 Populating `extractedAttributes`

The `extractedAttributes[]` array records exactly which data elements were read from each document and whether they match the asserted values in the IVMS 101 / `kycProfile` record:

```json
{
  "attributeName": "dateOfBirth",
  "value": "1985-07-22",
  "matchesRecord": true
}
```

Set `matchesRecord: false` when a discrepancy is detected — this flags the record for manual review before setting `bundleCompleteness: "COMPLETE"`.

### 8.5 Linking Documents to Assertions

Use the cross-reference fields added in v1.5.0 to connect verified claims back to their evidence:

```json
"nationalIdentification": {
  "nationalIdentifier": "L01X00T471",
  "nationalIdentifierType": "IDCD",
  "verifyingDocumentRef": "urn:doc:de-nid-andreas-schmidt-001"
}
```

```json
"legalPerson": {
  "legalFormCode": "Z13E",
  "verifyingDocumentRef": "urn:doc:gb-registry-extract-acme-plc-2026"
}
```

```json
"verificationMethods": [{
  "attribute": "legalPerson.legalFormCode",
  "method": "DATABASE_CHECK",
  "documentRef": "urn:doc:lei-529900W18LQJJN6SJ336-confirmation-2026"
}]
```

### 8.6 Complete Working Examples

- **Natural person bundle:** [`examples/document-bundle-natural-person.json`](../../examples/document-bundle-natural-person.json) — German national: Personalausweis + proof of address + eIDAS PID VC.
- **Legal entity bundle (UK PLC):** [`examples/document-bundle-legal-entity.json`](../../examples/document-bundle-legal-entity.json) — Certificate of Incorporation + Companies House extract + LEI registration + vLEI OOR + PSC register (GLEIF RAL `RA000585`, ELF code `Z13E`).

---

## 9. Versioning and Upgrades

OpenKYCAML follows **semantic versioning** (MAJOR.MINOR.PATCH):

| Change Type | Version Increment | Example |
|---|---|---|
| New optional field added | PATCH | `1.0.0` → `1.0.1` |
| New optional section added | MINOR | `1.0.0` → `1.1.0` |
| Required field changed / removed | MAJOR | `1.0.0` → `2.0.0` |

**Backward compatibility guarantee:** All MINOR and PATCH changes are backward-compatible. A validator for `v1.0.0` will accept any `v1.x.x` payload.

When upgrading:
1. Update the `$schema` URI in your payloads to the new version.
2. Update the `version` field value.
3. Run the new schema validator against existing payloads in test.

---

## 10. FAQ

**Q: Do I need to use the `verifiableCredential` wrapper?**
No. It is entirely optional. Use it only if you need eIDAS 2.0 / EUDIW-compatible attestations.

**Q: Can I extend the schema with custom fields?**
Yes. Add custom fields under a namespaced extension key (e.g., `"x-mycompany:internalRiskModel": {}`). Use the JSON Schema `additionalProperties: true` behaviour. Custom fields are ignored by standard validators.

**Q: Is the schema compliant with FATF Recommendation 16 today?**
Yes. The `ivms101` block is a strict superset of IVMS 101 version 1.0, which is the standard referenced by FATF Rec 16.

**Q: When is the `kycProfile` required?**
Never for Travel Rule messages alone. It is required when sharing CDD data under AMLR Art. 22(5) or when issuing a portable KYC VC.

**Q: How do I handle encryption for PII?**
Use your existing message encryption layer (e.g., JWE, TLS 1.3). OpenKYCAML defines the data structure, not the transport security. For VC-wrapped payloads, selective disclosure using SD-JWT or BBS+ is recommended.

**Q: How do I flag SAR-related data to prevent tipping-off?**
Use the `gdprSensitivityMetadata` block (added v1.3.0). Set `classification: "sar_restricted"`, `tippingOffProtected: true`, and populate `restrictedFields[]` with the JSON Pointer paths of SAR-linked fields. Set `disclosurePolicy.prohibitedRecipients` to include `"data_subject"`. Critically, do **not** include SAR-restricted fields in the SD-JWT `decodedDisclosures` array — they should appear only as `_sd` digests in the Issuer-JWT. See [`examples/hybrid-with-sar-restriction.json`](../../examples/hybrid-with-sar-restriction.json) for a complete example, and §12 of the [EUDI Wallet Integration Guide](eudi-wallet-integration.md) for full guidance.

**Q: What is the difference between `sar_restricted` and `internal_suspicion`?**
`sar_restricted` is for data linked to a SAR/STR that has been (or is being) filed. `internal_suspicion` is for earlier-stage AML flags before a formal SAR decision. Both require `tippingOffProtected: true` — the Pydantic model enforces this at construction time.

---

*For further guidance, open a [discussion on GitHub](https://github.com/Lazy-Jack-Ltd/openKYCAML/discussions).*
