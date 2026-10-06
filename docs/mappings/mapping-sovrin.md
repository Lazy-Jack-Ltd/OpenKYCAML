# OpenKYCAML ↔ Sovrin / Hyperledger Indy (AnonCreds) Mapping

This document maps every data point in the **Sovrin Network** and its underlying **Hyperledger Indy** ledger and **Hyperledger AnonCreds** credential model to the corresponding field in the OpenKYCAML schema. It also identifies the schema extensions made to v1.2.0 to achieve full coverage.

**Sovrin / Indy sources used:**
- [sovrin-foundation/sovrin](https://github.com/sovrin-foundation/sovrin) — Sovrin Network genesis transactions, DID Method Specification, Governance Framework
- [Sovrin DID Method Specification](https://github.com/sovrin-foundation/sovrin/blob/master/spec/did-method-spec-template.html) (`did:sov`)
- [hyperledger-indy/indy-node](https://github.com/hyperledger-indy/indy-node) — Full ledger transaction types (NYM, ATTRIB, SCHEMA, CLAIM_DEF, REVOC_REG_DEF, REVOC_REG_ENTRY, Rich Schema family)
- [Hyperledger AnonCreds Specification](https://hyperledger.github.io/anoncreds-spec/) — Credential issuance, presentation, and proof protocol

**Coverage legend:**
- ✅ Full coverage — field exists in OpenKYCAML schema
- 🔄 Conceptual mapping — equivalent concept captured differently (see notes)
- ⭐ Schema extended — field added or updated in OpenKYCAML v1.2.0 to close the gap
- ℹ️ Out of scope — ledger/network infrastructure, not part of an off-chain KYC credential

---

## 1. Architecture Overview

Sovrin is a **public permissioned distributed ledger** purpose-built for self-sovereign identity. The identity stack consists of three layers:

| Layer | Component | Purpose | OpenKYCAML Equivalent |
|---|---|---|---|
| **Identity (DID)** | NYM transaction | Creates and updates Decentralized Identifiers (DIDs) and their public keys | `verifiableCredential.credentialSubject.id` + `verifiableCredential.proof.verificationMethod` |
| **Identity Attributes** | ATTRIB transaction | Stores hashed off-ledger attributes (e.g. service endpoints, raw data) | `verifiableCredential.credentialSubject.*` + `kycProfile.*` |
| **Credential Schema** | SCHEMA transaction | Publishes credential attribute name lists to the ledger | `verifiableCredential.credentialSchema.id` |
| **Credential Definition** | CLAIM_DEF transaction | Publishes issuer's CL public key bound to a schema | `verifiableCredential.credentialSchema.credDefId` ⭐ |
| **Revocation** | REVOC_REG_DEF + REVOC_REG_ENTRY | Accumulator-based revocation registries (CL_ACCUM) | `verifiableCredential.credentialStatus` |
| **Credential** | AnonCreds VC | The signed, optionally privacy-preserving credential | `verifiableCredential` wrapper |
| **Presentation** | AnonCreds Proof | Zero-knowledge proof presentation of selected attributes and predicates | `verifiableCredential.selectiveDisclosure` |
| **Rich Schema** | JSON_LD_CONTEXT / RICH_SCHEMA / RICH_SCHEMA_MAPPING | JSON-LD-based credential schemas | `verifiableCredential.credentialSchema` (with URI pointing to ledger) |

OpenKYCAML uses the W3C Verifiable Credentials Data Model v2 as its credential envelope, which is interoperable with both the AnonCreds W3C binding (`AnonCredsProof2023`) and legacy AnonCreds.

---

## 2. DID / NYM Record (Identity Layer)

The NYM transaction is the primary identity record on the Sovrin ledger.

| Sovrin / Indy Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `dest` (DID) | base58 string (16–32 bytes) | The Decentralized Identifier being registered or updated | `verifiableCredential.credentialSubject.id` | In OpenKYCAML, the DID is expressed as a `did:sov:<base58>` or `did:indy:<namespace>:<base58>` URI. |
| `verkey` | base58 string (16 or 32 bytes, optionally `~`-prefixed for abbreviated form) | Ed25519 verification key (abbreviated = 16 bytes, full = 32 bytes) | `verifiableCredential.proof.verificationMethod` | The DID URL reference `did:sov:<DID>#key-1` resolves to this public key. |
| `role` | enum integer | Network role: `TRUSTEE` (0), `STEWARD` (2), `ENDORSER` (101), `NETWORK_MONITOR` (201), `USER` (null) | `verifiableCredential.issuer` | The issuer DID's role on the Sovrin ledger determines their authority to issue credentials. Role is not stored in the KYC credential but is enforced by the Sovrin network. |
| `alias` | string (optional) | Human-readable alias for the DID | ℹ️ Not stored in KYC credential | Network-level metadata. |
| `diddocContent` | JSON-LD (≤ 10 KiB) | Full DID Document JSON content stored on ledger (v2+ NYMs) | `verifiableCredential.credentialSubject.id` (resolves to DID Document) | DID resolution resolves the full DID Document including keys and services. |
| `version` | integer (0, 1, 2) | NYM binding validation: 0=none, 1=did:sov (first 16 bytes of verkey), 2=did:indy (SHA256-derived, self-certifying) | ℹ️ DID method metadata | Determines whether the DID is `did:sov` (v1) or `did:indy` (v2, self-certifying). |

### 2.1 DID Document Fields

The DID Document is resolved from the NYM record and any ATTRIB records. OpenKYCAML uses the resolved DID Document implicitly through the `did:sov` or `did:indy` DID in the VC.

| DID Document Field | Description | OpenKYCAML Field | Notes |
|---|---|---|---|
| `id` | DID URI (`did:sov:HR6vs6GEZ8rHaVgjg2WodM`) | `verifiableCredential.credentialSubject.id` | DID of the credential subject; `verifiableCredential.issuer` for the issuing entity. |
| `verificationMethod[].id` | DID URL key reference (`did:sov:...#key-1`) | `verifiableCredential.proof.verificationMethod` | JWS / DataIntegrityProof `verificationMethod` references this DID URL. |
| `verificationMethod[].type` | Key type (`Ed25519VerificationKey2018`, `X25519KeyAgreementKey2019`) | `verifiableCredential.proof.type` | `CLSignature2019` or `AnonCredsProof2023` are the AnonCreds proof types. |
| `verificationMethod[].publicKeyBase58` | Base58-encoded Ed25519 public key | `verifiableCredential.proof.verificationMethod` (resolved) | Proof verification uses this key. |
| `authentication[]` | Authentication key DID URL references | ℹ️ DID Document, not in KYC credential | Used for DIDComm and agent-to-agent communication. |
| `keyAgreement[]` | X25519 key agreement references | ℹ️ DID Document, not in KYC credential | Used for encrypted DIDComm message encryption. |
| `service[].id` | Service identifier | ℹ️ Agent endpoint, not in KYC credential | |
| `service[].type` | Service type (`endpoint`, `did-communication`, `DIDComm`, `agentService`) | ℹ️ Agent endpoint | |
| `service[].serviceEndpoint` | URL of the service | ℹ️ Agent endpoint | |
| `service[].routingKeys[]` | DIDComm routing key references | ℹ️ Agent endpoint | |
| `service[].accept[]` | DIDComm protocol versions accepted | ℹ️ Agent endpoint | |

---

## 3. ATTRIB (Off-Ledger Attributes)

The ATTRIB transaction stores a SHA256 hash on-ledger; the raw (or encrypted) data lives off-ledger in an attribute store.

| Sovrin / Indy Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `dest` | DID | The DID the attribute belongs to | `verifiableCredential.credentialSubject.id` | The subject DID. |
| `raw` | SHA256 hash | Hash of the raw attribute JSON (actual data off-ledger) | Various `ivms101.*` and `kycProfile.*` fields | The real off-chain attribute data (e.g. `{"endpoint": "https://..."}`) maps to the respective OpenKYCAML field. See §5 for the identity attribute mapping. |
| `hash` | SHA256 hash | Hash of attribute data as sent by the client | `verifiableCredential.proof.proofValue` | Integrity hash pattern; analogous to the proof value in a VC. |
| `enc` | SHA256 hash | Hash of encrypted attribute data | `verifiableCredential.selectiveDisclosure` | Encrypted attribute storage maps to selective disclosure in OpenKYCAML. |
| `endpoint` (raw value) | URL string | Agent service endpoint URL (common ATTRIB type) | ℹ️ Agent infrastructure, not KYC data | Resolved into the DID Document `service.serviceEndpoint`. |

---

## 4. Credential Schema (SCHEMA Transaction)

The SCHEMA transaction on the Sovrin ledger publishes a list of attribute names. OpenKYCAML maps this to the structured identity fields in the IVMS 101 and KYCProfile sections.

| Indy SCHEMA Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| Schema `id` | `<issuerDID>:2:<name>:<version>` | Unique ledger identifier for the schema | `verifiableCredential.credentialSchema.id` ⭐ | The schema ID is now documented as supporting the Sovrin ledger format in addition to HTTPS URIs. |
| `name` | string | Schema name (e.g. `KYCCredential`, `PersonIdentity`) | `verifiableCredential.type[]` | VC `type` array (e.g. `["VerifiableCredential","KYCCredential"]`) conveys the schema name. |
| `version` | string (semver) | Schema version string | `verifiableCredential.credentialSchema.id` (embedded in ID) | Schema version is part of the ledger `id` format `...:2:<name>:<version>`. |
| `attr_names` | string[] | Ordered list of credential attribute names | See §5 below | Each attribute name maps to a specific OpenKYCAML field — see §5 for the full attribute name mapping. |

---

## 5. Standard KYC Credential Attribute Names → OpenKYCAML Fields

These are the standard attribute names used in Sovrin KYC credential schemas published to the Sovrin ledger. They represent the actual personal data fields.

### 5.1 Natural Person Attributes

| Indy Schema Attribute | Description | OpenKYCAML Field |
|---|---|---|
| `first_name` / `given_name` | Given name(s) | `ivms101.originator.originatorPersons[].naturalPerson.name.nameIdentifier[].secondaryIdentifier` |
| `last_name` / `family_name` | Family / surname | `ivms101.originator.originatorPersons[].naturalPerson.name.nameIdentifier[].primaryIdentifier` |
| `full_name` | Full legal name | Combination of `primaryIdentifier` + `secondaryIdentifier` |
| `birth_date` / `date_of_birth` / `birthdate` | Date of birth (ISO 8601) | `ivms101.originator.originatorPersons[].naturalPerson.dateAndPlaceOfBirth.dateOfBirth` |
| `birth_place` / `place_of_birth` | Place of birth | `ivms101.originator.originatorPersons[].naturalPerson.dateAndPlaceOfBirth.placeOfBirth` |
| `nationality` | ISO 3166-1 alpha-2 nationality code | `ivms101.originator.originatorPersons[].naturalPerson.nationalIdentification.countryOfIssue` (nationality context) |
| `country_of_residence` | ISO 3166-1 alpha-2 country of residence | `ivms101.originator.originatorPersons[].naturalPerson.countryOfResidence` |
| `street_address` / `address` | Street address | `ivms101.originator.originatorPersons[].naturalPerson.geographicAddresses[].streetName` |
| `city` | City | `ivms101.originator.originatorPersons[].naturalPerson.geographicAddresses[].townName` |
| `state` / `county` / `region` | State or region | `ivms101.originator.originatorPersons[].naturalPerson.geographicAddresses[].countrySubDivision` |
| `postal_code` / `zip_code` | Postal / ZIP code | `ivms101.originator.originatorPersons[].naturalPerson.geographicAddresses[].postCode` |
| `country` | ISO 3166-1 alpha-2 country | `ivms101.originator.originatorPersons[].naturalPerson.geographicAddresses[].country` |
| `national_id` / `national_id_number` | National identity number | `ivms101.originator.originatorPersons[].naturalPerson.nationalIdentification.nationalIdentifier` (type `NATIONAL_IDENTITY_NUMBER`) |
| `passport_number` | Passport number | `ivms101.originator.originatorPersons[].naturalPerson.nationalIdentification.nationalIdentifier` (type `PASSPORT_NUMBER`) |
| `document_type` | Document type (PASSPORT, NATIONAL_ID, DRIVING_LICENCE) | `ivms101.originator.originatorPersons[].naturalPerson.nationalIdentification.nationalIdentifierType` |
| `document_number` | Document number | `ivms101.originator.originatorPersons[].naturalPerson.nationalIdentification.nationalIdentifier` |
| `issuing_country` | ISO 3166-1 alpha-2 country of document issue | `ivms101.originator.originatorPersons[].naturalPerson.nationalIdentification.countryOfIssue` |
| `issuing_authority` | Name of issuing authority | `ivms101.originator.originatorPersons[].naturalPerson.nationalIdentification.registrationAuthority` |
| `issue_date` | Document issue date | `ivms101.originator.originatorPersons[].naturalPerson.nationalIdentification.* ` (audit metadata) |
| `expiry_date` | Document expiry date | `kycProfile.monitoringInfo.nextReviewDate` (proxy) |
| `email` | Email address | ℹ️ Not in IVMS 101 / KYCProfile — store in ATTRIB or extend schema |
| `phone` / `phone_number` | Phone number | ℹ️ Not in IVMS 101 / KYCProfile — store in ATTRIB or extend schema |
| `tax_id` / `tin` | Tax identification number | `ivms101.originator.originatorPersons[].naturalPerson.nationalIdentification.nationalIdentifier` (type `TAX_IDENTIFICATION_NUMBER`) |
| `kyc_status` / `kyc_verified` | KYC status flag | `kycProfile.isEligible` + `kycProfile.kycCompletionDate` |
| `risk_level` | Risk classification | `kycProfile.customerRiskRating.overallRiskRating` |
| `aml_check_date` | Date of AML screening | `kycProfile.sanctionsScreening.lastScreenedDate` |

### 5.2 Legal Entity Attributes

| Indy Schema Attribute | Description | OpenKYCAML Field |
|---|---|---|
| `organization_name` / `org_name` / `legal_name` | Legal entity name | `ivms101.originator.originatorPersons[].legalPerson.name.nameIdentifier[].legalPersonName` |
| `registration_number` / `company_number` | Company registration number | `ivms101.originator.originatorPersons[].legalPerson.nationalIdentification.nationalIdentifier` (type `REGISTRATION_AUTHORITY`) |
| `legal_entity_identifier` / `lei` | LEI (ISO 17442) | `ivms101.originator.originatorPersons[].legalPerson.nationalIdentification.nationalIdentifier` (type `LEIX`) |
| `jurisdiction` / `country_of_registration` | Jurisdiction / country of incorporation | `ivms101.originator.originatorPersons[].legalPerson.countryOfRegistration` |
| `registered_address` | Registered office address | `ivms101.originator.originatorPersons[].legalPerson.geographicAddresses[].streetName` etc. |
| `business_type` / `industry` | Business type / industry sector | `kycProfile.customerClassification.industrySector` |
| `incorporation_date` | Date of incorporation | ℹ️ Not in current schema — available via KYCProfile audit |
| `vat_number` | VAT / tax number | `ivms101.originator.originatorPersons[].legalPerson.nationalIdentification.nationalIdentifier` (type `TAX_IDENTIFICATION_NUMBER`) |
| `website` | Company website URL | ℹ️ Not in IVMS 101 / KYCProfile |
| `ultimate_beneficial_owner` | UBO information | `kycProfile.beneficialOwnership[]` |

---

## 6. Credential Definition (CLAIM_DEF Transaction)

The CLAIM_DEF binds an issuer's CL public key to a specific schema. It enables AnonCreds (zero-knowledge-proof) credential issuance.

| Indy CLAIM_DEF Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `credDefId` | `<issuerDID>:3:CL:<schemaSeqNo>:<tag>` | Unique identifier of the Credential Definition | `verifiableCredential.credentialSchema.credDefId` ⭐ | New field added to `credentialSchema` object. Format: `Gs6cQcvrtWoZKsbBhD3dQJ:3:CL:1234:default`. |
| `ref` (schemaSeqNo) | integer | Sequence number of the SCHEMA transaction this definition is created for | Part of `credentialSchema.id` (schema ID) | The schema ID can be resolved back to its sequence number on the ledger. |
| `signature_type` | `CL` | Camenisch-Lysyanskaya signature type (only supported type) | `verifiableCredential.proof.type` = `CLSignature2019` or `AnonCredsProof2023` ⭐ | New proof types added to `VerifiableCredentialProof.type.examples`. |
| `tag` | string | Unique tag for multiple public keys per schema/issuer | Part of `credentialSchema.credDefId` | Embedded in the credDefId format as the last component. |
| `primary` (CL key) | dict | Primary CL public key material | ℹ️ Cryptographic material, not in KYC data | Verified implicitly when validating the AnonCreds proof. |
| `revocation` (CL key) | dict | Revocation CL public key material | ℹ️ Cryptographic material, not in KYC data | |

---

## 7. Revocation Registry (REVOC_REG_DEF + REVOC_REG_ENTRY)

AnonCreds uses cryptographic accumulator-based revocation (CL_ACCUM), where the revocation status is encoded in a mathematical accumulator rather than a list.

| Indy Revocation Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `revocRegDefId` | `<issuerDID>:4:<credDefId>:CL_ACCUM:<tag>` | Revocation Registry Definition ID | `verifiableCredential.credentialStatus.id` ⭐ | For AnonCreds credentials, `credentialStatus.id` holds the revocation registry definition ID or tails file URL. |
| `revocDefType` | `CL_ACCUM` | Revocation type (Camenisch-Lysyanskaya Accumulator) | `verifiableCredential.credentialStatus.type` = `AnonCredsCredentialStatusList2023` ⭐ | New `AnonCredsCredentialStatusList2023` type added to `credentialStatus.type.examples`. |
| `credDefId` | string | Associated Credential Definition ID | `verifiableCredential.credentialSchema.credDefId` ⭐ | Links revocation to the credential definition. |
| `tag` | string | Tag for multiple registries per credential definition | Part of `revocRegDefId` | |
| `maxCredNum` | integer | Maximum number of credentials the registry can handle | ℹ️ Registry capacity, not in KYC credential | |
| `tailsHash` | SHA256 hash | Tails file cryptographic hash | ℹ️ Cryptographic material | |
| `tailsLocation` | URL | URL of the tails file (needed by holder for NRP) | ℹ️ Infrastructure URL | |
| `issuanceType` | `ISSUANCE_BY_DEFAULT` / `ISSUANCE_ON_DEMAND` | Whether credentials are assumed issued or not | ℹ️ Registry configuration | |
| `publicKeys` | dict | Revocation registry public key | ℹ️ Cryptographic material | |
| `accum` (REVOC_REG_ENTRY) | string | Current accumulator value (updated on issuance/revocation) | ℹ️ Registry state | The accumulator is verified by the holder when generating a non-revocation proof. |
| `issued` (delta) | int[] | Indices of issued credentials (delta) | ℹ️ Registry state | |
| `revoked` (delta) | int[] | Indices of revoked credentials (delta) | ℹ️ Registry state | |

---

## 8. AnonCreds Credential (Issued Credential Data)

The AnonCreds credential is the signed object delivered to the holder. When represented as a W3C VC (AnonCreds W3C binding), it wraps these fields.

| AnonCreds Credential Field | Description | OpenKYCAML Field | Notes |
|---|---|---|---|
| `schema_id` | Sovrin ledger schema identifier | `verifiableCredential.credentialSchema.id` ⭐ | AnonCreds schema ID format `<issuerDID>:2:<name>:<version>`. |
| `cred_def_id` | Credential Definition identifier | `verifiableCredential.credentialSchema.credDefId` ⭐ | AnonCreds cred def format `<issuerDID>:3:CL:<seqNo>:<tag>`. |
| `rev_reg_id` | Revocation Registry Definition ID | `verifiableCredential.credentialStatus.id` ⭐ | `null` if credential is non-revocable. |
| `rev_reg_index` | Holder's index in the revocation registry | ℹ️ Holder-private cryptographic state | Not stored in the OpenKYCAML record. |
| `issuer_did` | DID of the credential issuer | `verifiableCredential.issuer` | Standard W3C VC field. |
| `issuance_date` / `issuance_nonce` | When the credential was issued | `verifiableCredential.validFrom` | Standard W3C VC DM 2.0 field. |
| `expiry` (if set) | Expiry epoch | `verifiableCredential.validUntil` | Standard W3C VC DM 2.0 field. |
| `values` (attr dict) | Dictionary of `{attr: {raw, encoded}}` pairs | `verifiableCredential.credentialSubject.*` / `ivms101.*` / `kycProfile.*` | See §5 for attribute-to-field mapping. |
| `signature` (CL) | Camenisch-Lysyanskaya signature over the credential | `verifiableCredential.proof.proofValue` | In the W3C AnonCreds binding, this is in the `proof` section. |
| `signature_correctness_proof` | Proof that the signature is correct | `verifiableCredential.proof.proofValue` | Included in the CL proof. |
| `witness` | Non-revocation proof witness value | ℹ️ Holder-private cryptographic state | Not stored in the KYC record. |

---

## 9. AnonCreds Presentation (ZKP Proof)

An AnonCreds presentation proves possession of credentials without necessarily revealing all attribute values.

| AnonCreds Presentation Field | Description | OpenKYCAML Field | Notes |
|---|---|---|---|
| `nonce` | Challenge nonce from the verifier | ℹ️ Protocol-level, not stored in KYC record | |
| `requested_attributes` | Attributes the verifier requested | `verifiableCredential.selectiveDisclosure.disclosableClaimPaths[]` | OpenKYCAML uses JSON Pointer paths to define which claims may be withheld. |
| `revealed_attrs` | Attribute values actually revealed | `verifiableCredential.credentialSubject.*` (fields with values) | Revealed attributes are present in the VC subject. |
| `unrevealed_attrs` | Attributes withheld (only proof of possession) | `verifiableCredential.selectiveDisclosure.disclosableClaimPaths[]` | OpenKYCAML marks these paths as selectively disclosable. |
| `self_attested_attrs` | Attributes not backed by a credential (self-asserted) | ℹ️ Not supported in OpenKYCAML KYC records | KYC data must be issuer-signed. |
| `requested_predicates` | Range/inequality predicates (e.g. `age >= 18`) | `verifiableCredential.selectiveDisclosure` | Predicates are implicitly supported via ZKP proof type; no explicit predicate field in OpenKYCAML (add to `selectiveDisclosure` if needed). |
| `proof` (ZKP) | The cryptographic proof dict (primary + non-revocation proofs) | `verifiableCredential.proof` | Proof type = `AnonCredsProof2023`. |
| `identifiers[]` | Array of `{schema_id, cred_def_id, rev_reg_id, timestamp}` | `verifiableCredential.credentialSchema` + `verifiableCredential.credentialStatus` | One entry per credential used in the presentation. |
| `proof.proofs[].primary_proof` | Equality and inequality proofs for revealed/predicate attributes | `verifiableCredential.proof.proofValue` | Compact-serialised in the AnonCreds W3C binding. |
| `proof.proofs[].non_revoc_proof` | Non-revocation proof (from accumulator witness) | `verifiableCredential.proof.proofValue` | Included when the credential is revocable. |

---

## 10. Rich Schema Objects (Advanced / Experimental)

The Rich Schema feature allows JSON-LD-based credentials on the Indy ledger. These are currently experimental but align more closely with the W3C VC Data Model.

| Indy Rich Schema Object | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| **JSON_LD_CONTEXT** (type 200) | `rsType: ctx` | JSON-LD `@context` definitions published to the ledger | `verifiableCredential.@context[]` | OpenKYCAML already supports JSON-LD context URIs in `@context`. A ledger-published context would be referenced by its `did:sov:<DID>` URI. |
| **RICH_SCHEMA** (type 201) | `rsType: sch` | JSON-LD schema object (`@id`, `@type`, attributes with types) | `verifiableCredential.credentialSchema.id` | Schema ID would be a `did:sov:<DID>` URI pointing to the Rich Schema on the ledger. |
| **RICH_SCHEMA_ENCODING** (type 202) | `rsType: enc` | Encoding algorithm definitions (maps string/date/etc. to integers for CL signing) | ℹ️ Cryptographic infrastructure | |
| **RICH_SCHEMA_MAPPING** (type 203) | `rsType: map` | Maps Rich Schema attributes to encodings with `rank` ordering | ℹ️ Cryptographic infrastructure | The `issuer` and `validFrom` mapped attributes correspond to `verifiableCredential.issuer` and `verifiableCredential.validFrom`. |
| **RICH_SCHEMA_CRED_DEF** (type 204) | `rsType: cdfd` | Credential Definition for a Rich Schema (issuer public key + mapping ref) | `verifiableCredential.credentialSchema.credDefId` ⭐ | Same field as CLAIM_DEF — `credDefId` can reference either a CLAIM_DEF or RICH_SCHEMA_CRED_DEF ledger object. |
| **RICH_SCHEMA_PRES_DEF** (type 205) | `rsType: pdf` | Presentation Definition — defines what attributes/predicates a verifier requires | `verifiableCredential.selectiveDisclosure.requiredClaimPaths[]` + `disclosableClaimPaths[]` | OpenKYCAML's selective disclosure paths mirror the intent of a presentation definition. |

**Rich Schema common fields:**

| Field | Description | OpenKYCAML Equivalent |
|---|---|---|
| `id` | DID URI (`did:sov:<hash>`) — unique ledger object identifier | `verifiableCredential.credentialSchema.id` |
| `rsName` | Human-readable name | `verifiableCredential.credentialSchema.id` (name embedded in ID) |
| `rsVersion` | Version string | `verifiableCredential.credentialSchema.id` (version embedded in ID) |
| `rsType` | Object type: `ctx`, `sch`, `enc`, `map`, `cdfd`, `pdf` | `verifiableCredential.credentialSchema.type` |
| `content` | JSON-serialised object content | The resolved content of the credential schema/context URI |

---

## 11. Transaction Metadata (Common to All Transactions)

These fields are common to all Indy ledger transactions. They are not part of the KYC credential data, but are relevant to the audit trail.

| Indy Metadata Field | Description | OpenKYCAML Field | Notes |
|---|---|---|---|
| `from` (DID) | Transaction author DID | `kycProfile.auditMetadata.lastModifiedBy` | The DID of the entity who wrote the transaction. |
| `endorser` (DID) | Endorser DID (submits on behalf of author) | `verifiableCredential.issuer` | The endorser has write permissions on the Sovrin ledger. |
| `reqId` | Unique request nonce | `kycProfile.auditMetadata.changeLog[].details` | Not stored in KYC record; relevant for ledger audit. |
| `txnTime` | POSIX timestamp of ledger write | `verifiableCredential.issuanceDate` | The VC issuance date corresponds to when the credential was issued, not when the schema was written. |
| `seqNo` | Ledger sequence number | ℹ️ Ledger infrastructure | |
| `txnId` | Transaction ID (state trie key) | `verifiableCredential.credentialSchema.id` (for SCHEMA) / `verifiableCredential.credentialSchema.credDefId` (for CLAIM_DEF) | The txnId is the basis for the schema and cred def IDs. |
| `reqSignature.type` | Signature type: `ED25519` / `ED25519_MULTI` | `verifiableCredential.proof.type` | `ED25519` → `Ed25519Signature2020`; `ED25519_MULTI` → `DataIntegrityProof` (multisig). |
| `reqSignature.value` | Signature value (base58) | `verifiableCredential.proof.proofValue` | |
| `taaAcceptance.mechanism` | Transaction Author Agreement acceptance mechanism (e.g. `EULA`) | `kycProfile.consentRecord.consentPurpose` | Maps to GDPR/AML consent record. |
| `taaAcceptance.time` | TAA acceptance timestamp | `kycProfile.consentRecord.consentTimestamp` | |
| `taaAcceptance.taaDigest` | SHA256 of the Transaction Author Agreement | `kycProfile.consentRecord.consentVersion` | Hash of agreement accepted. |
| `digest` (payload SHA256) | Integrity hash of all request fields | `verifiableCredential.proof.proofValue` | Integrity is covered by the VC proof in OpenKYCAML. |

---

## 12. Coverage Gap Summary

The following fields were **added to OpenKYCAML v1.2.0** to close gaps identified in this mapping:

| Schema Addition | Sovrin / Indy Equivalent | Location |
|---|---|---|
| `credentialSchema.credDefId` (string) | `CLAIM_DEF` transaction `credDefId` / `RICH_SCHEMA_CRED_DEF` ID | `VerifiableCredentialWrapper.credentialSchema.properties.credDefId` |
| `credentialSchema.type` enum (`AnonCredsDefinition`, `JsonSchema`) | CLAIM_DEF `signature_type` + Rich Schema type `sch` | Replaced `const: "JsonSchemaValidator2018"` with `enum` |
| `credentialSchema.id` description updated | Sovrin schema ID format `<did>:2:<name>:<version>` | `credentialSchema.properties.id.description` |
| `credentialStatus.type` example `AnonCredsCredentialStatusList2023` | `REVOC_REG_DEF` `revocDefType: CL_ACCUM` | `credentialStatus.properties.type.examples` |
| `proof.type` examples `CLSignature2019`, `AnonCredsProof2023` | `CLAIM_DEF` `signature_type: CL` | `VerifiableCredentialProof.properties.type.examples` |

**No schema changes** were required for the following — OpenKYCAML already covered them:

| Sovrin / Indy Data Point | Existing OpenKYCAML Coverage |
|---|---|
| DID (did:sov, did:indy) | `verifiableCredential.credentialSubject.id` (format: URI, description: DID) |
| Ed25519 verification key | `verifiableCredential.proof.verificationMethod` (DID URL resolves to key) |
| All KYC identity attributes (name, DOB, address, document numbers) | `ivms101.*` — full IVMS 101 model |
| Legal entity attributes (org name, registration, LEI) | `ivms101.*` legalPerson fields |
| Issuer identity | `verifiableCredential.issuer` |
| Credential issuance date | `verifiableCredential.validFrom` |
| Credential expiry | `verifiableCredential.validUntil` |
| JSON-LD context | `verifiableCredential.@context` |
| Selective disclosure / ZKP claims | `verifiableCredential.selectiveDisclosure` |
| KYC status, risk rating, AML checks | `kycProfile.*` |
| Beneficial ownership | `kycProfile.beneficialOwnership[]` |
| Sanctions / PEP screening | `kycProfile.sanctionsScreening`, `kycProfile.pepStatus` |
| Consent record (TAA acceptance → GDPR) | `kycProfile.consentRecord` |
| Audit trail | `kycProfile.auditMetadata` |
| Ongoing monitoring | `kycProfile.monitoringInfo` |

---

## 13. Integration Guidance: OpenKYCAML → Sovrin/Indy Pipeline

### Step 1 — Publish a KYC Schema to the Sovrin Ledger

Map the OpenKYCAML `ivms101` attribute names to an Indy SCHEMA `attr_names` array:

```json
{
  "name": "KYCCredential",
  "version": "1.0",
  "attr_names": [
    "first_name",
    "last_name",
    "birth_date",
    "country_of_residence",
    "national_id",
    "document_type",
    "issuing_country",
    "kyc_status",
    "kyc_completion_date",
    "risk_level"
  ]
}
```

Store the resulting schema ID in `verifiableCredential.credentialSchema.id`:
```json
{
  "credentialSchema": {
    "id": "Gs6cQcvrtWoZKsbBhD3dQJ:2:KYCCredential:1.0",
    "type": "AnonCredsDefinition",
    "credDefId": "Gs6cQcvrtWoZKsbBhD3dQJ:3:CL:1234:default"
  }
}
```

### Step 2 — Issue an AnonCreds KYC Credential

Map OpenKYCAML fields to AnonCreds attribute values:

```
first_name  → ivms101.originator.originatorPersons[0].naturalPerson.name.nameIdentifier[0].secondaryIdentifier
last_name   → ivms101.originator.originatorPersons[0].naturalPerson.name.nameIdentifier[0].primaryIdentifier
birth_date  → ivms101.originator.originatorPersons[0].naturalPerson.dateAndPlaceOfBirth.dateOfBirth
country_of_residence → ivms101.originator.originatorPersons[0].naturalPerson.countryOfResidence
national_id → ivms101.originator.originatorPersons[0].naturalPerson.nationalIdentification.nationalIdentifier
kyc_status  → kycProfile.isEligible (true/false → "verified"/"unverified")
risk_level  → kycProfile.customerRiskRating.overallRiskRating
```

### Step 3 — Set Proof Type for AnonCreds Credentials

```json
{
  "verifiableCredential": {
    "proof": {
      "type": "AnonCredsProof2023",
      "verificationMethod": "did:sov:Gs6cQcvrtWoZKsbBhD3dQJ#key-1",
      "proofPurpose": "assertionMethod",
      "proofValue": "<base64url-encoded CL proof>"
    }
  }
}
```

### Step 4 — Configure Revocation (if credential is revocable)

```json
{
  "verifiableCredential": {
    "credentialStatus": {
      "id": "Gs6cQcvrtWoZKsbBhD3dQJ:4:Gs6cQcvrtWoZKsbBhD3dQJ:3:CL:1234:default:CL_ACCUM:reg1",
      "type": "AnonCredsCredentialStatusList2023"
    }
  }
}
```

Set `kycProfile.isEligible = false` and update `kycProfile.monitoringInfo.monitoringStatus` when revocation is triggered.

### Step 5 — Selective Disclosure Configuration

For ZKP presentations where only some attributes are revealed (e.g., prove `age >= 18` without revealing actual DOB):

```json
{
  "verifiableCredential": {
    "selectiveDisclosure": {
      "_sd_alg": "sha-256",
      "disclosableClaimPaths": [
        "/credentialSubject/ivms101/originator/originatorPersons/0/naturalPerson/dateAndPlaceOfBirth/dateOfBirth"
      ],
      "requiredClaimPaths": [
        "/credentialSubject/ivms101/originator/originatorPersons/0/naturalPerson/name/nameIdentifier/0/primaryIdentifier",
        "/credentialSubject/kycProfile/isEligible"
      ]
    }
  }
}
```

FATF Travel Rule mandatory fields (name, account number) **must** be in `requiredClaimPaths` and **must not** appear in `disclosableClaimPaths`.

---

## 14. DID Method Comparison

| Aspect | `did:sov` | `did:indy` | OpenKYCAML Support |
|---|---|---|---|
| DID format | `did:sov:<base58-16bytes>` | `did:indy:<namespace>:<base58-SHA256>` | Both accepted in `credentialSubject.id` (format: URI) |
| Key binding | First 16 bytes of verkey (NYM v1) | SHA256-derived self-certifying (NYM v2) | Via `proof.verificationMethod` DID URL |
| Update | NYM transaction signed by current verkey | NYM transaction signed by current verkey | `kycProfile.auditMetadata.changeLog[]` |
| Deactivation | NYM `role: null` (removes write permissions); verkey → null (guardianship) | Same | `kycProfile.monitoringInfo.monitoringStatus` |
| Service endpoints | ATTRIB `endpoint` raw value | ATTRIB `endpoint` raw value | ℹ️ Agent infrastructure, not KYC data |
| Network | Sovrin MainNet (`did:sov`) | Any Indy network (e.g. `did:indy:sovrin`, `did:indy:idunion`) | Distinguish via DID method in `credentialSubject.id` |

---

*Document version: v1.12.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*
*Sovrin sources: [sovrin-foundation/sovrin](https://github.com/sovrin-foundation/sovrin), [hyperledger-indy/indy-node](https://github.com/hyperledger-indy/indy-node)*
*AnonCreds: [Hyperledger AnonCreds Specification](https://hyperledger.github.io/anoncreds-spec/)*
