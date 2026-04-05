# trust-complex-ubo.json — Structure Diagram

**Scenario:** Discretionary Trust Beneficial Ownership — Jersey Discretionary Trust with Corporate Trustee, Named Protector, Settlor and Beneficiaries.  
Windermere Digital Assets Ltd (BVI VASP) is 100% owned by the Windermere Discretionary Trust (Jersey). Sir James Hartley is the UBO through a combination of settlor reservation rights and protector influence. All four FATF R.25 trust principal categories are captured in `lpid.mandates`.

```mermaid
flowchart TD
    subgraph UBO["Ultimate Beneficial Owner"]
        UBO1["👤 Sir James Edward Hartley\nUBO · GB\nPassport: GB-PASS-PX1234567\nDOB: 1955-07-23, London\n14 Park Lane, London W1K 1QH\n⚠️ Dual role: Settlor + Life-Interest Beneficiary\nControl: DE_FACTO_CONTROL + CONTRACTUAL\nEffective 100% control"]
    end

    subgraph Trust["Windermere Discretionary Trust — Jersey"]
        TRUST["🏛️ Windermere Discretionary Trust\nJersey Registered · JE-RT-2015-00341\nEstablished: 12 March 2015\n(Trusts (Jersey) Law 1984)\nHolds 100% of Windermere Digital Assets Ltd"]

        subgraph Trustee["Corporate Trustee: Windermere Trustees Ltd (JE)"]
            T_DIR1["👤 Margaret Anne Forsyth\nDirector of Corporate Trustee · JE\nPassport: GB-PASS-PY9876543\nDOB: 1968-03-22, Edinburgh\nAuthorised signatory (since 2015-03-12)"]
            T_DIR2["👤 David Chukwuemeka Okonkwo\nDirector of Corporate Trustee · JE\nPassport: GB-PASS-PZ1122334\nDOB: 1975-08-07, Lagos\nAuthorised signatory (since 2019-06-15)"]
        end

        subgraph Protector["Protector"]
            PROT["👤 Lady Catherine Rose Hartley\nProtector · GB\nPassport: GB-PASS-PA3344556\nDOB: 1959-11-14, Oxford\n⚡ Power to remove & replace trustees\n(Trust Deed Clause 14)\nSpouse of settlor — acts per letter of wishes"]
        end

        subgraph Beneficiaries["Beneficiaries"]
            B1["👤 Sir James Hartley\nBeneficiary (life interest in income)\nAlso the settlor and UBO"]
            B2["👤 James William Hartley\nBeneficiary (remainder interest)\nSon of settlor — vests at age 30"]
            B3["👤 Emma Louise Hartley\nBeneficiary (remainder interest)\nDaughter of settlor — vests at age 30"]
        end
    end

    subgraph Subject["Subject Entity — VASP"]
        SUBJECT["🏢 Windermere Digital Assets Ltd\nVASP · British Virgin Islands\nReg: VG-BC-2021-000887\nLEI: 213800WDAVG00001VG00\nRisk: HIGH · EDD · FATF R.25"]
    end

    subgraph Transfer["Travel Rule Transfer — VG → GB"]
        BVASP["🏦 Caledonian Digital Bank plc · GB\nBeneficiary VASP\nDID: did:web:caledonian-digital-bank.example.co.uk\nLEI: 213800CALDBGB000GB00\nIssues KYCAttestation VC"]
    end

    UBO1 -- "Settlor: settled assets 2015\nRetains letter of wishes" --> TRUST
    PROT -- "Protector power:\ncan remove/replace trustees\n(acts per settlor's wishes)" --> TRUST
    TRUST -- "100% shareholding\n(legal title in trustee)" --> SUBJECT
    UBO1 -.-> B1
    SUBJECT -- "250,000 BTC\nOpenKYCAML VC" --> BVASP

    style UBO1 fill:#dbeafe,stroke:#3b82f6
    style TRUST fill:#f3e8ff,stroke:#9333ea
    style T_DIR1 fill:#ede9fe,stroke:#7c3aed
    style T_DIR2 fill:#ede9fe,stroke:#7c3aed
    style PROT fill:#fef3c7,stroke:#f59e0b
    style B1 fill:#dcfce7,stroke:#16a34a
    style B2 fill:#dcfce7,stroke:#16a34a
    style B3 fill:#dcfce7,stroke:#16a34a
    style SUBJECT fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
```

## FATF R.25 Trust Principal Categories

```mermaid
flowchart LR
    S["Settlor\nSir James Hartley\n(also UBO + Beneficiary)"]
    TR["Trustee\nWindermere Trustees Ltd\n(corporate)\nDirectors: Forsyth + Okonkwo"]
    PR["Protector\nLady Catherine Hartley\n(spouse of settlor)"]
    BEN["Beneficiaries\nSir James (life interest)\nJames William (remainder)\nEmma Louise (remainder)"]

    S -. "Letter of wishes\n(non-binding but followed)" .-> TR
    PR -- "Power to remove\ntrustee (Clause 14)" --> TR
    TR -- "Trustee administers\nfor beneficiaries" --> BEN
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Structure | Jersey Discretionary Trust (1984 Law) |
| Subject VASP | Windermere Digital Assets Ltd (BVI) |
| UBO | Sir James Edward Hartley (GB) — settlor + life beneficiary |
| Control mechanism | DE_FACTO_CONTROL (settlor rights + protector influence) |
| Trustee | Windermere Trustees Ltd — 2 natural person directors |
| Protector | Lady Catherine Hartley — removal/replacement power |
| Beneficiaries | 3 (Sir James life interest; 2 children remainder) |
| Asset / Amount | 250,000 BTC |
| Beneficiary VASP | Caledonian Digital Bank plc (GB) |
| Risk | HIGH · EDD |
| Regulatory basis | FATF Recommendation 25, AMLR Art. 26(2)(b) |
