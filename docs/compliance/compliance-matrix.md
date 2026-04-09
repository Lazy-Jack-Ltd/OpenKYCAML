# OpenKYCAML Compliance Matrix

This matrix documents the alignment of the OpenKYCAML v1.7.0 schema with major regulatory and technical standards.

**Legend:**
- ✅ Full alignment — the standard is directly addressed.
- 🟡 Partial alignment — the standard is partially addressed; notes explain scope.
- ⬜ Not in scope — explicitly out of scope or addressed by the transport layer.

---

## 1. FATF Recommendations

| FATF Recommendation | Coverage in OpenKYCAML | Relevant Schema Fields |
|---|---|---|
| **Rec 1** — Risk-based approach | ✅ | `kycProfile.customerRiskRating`, `kycProfile.dueDiligenceType` |
| **Rec 6** — Targeted financial sanctions | ✅ | `kycProfile.sanctionsScreening` |
| **Rec 10** — Customer due diligence | ✅ | `ivms101.originator`, `kycProfile.customerClassification`, `kycProfile.dueDiligenceType`, `kycProfile.beneficialOwnership` |
| **Rec 11** — Record keeping | ✅ | `kycProfile.auditMetadata` |
| **Rec 12** — Politically Exposed Persons | ✅ | `kycProfile.pepStatus`, `kycProfile.sourceOfFundsWealth` |
| **Rec 15** — New technologies (VASPs) | ✅ | Full IVMS 101 support; `kycProfile.customerClassification` = `VASP` |
| **Rec 16** — Wire transfers / Travel Rule | ✅ | `ivms101` block (IVMS 101 v1.0 superset), `ivms101.transferredAmount`, originating/beneficiary VASP fields |
| **Rec 20** — Reporting of suspicious transactions | 🟡 | `kycProfile.monitoringInfo.alerts` (SAR trigger fields); `gdprSensitivityMetadata.classification` = `sar_restricted` marks SAR-linked data — SAR submission itself is out of scope |
| **Rec 21** — Tipping-off and confidentiality | ✅ | `gdprSensitivityMetadata.tippingOffProtected` (AMLR Art. 73 / FATF Rec. 21); `disclosurePolicy.prohibitedRecipients` blocks disclosure to data subject; cryptographic withholding via SD-JWT `_sd` digests without appended disclosures (added v1.3.0) |
| **Rec 24** — Beneficial ownership of legal persons | ✅ | `kycProfile.beneficialOwnership[]`; `legalPerson.legalFormCode` (ISO 20275:2017 ELF code, v1.4.0); `legalPerson.entityType` typed classification |
| **Rec 25** — Beneficial ownership of legal arrangements | ✅ | `kycProfile.beneficialOwnership` covers natural-person and legal-person beneficial owners for trusts, foundations, and LLPs. `legalPerson.entityType` = `TRUST`/`FOUNDATION`/`PARTNERSHIP` drives typed sub-objects (`trustDetails`, `foundationDetails`, `partnershipDetails`) that explicitly capture settlor, trustee, protector, beneficiary class, founders, council members, and partner roles (v1.4.0). See `legal-entity-trust.json`, `legal-entity-partnership.json`, `trust-complex-ubo.json`, `foundation-complex-ubo.json`, `llp-complex-ubo.json`. |

---

## 2. EU Anti-Money Laundering Regulation (AMLR 2024)

> _Regulation (EU) 2024/1624 — applicable from 1 July 2027_

| AMLR Article | Topic | Coverage | Relevant Schema Fields |
|---|---|---|---|
| **Art. 15** — Risk-based approach | RBA framework | ✅ | `kycProfile.customerRiskRating` |
| **Art. 20** — Risk assessment | Risk factors | ✅ | `kycProfile.customerRiskRating.riskFactors` |
| **Art. 21** — Ongoing monitoring | Transaction and relationship monitoring | ✅ | `kycProfile.monitoringInfo` |
| **Art. 22(1)** — CDD measures | SDD / CDD / EDD | ✅ | `kycProfile.dueDiligenceType` |
| **Art. 22(2)** — CDD data required | Name, DoB, address, ID | ✅ | `ivms101.originator.originatorPersons[].naturalPerson.*` |
| **Art. 22(5)** — Remote / third-party CDD | Reliable electronic means; third-party reliance | ✅ | `verifiableCredential` wrapper; `kycProfile.onboardingChannel` |
| **Art. 24** — Targeted financial sanctions | Sanctions screening | ✅ | `kycProfile.sanctionsScreening` |
| **Art. 26** — Beneficial owners | UBOs of legal entities and legal arrangements | ✅ | `kycProfile.beneficialOwnership[]`; `legalPerson.entityType` + `trustDetails` / `foundationDetails` / `partnershipDetails` typed sub-objects capturing settlors, trustees, protectors, beneficiary class, founders, council members, and partners (v1.4.0, ISO 20275:2017 aligned) |
| **Art. 28–31** — PEP provisions | PEP identification and EDD | ✅ | `kycProfile.pepStatus` |
| **Art. 29** — EDD measures | Enhanced due diligence | ✅ | `kycProfile.dueDiligenceType` = `EDD`, `kycProfile.sourceOfFundsWealth` |
| **Art. 56** — Record keeping | 5-year minimum retention | ✅ | `kycProfile.auditMetadata.dataRetentionDate`, `changeLog` |
| **Art. 73** — Tipping-off prohibition | Prohibition on disclosing SAR/STR existence to data subject or unauthorised parties | ✅ | `gdprSensitivityMetadata.tippingOffProtected`; `gdprSensitivityMetadata.disclosurePolicy.prohibitedRecipients` (includes `"data_subject"`); SD-JWT cryptographic withholding of SAR fields; `gdprSensitivityMetadata.classification` = `sar_restricted` or `internal_suspicion` (added v1.3.0) |
| **Art. 48** — CDD reliance on third parties | Third-party reliance conditions, written arrangement, access to data | ✅ | `kycProfile.thirdPartyCDDReliance` (`relyingPartyId`, `providingPartyId`, `relianceScope`, `relianceContractRef`, `accessToUnderlyingDataConfirmed`, `providingPartyEligibilityConfirmed`, `liabilityNote`) |
| **Art. 83** — Transfer of funds (Travel Rule) | VASP Travel Rule obligations | ✅ | `ivms101` block |

---

## 3. EU Funds Transfer Regulation (TFR) 2023/1113 and EU Markets in Crypto Assets (MiCA) Regulation

> **Note on legal basis:** The EU Travel Rule obligation for crypto-asset transfers is primarily set out in **EU Funds Transfer Regulation (TFR) 2023/1113 Art. 14**. MiCA Art. 83 cross-references the TFR but the TFR is the operative instrument. Both are cited below for completeness.

| TFR / MiCA Article / Provision | Coverage | Notes |
|---|---|---|
| **TFR 2023/1113 Art. 14** — Transfer of crypto-assets (Travel Rule) | ✅ | `ivms101` block supports full VASP Travel Rule payload per IVMS 101; primary EU legal basis for crypto-asset transfer data requirements |
| **MiCA Art. 83** — Transfer of crypto-assets (cross-reference to TFR) | ✅ | Cross-references TFR 2023/1113 Art. 14; `ivms101` block satisfies both provisions |
| **Art. 68** — VASP authorisation | ⬜ | Out of scope — operational, not data model |
| **Art. 82** — Customer onboarding | 🟡 | `kycProfile.onboardingChannel`, `kycProfile.kycCompletionDate` |

---

## 4. IVMS 101 (InterVASP Messaging Standard v1.0)

