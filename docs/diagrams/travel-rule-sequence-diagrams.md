# Travel Rule Message Flow — Sequence Diagrams

This document contains Mermaid sequence diagrams for the five major Travel Rule protocols supported by OpenKYCAML: **TRISA**, **OpenVASP**, **Notabene / DAP**, **TRP (SWIFT)**, and **Sygna Bridge**.

For protocol integration code, see the [Travel Rule Implementation Guide](../guides/travel-rule-implementation-guide.md).

---

## Table of Contents

1. [Generic OpenKYCAML Travel Rule Flow](#1-generic-openkycaml-travel-rule-flow)
2. [TRISA Flow](#2-trisa-flow)
3. [OpenVASP Flow](#3-openvasp-flow)
4. [Notabene / DAP Flow](#4-notabene--dap-flow)
5. [TRP — SWIFT Travel Rule Protocol Flow](#5-trp--swift-travel-rule-protocol-flow)
6. [Sygna Bridge Flow](#6-sygna-bridge-flow)
7. [eIDAS 2.0 EUDI Wallet Enhanced Travel Rule Flow](#7-eidas-20-eudi-wallet-enhanced-travel-rule-flow)

---

## 1. Generic OpenKYCAML Travel Rule Flow

The following diagram shows the protocol-agnostic exchange pattern common to all Travel Rule integrations using OpenKYCAML.

```mermaid
sequenceDiagram
    autonumber
    participant Customer as Customer
    participant OrigVASP as Originating VASP
    participant BeneVASP as Beneficiary VASP

    Customer->>OrigVASP: Initiate virtual asset transfer
    OrigVASP->>OrigVASP: Build OpenKYCAML payload\n(ivms101 + optional kycProfile/VC)
    OrigVASP->>OrigVASP: Validate payload against\nOpenKYCAML schema v1.7.0
    OrigVASP->>BeneVASP: Transmit OpenKYCAML payload\n(via Travel Rule protocol)
    BeneVASP->>BeneVASP: Validate received payload
    BeneVASP->>BeneVASP: Screen originator (PEP/sanctions)
    alt Beneficiary VASP accepts
        BeneVASP-->>OrigVASP: ACK / confirmation
        OrigVASP->>OrigVASP: Execute blockchain transaction
        OrigVASP-->>Customer: Transfer complete
    else Beneficiary VASP rejects
        BeneVASP-->>OrigVASP: NACK / rejection with reason
        OrigVASP-->>Customer: Transfer rejected
    end
```

---

## 2. TRISA Flow

TRISA uses mutual TLS (mTLS) and gRPC. VASPs register in the TRISA Global Directory Service (GDS). The OpenKYCAML `ivms101` block maps directly to the TRISA `IdentityPayload` protobuf message.

```mermaid
sequenceDiagram
    autonumber
    participant Customer as Customer
    participant OrigVASP as Originating VASP
    participant GDS as TRISA GDS
    participant BeneVASP as Beneficiary VASP
    participant Blockchain as Blockchain

    Customer->>OrigVASP: Initiate transfer with asset amount and beneficiary address
    OrigVASP->>GDS: Lookup beneficiary VASP by address or DID
    GDS-->>OrigVASP: Return beneficiary VASP endpoint and mTLS certificate
    OrigVASP->>OrigVASP: Build OpenKYCAML payload and extract ivms101 block
    OrigVASP->>OrigVASP: Encrypt payload in TRISA SecureEnvelope using RSA AES
    OrigVASP->>BeneVASP: Send gRPC transfer with SecureEnvelope over mTLS
    BeneVASP->>BeneVASP: Decrypt SecureEnvelope and validate ivms101
    BeneVASP->>BeneVASP: Screen originator
    BeneVASP-->>OrigVASP: Return gRPC transfer response with sealed SecureEnvelope
    OrigVASP->>Blockchain: Broadcast transaction
    Blockchain-->>OrigVASP: Transaction hash confirmed
    OrigVASP-->>Customer: Transfer complete
```

---

## 3. OpenVASP Flow

OpenVASP is a peer-to-peer JSON protocol using Ethereum-based VASP discovery (VASP Index smart contract) and Whisper/Waku or HTTPS transport.

```mermaid
sequenceDiagram
    autonumber
    participant Customer as Customer
    participant OrigVASP as Originating VASP
    participant EthIndex as Ethereum VASP Index
    participant BeneVASP as Beneficiary VASP
    participant Blockchain as Blockchain

    Customer->>OrigVASP: Initiate transfer
    OrigVASP->>EthIndex: Resolve beneficiary VASP from destination address VAAN
    EthIndex-->>OrigVASP: Return beneficiary VASP metadata with transport endpoint and signing key
    OrigVASP->>OrigVASP: Build OpenKYCAML payload and extract ivms101 block
    OrigVASP->>BeneVASP: Send session request type 110 with originator ivms101 and VAAN
    BeneVASP-->>OrigVASP: Return session reply type 150 with beneficiary ivms101
    OrigVASP->>OrigVASP: Validate beneficiary details
    OrigVASP->>BeneVASP: Transfer Request (type 210)
    BeneVASP-->>OrigVASP: Transfer Reply (type 250) — accept/reject
    alt Transfer accepted
        OrigVASP->>Blockchain: Broadcast transaction
        Blockchain-->>OrigVASP: Confirmation
        OrigVASP->>BeneVASP: Send transfer dispatch type 310 with transaction hash
        BeneVASP-->>OrigVASP: Transfer Confirmation (type 350)
        OrigVASP-->>Customer: Transfer complete
    else Transfer rejected
        OrigVASP-->>Customer: Transfer rejected
    end
```

---

## 4. Notabene / DAP Flow

Notabene provides a managed Travel Rule API. The originating VASP posts the IVMS 101 payload via REST. Beneficiary VASP discovery uses DAP (`@` addressing) or the Notabene directory.

```mermaid
sequenceDiagram
    autonumber
    participant Customer as Customer
    participant OrigVASP as Originating VASP
    participant NotabeneAPI as Notabene API
    participant BeneVASP as Beneficiary VASP
    participant Blockchain as Blockchain

    Customer->>OrigVASP: Initiate transfer
    OrigVASP->>OrigVASP: Build OpenKYCAML payload and extract ivms101 block
    OrigVASP->>NotabeneAPI: Post transfer request with ivms101 and origin and destination addresses
    NotabeneAPI->>NotabeneAPI: Resolve beneficiary VASP via Notabene directory or DAP
    NotabeneAPI->>BeneVASP: Forward travel rule request with JSON ivms101 payload
    BeneVASP->>BeneVASP: Screen originator and validate data
    BeneVASP-->>NotabeneAPI: Return accepted or rejected response
    NotabeneAPI-->>OrigVASP: Transfer status update
    alt Accepted
        OrigVASP->>Blockchain: Broadcast transaction
        Blockchain-->>OrigVASP: Confirmation
        OrigVASP->>NotabeneAPI: Patch transfer with transaction hash
        OrigVASP-->>Customer: Transfer complete
    else Rejected
        OrigVASP-->>Customer: Transfer rejected
    end
```

---

## 5. TRP — SWIFT Travel Rule Protocol Flow

TRP is a REST-based protocol aligned with SWIFT. Financial institutions using SWIFT can additionally produce ISO 20022 pacs.008 XML with the OpenKYCAML envelope embedded in `<SplmtryData>`.

```mermaid
sequenceDiagram
    autonumber
    participant Customer as Customer
    participant OrigVASP as Originating VASP / FI
    participant TRPDir as TRP Directory
    participant BeneVASP as Beneficiary VASP / FI
    participant Blockchain as Blockchain

    Customer->>OrigVASP: Initiate transfer
    OrigVASP->>TRPDir: Resolve beneficiary VASP endpoint
    TRPDir-->>OrigVASP: Endpoint URL + public key
    OrigVASP->>OrigVASP: Build OpenKYCAML payload and map ivms101 to ivmsData
    Note over OrigVASP: Optional pacs.008 XML can be produced via ISO 20022 converter
    OrigVASP->>BeneVASP: Post transfer with asset type ivmsData originator reference and beneficiary reference
    BeneVASP->>BeneVASP: Validate ivmsData and screen originator
    BeneVASP-->>OrigVASP: Return accepted response or rejected response
    alt Accepted
        OrigVASP->>Blockchain: Broadcast transaction
        Blockchain-->>OrigVASP: Confirmation
        OrigVASP->>BeneVASP: Patch transfer with transaction hash and completed status
        OrigVASP-->>Customer: Transfer complete
    else Rejected
        OrigVASP-->>Customer: Transfer rejected
    end
```

---

## 6. Sygna Bridge Flow

Sygna Bridge is a commercial hub operated by CoolBitX. VASP-to-VASP data is ECIES-encrypted and routed via the Sygna Bridge API. Sygna uses `snake_case` IVMS 101 field names (protobuf convention); the OpenKYCAML converter handles the camelCase → snake_case transformation.

```mermaid
sequenceDiagram
    autonumber
    participant Customer as Customer
    participant OrigVASP as Originating VASP
    participant SygnaAPI as Sygna Bridge API
    participant BeneVASP as Beneficiary VASP
    participant Blockchain as Blockchain

    Customer->>OrigVASP: Initiate transfer
    OrigVASP->>OrigVASP: Build OpenKYCAML payload extract ivms101 and convert camelCase to snake_case
    OrigVASP->>SygnaAPI: Get beneficiary VASP ECIES key
    SygnaAPI-->>OrigVASP: Beneficiary VASP public key
    OrigVASP->>OrigVASP: Encrypt private_info with ECIES using ivms101 snake_case data
    OrigVASP->>SygnaAPI: Post permission request with encrypted private_info and metadata
    SygnaAPI->>BeneVASP: Forward permission request
    BeneVASP->>BeneVASP: Decrypt private_info then validate and screen originator
    BeneVASP-->>SygnaAPI: Post permission result accepted or rejected
    SygnaAPI-->>OrigVASP: Permission status
    alt Accepted
        OrigVASP->>Blockchain: Broadcast transaction
        Blockchain-->>OrigVASP: Transaction hash confirmed
        OrigVASP->>SygnaAPI: Post txid with signature
        OrigVASP-->>Customer: Transfer complete
    else Rejected
        OrigVASP-->>Customer: Transfer rejected
    end
```

---

## 7. eIDAS 2.0 EUDI Wallet Enhanced Travel Rule Flow

When the originator has an EUDI Wallet, a PID Verifiable Credential can be included in the OpenKYCAML payload as the `evidence` block, providing high-assurance identity triangulation.

```mermaid
sequenceDiagram
    autonumber
    participant Customer as EUDI Wallet Holder
    participant EUDIWallet as EUDI Wallet
    participant OrigVASP as Originating VASP
    participant BeneVASP as Beneficiary VASP
    participant Blockchain as Blockchain

    Customer->>OrigVASP: Initiate transfer
    OrigVASP->>EUDIWallet: Send OpenID4VP presentation request for PID attributes
    EUDIWallet->>Customer: Show consent prompt for selective disclosure of PID fields
    Customer->>EUDIWallet: Approve disclosure
    EUDIWallet-->>OrigVASP: Return VP token containing PID attributes
    OrigVASP->>OrigVASP: Verify VP signature map PID to ivms101 fields and build OpenKYCAML payload with evidence block
    Note over OrigVASP: Evidence records include PID issuer DID VASP verifier DID presentation method and presentation date
    OrigVASP->>BeneVASP: Transmit OpenKYCAML payload via travel rule protocol
    BeneVASP->>BeneVASP: Validate payload verify evidence chain and screen originator
    BeneVASP-->>OrigVASP: ACK
    OrigVASP->>Blockchain: Broadcast transaction
    Blockchain-->>OrigVASP: Confirmation
    OrigVASP-->>Customer: Transfer complete
```

---

*All diagrams are rendered with [Mermaid](https://mermaid.js.org/). Last updated: v1.12.0.*
