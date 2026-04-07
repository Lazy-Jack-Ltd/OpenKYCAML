# OpenKYCAML Documentation Roadmap

> **Scope:** This file tracks **documentation-specific** improvements (new docs, doc updates, example additions). It is the documentation-only backlog.
> For the full **project roadmap** covering schema features, tooling, new releases, and technical debt, see [`../ROADMAP.md`](../ROADMAP.md).

This page tracks documentation-specific improvements planned for upcoming releases.

## Documentation Backlog

### v1.1
- [x] Add TypeScript type definitions documentation (`typescript-types.md`).
- [x] Add Pydantic model documentation (auto-generated from schema) (`pydantic-models.md`).
- [x] Add sequence diagrams for Travel Rule message flows (`diagrams/travel-rule-sequence-diagrams.md`).
- [x] Add sequence diagrams for eIDAS 2.0 VC issuance and presentation flows (`diagrams/eidas-sequence-diagrams.md`).
- [x] Add Mermaid entity-relationship diagram for the full schema (`diagrams/schema-er-diagram.md`).

### v1.2
- [x] Add AMLR 2027 compliance checklist (`amlr-2027-compliance-checklist.md`).
- [x] Update compliance matrix to v1.2.0 (SD-JWT, deep UBO, PID/LPID, AMLA RTS alignment section).
- [x] Add ERC-3643 (T-REX) mapping document (`mapping-erc3643.md`).
- [x] Add Sovrin / Hyperledger Indy (AnonCreds) mapping document (`mapping-sovrin.md`).
- [x] Add compliance matrix §10 (ERC-3643) and §11 (Sovrin/Indy).

### v1.3
- [x] New §12 "Handling Restricted Data in EUDIW Presentations" in `eudi-wallet-integration.md` — tipping-off protection, classification table, cryptographic enforcement pattern, issuer guidance.
- [x] Update compliance matrix to v1.3.0: GDPR Art. 9/10 (✅), AMLR Art. 73 (new row), FATF Rec. 21 (new row).
- [x] Extend AMLR 2027 compliance checklist with §10 GDPR sensitivity items and §11 tipping-off/SAR checklist.
- [x] Add `gdprSensitivityMetadata` → GDPR/AMLR mapping section (§9) to `mapping-ivms101-eidas-amlr.md`.
- [x] Update adoption guide: FAQ entries for SAR/tipping-off and `sar_restricted` vs `internal_suspicion`.
- [x] Add `hybrid-with-sar-restriction.json` example to all example tables.
- [x] Update all document version footers to v1.3.0.
- [x] Add `iso20022-integration/README.md` — purpose statement, supported message types, folder guide, quick-start examples, standards references.
- [x] Add `iso20022-integration/mapping/` — bidirectional field mapping YAML (OpenKYCAML ↔ ISO 20022) and narrative gap analysis.
- [x] Add `iso20022-integration/supplementary-data/` — KYCAMLEnvelope JSON Schema + canonical reference instance.
- [x] Add `iso20022-integration/profiles/` — pacs.008 CBPR+ Travel Rule, pain.001 CDD reliance, camt.053 audit trail profiles.
- [x] Add `iso20022-integration/examples/` — three fully-structured XML examples (pacs.008, pain.001, minimal snippet).
- [x] Add `iso20022-integration/libraries/` — Python and TypeScript bidirectional converters (`openkycaml_to_pacs008`, `openkycaml_to_pain001`, `iso20022_to_openkycaml`).
- [x] Add `iso20022-integration/test-suite/` — pytest round-trip and schema validation tests (70 tests passing).
- [x] Expand compliance matrix §6 ISO 20022 to cover all new integration artefacts.
- [x] Update `docs/README.md` to link to ISO 20022 integration module.
- [x] Expand `mapping-ivms101-eidas-amlr.md` §7 ISO 20022 Cross-Reference with full table and `<SplmtryData>` fields.
- [x] Update `travel-rule-implementation-guide.md` TRP section to use new full XML converters.
- [x] Update `tools/converters/README.md` to mark ISO 20022 converters as available.

