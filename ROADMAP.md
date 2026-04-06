# OpenKYCAML Roadmap

This document is the **authoritative project roadmap** covering schema features, tooling releases, CI infrastructure, and technical debt.

> **Looking for documentation-specific tasks?** See [`docs/roadmap.md`](docs/roadmap.md) for the documentation-only backlog (new guides, example additions, doc updates).

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
- **21 validated example payloads** (including SD-JWT selective disclosure, deep UBO chain, and SAR-restriction variants).
- AMLR 2027 compliance checklist for obliged entities.
- **ERC-3643 (T-REX) mapping** — full field-level alignment with ONCHAINID (ERC-734/735) and ERC-3643 contract interfaces. New schema fields: `kycProfile.isEligible`, `kycProfile.eligibilityLastConfirmed`, `kycProfile.blockchainAccountIds[]` (address, network, ONCHAINID address, frozen status), `kycProfile.customerClassification.accreditedInvestor`, `kycProfile.customerClassification.investorCategoryJurisdiction`.
- **Sovrin / Hyperledger Indy (AnonCreds) mapping** — full field-level alignment with `did:sov` / `did:indy` DID Method, Indy NYM/ATTRIB/SCHEMA/CLAIM_DEF/REVOC_REG_DEF ledger transactions, AnonCreds ZKP credential and presentation protocol, and Rich Schema objects. New schema fields: `verifiableCredential.credentialSchema.credDefId`, `credentialSchema.type` extended to include `AnonCredsDefinition`, `credentialStatus.type` extended with `AnonCredsCredentialStatusList2023`, `proof.type` examples extended with `CLSignature2019` and `AnonCredsProof2023`.
- **`gdprSensitivityMetadata` block (v1.3.0)**: machine-readable GDPR/AML sensitivity classification for SAR/STR tipping-off protection (AMLR Art. 73 / FATF Rec. 21), GDPR Art. 9/10 special-category and criminal-offence data, retention rules, and disclosure policies for EUDI Wallet presentation flows. Enforces non-disclosure of SAR material at both policy and cryptographic (SD-JWT) layers.
- **ISO 20022 integration module** — complete bridge layer in [`iso20022-integration/`](iso20022-integration/): `<SplmtryData>` KYCAMLEnvelope JSON Schema, pacs.008 CBPR+ Travel Rule profile, pain.001 CDD reliance profile, camt.053 audit trail profile, Python + TypeScript bidirectional converters, XML examples, and 70-test pytest suite. Zero breaking changes to the core schema.

---

## Issues & Technical Debt — Found in April 2026 Repository Review

The following issues were identified during a critical review of the full repository in April 2026. They are grouped by priority and type. All are candidates for the v1.3.x patch stream or v1.4.0 depending on severity.

---

### 🔴 Bugs / Documentation Inaccuracies (Fix in v1.3.x)

| # | Issue | Location | Notes |
|---|---|---|---|
| 1 | **`nameIdentifier` vs `nameIdentifiers` field-name inconsistency** | `docs/mapping-ivms101-eidas-amlr.md`, `docs/adoption-guide.md` | The schema and all examples use `nameIdentifier` (no trailing 's'); several documentation files use `nameIdentifiers` with an 's'. Adopters implementing from docs will generate invalid payloads. |
| 2 | **Double-nested `originatingVASP.originatingVASP.*` field path** | `docs/adoption-guide.md` line 58 | The minimum-required-fields table writes `originatingVASP.originatingVASP.name.nameIdentifiers[0].legalPersonName` — the doubled `originatingVASP` prefix is wrong and will confuse integrators. |
| 3 | **Stale example count** | `ROADMAP.md` (v1.3.0 Highlights) | States "17 validated example payloads" but there are now 21 example JSON files in `examples/`. Needs updating everywhere it is cited. |
| 4 | **README example table incomplete** | `README.md` | The example table does not list the four complex-ownership examples added later: `complex-group-multi-tier.json`, `foundation-complex-ubo.json`, `llp-complex-ubo.json`, `trust-complex-ubo.json`. |
| 5 | **FATF Rec. 25 compliance matrix status outdated** | `docs/compliance-matrix.md` | Still shows `🟡 Partial` and "specific trust-deed fields planned for v1.1" — but `trust-complex-ubo.json`, `foundation-complex-ubo.json`, and `llp-complex-ubo.json` already demonstrate full trust/foundation/LLP beneficial-ownership coverage. Matrix should be updated to `✅` with a note on what is and isn't covered by `kycProfile.beneficialOwnership`. |
| 6 | **SWIFT MT→MX migration deadline is now past** | `iso20022-integration/README.md` line 128 | States "Mandatory for SWIFT MT→MX migration (November 2025)" — this deadline has passed (current date: April 2026). Reword to past tense or remove the deadline. |
| 7 | **W3C VC `@context` hard-coded to v1 URL despite v2 alignment claims** | `schema/versions/v1.3.0.json` line 692 | Schema's `verifiableCredential.@context[0]` has `const: "https://www.w3.org/2018/credentials/v1"` (W3C VC DM **v1** context), but the README, schema description, and docs all claim alignment with **W3C VC Data Model v2** (`https://www.w3.org/ns/credentials/v2`). Either migrate examples and schema to the v2 context URL, or explicitly document which version of the VC DM is supported and why v1 context is retained. |
| 8 | **MiCA Art. 83 cited as the Travel Rule provision** | `docs/compliance-matrix.md`, `iso20022-integration/README.md` | The EU Travel Rule for crypto-asset transfers is primarily in the **EU Funds Transfer Regulation (TFR) 2023/1113** (Art. 14), not directly in MiCA. MiCA cross-references TFR but TFR is the operative instrument. The compliance matrix should reference TFR 2023/1113 Art. 14 alongside MiCA to be accurate. |
| 9 | **`docs/AMLR-requirements.md` is a 23-line stub** | `docs/AMLR-requirements.md` | Contains only an introductory table without the full content expected of a requirements document. Should be expanded or clearly marked as a summary/pointer to the compliance checklist. |

