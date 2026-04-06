# OpenKYCAML ↔ XRPL Credentials, DIDs, and Multi-Purpose Tokens (MPTs) Mapping

This document maps every data point in the **XRP Ledger (XRPL) Credentials** standard (XLS-40d), the **XRPL DID** method, and the **XRPL Multi-Purpose Token (MPT)** standard (XLS-33d) to the corresponding field in the OpenKYCAML schema. It also documents the on-ledger KYC/AML gating pipeline and concludes on schema coverage versus the need for extensions.

**XRPL sources used:**
- [XLS-40d — Credentials amendment](https://github.com/XRPLF/XRPL-Standards/discussions/136) — `Credential` and `DID` ledger objects; `CredentialCreate`, `CredentialAccept`, `CredentialDelete` transactions; `DepositPreauth` with credential gating
- [XLS-33d — Multi-Purpose Tokens](https://github.com/XRPLF/XRPL-Standards/discussions/120) — `MPTIssuance` and `MPToken` ledger objects; `MPTokenIssuanceCreate`, `MPTokenIssuanceDestroy`, `MPTokenAuthorize`, `MPTokenIssuanceSet` transactions
- [XRPL DID Method Specification](https://github.com/XRPLF/XRPL-Standards/discussions/140) (`did:xrpl`) — on-ledger `DID` object, DID Document resolution, verification methods
- [W3C Verifiable Credentials Data Model v2.0](https://www.w3.org/TR/vc-data-model-2.0/)
- [W3C Decentralized Identifiers (DIDs) v1.0](https://www.w3.org/TR/did-core/)

**Coverage legend:**
- ✅ Full coverage — field exists in OpenKYCAML schema
- 🔄 Conceptual mapping — equivalent concept captured differently (see notes)
- ⭐ Schema extended — field added to OpenKYCAML v1.3.0 to close the gap
- ℹ️ Out of scope — on-ledger / runtime state not applicable to an off-chain KYC record

---

## 1. Architecture Overview

XRPL's compliance infrastructure combines three separate on-ledger primitives that together deliver credential-gated permissioned tokens — a strong parallel to the ERC-3643 pattern already mapped in OpenKYCAML:

| XRPL Component | Purpose | OpenKYCAML Equivalent |
|---|---|---|
| **`Credential` object** (XLS-40d) | On-ledger anchor for a W3C VC: binds `Subject` account + `Issuer` account + `CredentialType` + optional `URI` pointing to the off-chain VC payload | `verifiableCredential` wrapper — the OpenKYCAML VC is the off-chain content that `URI` references |
| **`DID` object** (XLS-40d) | On-ledger DID Document stub for `did:xrpl:<network>:<account>`; holds key material or a `URI` to the full DID Document | `verifiableCredential.issuer`, `verifiableCredential.credentialSubject.id`, and `verifiableCredential.evidence[].credentialIssuer` — all expressed as DIDs |
| **`MPTIssuance` object** (XLS-33d) | Permissioned token issuance with optional `lsfMPTRequireAuth` gate; holder accounts must be individually authorised by the issuer | `kycProfile.isEligible` + `kycProfile.blockchainAccountIds[]` — off-chain eligibility and wallet registration |
| **`MPToken` object** (XLS-33d) | Per-holder token balance with `lsfMPTAuthorized` flag | `kycProfile.isEligible`, `kycProfile.blockchainAccountIds[].isFrozen` |
| **`DepositPreauth` with credentials** (XLS-40d) | Account-level deposit gate: only senders holding a specified `{Issuer, CredentialType}` credential may pay to the account | `kycProfile.isEligible` + `verifiableCredential.type[]` — off-chain pre-authorisation record |

### How OpenKYCAML fits into the XRPL KYC/AML pipeline

```
1. VASP or KYC utility performs KYC/AML → issues OpenKYCAML payload
2. OpenKYCAML VC is stored off-ledger (HTTPS / IPFS / DIDComm)
3. VASP calls CredentialCreate:
      Subject      = rXRPL_account_of_customer
      Issuer       = rXRPL_account_of_VASP
      CredentialType = hex("OpenKYCAMLCredential")
      URI          = https://kyc.vasp.example/vc/<uuid>   ← OpenKYCAML payload URI
4. Customer calls CredentialAccept → lsfAccepted = true
5. MPT issuer or DepositPreauth account gate:
      AuthorizedCredentials = [{Issuer: rVASP, CredentialType: hex("OpenKYCAMLCredential")}]
6. Customer with accepted credential can now hold/transfer the MPT or deposit to gated accounts
```

This is structurally identical to the ERC-3643 pipeline (ONCHAINID on-chain + off-chain claim URI), confirming the strong synergy assertion: **no new VC payload fields are required** to describe the credential content. The XRPL-specific mapping primarily covers the on-ledger anchor fields and the DID method.

---

## 2. W3C Standards Alignment Assessment

### 2.1 W3C Verifiable Credentials Data Model v2.0 (VC DM v2)

The XRPL Credential object is explicitly designed as an **on-ledger anchor for a W3C VC**. The `URI` field in the `Credential` object is intended to resolve to a W3C VC payload — precisely what the OpenKYCAML `verifiableCredential` block produces.

| W3C VC DM v2 Concept | XRPL `Credential` Field | OpenKYCAML Field | Coverage |
|---|---|---|---|
| `id` — credential URI | Derived: `CredentialID` (SHA-512/256 hash of `{Subject, Issuer, CredentialType}`) | `verifiableCredential.id` | 🔄 XRPL uses a hash key; OpenKYCAML stores the canonical URI. Map: `verifiableCredential.id` → set as XRPL `URI` |
| `issuer` | `Issuer` (XRPL account address, e.g. `rKYCIssuer...`) | `verifiableCredential.issuer.id` (DID, e.g. `did:xrpl:1:rKYCIssuer...`) | ✅ DID-to-r-address derivation is deterministic (see §3) |
| `credentialSubject.id` | `Subject` (XRPL account address) | `verifiableCredential.credentialSubject.id` (DID, e.g. `did:xrpl:1:rCustomer...`) | ✅ Same derivation |
| `validUntil` / `expirationDate` | `Expiration` (Ripple epoch seconds) | `verifiableCredential.expirationDate` (ISO 8601) | ✅ Convert: Ripple epoch = Unix epoch − 946684800 |
| `type[]` — credential type | `CredentialType` (1–64 bytes hex-encoded) | `verifiableCredential.type[]` (string array) | 🔄 See §2.2 |
| `proof` — cryptographic proof | Validated by XRPL ledger consensus; `Issuer` account signature | `verifiableCredential.proof` (Ed25519Signature2020 / JWS) | 🔄 XRPL ledger consensus replaces the VC `proof` for on-ledger anchors; the off-chain VC retains its own `proof` |
| `credentialStatus` — revocation | `CredentialDelete` transaction removes the on-ledger credential | `verifiableCredential.credentialStatus` (StatusList2021Entry) | 🔄 On-ledger deletion is the XRPL revocation mechanism; off-chain `credentialStatus` is retained for VC-native verification flows |
| `issuanceDate` / `validFrom` | Not a distinct field (block close-time of `CredentialCreate` tx) | `verifiableCredential.issuanceDate` | ✅ Store block close-time as `issuanceDate` in the off-chain VC |
| `credentialSubject.*` | `URI` → off-chain payload | All `verifiableCredential.credentialSubject.*` fields | ✅ Full OpenKYCAML payload is the off-chain content |
| `lsfAccepted` flag | `Flags` bit on `Credential` | No direct field (acceptance is on-ledger state) | ℹ️ On-ledger only; record acceptance date in `kycProfile.auditMetadata.changeLog[]` |

### 2.2 CredentialType Encoding

XRPL encodes credential types as **hex strings** (1–64 bytes), typically the UTF-8 hex of a human-readable type name. W3C VC uses string arrays. The mapping is:

| XRPL `CredentialType` (hex) | Decoded string | OpenKYCAML `verifiableCredential.type[]` entry |
|---|---|---|
| `4b5943` | `KYC` | `"KYCCredential"` |
| `414d4c` | `AML` | `"AMLCredential"` |
| `4f70656e4b5943414d4c43726564656e7469616c` | `OpenKYCAMLCredential` | `"OpenKYCAMLCredential"` |
| `547261766c6552756c65417474657374` | `TravelRuleAttest` | `"TravelRuleAttestation"` |
| `41636372656469746564496e766573746f72` | `AccreditedInvestor` | `"AccreditedInvestorCredential"` |

**Recommended practice:** set `verifiableCredential.type[]` to include the decoded string equivalent, and record the hex value in `kycProfile.blockchainAccountIds[].xrplCredentialType` ⭐ (added v1.3.0) for auditability and round-trip XRPL reconstruction.

### 2.3 W3C DID Core v1.0

The `did:xrpl` method derives a DID deterministically from the XRPL account address. This is fully compatible with OpenKYCAML's DID-agnostic design — every DID field in the schema accepts `did:xrpl` URIs without modification.

---

## 3. XRPL DID Object

The `DID` ledger object is the on-ledger anchor for `did:xrpl:<network>:<account>` DIDs.

| XRPL DID Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `Account` | XRPL address | The XRPL account that owns and controls this DID | `verifiableCredential.credentialSubject.id` or `verifiableCredential.issuer.id` | DID form: `did:xrpl:1:<Account>` (mainnet), `did:xrpl:0:<Account>` (testnet/devnet). The DID URL is derived from the classic r-address. |
| `DIDDocument` | hex (≤ 256 bytes) | Abbreviated JSON-LD DID Document stub stored on-ledger. Full DID Document is off-ledger and referenced via `URI`. | `verifiableCredential.proof.verificationMethod` (resolved from DID Document) | The on-ledger stub typically carries only `@context`, `id`, and a single `verificationMethod` entry. OpenKYCAML resolves this at proof verification time. |
| `URI` | hex string | URI pointing to the full DID Document (off-ledger, e.g. `https://did.vasp.example/xrpl/<account>`) | `verifiableCredential.credentialSubject.id` (resolves via DID resolver) | The DID resolver fetches the full DID Document from this URI. The `DIDDocument` on-ledger is a cache/stub. |
| `Data` | hex (≤ 256 bytes) | Optional issuer-defined metadata associated with the DID | ℹ️ Not in KYC credential directly | May carry a JSON reference to the KYC utility endpoint. |

### 3.1 DID Document Fields (resolved)

| DID Document Field | Description | OpenKYCAML Field | Notes |
|---|---|---|---|
| `id` | `did:xrpl:1:<account>` | `verifiableCredential.issuer.id` or `verifiableCredential.credentialSubject.id` | ✅ |
| `verificationMethod[].id` | DID URL: `did:xrpl:1:<account>#key-1` | `verifiableCredential.proof.verificationMethod` | ✅ |
| `verificationMethod[].type` | `Ed25519VerificationKey2020` (XRPL native), `JsonWebKey2020` | `verifiableCredential.proof.type` | ✅ Ed25519Signature2020 matches XRPL native Ed25519 keys |
| `verificationMethod[].publicKeyMultibase` | Base58btc-encoded Ed25519 public key | `verifiableCredential.proof.verificationMethod` (resolved) | ✅ |
| `authentication[]` | Verification method references | ℹ️ DID Document, not in KYC credential | Used for DIDComm channel setup |
| `service[].type` | `LinkedDomains` or `KYCEndpoint` | ℹ️ Service endpoint, not in KYC credential | Can reference the VASP's OpenKYCAML endpoint |

### 3.2 DID Triangulation — XRPL Trust Chain

OpenKYCAML's three-party DID triangulation maps directly to XRPL:

| Role | XRPL Entity | DID Form | OpenKYCAML Field |
|---|---|---|---|
| **Subject** (customer wallet) | Customer XRPL account | `did:xrpl:1:rCustomer...` | `verifiableCredential.credentialSubject.id` |
| **Credential Issuer** (KYC VASP / utility) | Issuing VASP XRPL account | `did:xrpl:1:rKYCIssuer...` | `verifiableCredential.issuer.id` + `verifiableCredential.evidence[].credentialIssuer` |
| **Relying Party** (beneficiary VASP / MPT issuer) | Receiving VASP XRPL account | `did:xrpl:1:rRelyingParty...` | `verifiableCredential.evidence[].verifier` |

---

## 4. XRPL Credential Object

The `Credential` ledger object (XLS-40d) stores the on-ledger metadata for a W3C VC whose payload lives off-chain.

| XRPL `Credential` Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `Subject` | XRPL account address | The credential holder | `verifiableCredential.credentialSubject.id` | In OpenKYCAML, expressed as `did:xrpl:1:<Subject>`. The XRPL r-address is the last part of the DID. |
| `Issuer` | XRPL account address | The credential issuer | `verifiableCredential.issuer.id` | In OpenKYCAML, expressed as `did:xrpl:1:<Issuer>`. |
| `CredentialType` | hex (1–64 bytes) | Type identifier for the credential (e.g. `4b5943` = `KYC`) | `verifiableCredential.type[]` | See §2.2 for hex ↔ string mapping. The W3C VC `type[]` array carries the human-readable equivalent. |
| `URI` | hex (optional, ≤ 256 bytes) | URI of the off-chain VC payload | `verifiableCredential.id` | Set this to the canonical URI of the OpenKYCAML VC. Resolves to the full `verifiableCredential` block. |
| `Expiration` | UInt32 (Ripple epoch) | Credential expiry as seconds since 2000-01-01T00:00:00Z | `verifiableCredential.expirationDate` | Convert: Unix timestamp = Ripple epoch + 946684800. |
| `Flags: lsfAccepted` (0x00010000) | bool | Whether the `Subject` account has accepted the credential via `CredentialAccept` | ℹ️ On-ledger state only | Record the acceptance date in `kycProfile.auditMetadata.changeLog[]` with event `UPDATED` and note `"credential_accepted"`. |
| `CredentialID` | Hash256 | Ledger key: `SHA-512/256(Subject || Issuer || CredentialType)` | `kycProfile.auditMetadata.changeLog[].details` or external reference | Opaque on-ledger key; store in audit metadata if XRPL-anchored flow is needed for cross-reference. |
| `SubjectNode` / `IssuerNode` | UInt64 | Ledger navigation links (skiplist) | ℹ️ Ledger infrastructure, not KYC data | Not relevant to the KYC record. |

### 4.1 CredentialCreate Transaction

| `CredentialCreate` Field | OpenKYCAML Field | Notes |
|---|---|---|
| `Account` (tx submitter = Issuer) | `verifiableCredential.issuer.id` | Issuer signs and submits the create transaction. |
| `Subject` | `verifiableCredential.credentialSubject.id` | The customer receiving the credential. |
| `CredentialType` | `verifiableCredential.type[]` | Hex-encoded type; decode to string for OpenKYCAML. |
| `URI` | `verifiableCredential.id` | Canonical URI of the OpenKYCAML VC payload. |
| `Expiration` | `verifiableCredential.expirationDate` | Convert ISO 8601 → Ripple epoch. |

### 4.2 DepositPreauth with Credential Gating

XRPL accounts with `lsfDepositAuth` can specify `AuthorizedCredentials` — only senders holding a matching credential may deposit.

| `DepositPreauth` / `AuthorizedCredentials` Field | Description | OpenKYCAML Field | Notes |
|---|---|---|---|
| `Issuer` | Address of the trusted credential issuer | `verifiableCredential.issuer.id` (as DID) | The relying party trusts credentials issued by this XRPL account. |
| `CredentialType` | Hex type the sender must hold | `verifiableCredential.type[]` | Must match the `CredentialType` set on the sender's `Credential` object. |
| Evaluation: sender holds `lsfAccepted` credential | Whether the sender's `Credential` object exists, is accepted, and is not expired | `kycProfile.isEligible: true` | `isEligible` is the off-chain record of the same determination. |

---

## 5. MPTIssuance Object (Permissioned Token)

The `MPTIssuance` object (XLS-33d) is the XRPL equivalent of an ERC-3643 security token with `lsfMPTRequireAuth` as the permissioning gate.

| `MPTIssuance` Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `Issuer` | XRPL account | Token issuer | `verifiableCredential.issuer.id` (as DID) | The MPT issuer is typically the VASP or asset manager who also issues the KYC credential, or relies on a trusted KYC issuer DID. |
| `MPTokenIssuanceID` | Hash192 | Unique on-ledger identifier for the issuance | `kycProfile.blockchainAccountIds[].network` annotation | Not stored per-investor; it identifies the token issuance. Record in `kycProfile.auditMetadata` or a transaction reference if cross-referencing is needed. |
| `AssetScale` | UInt8 | Decimal scaling factor (analogous to ERC-20 `decimals`) | ℹ️ Token metadata, not investor KYC | |
| `MaximumAmount` | UInt64 (optional) | Maximum token supply | ℹ️ Token metadata | |
| `TransferFee` | UInt16 (optional) | Transfer fee in millionths | ℹ️ Token metadata | |
| `MPTokenMetadata` | hex (≤ 1024 bytes) | Issuer-defined token metadata (e.g. ISIN, asset class) | ℹ️ Token metadata | |
| `Flags: lsfMPTRequireAuth` | bool | Holders must be individually authorised before receiving tokens | `kycProfile.isEligible` | If `true`, the issuer must submit `MPTokenAuthorize` for each holder. `isEligible: true` is the off-chain prerequisite. |
| `Flags: lsfMPTCanTransfer` | bool | Whether MPTs can be transferred between non-issuer accounts | `kycProfile.dueDiligenceType` + `kycProfile.isEligible` | If `false`, only the issuer can move tokens (primary issuance model). CDD tier influences whether transfer is permissible. |
| `Flags: lsfMPTCanClawback` | bool | Whether the issuer can claw back tokens from any holder | `kycProfile.blockchainAccountIds[].isFrozen` | Clawback capability implies the issuer can reverse transfers — record custodial/claw-back risk in `monitoringInfo`. |
| `Flags: lsfMPTLocked` | bool | Whether the entire MPT issuance is locked (paused) | ℹ️ Token-level state, not investor-level | |

---

## 6. MPToken Object (Holder Authorisation)

The `MPToken` object is the per-holder state in an MPT issuance. `lsfMPTAuthorized` is the on-ledger gate that is directly driven by the KYC outcome.

| `MPToken` Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `Account` | XRPL address | The token holder | `kycProfile.blockchainAccountIds[].address` | Use `network: "xrpl"` (or CAIP-2 equivalent `xrpl:1` for mainnet). |
| `MPTokenIssuanceID` | Hash192 | Which MPT issuance this balance belongs to | `kycProfile.blockchainAccountIds[].network` + audit reference | Not per-investor KYC data; cross-reference in `kycProfile.auditMetadata.changeLog[]` for specific issuance association. |
| `MPTokenAmount` | UInt64 | Current balance | ℹ️ Token balance, not KYC data | Live on-chain state. |
| `Flags: lsfMPTAuthorized` | bool | Whether the issuer has authorised this holder via `MPTokenAuthorize` | `kycProfile.isEligible` | Direct equivalent: `isEligible: true` ↔ `lsfMPTAuthorized = 1`. Set by the issuer after KYC/AML completion. `kycProfile.eligibilityLastConfirmed` stores the date. |
| `Flags: lsfMPTLocked` | bool | Whether this specific holder's tokens are locked | `kycProfile.blockchainAccountIds[].isFrozen` | Per-holder freeze maps to `isFrozen: true` on the matching `blockchainAccountIds[]` entry. |

### 6.1 MPTokenAuthorize Transaction

| `MPTokenAuthorize` Field | Description | OpenKYCAML Field | Notes |
|---|---|---|---|
| `Account` (Issuer action) | Issuer grants or revokes holder authorisation | `verifiableCredential.issuer.id` | Issuer acts after verifying the OpenKYCAML KYC payload. |
| `MPTokenHolder` | Holder's XRPL address | `kycProfile.blockchainAccountIds[].address` | The address receiving authorisation. |
| `Flags: tfMPTUnauthorize` | Revokes authorisation | `kycProfile.isEligible: false` | After revocation, update `isEligible: false` and add a `changeLog` entry. |

---

## 7. KYC/AML Gating → OpenKYCAML Field Mapping

These are the per-investor KYC/AML data points that determine on-ledger gating decisions.

| KYC/AML Gate Requirement | XRPL Mechanism | OpenKYCAML Field | Notes |
|---|---|---|---|
| Identity verified (natural person) | `Credential` object with `CredentialType = KYC` | `kycProfile.kycCompletionDate` + `kycProfile.dueDiligenceRequirements` | ✅ |
| AML screening passed | `Credential` object with `CredentialType = AML` | `kycProfile.sanctionsScreening.screeningStatus = CLEAR` + `kycProfile.adverseMedia.overallOutcome = CLEAR` | ✅ |
| Accredited / eligible investor | `Credential` with `CredentialType = AccreditedInvestor` | `kycProfile.customerClassification.accreditedInvestor: true` + `investorCategoryJurisdiction` | ✅ |
| Country restriction | `DepositPreauth` country check (via investor country in KYC) | `ivms101.originator.originatorPersons[].naturalPerson.countryOfResidence` | ✅ XRPL uses the off-chain KYC record to determine permissible jurisdictions |
| Not on sanctions list | `Credential` with AML type and screening result | `kycProfile.sanctionsScreening.screeningStatus` ≠ `MATCH` | ✅ |
| PEP status determined | EDD triggers elevated `CredentialType` requirement | `kycProfile.pepStatus.isPEP` + `kycProfile.dueDiligenceType = EDD` | ✅ |
| Source of funds verified | Custom credential type in high-risk issuances | `kycProfile.sourceOfFundsWealthDetail` | ✅ |
| Credential not expired | `Expiration` on `Credential` object | `verifiableCredential.expirationDate` | ✅ |
| Credential accepted by holder | `lsfAccepted` flag | Record in `kycProfile.auditMetadata.changeLog[]` | 🔄 |
| Holder authorised for MPT | `lsfMPTAuthorized` on `MPToken` | `kycProfile.isEligible: true` + `kycProfile.eligibilityLastConfirmed` | ✅ |
| Holder wallet frozen | `lsfMPTLocked` on `MPToken` | `kycProfile.blockchainAccountIds[].isFrozen: true` | ✅ |
| XRPL on-ledger credential type (for cross-reference) | `Credential.CredentialType` (hex) | `kycProfile.blockchainAccountIds[].xrplCredentialType` ⭐ | ✅ v1.3.0+ — stores hex CredentialType for round-trip XRPL reconstruction |
| MPT issuance identifier (multi-issuance) | `MPToken.MPTokenIssuanceID` | `kycProfile.blockchainAccountIds[].mptIssuanceId` ⭐ | ✅ v1.3.0+ — stores Hash192 MPTokenIssuanceID for multi-pool eligibility tracking |

---

## 8. Coverage Gap Summary

### 8.1 No schema changes required

The following XRPL-specific concepts are **fully covered** by existing OpenKYCAML fields without modification:

| XRPL Concept | Existing OpenKYCAML Coverage |
|---|---|
| `Credential.Subject` → DID | `verifiableCredential.credentialSubject.id` (DID-agnostic) |
| `Credential.Issuer` → DID | `verifiableCredential.issuer.id` (DID-agnostic) |
| `Credential.Expiration` | `verifiableCredential.expirationDate` |
| `Credential.URI` → VC payload | `verifiableCredential.id` (canonical URI of the VC) |
| `did:xrpl` DID method | All DID fields are DID-method-agnostic; `did:xrpl:1:r...` is a valid value |
| DID triangulation (subject / KYC issuer / relying party) | `verifiableCredential.evidence[].credentialIssuer` + `.verifier` + `credentialSubject.id` |
| `MPToken.lsfMPTAuthorized` | `kycProfile.isEligible` |
| `MPToken.lsfMPTLocked` | `kycProfile.blockchainAccountIds[].isFrozen` |
| Holder XRPL wallet address | `kycProfile.blockchainAccountIds[].address` (`network: "xrpl"`) |
| XRPL on-ledger credential type | `kycProfile.blockchainAccountIds[].xrplCredentialType` ⭐ (hex CredentialType, added v1.3.0) |
| MPT issuance identifier | `kycProfile.blockchainAccountIds[].mptIssuanceId` ⭐ (Hash192 MPTokenIssuanceID, added v1.3.0) |
| Credential proof (ledger-validated) | `verifiableCredential.proof` (off-chain VC proof; ledger validation is additive) |
| Credential revocation | `verifiableCredential.credentialStatus` (StatusList2021Entry) + on-ledger `CredentialDelete` |
| Sanctions / AML screening | `kycProfile.sanctionsScreening`, `kycProfile.adverseMedia` |
| KYC completion | `kycProfile.kycCompletionDate`, `kycProfile.dueDiligenceRequirements` |
| Accredited investor | `kycProfile.customerClassification.accreditedInvestor` |
| Travel Rule (VASP-to-VASP) | `ivms101` block (IVMS 101 superset) |
| GDPR / SAR tipping-off | `gdprSensitivityMetadata` block |

### 8.2 Schema extensions added in v1.3.0 ⭐

Two optional fields were added to `kycProfile.blockchainAccountIds[]` items to improve the precision of XRPL-specific integrations without any breaking changes:

| Field | Rationale | Pattern |
|---|---|---|
| `kycProfile.blockchainAccountIds[].xrplCredentialType` ⭐ (string, optional) | Stores the hex `CredentialType` value from the XRPL `Credential` object alongside the wallet address entry, enabling round-trip reconstruction of the on-ledger credential without relying on external state. The decoded string equivalent is captured in `verifiableCredential.type[]`. Pattern: `^[0-9a-fA-F]{2,128}$` (2–128 hex chars = 1–64 bytes, case-insensitive). | `^[0-9a-fA-F]{2,128}$` |
| `kycProfile.blockchainAccountIds[].mptIssuanceId` ⭐ (string, optional) | Stores the `MPTokenIssuanceID` (Hash192) of the specific MPT issuance this wallet is authorised for. Useful for multi-issuance scenarios where a single investor holds authorisation for multiple regulated asset pools via separate `MPTokenAuthorize` transactions. Pattern: exactly 48 hex characters (24 bytes, case-insensitive). | `^[0-9a-fA-F]{48}$` |

Both fields are **additive** — existing payloads without these fields remain fully valid.

### 8.3 Conclusion: Is a mapping document sufficient?

**Yes.** The core assertion is confirmed:

> The existing OpenKYCAML VC wrapper and DID triangulation are architecturally sufficient to serve as the off-chain credential content anchored by the XRPL `Credential` ledger object. The `did:xrpl` DID method is compatible with OpenKYCAML's DID-agnostic design. The `kycProfile.isEligible` + `blockchainAccountIds[]` fields directly map to MPT holder authorisation. No structural schema redesign is needed.

---

## 9. Integration Guidance: OpenKYCAML → XRPL KYC/AML Gating Pipeline

### Step 1 — Issue the OpenKYCAML VC

Complete KYC/AML and issue the OpenKYCAML payload. Set:

```json
{
  "verifiableCredential": {
    "@context": [
      "https://www.w3.org/2018/credentials/v1",
      "https://openkycaml.org/contexts/v1"
    ],
    "id": "https://kyc.vasp.example/vc/550e8400-e29b-41d4-a716-446655440000",
    "type": ["VerifiableCredential", "OpenKYCAMLCredential", "KYCCredential"],
    "issuer": {
      "id": "did:xrpl:1:rKYCIssuerAccountAddress",
      "name": "VASP KYC Division"
    },
    "issuanceDate": "2026-04-01T12:00:00Z",
    "expirationDate": "2027-04-01T12:00:00Z",
    "credentialSubject": {
      "id": "did:xrpl:1:rCustomerAccountAddress",
      "ivms101": { "...": "..." },
      "kycProfile": {
        "isEligible": true,
        "eligibilityLastConfirmed": "2026-04-01",
        "blockchainAccountIds": [{
          "address": "rCustomerAccountAddress",
          "network": "xrpl"
        }]
      }
    },
    "evidence": [{
      "id": "urn:uuid:kyc-evidence-2026-04-01",
      "type": ["KYCCompletionEvidence"],
      "credentialIssuer": "did:xrpl:1:rKYCIssuerAccountAddress",
      "verifier": "did:xrpl:1:rRelyingPartyAccountAddress",
      "presentationMethod": "OpenID4VP",
      "presentationDate": "2026-04-01T11:55:00Z"
    }],
    "proof": {
      "type": "Ed25519Signature2020",
      "verificationMethod": "did:xrpl:1:rKYCIssuerAccountAddress#key-1",
      "proofPurpose": "assertionMethod",
      "proofValue": "..."
    }
  }
}
```

### Step 2 — Store VC off-chain and anchor on XRPL

Submit a `CredentialCreate` transaction:

```json
{
  "TransactionType": "CredentialCreate",
  "Account": "rKYCIssuerAccountAddress",
  "Subject": "rCustomerAccountAddress",
  "CredentialType": "4f70656e4b5943414d4c43726564656e7469616c",
  "URI": "68747470733a2f2f6b79632e766173702e6578616d706c652f76632f353530...",
  "Expiration": 859411200
}
```

Field derivation:
- `CredentialType` = `hex("OpenKYCAMLCredential")` = `4f70656e4b5943414d4c43726564656e7469616c`
- `URI` = hex-encoded `verifiableCredential.id`
- `Expiration` = ISO 8601 `expirationDate` converted to Ripple epoch (`Unix timestamp − 946684800`)

### Step 3 — Customer accepts the credential

Customer submits `CredentialAccept` (or issuer submits with the `tfAccept` flag if pre-approved). Record in OpenKYCAML:

```json
{
  "kycProfile": {
    "auditMetadata": {
      "changeLog": [{
        "eventType": "UPDATED",
        "eventDate": "2026-04-01T14:00:00Z",
        "changedBy": "rCustomerAccountAddress",
        "details": "XRPL Credential accepted by subject. CredentialType: OpenKYCAMLCredential. lsfAccepted = true."
      }]
    }
  }
}
```

### Step 4 — Authorise holder for MPT

After credential is accepted, submit `MPTokenAuthorize`:

```json
{
  "TransactionType": "MPTokenAuthorize",
  "Account": "rMPTIssuerAccountAddress",
  "MPTokenIssuanceID": "00070c44695f6d5468420c16ef71b6f1a27c8b0042a1ff00",
  "MPTokenHolder": "rCustomerAccountAddress"
}
```

Update OpenKYCAML:

```json
{
  "kycProfile": {
    "isEligible": true,
    "eligibilityLastConfirmed": "2026-04-01",
    "blockchainAccountIds": [{
      "address": "rCustomerAccountAddress",
      "network": "xrpl",
      "registeredAt": "2026-04-01",
      "xrplCredentialType": "4f70656e4b5943414d4c43726564656e7469616c",
      "mptIssuanceId": "00070c44695f6d5468420c16ef71b6f1a27c8b0042a1ff00"
    }]
  }
}
```

### Step 5 — Revoke on KYC expiry or sanctions hit

Submit `MPTokenAuthorize` with `tfMPTUnauthorize` flag (or `CredentialDelete`). Update OpenKYCAML:

```json
{
  "kycProfile": {
    "isEligible": false,
    "blockchainAccountIds": [{
      "address": "rCustomerAccountAddress",
      "network": "xrpl",
      "isFrozen": true
    }],
    "auditMetadata": {
      "changeLog": [{
        "eventType": "UPDATED",
        "eventDate": "2026-09-15T08:00:00Z",
        "changedBy": "rKYCIssuerAccountAddress",
        "details": "MPT authorisation revoked. Cause: sanctions screening match — OFAC SDN. lsfMPTAuthorized = 0."
      }]
    }
  }
}
```

---

## 10. Standard Claim Topics for XRPL KYC/AML Gating

Analogous to ERC-3643's numeric claim topics (§3.1 in the ERC-3643 mapping), XRPL uses hex-encoded `CredentialType` strings. The following table provides a recommended mapping:

| Credential Use Case | Recommended `CredentialType` string | Hex encoding | OpenKYCAML `verifiableCredential.type[]` | OpenKYCAML `kycProfile` Fields |
|---|---|---|---|---|
| KYC identity verified | `KYCCredential` | `4b594343726564656e7469616c` | `["VerifiableCredential", "KYCCredential"]` | `kycProfile.kycCompletionDate`, `dueDiligenceRequirements` |
| AML screening clear | `AMLCredential` | `414d4c43726564656e7469616c` | `["VerifiableCredential", "AMLCredential"]` | `kycProfile.sanctionsScreening`, `adverseMedia` |
| Full OpenKYCAML record | `OpenKYCAMLCredential` | `4f70656e4b5943414d4c43726564656e7469616c` | `["VerifiableCredential", "OpenKYCAMLCredential"]` | All `ivms101.*` + `kycProfile.*` |
| Travel Rule attestation | `TravelRuleAttestation` | `54726176656c52756c654174746573746174696f6e` | `["VerifiableCredential", "TravelRuleAttestation"]` | `ivms101.*`, `verifiableCredential.issuer`, `credentialSubject.id` |
| Accredited investor | `AccreditedInvestorCredential` | `41636372656469746564496e766573746f7243726564656e7469616c` | `["VerifiableCredential", "AccreditedInvestorCredential"]` | `kycProfile.customerClassification.accreditedInvestor: true` |
| EDD completed | `EDDCredential` | `45444443726564656e7469616c` | `["VerifiableCredential", "EDDCredential"]` | `kycProfile.dueDiligenceType: "EDD"`, `sourceOfFundsWealthDetail`, `pepStatus` |

---

## 11. Regulatory Compliance Notes

### FATF Recommendation 16 — Travel Rule on XRPL

XRPL VASPs using the Travel Rule protocol (TRISA, TRP, or XRPL-native messaging) embed the OpenKYCAML `ivms101` block in their Travel Rule messages. The XRPL `Credential` object provides an on-ledger attestation that the Travel Rule message was assembled from a verified KYC record.

### MiCA Article 83 — Transfer of Crypto-Assets

MPT issuances with `lsfMPTRequireAuth` and credential-gated `DepositPreauth` implement MiCA Art. 83 obligations at the ledger level. The off-chain OpenKYCAML record provides the auditable CDD basis for each `MPTokenAuthorize` action.

### EU AMLR Art. 22(5) — Remote CDD via Electronic Means

An XRPL Credential anchoring an OpenKYCAML VC issued following an eIDAS 2.0 EUDI Wallet presentation (`kycProfile.onboardingChannel: "EUDI_WALLET"`) satisfies the Art. 22(5) high-assurance remote CDD standard. The on-ledger Credential is the machine-verifiable attestation; the off-chain OpenKYCAML VC is the full CDD record.

### AMLR Art. 56 — Record Keeping

The `kycProfile.auditMetadata` block (including `dataRetentionDate` and `changeLog[]`) provides the 5-year retention record mandated by AMLR Art. 56. XRPL `Credential` objects are persistent ledger entries that independently support the audit trail.

---

*Document version: v1.3.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*
*XRPL references: [XLS-40d Credentials](https://github.com/XRPLF/XRPL-Standards/discussions/136), [XLS-33d MPTs](https://github.com/XRPLF/XRPL-Standards/discussions/120), [did:xrpl](https://github.com/XRPLF/XRPL-Standards/discussions/140), [W3C VC DM v2.0](https://www.w3.org/TR/vc-data-model-2.0/), [W3C DID Core v1.0](https://www.w3.org/TR/did-core/)*
