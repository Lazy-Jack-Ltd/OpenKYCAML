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
| **Rec 24** — Beneficial ownership of legal persons | ✅ | `kycProfile.beneficialOwnership[]`; `legalPerson.legalFormCode` (ISO 20275:2017 ELF code, v1.4.0); `legalPerson.entityType` typed classification; **Cell structures (PCC/ICC):** `cellCompanyDetails`, `parentCellCompanyReference`, `cellRiskProfileOverride` — see §22 |
| **Rec 25** — Beneficial ownership of legal arrangements | ✅ | `kycProfile.beneficialOwnership` covers natural-person and legal-person beneficial owners for trusts, foundations, and LLPs. `legalPerson.entityType` = `TRUST`/`FOUNDATION`/`PARTNERSHIP` drives typed sub-objects (`trustDetails`, `foundationDetails`, `partnershipDetails`) that explicitly capture settlor, trustee, protector, beneficiary class, founders, council members, and partner roles (v1.4.0). See `legal-entity-trust.json`, `legal-entity-partnership.json`, `trust-complex-ubo.json`, `foundation-complex-ubo.json`, `llp-complex-ubo.json`. **Cell structures (PCC/ICC):** `cellCompanyDetails` describes cell legal form; `parentCellCompanyReference` links cells to their Core — see §22 |

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
| **Art. 26** — Beneficial owners | UBOs of legal entities and legal arrangements | ✅ | `kycProfile.beneficialOwnership[]`; `legalPerson.entityType` + `trustDetails` / `foundationDetails` / `partnershipDetails` typed sub-objects capturing settlors, trustees, protectors, beneficiary class, founders, council members, and partners (v1.4.0, ISO 20275:2017 aligned); **Cell structures (PCC/ICC):** `cellCompanyDetails`, `parentCellCompanyReference`, `cellRiskProfileOverride` (AMLR Art. 26 / FATF Rec. 24–25) — see §22 |
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
| **`Credential.Expiration`** (Ripple epoch) — XLS-70 | ✅ | `verifiableCredential.validUntil` (ISO 8601; Ripple epoch = Unix − 946684800) |
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

### 22.5 Schema-Enforced Constraints (v1.11.1)

The following conditions were originally validator business warnings (v1.11.0) and were promoted to hard JSON Schema `if`/`then` constraints in v1.11.1. Payloads that violate them **fail schema validation**.

| Condition | Enforcement mechanism | Regulatory basis |
|---|---|---|
| `cellCompanyType` is PCC_CELL/ICC_CELL + no `parentCellCompanyReference` | `LegalPerson` `allOf` `if`/`then` | FATF Rec. 24; AMLR Art. 26 |
| `isCellCompanyIssuer: true` + no `issuancePurpose` | `CellCompanyDetails` `if`/`then` | AML/CFT instrument-level risk classification |

_✅ = full field mapping. ⭐ = added in v1.11.0. ⭐⭐ = promoted to hard constraint in v1.11.1. All additions backward-compatible._

---

## 23. Natural-Person Governance, Entity Governance, and Review Lifecycle (v1.12.0)

> Three independent optional extensions that close the remaining CDD data gaps identified in the v1.11.2 compliance gap analysis. All additions are backward-compatible.

### 23.1 Natural-Person Completeness — `gender` and `occupation` (v1.12.0)

Fields added to `NaturalPerson` $def. Both are optional.

| Field | Schema path | Standard alignment | Regulatory basis |
|---|---|---|---|
| `gender` ⭐⭐⭐ | `NaturalPerson.gender` | eIDAS 2.0 PID `gender` (ISO/IEC 5218); IVMS 101 extended CDD | AMLR Art. 22 CDD data; IVMS 101 §3; jurisdictional KYC rules requiring sex/gender |
| `occupation.occupationCode` ⭐⭐⭐ | `NaturalPerson.occupation.occupationCode` | ILO/ISCO-08 broad category; eIDAS 2.0 PID `occupation`; IVMS 101 extended CDD | AMLR Art. 22 source-of-wealth/funds CDD; FATF Rec. 12 (PUBLIC_OFFICIAL triggers PEP screening) |
| `occupation.occupationDescription` ⭐⭐⭐ | `NaturalPerson.occupation.occupationDescription` | Free-text complement to occupationCode | AMLR Art. 22 CDD data; IVMS 101 extended CDD |

**GDPR note:** `gender` is a special-category personal data element under GDPR Art. 9. Collect only where lawfully required; document legal basis in ROPA (Art. 30).

**Relationship to `occupationOrPurpose`:** `kycProfile.customerClassification.occupationOrPurpose` (free-text, natural persons and legal entities) is **not deprecated**. `NaturalPerson.occupation` provides a structured, person-level complement for IVMS 101 and eIDAS PID interoperability.

See [docs/mappings/natural-person-governance.md](../mappings/natural-person-governance.md) for full field mapping and GDPR guidance.

### 23.2 Legal-Entity Governance Flags — `EntityGovernance` (v1.12.0)

New `EntityGovernance` $def, exposed as optional `LegalPerson.entityGovernance`. All sub-fields are optional.

