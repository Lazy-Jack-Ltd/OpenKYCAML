# Changelog

All notable changes to OpenKYCAML are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

For the full project roadmap and planned features, see [ROADMAP.md](ROADMAP.md).

---

## [Unreleased]

---

## [1.18.0] — April 2026

### Changed — v1.18.0: W3C VC Data Model 2.0 upgrade

Upgraded the `VerifiableCredentialWrapper` from W3C VC Data Model v1.1 to the W3C VC DM 2.0 Recommendation (published May 2024). Only payloads that include a `verifiableCredential` block are affected; all other schema structure is unchanged.

#### Schema changes

- **`VerifiableCredentialWrapper.$defs`**: `@context[0]` const changed from `https://www.w3.org/2018/credentials/v1` to `https://www.w3.org/ns/credentials/v2`.
- **`issuanceDate`** (required string, ISO 8601) **renamed to `validFrom`**.
- **`expirationDate`** (optional string, ISO 8601) **renamed to `validUntil`**.
- All 23 VC-bearing example payloads updated to use the new field names and context URL.
- All "planned for v2.0.0" deferral notes removed from schema, validator, and documentation.
- `TinIdentifier.issuanceDate` is a separate field and remains **unchanged**.

#### New documentation

- **`docs/reference/vc-data-model-migration.md`** — migration reference and adopter checklist for upgrading existing VC payloads from v1.1 to v2.0.
- **`docs/guides/eudi-wallet-integration.md`** updated to reflect VC DM 2.0 context URL and `validFrom`/`validUntil` field names.
- **Compliance matrix §27** — VC DM 2.0 alignment section added.

#### Backward compatibility

Only payloads with a `verifiableCredential` block are affected. Non-VC payloads (IVMS 101 only, `kycProfile`, `taxStatus`, etc.) require no changes. Adopters of VC payloads must update `@context[0]`, rename `issuanceDate` → `validFrom`, and optionally rename `expirationDate` → `validUntil`.

---

## [1.17.0] — April 2026

### Added — v1.17.0: Extended structured array properties (PersonIdentifier, RiskRatingEntry, RevenueRecord, ConsentRecord)

All additions are optional and backward-compatible. No existing required fields changed. Version: `1.17.0`.

#### New $defs

- **`PersonIdentifier`** — 17-value `identifierType` enum for natural person identifier categorisation (NATIONAL_ID, PASSPORT, DRIVERS_LICENCE, TAX_ID, SOCIAL_SECURITY, BIRTH_CERTIFICATE, VOTER_ID, RESIDENT_PERMIT, WORK_PERMIT, STUDENT_ID, MILITARY_ID, HEALTH_CARD, PROFESSIONAL_LICENCE, CREDIT_BUREAU_ID, BIOMETRIC_ID, DIGITAL_ID, OTHER).
- **`RiskRatingEntry`** — structured risk rating history entry with `riskRating`, `riskScore`, `ratedAt`, `ratedBy`, `ratingMethod`, and optional `notes`.
- **`RevenueRecord`** — timestamped revenue record with `amount`, `currency`, `period`, `source`, and optional `verificationDate`.
- **`ConsentRecord`** — GDPR/AML consent record with `consentType`, `givenAt`, `withdrawnAt`, `legalBasis`, `dataCategories[]`, and `consentVersion`.

#### New array properties — 12 additive fields

- **`NaturalPerson`**: `naturalPersonIdentifiers[]` (`$ref PersonIdentifier`), `countriesOfResidence[]` (ISO 3166-1 alpha-2), `nationalities[]` (ISO 3166-1 alpha-2), `occupations[]` (structured occupation array), `emergencyContacts[]` (`$ref EmergencyContact`).
- **`LegalPerson`**: `legalNationalIdentifiers[]` (`$ref PersonIdentifier`), `revenueHistory[]` (`$ref RevenueRecord`), `registeredAgents[]` (`$ref RegisteredAgent`).
- **`KYCProfile`**: `pepStatuses[]` (structured PEP status history), `riskRatingHistory[]` (`$ref RiskRatingEntry`), `consentRecords[]` (`$ref ConsentRecord`).
- **`EntityGovernance`**: `parentCompanies[]` (array of `EntityReference`).

#### Version, snapshot, and documentation

- `schema/kyc-aml-hybrid-extended.json`: `$id` and `version` bumped to `v1.17.0`.
- `schema/versions/v1.17.0.json`: versioned snapshot created.
- `docs/compliance/compliance-matrix.md` §26: extended array grouping section added.
- New examples: `examples/array-grouping-v1-17.json` (natural person) and `examples/array-grouping-legal-entity-v1-17.json` (legal entity).

---

## [1.16.0] — April 2026

### Added — v1.16.0: Company Identifiers — structured legal entity identifier types

All additions are optional and backward-compatible. No existing required fields changed. Version: `1.16.0`.

#### New $defs

- **`CompanyIdentifier`** — structured company identifier with a 23-value `identifierType` enum: `DUNS`, `LEI`, `CRN_GB`, `SIREN_FR`, `SIRET_FR`, `HRB_DE`, `HRA_DE`, `CNPJ_BR`, `ABN_AU`, `ACN_AU`, `EIN_US`, `CIK_US`, `CAGE_US`, `PIC_EU`, `BVDID`, `ISIN`, `BIC`, `CHARITY_GB`, `KVK_NL`, `UID_AT`, `NIF_ES`, `RCS_LU`, `OTHER`. An `if`/`then` constraint requires `identifierIssuingBody` when `identifierType` is `OTHER`.

