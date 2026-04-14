# JSON 102 for AML: JSON Schema — The Contract That Keeps Your AML Systems in Sync

**Audience:** Compliance officers, operations managers, project leads, and business analysts specifying data requirements to technology vendors. Familiarity with [JSON 101](json-101-for-aml.md) is assumed.

---

## Table of Contents

1. [Recap and bridge from JSON 101](#1-recap-and-bridge-from-json-101)
2. [The schema as a data contract](#2-the-schema-as-a-data-contract)
3. [Required fields — stopping silent data loss](#3-required-fields--stopping-silent-data-loss)
4. [Reusable building blocks (`$defs` / `$ref`)](#4-reusable-building-blocks-defs--ref)
5. [Controlled vocabularies (`enum`, `const`)](#5-controlled-vocabularies-enum-const)
6. [Format rules that prevent bad data at source](#6-format-rules-that-prevent-bad-data-at-source)
7. [Conditional rules (`if` / `then` / `else`)](#7-conditional-rules-if--then--else)
8. [Strict mode (`additionalProperties: false`)](#8-strict-mode-additionalproperties-false)
9. [Annotation fields (`_comment`, `_disclaimer`)](#9-annotation-fields-_comment-_disclaimer)
10. [The OpenKYCAML schema in practice](#10-the-openkycaml-schema-in-practice)
11. [Glossary](#11-glossary)

---

## 1. Recap and bridge from JSON 101

[JSON 101](json-101-for-aml.md) showed that JSON is a universal text format for exchanging data, built from just six building blocks: objects, arrays, strings, numbers, booleans, and null. It also showed the four ways integrations break when two systems agree to "use JSON" but disagree on the details.

The resolution to every one of those failure patterns is the same: a **JSON Schema**.

Think of it this way:

- **JSON** is the message — the actual customer record, the screening result, the transaction alert.
- **JSON Schema** is the envelope — a precise, formal description of what must be in that message, what field names to use, what values are allowed, and what happens if something is wrong.

If you have worked with traditional financial messaging, this is the same concept as SWIFT MT message validation or ISO 20022 schema constraints. Both sides agree on the structure in advance. When a message arrives, it is validated against the agreed structure before any system processes it. If it does not match, it is rejected with a machine-readable error — not silently accepted and quietly corrupting your data.

JSON Schema is the official companion standard to JSON. The current version is **Draft 2020-12**. OpenKYCAML uses it to define the exact structure, rules, and constraints for every KYC/AML message.

---

## 2. The schema as a data contract

A JSON Schema document is itself a JSON file. Its first three lines establish the contract:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id":     "https://openkycaml.org/schema/v1.15.0/kyc-aml-hybrid-extended.json",
  "version": "1.15.0"
}
```

| Field | What it means for a business user |
|---|---|
| `$schema` | Declares which version of the JSON Schema standard this document uses — so validators know which rules to apply. |
| `$id` | A unique, permanent address (URL) for this specific version of the schema. Both parties in an integration reference this URL to confirm they are using the same contract. |
| `version` | A human-readable version number that can be included in every message, so an auditor or support team can tell immediately which schema version was in force when a record was created. |

**In practice for your organisation:**

When your technology vendor says "we support OpenKYCAML v1.15.0," that statement is pinned to the `$id` URL above. If your vendor later upgrades to v1.16.0 without telling you, the `$id` in their messages will change — and your validator will flag the mismatch immediately rather than silently processing incompatible data.

Agreeing on a schema `$id` before go-live is the equivalent of two banks agreeing on which version of the SWIFT rulebook they are operating under.

---

## 3. Required fields — stopping silent data loss

One of the most valuable things a schema does is define which fields **must** be present. In JSON Schema this is the `required` keyword.

### 3.1 `required` — mandatory fields

```json
"required": ["messageId", "messageDateTime", "ivms101"]
```

This instruction tells any validator: if a message arrives without `messageId`, `messageDateTime`, or `ivms101`, reject it immediately.

**AML example — why this matters:**

Imagine a sanctions screening result arrives in your transaction monitoring system. It contains the screening decision and the screening provider's name — but no `screeningDate`. Without a date, the result is legally useless. You cannot prove to a regulator when the check was performed. A `required` constraint on `screeningDate` makes it impossible for an incomplete result to pass validation and enter your records.

> A validation error at the system boundary is far cheaper than a gap discovered during an audit.

### 3.2 `minLength: 1` — empty strings are as dangerous as missing fields

The `required` keyword confirms a field is present, but it does not prevent a system from sending an empty string:

```json
{ "nationalIdentifier": "" }
```

This message passes the `required` check — the field is there. But an empty national identifier is worthless. OpenKYCAML therefore applies `minLength: 1` to ten critical fields, including `nationalIdentifier`, `legalPersonName`, `customerNumber`, and `emailAddress`. A message with `""` for any of these fields will fail validation just as surely as a message with a missing field.

---

## 4. Reusable building blocks (`$defs` / `$ref`)

In a complex KYC record, the same type of sub-object appears in many places. An **address**, for example, is needed for:

- Current residential address
- Previous address
- Registered office address
- Mailing address
- Correspondence address for a related entity

Without a schema, every system defines "address" differently — different field names, different required fields, different country-code formats. With a schema, you define the address structure **once** and reuse it everywhere.

JSON Schema uses two keywords for this:

- **`$defs`** — a container in the schema where reusable definitions live.
- **`$ref`** — a pointer that says "use the definition from here."

**Example from OpenKYCAML — Address definition (simplified):**

```json
"$defs": {
  "Address": {
    "type": "object",
    "properties": {
      "addressType": { "type": "string", "enum": ["HOME", "BUSINESS", "REGISTERED", "MAILING", "CORRESPONDENCE"] },
      "streetName":  { "type": "string" },
      "townName":    { "type": "string" },
      "postCode":    { "type": "string" },
      "country":     { "type": "string" },
      "isPrimary":   { "type": "boolean" }
    },
    "required": ["addressType", "townName", "country"]
  }
}
```

Anywhere in the schema that an address is needed — for the natural person, for the legal entity, for the registered agent — the schema simply says:

```json
"geographicAddress": {
  "type": "array",
  "items": { "$ref": "#/$defs/Address" }
}
```

**Business benefit:** When a regulatory change requires a new field on all addresses (for example, adding a county or state field for US reporting), you update the `Address` definition once. Every part of the schema that references it inherits the change automatically. Compare this to updating "address" independently in dozens of separate system integrations.

---

## 5. Controlled vocabularies (`enum`, `const`)

One of the most persistent data quality problems in AML is inconsistent coding. Different systems represent the same concept with different text values:

| System | Value sent | Intended meaning |
|---|---|---|
| Onboarding | `"high"` | High risk |
| KYC Review | `"HIGH"` | High risk |
| Sanctions | `"High Risk"` | High risk |
| Transaction monitoring | `"3"` | High risk (numeric code) |

When these records are matched or aggregated, none of them align automatically. Analysts spend time reconciling values that should have been identical.

JSON Schema solves this with the **`enum`** keyword — a fixed list of allowed values. If a message contains any value not on the list, it fails validation.

**AML examples:**

Risk rating — only four values are allowed:

```json
"customerRiskRating": {
  "type": "string",
  "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
}
```

Due diligence type — three values only:

```json
"dueDiligenceType": {
  "type": "string",
  "enum": ["SDD", "CDD", "EDD"]
}
```

Gender (ISO/IEC 5218):

```json
"gender": {
  "type": "string",
  "enum": ["MALE", "FEMALE", "NON_BINARY", "OTHER", "PREFER_NOT_TO_SAY"]
}
```

**The `const` keyword** is `enum` with exactly one allowed value — used when a field must always contain a specific value, such as a schema version indicator or a protocol identifier:

```json
"nameIdentifierType": { "const": "LEGL" }
```

**Business benefit:** Every system in your ecosystem sends exactly the same codes for the same concepts. Aggregation, matching, and reporting work without translation layers. Regulators and auditors see consistent data.

---

## 6. Format rules that prevent bad data at source

Beyond controlled vocabularies, JSON Schema can enforce the **format** of string values — making it impossible for a malformed identifier or an invalid date to enter your systems.

### 6.1 `format: date` and `format: date-time` — ISO 8601 dates

Dates are one of the highest-risk fields in cross-system AML data exchange. A date of birth could legitimately be represented as:

- `"1978-11-22"` (ISO 8601 — correct)
- `"22/11/1978"` (UK format — ambiguous with US `MM/DD/YYYY`)
- `"22-Nov-78"` (abbreviated — non-standard)
- `28791` (days since 1 January 1900 — spreadsheet format)

OpenKYCAML uses `"format": "date"` on all date fields and `"format": "date-time"` on all timestamp fields. A validator will reject anything that is not a valid ISO 8601 value. This ensures:

- Audit timestamps are always unambiguous across time zones.
- Cross-border reports (FATCA, CRS, STR/SAR) contain dates that regulators and counterpart systems can parse without guesswork.
- Sanctions screening dates are comparable chronologically.

### 6.2 `format: uuid` — globally unique message identifiers

Every OpenKYCAML message has a `messageId` with `"format": "uuid"`. A UUID (Universally Unique Identifier) is a 36-character string in a specific format such as `a1b2c3d4-e5f6-7890-abcd-ef1234567890`.

This format guarantee means:

- Every message has an ID that is unique across all systems, all time, and all organisations — without any central coordination.
- Deduplication logic can rely on `messageId` without cross-checking other fields.
- An auditor can cite a specific message ID and know it refers to exactly one record, anywhere in the world.

### 6.3 `pattern` — enforcing identifier formats

For identifiers that follow a published standard format, JSON Schema uses the **`pattern`** keyword — a rule that checks the exact character-by-character structure of a string.

**LEI (Legal Entity Identifier — ISO 17442):**

A LEI is always exactly 20 alphanumeric characters. The schema enforces this:

```json
"lei": {
  "type": "string",
  "pattern": "^[0-9A-Z]{20}$"
}
```

A value like `"529900T8BM49AURSDO55"` passes. A value like `"529900-T8BM49-AURSDO55"` (with hyphens) or `"529900T8BM"` (too short) fails immediately.

**GIIN (Global Intermediary Identification Number — FATCA):**

The FATCA GIIN follows a specific structure defined by the IRS. OpenKYCAML enforces it:

```json
"giin": {
  "type": "string",
  "pattern": "^[0-9A-Z]{6}\\.[0-9A-Z]{5}\\.[0-9A-Z]{2}\\.[0-9A-Z]{3}$"
}
```

**Business benefit:** A malformed LEI or GIIN caught at the validation boundary saves an operations team from submitting an incorrect regulatory report. The cost of fixing a validation error before submission is a fraction of the cost of correcting a filed report.

---

## 7. Conditional rules (`if` / `then` / `else`)

Some data requirements depend on the value of another field. JSON Schema supports this through `if` / `then` / `else` logic — conditional rules that mirror real-world regulatory requirements.

### 7.1 Deceased customers

In OpenKYCAML, when a customer is marked as deceased (`"isDeceased": true`), the date of death becomes mandatory. This is expressed as:

> **If** `isDeceased` is `true`, **then** `deceasedDate` is required.

```json
"if":   { "properties": { "isDeceased": { "const": true } } },
"then": { "required": ["deceasedDate"] }
```

Without this rule, a system could record `"isDeceased": true` without a date — creating a record that says a customer is deceased but provides no evidence of when. With the rule, any message that marks a customer as deceased without a date fails validation at the boundary.

### 7.2 Cell company structures

A PCC (Protected Cell Company) cell must always reference its parent cell company. In OpenKYCAML:

> **If** `cellCompanyType` is `"PCC_CELL"` or `"ICC_CELL"`, **then** `parentCellCompanyReference` is required.

This prevents a cell being onboarded as a standalone entity when it should be recorded under its parent structure — a situation that can obscure beneficial ownership and create FATF Recommendation 24 compliance gaps.

### 7.3 Business value

Conditional rules embed regulatory logic directly into the data contract. They are not just documentation — they are enforceable at every system boundary. You do not need to rely on each system individually implementing the same business rule correctly. The shared schema enforces it once, for everyone.

---

## 8. Strict mode (`additionalProperties: false`)

By default, a lenient JSON Schema will accept any extra fields in a message — it simply ignores anything it does not recognise. This might seem harmless, but in AML data exchange it creates real problems:

1. **Silent data loss** — a downstream system imports the fields it knows about and quietly discards the rest, including potentially important evidence.
2. **Version confusion** — extra fields may be valid in a newer schema version; silently accepting them obscures the fact that two parties are running different versions.
3. **Injection risk** — malformed or malicious payloads can include extra fields designed to confuse downstream processing.

OpenKYCAML sets `"additionalProperties": false` at the root level (introduced in v1.15.0). This means a message containing any field not defined in the schema will fail validation immediately.

```json
{
  "nationalIdentifier": "DE-PASSPORT-C1234567",
  "nationalIdentifierType": "CCPT",
  "unofficial_note": "check this customer again"
}
```

The field `unofficial_note` is not defined in the schema. With `additionalProperties: false`, this message is rejected. The sender must either remove the non-standard field or upgrade to a schema version that formally defines it.

**Practical guidance for integration projects:**

When specifying requirements to a vendor, always ask: *"Does your system validate outgoing messages against the agreed schema before sending?"* If the answer is no, extra or malformed fields will arrive at your boundary. You should be validating incoming messages on your side regardless — but a vendor that validates outbound messages catches errors earlier and reduces operational noise.

---

## 9. Annotation fields (`_comment`, `_disclaimer`)

If you have looked at OpenKYCAML example files, you may have noticed fields like `_comment` or `_disclaimer`:

```json
{
  "_comment": "Minimal Travel Rule example — originator fields only",
  "_disclaimer": "For illustration purposes only. Not a production-valid payload.",
  "messageId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

These are **annotation fields** — human-readable notes for developers and business analysts reading the example. They are not part of the validated data. The schema allows them via `patternProperties`, which permits any field whose name starts with `_` to coexist with `additionalProperties: false`.

This design means:

- Example files can carry explanatory notes without those notes breaking schema validation of the rest of the example.
- Production messages never include `_comment` or `_disclaimer` fields — validators in the CI pipeline flag example files differently from production payload validation.
- Developers and compliance teams can annotate examples for internal documentation without forking the schema.

---

## 10. The OpenKYCAML schema in practice

Here is what the schema contract means for a typical integration project.

### Before the integration goes live

1. Both parties agree on the schema `$id` — the exact URL of the schema version to use.
2. Both parties download and run a validator (available in Python and JavaScript — see [`tools/`](../../tools/)).
3. Each party validates their test messages against the schema before connecting systems.
4. Any validation errors are resolved during the test phase, not in production.

### When a message is received

1. The receiving system's validator checks the message against the agreed schema.
2. If validation passes, the message is processed normally.
3. If validation fails, the message is rejected with a structured error describing exactly which field failed and why:

```
Validation error:
  Field: ivms101.originator.originatorPersons[0].naturalPerson.nationalIdentification.nationalIdentifier
  Error: minLength constraint violated — value is empty string
  Rule:  minLength: 1
```

The sending system receives the error, fixes the field, and resubmits. The receiving system's database never sees the invalid record.

### What this replaces

Without schema validation, the alternative is:

- A manual data quality review discovers that 3% of customer records have blank national identifiers — weeks or months after they were created.
- An audit finds that screening dates are missing for records onboarded during a specific period.
- A regulatory report is filed with inconsistent risk ratings because two systems used different coding schemes.

Schema validation at the boundary eliminates these problems systematically. It is not a substitute for good process — but it is a highly effective technical control that makes good process easier to maintain.

### OpenKYCAML versioning and audit trail

Every message includes a `version` field:

```json
{ "version": "1.15.0" }
```

This creates an audit trail. For any historical record, you can retrieve the schema version that was current when the record was created, and validate the record against that version. This is essential for:

- Demonstrating to regulators that your data met the required standard at the time of collection.
- Understanding which fields were and were not required under the schema version in force during a specific period.
- Managing schema upgrades without invalidating historical records.

---

## 11. Glossary

| Term | Plain-English definition |
|---|---|
| **Schema** | A formal, machine-readable set of rules that describes what a valid JSON message must look like — field names, types, formats, and which fields are required. |
| **Validation** | The process of checking a JSON message against a schema. A message either passes (valid) or fails with a specific error. |
| **Field** | A named piece of information in a JSON object — e.g. `dateOfBirth` or `riskRating`. Also called a "property." |
| **Property** | Another word for "field" in JSON Schema terminology. |
| **`enum`** | A constraint that limits a field to a fixed list of allowed values — e.g. `["LOW", "MEDIUM", "HIGH", "CRITICAL"]`. |
| **`pattern`** | A constraint that checks whether a string matches a specific character-by-character rule — e.g. a LEI must be exactly 20 alphanumeric characters. |
| **`format`** | A named constraint that gives a string a recognised semantic meaning — e.g. `"date"` (ISO 8601), `"email"`, `"uuid"`. |
| **`required`** | A list of fields that must be present in a message. A message missing any required field fails validation. |
| **`null`** | A JSON value meaning "this field is present but has no value." Different from an absent field or an empty string. |
| **Array** | An ordered list of values in JSON, delimited by `[ ]`. Used for multiple addresses, multiple beneficial owners, multiple screening results, etc. |
| **`$ref`** | A pointer inside a schema that says "use the definition from this location." Allows one definition to be reused in multiple places. |
| **`$defs`** | A container inside a schema where reusable definitions are stored. Referenced via `$ref`. |
| **`additionalProperties: false`** | A schema constraint that rejects any message containing fields not explicitly defined in the schema. Enforces strict data hygiene. |
| **`if` / `then` / `else`** | Conditional schema logic — certain fields become required or validated differently depending on the value of another field. |
| **`minLength: 1`** | A constraint that rejects empty strings. Ensures a field that is present actually contains a value. |

---

*Part of the OpenKYCAML documentation series. Schema: [kyc-aml-hybrid-extended.json](../../schema/kyc-aml-hybrid-extended.json) — current version v1.15.0.*

*Prerequisites: [JSON 101 for AML](json-101-for-aml.md) | Next: [Adoption Guide](adoption-guide.md)*
