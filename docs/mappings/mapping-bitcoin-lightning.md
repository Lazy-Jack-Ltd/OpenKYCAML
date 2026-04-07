# OpenKYCAML ↔ Bitcoin and Lightning Network Mapping

This document maps **Bitcoin** (UTXO model) and **Lightning Network** (payment channel network) compliance data points to OpenKYCAML v1.7.0 fields. It is a companion to the XRPL mapping (`mapping-xrpl-credentials-mpt.md`) and covers the two most significant pre-XRPL blockchain networks requiring AML/KYC integration.

**Standards and sources:**
- FATF R.16 — Wire transfers / Travel Rule (applies to Lightning Network payments)
- FATF R.15 — New technologies (virtual assets and VASPs)
- EU TFR 2023/1113 Art. 14 — Transfer of crypto-assets Travel Rule
- BIP-32/44/84/86 — Bitcoin HD wallet standards
- BOLT (Basis of Lightning Technology) specifications
- LSPS (Lightning Service Provider Specification)

---

## 1. Bitcoin Address Types

| Bitcoin Script Type | OpenKYCAML Field | Value | Notes |
|---|---|---|---|
| P2PKH (Legacy) | `kycProfile.blockchainAccountIds[].bitcoinScriptType` | `"P2PKH"` | `1...` address format; UTXO-based; common in older wallets |
| P2SH (Script Hash / SegWit-wrapped) | `kycProfile.blockchainAccountIds[].bitcoinScriptType` | `"P2SH"` | `3...` address format; multisig or SegWit-wrapped |
| P2WPKH (Native SegWit v0) | `kycProfile.blockchainAccountIds[].bitcoinScriptType` | `"P2WPKH"` | `bc1q...` address format; lower fees; most common modern format |
| P2WSH (Native SegWit v0 multisig) | `kycProfile.blockchainAccountIds[].bitcoinScriptType` | `"P2WSH"` | `bc1q...` (32-byte hash); institutional multisig |
| P2TR (Taproot / SegWit v1) | `kycProfile.blockchainAccountIds[].bitcoinScriptType` | `"P2TR"` | `bc1p...` address format; privacy-enhanced (MAST, Schnorr); higher AML scrutiny due to fungibility |
| Other / non-standard | `kycProfile.blockchainAccountIds[].bitcoinScriptType` | `"OTHER"` | Non-standard scripts, OP_RETURN, etc. |

### Address Type AML Significance

| Script Type | AML Risk Factor | Chain Analytics Integration |
|---|---|---|
| P2TR (Taproot) | 🔴 Enhanced scrutiny — MAST enables script privacy; Schnorr signatures enable key aggregation | Most analytics platforms support P2TR UTXO tracking |
| P2WSH multisig | 🟡 Medium — Multisig coordination may indicate business/custodial use | Standard support across Chainalysis, Elliptic, TRM |
| P2PKH | 🟡 Medium — Legacy format may indicate old wallet reuse; common in mixer outputs | Full support |
| P2WPKH | ✅ Low/baseline | Full support |

---

## 2. Bitcoin Wallet Identification

| Data Point | OpenKYCAML Field | Notes |
|---|---|---|
| Bitcoin address | `kycProfile.blockchainAccountIds[].address` | Bech32 (P2WPKH/P2TR) or Base58Check (P2PKH/P2SH) encoding |
| Network | `kycProfile.blockchainAccountIds[].network` | `"bitcoin"` (mainnet), `"bitcoin-testnet"` (testnet), CAIP-2: `"bip122:000000000019d6689c085ae165831e93"` |
| Script type | `kycProfile.blockchainAccountIds[].bitcoinScriptType` | Enables chain analytics platform integration |
| Registration date | `kycProfile.blockchainAccountIds[].registeredAt` | Date address was first associated with this KYC record |

---

## 3. Lightning Network

### 3.1 Node Identification

| Lightning Data Point | OpenKYCAML Field | Notes |
|---|---|---|
| Node public key | `kycProfile.blockchainAccountIds[].lightningNodePubkey` | 33-byte compressed secp256k1 point (66 hex chars); primary node identifier on the Lightning Network |
| Network | `kycProfile.blockchainAccountIds[].network` | `"lightning"` or `"lightning-testnet"` |
| LSP / custodial provider | `kycProfile.blockchainAccountIds[].lightningServiceProvider` | Name or DID of Lightning Service Provider (LSP) managing channels on behalf of the customer |

### 3.2 Lightning Travel Rule

The Lightning Network presents specific Travel Rule challenges due to its off-chain, channel-based payment model. OpenKYCAML captures the minimum information required for FATF R.16 and EU TFR Art. 14 compliance:

| Travel Rule Requirement | OpenKYCAML Field | Notes |
|---|---|---|
| Originating customer identification | `ivms101.originator.originatorPersons[]` | Full IVMS 101 natural/legal person |
| Originating VASP / LSP identification | `ivms101.originatingVASP` | LSP acts as VASP for custodial Lightning wallets |
| Beneficiary VASP / LSP identification | `ivms101.beneficiaryVASP` | Receiving LSP |
| Node pubkey as wallet identifier | `kycProfile.blockchainAccountIds[].lightningNodePubkey` | Used for VASP-to-VASP correlation |
| Transfer amount | `ivms101.transferredAmount` | Off-chain amount; must be captured at channel open/route |

### 3.3 LSP AML Considerations

| Scenario | OpenKYCAML Handling |
|---|---|
| Custodial Lightning wallet (LSP holds keys) | LSP is the obliged entity VASP; `lightningServiceProvider` = LSP DID/name; standard IVMS 101 Travel Rule |
| Self-custodial Lightning node | Customer is own VASP; `lightningNodePubkey` identifies their node; Travel Rule applies at channel partner level |
| Wrapped Lightning (L402, Bolt12) | Same as self-custodial; invoice/offer metadata captured in `ivms101` supplementary data |

---

## 4. Multi-Asset / Multi-Chain Wallets

For customers holding both Bitcoin and Lightning wallets, multiple `blockchainAccountIds[]` entries should be used:

```json
{
  "kycProfile": {
    "blockchainAccountIds": [
      {
        "address": "bc1p...",
        "network": "bitcoin",
        "bitcoinScriptType": "P2TR"
      },
      {
        "address": "02a1b2c3...",
        "network": "lightning",
        "lightningNodePubkey": "02a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3",
        "lightningServiceProvider": "Voltage Cloud"
      }
    ]
  }
}
```

---

## 5. Coverage Assessment

| Requirement | Coverage | Field |
|---|---|---|
| Bitcoin address type identification | ✅ Full (v1.7.0) | `bitcoinScriptType` |
| Bitcoin network identification | ✅ Full | `network` (CAIP-2 supported) |
| Lightning node pubkey | ✅ Full (v1.7.0) | `lightningNodePubkey` |
| LSP identification | ✅ Full (v1.7.0) | `lightningServiceProvider` |
| Lightning Travel Rule | ✅ Full | IVMS 101 `originator`/`beneficiary` + `originatingVASP`/`beneficiaryVASP` |
| Bitcoin UTXO analytics integration | ✅ Full (v1.7.0) | `bitcoinScriptType` |
| Taproot privacy risk flag | 🟡 Partial | `bitcoinScriptType` = `P2TR` (no dedicated risk flag; use `customerRiskRating` enrichment) |

---

*Last updated: April 2026 — OpenKYCAML v1.7.0*
