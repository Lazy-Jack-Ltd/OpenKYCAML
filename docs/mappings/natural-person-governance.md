# Natural Person Governance Fields — `gender` and `occupation`

> Added in **v1.12.0**. Both fields are **optional** and backward-compatible.

---

## 1. Overview

OpenKYCAML v1.12.0 adds two structured fields directly to the `NaturalPerson` $def to close
gaps identified in the v1.11.2 compliance gap analysis:

| Field | Type | Standard alignment |
|---|---|---|
| `gender` | string enum | eIDAS 2.0 PID `gender` attribute (ISO/IEC 5218) |
| `occupation` | object | IVMS 101 extended CDD; eIDAS 2.0 PID `occupation`; ILO/ISCO-08 |

These fields sit alongside the existing `kycProfile.customerClassification.occupationOrPurpose`
free-text field, which is **not deprecated**. The new `occupation` block provides a structured,
person-level complement for risk scoring and eIDAS PID interoperability.

---

## 2. `gender`

### 2.1 Schema path

```
ivms101.originator.originatorPersons[].naturalPerson.gender
ivms101.beneficiary.beneficiaryPersons[].naturalPerson.gender
```

### 2.2 Enum values

| Value | Notes |
|---|---|
| `MALE` | ISO/IEC 5218 code 1 |
| `FEMALE` | ISO/IEC 5218 code 2 |
| `NON_BINARY` | ISO/IEC 5218 code 9 (not applicable / other) extended |
| `OTHER` | Self-described gender outside binary categories |
| `PREFER_NOT_TO_SAY` | Data subject has declined to specify |

### 2.3 Regulatory and standard alignment

| Standard / Regulation | Alignment |
|---|---|
| **eIDAS 2.0 ARF** | Maps to PID attribute `gender` (ISO/IEC 5218). Required by some EUDI Wallet PID issuers for identity assurance at LoA High. |
| **IVMS 101** | Extended CDD data element for natural persons. Optional in IVMS 101 v1.0 but recommended for jurisdictions requiring sex/gender in KYC records. |
| **AMLR Art. 22** | Not explicitly required by AMLR; included for completeness of natural-person CDD record. |

### 2.4 GDPR Art. 9 sensitivity

Gender is a **special-category personal data** element under **GDPR Art. 9** if it relates to a
person's sex life or sexual orientation. Even as a binary `MALE`/`FEMALE` value it is personal data
under Art. 4(1). Obliged entities **must**:

- Identify a lawful basis under Art. 6 (and Art. 9(2) if applicable).
- Apply data minimisation — collect only where jurisdictionally required or necessary for the
  specific CDD purpose.
- Document in the ROPA (Art. 30 records) the purpose and legal basis.
- Apply appropriate access controls and encryption at rest.

### 2.5 JSON example

```json
{
  "naturalPerson": {
    "name": { "nameIdentifier": [{ "primaryIdentifier": "SCHMIDT", "secondaryIdentifier": "ANNA", "nameIdentifierType": "LEGL" }] },
    "gender": "FEMALE"
  }
}
```

---

## 3. `occupation`

### 3.1 Schema path

```
ivms101.originator.originatorPersons[].naturalPerson.occupation
ivms101.beneficiary.beneficiaryPersons[].naturalPerson.occupation
```

### 3.2 Sub-fields

| Sub-field | Type | Description |
|---|---|---|
| `occupationCode` | string enum | Broad ILO/ISCO-08-aligned occupation category |
| `occupationDescription` | string (max 200) | Free-text job title or occupation detail |

Both sub-fields are optional. Either or both may be populated.

### 3.3 `occupationCode` enum values

| Value | ILO/ISCO-08 alignment | Notes |
|---|---|---|
| `EMPLOYED` | Major groups 1–9 (employed persons) | In salaried or waged employment |
| `SELF_EMPLOYED` | Major groups 1–3, 5 (own-account workers) | Freelancer, sole trader, contractor |
| `BUSINESS_OWNER` | Major group 1 (managers and proprietors) | Owns and manages a business |
| `STUDENT` | — | Full-time or part-time student |
| `RETIRED` | — | Retired from active employment |
| `UNEMPLOYED` | — | Actively seeking employment |
| `PUBLIC_OFFICIAL` | Major group 1 sub-group 111 (legislators, senior officials) | Government/public-sector official; may trigger PEP screening |
| `OTHER` | — | Occupation does not fit any above category; use occupationDescription |

### 3.4 Relationship to `occupationOrPurpose`

| Field | Location | Format | Purpose |
|---|---|---|---|
| `occupationOrPurpose` | `kycProfile.customerClassification` | Free-text string (max 200) | Shared CDD field for both natural persons and legal entities; business purpose for entities |
| `occupation` | `NaturalPerson` | Structured object | Structured, person-level; aligned to eIDAS PID and IVMS 101; supports structured risk scoring |

The two fields are complementary. Where both are present, `occupation` takes precedence for structured
processing; `occupationOrPurpose` provides the human-readable narrative.

### 3.5 Regulatory alignment

| Standard / Regulation | Alignment |
|---|---|
| **IVMS 101 extended CDD** | `occupation` aligns with the IVMS 101 extended CDD data set for natural person source-of-funds verification. |
| **eIDAS 2.0 PID** | Maps to the optional eIDAS 2.0 PID attribute `occupation` where issued by a PID issuer. |
| **AMLR Art. 22** | Supports source-of-wealth and source-of-funds verification for CDD and EDD. `PUBLIC_OFFICIAL` code may trigger PEP screening. |
| **FATF Rec. 12** | `PUBLIC_OFFICIAL` occupationCode directly supports PEP identification workflows. |

### 3.6 JSON example

```json
{
  "naturalPerson": {
    "name": { "nameIdentifier": [{ "primaryIdentifier": "MÜLLER", "secondaryIdentifier": "THOMAS", "nameIdentifierType": "LEGL" }] },
    "gender": "MALE",
    "occupation": {
      "occupationCode": "SELF_EMPLOYED",
      "occupationDescription": "Freelance software consultant"
    }
  }
}
```

---

## 4. Field mapping summary

| OpenKYCAML field | eIDAS 2.0 PID attribute | IVMS 101 element | GDPR sensitivity |
|---|---|---|---|
| `NaturalPerson.gender` | `gender` (ISO/IEC 5218) | Extended CDD (optional) | Art. 9 special category — handle with care |
| `NaturalPerson.occupation.occupationCode` | `occupation` (ILO code) | Extended CDD (optional) | Standard personal data (Art. 4) |
| `NaturalPerson.occupation.occupationDescription` | `occupation` (free text) | Extended CDD (optional) | Standard personal data (Art. 4) |

---

*Last updated: v1.12.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*
