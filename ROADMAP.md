# OpenKYCAML Roadmap

This document outlines the planned development of the OpenKYCAML standard.

---

## Current Version: v1.1.0

**Released:** April 2025

**Highlights:**
- Full IVMS 101 v1.0 payload support (backward-compatible superset).
- Optional W3C Verifiable Credential wrapper (eIDAS 2.0 / ARF-aligned), with W3C VC `evidence` block for EUDI Wallet source credential attribution.
- Native **eIDAS 2.0 LPID** (Legal Person Identification Data) support with QEAA mandate/representative fields.
- `EUDI_WALLET` onboarding channel (AMLR Art. 22(5) high-assurance remote CDD).
- Full `kycProfile` section: risk rating, PEP, sanctions, adverse media, UBOs, monitoring, audit trail.
- **12 validated example payloads** — every scenario covered in both a plain IVMS 101 baseline and an EUDI Wallet / DID-triangulated VC-wrapped version.
- Python and JavaScript validator tools.
- IVMS 101 ↔ OpenKYCAML converter (Python).
- Compliance matrix for FATF, AMLR, IVMS 101, ISO 20022, GLEIF, eIDAS 2.0, GDPR.
- GitHub Actions CI for schema and example validation.
- ISO 17442-valid example LEIs throughout all payloads.

---

## v1.2.0 — Planned Q3 2025

**Theme: Tooling, Type Safety & Selective Disclosure**

| Feature | Status | Issue |
|---|---|---|
| TypeScript type definitions (auto-generated from schema) | Planned | — |
| Pydantic v2 models (auto-generated from schema) | Planned | — |
| IBAN / crypto account number format validation | Planned | — |
| Trust registry endpoint field (`kycProfile.trustRegistryUrl`) | Planned | — |
| Trust framework field (`verifiableCredential.trustFramework`) | Planned | — |
| Support for `SD-JWT` selective disclosure notation | Planned | — |
| Go validator | Planned | — |
| OpenID4VP presentation request / response cookbook | Planned | — |

---

## v1.3.0 — Planned Q4 2025

**Theme: Institutional and Cross-Border Interoperability**

| Feature | Status | Issue |
|---|---|---|
| Correspondent banking extension fields | Planned | — |
| Trust chain / CDD reliance chain tracking (`kycProfile.cddRelianceChain`) | Planned | — |
| Multi-jurisdiction risk model fields | Planned | — |
| SAR/STR flag field (`kycProfile.sarFiled`) | Planned | — |
| FATCA / CRS tax residency extension | Planned | — |
| ISO 20022 pain.001 full serialiser (Python) | Planned | — |
| TRISA / OpenVASP protocol integration cookbook | Planned | — |

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

---

## How to Influence the Roadmap

1. Open an issue with the label `type: enhancement` or `type: rfc`.
2. Join the [GitHub Discussions](https://github.com/Lazy-Jack-Ltd/openKYCAML/discussions).
3. Attend TWG calls (schedule posted in Discussions).
4. See [GOVERNANCE.md](GOVERNANCE.md) for the formal decision process.