#### `LegalPerson` additions

- `companyIdentifiers[]` — optional array of `$ref CompanyIdentifier`. Enables multi-registry legal entity identification beyond IVMS 101 `nationalIdentification` (LEIX/RAID/etc.).

#### Version, snapshot, and documentation

- `schema/kyc-aml-hybrid-extended.json`: `$id` and `version` bumped to `v1.16.0`.
- `schema/versions/v1.16.0.json`: versioned snapshot created.
- `docs/compliance/compliance-matrix.md` §25: company identifier section added.
- New example: `examples/company-identifiers.json`.

---

## [1.15.0] — April 2026

### Changed — v1.15.0: Schema hardening — strict mode, mandatory field validation, and structural improvements

All changes are additive or constraint-tightening. No fields removed; no existing valid payloads broken (payloads with empty-string values on critical fields will now fail validation). Version: `1.15.0`.

#### Schema hardening

- **`additionalProperties: false`** added at root level — payloads may not include unrecognised root properties. Prevents silent schema drift.
- **`messageType`** — new optional root string property for message classification (e.g. `TRAVEL_RULE`, `CDD_SHARE`, `ONBOARDING`).
- **`minLength: 1`** enforced on 10 critical fields: `primaryIdentifier`, `nationalIdentifier`, `customerIdentification`, `legalPersonName`, `currentLegalName`, `uniqueIdentifier`, `taxReferenceNumber`, `customerNumber`, `emailAddress`, `phoneNumber`. Prevents semantically empty strings.
- **Root `examples` array** — added to schema for tooling/IDE support.

#### Conditional constraints

- **`NaturalPerson` allOf** — new `if`/`then` constraint: `isDeceased: true` **requires** `deceasedDate`. Prevents records marked deceased without a date.
- **`uniqueItems: true`** on `NaturalPerson.tags[]`, `LegalPerson.tags[]`, and `KYCProfile.tags[]` — prevents duplicate tag entries.

#### New $defs

- **`EUDIWalletPresentationContext`** — structured EUDI Wallet presentation context object.

#### Documentation and tooling

- `schema/kyc-aml-hybrid-extended.json`: `$id` and `version` bumped to `v1.15.0`.
- `schema/versions/v1.15.0.json`: versioned snapshot created.
- `_comment*` / `_disclaimer` annotation strings stripped from 18 example files to comply with `additionalProperties: false`.
- `examples/sd-jwt-compact-token.json` stripped of SD-JWT compact token format fields not conforming to the schema.
- Both Python and JS validators updated to reflect new constraints.

---

## [1.14.0] — April 2026

### Changed — v1.14.0: Schema cleanup — alias removal, `isPrimary` constraints, and `EntityReference` rename

All changes remove deprecated aliases or tighten existing constraints. No new fields added. Version: `1.14.0`.

#### Removed deprecated alias fields

Eight alias fields that duplicated information already captured in primary fields were removed:

- `isPep` (alias of `pepStatus.isPep`) from `KYCProfile`
- `lastPepCheckDate` (alias of `pepStatus.lastCheckDate`) from `KYCProfile`
- `SanctionsScreening.status` (alias of `sanctionsScreening.overallResult`)
- `SanctionsScreening.lastScreenedDate` (alias of `sanctionsScreening.lastScreened`)
- `AdverseMedia.lastCheckedDate` (alias of `adverseMedia.lastChecked`)
- `AuditMetadata.timestamp` (alias of `auditMetadata.createdAt`)
- `lastKycReviewDate` (alias of `monitoringInfo.lastReviewDate`) from `KYCProfile`
- `BeneficialOwner.naturalPerson` (alias of `BeneficialOwner.person`)

#### Removed legacy contact string fields

Five legacy single-string contact fields removed from `NaturalPerson` and `LegalPerson` (superseded by the typed arrays added in v1.13.0):

- `emailAddress`, `phoneNumber`, `mobileNumber` from `NaturalPerson`
- `emailAddress`, `phoneNumber` from `LegalPerson`

#### Removed deprecated array field

- `KYCProfile.sourceOfFundsWealth` (untyped string array) removed; replaced by the structured `SourceOfFundsWealth` $def introduced in an earlier version.

#### Renamed $def

- **`ParentCellCompanyReference` renamed to `EntityReference`** — the $def now serves as a general-purpose parent/related-entity reference, not just for cell company parent linkage.

#### `isPrimary` constraints

- `maxContains: 1` constraints added to 6 arrays to enforce at most one `isPrimary: true` item: `NaturalPerson.emailAddresses[]`, `NaturalPerson.phoneNumbers[]`, `LegalPerson.emailAddresses[]`, `LegalPerson.phoneNumbers[]`, `NaturalPerson.addresses[]`, `LegalPerson.addresses[]`.

#### Version, snapshot, and documentation

- `schema/kyc-aml-hybrid-extended.json`: `$id` and `version` bumped to `v1.14.0`.
- `schema/versions/v1.14.0.json`: versioned snapshot created.
- Python and JavaScript validators updated to remove references to removed fields.