| Field | Type / Enum | Regulatory basis |
|---|---|---|
| `regulatoryStatus` ⭐⭐⭐ | `REGULATED`, `RECOGNISED`, `UNREGULATED`, `EXEMPT` | AMLR Art. 48 CDD reliance; FATF Rec. 17 (third-party reliance) |
| `regulators[]` ⭐⭐⭐ | Array: `regulatorName`, `jurisdiction` (`^[A-Z]{2}$`), `licenceNumber` | AMLR Art. 48; FATF Rec. 17; Wolfsberg CBDDQ §3 — multi-regulator cross-border CDD reliance |
| `listedStatus.isListed` ⭐⭐⭐ | boolean | AMLR Art. 22 (SDD for listed entities); MAR (market-abuse risk) |
| `listedStatus.marketIdentifier` ⭐⭐⭐ | ISO 10383 MIC code | MiFID II Art. 4(1)(21); MAR insider-dealing risk scoring |
| `listedStatus.recognisedMarket` ⭐⭐⭐ | boolean | AMLR Art. 22 SDD eligibility; MiFID II regulated market definition |
| `parentCompany` ⭐⭐⭐ | `$ref: ParentCellCompanyReference` | FATF Rec. 24; AMLR Art. 26 (group beneficial ownership chain) |
| `parentRegulated` ⭐⭐⭐ | boolean | AMLR Art. 48 intra-group reliance; Wolfsberg CBDDQ §3.3 |
| `parentListed` ⭐⭐⭐ | boolean | AMLR Art. 22 SDD conditions for listed-group subsidiaries; MAR |
| `majorityOwnedSubsidiary` ⭐⭐⭐ | boolean | FATF Rec. 24; AMLR Art. 26 (ownership chain); AMLR Art. 48 intra-group reliance |
| `stateOwned` ⭐⭐⭐ | boolean | FATF PEP Guidance; AMLR Art. 28–31 (PEP adjacency for SOEs) |
| `governmentOwnershipPercentage` ⭐⭐⭐ | number 0–100 | FATF Rec. 12; AMLR Art. 28–31; IMF/OECD SOE governance frameworks |

See [docs/mappings/entity-governance.md](../mappings/entity-governance.md) for full field reference and JSON example.

### 23.3 Review Lifecycle State Machine — `ReviewLifecycle` (v1.12.0)

New `ReviewLifecycle` $def, exposed as optional `MonitoringInfo.reviewLifecycle`. Provides an explicit, timestamped audit trail of lifecycle transitions.

| Field | Type / Enum | Regulatory basis |
|---|---|---|
| `currentState` ⭐⭐⭐ | `ONBOARDING`, `INITIAL_REVIEW`, `PERIODIC_REVIEW`, `TRIGGERED_REVIEW`, `OFFBOARDING`, `TERMINATED` | AMLR Art. 21 (ongoing monitoring lifecycle); FATF Rec. 11 (record keeping) |
| `stateHistory[].state` ⭐⭐⭐ | Same enum | AMLR Art. 21 supervisory inspection; AMLR Art. 56 5-year record retention |
| `stateHistory[].enteredAt` ⭐⭐⭐ | ISO 8601 date-time | AMLR Art. 21 audit trail; FATF Rec. 11 |
| `stateHistory[].exitedAt` ⭐⭐⭐ | ISO 8601 date-time (optional) | Duration analysis; supervisory inspection |
| `stateHistory[].triggeredBy` ⭐⭐⭐ | string (optional) | AMLR Art. 21 — record of who/what triggered each review transition |
| `stateHistory[].notes` ⭐⭐⭐ | string max 500 (optional) | Free-text rationale for transition; supervisory inspection narrative |

**Relationship to `monitoringStatus`:** `MonitoringInfo.monitoringStatus` (ACTIVE / SUSPENDED / TERMINATED) continues to represent the operational status of the relationship. `reviewLifecycle` adds the formal compliance lifecycle state machine with full history. The two fields are complementary.

### 23.4 Schema-Level Changes (v1.12.0)

| Change | Scope | Backward compatible |
|---|---|---|
| `NaturalPerson.gender` (optional) | `$defs.NaturalPerson` | ✅ |
| `NaturalPerson.occupation` (optional object) | `$defs.NaturalPerson` | ✅ |
| `EntityGovernance` $def (new) | `$defs` | ✅ |
| `LegalPerson.entityGovernance` (optional) | `$defs.LegalPerson` | ✅ |
| `ReviewLifecycle` $def (new) | `$defs` | ✅ |
| `MonitoringInfo.reviewLifecycle` (optional) | `$defs.MonitoringInfo` | ✅ |
| Schema `$id` and `version` bumped to `v1.12.0` | Root | ✅ |

_✅ = full field mapping. ⭐ = added in v1.11.0. ⭐⭐ = promoted to hard constraint in v1.11.1. ⭐⭐⭐ = added in v1.12.0. All additions backward-compatible._

---

## 24. CRM Completeness — 20 Contact/Account Field Gaps Closed (v1.13.0)

> All additions are optional and backward-compatible. No existing required fields changed.

### 24.1 New $defs (v1.13.0)

