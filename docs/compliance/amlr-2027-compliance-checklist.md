# AMLR 2027 Compliance Checklist for OpenKYCAML Adopters

> **Regulation (EU) 2024/1624 (AMLR)** applies from **1 July 2027** to all obliged entities in the EU. This checklist helps teams using the OpenKYCAML schema confirm that their implementation satisfies AMLR obligations. It covers schema configuration, operational processes, and gaps that depend on forthcoming AMLA RTS.

**Scope:** Banks, payment institutions, CASPs/VASPs, crowdfunding platforms, and other obliged entities under AMLR Article 3.

**Legend:**
- ✅ Fully supported by the OpenKYCAML schema — configure and implement
- 🟡 Partially supported — awaiting AMLA RTS finalisation; configure what is available now
- ⬜ Operational — outside schema scope; process/governance obligation

---

## 1. Customer Identification and Verification (AMLR Art. 22)

### 1.1 Identity Attribute Collection
- [ ] ✅ Collect and store the IVMS 101 natural person attributes for all individuals: `naturalPerson.name` (LEGL type), `naturalPerson.dateAndPlaceOfBirth`, `nationalIdentification`, `address`, `countryOfResidence`.
- [ ] ✅ Collect and store IVMS 101 legal person attributes for all entities: `legalPerson.name` (LEGL type), `nationalIdentification` (LEI preferred, LEIX type), `countryOfRegistration`.
- [ ] 🟡 Populate `kycProfile.dueDiligenceRequirements.verifiedAttributes` with the list of attributes actually collected and verified. Update this list once the AMLA RTS on CDD attribute sets (Art. 22(4)) is published with binding minimum attribute sets per tier.
- [ ] 🟡 Set `kycProfile.dueDiligenceRequirements.appliedTier` to `SDD`, `CDD`, or `EDD` as appropriate. Add a `rtsComplianceNote` documenting the basis for tier selection pending the AMLA RTS.

### 1.2 Verification Methods and Assurance Levels
- [ ] ✅ Populate `kycProfile.dueDiligenceRequirements.verificationMethods[]` for each verified attribute, recording: `attribute`, `method`, `assuranceLevel`, `verificationDate`, `verificationProvider`.
- [ ] ✅ For EUDI Wallet onboarding, set `kycProfile.onboardingChannel` to `EUDI_WALLET` and `verificationMethods[].method` to `EUDI_WALLET_PID`. Record the PID Issuer DID in `verifiableCredential.evidence[].credentialIssuer`.
- [ ] ✅ For eIDAS-based verification, set `assuranceLevel` to `SUBSTANTIAL` (minimum for standard CDD) or `HIGH` (required for EDD and for EUDI Wallet PID presentation under eIDAS Article 5f).
- [ ] ⬜ Ensure your onboarding process accepts EUDI Wallet presentations (mandated for obliged entities under AMLR Art. 22 cross-referencing eIDAS Art. 5f). Update internal procedures by 2027.

### 1.3 Remote CDD
- [ ] ✅ For remote onboarding, set `kycProfile.onboardingChannel` to `REMOTE_VIDEO`, `REMOTE_AUTOMATED`, or `EUDI_WALLET` as applicable.
- [ ] ✅ Store the W3C Verifiable Credential evidence chain in `verifiableCredential.evidence[]` to provide tamper-evident proof for remote identification under AMLR Art. 22(5).
- [ ] ✅ For EUDI Wallet / SD-JWT presentations, populate `verifiableCredential.selectiveDisclosure` with `_sd_alg`, `disclosableClaimPaths`, and `decodedDisclosures` to satisfy GDPR data minimisation while preserving an auditable attribute record.

---

## 2. Risk-Based Approach (AMLR Art. 15, 20, 21)

- [ ] ✅ Set `kycProfile.customerRiskRating` for every customer record (`LOW`, `MEDIUM`, `HIGH`, `VERY_HIGH`, `UNACCEPTABLE`, or `PROHIBITED`).
- [ ] ✅ Populate `kycProfile.riskRatingDetail.riskFactors` with individual factor scores: `geographicRisk`, `productRisk`, `channelRisk`, `customerTypeRisk`.
- [ ] ✅ Set `kycProfile.monitoringInfo.monitoringLevel` and `reviewFrequency` in line with the customer's risk rating (e.g. `CONTINUOUS` / `MONTHLY` for HIGH/VERY_HIGH; `STANDARD` / `ANNUAL` for LOW).
- [ ] ✅ Set `kycProfile.monitoringInfo.nextReviewDate` and update `lastReviewDate` after each periodic review.
- [ ] 🟡 Once the AMLA Guidelines on Risk Factors (successor to EBA Joint Guidelines, AMLR Art. 20(6)) are adopted, map the risk factors listed in the guidelines to `kycProfile.riskRatingDetail.riskFactors`.

