# Changelog

All notable changes to OpenKYCAML are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

For the full project roadmap and planned features, see [ROADMAP.md](ROADMAP.md).

---

## [Unreleased]

### Added

- `docs/naming-convention.md` — new document defining the repository-wide file and directory naming convention (lowercase kebab-case, sub-folder organisation for docs, pattern rules for examples, schema versions, and versioned artefacts).

### Changed (naming/organisation — no schema changes)

- `docs/` reorganised into sub-folders by type: `guides/`, `mappings/`, `compliance/`, `reference/` (existing `diagrams/` and `versions/` unchanged). All cross-references updated.
- `docs/AMLR-requirements.md` → `docs/compliance/amlr-requirements.md` (lowercase, moved to compliance sub-folder).
- `docs/versions/roadmapv0.1.md` → `docs/versions/roadmap-v0.1.md` (added hyphen before version).
- `examples/structure_diagrams/` → `examples/structure-diagrams/` (underscores → hyphens).
- `tools/javascript/openvaspConverter.js` → `tools/javascript/openvasp-converter.js` (camelCase → kebab-case).
- `schema/versions/archive/v0.1.hybrid.json` → `schema/versions/archive/v0.1.0-hybrid.json`.
- `schema/versions/archive/v0.1.1.hybrid.json` → `schema/versions/archive/v0.1.1-hybrid.json`.
- `schema/versions/archive/v0.1.a.json` → `schema/versions/archive/v0.1.0-alpha.json`.
- `CONTRIBUTING.md` updated with new §7 "File and Document Naming" section.
- `docs/README.md` restructured to reflect sub-folder organisation with section headers per category.
- CI (`validate-schema.yml`) gains a new `lint-naming` job that enforces the naming convention on every push and pull request.

---

## [1.9.0] — April 2026

### Added

- **`taxStatus` top-level block** — New optional `TaxStatus` $def and root property covering four global tax and economic substance regimes:
  - **`tinIdentifiers[]`** (`TinIdentifier` $def) — Structured, multi-jurisdiction TIN array. Each entry carries `jurisdiction` (ISO 3166-1 alpha-2), `tinType` enum (`TIN | VAT | GST | PST | EIN | functionalEquivalent | other`), `tinValue`, optional `issuanceDate`, `verificationStatus`, and `verificationSource`. Supersedes and extends IVMS 101 `nationalIdentification.TXID` for OECD CRS/CARF, FATCA, and AMLR Art. 22 tax-residency verification.
  - **`indirectTaxRegistrations[]`** (`IndirectTaxRegistration` $def) — VAT, GST, PST, HST, and salesTax registration entries per jurisdiction. Each carries `taxType`, `jurisdiction`, `registrationNumber`, `status` (`active | suspended | revoked | exempt`), and `effectiveFrom`. Supports EU VIES, India GSTIN, Australia ABN/GST, Canada HST/PST.
  - **`economicSubstance`** (`EconomicSubstance` $def) — Economic Substance Regulation (ESR) block for entities in BVI, Cayman Islands, UAE, Jersey, Guernsey, Isle of Man, and other ESR jurisdictions. Fields: `jurisdiction`, `status` (5-value enum: `inScope-RelevantEntity | exempt-TaxResidentElsewhere | exempt-PureEquityHolding | compliant | nonCompliant`), `relevantActivities[]`, `coreIncomeGeneratingActivitiesPerformed`, `lastNotificationDate`, `lastReportReference`.
  - **`pillarTwo`** (`PillarTwo` $def) — OECD Pillar 2 GloBE (BEPS 2.0) block for MNE constituent entities with consolidated revenue >= EUR 750 million. Fields: `inScopeMNE`, `consolidatedRevenueEUR`, `constituentEntityStatus` (`inScope | excluded | QDMTT`), `etrJurisdictions[]` (`{jurisdiction, etr}` — ETR as decimal), `safeHarbourApplied` (`SimplifiedETR | SubstanceBased | DeMinimis | none`), `girFilingReference`, `lastGIRDate`.