| $def | Required fields | Key optional fields | Regulatory / Operational basis |
|---|---|---|---|
| **`EmailAddress`** ⭐⭐⭐⭐ | `emailAddress` | `emailType`, `isPrimary`, `verificationStatus` | AMLR Art. 22 (CDD contact data); GDPR Art. 5 (accuracy principle) |
| **`EmergencyContact`** ⭐⭐⭐⭐ | `name` | `relationship`, `phoneNumber`, `emailAddress` | Account succession; estate-handling workflows; GDPR Art. 9 note |
| **`IndustryCode`** ⭐⭐⭐⭐ | `codeSystem`, `codeValue` | `codeDescription` | AMLR Art. 20 risk factors (sector risk); NACE Rev.2 / NAICS 2022 / SIC / ISIC alignment |
| **`Mandate`** ⭐⭐⭐⭐ | `mandateType` | `signatoryName`, `signatoryRef`, `scope`, `effectiveFrom`, `effectiveTo` | eIDAS 2.0 LPID mandates attribute; AMLR Art. 26 authorised representatives; FATF Rec. 24 |
| **`PhoneNumber`** ⭐⭐⭐⭐ | `phoneNumber` | `phoneType`, `isPrimary` | AMLR Art. 22 CDD contact data; E.164 format alignment |
| **`RegisteredAgent`** ⭐⭐⭐⭐ | `name` | `jurisdiction`, `address`, `agentType` | FATF Rec. 24 (registered agent transparency); AMLR Art. 26 (offshore / SPV structures) |

### 24.2 `NaturalPersonNameIdentifier` — Gap 1 (CRM name completeness)

| Field | Type / Constraint | Regulatory / Operational basis |
|---|---|---|
| `salutation` ⭐⭐⭐⭐ | enum: MR/MRS/MS/MISS/DR/PROF/REV/OTHER | CRM correspondence; AMLR Art. 22(2) customer identity |
| `middleName` ⭐⭐⭐⭐ | string max 200 | PEP/sanctions screening completeness; AMLR Art. 22 |
| `nameSuffix` ⭐⭐⭐⭐ | string max 50 | CRM identity matching |
| `preferredName` ⭐⭐⭐⭐ | string max 200 | Customer correspondence; AMLR Art. 22 |
| `formerName` ⭐⭐⭐⭐ | string max 200 | Name-change records; AMLR Art. 22; PEP screening |
| `pronouns` ⭐⭐⭐⭐ | string max 50 | GDPR Art. 9 — collect only with explicit consent or legal requirement |

### 24.3 `DateAndPlaceOfBirth` — Gap 3

| Field | Type / Constraint | Regulatory / Operational basis |
|---|---|---|
| `countryOfBirth` ⭐⭐⭐⭐ | ISO 3166-1 alpha-2 pattern | IVMS 101 optional birth-country field; eIDAS 2.0 PID; AMLR Art. 22(2) |

### 24.4 `Address` — Gap 5 (richer vocabulary + history tracking)

| Field / Change | Type / Enum | Regulatory / Operational basis |
|---|---|---|
| `addressType` enum expanded ⭐⭐⭐⭐ | +REGISTERED_OFFICE, PRINCIPAL_PLACE_OF_BUSINESS, MAILING, BILLING, SHIPPING, CORRESPONDENCE, PREVIOUS, OTHER | AMLR Art. 22(2) address types; FATF Rec. 10; backward-compat: GEOG + BIZZ retained |
| `isPrimary` ⭐⭐⭐⭐ | boolean | CRM primary address designation |
| `effectiveFrom` ⭐⭐⭐⭐ | ISO 8601 date | AMLR Art. 21 ongoing monitoring; FATF Rec. 11 record keeping |
| `effectiveTo` ⭐⭐⭐⭐ | ISO 8601 date | Historical address tracking for AML; AMLR Art. 56 record retention |

### 24.5 `NaturalPerson` — Gaps 2, 4, 6, 7, 8, 17, 19, 20

| Field | Gap | Type | Regulatory / Operational basis |
|---|---|---|---|
| `isDeceased` ⭐⭐⭐⭐ | 2 | boolean | Estate-handling; GDPR (deceased generally out of scope) |
| `deceasedDate` ⭐⭐⭐⭐ | 2 | ISO 8601 date | Account offboarding; probate workflow |
| `emailAddresses[]` ⭐⭐⭐⭐ | 4 | `$ref EmailAddress` | AMLR Art. 22 CDD contact; supplements legacy `emailAddress` string |
| `phoneNumbers[]` ⭐⭐⭐⭐ | 4 | `$ref PhoneNumber` | AMLR Art. 22 CDD contact; supplements legacy `phoneNumber`/`mobileNumber` |
| `faxNumber` ⭐⭐⭐⭐ | 4 | string (E.164) | Legacy contact channel support |
| `preferredLanguage` ⭐⭐⭐⭐ | 6 | BCP 47 pattern | AMLR Art. 22 multilingual CDD; CRM communications routing |
| `preferredCommunicationChannel` ⭐⭐⭐⭐ | 6 | enum EMAIL/PHONE/SMS/POST/PORTAL/OTHER | CRM service delivery; GDPR consent records |
| `marketingOptOut` ⭐⭐⭐⭐ | 6 | boolean | GDPR Art. 21 right to object; ePrivacy Directive |
| `maritalStatus` ⭐⭐⭐⭐ | 7 | enum (8 values) | GDPR Art. 9 — collect only where legally required; inheritance / joint-account governance |
| `numberOfDependants` ⭐⭐⭐⭐ | 8 | integer ≥ 0 | Source-of-wealth risk assessment; affordability analysis |
| `householdSize` ⭐⭐⭐⭐ | 8 | integer ≥ 1 | Wealth-management profiling; source-of-wealth |
| `emergencyContact` ⭐⭐⭐⭐ | 17 | `$ref EmergencyContact` | Account succession; estate-handling; GDPR Art. 9 note |
| `tags[]` ⭐⭐⭐⭐ | 19 | string array max 100 each | CRM segmentation; workflow routing |
| `customAttributes` ⭐⭐⭐⭐ | 19 | open object | Implementer extensibility without schema fork |
| `historicalNames[]` ⭐⭐⭐⭐ | 20 | array of `{ name, nameType, effectiveFrom, effectiveTo }` | FATF Rec. 12 PEP screening; AMLR Art. 28–31; sanctions screening all known aliases |