| IVMS 101 Section | Coverage | Notes |
|---|---|---|
| §3.2 — NaturalPersonName | ✅ | `NaturalPersonNameIdentifier` — all name identifier types supported (ALIA, BIRT, MAID, LEGL, MISC) |
| §3.3 — DateAndPlaceOfBirth | ✅ | `DateAndPlaceOfBirth` |
| §3.4 — NaturalPersonNationalIdentification | ✅ | `NationalIdentification` — all types (ARNU, CCPT, RAID, DRLC, FIIN, TXID, SOCS, IDCD, LEIX, MISC) |
| §3.5 — Address | ✅ | `Address` — all 14 structured fields + unstructured `addressLine[]` |
| §3.6 — CountryOfResidence | ✅ | `NaturalPerson.countryOfResidence` |
| §3.7 — CustomerIdentification | ✅ | `customerIdentification` on both `NaturalPerson` and `LegalPerson` |
| §3.8 — LegalPersonName | ✅ | `LegalPersonNameIdentifier` — LEGL, SHRT, TRAD |
| §3.9 — LegalPersonNationalIdentification | ✅ | `NationalIdentification` with LEIX type and `registrationAuthority` |
| §3.10 — CountryOfRegistration | ✅ | `LegalPerson.countryOfRegistration` |
| §4 — TransferredAmount | ✅ | `transferredAmount.amount`, `transferredAmount.assetType` |
| §5 — OriginatingVASP / BeneficiaryVASP | ✅ | `originatingVASP`, `beneficiaryVASP` |

**Backward compatibility:** A validator accepting IVMS 101 JSON payloads will also accept the `ivms101` block of any OpenKYCAML payload.

---

## 5. eIDAS 2.0 / EU Digital Identity Architecture and Reference Framework (ARF)

| ARF Component | Coverage | Relevant Schema Fields |
|---|---|---|
| W3C VC Data Model v2 | ✅ | `verifiableCredential` block |
| VC Issuer (PID Issuer) | ✅ | `verifiableCredential.issuer` (DID URL) |
| VC Subject (User DID) | ✅ | `verifiableCredential.credentialSubject.id` |
| Credential Status / Revocation | ✅ | `verifiableCredential.credentialStatus` (StatusList2021) |
| Proof suites (Ed25519, JWS, DataIntegrity) | ✅ | `verifiableCredential.proof.type` |
| PID (Person Identification Data) — natural persons | ✅ | `NaturalPerson.*` fields with eIDAS attribute annotations (`family_name`, `given_name`, `birth_date`, `resident_address`, etc.) |
| **LPID (Legal Person Identification Data)** — legal entities | ✅ | `legalPerson.lpid` — `LegalPersonIdentificationData` definition; covers mandatory (`currentLegalName`, `uniqueIdentifier`) and optional attributes (`lei`, `vatRegistrationNumber`, `taxReferenceNumber`, `eoriNumber`, `europeanUniqueIdentifier`, `currentAddress`) |
| **QEAA / Representation & Mandates** | ✅ | `legalPerson.lpid.mandates[]` — natural person representatives with `roleOrPower`, `validFrom`/`validUntil`; supports AMLR authorised representative and UBO verification |
| LPID in VC credentialSubject | ✅ | `verifiableCredential.credentialSubject.lpid` — standalone LPID VC for EUDI Wallet issuance flows |
| OpenID4VCI (issuance) | ⬜ | Transport protocol — out of schema scope |
| OpenID4VP (presentation) | ⬜ | Transport protocol — out of schema scope |
| SD-JWT selective disclosure | ✅ | `verifiableCredential.selectiveDisclosure` block: `_sd_alg`, `disclosableClaimPaths`, `requiredClaimPaths`, `decodedDisclosures` (added v1.2.0); SAR-restricted fields withheld via `_sd` digests only — no disclosures appended (v1.3.0 tipping-off pattern) |

---

## 6. ISO 20022

| ISO 20022 Element | Coverage | Notes |
|---|---|---|
| `pain.001` — Credit Transfer | ✅ | Full XML serialiser via `openkycaml_to_pain001()` — see [`iso20022-integration/libraries/python/`](../../iso20022-integration/libraries/python/) |
| `pacs.008` — FI Credit Transfer (CBPR+) | ✅ | Full XML serialiser via `openkycaml_to_pacs008()` + Travel Rule profile — see [`iso20022-integration/profiles/travel-rule-pacs.008-profile.json`](../../iso20022-integration/profiles/travel-rule-pacs.008-profile.json) |
| `camt.053` — Bank-to-Customer Statement | ✅ | Audit trail + data-retention profile — see [`iso20022-integration/profiles/camt.053-kyc-audit-profile.json`](../../iso20022-integration/profiles/camt.053-kyc-audit-profile.json) |
| `<SplmtryData>` KYCAMLEnvelope schema | ✅ | JSON Schema for the envelope embedded in `<Envlp>` — [`iso20022-integration/supplementary-data/kyc-aml-envelope-schema.json`](../../iso20022-integration/supplementary-data/kyc-aml-envelope-schema.json) |
| pacs.008 CBPR+ profile | ✅ | FATF Rec 16 + TFR 2023/1113 Art. 14 / MiCA Art. 83 minimum required fields defined |
| pain.001 CDD reliance profile | ✅ | AMLR Art. 48 `thirdPartyCDDReliance` + risk rating in `<SplmtryData>` |
| camt.053 audit profile | ✅ | `auditMetadata.changeLog` + `dataRetentionDate` in `<SplmtryData>` |
| Python converter (bidirectional) | ✅ | `openkycaml_to_pacs008`, `openkycaml_to_pain001`, `iso20022_to_openkycaml` |
| TypeScript ESM converter (bidirectional) | ✅ | Same three functions, typed interfaces — [`iso20022-integration/libraries/typescript/`](../../iso20022-integration/libraries/typescript/) |
| XML examples | ✅ | pacs.008 + pain.001 full messages + minimal copy-paste snippet |
| Bidirectional field mapping YAML | ✅ | [`iso20022-integration/mapping/`](../../iso20022-integration/mapping/) — 14 clean 1:1 mappings, ~12 transformations, ~30 SplmtryData-only fields documented |
| LEI (`LEIX` type) | ✅ | `nationalIdentification.nationalIdentifierType` = `"LEIX"`, `registrationAuthority` per GLEIF |
| BIC/SWIFT (RAID type) | ✅ | `nationalIdentification.nationalIdentifierType` = `"RAID"` |
| IBAN | ✅ | Detected by pattern and mapped to dedicated `<IBAN>` element; non-IBAN accounts to `<Othr>` |
| Formal XSD validation in CI | 🟡 | Planned v1.4 |

---

## 7. GLEIF / Legal Entity Identifier (LEI)

| LEI Requirement | Coverage | Notes |
|---|---|---|
| LEI code (20-char ISO 17442) | ✅ | `nationalIdentification.nationalIdentifier` with type `LEIX` |
| Registration Authority code | ✅ | `nationalIdentification.registrationAuthority` |
| Level 2 data (UBOs) | ✅ | `kycProfile.beneficialOwnership[]` — maps to GLEIF Level 2 / Relationship Records |

---

## 8. General Data Protection Regulation (GDPR)

| GDPR Requirement | Coverage | Notes |
|---|---|---|
| Lawful basis for processing (Art. 6) | ✅ | `kycProfile.consentRecord.consentPurpose` for consent; `gdprSensitivityMetadata.legalBasis` enumerates the applicable Art. 6/9/10 or AMLR legal basis per payload (added v1.3.0) |
| Consent record (Art. 7) | ✅ | `kycProfile.consentRecord`; `gdprSensitivityMetadata.consentRecord` for sensitivity-specific consent |
| Right to erasure (Art. 17) | 🟡 | `kycProfile.auditMetadata.dataRetentionDate` supports scheduled deletion; erasure workflow is operational |
| Data minimisation (Art. 5(1)(c)) | ✅ | All fields optional except those required for compliance; schema supports minimal payloads |
| Special categories (Art. 9) — biometrics, criminal suspicion | ✅ | `gdprSensitivityMetadata.classification` = `sensitive_personal` or `sar_restricted`; `legalBasis` = `GDPR-Art9-2g` (substantial public interest); machine-readable classification enables automated enforcement in EUDI Wallet flows (added v1.3.0) |
| Criminal convictions and offences (Art. 10) | ✅ | `gdprSensitivityMetadata.classification` = `criminal_offence`; `legalBasis` = `GDPR-Art10`; `tippingOffProtected` flag prevents disclosure of pending allegations (added v1.3.0) |
| Sensitivity / SAR classification | ✅ | `gdprSensitivityMetadata` block — `classification`, `restrictedFields`, `tippingOffProtected`, `disclosurePolicy`, `retentionPeriod`, `auditReference`; ISO 8601 retention periods with pattern validation (added v1.3.0) |

