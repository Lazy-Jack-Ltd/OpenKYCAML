# OpenKYCAML ↔ Bitcoin and Lightning Network Mapping

This document describes how OpenKYCAML supports Bitcoin and Lightning Network compliance workflows. Unlike Ethereum (ERC-3643) and XRPL (XLS-70/80/81/96), Bitcoin has no protocol-level compliance framework. Compliance on Bitcoin and Lightning is enforced entirely at the **service layer** — by Lightning Service Providers (LSPs), VASP compliance engines, and custodial platforms.

**Sources used:**
- [FATF Guidance for Virtual Assets and VASPs (2021)](https://www.fatf-gafi.org/publications/fatfgeneral/documents/guidance-rba-virtual-assets-2021.html)
- [Lightspark Compliance API](https://docs.lightspark.com/lightspark-sdk/compliance) — enterprise Lightning compliance wrapper
- [Voltage Flow](https://docs.voltage.cloud) — Lightning infrastructure with compliance controls
- [RGB Protocol](https://rgb.tech/) — client-side validation for Bitcoin assets
- [Taproot Assets Protocol](https://docs.lightning.engineering/the-lightning-network/taproot-assets) — Lightning Labs asset issuance on Bitcoin
- [Liquid Network](https://blockstream.com/liquid/) — federated Bitcoin sidechain for confidential transactions
- [BIP-341 Taproot](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki) — Schnorr + MAST Bitcoin script type

**Coverage legend:**
- ✅ Full coverage — field exists in OpenKYCAML schema
- 🔄 Conceptual mapping — equivalent concept captured differently
- ⭐ Schema extended — field added to OpenKYCAML v1.7.0
- ⬜ Not in scope — no protocol-level equivalent; service-layer enforcement only

---

## 1. Architecture: Three-Tier Enforcement Model

OpenKYCAML supports three enforcement tiers. Bitcoin and Lightning operate entirely at Tier 3:

```
Tier 1 — On-chain enforcement (Ethereum)
    ERC-3643 smart contracts enforce transfer rules, eligibility, freeze, and clawback
    at the token contract level. No transfer proceeds without contract approval.

Tier 2 — Protocol-level enforcement (XRPL)
    The ledger itself enforces credentials (XLS-70), permissioned domains (XLS-80),
    DEX access (XLS-81d), freeze/deep-freeze (XLS-77), and clawback natively.
    No off-ledger intermediary needed for enforcement.

Tier 3 — Service-layer enforcement (Bitcoin / Lightning)
    Bitcoin scripting is intentionally limited. There is no equivalent of ERC-3643
    or XRPL credentials at the protocol level. Compliance is provided entirely by
    the service layer: LSPs, custodians, and VASP compliance engines.
    The OpenKYCAML payload feeds the service layer — same data, different enforcement.
```

See [docs/compliance/enforcement-tiers.md](../compliance/enforcement-tiers.md) for the complete three-tier model.

---

## 2. Bitcoin Protocol Compliance Limitations

Bitcoin's scripting language (Script) is intentionally Turing-incomplete and designed for minimal trust assumptions. It does not support:

| Capability | ERC-3643 (Ethereum) | XRPL | Bitcoin |
|---|---|---|---|
| On-chain identity/credential | ONCHAINID (ERC-734/735) | XLS-70 Credentials | ❌ Not supported |
| Permissioned trading | `ICompliance.canTransfer()` | XLS-80/81 Permissioned DEX | ❌ Not supported |
| Token compliance rules | ERC-3643 T-REX contracts | MPTs (XLS-33d) with `lsfMPTRequireAuth` | ❌ Not supported (Bitcoin native) |
| Freeze / clawback | `setAddressFrozen()` / `forcedTransfer()` | Native Freeze + Clawback + Deep Freeze | ❌ Not supported |
| Privacy | None natively | XLS-96 EC-ElGamal + ZKP | Confidential Transactions on Liquid |

**Consequence:** For Bitcoin-native assets, compliance must be enforced off-chain by the institution operating the VASP, LSP, or custodial service. OpenKYCAML provides the standardised KYC/AML data record; the compliance enforcement mechanism is the service's own policy engine.

---

## 3. Layer-2 Solutions: Limited Protocol-Level Compliance

Bitcoin Layer-2 solutions offer some improvements but do not achieve on-chain compliance enforcement equivalent to ERC-3643 or XRPL:

| Layer-2 Solution | Purpose | Compliance Level | OpenKYCAML Role |
|---|---|---|---|
| **Lightning Network** | Off-chain payment channels for micro-payments and fast settlement | Service-layer only — compliance at LSP level | `lightningNodePubkey` + `lightningServiceProvider` ⭐ — links KYC identity to node |
| **Liquid Network** (Blockstream) | Federated Bitcoin sidechain for confidential transactions; supports Issued Assets | Partially — Confidential Transactions hide amounts; asset issuance controlled by federation | `blockchainAccountIds[].network: "liquid"` — standard wallet address and network identifier |
| **Taproot Assets** (Lightning Labs) | Issue and transfer assets over Bitcoin and Lightning using Taproot | Service-layer — Taproot Assets UTXOs carry asset metadata, but compliance is enforced by the universe server | `blockchainAccountIds[].address` + `bitcoinScriptType: "P2TR"` ⭐ |
| **RGB Protocol** | Client-side validation protocol for issuing assets on Bitcoin | Client-side only — validation is off-chain; the Bitcoin blockchain carries only commitments | `blockchainAccountIds[].address` — RGB uses standard Bitcoin addresses |

---

## 4. Bitcoin Address Types → OpenKYCAML Mapping

| Bitcoin Script Type | Description | OpenKYCAML `bitcoinScriptType` ⭐ | OpenKYCAML `address` format |
|---|---|---|---|
| **P2PKH** (Pay to Public Key Hash) | Legacy address format (Base58Check, starts with `1`) | `"P2PKH"` | e.g. `1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf` |
| **P2WPKH** (Pay to Witness Public Key Hash) | Native SegWit (bech32, starts with `bc1q`) — lower fees, better malleability protection | `"P2WPKH"` | e.g. `bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq` |
| **P2TR** (Pay to Taproot) | Taproot (bech32m, starts with `bc1p`) — Schnorr signatures, MAST script trees, privacy-enhanced. Supports Taproot Assets. | `"P2TR"` | e.g. `bc1p5d7rjq7g6rdk2yhzks9smlaqtedr4dekq08ge8ztwac72sfr9rusxg3297` |

**Usage note:** `bitcoinScriptType` is applicable when `network` is `"bitcoin"`, a Bitcoin testnet, or a Bitcoin Layer-2 network (Liquid, Taproot Assets, RGB). Not applicable for Lightning channel addresses — use `lightningNodePubkey` instead.

---

## 5. Lightning Network → OpenKYCAML Mapping

The Lightning Network is a Layer-2 payment channel network built on Bitcoin. Institutions including BitGo, Coinbase, Revolut, and many others operate Lightning nodes serving 600M+ users. Compliance is entirely at the service layer.

### 5.1 Lightning Node Identity

| Lightning Concept | Description | OpenKYCAML Field | Notes |
|---|---|---|---|
| **Node public key** (compressed secp256k1, 33 bytes) | Unique identity of a Lightning node on the network. Used for node-to-node authentication and LNURL-auth identity binding. | `kycProfile.blockchainAccountIds[].lightningNodePubkey` ⭐ | 66-char hex. Pattern: `^[0-9a-fA-F]{66}$`. Added v1.7.0. |
| **Lightning Service Provider (LSP)** | The regulated entity providing compliance infrastructure for the Lightning node (e.g. Lightspark, Voltage, BitGo) | `kycProfile.blockchainAccountIds[].lightningServiceProvider` ⭐ | Name or DID. Identifies who is responsible for AML/KYC enforcement. Added v1.7.0. |
| **Channel address** | Bitcoin on-chain address for the channel funding transaction | `kycProfile.blockchainAccountIds[].address` + `bitcoinScriptType: "P2TR"` | Taproot channels use P2TR; legacy channels use P2WSH (not enumerated — use P2WPKH approximation for screening). |

### 5.2 LNURL-Auth Identity Binding

LNURL-auth is a Lightning-native identity protocol that uses challenge-response with the node's key to authenticate users without passwords or email. The node public key can be used to bind a Lightning identity to an OpenKYCAML KYC record:

```json
{
  "kycProfile": {
    "blockchainAccountIds": [{
      "address": "bc1p5d7rjq7g6rdk2yhzks9smlaqtedr4dekq08ge8ztwac72sfr9rusxg3297",
      "network": "bitcoin",
      "bitcoinScriptType": "P2TR",
      "lightningNodePubkey": "02a7f4a1b3c9e8d6f2b4c5e7a9d1f3b5c7e9a2d4f6b8c0e2a4d6f8b0c2e4a6d8f0",
      "lightningServiceProvider": "Lightspark"
    }]
  }
}
```

### 5.3 Service-Layer Compliance Providers

Major Lightning compliance infrastructure providers and their integration pattern with OpenKYCAML:

| Provider | Compliance Approach | OpenKYCAML Integration |
|---|---|---|
| **Lightspark** (Lightspark Compliance API) | Turnkey Lightning node with built-in Travel Rule, sanctions screening, and KYC orchestration via Lightspark Compliance API | `lightningServiceProvider: "Lightspark"` — Lightspark ingests OpenKYCAML `ivms101` block for Travel Rule compliance |
| **Voltage** (Voltage Flow) | Cloud Lightning node infrastructure with compliance controls and analytics | `lightningServiceProvider: "Voltage"` — OpenKYCAML record feeds Voltage Flow compliance pipeline |
| **BitGo** | Institutional custodian with Lightning support and enterprise KYC | `lightningServiceProvider: "BitGo"` — BitGo uses KYC data for Travel Rule and FATF compliance |
| **Coinbase** | Consumer and institutional Lightning with in-house KYC/AML | `lightningServiceProvider: "Coinbase"` |
| **Revolut** | Consumer Lightning with in-house compliance | `lightningServiceProvider: "Revolut"` |

---

## 6. Travel Rule on Lightning

FATF Recommendation 16 applies to Lightning Network transactions above the threshold when operated by a VASP. Compliance is at the service layer:

| Travel Rule Requirement | Lightning Mechanism | OpenKYCAML Coverage |
|---|---|---|
| Originator information (name, address, account) | Not in Lightning protocol — provided by LSP | `ivms101.originator.*` — same fields as any VASP Travel Rule message |
| Beneficiary information | Not in Lightning protocol — provided by destination LSP | `ivms101.beneficiary.*` |
| Transfer amount | Payment amount in Lightning invoice / HTLC | `ivms101.transferredAmount.amount` (in satoshis or XBT) |
| VASP identification | LNURL-pay endpoint domain, node public key | `ivms101.originatingVASP`, `kycProfile.blockchainAccountIds[].lightningNodePubkey` ⭐ |
| Travel Rule message exchange | TRISA, TRP, or LSP proprietary API (e.g. Lightspark Compliance API) | `ivms101` block consumed by Travel Rule protocol |

---

## 7. Coverage Summary

### 7.1 What OpenKYCAML covers for Bitcoin / Lightning

| Requirement | Coverage | OpenKYCAML Field |
|---|---|---|
| KYC identity record (natural person) | ✅ | `ivms101.originator.originatorPersons[].naturalPerson.*` |
| KYC identity record (legal entity) | ✅ | `ivms101.originator.originatorPersons[].legalPerson.*` |
| AML screening | ✅ | `kycProfile.sanctionsScreening`, `kycProfile.adverseMedia` |
| Travel Rule data | ✅ | `ivms101` block (IVMS 101 v1.0 superset) |
| Bitcoin address (all script types) | ✅ | `kycProfile.blockchainAccountIds[].address` + `bitcoinScriptType` ⭐ |
| Lightning node identity | ✅ | `kycProfile.blockchainAccountIds[].lightningNodePubkey` ⭐ |
| Lightning LSP identification | ✅ | `kycProfile.blockchainAccountIds[].lightningServiceProvider` ⭐ |
| Risk rating | ✅ | `kycProfile.customerRiskRating` |
| PEP / sanctions | ✅ | `kycProfile.pepStatus`, `kycProfile.sanctionsScreening` |
| Audit trail | ✅ | `kycProfile.auditMetadata.changeLog[]` |
| GDPR compliance | ✅ | `gdprSensitivityMetadata` block |

### 7.2 What is out of scope for Bitcoin / Lightning

| Requirement | Status | Reason |
|---|---|---|
| Protocol-level transfer restrictions | ⬜ | Bitcoin scripting does not support this; no on-chain compliance hook |
| Protocol-level freeze / clawback | ⬜ | Not available at the Bitcoin protocol level; enforcement is service-layer only |
| On-chain credential/identity | ⬜ | No equivalent of ONCHAINID (Ethereum) or XLS-70 Credentials (XRPL) on Bitcoin |
| Taproot Assets compliance rules in token | ⬜ | Taproot Assets metadata is off-chain; the universe server enforces rules at service layer |
| RGB Protocol on-chain compliance | ⬜ | RGB uses client-side validation; no on-chain compliance enforcement |

---

## 8. Schema Extensions Added in v1.7.0

| Field | Location | Purpose |
|---|---|---|
| `lightningNodePubkey` ⭐ | `kycProfile.blockchainAccountIds[]` | Links KYC record to a Lightning node via its compressed public key (66-char hex, secp256k1) |
| `lightningServiceProvider` ⭐ | `kycProfile.blockchainAccountIds[]` | Identifies the LSP responsible for service-layer compliance enforcement |
| `bitcoinScriptType` ⭐ | `kycProfile.blockchainAccountIds[]` | Bitcoin script type for chain analysis context: `P2PKH` / `P2WPKH` / `P2TR` |

All fields are optional and additive. Existing payloads remain fully valid.

---

*Document version: v1.12.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*
*References: [FATF VA Guidance](https://www.fatf-gafi.org/publications/fatfgeneral/documents/guidance-rba-virtual-assets-2021.html), [Lightspark](https://docs.lightspark.com/lightspark-sdk/compliance), [Voltage](https://docs.voltage.cloud), [RGB Protocol](https://rgb.tech/), [Taproot Assets](https://docs.lightning.engineering/the-lightning-network/taproot-assets), [Liquid Network](https://blockstream.com/liquid/), [BIP-341 Taproot](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki)*
