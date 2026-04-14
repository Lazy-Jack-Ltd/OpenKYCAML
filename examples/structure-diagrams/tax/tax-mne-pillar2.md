# tax/tax-mne-pillar2.json — Structure Diagram

**Scenario:** Multinational Enterprise — OECD Pillar Two GloBE Compliance (v1.9.0).  
Apex Ireland Operations Ltd (IE) is an in-scope Pillar Two constituent entity of Apex International Group PLC (consolidated revenue €2.1 billion). The `taxStatus.pillarTwo` block captures ETRs across three jurisdictions (IE 12.5%, US 21%, DE 29.8%), the Global Information Return (GIR) filing reference, and the substance-based `safeHarbourApplied`. IE rate of 12.5% is below the GloBE 15% minimum — potential IIR/UTPR top-up applies.

```mermaid
flowchart TD
    subgraph Entity["Legal Entity — Subject"]
        LP["🏢 Apex Ireland Operations Ltd\nLegalPerson · IE\nConstituentEntity of Apex International Group PLC\nBO: Apex International Group PLC (100%)"]
    end

    subgraph TaxStatus["taxStatus — Pillar Two GloBE (v1.9.0)"]
        subgraph TINBlock["tinIdentifiers"]
            TIN1["🇮🇪 TIN (IE): IE6336214T · Revenue-IE ✅"]
            TIN2["🇺🇸 EIN (US): 98-7654321 · IRS-TIN-Matching ✅"]
        end

        subgraph IndTax["indirectTaxRegistrations"]
            VAT["🇮🇪 VAT: IE6336214T · active ✅"]
        end

        subgraph P2["pillarTwo — OECD GloBE"]
            P2INFO["🌍 inScopeMNE: true\nconstituentEntityStatus: inScope\nconsolidatedRevenueEUR: 2,100,000,000\ngirFilingReference: GIR-APEX-IE-2025-001\nlastGIRDate: 2026-03-31\nsafeHarbourApplied: SubstanceBased"]

            subgraph ETR["Effective Tax Rates by Jurisdiction"]
                IE_ETR["🇮🇪 IE: ETR 12.5% ⚠️\n(below GloBE 15% minimum)\nIIR/UTPR top-up may apply"]
                US_ETR["🇺🇸 US: ETR 21.0% ✅"]
                DE_ETR["🇩🇪 DE: ETR 29.8% ✅"]
            end
        end
    end

    subgraph KYC["KYC Profile"]
        KYCP["📋 kycLevel: CDD · risk: MEDIUM\nBO: Apex International Group PLC (100%)"]
    end

    LP --> TaxStatus
    LP -.-> KYC

    style LP fill:#ede9fe,stroke:#7c3aed
    style TIN1 fill:#dcfce7,stroke:#16a34a
    style TIN2 fill:#dcfce7,stroke:#16a34a
    style VAT fill:#dbeafe,stroke:#3b82f6
    style P2INFO fill:#fef3c7,stroke:#f59e0b
    style IE_ETR fill:#fef2f2,stroke:#ef4444
    style US_ETR fill:#dcfce7,stroke:#16a34a
    style DE_ETR fill:#dcfce7,stroke:#16a34a
    style KYCP fill:#f0fdf4,stroke:#16a34a
```

## Pillar Two ETR Summary

| Jurisdiction | ETR | GloBE 15% test | Action |
|---|---|---|---|
| IE | 12.5% | ❌ Below threshold | IIR/UTPR top-up potentially applicable |
| US | 21.0% | ✅ Above threshold | No top-up |
| DE | 29.8% | ✅ Above threshold | No top-up |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.9.0 |
| Subject | Apex Ireland Operations Ltd (IE) |
| Parent MNE | Apex International Group PLC |
| Consolidated revenue | €2.1 billion (in-scope — above €750m threshold) |
| GIR reference | `GIR-APEX-IE-2025-001` (filed 2026-03-31) |
| Safe harbour | `SubstanceBased` |
| IE ETR | 12.5% — ⚠️ below GloBE 15% minimum |
| Risk | MEDIUM |
| Regulatory basis | OECD Pillar Two GloBE Rules (Dec 2021); EU GloBE Directive 2022/2523; AMLR Art. 22 |
