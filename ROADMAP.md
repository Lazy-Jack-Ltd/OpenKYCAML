# OpenKYCAML Roadmap

This document outlines the planned development of the OpenKYCAML standard.

---

## Current Version: v1.3.0

**Released:** April 2026

**Highlights:**
- Full IVMS 101 v1.0 payload support (backward-compatible superset).
- Optional W3C Verifiable Credential wrapper (eIDAS 2.0 / ARF-aligned), with W3C VC `evidence` block for EUDI Wallet source credential attribution.
- Native **eIDAS 2.0 LPID** (Legal Person Identification Data) support with QEAA mandate/representative fields.
- `EUDI_WALLET` onboarding channel (AMLR Art. 22(5) high-assurance remote CDD).
- Full `kycProfile` section: risk rating, PEP, sanctions, adverse media, UBOs, monitoring, audit trail.
- **SD-JWT selective disclosure** block (`verifiableCredential.selectiveDisclosure`) for EUDI Wallet GDPR-minimised presentations.
- **Deep UBO chain** support: `beneficialOwnership[].intermediateEntities[]` and `ownershipChainDepth` (AMLR Art. 26 full-chain disclosure).
- **AMLA RTS alignment (v1.2.0)**:
  - `kycProfile.thirdPartyCDDReliance` — structured CDD reliance record (AMLR Art. 48(3)).
  - `kycProfile.dueDiligenceRequirements` — machine-readable attribute verification record per DD tier (AMLR Art. 22, pending AMLA RTS on CDD attribute sets).
  - `kycProfile.pepStatus.pepCategory` aligned to AMLA draft PEP taxonomy (AMLR Art. 28–31).
- PID/LPID converters (Python) for ARF flat-format ↔ OpenKYCAML envelope.
- Travel Rule implementation guide covering TRISA, OpenVASP, Notabene, TRP, Sygna Bridge.
- **17 validated example payloads** (including SD-JWT selective disclosure, deep UBO chain, and SAR-restriction variants).
- AMLR 2027 compliance checklist for obliged entities.
- **ERC-3643 (T-REX) mapping** — full field-level alignment with ONCHAINID (ERC-734/735) and ERC-3643 contract interfaces. New schema fields: `kycProfile.isEligible`, `kycProfile.eligibilityLastConfirmed`, `kycProfile.blockchainAccountIds[]` (address, network, ONCHAINID address, frozen status), `kycProfile.customerClassification.accreditedInvestor`, `kycProfile.customerClassification.investorCategoryJurisdiction`.
- **Sovrin / Hyperledger Indy (AnonCreds) mapping** — full field-level alignment with `did:sov` / `did:indy` DID Method, Indy NYM/ATTRIB/SCHEMA/CLAIM_DEF/REVOC_REG_DEF ledger transactions, AnonCreds ZKP credential and presentation protocol, and Rich Schema objects. New schema fields: `verifiableCredential.credentialSchema.credDefId`, `credentialSchema.type` extended to include `AnonCredsDefinition`, `credentialStatus.type` extended with `AnonCredsCredentialStatusList2023`, `proof.type` examples extended with `CLSignature2019` and `AnonCredsProof2023`.
- **`gdprSensitivityMetadata` block (v1.3.0)**: machine-readable GDPR/AML sensitivity classification for SAR/STR tipping-off protection (AMLR Art. 73 / FATF Rec. 21), GDPR Art. 9/10 special-category and criminal-offence data, retention rules, and disclosure policies for EUDI Wallet presentation flows. Enforces non-disclosure of SAR material at both policy and cryptographic (SD-JWT) layers.
- **ISO 20022 integration module** — complete bridge layer in [`iso20022-integration/`](iso20022-integration/): `<SplmtryData>` KYCAMLEnvelope JSON Schema, pacs.008 CBPR+ Travel Rule profile, pain.001 CDD reliance profile, camt.053 audit trail profile, Python + TypeScript bidirectional converters, XML examples, and 70-test pytest suite. Zero breaking changes to the core schema.

---

## v1.4.0 — Planned Q3 2026

**Theme: Institutional and Cross-Border Interoperability**

