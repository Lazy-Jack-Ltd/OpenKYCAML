<div align="center">

# OpenKYCAML

**The neutral, open hybrid KYC/AML data standard for the compliant digital economy.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Schema Version](https://img.shields.io/badge/schema-v1.3.0-brightgreen.svg)](schema/kyc-aml-hybrid-extended.json)
[![IVMS 101](https://img.shields.io/badge/IVMS%20101-compatible-orange.svg)](docs/mapping-ivms101-eidas-amlr.md)
[![eIDAS 2.0](https://img.shields.io/badge/eIDAS%202.0-VC%20ready-blueviolet.svg)](docs/mapping-ivms101-eidas-amlr.md)
[![AMLR 2027 Ready](https://img.shields.io/badge/AMLR%202027-ready-red.svg)](docs/compliance-matrix.md)
[![FATF Rec 16](https://img.shields.io/badge/FATF%20Rec%2016-compliant-yellow.svg)](docs/compliance-matrix.md)
[![CI](https://github.com/Lazy-Jack-Ltd/openKYCAML/actions/workflows/validate-schema.yml/badge.svg)](https://github.com/Lazy-Jack-Ltd/openKYCAML/actions/workflows/validate-schema.yml)

---

*IVMS 101 · eIDAS 2.0 Verifiable Credentials · EU Digital Identity Wallet · AMLR 2027 · FATF Recommendation 16 · ISO 20022 · LEI*

</div>

---

## What is OpenKYCAML?

**OpenKYCAML** is a free, open JSON Schema standard that unifies customer KYC and AML data across institutions, VASPs, banks, and KYC utilities into a single interoperable format.

It is a **superset of IVMS 101** — the Travel Rule standard — extended with:

- 🔐 An optional **W3C Verifiable Credential (VC) wrapper** for eIDAS 2.0 / EU Digital Identity Wallet (EUDIW) attestation, including a W3C VC `evidence` block that records the source PID/LPID credential presented from a user's data wallet.
- 🪪 Native **eIDAS 2.0 LPID** (Legal Person Identification Data) support with QEAA mandate/representative fields — enabling direct EUDI Wallet flows for legal entities.
- 📊 A full **`kycProfile` section** covering every AML data point required by AMLR 2027, EBA Risk Factor Guidelines, and FATF Recommendations 10, 12, 16, and 24.
- 🔗 **DID triangulation** — every EUDI Wallet example captures the three-party trust chain: subject wallet DID, national PID/LPID issuer DID, and VASP relying-party DID.

**One schema. Every compliance use case.**

---

## Why OpenKYCAML?

### The Problem

Today, every KYC platform, Travel Rule protocol, and AML system uses a different data format. The result:

- **Travel Rule** messages arrive but can't be ingested without bespoke adapters.
- **Third-party CDD reliance** under AMLR Art. 22(5) is blocked by incompatible data models.
- **Re-KYC** is performed repeatedly because KYC data can't be ported between institutions.
- **AMLR 2027** will mandate machine-readable CDD sharing — but no shared format exists yet.
- **EUDI Wallet** holders have no standard format for presenting PID/LPID data to VASPs and banks.

### The Solution

OpenKYCAML provides the common language that turns KYC data into an interoperable, verifiable asset.

| Without OpenKYCAML | With OpenKYCAML |
|---|---|
| Custom adapters for each integration | One schema, zero adapters |
| Travel Rule data siloed per protocol | IVMS 101 superset works with any protocol |
| Re-KYC on every new relationship | Portable VC attests KYC once |
| Manual AMLR compliance gap analysis | Machine-readable compliance matrix |
| Proprietary risk scoring formats | Standardised risk fields for CDD reliance |
| EUDI Wallet data stranded in national silos | LPID + PID → IVMS 101 mapping built-in |

### Not adopting this is a competitive disadvantage

> By 2027, EU AMLR Articles 22 and 26 will require obliged entities to share CDD data in machine-readable form. VASPs that already speak OpenKYCAML will onboard new correspondents and institutional clients in minutes. Those that don't will face months of integration work — or be unable to onboard at all.

---

## Schema at a Glance

```
OpenKYCAML payload
├── ivms101                      ← IVMS 101 Travel Rule payload (backward-compatible)
│   ├── originator               ← Natural person or legal entity (+ optional LPID block)
│   ├── beneficiary              ← Natural person or legal entity
│   ├── originatingVASP          ← LEI + DID-addressable identifier
│   ├── beneficiaryVASP
│   └── transferredAmount        ← Asset type + amount
│
├── verifiableCredential         ← (optional) W3C VC / eIDAS 2.0 wrapper
│   ├── @context, type, issuer   ← DID of issuing VASP or KYC utility
│   ├── credentialSubject        ← Subject DID (EUDI Wallet) + IVMS 101 + kycProfile + lpid
│   ├── credentialSchema         ← JSON Schema (JsonSchemaValidator2018) or AnonCreds (AnonCredsDefinition + credDefId)
│   ├── evidence[]               ← Source PID/LPID credential: issuer DID, presentationMethod,
│   │                                presentationDate — triangulates the identity chain
│   ├── credentialStatus         ← Revocation endpoint (StatusList2021 / AnonCredsCredentialStatusList2023)
│   ├── selectiveDisclosure      ← SD-JWT selective disclosure metadata (EUDI Wallet / GDPR minimisation)
│   └── proof                    ← Ed25519Signature2020 / JWS / CLSignature2019 / AnonCredsProof2023
│
├── kycProfile                   ← (optional) Full KYC/AML profile
│   ├── customerRiskRating        ← Overall risk, score, risk factors
│   ├── customerClassification    ← RETAIL / CORPORATE / VASP / HNW / ... + accreditedInvestor
│   ├── dueDiligenceType          ← SDD / CDD / EDD
│   ├── pepStatus                 ← PEP flag, category, role
│   ├── sanctionsScreening        ← OFAC, UN, EU, HMT results
│   ├── adverseMedia              ← Adverse news screening
│   ├── sourceOfFundsWealth       ← SOF/SOW declarations and verification
│   ├── beneficialOwnership[]     ← UBOs (AMLR Art. 26) + deep intermediate entity chain
│   ├── onboardingChannel         ← IN_PERSON / REMOTE_VIDEO / EUDI_WALLET / ...
│   ├── isEligible                ← ERC-3643 eligibility flag (IIdentityRegistry.isVerified)
│   ├── eligibilityLastConfirmed  ← Date eligibility was last confirmed on-chain
│   ├── blockchainAccountIds[]    ← On-chain wallet addresses (ONCHAINID, network, frozen status)
│   ├── monitoringInfo            ← Monitoring level, alerts, review dates
│   └── auditMetadata             ← Record ID, version, change log
│
└── gdprSensitivityMetadata      ← (optional, v1.3.0+) GDPR/AML sensitivity classification
    ├── classification            ← standard / sensitive_personal / criminal_offence /
    │                                sar_restricted / internal_suspicion / confidential_aml
    ├── restrictedFields[]        ← JSON Pointers to individual restricted fields
    ├── tippingOffProtected       ← AMLR Art. 73 / FATF Rec. 21 SAR non-disclosure flag
    ├── legalBasis                ← GDPR Art. 6/9/10 or AMLR Art. 55/73 code
    ├── retentionPeriod           ← ISO 8601 duration (e.g. "P5Y")
    ├── consentRecord             ← Consent given/withdrawn (for consent-based processing)
    ├── disclosurePolicy          ← allowedRecipients / prohibitedRecipients
    └── auditReference            ← Opaque DPO/SAR case reference (hash only, no content)
```

---

## ISO 20022 Integration

OpenKYCAML v1.3.0 ships a complete ISO 20022 bridge layer, enabling any adopter to embed the full KYC/AML dataset inside standard `pacs.008`, `pain.001`, and `camt.053` messages using the ISO-approved `<SplmtryData>` extension point — no schema modifications, no breaking changes.

See [`iso20022-integration/`](iso20022-integration/) for the full module: bidirectional field mapping, JSON Schema envelope, three pre-validated profiles, XML examples, and Python + TypeScript converters.

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
  "$schema": "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
  "version": "1.3.0",
  "messageId": "550e8400-e29b-41d4-a716-446655440001",
  "messageDateTime": "2024-06-15T09:30:00Z",
  "ivms101": {
    "originator": {
      "originatorPersons": [{
        "naturalPerson": {
          "name": {
            "nameIdentifier": [{
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
    "originatingVASP": { "name": "Acme Crypto Exchange BV", "lei": "724500VNNHZHYDLFMO70" },
    "beneficiaryVASP": { "...": "..." },
    "transferredAmount": { "amount": "0.5", "assetType": "BTC" }
  }
}
```

### 4. EUDI Wallet / DID Triangulation — minimal example

```json
{
  "$schema": "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
  "version": "1.3.0",
  "verifiableCredential": {
    "issuer": { "id": "did:web:acme-crypto.example.nl", "name": "Acme Crypto Exchange BV" },
    "credentialSubject": {
      "id": "did:ebsi:zABkFm2PRPvLxNksMqJdVHK7",
      "ivms101": { "...": "..." }
    },
    "evidence": [{
      "id": "urn:uuid:pid-nl-satoshi-nakamoto-2025-12-01",
      "type": ["PIDCredential", "EUDIWalletPresentationEvidence"],
      "credentialIssuer": "did:web:pid-provider.rvo.example.nl",
      "verifier": "did:web:acme-crypto.example.nl",
      "presentationMethod": "OpenID4VP",
      "presentationDate": "2025-12-01T10:27:00Z"
    }],
    "proof": { "type": "Ed25519Signature2020", "...": "..." }
  }
}
```

---

## Example Payloads

Every scenario is available in two forms: a **plain IVMS 101** baseline and an **EUDI Wallet VC-wrapped** companion that demonstrates DID triangulation (subject wallet DID · PID/LPID issuer DID · VASP DID). SD-JWT selective disclosure variants are provided for the natural person and legal entity scenarios.

| Scenario | Plain baseline | EUDI Wallet / DID version |
|---|---|---|
| Natural person Travel Rule | [`natural-person-plain.json`](examples/natural-person-plain.json) | [`natural-person-eudi-wallet.json`](examples/natural-person-eudi-wallet.json) |
| Natural person — SD-JWT selective disclosure | — | [`natural-person-sd-jwt-eudi-wallet.json`](examples/natural-person-sd-jwt-eudi-wallet.json) |
| Legal entity Travel Rule | [`legal-entity-plain.json`](examples/legal-entity-plain.json) | [`legal-entity-eudi-wallet.json`](examples/legal-entity-eudi-wallet.json) |
| Legal entity — SD-JWT selective disclosure | — | [`legal-entity-sd-jwt-eudi-wallet.json`](examples/legal-entity-sd-jwt-eudi-wallet.json) |
| Legal entity — Deep UBO chain (AMLR Art. 26) | [`legal-entity-deep-ubo.json`](examples/legal-entity-deep-ubo.json) | — |
| Hybrid VC-wrapped (IVMS 101 + kycProfile) | [`hybrid-vc-wrapped.json`](examples/hybrid-vc-wrapped.json) | [`hybrid-vc-eudi-wallet.json`](examples/hybrid-vc-eudi-wallet.json) |
| Full KYC profile (EDD, PEP, UBOs) | [`full-kyc-profile.json`](examples/full-kyc-profile.json) | [`full-kyc-profile-eudi-wallet.json`](examples/full-kyc-profile-eudi-wallet.json) |
| Minimal Travel Rule | [`minimal-travel-rule.json`](examples/minimal-travel-rule.json) | [`minimal-travel-rule-eudi-wallet.json`](examples/minimal-travel-rule-eudi-wallet.json) |
| Travel Rule VC-wrapped | [`travel-rule-vc-wrapped.json`](examples/travel-rule-vc-wrapped.json) | [`travel-rule-vc-eudi-wallet.json`](examples/travel-rule-vc-eudi-wallet.json) |
| SAR-restricted VC — tipping-off protection (v1.3.0) | [`hybrid-with-sar-restriction.json`](examples/hybrid-with-sar-restriction.json) | — |

### EUDI Wallet examples — DID triangulation

Each `-eudi-wallet.json` example documents a **trust chain** using W3C VC evidence blocks:

| Role | DID example | Purpose |
|---|---|---|
| **Subject wallet** | `did:ebsi:z2LSzT7LiUNMxKKyGCnNjNT` | User's EU Digital Identity Wallet |
| **PID/LPID issuer** | `did:web:pid-provider.bsi.example.de` | National PID Provider (e.g. German BSI) |
| **VASP / relying party** | `did:web:acme-crypto.example.nl` | Receiving institution |
| **Beneficiary VASP** | `did:web:fintech-exchange.example.gb` | Travel Rule counterpart |

---

## Documentation

| Document | Description |
|---|---|
| [Adoption Guide](docs/adoption-guide.md) | Step-by-step integration for VASPs, banks, KYC utilities |
| [ISO 20022 Integration](iso20022-integration/README.md) | Complete ISO 20022 bridge — pacs.008/pain.001/camt.053 profiles, Python & TypeScript converters, XML examples, KYCAMLEnvelope schema |
| [Mapping: IVMS 101 / eIDAS / AMLR](docs/mapping-ivms101-eidas-amlr.md) | Field-level mapping across all referenced standards |
| [Compliance Matrix](docs/compliance-matrix.md) | Exact alignment with FATF, AMLR, ISO 20022, LEI, eIDAS, ERC-3643, Sovrin |
| [AMLR 2027 Compliance Checklist](docs/amlr-2027-compliance-checklist.md) | Operational checklist for obliged entities — schema configuration and process obligations |
| [Travel Rule Implementation Guide](docs/travel-rule-implementation-guide.md) | Protocol-specific integration guide (TRISA, OpenVASP, Notabene, TRP, Sygna Bridge) |
| [ERC-3643 (T-REX) Mapping](docs/mapping-erc3643.md) | Field-level mapping from OpenKYCAML to ERC-3643 on-chain permissioned token standard |
| [Sovrin / Hyperledger Indy (AnonCreds) Mapping](docs/mapping-sovrin.md) | Field-level mapping from OpenKYCAML to Sovrin DID Method, Indy ledger transactions, and AnonCreds ZKP credentials |
| [XRPL Credentials, DIDs, and MPTs Mapping](docs/mapping-xrpl-credentials-mpt.md) | Field-level mapping from OpenKYCAML to XRPL Credentials (XLS-40d), `did:xrpl` DID method, and Multi-Purpose Tokens (XLS-33d) for on-ledger KYC/AML gating and regulated asset compliance |
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
| **eIDAS 2.0 / ARF** | ✅ W3C VC Data Model v2, DID, Ed25519 proof suites, LPID, QEAA mandates |
| **EU Digital Identity Wallet (EUDIW)** | ✅ PID + LPID credential flows via OpenID4VP; W3C VC evidence block; EUDI_WALLET onboarding channel; `gdprSensitivityMetadata` for tipping-off-safe EUDIW presentations (v1.3.0) |
| **ISO 20022** | ✅ v1.3.0 — SupplementaryData envelope, pacs.008/pain.001/camt.053 profiles, Python & TypeScript converters (bidirectional) — see [`iso20022-integration/`](iso20022-integration/) |
| **GLEIF / LEI** | ✅ LEIX national identifier type; ISO 17442 check digit validation |
| **GDPR** | ✅ Consent record, data retention date, EUDI Wallet SD-JWT selective disclosure; `gdprSensitivityMetadata` block for SAR/tipping-off protection (Art. 9/10 special categories and criminal-offence data, AMLR Art. 73) — added v1.3.0 |
| **ERC-3643 (T-REX)** | ✅ ONCHAINID, eligibility flag, wallet addresses, frozen tokens, accredited investor claim — see [ERC-3643 mapping](docs/mapping-erc3643.md) |
| **Sovrin / Hyperledger Indy (AnonCreds)** | ✅ `did:sov` / `did:indy` DIDs, AnonCreds CL credentials, CLAIM_DEF, REVOC_REG, Rich Schema — see [Sovrin mapping](docs/mapping-sovrin.md) |
| **XRPL Credentials (XLS-40d), DIDs (`did:xrpl`), and MPTs (XLS-33d)** | ✅ On-ledger `Credential` object anchoring W3C VCs, `did:xrpl` DID method, MPT permissioned tokens with `lsfMPTRequireAuth` / `lsfMPTAuthorized` KYC/AML gating, `DepositPreauth` credential gates — see [XRPL mapping](docs/mapping-xrpl-credentials-mpt.md) |

---

## Repository Structure

```
openKYCAML/
├── schema/
│   ├── kyc-aml-hybrid-extended.json     ← Canonical schema (latest — currently v1.3.0)
│   └── versions/
│       ├── v1.0.0.json                  ← v1.0.0 snapshot
│       ├── v1.1.0.json                  ← v1.1.0 snapshot
│       ├── v1.2.0.json                  ← v1.2.0 snapshot
│       └── v1.3.0.json                  ← v1.3.0 snapshot (current)
├── examples/
│   ├── *-plain.json                     ← Plain IVMS 101 baseline examples
│   ├── *-wrapped.json                   ← VC-wrapped examples
│   └── *-eudi-wallet.json               ← EUDI Wallet / DID triangulation examples
├── iso20022-integration/                ← ISO 20022 bridge module (v1.3.0)
│   ├── mapping/                         ← Bidirectional field mapping YAML + gap analysis
│   ├── supplementary-data/              ← KYCAMLEnvelope JSON Schema + reference instance
│   ├── profiles/                        ← pacs.008 / pain.001 / camt.053 profiles
│   ├── examples/                        ← pacs.008 / pain.001 XML examples
│   ├── libraries/python/                ← Python converter (3 functions)
│   ├── libraries/typescript/            ← TypeScript ESM converter
│   └── test-suite/                      ← pytest round-trip + schema validation tests
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
- **EU Digital Identity Wallet providers** — for PID/LPID → IVMS 101 bridging and CDD attestation.
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

