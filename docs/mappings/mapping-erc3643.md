# OpenKYCAML ↔ ERC-3643 (T-REX) Mapping

This document maps every data point in the **ERC-3643 (T-REX)** standard — including the underlying **ONCHAINID** identity model (ERC-734 Key Holder + ERC-735 Claim Holder) — to the corresponding field in the OpenKYCAML schema. It also identifies the few fields that required schema extensions to achieve full coverage.

**ERC-3643 sources used:**
- [EIP-3643 specification](https://github.com/TokenySolutions/EIP3643/blob/main/eip-3643.md)
- `IIdentityRegistry.sol`, `IIdentityRegistryStorage.sol`, `ITrustedIssuersRegistry.sol`, `IClaimTopicsRegistry.sol`, `IERC3643.sol`, `ICompliance.sol`
- ONCHAINID: `IERC734.sol` (Key Holder), `IERC735.sol` (Claim Holder)

**Coverage legend:**
- ✅ Full coverage — field exists in OpenKYCAML schema
- 🔄 Conceptual mapping — equivalent concept captured differently (see notes)
- ⭐ Schema extended — field added to OpenKYCAML v1.2.0 to close the gap
- ℹ️ Out of scope — on-chain / runtime state not applicable to an off-chain KYC record

---

## 1. Architecture Overview

ERC-3643 is an **on-chain permissioned token standard** for security tokens. It separates token transfer logic from investor identity management through a suite of six smart contracts:

| ERC-3643 Component | Purpose | OpenKYCAML Equivalent |
|---|---|---|
| **IERC3643** (Token contract) | Permissioned ERC-20 with transfer rules, freeze, mint/burn, recovery | ℹ️ Token-level — OpenKYCAML covers investor KYC, not the token contract itself |
| **IIdentityRegistry** | Links wallet addresses to ONCHAINID contracts and country codes; `isVerified()` gate | `kycProfile.isEligible` + `kycProfile.blockchainAccountIds[]` |
| **IIdentityRegistryStorage** | Persists the wallet → identity mapping on-chain | `kycProfile.blockchainAccountIds[]` |
| **ICompliance** | Enforces transfer rules (country limits, holder caps, max per wallet) | `kycProfile.dueDiligenceType` + `kycProfile.monitoringInfo`; transfer rules are off-chain in OpenKYCAML |
| **ITrustedIssuersRegistry** | Whitelist of claim issuers authorised to issue specific claim topics | `verifiableCredential.evidence[].credentialIssuer` |
| **IClaimTopicsRegistry** | Required claim topic IDs for investors holding the token | `kycProfile.dueDiligenceRequirements.verifiedAttributes[]` |

The identity of each investor is an **ONCHAINID** smart contract (ERC-734/735), which stores cryptographic keys and signed claims. OpenKYCAML represents the same identity data as a structured JSON record with an optional W3C Verifiable Credential wrapper.

---

## 2. Identity Registry: Investor Data Points

These are the per-investor fields stored in the ERC-3643 Identity Registry.

| ERC-3643 Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `investorAddress` | `address` (20 bytes) | Ethereum wallet address of the investor — the primary key in the registry | `kycProfile.blockchainAccountIds[].address` ⭐ | OpenKYCAML adds `blockchainAccountIds[]` array to support multi-wallet and multi-chain. Use CAIP-2 `network` field to specify chain. |
| `identity` (ONCHAINID) | `IIdentity` (contract address) | Address of the investor's ONCHAINID ERC-734/735 contract | `kycProfile.blockchainAccountIds[].onchainIDAddress` ⭐ | Stored per wallet entry. In DID-based flows, the ONCHAINID resolves to the same identity as `verifiableCredential.credentialSubject.id`. |
| `investorCountry` | `uint16` (ISO 3166-1 numeric) | Investor's country of residence (numeric code, e.g. 276 = DE) | `ivms101.originator.originatorPersons[].naturalPerson.geographicAddresses[].country` | OpenKYCAML uses ISO 3166-1 **alpha-2** strings (e.g. `"DE"`). Conversion: numeric ↔ alpha-2 is 1:1 via ISO 3166-1 table. |
| `isVerified(address)` | `bool` | Whether the investor's ONCHAINID holds all required claims from trusted issuers | `kycProfile.isEligible` ⭐ | Direct boolean equivalent. Set by the obliged entity after completing KYC/AML and confirming all required claim topics are satisfied. |
| `contains(address)` | `bool` | Whether the wallet is registered in this Identity Registry | Implied by presence of `kycProfile.blockchainAccountIds[]` entry | An entry in `blockchainAccountIds[]` with `onchainIDAddress` set implies the wallet is registered. |
| Registration event timestamp | (block timestamp) | When the identity was registered | `kycProfile.blockchainAccountIds[].registeredAt` ⭐ | ISO 8601 date stored off-chain. |
| Eligibility confirmed date | (derived) | When `isVerified()` was last evaluated as `true` | `kycProfile.eligibilityLastConfirmed` ⭐ | New field added to pair with `isEligible`. |

---

## 3. ONCHAINID: Claims (ERC-735)

Each claim is an attestation stored in the investor's ONCHAINID contract. Claims implement the ERC-735 Claim Holder interface.

| ERC-735 Claim Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `claimId` | `bytes32` | `keccak256(abi.encode(issuer, topic))` — unique claim identifier | `verifiableCredential.id` | W3C VC `id` serves as the unique credential identifier. |
| `topic` | `uint256` | Numeric claim category (1=KYC, 2=AML, 3=Country, 101=Accredited, etc.) | `verifiableCredential.type[]` | VC `type` array serves the same role: `["VerifiableCredential", "KYCCredential"]`. See claim topic table §3.1 below. |
| `scheme` | `uint256` | Signature scheme (1=ECDSA, 2=RSA, 3=Contract) | `verifiableCredential.proof.type` | `1` → `EcdsaSecp256k1Signature2019`; `2` → `RsaSignature2018`; W3C VC proof type covers the same information. |
| `issuer` | `address` | Ethereum address of the IClaimIssuer contract | `verifiableCredential.issuer` | In OpenKYCAML, the issuer is expressed as a DID URI (e.g. `did:ebsi:...`). The DID resolves to the same Ethereum address where applicable. |
| `signature` | `bytes` | `keccak256(abi.encode(identityAddress, topic, data))` signed by issuer key | `verifiableCredential.proof.proofValue` or `verifiableCredential.proof.jws` | JWS or DataIntegrityProof compact serialisation of the equivalent W3C VC proof. |
| `data` | `bytes` | ABI-encoded claim payload (actual identity data) | Various `ivms101.*` and `kycProfile.*` fields | ERC-735 stores raw bytes; OpenKYCAML stores structured JSON. See claim topic mapping §3.1 below. |
| `uri` | `string` | Off-chain reference URI for the claim | `verifiableCredential.credentialSchema.id` or `kycProfile.auditMetadata.changeLog[].details` | Provides a resolvable off-chain reference. |
| `getClaimIdsByTopic(topic)` | `bytes32[]` | All claim IDs for a given topic | `verifiableCredential.type[]` filtered by type | Query pattern; no direct JSON field. |

### 3.1 Standard T-REX Claim Topic → OpenKYCAML Field Mapping

| Claim Topic | Topic ID | Description | OpenKYCAML Field(s) |
|---|---|---|---|
| **KYC** | 1 | Know Your Customer identity verification completed | `kycProfile.kycCompletionDate`, `kycProfile.dueDiligenceRequirements`, `kycProfile.onboardingChannel`, `kycProfile.auditMetadata` |
| **AML** | 2 | Anti-Money Laundering check passed | `kycProfile.sanctionsScreening`, `kycProfile.adverseMedia`, `kycProfile.monitoringInfo` |
| **Country** | 3 | Investor country of residence / jurisdiction | `ivms101.originator.originatorPersons[].naturalPerson.countryOfResidence`, `ivms101.*.geographicAddresses[].country` |
| **Age 18+** | 10 | Investor is 18 years or older | `ivms101.originator.originatorPersons[].naturalPerson.dateAndPlaceOfBirth.dateOfBirth` (derive age from DOB) |
| **Accredited / Eligible Investor** | 101 | Investor qualifies as accredited (US), professional (MiFID II), or otherwise eligible to hold the security token | `kycProfile.customerClassification.accreditedInvestor` ⭐ + `kycProfile.customerClassification.investorCategoryJurisdiction` ⭐ |
| **Blacklist** | 1023 | Investor is on a watch/blacklist | `kycProfile.sanctionsScreening.screeningStatus` = `MATCH` + `kycProfile.sanctionsScreening.hits[]` |
| **KYC Expiry** | 2023 | Expiry date of KYC validity | `kycProfile.monitoringInfo.nextReviewDate` + `kycProfile.eligibilityLastConfirmed` |
| **Source of Funds** | Custom (varies) | Verified source of funds/wealth | `kycProfile.sourceOfFundsWealthDetail` |
| **PEP Status** | Custom (varies) | Politically Exposed Person determination | `kycProfile.pepStatus.isPEP` + `kycProfile.pepStatus.pepCategory` |
| **Beneficial Ownership** | Custom (varies) | UBO information verified | `kycProfile.beneficialOwnership[]` |

---

## 4. ONCHAINID: Keys (ERC-734)

Each key represents a cryptographic key attached to the ONCHAINID contract for key management and claim signing.

| ERC-734 Key Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `key` | `bytes32` | `keccak256(abi.encode(publicKey))` — key identifier | `verifiableCredential.proof.verificationMethod` | The W3C DID `verificationMethod` URI resolves to the equivalent public key. |
| `purpose` (1 = Management) | `uint256` | Key can manage other keys and execute operations | `verifiableCredential.issuer` (DID controller) | The DID controller key corresponds to ERC-734 purpose 1. |
| `purpose` (2 = Action) | `uint256` | Key can execute actions on behalf of the identity | ℹ️ Not represented — execution keys are on-chain only | |
| `purpose` (3 = Claim) | `uint256` | Key can sign claims (issue attestations) | `verifiableCredential.proof.verificationMethod` | The VC proof `verificationMethod` references the claim-signing key. |
| `purpose` (4 = Encryption) | `uint256` | Key for encryption | ℹ️ Not represented — encryption key management is out of scope | |
| `keyType` (1 = ECDSA) | `uint256` | ECDSA key | `verifiableCredential.proof.type` = `EcdsaSecp256k1Signature2019` | |
| `keyType` (2 = RSA) | `uint256` | RSA key | `verifiableCredential.proof.type` = `RsaSignature2018` | |

---

## 5. Trusted Issuers Registry

Per-token registry of claim issuers authorised to issue specific claim topics.

| ERC-3643 Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `trustedIssuer` | `IClaimIssuer` (address) | ONCHAINID address of the trusted issuer's contract | `verifiableCredential.evidence[].credentialIssuer` | In OpenKYCAML, each evidence entry records the DID of the credential issuer. |
| `claimTopics` | `uint[]` | Claim topics this issuer is authorised to emit | `verifiableCredential.type[]` | VC type array scopes the claims. No explicit claim topic number field — see §3.1 for topic→type mapping. |
| `isTrustedIssuer(address)` | `bool` | Whether an issuer is trusted | Implied by `verifiableCredential.issuer` matching a known trusted issuer DID | The issuer's DID is the off-chain equivalent of the trusted issuer address. |

---

## 6. Claim Topics Registry

Per-token list of claim topics that investors must hold valid claims for.

| ERC-3643 Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `claimTopics` | `uint256[]` | Required claim topic IDs | `kycProfile.dueDiligenceRequirements.verifiedAttributes[]` | Each verified attribute corresponds to a claim topic. See §3.1 for mapping. |
| `getClaimTopics()` | `uint256[]` | Returns all required topics | `kycProfile.dueDiligenceRequirements.verifiedAttributes[]` + `kycProfile.dueDiligenceType` | The DD tier determines which claim topics are required (SDD = topics 1+3; CDD = 1+2+3; EDD = 1+2+3+101+SoF). |

---

## 7. Token Contract (IERC3643)

These data points are token-level (not investor-level). OpenKYCAML focuses on investor KYC/AML records, not the token contract itself. However, the following token-level state is relevant to investor records.

| ERC-3643 Field | Type | Description | OpenKYCAML Field | Notes |
|---|---|---|---|---|
| `isFrozen(address)` | `bool` | Whether the investor's wallet is frozen | `kycProfile.blockchainAccountIds[].isFrozen` ⭐ | Per-wallet entry in `blockchainAccountIds[]`. For XRPL, use `xrplFreezeType` ⭐ (v1.7.0) to distinguish Individual, Global, or Deep Freeze (XLS-77). |
| `getFrozenTokens(address)` | `uint256` | Amount frozen on the wallet | `kycProfile.blockchainAccountIds[].frozenTokenAmount` ⭐ | Decimal string per-wallet entry. |
| `onchainID` (token's) | `address` | Token issuer's ONCHAINID address | ℹ️ Token metadata, not investor KYC | Not in scope of investor KYC record. |
| `name`, `symbol`, `decimals`, `version` | Token metadata | Token contract metadata | ℹ️ Not investor data | Could be referenced in `kycProfile.auditMetadata` or transaction records. |
| `paused` | `bool` | Token transfer pause status | ℹ️ Token-level state | Not investor-specific. |
| `recoveryAddress(lost, new, onchainID)` | action | Key recovery for lost wallets | `kycProfile.auditMetadata.changeLog[]` with event type `UPDATED` + note on wallet change | The old and new wallet addresses should be logged in the audit trail. |
| `forcedTransfer(from, to, amount)` | action | Issuer-initiated forced transfer of tokens from a holder | `kycProfile.auditMetadata.changeLog[]` with event type `UPDATED` | XRPL equivalent: Native Clawback amendment (`Clawback` transaction); `kycProfile.blockchainAccountIds[].xrplClawbackEnabled` ⭐ (v1.7.0) records whether the issuer holds clawback rights. |

---

## 8. Compliance Contract (ICompliance)

Compliance rules are enforced on-chain per token. The equivalent off-chain state in OpenKYCAML is the KYC/AML profile.

| ERC-3643 Compliance Check | Description | OpenKYCAML Field | Notes |
|---|---|---|---|
| `canTransfer(from, to, amount)` | Whether a transfer is permitted under current rules | `kycProfile.isEligible` + `kycProfile.customerRiskRating` + `kycProfile.sanctionsScreening.screeningStatus` | Off-chain evaluation. Both parties need `isEligible: true` and no sanctions hits. |
| Country-based transfer restrictions | Restrict transfers to/from certain investor countries | `kycProfile.blockchainAccountIds[].network` + `ivms101.*.naturalPerson.countryOfResidence` | Country is `investorCountry` in registry; see §2 for mapping. |
| Maximum token holders | Hard cap on number of distinct wallet holders | ℹ️ On-chain rule only | Not stored in investor KYC record. |
| Maximum tokens per investor | Cap on balance per wallet | ℹ️ On-chain rule only | Not stored in investor KYC record. |

---

## 9. Coverage Gap Summary

The following fields were **added to OpenKYCAML v1.2.0** to close gaps identified in this mapping:

| Schema Addition | ERC-3643 Equivalent | Location |
|---|---|---|
| `kycProfile.isEligible` (boolean) | `IIdentityRegistry.isVerified(address)` | `KYCProfile.properties.isEligible` |
| `kycProfile.eligibilityLastConfirmed` (date) | Block timestamp of last successful `isVerified()` | `KYCProfile.properties.eligibilityLastConfirmed` |
| `kycProfile.blockchainAccountIds[]` (array) | `IIdentityRegistry.identity(address)` + `investorCountry(address)` | `KYCProfile.properties.blockchainAccountIds` |
| `kycProfile.blockchainAccountIds[].onchainIDAddress` | `IIdentityRegistry.identity(address)` → ONCHAINID address | Inside `blockchainAccountIds` item |
| `kycProfile.blockchainAccountIds[].isFrozen` | `IERC3643.isFrozen(address)` | Inside `blockchainAccountIds` item |
| `kycProfile.blockchainAccountIds[].frozenTokenAmount` | `IERC3643.getFrozenTokens(address)` | Inside `blockchainAccountIds` item |
| `kycProfile.customerClassification.accreditedInvestor` (boolean) | Claim topic 101 (Accredited / Eligible Investor) | `customerClassification.properties.accreditedInvestor` |
| `kycProfile.customerClassification.investorCategoryJurisdiction` (alpha-2) | Jurisdiction of accreditation assessment | `customerClassification.properties.investorCategoryJurisdiction` |

**No schema changes** were required for the following — OpenKYCAML already covered them:

| ERC-3643 Data Point | Existing OpenKYCAML Coverage |
|---|---|
| Claim topic 1 (KYC) | `kycProfile.kycCompletionDate` + `dueDiligenceRequirements` |
| Claim topic 2 (AML) | `kycProfile.sanctionsScreening` + `adverseMedia` |
| Claim topic 3 (Country) | `ivms101.*.naturalPerson.countryOfResidence` |
| Claim issuer | `verifiableCredential.issuer` + `evidence[].credentialIssuer` |
| Claim signature | `verifiableCredential.proof` |
| Claim identity data (ABI payload) | `ivms101.*` and `kycProfile.*` (structured JSON equivalent) |
| Claim URI | `verifiableCredential.credentialSchema.id` |
| ERC-734 claim signing key | `verifiableCredential.proof.verificationMethod` |
| Investor country (ISO 3166-1) | `ivms101.*.naturalPerson.geographicAddresses[].country` (alpha-2) |

---

## 10. Integration Guidance: OpenKYCAML → ERC-3643 Pipeline

To use an OpenKYCAML record as the data source for registering an investor in an ERC-3643 Identity Registry:

### Step 1 — Build the ONCHAINID contract
Map the following OpenKYCAML fields to ERC-735 claims:

```
Claim Topic 1 (KYC):
  data = abi.encode(kycProfile.kycCompletionDate, kycProfile.dueDiligenceType)
  issuer = DID-resolved Ethereum address of verifiableCredential.issuer
  uri  = verifiableCredential.id (VC URL)

Claim Topic 2 (AML):
  data = abi.encode(kycProfile.sanctionsScreening.screeningStatus, screeningDate)
  issuer = DID-resolved address of verifiableCredential.issuer

Claim Topic 3 (Country):
  data = abi.encode(ISO3166Numeric(ivms101.originator.*.naturalPerson.countryOfResidence))
  issuer = DID-resolved address of verifiableCredential.issuer

Claim Topic 101 (Accredited):
  data = abi.encode(kycProfile.customerClassification.accreditedInvestor)
  issuer = DID-resolved address of verifiableCredential.issuer
```

### Step 2 — Register in Identity Registry

```solidity
identityRegistry.registerIdentity(
    kycProfile.blockchainAccountIds[0].address,        // investorAddress
    address(onchainIDContract),                         // identity (ONCHAINID)
    ISO3166Numeric(investorCountry)                     // country (uint16)
);
```
→ Store the ONCHAINID contract address back in `kycProfile.blockchainAccountIds[0].onchainIDAddress`.

### Step 3 — Set eligibility flag
After successful registration and claim verification:
```json
{
  "kycProfile": {
    "isEligible": true,
    "eligibilityLastConfirmed": "2026-04-05"
  }
}
```

### Step 4 — Country code conversion
ERC-3643 uses ISO 3166-1 **numeric** uint16 codes. OpenKYCAML uses ISO 3166-1 **alpha-2** strings.
Reference table (selected): `"DE"` → `276`, `"GB"` → `826`, `"US"` → `840`, `"FR"` → `250`, `"CH"` → `756`, `"SG"` → `702`, `"AE"` → `784`.
Full mapping: [ISO 3166-1 alpha-2 to numeric](https://en.wikipedia.org/wiki/ISO_3166-1_numeric).

---

*Document version: v1.12.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*
*ERC-3643 reference: [EIP-3643](https://github.com/TokenySolutions/EIP3643), [ONCHAINID](https://github.com/onchain-id/solidity)*

---

## 11. Cross-Network Equivalence: ERC-3643 vs XRPL vs Bitcoin/Lightning

The table below maps ERC-3643 capabilities to their equivalents on XRPL and Bitcoin/Lightning, showing how the same OpenKYCAML fields serve all three enforcement models. See [docs/compliance/enforcement-tiers.md](../compliance/enforcement-tiers.md) for the full three-tier enforcement model.

| Capability | ERC-3643 (Ethereum) | XRPL | Bitcoin / Lightning |
|---|---|---|---|
| **On-chain identity** | ONCHAINID (ERC-734/735) contract — `onchainIDAddress` | XLS-70 `Credential` object — `xrplCredentialType` | Not applicable (service-layer only) |
| **Compliance-gated trading** | `ICompliance.canTransfer()` transfer restriction | XLS-80 Permissioned Domains + XLS-81d Permissioned DEX — `xrplPermissionedDomainId` | Not applicable (LSP compliance engine) |
| **Token standard** | ERC-3643 T-REX (ERC-20 extension) | Multi-Purpose Tokens (XLS-33d) — `mptIssuanceId`, `mptFlags`, `mptMetadata` | Not applicable |
| **Privacy** | None natively | XLS-96 Confidential Transfers (EC-ElGamal + ZKP) — `xrplConfidentialTransfer` | Not applicable |
| **Clawback / forced transfer** | `forcedTransfer(from, to, amount)` in T-REX | Native Clawback amendment — `xrplClawbackEnabled` | Not applicable |
| **Freeze** | `setAddressFrozen(address, true)` in T-REX | Native Freeze + Deep Freeze (XLS-77) — `xrplFreezeType` (`INDIVIDUAL_FREEZE` / `GLOBAL_FREEZE` / `DEEP_FREEZE`) | Not applicable |
| **Eligibility gate** | `IIdentityRegistry.isVerified(address)` | `lsfMPTAuthorized` on `MPToken` | `kycProfile.isEligible` fed to LSP |
| **OpenKYCAML eligibility field** | `kycProfile.isEligible` | `kycProfile.isEligible` | `kycProfile.isEligible` |
| **Lightning node identity** | Not applicable | Not applicable | `lightningNodePubkey` ⭐ |
| **Service provider** | Not applicable | Not applicable | `lightningServiceProvider` ⭐ |
