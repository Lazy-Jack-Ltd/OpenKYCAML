# legal-entity-trust.json — Structure Diagram

**Scenario:** Cayman Islands Discretionary Trust — Harbour Gate Discretionary Trust (KY) sends 85,000 USDC to Meridian Digital Custody Ltd via its associated digital assets VASP. The structure captures the trust principals under FATF Recommendation 25 — settlor, corporate trustee, named beneficiaries — against AMLR Art. 26(2)(b).

```mermaid
flowchart TD
    subgraph TrustPrincipals["FATF R.25 Trust Principal Categories"]
        SETTLOR["👤 Edmund Charles Whitmore\nSettlor · GB\nEstablished trust 2019\nRetains letter of wishes\n(also life beneficiary)"]

        TRUSTEE["🏢 Harbour Gate Trust Company Ltd\nCorporate Trustee · KY\nReg: KY-CI-HGT-2019-000221\nHolds legal title to assets\n(administers trust for beneficiaries)"]

        BEN1["👤 Edmund Charles Whitmore\nBeneficiary — Life interest\n(also the settlor)"]

        BEN2["👤 Sophia Elaine Whitmore\nBeneficiary — Remainder\n(daughter of settlor)"]
    end

    subgraph Trust["Trust Structure"]
        TRUST_OBJ["🏛️ Harbour Gate Discretionary Trust\nCayman Islands Discretionary Trust\nReg: KY-TR-2019-004421\nTrust Deed: HGTC-DEED-2019-004421\nLaw: Cayman Islands (Trusts Law, 2017)"]
    end

    subgraph Subject["Subject Entity — Associated Digital Assets VASP"]
        SUBJECT["🏢 Harbour Gate Digital Assets Ltd\nOriginating VASP · KY\nLinked to trust via beneficial ownership\nRisk: HIGH · EDD"]
    end

    subgraph KYC["KYC Profile — EDD"]
        KYCP["📋 KYC Level: EDD\nriskRating: HIGH\nddt: EDD\nBO: Harbour Gate Trust (100% held by trust)\nSettlor and beneficiaries all identified\nSanctions: CLEAR"]
    end

    subgraph Transfer["Travel Rule Transfer — KY → KY"]
        BVASP["🏦 Meridian Digital Custody Ltd\nBeneficiary VASP · KY"]
    end

    SETTLOR -- "Established 2019\nLetter of wishes" --> TRUST_OBJ
    TRUSTEE -- "Corporate trustee\nadministers assets" --> TRUST_OBJ
    BEN1 -.-> TRUST_OBJ
    BEN2 -.-> TRUST_OBJ
    TRUST_OBJ -- "100% beneficial ownership" --> SUBJECT

    SUBJECT -- "85,000 USDC" --> BVASP
    SUBJECT -.-> KYC

    style SETTLOR fill:#dbeafe,stroke:#3b82f6
    style TRUSTEE fill:#ede9fe,stroke:#7c3aed
    style BEN1 fill:#dcfce7,stroke:#16a34a
    style BEN2 fill:#dcfce7,stroke:#16a34a
    style TRUST_OBJ fill:#f3e8ff,stroke:#9333ea
    style SUBJECT fill:#fef9c3,stroke:#eab308
    style KYCP fill:#f0fdf4,stroke:#16a34a
    style BVASP fill:#fef9c3,stroke:#eab308
```

## FATF R.25 Trust Principals

| Role | Name | Jurisdiction | Notes |
|---|---|---|---|
| Settlor | Edmund Charles Whitmore | GB | Also life-interest beneficiary; letter of wishes |
| Trustee | Harbour Gate Trust Company Ltd (corporate) | KY | Legal title holder; administers for beneficiaries |
| Beneficiary 1 | Edmund Charles Whitmore | GB | Life interest in income |
| Beneficiary 2 | Sophia Elaine Whitmore | GB | Remainder interest (daughter) |
| Protector | — | — | Not appointed in this trust |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.4.0 |
| Structure | Cayman Islands Discretionary Trust |
| Trust reference | HGTC-DEED-2019-004421 |
| Governing law | Cayman Islands Trusts Law 2017 |
| Settlor | Edmund Whitmore (GB) |
| Corporate trustee | Harbour Gate Trust Company Ltd |
| Beneficiaries | 2 (settlor life interest + daughter remainder) |
| Asset / Amount | 85,000 USDC |
| KYC level | EDD |
| Risk | HIGH |
| Beneficiary VASP | Meridian Digital Custody Ltd (KY) |
| Regulatory basis | FATF Rec. 25; AMLR Art. 26(2)(b); Cayman Trusts Law 2017 |