- **4 new examples** in `examples/tax/`:
  - `tax-individual-tin.json` — natural person with US EIN + UK UTR (`functionalEquivalent`) TIN array.
  - `tax-corporate-vat-gst.json` — German legal entity with EU VAT and India GSTIN indirect tax registrations plus DE/IN TIN identifiers.
  - `tax-offshore-esr.json` — Cayman Islands holding company with `economicSubstance` block (`inScope-RelevantEntity` status, relevant activities, notification reference).
  - `tax-mne-pillar2.json` — Irish MNE constituent entity with full `pillarTwo` block including `etrJurisdictions[]` and `girFilingReference`.

- **`docs/mappings/tax-status-oecd-esr-pillar2.md`** + **`tax-status-oecd-esr-pillar2.yaml`** — new mapping document covering OECD CRS/CARF TIN, EU VAT/GST/PST, ESR, and Pillar 2 GloBE. Includes IVMS 101 TXID migration path (§2.3).

- **`schema/versions/v1.9.0.json`** — versioned copy of updated canonical schema.

- **Compliance matrix §18–§20** — Tax Status (TIN/CRS/CARF), ESR, and Pillar 2 GloBE sections added to `docs/compliance/compliance-matrix.md`.

- **IVMS 101 mapping §11** — TXID → `taxStatus.tinIdentifiers[]` structured migration path added to `docs/mappings/mapping-ivms101-eidas-amlr.md`.

- **Validator business warnings** (Python + Node.js + Go):
  - `taxStatus.economicSubstance.status = "nonCompliant"` → ESR red-flag warning (EDD + SAR recommendation).
  - `taxStatus.pillarTwo.inScopeMNE = true` + `girFilingReference` absent → GIR missing warning.

### Changed

- `schema/kyc-aml-hybrid-extended.json` — version bumped from `1.8.0` to `1.9.0`; `$id` updated to `https://openkycaml.org/schema/v1.9.0/kyc-aml-hybrid-extended.json`.
- `tools/go/validator.go` — `ValidationResult` gains `Warnings []string` field; `businessWarnings()` function added.

---

## [1.8.0] — April 2026

### Added

- **`legacyIdentifiers` top-level block** — New optional `LegacyIdentifiers` $def and root property for X.500 Distinguished Names:
  - `x500DN` (string, regex-validated RFC 4514 pattern) — carries the X.500 DN as used in X.509 certificate Subject/Issuer fields, SWIFTNet technical addresses, or LDAP directory entries.
  - `x500DNType` (enum) — context: `certificateSubject`, `certificateIssuer`, `directoryEntry`, `swiftNetAddress`.
  - X.400 O/R Addresses explicitly excluded; see `docs/mappings/x500-x400-legacy.md` §3.

- **`pkiEvidence` top-level block** — New optional `PkiEvidence` $def and root property for X.509 PKI certificate metadata:
  - `x509Certificate` sub-object — `serialNumber`, `subjectDN`, `issuerDN`, `validFrom`, `validTo`, `signatureAlgorithm`, `qcStatements[]` (ETSI EN 319 412 QCStatement OID names), `crlDistributionPoints[]` (URIs), `ocspResponderUrl` (URI), `thumbprintSha256` (lowercase hex, exactly 64 chars, regex-validated).
  - `oids[]` array — machine-readable ASN.1 Object Identifiers with `oid` (dotted-decimal, regex-validated), `description`, and optional `value`.
  - `certificateDocumentRef` (URI) — links to `identityDocuments` for full eIDAS triangulation.

- **2 new examples** in `examples/evidence/`:
  - `eidas-x509-dn.json` — legal entity (Acme Bank PLC) with QSealC `pkiEvidence` and `legacyIdentifiers.x500DN`.
  - `eidas-x509-qeaa.json` — natural person (Anna Schmidt) with eIDAS 2.0 QEAA evidence triangulation: `verifiableCredential.evidence[]` (EUDI Wallet DID) + `pkiEvidence` (BSI QTSP X.509 cert metadata) + `legacyIdentifiers.x500DN`.

