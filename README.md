<div align="center">

# OpenKYCAML

**The neutral, open hybrid KYC/AML data standard for the compliant digital economy.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Schema Version](https://img.shields.io/badge/schema-v1.18.0-brightgreen.svg)](schema/kyc-aml-hybrid-extended.json)
[![IVMS 101](https://img.shields.io/badge/IVMS%20101-compatible-orange.svg)](docs/mappings/mapping-ivms101-eidas-amlr.md)
[![eIDAS 2.0](https://img.shields.io/badge/eIDAS%202.0-VC%20ready-blueviolet.svg)](docs/mappings/mapping-ivms101-eidas-amlr.md)
[![AMLR 2027 Ready](https://img.shields.io/badge/AMLR%202027-ready-red.svg)](docs/compliance/compliance-matrix.md)
[![FATF Rec 16](https://img.shields.io/badge/FATF%20Rec%2016-compliant-yellow.svg)](docs/compliance/compliance-matrix.md)
[![CI](https://github.com/Lazy-Jack-Ltd/OpenKYCAML/actions/workflows/validate-examples.yml/badge.svg)](https://github.com/Lazy-Jack-Ltd/OpenKYCAML/actions/workflows/validate-examples.yml)

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

> By 2027, EU AMLR Articles 22 and 26 will require obliged entities to share CDD data in machine-readable form. FS businesses including VASPs that already speak OpenKYCAML will be able to continue to onboard new correspondents and institutional clients in minutes. Those that don't will face months of integration work — or be unable to onboard at all.

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
├── identityDocuments            ← (optional, v1.5.0+) Verification document bundle
│   ├── naturalPersonDocuments[] ← Typed docs: PASSPORT / NATIONAL_ID_CARD / EIDAS_PID_CREDENTIAL / ...
│   ├── legalEntityDocuments[]   ← Typed docs: CERTIFICATE_OF_INCORPORATION / REGISTRY_EXTRACT /
│   │                                LEI_REGISTRATION / VLEI_CREDENTIAL / TRUST_DEED / ...
│   ├── bundleCompleteness        ← COMPLETE / PARTIAL / PENDING
│   ├── bundleValidatedBy         ← Compliance officer or automated system
│   └── requiredDocumentTypes[]  ← Jurisdiction/entity-type-specific required doc list
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

legacyIdentifiers                ← (optional, v1.8.0+) X.500 DN for eIDAS QTS / SWIFTNet / LDAP
    ├── x500DN                    ← RFC 4514 Distinguished Name string (regex-validated)
    └── x500DNType                ← certificateSubject / certificateIssuer / directoryEntry / swiftNetAddress

pkiEvidence                      ← (optional, v1.8.0+) X.509 certificate evidence block
    ├── x509Certificate           ← serialNumber, subjectDN, issuerDN, validFrom/To,
    │                                signatureAlgorithm, qcStatements[], crlDistributionPoints[],
    │                                ocspResponderUrl, thumbprintSha256
    ├── oids[]                    ← ASN.1 OIDs (dotted-decimal + description + value)
    └── certificateDocumentRef   ← URI back-link to identityDocuments[]
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
  "$schema": "https://openkycaml.org/schema/v1.18.0/kyc-aml-hybrid-extended.json",
  "version": "1.18.0",
  "messageDateTime": "2024-06-15T09:30:00Z",
  "ivms101": {
    "originator": {
      "originatorPersons": [{
        "naturalPerson": {
          "name": {
            "nameIdentifier": [{
              "primaryIdentifier": "Van Dijk",
              "secondaryIdentifier": "Pieter Jan",
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
  "$schema": "https://openkycaml.org/schema/v1.18.0/kyc-aml-hybrid-extended.json",
  "version": "1.18.0",
  "verifiableCredential": {
    "issuer": { "id": "did:web:acme-crypto.example.nl", "name": "Acme Crypto Exchange BV" },
    "credentialSubject": {
      "id": "did:ebsi:zABkFm2PRPvLxNksMqJdVHK7",
      "ivms101": { "...": "..." }
    },
    "evidence": [{
      "id": "urn:uuid:pid-nl-pieter-van-dijk-2025-12-01",
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

> **Fictional data notice:** All names, passport numbers, national identifiers, addresses, entity names, LEIs, DIDs, wallet addresses, and any other personal or entity data in the example payloads are **entirely fictional** and have been created solely for illustrative purposes. Any resemblance to real persons (living or deceased), real legal entities, or real transactions is entirely coincidental. Any names that may coincidentally resemble those of real-world individuals or organisations have been deliberately altered.

There are **49 example payloads** in [`examples/`](examples/) covering the full range of scenarios — from a minimal two-party Travel Rule message to complex 4-tier ownership structures, EUDI Wallet DID triangulation, SD-JWT selective disclosure, v1.5.0 Verification Document Bundles, v1.8.0 X.509 PKI evidence, v1.9.0 taxStatus examples, v1.10.0 contact/banking, v1.11.0 PCC/ICC cell companies, v1.12.0 entity governance / review lifecycle examples, v1.13.0 CRM completeness examples, v1.14.0 schema cleanup (alias removal, `isPrimary` constraints, `EntityReference` rename), v1.15.0 schema hardening (`additionalProperties:false`, `messageType`, `minLength` enforcement), v1.16.0 company identifiers (`CompanyIdentifier` $def with 23-value enum), v1.17.0 array grouping (new structured arrays for `naturalPersonIdentifiers[]`, `riskRatingHistory[]`, `consentRecords[]` and more), and v1.18.0 W3C VC Data Model 2.0 upgrade (`validFrom`/`validUntil`, updated `@context`).

The complete catalogue with per-file descriptions, schema block inventory, and testing guidance is in **[`examples/EXAMPLES.md`](examples/EXAMPLES.md)**.

### Highlights

| Scenario | File(s) | Schema ver |
|---|---|---|
| Minimal Travel Rule (FATF baseline) | [`minimal-travel-rule.json`](examples/minimal-travel-rule.json) · [`-eudi-wallet`](examples/minimal-travel-rule-eudi-wallet.json) | 1.3.0 |
| Natural person — full EDD / PEP profile | [`full-kyc-profile.json`](examples/full-kyc-profile.json) · [`-eudi-wallet`](examples/full-kyc-profile-eudi-wallet.json) | 1.3.0 |
| Legal entity — deep 4-tier UBO chain (AMLR Art. 26) | [`legal-entity-deep-ubo.json`](examples/legal-entity-deep-ubo.json) | 1.3.0 |
| ISO 20275 trust / partnership (ELF codes) | [`legal-entity-trust.json`](examples/legal-entity-trust.json) · [`legal-entity-partnership.json`](examples/legal-entity-partnership.json) | 1.4.0 |
| Verification Document Bundle | [`document-bundle-natural-person.json`](examples/document-bundle-natural-person.json) · [`document-bundle-legal-entity.json`](examples/document-bundle-legal-entity.json) | 1.5.0 |
| SAR tipping-off protection | [`hybrid-with-sar-restriction.json`](examples/hybrid-with-sar-restriction.json) | 1.3.0 |
| eIDAS 2.0 X.509 QSealC cert (legal entity) | [`evidence/eidas-x509-dn.json`](examples/evidence/eidas-x509-dn.json) | 1.8.0 |
| eIDAS 2.0 QEAA + EUDI Wallet triangulation (natural person) | [`evidence/eidas-x509-qeaa.json`](examples/evidence/eidas-x509-qeaa.json) | 1.8.0 |

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
| [Adoption Guide](docs/guides/adoption-guide.md) | Step-by-step integration for VASPs, banks, KYC utilities |
| [JSON 101 for AML](docs/guides/json-101-for-aml.md) | Plain-English introduction to JSON for compliance officers and operations managers — building blocks, AML examples, and common data-sync failure patterns |
| [JSON 102 for AML](docs/guides/json-102-for-aml.md) | JSON Schema as a business data contract — `required`, `enum`, `format`, `pattern`, `$defs`, `if/then/else`, `additionalProperties`, and how OpenKYCAML v1.15.0 uses them |
| [ISO 20022 Integration](iso20022-integration/README.md) | Complete ISO 20022 bridge — pacs.008/pain.001/camt.053 profiles, Python & TypeScript converters, XML examples, KYCAMLEnvelope schema |
| [Mapping: IVMS 101 / eIDAS / AMLR](docs/mappings/mapping-ivms101-eidas-amlr.md) | Field-level mapping across all referenced standards |
| [Compliance Matrix](docs/compliance/compliance-matrix.md) | Exact alignment with FATF, AMLR, ISO 20022, LEI, eIDAS, ERC-3643, Sovrin |
| [AMLR 2027 Compliance Checklist](docs/compliance/amlr-2027-compliance-checklist.md) | Operational checklist for obliged entities — schema configuration and process obligations |
| [Travel Rule Implementation Guide](docs/guides/travel-rule-implementation-guide.md) | Protocol-specific integration guide (TRISA, OpenVASP, Notabene, TRP, Sygna Bridge) |
| [ERC-3643 (T-REX) Mapping](docs/mappings/mapping-erc3643.md) | Field-level mapping from OpenKYCAML to ERC-3643 on-chain permissioned token standard |
| [Sovrin / Hyperledger Indy (AnonCreds) Mapping](docs/mappings/mapping-sovrin.md) | Field-level mapping from OpenKYCAML to Sovrin DID Method, Indy ledger transactions, and AnonCreds ZKP credentials |
| [XRPL Credentials, DIDs, MPTs, Permissioned Domains, and Confidential Transfers Mapping](docs/mappings/mapping-xrpl-credentials-mpt.md) | Field-level mapping from OpenKYCAML to XRPL Credentials (XLS-70), `did:xrpl` DID method, Multi-Purpose Tokens (XLS-33d), Permissioned Domains (XLS-80), Permissioned DEX (XLS-81d), Deep Freeze (XLS-77), and Confidential Transfers (XLS-96) |
| [Bitcoin and Lightning Network Mapping](docs/mappings/mapping-bitcoin-lightning.md) | Service-layer enforcement for Bitcoin/Lightning — Lightspark, Voltage, LNURL-auth, Taproot Assets, RGB, Liquid Network |
| [Wolfsberg FCCQ / CBDDQ Mapping](docs/mappings/wolfsberg-fccq-cbddq.md) | Field-level mapping from OpenKYCAML to Wolfsberg FCCQ and CBDDQ v1.4 questionnaire fields |
| [BCBS 239 Data Governance Mapping](docs/mappings/bcbs239.md) | OpenKYCAML field coverage for BCBS 239 data accuracy, aggregation, and reporting principles |
| [FATF Recommendations 24/25 Mapping](docs/mappings/fatf-r24-r25.md) | Beneficial ownership transparency fields — FATF Rec. 24 (corporate) and Rec. 25 (arrangements) |
| [EU AI Act Mapping](docs/mappings/eu-ai-act.md) | PredictiveAML field coverage for EU AI Act Art. 13 transparency and explainability requirements |
| [X.500 DN / X.400 Legacy Mapping](docs/mappings/x500-x400-legacy.md) | X.500 Distinguished Name use-cases (eIDAS QTS, SWIFTNet, LDAP); X.400 explicitly out-of-scope rationale |
| [X.509 PKI Evidence Mapping](docs/mappings/x509-pki.md) | Full X.509 certificate metadata, ETSI QCStatements, ASN.1 OID array — eIDAS Qualified Certificates and AMLR Art. 22/56 compliance |
| [Tax Status / TIN / OECD ESR / Pillar 2 Mapping](docs/mappings/tax-status-oecd-esr-pillar2.md) | TIN array, VAT/GST registrations, Economic Substance Regulations, and OECD Pillar 2 GloBE field mapping |
| [FATCA and CRS Mapping](docs/mappings/fatca-crs.md) | US FATCA Chapter 4 (`fatcaStatus`) and OECD CRS (`crsTaxResidencies[]`) first-class field mapping |
| [Contact and Financial Identifiers Mapping](docs/mappings/contact-financial-identifiers.md) | Format/pattern coverage for contact fields (email, phone) and banking identifiers (IBAN, BIC) — v1.10.0 |
| [Cell Company Structures Mapping](docs/mappings/cell-company.md) | PCC and ICC cell company KYC/AML field mapping — `CellCompanyDetails`, `ParentCellCompanyReference` — v1.11.0 |
| [Entity Governance Flags Mapping](docs/mappings/entity-governance.md) | `EntityGovernance` $def — regulatory status, multi-regulator array, listed status, parent/ownership flags — v1.12.0 |
| [Natural Person Governance Mapping](docs/mappings/natural-person-governance.md) | `gender` and `occupation` fields — eIDAS PID / IVMS 101 alignment, GDPR Art. 9 guidance — v1.12.0 |
| [Three-Tier Enforcement Model](docs/compliance/enforcement-tiers.md) | Normative document mapping Tier 1 (Ethereum ERC-3643), Tier 2 (XRPL protocol), and Tier 3 (Bitcoin/Lightning service-layer) compliance enforcement |
| [EUDI Wallet Integration Guide](docs/guides/eudi-wallet-integration.md) | EUDIW storage profile (VC-JWT vs SD-JWT vs JSON-LD), OpenID4VCI/VP wallet API mapping, selective disclosure, trusted issuer validation, and GDPR/SAR tipping-off protection |
| [W3C VC Data Model Migration Guide](docs/reference/vc-data-model-migration.md) | Migration reference for upgrading VC payloads from W3C VC DM v1.1 (≤ v1.17.0) to VC DM 2.0 (v1.18.0+) |
| [BIPCircle / AML Gate Integration Wiring Guide](docs/integrations/bipcircle-aml-gate-wiring.md) | Integration wiring briefing capturing reusable adoption patterns: Pub/Sub event schema, wallet DID convention, dual-read fallback, and MLRO case auto-creation |
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
| **FATF Recommendations 24/25 (2022 revision)** | ✅ v1.7.0 — `beneficialOwnership[].nomineeFlags` (isNominee, nominatorIdentified, bearerShareFlag), `roleInArrangement`, `trustInstrumentReference` — see [FATF R.24/25 mapping](docs/mappings/fatf-r24-r25.md) |
| **EU AMLR 2024** | ✅ Art. 20–22, 24, 26, 28–31, 56, 73, 83; verification document bundle (Art. 22 & 26, v1.5.0); document ID URN scheme (Art. 56, v1.6.0); entity governance flags including `regulatoryStatus`, `regulators[]`, `listedStatus`, `stateOwned` (Art. 22/26/48, v1.12.0) |
| **eIDAS 2.0 / ARF** | ✅ W3C VC Data Model v2, DID, Ed25519 proof suites, LPID, QEAA mandates |
| **EU Digital Identity Wallet (EUDIW)** | ✅ PID + LPID credential flows via OpenID4VP; W3C VC evidence block; EUDI_WALLET onboarding channel; `gdprSensitivityMetadata` for tipping-off-safe EUDIW presentations (v1.3.0) |
| **ISO 20022** | ✅ v1.3.0 — SupplementaryData envelope, pacs.008/pain.001/camt.053 profiles, Python & TypeScript converters (bidirectional) — see [`iso20022-integration/`](iso20022-integration/) |
| **GLEIF / LEI** | ✅ LEIX national identifier type; ISO 17442 check digit validation; GLEIF RAL `RegistrationAuthorityDetail` (v1.5.0); `LegalEntityDocument` with `gleifRegistrationAuthority`, `elfCodeVerified`, and `vLEICredentialType` (QVI/OOR/ECR) |
| **ISO 17442 / vLEI** | ✅ v1.5.0 — LEI field, GLEIF RAL structured reference, vLEI Verifiable Credential support (QVI → OOR → ECR hierarchy), `LEI_REGISTRATION` and `VLEI_CREDENTIAL` document types |
| **GDPR** | ✅ Consent record, data retention date, EUDI Wallet SD-JWT selective disclosure; `gdprSensitivityMetadata` block for SAR/tipping-off protection (Art. 9/10 special categories and criminal-offence data, AMLR Art. 73) — added v1.3.0 |
| **ERC-3643 (T-REX)** | ✅ ONCHAINID, eligibility flag, wallet addresses, frozen tokens, accredited investor claim — see [ERC-3643 mapping](docs/mappings/mapping-erc3643.md) |
| **Sovrin / Hyperledger Indy (AnonCreds)** | ✅ `did:sov` / `did:indy` DIDs, AnonCreds CL credentials, CLAIM_DEF, REVOC_REG, Rich Schema — see [Sovrin mapping](docs/mappings/mapping-sovrin.md) |
| **XRPL Credentials (XLS-70), DIDs (`did:xrpl`), MPTs (XLS-33d), Permissioned Domains (XLS-80/81d), Confidential Transfers (XLS-96), Deep Freeze (XLS-77)** | ✅ On-ledger `Credential` anchoring W3C VCs (XLS-70, live on mainnet), `did:xrpl` DID method, MPT permissioned tokens, Permissioned Domain + DEX gating (v1.7.0), EC-ElGamal Confidential Transfers with selective disclosure (v1.7.0), Deep Freeze (v1.7.0), Native Clawback (v1.7.0) — see [XRPL mapping](docs/mappings/mapping-xrpl-credentials-mpt.md) |
| **Bitcoin / Lightning Network** | ✅ v1.7.0 — service-layer enforcement; Lightning node pubkey (`lightningNodePubkey`), LSP identification (`lightningServiceProvider`), Bitcoin script type (`bitcoinScriptType`); Lightspark/Voltage/BitGo compliance wrapper integration — see [Bitcoin/Lightning mapping](docs/mappings/mapping-bitcoin-lightning.md) |
| **Wolfsberg FCCQ / CBDDQ** | ✅ v1.7.0 — field-level mapping to Wolfsberg Financial Crime Compliance Questionnaire and Correspondent Banking Due Diligence Questionnaire v1.4; CBDDQ importer tool — see [Wolfsberg mapping](docs/mappings/wolfsberg-fccq-cbddq.md) |
| **BCBS 239** | ✅ v1.7.0 — `dataAggregationMetadata` (P1–P6 accuracy/completeness), `predictiveAML.explainability` (P8 model transparency) — see [BCBS 239 mapping](docs/mappings/bcbs239.md) |
| **EU AI Act (Art. 13 / Annex IV)** | ✅ v1.7.0 — `predictiveAML.modelMetadata` (Art. 13 model card), `explainability` (SHAP/LIME/counterfactual), EU AI Act conformity statement — see [EU AI Act mapping](docs/mappings/eu-ai-act.md) |
| **X.500 Distinguished Names / X.509 PKI** | ✅ v1.8.0 — optional `legacyIdentifiers.x500DN` (RFC 4514, regex-validated) for eIDAS QTS certificate Subject/Issuer, SWIFTNet addressing, and LDAP entries; optional `pkiEvidence` block with X.509 metadata (serial number, validity, signature algorithm, ETSI QCStatements[], CRL/OCSP, SHA-256 thumbprint) and OID array — see [X.500/X.400 mapping](docs/mappings/x500-x400-legacy.md) and [X.509 PKI mapping](docs/mappings/x509-pki.md) |
| **Tax Status / TIN / OECD CRS (crsTaxResidencies) / FATCA (GIIN + Chapter 4) / ESR / Pillar 2 GloBE** | ✅ v1.9.1 — optional `taxStatus` block: `tinIdentifiers[]` (OECD CRS/CARF TIN array, multi-jurisdiction, replaces IVMS 101 TXID), `indirectTaxRegistrations[]` (VAT/GST/PST/HST with VIES/GST-portal verification), `economicSubstance` (ESR status for BVI/Cayman/UAE/Jersey/Guernsey/IoM — `nonCompliant` triggers EDD+SAR warning), `pillarTwo` (GloBE ETR per jurisdiction, GIR reference, safe-harbour election) — see [Tax Status mapping](docs/mappings/tax-status-oecd-esr-pillar2.md) |
| **Contact and Financial Identifiers** | ✅ v1.10.0 — RFC 5321 email, E.164 phone/mobile, ISO 13616 IBAN, ISO 9362 BIC — validated as optional fields on both `NaturalPerson` and `LegalPerson`; account type classification — see [Contact/Financial mapping](docs/mappings/contact-financial-identifiers.md) |
| **Cell Company Structures (PCC / ICC)** | ✅ v1.11.0 — Protected Cell Companies and Incorporated Cell Companies in Guernsey, Jersey, Cayman, Malta, and Gibraltar; `CellCompanyType` enum, `CellCompanyDetails`, `ParentCellCompanyReference`; hard schema constraints (v1.11.1) — see [Cell Company mapping](docs/mappings/cell-company.md) |
| **Entity Governance / Review Lifecycle / Natural Person Completeness** | ✅ v1.12.0 — `EntityGovernance` $def (`regulatoryStatus`, `regulators[]`, `listedStatus`, `parentCompany`, `stateOwned`, `governmentOwnershipPercentage`); `ReviewLifecycle` state machine (AMLR Art. 21 audit trail); `NaturalPerson.gender` (ISO/IEC 5218) and `occupation` (ILO/ISCO-08) — see [Entity Governance mapping](docs/mappings/entity-governance.md) and [Natural Person Governance mapping](docs/mappings/natural-person-governance.md) |
| **CRM Completeness — 20 field gaps closed** | ✅ v1.13.0 — 6 new $defs (`EmailAddress`, `EmergencyContact`, `IndustryCode`, `Mandate`, `PhoneNumber`, `RegisteredAgent`); typed contact arrays, historical names, marital status, deceased flag, preferred language/channel, emergency contact, incorporation/dissolution dates, operational status, employee count, revenue, website, social media, industry codes, registered agent, GLEIF ultimate parent/group, relationship manager, customer segment, net worth, structured mandates — see §24 in compliance matrix |
| **Schema Cleanup — Alias removal and `isPrimary` constraints** | ✅ v1.14.0 — removed 8 deprecated alias fields (`isPep`, `lastPepCheckDate`, `SanctionsScreening.status`, `lastScreenedDate`, `AdverseMedia.lastCheckedDate`, `AuditMetadata.timestamp`, `lastKycReviewDate`, `BeneficialOwner.naturalPerson`); removed 5 legacy contact strings (`emailAddress`/`phoneNumber`/`mobileNumber` from `NaturalPerson`/`LegalPerson`); removed `KYCProfile.sourceOfFundsWealth` string array; renamed `ParentCellCompanyReference` → `EntityReference`; added `isPrimary` `maxContains:1` constraints on 6 arrays |
| **Schema Hardening — Strict mode and mandatory field validation** | ✅ v1.15.0 — `additionalProperties: false` at root level; optional `messageType` root property; `minLength: 1` enforced on 10 critical fields (`primaryIdentifier`, `nationalIdentifier`, `customerIdentification`, `legalPersonName`, `currentLegalName`, `uniqueIdentifier`, `taxReferenceNumber`, `customerNumber`, `emailAddress`, `phoneNumber`); root `examples` array; `NaturalPerson` allOf `deceasedDate` conditional (required when `isDeceased: true`); `uniqueItems: true` on `NaturalPerson`/`LegalPerson`/`KYCProfile` `tags[]` |
| **Company Identifiers — Structured legal entity identifier types** | ✅ v1.16.0 — new `CompanyIdentifier` $def with 23-value `identifierType` enum (DUNS, LEI, CRN_GB, SIREN_FR, SIRET_FR, HRB_DE, HRA_DE, CNPJ_BR, ABN_AU, ACN_AU, EIN_US, CIK_US, CAGE_US, PIC_EU, BVDID, ISIN, BIC, CHARITY_GB, KVK_NL, UID_AT, NIF_ES, RCS_LU, OTHER); `identifierIssuingBody` required when type = OTHER; `LegalPerson.companyIdentifiers[]` added; see §25 in compliance matrix |
| **Array Grouping — Extended structured arrays** | ✅ v1.17.0 — 4 new $defs (`PersonIdentifier` 17-value enum, `RiskRatingEntry`, `RevenueRecord`, `ConsentRecord`); 12 new optional additive array properties: `NaturalPerson.naturalPersonIdentifiers[]`, `countriesOfResidence[]`, `nationalities[]`, `occupations[]`, `emergencyContacts[]`; `LegalPerson.legalNationalIdentifiers[]`, `revenueHistory[]`, `registeredAgents[]`; `KYCProfile.pepStatuses[]`, `riskRatingHistory[]`, `consentRecords[]`; `EntityGovernance.parentCompanies[]`; see §26 in compliance matrix |
| **W3C VC Data Model 2.0** | ✅ v1.18.0 — `VerifiableCredentialWrapper` upgraded from W3C VC DM v1.1 to VC DM 2.0 (W3C Recommendation, May 2024); `@context[0]` const changed to `https://www.w3.org/ns/credentials/v2`; `issuanceDate` renamed to `validFrom` (required); `expirationDate` renamed to `validUntil` (optional); all 23 VC-bearing examples updated; all "planned for v2.0.0" deferral notes removed; see [VC Data Model Migration Guide](docs/reference/vc-data-model-migration.md) |

---

## Repository Structure

```
openKYCAML/
├── schema/
│   ├── kyc-aml-hybrid-extended.json     ← Canonical schema (latest — currently v1.18.0)
│   └── versions/
│       ├── v1.0.0.json                  ← v1.0.0 snapshot
│       ├── v1.1.0.json                  ← v1.1.0 snapshot
│       ├── v1.2.0.json                  ← v1.2.0 snapshot
│       ├── v1.3.0.json                  ← v1.3.0 snapshot
│       ├── v1.5.0.json                  ← v1.5.0 snapshot (Verification Document Bundle)
│       ├── v1.6.0.json                  ← v1.6.0 snapshot (Document ID URN scheme)
│       ├── v1.7.0.json                  ← v1.7.0 snapshot (XRPL XLS-70/80/81/96/77, Bitcoin/Lightning)
│       ├── v1.8.0.json                  ← v1.8.0 snapshot (X.500 DN, X.509 PKI evidence)
│       ├── v1.9.0.json                  ← v1.9.0 snapshot (taxStatus: TIN/ESR/Pillar 2)
│       ├── v1.9.1.json                  ← v1.9.1 snapshot (FATCA/CRS: crsTaxResidencies, fatcaStatus)
│       ├── v1.10.0.json                 ← v1.10.0 snapshot (contact details, banking identifiers)
│       ├── v1.11.0.json                 ← v1.11.0 snapshot (PCC/ICC cell company structures)
│       ├── v1.11.1.json                 ← v1.11.1 snapshot (hard if/then constraints for cell companies)
│       ├── v1.11.2.json                 ← v1.11.2 snapshot (cell-level predictive AML scores)
│       ├── v1.12.0.json                 ← v1.12.0 snapshot (gender, occupation, EntityGovernance, ReviewLifecycle)
│       ├── v1.13.0.json                 ← v1.13.0 snapshot (CRM completeness: 20 field gaps, 6 new $defs)
│       ├── v1.14.0.json                 ← v1.14.0 snapshot (alias removal, isPrimary constraints, EntityReference rename)
│       ├── v1.15.0.json                 ← v1.15.0 snapshot (additionalProperties:false, messageType, minLength enforcement)
│       ├── v1.16.0.json                 ← v1.16.0 snapshot (CompanyIdentifier $def, 23-value enum, companyIdentifiers[])
│       ├── v1.17.0.json                 ← v1.17.0 snapshot (PersonIdentifier, RiskRatingEntry, ConsentRecord, RevenueRecord; 12 new array fields)
│       └── v1.18.0.json                 ← v1.18.0 snapshot (current — W3C VC DM 2.0: validFrom/validUntil, updated @context)
├── examples/
│   ├── *-plain.json                     ← Plain IVMS 101 baseline examples
│   ├── *-wrapped.json                   ← VC-wrapped examples
│   ├── *-eudi-wallet.json               ← EUDI Wallet / DID triangulation examples
│   ├── document-bundle-*.json           ← Verification document bundle examples (v1.5.0)
│   ├── evidence/                        ← X.509 PKI evidence examples (v1.8.0)
│   ├── tax/                             ← Tax status examples (v1.9.0)
│   ├── contact-banking/                 ← Contact/banking identifier examples (v1.10.0)
│   ├── cell-company/                    ← PCC/ICC cell company examples (v1.11.0)
│   ├── predictive/                      ← PredictiveAML / EU AI Act examples (v1.7.0)
│   ├── company-identifiers.json         ← CompanyIdentifier $def examples (v1.16.0)
│   ├── array-grouping-*.json            ← Array-grouping field examples (v1.17.0)
│   └── presentation-definitions/        ← OpenID4VP presentation definitions
├── iso20022-integration/                ← ISO 20022 bridge module (v1.3.0+)
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