### 24.6 `LegalPerson` — Gaps 4, 9, 10, 11, 12, 13, 19

| Field | Gap | Type | Regulatory / Operational basis |
|---|---|---|---|
| `emailAddresses[]` ⭐⭐⭐⭐ | 4 | `$ref EmailAddress` | AMLR Art. 22 CDD contact |
| `phoneNumbers[]` ⭐⭐⭐⭐ | 4 | `$ref PhoneNumber` | AMLR Art. 22 CDD contact |
| `faxNumber` ⭐⭐⭐⭐ | 4 | string (E.164) | Legacy contact channel |
| `dateOfIncorporation` ⭐⭐⭐⭐ | 9 | ISO 8601 date | AMLR Art. 22(2); Companies House / GLEIF alignment |
| `dateOfRegistration` ⭐⭐⭐⭐ | 9 | ISO 8601 date | AMLR Art. 22(2); cross-border registration |
| `dateOfDissolution` ⭐⭐⭐⭐ | 9 | ISO 8601 date | AMLR Art. 56 record retention; offboarding workflow |
| `operationalStatus` ⭐⭐⭐⭐ | 9 | enum (7 values) | AMLR Art. 21 ongoing monitoring; Companies House / GLEIF alignment |
| `numberOfEmployees` ⭐⭐⭐⭐ | 10 | integer ≥ 0 | Customer classification; EDD sizing; Salesforce/Dynamics alignment |
| `annualRevenue` ⭐⭐⭐⭐ | 10 | number ≥ 0 | Risk-tier assignment; product suitability; AMLR Art. 20 risk factors |
| `annualRevenueCurrency` ⭐⭐⭐⭐ | 10 | ISO 4217 3-char | Currency denomination for annualRevenue |
| `annualRevenueVerificationDate` ⭐⭐⭐⭐ | 10 | ISO 8601 date | AMLR Art. 21 periodic review; data freshness |
| `websiteUrl` ⭐⭐⭐⭐ | 11 | URI format | Adverse media screening; VASP identification |
| `socialMediaProfiles[]` ⭐⭐⭐⭐ | 11 | array `{ platform, url, isVerified }` | Adverse media screening; EDD digital footprint |
| `industryCodes[]` ⭐⭐⭐⭐ | 12 | `$ref IndustryCode` | AMLR Art. 20 sector risk; NACE/NAICS/SIC/ISIC alignment |
| `registeredAgent` ⭐⭐⭐⭐ | 13 | `$ref RegisteredAgent` | FATF Rec. 24; AMLR Art. 26 — offshore / SPV / cell company transparency |
| `tags[]` ⭐⭐⭐⭐ | 19 | string array | CRM segmentation; workflow routing |
| `customAttributes` ⭐⭐⭐⭐ | 19 | open object | Implementer extensibility |

### 24.7 `LegalPersonIdentificationData` — Gap 18 (structured mandates)

| Change | Regulatory / Operational basis |
|---|---|
| `mandates[]` items now `$ref Mandate` ⭐⭐⭐⭐ | eIDAS 2.0 LPID mandates attribute; AMLR Art. 26 authorised representatives; FATF Rec. 24 |

### 24.8 `EntityGovernance` — Gap 15 (GLEIF ultimate parent / group)

| Field | Type / Constraint | Regulatory / Operational basis |
|---|---|---|
| `ultimateParentLEI` ⭐⭐⭐⭐ | ISO 17442 20-char pattern | GLEIF Level 2 ultimate parent; FATF Rec. 24; AMLR Art. 26 |
| `ultimateParentName` ⭐⭐⭐⭐ | string max 300 | Group beneficial ownership chain; AMLR Art. 26 |
| `groupName` ⭐⭐⭐⭐ | string max 300 | Group-level risk aggregation; Wolfsberg CBDDQ §3 |
| `groupLEI` ⭐⭐⭐⭐ | ISO 17442 20-char pattern | GLEIF group identification; FATF Rec. 24 |

### 24.9 `KYCProfile` — Gaps 14, 16, 19

