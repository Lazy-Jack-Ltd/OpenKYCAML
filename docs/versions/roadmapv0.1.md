# OpenKYCAML Roadmap

## v1.0.0 — Launched (April 2026)
- Full hybrid schema (IVMS 101 + eIDAS 2.0 VC wrapper + kycProfile)
- Python & JavaScript validators
- 5 realistic examples
- Complete documentation & compliance matrix
- Governance model and contributor guidelines

## v1.1.0 — Released Q2 2026 ✅
- Official SD-JWT selective disclosure examples for EUDI Wallet (`natural-person-sd-jwt-eudi-wallet.json`, `legal-entity-sd-jwt-eudi-wallet.json`)
- Additional converters: PID/LPID ↔ OpenKYCAML (Python `converter.py`)
- Enhanced beneficial ownership depth: `intermediateEntities[]`, `ownershipChainDepth` (deep UBO example: `legal-entity-deep-ubo.json`)
- Travel Rule implementation guide for TRISA, OpenVASP, Notabene/DAP, TRP, Sygna Bridge

## v1.2.0 — Released Q2 2026 ✅
- **AMLA RTS alignment** (post-draft consultation):
  - `kycProfile.thirdPartyCDDReliance` block — structured CDD reliance record per AMLR Art. 48(3): relying/providing party, reliance scope, contract reference, access-to-data confirmation, liability note.
  - `kycProfile.dueDiligenceRequirements` block — machine-readable DD tier + verified attribute record per AMLR Art. 22; designed to track binding attribute sets once the AMLA RTS on CDD attribute sets is published.
  - `kycProfile.pepStatus.pepCategory` — consolidated AMLA draft RTS taxonomy: `DOMESTIC_PEP`, `FOREIGN_PEP`, `INTERNATIONAL_ORGANISATION`, `FAMILY_MEMBER_OF_PEP`, `CLOSE_ASSOCIATE_OF_PEP`, `FORMER_PEP`, `NOT_PEP` (AMLR Art. 28–31).
- Compliance matrix updated to v1.2.0 (SD-JWT, deep UBO, PID/LPID, new AMLA RTS alignment section with pending-RTS tracking).
- AMLR 2027 compliance checklist (`docs/amlr-2027-compliance-checklist.md`).
- ⚠ Items pending AMLA RTS publication (to be finalised in v1.3.0 or v2.0.0 once binding RTS adopted):
  - CDD attribute sets per tier (Art. 22(4) RTS)
  - EDD measures for high-risk third countries (Art. 29(4) RTS)
  - Final PEP category names (Art. 28(3)/Art. 31 RTS)
  - Group-wide policy and data-sharing RTS (Art. 15(5))
- Certification badge program for adopters
- Hosted public validator service (openkycaml.org)

## v2.0.0 — 2027 (AMLR go-live)
- Full support for Qualified Electronic Attestations of Attributes (QEAA)
- Machine-readable SAR/reporting extensions
- Formal submission to AMLA and FATF as recommended open standard

## Long-term
- Integration with ISO 20022 payment messages
- Decentralized identity (DID) extensions
- Community-led governance transition

**How to influence the roadmap**  
Open a GitHub Issue with the label `roadmap` or join the monthly community call (link in GOVERNANCE.md).

*Last updated: April 2026*