---

## [1.13.0] — April 2026

### Added — v1.13.0: CRM completeness — 20 contact/account field gaps closed (P1–P4)

All additions are optional and backward-compatible. No existing required fields changed. Version: `1.13.0`.

#### New $defs

- **`EmailAddress`** — typed email address entry with `emailType` (WORK/PERSONAL/OTHER), `emailAddress`, `isPrimary`, `verificationStatus`.
- **`EmergencyContact`** — emergency contact / next-of-kin with `name`, `relationship`, `phoneNumber`, `emailAddress`. GDPR Art. 9 note included.
- **`IndustryCode`** — structured industry classification entry with `codeSystem` (NAICS/NACE/SIC/ISIC/OTHER), `codeValue`, `codeDescription`.
- **`Mandate`** — authorised-signatory mandate with `signatoryName`, `signatoryRef`, `mandateType` (SOLE/JOINT_ANY_TWO/JOINT_ALL/LIMITED/OTHER), `scope`, `effectiveFrom`, `effectiveTo`.
- **`PhoneNumber`** — typed phone number entry with `phoneType` (WORK/MOBILE/HOME/FAX/DIRECT/OTHER), `phoneNumber` (E.164), `isPrimary`.
- **`RegisteredAgent`** — registered agent / company secretary with `name`, `jurisdiction`, `address`, `agentType` (REGISTERED_AGENT/COMPANY_SECRETARY/RESIDENT_DIRECTOR/OTHER).

#### `NaturalPersonNameIdentifier` — Gap 1 (CRM name completeness)

Added 6 optional fields: `salutation` (MR/MRS/MS/MISS/DR/PROF/REV/OTHER), `middleName`, `nameSuffix`, `preferredName`, `formerName`, `pronouns` (GDPR Art. 9 note).

#### `DateAndPlaceOfBirth` — Gap 3 (structured country of birth)

Added `countryOfBirth` (ISO 3166-1 alpha-2). Complements free-text `placeOfBirth`. Aligns with IVMS 101 optional field and eIDAS 2.0 PID.

#### `Address` — Gap 5 (richer address type vocabulary + history tracking)

- Expanded `addressType` enum to include: `HOME`, `REGISTERED_OFFICE`, `PRINCIPAL_PLACE_OF_BUSINESS`, `MAILING`, `BILLING`, `SHIPPING`, `CORRESPONDENCE`, `PREVIOUS`, `OTHER` (GEOG and BIZZ retained for IVMS 101 back-compat).
- Added `isPrimary` (boolean), `effectiveFrom` (date), `effectiveTo` (date) for historical address tracking.

#### `NaturalPerson` — Gaps 2, 4, 6, 7, 8, 17, 19, 20

- **Gap 2**: `isDeceased` (boolean), `deceasedDate` (date).
- **Gap 4**: `emailAddresses[]` (`$ref EmailAddress`), `phoneNumbers[]` (`$ref PhoneNumber`), `faxNumber`. Supplement legacy single-string fields; prefer arrays for new integrations.
- **Gap 6**: `preferredLanguage` (BCP 47), `preferredCommunicationChannel` (EMAIL/PHONE/SMS/POST/PORTAL/OTHER), `marketingOptOut`.
- **Gap 7**: `maritalStatus` (SINGLE/MARRIED/CIVIL_PARTNERSHIP/SEPARATED/DIVORCED/WIDOWED/OTHER/PREFER_NOT_TO_SAY). GDPR Art. 9 note.
- **Gap 8**: `numberOfDependants` (integer ≥ 0), `householdSize` (integer ≥ 1).
- **Gap 17**: `emergencyContact` (`$ref EmergencyContact`).
- **Gap 19**: `tags[]` (string array), `customAttributes` (open object).
- **Gap 20**: `historicalNames[]` — array of `{ name, nameType (MAIDEN/PREVIOUS_LEGAL/ALIAS/TRADING/OTHER), effectiveFrom, effectiveTo }`. Critical for PEP/sanctions screening against all known aliases.

#### `LegalPerson` — Gaps 4, 9, 10, 11, 12, 13, 19

- **Gap 4**: `emailAddresses[]`, `phoneNumbers[]`, `faxNumber`.
- **Gap 9**: `dateOfIncorporation`, `dateOfRegistration`, `dateOfDissolution`, `operationalStatus` (ACTIVE/DORMANT/IN_LIQUIDATION/DISSOLVED/STRUCK_OFF/SUSPENDED/OTHER).
- **Gap 10**: `numberOfEmployees` (integer ≥ 0), `annualRevenue` (number ≥ 0), `annualRevenueCurrency` (ISO 4217), `annualRevenueVerificationDate`.
- **Gap 11**: `websiteUrl` (URI), `socialMediaProfiles[]` — `{ platform (LINKEDIN/TWITTER/FACEBOOK/INSTAGRAM/YOUTUBE/OTHER), url, isVerified }`.
- **Gap 12**: `industryCodes[]` (`$ref IndustryCode`). Structured NAICS/NACE/SIC codes alongside free-text `industrySector` in KYCProfile.
- **Gap 13**: `registeredAgent` (`$ref RegisteredAgent`).
- **Gap 19**: `tags[]`, `customAttributes`.

