<div align="center">

# OpenKYCAML

**The neutral, open hybrid KYC/AML data standard for the compliant digital economy.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Schema Version](https://img.shields.io/badge/schema-v1.0.0-brightgreen.svg)](schema/kyc-aml-hybrid-extended.json)
[![IVMS 101](https://img.shields.io/badge/IVMS%20101-compatible-orange.svg)](docs/mapping-ivms101-eidas-amlr.md)
[![eIDAS 2.0](https://img.shields.io/badge/eIDAS%202.0-VC%20ready-blueviolet.svg)](docs/mapping-ivms101-eidas-amlr.md)
[![AMLR 2027 Ready](https://img.shields.io/badge/AMLR%202027-ready-red.svg)](docs/compliance-matrix.md)
[![FATF Rec 16](https://img.shields.io/badge/FATF%20Rec%2016-compliant-yellow.svg)](docs/compliance-matrix.md)
[![CI](https://github.com/Lazy-Jack-Ltd/openKYCAML/actions/workflows/validate-schema.yml/badge.svg)](https://github.com/Lazy-Jack-Ltd/openKYCAML/actions/workflows/validate-schema.yml)

---

*IVMS 101 · eIDAS 2.0 Verifiable Credentials · AMLR 2027 · FATF Recommendation 16 · ISO 20022 · LEI*

</div>

---

## What is OpenKYCAML?

**OpenKYCAML** is a free, open JSON Schema standard that unifies customer KYC and AML data across institutions, VASPs, banks, and KYC utilities into a single interoperable format.

It is a **superset of IVMS 101** — the Travel Rule standard — extended with:

- 🔐 An optional **W3C Verifiable Credential (VC) wrapper** for eIDAS 2.0 / EU Digital Identity Wallet (EUDIW) attestation.
- 📊 A full **`kycProfile` section** covering every AML data point required by AMLR 2027, EBA Risk Factor Guidelines, and FATF Recommendations 10, 12, 16, and 24.

**One schema. Every compliance use case.**

---

## Why OpenKYCAML?

### The Problem

Today, every KYC platform, Travel Rule protocol, and AML system uses a different data format. The result:

- **Travel Rule** messages arrive but can't be ingested without bespoke adapters.
- **Third-party CDD reliance** under AMLR Art. 22(5) is blocked by incompatible data models.
- **Re-KYC** is performed repeatedly because KYC data can't be ported between institutions.
- **AMLR 2027** will mandate machine-readable CDD sharing — but no shared format exists yet.

### The Solution

OpenKYCAML provides the common language that turns KYC data into an interoperable, verifiable asset.

| Without OpenKYCAML | With OpenKYCAML |
|---|---|
| Custom adapters for each integration | One schema, zero adapters |
| Travel Rule data siloed per protocol | IVMS 101 superset works with any protocol |
| Re-KYC on every new relationship | Portable VC attests KYC once |
| Manual AMLR compliance gap analysis | Machine-readable compliance matrix |
| Proprietary risk scoring formats | Standardised risk fields for CDD reliance |

### Not adopting this is a competitive disadvantage

> By 2027, EU AMLR Articles 22 and 26 will require obliged entities to share CDD data in machine-readable form. VASPs that already speak OpenKYCAML will onboard new correspondents and institutional clients in minutes. Those that don't will face months of integration work — or be unable to onboard at all.

---

## Schema at a Glance

```
OpenKYCAML payload
├── ivms101                      ← IVMS 101 Travel Rule payload (backward-compatible)
│   ├── originator               ← Natural person or legal entity
│   ├── beneficiary              ← Natural person or legal entity
│   ├── originatingVASP
│   ├── beneficiaryVASP
│   └── transferredAmount        ← Asset type + amount
│
├── verifiableCredential         ← (optional) W3C VC / eIDAS 2.0 wrapper
│   ├── @context, type, issuer
│   ├── credentialSubject        ← Subject DID + KYC attestation
│   ├── credentialStatus         ← Revocation endpoint
│   └── proof                    ← Ed25519 / JWS signature
│
└── kycProfile                   ← (optional) Full KYC/AML profile
    ├── customerRiskRating        ← Overall risk, score, risk factors
    ├── customerClassification    ← RETAIL / CORPORATE / VASP / HNW / ...
    ├── dueDiligenceType          ← SDD / CDD / EDD
    ├── pepStatus                 ← PEP flag, category, role
    ├── sanctionsScreening        ← OFAC, UN, EU, HMT results
    ├── adverseMedia              ← Adverse news screening
    ├── sourceOfFundsWealth       ← SOF/SOW declarations and verification
    ├── beneficialOwnership[]     ← UBOs (AMLR Art. 26)
    ├── monitoringInfo            ← Monitoring level, alerts, review dates
    └── auditMetadata             ← Record ID, version, change log
```

---

## Quick Start

### 1. Validate a payload (Python)

```bash
pip install jsonschema
python tools/python/validator.py examples/full-kyc-profile.json
```

### 2. Validate a payload (Node.js)

```bash
cd tools/javascript && npm install
node validator.js ../../examples/full-kyc-profile.json
```

### 3. Minimal Travel Rule message

```json
{
  "$schema": "https://openkycaml.org/schema/v1.0.0/kyc-aml-hybrid-extended.json",
  "version": "1.0.0",
  "messageId": "550e8400-e29b-41d4-a716-446655440001",
  "messageDateTime": "2024-06-15T09:30:00Z",
  "ivms101": {
    "originator": {
      "originatorPersons": [{
        "naturalPerson": {
          "name": {
            "nameIdentifiers": [{
              "primaryIdentifier": "Nakamoto",
              "secondaryIdentifier": "Satoshi",
              "nameIdentifierType": "LEGL"
            }]
          },
          "nationalIdentification": {
            "nationalIdentifier": "NL-PASSPORT-AB123456",
            "nationalIdentifierType": "CCPT",
            "countryOfIssue": "NL"
          },
          "countryOfResidence": "NL"
        }
      }],
      "accountNumber": ["bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"]
    },
    "beneficiary": { "...": "..." },
    "transferredAmount": { "amount": "0.5", "assetType": "BTC" }
  }
}
```

---

## Example Payloads

| File | Description |
|---|---|
| [`natural-person-plain.json`](examples/natural-person-plain.json) | IVMS 101 Travel Rule — natural person originator |
| [`legal-entity-plain.json`](examples/legal-entity-plain.json) | IVMS 101 Travel Rule — legal entity originator |
| [`hybrid-vc-wrapped.json`](examples/hybrid-vc-wrapped.json) | IVMS 101 + eIDAS 2.0 Verifiable Credential wrapper |
| [`full-kyc-profile.json`](examples/full-kyc-profile.json) | Full KYC profile — EDD, PEP, sanctions, UBOs, monitoring |
| [`minimal-travel-rule.json`](examples/minimal-travel-rule.json) | Minimum FATF Rec 16 compliant payload |

---

## Documentation

| Document | Description |
|---|---|
| [Adoption Guide](docs/adoption-guide.md) | Step-by-step integration for VASPs, banks, KYC utilities |
| [Mapping: IVMS 101 / eIDAS / AMLR](docs/mapping-ivms101-eidas-amlr.md) | Field-level mapping across all referenced standards |
| [Compliance Matrix](docs/compliance-matrix.md) | Exact alignment with FATF, AMLR, ISO 20022, LEI, eIDAS |
| [Roadmap](ROADMAP.md) | Planned features and upcoming versions |
| [Contributing](CONTRIBUTING.md) | How to contribute to the standard |
| [Governance](GOVERNANCE.md) | Steering committee model, RFC process |

---

## Standards Alignment

| Standard | Coverage |
|---|---|
| **IVMS 101 v1.0** | ✅ Full superset — all fields supported |
| **FATF Recommendation 16** | ✅ Travel Rule compliant |
| **FATF Recommendations 10, 12, 24** | ✅ CDD, PEP, UBO fields |
| **EU AMLR 2024** | ✅ Art. 20–22, 24, 26, 28–31, 56, 83 |
| **eIDAS 2.0 / ARF** | ✅ W3C VC Data Model v2, DID, proof suites |
| **ISO 20022** | 🟡 Key fields mapped (full serialisation planned for v1.2) |
| **GLEIF / LEI** | ✅ LEIX national identifier type |
| **GDPR** | ✅ Consent record, data retention date |

---

## Repository Structure

```
openKYCAML/
├── schema/
│   ├── kyc-aml-hybrid-extended.json     ← Canonical schema (JSON Schema 2020-12)
│   └── versions/
│       └── v1.0.0.json                  ← Versioned snapshots
├── examples/                            ← Ready-to-use example payloads
├── docs/                                ← Technical and governance documentation
├── tools/
│   ├── python/                          ← Python validator, converter, Pydantic models
│   └── javascript/                      ← Node.js / Ajv validator
├── .github/workflows/                   ← CI — schema and example validation
├── LICENSE                              ← Apache 2.0
├── CONTRIBUTING.md
├── GOVERNANCE.md
├── ROADMAP.md
└── CODE_OF_CONDUCT.md
```

---

## Adopters

OpenKYCAML is designed to be adopted by:

- **Virtual Asset Service Providers (VASPs)** — for Travel Rule compliance via any protocol (TRISA, TRP, OpenVASP, Notabene).
- **Banks and payment institutions** — for third-party CDD reliance under AMLR Art. 22(5).
- **KYC utilities** — for issuing portable eIDAS 2.0 Verifiable Credentials.
- **Regulators and supervisory authorities** — as a reference data model for regulatory reporting.

**To register your organisation as an adopter**, open an issue with the label `governance: adopter`.

---

## Contributing

We welcome contributions from the community. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

For significant schema changes, start an [RFC discussion](https://github.com/Lazy-Jack-Ltd/openKYCAML/discussions) first.

---

## License

Licensed under the [Apache License 2.0](LICENSE).

This standard references IVMS 101, eIDAS 2.0 ARF, FATF Recommendations, EU AMLR, ISO 20022, and LEI standards. These remain the intellectual property of their respective owners. See [NOTICE](NOTICE) for full attribution.

---

<div align="center">

**[Schema](schema/kyc-aml-hybrid-extended.json) · [Examples](examples/) · [Docs](docs/) · [Roadmap](ROADMAP.md) · [Contributing](CONTRIBUTING.md)**

*Building the common language for compliant digital finance.*

</div>
