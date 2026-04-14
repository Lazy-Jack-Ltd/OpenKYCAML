# OpenKYCAML ↔ XRPL Credentials, DIDs, and Multi-Purpose Tokens (MPTs) Mapping

This document maps every data point in the **XRP Ledger (XRPL) Credentials** standard (XLS-70), the **XRPL DID** method, and the **XRPL Multi-Purpose Token (MPT)** standard (XLS-33d) to the corresponding field in the OpenKYCAML schema. It also documents the on-ledger KYC/AML gating pipeline and concludes on schema coverage versus the need for extensions.

**XRPL sources used:**
- [XLS-70 — On-Chain Credentials (final published standard)](https://opensource.ripple.com/docs/xls-70-credentials) — `Credential` and `DID` ledger objects; `CredentialCreate`, `CredentialAccept`, `CredentialDelete` transactions; `DepositPreauth` with credential gating. Live on XRPL mainnet.
- [XLS-80 — Permissioned Domains](https://xrpl.org/docs/concepts/tokens/decentralized-exchange/permissioned-domains) — controlled access environments for Permissioned DEXes and lending protocols
- [XLS-81d — Permissioned DEX](https://xrpl.org/docs/concepts/tokens/decentralized-exchange/permissioned-dex) — DEX offer matching restricted to domain members
- [XLS-33d — Multi-Purpose Tokens](https://github.com/XRPLF/XRPL-Standards/discussions/120) — `MPTIssuance` and `MPToken` ledger objects; `MPTokenIssuanceCreate`, `MPTokenIssuanceDestroy`, `MPTokenAuthorize`, `MPTokenIssuanceSet` transactions
- [XLS-77 — Deep Freeze](https://github.com/XRPLF/XRPL-Standards/discussions/200) — enhanced freeze enforcement for XRPL assets
- [XLS-96 — Confidential Transfers for Multi-Purpose Tokens](https://github.com/XRPLF/XRPL-Standards/discussions/220) — EC-ElGamal + ZKP encrypted balances with selective disclosure
- [XRPL DID Method Specification](https://github.com/XRPLF/XRPL-Standards/discussions/140) (`did:xrpl`) — on-ledger `DID` object, DID Document resolution, verification methods
- [W3C Verifiable Credentials Data Model v2.0](https://www.w3.org/TR/vc-data-model-2.0/)
- [W3C Decentralized Identifiers (DIDs) v1.0](https://www.w3.org/TR/did-core/)

**Coverage legend:**
- ✅ Full coverage — field exists in OpenKYCAML schema
- 🔄 Conceptual mapping — equivalent concept captured differently (see notes)
- ⭐ Schema extended — field added to OpenKYCAML to close the gap
- ℹ️ Out of scope — on-ledger / runtime state not applicable to an off-chain KYC record

---

## 1. Architecture Overview

XRPL's compliance infrastructure combines multiple on-ledger primitives that together deliver credential-gated permissioned tokens — a strong parallel to the ERC-3643 pattern already mapped in OpenKYCAML:

| XRPL Component | Purpose | OpenKYCAML Equivalent |
|---|---|---|
| **`Credential` object** (XLS-70) | On-ledger anchor for a W3C VC: binds `Subject` account + `Issuer` account + `CredentialType` + optional `URI` pointing to the off-chain VC payload | `verifiableCredential` wrapper — the OpenKYCAML VC is the off-chain content that `URI` references |
| **`DID` object** (XLS-70) | On-ledger DID Document stub for `did:xrpl:<network>:<account>`; holds key material or a `URI` to the full DID Document | `verifiableCredential.issuer`, `verifiableCredential.credentialSubject.id`, and `verifiableCredential.evidence[].credentialIssuer` — all expressed as DIDs |
| **Permissioned Domain** (XLS-80) | On-ledger controlled environment that restricts access to DEXes and lending protocols to verified members; requires specified credential types | `kycProfile.blockchainAccountIds[].xrplPermissionedDomainId` ⭐ + `xrplAuthorizedCredentialTypes[]` ⭐ |
| **Permissioned DEX** (XLS-81d) | DEX offer matching restricted to members of a Permissioned Domain; builds on XLS-80 | `kycProfile.isEligible` + `kycProfile.blockchainAccountIds[].xrplPermissionedDomainId` ⭐ |
| **`MPTIssuance` object** (XLS-33d) | Permissioned token issuance with optional `lsfMPTRequireAuth` gate; holder accounts must be individually authorised by the issuer | `kycProfile.isEligible` + `kycProfile.blockchainAccountIds[]` — off-chain eligibility and wallet registration |
| **`MPToken` object** (XLS-33d) | Per-holder token balance with `lsfMPTAuthorized` flag | `kycProfile.isEligible`, `kycProfile.blockchainAccountIds[].isFrozen` |
| **Confidential Transfer** (XLS-96) | EC-ElGamal + ZKP encrypted MPT balances; selective disclosure keys for auditors/regulators | `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer` ⭐ |
| **Deep Freeze** (XLS-77) | Enhanced freeze preventing token receipt even without issuer release | `kycProfile.blockchainAccountIds[].xrplFreezeType: "DEEP_FREEZE"` ⭐ |
| **Native Clawback** | Issuer can claw back tokens from any holder (XRPL Clawback amendment) | `kycProfile.blockchainAccountIds[].xrplClawbackEnabled` ⭐ |
| **`DepositPreauth` with credentials** (XLS-70) | Account-level deposit gate: only senders holding a specified `{Issuer, CredentialType}` credential may pay to the account | `kycProfile.isEligible` + `verifiableCredential.type[]` — off-chain pre-authorisation record |

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
7. (Optional) Permissioned Domain gate (XLS-80/81):
      Domain owner adds credential type requirement to domain
      Customer's xrplPermissionedDomainId is set in OpenKYCAML
      Customer can now trade on Permissioned DEX within the domain
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
| `validUntil` / `expirationDate` | `Expiration` (Ripple epoch seconds) | `verifiableCredential.validUntil` (ISO 8601) | ✅ Convert: Ripple epoch = Unix epoch − 946684800 |
| `type[]` — credential type | `CredentialType` (1–64 bytes hex-encoded) | `verifiableCredential.type[]` (string array) | 🔄 See §2.2 |
| `proof` — cryptographic proof | Validated by XRPL ledger consensus; `Issuer` account signature | `verifiableCredential.proof` (Ed25519Signature2020 / JWS) | 🔄 XRPL ledger consensus replaces the VC `proof` for on-ledger anchors; the off-chain VC retains its own `proof` |
| `credentialStatus` — revocation | `CredentialDelete` transaction removes the on-ledger credential | `verifiableCredential.credentialStatus` (StatusList2021Entry) | 🔄 On-ledger deletion is the XRPL revocation mechanism; off-chain `credentialStatus` is retained for VC-native verification flows |
| `validFrom` | Not a distinct field (block close-time of `CredentialCreate` tx) | `verifiableCredential.validFrom` | ✅ Store block close-time as `validFrom` in the off-chain VC |
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

The `Credential` ledger object (XLS-70) stores the on-ledger metadata for a W3C VC whose payload lives off-chain.

| XRPL `Credential` Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `Subject` | XRPL account address | The credential holder | `verifiableCredential.credentialSubject.id` | In OpenKYCAML, expressed as `did:xrpl:1:<Subject>`. The XRPL r-address is the last part of the DID. |
| `Issuer` | XRPL account address | The credential issuer | `verifiableCredential.issuer.id` | In OpenKYCAML, expressed as `did:xrpl:1:<Issuer>`. |
| `CredentialType` | hex (1–64 bytes) | Type identifier for the credential (e.g. `4b5943` = `KYC`) | `verifiableCredential.type[]` | See §2.2 for hex ↔ string mapping. The W3C VC `type[]` array carries the human-readable equivalent. |
| `URI` | hex (optional, ≤ 256 bytes) | URI of the off-chain VC payload | `verifiableCredential.id` | Set this to the canonical URI of the OpenKYCAML VC. Resolves to the full `verifiableCredential` block. |
| `Expiration` | UInt32 (Ripple epoch) | Credential expiry as seconds since 2000-01-01T00:00:00Z | `verifiableCredential.validUntil` | Convert: Unix timestamp = Ripple epoch + 946684800. |
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
| `Expiration` | `verifiableCredential.validUntil` | Convert ISO 8601 → Ripple epoch. |

### 4.2 DepositPreauth with Credential Gating

XRPL accounts with `lsfDepositAuth` can specify `AuthorizedCredentials` — only senders holding a matching credential may deposit.

| `DepositPreauth` / `AuthorizedCredentials` Field | Description | OpenKYCAML Field | Notes |
|---|---|---|---|
| `Issuer` | Address of the trusted credential issuer | `verifiableCredential.issuer.id` (as DID) | The relying party trusts credentials issued by this XRPL account. |
| `CredentialType` | Hex type the sender must hold | `verifiableCredential.type[]` | Must match the `CredentialType` set on the sender's `Credential` object. |
| Evaluation: sender holds `lsfAccepted` credential | Whether the sender's `Credential` object exists, is accepted, and is not expired | `kycProfile.isEligible: true` | `isEligible` is the off-chain record of the same determination. |

---

## 5. XLS-80: Permissioned Domains

Permissioned Domains (XLS-80) are controlled environments within the XRPL that allow financial institutions to restrict access to DEXes, lending protocols, and other services to verified, compliant participants. A domain is an on-ledger object owned by the domain operator (e.g. an asset manager or regulated exchange) that defines which credential types a wallet must hold before being permitted to interact with domain-gated functionality.

### 5.1 Domain Architecture

```
Domain Operator (rDomainOwner)
    creates PermissionedDomain object on-ledger
    specifies AuthorizedCredentials = [
      {Issuer: rKYCIssuer, CredentialType: hex("KYCCredential")},
      {Issuer: rKYCIssuer, CredentialType: hex("AMLCredential")}
    ]

Customer (rCustomer) must hold BOTH credentials (issued + accepted)
    → gains access to Permissioned DEX within the domain
    → can interact with lending protocols scoped to this domain
```

### 5.2 Permissioned Domain → OpenKYCAML Mapping

| XRPL Permissioned Domain Concept | OpenKYCAML Field | Notes |
|---|---|---|
| `PermissionedDomainID` (Hash256 of domain object) | `kycProfile.blockchainAccountIds[].xrplPermissionedDomainId` ⭐ (added v1.7.0) | 64-char hex Hash256. Links the investor's wallet to the specific domain gate. |
| Required credential types for domain membership | `kycProfile.blockchainAccountIds[].xrplAuthorizedCredentialTypes[]` ⭐ (added v1.7.0) | Array of hex `CredentialType` strings satisfied by this wallet in this domain. Cross-references `xrplCredentialType`. |
| Domain membership eligibility | `kycProfile.isEligible: true` | `isEligible` is the off-chain record of domain admission; the domain itself enforces it on-ledger via credential checks. |
| Domain-scoped investor country restriction | `ivms101.originator.originatorPersons[].naturalPerson.countryOfResidence` | Domain operators may configure country-level restrictions; the investor's country in OpenKYCAML is the authoritative source. |

### 5.3 Integration: Linking an OpenKYCAML Record to a Permissioned Domain

```json
{
  "kycProfile": {
    "isEligible": true,
    "blockchainAccountIds": [{
      "address": "rCustomerAccountAddress",
      "network": "xrpl",
      "xrplCredentialType": "4b594343726564656e7469616c",
      "xrplPermissionedDomainId": "A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2",
      "xrplAuthorizedCredentialTypes": [
        "4b594343726564656e7469616c",
        "414d4c43726564656e7469616c"
      ]
    }]
  }
}
```

---

## 6. XLS-81d: Permissioned DEX

The Permissioned DEX (XLS-81d) restricts DEX offer matching to members of a Permissioned Domain (XLS-80). Only wallets that are registered within the domain and hold all required credential types can place or fill offers on the Permissioned DEX. This enables regulated financial institutions to operate compliant secondary markets on XRPL.

### 6.1 How Domain Membership Gates DEX Access

```
Standard XRPL DEX:  any account can trade
Permissioned DEX:   OfferCreate with domain flag → only domain members can match

Domain membership = wallet holds all required {Issuer, CredentialType} credentials
                    in lsfAccepted state, and is not expired
```

### 6.2 Authorised Trustlines and Permissioned DEX

The Permissioned DEX system works alongside XRPL's **Authorised Trustlines** mechanism (IssuerAuthorizesTrustline). Together they provide two independent compliance gates:

| Mechanism | Gate | OpenKYCAML Enforcement Field |
|---|---|---|
| **Authorised Trustline** (issuer sets `RequireAuth` on account) | Issuer must explicitly authorise each trustline before the holder can receive the asset | `kycProfile.isEligible: true` → triggers `TrustSet` auth by issuer |
| **Permissioned Domain membership** (XLS-80) | Wallet must hold all domain-required credentials | `kycProfile.blockchainAccountIds[].xrplPermissionedDomainId` + `xrplAuthorizedCredentialTypes[]` |
| **Permissioned DEX offer matching** (XLS-81d) | Both taker and maker must be domain members | `kycProfile.isEligible: true` + `xrplPermissionedDomainId` set on both wallets |

When a VASP processes a secondary market trade on a Permissioned DEX, it should verify that both parties have an OpenKYCAML record with:
- `isEligible: true`
- `xrplPermissionedDomainId` matching the domain governing that DEX
- `xrplAuthorizedCredentialTypes[]` containing all types required by the domain

This dual-gate model is the XRPL equivalent of ERC-3643's combined `IIdentityRegistry.isVerified()` + `ICompliance.canTransfer()` check.

---

## 7. MPTIssuance Object (Permissioned Token)

The `MPTIssuance` object (XLS-33d) is the XRPL equivalent of an ERC-3643 security token with `lsfMPTRequireAuth` as the permissioning gate.

| `MPTIssuance` Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `Issuer` | XRPL account | Token issuer | `verifiableCredential.issuer.id` (as DID) | The MPT issuer is typically the VASP or asset manager who also issues the KYC credential, or relies on a trusted KYC issuer DID. |
| `MPTokenIssuanceID` | Hash192 | Unique on-ledger identifier for the issuance | `kycProfile.blockchainAccountIds[].mptIssuanceId` ⭐ | Added v1.3.0. 48-char hex. |
| `AssetScale` | UInt8 | Decimal scaling factor (analogous to ERC-20 `decimals`) | ℹ️ Token metadata, not investor KYC | |
| `MaximumAmount` | UInt64 (optional) | Maximum token supply | ℹ️ Token metadata | |
| `TransferFee` | UInt16 (optional) | Transfer fee in millionths | `kycProfile.blockchainAccountIds[].mptTransferFee` ⭐ | Added v1.7.0. Records the per-issuance fee for fee-aware compliance calculations. |
| `MPTokenMetadata` | hex (≤ 1024 bytes) | Issuer-defined token metadata (e.g. ISIN, asset class, compliance URI) | `kycProfile.blockchainAccountIds[].mptMetadata` ⭐ | Added v1.7.0. Mirrors the 'compliance rules in token' pattern: issuers embed metadata (ISIN, prospectus URI, asset class) directly in the token at the protocol level. |
| `Flags: lsfMPTRequireAuth` | bool | Holders must be individually authorised before receiving tokens | `kycProfile.isEligible` | If `true`, the issuer must submit `MPTokenAuthorize` for each holder. `isEligible: true` is the off-chain prerequisite. |
| `Flags: lsfMPTCanTransfer` | bool | Whether MPTs can be transferred between non-issuer accounts | `kycProfile.dueDiligenceType` + `kycProfile.isEligible` | If `false`, only the issuer can move tokens (primary issuance model). |
| `Flags: lsfMPTCanClawback` | bool | Whether the issuer can claw back tokens from any holder | `kycProfile.blockchainAccountIds[].xrplClawbackEnabled` ⭐ | Added v1.7.0. Records clawback capability; `isFrozen` records current state. |
| `Flags: lsfMPTLocked` | bool | Whether the entire MPT issuance is locked (paused) | ℹ️ Token-level state, not investor-level | |
| All MPTIssuance flags (bitmask) | UInt32 | Composite compliance configuration of the issuance | `kycProfile.blockchainAccountIds[].mptFlags` ⭐ | Added v1.7.0. Enables downstream systems to derive the applicable compliance enforcement model without querying the ledger. |

### 7.1 MPT Flags Reference

| Flag | Bit | Meaning | OpenKYCAML Implication |
|---|---|---|---|
| `lsfMPTCanLock` | 0x0002 | Individual holder balances can be frozen | `isFrozen` / `xrplFreezeType` fields are applicable |
| `lsfMPTRequireAuth` | 0x0004 | Holders must be individually authorised | `isEligible: true` is the off-chain prerequisite |
| `lsfMPTCanEscrow` | 0x0008 | Tokens can be placed in escrow | Record escrow events in `auditMetadata.changeLog[]` |
| `lsfMPTCanTrade` | 0x0010 | Tokens are tradeable (including on Permissioned DEX) | `xrplPermissionedDomainId` gates domain-scoped trading |
| `lsfMPTCanTransfer` | 0x0020 | Tokens can transfer between non-issuer accounts | Both parties need `isEligible: true` for peer transfers |
| `lsfMPTCanClawback` | 0x0040 | Issuer can claw back tokens | `xrplClawbackEnabled: true` on the wallet entry |

---

## 8. MPToken Object (Holder Authorisation)

The `MPToken` object is the per-holder state in an MPT issuance. `lsfMPTAuthorized` is the on-ledger gate that is directly driven by the KYC outcome.

| `MPToken` Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `Account` | XRPL address | The token holder | `kycProfile.blockchainAccountIds[].address` | Use `network: "xrpl"` (or CAIP-2 equivalent `xrpl:1` for mainnet). |
| `MPTokenIssuanceID` | Hash192 | Which MPT issuance this balance belongs to | `kycProfile.blockchainAccountIds[].mptIssuanceId` ⭐ | 48-char hex, added v1.3.0. |
| `MPTokenAmount` | UInt64 | Current balance | ℹ️ Token balance, not KYC data | Live on-chain state. |
| `Flags: lsfMPTAuthorized` | bool | Whether the issuer has authorised this holder via `MPTokenAuthorize` | `kycProfile.isEligible` | Direct equivalent: `isEligible: true` ↔ `lsfMPTAuthorized = 1`. Set by the issuer after KYC/AML completion. `kycProfile.eligibilityLastConfirmed` stores the date. |
| `Flags: lsfMPTLocked` | bool | Whether this specific holder's tokens are locked | `kycProfile.blockchainAccountIds[].isFrozen` | Per-holder freeze maps to `isFrozen: true` on the matching `blockchainAccountIds[]` entry. |

### 8.1 MPTokenAuthorize Transaction

| `MPTokenAuthorize` Field | Description | OpenKYCAML Field | Notes |
|---|---|---|---|
| `Account` (Issuer action) | Issuer grants or revokes holder authorisation | `verifiableCredential.issuer.id` | Issuer acts after verifying the OpenKYCAML KYC payload. |
| `MPTokenHolder` | Holder's XRPL address | `kycProfile.blockchainAccountIds[].address` | The address receiving authorisation. |
| `Flags: tfMPTUnauthorize` | Revokes authorisation | `kycProfile.isEligible: false` | After revocation, update `isEligible: false` and add a `changeLog` entry. |

---

## 9. XLS-77: Deep Freeze and XRPL Native Clawback

XRPL provides native protocol-level enforcement for freezing and clawback that is more powerful than the standard `isFrozen` boolean. This section maps these capabilities to the comparison table with ERC-3643's `forcedTransfer()` and `setAddressFrozen()`.

### 9.1 Freeze Hierarchy

| Freeze Level | XRPL Mechanism | `xrplFreezeType` Value | ERC-3643 Equivalent | OpenKYCAML Fields |
|---|---|---|---|---|
| **Individual Freeze** | Issuer freezes a single trustline or MPToken holding (`TrustSet tf_SetFreeze` or `MPTokenIssuanceSet` lock flag) | `"INDIVIDUAL_FREEZE"` | `setAddressFrozen(address, true)` | `isFrozen: true`, `xrplFreezeType: "INDIVIDUAL_FREEZE"` ⭐ |
| **Global Freeze** | Issuer freezes all trustlines for an issued currency (`AccountSet tf_SetGlobalFreeze`) | `"GLOBAL_FREEZE"` | Token-wide `paused` state | `isFrozen: true`, `xrplFreezeType: "GLOBAL_FREEZE"` ⭐ |
| **Deep Freeze** (XLS-77) | Enhanced freeze: holder cannot receive tokens or transfer frozen funds even after freeze is lifted without issuer action; stronger enforcement for regulated securities | `"DEEP_FREEZE"` | No direct equivalent (stronger than `setAddressFrozen`) | `isFrozen: true`, `xrplFreezeType: "DEEP_FREEZE"` ⭐ |

### 9.2 Native Clawback

| XRPL Mechanism | Description | OpenKYCAML Field | ERC-3643 Equivalent | Notes |
|---|---|---|---|---|
| **Clawback amendment** (`Clawback` transaction) | Issuer can reclaim tokens from any trustline holder by submitting a `Clawback` transaction specifying the holder and amount. Requires the issuer account to have `allowClawback` set on the token (opt-in during issuance). | `kycProfile.blockchainAccountIds[].xrplClawbackEnabled` ⭐ | `forcedTransfer(from, to, amount)` in T-REX | Added v1.7.0. When `true`, the issuer holds protocol-level clawback rights. Record actual clawback events in `auditMetadata.changeLog[]`. |
| **MPT Clawback** (`MPTokenIssuanceSet` with clawback flag) | MPT-specific clawback at the issuance level. Controlled by `lsfMPTCanClawback` flag on the `MPTIssuance` object. | `kycProfile.blockchainAccountIds[].xrplClawbackEnabled: true` + `mptFlags` including `lsfMPTCanClawback` (0x0040) | `forcedTransfer()` | Both `xrplClawbackEnabled` and `mptFlags` should reflect this capability. |

**Compliance note:** Clawback capability should be disclosed to investors at onboarding. Record the disclosure in `kycProfile.auditMetadata.changeLog[]` and in the applicable `consentRecord`.

---

## 10. XLS-96: Confidential Transfers for Multi-Purpose Tokens

XLS-96 encrypts MPT balances and transfer amounts using EC-ElGamal combined with Zero-Knowledge Proofs. Validators enforce supply limits and prevent double-spends without seeing actual amounts. Issuers and designated auditors hold decryption keys for selective disclosure.

### 10.1 Privacy and Regulatory Balance

| Capability | XLS-96 Mechanism | OpenKYCAML Implication |
|---|---|---|
| **Encrypted balances** | EC-ElGamal encryption of individual MPToken amounts | Issuer and auditor hold decryption keys; regulatory visibility requires selective disclosure |
| **ZKP supply enforcement** | Validators verify supply invariants using ZKPs without decryption | Validators can still enforce compliance rules without accessing PII |
| **Auditor disclosure** | Designated auditor holds a decryption key for all balances in the issuance | `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer.auditorPublicKey` ⭐ |
| **Regulator disclosure** | Regulators get visibility only when legally required via their decryption key | `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer.regulatorPublicKey` ⭐ |
| **Issuer visibility** | Issuers always retain decryption access for their own issuances | The issuer's key is managed off-chain; not stored in the KYC record |

### 10.2 XLS-96 → OpenKYCAML Field Mapping

| XLS-96 Concept | OpenKYCAML Field | Notes |
|---|---|---|
| Confidential transfer flag on `MPTIssuance` | `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer.enabled` ⭐ | `true` when the associated MPT issuance uses XLS-96 confidential transfers. Added v1.7.0. |
| Auditor EC public key | `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer.auditorPublicKey` ⭐ | Compressed EC public key (hex, 66 chars) of the designated auditor. |
| Regulator EC public key (optional) | `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer.regulatorPublicKey` ⭐ | Only populated when a regulatory authority holds decryption rights. |
| Encryption scheme | `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer.encryptionScheme` ⭐ | `"EC_ELGAMAL"` for XLS-96. Enum allows future schemes. |

### 10.3 GDPR and Privacy Notes

XLS-96 confidential transfers align well with GDPR data minimisation (Art. 5(1)(c)):
- Balance data is encrypted on-ledger — no third-party observer can correlate amounts to identities
- `gdprSensitivityMetadata.classification` should be `"sensitive_personal"` or higher when wallet holdings are linked to KYC identities under XLS-96
- Selective disclosure via `xrplConfidentialTransfer.regulatorPublicKey` corresponds to the lawful access mechanism under GDPR Art. 6(1)(c) (legal obligation) or Art. 9(2)(g) (substantial public interest)
- The ZKP proofs on the ledger do not constitute personal data — only the decryption keys and the off-chain OpenKYCAML payload do

### 10.4 Integration Example

```json
{
  "kycProfile": {
    "blockchainAccountIds": [{
      "address": "rCustomerAccountAddress",
      "network": "xrpl",
      "mptIssuanceId": "00070c44695f6d5468420c16ef71b6f1a27c8b0042a1ff00",
      "mptFlags": 68,
      "xrplConfidentialTransfer": {
        "enabled": true,
        "encryptionScheme": "EC_ELGAMAL",
        "auditorPublicKey": "02a7f4a1b3c9e8d6f2b4c5e7a9d1f3b5c7e9a2d4f6b8c0e2a4d6f8b0c2e4a6d8f0",
        "regulatorPublicKey": "03b8e5c2d4f6a8c0e2d4f6a8c0e2d4f6a8c0e2d4f6a8c0e2d4f6a8c0e2d4f6a8c1"
      }
    }],
    "gdprSensitivityMetadata": {
      "classification": "sensitive_personal",
      "legalBasis": "GDPR-Art6-1c"
    }
  }
}
```

---

## 11. KYC/AML Gating → OpenKYCAML Field Mapping

These are the per-investor KYC/AML data points that determine on-ledger gating decisions.

| KYC/AML Gate Requirement | XRPL Mechanism | OpenKYCAML Field | Notes |
|---|---|---|---|
| Identity verified (natural person) | `Credential` object with `CredentialType = KYC` (XLS-70) | `kycProfile.kycCompletionDate` + `kycProfile.dueDiligenceRequirements` | ✅ |
| AML screening passed | `Credential` object with `CredentialType = AML` | `kycProfile.sanctionsScreening.screeningStatus = CLEAR` + `kycProfile.adverseMedia.overallOutcome = CLEAR` | ✅ |
| Accredited / eligible investor | `Credential` with `CredentialType = AccreditedInvestor` | `kycProfile.customerClassification.accreditedInvestor: true` + `investorCategoryJurisdiction` | ✅ |
| Country restriction | `DepositPreauth` country check (via investor country in KYC) | `ivms101.originator.originatorPersons[].naturalPerson.countryOfResidence` | ✅ XRPL uses the off-chain KYC record to determine permissible jurisdictions |
| Not on sanctions list | `Credential` with AML type and screening result | `kycProfile.sanctionsScreening.screeningStatus` ≠ `MATCH` | ✅ |
| PEP status determined | EDD triggers elevated `CredentialType` requirement | `kycProfile.pepStatus.isPEP` + `kycProfile.dueDiligenceType = EDD` | ✅ |
| Source of funds verified | Custom credential type in high-risk issuances | `kycProfile.sourceOfFundsWealthDetail` | ✅ |
| Credential not expired | `Expiration` on `Credential` object (XLS-70) | `verifiableCredential.validUntil` | ✅ |
| Credential accepted by holder | `lsfAccepted` flag (XLS-70) | Record in `kycProfile.auditMetadata.changeLog[]` | 🔄 |
| Holder authorised for MPT | `lsfMPTAuthorized` on `MPToken` | `kycProfile.isEligible: true` + `kycProfile.eligibilityLastConfirmed` | ✅ |
| Holder wallet frozen | `lsfMPTLocked` on `MPToken` | `kycProfile.blockchainAccountIds[].isFrozen: true` | ✅ |
| XRPL on-ledger credential type (for cross-reference) | `Credential.CredentialType` (hex) (XLS-70) | `kycProfile.blockchainAccountIds[].xrplCredentialType` ⭐ | ✅ v1.3.0+ — stores hex CredentialType for round-trip XRPL reconstruction |
| MPT issuance identifier (multi-issuance) | `MPToken.MPTokenIssuanceID` | `kycProfile.blockchainAccountIds[].mptIssuanceId` ⭐ | ✅ v1.3.0+ — stores Hash192 MPTokenIssuanceID for multi-pool eligibility tracking |
| Permissioned Domain membership (XLS-80) | `PermissionedDomainID` + credential gate | `kycProfile.blockchainAccountIds[].xrplPermissionedDomainId` ⭐ + `xrplAuthorizedCredentialTypes[]` ⭐ | ✅ v1.7.0+ |
| Permissioned DEX access (XLS-81d) | Domain membership + credential gate | `kycProfile.isEligible: true` + `xrplPermissionedDomainId` ⭐ | ✅ v1.7.0+ |
| Deep Freeze enforcement (XLS-77) | `xrplFreezeType = DEEP_FREEZE` | `kycProfile.blockchainAccountIds[].xrplFreezeType` ⭐ | ✅ v1.7.0+ |
| Clawback enabled | Clawback amendment / `lsfMPTCanClawback` | `kycProfile.blockchainAccountIds[].xrplClawbackEnabled` ⭐ | ✅ v1.7.0+ |
| Confidential transfer configured (XLS-96) | `xrplConfidentialTransfer.enabled = true` | `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer` ⭐ | ✅ v1.7.0+ |
| MPT compliance flags | `MPTIssuance.Flags` bitmask | `kycProfile.blockchainAccountIds[].mptFlags` ⭐ | ✅ v1.7.0+ |
| MPT metadata / ISIN / prospectus | `MPTokenMetadata` | `kycProfile.blockchainAccountIds[].mptMetadata` ⭐ | ✅ v1.7.0+ |
| MPT transfer fee | `MPTIssuance.TransferFee` | `kycProfile.blockchainAccountIds[].mptTransferFee` ⭐ | ✅ v1.7.0+ |

---

## 12. Coverage Gap Summary

### 12.1 No schema changes required

The following XRPL-specific concepts are **fully covered** by existing OpenKYCAML fields without modification:

| XRPL Concept | Existing OpenKYCAML Coverage |
|---|---|
| `Credential.Subject` → DID | `verifiableCredential.credentialSubject.id` (DID-agnostic) |
| `Credential.Issuer` → DID | `verifiableCredential.issuer.id` (DID-agnostic) |
| `Credential.Expiration` | `verifiableCredential.validUntil` |
| `Credential.URI` → VC payload | `verifiableCredential.id` (canonical URI of the VC) |
| `did:xrpl` DID method | All DID fields are DID-method-agnostic; `did:xrpl:1:r...` is a valid value |
| DID triangulation (subject / KYC issuer / relying party) | `verifiableCredential.evidence[].credentialIssuer` + `.verifier` + `credentialSubject.id` |
| `MPToken.lsfMPTAuthorized` | `kycProfile.isEligible` |
| `MPToken.lsfMPTLocked` | `kycProfile.blockchainAccountIds[].isFrozen` |
| Holder XRPL wallet address | `kycProfile.blockchainAccountIds[].address` (`network: "xrpl"`) |
| Credential proof (ledger-validated) | `verifiableCredential.proof` (off-chain VC proof; ledger validation is additive) |
| Credential revocation | `verifiableCredential.credentialStatus` (StatusList2021Entry) + on-ledger `CredentialDelete` |
| Sanctions / AML screening | `kycProfile.sanctionsScreening`, `kycProfile.adverseMedia` |
| KYC completion | `kycProfile.kycCompletionDate`, `kycProfile.dueDiligenceRequirements` |
| Accredited investor | `kycProfile.customerClassification.accreditedInvestor` |
| Travel Rule (VASP-to-VASP) | `ivms101` block (IVMS 101 superset) |
| GDPR / SAR tipping-off | `gdprSensitivityMetadata` block |

### 12.2 Schema extensions added in v1.3.0 ⭐

| Field | Rationale | Pattern |
|---|---|---|
| `kycProfile.blockchainAccountIds[].xrplCredentialType` ⭐ | Hex CredentialType for round-trip XRPL reconstruction (XLS-70) | `^[0-9a-fA-F]{2,128}$` |
| `kycProfile.blockchainAccountIds[].mptIssuanceId` ⭐ | Hash192 MPTokenIssuanceID for multi-pool eligibility (XLS-33d) | `^[0-9a-fA-F]{48}$` |

### 12.3 Schema extensions added in v1.7.0 ⭐

| Field | XRPL Standard | Rationale |
|---|---|---|
| `kycProfile.blockchainAccountIds[].xrplPermissionedDomainId` ⭐ | XLS-80 | Links wallet to on-ledger domain gate (Hash256 hex, 64 chars) |
| `kycProfile.blockchainAccountIds[].xrplAuthorizedCredentialTypes[]` ⭐ | XLS-80 | Records which credential types are satisfied within the domain |
| `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer` ⭐ | XLS-96 | Carries auditor/regulator public keys and encryption scheme for selective disclosure |
| `kycProfile.blockchainAccountIds[].mptFlags` ⭐ | XLS-33d | Bitmask of MPTIssuance compliance configuration flags |
| `kycProfile.blockchainAccountIds[].mptMetadata` ⭐ | XLS-33d | ISIN, prospectus URI, or compliance metadata embedded in the MPT issuance |
| `kycProfile.blockchainAccountIds[].mptTransferFee` ⭐ | XLS-33d | Transfer fee in millionths (0–50000) |
| `kycProfile.blockchainAccountIds[].xrplFreezeType` ⭐ | XLS-77 | Granular freeze type: INDIVIDUAL_FREEZE / GLOBAL_FREEZE / DEEP_FREEZE |
| `kycProfile.blockchainAccountIds[].xrplClawbackEnabled` ⭐ | Clawback amendment | Whether the issuer holds protocol-level clawback rights (equivalent to ERC-3643 `forcedTransfer()`) |

All v1.7.0 extensions are **additive** — existing payloads without these fields remain fully valid.

---

## 13. Integration Guidance: OpenKYCAML → XRPL KYC/AML Gating Pipeline

### Step 1 — Issue the OpenKYCAML VC

Complete KYC/AML and issue the OpenKYCAML payload. Set:

```json
{
  "verifiableCredential": {
    "@context": [
      "https://www.w3.org/ns/credentials/v2",
      "https://openkycaml.org/contexts/v1"
    ],
    "id": "https://kyc.vasp.example/vc/550e8400-e29b-41d4-a716-446655440000",
    "type": ["VerifiableCredential", "OpenKYCAMLCredential", "KYCCredential"],
    "issuer": {
      "id": "did:xrpl:1:rKYCIssuerAccountAddress",
      "name": "VASP KYC Division"
    },
    "validFrom": "2026-04-01T12:00:00Z",
    "validUntil": "2027-04-01T12:00:00Z",
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
- `Expiration` = ISO 8601 `validUntil` converted to Ripple epoch (`Unix timestamp − 946684800`)

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
      "mptIssuanceId": "00070c44695f6d5468420c16ef71b6f1a27c8b0042a1ff00",
      "mptFlags": 36,
      "xrplPermissionedDomainId": "A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2",
      "xrplAuthorizedCredentialTypes": [
        "4f70656e4b5943414d4c43726564656e7469616c",
        "414d4c43726564656e7469616c"
      ]
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
      "isFrozen": true,
      "xrplFreezeType": "INDIVIDUAL_FREEZE"
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

## 14. Standard Claim Topics for XRPL KYC/AML Gating

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

## 15. Regulatory Compliance Notes

### FATF Recommendation 16 — Travel Rule on XRPL

XRPL VASPs using the Travel Rule protocol (TRISA, TRP, or XRPL-native messaging) embed the OpenKYCAML `ivms101` block in their Travel Rule messages. The XRPL `Credential` object (XLS-70) provides an on-ledger attestation that the Travel Rule message was assembled from a verified KYC record.

### MiCA Article 83 — Transfer of Crypto-Assets

MPT issuances with `lsfMPTRequireAuth` and credential-gated `DepositPreauth` implement MiCA Art. 83 obligations at the ledger level. The off-chain OpenKYCAML record provides the auditable CDD basis for each `MPTokenAuthorize` action. Permissioned Domain gating (XLS-80/81d) provides an additional compliance layer for secondary market trading.

### EU AMLR Art. 22(5) — Remote CDD via Electronic Means

An XRPL Credential (XLS-70) anchoring an OpenKYCAML VC issued following an eIDAS 2.0 EUDI Wallet presentation (`kycProfile.onboardingChannel: "EUDI_WALLET"`) satisfies the Art. 22(5) high-assurance remote CDD standard. The on-ledger Credential is the machine-verifiable attestation; the off-chain OpenKYCAML VC is the full CDD record.

### AMLR Art. 56 — Record Keeping

The `kycProfile.auditMetadata` block (including `dataRetentionDate` and `changeLog[]`) provides the 5-year retention record mandated by AMLR Art. 56. XRPL `Credential` objects are persistent ledger entries that independently support the audit trail.

### Confidential Transfers and GDPR

XLS-96 confidential transfers encrypt balance data on-ledger. The `xrplConfidentialTransfer` fields in OpenKYCAML record the selective disclosure keys that allow auditors and regulators to access balance data consistent with GDPR Art. 6(1)(c) legal obligation requirements and AMLR audit requirements.

---

*Document version: v1.12.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*
*XRPL references: [XLS-70 Credentials](https://opensource.ripple.com/docs/xls-70-credentials), [XLS-80 Permissioned Domains](https://xrpl.org/docs/concepts/tokens/decentralized-exchange/permissioned-domains), [XLS-33d MPTs](https://github.com/XRPLF/XRPL-Standards/discussions/120), [XLS-96 Confidential Transfers](https://github.com/XRPLF/XRPL-Standards/discussions/220), [XLS-77 Deep Freeze](https://github.com/XRPLF/XRPL-Standards/discussions/200), [did:xrpl](https://github.com/XRPLF/XRPL-Standards/discussions/140), [W3C VC DM v2.0](https://www.w3.org/TR/vc-data-model-2.0/), [W3C DID Core v1.0](https://www.w3.org/TR/did-core/)*