---

## 10. ERC-3643 (T-REX) — On-Chain Permissioned Token Standard

> ERC-3643 is the Ethereum standard for regulated / security token issuance. It uses ONCHAINID (ERC-734/735) to manage investor identities on-chain. The full field-level mapping is in [mapping-erc3643.md](../mappings/mapping-erc3643.md).

| ERC-3643 Data Point | Coverage | OpenKYCAML Field(s) |
|---|---|---|
| **Investor wallet address** (`investorAddress`) | ✅ | `kycProfile.blockchainAccountIds[].address` |
| **ONCHAINID contract address** (`identity`) | ✅ | `kycProfile.blockchainAccountIds[].onchainIDAddress` |
| **Investor country** (`investorCountry`, uint16 ISO 3166-1 numeric) | ✅ | `ivms101.*.naturalPerson.countryOfResidence` (alpha-2; numeric conversion documented in mapping) |
| **Eligibility flag** (`isVerified()`) | ✅ | `kycProfile.isEligible` (boolean) |
| **Eligibility date** (last confirmed) | ✅ | `kycProfile.eligibilityLastConfirmed` |
| **Wallet frozen** (`isFrozen(address)`) | ✅ | `kycProfile.blockchainAccountIds[].isFrozen` |
| **Frozen token amount** (`getFrozenTokens(address)`) | ✅ | `kycProfile.blockchainAccountIds[].frozenTokenAmount` |
| **Claim topic 1 — KYC** | ✅ | `kycProfile.kycCompletionDate` + `kycProfile.dueDiligenceRequirements` |
| **Claim topic 2 — AML** | ✅ | `kycProfile.sanctionsScreening` + `kycProfile.adverseMedia` |
| **Claim topic 3 — Country** | ✅ | `ivms101.*.naturalPerson.countryOfResidence` |
| **Claim topic 101 — Accredited Investor** | ✅ | `kycProfile.customerClassification.accreditedInvestor` + `investorCategoryJurisdiction` |
| **Claim issuer** (`issuer` address → DID) | ✅ | `verifiableCredential.issuer` + `verifiableCredential.evidence[].credentialIssuer` |
| **Claim signature** (ERC-735 signature bytes) | ✅ | `verifiableCredential.proof.proofValue` / `verifiableCredential.proof.jws` |
| **Claim data** (ABI-encoded payload) | ✅ | Structured JSON across `ivms101.*` and `kycProfile.*` |
| **Claim URI** | ✅ | `verifiableCredential.credentialSchema.id` |
| **Claim topic type** | ✅ | `verifiableCredential.type[]` |
| **ERC-734 Claim signing key** | ✅ | `verifiableCredential.proof.verificationMethod` |
| **Trusted Issuers Registry** (per issuer + topics) | 🔄 | `verifiableCredential.evidence[].credentialIssuer` (per credential); no central registry ref in the KYC record |
| **Claim Topics Registry** (required topics) | 🔄 | `kycProfile.dueDiligenceRequirements.verifiedAttributes[]` (attributes per DD tier) |
| **Transfer compliance (`canTransfer`)** | 🔄 | Off-chain: `kycProfile.isEligible` + `kycProfile.customerRiskRating` + `kycProfile.sanctionsScreening` |
| **Token contract metadata** (name, symbol, decimals) | ℹ️ | Out of scope — token-level, not investor KYC |

_✅ = full field mapping. 🔄 = conceptual equivalent (see [mapping-erc3643.md](../mappings/mapping-erc3643.md)). ℹ️ = out of scope._

> _AMLA (Anti-Money Laundering Authority, established under Regulation (EU) 2024/1620) is mandated to issue Regulatory Technical Standards (RTS) and Guidelines under the AMLR. Several RTS are anticipated but not yet published as of April 2026. This section tracks alignment with draft and final RTS._

| AMLA RTS Topic | Expected Legal Basis | Status | OpenKYCAML Coverage |
|---|---|---|---|
| **RTS on CDD attribute sets** — mandatory attribute sets for SDD, CDD, and EDD tiers | AMLR Art. 22(4) | 🟡 Pending AMLA RTS publication | `kycProfile.dueDiligenceRequirements` captures applied tier and verified attributes; `dueDiligenceType` enum (SDD / CDD / EDD). Field designed to be updated once the binding RTS attribute lists are published. |
| **RTS on EDD for high-risk third countries** — specific EDD measures | AMLR Art. 29(4) | 🟡 Pending AMLA RTS publication | `kycProfile.riskRatingDetail.riskFactors.geographicRisk`; `kycProfile.dueDiligenceType` = `EDD`; `kycProfile.monitoringInfo.eddRequired`. |
| **RTS on CDD reliance conditions** — conditions, form of written arrangement, access to underlying data | AMLR Art. 48(5) | ✅ Schema ready | `kycProfile.thirdPartyCDDReliance` block: `relyingPartyId`, `providingPartyId`, `relianceScope`, `relianceContractRef`, `relianceDate`, `accessToUnderlyingDataConfirmed`, `providingPartyEligibilityConfirmed`, `liabilityNote` (Art. 48(3)–(4)). |
| **RTS on PEP lists and harmonised category taxonomy** | AMLR Art. 28(3) / Art. 31 | 🟡 Pending AMLA RTS publication | `kycProfile.pepStatus.pepCategory` updated to AMLA draft taxonomy: `DOMESTIC_PEP`, `FOREIGN_PEP`, `INTERNATIONAL_ORGANISATION`, `FAMILY_MEMBER_OF_PEP`, `CLOSE_ASSOCIATE_OF_PEP`, `FORMER_PEP`, `NOT_PEP`. Enum will be finalised once RTS is adopted. |
| **RTS on remote CDD and electronic identification** — minimum assurance levels and accepted eID means | AMLR Art. 22(4) | ✅ Schema ready | `kycProfile.dueDiligenceRequirements.verificationMethods[].method` supports `EIDAS_HIGH`, `EIDAS_SUBSTANTIAL`, `EUDI_WALLET_PID`; `assuranceLevel` field (LOW / SUBSTANTIAL / HIGH). |
| **RTS on group-wide AML/CFT policies and data sharing** | AMLR Art. 15(5) | 🟡 Pending AMLA RTS publication | `kycProfile.auditMetadata.sharingConsentReference`; `dataProvider`; `thirdPartyCDDReliance`. |
| **Guidelines on risk factors** (successor to EBA Joint Guidelines) | AMLR Art. 20(6) | ✅ Schema ready | `kycProfile.riskRatingDetail.riskFactors` (geographic, product, channel, customer-type risk); `kycProfile.customerRiskRating`. |

---

## 11. Sovrin / Hyperledger Indy (AnonCreds) — Decentralised Identity Network

> Sovrin is a public permissioned blockchain for self-sovereign identity built on Hyperledger Indy, using AnonCreds (Camenisch-Lysyanskaya) zero-knowledge proof credentials. The full field-level mapping is in [mapping-sovrin.md](../mappings/mapping-sovrin.md).

