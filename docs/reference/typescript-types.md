# TypeScript Type Definitions

This document provides TypeScript type definitions for the OpenKYCAML v1.7.0 schema. These types mirror the JSON Schema `$defs` and can be used to build strongly-typed OpenKYCAML payloads in TypeScript / Node.js projects.

> **Installation tip:** Copy the types below into a `types/openkycaml.d.ts` file in your project, or use them alongside the JavaScript validator at [`tools/javascript/validator.js`](../../tools/javascript/validator.js).

---

## Table of Contents

1. [Root Document](#1-root-document)
2. [IVMS 101 Types](#2-ivms-101-types)
3. [Person Types](#3-person-types)
4. [KYC Profile Types](#4-kyc-profile-types)
5. [Verification Document Bundle Types (v1.5.0+)](#4b-verification-document-bundle-types-v150v160)
6. [Verifiable Credential Types](#5-verifiable-credential-types)
7. [GDPR Sensitivity Types](#6-gdpr-sensitivity-types)
8. [Validator API](#7-validator-api)
9. [Usage Examples](#8-usage-examples)

---

## 1. Root Document

```typescript
/**
 * Root OpenKYCAML document envelope (schema v1.7.0).
 * At least one of `ivms101` or `verifiableCredential` must be present.
 */
export interface OpenKYCAMLDocument {
  /** JSON Schema identifier */
  $schema?: string;
  /** OpenKYCAML schema version (e.g. "1.7.0") */
  version?: string;
  /** UUID v4 message identifier — unique per exchange */
  messageId: string;
  /** ISO 8601 UTC timestamp of message creation */
  messageDateTime: string;
  /** Message type descriptor */
  messageType?: string;
  /** IVMS 101 Travel Rule payload */
  ivms101?: IVMS101Payload;
  /** KYC/AML profile (top-level, outside VC) */
  kycProfile?: KYCProfile;
  /** W3C Verifiable Credential envelope */
  verifiableCredential?: VerifiableCredentialWrapper;
  /** Verification Document Bundle — typed identity document evidence (v1.5.0). */
  identityDocuments?: VerificationDocumentBundle;
  /** GDPR/AML sensitivity classification at document level (v1.3.0). */
  gdprSensitivityMetadata?: GdprSensitivityMetadata;
  /** Transaction monitoring metadata. */
  transactionMonitoring?: TransactionMonitoring;
  /** Trusted issuer registry entries. */
  trustedIssuers?: TrustedIssuer[];
}
```

---

## 2. IVMS 101 Types

```typescript
/** Root IVMS 101 Travel Rule message payload. */
export interface IVMS101Payload {
  originator: Originator;
  beneficiary: Beneficiary;
  originatingVASP: VASP;
  beneficiaryVASP: VASP;
  /** Ordered list of intermediate VASPs in multi-hop transfers */
  transferPath?: VASP[];
  payloadMetadata?: {
    transactionIdentifier?: string;
    timestamp?: string;
    /** Always "IVMS101.2023" */
    version?: string;
  };
  transferredAmount?: {
    /** Decimal string, e.g. "0.5" */
    amount: string;
    /** Asset code, e.g. "BTC", "ETH", "EUR" */
    assetType: string;
  };
}

/** IVMS 101 originator — sending party in a virtual asset transfer. */
export interface Originator {
  originatorPersons: PersonWrapper[];
  accountNumber?: string[];
}

/** IVMS 101 beneficiary — receiving party in a virtual asset transfer. */
export interface Beneficiary {
  beneficiaryPersons: PersonWrapper[];
  accountNumber?: string[];
}

/** A person wrapper — exactly one of naturalPerson or legalPerson must be present. */
export type PersonWrapper =
  | { naturalPerson: NaturalPerson; legalPerson?: never }
  | { legalPerson: LegalPerson; naturalPerson?: never };

/** Virtual Asset Service Provider identifier. */
export interface VASP {
  name?: string;
  vaspIdentifier?: string;
  /** ISO 17442 LEI (20 uppercase alphanumeric characters) */
  lei?: string;
}
```

---

## 3. Person Types

```typescript
/** IVMS 101 NaturalPerson entity. */
export interface NaturalPerson {
  name: NaturalPersonName;
  geographicAddress?: Address[];
  nationalIdentification?: NationalIdentification;
  customerIdentification?: string;
  dateAndPlaceOfBirth?: DateAndPlaceOfBirth;
  /** ISO 3166-1 alpha-2 country code */
  countryOfResidence?: string;
  /** ISO 3166-1 alpha-2 nationality */
  nationality?: string;
  /** RFC 5321 email address (v1.10.0) */
  emailAddress?: string;
  /** E.164 international phone number, e.g. '+447911123456' (v1.10.0) */
  phoneNumber?: string;
  /** E.164 mobile/cell number for mTAN/OTP delivery (v1.10.0) */
  mobileNumber?: string;
  /** Verified banking account details — IBAN, BIC, account type (v1.10.0) */
  bankingDetails?: BankingDetails[];
}

export interface NaturalPersonName {
  nameIdentifier: NaturalPersonNameIdentifier[];
  localNameIdentifier?: NaturalPersonNameIdentifier[];
  phoneticNameIdentifier?: NaturalPersonNameIdentifier[];
}

export interface NaturalPersonNameIdentifier {
  /** Family name / surname */
  primaryIdentifier: string;
  /** Given name(s) */
  secondaryIdentifier?: string;
  nameIdentifierType: 'ALIA' | 'BIRT' | 'MAID' | 'LEGL' | 'MISC';
}

/** IVMS 101 LegalPerson entity. */
export interface LegalPerson {
  name: LegalPersonName;
  geographicAddress?: Address[];
  customerNumber?: string;
  /** ISO 17442 LEI */
  lei?: string;
  nationalIdentification?: NationalIdentification;
  /** ISO 3166-1 alpha-2 country of registration */
  countryOfRegistration?: string;
  /** eIDAS 2.0 LPID block (optional — omit for pure IVMS 101 usage) */
  lpid?: LegalPersonIdentificationData;
  /** RFC 5321 business email address (v1.10.0) */
  emailAddress?: string;
  /** E.164 international business phone number (v1.10.0) */
  phoneNumber?: string;
  /** E.164 mobile contact for authorised representative (v1.10.0) */
  mobileNumber?: string;
  /** Verified banking account details — IBAN, BIC, account type (v1.10.0) */
  bankingDetails?: BankingDetails[];
}

export interface LegalPersonName {
  nameIdentifier: LegalPersonNameIdentifier[];
  localNameIdentifier?: LegalPersonNameIdentifier[];
  phoneticNameIdentifier?: LegalPersonNameIdentifier[];
}

export interface LegalPersonNameIdentifier {
  legalPersonName: string;
  legalPersonNameIdentifierType: 'LEGL' | 'SHRT' | 'TRAD';
}

/**
 * Validated banking account details — IBAN, BIC, currency, account type (v1.10.0).
 * Wired as bankingDetails[] on NaturalPerson and LegalPerson.
 *
 * IBAN pattern:  /^[A-Z]{2}[0-9]{2}[A-Z0-9]{4,30}$/ (ISO 13616 structural)
 * BIC pattern:   /^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$/ (ISO 9362, 8/11-char)
 */
export interface BankingDetails {
  /** ISO 13616 IBAN — structural pattern (modulo-97 checksum is a runtime concern) */
  iban?: string;
  /** ISO 9362 BIC/SWIFT code — 8-char or 11-char */
  bic?: string;
  /** Full legal name of the financial institution */
  bankName?: string;
  /** ISO 4217 three-letter currency code, e.g. 'EUR', 'GBP' */
  accountCurrency?: string;
  /** Account classification */
  accountType?: 'CURRENT' | 'SAVINGS' | 'CORRESPONDENT' | 'CRYPTO_FIAT_GATEWAY' | 'OTHER';
  /** ISO 3166-1 alpha-2 country of the holding bank */
  bankingCountry?: string;
}


export interface Address {
  country: string;
  addressType?: 'HOME' | 'BIZZ' | 'GEOG';
  department?: string;
  subDepartment?: string;
  streetName?: string;
  buildingNumber?: string;
  buildingName?: string;
  floor?: string;
  postBox?: string;
  room?: string;
  postCode?: string;
  townName?: string;
  townLocationName?: string;
  districtName?: string;
  countrySubDivision?: string;
  /** Unstructured address lines (up to 7) */
  addressLine?: string[];
}

/** National identification document (IVMS 101 §3.6). */
export interface NationalIdentification {
  nationalIdentifier: string;
  nationalIdentifierType:
    | 'ARNU' | 'CCPT' | 'RAID' | 'DRLC' | 'FIIN'
    | 'TXID' | 'SOCS' | 'IDCD' | 'LEIX' | 'MISC';
  countryOfIssue?: string;
  registrationAuthority?: string;
}

/** Birth information for a natural person (IVMS 101 §3.3). */
export interface DateAndPlaceOfBirth {
  /** ISO 8601 date, e.g. "1985-07-14" */
  dateOfBirth: string;
  placeOfBirth: string;
}

/** eIDAS 2.0 Legal Person Identification Data (LPID). */
export interface LegalPersonIdentificationData {
  currentLegalName: string;
  uniqueIdentifier: string;
  currentAddress?: Address;
  vatRegistrationNumber?: string;
  taxReferenceNumber?: string;
  europeanUniqueIdentifier?: string;
  /** ISO 17442 LEI */
  lei?: string;
  eoriNumber?: string;
  mandates?: Mandate[];
}

export interface Mandate {
  naturalPerson: NaturalPerson;
  roleOrPower: string;
  validFrom?: string;
  validUntil?: string;
}
```

---

## 4. KYC Profile Types

```typescript
/** KYC/AML profile — risk rating, screening results, UBO chain, monitoring. */
export interface KYCProfile {
  customerRiskRating: 'LOW' | 'MEDIUM' | 'HIGH' | 'VERY_HIGH';
  /** Narrative detail explaining the risk rating. */
  riskRatingDetail?: string;
  /** Customer classification segment (e.g. RETAIL, PROFESSIONAL, INSTITUTIONAL). */
  customerClassification?: string;
  dueDiligenceType: 'SDD' | 'CDD' | 'EDD';
  pepStatus?: PEPStatus;
  sanctionsScreening?: SanctionsScreening;
  adverseMedia?: AdverseMedia;
  sourceOfFundsWealth?: SourceOfFundsWealth;
  /** Narrative detail supporting the source-of-funds/wealth declaration. */
  sourceOfFundsWealthDetail?: string;
  /** Beneficial ownership chain (UBO records). */
  beneficialOwnership?: BeneficialOwner[];
  monitoringInfo?: MonitoringInfo;
  auditMetadata?: AuditMetadata;
  gdprSensitivityMetadata?: GdprSensitivityMetadata;
  onboardingChannel?: string;
  kycCompletionDate?: string;
  /** Consent record for GDPR Art. 6/9 lawful-basis tracking. */
  consentRecord?: ConsentRecord;
  /** AMLA RTS CDD tier requirements (added v1.2.0). */
  dueDiligenceRequirements?: DueDiligenceRequirements;
  /** Third-party CDD reliance record (added v1.2.0). */
  thirdPartyCDDReliance?: ThirdPartyCDDReliance;
  /** Whether the customer is eligible to transact (ERC-3643 / XRPL compliance gate). */
  isEligible?: boolean;
  /** ISO 8601 timestamp of the last eligibility confirmation. */
  eligibilityLastConfirmed?: string;
  /** Blockchain wallet addresses associated with this customer (v1.3.0+). */
  blockchainAccountIds?: BlockchainAccountId[];
  jurisdictionOfService?: string;
}

/** GDPR consent record (Art. 6 / Art. 9 lawful basis). */
export interface ConsentRecord {
  consentGiven: boolean;
  consentDate?: string;
  withdrawalPossible?: boolean;
  consentPurpose?: string;
}

/** AMLA RTS CDD tier requirements (v1.2.0). */
export interface DueDiligenceRequirements {
  requiresEDD?: boolean;
  eddTriggerReason?: string;
  sddEligible?: boolean;
  sddExpiryDate?: string;
}

/** Third-party CDD reliance record (v1.2.0). */
export interface ThirdPartyCDDReliance {
  relyingOnThirdParty: boolean;
  thirdPartyName?: string;
  thirdPartyLEI?: string;
  relianceDate?: string;
  cddStandardApplied?: string;
}

/**
 * Blockchain wallet address entry (v1.3.0–v1.7.0).
 * Supports Ethereum (ONCHAINID/ERC-3643), XRPL (XLS-70/80/81/96/77),
 * and Bitcoin/Lightning service-layer fields.
 */
export interface BlockchainAccountId {
  /** Blockchain address (Ethereum hex, XRPL r-address, Bitcoin bech32, etc.). */
  address: string;
  /** Network identifier — e.g. "ethereum", "xrpl", "bitcoin". */
  network: string;
  /** ERC-734/735 ONCHAINID smart contract address (Ethereum). */
  onchainIDAddress?: string;
  /** ISO 8601 timestamp when this wallet was registered with the VASP. */
  registeredAt?: string;
  /** Whether this wallet/trustline is currently frozen. */
  isFrozen?: boolean;
  /** Amount of tokens frozen (string to avoid precision loss). */
  frozenTokenAmount?: string;
  // ── XRPL-specific fields ─────────────────────────────────────────────────
  /** XLS-70 CredentialType hex string (2–128 chars) anchoring a W3C VC on XRPL. */
  xrplCredentialType?: string;
  /** XLS-33d MPTokenIssuanceID — 48-char Hash192 hex identifying the MPT issuance. */
  mptIssuanceId?: string;
  /**
   * XLS-80 Permissioned Domain ID — 64-char Hash256 hex.
   * Links this wallet to a Permissioned Domain gate on XRPL.
   */
  xrplPermissionedDomainId?: string;
  /**
   * XLS-80 authorised CredentialType hex strings accepted within this domain.
   * Cross-references XLS-70 credential types.
   */
  xrplAuthorizedCredentialTypes?: string[];
  /** XLS-96 Confidential Transfer configuration for this MPT issuance. */
  xrplConfidentialTransfer?: XrplConfidentialTransfer;
  /**
   * XLS-33d MPTIssuance flags bitmask.
   * Common flags: lsfMPTCanLock (0x0002), lsfMPTRequireAuth (0x0004),
   * lsfMPTCanClawback (0x0008), lsfMPTCanTransfer (0x0010), lsfMPTCanTrade (0x0020).
   */
  mptFlags?: number;
  /** XLS-33d MPTIssuance URI or hex metadata blob (compliance rules in token). */
  mptMetadata?: string;
  /** XLS-33d transfer fee in millionths of the token (0–50000; e.g. 1000 = 0.1%). */
  mptTransferFee?: number;
  /**
   * XLS-77 freeze granularity — extends the boolean `isFrozen` field.
   * INDIVIDUAL_FREEZE: single trustline frozen.
   * GLOBAL_FREEZE: issuer-level global freeze (no transfers).
   * DEEP_FREEZE: XLS-77 deep freeze — no inbound or outbound transfers.
   */
  xrplFreezeType?: 'INDIVIDUAL_FREEZE' | 'GLOBAL_FREEZE' | 'DEEP_FREEZE';
  /**
   * Whether the issuer has the Clawback amendment enabled for this trustline/MPT.
   * XRPL protocol-level equivalent of ERC-3643 forcedTransfer().
   */
  xrplClawbackEnabled?: boolean;
  // ── Bitcoin / Lightning fields ────────────────────────────────────────────
  /**
   * Lightning Network node public key — 66-char hex compressed secp256k1 pubkey.
   * Used for LNURL-auth identity binding.
   */
  lightningNodePubkey?: string;
  /**
   * Name or DID of the Lightning Service Provider delivering the compliance wrapper.
   * Examples: "Lightspark", "Voltage", "BitGo".
   */
  lightningServiceProvider?: string;
  /**
   * Bitcoin script type — used for chain analysis context.
   * P2PKH: legacy, P2WPKH: native SegWit, P2TR: Taproot.
   */
  bitcoinScriptType?: 'P2PKH' | 'P2WPKH' | 'P2TR';
}

/** XLS-96 Confidential Transfer configuration (EC-ElGamal + ZKP). */
export interface XrplConfidentialTransfer {
  /** Whether this MPT issuance uses XLS-96 confidential transfers. */
  enabled: boolean;
  /**
   * Encryption scheme identifier.
   * Currently: "EC_ELGAMAL". Additional schemes may be added in future XLS revisions.
   */
  encryptionScheme?: 'EC_ELGAMAL';
  /** EC public key of the designated auditor (hex or base58). */
  auditorPublicKey?: string;
  /** Regulator's selective disclosure key — optional; only for regulated issuances. */
  regulatorPublicKey?: string;
}

/** Politically Exposed Person screening result. */
export interface PEPStatus {
  isPEP: boolean;
  pepCategory?:
    | 'DOMESTIC_PEP' | 'FOREIGN_PEP' | 'INTERNATIONAL_ORGANISATION'
    | 'FAMILY_MEMBER_OF_PEP' | 'CLOSE_ASSOCIATE_OF_PEP'
    | 'FORMER_PEP' | 'NOT_PEP';
  pepRole?: string;
  screeningDate?: string;
  screeningProvider?: string;
}

/** Sanctions list screening result. */
export interface SanctionsScreening {
  screeningStatus: 'CLEAR' | 'HIT' | 'POTENTIAL_MATCH' | 'FALSE_POSITIVE' | 'PENDING' | 'ESCALATED';
  screeningDate: string;
  screeningProvider?: string;
  listsChecked?: string[];
  matchDetails?: SanctionsMatchDetail[];
}

export interface SanctionsMatchDetail {
  listName: string;
  matchScore: number;
  matchedName?: string;
  disposition?: 'CONFIRMED_HIT' | 'FALSE_POSITIVE' | 'UNDER_REVIEW';
  reviewedBy?: string;
  reviewDate?: string;
}

/** Adverse media / negative news screening result. */
export interface AdverseMedia {
  hasHits?: boolean;
  screeningStatus: 'CLEAR' | 'ADVERSE_FOUND' | 'UNDER_REVIEW' | 'FALSE_POSITIVE' | 'PENDING';
  screeningDate: string;
  screeningProvider?: string;
  categories?: AdverseMediaCategory[];
  summary?: string;
  articles?: AdverseMediaArticle[];
}

export type AdverseMediaCategory =
  | 'FINANCIAL_CRIME' | 'FRAUD' | 'CORRUPTION' | 'MONEY_LAUNDERING'
  | 'TERRORISM_FINANCING' | 'DRUG_TRAFFICKING' | 'HUMAN_TRAFFICKING'
  | 'CYBERCRIME' | 'TAX_EVASION' | 'OTHER';

export interface AdverseMediaArticle {
  url?: string;
  headline?: string;
  publicationDate?: string;
  source?: string;
}

/** Declared and verified source of funds and source of wealth. */
export interface SourceOfFundsWealth {
  sourceOfFunds?: SourceOfFundsCode[];
  sourceOfWealthNarrative?: string;
  verificationStatus?: 'DECLARED_ONLY' | 'PARTIALLY_VERIFIED' | 'FULLY_VERIFIED' | 'INCONSISTENT';
  supportingDocuments?: SupportingDocument[];
}

export type SourceOfFundsCode =
  | 'EMPLOYMENT_INCOME' | 'BUSINESS_INCOME' | 'INVESTMENT_RETURNS'
  | 'INHERITANCE' | 'GIFT' | 'SALE_OF_PROPERTY' | 'SALE_OF_ASSETS'
  | 'LOAN' | 'PENSION' | 'RENTAL_INCOME' | 'CRYPTOCURRENCY_GAINS' | 'OTHER';

export interface SupportingDocument {
  documentType:
    | 'TAX_RETURN' | 'BANK_STATEMENT' | 'PAYSLIP' | 'AUDITED_ACCOUNTS'
    | 'COMPANY_ACCOUNTS' | 'INHERITANCE_DOCUMENTS' | 'SALE_AGREEMENT' | 'OTHER';
  documentReference?: string;
  verifiedDate?: string;
}

/** Ultimate Beneficial Owner (UBO) record. */
export interface BeneficialOwner {
  person?:
    | { naturalPerson: NaturalPerson; legalPerson?: never }
    | { legalPerson: LegalPerson; naturalPerson?: never };
  ownershipPercentage: number;
  ownershipType?: 'DIRECT' | 'INDIRECT' | 'BOTH';
  controlMechanism?: 'SHAREHOLDING' | 'VOTING_RIGHTS' | 'CONTRACTUAL' | 'DE_FACTO_CONTROL' | 'OTHER';
  verificationDate?: string;
  isPEP?: boolean;
  ownershipChainDepth?: number;
  intermediateEntities?: IntermediateEntity[];
}

export interface IntermediateEntity {
  legalPerson: LegalPerson;
  ownershipPercentage?: number;
  ownershipType?: 'DIRECT' | 'INDIRECT';
  controlMechanism?: 'SHAREHOLDING' | 'VOTING_RIGHTS' | 'CONTRACTUAL' | 'DE_FACTO_CONTROL' | 'OTHER';
  /** ISO 3166-1 alpha-2 country of incorporation */
  jurisdiction?: string;
}

/** Ongoing AML monitoring metadata. */
export interface MonitoringInfo {
  monitoringLevel?: 'STANDARD' | 'ENHANCED' | 'SIMPLIFIED' | 'CONTINUOUS';
  monitoringStatus?: 'ACTIVE' | 'SUSPENDED' | 'TERMINATED';
  eddRequired?: boolean;
  lastReviewDate?: string;
  nextReviewDate?: string;
  reviewFrequency?: 'MONTHLY' | 'QUARTERLY' | 'SEMI_ANNUAL' | 'ANNUAL' | 'BIENNIAL' | 'RISK_TRIGGERED';
  alerts?: MonitoringAlert[];
}

export interface MonitoringAlert {
  alertId: string;
  alertDate: string;
  alertType:
    | 'UNUSUAL_TRANSACTION' | 'VELOCITY_BREACH' | 'PATTERN_CHANGE'
    | 'SANCTIONS_HIT' | 'PEP_CHANGE' | 'ADVERSE_MEDIA' | 'SAR_TRIGGER' | 'OTHER';
  alertStatus: 'OPEN' | 'UNDER_REVIEW' | 'CLOSED_NO_ACTION' | 'SAR_FILED' | 'ESCALATED';
  description?: string;
  assignedTo?: string;
}

/** Audit trail and provenance metadata. */
export interface AuditMetadata {
  recordId?: string;
  recordCreatedAt: string;
  recordUpdatedAt?: string;
  recordVersion: number;
  createdBy?: string;
  dataSourceSystem?: string;
  dataProvider?: string;
  dataRetentionDate?: string;
}

/** Transaction monitoring metadata (top-level). */
export interface TransactionMonitoring {
  transactionId?: string;
  monitoringStatus?: 'PASS' | 'REVIEW' | 'ESCALATED' | 'BLOCKED';
  riskScore?: number;
  riskIndicators?: string[];
  lastChecked?: string;
}

/** Trusted issuer registry entry. */
export interface TrustedIssuer {
  issuerDID: string;
  issuerName?: string;
  credentialTypes?: string[];
  trustedSince?: string;
}
```

---

## 4b. Verification Document Bundle Types (v1.5.0–v1.6.0)

```typescript
/** Root container for identity verification documents (v1.5.0). */
export interface VerificationDocumentBundle {
  naturalPersonDocuments?: NaturalPersonDocument[];
  legalEntityDocuments?: LegalEntityDocument[];
}

/**
 * Individual identity document (passport, driving licence, national ID,
 * PID Verifiable Credential, etc.).
 * Added v1.5.0. Document ID URN pattern added v1.6.0.
 */
export interface NaturalPersonDocument {
  /**
   * URN document ID following the pattern:
   * urn:openkycaml:doc:{countryCode}:{documentType}:{issuingAuthority}:{YYYY-MM}
   * Example: urn:openkycaml:doc:gb:passport:hm-passport-office:2024-03
   */
  documentId?: string;
  documentType:
    | 'PASSPORT' | 'NATIONAL_ID' | 'DRIVING_LICENCE' | 'RESIDENCE_PERMIT'
    | 'UTILITY_BILL' | 'BANK_STATEMENT' | 'PID_CREDENTIAL' | 'EUDI_PID'
    | 'OTHER';
  documentNumber?: string;
  issuingCountry?: string;
  issuingAuthority?: string;
  issueDate?: string;
  expiryDate?: string;
  /** Whether document was verified against authoritative source. */
  verified?: boolean;
  verificationMethod?: string;
  /** Fields extracted from the document and their match status. */
  extractedAttributes?: ExtractedAttribute[];
  /** Reference to the original document image/file (URI or CID). */
  documentReference?: string;
}

/**
 * Corporate / legal entity verification document (certificate of incorporation,
 * LEI registration, vLEI VC, GLEIF BRIS filing, etc.).
 */
export interface LegalEntityDocument {
  /** URN document ID (same pattern as NaturalPersonDocument.documentId). */
  documentId?: string;
  documentType:
    | 'CERTIFICATE_OF_INCORPORATION' | 'ARTICLES_OF_ASSOCIATION'
    | 'LEI_REGISTRATION' | 'VLEI_CREDENTIAL' | 'PROOF_OF_ADDRESS'
    | 'AUDITED_ACCOUNTS' | 'REGISTER_EXTRACT' | 'OTHER';
  documentNumber?: string;
  issuingCountry?: string;
  issuingAuthority?: string;
  issueDate?: string;
  expiryDate?: string;
  verified?: boolean;
  verificationMethod?: string;
  extractedAttributes?: ExtractedAttribute[];
  documentReference?: string;
  /** Structured GLEIF RAL reference (v1.5.0). */
  registrationAuthorityDetail?: RegistrationAuthorityDetail;
  gleifRegistrationAuthority?: string;
  elfCodeVerified?: boolean;
  vLEICredentialType?: 'QVI' | 'OOR' | 'ECR';
}

/** Field extracted from a verification document with match status. */
export interface ExtractedAttribute {
  fieldName: string;
  value: string;
  /** Whether the extracted value matches the corresponding claim in the KYC record. */
  matchesRecord?: boolean;
  confidence?: number;
}

/** Structured GLEIF Registration Authority List (RAL) reference (v1.5.0). */
export interface RegistrationAuthorityDetail {
  /** GLEIF RAL code (e.g. "RA000585" for Companies House UK). */
  ralCode?: string;
  authorityName?: string;
  jurisdiction?: string;
  registrationUrl?: string;
}

```typescript
/** W3C Verifiable Credential envelope (VC Data Model v2 / eIDAS 2.0 ARF). */
export interface VerifiableCredentialWrapper {
  '@context': string[];
  id?: string;
  type: string[];
  issuer: string | { id: string; name?: string };
  validFrom: string;
  validUntil?: string;
  credentialSubject: CredentialSubject;
  credentialStatus?: CredentialStatus;
  credentialSchema?: CredentialSchema;
  evidence?: CredentialEvidence[];
  proof?: VerifiableCredentialProof;
  selectiveDisclosure?: SelectiveDisclosure;
}

export interface CredentialSubject {
  id?: string;
  ivms101?: IVMS101Payload;
  kycProfile?: KYCProfile;
  lpid?: LegalPersonIdentificationData;
}

export interface CredentialStatus {
  id: string;
  type: 'StatusList2021Entry' | 'RevocationList2020Status' | 'AnonCredsCredentialStatusList2023';
  [key: string]: unknown;
}

export interface CredentialSchema {
  id: string;
  type: 'JsonSchemaValidator2018' | 'AnonCredsDefinition' | 'JsonSchema';
  credDefId?: string;
}

/** W3C VC evidence block — records the source credential used during KYC. */
export interface CredentialEvidence {
  id: string;
  type: string[];
  verifier?: string;
  credentialIssuer?: string;
  evidenceDocument?: string;
  subjectPresence?: 'Physical' | 'Digital';
  documentPresence?: 'Physical' | 'Digital';
  presentationMethod?: string;
  presentationDate?: string;
}

/** Cryptographic proof (Ed25519Signature2020, JsonWebSignature2020, etc.). */
export interface VerifiableCredentialProof {
  type: string;
  created: string;
  verificationMethod: string;
  proofPurpose:
    | 'assertionMethod' | 'authentication' | 'keyAgreement'
    | 'capabilityInvocation' | 'capabilityDelegation';
  proofValue?: string;
  jws?: string;
}

/** SD-JWT VC selective disclosure metadata. */
export interface SelectiveDisclosure {
  _sd_alg?: 'sha-256' | 'sha-384';
  disclosableClaimPaths?: string[];
  requiredClaimPaths?: string[];
  decodedDisclosures?: DecodedDisclosure[];
  sdJwtNote?: string;
}

export interface DecodedDisclosure {
  salt: string;
  claimName: string;
  claimValue?: unknown;
}
```

---

## 6. GDPR Sensitivity Types

```typescript
/** GDPR/AML sensitivity classification for tipping-off protection (AMLR Art. 73). */
export interface GdprSensitivityMetadata {
  classification:
    | 'standard' | 'sensitive_personal' | 'criminal_offence'
    | 'sar_restricted' | 'internal_suspicion' | 'confidential_aml';
  /** RFC 6901 JSON Pointer paths to restricted fields */
  restrictedFields?: string[];
  /**
   * Must be `true` when classification is `sar_restricted` or `internal_suspicion`.
   * Wallets and relying parties MUST NOT reveal the existence of a SAR to the data subject.
   */
  tippingOffProtected?: boolean;
  legalBasis?:
    | 'GDPR-Art6-1c' | 'GDPR-Art6-1e' | 'GDPR-Art9-2g' | 'GDPR-Art10'
    | 'AMLR-Art55' | 'AMLR-Art73' | 'national_AML_law';
  /** ISO 8601 duration, e.g. "P5Y" */
  retentionPeriod?: string;
  consentRecord?: GdprConsentRecord;
  disclosurePolicy?: DisclosurePolicy;
  /** Opaque DPO record or SAR case reference — MUST NOT contain SAR narrative */
  auditReference?: string;
}

export interface GdprConsentRecord {
  consentGiven: boolean;
  consentDate?: string;
  withdrawalPossible?: boolean;
}

export interface DisclosurePolicy {
  allowedRecipients?: string[];
  prohibitedRecipients?: string[];
  requiresExplicitConsent?: boolean;
}
```

---

## 7. Validator API

The JavaScript validator at [`tools/javascript/validator.js`](../../tools/javascript/validator.js) exposes the following TypeScript-compatible interface:

```typescript
/** Field-level validation error. */
export interface FieldError {
  /** JSON Pointer to the failing field (e.g. "/ivms101/originator") */
  instancePath: string;
  /** Human-readable error description */
  message: string;
  /** JSON Pointer into the schema */
  schemaPath: string;
}

/** Result returned by OpenKYCAMLValidator.validate(). */
export interface ValidationResult {
  /** true if the payload passes JSON Schema validation */
  isValid: boolean;
  /** Array of field-level errors (empty when isValid is true) */
  errors: FieldError[];
  /** Advisory warnings — schema-valid but non-compliant patterns */
  warnings: string[];
  /** The `version` field extracted from the payload */
  payloadVersion: string | null;
}

declare class OpenKYCAMLValidator {
  constructor(schemaPath?: string);
  validate(payload: OpenKYCAMLDocument): ValidationResult;
  validateFile(filePath: string): ValidationResult;
}

export { OpenKYCAMLValidator };
```

---

## 8. Usage Examples

### Validate a payload

```typescript
import { OpenKYCAMLValidator, OpenKYCAMLDocument } from './types/openkycaml';

const validator = new OpenKYCAMLValidator();

const payload: OpenKYCAMLDocument = {
  messageId: '550e8400-e29b-41d4-a716-446655440000',
  messageDateTime: '2025-09-10T10:57:00Z',
  ivms101: {
    originator: {
      originatorPersons: [
        {
          naturalPerson: {
            name: {
              nameIdentifier: [
                {
                  primaryIdentifier: 'Müller',
                  secondaryIdentifier: 'Hans',
                  nameIdentifierType: 'LEGL',
                },
              ],
            },
            dateAndPlaceOfBirth: {
              dateOfBirth: '1985-07-14',
              placeOfBirth: 'Berlin',
            },
          },
        },
      ],
      accountNumber: ['0x71C7656EC7ab88b098defB751B7401B5f6d8976F'],
    },
    beneficiary: {
      beneficiaryPersons: [
        {
          naturalPerson: {
            name: {
              nameIdentifier: [
                { primaryIdentifier: 'Smith', nameIdentifierType: 'LEGL' },
              ],
            },
          },
        },
      ],
      accountNumber: ['0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045'],
    },
    originatingVASP: { name: 'Acme Crypto GmbH', lei: 'ACMECRYPTOGMB0000001' },
    beneficiaryVASP: { name: 'Beta Exchange Ltd', lei: 'BETAEXCHANGELTD00001' },
    transferredAmount: { amount: '0.5', assetType: 'ETH' },
  },
};

const result = validator.validate(payload);
console.log(result.isValid);   // true
console.log(result.warnings);  // advisory warnings
```

### Build a KYC profile with PEP status

```typescript
import { KYCProfile } from './types/openkycaml';

const profile: KYCProfile = {
  customerRiskRating: 'HIGH',
  dueDiligenceType: 'EDD',
  pepStatus: {
    isPEP: true,
    pepCategory: 'DOMESTIC_PEP',
    pepRole: 'Member of Parliament',
    screeningDate: '2025-09-01',
    screeningProvider: 'Refinitiv World-Check',
  },
  sanctionsScreening: {
    screeningStatus: 'CLEAR',
    screeningDate: '2025-09-01T09:00:00Z',
    listsChecked: ['OFAC_SDN', 'EU_CONSOLIDATED', 'UN_CONSOLIDATED'],
  },
  onboardingChannel: 'EUDI_WALLET',
  kycCompletionDate: '2025-09-10',
  auditMetadata: {
    recordCreatedAt: '2025-09-10T10:00:00Z',
    recordVersion: 1,
    dataSourceSystem: 'KYC-Platform-v3',
  },
};
```

### Mark a payload as SAR-restricted (tipping-off protection)

```typescript
import { GdprSensitivityMetadata } from './types/openkycaml';

const sensitivity: GdprSensitivityMetadata = {
  classification: 'sar_restricted',
  tippingOffProtected: true,   // required when classification is sar_restricted
  legalBasis: 'AMLR-Art73',
  retentionPeriod: 'P5Y',
  disclosurePolicy: {
    allowedRecipients: ['fiu_only'],
    prohibitedRecipients: ['data_subject'],
  },
  auditReference: 'SAR-REF-2025-00142',   // opaque — no SAR content
};
```

---

*Type definitions derived from OpenKYCAML JSON Schema v1.7.0. Last updated: v1.7.0.*

---

## Tax Status Types (v1.9.0)

```typescript
/** ISO 3166-1 alpha-2 country code. */
type JurisdictionCode = string;

/** Type of tax identifier. */
type TinType = 'TIN' | 'VAT' | 'GST' | 'PST' | 'EIN' | 'functionalEquivalent' | 'other';

/** Verification status of a TIN entry. */
type TinVerificationStatus = 'verified' | 'unverified' | 'revoked' | 'suspended';

/** A single TIN or functional equivalent for one jurisdiction (OECD CRS/CARF, FATCA). */
interface TinIdentifier {
  jurisdiction: JurisdictionCode;
  tinType: TinType;
  tinValue: string;
  issuanceDate?: string;           // ISO 8601 date-time
  verificationStatus?: TinVerificationStatus;
  verificationSource?: string;     // e.g. 'OECD-TIN-list', 'VIES', 'IRS-TIN-Matching'
}

/** Type of indirect tax registration. */
type IndirectTaxType = 'VAT' | 'GST' | 'PST' | 'HST' | 'salesTax';

/** Registration status for an indirect tax. */
type IndirectTaxStatus = 'active' | 'suspended' | 'revoked' | 'exempt';

/** A VAT/GST/PST/HST/salesTax registration entry for one jurisdiction. */
interface IndirectTaxRegistration {
  taxType?: IndirectTaxType;
  jurisdiction?: JurisdictionCode;
  registrationNumber?: string;
  status?: IndirectTaxStatus;
  effectiveFrom?: string;          // ISO 8601 date
}

/** ESR status for an entity in an ESR-regime jurisdiction. */
type EsrStatus =
  | 'inScope-RelevantEntity'
  | 'exempt-TaxResidentElsewhere'
  | 'exempt-PureEquityHolding'
  | 'compliant'
  | 'nonCompliant';

/** Economic Substance Regulation (ESR) classification block. */
interface EconomicSubstance {
  jurisdiction?: JurisdictionCode;
  status?: EsrStatus;
  relevantActivities?: string[];   // e.g. 'holdingCompany', 'intellectualProperty'
  coreIncomeGeneratingActivitiesPerformed?: boolean;
  lastNotificationDate?: string;   // ISO 8601 date
  lastReportReference?: string;
}

/** GloBE constituent entity status. */
type ConstituentEntityStatus = 'inScope' | 'excluded' | 'QDMTT';

/** Safe harbour election type. */
type SafeHarbour = 'SimplifiedETR' | 'SubstanceBased' | 'DeMinimis' | 'none';

/** Effective tax rate entry for one jurisdiction. */
interface EtrJurisdiction {
  jurisdiction: JurisdictionCode;
  etr: number;   // decimal 0–1; e.g. 0.15 = 15%
}

/** OECD Pillar 2 GloBE (BEPS 2.0) classification block. */
interface PillarTwo {
  inScopeMNE?: boolean;
  consolidatedRevenueEUR?: number;
  constituentEntityStatus?: ConstituentEntityStatus;
  etrJurisdictions?: EtrJurisdiction[];
  safeHarbourApplied?: SafeHarbour;
  girFilingReference?: string;
  lastGIRDate?: string;            // ISO 8601 date-time
}

/** Root taxStatus block (v1.9.0). All sub-properties optional. */
interface TaxStatus {
  tinIdentifiers?: TinIdentifier[];
  indirectTaxRegistrations?: IndirectTaxRegistration[];
  economicSubstance?: EconomicSubstance;
  pillarTwo?: PillarTwo;
}
```

*Tax status types added in OpenKYCAML v1.9.0. Last updated: v1.9.0.*

---

## FATCA & CRS Types (v1.9.1)

```typescript
/** OECD CRS TIN verification / reason-code status. */
type CrsTinVerificationStatus = 'verified' | 'unverified' | 'relief-applied' | 'not-required';

/** Enhanced OECD CRS per-jurisdiction tax-residency entry. */
interface CrsTaxResidency {
  jurisdiction: JurisdictionCode;          // required
  tinValue?: string;
  tinVerificationStatus?: CrsTinVerificationStatus;
  selfCertificationDate?: string;          // ISO 8601 date-time
  controllingPersonFlag?: boolean;         // true for Passive NFE controlling persons
}

/** US FATCA Chapter 4 entity classification. */
type Chapter4Classification =
  | 'participatingFFI'
  | 'registeredDeemedCompliantFFI'
  | 'certifiedDeemedCompliantFFI'
  | 'sponsoredDirectReportingNFFE'
  | 'exemptBeneficialOwner'
  | 'nonFinancialNonReportingEntity'
  | 'nonParticipatingFFI'
  | 'other';

/**
 * US FATCA Chapter 4 status block.
 * GIIN pattern: /^[0-9A-Z]{6}\.[0-9A-Z]{5}\.[0-9A-Z]{2}\.[0-9A-Z]{3}$/
 */
interface FatcaStatus {
  giin?: string;                           // 19-char IRS GIIN, regex-validated
  chapter4Classification?: Chapter4Classification;
  usTinRequired?: boolean;
  temporaryReliefApplied?: boolean;        // IRS Notice 2024-78 relief (2025-2027)
  ffiListVerificationTimestamp?: string;   // ISO 8601; refresh every 35 days
  withholdingAgentReference?: string;
}

/** Updated TaxStatus interface (v1.9.1) — adds crsTaxResidencies[] and fatcaStatus. */
interface TaxStatus {
  tinIdentifiers?: TinIdentifier[];
  indirectTaxRegistrations?: IndirectTaxRegistration[];
  economicSubstance?: EconomicSubstance;
  pillarTwo?: PillarTwo;
  crsTaxResidencies?: CrsTaxResidency[];   // v1.9.1 — enhanced CRS per-residency data
  fatcaStatus?: FatcaStatus;               // v1.9.1 — FATCA Chapter 4 first-class block
}
```

*FATCA & CRS first-class types added in OpenKYCAML v1.9.1. Last updated: v1.9.1.*

---

## Contact and Banking Types (v1.10.0)

```typescript
/**
 * Validated banking account details per ISO 13616 (IBAN) and ISO 9362 (BIC).
 * Wired as bankingDetails[] on NaturalPerson and LegalPerson (v1.10.0).
 *
 * Validation:
 *   iban:            /^[A-Z]{2}[0-9]{2}[A-Z0-9]{4,30}$/  (ISO 13616 structural)
 *   bic:             /^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$/  (ISO 9362, 8/11-char)
 *   accountCurrency: /^[A-Z]{3}$/                            (ISO 4217)
 *   bankingCountry:  /^[A-Z]{2}$/                            (ISO 3166-1 alpha-2)
 */
export interface BankingDetails {
  iban?: string;
  bic?: string;
  bankName?: string;
  accountCurrency?: string;
  accountType?: 'CURRENT' | 'SAVINGS' | 'CORRESPONDENT' | 'CRYPTO_FIAT_GATEWAY' | 'OTHER';
  bankingCountry?: string;
}

/**
 * NaturalPerson and LegalPerson updated interfaces (v1.10.0 additions only).
 * Contact fields use format: "email" and E.164 pattern for guaranteed interoperability.
 */
interface PersonContactExtension {
  /** RFC 5321 email address (format: "email", maxLength: 254) */
  emailAddress?: string;
  /** E.164 phone number, e.g. '+447911123456' (pattern: /^\+[1-9]\d{1,14}$/) */
  phoneNumber?: string;
  /** E.164 mobile number for mTAN/OTP (pattern: /^\+[1-9]\d{1,14}$/) */
  mobileNumber?: string;
  /** Verified banking accounts — IBAN, BIC, account classification */
  bankingDetails?: BankingDetails[];
}
```

*Contact and banking types added in OpenKYCAML v1.10.0. Last updated: v1.10.0.*

---

## Cell Company Types (v1.11.0)

```typescript
/** PCC/ICC cell classification. */
export type CellCompanyType = 'NONE' | 'PCC_CORE' | 'PCC_CELL' | 'ICC_CORE' | 'ICC_CELL';

/**
 * Metadata for a LegalPerson that is a Core or Cell of a PCC or ICC (v1.11.0).
 * Present on LegalPerson when cellCompanyType != 'NONE'.
 */
export interface CellCompanyDetails {
  /** Required — cell structure classification */
  cellCompanyType: CellCompanyType;
  /** Unique cell number/designator within the parent structure (e.g. 'CELL-007') */
  cellIdentifier?: string;
  /** Human-readable cell name */
  cellName?: string;
  /**
   * ICC cell-specific registration number (pattern: /^[A-Z0-9]{1,35}$/).
   * Only for ICC cells (hasIndependentLegalPersonality: true).
   */
  cellRegistrationNumber?: string;
  /**
   * true = ICC cell (own legal entity, own registration, full contracting capacity).
   * false = PCC cell (transacts through PCC as single legal entity).
   */
  hasIndependentLegalPersonality?: boolean;
  /** true when this cell is a securities/ILS/cat bond issuer vehicle */
  isCellCompanyIssuer?: boolean;
  /** Required when isCellCompanyIssuer is true */
  issuancePurpose?: 'INSURANCE_LINKED_SECURITY' | 'CATASTROPHE_BOND' | 'STRUCTURED_NOTE' | 'DEBT_INSTRUMENT' | 'OTHER';
  /** URI link to prospectus / instrument document (format: "uri") */
  cellSpecificInstrumentReference?: string;
}

/**
 * Link to the parent PCC or ICC Core (v1.11.0).
 * Required when cellCompanyDetails.cellCompanyType is PCC_CELL or ICC_CELL.
 * Enables FATF beneficial-ownership tracing and AMLR Art. 26 entity verification.
 */
export interface ParentCellCompanyReference {
  /** LEI (20-char) or registration number of parent Core (pattern: /^[A-Z0-9]{1,35}$/) */
  legalEntityIdentifier: string;
  /** ISO 3166-1 alpha-2 incorporation jurisdiction of parent Core */
  jurisdiction: string;
  /** Registered legal name of parent Core */
  parentName?: string;
}

/**
 * LegalPerson cell company extensions (v1.11.0 additions only).
 * All optional — absent for ordinary non-cell companies.
 */
interface LegalPersonCellExtension {
  cellCompanyDetails?: CellCompanyDetails;
  parentCellCompanyReference?: ParentCellCompanyReference;
  /** Cell-level risk snapshot (overrides Core risk where cell risk differs) */
  cellRiskProfileOverride?: RiskSnapshot;
  /** Cell-level source of funds/wealth for AMLR Art. 29 / FATF Rec. 12 EDD */
  cellSourceOfFundsWealth?: SourceOfFundsWealth;
  /** Per-cell audit trail for AMLR Art. 56 5-year retention */
  cellAuditMetadata?: AuditMetadata;
}
```

*Cell company types added in OpenKYCAML v1.11.0. Last updated: v1.11.0.*

---

## Entity Governance, Natural Person Governance, and Review Lifecycle Types (v1.12.0)

```typescript
/** Gender enum for NaturalPerson — ISO/IEC 5218 aligned (v1.12.0).
 *  GDPR Art. 9 special-category data — collect only where lawfully required. */
export type NaturalPersonGender =
  | 'MALE'           // ISO/IEC 5218 code 1
  | 'FEMALE'         // ISO/IEC 5218 code 2
  | 'NON_BINARY'     // ISO/IEC 5218 code 9 (extended)
  | 'OTHER'          // Self-described gender outside binary categories
  | 'PREFER_NOT_TO_SAY';  // Data subject has declined to specify

/** ILO/ISCO-08 aligned broad occupation category (v1.12.0). */
export type OccupationCode =
  | 'EMPLOYED'       // Major groups 1–9 (salaried/waged employment)
  | 'SELF_EMPLOYED'  // Major groups 1–3, 5 (own-account workers)
  | 'BUSINESS_OWNER' // Major group 1 (managers and proprietors)
  | 'STUDENT'
  | 'RETIRED'
  | 'UNEMPLOYED'
  | 'PUBLIC_OFFICIAL' // Major group 1 sub-group 111 — may trigger PEP screening
  | 'OTHER';

/**
 * Structured occupation for a natural person (v1.12.0).
 * Aligned to eIDAS 2.0 PID occupation attribute and IVMS 101 extended CDD.
 * Complements — does not replace — kycProfile.customerClassification.occupationOrPurpose.
 */
export interface NaturalPersonOccupation {
  /** Broad ILO/ISCO-08-aligned occupation category */
  occupationCode?: OccupationCode;
  /** Free-text job title or occupation detail (maxLength: 200) */
  occupationDescription?: string;
}

/**
 * NaturalPerson v1.12.0 additions.
 * Both fields are optional and backward-compatible.
 */
interface NaturalPersonGovernanceExtension {
  /** ISO/IEC 5218 aligned gender — GDPR Art. 9 special-category data (v1.12.0) */
  gender?: NaturalPersonGender;
  /** Structured occupation — eIDAS PID / IVMS 101 alignment (v1.12.0) */
  occupation?: NaturalPersonOccupation;
}

/** Regulatory status of a legal entity (v1.12.0). */
export type RegulatoryStatus = 'REGULATED' | 'RECOGNISED' | 'UNREGULATED' | 'EXEMPT';

/** Single regulator entry in EntityGovernance.regulators[] (v1.12.0). */
export interface RegulatorEntry {
  /** e.g. 'Financial Conduct Authority', 'BaFin', 'CSSF' (maxLength: 200) */
  regulatorName?: string;
  /** ISO 3166-1 alpha-2 — pattern: /^[A-Z]{2}$/ */
  jurisdiction?: string;
  /** Licence or registration number (maxLength: 100) */
  licenceNumber?: string;
}

/** Listed-exchange status (v1.12.0). */
export interface ListedStatus {
  /** Whether the entity is listed on any exchange */
  isListed?: boolean;
  /** ISO 10383 MIC code (e.g. 'XLON', 'XNAS', 'XETR') — maxLength: 10 */
  marketIdentifier?: string;
  /** Whether the market is a regulated/recognised market under applicable law (MiFID II, FCA) */
  recognisedMarket?: boolean;
}

/**
 * Entity governance flags for LegalPerson (v1.12.0).
 * Exposed as optional LegalPerson.entityGovernance.
 * Supports AMLR Art. 22 (SDD), Art. 26 (group UBO), Art. 48 (third-party reliance),
 * FATF Rec. 10/12/17/24, Wolfsberg CBDDQ §3.
 */
export interface EntityGovernance {
  /** Regulatory licensing status of this entity */
  regulatoryStatus?: RegulatoryStatus;
  /** Array of regulators holding jurisdiction over this entity */
  regulators?: RegulatorEntry[];
  /** Stock exchange listing metadata */
  listedStatus?: ListedStatus;
  /**
   * Parent company reference for non-cell corporate groups.
   * Reuses ParentCellCompanyReference $def (legalEntityIdentifier, jurisdiction, parentName).
   * For PCC/ICC cells use LegalPerson.parentCellCompanyReference instead.
   */
  parentCompany?: ParentCellCompanyReference;
  /** Whether the immediate parent is regulated by a recognised regulator (AMLR Art. 48) */
  parentRegulated?: boolean;
  /** Whether the immediate parent is listed on a recognised market (AMLR Art. 22 SDD) */
  parentListed?: boolean;
  /** Whether this entity is a majority-owned (>50%) subsidiary (FATF Rec. 24, AMLR Art. 26) */
  majorityOwnedSubsidiary?: boolean;
  /** Whether the entity is owned or controlled by a state/government body (FATF PEP Guidance) */
  stateOwned?: boolean;
  /** Percentage of entity owned directly or indirectly by a government (0–100) */
  governmentOwnershipPercentage?: number;
}

/**
 * LegalPerson v1.12.0 addition.
 */
interface LegalPersonGovernanceExtension {
  /** Entity governance flags — regulatory status, listed status, ownership chain (v1.12.0) */
  entityGovernance?: EntityGovernance;
}

/** Review lifecycle state enum (v1.12.0). */
export type ReviewLifecycleState =
  | 'ONBOARDING'        // Initial customer acceptance / KYC onboarding
  | 'INITIAL_REVIEW'    // First full KYC review after onboarding
  | 'PERIODIC_REVIEW'   // Scheduled periodic CDD refresh
  | 'TRIGGERED_REVIEW'  // Event-triggered re-KYC (e.g. transaction alert, SAR)
  | 'OFFBOARDING'       // Customer exit / relationship termination in progress
  | 'TERMINATED';       // Relationship permanently terminated

/** Single historical state transition entry (v1.12.0). */
export interface ReviewLifecycleHistory {
  /** State that was exited */
  fromState?: ReviewLifecycleState;
  /** State that was entered */
  toState: ReviewLifecycleState;
  /** ISO 8601 timestamp of the state transition */
  transitionAt: string;
  /** Free-text reason or trigger description (maxLength: 500) */
  reason?: string;
  /** User or system actor that triggered the transition */
  actor?: string;
}

/**
 * KYC/AML review lifecycle state machine (v1.12.0).
 * Exposed as optional MonitoringInfo.reviewLifecycle.
 * Provides AMLR Art. 21 audit trail for the review lifecycle.
 */
export interface ReviewLifecycle {
  /** Current lifecycle state */
  currentState?: ReviewLifecycleState;
  /** Full ordered history of state transitions (append-only audit log) */
  stateHistory?: ReviewLifecycleHistory[];
}

/**
 * MonitoringInfo v1.12.0 addition.
 */
interface MonitoringInfoReviewExtension {
  /** KYC review lifecycle state machine and audit trail (v1.12.0) */
  reviewLifecycle?: ReviewLifecycle;
}
```

*Entity governance, natural person governance, and review lifecycle types added in OpenKYCAML v1.12.0. Last updated: v1.12.0.*