| Field | Gap | Type | Regulatory / Operational basis |
|---|---|---|---|
| `relationshipManagerId` ⭐⭐⭐⭐ | 14 | string max 100 | Compliance audit trail; AMLR Art. 56 record keeping |
| `relationshipManagerName` ⭐⭐⭐⭐ | 14 | string max 200 | CRM accountability; supervisory inspection |
| `primaryBranchCode` ⭐⭐⭐⭐ | 14 | string max 50 | Regulatory reporting; geographic risk attribution |
| `servingBusinessUnit` ⭐⭐⭐⭐ | 14 | string max 200 | Product suitability; EDD routing |
| `customerSegment` ⭐⭐⭐⭐ | 16 | enum (9 values) | EDD thresholds; service-level routing; product suitability |
| `estimatedNetWorth` ⭐⭐⭐⭐ | 16 | number ≥ 0 | EDD sizing; AMLR Art. 29 source-of-wealth assessment |
| `estimatedNetWorthCurrency` ⭐⭐⭐⭐ | 16 | ISO 4217 3-char | Currency denomination |
| `estimatedNetWorthDate` ⭐⭐⭐⭐ | 16 | ISO 8601 date | AMLR Art. 21 periodic review; data freshness |
| `tags[]` ⭐⭐⭐⭐ | 19 | string array | CRM segmentation |
| `customAttributes` ⭐⭐⭐⭐ | 19 | open object | Implementer extensibility |

### 24.10 Schema-Level Changes (v1.13.0)

| Change | Scope | Backward compatible |
|---|---|---|
| 6 new $defs (EmailAddress, EmergencyContact, IndustryCode, Mandate, PhoneNumber, RegisteredAgent) | `$defs` | ✅ |
| `NaturalPersonNameIdentifier` — 6 new optional fields | `$defs.NaturalPersonNameIdentifier` | ✅ |
| `DateAndPlaceOfBirth.countryOfBirth` | `$defs.DateAndPlaceOfBirth` | ✅ |
| `Address.addressType` enum expanded; `isPrimary`, `effectiveFrom`, `effectiveTo` | `$defs.Address` | ✅ |
| `NaturalPerson` — 15 new optional fields | `$defs.NaturalPerson` | ✅ |
| `LegalPerson` — 17 new optional fields | `$defs.LegalPerson` | ✅ |
| `EntityGovernance` — 4 new optional fields | `$defs.EntityGovernance` | ✅ |
| `KYCProfile` — 10 new optional fields | `$defs.KYCProfile` | ✅ |
| `LegalPersonIdentificationData.mandates` — typed array items | `$defs.LegalPersonIdentificationData` | ✅ |
| Schema `$id` and `version` bumped to `v1.13.0` | Root | ✅ |

_✅ = full field mapping. ⭐⭐⭐⭐ = added in v1.13.0. All additions backward-compatible._

---

## §25. Company Identifier Registry Array — `companyIdentifiers[]` (v1.16.0)

Multi-registry company identifiers are critical for legal-entity due diligence. D&B D-U-N-S, Companies House CRN, GLEIF LEI, and commercial data-provider IDs (BvD Orbis, SWIFT BIC, ISIN) are routinely required by FATF Recommendations 10, 24 & 25, EU AMLR Art. 20 & 26, and Wolfsberg CBDDQ. Prior to v1.16.0 the schema offered only a single `nationalIdentification` object with an IVMS 101-constrained type enum; there was no way to carry DUNS, CRN, BvD IDs, or other commercial data-provider references. v1.16.0 adds:

* **`CompanyIdentifier` $def** — typed object with `identifierType` (23-value enum), `identifierValue`, optional `identifierIssuingBody`, `countryOfIssue`, `verificationDate`, `verificationSource`. A hard `if/then` constraint requires `identifierIssuingBody` when `identifierType = "OTHER"`.
* **`LegalPerson.companyIdentifiers[]`** — array of `CompanyIdentifier` items with `uniqueItems: true`.

### 25.1 Supported Identifier Types

| Code | Full Name | Issuing Body | Country Scope |
|---|---|---|---|
| `DUNS` | D-U-N-S Number | Dun & Bradstreet (dnb.co.uk) | Global |
| `LEI` | Legal Entity Identifier | GLEIF / ISO 17442 | Global |
| `CRN_GB` | Companies House Registration Number | Companies House (UK) | GB |
| `SIREN_FR` | SIREN | INSEE (France) | FR |
| `SIRET_FR` | SIRET | INSEE (France) | FR |
| `HRB_DE` | Handelsregister B (GmbH/AG) | German state courts | DE |
| `HRA_DE` | Handelsregister A (OHG/KG) | German state courts | DE |
| `CNPJ_BR` | CNPJ | Receita Federal (Brazil) | BR |
| `ABN_AU` | Australian Business Number | ATO | AU |
| `ACN_AU` | Australian Company Number | ASIC | AU |
| `EIN_US` | Employer Identification Number | IRS (USA) | US |
| `CIK_US` | Central Index Key | SEC EDGAR (USA) | US |
| `CAGE_US` | Commercial and Government Entity Code | US DoD SAM.gov | US |
| `PIC_EU` | Participant Identification Code | EU Funding & Tenders Portal | EU |
| `BVDID` | Bureau van Dijk (Orbis) ID | Moody's Analytics / BvD | Global |
| `ISIN` | International Securities Identification Number | ISO 6166 / ANNA | Global |
| `BIC` | Business Identifier Code | SWIFT / ISO 9362 | Global |
| `CHARITY_GB` | Charity Commission Registration Number | Charity Commission (UK) | GB |
| `KVK_NL` | KvK Number | Netherlands Chamber of Commerce | NL |
| `UID_AT` | Umsatzsteueridentifikationsnummer | Austrian Finanzamt | AT |
| `NIF_ES` | Número de Identificación Fiscal / CIF | Spain AEAT | ES |
| `RCS_LU` | Registre de Commerce et des Sociétés | Luxembourg RCS | LU |
| `OTHER` | Custom / non-enumerated type | Implementer-defined | Any |