| Feature | Status | Issue |
|---|---|---|
| TypeScript type definitions (auto-generated from schema) | Planned | — |
| Pydantic v2 models (auto-generated from schema) | Planned | — |
| IBAN / crypto account number format validation | Planned | — |
| Trust registry endpoint field (`kycProfile.trustRegistryUrl`) | Planned | — |
| Trust framework field (`verifiableCredential.trustFramework`) | Planned | — |
| Go validator | Planned | — |
| OpenID4VP presentation request / response cookbook | Planned | — |
| Correspondent banking extension fields | Planned | — |
| Multi-jurisdiction risk model fields | Planned | — |
| FATCA / CRS tax residency extension | Planned | — |
| ISO 20022 pain.001 full serialiser (Python) | ✅ Completed in v1.3.0 | — |
| XRPL schema fields: `blockchainAccountIds[].xrplCredentialType` (hex CredentialType) and `blockchainAccountIds[].mptIssuanceId` (MPTokenIssuanceID) | ✅ Completed in v1.3.0 | — |

---

## v1.3.0 — ISO 20022 Integration (Complete)

| Feature | Status |
|---|---|
| ISO 20022 `<SplmtryData>` KYCAMLEnvelope schema | ✅ Complete |
| pacs.008 CBPR+ Travel Rule profile | ✅ Complete |
| pain.001 third-party CDD reliance profile | ✅ Complete |
| camt.053 audit trail / data-retention profile | ✅ Complete |
| Python converter (`openkycaml_to_pacs008`, `openkycaml_to_pain001`, `iso20022_to_openkycaml`) | ✅ Complete |
| TypeScript ESM converter (same three functions) | ✅ Complete |
| XML examples (pacs.008, pain.001, minimal snippet) | ✅ Complete |
| Bidirectional field mapping YAML (OpenKYCAML ↔ ISO 20022) | ✅ Complete |
| Field-level gap analysis (narrative + tables) | ✅ Complete |
| pytest test suite — round-trip + schema validation (70 tests) | ✅ Complete |

See [`iso20022-integration/`](iso20022-integration/) for all artefacts.

## v2.0.0 — Planned 2027

**Theme: AMLR 2027 Full Applicability Alignment**

This major version will be timed to align with the EU AMLR full applicability date (1 July 2027), giving adopters a 2-year migration window.

Planned breaking changes (subject to TWG consensus):
- Remove deprecated IVMS 101 fields no longer required by updated standards.
- Require `kycProfile.auditMetadata` for all CDD records (currently optional).
- Align `verifiableCredential` structure with final W3C VC Data Model v2.0 spec and final eIDAS 2.0 ARF (expected publication 2025–2026).
- Full EUDI Wallet interoperability profile targeting EU AMLR Art. 22 and Art. 26.

---

## Completed

| Version | Date | Highlights |
|---|---|---|
| v1.0.0 | June 2024 | Initial release — IVMS 101 superset, kycProfile, VC wrapper, CI tooling |
| v1.1.0 | April 2025 | EUDI Wallet evidence block, LPID + QEAA mandates, DID triangulation examples, `EUDI_WALLET` onboarding channel, ISO 17442 LEI fixes |
| v1.2.0 | April 2026 | SD-JWT selective disclosure, deep UBO chain, PID/LPID converters, Travel Rule guide, AMLA RTS alignment (`thirdPartyCDDReliance`, `dueDiligenceRequirements`, AMLA PEP taxonomy), AMLR 2027 compliance checklist |
| v1.3.0 | April 2026 | `gdprSensitivityMetadata` block — SAR/STR tipping-off protection (AMLR Art. 73 / FATF Rec. 21), GDPR Art. 9/10 classification, EUDI Wallet restricted-data handling, SAR-restriction example, updated compliance docs. **ISO 20022 integration** — complete `<SplmtryData>` KYCAMLEnvelope, pacs.008/pain.001/camt.053 profiles, Python + TypeScript bidirectional converters, XML examples, 70-test test suite. **XRPL Credentials, DIDs, and MPTs mapping** — full field-level mapping to XLS-40d `Credential` and `DID` objects, `did:xrpl` DID method, and XLS-33d Multi-Purpose Tokens. **XRPL schema extensions** — `blockchainAccountIds[].xrplCredentialType` (hex CredentialType, XLS-40d) and `blockchainAccountIds[].mptIssuanceId` (MPTokenIssuanceID Hash192, XLS-33d) added to `kycProfile`; see [mapping-xrpl-credentials-mpt.md](docs/mapping-xrpl-credentials-mpt.md) |

---

## How to Influence the Roadmap

1. Open an issue with the label `type: enhancement` or `type: rfc`.
2. Join the [GitHub Discussions](https://github.com/Lazy-Jack-Ltd/openKYCAML/discussions).
3. Attend TWG calls (schedule posted in Discussions).
4. See [GOVERNANCE.md](GOVERNANCE.md) for the formal decision process.