### v1.4
- [x] Add ISO 20275 ELF code and entity-type documentation to adoption guide.
- [x] Update `mapping-erc3643.md` to reflect `legalFormCode` and typed entity sub-objects (TrustDetails, FoundationDetails, PartnershipDetails).
- [x] Update compliance matrix §5 AMLR Art. 26 to reference `trustDetails` / `foundationDetails` / `partnershipDetails`.
- [x] Add trust/partnership/LLP complex-UBO examples to example catalogue.
- [x] Update all document version footers to v1.4.0.

### v1.5
- [x] Add `identityDocuments` block documentation section to adoption guide (§8 Verification Document Bundle).
- [x] Add `mapping-ivms101-eidas-amlr.md` §10 (Verification Document Bundle) mapping table.
- [x] Update compliance matrix to cover GLEIF RAL `RegistrationAuthorityDetail`, `documentId`, `ExtractedAttribute`.
- [x] Add `document-bundle-natural-person.json` and `document-bundle-legal-entity.json` examples with narrative walkthrough.
- [x] Update ER diagram to include VerificationDocumentBundle, NaturalPersonDocument, LegalEntityDocument, ExtractedAttribute, RegistrationAuthorityDetail entities.
- [x] Update all document version footers to v1.5.0.

### v1.6
- [x] Add `docs/reference/document-id-convention.md` — URN scheme specification, regex pattern, issuing-country and document-type code tables, GLEIF RAL cross-reference.
- [x] Update `NaturalPersonDocument` and `LegalEntityDocument` documentation with `documentId` field and URN format guidance.
- [x] Update compliance matrix §5 AMLR Art. 56 to reference the document ID URN scheme.
- [x] Update all document version footers to v1.6.0.

### v1.7
- [x] **XLS-70 rename** — update all `XLS-40d` references to `XLS-70` across `mapping-xrpl-credentials-mpt.md`, `compliance-matrix.md`, README, ROADMAP.
- [x] Rewrite `mapping-xrpl-credentials-mpt.md` — new sections for XLS-80 Permissioned Domains (§5), XLS-81d Permissioned DEX (§6), enhanced MPT flags/metadata/fee (§7), XLS-77 freeze hierarchy (§9), XLS-96 Confidential Transfers + GDPR ZKP note (§10).
- [x] Add domain-gating integration steps to `travel-rule-implementation-guide.md`.
- [x] Update compliance matrix §12 XRPL expanded (XLS-80/81/96/77, Clawback) and new §13 Bitcoin/Lightning service-layer enforcement.
- [x] Update `mapping-erc3643.md` §11 cross-network equivalence table (Ethereum vs XRPL vs Bitcoin/Lightning); `forcedTransfer()` row references XRPL Native Clawback.
- [x] Create `docs/compliance/enforcement-tiers.md` — normative three-tier model (Tier 1: ERC-3643 on-chain, Tier 2: XRPL protocol, Tier 3: Bitcoin/Lightning service-layer).
- [x] Create `docs/mappings/mapping-bitcoin-lightning.md` — service-layer enforcement pattern, LSP providers, Layer-2 scope (RGB, Taproot Assets, Liquid).
- [x] Update TypeScript types (`typescript-types.md`) — add `BlockchainAccountId`, `XrplConfidentialTransfer`, v1.2.0–v1.7.0 `KYCProfile` fields, `VerificationDocumentBundle` types.
- [x] Update Pydantic models (`pydantic-models.md`) — add note on v1.4.0–v1.7.0 additions not yet in `models.py` generated stubs.
- [x] Update ER diagram to include v1.4.0–v1.7.0 entities (TrustDetails, FoundationDetails, PartnershipDetails, BlockchainAccountId, XrplConfidentialTransfer, VerificationDocumentBundle, and supporting types).
- [x] Update all diagram and document version footers to v1.7.0.