### 25.2 Regulatory Mapping

| Requirement | Standard / Article | Coverage |
|---|---|---|
| Legal entity identification | FATF Rec. 10 | DUNS, LEI, CRN, national IDs all supported |
| Beneficial ownership & entity transparency | FATF Rec. 24 / 25 | Multi-registry cross-check via array |
| Legal-entity CDD | EU AMLR Art. 20 | LEI + national registry IDs |
| Entity verification | EU AMLR Art. 26 | CRN, SIREN, Handelsregister, etc. |
| Correspondent banking — entity due diligence | FATF Rec. 13 / Wolfsberg CBDDQ | BIC, LEI, DUNS |
| Commercial-data enrichment | BvD Orbis / D&B data-layer KYC | BVDID, DUNS |

### 25.3 Relationship to Existing Identifier Fields

The existing `LegalPerson.lei` (IVMS 101 scalar) and `LegalPerson.nationalIdentification` (single IVMS 101 object) are **retained as authoritative IVMS 101 / travel-rule fields**. `companyIdentifiers[]` is an additive overlay allowing multiple registries and commercial-data identifiers to be recorded alongside the primary IVMS fields, with full verification metadata per entry.

### 25.4 Schema-Level Changes (v1.16.0)

| Change | Scope | Backward compatible |
|---|---|---|
| New `CompanyIdentifier` $def (23-value enum, if/then for OTHER) | `$defs` | ✅ |
| `LegalPerson.companyIdentifiers[]` optional array | `$defs.LegalPerson` | ✅ |
| New example `examples/company-identifiers.json` | `examples/` | ✅ |
| Schema `$id` bumped to `v1.16.0` | Root | ✅ |

_✅ = full field mapping. All additions backward-compatible._

---

---

## §26. Array-Grouping Enhancements — Multi-Identifier, Multi-PEP, History Arrays (v1.17.0)

Prior to v1.17.0 several KYC/AML data elements were constrained to single scalars or single objects, preventing the recording of real-world multi-value data (multiple government IDs, dual residency, simultaneous PEP roles, risk-rating audit trails, multi-year revenue records). v1.17.0 adds 12 backward-compatible additive arrays covering all high-, medium-, and lower-priority gaps.

### 26.1 Natural Person Identifier Array (`naturalPersonIdentifiers[]`)

| Change | Schema Location | Compliance Driver |
|---|---|---|
| New `PersonIdentifier` $def (17-value enum: CCPT, IDCD, ARNU, DRLC, TXID, SOCS, FIIN, RAID, LEIX, BTHC, VDOC, RESI, HLTH, MILN, EMPL, MISC, OTHER) | `$defs.PersonIdentifier` | FATF Rec. 10, AMLR Art. 20 |
| `NaturalPerson.naturalPersonIdentifiers[]` optional array with `isPrimary` maxContains:1 | `$defs.NaturalPerson` | FATF Rec. 10, eIDAS 2.0 PID |
| if/then: MISC or OTHER requires `identifierIssuingBody` | `$defs.PersonIdentifier` | Data quality / audit trail |

**Supported identifier types:** Passport (CCPT), National/Identity Card (IDCD), Alien Registration (ARNU), Driver Licence (DRLC), Tax ID (TXID), Social Security/NI (SOCS), Foreign Investment (FIIN), eIDAS Registration Authority ID (RAID), LEI-sole-trader (LEIX), Birth Certificate (BTHC), Voter ID (VDOC), Residence Permit (RESI), Health/Medical (HLTH), Military ID (MILN), Employer ID (EMPL), Miscellaneous (MISC), Other (OTHER).

### 26.2 Legal Entity National Identifier Array (`legalNationalIdentifiers[]`)

| Change | Schema Location | Compliance Driver |
|---|---|---|
| `LegalPerson.legalNationalIdentifiers[]` — array of `NationalIdentification` items | `$defs.LegalPerson` | FATF Rec. 10, 24; AMLR Art. 20 |

Allows a legal entity to carry multiple IVMS 101-typed national identifiers simultaneously (e.g. LEIX + MISC + ISO_20275_ELF_CODE). Additive alongside `nationalIdentification` (primary IVMS 101 / travel-rule field) and `companyIdentifiers[]` (commercial registry IDs).

### 26.3 PEP Status Array (`pepStatuses[]`)

| Change | Schema Location | Compliance Driver |
|---|---|---|
| `KYCProfile.pepStatuses[]` — array of `PEPStatus` items | `$defs.KYCProfile` | FATF Rec. 12 EDD, Wolfsberg CBDDQ |

A person may hold multiple simultaneous PEP roles (e.g. CLOSE_ASSOCIATE_OF_PEP + FORMER_PEP). Each item carries its own `pepCategory`, `pepRole`, `screeningDate`, and `screeningProvider`. Additive alongside legacy `pepStatus` scalar.

### 26.4 Countries of Residence Array (`countriesOfResidence[]`)

| Change | Schema Location | Compliance Driver |
|---|---|---|
| `NaturalPerson.countriesOfResidence[]` — alpha-2 string array | `$defs.NaturalPerson` | FATCA/CRS, AMLR Art. 20 |

