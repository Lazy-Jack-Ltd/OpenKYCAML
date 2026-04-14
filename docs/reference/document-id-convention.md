# OpenKYCAML Document ID Convention

**Introduced:** v1.6.0  
**Status:** Normative  
**Applies to:** `NaturalPersonDocument.documentId`, `LegalEntityDocument.documentId`

---

## Purpose

When KYC/AML payloads are shared between VASPs or compliance systems, each system needs a stable, portable identifier to unambiguously identify, deduplicate, and audit every document in an `identityDocuments` bundle. The OpenKYCAML Document ID Convention defines the canonical URN scheme for this purpose.

The `documentId` field is distinct from two other document identifier fields already present in the schema:

| Field | Purpose | Scope |
|---|---|---|
| `documentId` | Portable canonical identifier for inter-system exchange | Cross-system; must be stable |
| `documentRef` | Internal storage path or content-addressed URI to the file | Internal to the obliged entity |
| `credentialId` | URI of the underlying W3C VC / SD-JWT VC / ISO mDL | VC-specific; used only for digital credentials |

---

## URN Pattern

```
urn:openkycaml:doc:{issuing-country}:{doc-type-code}:{subject-ref}:{discriminator}
```

| Segment | Description | Format | Examples |
|---|---|---|---|
| `issuing-country` | ISO 3166-1 alpha-2 code of the issuing state, lowercase | `[a-z]{2}` | `de`, `gb`, `us` |
| `doc-type-code` | Short code for the document type (see [Short-Code Table](#short-code-table)) | `[a-z0-9-]+` | `national-id`, `passport`, `cert-incorp` |
| `subject-ref` | Stable pseudonymous reference to the subject (see [Subject Reference](#subject-reference-construction)) | `[a-z0-9-]+` | `sha256-421149`, `529900w18lqjjn6sj336` |
| `discriminator` | `YYYY-MM` of the document's issue date, used to distinguish multiple documents of the same type for the same subject | `[0-9]{4}-[0-9]{2}` | `2021-03`, `2026-01` |

The full URN matches the regex pattern:

```
^urn:openkycaml:doc:[a-z]{2}:[a-z0-9-]+:[a-z0-9-]+:[0-9]{4}-[0-9]{2}$
```

### Examples

```
urn:openkycaml:doc:de:national-id:sha256-421149:2021-03
urn:openkycaml:doc:de:proof-of-address:sha256-421149:2026-02
urn:openkycaml:doc:de:eidas-pid:sha256-421149:2026-01
urn:openkycaml:doc:gb:cert-incorp:529900w18lqjjn6sj336:2009-06
urn:openkycaml:doc:gb:registry-extract:529900w18lqjjn6sj336:2026-03
urn:openkycaml:doc:gb:vlei:529900w18lqjjn6sj336:2026-02
```

---

## Short-Code Table

The `doc-type-code` segment maps to the `documentType` enum values defined in the schema.

### Natural Person Document Types

| `documentType` enum value | `doc-type-code` |
|---|---|
| `NATIONAL_ID_CARD` | `national-id` |
| `PASSPORT` | `passport` |
| `RESIDENCE_PERMIT` | `residence-permit` |
| `DRIVERS_LICENCE` | `drivers-licence` |
| `BIRTH_CERTIFICATE` | `birth-cert` |
| `PROOF_OF_ADDRESS` | `proof-of-address` |
| `TAX_IDENTIFICATION` | `tax-id` |
| `SOCIAL_SECURITY` | `social-security` |
| `BIOMETRIC_DATA_RECORD` | `biometric` |
| `EIDAS_PID_CREDENTIAL` | `eidas-pid` |
| `OTHER` | `other` |

### Legal Entity Document Types

| `documentType` enum value | `doc-type-code` |
|---|---|
| `CERTIFICATE_OF_INCORPORATION` | `cert-incorp` |
| `ARTICLES_OF_ASSOCIATION` | `articles` |
| `REGISTRY_EXTRACT` | `registry-extract` |
| `LEI_REGISTRATION` | `lei` |
| `VLEI_CREDENTIAL` | `vlei` |
| `PROOF_OF_REGISTERED_ADDRESS` | `proof-reg-address` |
| `TRUST_DEED` | `trust-deed` |
| `PARTNERSHIP_AGREEMENT` | `partnership-agreement` |
| `FOUNDATION_CHARTER` | `foundation-charter` |
| `ULTIMATE_BENEFICIAL_OWNER_REGISTER` | `ubo-register` |
| `AUTHORISED_SIGNATORY_LIST` | `auth-signatory` |
| `ANNUAL_REPORT_ACCOUNTS` | `annual-report` |
| `VAT_REGISTRATION_CERTIFICATE` | `vat-cert` |
| `REGULATORY_LICENCE` | `reg-licence` |
| `LPID_CREDENTIAL` | `lpid` |
| `OTHER` | `other` |

> **Note:** The enum values in the schema remain the canonical `SCREAMING_SNAKE_CASE` identifiers. The short codes in this table are only used inside `documentId` URNs.

---

## Subject Reference Construction

The `subject-ref` segment provides a stable, pseudonymous reference to the subject of the document. The construction method differs for natural persons and legal entities.

### Natural Persons — Pseudonymous Hash

Compute `subject-ref` as the string `sha256-` followed by the first 6 hexadecimal characters of the SHA-256 digest of the concatenation of three subject attributes:

```
subject-ref = "sha256-" + SHA256(nationalIdentifier + issuingCountry + dateOfBirth)[0:6]
```

All values are concatenated without a separator, using their raw string form:

- `nationalIdentifier` — as recorded in `nationalIdentification.nationalIdentifier`
- `issuingCountry` — ISO 3166-1 alpha-2 uppercase (e.g. `DE`)
- `dateOfBirth` — ISO 8601 date string (e.g. `1985-07-22`)

**Fallback** — If `nationalIdentifier` is unavailable, substitute the document's `primaryIdentifier` (family name) and `secondaryIdentifier` (given name) concatenated as `primaryIdentifier + secondaryIdentifier + dateOfBirth`.

**Example:**

```
nationalIdentifier = "L01X00T471"
issuingCountry     = "DE"
dateOfBirth        = "1985-07-22"

input  = "L01X00T471DE1985-07-22"
SHA256 = 421149...
subject-ref = "sha256-421149"
```

> **GDPR:** The 6-character truncation of a SHA-256 hash cannot be reverse-engineered to recover any personal attribute. Do not use a raw name, date of birth, or national identifier as the `subject-ref` for natural persons.

### Legal Entities — Public Registration Number or LEI

Use the entity's publicly available registration identifier, lowercased and stripped of spaces and hyphens:

1. **Preferred:** LEI (ISO 17442), lowercased — e.g. `529900W18LQJJN6SJ336` → `529900w18lqjjn6sj336`
2. **Alternative:** Company registration number (from the issuing registry), lowercased — e.g. `00123456`

Use the LEI as `subject-ref` whenever one is available, since it is globally unique and unambiguous across jurisdictions. Fall back to the registration number only when no LEI has been assigned.

**Example:**

```
LEI = "529900W18LQJJN6SJ336"
subject-ref = "529900w18lqjjn6sj336"
```

---

## Discriminator

The `discriminator` segment is the `YYYY-MM` of the document's `issueDate`. It prevents `documentId` collisions when a subject holds multiple documents of the same type issued in the same month.

If two documents of the same `documentType`, same `issuingCountry`, and same `subject-ref` have the same `YYYY-MM` issue date, append `-02`, `-03`, etc. to the discriminator of the later-processed document:

```
urn:openkycaml:doc:de:passport:sha256-421149:2025-06
urn:openkycaml:doc:de:passport:sha256-421149:2025-06-02   ← second passport issued same month
```

---

## Relationship to Other Document Fields

| Field | Used for | Cross-system portable? |
|---|---|---|
| `documentId` | Canonical identifier for deduplication and audit across VASPs | ✅ Yes — must be stable |
| `documentRef` | Internal storage URI or content-addressed reference to the file held by this obliged entity | ❌ No — internal only |
| `credentialId` | URI of the underlying W3C VC, SD-JWT VC, or ISO mDL | Partially — only meaningful when the VC is publicly accessible |
| `verifyingDocumentRef` | Cross-reference from an identity assertion (e.g. `NationalIdentification`, `BeneficialOwner`) to the document that evidenced it, within the same payload | Within-payload — points to `documentRef` |

When a receiving system needs to check whether a document in an incoming payload is the same physical document it already holds, it should compare `documentId` values. Do not use `documentRef` for cross-system deduplication, as it is an internal storage path that has no meaning outside the originating system.

---

## Cross-System Deduplication

When two VASPs exchange payloads referencing the same underlying document:

1. The originating VASP includes `documentId` on the document record.
2. The receiving VASP computes or extracts the `documentId` from the received payload.
3. If the receiving VASP already holds a document with the same `documentId`, it can treat the incoming record as a re-share of the same document rather than a new one.
4. If the `documentId` is absent, the receiving system may attempt to derive it from `documentType`, `issuingCountry`, `documentNumber`, and `issueDate`, or treat the document as unresolvable.

---

## Lifecycle Rules

- A document's `documentId` **must not change** when it is re-shared between systems or when the obliged entity's internal `documentRef` changes (e.g. after a file-store migration).
- If a document is superseded (e.g. a renewed passport), the new document gets a **new `documentId`** reflecting its own `issuingCountry`, `doc-type-code`, `subject-ref`, and `issueDate` discriminator.
- `documentId` values are case-sensitive. All segments are lowercase.

---

## Field Placement in Schema

`documentId` is an optional field on both `NaturalPersonDocument` and `LegalEntityDocument`. It is strongly recommended for all payloads exchanged between systems. When present, it must conform to the URN pattern above.

Schema path: `identityDocuments.naturalPersonDocuments[*].documentId`  
Schema path: `identityDocuments.legalEntityDocuments[*].documentId`