- **`docs/mappings/x500-x400-legacy.md`** + **`x500-x400-legacy.yaml`** — mapping of X.500 DN use cases and X.400 scope exclusion.
- **`docs/mappings/x509-pki.md`** + **`x509-pki.yaml`** — full X.509 / ETSI QCStatement / ASN.1 OID mapping with compliance alignment table.
- **`schema/versions/v1.8.0.json`** — versioned copy of updated canonical schema.
- **Compliance matrix §17** — X.500/X.509 PKI support section added to `docs/compliance/compliance-matrix.md`.

### Changed

- `schema/kyc-aml-hybrid-extended.json` — version bumped from `1.7.0` to `1.8.0`; `$id` updated to `https://openkycaml.org/schema/v1.8.0/kyc-aml-hybrid-extended.json`.
- `ROADMAP.md` — v1.8.0 milestone added.

---

## [1.7.0] — April 2026

### Added

- **XLS-70 Credentials support (rename from XLS-40d draft)** — Updated all references to use the final published standard number. The XRPL On-Chain Credentials standard is now XLS-70 (live on XRPL mainnet), superseding the draft number XLS-40d used in previous versions. All schema field descriptions, mapping documents, and compliance matrix updated.

- **XLS-80: Permissioned Domains** — New fields on `kycProfile.blockchainAccountIds[]`:
  - `xrplPermissionedDomainId` (string, optional) — Hash256 identifier (64-char hex) of the XRPL Permissioned Domain (XLS-80) that this wallet is authorised within. Links the investor to a specific domain gate controlling access to Permissioned DEXes and lending protocols.
  - `xrplAuthorizedCredentialTypes[]` (array of strings, optional) — Hex credential type strings that have been accepted within the domain. Records which XLS-70 credential types satisfy the domain's access requirements.

- **XLS-81d: Permissioned DEX coverage** — Documentation in `docs/mappings/mapping-xrpl-credentials-mpt.md` §6 explains how `xrplPermissionedDomainId` gates access to the Permissioned DEX, and how the dual-gate model (Authorised Trustlines + Permissioned Domain) is the XRPL equivalent of ERC-3643's combined `isVerified()` + `canTransfer()` check.

- **XLS-96: Confidential Transfers** — New `xrplConfidentialTransfer` object on `kycProfile.blockchainAccountIds[]`:
  - `enabled` (boolean, required when present) — Whether the MPT issuance uses XLS-96 confidential transfers (EC-ElGamal + ZKP encrypted balances).
  - `encryptionScheme` (enum: `"EC_ELGAMAL"`) — Encryption scheme; enum allows future schemes.
  - `auditorPublicKey` (string, optional) — Compressed EC public key of the designated auditor for selective disclosure.
  - `regulatorPublicKey` (string, optional) — Regulator's selective disclosure key for legally-required visibility.

- **Enhanced MPT (XLS-33d) coverage** — Three new fields on `kycProfile.blockchainAccountIds[]`:
  - `mptFlags` (integer, optional) — Bitmask of `MPTIssuance` compliance flags (`lsfMPTCanLock`, `lsfMPTRequireAuth`, `lsfMPTCanEscrow`, `lsfMPTCanTrade`, `lsfMPTCanTransfer`, `lsfMPTCanClawback`). Enables downstream systems to derive the compliance enforcement model without querying the ledger.
  - `mptMetadata` (string, optional) — Issuer-defined token metadata (ISIN, prospectus URI, asset class, compliance rules embedded in the token at the protocol level). Mirrors the `MPTokenMetadata` field.
  - `mptTransferFee` (integer 0–50000, optional) — Transfer fee in millionths; mirrors `MPTIssuance.TransferFee`.