Allows dual- or multi-residency to be recorded (e.g. UK/UAE). Required for accurate FATCA/CRS multi-residency reporting and geographic risk-tier scoring.

### 26.5 Unified Nationality Array (`nationalities[]`)

| Change | Schema Location | Compliance Driver |
|---|---|---|
| `NaturalPerson.nationalities[]` — alpha-2 string array | `$defs.NaturalPerson` | IVMS 101 §3.3, eIDAS 2.0 PID |

Unifies the legacy `nationality` (single alpha-2) and `nationalitiesAlpha3[]` (alpha-3 EUDI wallet array) into a single IVMS 101-compatible alpha-2 array. Legacy fields retained for backward compatibility; new implementations should use `nationalities[]`.

### 26.6 Risk Rating History (`riskRatingHistory[]`)

| Change | Schema Location | Compliance Driver |
|---|---|---|
| New `RiskRatingEntry` $def (customerRiskRating, riskScore, riskRatingDate, ratingMethodology, ratingChangedBy, ratingChangeReason, riskFactors) | `$defs.RiskRatingEntry` | BCBS 239, AMLR Art. 21 |
| `KYCProfile.riskRatingHistory[]` optional array | `$defs.KYCProfile` | BCBS 239, AMLR Art. 21 |

Enables chronological audit trails of all risk rating changes for periodic- and event-driven re-assessment compliance.

### 26.7 Multiple Occupations (`occupations[]`)

| Change | Schema Location | Compliance Driver |
|---|---|---|
| `NaturalPerson.occupations[]` — inline object array (occupationCode, occupationDescription, employerName, isPrimary) with maxContains:1 on isPrimary | `$defs.NaturalPerson` | EDD / CDD completeness |

Allows multiple concurrent occupations (employed + director + self-employed consultant) to be recorded with employer names. Additive alongside legacy `occupation` scalar.

### 26.8 Revenue History (`revenueHistory[]`)

| Change | Schema Location | Compliance Driver |
|---|---|---|
| New `RevenueRecord` $def (amount, currency, fiscalYear, verificationDate, verificationSource) | `$defs.RevenueRecord` | AMLR Art. 29 EDD |
| `LegalPerson.revenueHistory[]` optional array | `$defs.LegalPerson` | AMLR Art. 29, Wolfsberg CBDDQ |

Enables multi-year revenue history to be maintained. Additive alongside legacy `annualRevenue` / `annualRevenueCurrency` / `annualRevenueVerificationDate` scalars.

### 26.9 Consent Record Array (`consentRecords[]`)

| Change | Schema Location | Compliance Driver |
|---|---|---|
| New `ConsentRecord` $def (consentPurpose, consentGiven, consentDate, consentWithdrawnDate, consentMethod, consentReference, legalBasis) | `$defs.ConsentRecord` | GDPR Art. 7 |
| `KYCProfile.consentRecords[]` optional array | `$defs.KYCProfile` | GDPR Art. 7 |

Per-purpose consent event records maintain a full GDPR Art. 7 audit trail. `legalBasis` records the applicable Art. 6 basis (CONSENT, CONTRACT, LEGAL_OBLIGATION, VITAL_INTERESTS, PUBLIC_TASK, LEGITIMATE_INTERESTS).

### 26.10 Multiple Parent Companies (`parentCompanies[]`)

| Change | Schema Location | Compliance Driver |
|---|---|---|
| `EntityGovernance.parentCompanies[]` — array of `EntityReference` items | `$defs.EntityGovernance` | FATF Rec. 24 |

Handles joint-venture parents, dual-listed holding structures, or entities with multiple co-owners. Additive alongside legacy `parentCompany` scalar.

### 26.11 Multiple Emergency Contacts (`emergencyContacts[]`)

| Change | Schema Location | Compliance Driver |
|---|---|---|
| `NaturalPerson.emergencyContacts[]` — array of `EmergencyContact` items | `$defs.NaturalPerson` | CRM completeness |

CRM systems typically support multiple emergency contacts. Additive alongside legacy `emergencyContact` scalar.

### 26.12 Multiple Registered Agents (`registeredAgents[]`)

| Change | Schema Location | Compliance Driver |
|---|---|---|
| `LegalPerson.registeredAgents[]` — array of `RegisteredAgent` items | `$defs.LegalPerson` | Cayman / BVI / Jersey / Guernsey CDD |

Handles offshore jurisdictions requiring multiple registered agents (REGISTERED_AGENT, COMPANY_SECRETARY, RESIDENT_DIRECTOR, OTHER) or agent-change history. Additive alongside legacy `registeredAgent` scalar.

### 26.13 Regulatory Mapping Summary