#### `LegalPersonIdentificationData` — Gap 18 (structured mandates)

`mandates[]` array items now reference the new `Mandate` $def (previously an untyped opaque array).

#### `EntityGovernance` — Gap 15 (GLEIF ultimate parent / group structure)

Added: `ultimateParentLEI` (ISO 17442 20-char pattern), `ultimateParentName`, `groupName`, `groupLEI` (ISO 17442 20-char pattern).

#### `KYCProfile` — Gaps 14, 16, 19

- **Gap 14**: `relationshipManagerId`, `relationshipManagerName`, `primaryBranchCode`, `servingBusinessUnit`.
- **Gap 16**: `customerSegment` (MASS_MARKET/AFFLUENT/PRIVATE_BANKING/ULTRA_HIGH_NET_WORTH/INSTITUTIONAL/SME/MID_MARKET/LARGE_CORPORATE/OTHER), `estimatedNetWorth`, `estimatedNetWorthCurrency` (ISO 4217), `estimatedNetWorthDate`.
- **Gap 19**: `tags[]`, `customAttributes`.

#### Version, snapshot, and documentation

- `schema/kyc-aml-hybrid-extended.json`: `$id` and `version` bumped to `v1.13.0`.
- `schema/versions/v1.13.0.json`: versioned snapshot created.
- `docs/compliance/compliance-matrix.md` §24: CRM completeness section added.
- `README.md`: schema version badge and version tree updated to `v1.13.0`.

---

## [1.12.0] — April 2026

### Added — v1.12.0: Natural-person completeness, entity governance flags, and review lifecycle state machine

Three independent optional extensions that close CDD data gaps identified in the v1.11.2 compliance gap analysis. All additions are backward-compatible; no existing required fields changed.

#### 1. Natural-person completeness — `gender` and `occupation` (IVMS 101 / eIDAS 2.0 alignment)

- **`schema/kyc-aml-hybrid-extended.json`** (`$defs` → `NaturalPerson`): added two optional properties:
  - `gender` (string enum: `MALE`, `FEMALE`, `NON_BINARY`, `OTHER`, `PREFER_NOT_TO_SAY`). Maps to eIDAS 2.0 PID `gender` attribute (ISO/IEC 5218). GDPR Art. 9 special-category data — collect only where lawfully required.
  - `occupation` (object with `occupationCode` enum (`EMPLOYED`, `SELF_EMPLOYED`, `BUSINESS_OWNER`, `STUDENT`, `RETIRED`, `UNEMPLOYED`, `PUBLIC_OFFICIAL`, `OTHER`) and free-text `occupationDescription` max 200). Aligned with ILO/ISCO-08 broad categories, IVMS 101 extended CDD, and eIDAS 2.0 PID `occupation` attribute. Complements — does not replace — the existing `kycProfile.customerClassification.occupationOrPurpose` free-text field.
- **`docs/mappings/natural-person-governance.md`**: new mapping document covering `gender` and `occupation`, eIDAS PID / IVMS 101 alignment, GDPR Art. 9 guidance, and JSON examples.
- **`examples/natural-person-gender-occupation.json`**: new example showing a natural person with `gender: FEMALE`, `occupation.occupationCode: SELF_EMPLOYED`, and `reviewLifecycle` state history.

#### 2. Legal-entity governance flags — `EntityGovernance` $def + `LegalPerson.entityGovernance`

- **`schema/kyc-aml-hybrid-extended.json`** (`$defs`): added new `EntityGovernance` $def with all properties optional:
  - `regulatoryStatus` (enum: `REGULATED`, `RECOGNISED`, `UNREGULATED`, `EXEMPT`) — fills "no top-level regulatoryStatus" gap.
  - `regulators[]` (array of `regulatorName` / `jurisdiction` / `licenceNumber` objects) — fills "no array for multiple regulators" gap; critical for cross-border CDD reliance (AMLR Art. 48).
  - `listedStatus` (inline object: `isListed` boolean, `marketIdentifier` ISO 10383 MIC, `recognisedMarket` boolean) — fills "entity is listed / listed on a recognised market" gaps.
  - `parentCompany` (`$ref: ParentCellCompanyReference`) — reuses existing $def for non-cell entity parent linkage.
  - `parentRegulated` (boolean) — fills "parent is regulated" gap.
  - `parentListed` (boolean) — fills "parent is listed" gap.
  - `majorityOwnedSubsidiary` (boolean) — fills "majority owned subsidiary" gap.
  - `stateOwned` (boolean) — fills "state owned" gap.
  - `governmentOwnershipPercentage` (number 0–100) — fills "government ownership percentage" gap.
- **`schema/kyc-aml-hybrid-extended.json`** (`$defs` → `LegalPerson`): added optional `entityGovernance` property (`$ref: EntityGovernance`).
- **`docs/mappings/entity-governance.md`**: new mapping document covering all `EntityGovernance` fields, regulatory basis (FATF Rec. 24/25, AMLR Art. 26/48, MAR), and full JSON example.
- **`examples/legal-entity-governance.json`**: new example showing a dual-regulated, exchange-listed subsidiary with full `entityGovernance` block and `reviewLifecycle` state history.

