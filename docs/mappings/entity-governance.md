# Entity Governance Flags — `EntityGovernance` $def

> Added in **v1.12.0**. The entire block is **optional** and backward-compatible.
> Applicable only to `LegalPerson` records.

---

## 1. Overview

OpenKYCAML v1.12.0 adds an `entityGovernance` property to `LegalPerson` backed by a new
`EntityGovernance` $def. It closes the following gaps identified in the v1.11.2 compliance review:

| Gap | Field(s) added |
|---|---|
| No top-level regulatoryStatus | `regulatoryStatus` enum |
| No array for multiple regulators | `regulators[]` |
| Entity is listed / listed on a recognised market | `listedStatus.isListed`, `listedStatus.marketIdentifier`, `listedStatus.recognisedMarket` |
| Parent is regulated | `parentRegulated` |
| Parent is listed | `parentListed` |
| Parent company reference (non-cell entities) | `parentCompany` (`$ref: ParentCellCompanyReference`) |
| Majority-owned subsidiary | `majorityOwnedSubsidiary` |
| State owned / government ownership | `stateOwned`, `governmentOwnershipPercentage` |

---

## 2. Schema path

```
ivms101.originator.originatorPersons[].legalPerson.entityGovernance
ivms101.beneficiary.beneficiaryPersons[].legalPerson.entityGovernance
kycProfile.* (wherever LegalPerson is embedded)
```

---

## 3. Field reference

### 3.1 `regulatoryStatus`

| Value | Meaning |
|---|---|
| `REGULATED` | Entity holds an active licence issued by a recognised regulatory authority. |
| `RECOGNISED` | Entity is formally recognised (e.g. central bank, supranational body, international organisation) but does not hold a licence per se. |
| `UNREGULATED` | Entity operates in a sector or jurisdiction with no applicable regulatory licence requirement. |
| `EXEMPT` | Entity is explicitly exempted from licensing under applicable law (e.g. intra-group exemption, de minimis threshold). |

**Regulatory basis:** AMLR Art. 48 (CDD reliance — third party must be subject to equivalent AML/CFT
supervision); FATF Rec. 17 (reliance on third parties).

### 3.2 `regulators[]`

Array of regulator objects, each with:

| Sub-field | Type | Required | Notes |
|---|---|---|---|
| `regulatorName` | string (max 200) | No | e.g. `"Financial Conduct Authority"`, `"BaFin"`, `"CSSF"` |
| `jurisdiction` | string (`^[A-Z]{2}$`) | No | ISO 3166-1 alpha-2 country code |
| `licenceNumber` | string (max 100) | No | Licence or registration number |

**Regulatory basis:** AMLR Art. 48 requires verification that a third party is regulated; FATF Rec.
17 cross-border reliance; Wolfsberg CBDDQ §3.2 (regulatory licences).

### 3.3 `listedStatus`

Inline object with:

| Sub-field | Type | Notes |
|---|---|---|
| `isListed` | boolean | Whether the entity is listed on any exchange. |
| `marketIdentifier` | string (max 10) | ISO 10383 MIC code (e.g. `"XLON"`, `"XNAS"`, `"XETR"`). |
| `recognisedMarket` | boolean | Whether the market is a regulated/recognised market under applicable law (EU MiFID II, UK FCA). |

**Regulatory basis:**
- AMLR Art. 22 simplified CDD — entities listed on recognised markets may qualify.
- MiFID II Art. 4(1)(21) — definition of a regulated market.
- Market Abuse Regulation (MAR) — insider dealing and market manipulation risk.

### 3.4 `parentCompany`

`$ref: ParentCellCompanyReference` — reuses the existing $def (fields: `legalEntityIdentifier`,
`jurisdiction`, optional `parentName`). Use for **non-cell** legal entities where the parent
relationship is relevant for beneficial-ownership tracing or group CDD.

> **Note:** For PCC/ICC cell structures use the existing `LegalPerson.parentCellCompanyReference`
> instead. `entityGovernance.parentCompany` is intended for ordinary corporate groups.

