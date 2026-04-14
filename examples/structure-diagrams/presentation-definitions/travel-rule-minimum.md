# presentation-definitions/travel-rule-minimum.json — Structure Diagram

**Scenario:** OpenID4VP Presentation Definition — FATF Rec 16 / TFR 2023/1113 Travel Rule Minimum.  
This is a W3C Presentation Exchange 2.0 `presentation_definition` object (not a schema payload). It describes the minimum claims a VASP must request via OpenID4VP Authorization Request to verify the Travel Rule minimum identity data for a natural person originator or beneficiary — aligned with FATF Recommendation 16 and EU TFR Art. 14.

```mermaid
flowchart LR
    subgraph Verifier["Verifier — VASP / Obliged Entity"]
        VP["🏦 VASP or Bank\nOpenID4VP Authorization Request\n(sends presentation_definition)"]
    end

    subgraph PD["presentation_definition"]
        ID["id: openkycaml-travel-rule-minimum-v1\nname: OpenKYCAML Travel Rule Minimum\n(FATF Rec 16 / TFR 2023/1113 Art. 14)\nspec: W3C Presentation Exchange 2.0"]

        subgraph DESC["input_descriptors[0]"]
            D_META["id: openkycaml-natural-person-identity\nname: OpenKYCAML KYC Identity Attestation — Natural Person"]

            subgraph Fields["Required Claim Paths (FATF Rec 16 minimum)"]
                F1["vct / type\n(credential type assertion)"]
                F2["naturalPerson.name.nameIdentifier[0]\n.primaryIdentifier\n(family name — IVMS 101)"]
                F3["naturalPerson.name.nameIdentifier[0]\n.secondaryIdentifier\n(given name — IVMS 101)"]
                F4["naturalPerson.nationalIdentification\n.nationalIdentifier\n(national ID / passport number)"]
                F5["[additional fields...]\n(address, DOB, account number)"]
            end
        end
    end

    subgraph Holder["Holder — EUDI Wallet / Credential Issuer"]
        WALLET["📲 EUDI Wallet or SD-JWT VC\nPresents vp_token with selected disclosures"]
    end

    VP -- "Authorization Request\n(includes presentation_definition)" --> WALLET
    WALLET -- "vp_token + id_token\n(VP containing OpenKYCAML SD-JWT VC)" --> VP

    style VP fill:#fef9c3,stroke:#eab308
    style PD fill:#f0fdf4,stroke:#16a34a
    style ID fill:#dcfce7,stroke:#16a34a
    style D_META fill:#dbeafe,stroke:#3b82f6
    style F1 fill:#e0e7ff,stroke:#6366f1
    style F2 fill:#e0e7ff,stroke:#6366f1
    style F3 fill:#e0e7ff,stroke:#6366f1
    style F4 fill:#e0e7ff,stroke:#6366f1
    style F5 fill:#f8fafc,stroke:#64748b
    style WALLET fill:#ede9fe,stroke:#7c3aed
```

## Required Claim Paths (FATF Rec 16 Minimum)

| # | Claim | IVMS 101 mapping | FATF Rec 16 basis |
|---|---|---|---|
| 1 | `vct` / `type` | Credential type assertion | — |
| 2 | `naturalPerson.name.primaryIdentifier` | Family name | Mandatory originator name |
| 3 | `naturalPerson.name.secondaryIdentifier` | Given name | Mandatory originator name |
| 4 | `naturalPerson.nationalIdentification.nationalIdentifier` | National ID / passport | Mandatory originator ID |
| 5+ | Address, DOB, account number | Additional IVMS 101 fields | TFR Art. 14 extended |

## Key Data Points

| Field | Value |
|---|---|
| File type | W3C Presentation Exchange 2.0 `presentation_definition` (not an OpenKYCAML schema payload) |
| PD ID | `openkycaml-travel-rule-minimum-v1` |
| Protocol | OpenID4VP (OpenID for Verifiable Presentations) |
| Credential format | SD-JWT VC (OpenKYCAML SD-JWT) |
| Minimum claims | 5 field groups covering FATF Rec 16 natural person identity |
| Spec version | `1.3.0` |
| Regulatory basis | FATF Rec. 16; EU TFR 2023/1113 Art. 14; W3C PE 2.0; OpenID4VP |