#### 3. Review lifecycle state machine — `ReviewLifecycle` $def + `MonitoringInfo.reviewLifecycle`

- **`schema/kyc-aml-hybrid-extended.json`** (`$defs`): added new `ReviewLifecycle` $def:
  - `currentState` (string enum: `ONBOARDING`, `INITIAL_REVIEW`, `PERIODIC_REVIEW`, `TRIGGERED_REVIEW`, `OFFBOARDING`, `TERMINATED`) — fills "no formal state machine" gap.
  - `stateHistory[]` (array with required `state` enum + `enteredAt` date-time, optional `exitedAt`, `triggeredBy`, `notes` max 500) — full timestamped audit trail.
- **`schema/kyc-aml-hybrid-extended.json`** (`$defs` → `MonitoringInfo`): added optional `reviewLifecycle` property (`$ref: ReviewLifecycle`). Complements existing `monitoringStatus` with structured history for AMLR Art. 21 auditability.

#### 4. Version bump, snapshot, and documentation

- `schema/kyc-aml-hybrid-extended.json`: `$id` and `version` bumped to `v1.12.0`.
- `schema/versions/v1.12.0.json`: versioned snapshot created.
- `docs/compliance/compliance-matrix.md` §23: new section covering all three extensions with full regulatory mapping.
- `README.md`: schema version badge updated to `v1.12.0`.

---

## [1.11.2] — April 2026

### Fixed — v1.11.2 Polish (cell identifier disambiguation, recursion-depth guidance, predictive AML cell scores, compliance matrix)

#### 1. Field-name disambiguation — `cellIdentifier` (Low)

- **`schema/kyc-aml-hybrid-extended.json`** (`$defs` → `CellCompanyDetails`): clarified `cellIdentifier` description to explicitly state it is the sole cell identifier field; added note that the historical draft name `cellCompanyIdentifier` was never adopted.
- **`docs/mappings/cell-company.md`** §3 table: added note to `cellIdentifier` row — *"This is the sole cell identifier field; do not use `cellCompanyIdentifier` (historical draft name, never adopted)."*

#### 2. `ParentCellCompanyReference` recursion-depth guidance (Medium)

- **`schema/kyc-aml-hybrid-extended.json`** (`$defs` → `ParentCellCompanyReference`): appended sentence — *"Use `legalEntityIdentifier` + `jurisdiction` as the primary reference link. For performance-critical or deeply-nested cell-of-cell payloads, avoid embedding full parent objects — reference by identifier only."*
- **`docs/mappings/cell-company.md`** §4: mirrored the recursion-depth guidance as a blockquote.

#### 3. Predictive AML — cell-level scores (Low)

- **`schema/kyc-aml-hybrid-extended.json`** (`$defs` → `PredictiveAML`): added optional `cellLevelPredictiveScores[]` array. Each item has `cellIdentifier` (string, required) + `scores[]` (array with `scoreType`, `value`, `confidence`, optional `horizonDays` and `timestamp`).
- **`schema/predictive-aml/v1.11.2.json`**: new versioned standalone PredictiveAML schema including `cellLevelPredictiveScores`.
- **`docs/mappings/cell-company.md`** §5.1: new sub-section documenting `predictiveAML.cellLevelPredictiveScores[]` with field reference table.
- **`examples/cell-company/pcc-cell-predictive-aml.json`**: new example showing a PCC cell with both `kycProfile.cellRiskProfileOverride` and `predictiveAML.cellLevelPredictiveScores`.

#### 4. Compliance matrix — Cell structures row (Documentation)

- **`docs/compliance/compliance-matrix.md`** §1 (FATF Rec. 24 and Rec. 25 rows): added explicit Cell structures (PCC/ICC) references to `cellCompanyDetails`, `parentCellCompanyReference`, `cellRiskProfileOverride` with cross-reference to §22.
- **`docs/compliance/compliance-matrix.md`** §2 (AMLR Art. 26 row): added Cell structures cross-reference to §22.
- Document footer updated to v1.11.2.

#### 5. Version bump and snapshot

- `schema/kyc-aml-hybrid-extended.json`: `$id` and `version` bumped to `v1.11.2`.
- `schema/versions/v1.11.2.json`: versioned snapshot created.
- `README.md`: schema version badge updated to `v1.11.2`.

**No breaking changes.** All schema additions are optional properties; all documentation changes are additive.

---

## [1.11.1] — April 2026

### Changed — Cell Company Constraints Promoted to Schema-Enforced Rules

Both cell company conditions that were previously advisory business warnings in the Python and Node.js validators have been promoted to hard JSON Schema `if`/`then` constraints. Payloads that violate them now fail schema validation rather than producing warnings.

#### Schema changes (`$defs`)

**`CellCompanyDetails`** — new `if`/`then` at the object level:
- If `isCellCompanyIssuer` is `true` → `issuancePurpose` is **required**.
- Prevents issuer vehicles from omitting instrument-level classification (previously a soft advisory).

**`LegalPerson`** — existing `if`/`then`/`else` chain (entityType → typed sub-object) restructured into `allOf` to support multiple independent conditionals; new constraint added:
- If `cellCompanyDetails.cellCompanyType` is `PCC_CELL` or `ICC_CELL` → `parentCellCompanyReference` is **required**.
- Prevents orphan cell records that cannot be linked to a PCC/ICC Core (previously a soft advisory; now a schema validation error).

