# IVMS 101 Mapping

This document maps OpenKYCAML schema fields to the
[InterVASP Messaging Standard (IVMS 101)](https://www.intervasp.org/)
data model, which is used for FATF Travel Rule compliance in virtual asset
transfers.

---

## Overview

IVMS 101 defines a standardized message format for transmitting originator and
beneficiary information between Virtual Asset Service Providers (VASPs). The
OpenKYCAML `travelRule` section is designed to align with IVMS 101 data
elements.

---

## Field Mapping

### Originator / Beneficiary

| IVMS 101 Field | OpenKYCAML Field | Notes |
|----------------|------------------|-------|
| `originator.originatorPersons[].naturalPerson.name` | `travelRule.originator.name` | Combined name field. |
| `originator.accountNumber` | `travelRule.originator.accountNumber` | Wallet address or account. |
| `originator.originatorPersons[].naturalPerson.geographicAddress` | `travelRule.originator.address` | Mapped to Address type. |
| `originator.originatorPersons[].naturalPerson.dateAndPlaceOfBirth.dateOfBirth` | `travelRule.originator.dateOfBirth` | ISO 8601 date. |
| `originator.originatorPersons[].naturalPerson.dateAndPlaceOfBirth.placeOfBirth` | `travelRule.originator.placeOfBirth` | |
| `originator.originatorPersons[].naturalPerson.nationalIdentification` | `travelRule.originator.nationalIdentification` | |
| `beneficiary.beneficiaryPersons[].naturalPerson.name` | `travelRule.beneficiary.name` | |
| `beneficiary.accountNumber` | `travelRule.beneficiary.accountNumber` | |

### VASP Identification

| IVMS 101 Field | OpenKYCAML Field | Notes |
|----------------|------------------|-------|
| `originatingVASP.originatingVASP.legalPerson.name` | `travelRule.originatingVASP.name` | |
| `originatingVASP.originatingVASP.legalPerson.legalPersonIdentifier` (LEI) | `travelRule.originatingVASP.leiCode` | 20-char LEI. |
| `originatingVASP.originatingVASP.legalPerson.countryOfRegistration` | `travelRule.originatingVASP.registrationCountry` | ISO 3166-1 alpha-2. |
| `beneficiaryVASP.beneficiaryVASP.legalPerson.name` | `travelRule.beneficiaryVASP.name` | |
| `beneficiaryVASP.beneficiaryVASP.legalPerson.legalPersonIdentifier` (LEI) | `travelRule.beneficiaryVASP.leiCode` | |

### Transaction Data

| IVMS 101 Field | OpenKYCAML Field | Notes |
|----------------|------------------|-------|
| `transactionIdentifier` | `travelRule.transactionReference` | Unique TX ID. |
| `transferAmount.amount` | `travelRule.transferAmount.amount` | Numeric string. |
| `transferAmount.currency` | `travelRule.transferAmount.currency` | ISO 4217 or asset code. |
| `transferDate` | `travelRule.transferDate` | ISO 8601 date-time. |

---

## Notes

- IVMS 101 supports both natural and legal persons as originators/beneficiaries.
  OpenKYCAML currently uses a simplified party model with a `name` string field.
- IVMS 101 name structures (primary, secondary, local) are flattened in
  OpenKYCAML to a single `name` field in the travel rule party.
- For full IVMS 101 compliance, integrators may extend the party model with
  additional name components.

---

## References

- [IVMS 101 Specification](https://www.intervasp.org/)
- [FATF Recommendation 16](https://www.fatf-gafi.org/recommendations.html)
- [OpenKYCAML Schema Reference](../schema-reference.md)
