# OpenKYCAML Roadmap

This document outlines the planned development of the OpenKYCAML standard.

---

## Current Version: v1.2.0

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
- **15 validated example payloads** (including SD-JWT selective disclosure and deep UBO chain variants).
- AMLR 2027 compliance checklist for obliged entities.
- **ERC-3643 (T-REX) mapping** — full field-level alignment with ONCHAINID (ERC-734/735) and ERC-3643 contract interfaces. New schema fields: `kycProfile.isEligible`, `kycProfile.eligibilityLastConfirmed`, `kycProfile.blockchainAccountIds[]` (address, network, ONCHAINID address, frozen status), `kycProfile.customerClassification.accreditedInvestor`, `kycProfile.customerClassification.investorCategoryJurisdiction`.
- **Sovrin / Hyperledger Indy (AnonCreds) mapping** — full field-level alignment with `did:sov` / `did:indy` DID Method, Indy NYM/ATTRIB/SCHEMA/CLAIM_DEF/REVOC_REG_DEF ledger transactions, AnonCreds ZKP credential and presentation protocol, and Rich Schema objects. New schema fields: `verifiableCredential.credentialSchema.credDefId`, `credentialSchema.type` extended to include `AnonCredsDefinition`, `credentialStatus.type` extended with `AnonCredsCredentialStatusList2023`, `proof.type` examples extended with `CLSignature2019` and `AnonCredsProof2023`.

---

## v1.3.0 — Planned Q3 2026

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
| SAR/STR flag field (`kycProfile.sarFiled`) | Planned | — |
| FATCA / CRS tax residency extension | Planned | — |
| ISO 20022 pain.001 full serialiser (Python) | Planned | — |

---

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

---

## How to Influence the Roadmap

1. Open an issue with the label `type: enhancement` or `type: rfc`.
2. Join the [GitHub Discussions](https://github.com/Lazy-Jack-Ltd/openKYCAML/discussions).
3. Attend TWG calls (schedule posted in Discussions).
4. See [GOVERNANCE.md](GOVERNANCE.md) for the formal decision process.