- **XRPL Native Clawback and Deep Freeze (XLS-77)** — Two new fields on `kycProfile.blockchainAccountIds[]`:
  - `xrplFreezeType` (enum, optional) — Granular freeze type: `"INDIVIDUAL_FREEZE"` (single trustline/MPToken), `"GLOBAL_FREEZE"` (all issuance trustlines), `"DEEP_FREEZE"` (XLS-77 enhanced freeze preventing receipt). Supersedes the boolean `isFrozen` for XRPL-specific flows.
  - `xrplClawbackEnabled` (boolean, optional) — Whether the XRPL Clawback amendment (or `lsfMPTCanClawback`) is enabled for this wallet's trustline/MPT. Protocol-level equivalent of ERC-3643 `forcedTransfer()`.

- **Bitcoin and Lightning Network fields** — Three new fields on `kycProfile.blockchainAccountIds[]`:
  - `lightningNodePubkey` (string, optional) — Lightning node compressed public key (66-char hex, secp256k1). Links KYC identity to a Lightning node for LNURL-auth or LSP compliance workflows.
  - `lightningServiceProvider` (string, optional) — Name or DID of the Lightning Service Provider responsible for service-layer compliance enforcement (e.g. Lightspark, Voltage, BitGo).
  - `bitcoinScriptType` (enum, optional) — Bitcoin script type: `"P2PKH"`, `"P2WPKH"`, `"P2TR"` (Taproot). Provides chain analysis context.

- **`docs/compliance/enforcement-tiers.md`** — New normative document defining the OpenKYCAML Three-Tier Compliance Enforcement Model:
  - Tier 1: On-chain enforcement (Ethereum / ERC-3643 smart contracts)
  - Tier 2: Protocol-level enforcement (XRPL / XLS-70/80/81/96/77 + MPTs + Clawback)
  - Tier 3: Service-layer enforcement (Bitcoin / Lightning / LSPs)
  - Includes capability comparison table, field-to-tier mapping, regulatory alignment, and multi-tier implementation guidance.

- **`docs/mappings/mapping-bitcoin-lightning.md`** — New comprehensive mapping document covering:
  - Bitcoin protocol compliance limitations (no on-chain enforcement)
  - Layer-2 solutions: Lightning Network, Liquid Network, Taproot Assets, RGB Protocol
  - Bitcoin address type mapping (P2PKH / P2WPKH / P2TR)
  - Lightning node identity and LNURL-auth binding
  - Service-layer compliance providers: Lightspark, Voltage, BitGo, Coinbase, Revolut
  - Travel Rule on Lightning (FATF Rec. 16 at service layer)

- **`schema/versions/v1.7.0.json`** — Versioned snapshot of the schema at v1.7.0.

### Changed

- `docs/mappings/mapping-xrpl-credentials-mpt.md` — Comprehensive update:
  - Renamed all XLS-40d references to XLS-70 (final published standard)
  - Added §5 "XLS-80: Permissioned Domains" with architecture, mapping table, and JSON example
  - Added §6 "XLS-81d: Permissioned DEX" with dual-gate model (Authorised Trustlines + Permissioned Domain)
  - Added §9 "XLS-77: Deep Freeze and XRPL Native Clawback" with freeze hierarchy table and clawback mapping
  - Added §10 "XLS-96: Confidential Transfers" with privacy/regulatory balance table, GDPR notes, and JSON example
  - Enhanced §7 "MPTIssuance Object" to include `mptFlags`, `mptMetadata`, `mptTransferFee` fields
  - Updated §11 "KYC/AML Gating" table with all new v1.7.0 fields
  - Updated §12 "Coverage Gap Summary" with v1.7.0 additions
  - Updated architecture overview diagram and XRPL source references
  - Document version bumped to v1.7.0

- `docs/compliance/compliance-matrix.md` — Updated:
  - Section 12 renamed to "XRPL Credentials (XLS-70), DIDs, Permissioned Domains (XLS-80), and Multi-Purpose Tokens (XLS-33d)"
  - Added rows for XLS-80 Permissioned Domain ID, domain credential requirements, XLS-81d Permissioned DEX, Authorised Trustlines, MPT flags/metadata/fee, Deep Freeze (XLS-77), clawback, XLS-96 confidential transfer fields
  - Added §13 "Bitcoin and Lightning Network (Service-Layer Enforcement)" with coverage table
  - Matrix version updated from v1.3.0 to v1.7.0