| Sovrin / Indy Data Point | Coverage | OpenKYCAML Field(s) |
|---|---|---|
| **DID** (`did:sov:<base58>` / `did:indy:<ns>:<base58>`) | ✅ | `verifiableCredential.credentialSubject.id` |
| **Verification key** (Ed25519 base58 public key) | ✅ | `verifiableCredential.proof.verificationMethod` (DID URL) |
| **Credential Schema ID** (`<did>:2:<name>:<version>`) | ✅ | `verifiableCredential.credentialSchema.id` |
| **Credential Definition ID** (`<did>:3:CL:<seqNo>:<tag>`) | ✅ | `verifiableCredential.credentialSchema.credDefId` |
| **Revocation Registry ID** (CL_ACCUM accumulator) | ✅ | `verifiableCredential.credentialStatus.id` |
| **Revocation type** (`AnonCredsCredentialStatusList2023`) | ✅ | `verifiableCredential.credentialStatus.type` |
| **CL Proof type** (`CLSignature2019`, `AnonCredsProof2023`) | ✅ | `verifiableCredential.proof.type` |
| **Natural person attributes** (first_name, last_name, birth_date, address, document numbers) | ✅ | `ivms101.originator.*.naturalPerson.*` |
| **Legal entity attributes** (org_name, registration_number, LEI, jurisdiction) | ✅ | `ivms101.originator.*.legalPerson.*` |
| **KYC status** (`kyc_status`, `kyc_verified`) | ✅ | `kycProfile.isEligible` + `kycProfile.kycCompletionDate` |
| **Risk level** (`risk_level`) | ✅ | `kycProfile.customerRiskRating.overallRiskRating` |
| **AML check date** | ✅ | `kycProfile.sanctionsScreening.lastScreenedDate` |
| **UBO / beneficial owner** | ✅ | `kycProfile.beneficialOwnership[]` |
| **Selective disclosure / ZKP attributes** | ✅ | `verifiableCredential.selectiveDisclosure` |
| **Consent / TAA acceptance** (TAA mechanism, time, digest) | 🔄 | `kycProfile.consentRecord` (mechanism, timestamp, version) |
| **Rich Schema** (JSON_LD_CONTEXT, RICH_SCHEMA) | ✅ | `verifiableCredential.credentialSchema.id` (did:sov URI) + `@context[]` |
| **Rich Schema Credential Definition** (RICH_SCHEMA_CRED_DEF) | ✅ | `verifiableCredential.credentialSchema.credDefId` |
| **DID Document service endpoints** | ℹ️ | Out of scope — agent infrastructure, not KYC data |
| **Ledger transaction metadata** (seqNo, txnTime) | ℹ️ | Out of scope — network infrastructure |
| **NYM network roles** (TRUSTEE, STEWARD, ENDORSER) | ℹ️ | Out of scope — ledger governance, not investor KYC data |

_✅ = full field mapping. 🔄 = conceptual equivalent (see [mapping-sovrin.md](../mappings/mapping-sovrin.md)). ℹ️ = out of scope._

---

## 12. XRPL Credentials (XLS-70), DIDs (did:xrpl), Permissioned Domains (XLS-80), and Multi-Purpose Tokens (XLS-33d)

> XRPL Credentials (XLS-70, live on mainnet) provide an on-ledger anchor for W3C VCs; the `did:xrpl` DID method binds XRPL accounts to W3C DIDs; Permissioned Domains (XLS-80) and the Permissioned DEX (XLS-81d) gate access to trading venues; XLS-96 provides encrypted confidential transfers; and MPTs (Multi-Purpose Tokens) implement permissioned token issuance with KYC/AML gating analogous to ERC-3643. The full field-level mapping is in [mapping-xrpl-credentials-mpt.md](../mappings/mapping-xrpl-credentials-mpt.md).

| XRPL Data Point | Coverage | OpenKYCAML Field(s) |
|---|---|---|
| **`Credential.Subject`** (XRPL account → `did:xrpl`) — XLS-70 | ✅ | `verifiableCredential.credentialSubject.id` (`did:xrpl:1:r...`) |
| **`Credential.Issuer`** (XRPL account → `did:xrpl`) — XLS-70 | ✅ | `verifiableCredential.issuer.id` (`did:xrpl:1:r...`) |
| **`Credential.URI`** (off-chain VC payload URI) — XLS-70 | ✅ | `verifiableCredential.id` (canonical URI of the OpenKYCAML VC) |
| **`Credential.Expiration`** (Ripple epoch) — XLS-70 | ✅ | `verifiableCredential.expirationDate` (ISO 8601; Ripple epoch = Unix − 946684800) |
| **`Credential.CredentialType`** (hex-encoded type) — XLS-70 | 🔄 | `verifiableCredential.type[]` (decoded string; see hex→string table in mapping doc §2.2) |
| **`lsfAccepted`** (credential accepted by subject) — XLS-70 | 🔄 | `kycProfile.auditMetadata.changeLog[]` entry (`credential_accepted`) |
| **`DID` object** (`DIDDocument` + `URI`) — XLS-70 | ✅ | `verifiableCredential.credentialSubject.id` / `verifiableCredential.issuer.id` (DID resolves via XRPL DID resolver) |
| **`did:xrpl` DID method** | ✅ | All DID fields are DID-method-agnostic; `did:xrpl:1:r...` is a valid value |
| **DID triangulation** (subject / issuer / relying party) | ✅ | `verifiableCredential.evidence[].credentialIssuer` + `.verifier` + `credentialSubject.id` |
| **`DepositPreauth` credential gate** (`{Issuer, CredentialType}`) — XLS-70 | ✅ | `kycProfile.isEligible: true` + `verifiableCredential.type[]` (off-chain pre-authorisation record) |
| **Permissioned Domain ID** (Hash256) — XLS-80 | ✅ | `kycProfile.blockchainAccountIds[].xrplPermissionedDomainId` ⭐ (64-char hex; added v1.7.0) |
| **Permissioned Domain credential requirements** — XLS-80 | ✅ | `kycProfile.blockchainAccountIds[].xrplAuthorizedCredentialTypes[]` ⭐ (added v1.7.0) |
| **Permissioned DEX access gate** — XLS-81d | ✅ | `kycProfile.isEligible: true` + `xrplPermissionedDomainId` ⭐ — domain membership gates DEX offer matching |
| **Authorised Trustline** (IssuerAuthorizesTrustline) | ✅ | `kycProfile.isEligible: true` → triggers trustline auth by issuer |
| **`MPToken.lsfMPTAuthorized`** (holder authorised) | ✅ | `kycProfile.isEligible` (boolean) + `kycProfile.eligibilityLastConfirmed` |
| **`MPToken.lsfMPTLocked`** (holder frozen) | ✅ | `kycProfile.blockchainAccountIds[].isFrozen` |
| **Holder XRPL wallet address** | ✅ | `kycProfile.blockchainAccountIds[].address` (`network: "xrpl"`) |
| **`MPTIssuance.lsfMPTRequireAuth`** (gate flag) | 🔄 | `kycProfile.isEligible` — off-chain prerequisite for `MPTokenAuthorize` |
| **MPT flags bitmask** — XLS-33d | ✅ | `kycProfile.blockchainAccountIds[].mptFlags` ⭐ (added v1.7.0) |
| **MPT metadata / ISIN / compliance rules** — XLS-33d | ✅ | `kycProfile.blockchainAccountIds[].mptMetadata` ⭐ (added v1.7.0) |
| **MPT transfer fee** — XLS-33d | ✅ | `kycProfile.blockchainAccountIds[].mptTransferFee` ⭐ (added v1.7.0) |
| **Credential revocation** (`CredentialDelete`) | ✅ | `verifiableCredential.credentialStatus` (StatusList2021Entry) + `kycProfile.isEligible: false` + `changeLog[]` |
| **KYC type** (`CredentialType = KYCCredential`) | ✅ | `kycProfile.kycCompletionDate` + `kycProfile.dueDiligenceRequirements` |
| **XRPL `CredentialType` hex** (round-trip reconstruction) — XLS-70 | ✅ | `kycProfile.blockchainAccountIds[].xrplCredentialType` ⭐ (hex string, 2–128 chars; added v1.3.0) |
| **MPT issuance identifier** (`MPTokenIssuanceID`) | ✅ | `kycProfile.blockchainAccountIds[].mptIssuanceId` ⭐ (48-char hex Hash192; added v1.3.0) |
| **AML type** (`CredentialType = AMLCredential`) | ✅ | `kycProfile.sanctionsScreening` + `kycProfile.adverseMedia` |
| **Accredited investor type** | ✅ | `kycProfile.customerClassification.accreditedInvestor` + `investorCategoryJurisdiction` |
| **Deep Freeze** (XLS-77) | ✅ | `kycProfile.blockchainAccountIds[].xrplFreezeType: "DEEP_FREEZE"` ⭐ (added v1.7.0) |
| **Individual / Global Freeze** | ✅ | `kycProfile.blockchainAccountIds[].isFrozen` + `xrplFreezeType` ⭐ (`"INDIVIDUAL_FREEZE"` / `"GLOBAL_FREEZE"`; added v1.7.0) |
| **Native Clawback** (Clawback amendment / `lsfMPTCanClawback`) | ✅ | `kycProfile.blockchainAccountIds[].xrplClawbackEnabled` ⭐ (added v1.7.0) |
| **Confidential transfer flag** — XLS-96 | ✅ | `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer.enabled` ⭐ (added v1.7.0) |
| **Auditor public key** — XLS-96 | ✅ | `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer.auditorPublicKey` ⭐ (added v1.7.0) |
| **Regulator public key** — XLS-96 | ✅ | `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer.regulatorPublicKey` ⭐ (added v1.7.0) |
| **Travel Rule on XRPL** (FATF Rec 16 / TFR 2023/1113 Art. 14 / MiCA Art. 83) | ✅ | `ivms101` block; `Credential.URI` anchors the IVMS 101 payload on-ledger |

