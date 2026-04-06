# OpenKYCAML Three-Tier Compliance Enforcement Model

This document defines the three-tier enforcement model that OpenKYCAML supports, reflecting the architectural reality that compliance is enforced at fundamentally different levels across blockchain networks. The same OpenKYCAML payload serves all three tiers — the difference is *how* and *where* the enforcement is applied.

---

## 1. The Three Tiers

```
┌─────────────────────────────────────────────────────────────────────────┐
│  TIER 1: On-Chain Enforcement                                           │
│  Network: Ethereum (and EVM-compatible chains)                          │
│  Mechanism: Smart contract logic in ERC-3643 (T-REX)                   │
│  Key property: No transfer can proceed without contract approval.        │
│  Who enforces: The token contract itself.                               │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  TIER 2: Protocol-Level Enforcement                                     │
│  Network: XRP Ledger (XRPL)                                             │
│  Mechanism: XRPL protocol primitives — XLS-70 Credentials,             │
│             XLS-80 Permissioned Domains, XLS-81d Permissioned DEX,     │
│             XLS-77 Deep Freeze, Native Clawback, MPTs (XLS-33d)        │
│  Key property: The ledger itself enforces credentials and access gates. │
│  Who enforces: The XRPL consensus mechanism.                            │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  TIER 3: Service-Layer Enforcement                                      │
│  Networks: Bitcoin, Lightning Network (and Layer-2s: RGB, Taproot       │
│             Assets, Liquid)                                             │
│  Mechanism: LSP / VASP compliance engine — Lightspark Compliance API,  │
│             Voltage Flow, BitGo, Coinbase compliance stack              │
│  Key property: The protocol has no compliance hooks. Enforcement is     │
│                entirely off-chain by the service operator.              │
│  Who enforces: The LSP / custodian / VASP.                              │
└─────────────────────────────────────────────────────────────────────────┘
```

**Important:** Neither approach is inherently better. They are architecturally different solutions to the same problem — ensuring that regulated assets can only be held and transferred by KYC/AML-verified parties.

---

## 2. Capability Comparison

| Capability | Tier 1: Ethereum (ERC-3643) | Tier 2: XRPL | Tier 3: Bitcoin / Lightning |
|---|---|---|---|
| **On-chain identity** | ONCHAINID (ERC-734/735) smart contract | XLS-70 On-Chain Credentials (live on mainnet) | ❌ Not available at protocol level |
| **Compliance-gated trading** | `ICompliance.canTransfer()` enforced by token contract | XLS-80 Permissioned Domains + XLS-81d Permissioned DEX | Service-layer only (LSP compliance engine) |
| **Token standard** | ERC-3643 T-REX (ERC-20 extension with transfer rules) | Multi-Purpose Tokens (XLS-33d) with `lsfMPTRequireAuth` gate | Not applicable at protocol level |
| **Privacy** | None natively — all balances and transfers visible | XLS-96 Confidential Transfers (EC-ElGamal + ZKP) | Liquid Network Confidential Transactions (federation) |
| **Clawback / forced transfer** | `forcedTransfer(from, to, amount)` in T-REX contract | Native Clawback amendment + `lsfMPTCanClawback` | ❌ Not available at protocol level |
| **Freeze** | `setAddressFrozen(address, true)` in T-REX contract | Native Freeze + Deep Freeze (XLS-77) | ❌ Not available at protocol level |
| **Eligibility gate** | `IIdentityRegistry.isVerified(address)` | `lsfMPTAuthorized` on `MPToken` | Service-layer check by LSP |
| **Revocation** | Remove ONCHAINID claim + `isVerified()` returns false | `CredentialDelete` transaction (XLS-70) | Service-layer revocation |
| **Compliance enforcement party** | Smart contract (autonomous, always-on) | XRPL validators (consensus-enforced) | LSP / VASP service operator |
| **Enforcement latency** | Every transfer checked at contract execution | Every transaction checked by validators | Checked at payment initiation by LSP |

---

## 3. How OpenKYCAML Serves All Three Tiers

OpenKYCAML is the **neutral, shared data standard** that feeds compliance enforcement regardless of tier. The same payload structure is used across all three — the enforcement mechanism differs, not the data.

### 3.1 Tier 1: OpenKYCAML → ERC-3643 Pipeline