- `docs/mappings/mapping-erc3643.md` — Added:
  - `forcedTransfer()` row in §7 Token Contract table with XRPL clawback cross-reference
  - `isFrozen()` note updated with XLS-77 Deep Freeze cross-reference
  - New §11 "Cross-Network Equivalence: ERC-3643 vs XRPL vs Bitcoin/Lightning" comparison table
  - Document version bumped to v1.7.0

- `schema/kyc-aml-hybrid-extended.json` — `$id` and `version` bumped to `v1.7.0`.

### Scope

All v1.7.0 changes are fully additive and backward-compatible with v1.6.0 payloads. No existing required fields or enum values changed.

---

## [1.6.0] — April 2026

### Added

- **`documentId` on `NaturalPersonDocument` and `LegalEntityDocument`** — new optional (strongly recommended) canonical portable identifier for inter-system document exchange. Uses the OpenKYCAML Document ID URN scheme:
  ```
  urn:openkycaml:doc:{issuing-country}:{doc-type-code}:{subject-ref}:{YYYY-MM}
  ```
  Distinct from `documentRef` (internal storage path) and `credentialId` (W3C VC URI). Must remain stable when the document is re-shared. Validated by schema `pattern` constraint.

- **`docs/reference/document-id-convention.md`** — normative specification for the Document ID URN scheme. Covers: pattern and segment semantics, short-code table for all 11 natural-person and 16 legal-entity `documentType` enum values, subject-reference construction (pseudonymous SHA-256 truncation for natural persons; LEI or registration number for legal entities), discriminator rules for same-month collisions, relationship to `documentRef`/`credentialId`/`verifyingDocumentRef`, cross-system deduplication guidance, and document lifecycle rules.

- **`schema/versions/v1.6.0.json`** — versioned snapshot of the schema at v1.6.0.

- **Validator warnings for missing or malformed `documentId`** — both the Python (`tools/python/validator.py`) and JavaScript (`tools/javascript/validator.js`) validators now emit advisory warnings when a document in `identityDocuments` is missing `documentId` or when the value does not conform to the URN pattern.

### Changed

- `examples/document-bundle-natural-person.json` — added `documentId` to each of the three document records. Subject reference for Andreas Schmidt: `sha256-421149` (derived from `SHA256("L01X00T471DE1985-07-22")[0:6]`).
- `examples/document-bundle-legal-entity.json` — added `documentId` to each of the six document records for Acme Global Trading PLC. Subject reference: LEI `529900w18lqjjn6sj336`.

### Scope

Fully additive and backward-compatible with v1.5.0 payloads. No existing required fields or enum values changed.

---

## [1.5.0] — April 2026

### Added

- **Verification Document Bundle (`identityDocuments`)** — new optional root-level property providing a typed, structured bundle of verification documents for natural persons and legal entities. Satisfies ISO 17442 (LEI), GLEIF LOU documentary evidence requirements, FATF Rec. 10/24/25, and AMLR Art. 22 and 26. All changes are fully additive and backward-compatible with v1.4.0 payloads.

- **`$defs/ExtractedAttribute`** — new reusable definition recording a single data element extracted from a verification document (`attributeName`, `value`, `matchesRecord`). Enables traceability from raw document data to asserted IVMS 101 / kycProfile fields.

- **`$defs/NaturalPersonDocument`** — typed document record for natural person identity verification. Supports 11 document types: `NATIONAL_ID_CARD`, `PASSPORT`, `RESIDENCE_PERMIT`, `DRIVERS_LICENCE`, `BIRTH_CERTIFICATE`, `PROOF_OF_ADDRESS`, `TAX_IDENTIFICATION`, `SOCIAL_SECURITY`, `BIOMETRIC_DATA_RECORD`, `EIDAS_PID_CREDENTIAL`, `OTHER`. Carries issuing authority, dates, verification method, assurance level, document presence (Physical/Digital), internal document URI, credential ID (for VCs), and `extractedAttributes[]`.