---

### 🟠 CI / Infrastructure Gaps (Fix in v1.3.x / v1.4.0)

| # | Issue | Location | Notes |
|---|---|---|---|
| 10 | **ISO 20022 pytest tests never run in CI** | `.github/workflows/validate-schema.yml` | The 70-test suite in `iso20022-integration/test-suite/` is never invoked by CI. A new workflow step (or separate workflow) should run `pytest iso20022-integration/test-suite/` on every push that changes `iso20022-integration/**`. |
| 11 | **CI path triggers exclude `iso20022-integration/`** | `.github/workflows/validate-schema.yml` `on.push.paths` | The workflow only triggers on `schema/**`, `examples/**`, `tools/**` — changes to `iso20022-integration/**` or `docs/**` never trigger validation. |
| 12 | **`tools/javascript/package.json` test script references non-existent `tests/` directory** | `tools/javascript/package.json` | `"test": "node --test tests/"` will fail with "directory not found". Either create `tests/` with Node.js test files, or update the script to point to the correct location. |
| 13 | **`package-lock.json` excluded from git** | `.gitignore` | `package-lock.json` is gitignored, making Node.js CI builds non-reproducible (each run may get different transitive dependency versions). For a security-sensitive standard, reproducible builds matter. Consider removing the gitignore exclusion and committing it for the `tools/javascript/` package. |
| 14 | **ISO 20022 test suite has no `requirements.txt`** | `iso20022-integration/test-suite/` | Test files import `pytest` and `jsonschema` but there is no `requirements.txt` in the test-suite directory. A contributor or CI runner following the test docstring (`pip install pytest jsonschema`) may get wrong versions. Add a pinned `requirements.txt` here. |

---

### 🟡 Missing Assets & Governance Gaps (v1.4.0)