_✅ = full field mapping. 🔄 = conceptual equivalent (see [mapping-xrpl-credentials-mpt.md](../mappings/mapping-xrpl-credentials-mpt.md)). ℹ️ = out of scope. ⭐ = schema extended in v1.3.0. 🌟 = schema extended in v1.7.0._

---

## 13. PredictiveAML Extension (v1.7.0)

The `predictiveAML` top-level block is a new optional extension providing ML-ready, explainable, auditable risk scores. It supports EU AI Act Art. 13, AMLR Art. 22, and BCBS 239. Full details in [eu-ai-act.md](../mappings/eu-ai-act.md) and [bcbs239.md](../mappings/bcbs239.md).

| Standard / Requirement | Coverage | PredictiveAML v1.7.0 Field |
|---|---|---|
| **EU AI Act Annex III** — High-risk AML AI classification | ✅ | `predictiveAML.modelMetadata.euAiActClassification` |
| **EU AI Act Art. 13(3)(a)** — Provider identity | ✅ | `predictiveAML.modelMetadata.provider` |
| **EU AI Act Art. 13(3)(b)(ii)** — Accuracy/confidence | ✅ | `predictiveAML.predictiveScores[].confidence` |
| **EU AI Act Art. 13(3)(b)(iii)** — Output interpretation | ✅ | `predictiveAML.explainability` (SHAP/LIME/counterfactual) |
| **EU AI Act Art. 43** — Conformity assessment | ✅ | `predictiveAML.modelMetadata.conformityAssessmentReference` |
| **AMLR Art. 22(5)** — Third-party reliance with provenance | ✅ | `predictiveAML.modelMetadata.modelId` + `modelVersion` + `trainingDate` |
| **AMLR Art. 21** — Ongoing monitoring (delta-based cKYC) | ✅ | `predictiveAML.riskEvolutionHistory[]` |
| **BCBS 239 P2** — Data architecture and lineage | ✅ | `predictiveAML.dataAggregationMetadata.dataLineageReference` |
| **BCBS 239 P5** — Timeliness | ✅ | `predictiveAML.dataAggregationMetadata.lastAggregationTimestamp` |
| **BCBS 239 P12** — Supervisory review | ✅ | `predictiveAML.dataAggregationMetadata.bcbs239ComplianceLevel` |
| Alert closed-loop feedback | ✅ | `predictiveAML.alertCorrelationId` |
| Transaction anomaly scoring | ✅ | `predictiveAML.predictiveScores[].scoreType` = `transaction_anomaly` |
| UBO graph risk scoring | ✅ | `predictiveAML.predictiveScores[].scoreType` = `ubo_graph_risk` |
| Network risk scoring | ✅ | `predictiveAML.predictiveScores[].scoreType` = `network_risk` |

---

---

## 14. FinCEN 314(a)/(b) — Information Sharing Flags (v1.7.0)

| FinCEN Provision | Coverage | OpenKYCAML v1.7.0 Field |
|---|---|---|
| **Section 314(a)** — Mandatory law enforcement information request | ✅ 🌟 | `informationSharingFlags.section314aRequestId` |
| **Section 314(b)** — Voluntary institution-to-institution sharing safe-harbor | ✅ 🌟 | `informationSharingFlags.section314bSafeHarbor` |
| Sharing consent timestamp | ✅ 🌟 | `informationSharingFlags.sharingConsentTimestamp` |

---

---

## 15. Wolfsberg FCCQ v1.2 / CBDDQ v1.4 (v1.7.0)

See [wolfsberg-fccq-cbddq.md](../mappings/wolfsberg-fccq-cbddq.md) for the full mapping.

| Wolfsberg Section | Coverage | Notes |
|---|---|---|
| A — Organisation & Structure | ✅ | `ivms101.originator.originatorPersons[].legalPerson.*` |
| B — Ownership & Control | ✅ | `kycProfile.beneficialOwnership[]` + v1.7.0 nominee/bearer flags |
| C — AML/CTF Programme | ✅ | `predictiveAML.modelMetadata` + `monitoringInfo.tmModelVersion` |
| D — Customer Due Diligence | ✅ | `kycProfile.customerRiskRating` + `dueDiligenceType` |
| E — Sanctions & PEP | ✅ | `kycProfile.sanctionsScreening` + `pepStatus` |
| F — Transaction Monitoring | ✅ | `monitoringInfo.ruleTriggerHistory[]` + `predictiveAML.predictiveScores[]` |
| G — Information Sharing | ✅ | `informationSharingFlags.section314bSafeHarbor` |
| Products & Services (Q19b) | 🟡 | `productUsage[]` planned |

---

## 16. Bitcoin and Lightning Network (Service-Layer Enforcement)

> Bitcoin has no protocol-level compliance framework comparable to ERC-3643 or XRPL's credential system. Compliance on Bitcoin and Lightning is enforced entirely at the service layer. The full mapping is in [mapping-bitcoin-lightning.md](../mappings/mapping-bitcoin-lightning.md).