- **`$defs/LegalEntityDocument`** — typed document record for legal entity identity verification. Supports 16 document types: `CERTIFICATE_OF_INCORPORATION`, `ARTICLES_OF_ASSOCIATION`, `REGISTRY_EXTRACT`, `LEI_REGISTRATION`, `VLEI_CREDENTIAL`, `PROOF_OF_REGISTERED_ADDRESS`, `TRUST_DEED`, `PARTNERSHIP_AGREEMENT`, `FOUNDATION_CHARTER`, `ULTIMATE_BENEFICIAL_OWNER_REGISTER`, `AUTHORISED_SIGNATORY_LIST`, `ANNUAL_REPORT_ACCOUNTS`, `VAT_REGISTRATION_CERTIFICATE`, `REGULATORY_LICENCE`, `LPID_CREDENTIAL`, `OTHER`. Includes `gleifRegistrationAuthority` (structured RAL reference), `elfCodeVerified` (ISO 20275 ELF code confirmed), `vLEICredentialType` (`QVI`/`OOR`/`ECR`), `registryUrl` (permalink to live registry record), and `extractedAttributes[]`.

- **`$defs/RegistrationAuthorityDetail`** — structured GLEIF Registration Authorities List (RAL) reference replacing the free-text `registrationAuthority` field. Contains `ralCode` (pattern `RA######`), `authorityName`, `jurisdiction` (ISO 3166-1 or 3166-2), `registryUrl`, and `digitalAccessible`. Used in `NationalIdentification.registrationAuthorityDetail` and `LegalEntityDocument.gleifRegistrationAuthority`.

- **`$defs/VerificationDocumentBundle`** — top-level container for the document bundle. Contains `naturalPersonDocuments[]`, `legalEntityDocuments[]`, `bundleCompleteness` (`COMPLETE`/`PARTIAL`/`PENDING`), `bundleValidatedBy`, `bundleValidationDate`, and `requiredDocumentTypes[]`.

- **Cross-reference fields** on existing schema objects:
  - `NationalIdentification.verifyingDocumentRef` — links the national identifier to its source document in the bundle.
  - `NationalIdentification.registrationAuthorityDetail` — structured GLEIF RAL reference alongside the existing free-text `registrationAuthority`.
  - `LegalPerson.verifyingDocumentRef` — links `legalFormCode` to the `LegalEntityDocument` that confirmed it via the GLEIF RAL.
  - `DueDiligenceRequirements.verificationMethods[].documentRef` — links each verified attribute to its source document.
  - `BeneficialOwner.verifyingDocumentRefs[]` — links each UBO claim to the evidence documents (e.g. PSC register extract, trust deed).

- **`examples/document-bundle-natural-person.json`** — complete natural person verification bundle: German Personalausweis + proof of address + eIDAS 2.0 PID Verifiable Credential (Bundesdruckerei GmbH PID Provider), with `extractedAttributes` cross-referencing IVMS 101 fields and `documentRef` linkage in `nationalIdentification`.

- **`examples/document-bundle-legal-entity.json`** — complete UK PLC verification bundle (EDD level): Certificate of Incorporation + Companies House current appointments extract + LEI confirmation (Bloomberg LOU) + GLEIF vLEI OOR credential (LuxTrust QVI) + PSC register UBO extract. Demonstrates `gleifRegistrationAuthority = RA000585`, `elfCodeVerified = Z13E`, `verifyingDocumentRefs[]` on beneficial owner record, and `documentRef` linkage in `verificationMethods[]`.

- **`schema/versions/v1.5.0.json`** — versioned copy of the schema.

- **`docs/mappings/mapping-ivms101-eidas-amlr.md` §10** — new section "Verification Document Bundle" with mapping tables for all 11 natural person document types and 16 legal entity document types to AMLR articles, FATF recommendations, and relevant ISO standards; cross-reference field table; and document completeness guidance by entity type.

