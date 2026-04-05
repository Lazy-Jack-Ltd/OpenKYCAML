# OpenKYCAML Roadmap

This document outlines the planned development of the OpenKYCAML standard.

---

## Current Version: v1.0.0

**Released:** June 2024

**Highlights:**
- Full IVMS 101 v1.0 payload support (backward-compatible superset).
- Optional W3C Verifiable Credential wrapper (eIDAS 2.0 / ARF-aligned).
- Full `kycProfile` section: risk rating, PEP, sanctions, adverse media, UBOs, monitoring, audit trail.
- Python and JavaScript validator tools.
- IVMS 101 ↔ OpenKYCAML converter (Python).
- Compliance matrix for FATF, AMLR, IVMS 101, ISO 20022, GLEIF, eIDAS 2.0, GDPR.
- GitHub Actions CI for schema and example validation.

---

## v1.1.0 — Planned Q3 2024

**Theme: Enhanced Identity & Trust Anchors**

| Feature | Status | Issue |
|---|---|---|
| TypeScript type definitions (auto-generated from schema) | Planned | — |
| Pydantic v2 models (auto-generated from schema) | Planned | — |
| IBAN / account number format validation | Planned | — |
| Trust registry endpoint field (`kycProfile.trustRegistryUrl`) | Planned | — |
| Trust framework field (`verifiableCredential.trustFramework`) | Planned | — |
| eIDAS 2.0 PID (Person Identification Data) attribute mapping | Planned | — |
| Support for `SD-JWT` selective disclosure notation | Planned | — |
| Go validator / Pydantic model | Planned | — |

---

## v1.2.0 — Planned Q4 2024

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

## v2.0.0 — Planned 2025

**Theme: AMLR 2027 Readiness**

This major version will be timed to align with the EU AMLR full applicability date (1 July 2027), giving adopters a 2-year migration window.

Planned breaking changes (subject to TWG consensus):
- Remove deprecated IVMS 101 fields no longer required by updated standards.
- Require `kycProfile.auditMetadata` for all CDD records (currently optional).
- Align `verifiableCredential` structure with final W3C VC Data Model v2.0 spec and final eIDAS 2.0 ARF.

---

## Completed

| Version | Date | Change |
|---|---|---|
| v1.0.0 | June 2024 | Initial release |

---

## How to Influence the Roadmap

1. Open an issue with the label `type: enhancement` or `type: rfc`.
2. Join the [GitHub Discussions](https://github.com/Lazy-Jack-Ltd/openKYCAML/discussions).
3. Attend TWG calls (schedule posted in Discussions).
4. See [GOVERNANCE.md](GOVERNANCE.md) for the formal decision process.