**Regulatory basis:** FATF Rec. 24 (beneficial ownership transparency for corporate groups);
AMLR Art. 26 (group-level beneficial ownership).

### 3.5 `parentRegulated`

Boolean. Whether the immediate parent company is regulated by a recognised regulator.

**Regulatory basis:** AMLR Art. 48 group-reliance conditions; Wolfsberg CBDDQ §3.3.

### 3.6 `parentListed`

Boolean. Whether the immediate parent company is listed on a recognised market.

**Regulatory basis:** AMLR Art. 22 simplified CDD conditions for subsidiaries of listed groups;
MAR insider-dealing risk for group companies.

### 3.7 `majorityOwnedSubsidiary`

Boolean. Whether this entity is a majority-owned (>50%) subsidiary of another entity.

**Regulatory basis:** FATF Rec. 24 (group ownership structures); AMLR Art. 26 (group beneficial
ownership chain); AMLR Art. 48 intra-group reliance.

### 3.8 `stateOwned`

Boolean. Whether the entity is owned or controlled by a state or government body.

**Regulatory basis:** FATF Guidance on PEPs (2013/2022) — state-owned enterprises are vehicles
for PEP influence; enhanced scrutiny required. AMLR Art. 28–31 PEP provisions.

### 3.9 `governmentOwnershipPercentage`

Number (0–100). The percentage of the entity owned directly or indirectly by a government or
state body.

- ≥ 50%: entity is effectively state-controlled; PEP-adjacency scoring should be elevated.
- ≥ 25%: significant state influence; enhanced due diligence consideration.

**Regulatory basis:** FATF Rec. 12 / AMLR Art. 28 PEP provisions; IMF/OECD state-owned
enterprise governance frameworks.

---

## 4. Full JSON example

```json
{
  "legalPerson": {
    "name": {
      "nameIdentifier": [
        { "legalPersonName": "Acme Financial Services GmbH", "legalPersonNameIdentifierType": "LEGL" }
      ]
    },
    "countryOfRegistration": "DE",
    "lei": "529900HNOAA1KXQJUQ27",
    "entityGovernance": {
      "regulatoryStatus": "REGULATED",
      "regulators": [
        {
          "regulatorName": "BaFin",
          "jurisdiction": "DE",
          "licenceNumber": "BAFIN-123456"
        },
        {
          "regulatorName": "Financial Conduct Authority",
          "jurisdiction": "GB",
          "licenceNumber": "FCA-789012"
        }
      ],
      "listedStatus": {
        "isListed": true,
        "marketIdentifier": "XETR",
        "recognisedMarket": true
      },
      "parentCompany": {
        "legalEntityIdentifier": "PARENT0000001234567890",
        "jurisdiction": "DE",
        "parentName": "Acme Group AG"
      },
      "parentRegulated": true,
      "parentListed": true,
      "majorityOwnedSubsidiary": true,
      "stateOwned": false
    }
  }
}
```

---

## 5. Regulatory mapping summary

| `EntityGovernance` field | FATF Rec. | AMLR Article | Other |
|---|---|---|---|
| `regulatoryStatus` | Rec. 17 | Art. 48 | Wolfsberg CBDDQ §3 |
| `regulators[]` | Rec. 17 | Art. 48 | Wolfsberg CBDDQ §3 |
| `listedStatus` | Rec. 10 | Art. 22 (SDD) | MiFID II Art. 4; MAR |
| `parentCompany` | Rec. 24 | Art. 26 | — |
| `parentRegulated` | Rec. 17 | Art. 48 | Wolfsberg CBDDQ §3.3 |
| `parentListed` | Rec. 10 | Art. 22 (SDD) | MAR |
| `majorityOwnedSubsidiary` | Rec. 24 | Art. 26, Art. 48 | — |
| `stateOwned` | Rec. 12 | Art. 28–31 | FATF PEP Guidance |
| `governmentOwnershipPercentage` | Rec. 12 | Art. 28–31 | IMF/OECD SOE frameworks |

---

*Last updated: v1.12.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*