- **`docs/guides/adoption-guide.md` §8** — new section "Building a Compliant Document Bundle" covering: GLEIF RAL lookup workflow with common RAL codes (UK, DE, US, FR, NL, JP, IE); required documents by entity type (natural person CDD/EDD, company, trust, foundation, partnership); GLEIF vLEI credential hierarchy (QVI → OOR → ECR); guidance on populating `extractedAttributes[]`; and cross-reference field usage with JSON examples.

---

## [Unreleased]

### Fixed
- `nameIdentifier` field-name inconsistency in `docs/mappings/mapping-ivms101-eidas-amlr.md` and `docs/guides/adoption-guide.md` (was incorrectly written as `nameIdentifiers` with a trailing 's' in several places).
- Double `originatingVASP.originatingVASP.*` field path in `docs/guides/adoption-guide.md` minimum-required-fields table — corrected to `originatingVASP.*`.
- Example count updated from 17 to 21 in `ROADMAP.md` highlights.
- README example table now includes all four complex-ownership examples (`complex-group-multi-tier.json`, `foundation-complex-ubo.json`, `llp-complex-ubo.json`, `trust-complex-ubo.json`).
- FATF Rec. 25 compliance matrix row updated from `🟡 Partial` to `✅` reflecting existing trust/foundation/LLP example coverage; note added for planned typed sub-object extensions (v1.4.0).
- Stale SWIFT MT→MX "November 2025" migration deadline reworded to past tense in `iso20022-integration/README.md`.
- MiCA Art. 83 Travel Rule citations in compliance matrix and ISO 20022 README now correctly reference **TFR 2023/1113 Art. 14** as the primary EU operative instrument alongside MiCA.
- `docs/compliance/amlr-requirements.md` (formerly `docs/compliance/amlr-requirements.md`) expanded from a 23-line stub to a full quick-reference document with article-to-field mapping table, AMLA RTS status table, and links to the compliance checklist.
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
- `docs/reference/vc-data-model-migration.md` — W3C VC Data Model v1.1 → v2.0 migration guide for adopters.
- `examples/presentation-definitions/travel-rule-minimum.json` — canonical OpenID4VP Presentation Definition for FATF Rec 16 Travel Rule minimum claims.
- `tools/go/` — Go validator scaffold (`go.mod`, `validator.go`, `validator_test.go`) for TRISA-native integrations.
- `tools/javascript/openvasp-converter.js` — OpenVASP identity payload ↔ OpenKYCAML `ivms101` block converter.
- `tools/python/tests/` — pytest test suite for core Python tooling (`validator.py`, `converter.py`, `models.py`).
- `pyproject.toml` — packaging metadata enabling `pip install openkycaml`.

### Changed
- `.gitignore` — `package-lock.json` removed from ignore list to enable reproducible Node.js dependency resolution.

---

## [1.4.0] — April 2026

### Added
- **ISO 20275:2017 Entity Legal Form (ELF) classification** — new optional fields on `LegalPerson`:
  - `legalFormCode` — 4-character GLEIF ELF code (pattern `^[A-Z0-9]{4}$`), references the ISO 20275 Annex A / GLEIF ELF code list (e.g. `8888` = US LLC, `Z13E` = UK PLC, `KY39` = Cayman Exempted Trust). Mandatory for GLEIF LEI registration compliance.
  - `legalFormDescription` — free-text fallback where the ELF code is unavailable or the jurisdiction is not yet in the GLEIF code list.
  - `entityType` — enum discriminator (`COMPANY`, `TRUST`, `FOUNDATION`, `PARTNERSHIP`, `OTHER`) driving typed sub-object validation.
