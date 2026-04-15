# tax/tax-fatca-crs.json — Structure Diagram

**Scenario:** Financial Institution — FATCA GIIN + Dual-Jurisdiction CRS Tax Residencies (v1.9.1).  
Atlantic Asset Management Ltd (IE) is a FATCA `registeredDeemedCompliantFFI` with GIIN `ABC123.DEF45.LE.372`. It has two CRS tax residencies (IE + US) and carries a withholding-agent reference. The `taxStatus` block demonstrates `fatcaStatus`, `crsTaxResidencies[]`, and `tinIdentifiers[]` — the complete FATCA/CRS data model added in v1.9.1.

```mermaid
flowchart TD
    subgraph Entity["Legal Entity — Subject"]
        LP["🏢 Atlantic Asset Management Ltd\nLegalPerson · IE\nFATCA-registered FFI\nMedium-risk financial institution"]
    end

    subgraph TaxStatus["taxStatus — FATCA + CRS Block (v1.9.1)"]
        subgraph TINBlock["tinIdentifiers"]
            TIN1["🇮🇪 TIN (IE)\ntinType: TIN\ntinValue: IE6336214T\nverification: Revenue-IE ✅"]
        end

        subgraph FATCA["fatcaStatus (v1.9.1)"]
            FS["🇺🇸 FATCA\nfatcaClassification: registeredDeemedCompliantFFI\ngiin: ABC123.DEF45.LE.372 ✅\nffiListVerification: 2026-04-01\nusTinRequired: true\nwithholdingAgentRef: WA-ATLANTIC-VASP-2026-001\ntemporaryReliefApplied: false"]
        end

        subgraph CRS["crsTaxResidencies (v1.9.1)"]
            CRS1["🇮🇪 CRS Residency 1 — IE\ntinValue: IE6336214T\ncontrollingPersonFlag: false\nselfCertDate: 2026-01-15\ntinVerification: verified ✅"]
            CRS2["🇺🇸 CRS Residency 2 — US\ntinValue: 98-7654321\ncontrollingPersonFlag: false\nselfCertDate: 2026-01-15\ntinVerification: verified ✅"]
        end
    end

    subgraph KYC["KYC Profile"]
        KYCP["📋 kycLevel: CDD · risk: MEDIUM\nonboardingChannel: REMOTE_AUTOMATED"]
    end

    LP --> TaxStatus
    LP -.-> KYC

    style LP fill:#ede9fe,stroke:#7c3aed
    style TIN1 fill:#dcfce7,stroke:#16a34a
    style FS fill:#fef3c7,stroke:#f59e0b
    style CRS1 fill:#dbeafe,stroke:#3b82f6
    style CRS2 fill:#dbeafe,stroke:#3b82f6
    style KYCP fill:#f0fdf4,stroke:#16a34a
```

## FATCA / CRS Data Summary

| Block | Field | Value |
|---|---|---|
| `fatcaStatus` | `fatcaClassification` | `registeredDeemedCompliantFFI` |
| `fatcaStatus` | `giin` | `ABC123.DEF45.LE.372` |
| `fatcaStatus` | `usTinRequired` | `true` |
| `fatcaStatus` | `withholdingAgentReference` | `WA-ATLANTIC-VASP-2026-001` |
| `crsTaxResidencies[0]` | IE TIN | `IE6336214T` — Revenue-IE ✅ |
| `crsTaxResidencies[1]` | US TIN | `98-7654321` |

## GIIN Format (v1.9.1)

`ABC123.DEF45.LE.372` = `[FATCA ID].[GIIN Suffix].[Entity Type].[Country Code]`  
Pattern: `^[0-9A-Z]{6}\.[0-9A-Z]{5}\.[0-9A-Z]{2}\.[0-9A-Z]{3}$`

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.9.1 |
| Subject | Atlantic Asset Management Ltd (IE) |
| FATCA classification | `registeredDeemedCompliantFFI` |
| GIIN | `ABC123.DEF45.LE.372` |
| CRS residencies | IE + US (2 jurisdictions) |
| Risk | MEDIUM |
| Regulatory basis | FATCA (IRC §§1471-1474); IGA Model 1; OECD CRS 2014; AMLR Art. 22 |
