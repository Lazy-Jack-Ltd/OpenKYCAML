# eIDAS 2.0 VC Issuance and Presentation Flows — Sequence Diagrams

This document contains Mermaid sequence diagrams for the eIDAS 2.0 OpenKYCAML Verifiable Credential lifecycle: issuance via **OpenID4VCI** and presentation via **OpenID4VP**.

For narrative integration guidance, see the [EUDI Wallet Integration Guide](../guides/eudi-wallet-integration.md).

---

## Table of Contents

1. [Overview: OpenKYCAML VC Lifecycle](#1-overview-openkycaml-vc-lifecycle)
2. [VC Issuance — OpenID4VCI Pre-Authorised Code Flow](#2-vc-issuance--openid4vci-pre-authorised-code-flow)
3. [VC Issuance — OpenID4VCI Authorisation Code Flow](#3-vc-issuance--openid4vci-authorisation-code-flow)
4. [VC Presentation — OpenID4VP (Same-Device)](#4-vc-presentation--openid4vp-same-device)
5. [VC Presentation — OpenID4VP (Cross-Device / QR Code)](#5-vc-presentation--openid4vp-cross-device--qr-code)
6. [SD-JWT Selective Disclosure Flow](#6-sd-jwt-selective-disclosure-flow)
7. [Credential Status Check (StatusList2021)](#7-credential-status-check-statuslist2021)
8. [PID-Backed OpenKYCAML Issuance (Full EUDI Wallet Onboarding)](#8-pid-backed-openkycaml-issuance-full-eudi-wallet-onboarding)

---

## 1. Overview: OpenKYCAML VC Lifecycle

```mermaid
sequenceDiagram
    autonumber
    participant Holder as EUDI Wallet Holder
    participant Wallet as EUDI Wallet
    participant Issuer as OpenKYCAML Issuer (VASP / KYC Utility)
    participant Verifier as Relying Party (Beneficiary VASP / Bank)

    Note over Holder,Verifier: Phase 1 — Issuance (OpenID4VCI)
    Holder->>Issuer: Complete KYC onboarding
    Issuer->>Issuer: Build and sign OpenKYCAML VC / (SD-JWT VC / VC-JWT)
    Issuer-->>Wallet: Deliver credential / (OpenID4VCI pre-auth or auth flow)
    Wallet->>Wallet: Store credential

    Note over Holder,Verifier: Phase 2 — Presentation (OpenID4VP)
    Verifier->>Wallet: Presentation Request / (select OpenKYCAML VC fields)
    Wallet->>Holder: Consent prompt
    Holder->>Wallet: Approve selective disclosure
    Wallet-->>Verifier: VP Token (SD-JWT VC)
    Verifier->>Verifier: Verify signature, status, issuer
```

---

## 2. VC Issuance — OpenID4VCI Pre-Authorised Code Flow

Used when the issuer pre-approves the credential offer (e.g., after in-person or online KYC). The EUDI Wallet scans a QR code or deep-links to the credential offer URI.

```mermaid
sequenceDiagram
    autonumber
    participant Holder as EUDI Wallet Holder
    participant Wallet as EUDI Wallet
    participant Issuer as OpenKYCAML Issuer
    participant AuthServer as Authorisation Server

    Issuer->>Issuer: KYC completed then build and sign OpenKYCAML VC
    Issuer->>Holder: Send credential offer URI by QR code or deep link
    Holder->>Wallet: Open credential offer
    Wallet->>Issuer: Fetch issuer metadata
    Issuer-->>Wallet: Return issuer metadata and supported credentials
    Wallet->>AuthServer: Request token with pre authorized code
    AuthServer-->>Wallet: Access Token and c_nonce
    Wallet->>Wallet: Generate key bound proof JWT with c_nonce
    Wallet->>Issuer: Request credential with proof JWT
    Issuer->>Issuer: Verify holder key binding and bind VC to wallet key
    Issuer-->>Wallet: Return SD JWT VC credential
    Wallet->>Wallet: Store OpenKYCAML VC
    Wallet-->>Holder: Credential stored
```

---

## 3. VC Issuance — OpenID4VCI Authorisation Code Flow

Used when the holder must authenticate with the issuer before receiving the credential (e.g., existing customer account login).

```mermaid
sequenceDiagram
    autonumber
    participant Holder as EUDI Wallet Holder
    participant Wallet as EUDI Wallet
    participant Issuer as OpenKYCAML Issuer
    participant AuthServer as Authorisation Server

    Holder->>Wallet: Request OpenKYCAML credential from issuer
    Wallet->>Issuer: Fetch issuer metadata
    Issuer-->>Wallet: Issuer Metadata
    Wallet->>AuthServer: Send authorisation request
    AuthServer->>Holder: Authentication and consent screen
    Holder->>AuthServer: Authenticate and approve
    AuthServer-->>Wallet: Return authorisation code
    Wallet->>AuthServer: Exchange authorisation code for token
    AuthServer-->>Wallet: Access Token and c_nonce
    Wallet->>Wallet: Generate key bound proof JWT signed with wallet key
    Wallet->>Issuer: Request credential with proof JWT
    Issuer->>Issuer: Verify proof then build VC and bind to holder key
    Issuer-->>Wallet: Return SD JWT VC credential
    Wallet->>Wallet: Store credential
    Wallet-->>Holder: Credential stored
```

---

## 4. VC Presentation — OpenID4VP (Same-Device)

Used when the verifier and the EUDI Wallet are on the same device (e.g., browser and mobile wallet via universal link).

```mermaid
sequenceDiagram
    autonumber
    participant Holder as EUDI Wallet Holder
    participant Wallet as EUDI Wallet
    participant Verifier as Relying Party (Beneficiary VASP / Bank)

    Holder->>Verifier: Access service requiring KYC
    Verifier->>Verifier: Build Presentation Request / (select ivms101 / kycProfile fields)
    Verifier-->>Wallet: Authorization Request / (openid4vp:// deep link) / {client_id, response_type: vp_token, / presentation_definition}
    Wallet->>Wallet: Locate matching OpenKYCAML VC
    Wallet->>Holder: Consent screen — / show requested fields
    Holder->>Wallet: Approve
    Wallet->>Wallet: Build VP Token / (SD-JWT with selected disclosures)
    Wallet-->>Verifier: POST response_uri / {vp_token, presentation_submission}
    Verifier->>Verifier: Verify VP Token: / 1. SD-JWT signature / 2. Holder key binding / 3. Credential status / 4. Issuer trust chain
    Verifier-->>Holder: Access granted ✓
```

---

## 5. VC Presentation — OpenID4VP (Cross-Device / QR Code)

Used when the relying party is on a desktop browser and the EUDI Wallet is on the holder's mobile device.

```mermaid
sequenceDiagram
    autonumber
    participant Holder as EUDI Wallet Holder
    participant Mobile as EUDI Wallet (Mobile)
    participant Desktop as Relying Party (Desktop Browser)
    participant Verifier as Verifier Backend

    Holder->>Desktop: Navigate to service requiring KYC
    Desktop->>Verifier: Request Presentation session
    Verifier-->>Desktop: Presentation Request URI / and session_id (display as QR code)
    Desktop->>Holder: Show QR code
    Holder->>Mobile: Scan QR code
    Mobile->>Verifier: GET Presentation Request / {session_id}
    Verifier-->>Mobile: Authorization Request / {presentation_definition, client_id, / response_uri, nonce}
    Mobile->>Mobile: Find matching VC
    Mobile->>Holder: Consent prompt
    Holder->>Mobile: Approve
    Mobile->>Mobile: Build VP Token / (SD-JWT and disclosures)
    Mobile-->>Verifier: POST response_uri / {vp_token, presentation_submission}
    Verifier->>Verifier: Verify VP Token
    Verifier-->>Desktop: Session complete (SSE / poll)
    Desktop-->>Holder: Access granted ✓
```

---

## 6. SD-JWT Selective Disclosure Flow

Illustrates how the EUDI Wallet selectively discloses only the fields requested by the verifier, protecting GDPR-sensitive fields not required for the use case.

```mermaid
sequenceDiagram
    autonumber
    participant Verifier as Relying Party
    participant Wallet as EUDI Wallet
    participant Holder as Holder

    Note over Wallet: Stored SD-JWT VC contains / disclosures for all fields: / - name (required) / - dateOfBirth / - nationality / - kycProfile.customerRiskRating / - kycProfile.pepStatus / - kycProfile.sourceOfFunds

    Verifier-->>Wallet: Presentation request for name and date of birth only
    Wallet->>Holder: Consent: share name and dateOfBirth?
    Holder->>Wallet: Approve
    Wallet->>Wallet: Include only matching disclosures in VP token and omit nationality and kycProfile fields
    Wallet-->>Verifier: VP Token / (SD-JWT ~ name_disclosure ~ dob_disclosure)
    Verifier->>Verifier: Hash disclosures then match sd digests then verify only disclosed fields are visible
    Note over Verifier: nationality, kycProfile fields / not disclosed — GDPR minimisation ✓
```

---

## 7. Credential Status Check (StatusList2021)

Shows the revocation check flow using W3C Status List 2021, which is embedded in the `credentialStatus` field of the OpenKYCAML VC.

```mermaid
sequenceDiagram
    autonumber
    participant Verifier as Relying Party
    participant StatusEndpoint as Status List Endpoint

    Verifier->>Verifier: Parse VP token and extract credentialStatus id
    Verifier->>StatusEndpoint: Fetch status list JWT from status endpoint
    StatusEndpoint-->>Verifier: Return status list JWT with compressed bitstring
    Verifier->>Verifier: Decompress bitstring and check bit at index 42
    alt Bit = 0 (not revoked)
        Verifier->>Verifier: Credential is valid
    else Bit = 1 (revoked)
        Verifier->>Verifier: Credential is revoked and presentation is rejected
    end
```

---

## 8. PID-Backed OpenKYCAML Issuance (Full EUDI Wallet Onboarding)

End-to-end flow for a new customer who uses their eIDAS 2.0 PID (Personal Identification Data) credential to onboard with a VASP. The VASP verifies the PID and issues an OpenKYCAML VC back to the wallet, recording the evidence chain.

```mermaid
sequenceDiagram
    autonumber
    participant Holder as New Customer
    participant Wallet as EUDI Wallet
    participant PIDProvider as PID Provider
    participant VASP as VASP / Issuer
    participant Blockchain as Blockchain / Registry

    Note over Holder,PIDProvider: Step 1 — PID already in wallet / (issued by national PID Provider)
    PIDProvider-->>Wallet: PID SD-JWT VC / (family_name, given_name, birth_date, etc.)

    Note over Holder,VASP: Step 2 — VASP KYC onboarding
    Holder->>VASP: Begin KYC onboarding
    VASP->>Wallet: OpenID4VP Presentation Request / {fields: family_name, given_name, / birth_date, nationality, ...}
    Wallet->>Holder: Consent prompt / (selective disclosure of PID fields)
    Holder->>Wallet: Approve
    Wallet-->>VASP: VP Token containing PID / (SD-JWT VC with selected disclosures)
    VASP->>VASP: Verify PID VP Token: / 1. Issuer signature (PID Provider DID) / 2. Holder key binding / 3. Status check
    VASP->>VASP: Map PID → ivms101 fields / (family_name → primaryIdentifier / given_name → secondaryIdentifier / birth_date → dateOfBirth etc.)
    VASP->>VASP: Run PEP and sanctions screening
    VASP->>VASP: Build OpenKYCAML payload with / evidence block: / {credentialIssuer: did:web:pid-provider, / verifier: did:web:vasp, / presentationMethod: OpenID4VP}
    VASP->>VASP: Sign OpenKYCAML VC / (SD-JWT, issuer DID = did:web:vasp)

    Note over VASP,Holder: Step 3 — Deliver OpenKYCAML VC to wallet
    VASP->>Wallet: Credential Offer / (OpenID4VCI pre-auth flow)
    Wallet->>VASP: POST /credential / {proof: key-bound JWT}
    VASP-->>Wallet: OpenKYCAML SD-JWT VC
    Wallet->>Wallet: Store OpenKYCAML VC
    Wallet-->>Holder: Onboarding complete ✓

    Note over Holder,Blockchain: Step 4 — Use VC for Travel Rule
    Holder->>VASP: Initiate virtual asset transfer
    VASP->>Wallet: OpenID4VP — request OpenKYCAML VC
    Wallet-->>VASP: VP Token (OpenKYCAML SD-JWT VC)
    VASP->>VASP: Build Travel Rule payload from VC
    VASP->>Blockchain: Broadcast transaction / and Travel Rule message
```

---

*All diagrams are rendered with [Mermaid](https://mermaid.js.org/). For the Travel Rule protocol-specific flows, see [Travel Rule Sequence Diagrams](travel-rule-sequence-diagrams.md). Last updated: v1.12.0.*
