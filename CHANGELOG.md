# Changelog

All notable changes to OpenKYCAML are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

For the full project roadmap and planned features, see [ROADMAP.md](ROADMAP.md).

---

## [Unreleased]

### Fixed
- `nameIdentifier` field-name inconsistency in `docs/mapping-ivms101-eidas-amlr.md` and `docs/adoption-guide.md` (was incorrectly written as `nameIdentifiers` with a trailing 's' in several places).
- Double `originatingVASP.originatingVASP.*` field path in `docs/adoption-guide.md` minimum-required-fields table — corrected to `originatingVASP.*`.
- Example count updated from 17 to 21 in `ROADMAP.md` highlights.
- README example table now includes all four complex-ownership examples (`complex-group-multi-tier.json`, `foundation-complex-ubo.json`, `llp-complex-ubo.json`, `trust-complex-ubo.json`).
- FATF Rec. 25 compliance matrix row updated from `🟡 Partial` to `✅` reflecting existing trust/foundation/LLP example coverage; note added for planned typed sub-object extensions (v1.4.0).
- Stale SWIFT MT→MX "November 2025" migration deadline reworded to past tense in `iso20022-integration/README.md`.
- MiCA Art. 83 Travel Rule citations in compliance matrix and ISO 20022 README now correctly reference **TFR 2023/1113 Art. 14** as the primary EU operative instrument alongside MiCA.
- `docs/AMLR-requirements.md` expanded from a 23-line stub to a full quick-reference document with article-to-field mapping table, AMLA RTS status table, and links to the compliance checklist.
- Roadmap cross-references: `docs/roadmap.md` header clarified as documentation-only backlog; `ROADMAP.md` now points readers to `docs/roadmap.md` for doc-specific tasks.

### Added
- `iso20022-integration/test-suite/requirements.txt` — pinned `pytest` and `jsonschema` dependencies for the ISO 20022 test suite.
- CI workflow (`validate-schema.yml`) now triggers on changes to `iso20022-integration/**` and `docs/**` in addition to `schema/**`, `examples/**`, and `tools/**`.
- New `validate-iso20022` CI job runs the 70-test ISO 20022 pytest suite on every qualifying push and PR.
- `tools/javascript/tests/validator.test.js` — basic Node.js test suite for the JavaScript validator; fixes the broken `npm test` script.
- `schema/versions/archive/` — pre-release `v0.1*` schema drafts moved here and normalised to lowercase `.json` extensions; `README.md` added explaining their historical-only status.
- `NOTICE` — OpenID Foundation attribution added for OpenID4VP and OpenID4VCI specifications.
- `examples/sd-jwt-compact-token.json` — `_disclaimer` field added making the placeholder-signature nature of the file explicit.
- `SECURITY.md` — responsible-disclosure policy, severity classification table, and scope statement.
- `CHANGELOG.md` — this file (backfilled from v1.0.0).
- `docs/vc-data-model-migration.md` — W3C VC Data Model v1.1 → v2.0 migration guide for adopters.
- `examples/presentation-definitions/travel-rule-minimum.json` — canonical OpenID4VP Presentation Definition for FATF Rec 16 Travel Rule minimum claims.
- `tools/go/` — Go validator scaffold (`go.mod`, `validator.go`, `validator_test.go`) for TRISA-native integrations.
- `tools/javascript/openvaspConverter.js` — OpenVASP identity payload ↔ OpenKYCAML `ivms101` block converter.
- `tools/python/tests/` — pytest test suite for core Python tooling (`validator.py`, `converter.py`, `models.py`).
- `pyproject.toml` — packaging metadata enabling `pip install openkycaml`.

### Changed
- `.gitignore` — `package-lock.json` removed from ignore list to enable reproducible Node.js dependency resolution.

---

## [1.3.0] — April 2026