---

## 3. Simplified Due Diligence (SDD) (AMLR Art. 22(1) / Art. 27)

- [ ] ✅ Set `kycProfile.dueDiligenceType` to `SDD` when applying simplified measures.
- [ ] ✅ Set `kycProfile.dueDiligenceRequirements.appliedTier` to `SDD` and record the minimum attribute set verified.
- [ ] ✅ Set `kycProfile.monitoringInfo.monitoringLevel` to `SIMPLIFIED`.
- [ ] 🟡 Once the AMLA RTS on CDD attribute sets is published, confirm that your SDD attribute set meets the binding minimum and update `dueDiligenceRequirements.rtsComplianceNote`.

---

## 4. Enhanced Due Diligence (EDD) (AMLR Art. 29–33)

- [ ] ✅ Set `kycProfile.dueDiligenceType` to `EDD`.
- [ ] ✅ Set `kycProfile.monitoringInfo.eddRequired` to `true`.
- [ ] ✅ Set `kycProfile.monitoringInfo.monitoringLevel` to `ENHANCED` or `CONTINUOUS`.
- [ ] ✅ For high-risk third countries (AMLR Art. 29), set `kycProfile.riskRatingDetail.riskFactors.geographicRisk` to `HIGH` or `VERY_HIGH` and add a `rtsComplianceNote` referencing the high-risk country list in force.
- [ ] ✅ For PEP customers, set `kycProfile.pepStatus.isPEP` to `true`, populate `pepCategory` (using the AMLA taxonomy: `DOMESTIC_PEP`, `FOREIGN_PEP`, `INTERNATIONAL_ORGANISATION`, `FAMILY_MEMBER_OF_PEP`, `CLOSE_ASSOCIATE_OF_PEP`), and record `pepRole`, `screeningDate`, and `screeningProvider`.
- [ ] ✅ For EDD, populate `kycProfile.sourceOfFundsWealthDetail` with verified source of funds and wealth, `verificationStatus`, and `supportingDocuments`.
- [ ] 🟡 Once the AMLA RTS on EDD measures for high-risk third countries (AMLR Art. 29(4)) is published, confirm that your EDD process covers the specific additional measures listed and update `dueDiligenceRequirements`.

---

## 5. Beneficial Ownership (AMLR Art. 26)

- [ ] ✅ For all legal entities, populate `kycProfile.beneficialOwnership[]`. Include all UBOs with ≥ 25% ownership or effective control.
- [ ] ✅ For each UBO, record: `naturalPerson` identity attributes, `ownershipPercentage`, `ownershipType`, `controlMechanism`, `verificationDate`, `isPEP`.
- [ ] ✅ For complex ownership structures, use `ownershipChainDepth` and `intermediateEntities[]` to document the full holding chain (AMLR Art. 26 full-chain disclosure requirement).
- [ ] ⬜ Verify beneficial ownership against the EU/national BO registers where available (AMLR Art. 26 requires cross-checking with central registers). Document verification outcome in `auditMetadata.changeLog`.

---

## 6. Targeted Financial Sanctions and PEP Screening (AMLR Art. 24, 28–31)

- [ ] ✅ Populate `kycProfile.sanctionsScreening` for every customer: `isMatch`, `screeningDate`, `screeningProvider`, `listsChecked[]` (include UN, EU, and national lists).
- [ ] ✅ Populate `kycProfile.adverseMedia` for EDD customers and PEPs: `hasHits`, `screeningDate`, `screeningProvider`, `categories[]`.
- [ ] ✅ For sanctions matches, trigger `kycProfile.monitoringInfo.alerts[]` with `alertType: SANCTIONS_HIT` and escalate per your internal procedures.
- [ ] ⬜ Implement ongoing screening (not just onboarding) — re-screen against updated lists at least monthly for high-risk customers. Update `sanctionsScreening.screeningDate` and `adverseMedia.lastCheckedDate` after each run.

