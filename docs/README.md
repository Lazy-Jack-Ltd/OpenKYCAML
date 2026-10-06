# OpenKYCAML Documentation

Welcome to the OpenKYCAML documentation. This directory contains detailed technical and governance documentation for the standard, organised into sub-folders by type.

## Guides

Step-by-step integration and implementation guides.

| Document | Description |
|---|---|
| [JSON 101 for AML](guides/json-101-for-aml.md) | Plain-English introduction to JSON for compliance officers and operations managers — building blocks, AML examples, and common data-sync failure patterns |
| [JSON 102 for AML](guides/json-102-for-aml.md) | JSON Schema as a business data contract — `required`, `enum`, `format`, `pattern`, `$defs`, `if/then/else`, `additionalProperties`, and how OpenKYCAML v1.15.0 uses them |
| [Adoption Guide](guides/adoption-guide.md) | Step-by-step guide for VASPs, banks, and KYC utilities |
| [Travel Rule Implementation Guide](guides/travel-rule-implementation-guide.md) | Protocol-specific integration guide (TRISA, OpenVASP, Notabene, TRP, Sygna Bridge) |
| [EUDI Wallet Integration](guides/eudi-wallet-integration.md) | EUDIW storage profile (VC-JWT vs SD-JWT vs JSON-LD), OpenID4VCI/VP wallet API mapping, selective disclosure, trusted issuer validation, and GDPR/SAR tipping-off protection |

## Mappings

Field-level mapping documents to other standards.

| Document | Description |
|---|---|
| [Mapping: IVMS 101 / eIDAS 2.0 / AMLR](mappings/mapping-ivms101-eidas-amlr.md) | Field-level mapping across IVMS 101, eIDAS 2.0 ARF, and EU AMLR |
| [ERC-3643 (T-REX) Mapping](mappings/mapping-erc3643.md) | Field-level mapping from OpenKYCAML to ERC-3643 on-chain identity and security token standard |
| [Sovrin / Hyperledger Indy (AnonCreds) Mapping](mappings/mapping-sovrin.md) | Field-level mapping from OpenKYCAML to Sovrin DID Method, Hyperledger Indy ledger transactions, and AnonCreds ZKP credential model |
| [XRPL Credentials, DIDs, MPTs, Permissioned Domains, and Confidential Transfers Mapping](mappings/mapping-xrpl-credentials-mpt.md) | Field-level mapping from OpenKYCAML to XRPL Credentials (XLS-70), `did:xrpl` DID method, MPTs (XLS-33d), Permissioned Domains (XLS-80), Permissioned DEX (XLS-81d), Deep Freeze (XLS-77), Native Clawback, and Confidential Transfers (XLS-96) |
| [Bitcoin and Lightning Network Mapping](mappings/mapping-bitcoin-lightning.md) | Field-level mapping for Bitcoin and Lightning Network service-layer enforcement (Lightspark, Voltage, BitGo, LNURL-auth, Taproot Assets, RGB Protocol) |
| [Wolfsberg FCCQ / CBDDQ Mapping](mappings/wolfsberg-fccq-cbddq.md) | Field-level mapping from OpenKYCAML to Wolfsberg Financial Crime Compliance Questionnaire (FCCQ) and Correspondent Banking Due Diligence Questionnaire (CBDDQ) v1.4 |
| [BCBS 239 Data Governance Mapping](mappings/bcbs239.md) | OpenKYCAML field coverage for BCBS 239 data accuracy, aggregation, and reporting principles (P1–P11) |
| [FATF Recommendations 24/25 Mapping](mappings/fatf-r24-r25.md) | Beneficial ownership transparency fields — FATF Rec. 24 (corporate structures) and Rec. 25 (legal arrangements) |
| [EU AI Act Mapping](mappings/eu-ai-act.md) | PredictiveAML field coverage for EU AI Act Art. 13 transparency, explainability, and model-card requirements |
| [X.500 DN / X.400 Legacy Mapping](mappings/x500-x400-legacy.md) | X.500 Distinguished Name use-cases (eIDAS QTS, SWIFTNet, LDAP); X.400 explicitly out-of-scope rationale |
| [X.509 PKI Evidence Mapping](mappings/x509-pki.md) | Full X.509 certificate metadata, ETSI QCStatements, ASN.1 OID array — eIDAS Qualified Certificates and AMLR Art. 22/56 compliance |
| [Tax Status / TIN / OECD ESR / Pillar 2 Mapping](mappings/tax-status-oecd-esr-pillar2.md) | TIN array, VAT/GST indirect tax registrations, Economic Substance Regulations (BVI/Cayman/UAE/Jersey/IoM/Guernsey), and OECD Pillar 2 GloBE field mapping |
| [FATCA and CRS Mapping](mappings/fatca-crs.md) | US FATCA Chapter 4 (`fatcaStatus`) and OECD CRS (`crsTaxResidencies[]`) first-class field mapping |
| [Contact and Financial Identifiers Mapping](mappings/contact-financial-identifiers.md) | Format/pattern coverage for contact fields (email, phone/mobile E.164) and banking identifiers (IBAN ISO 13616, BIC ISO 9362) — v1.10.0 |
| [Cell Company Structures Mapping](mappings/cell-company.md) | PCC and ICC cell company KYC/AML support — `CellCompanyType` enum, `CellCompanyDetails`, `ParentCellCompanyReference` — Guernsey, Jersey, Cayman, Malta, Gibraltar — v1.11.0 |
| [Entity Governance Flags Mapping](mappings/entity-governance.md) | `EntityGovernance` $def — regulatory status, multi-regulator array, listed status, parent/state-ownership flags — FATF Rec. 24/25, AMLR Art. 26/48 — v1.12.0 |
| [Natural Person Governance Mapping](mappings/natural-person-governance.md) | `gender` (ISO/IEC 5218) and `occupation` (ILO/ISCO-08) fields — eIDAS PID / IVMS 101 alignment, GDPR Art. 9 guidance — v1.12.0 |

