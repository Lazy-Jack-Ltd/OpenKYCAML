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

---

## Part 2: Regulatory Compliance Tiers — Field Enforcement by Obliged Entity Type

The following tiers define which OpenKYCAML fields are mandatory, strongly recommended, or optional for different obliged entity types and regulatory regimes. They complement the three-tier blockchain enforcement model above and support AMLR 2027 compliance programme gap analysis.

### Tier Overview

| Tier | Label | Enforcement Standard | Use Cases |
|---|---|---|---|
| **Tier 0** | Absolute minimum | JSON schema `required` constraints — payload is invalid without these | Any OpenKYCAML envelope regardless of use case |
| **Tier 1** | FATF Core | Required for FATF-compliant Travel Rule and CDD | VASPs, banks under FATF R.10/16 |
| **Tier 2** | AMLR 2027 | Required for EU obliged entities from 1 July 2027 | EU banks, fintechs, crypto-asset service providers under AMLR |
| **Tier 3** | EDD / High-Risk | Required when `dueDiligenceType` = `EDD` or `customerRiskRating` = `VERY_HIGH` | PEP, high-risk country, complex ownership |
| **Tier 4** | PredictiveAML | Required when using AI-based AML scoring under EU AI Act | Obliged entities deploying high-risk AI for AML |
| **Tier 5** | XRPL / Blockchain | Required for on-chain VASP Travel Rule and XRPL credential-gated tokens | XRPL-based VASPs, MPT issuers, permissioned domain operators |

### Tier 0 — Absolute Minimum (Schema Required)

These fields are enforced by JSON Schema `required` constraints. A payload without them fails validation.

| Field | Constraint |
|---|---|
| `predictiveAML.modelMetadata.modelId` | Required when `predictiveAML` is present |
| `predictiveAML.modelMetadata.modelVersion` | Required when `predictiveAML` is present |
| `predictiveAML.modelMetadata.euAiActClassification` | Required when `predictiveAML` is present |
| `predictiveAML.predictiveScores[]` (minItems: 1) | Required when `predictiveAML` is present |
| `predictiveAML.predictiveScores[].scoreType` | Required per score |
| `predictiveAML.predictiveScores[].value` | Required per score |
| `predictiveAML.predictiveScores[].confidence` | Required per score |

### Tier 1 — FATF Core

| Field | Regulatory Basis | Applicability |
|---|---|---|
| `ivms101.originator` | FATF R.16 Travel Rule | All VASPs |
| `ivms101.beneficiary` | FATF R.16 Travel Rule | All VASPs |
| `kycProfile.customerRiskRating` | FATF R.1 (RBA) | All obliged entities |
| `kycProfile.dueDiligenceType` | FATF R.10 (CDD) | All obliged entities |
| `kycProfile.sanctionsScreening` | FATF R.6 | All obliged entities |
| `kycProfile.beneficialOwnership[]` | FATF R.24/R.25 | Legal persons and arrangements |
| `kycProfile.monitoringInfo` | FATF R.10 (ongoing monitoring) | All obliged entities |

### Tier 2 — AMLR 2027

| Field | AMLR Article | Deadline |
|---|---|---|
| `kycProfile.pepStatus` | Art. 28–31 | 1 July 2027 |
| `kycProfile.sourceOfFundsWealth` | Art. 29 (EDD) | 1 July 2027 |
| `kycProfile.thirdPartyCDDReliance` | Art. 48 | 1 July 2027 |
| `kycProfile.auditMetadata.dataRetentionDate` | Art. 56 (5-year retention) | 1 July 2027 |
| `gdprSensitivityMetadata.tippingOffProtected` | Art. 73 | 1 July 2027 |
| `kycProfile.beneficialOwnership[].intermediateEntities[]` | Art. 26 (full chain) | 1 July 2027 |

### Tier 3 — EDD / High-Risk

Required when `kycProfile.dueDiligenceType` = `EDD` or `kycProfile.customerRiskRating` = `VERY_HIGH`:

| Field | EDD Trigger | Notes |
|---|---|---|
| `kycProfile.sourceOfFundsWealth` | PEP, high-risk country, complex structure | Mandatory source of funds narrative |
| `kycProfile.beneficialOwnership[].nomineeFlags` | Nominee arrangements identified | FATF R.24 (2022 rev.) |
| `kycProfile.beneficialOwnership[].trustInstrumentReference` | Trust/foundation structures | FATF R.25 (2022 rev.) |
| `kycProfile.monitoringInfo.alertFrequency` | EDD = REAL_TIME or DAILY recommended | Ongoing monitoring intensity |
| `kycProfile.monitoringInfo.ruleTriggerHistory[]` | All EDD customers | Audit trail for SAR/STR decisions |

### Tier 4 — PredictiveAML (EU AI Act)

Required when deploying AI-based AML scoring:

| Field | EU AI Act Article | Notes |
|---|---|---|
| `predictiveAML.modelMetadata.euAiActClassification` | Art. 6(2) + Annex III | Mandatory classification |
| `predictiveAML.modelMetadata.conformityAssessmentReference` | Art. 43 | Required for `high-risk-aml` classification |
| `predictiveAML.predictiveScores[].confidence` | Art. 13(3)(b)(ii) | Per-score confidence mandatory |
| `predictiveAML.explainability` | Art. 13(3)(b)(iii) | Output interpretation mandatory |
| `predictiveAML.dataAggregationMetadata.bcbs239ComplianceLevel` | BCBS 239 / supervisory expectation | Mandatory for G-SIBs and D-SIBs |

### Tier 5 — XRPL / Blockchain

Required for XRPL-based VASPs and token issuers:

| Field | Standard | When Required |
|---|---|---|
| `kycProfile.blockchainAccountIds[].xrplCredentialType` | XLS-70 | XRPL Credential-gated operations |
| `kycProfile.blockchainAccountIds[].mptIssuanceId` | XLS-33d (MPT) | MPT holder authorisation |
| `kycProfile.blockchainAccountIds[].xrplPermissionedDomainId` | XLS-80d | Permissioned domain participation |
| `kycProfile.blockchainAccountIds[].xrplAuthorizedCredentialTypes[]` | XLS-80d | Domain-level credential acceptance |
| `kycProfile.blockchainAccountIds[].xrplConfidentialTransfer` | XLS-96d | Confidential transaction compliance |
| `kycProfile.blockchainAccountIds[].xrplFreezeType` | XRPL freeze mechanism | Sanctions enforcement status |
| `kycProfile.blockchainAccountIds[].xrplClawbackEnabled` | XRPL clawback | Regulatory seizure capability |
| `kycProfile.blockchainAccountIds[].lightningNodePubkey` | Lightning Network / FATF R.16 | Lightning VASP Travel Rule |
| `kycProfile.blockchainAccountIds[].bitcoinScriptType` | Bitcoin UTXO analytics | Chain analytics integration |

### Gap Analysis Summary by Entity Type

| Entity Type | Minimum Tier | Recommended Tier |
|---|---|---|
| Non-EU VASP (Travel Rule only) | Tier 1 | Tier 1 |
| EU CASP / VASP (MiCA + AMLR) | Tier 2 | Tier 3 |
| EU Bank (AMLR 2027) | Tier 2 | Tier 3–4 |
| G-SIB / D-SIB | Tier 2 | Tier 4 (BCBS 239) |
| XRPL VASP / MPT issuer | Tier 1 + Tier 5 | Tier 2 + Tier 5 |
| AI-driven AML platform | Tier 4 | Tier 4 (mandatory) |
