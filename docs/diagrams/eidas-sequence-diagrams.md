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
    participant Issuer as OpenKYCAML Issuer\n(VASP / KYC Utility)
    participant Verifier as Relying Party\n(Beneficiary VASP / Bank)

    Note over Holder,Verifier: Phase 1 — Issuance (OpenID4VCI)
    Holder->>Issuer: Complete KYC onboarding
    Issuer->>Issuer: Build + sign OpenKYCAML VC\n(SD-JWT VC / VC-JWT)
    Issuer-->>Wallet: Deliver credential\n(OpenID4VCI pre-auth or auth flow)
    Wallet->>Wallet: Store credential

    Note over Holder,Verifier: Phase 2 — Presentation (OpenID4VP)
    Verifier->>Wallet: Presentation Request\n(select OpenKYCAML VC fields)
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

    Issuer->>Issuer: KYC completed; build\nOpenKYCAML payload + sign VC
    Issuer->>Holder: Credential Offer URI\n(QR code / deep link)\nopenid-credential-offer://?credential_offer=...
    Holder->>Wallet: Open credential offer
    Wallet->>Issuer: GET /.well-known/openid-credential-issuer\n(fetch issuer metadata)
    Issuer-->>Wallet: Credential Issuer Metadata\n{credential_configurations_supported, ...}
    Wallet->>AuthServer: POST /token\n{grant_type: urn:...pre-authorized_code,\npre-authorized_code, tx_code}
    AuthServer-->>Wallet: Access Token + c_nonce
    Wallet->>Wallet: Generate key-bound proof\n(JWT with c_nonce)
    Wallet->>Issuer: POST /credential\n{format: dc+sd-jwt,\ncredential_identifier,\nproof: {jwt}}
    Issuer->>Issuer: Verify holder key binding;\nbind VC to wallet key (cnf.jwk)
    Issuer-->>Wallet: Credential Response\n{credential: <SD-JWT VC>}
    Wallet->>Wallet: Store OpenKYCAML VC
    Wallet-->>Holder: Credential stored ✓
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

    Holder->>Wallet: Request OpenKYCAML credential\nfrom issuer
    Wallet->>Issuer: GET /.well-known/openid-credential-issuer
    Issuer-->>Wallet: Issuer Metadata
    Wallet->>AuthServer: Authorisation Request\n{response_type: code,\nclient_id, redirect_uri,\nscope / authorization_details}
    AuthServer->>Holder: Authentication + consent screen
    Holder->>AuthServer: Authenticate + approve
    AuthServer-->>Wallet: Authorisation Code\n(redirect)
    Wallet->>AuthServer: POST /token\n{grant_type: authorization_code, code}
    AuthServer-->>Wallet: Access Token + c_nonce
    Wallet->>Wallet: Generate key-bound proof\n(JWT signed with wallet key)
    Wallet->>Issuer: POST /credential\n{format: dc+sd-jwt, proof}
    Issuer->>Issuer: Verify proof; build VC;\nbind to holder key
    Issuer-->>Wallet: Credential Response\n{credential: <SD-JWT VC>}
    Wallet->>Wallet: Store credential
    Wallet-->>Holder: Credential stored ✓