| Bitcoin / Lightning Data Point | Coverage | OpenKYCAML Field(s) |
|---|---|---|
| **Bitcoin wallet address** (P2PKH / P2WPKH / P2TR) | ✅ | `kycProfile.blockchainAccountIds[].address` (`network: "bitcoin"`) |
| **Bitcoin script type** (P2PKH / P2WPKH / P2TR) | ✅ | `kycProfile.blockchainAccountIds[].bitcoinScriptType` ⭐ (added v1.7.0) |
| **Lightning node public key** | ✅ | `kycProfile.blockchainAccountIds[].lightningNodePubkey` ⭐ (66-char hex; added v1.7.0) |
| **Lightning Service Provider** (Lightspark, Voltage, etc.) | ✅ | `kycProfile.blockchainAccountIds[].lightningServiceProvider` ⭐ (name or DID; added v1.7.0) |
| **KYC identity** (natural or legal person) | ✅ | `ivms101.originator.*` and `kycProfile.*` — same payload as Ethereum/XRPL; compliance is at service layer |
| **Travel Rule** (FATF Rec 16 — Lightning service providers) | ✅ | `ivms101` block — Lightning VASP Travel Rule uses the same IVMS 101 fields; enforcement is by the LSP (Lightspark Compliance API, Voltage Flow, etc.) |
| **AML screening** | ✅ | `kycProfile.sanctionsScreening`, `kycProfile.adverseMedia` — fed into LSP compliance engine |
| **Beneficial ownership** (Bitcoin VASP entity) | ✅ | `kycProfile.beneficialOwnership[]` |
| **On-chain enforcement** | ⬜ | Not applicable — Bitcoin scripting language does not support compliance enforcement at the protocol level |
| **Layer-2 compliance** (RGB Protocol, Taproot Assets, Liquid Network) | ⬜ | Out of scope at the protocol level; these Layer-2 networks do not have on-chain compliance enforcement comparable to ERC-3643 or XRPL credentials. OpenKYCAML payloads feed the off-chain compliance systems that wrap these networks. |

_✅ = full field mapping. ⬜ = not in scope / service-layer enforcement only._

---

## 17. X.500 Distinguished Names and X.509 PKI Evidence (v1.8.0)

> X.500 DNs are the canonical Subject/Issuer identifier in X.509 certificates. X.509 PKI certificates underpin eIDAS 2.0 Qualified Trust Services (QES, QSealC, QWAC, QEAA) and SWIFTNet addressing. Full mappings are in [x500-x400-legacy.md](../mappings/x500-x400-legacy.md) and [x509-pki.md](../mappings/x509-pki.md).

| Standard / Provision | Coverage | OpenKYCAML v1.8.0 Field(s) |
|---|---|---|
| **X.500 DN — certificate Subject** (ITU-T X.500 / RFC 4514) | ✅ ⭐ | `legacyIdentifiers.x500DN` (`x500DNType: "certificateSubject"`) |
| **X.500 DN — certificate Issuer** | ✅ ⭐ | `legacyIdentifiers.x500DN` (`x500DNType: "certificateIssuer"`) |
| **X.500 DN — SWIFTNet technical address** | ✅ ⭐ | `legacyIdentifiers.x500DN` (`x500DNType: "swiftNetAddress"`) |
| **X.500 DN — LDAP/directory entry** | ✅ ⭐ | `legacyIdentifiers.x500DN` (`x500DNType: "directoryEntry"`) |
| **X.400 O/R Addresses** (ITU-T X.400) | ⬜ | Not added — no current regulatory mandate; explicitly excluded |
| **X.509 certificate Subject DN** (RFC 5280 §4.1.2.6) | ✅ ⭐ | `pkiEvidence.x509Certificate.subjectDN` |
| **X.509 certificate Issuer DN** (RFC 5280 §4.1.2.4) | ✅ ⭐ | `pkiEvidence.x509Certificate.issuerDN` |
| **X.509 serial number** (RFC 5280 §4.1.2.2) | ✅ ⭐ | `pkiEvidence.x509Certificate.serialNumber` |
| **X.509 validity period** (RFC 5280 §4.1.2.5) | ✅ ⭐ | `pkiEvidence.x509Certificate.validFrom` + `validTo` |
| **X.509 signature algorithm** (RFC 5280 §4.1.1.2) | ✅ ⭐ | `pkiEvidence.x509Certificate.signatureAlgorithm` |
| **eIDAS QCStatements** (ETSI EN 319 412 — id-pe-QCStatements) | ✅ ⭐ | `pkiEvidence.x509Certificate.qcStatements[]` |
| **OCSP revocation** (RFC 6960) | ✅ ⭐ | `pkiEvidence.x509Certificate.ocspResponderUrl` |
| **CRL Distribution Points** (RFC 5280 §4.2.1.13) | ✅ ⭐ | `pkiEvidence.x509Certificate.crlDistributionPoints[]` |
| **SHA-256 cert fingerprint** | ✅ ⭐ | `pkiEvidence.x509Certificate.thumbprintSha256` |
| **ASN.1 OIDs** (RFC 5280 / ETSI profiles) | ✅ ⭐ | `pkiEvidence.oids[]` (oid + description + value) |
| **eIDAS 2.0 QES** (Reg. 910/2014 + EU 2024/1183) | ✅ ⭐ | `qcStatements` includes `id-etsi-qcs-QcType-eSign` |
| **eIDAS 2.0 QSealC** | ✅ ⭐ | `qcStatements` includes `id-etsi-qcs-QcType-eSeal` |
| **eIDAS 2.0 QWAC** | ✅ ⭐ | `qcStatements` includes `id-etsi-qcs-QcType-Web` |
| **eIDAS 2.0 QEAA** (Art. 45f) | ✅ ⭐ | `qcStatements` includes `id-etsi-qcs-QcEAA` + `verifiableCredential.evidence[]` |
| **AMLR 2027 Art. 22(6)** — QC as remote CDD evidence | ✅ ⭐ | `pkiEvidence` + `pkiEvidence.certificateDocumentRef` → `identityDocuments` |
| **AMLR 2027 Art. 56** — Record keeping (cert fingerprint) | ✅ ⭐ | `pkiEvidence.x509Certificate.thumbprintSha256` + `validFrom/validTo` |
| **ETSI EN 319 412 series** — QTSP cert profiles | ✅ ⭐ | `pkiEvidence.x509Certificate.*` + `pkiEvidence.oids[]` |
| **ETSI TS 119 461 v2.1.1** — Identity proofing | ✅ ⭐ | `pkiEvidence` + `identityDocuments` + `certificateDocumentRef` |
| **Predictive AML cert provenance** | ✅ ⭐ | `validTo` + `ocspResponderUrl` → `predictiveAML.riskEvolutionHistory[]` cert-expiry signals |

_✅ = full field mapping. ⬜ = explicitly out of scope. ⭐ = added in v1.8.0._

---

## 18. Tax Status — TIN / OECD CRS / CARF / FATCA (v1.9.0+)

> Full mapping in [tax-status-oecd-esr-pillar2.md](../mappings/tax-status-oecd-esr-pillar2.md), [tax-status-oecd-esr-pillar2.yaml](../mappings/tax-status-oecd-esr-pillar2.yaml), [fatca-crs.md](../mappings/fatca-crs.md), and [fatca-crs.yaml](../mappings/fatca-crs.yaml).

