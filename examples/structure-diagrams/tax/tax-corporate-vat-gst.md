# tax/tax-corporate-vat-gst.json — Structure Diagram

**Scenario:** Corporate Entity — Multi-Jurisdiction VAT + GST Registrations (v1.9.0).  
TechGlobal Solutions GmbH (DE) holds a German TIN, a German VAT registration (DE123456789), and an Indian GST registration (27AAPFU0939F1ZV). The `taxStatus` block captures both `tinIdentifiers[]` and `indirectTaxRegistrations[]` — supporting OECD BEPS and AMLR Art. 22 corporate tax-compliance checks. UBO: Klaus Hoffmann (75%, DE).

```mermaid
flowchart TD
    subgraph Entity["Legal Entity — Subject"]
        LP["🏢 TechGlobal Solutions GmbH\nLegalPerson · DE\ncountryOfRegistration: DE\nUBO: Klaus Hoffmann (75%)"]
    end

    subgraph TaxStatus["taxStatus — Corporate Tax Identifiers (v1.9.0)"]
        subgraph TINs["tinIdentifiers"]
            TIN1["🇩🇪 TIN (DE)\ntinType: TIN\ntinValue: 86095742719\njurisdiction: DE\nverification: OECD-TIN-list ✅"]
            TIN2["🇮🇳 TIN (IN)\ntinType: GST\ntinValue: 27AAPFU0939F1ZV\njurisdiction: IN\nverification: GST-portal ✅"]
        end

        subgraph IndTax["indirectTaxRegistrations"]
            VAT["🇩🇪 VAT · Germany\nregistrationNumber: DE123456789\njurisdiction: DE\nstatus: active ✅\neffectiveFrom: 2012-01-15"]
            GST["🇮🇳 GST · India\nregistrationNumber: 27AAPFU0939F1ZV\njurisdiction: IN\nstatus: active ✅\neffectiveFrom: 2017-07-01"]
        end
    end

    subgraph KYC["KYC Profile"]
        KYCP["📋 kycLevel: CDD · risk: LOW\nonboardingChannel: REMOTE_AUTOMATED\nBO: Klaus Hoffmann (75%)"]
    end

    LP --> TaxStatus
    LP -.-> KYC

    style LP fill:#ede9fe,stroke:#7c3aed
    style TIN1 fill:#dcfce7,stroke:#16a34a
    style TIN2 fill:#dcfce7,stroke:#16a34a
    style VAT fill:#dbeafe,stroke:#3b82f6
    style GST fill:#dbeafe,stroke:#3b82f6
    style KYCP fill:#f0fdf4,stroke:#16a34a
```

## Tax Registration Summary

| Type | Jurisdiction | Registration | Value | Status |
|---|---|---|---|---|
| `TIN` | DE | `tinIdentifiers[0]` | `86095742719` | verified ✅ |
| `GST` | IN | `tinIdentifiers[1]` | `27AAPFU0939F1ZV` | verified ✅ |
| `VAT` | DE | `indirectTaxRegistrations[0]` | `DE123456789` | active ✅ |
| `GST` | IN | `indirectTaxRegistrations[1]` | `27AAPFU0939F1ZV` | active ✅ |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.9.0 |
| Subject | TechGlobal Solutions GmbH (DE) |
| UBO | Klaus Hoffmann (75%, DE) |
| TINs | 2 (DE + IN) |
| Indirect tax | DE VAT (2012) + IN GST (2017) |
| Risk | LOW |
| Regulatory basis | EU VAT Directive 2006/112/EC; Indian GST Act 2017; OECD BEPS; AMLR Art. 22 |