#### Validator changes

- **Python validator** (`tools/python/validator.py`) — cell company advisory warning blocks removed; conditions are now enforced by the schema itself.
- **Node.js validator** (`tools/javascript/validator.js`) — same removal.

#### Backward compatibility

- Payloads that previously satisfied both conditions (cell with parent ref; issuer with purpose) are unaffected — they still validate correctly.
- Payloads that previously triggered warnings will now fail schema validation. This is the intended behaviour: the conditions represent genuine compliance requirements (FATF Rec. 24, AMLR Art. 26) that must be enforced, not just advised upon.

---

## [1.11.0] — April 2026

### Added — Cell Company Support (PCC / ICC)

#### New $defs
- **`CellCompanyType`** — string enum `["NONE", "PCC_CORE", "PCC_CELL", "ICC_CORE", "ICC_CELL"]` for precise classification of cell-structured entities.
- **`CellCompanyDetails`** — structured metadata for PCC/ICC cells and cores:
  - `cellCompanyType` (required, `$ref: CellCompanyType`)
  - `cellIdentifier` — unique cell number/name, pattern `^[A-Za-z0-9 \-]{1,64}$`
  - `cellName` — human-readable cell description, `maxLength: 128`
  - `cellRegistrationNumber` — ICC cell registration number, pattern `^[A-Z0-9]{1,35}$` (ICC cells only)
  - `hasIndependentLegalPersonality` — boolean; `true` for ICC cells (independent legal personality), `false` for PCC cells
  - `isCellCompanyIssuer` — boolean; `true` when cell is a securities/ILS issuer vehicle
  - `issuancePurpose` — enum `["INSURANCE_LINKED_SECURITY", "CATASTROPHE_BOND", "STRUCTURED_NOTE", "DEBT_INSTRUMENT", "OTHER"]`
  - `cellSpecificInstrumentReference` — `format: "uri"` link to instrument/prospectus
- **`ParentCellCompanyReference`** — required parent link for any cell:
  - `legalEntityIdentifier` (required) — LEI or registration number of parent Core, pattern `^[A-Z0-9]{1,35}$`
  - `jurisdiction` (required) — ISO 3166-1 alpha-2 of parent Core's incorporation jurisdiction
  - `parentName` — registered name of parent Core, `maxLength: 128`

#### `LegalPerson` extensions (all optional, backward-compatible)
- `cellCompanyDetails` — `$ref: CellCompanyDetails`
- `parentCellCompanyReference` — `$ref: ParentCellCompanyReference`
- `cellRiskProfileOverride` — `$ref: RiskSnapshot` — cell-level risk snapshot where cell risk differs from Core
- `cellSourceOfFundsWealth` — `$ref: SourceOfFundsWealth` — cell-level source of funds (AMLR Art. 29, FATF Rec. 12)
- `cellAuditMetadata` — `$ref: AuditMetadata` — per-cell audit trail (AMLR Art. 56 5-year retention)

#### Documentation
- **`schema/versions/v1.11.0.json`** — versioned snapshot.
- **`docs/mappings/cell-company.md`** + **`.yaml`** — new mapping document covering PCC/ICC structures, field rationale, KYC/AML obligations, and regulatory jurisdictions.
- **`docs/compliance/compliance-matrix.md §22`** — Cell Company and Special Purpose Vehicle section.
- **`docs/diagrams/schema-er-diagram.md`** — `CellCompanyDetails`, `CellCompanyType`, `ParentCellCompanyReference` entities with relationships; footer updated to v1.11.0.
- **`docs/reference/typescript-types.md`** — `CellCompanyDetails`, `CellCompanyType`, `ParentCellCompanyReference` interfaces.

#### Validator business warnings (Python + Node.js)
- `legalPerson.cellCompanyDetails.cellCompanyType` is `PCC_CELL` or `ICC_CELL` but `parentCellCompanyReference` is absent → FATF beneficial-ownership tracing / AMLR Art. 26 advisory.
- `cellCompanyDetails.isCellCompanyIssuer` is `true` but `issuancePurpose` is absent → instrument-level classification advisory.

#### New examples
- `examples/cell-company/pcc-cell.json` — Guernsey PCC Cell 7 (catastrophe bond issuer, no independent legal personality).
- `examples/cell-company/icc-cell.json` — Jersey ICC Cell 3 (marine ILS, independent legal personality, `cellRegistrationNumber`, `cellSourceOfFundsWealth`).

### Changed
- `schema/kyc-aml-hybrid-extended.json` — version bumped from `1.10.0` to `1.11.0`; `$id` updated.
- All additions are strictly additive and backward-compatible with v1.10.x and earlier payloads.

- `docs/naming-convention.md` — new document defining the repository-wide file and directory naming convention (lowercase kebab-case, sub-folder organisation for docs, pattern rules for examples, schema versions, and versioned artefacts).

---

## [1.10.0] — April 2026

### Added — Enhanced Validation: Format and Pattern Completeness

