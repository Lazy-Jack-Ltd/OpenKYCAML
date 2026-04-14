# JSON 101 for AML: What Is JSON and Why Do Your AML Systems Use It?

**Audience:** Compliance officers, operations managers, and project leads. No coding background required.

---

## Table of Contents

1. [Why this document exists](#1-why-this-document-exists)
2. [What JSON actually is](#2-what-json-actually-is)
3. [The six building blocks — with AML examples](#3-the-six-building-blocks--with-aml-examples)
4. [Reading your first real JSON payload](#4-reading-your-first-real-json-payload)
5. [What goes wrong when systems don't agree on JSON](#5-what-goes-wrong-when-systems-dont-agree-on-json)
6. [Key takeaway: JSON is not the problem](#6-key-takeaway-json-is-not-the-problem)

---

## 1. Why this document exists

Your sanctions screening system says a customer has a registered address in London. Your onboarding platform says Frankfurt. Your transaction monitoring tool can't find the record at all. All three systems are working correctly — they just can't agree on how to describe the same customer.

This is one of the most common sources of friction in AML operations today. Data moves between systems constantly — from onboarding to KYC review, from KYC review to sanctions screening, from sanctions screening to transaction monitoring, and from all of those into regulatory reporting. Every time data crosses a system boundary, there is a risk that something is lost, misread, or rejected.

JSON is one of the technologies at the heart of how modern software systems exchange data. Understanding what it is — and where it can go wrong — will help you ask better questions of your technology vendors, understand your integration team's decisions, and spot the root cause of data quality issues before they become compliance failures.

You do not need to be a programmer to read this document.

---

## 2. What JSON actually is

**JSON** stands for **JavaScript Object Notation**. Do not be put off by the word "JavaScript" — that is simply the programming language in which it was invented in the early 2000s. JSON has nothing to do with JavaScript in practice. Every modern programming language in the world — Python, Java, C#, Go, Ruby, Scala — can read and write JSON natively.

The official definition from the IETF standard (RFC 8259) is:

> *"JSON (JavaScript Object Notation) is a lightweight data-interchange format."*

Think of it this way: when two AML systems need to share a customer record, they do not send a Word document, a PDF, or a spreadsheet. They send a JSON message — a structured, text-based description of the customer that any system on either end can read without ambiguity.

A JSON message looks like this:

```json
{
  "familyName": "Rosenberg",
  "givenName": "Clara",
  "dateOfBirth": "1978-11-22",
  "countryOfResidence": "DE",
  "riskRating": "LOW",
  "isPEP": false
}
```

That is a complete, valid JSON message. It is plain text. You can read it. A computer can read it. A different computer running different software in a different country can read it. That universality is why JSON became the dominant interchange format for APIs and data exchange across the whole software industry — including AML and KYC systems.

---

## 3. The six building blocks — with AML examples

JSON has exactly six building blocks. Everything you will ever see in a JSON message is made up of these six things and nothing else.

### 3.1 Object `{ }`

An **object** is a container, delimited by curly braces. It holds a collection of named fields — each field has a name (always in double quotes) and a value. Think of it as a form with labelled fields.

**AML example — a customer record:**

```json
{
  "familyName": "Rosenberg",
  "dateOfBirth": "1978-11-22",
  "riskRating": "LOW",
  "isPEP": false
}
```

Objects can contain other objects. A full KYC record is one large object containing smaller objects for identity, address, screening results, and so on.

---

### 3.2 Array `[ ]`

An **array** is an ordered list, delimited by square brackets. It holds zero or more items. The items can be of any type — including objects.

**AML examples:**

A list of sanctions matches:

```json
["OFAC-SDN", "EU-CONSOLIDATED", "UN-SECURITY-COUNCIL"]
```

A list of addresses for the same customer (home, mailing, previous):

```json
[
  { "addressType": "HOME",    "townName": "Munich",  "country": "DE" },
  { "addressType": "MAILING", "townName": "Munich",  "country": "DE" },
  { "addressType": "PREVIOUS","townName": "Berlin",  "country": "DE" }
]
```

A list of beneficial owners in a corporate structure:

```json
[
  { "name": "Alice Holdings Ltd", "ownershipPercentage": 51 },
  { "name": "Bob Trust",          "ownershipPercentage": 49 }
]
```

---

### 3.3 String `"text"`

A **string** is any piece of text, always wrapped in double quotes.

**AML examples:**

| Value | What it represents |
|---|---|
| `"Rosenberg"` | A customer surname |
| `"529900T8BM49AURSDO55"` | A Legal Entity Identifier (LEI) |
| `"DE89370400440532013000"` | An IBAN |
| `"CCPT"` | A code meaning "passport" (IVMS 101 standard) |
| `"2024-03-15"` | A date written as an ISO 8601 string |
| `"HIGH"` | A risk rating expressed as text |

Strings carry the bulk of the meaningful content in a KYC/AML message. Identifiers, names, codes, dates, and free-text notes are all strings.

---

### 3.4 Number

A **number** is a numeric value with no quotes. It can be an integer (whole number) or a decimal.

**AML examples:**

| Value | What it represents |
|---|---|
| `51` | Ownership percentage (51%) |
| `22` | An internal risk score |
| `2500.00` | A transfer amount |
| `3` | Number of dependants |

> **Note on dates:** Despite being a "number," a year like `2024` should **never** be stored as a raw number in AML data — it should be a string in ISO 8601 format (`"2024-03-15"`). Storing dates as numbers is one of the most common sources of interoperability failures. See [Section 5](#5-what-goes-wrong-when-systems-dont-agree-on-json).

---

### 3.5 Boolean (`true` or `false`)

A **boolean** is a yes/no flag. In JSON it is always written in lowercase: `true` or `false` — never `"true"`, `"yes"`, `1`, or `0`.

**AML examples:**

| Field | Value | Meaning |
|---|---|---|
| `"isPEP"` | `false` | Customer is not a Politically Exposed Person |
| `"isSanctioned"` | `false` | No active sanctions match |
| `"isDeceased"` | `true` | Customer is deceased |
| `"marketingOptOut"` | `true` | Customer has opted out of marketing |

> **Common mistake:** Many legacy systems send booleans as the string `"true"` or the number `1`. A strict receiving system that expects a real JSON boolean will reject or misread these values.

---

### 3.6 `null`

**`null`** means "this field exists in the schema but we do not currently have a value for it." It is not the same as zero, not the same as an empty string (`""`), and not the same as the field being absent altogether.

**AML examples:**

| Scenario | How to express it |
|---|---|
| Customer's middle name is unknown | `"middleName": null` |
| Date of death not yet confirmed | `"deceasedDate": null` |
| Tax reference not yet collected | `"taxReferenceNumber": null` |

`null` is a deliberate "we don't know yet" signal. Systems that treat `null` and missing as identical will silently discard information that may be meaningful to a downstream process.

---

### Summary table

| Building block | Symbol | AML example |
|---|---|---|
| Object | `{ }` | A customer record, a screening result |
| Array | `[ ]` | A list of sanctions lists, a list of addresses |
| String | `"text"` | A name, a LEI, an IBAN, a date |
| Number | `42` | An ownership percentage, a risk score |
| Boolean | `true` / `false` | `isPEP`, `isSanctioned`, `isActive` |
| Null | `null` | "We don't have this information yet" |

---

## 4. Reading your first real JSON payload

Below is a simplified fragment from an OpenKYCAML message. It represents a natural person undergoing onboarding. Read it top to bottom — everything you see is made from the six building blocks above.

```json
{
  "messageId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "messageDateTime": "2026-04-13T10:00:00Z",

  "ivms101": {
    "originator": {
      "originatorPersons": [
        {
          "naturalPerson": {
            "name": {
              "nameIdentifier": [
                {
                  "primaryIdentifier": "Rosenberg",
                  "secondaryIdentifier": "Clara",
                  "nameIdentifierType": "LEGL"
                }
              ]
            },
            "dateAndPlaceOfBirth": {
              "dateOfBirth": "1978-11-22",
              "placeOfBirth": "Berlin",
              "countryOfBirth": "DE"
            },
            "countryOfResidence": "DE",
            "nationalIdentification": {
              "nationalIdentifier": "DE-PASSPORT-C1234567",
              "nationalIdentifierType": "CCPT",
              "countryOfIssue": "DE"
            },
            "isPEP": false,
            "isSanctioned": false,
            "deceasedDate": null
          }
        }
      ],
      "accountNumber": ["DE89370400440532013000"]
    }
  },

  "kycProfile": {
    "customerRiskRating": "LOW",
    "dueDiligenceType": "SDD",
    "customerNumber": "CUST-DE-0012345"
  }
}
```

**Annotations:**

| What you see | Building block | What it means |
|---|---|---|
| The outer `{ … }` | **Object** | The whole message is one object |
| `"messageId": "a1b2c3d4-…"` | **String** | A unique ID for this specific message |
| `"messageDateTime": "2026-04-13T10:00:00Z"` | **String** | The date and time in ISO 8601 format |
| `"ivms101": { … }` | **Object** | The IVMS 101 identity block, itself an object |
| `"originatorPersons": [ … ]` | **Array** | A list — even if there is only one person |
| `"nameIdentifier": [ … ]` | **Array** | A list of name records (legal name, alias, etc.) |
| `"primaryIdentifier": "Rosenberg"` | **String** | The customer's family name |
| `"dateOfBirth": "1978-11-22"` | **String** | Date as ISO 8601 — not a number |
| `"isPEP": false` | **Boolean** | Not a Politically Exposed Person |
| `"deceasedDate": null` | **Null** | Field is known but value not yet available |
| `"customerRiskRating": "LOW"` | **String** | Risk rating as a controlled code |
| `"accountNumber": ["DE89370400440532013000"]` | **Array** | One IBAN, in a list (there could be more) |

Notice that `originatorPersons` is an array even though there is only one person. This is intentional — the schema is designed for a joint account or multi-party transaction. The array is always there; it just happens to have one item in this example.

---

## 5. What goes wrong when systems don't agree on JSON

JSON itself does not break. Integrations break when two systems agree to "use JSON" but each system has its own interpretation of what the fields should be called, what format values should take, or how to handle missing data.

Here are the four most common failure patterns in AML data exchange.

---

### 5.1 Field-name mismatch

System A sends:

```json
{ "dateOfBirth": "1978-11-22" }
```

System B expects:

```json
{ "dob": "1978-11-22" }
```

System C expects:

```json
{ "birth_date": "1978-11-22" }
```

None of these will successfully populate the other. System B ignores `dateOfBirth` entirely, and the customer's date of birth arrives as blank — invisible, with no error raised.

**Impact in AML:** A CDD check that requires date of birth silently passes with a blank field. The compliance record shows a completed check against an empty value.

---

### 5.2 Type mismatch — especially with dates

System A sends the date of birth as a number (days since 1 January 1900 — a common spreadsheet format):

```json
{ "dateOfBirth": 28791 }
```

System B expects an ISO 8601 string:

```json
{ "dateOfBirth": "1978-11-22" }
```

System B either throws an error, stores the number `28791` as a date, or silently ignores the field.

**Other common type mismatches:**

| What was sent | What was expected | Problem |
|---|---|---|
| `"isPEP": "true"` (string) | `"isPEP": true` (boolean) | Strict systems reject the string; lenient ones may treat it as always-true |
| `"riskScore": "22"` (string) | `"riskScore": 22` (number) | Mathematical comparisons fail on a string |
| `"active": 1` (number) | `"active": true` (boolean) | The number `1` is not a JSON boolean |

---

### 5.3 `null` versus missing field

These three messages look similar but mean different things to different systems:

```json
{ "middleName": null }         // Field present, value explicitly unknown
{ "middleName": "" }           // Field present, value is an empty string
{ }                            // Field absent entirely
```

- A **strict** system may reject `{ }` as missing a required field.
- A **lenient** system may treat all three as equivalent.
- A **database** storing the message may record `null`, `""`, and `missing` as three different states — which then causes mismatches when queried.

**Impact in AML:** If your transaction monitoring system treats a missing `taxReferenceNumber` differently from `null`, records may fail to match across systems that happen to send the field differently.

---

### 5.4 Extra or unexpected fields

System A is a modern system with an updated schema. It sends a field that System B — running an older version — does not recognise:

```json
{
  "nationalIdentifier": "DE-PASSPORT-C1234567",
  "nationalIdentifierType": "CCPT",
  "verifyingDocumentRef": "doc-001"
}
```

If System B is configured to reject messages with unrecognised fields (which is best practice for data hygiene — see JSON 102), the entire message fails. If System B silently ignores the unknown field, the document reference is lost and a manual re-entry may be required.

**Impact in AML:** Schema version mismatches between two organisations are one of the most common causes of integration failures during system upgrades.

---

## 6. Key takeaway: JSON is not the problem

JSON itself is not the source of any of the problems described above. JSON is just a format — a universal language for structuring data. The building blocks are simple, unambiguous, and understood by every system in the world.

The problems arise when two systems agree to "use JSON" without agreeing on:

- **Which fields** to include
- **What those fields should be named** (camelCase vs snake_case vs abbreviations)
- **What format values should take** (ISO 8601 dates vs epoch numbers vs DD/MM/YYYY strings)
- **Whether unknown fields are allowed or rejected**
- **What null and missing mean**

The agreement that answers all of those questions is called a **JSON Schema** — a formal, machine-readable contract that describes exactly what a valid JSON message must look like.

If both systems validate every message against the same JSON Schema before processing it, the integration failures described in this document become impossible. The schema catches them at the boundary before they can corrupt your data.

**[JSON 102: JSON Schema — the contract that keeps your AML systems in sync →](json-102-for-aml.md)**

---

*Part of the OpenKYCAML documentation series. Schema: [kyc-aml-hybrid-extended.json](../../schema/kyc-aml-hybrid-extended.json) — current version v1.15.0.*