```

---

## 4. VC Presentation — OpenID4VP (Same-Device)

Used when the verifier and the EUDI Wallet are on the same device (e.g., browser + mobile wallet via universal link).

```mermaid
sequenceDiagram
    autonumber
    participant Holder as EUDI Wallet Holder
    participant Wallet as EUDI Wallet
    participant Verifier as Relying Party\n(Beneficiary VASP / Bank)

    Holder->>Verifier: Access service requiring KYC
    Verifier->>Verifier: Build Presentation Request\n(select ivms101 / kycProfile fields)
    Verifier-->>Wallet: Authorization Request\n(openid4vp:// deep link)\n{client_id, response_type: vp_token,\npresentation_definition}
    Wallet->>Wallet: Locate matching OpenKYCAML VC
    Wallet->>Holder: Consent screen —\nshow requested fields
    Holder->>Wallet: Approve
    Wallet->>Wallet: Build VP Token\n(SD-JWT with selected disclosures)
    Wallet-->>Verifier: POST response_uri\n{vp_token, presentation_submission}
    Verifier->>Verifier: Verify VP Token:\n1. SD-JWT signature\n2. Holder key binding\n3. Credential status\n4. Issuer trust chain
    Verifier-->>Holder: Access granted ✓
```

---

## 5. VC Presentation — OpenID4VP (Cross-Device / QR Code)

Used when the relying party is on a desktop browser and the EUDI Wallet is on the holder's mobile device.

```mermaid
sequenceDiagram
    autonumber
    participant Holder as EUDI Wallet Holder
    participant Mobile as EUDI Wallet\n(Mobile)
    participant Desktop as Relying Party\n(Desktop Browser)
    participant Verifier as Verifier Backend

    Holder->>Desktop: Navigate to service requiring KYC
    Desktop->>Verifier: Request Presentation session
    Verifier-->>Desktop: Presentation Request URI\n+ session_id (display as QR code)
    Desktop->>Holder: Show QR code
    Holder->>Mobile: Scan QR code
    Mobile->>Verifier: GET Presentation Request\n{session_id}
    Verifier-->>Mobile: Authorization Request\n{presentation_definition, client_id,\nresponse_uri, nonce}
    Mobile->>Mobile: Find matching VC
    Mobile->>Holder: Consent prompt
    Holder->>Mobile: Approve
    Mobile->>Mobile: Build VP Token\n(SD-JWT + disclosures)
    Mobile-->>Verifier: POST response_uri\n{vp_token, presentation_submission}
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

    Note over Wallet: Stored SD-JWT VC contains\ndisclosures for all fields:\n- name (required)\n- dateOfBirth\n- nationality\n- kycProfile.customerRiskRating\n- kycProfile.pepStatus\n- kycProfile.sourceOfFunds

    Verifier-->>Wallet: Presentation Request\n{fields: [name, dateOfBirth]\n— travel-rule minimum}
    Wallet->>Holder: Consent: share name + dateOfBirth?
    Holder->>Wallet: Approve
    Wallet->>Wallet: Include ONLY matching disclosures\nin VP Token;\nomit nationality, kycProfile fields
    Wallet-->>Verifier: VP Token\n(SD-JWT ~ name_disclosure ~ dob_disclosure)
    Verifier->>Verifier: Hash disclosures;\nmatch _sd digests;\nverify — only disclosed fields visible
    Note over Verifier: nationality, kycProfile fields\nnot disclosed — GDPR minimisation ✓
```

---

## 7. Credential Status Check (StatusList2021)

Shows the revocation check flow using W3C Status List 2021, which is embedded in the `credentialStatus` field of the OpenKYCAML VC.

```mermaid
sequenceDiagram
    autonumber
    participant Verifier as Relying Party
    participant StatusEndpoint as Status List Endpoint\n(Issuer infrastructure)

    Verifier->>Verifier: Parse VP Token;\nextract credentialStatus.id\n(e.g. https://issuer.example.com/status/1#42)
    Verifier->>StatusEndpoint: GET /status/1\n(fetch Status List JWT)
    StatusEndpoint-->>Verifier: Status List JWT\n(compressed bitstring)
    Verifier->>Verifier: Decompress bitstring;\ncheck bit at index 42
    alt Bit = 0 (not revoked)
        Verifier->>Verifier: Credential is VALID ✓
    else Bit = 1 (revoked)
        Verifier->>Verifier: Credential is REVOKED ✗\nreject presentation
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
    participant PIDProvider as PID Provider\n(Member State)
    participant VASP as VASP / Issuer
    participant Blockchain as Blockchain / Registry

    Note over Holder,PIDProvider: Step 1 — PID already in wallet\n(issued by national PID Provider)
    PIDProvider-->>Wallet: PID SD-JWT VC\n(family_name, given_name, birth_date, etc.)

    Note over Holder,VASP: Step 2 — VASP KYC onboarding
    Holder->>VASP: Begin KYC onboarding
    VASP->>Wallet: OpenID4VP Presentation Request\n{fields: family_name, given_name,\nbirth_date, nationality, ...}
    Wallet->>Holder: Consent prompt\n(selective disclosure of PID fields)
    Holder->>Wallet: Approve
    Wallet-->>VASP: VP Token containing PID\n(SD-JWT VC with selected disclosures)
    VASP->>VASP: Verify PID VP Token:\n1. Issuer signature (PID Provider DID)\n2. Holder key binding\n3. Status check
    VASP->>VASP: Map PID → ivms101 fields\n(family_name → primaryIdentifier\ngiven_name → secondaryIdentifier\nbirth_date → dateOfBirth etc.)
    VASP->>VASP: Run PEP + sanctions screening
    VASP->>VASP: Build OpenKYCAML payload with\nevidence block:\n{credentialIssuer: did:web:pid-provider,\nverifier: did:web:vasp,\npresentationMethod: OpenID4VP}
    VASP->>VASP: Sign OpenKYCAML VC\n(SD-JWT, issuer DID = did:web:vasp)

    Note over VASP,Holder: Step 3 — Deliver OpenKYCAML VC to wallet
    VASP->>Wallet: Credential Offer\n(OpenID4VCI pre-auth flow)
    Wallet->>VASP: POST /credential\n{proof: key-bound JWT}
    VASP-->>Wallet: OpenKYCAML SD-JWT VC
    Wallet->>Wallet: Store OpenKYCAML VC
    Wallet-->>Holder: Onboarding complete ✓

    Note over Holder,Blockchain: Step 4 — Use VC for Travel Rule
    Holder->>VASP: Initiate virtual asset transfer
    VASP->>Wallet: OpenID4VP — request OpenKYCAML VC
    Wallet-->>VASP: VP Token (OpenKYCAML SD-JWT VC)
    VASP->>VASP: Build Travel Rule payload from VC
    VASP->>Blockchain: Broadcast transaction\n+ Travel Rule message
```

---

*All diagrams are rendered with [Mermaid](https://mermaid.js.org/). For the Travel Rule protocol-specific flows, see [Travel Rule Sequence Diagrams](travel-rule-sequence-diagrams.md). Last updated: v1.3.0.*