#### New `BankingDetails` $def — IBAN / BIC / account data
- **`BankingDetails` $def** — New reusable financial account definition wired as `bankingDetails[]` arrays on both `NaturalPerson` and `LegalPerson`. Fields:
  - `iban` — `type: string`, ISO 13616 structural pattern `^[A-Z]{2}[0-9]{2}[A-Z0-9]{4,30}$`, `maxLength: 34`.
  - `bic` — `type: string`, ISO 9362 pattern `^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$` (8-char and 11-char BIC), `maxLength: 11`.
  - `bankName` — `type: string`, `maxLength: 140`.
  - `accountCurrency` — `type: string`, ISO 4217 pattern `^[A-Z]{3}$`, `maxLength: 3`.
  - `accountType` — `enum: ["CURRENT", "SAVINGS", "CORRESPONDENT", "CRYPTO_FIAT_GATEWAY", "OTHER"]`.
  - `bankingCountry` — `type: string`, pattern `^[A-Z]{2}$`.

#### Contact fields on `NaturalPerson` and `LegalPerson`
- **`emailAddress`** — `type: string`, `format: "email"`, `maxLength: 254` (RFC 5321). Added to both `NaturalPerson` and `LegalPerson`. Addresses the most impactful format gap for B2B data exchange; aligns with FATF Rec. 16 counterparty contact requirements and AMLR Art. 22 CDD.
- **`phoneNumber`** — `type: string`, E.164 pattern `^\+[1-9]\d{1,14}$`, `maxLength: 16`. Added to both `NaturalPerson` and `LegalPerson`.
- **`mobileNumber`** — `type: string`, same E.164 pattern, `maxLength: 16`. Added to both `NaturalPerson` and `LegalPerson`. Separate field for mTAN/OTP delivery in remote CDD (AMLR Art. 22(5)) and EUDI Wallet notification flows.

#### Patterns on existing regulatory identifier fields
- **`LegalPersonIdentificationData.vatRegistrationNumber`** — pattern `^[A-Z]{2}[A-Z0-9]{2,12}$` (EU VAT structural form: 2-char country prefix + 2–12 alphanumeric).
- **`LegalPersonIdentificationData.eoriNumber`** — pattern `^[A-Z]{2}[A-Z0-9]{1,15}$` (EU/UK EORI: country prefix + up to 15 alphanumeric).
- **`LegalPersonIdentificationData.europeanUniqueIdentifier`** — pattern `^[A-Z]{2}-[A-Za-z0-9.\-]{6,40}$` (eIDAS EUID: CC-RegistrationAuthority-RegistrationNumber format per Directive (EU) 2017/1132).
- **`IndirectTaxRegistration.registrationNumber`** — pattern `^[A-Z0-9\-\/]{2,30}$` (generic: 2–30 uppercase alphanumeric with hyphens/slashes; covers EU VAT, India GSTIN, Australia ABN, Canada HST/PST).
- **`TinIdentifier.tinValue`** — pattern `^[A-Z0-9\-\/]{5,20}$` (5–20 uppercase alphanumeric with hyphens/slashes; intentionally loose to cover global TIN formats; jurisdiction-specific validation is a runtime concern).
- **`FatcaStatus.withholdingAgentReference`** — pattern `^[A-Z0-9\-]{1,30}$`, `maxLength: 30`.

#### Patterns on document number fields
- **`NaturalPersonDocument.documentNumber`** — pattern `^[A-Z0-9\-\/ ]{1,50}$` (allows standard global passport and national ID formats; rejects control characters).
- **`LegalEntityDocument.documentNumber`** — pattern `^[A-Z0-9\-\/ ]{1,100}$`.
- **`LegalEntityDocument.registrationNumber`** — pattern `^[A-Z0-9\-\/ ]{1,100}$`.

#### Miscellaneous field tightening
- **`Originator.accountNumber` items**, **`Beneficiary.accountNumber` items** — pattern `^[A-Za-z0-9\-\/.]{1,100}$` (mixed-case to support Ethereum 0x hex, Bitcoin bech32, IBANs, and proprietary identifiers).
- **`NationalIdentification.registrationAuthority`** — pattern `^RA[0-9]{6}$` (GLEIF RAL code format; aligns with `RegistrationAuthorityDetail.ralCode`).
- **`TransactionMonitoring` currency sub-fields** (`jurisdictionThreshold.currency`, `reportingThreshold.currency`) — pattern `^[A-Z]{3}$` (ISO 4217).
- **`IVMS101Payload.transferredAmount.assetType`** — pattern `^[A-Z]{3,10}$` (ISO 4217 currency codes and crypto-asset tickers 3–10 uppercase chars).
- **`Address.postCode`** — pattern `^[A-Z0-9\- ]{2,10}$` (generic: 2–10 uppercase alphanumeric with hyphens and spaces; country-specific validation is a runtime concern).

#### Documentation
- **`schema/versions/v1.10.0.json`** — versioned snapshot of canonical schema.
- **`docs/mappings/contact-financial-identifiers.md`** + **`.yaml`** — new mapping document covering email/phone/IBAN/BIC alignment with IVMS 101, FATF Rec. 16, ISO 13616/9362, and eIDAS contact field requirements.
- **`docs/compliance/compliance-matrix.md §21`** — Format and Pattern Completeness section.
- **`docs/diagrams/schema-er-diagram.md`** — `BankingDetails` entity added with relationships to `NaturalPerson` and `LegalPerson`; footer updated to v1.10.0.
- **`docs/reference/typescript-types.md`** — `BankingDetails` interface added.

