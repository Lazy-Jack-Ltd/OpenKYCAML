# Compliance Overview

OpenKYCAML is designed to support compliance with major international KYC/AML
regulations and standards. This document provides a high-level overview of the
regulatory frameworks the schema aligns with.

---

## FATF Recommendations & Travel Rule

The **Financial Action Task Force (FATF)** sets international standards for
combating money laundering and terrorist financing. FATF Recommendation 16
(the "Travel Rule") requires that originator and beneficiary information
accompany virtual asset transfers.

OpenKYCAML's `travelRule` section is aligned with the
[IVMS 101](https://www.intervasp.org/) messaging standard to provide a
structured, interoperable format for Travel Rule compliance.

### Key Fields

- Originator name, account, address, date/place of birth
- Beneficiary name and account
- Originating and beneficiary VASP identification
- Transaction reference, amount, and currency

See the [IVMS 101 mapping](mappings/ivms101-mapping.md) for a detailed
field-by-field alignment.

---

## Anti-Money Laundering Directives (EU AMLD)

The EU Anti-Money Laundering Directives (currently 6AMLD) require obliged
entities to perform customer due diligence (CDD), including:

- Identification and verification of natural persons and legal entities
- Beneficial ownership identification
- Politically Exposed Person (PEP) screening
- Ongoing monitoring and risk assessment

OpenKYCAML covers these requirements through the `naturalPerson`,
`legalEntity`, and `riskAssessment` sections of the schema.

---

## eIDAS Regulation

The EU **Electronic Identification, Authentication and Trust Services (eIDAS)**
regulation provides a framework for electronic identification and trust
services. OpenKYCAML supports eIDAS-aligned identity attributes and can
be used alongside eIDAS-compliant electronic identification schemes.

See the [eIDAS mapping](mappings/eidas-basics.md) for alignment details.

---

## Verifiable Credentials (W3C)

OpenKYCAML supports wrapping KYC/AML data in
[W3C Verifiable Credentials](https://www.w3.org/TR/vc-data-model/), enabling:

- Decentralized identity interoperability
- Cryptographic proof of credential authenticity
- Selective disclosure of identity attributes
- Portable, machine-verifiable compliance data

The `verifiableCredential` section follows the W3C VC Data Model and can be
used with DID-based identity systems.

---

## Sanctions Screening

The `riskAssessment.sanctions` section supports recording results of screening
against major sanctions lists, including:

- **OFAC SDN** (US Treasury)
- **EU Sanctions List**
- **UN Sanctions List**
- **HMT** (UK)

---

## PEP Screening

Politically Exposed Person screening is supported through:

- `naturalPerson.politicallyExposedPerson` — boolean flag
- `riskAssessment.pepStatus` — structured screening results

---

## Risk-Based Approach

OpenKYCAML's `riskAssessment` section enables a risk-based approach with:

- Risk levels: `low`, `medium`, `high`, `prohibited`
- Numeric risk score (0–100)
- Assessment and review dates
- Sanctions, PEP, and adverse media screening results

This aligns with FATF's guidance on the risk-based approach to AML/CFT.

---

## Further Reading

- [FATF Recommendations](https://www.fatf-gafi.org/recommendations.html)
- [IVMS 101 Standard](https://www.intervasp.org/)
- [EU 6AMLD](https://eur-lex.europa.eu/)
- [eIDAS Regulation](https://digital-strategy.ec.europa.eu/en/policies/eidas-regulation)
- [W3C Verifiable Credentials](https://www.w3.org/TR/vc-data-model/)
