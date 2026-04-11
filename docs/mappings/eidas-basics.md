# eIDAS Basics Mapping

This document describes how OpenKYCAML schema fields relate to identity
attributes defined under the EU **Electronic Identification, Authentication
and Trust Services (eIDAS)** regulation.

---

## Overview

eIDAS establishes a framework for cross-border electronic identification
within the EU. It defines a minimum dataset (MDS) of identity attributes
that member states must support for natural persons and legal entities.

OpenKYCAML covers these core attributes, making it suitable for use alongside
eIDAS-compliant identification schemes.

---

## Natural Person — Minimum Dataset

| eIDAS Attribute | OpenKYCAML Field | Notes |
|-----------------|------------------|-------|
| Current family name(s) | `naturalPerson.name.lastName` | |
| Current first name(s) | `naturalPerson.name.firstName` | |
| Date of birth | `naturalPerson.dateOfBirth` | ISO 8601. |
| Unique identifier | `naturalPerson.identificationDocuments[].documentNumber` | Mapped via national ID document. |

### Optional eIDAS Attributes

| eIDAS Attribute | OpenKYCAML Field | Notes |
|-----------------|------------------|-------|
| Place of birth | `naturalPerson.placeOfBirth` | |
| Current address | `naturalPerson.address` | Mapped to Address type. |
| Gender | — | Not currently in schema. |

---

## Legal Person — Minimum Dataset

| eIDAS Attribute | OpenKYCAML Field | Notes |
|-----------------|------------------|-------|
| Current legal name | `legalEntity.legalName` | |
| Unique identifier | `legalEntity.registrationNumber` or `legalEntity.leiCode` | LEI preferred where available. |

### Optional eIDAS Attributes

| eIDAS Attribute | OpenKYCAML Field | Notes |
|-----------------|------------------|-------|
| Current address | `legalEntity.registeredAddress` | |
| VAT registration number | — | Not currently in schema; can be added as extension. |
| Tax reference number | — | Not currently in schema. |
| LEI | `legalEntity.leiCode` | 20-character LEI. |

---

## Levels of Assurance

eIDAS defines three levels of assurance (LoA) for electronic identification:

| Level | Description | OpenKYCAML Relevance |
|-------|-------------|---------------------|
| **Low** | Basic identity confidence | Minimal profile (name + DOB). |
| **Substantial** | Moderate identity confidence | Profile with ID documents. |
| **High** | High identity confidence | Profile with verified ID documents + VC proof. |

OpenKYCAML's Verifiable Credential wrapper (`verifiableCredential`) supports
high-assurance scenarios by providing cryptographic proof of identity
verification.

---

## Integration Notes

- eIDAS identifiers are typically issued by national eID schemes. Map these
  to `identificationDocuments` with `documentType: "national_id"`.
- For cross-border scenarios, combine eIDAS electronic identification with
  OpenKYCAML's Travel Rule section for comprehensive compliance coverage.
- The `verifiableCredential` section can carry eIDAS-compliant identity
  assertions when issued by a qualified trust service provider.

---

## References

- [eIDAS Regulation (EU 910/2014)](https://digital-strategy.ec.europa.eu/en/policies/eidas-regulation)
- [eIDAS Minimum Dataset](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/eIDAS+eID+Profile)
- [OpenKYCAML Schema Reference](../schema-reference.md)