#### Validator business warnings (Python + Node.js)
- Missing `emailAddress` or `phoneNumber` on a natural person with `dueDiligenceType: ENHANCED` — FATF Rec. 16 / AMLR Art. 22 contact requirement advisory.
- `bankingDetails` entry with `iban` present but no `bic` — SEPA/correspondent banking reconciliation advisory.

#### New examples
- `examples/contact-banking/natural-person-with-contact.json` — natural person with email, E.164 phone, and IBAN/BIC banking details.
- `examples/contact-banking/legal-entity-with-banking.json` — legal entity with contact fields and full `BankingDetails` entry.

### Changed
- `schema/kyc-aml-hybrid-extended.json` — version bumped from `1.9.1` to `1.10.0`; `$id` updated to `https://openkycaml.org/schema/v1.10.0/kyc-aml-hybrid-extended.json`.
- All new fields are **strictly additive and backward-compatible** — no existing required fields changed; no existing patterns modified.

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

## [1.9.1] — April 2026

### Added

- **`taxStatus.crsTaxResidencies[]`** (`CrsTaxResidency` $def) — First-class OECD CRS per-jurisdiction residency array (v1.9.1). Each entry carries `jurisdiction` (ISO 3166-1 alpha-2), `tinValue`, `tinVerificationStatus` enum (`verified | unverified | relief-applied | not-required` — maps to CRS reason codes A/B/C), `selfCertificationDate` (ISO 8601), and `controllingPersonFlag` (boolean — for Passive NFE controlling persons per OECD CRS Section VIII.D.6). Supersedes flat `tinIdentifiers[]` for AEOI CRS flows; maps directly to OECD CRS XML Schema v2.0 `AccountHolder/ControllingPerson` TIN elements.

- **`taxStatus.fatcaStatus`** (`FatcaStatus` $def) — First-class US FATCA Chapter 4 block (v1.9.1). Fields: `giin` (19-char IRS GIIN, regex-validated `^[0-9A-Z]{6}\.[0-9A-Z]{5}\.[0-9A-Z]{2}\.[0-9A-Z]{3}$`), `chapter4Classification` (8-value enum: `participatingFFI | registeredDeemedCompliantFFI | certifiedDeemedCompliantFFI | sponsoredDirectReportingNFFE | exemptBeneficialOwner | nonFinancialNonReportingEntity | nonParticipatingFFI | other`), `usTinRequired`, `temporaryReliefApplied` (IRS Notice 2024-78, 2025–2027 deferral for Model 1 IGA pre-existing accounts), `ffiListVerificationTimestamp`, `withholdingAgentReference`. Feeds directly into `predictiveAML` risk scoring.

- **1 new example** — `examples/tax/tax-fatca-crs.json`: Irish FFI (registeredDeemedCompliantFFI) with GIIN, dual-jurisdiction CRS residencies (IE + US), and FATCA status block.

- **`docs/mappings/fatca-crs.md`** + **`fatca-crs.yaml`** — New dedicated mapping document covering: §1 Introduction (FATCA/CRS interoperability, tinIdentifiers[] relationship), §2 OECD CRS crsTaxResidencies[] field mapping + TIN reason-code table + Passive NFE controlling person, §3 FATCA fatcaStatus field mapping + GIIN structure + Chapter 4 classification table + IRS Notice 2024-78 relief, §4 PredictiveAML synergy, §5 compliance and backward-compatibility notes.

- **`schema/versions/v1.9.1.json`** — versioned snapshot of canonical schema.

- **`api/openkycaml-v1.9.0.yaml`** — new OpenAPI 3.1.0 spec with `TinIdentifier`, `IndirectTaxRegistration`, `EconomicSubstance`, `PillarTwo`, `CrsTaxResidency`, `FatcaStatus`, and `TaxStatus` component schemas.

- **Validator business warnings** (Python + Node.js + Go):
  - `taxStatus.fatcaStatus.giin` fails IRS regex → GIIN format warning.
  - `taxStatus.fatcaStatus.chapter4Classification = "nonParticipatingFFI"` → 30% withholding EDD warning.
  - `taxStatus.fatcaStatus.ffiListVerificationTimestamp` > 35 days old → stale FFI List warning.

- **ER diagram** (`docs/diagrams/schema-er-diagram.md`) — added `TaxStatus`, `TinIdentifier`, `IndirectTaxRegistration`, `EconomicSubstance`, `PillarTwo`, `CrsTaxResidency`, `FatcaStatus` entities with relationships; footer updated to v1.9.1.

- **Compliance matrix §18** — Expanded from generic TIN rows to explicit FATCA/CRS first-class rows: GIIN, Chapter 4, controlling-person flag, TIN reason codes A/B/C, FATCA/CRS XML Schema v2.0 export, AMLR Art. 22.

### Changed

- `schema/kyc-aml-hybrid-extended.json` — version bumped from `1.9.0` to `1.9.1`; `$id` updated to `https://openkycaml.org/schema/v1.9.1/kyc-aml-hybrid-extended.json`; `TaxStatus.description` updated.
- `taxStatus` root property description updated to reference v1.9.1 additions.

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
