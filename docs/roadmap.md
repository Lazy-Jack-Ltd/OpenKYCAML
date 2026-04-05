# OpenKYCAML Documentation Roadmap

> For the project roadmap, see [`../ROADMAP.md`](../ROADMAP.md).

This page tracks documentation-specific improvements planned for upcoming releases.

## Documentation Backlog

### v1.1
- [ ] Add TypeScript type definitions documentation.
- [ ] Add Pydantic model documentation (auto-generated from schema).
- [ ] Add sequence diagrams for Travel Rule message flows.
- [ ] Add sequence diagrams for eIDAS 2.0 VC issuance and presentation flows.
- [ ] Add Mermaid entity-relationship diagram for the full schema.

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
