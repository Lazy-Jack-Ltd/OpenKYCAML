# OpenKYCAML — AMLR Requirements Reference

> **Summary document.** This file provides a concise mapping of EU Anti-Money Laundering Regulation (AMLR) requirements to OpenKYCAML schema fields and tooling. For the full implementer compliance checklist, see [`amlr-2027-compliance-checklist.md`](amlr-2027-compliance-checklist.md). For the full regulatory-to-schema field mapping, see [`compliance-matrix.md`](compliance-matrix.md).

---

## AMLR Quick-Reference: Key Articles and Schema Coverage

| AMLR Article | Subject | OpenKYCAML Schema Field(s) | Checklist Section |
|---|---|---|---|
| **Art. 2** | Scope — obliged entities (banks, PSPs, CASPs/VASPs, etc.) | — | §1 |
| **Art. 20** | Risk-based approach — customer risk assessment | `kycProfile.customerRiskRating`, `kycProfile.riskFactors` | §2 |
| **Art. 22** | CDD — identity verification (eIDAS / EUDI Wallet accepted) | `ivms101.originator/beneficiary`, `verifiableCredential`, `kycProfile.onboardingChannel` = `EUDI_WALLET` | §3 |
| **Art. 22(5)** | High-assurance remote CDD via EUDI Wallet | `kycProfile.onboardingChannel` = `EUDI_WALLET`, `verifiableCredential.evidence` (DID triangulation) | §3 |
| **Art. 26** | Enhanced CDD — legal entities and beneficial ownership disclosure | `kycProfile.beneficialOwnership[]`, `ivms101.*.legalPerson`, `beneficialOwnership[].ownershipChainDepth` | §4 |
| **Art. 28–31** | PEP identification and enhanced measures | `kycProfile.pepStatus.isPEP`, `kycProfile.pepStatus.pepCategory` (AMLA PEP taxonomy) | §5 |
| **Art. 29** | Enhanced due diligence (EDD) triggers | `kycProfile.dueDiligenceType` = `EDD`, `kycProfile.sourceOfFundsWealth` | §5 |
| **Art. 48** | Third-party CDD reliance conditions | `kycProfile.thirdPartyCDDReliance` (`relyingPartyId`, `relianceScope`, `accessToUnderlyingDataConfirmed`) | §6 |
| **Art. 56** | Record-keeping — 5-year minimum retention | `kycProfile.auditMetadata.dataRetentionDate`, `kycProfile.auditMetadata.changeLog` | §7 |
| **Art. 73** | Tipping-off prohibition — SAR/STR confidentiality | `gdprSensitivityMetadata.tippingOffProtected`, `gdprSensitivityMetadata.disclosurePolicy.prohibitedRecipients` | §10–11 |

---

### 1. AMLR Timeline and Scope (Directly Applicable Single Rulebook)
- **Entry into force**: 10 July 2027 (full application; no national transposition needed).
- **Scope**: All obliged entities (banks, payment providers, crypto-asset service providers/CASPs/VASPs, crowdfunding platforms, etc.) across the EU.
- **Core goal**: Harmonise CDD/KYC rules, reduce fragmentation, and explicitly embrace trusted digital identity to support remote onboarding while maintaining a risk-based approach.

AMLR replaces and strengthens parts of the old AML Directives with directly binding rules.

### 2. Key AMLR Integration Requirements for KYC/CDD
AMLR Article 22 (and recitals) is the centrepiece for **remote customer due diligence** and identity verification:

| Requirement | AMLR Detail | Relevance to Your Schema / App |
|-------------|-------------|--------------------------------|
| **Electronic identification acceptance** | Must accept eIDAS-compliant electronic identification means at **"substantial" or "high" assurance level** (or qualified trust services when eID unavailable). | The **VerifiableCredential** wrapper (W3C VC v1.1 + SD-JWT support) matches eIDAS 2.0 / EUDI Wallet exactly. EUDI Wallets will be the primary high-assurance channel by end-2027. |
| **EUDI Wallet mandate** | Obliged entities **must accept** the European Digital Identity Wallet (EUDI) for identification/authentication where strong user authentication is required (cross-referenced with eIDAS Article 5f). | Hybrid schema lets you ingest wallet-presented credentials directly (selective disclosure of PID/LPID attributes) and embed them in `credentialSubject.ivms101`. |
| **Attribute verification** | Verify identity against authoritative sources via eIDAS methods. AMLA will issue RTS specifying required attribute sets for standard/simplified/enhanced DD. | The mapping table (IVMS 101 ↔ eIDAS PID/LPID) covers the expected fields (name, DOB, address, national ID, LEI, etc.). See [`mapping-ivms101-eidas-amlr.md`](../mappings/mapping-ivms101-eidas-amlr.md). |
| **Record-keeping & evidence** | Retain full evidence of verification (including cryptographic proofs from eIDAS). | `proof` field in the VC wrapper + IVMS 101 payload provides auditable, tamper-evident records. |
| **Risk-based flexibility** | High-assurance eIDAS methods can reduce risk rating to standard/low (with appropriate controls). | Using the VC path in the schema can justify lighter ongoing monitoring. |
| **Legal entities / beneficial owners** | Same rules apply to legal persons and UBO verification (Art. 26 chain disclosure). | `legalPerson` block + `kycProfile.beneficialOwnership[]` with `intermediateEntities[]` and `ownershipChainDepth`. |

Additional AMLR provisions relevant to data sharing:
- Reliance on third-party CDD (Art. 48) — with conditions and contractual access to underlying data; use `kycProfile.thirdPartyCDDReliance`.
- Group-wide data sharing (with safeguards) — use `kycProfile.auditMetadata` provenance fields.
- No new mandates conflicting with IVMS 101 for Travel Rule (crypto transfers remain zero-threshold in the EU and continue to use IVMS 101 as the interoperability standard; primary basis is TFR 2023/1113 Art. 14).

---

### 3. AMLA RTS Status (as of April 2026)

The EU Anti-Money Laundering Authority (AMLA) is drafting Regulatory Technical Standards under several AMLR Articles. The following are most relevant to OpenKYCAML:

| RTS Topic | AMLR Basis | Schema Impact | Status |
|---|---|---|---|
| CDD attribute sets (standard / SDD / EDD) | Art. 22 | May specify exactly which `ivms101` and `kycProfile` fields are required per DD tier | Draft expected 2025–2026 |
| PEP category list | Art. 28–31 | `kycProfile.pepStatus.pepCategory` — aligned to AMLA draft taxonomy | Draft taxonomy implemented in v1.2.0 |
| Third-party CDD reliance conditions | Art. 48 | `kycProfile.thirdPartyCDDReliance` field set | Final RTS pending |

---

*Last updated: v1.12.0 — April 2026. For the full implementer checklist see [`amlr-2027-compliance-checklist.md`](amlr-2027-compliance-checklist.md).*