---

## 7. Third-Party CDD Reliance (AMLR Art. 48)

- [ ] ✅ When relying on CDD performed by a third party, set `kycProfile.onboardingChannel` to `THIRD_PARTY_CDD` and populate `kycProfile.thirdPartyCDDReliance`:
  - `relyingPartyId` — your institution's LEI or DID
  - `providingPartyId` — the third party's LEI or DID
  - `relianceScope` — `SDD`, `CDD`, or `EDD`
  - `relianceContractRef` — reference to the written arrangement (AMLR Art. 48(3)(a))
  - `relianceDate` — date the reliance arrangement was established
  - `accessToUnderlyingDataConfirmed: true` — only once you have confirmed (or documented) right of immediate access (AMLR Art. 48(3)(b))
  - `providingPartyEligibilityConfirmed: true` — after assessing the providing party meets Art. 48(1) conditions
  - `liabilityNote` — document that your institution retains ultimate liability (AMLR Art. 48(4))
- [ ] ✅ Record the reliance reference in `kycProfile.auditMetadata.sharingConsentReference`.
- [ ] ⬜ Maintain the written arrangement with the providing party in your legal records. OpenKYCAML stores the contract reference, not the contract itself.
- [ ] ⬜ Perform at least sample-level independent verification for EDD customers — do not rely solely on third-party results for enhanced due diligence.

---

## 8. Record Keeping (AMLR Art. 56)

- [ ] ✅ Populate `kycProfile.auditMetadata.recordCreatedAt`, `recordUpdatedAt`, `recordVersion` for every record.
- [ ] ✅ Set `kycProfile.auditMetadata.dataRetentionDate` to at least 5 years from the end of the business relationship (AMLR Art. 56 minimum; some member state laws require up to 10 years).
- [ ] ✅ Use `kycProfile.auditMetadata.changeLog[]` to record every update, approval, or review event (`CREATED`, `UPDATED`, `REVIEWED`, `APPROVED`). Include `changedBy` and `fieldsChanged`.
- [ ] ✅ Store cryptographic proof of the VC if the identity was verified via EUDI Wallet: `verifiableCredential.proof` provides a tamper-evident audit record.
- [ ] ✅ Set `kycProfile.auditMetadata.dataProvider` when records were received from another institution (group sharing or third-party reliance).

---

## 9. Ongoing Monitoring and Transaction Monitoring (AMLR Art. 21)

- [ ] ✅ Use `kycProfile.monitoringInfo.alerts[]` to record customer-level anomalies (`UNUSUAL_TRANSACTION`, `VELOCITY_BREACH`, `PATTERN_CHANGE`, `PEP_CHANGE`, `ADVERSE_MEDIA`, `SAR_TRIGGER`).
- [ ] ✅ Use the top-level `transactionMonitoring` block for transaction-level monitoring results: `overallOutcome`, `rulesEvaluated[]`, `travelRuleCompliance`, `reportingObligations[]`.
- [ ] ✅ For SAR-triggered alerts, set `alertStatus` to `SAR_TRIGGER` or `SAR_FILED` as appropriate.
- [ ] ⬜ SAR/STR submission to your national FIU is an operational obligation outside schema scope. The `transactionMonitoring.reportingObligations[].reportFiled` and `reportReference` fields can record post-filing evidence.

---

## 10. GDPR and Data Minimisation

- [ ] ✅ Use SD-JWT selective disclosure (`verifiableCredential.selectiveDisclosure`) to present only the minimum attributes necessary for each use case (GDPR Art. 5(1)(c)).
- [ ] ✅ Populate `kycProfile.consentRecord` when processing is based on consent (GDPR Art. 6(1)(a) or Art. 7).
- [ ] ✅ Set `kycProfile.auditMetadata.dataRetentionDate` and implement automated deletion workflows when the date is reached (GDPR Art. 17 right to erasure, balanced against AMLR Art. 56 retention obligations).
- [ ] ✅ For any payload containing special-category data (Art. 9 — biometrics, criminal suspicion) or criminal-offence data (Art. 10), populate `gdprSensitivityMetadata` with `classification: "sensitive_personal"` or `"criminal_offence"` and set `legalBasis` to `GDPR-Art9-2g` or `GDPR-Art10` as appropriate.
- [ ] ✅ Set `gdprSensitivityMetadata.retentionPeriod` to at least `"P5Y"` (AMLR Art. 55 / Art. 56 minimum). Use `gdprSensitivityMetadata.retentionPeriod` in preference to `kycProfile.auditMetadata.dataRetentionDate` for sensitive data where different retention rules apply.
- [ ] ✅ Populate `gdprSensitivityMetadata.disclosurePolicy.allowedRecipients` with the categories of entities permitted to receive sensitive data (e.g. `"regulated_fi"`, `"fiu_only"`).