| Requirement | Standard / Article | Fields Added |
|---|---|---|
| Natural person identification | FATF Rec. 10, AMLR Art. 20 | `naturalPersonIdentifiers[]`, `PersonIdentifier` $def |
| Legal entity identification | FATF Rec. 10, 24; AMLR Art. 20 | `legalNationalIdentifiers[]` |
| PEP disclosure — all roles | FATF Rec. 12 EDD, Wolfsberg CBDDQ | `pepStatuses[]` |
| Multi-residency / FATCA/CRS | FATCA §1471, OECD CRS, AMLR Art. 20 | `countriesOfResidence[]` |
| Nationality (IVMS 101-aligned) | IVMS 101 §3.3, eIDAS 2.0 PID | `nationalities[]` |
| Risk rating audit trail | BCBS 239 Principle 6, AMLR Art. 21 | `riskRatingHistory[]`, `RiskRatingEntry` $def |
| Occupation (multi-role EDD) | EDD / CDD best practice | `occupations[]` |
| Revenue history (EDD) | AMLR Art. 29, Wolfsberg CBDDQ | `revenueHistory[]`, `RevenueRecord` $def |
| Consent audit trail | GDPR Art. 7, Art. 6 | `consentRecords[]`, `ConsentRecord` $def |
| Beneficial ownership chain | FATF Rec. 24 | `parentCompanies[]` |
| Emergency contacts (CRM) | CRM completeness | `emergencyContacts[]` |
| Multi-agent offshore CDD | Cayman / BVI / Jersey AML regs | `registeredAgents[]` |

### 26.14 Schema-Level Changes (v1.17.0)

| Change | Scope | Backward compatible |
|---|---|---|
| New `PersonIdentifier` $def (17-value enum, if/then for MISC/OTHER) | `$defs` | ✅ |
| New `RiskRatingEntry` $def | `$defs` | ✅ |
| New `RevenueRecord` $def | `$defs` | ✅ |
| New `ConsentRecord` $def | `$defs` | ✅ |
| `NaturalPerson.naturalPersonIdentifiers[]` optional array | `$defs.NaturalPerson` | ✅ |
| `NaturalPerson.countriesOfResidence[]` optional array | `$defs.NaturalPerson` | ✅ |
| `NaturalPerson.nationalities[]` optional array | `$defs.NaturalPerson` | ✅ |
| `NaturalPerson.occupations[]` optional array | `$defs.NaturalPerson` | ✅ |
| `NaturalPerson.emergencyContacts[]` optional array | `$defs.NaturalPerson` | ✅ |
| `LegalPerson.legalNationalIdentifiers[]` optional array | `$defs.LegalPerson` | ✅ |
| `LegalPerson.revenueHistory[]` optional array | `$defs.LegalPerson` | ✅ |
| `LegalPerson.registeredAgents[]` optional array | `$defs.LegalPerson` | ✅ |
| `KYCProfile.pepStatuses[]` optional array | `$defs.KYCProfile` | ✅ |
| `KYCProfile.riskRatingHistory[]` optional array | `$defs.KYCProfile` | ✅ |
| `KYCProfile.consentRecords[]` optional array | `$defs.KYCProfile` | ✅ |
| `EntityGovernance.parentCompanies[]` optional array | `$defs.EntityGovernance` | ✅ |
| New examples `examples/array-grouping-v1-17.json`, `examples/array-grouping-legal-entity-v1-17.json` | `examples/` | ✅ |
| Schema `$id` and `version` bumped to `v1.17.0` | Root | ✅ |

_✅ = full field mapping. All additions backward-compatible. All legacy scalar/object fields retained._

---

## §27 — W3C VC Data Model 2.0 (v1.18.0)

Upgrades the `VerifiableCredentialWrapper` from W3C VC DM v1.1 to the W3C VC DM 2.0 W3C Recommendation (May 2024), completing the upgrade that was previously deferred. This also aligns with OID4VP and W3C DID Auth interoperability requirements that increasingly assume the v2 context URL.

### 27.1 Regulatory Alignment

| Standard | Requirement | Schema Coverage | Status |
|---|---|---|---|
| EU eIDAS 2.0 ARF §6.3 | EUDIW credentials must use VCDM 2.0-compatible structures | `verifiableCredential.@context[0]: "https://www.w3.org/ns/credentials/v2"` | ✅ |
| W3C VC DM 2.0 (May 2024) | `@context[0]` must be `https://www.w3.org/ns/credentials/v2` | `@context` contains constraint updated | ✅ |
| W3C VC DM 2.0 (May 2024) | `issuanceDate` renamed to `validFrom` | `VerifiableCredentialWrapper.validFrom` (required) | ✅ |
| W3C VC DM 2.0 (May 2024) | `expirationDate` renamed to `validUntil` | `VerifiableCredentialWrapper.validUntil` (optional) | ✅ |
| OID4VP / OpenID4VC | Credential presentation assumes v2 context URL | Context URL aligned | ✅ |

### 27.2 Schema-Level Changes (v1.18.0)

| Change | Scope | Backward compatible |
|---|---|---|
| `@context` contains constraint updated from v1.1 URL to v2 URL | `$defs.VerifiableCredentialWrapper` | ⚠️ Breaking for existing VC payloads (context URL must be updated) |
| `issuanceDate` renamed to `validFrom` (required) | `$defs.VerifiableCredentialWrapper` | ⚠️ Breaking — field rename |
| `expirationDate` renamed to `validUntil` (optional) | `$defs.VerifiableCredentialWrapper` | ⚠️ Breaking — field rename |
| Description updated to reference W3C VC DM 2.0 | `$defs.VerifiableCredentialWrapper` | ✅ |
| All 23 VC-bearing examples updated | `examples/` | ✅ |
| "Planned for v2.0.0" deferral notes removed from schema and docs | Schema, guides, mappings | ✅ |
| Schema `$id` and `version` bumped to `v1.18.0` | Root | ✅ |

---

*Last updated: v1.18.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*