- **Typed legal-arrangement sub-objects** for FATF Rec. 25 / AMLR Art. 26(2)(b) structured disclosure:
  - `trustDetails` (`TrustDetails`) — settlors, trustees, protectors, `beneficiaryClass`, `namedBeneficiaries`, `dateEstablished`, `jurisdictionOfLaw`, `trustDeedReference`. Required when `entityType = TRUST`.
  - `foundationDetails` (`FoundationDetails`) — founders, councilMembers, `foundationPurpose`, `dateEstablished`, `jurisdictionOfRegistration`. Required when `entityType = FOUNDATION`.
  - `partnershipDetails` (`PartnershipDetails`) — `partnershipType` (`LP`/`LLP`/`GP`), `generalPartners`, `limitedPartners`, `members`, `dateEstablished`, `jurisdictionOfRegistration`. Required when `entityType = PARTNERSHIP`.
  - All person arrays within the typed sub-objects accept `naturalPerson` or `legalPerson` references to support corporate trustees, general partners that are companies, etc.
  - `otherEntityDescription` free-text for `entityType = OTHER`.
- **`ISO_20275_ELF_CODE`** added to `nationalIdentifierType` enum — provides an IVMS 101-interoperable path to record ELF codes in the `nationalIdentification` block for counterparties that require strict IVMS 101 field-path compliance.
- **New examples**:
  - `examples/legal-entity-trust.json` — Cayman Islands Exempted Discretionary Trust (`legalFormCode: KY39`, full `trustDetails` with corporate trustee and named protector).
  - `examples/legal-entity-partnership.json` — Scotland LLP (`legalFormCode: XLCT`, `partnershipDetails` with two natural-person members and one corporate member).

### Changed
- `$id` and `version` bumped to `v1.4.0`.
- `docs/compliance/compliance-matrix.md` — FATF Rec. 24/25 and AMLR Art. 26 rows updated to reflect full structural coverage provided by v1.4.0 typed sub-objects; "RFC pending" caveat removed.
- `docs/mappings/mapping-ivms101-eidas-amlr.md` — ISO 20275 mapping rows added to §3 Legal Entity Fields.

### Added (SWIFT MT Converter)
- **SWIFT MT legacy bridge** (`iso20022-integration/libraries/python/swift_mt_converter.py` + `iso20022-integration/libraries/typescript/swift-mt-converter.ts`) — bidirectional converter between OpenKYCAML v1.4.0 payloads and SWIFT FIN MT messages, addressing Issue #28:
  - **Message types supported:** MT 103 (customer credit transfer), MT 202 (general FI transfer), MT 202 COV (covered FI transfer), MT 910 (confirmation of credit), MT 940 (customer statement).
  - **Direction:** bidirectional — OpenKYCAML → MT (outbound) and MT → OpenKYCAML (inbound parsing).
  - **Field mapping:** full MT 103 field set including `:32A:` value date/currency/amount, `:50K:` / `:59:` parties with address, `:52A:` / `:57A:` VASP agents, `:71A:` charges, `:70:` remittance info, `:77B:` regulatory reporting.
  - **:77B: Travel Rule carrier (FATF Rec. 16):** `build_77b` / `build77b` writes structured `/ORDERRES/` + `/BENEFRES/` + `/UETR/` lines from OpenKYCAML data; `parse_77b` / `parse77b` performs best-effort extraction back to `ivms101` originator/beneficiary fields.
  - **Test coverage:** 91-test Python pytest suite + 83-test TypeScript/Node.js suite; all pass ✅.
  - **No new dependencies** — Python standard library only; TypeScript uses only `node:crypto`.

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

[Unreleased]: https://github.com/Lazy-Jack-Ltd/openKYCAML/compare/v1.7.0...HEAD
[1.7.0]: https://github.com/Lazy-Jack-Ltd/openKYCAML/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/Lazy-Jack-Ltd/openKYCAML/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/Lazy-Jack-Ltd/openKYCAML/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/Lazy-Jack-Ltd/openKYCAML/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/Lazy-Jack-Ltd/openKYCAML/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Lazy-Jack-Ltd/openKYCAML/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Lazy-Jack-Ltd/openKYCAML/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Lazy-Jack-Ltd/openKYCAML/releases/tag/v1.0.0
