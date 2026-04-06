# OpenKYCAML Documentation

Welcome to the OpenKYCAML documentation. This directory contains detailed technical and governance documentation for the standard, organised into sub-folders by type.

## Guides

Step-by-step integration and implementation guides.

| Document | Description |
|---|---|
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
| [XRPL Credentials, DIDs, and MPTs Mapping](mappings/mapping-xrpl-credentials-mpt.md) | Field-level mapping from OpenKYCAML to XRPL Credentials (XLS-40d), `did:xrpl` DID method, and Multi-Purpose Tokens (XLS-33d) |

## Compliance

Regulatory compliance documents and checklists.

| Document | Description |
|---|---|
| [AMLR Requirements Reference](compliance/amlr-requirements.md) | Quick-reference mapping of EU AMLR articles to OpenKYCAML schema fields |
| [Compliance Matrix](compliance/compliance-matrix.md) | Alignment with FATF, AMLR, ISO 20022, LEI, eIDAS ARF |
| [AMLR 2027 Compliance Checklist](compliance/amlr-2027-compliance-checklist.md) | Operational checklist for obliged entities — schema configuration and process obligations |

## Reference

API references, generated model docs, and migration guides.

| Document | Description |
|---|---|
| [TypeScript Type Definitions](reference/typescript-types.md) | TypeScript interfaces for all OpenKYCAML schema types, validator API, and usage examples |
| [Pydantic Model Documentation](reference/pydantic-models.md) | Pydantic v2 model reference (auto-generated from schema), with field tables, validators, and usage examples |
| [W3C VC Data Model Migration Guide](reference/vc-data-model-migration.md) | Migration guide from W3C VC Data Model v1.1 to v2.0 for adopters |

## Diagrams

Mermaid diagram sources.

| Diagram | Description |
|---|---|
| [Schema ER Diagram](diagrams/schema-er-diagram.md) | Mermaid entity-relationship diagram for the full OpenKYCAML schema |
| [Travel Rule Sequence Diagrams](diagrams/travel-rule-sequence-diagrams.md) | Mermaid sequence diagrams for TRISA, OpenVASP, Notabene, TRP, Sygna Bridge, and EUDI Wallet Travel Rule flows |
| [eIDAS 2.0 VC Issuance and Presentation Flows](diagrams/eidas-sequence-diagrams.md) | Mermaid sequence diagrams for OpenID4VCI issuance (pre-auth and auth code flows) and OpenID4VP presentation (same-device and cross-device) |

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
