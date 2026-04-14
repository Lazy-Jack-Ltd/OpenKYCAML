### Mapping Table: IVMS 101 ↔ eIDAS 2.0 PID / LPID Attributes

| IVMS 101 Field (Natural Person)                  | eIDAS 2.0 PID Attribute (Mandatory / Optional) | Notes / Mapping Guidance |
|--------------------------------------------------|-------------------------------------------------|--------------------------|
| `naturalPerson.name.nameIdentifier[0].primaryIdentifier` (LEGL) | `family_name` (M)                              | Primary surname |
| `naturalPerson.name.nameIdentifier[0].secondaryIdentifier` | `given_name` (M)                               | First/middle names |
| `naturalPerson.dateAndPlaceOfBirth.dateOfBirth`  | `birth_date` (M)                               | ISO 8601 date |
| `naturalPerson.dateAndPlaceOfBirth.placeOfBirth` | `birth_place` (O)                              | City / country of birth |
| `naturalPerson.countryOfResidence`               | `resident_country` or `nationality` (O)        | Two-letter ISO code |
| `naturalPerson.geographicAddress[]`              | `resident_address` (structured: street, house number, postal code, city, etc.) (O) | Full structured address mapping |
| `naturalPerson.nationalIdentification.nationalIdentifier` + `nationalIdentifierType` | `person_identifier` or `personal_administrative_number` (O) | National ID / passport number |
| `naturalPerson.nationalIdentification` with `LEIX` | `person_identifier` (can carry LEI)           | LEI support |

| IVMS 101 Field (Legal Person)                    | eIDAS 2.0 LPID Attribute                        | Notes / Mapping Guidance |
|--------------------------------------------------|-------------------------------------------------|--------------------------|
| `legalPerson.name.nameIdentifier[0].legalPersonName` | `current_legal_name` (M)                       | Legal entity name |
| `legalPerson.nationalIdentification.nationalIdentifier` (LEIX) | `lei` or `unique_identifier` (O/M)             | LEI is explicitly supported in LPID |
| `legalPerson.geographicAddress[]`                | `current_address` (O)                          | Registered address |
| `legalPerson.countryOfRegistration`              | Registration country (derived from unique ID)  | ISO code |
| `legalPerson.customerNumber`                     | VAT / Tax reference / EORI (O)                 | Optional LPID fields |

**Key differences**
- eIDAS PID/LPID are **flatter** and privacy-focused (selective disclosure via SD-JWT).
- IVMS 101 is richer for financial messaging (multiple name types, phonetic names, VASP details, transfer path).
- The hybrid schema lets you store the rich IVMS data inside the VC so you stay compliant with both worlds.