### Added
- **`gdprSensitivityMetadata` block** — machine-readable GDPR/AML sensitivity classification for SAR/STR tipping-off protection (AMLR Art. 73 / FATF Rec. 21), GDPR Art. 9/10 special-category and criminal-offence data, retention rules, and disclosure policies for EUDI Wallet presentation flows. Enforces non-disclosure of SAR material at both policy and cryptographic (SD-JWT) layers.
- **ISO 20022 integration module** (`iso20022-integration/`) — complete bridge layer: `<SplmtryData>` KYCAMLEnvelope JSON Schema, pacs.008 CBPR+ Travel Rule profile, pain.001 CDD reliance profile, camt.053 audit trail profile, Python + TypeScript bidirectional converters, XML examples, and 70-test pytest suite. Zero breaking changes to the core schema.
- **XRPL Credentials, DIDs, and MPTs mapping** — full field-level mapping to XLS-40d `Credential` and `DID` objects, `did:xrpl` DID method, and XLS-33d Multi-Purpose Tokens.
- Schema fields: `blockchainAccountIds[].xrplCredentialType` (hex CredentialType, XLS-40d) and `blockchainAccountIds[].mptIssuanceId` (MPTokenIssuanceID Hash192, XLS-33d).
- **ERC-3643 (T-REX) mapping** — full field-level alignment with ONCHAINID (ERC-734/735) and ERC-3643 contract interfaces. New schema fields: `kycProfile.isEligible`, `kycProfile.eligibilityLastConfirmed`, `kycProfile.blockchainAccountIds[]` (address, network, ONCHAINID address, frozen status), `kycProfile.customerClassification.accreditedInvestor`, `kycProfile.customerClassification.investorCategoryJurisdiction`.
- **Sovrin / Hyperledger Indy (AnonCreds) mapping** — full field-level alignment; new schema fields supporting `CLSignature2019`, `AnonCredsProof2023`, `AnonCredsDefinition`, `AnonCredsCredentialStatusList2023`.

---

## [1.2.0] — April 2026

### Added
- **SD-JWT selective disclosure** block (`verifiableCredential.selectiveDisclosure`) for EUDI Wallet GDPR-minimised presentations.
- **Deep UBO chain** support: `beneficialOwnership[].intermediateEntities[]` and `ownershipChainDepth` (AMLR Art. 26 full-chain disclosure).
- **AMLA RTS alignment**:
  - `kycProfile.thirdPartyCDDReliance` — structured CDD reliance record (AMLR Art. 48(3)).
  - `kycProfile.dueDiligenceRequirements` — machine-readable attribute verification record per DD tier.
  - `kycProfile.pepStatus.pepCategory` aligned to AMLA draft PEP taxonomy (AMLR Art. 28–31).
- PID/LPID converters (Python) for ARF flat-format ↔ OpenKYCAML envelope.
- Travel Rule implementation guide covering TRISA, OpenVASP, Notabene, TRP, Sygna Bridge.
- 17 validated example payloads (including SD-JWT selective disclosure, deep UBO chain, SAR-restriction variants).
- AMLR 2027 compliance checklist for obliged entities.

---

## [1.1.0] — April 2025

### Added
- **EUDI Wallet evidence block** — W3C VC `evidence` block for EUDI Wallet source credential attribution with `credentialIssuer`, `verifier`, and `presentationMethod` fields.
- **Native eIDAS 2.0 LPID** (Legal Person Identification Data) support with QEAA mandate/representative fields.
- `EUDI_WALLET` onboarding channel (AMLR Art. 22(5) high-assurance remote CDD).
- DID triangulation examples: subject wallet DID, national PID/LPID issuer DID, VASP relying-party DID.
- ISO 17442 LEI fixes.

---

## [1.0.0] — June 2024

### Added
- Initial release — IVMS 101 v1.0 payload support (backward-compatible superset).
- Optional W3C Verifiable Credential wrapper (eIDAS 2.0 / ARF-aligned).
- Full `kycProfile` section: risk rating, PEP, sanctions, adverse media, UBOs, monitoring, audit trail.
- Python and JavaScript/Node.js validators.
- CI tooling (GitHub Actions) — schema meta-validation and example payload validation.

---

[Unreleased]: https://github.com/Lazy-Jack-Ltd/openKYCAML/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/Lazy-Jack-Ltd/openKYCAML/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Lazy-Jack-Ltd/openKYCAML/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Lazy-Jack-Ltd/openKYCAML/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Lazy-Jack-Ltd/openKYCAML/releases/tag/v1.0.0
