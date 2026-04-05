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
6. [Validation](#6-validation)
7. [Versioning and Upgrades](#7-versioning-and-upgrades)
8. [FAQ](#8-faq)

---

## 1. Prerequisites

- An understanding of [IVMS 101](https://intervasp.org/) for the Travel Rule payload.
- JSON Schema draft 2020-12 compatible validator (see [tools/](../tools/)).
- Optional: familiarity with [W3C Verifiable Credentials Data Model v2](https://www.w3.org/TR/vc-data-model-2.0/) for VC wrapping.

---

## 2. Use Case 1: Travel Rule (VASP)

### Goal
Transmit compliant Travel Rule messages between VASPs under FATF Recommendation 16, MiCA Article 83, and the EU Funds Transfer Regulation (TFR) 2023.

### Minimum Required Fields
For a FATF-compliant Travel Rule message, the `ivms101` block must include:

**Originator (natural person):**
- `name.nameIdentifiers[0].primaryIdentifier` — family name
- `name.nameIdentifiers[0].secondaryIdentifier` — given name
- `name.nameIdentifiers[0].nameIdentifierType` = `"LEGL"`
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
- `originatingVASP.originatingVASP.name.nameIdentifiers[0].legalPersonName`
- `originatingVASP.originatingVASP.nationalIdentification.nationalIdentifier` (LEI preferred)

### Example
See [`examples/minimal-travel-rule.json`](../examples/minimal-travel-rule.json).

### Integration Checklist
- [ ] Generate a unique `messageId` (UUID v4) per message.
- [ ] Set `messageDateTime` to the current UTC timestamp.
- [ ] Set `version` to `"1.2.0"` (or the current schema version).
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
See [`examples/full-kyc-profile.json`](../examples/full-kyc-profile.json).

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
See [`examples/hybrid-vc-wrapped.json`](../examples/hybrid-vc-wrapped.json).

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
See [`examples/legal-entity-plain.json`](../examples/legal-entity-plain.json) and [`examples/full-kyc-profile.json`](../examples/full-kyc-profile.json).

---

## 6. Validation

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

---

## 7. Versioning and Upgrades

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

## 8. FAQ

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

---

*For further guidance, open a [discussion on GitHub](https://github.com/Lazy-Jack-Ltd/openKYCAML/discussions).*
