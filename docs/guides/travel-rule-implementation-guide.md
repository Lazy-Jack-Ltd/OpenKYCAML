# Travel Rule Implementation Guide

This guide explains how to embed and exchange **OpenKYCAML** payloads across the major Travel Rule protocols used by VASPs worldwide: **TRISA**, **OpenVASP**, **Notabene / DAP**, **TRP (Travel Rule Protocol / SWIFT)**, and **Sygna Bridge**.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Protocol Comparison](#2-protocol-comparison)
3. [TRISA (Travel Rule Information Sharing Architecture)](#3-trisa)
4. [OpenVASP](#4-openvasp)
5. [Notabene / DAP (Digital Asset Protocol)](#5-notabene--dap)
6. [TRP — SWIFT Travel Rule Protocol](#6-trp--swift-travel-rule-protocol)
7. [Sygna Bridge](#7-sygna-bridge)
8. [Protocol-Agnostic Best Practices](#8-protocol-agnostic-best-practices)
9. [Decision Guide: Choosing a Protocol](#9-decision-guide-choosing-a-protocol)
10. [XRPL Domain-Gating and Permissioned DEX Integration](#10-xrpl-domain-gating-and-permissioned-dex-integration)

---

## 1. Overview

The **FATF Recommendation 16** ("Travel Rule") requires VASPs to pass originator and beneficiary information alongside virtual asset transfers. The **EU Funds Transfer Regulation (TFR) 2023** and **MiCA Article 83** extend this to all crypto-asset transactions above €0 for EU-regulated entities.

OpenKYCAML is **protocol-neutral**: it defines *what* data to carry, not *how* to transport it. The `ivms101` block inside an OpenKYCAML payload is already the IVMS 101 data format that most Travel Rule protocols require. The `kycProfile` and `verifiableCredential` sections are optional enrichment layers.

### Integration Pattern

```
Originating VASP                              Beneficiary VASP
┌─────────────────┐   Travel Rule Protocol   ┌─────────────────┐
│  OpenKYCAML     │ ──────────────────────►  │  OpenKYCAML     │
│  ┌───────────┐  │   (TRISA / OpenVASP /    │  ┌───────────┐  │
│  │ ivms101   │  │    Notabene / TRP /       │  │ ivms101   │  │
│  │ kycProfile│  │    Sygna Bridge)          │  │ kycProfile│  │
│  │ vc (opt.) │  │                           │  │ vc (opt.) │  │
│  └───────────┘  │                           │  └───────────┘  │
└─────────────────┘                           └─────────────────┘
```

The **minimum required** OpenKYCAML fields for any Travel Rule exchange are the fields within `ivms101` that satisfy FATF Rec 16 / TFR 2023. See [Use Case 1 in the Adoption Guide](adoption-guide.md#2-use-case-1-travel-rule-vasp).

---

## 2. Protocol Comparison

| Feature | TRISA | OpenVASP | Notabene / DAP | TRP (SWIFT) | Sygna Bridge |
|---|---|---|---|---|---|
| **Governance** | Open protocol (TRISA WG) | Open standard (OpenVASP) | Managed service + open protocol | SWIFT consortium | CoolBitX commercial |
| **Data format** | Protocol Buffers (IVMS 101) | JSON (IVMS 101) | JSON (IVMS 101) | JSON / ISO 20022 | JSON (IVMS 101) |
| **Transport** | mTLS + gRPC | P2P HTTPS | API (Notabene gateway) | SWIFT network | API (Sygna gateway) |
| **VASP discovery** | TRISA Directory Service | OpenVASP Directory | Notabene Directory | SWIFT BIC/LEI | Sygna Network |
| **Encryption** | Envelope encryption (RSA/AES) | ECIES | TLS + API key | SWIFT PKI | ECIES |
| **OpenKYCAML embedding** | `ivms101` block → `IdentityPayload` | `ivms101` block → `VASP Identity` | `ivms101` block → `ivms` field | `ivms101` block → `data.ivms101` | `ivms101` block → `private_info` |
| **eIDAS 2.0 / EUDI Wallet** | Via `kycProfile` + VC extension | Custom extension | Not natively | Not natively | Not natively |

---

## 3. TRISA

### Overview
[TRISA](https://trisa.io) (Travel Rule Information Sharing Architecture) is an open-source, peer-to-peer protocol using mutual TLS (mTLS) for authentication and gRPC for message transport. VASPs register in the TRISA Global Directory Service (GDS) and communicate directly without a central intermediary.

### How to embed OpenKYCAML

TRISA uses Protocol Buffers. The `ivms101` block in your OpenKYCAML payload maps directly to the TRISA `IdentityPayload` message's `originator` and `beneficiary` fields, which are typed as IVMS 101 protobuf messages.

**Step 1: Extract the IVMS 101 block**

```python
from tools.python.converter import openkycaml_to_ivms101
import json

with open("my-payload.json") as f:
    payload = json.load(f)

ivms = openkycaml_to_ivms101(payload)
```

**Step 2: Map to TRISA IdentityPayload**

```json
{
  "originator": {
    "originatorPersons": [...],
    "accountNumber": ["0x..."]
  },
  "beneficiary": {
    "beneficiaryPersons": [...],
    "accountNumber": ["0x..."]
  },
  "originating_vasp": {
    "originating_vasp": {
      "name": { "name_identifier": [{"legal_person_name": "...", "legal_person_name_identifier_type": "LEGL"}] },
      "national_identification": { "national_identifier": "LEI...", "national_identifier_type": "LEIX" }
    }
  }
}
```

> **Note:** TRISA protobuf field names are `snake_case` (protobuf convention) whereas IVMS 101 JSON uses `camelCase`. TRISA SDKs handle the serialization automatically.

**Step 3: Attach kycProfile as TRISA extra data (optional)**

TRISA supports an `extra_json` field in the `SecureEnvelope` for additional data. Include the `kycProfile` JSON-encoded string here if sharing risk ratings or screening results with a trusted counterparty.

**Step 4: Send via TRISA**

Use the [TRISA Python SDK](https://github.com/trisacrypto/trisa) or [Go SDK](https://pkg.go.dev/github.com/trisacrypto/trisa):

```python
from trisa.api.v1beta1 import trisa_pb2_grpc, trisa_pb2
import grpc

channel = grpc.secure_channel("counterparty.vasp.example.com:443", credentials)
stub = trisa_pb2_grpc.TRISANetworkStub(channel)
response = stub.Transfer(trisa_pb2.SecureEnvelope(...))
```

### Key References
- TRISA spec: https://trisa.dev/
- TRISA Global Directory: https://vaspdirectory.net/
- IVMS 101 protobuf definitions: https://github.com/trisacrypto/trisa/tree/main/pkg/ivms101

---

## 4. OpenVASP

### Overview
[OpenVASP](https://openvasp.org) is an open, P2P JSON-based protocol for Travel Rule compliance. It uses the Ethereum Whisper / Waku transport layer (or HTTPS) and VASP discovery via the Ethereum blockchain (VASP Index smart contract). It does not require a central directory authority.

### How to embed OpenKYCAML

The OpenVASP VASP Information message (`vaan`, `vasp`, `originator`, `beneficiary`) maps directly to the OpenKYCAML `ivms101` block.

**OpenVASP Session Request (Transfer Request) — payload structure:**

```json
{
  "msg": {
    "type": "110",
    "msgid": "<uuid>",
    "session": "<session-id>",
    "code": "1"
  },
  "originator": {
    "vaan": "0x<originator-vaan>",
    "ivms101": {
      "originator": "<extracted ivms101.originator>",
      "originatingVasp": "<extracted ivms101.originatingVASP>"
    }
  },
  "beneficiary": {
    "vaan": "0x<beneficiary-vaan>"
  },
  "transfer": {
    "va": "ETH",
    "ttype": "blockchain",
    "amount": "0.15"
  }
}
```

**Embedding the OpenKYCAML ivms101 block:**

```python
from tools.python.converter import openkycaml_to_ivms101
import json

with open("my-payload.json") as f:
    payload = json.load(f)

ivms = openkycaml_to_ivms101(payload)

openvasp_request = {
    "msg": {"type": "110", "msgid": payload["messageId"], "session": "<session>", "code": "1"},
    "originator": {
        "vaan": "0x<vaan>",
        "ivms101": {
            "originator": ivms.get("originator"),
            "originatingVasp": {"originatingVasp": ivms.get("originatingVASP")}
        }
    },
    "beneficiary": {"vaan": "0x<beneficiary-vaan>"},
    "transfer": {
        "va": ivms.get("transferredAmount", {}).get("assetType", ""),
        "ttype": "blockchain",
        "amount": ivms.get("transferredAmount", {}).get("amount", "")
    }
}
```

### Key References
- OpenVASP specification: https://github.com/OpenVASP/ovips
- OVIP-0009 (IVMS 101 mapping): https://github.com/OpenVASP/ovips/blob/master/ovip-0009.md

---

## 5. Notabene / DAP

### Overview
[Notabene](https://notabene.id) provides a managed Travel Rule network accessible via REST API. The underlying data format is IVMS 101. Notabene also supports the **Digital Asset Protocol (DAP)** for beneficiary VASP discovery using `@` addressing (e.g. `alice@vasp.com`).

### How to embed OpenKYCAML

Notabene's `/transfers` API accepts an `ivms` field containing the IVMS 101 payload.

**API Request:**

```bash
POST https://api.notabene.id/api/v1/transfers
Authorization: Bearer <api_key>
Content-Type: application/json
```

```json
{
  "transaction_asset": "ETH",
  "transaction_amount": "150000000000000000",
  "origin_vasp_did": "did:ethr:0x...",
  "origin_address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
  "destination_vasp_did": "did:ethr:0x...",
  "destination_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
  "ivms101": {
    "originator": { ... },
    "beneficiary": { ... },
    "originatingVASP": { ... },
    "beneficiaryVASP": { ... }
  }
}
```

**Extracting the ivms101 block for Notabene:**

```python
from tools.python.converter import openkycaml_to_ivms101
import json, requests

with open("my-payload.json") as f:
    payload = json.load(f)

ivms = openkycaml_to_ivms101(payload)

notabene_body = {
    "transaction_asset": ivms.get("transferredAmount", {}).get("assetType"),
    "origin_address": ivms.get("originator", {}).get("accountNumber", [None])[0],
    "destination_address": ivms.get("beneficiary", {}).get("accountNumber", [None])[0],
    "ivms101": ivms
}

response = requests.post(
    "https://api.notabene.id/api/v1/transfers",
    headers={"Authorization": "Bearer <api_key>"},
    json=notabene_body
)
```

### Key References
- Notabene API docs: https://docs.notabene.id/
- DAP specification: https://dap.dev/

---

## 6. TRP — SWIFT Travel Rule Protocol

### Overview
[TRP](https://github.com/travelruleprotocol) (Travel Rule Protocol) is a REST-based open protocol initially developed by a consortium of crypto companies and later aligned with SWIFT's network. It is widely used by regulated institutions and custodians that also participate in the SWIFT network.

### How to embed OpenKYCAML

TRP messages use JSON and accept IVMS 101-structured originator/beneficiary data. The `ivms101` block maps to the `ivmsData` field in the TRP transfer request.

**TRP Transfer Request:**

```json
{
  "assetType": "ETH",
  "transactionIdentifier": "<tx-hash>",
  "originatorAssetTransferReference": "0x71C7...",
  "beneficiaryAssetTransferReference": "0xd8dA...",
  "ivmsData": {
    "originator": { ... },
    "beneficiary": { ... },
    "originatingVasp": {
      "originatingVasp": {
        "name": { "nameIdentifier": [{"legalPersonName": "...", "legalPersonNameIdentifierType": "LEGL"}] },
        "nationalIdentification": { "nationalIdentifier": "...", "nationalIdentifierType": "LEIX" }
      }
    },
    "beneficiaryVasp": { ... }
  }
}
```

**Extracting for TRP:**

```python
from tools.python.converter import openkycaml_to_ivms101
import json

with open("my-payload.json") as f:
    payload = json.load(f)

ivms = openkycaml_to_ivms101(payload)

trp_body = {
    "assetType": ivms.get("transferredAmount", {}).get("assetType"),
    "transactionIdentifier": payload.get("messageId"),
    "originatorAssetTransferReference": ivms.get("originator", {}).get("accountNumber", [None])[0],
    "beneficiaryAssetTransferReference": ivms.get("beneficiary", {}).get("accountNumber", [None])[0],
    "ivmsData": ivms
}
```

**ISO 20022 output (for SWIFT-connected entities):**

For financial institutions transmitting via the SWIFT network, use the ISO 20022 integration library to produce a standards-compliant pacs.008 XML message with the full KYC/AML envelope embedded in `<SplmtryData>`:

```python
import sys
sys.path.insert(0, "iso20022-integration/libraries/python")
from converter import openkycaml_to_pacs008

with open("my-payload.json") as f:
    payload = json.load(f)

# Returns a complete pacs.008 XML string with KYCAMLEnvelope in <SplmtryData>
pacs008_xml = openkycaml_to_pacs008(payload)
```

For pain.001 (customer credit transfer initiation):

```python
from converter import openkycaml_to_pain001
pain001_xml = openkycaml_to_pain001(payload)
```

See [`iso20022-integration/`](../../iso20022-integration/) for the full library, XML examples, and pre-validated profiles.

### Key References
- TRP GitHub: https://github.com/travelruleprotocol
- TRP specification: https://travelruleprotocol.org/

---

## 7. Sygna Bridge

### Overview
[Sygna Bridge](https://www.sygna.io) is a commercial Travel Rule compliance network operated by CoolBitX. It provides an API-based hub model with ECIES encryption for permissioned information exchange between registered VASPs.

### How to embed OpenKYCAML

Sygna uses a `private_info` field that is ECIES-encrypted and contains the IVMS 101 originator/beneficiary data.

**Sygna Transfer Request (before encryption):**

```json
{
  "originator": {
    "originator_persons": [
      {
        "natural_person": {
          "name": {
            "name_identifier": [{"primary_identifier": "...", "secondary_identifier": "...", "name_identifier_type": "LEGL"}]
          },
          "national_identification": { ... },
          "date_and_place_of_birth": { ... }
        }
      }
    ],
    "account_number": ["0x..."]
  },
  "beneficiary": { ... }
}
```

> **Note:** Sygna uses `snake_case` IVMS 101 field names (matching the protobuf convention), while OpenKYCAML uses `camelCase` (matching IVMS 101 JSON). Conversion is required.

**Sygna field mapping from OpenKYCAML:**

```python
def camel_to_snake(d):
    """Recursively convert camelCase keys to snake_case for Sygna."""
    import re
    if isinstance(d, dict):
        return {
            re.sub(r'(?<!^)(?=[A-Z])', '_', k).lower(): camel_to_snake(v)
            for k, v in d.items()
        }
    elif isinstance(d, list):
        return [camel_to_snake(i) for i in d]
    return d

from tools.python.converter import openkycaml_to_ivms101
ivms = openkycaml_to_ivms101(payload)
sygna_private_info = camel_to_snake(ivms)
```

### Key References
- Sygna Bridge API docs: https://developers.sygna.io/

---

## 8. Protocol-Agnostic Best Practices

### Always validate before sending

```python
from tools.python.validator import OpenKYCAMLValidator

validator = OpenKYCAMLValidator()
result = validator.validate(payload)
if not result.is_valid:
    raise ValueError(f"Payload invalid: {result.errors}")
```

### Generate a unique messageId per transfer

Each OpenKYCAML message MUST have a unique `messageId` (UUID v4). Never reuse message IDs across transfers.

```python
import uuid
payload["messageId"] = str(uuid.uuid4())
```

### Timestamp in UTC ISO 8601

```python
from datetime import datetime, timezone
payload["messageDateTime"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
```

### FATF-minimum field checklist

Before transmitting, verify the IVMS 101 block contains at minimum:

**Natural person originator:**
- [ ] `name.nameIdentifier[0].primaryIdentifier` (family name)
- [ ] `name.nameIdentifier[0].secondaryIdentifier` (given names)
- [ ] `name.nameIdentifier[0].nameIdentifierType = "LEGL"`
- [ ] ONE of: `nationalIdentification`, `dateAndPlaceOfBirth.dateOfBirth`, or `geographicAddress`
- [ ] `accountNumber[0]`
- [ ] `originatingVASP` name and identifier

**Legal entity originator:**
- [ ] `name.nameIdentifier[0].legalPersonName`
- [ ] `name.nameIdentifier[0].legalPersonNameIdentifierType = "LEGL"`
- [ ] `nationalIdentification.nationalIdentifier` (LEI preferred: `nationalIdentifierType = "LEIX"`)
- [ ] `countryOfRegistration`
- [ ] `accountNumber[0]`
- [ ] `originatingVASP` name and identifier

### EUDI Wallet evidence preservation

When an EUDI Wallet PID was used for identity verification, include the `evidence` block in the `verifiableCredential` to preserve the audit trail of which PID Provider attested the identity:

```json
"evidence": [
  {
    "type": ["PIDCredential", "EUDIWalletPresentationEvidence"],
    "verifier": "did:web:<your-vasp>",
    "credentialIssuer": "did:web:<pid-provider>",
    "presentationMethod": "OpenID4VP",
    "presentationDate": "2025-09-10T10:57:00Z"
  }
]
```

For SD-JWT VC presentations, set `"presentationMethod": "OpenID4VP+SD-JWT"` and include `selectiveDisclosure` metadata.

### Counterparty verification

Before sending sensitive KYC data, verify the counterparty VASP's identity:

| Protocol | Verification method |
|---|---|
| TRISA | mTLS certificate chain to TRISA GDS root CA |
| OpenVASP | VASP Index smart contract on Ethereum mainnet |
| Notabene | Notabene directory (DID-based) |
| TRP | Manual certificate exchange + TRP directory |
| Sygna | Sygna network registration |

---

## 9. Decision Guide: Choosing a Protocol

```
Is your counterparty already on a specific network?
  └─ Yes → use that network's protocol
  └─ No ─→ Continue below

Are you a bank or traditional FI also connected to SWIFT?
  └─ Yes → TRP (aligns with ISO 20022, SWIFT infrastructure)
  └─ No ─→ Continue below

Do you need a managed service with support?
  └─ Yes → Notabene / DAP or Sygna Bridge
  └─ No ─→ Continue below

Do you prefer a fully open, decentralised, self-hosted approach?
  └─ Yes → TRISA (PKI-based, open-source SDKs) or OpenVASP (Ethereum-based)

Regulatory preference:
  FATF guidance (global)    → all protocols comply
  EU TFR 2023 / MiCA        → all protocols comply; eIDAS 2.0 EUDI Wallet
                               enrichment available via OpenKYCAML VC layer
  US FinCEN Travel Rule      → TRISA and Notabene have strong US adoption
  APAC regulators            → Sygna Bridge strong in Asia-Pacific
```

> **Multi-protocol tip:** Because OpenKYCAML separates data format from transport, you can run a single internal OpenKYCAML record and fan out to multiple protocol networks simultaneously by extracting and transforming the `ivms101` block as shown in each section above.

---

## 10. XRPL Domain-Gating and Permissioned DEX Integration

When a counterparty transacts on the **XRP Ledger**, Travel Rule data delivery may need to be co-ordinated with XRPL's protocol-level compliance gates. This section describes the integration pattern for VASPs that interact with XRPL accounts enrolled in a **Permissioned Domain** (XLS-80) and/or a **Permissioned DEX** (XLS-81d).

### 10.1 What is an XRPL Permissioned Domain?

An XRPL Permissioned Domain (XLS-80) is an on-ledger object that restricts DEX access, lending protocols, or other XRPL primitives to accounts holding specific on-chain credentials (XLS-70). The domain operator specifies a set of accepted `CredentialType` hex values; only accounts holding a matching, non-expired credential may participate.

Field mapping:

| OpenKYCAML Field | XRPL On-Ledger Object | Meaning |
|---|---|---|
| `blockchainAccountIds[].xrplPermissionedDomainId` | `DomainID` (Hash256) | Identifies the Permissioned Domain gate |
| `blockchainAccountIds[].xrplAuthorizedCredentialTypes[]` | `AcceptedCredentials[].CredentialType` | Credential types accepted in this domain (cross-ref XLS-70) |
| `blockchainAccountIds[].xrplCredentialType` | `Credential.CredentialType` | The credential held by this wallet anchoring the KYC/AML proof |
| `kycProfile.isEligible` | Derived from credential validity + domain check | Eligibility gate — `true` only if credential is valid and accepted by domain |

### 10.2 Integration Steps

**Step 1 — Identify the Permissioned Domain**

Before initiating a Travel Rule exchange for an XRPL-originated or XRPL-destined transfer, determine whether the originator or beneficiary wallet is a member of a Permissioned Domain:

```
GET /v1/ledger/accounts/{rAddress}/domains    (XRPL REST gateway)
```

If a `DomainID` is returned, record it in `blockchainAccountIds[].xrplPermissionedDomainId`.

**Step 2 — Retrieve accepted credential types**

Fetch the domain's `AcceptedCredentials` list and record the matching `CredentialType` hex strings in `xrplAuthorizedCredentialTypes[]`. Cross-reference these against the wallet's live `Credential` objects to confirm that `xrplCredentialType` is in the accepted set.

**Step 3 — Set isEligible**

Set `kycProfile.isEligible: true` only when:
1. The wallet holds a valid (non-expired, non-revoked) XLS-70 credential whose `CredentialType` is in `xrplAuthorizedCredentialTypes[]`.
2. The credential's subject matches the KYC record subject (IVMS 101 name + national ID).
3. No open sanctions hit, freeze, or clawback applies.

**Step 4 — Include domain fields in Travel Rule payload**

Embed the XRPL-specific fields in the OpenKYCAML payload alongside the IVMS 101 block:

```json
{
  "$schema": "https://openkycaml.org/schema/v1.7.0/kyc-aml-hybrid-extended.json",
  "version": "1.7.0",
  "ivms101": { "...": "..." },
  "kycProfile": {
    "customerRiskRating": "LOW",
    "dueDiligenceType": "CDD",
    "isEligible": true,
    "eligibilityLastConfirmed": "2026-04-06T18:00:00Z",
    "blockchainAccountIds": [
      {
        "address": "rCustomerXRPLAddress...",
        "network": "xrpl",
        "xrplCredentialType": "4b594343726564656e7469616c",
        "xrplPermissionedDomainId": "A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F60001",
        "xrplAuthorizedCredentialTypes": ["4b594343726564656e7469616c"],
        "isFrozen": false,
        "xrplClawbackEnabled": false
      }
    ]
  }
}
```

**Step 5 — Beneficiary VASP verification**

The beneficiary VASP should:
1. Re-verify the wallet's credential status on XRPL using a local rippled or Clio node (do not rely solely on the originator's `isEligible` flag).
2. Confirm the `xrplPermissionedDomainId` value matches their own domain registration if they operate a domain gate.
3. Reject the payload and escalate for review if `isEligible: false` or if the credential has expired.

### 10.3 Permissioned DEX (XLS-81d)

XLS-81d restricts DEX offer matching to domain members. No additional schema fields are required beyond those in §10.1 — domain membership established by `xrplPermissionedDomainId` and `isEligible` together gates DEX participation.

Key points for compliance teams:
- Secondary market trading of a permissioned MPT via the XRPL DEX requires the trading wallet to be a domain member (`xrplPermissionedDomainId` set and `isEligible: true`).
- In combination with `lsfMPTRequireAuth` MPT flag (bitfield 0x0004 in `mptFlags`), issuers can require both KYC verification *and* domain membership before any MPT transfer settles.
- `isEligible: false` combined with an `xrplFreezeType` of `INDIVIDUAL_FREEZE` or `DEEP_FREEZE` indicates a holder who was previously eligible but has been suspended — flag for EDD review.