| Standard / Provision | Coverage | OpenKYCAML v1.9.1 Field(s) |
|---|---|---|
| **OECD CRS TIN** — account holder TIN (per OECD CRS §IV.C) | ✅ ⭐ | `taxStatus.tinIdentifiers[tinType=TIN].tinValue` |
| **OECD CRS multi-residency** — enhanced per-jurisdiction CRS data | ✅ ⭐⭐ | `taxStatus.crsTaxResidencies[]` (jurisdiction + tinValue + tinVerificationStatus + selfCertificationDate) |
| **OECD CRS controlling persons (Passive NFE)** | ✅ ⭐⭐ | `taxStatus.crsTaxResidencies[controllingPersonFlag=true]` |
| **OECD CRS TIN reason codes A/B/C** | ✅ ⭐⭐ | `taxStatus.crsTaxResidencies[].tinVerificationStatus` (not-required / unverified / relief-applied) |
| **OECD CARF TIN** — crypto-asset user identifier | ✅ ⭐ | `taxStatus.tinIdentifiers[].tinValue` + `tinType` |
| **FATCA GIIN** — IRS FFI List identifier (19-char, regex-validated) | ✅ ⭐⭐ | `taxStatus.fatcaStatus.giin` |
| **FATCA Chapter 4 classification** — participatingFFI, RDCFFI, exemptBeneficialOwner, etc. | ✅ ⭐⭐ | `taxStatus.fatcaStatus.chapter4Classification` |
| **FATCA US TIN required flag** | ✅ ⭐⭐ | `taxStatus.fatcaStatus.usTinRequired` |
| **FATCA IRS Notice 2024-78 temporary relief** (2025–2027 deferral) | ✅ ⭐⭐ | `taxStatus.fatcaStatus.temporaryReliefApplied` |
| **FATCA FFI List verification timestamp** — monthly refresh | ✅ ⭐⭐ | `taxStatus.fatcaStatus.ffiListVerificationTimestamp` |
| **FATCA withholding agent / sponsored entity reference** | ✅ ⭐⭐ | `taxStatus.fatcaStatus.withholdingAgentReference` |
| **FATCA EIN** — US Employer Identification Number | ✅ ⭐ | `taxStatus.tinIdentifiers[tinType=EIN].tinValue` |
| **TIN functional equivalent** — UK UTR, Chile RUT, AU TFN, etc. | ✅ ⭐ | `taxStatus.tinIdentifiers[tinType=functionalEquivalent]` |
| **FATCA/CRS XML Schema v2.0 export** — entire taxStatus as AEOI payload | ✅ ⭐⭐ | `taxStatus` root block |
| **IVMS 101 TXID migration** — structured replacement for TXID | ✅ ⭐ | `taxStatus.tinIdentifiers[0]` ↔ `nationalIdentification.TXID` |
| **AMLR Art. 22 tax-residency verification** | ✅ ⭐ | `taxStatus.tinIdentifiers[]` + `crsTaxResidencies[]` + `verificationSource` |

_✅ = full field mapping. ⭐ = added in v1.9.0. ⭐⭐ = added in v1.9.1._

---

## 19. Economic Substance Regulations — ESR (v1.9.0)

> ESR regimes: BVI (VIBES Act 2019), Cayman Islands (ES Law 2018), UAE (ESR 2019), Jersey (ES (Jersey) Law 2019), Guernsey (ES Regulations 2018), Isle of Man (IOM ES Act 2018/2019 amendments).

| Standard / Provision | Coverage | OpenKYCAML v1.9.0 Field(s) |
|---|---|---|
| **ESR jurisdiction classification** — in-scope / exempt / compliant | ✅ ⭐ | `taxStatus.economicSubstance.status` (5-value enum) |
| **Relevant activities** — holding, IP, banking, fund management, etc. | ✅ ⭐ | `taxStatus.economicSubstance.relevantActivities[]` |
| **CIGAs performed** — core income generating activities in jurisdiction | ✅ ⭐ | `taxStatus.economicSubstance.coreIncomeGeneratingActivitiesPerformed` |
| **Annual notification date** | ✅ ⭐ | `taxStatus.economicSubstance.lastNotificationDate` |
| **Annual report reference** — filing reference / acknowledgment | ✅ ⭐ | `taxStatus.economicSubstance.lastReportReference` |
| **ESR jurisdiction code** (BVI=VG, Cayman=KY, UAE=AE, Jersey=JE) | ✅ ⭐ | `taxStatus.economicSubstance.jurisdiction` (ISO 3166-1 alpha-2) |
| **Shell-company red flag** — nonCompliant ESR status | ✅ ⭐ | `taxStatus.economicSubstance.status = "nonCompliant"` → validator warning → EDD |
| **AMLR Art. 26** — legal entity establishment verification | ✅ ⭐ | `taxStatus.economicSubstance` combined with `identityDocuments.legalEntityDocuments[]` |
| **FATF Rec. 24** — transparency of legal persons (shell company risk) | ✅ ⭐ | `taxStatus.economicSubstance.status` + `relevantActivities[]` |

_✅ = full field mapping. ⭐ = added in v1.9.0._

---

## 20. OECD Pillar 2 GloBE — BEPS 2.0 (v1.9.0)

> Governing instruments: OECD/G20 Inclusive Framework GloBE Model Rules (December 2021); OECD GloBE Commentary (March 2022); EU Pillar 2 Directive (2022/2523); OECD Agreed Administrative Guidance (2023–2025); GloBE Information Return XML Schema (2024).

| Standard / Provision | Coverage | OpenKYCAML v1.9.0 Field(s) |
|---|---|---|
| **In-scope MNE flag** — group revenue >= EUR 750 m threshold | ✅ ⭐ | `taxStatus.pillarTwo.inScopeMNE` |
| **Consolidated group revenue (EUR)** — GloBE Art. 1.1 threshold test | ✅ ⭐ | `taxStatus.pillarTwo.consolidatedRevenueEUR` |
| **Constituent entity status** — inScope / excluded / QDMTT | ✅ ⭐ | `taxStatus.pillarTwo.constituentEntityStatus` |
| **ETR per jurisdiction** — effective tax rate array | ✅ ⭐ | `taxStatus.pillarTwo.etrJurisdictions[]` (`{jurisdiction, etr}`) |
| **GloBE minimum rate (15%)** — ETR < 0.15 triggers top-up tax | ✅ ⭐ | `taxStatus.pillarTwo.etrJurisdictions[].etr` — validator flags ETR < 0.15 |
| **Safe harbour election** — Simplified ETR / Substance-Based / De Minimis | ✅ ⭐ | `taxStatus.pillarTwo.safeHarbourApplied` |
| **GIR filing reference** — GloBE Information Return reference | ✅ ⭐ | `taxStatus.pillarTwo.girFilingReference` |
| **GIR filing date** | ✅ ⭐ | `taxStatus.pillarTwo.lastGIRDate` |
| **GIR missing warning** — inScopeMNE=true but girFilingReference absent | ✅ ⭐ | Validator business warning (Python + JS + Go) |
| **BEPS / profit-shifting predictive AML linkage** | ✅ ⭐ | `taxStatus.pillarTwo.etrJurisdictions[]` → `predictiveAML.predictiveScores` BEPS risk flag |
| **QDMTT** — Qualified Domestic Minimum Top-up Tax | ✅ ⭐ | `taxStatus.pillarTwo.constituentEntityStatus = "QDMTT"` |

_✅ = full field mapping. ⭐ = added in v1.9.0._

---

---

## 21. Format and Pattern Completeness — Contact, Financial Identifiers, and Validation Strength (v1.10.0)

> Full mapping in [contact-financial-identifiers.md](../mappings/contact-financial-identifiers.md).

This section documents the format/pattern coverage added in v1.10.0 to achieve comprehensive machine-enforceable validation across internal systems, suppliers, clients, and regulatory counterparties. All additions are strictly additive and backward-compatible.

### 21.1 Contact Fields — FATF Rec. 16 / AMLR Art. 22

| Field | $def | Format / Pattern | Standard Reference |
|---|---|---|---|
| `emailAddress` | `NaturalPerson`, `LegalPerson` | ✅ ⭐ `format: "email"` (RFC 5321, max 254 chars) | FATF Rec. 16 counterparty contact data; AMLR Art. 22 CDD |
| `phoneNumber` | `NaturalPerson`, `LegalPerson` | ✅ ⭐ E.164 pattern `^\+[1-9]\d{1,14}$` | FATF Rec. 16; AMLR Art. 22(5) remote CDD; ITU-T E.164 |
| `mobileNumber` | `NaturalPerson`, `LegalPerson` | ✅ ⭐ E.164 pattern `^\+[1-9]\d{1,14}$` | AMLR Art. 22(5) remote CDD; EUDI Wallet mTAN/OTP notification |

### 21.2 Banking Identifiers — ISO 13616 IBAN / ISO 9362 BIC