## Compliance

Regulatory compliance documents and checklists.

| Document | Description |
|---|---|
| [AMLR Requirements Reference](compliance/amlr-requirements.md) | Quick-reference mapping of EU AMLR articles to OpenKYCAML schema fields |
| [Compliance Matrix](compliance/compliance-matrix.md) | Alignment with FATF, AMLR, ISO 20022, LEI, eIDAS ARF, ERC-3643, XRPL (XLS-70/80/81/96/77), Bitcoin/Lightning |
| [AMLR 2027 Compliance Checklist](compliance/amlr-2027-compliance-checklist.md) | Operational checklist for obliged entities — schema configuration and process obligations |
| [Three-Tier Enforcement Model](compliance/enforcement-tiers.md) | Normative document defining Tier 1 (Ethereum/ERC-3643 on-chain), Tier 2 (XRPL protocol-level), and Tier 3 (Bitcoin/Lightning service-layer) compliance enforcement with field-to-tier mapping |

## Reference

API references, generated model docs, and migration guides.

| Document | Description |
|---|---|
| [TypeScript Type Definitions](reference/typescript-types.md) | TypeScript interfaces for all OpenKYCAML schema types, validator API, and usage examples |
| [Pydantic Model Documentation](reference/pydantic-models.md) | Pydantic v2 model reference (auto-generated from schema), with field tables, validators, and usage examples |
| [W3C VC Data Model Migration Guide](reference/vc-data-model-migration.md) | Migration guide from W3C VC Data Model v1.1 to v2.0 for adopters |

## Integrations

Real-world integration wiring guides and platform-specific adoption patterns.

| Document | Description |
|---|---|
| [BIPCircle / AML Gate Integration Wiring Guide](integrations/bipcircle-aml-gate-wiring.md) | Pre-meeting briefing snapshot of the BIPCircle ↔ AML Gate integration wiring — Pub/Sub event schema reconciliation, compliance gate gaps, wallet DID convention, dual-read fallback, and MLRO case auto-creation. Captures reusable OpenKYCAML adoption patterns. |

## Diagrams

Mermaid diagram sources.

| Diagram | Description |
|---|---|
| [Schema ER Diagram](diagrams/schema-er-diagram.md) | Mermaid entity-relationship diagram for the full OpenKYCAML schema |
| [Travel Rule Sequence Diagrams](diagrams/travel-rule-sequence-diagrams.md) | Mermaid sequence diagrams for TRISA, OpenVASP, Notabene, TRP, Sygna Bridge, and EUDI Wallet Travel Rule flows |
| [eIDAS 2.0 VC Issuance and Presentation Flows](diagrams/eidas-sequence-diagrams.md) | Mermaid sequence diagrams for OpenID4VCI issuance (pre-auth and auth code flows) and OpenID4VP presentation (same-device and cross-device) |
| [Tax Status Sequence Diagrams](diagrams/tax-status-diagrams.md) | Mermaid sequence diagrams for all five tax status scenarios (TIN, VAT/GST, FATCA/CRS, Pillar 2, ESR) — v1.9.1 |

## Naming Convention

The repository naming convention for all files and directories is documented in [`naming-convention.md`](naming-convention.md).

## Other

| Document | Description |
|---|---|
| [Documentation Roadmap](roadmap.md) | Documentation-specific backlog (doc updates, new guides, example additions). For the full project roadmap, see [`../ROADMAP.md`](../ROADMAP.md) |
| [ISO 20022 Integration](../iso20022-integration/README.md) | Complete ISO 20022 bridge — pacs.008/pain.001/camt.053 profiles, Python & TypeScript converters, XML examples, KYCAMLEnvelope schema |

## Schema

The canonical schema lives at [`../schema/kyc-aml-hybrid-extended.json`](../schema/kyc-aml-hybrid-extended.json).

Versioned schemas are maintained at [`../schema/versions/`](../schema/versions/).

## Examples

Ready-to-use example payloads are available in [`../examples/`](../examples/).