| # | Issue | Location | Notes |
|---|---|---|---|
| 15 | **No `SECURITY.md` file** | Repository root | GitHub security policy file is absent. For a standard handling sensitive financial and identity data, a responsible-disclosure policy and contact for security reports is important. Add `SECURITY.md`. |
| 16 | **No `CHANGELOG.md`** | Repository root | Version history is embedded only in `ROADMAP.md`. A dedicated `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/) conventions is standard practice and makes it easier for adopters to audit what changed between versions. |
| 17 | **NOTICE file missing OpenID Foundation attribution** | `NOTICE` | The standard relies heavily on OpenID4VP and OpenID4VCI for EUDI Wallet flows, but the NOTICE file does not acknowledge the OpenID Foundation. Add an attribution for OpenID4VP (draft specification, OpenID Foundation). |
| 18 | **Legacy `v0.1*` schema files with uppercase `.JSON` extension** | `schema/versions/` | `v0.1.1.hybrid.JSON`, `v0.1.a.JSON`, `v0.1.hybrid.JSON` use uppercase `.JSON` extensions, inconsistent with all other `.json` files in the repo. These pre-release drafts should either be normalised to `.json` or moved to an `archive/` folder to avoid confusion. |
| 19 | **Two roadmap files with overlapping scope** | `ROADMAP.md` (root), `docs/roadmap.md` | The root `ROADMAP.md` covers features; `docs/roadmap.md` covers documentation tasks. The relationship is not clearly stated in either file. Add a header/cross-reference clarifying that `docs/roadmap.md` is a documentation-only backlog and `ROADMAP.md` is the authoritative project roadmap. |
| 20 | **`sd-jwt-compact-token.json` contains placeholder/stub signature values** | `examples/sd-jwt-compact-token.json` | The example sets `"encodedToken": "******"` and explicitly notes that signature values are placeholder stubs that "CANNOT be cryptographically verified." This is valuable as a reference document but should be clearly excluded from automated schema validation or moved to `docs/` to avoid false assurance. |
| 21 | **No published npm package or Python package** | — | `tools/javascript/package.json` uses `@openkycaml/tools` as the package name, implying npm publication intent. Similarly, there is no `pyproject.toml` / `setup.py` for a `pip install openkycaml` workflow. Publishing to npm and PyPI would significantly lower the barrier to adoption. |

---

### 🔵 Technical Standards Considerations (v1.4.0 / v2.0.0)

| # | Issue | Location | Notes |
|---|---|---|---|
| 22 | **Schema `$id` and `$schema` URLs reference `openkycaml.org` — domain status unconfirmed** | `schema/kyc-aml-hybrid-extended.json`, all examples | The schema `$id` is `https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json` and all example `$schema` fields reference this URL. If `openkycaml.org` is not actively registered and serving the schema, this creates both a usability problem (remote $id resolution fails) and a potential security risk (domain squatting). Verify the domain is registered and serving the schema, or migrate to the GitHub Pages URL `https://lazy-jack-ltd.github.io/openKYCAML/...` as a fallback. |
| 23 | **EUDI Wallet `@context` URL is a placeholder** | All `-eudi-wallet.json` examples | Examples use `"https://europa.eu/2018/credentials/eudi/v1"` as the EUDI context URL. The EU Commission has not published an official EUDI Wallet VC JSON-LD context URL. This should be documented as a placeholder pending the final ARF VC context publication, and examples/schema should be updated when the official URL is released. |
| 24 | **No formal W3C VC Data Model v2 migration path documented** | `docs/`, `schema/` | The v2 DM introduces breaking changes to `@context`, `type`, and `credentialStatus`. Given the roadmap target of "aligning with final W3C VC Data Model v2" in v2.0.0, a documented migration guide between v1 and v2 VC context URLs would help adopters plan integrations today. |
| 25 | **`kycProfile.beneficialOwnership` trust/foundation fields are generic** | Schema | The existing `beneficialOwnership` array covers trusts and foundations only via the generic `naturalPerson`/`legalPerson` person wrapper. Fields specific to trusts (settlor, trustee, protector, letter of wishes reference), foundations (founder, council, statutory powers), and LLPs (GP/LP distinction, management rights) are not captured in schema. This limits FATF R.25 compliance to narrative-only. Add typed sub-objects for trust deeds, foundation statutes, and partnership agreements. |
| 26 | **No machine-readable OpenID4VP Presentation Definition for Travel Rule minimum** | `docs/`, `examples/` | The EUDI Wallet integration guide describes the presentation flow but does not include a reference `presentation_definition` JSON object that a VASP relying party can use to request exactly the Travel Rule-minimum claims from a wallet. Including a canonical `presentation_definition` example (and optionally registering it in a trust registry) would accelerate interoperability. |
| 27 | **Go validator not started despite TRISA ecosystem using Go natively** | `tools/` | TRISA, the most widely deployed Travel Rule protocol, is Go-native. The absence of a Go validator means TRISA node operators face a friction point in validating OpenKYCAML payloads. Prioritise the Go validator in v1.4.0. |
| 28 | **SWIFT MT to OpenKYCAML converter not started** | `tools/converters/` | `swift-mt-to-openkycaml.py` is listed as planned but not started. The SWIFT MT→MX migration deadline (November 2025) has passed; CBPR+ is now mandatory, making the MT converter less urgent, but many institutions still operate legacy MT rails in parallel. Reassess priority. |
| 29 | **No `openvasp-to-openkycaml.js` converter** | `tools/converters/` | Listed as planned for v1.4 but not started. |
| 30 | **No formal test suite for core Python tools (`validator.py`, `converter.py`, `models.py`)** | `tools/python/` | There are no unit or integration tests for the primary Python tooling in `tools/python/`. Only the ISO 20022 converter has a test suite. The core validator and converter should have tests, especially for the business-logic warning paths. |

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
| Add CI step for ISO 20022 pytest suite + widen path triggers | Planned | Technical Debt #10, #11 |
| Fix `nameIdentifier` field-name inconsistency in docs | Planned | Bug #1 |
| Fix `originatingVASP.originatingVASP` double-nesting in adoption guide | Planned | Bug #2 |
| Add `SECURITY.md` and `CHANGELOG.md` | Planned | Gap #15, #16 |
| Publish `@openkycaml/tools` to npm and `openkycaml` to PyPI | Planned | Gap #21 |
| Fix JS `tests/` directory referenced in `package.json` | Planned | CI #12 |
| Typed trust/foundation/LLP sub-objects in `beneficialOwnership` | Planned | Standards #25 |
| Canonical OpenID4VP Presentation Definition for Travel Rule minimum | Planned | Standards #26 |

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

> For the full detailed change history, see [CHANGELOG.md](CHANGELOG.md).

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