| Field | $def | Format / Pattern | Standard Reference |
|---|---|---|---|
| `iban` | `BankingDetails` | ✅ ⭐ `^[A-Z]{2}[0-9]{2}[A-Z0-9]{4,30}$` (ISO 13616 structural) | ISO 13616:2020; SEPA; FATF Rec. 16 correspondent banking due diligence |
| `bic` | `BankingDetails` | ✅ ⭐ `^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$` (ISO 9362, 8/11-char) | ISO 9362:2022; SWIFT; SEPA; FATF Rec. 16 |
| `accountCurrency` | `BankingDetails` | ✅ ⭐ `^[A-Z]{3}$` (ISO 4217) | ISO 4217; IVMS 101 §4 |
| `bankingCountry` | `BankingDetails` | ✅ ⭐ `^[A-Z]{2}$` (ISO 3166-1 alpha-2) | ISO 3166-1; AMLR Art. 22 |

### 21.3 Regulatory Identifiers — EU VAT, EORI, EUID

| Field | $def | Pattern Added | Standard Reference |
|---|---|---|---|
| `vatRegistrationNumber` | `LegalPersonIdentificationData` | ✅ ⭐ `^[A-Z]{2}[A-Z0-9]{2,12}$` | EU VAT Directive 2006/112/EC; eIDAS 2.0 LPID optional attribute |
| `eoriNumber` | `LegalPersonIdentificationData` | ✅ ⭐ `^[A-Z]{2}[A-Z0-9]{1,15}$` | EU Reg. 952/2013 (Union Customs Code); eIDAS 2.0 LPID optional attribute |
| `europeanUniqueIdentifier` | `LegalPersonIdentificationData` | ✅ ⭐ `^[A-Z]{2}-[A-Za-z0-9.\-]{6,40}$` | Directive (EU) 2017/1132 Art. 16; eIDAS EUID (CC-RA-RN format) |
| `registrationNumber` | `IndirectTaxRegistration` | ✅ ⭐ `^[A-Z0-9\-\/]{2,30}$` | EU VIES; India GSTIN; Australia ABN; Canada HST/PST |
| `tinValue` | `TinIdentifier` | ✅ ⭐ `^[A-Z0-9\-\/]{5,20}$` | OECD CRS §IV.C; FATCA; AMLR Art. 22 |
| `withholdingAgentReference` | `FatcaStatus` | ✅ ⭐ `^[A-Z0-9\-]{1,30}$` | IRS FATCA withholding agent obligations |

### 21.4 Document Number Fields

| Field | $def | Pattern Added | Notes |
|---|---|---|---|
| `documentNumber` | `NaturalPersonDocument` | ✅ ⭐ `^[A-Z0-9\-\/ ]{1,50}$` | Global passport / national ID formats; rejects control characters |
| `documentNumber` | `LegalEntityDocument` | ✅ ⭐ `^[A-Z0-9\-\/ ]{1,100}$` | Company document reference numbers |
| `registrationNumber` | `LegalEntityDocument` | ✅ ⭐ `^[A-Z0-9\-\/ ]{1,100}$` | Company registration numbers across jurisdictions |

### 21.5 Miscellaneous Field Tightening

| Field | $def | Change | Standard Reference |
|---|---|---|---|
| `accountNumber` items | `Originator`, `Beneficiary` | ✅ ⭐ `^[A-Za-z0-9\-\/.]{1,100}$` | IVMS 101 §4; Ethereum 0x, Bitcoin bech32, IBAN formats |
| `registrationAuthority` | `NationalIdentification` | ✅ ⭐ `^RA[0-9]{6}$` | GLEIF Registration Authority List (RAL) code format |
| `currency` (TM threshold) | `TransactionMonitoring` | ✅ ⭐ `^[A-Z]{3}$` | ISO 4217 |
| `assetType` | `IVMS101Payload` | ✅ ⭐ `^[A-Z]{3,10}$` | ISO 4217 + crypto-asset tickers (IVMS 101 §4) |
| `postCode` | `Address` | ✅ ⭐ `^[A-Z0-9\- ]{2,10}$` | Generic postal code structural validation; IVMS 101 §3.5 |

_✅ = full field mapping. ⭐ = added in v1.10.0. All additions backward-compatible._

---

## 22. Cell Company Structures — PCC and ICC KYC/AML Support (v1.11.0)

> Full mapping in [cell-company.md](../mappings/cell-company.md).

Cell companies (Protected Cell Companies and Incorporated Cell Companies) are specialised corporate vehicles used in insurance, reinsurance, securitisation, and alternative investment markets. They require explicit schema support because risk, sanctions/PEP exposure, beneficial ownership, and source-of-funds can differ materially between cells within the same parent structure.

### 22.1 Cell Company Type Classification

| `cellCompanyType` Value | Legal Structure | Independent Legal Personality | Typical Jurisdiction |
|---|---|---|---|
| `NONE` | Ordinary company (no cells) | Yes | All |
| `PCC_CORE` | PCC overarching entity | Yes (single entity for all cells) | GG, JE, IM, KY, MT, GI |
| `PCC_CELL` | Cell within a PCC | No (transacts through PCC) | GG, JE, IM, KY, MT, GI |
| `ICC_CORE` | ICC coordinating core | Yes | GG, JE, IM, KY |
| `ICC_CELL` | Incorporated cell (own legal entity) | Yes (own registration, LEI) | GG, JE, IM, KY |

### 22.2 CellCompanyDetails Field Mapping

| Field | Format / Pattern | Regulatory Basis |
|---|---|---|
| `cellCompanyType` | ✅ ⭐ Enum (5 values) | FATF Rec. 24/25 legal arrangement disclosure; AMLR Art. 26(2)(b) |
| `cellIdentifier` | ✅ ⭐ `^[A-Za-z0-9 \-]{1,64}$` | Cell register identifier (jurisdiction-specific) |
| `cellRegistrationNumber` | ✅ ⭐ `^[A-Z0-9]{1,35}$` | ICC cell company registration; own LEI eligibility |
| `hasIndependentLegalPersonality` | ✅ ⭐ boolean | Determines whether cell can hold own LEI, file own returns, contract independently |
| `isCellCompanyIssuer` | ✅ ⭐ boolean | ILS/cat bond issuer identification for IVMS 101 / FATF Rec. 16 |
| `issuancePurpose` | ✅ ⭐ Enum (5 values) | Instrument classification for AML/CFT risk assessment |
| `cellSpecificInstrumentReference` | ✅ ⭐ `format: "uri"` | Prospectus/term sheet link for EDD file evidence |

### 22.3 ParentCellCompanyReference Field Mapping

| Field | Format / Pattern | Regulatory Basis |
|---|---|---|
| `legalEntityIdentifier` | ✅ ⭐ `^[A-Z0-9]{1,35}$` | FATF beneficial-ownership chain; AMLR Art. 26 parent entity verification |
| `jurisdiction` | ✅ ⭐ `^[A-Z]{2}$` (ISO 3166-1) | Cross-border legal hierarchy identification |

### 22.4 Cell-Level Risk and Audit Fields (LegalPerson extensions)

| Field | $ref | Regulatory Basis |
|---|---|---|
| `cellRiskProfileOverride` | `RiskSnapshot` | Cell-level risk granularity; FATF Rec. 1 risk-based approach |
| `cellSourceOfFundsWealth` | `SourceOfFundsWealth` | AMLR Art. 29; FATF Rec. 12 higher-risk countries |
| `cellAuditMetadata` | `AuditMetadata` | AMLR Art. 56 5-year record retention per cell |

### 22.5 Validator Business Warnings

| Condition | Warning |
|---|---|
| `cellCompanyType` is PCC_CELL/ICC_CELL + no `parentCellCompanyReference` | FATF beneficial-ownership tracing requires parent link (AMLR Art. 26) |
| `isCellCompanyIssuer: true` + no `issuancePurpose` | Instrument-level classification required for risk assessment |

_✅ = full field mapping. ⭐ = added in v1.11.0. All additions backward-compatible._

---

*Last updated: v1.11.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*