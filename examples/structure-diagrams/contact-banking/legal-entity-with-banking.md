# contact-banking/legal-entity-with-banking.json — Structure Diagram

**Scenario:** Legal Entity with Contact Details and Multiple Bank Accounts.  
Nordvik Shipping AS (NO) sends 250,000 EUR. The record demonstrates multi-account `bankingDetails` on a `LegalPerson` — a Norwegian IBAN and a Dutch account — along with compliance email and switchboard phone, for AMLR Art. 22 / IVMS 101 enriched CDD.

```mermaid
flowchart TD
    subgraph Entity["Legal Entity — Originator"]
        LP["🏢 Nordvik Shipping AS\nLegalPerson · NO\n(Short name: Nordvik)\nHQ: Oslo, Norway"]

        subgraph Contact["Contact Details (LegalPerson extensions)"]
            EMAIL["📧 compliance@nordvik-shipping.example"]
            PHONE["📞 +47 22 12 34 56"]
        end

        subgraph Banking["Banking Details — Multiple Accounts"]
            IBAN1["🏦 Account 1: NO93 8601 1117 947\n(Norwegian bank — primary)"]
            IBAN2["🏦 Account 2: NL91ABNA0417164300\n(ABN AMRO Amsterdam — EU correspondent)"]
        end
    end

    subgraph Transfer["Transfer"]
        OVASP["🏦 Originating VASP · NO"]
        BVASP["🏦 Beneficiary VASP · Counterparty"]
    end

    LP --> Contact
    LP --> Banking
    LP -- "250,000 EUR" --> OVASP
    OVASP -- "IVMS 101 Travel Rule\n250,000 EUR" --> BVASP

    style LP fill:#ede9fe,stroke:#7c3aed
    style EMAIL fill:#f0fdf4,stroke:#16a34a
    style PHONE fill:#f0fdf4,stroke:#16a34a
    style IBAN1 fill:#dbeafe,stroke:#3b82f6
    style IBAN2 fill:#dbeafe,stroke:#3b82f6
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
```

## Contact and Banking Fields

| Field | Path | Value |
|---|---|---|
| Email | `legalPerson.emailAddress` | `compliance@nordvik-shipping.example` |
| Phone | `legalPerson.phoneNumber` | `+4722123456` |
| Account 1 | `legalPerson.bankingDetails[0]` | `NO9386011117947` (primary) |
| Account 2 | `legalPerson.bankingDetails[1]` | `NL91ABNA0417164300` (EU correspondent) |

## Key Data Points

| Field | Value |
|---|---|
| Subject | Nordvik Shipping AS (NO) |
| Contact | Compliance email + main phone |
| Banking | 2 accounts — NO primary + NL EU correspondent |
| Amount | 250,000 EUR |
| Regulatory basis | AMLR Art. 22 CDD; IVMS 101 extended legal-entity profile |