```
1. VASP completes KYC/AML → issues OpenKYCAML payload
2. OpenKYCAML data used to:
   - Build ONCHAINID claims (ERC-735): topic 1 (KYC), topic 2 (AML), topic 101 (Accredited)
   - Register investor in IIdentityRegistry: investorAddress, ONCHAINID contract, country code
   - Set kycProfile.isEligible: true → triggers IIdentityRegistry.registerIdentity()
3. ERC-3643 token contract calls IIdentityRegistry.isVerified() on every transfer
4. If kycProfile.isEligible: false → ONCHAINID claim removed → isVerified() returns false → transfer reverts
```

**Key OpenKYCAML fields for Tier 1:**
- `kycProfile.isEligible` → `IIdentityRegistry.isVerified()`
- `kycProfile.blockchainAccountIds[].onchainIDAddress` → ONCHAINID contract address
- `kycProfile.blockchainAccountIds[].isFrozen` → `IERC3643.isFrozen()`
- `verifiableCredential.type[]` → ERC-735 claim topics

### 3.2 Tier 2: OpenKYCAML → XRPL Protocol Pipeline

```
1. VASP completes KYC/AML → issues OpenKYCAML payload
2. OpenKYCAML VC stored off-ledger, URI encoded in CredentialCreate transaction
3. XRPL protocol enforces:
   - CredentialCreate (XLS-70): anchors OpenKYCAML VC on-ledger
   - DepositPreauth credential gate: only holders of {Issuer, CredentialType} may transact
   - MPTokenAuthorize: kycProfile.isEligible: true → lsfMPTAuthorized = 1
   - Permissioned Domain (XLS-80): xrplPermissionedDomainId gates DEX access
   - Deep Freeze (XLS-77): xrplFreezeType: "DEEP_FREEZE" on holder
   - Clawback: xrplClawbackEnabled: true → issuer can invoke Clawback transaction
4. XRPL validators enforce these rules on every transaction — no service intermediary needed
```

**Key OpenKYCAML fields for Tier 2:**
- `kycProfile.blockchainAccountIds[].xrplCredentialType` → `CredentialType` in XLS-70
- `kycProfile.blockchainAccountIds[].mptIssuanceId` → `MPTokenIssuanceID`
- `kycProfile.blockchainAccountIds[].xrplPermissionedDomainId` → Permissioned Domain gate (XLS-80)
- `kycProfile.blockchainAccountIds[].xrplAuthorizedCredentialTypes[]` → domain credential requirements
- `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer` → XLS-96 auditor/regulator keys
- `kycProfile.blockchainAccountIds[].xrplFreezeType` → freeze level (XLS-77)
- `kycProfile.blockchainAccountIds[].xrplClawbackEnabled` → clawback capability

### 3.3 Tier 3: OpenKYCAML → Bitcoin/Lightning Service Pipeline

```
1. VASP / LSP completes KYC/AML → issues OpenKYCAML payload
2. OpenKYCAML payload fed into LSP compliance engine:
   - Lightspark Compliance API ingests ivms101 block for Travel Rule
   - Voltage Flow uses kycProfile.sanctionsScreening for payment risk scoring
   - BitGo / Coinbase compliance uses kycProfile.isEligible for payment approval
3. LSP enforces at payment initiation:
   - If kycProfile.isEligible: false → LSP blocks payment
   - If kycProfile.sanctionsScreening.screeningStatus: "MATCH" → LSP blocks payment
   - Travel Rule data from ivms101 block is transmitted to counterparty LSP
4. No protocol-level enforcement — the LSP is the single point of compliance control
```

**Key OpenKYCAML fields for Tier 3:**
- `kycProfile.blockchainAccountIds[].lightningNodePubkey` → Lightning node identity
- `kycProfile.blockchainAccountIds[].lightningServiceProvider` → identifies the enforcing LSP
- `kycProfile.blockchainAccountIds[].bitcoinScriptType` → chain analysis context
- `kycProfile.isEligible` → fed to LSP for payment approval
- `ivms101` block → Travel Rule data for LSP-to-LSP exchange

---

## 4. OpenKYCAML Field-to-Tier Mapping

The following table maps every key OpenKYCAML field to the tier(s) that consume it:

| OpenKYCAML Field | Tier 1 (Ethereum) | Tier 2 (XRPL) | Tier 3 (Bitcoin/Lightning) |
|---|---|---|---|
| `ivms101.*` (all Travel Rule fields) | ✅ T-REX compliance context | ✅ Anchored via Credential URI | ✅ Primary data source for LSP Travel Rule |
| `kycProfile.isEligible` | ✅ Maps to `isVerified()` | ✅ Maps to `lsfMPTAuthorized` | ✅ Fed to LSP for payment approval |
| `kycProfile.eligibilityLastConfirmed` | ✅ For re-KYC scheduling | ✅ For credential renewal | ✅ For LSP refresh triggers |
| `kycProfile.blockchainAccountIds[].address` | ✅ `investorAddress` in registry | ✅ XRPL r-address | ✅ Bitcoin on-chain address |
| `kycProfile.blockchainAccountIds[].onchainIDAddress` | ✅ ONCHAINID contract address | — | — |
| `kycProfile.blockchainAccountIds[].isFrozen` | ✅ Mirrors `isFrozen(address)` | ✅ Mirrors `lsfMPTLocked` | — |
| `kycProfile.blockchainAccountIds[].frozenTokenAmount` | ✅ Mirrors `getFrozenTokens()` | ✅ For clawback context | — |
| `kycProfile.blockchainAccountIds[].xrplCredentialType` | — | ✅ Hex CredentialType (XLS-70) | — |
| `kycProfile.blockchainAccountIds[].mptIssuanceId` | — | ✅ Hash192 MPTokenIssuanceID | — |
| `kycProfile.blockchainAccountIds[].xrplPermissionedDomainId` | — | ✅ Permissioned Domain gate (XLS-80) | — |
| `kycProfile.blockchainAccountIds[].xrplAuthorizedCredentialTypes[]` | — | ✅ Domain credential requirements (XLS-80) | — |
| `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer` | — | ✅ XLS-96 auditor/regulator keys | — |
| `kycProfile.blockchainAccountIds[].mptFlags` | — | ✅ MPT compliance configuration flags | — |
| `kycProfile.blockchainAccountIds[].mptMetadata` | — | ✅ ISIN / compliance rules in token | — |
| `kycProfile.blockchainAccountIds[].mptTransferFee` | — | ✅ Fee-aware compliance calculations | — |
| `kycProfile.blockchainAccountIds[].xrplFreezeType` | — | ✅ INDIVIDUAL / GLOBAL / DEEP (XLS-77) | — |
| `kycProfile.blockchainAccountIds[].xrplClawbackEnabled` | — | ✅ Native Clawback rights | — |
| `kycProfile.blockchainAccountIds[].lightningNodePubkey` | — | — | ✅ Lightning node identity |
| `kycProfile.blockchainAccountIds[].lightningServiceProvider` | — | — | ✅ Identifies enforcing LSP |
| `kycProfile.blockchainAccountIds[].bitcoinScriptType` | — | — | ✅ Chain analysis context |
| `kycProfile.sanctionsScreening` | ✅ Fed to claim topics registry | ✅ AML credential gate | ✅ Fed to LSP payment risk engine |
| `kycProfile.adverseMedia` | ✅ EDD trigger | ✅ EDD credential gate | ✅ LSP risk score input |
| `kycProfile.pepStatus` | ✅ PEP claim topic | ✅ EDD credential type | ✅ LSP EDD flag |
| `kycProfile.customerRiskRating` | ✅ Transfer rule input | ✅ Credential type selection | ✅ LSP risk-based limits |
| `kycProfile.beneficialOwnership[]` | ✅ UBO claim (custom topic) | ✅ UBO credential type | ✅ VASP CDD context |
| `verifiableCredential.*` | ✅ Claims in ONCHAINID contract | ✅ Off-chain content at Credential.URI | ✅ LSP identity attestation |
| `gdprSensitivityMetadata` | ✅ GDPR-compliant disclosure | ✅ ZKP privacy alignment (XLS-96) | ✅ LSP data minimisation |

---

## 5. Regulatory Alignment by Tier

All three tiers satisfy the same regulatory requirements — FATF Recommendations, AMLR 2027, eIDAS 2.0 — but through different enforcement mechanisms:

