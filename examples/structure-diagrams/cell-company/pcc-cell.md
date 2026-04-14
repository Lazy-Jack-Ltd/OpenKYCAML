# cell-company/pcc-cell.json — Structure Diagram

**Scenario:** Protected Cell Company — PCC Cell (IVMS 101).  
Guernsey Re PCC — Cell 7 Property Catastrophe Series 2026 (`CELL-007`) sends 5,000,000 USD to Cayman Digital Finance Ltd. The PCC cell has no independent legal personality; the parent PCC (Guernsey Re PCC) is the counterparty of record. The cell is an ILS catastrophe bond issuer, governed by FATF Rec. 24 and the Guernsey Companies (Guernsey) Law 2008.

```mermaid
flowchart TD
    subgraph PCC["Protected Cell Company Structure — Guernsey"]
        PARENT_PCC["🏢 Guernsey Re PCC\nParent PCC · Guernsey (GG)\nLEI: 549300ABCDEF12345678\nRegistered PCC under Guernsey law\n(Companies (Guernsey) Law 2008)"]

        CELL7["🏢 Cell 7 — Property Catastrophe Series 2026\ncellCompanyType: PCC_CELL 🆕 v1.11.0\ncellIdentifier: CELL-007\nhasIndependentLegalPersonality: false ⚠️\nisCellCompanyIssuer: true\nissuancePurpose: CATASTROPHE_BOND\ninstrumentRef: ils/2026-property-cat\nAccount: GB29NWBK60161331926819"]
    end

    subgraph Transfer["Travel Rule Transfer — GG → KY"]
        OVASP["🏦 Guernsey Trust & Custody Ltd\nOriginating VASP · GG\nLEI: 254900A6F3BJKMBWSP32"]
        BVASP["🏦 Cayman Digital Finance Ltd\nBeneficiary VASP · KY\nLEI: 549300PM8ZMDKJEPOW16"]
    end

    PARENT_PCC -- "CELL-007 is a segregated cell\n(no independent legal personality)" --> CELL7
    CELL7 -- "5,000,000 USD\n(CatBond proceeds)" --> OVASP
    OVASP -- "IVMS 101 Travel Rule\n5,000,000 USD" --> BVASP

    style PARENT_PCC fill:#ede9fe,stroke:#7c3aed
    style CELL7 fill:#dbeafe,stroke:#3b82f6
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
```

## Cell Company Fields (v1.11.0+)

| Field | Value | Notes |
|---|---|---|
| `cellCompanyType` | `PCC_CELL` | Segregated cell — no independent legal personality |
| `cellIdentifier` | `CELL-007` | Unique identifier within parent PCC |
| `cellName` | `Cell 7 - Property Catastrophe Series 2026` | Human-readable name |
| `hasIndependentLegalPersonality` | `false` | PCC cell — parent PCC is legal counterparty |
| `isCellCompanyIssuer` | `true` | Cell issues catastrophe bond instruments |
| `issuancePurpose` | `CATASTROPHE_BOND` | ILS product type |
| `parentCellCompanyReference` | Guernsey Re PCC — LEI + GG | Mandatory when `cellCompanyType = PCC_CELL` |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.11.0 |
| Cell type | PCC_CELL (Protected Cell Company) |
| Cell | Guernsey Re PCC · Cell 7 (CELL-007) |
| Governing law | Guernsey Companies (Guernsey) Law 2008 |
| Asset / Amount | 5,000,000 USD (catastrophe bond) |
| Originating VASP | Guernsey Trust & Custody Ltd (GG) |
| Beneficiary VASP | Cayman Digital Finance Ltd (KY) |
| Regulatory basis | FATF Rec. 24; AMLR Art. 26; Guernsey VASP Rules 2021 |