---

## 11. Tipping-Off Protection and SAR Handling (AMLR Art. 73 / FATF Rec. 21)

> AMLR Art. 73 and FATF Recommendation 21 prohibit disclosing the existence of a SAR/STR or internal suspicion flag to the data subject or unauthorised parties. Violation is a criminal offence in most jurisdictions.

- [ ] ✅ When a Suspicious Activity Report has been filed (or is under consideration) for a customer, set `gdprSensitivityMetadata.classification` to `"sar_restricted"` (post-SAR) or `"internal_suspicion"` (pre-SAR) and `gdprSensitivityMetadata.tippingOffProtected` to `true`.
- [ ] ✅ Populate `gdprSensitivityMetadata.restrictedFields[]` with the RFC 6901 JSON Pointer paths of all SAR-linked fields (e.g. `/kycProfile/adverseMedia`, `/kycProfile/monitoringInfo/alerts`). This scopes the tipping-off restriction to specific fields rather than the entire payload.
- [ ] ✅ Set `gdprSensitivityMetadata.disclosurePolicy.prohibitedRecipients` to include `"data_subject"` and `"counterparty_vasp"` at minimum. Set `allowedRecipients` to `"fiu_only"` and/or `"law_enforcement_authority"` as applicable.
- [ ] ✅ Set `gdprSensitivityMetadata.legalBasis` to `"AMLR-Art73"`.
- [ ] ✅ Do **not** include any SAR-restricted field in the SD-JWT `decodedDisclosures` array. These fields must appear only as SHA-256 digests in the Issuer-JWT `_sd` array and must never be appended as disclosures in any presentation token. This is the cryptographic enforcement layer for the policy hint above.
- [ ] ✅ Set `gdprSensitivityMetadata.auditReference` to an opaque case reference (SHA-256 hash or UUID). This MUST NOT contain the SAR narrative, case details, or any information that would itself constitute tipping-off if exposed.
- [ ] ⬜ Do not include SAR-restricted OpenKYCAML credentials in EUDI Wallet user-visible credential list views. If your wallet integration uses the `gdprSensitivityMetadata.tippingOffProtected` flag, instruct the wallet delivery system to suppress display of the credential's restricted fields in the UI.
- [ ] ⬜ SAR/STR submission to your national FIU remains an operational obligation outside schema scope. Record post-filing evidence in `transactionMonitoring.reportingObligations[].reportFiled` and `reportReference`.

---

## 12. AMLA RTS — Items Requiring Re-Review After Publication

The following items are captured in the schema with placeholder fields or notes. Review and update them when the referenced AMLA RTS is published:

| RTS | Expected AMLA action | Schema field to update |
|---|---|---|
| RTS on CDD attribute sets (Art. 22(4)) | Binding minimum attribute lists per SDD/CDD/EDD tier | `kycProfile.dueDiligenceRequirements.verifiedAttributes` and `rtsComplianceNote` |
| RTS on EDD for high-risk third countries (Art. 29(4)) | Specific mandatory EDD measures | `kycProfile.dueDiligenceRequirements` (add measures as verified attributes) |
| RTS on CDD reliance conditions (Art. 48(5)) | Form of written arrangement; eligible third-party types | `kycProfile.thirdPartyCDDReliance` (already structured; confirm field alignment) |
| RTS on PEP lists / harmonised taxonomy (Art. 28(3) / Art. 31) | Final harmonised PEP category names and list criteria | `kycProfile.pepStatus.pepCategory` enum (update description and examples once binding) |
| Guidelines on risk factors (Art. 20(6)) | Risk factor taxonomy and weighting guidance | `kycProfile.riskRatingDetail.riskFactors` (confirm factor names align with guidelines) |

---

*Document version: v1.12.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*
*For schema field reference, see [mapping-ivms101-eidas-amlr.md](../mappings/mapping-ivms101-eidas-amlr.md) and the [compliance matrix](compliance-matrix.md).*