| Regulation | Tier 1 (Ethereum) | Tier 2 (XRPL) | Tier 3 (Bitcoin/Lightning) |
|---|---|---|---|
| **FATF Rec 10** — CDD | KYC data populates ONCHAINID claims | KYC data anchored in XLS-70 Credential URI | KYC data in OpenKYCAML fed to LSP |
| **FATF Rec 16** — Travel Rule | Off-chain IVMS 101 exchange; `investorAddress` identifies chain counterparty | `ivms101` block anchored via Credential; XRPL Travel Rule protocols (TRISA, TRP) | `ivms101` block consumed by Lightspark/Voltage/Notabene Travel Rule APIs |
| **AMLR Art. 22** — CDD measures | ERC-3643 claim topics map to CDD tiers | XLS-70 credential types map to CDD tiers | LSP applies CDD tiers based on OpenKYCAML `dueDiligenceType` |
| **AMLR Art. 56** — Record keeping | `auditMetadata` + on-chain ONCHAINID history | `auditMetadata` + persistent on-ledger Credential objects | `auditMetadata` + LSP audit trail |
| **GDPR Art. 5(1)(c)** — Data minimisation | SD-JWT selective disclosure of OpenKYCAML VC | XLS-96 encrypted balances + selective disclosure keys | SD-JWT minimised payload to LSP |
| **MiCA Art. 83** — Transfer data | ERC-3643 permissioned token enforces CDD basis | MPT `lsfMPTRequireAuth` + Credential gate enforces CDD basis | LSP enforces CDD basis before payment |

---

## 6. Guidance for Implementers

### Choosing the right tier

- **Issuing regulated securities (RWAs, tokenised bonds/equities):** Use Tier 1 (ERC-3643) or Tier 2 (XRPL MPTs) depending on your chain of choice. Both provide on-chain enforcement that meets MiCA Art. 83 and AMLR Art. 22 requirements without requiring a trust relationship with a service provider.

- **Retail payment infrastructure:** Tier 3 (Lightning) is appropriate when the LSP is a licensed VASP that enforces compliance at the service layer. Lightspark and Voltage provide enterprise-grade compliance wrappers that satisfy FATF Rec. 16 Travel Rule requirements.

- **Multi-chain / multi-tier deployments:** OpenKYCAML is designed for this. A single KYC record with multiple `blockchainAccountIds[]` entries can simultaneously feed an ERC-3643 Identity Registry (Tier 1), an XRPL MPT issuance (Tier 2), and a Lightning LSP compliance engine (Tier 3).

### A single OpenKYCAML record for all three tiers

```json
{
  "kycProfile": {
    "isEligible": true,
    "eligibilityLastConfirmed": "2026-04-01",
    "blockchainAccountIds": [
      {
        "address": "0xAbCd1234...",
        "network": "eip155:1",
        "onchainIDAddress": "0x1234AbCd...",
        "isFrozen": false
      },
      {
        "address": "rCustomerAccountAddress",
        "network": "xrpl",
        "xrplCredentialType": "4f70656e4b5943414d4c43726564656e7469616c",
        "mptIssuanceId": "00070c44695f6d5468420c16ef71b6f1a27c8b0042a1ff00",
        "xrplPermissionedDomainId": "A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2",
        "xrplClawbackEnabled": false,
        "xrplFreezeType": null
      },
      {
        "address": "bc1p5d7rjq7g6rdk2yhzks9smlaqtedr4dekq08ge8ztwac72sfr9rusxg3297",
        "network": "bitcoin",
        "bitcoinScriptType": "P2TR",
        "lightningNodePubkey": "02a7f4a1b3c9e8d6f2b4c5e7a9d1f3b5c7e9a2d4f6b8c0e2a4d6f8b0c2e4a6d8f0",
        "lightningServiceProvider": "Lightspark"
      }
    ]
  }
}
```

---

## 7. Related Documents

| Document | Description |
|---|---|
| [mapping-erc3643.md](../mappings/mapping-erc3643.md) | Full field-level mapping for Tier 1 (ERC-3643 / ONCHAINID) |
| [mapping-xrpl-credentials-mpt.md](../mappings/mapping-xrpl-credentials-mpt.md) | Full field-level mapping for Tier 2 (XLS-70/80/81/96, MPTs, Clawback, Deep Freeze) |
| [mapping-bitcoin-lightning.md](../mappings/mapping-bitcoin-lightning.md) | Full field-level mapping for Tier 3 (Bitcoin / Lightning) |
| [compliance-matrix.md](compliance-matrix.md) | Regulatory alignment matrix across all tiers |

---

*Document version: v1.7.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*
