# OpenKYCAML Documentation

Welcome to the OpenKYCAML documentation. This directory contains detailed technical and governance documentation for the standard.

## Documents

| Document | Description |
|---|---|
| [EUDI Wallet Integration](eudi-wallet-integration.md) | EUDIW storage profile (VC-JWT vs SD-JWT vs JSON-LD), OpenID4VCI/VP wallet API mapping, selective disclosure, trusted issuer validation, and GDPR/SAR tipping-off protection |
| [Mapping: IVMS 101 / eIDAS 2.0 / AMLR](mapping-ivms101-eidas-amlr.md) | Field-level mapping across IVMS 101, eIDAS 2.0 ARF, and EU AMLR |
| [Adoption Guide](adoption-guide.md) | Step-by-step guide for VASPs, banks, and KYC utilities |
| [Compliance Matrix](compliance-matrix.md) | Alignment with FATF, AMLR, ISO 20022, LEI, eIDAS ARF |
| [AMLR 2027 Compliance Checklist](amlr-2027-compliance-checklist.md) | Operational checklist for obliged entities — schema configuration and process obligations |
| [ERC-3643 (T-REX) Mapping](mapping-erc3643.md) | Field-level mapping from OpenKYCAML to ERC-3643 on-chain identity and security token standard |
| [Sovrin / Hyperledger Indy (AnonCreds) Mapping](mapping-sovrin.md) | Field-level mapping from OpenKYCAML to Sovrin DID Method, Hyperledger Indy ledger transactions, and AnonCreds ZKP credential model |
| [Travel Rule Implementation Guide](travel-rule-implementation-guide.md) | Protocol-specific integration guide (TRISA, OpenVASP, Notabene, TRP, Sygna Bridge) |
| [ISO 20022 Integration](../iso20022-integration/README.md) | Complete ISO 20022 bridge — pacs.008/pain.001/camt.053 profiles, Python & TypeScript converters, XML examples, KYCAMLEnvelope schema |
| [Roadmap](roadmap.md) | Planned features, community milestones, and version history |

## Schema

The canonical schema lives at [`../schema/kyc-aml-hybrid-extended.json`](../schema/kyc-aml-hybrid-extended.json).

Versioned schemas are maintained at [`../schema/versions/`](../schema/versions/).

## Examples

Ready-to-use example payloads are available in [`../examples/`](../examples/).
