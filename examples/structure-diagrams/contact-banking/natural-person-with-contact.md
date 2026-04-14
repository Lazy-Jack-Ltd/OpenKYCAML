# contact-banking/natural-person-with-contact.json — Structure Diagram

**Scenario:** Natural Person with Contact Details and Banking Information.  
Anna Mueller (DE) sends 1,500 EUR. The record demonstrates the `emailAddress`, `phoneNumber`, and `bankingDetails` extensions on `NaturalPerson` — capturing real-world CDD contact-and-account data for AMLR Art. 22 and IVMS 101 enriched profiles.

```mermaid
flowchart TD
    subgraph Person["Natural Person — Originator"]
        NP["👤 Anna Mueller\nNaturalPerson · DE\nDOB / address on file"]

        subgraph Contact["Contact Details (NaturalPerson extensions)"]
            EMAIL["📧 email: anna.mueller@example.de"]
            PHONE["📞 phone: +49 69 12 34 56 789"]
        end

        subgraph Banking["Banking Details"]
            IBAN["🏦 IBAN: DE89370400440532013000\n(Commerzbank Frankfurt)"]
        end
    end

    subgraph Transfer["Transfer"]
        OVASP["🏦 Originating VASP · DE"]
        BVASP["🏦 Beneficiary VASP · Counterparty"]
    end

    NP --> Contact
    NP --> Banking
    NP -- "1,500 EUR" --> OVASP
    OVASP -- "IVMS 101 Travel Rule\n1,500 EUR" --> BVASP

    style NP fill:#dbeafe,stroke:#3b82f6
    style EMAIL fill:#f0fdf4,stroke:#16a34a
    style PHONE fill:#f0fdf4,stroke:#16a34a
    style IBAN fill:#dbeafe,stroke:#3b82f6
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
```

## Contact and Banking Fields

| Field | Path | Value |
|---|---|---|
| Email address | `naturalPerson.emailAddress` | `anna.mueller@example.de` |
| Phone number | `naturalPerson.phoneNumber` | `+4969123456789` |
| IBAN | `naturalPerson.bankingDetails[0].iban` | `DE89370400440532013000` |

## Key Data Points

| Field | Value |
|---|---|
| Subject | Anna Mueller (DE) |
| Contact | Email + phone on record |
| Banking | DE IBAN (Commerzbank Frankfurt) |
| Amount | 1,500 EUR |
| Regulatory basis | AMLR Art. 22 CDD data collection; IVMS 101 extended profile |
