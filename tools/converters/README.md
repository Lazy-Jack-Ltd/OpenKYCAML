# OpenKYCAML Converters

This directory contains mapping scripts for converting between OpenKYCAML and other formats.

## Available Converters

| Script | Language | Description |
|---|---|---|
| [`../python/converter.py`](../python/converter.py) | Python | IVMS 101 ↔ OpenKYCAML, eIDAS 2.0 PID ↔ OpenKYCAML, eIDAS 2.0 LPID ↔ OpenKYCAML, OpenKYCAML → ISO 20022 (simplified dict), VC extraction |
| [`../../iso20022-integration/libraries/python/converter.py`](../../iso20022-integration/libraries/python/converter.py) | Python | **Full ISO 20022 XML** — `openkycaml_to_pacs008()`, `openkycaml_to_pain001()`, `iso20022_to_openkycaml()` |
| [`../../iso20022-integration/libraries/typescript/converter.ts`](../../iso20022-integration/libraries/typescript/converter.ts) | TypeScript | Same three ISO 20022 functions as ESM module |
| [`../javascript/openvasp-converter.js`](../javascript/openvasp-converter.js) | JavaScript | OpenVASP Transfer body ↔ OpenKYCAML `ivms101` block |

## Supported Conversion Commands

### `tools/python/converter.py` (general converters)

| Command | Direction | Description |
|---|---|---|
| `ivms101-to-openkycaml` | IVMS 101 → OpenKYCAML | Wrap a raw IVMS 101 JSON object in an OpenKYCAML envelope |
| `openkycaml-to-ivms101` | OpenKYCAML → IVMS 101 | Extract the raw `ivms101` block from an OpenKYCAML envelope |
| `pid-to-openkycaml` | eIDAS 2.0 PID → OpenKYCAML | Convert a flat eIDAS 2.0 PID attribute map to an OpenKYCAML envelope (natural person originator) |
| `openkycaml-to-pid` | OpenKYCAML → eIDAS 2.0 PID | Extract the natural person originator and return ARF-compliant PID attributes |
| `lpid-to-openkycaml` | eIDAS 2.0 LPID → OpenKYCAML | Convert a flat eIDAS 2.0 LPID attribute map to an OpenKYCAML envelope (legal person originator) |
| `openkycaml-to-lpid` | OpenKYCAML → eIDAS 2.0 LPID | Extract the legal person originator and LPID block, returning ARF-compliant LPID attributes |
| `openkycaml-to-iso20022` | OpenKYCAML → ISO 20022 | Simplified ISO 20022 pain.001 dict (for legacy integrations — use the full XML library below for production) |
| `extract-vc` | OpenKYCAML → W3C VC | Extract the `verifiableCredential` block from an OpenKYCAML envelope |

### `iso20022-integration/libraries/python/converter.py` (full ISO 20022 XML)

| Command | Direction | Description |
|---|---|---|
| `openkycaml-to-pacs008` | OpenKYCAML → pacs.008 XML | Full CBPR+ pacs.008 message with KYCAMLEnvelope in `<SplmtryData>` |
| `openkycaml-to-pain001` | OpenKYCAML → pain.001 XML | Full pain.001 message with KYCAMLEnvelope in `<SplmtryData>` |
| `iso20022-to-openkycaml` | pacs.008/pain.001 XML → OpenKYCAML | Parse XML and reconstruct OpenKYCAML payload including KYCAMLEnvelope |

## PID / LPID Flat Attribute Maps

The **PID** (Person Identification Data) and **LPID** (Legal Person Identification Data)
converters follow the EU Digital Identity Architecture and Reference Framework (ARF)
attribute naming conventions.

### PID Attributes Supported

| ARF Attribute | Maps to OpenKYCAML |
|---|---|
| `family_name` | `ivms101.originator.originatorPersons[0].naturalPerson.name.nameIdentifier[0].primaryIdentifier` |
| `given_name` | `ivms101.originator.originatorPersons[0].naturalPerson.name.nameIdentifier[0].secondaryIdentifier` |
| `birth_date` | `naturalPerson.dateAndPlaceOfBirth.dateOfBirth` |
| `birth_place` | `naturalPerson.dateAndPlaceOfBirth.placeOfBirth` |
| `resident_street` / `resident_house_number` | `naturalPerson.geographicAddress[0].streetName` / `buildingNumber` |
| `resident_postal_code` | `naturalPerson.geographicAddress[0].postCode` |
| `resident_city` | `naturalPerson.geographicAddress[0].townName` |
| `resident_country` | `naturalPerson.geographicAddress[0].country` |
| `personal_administrative_number` | `naturalPerson.nationalIdentification.nationalIdentifier` |
| `issuing_country` | `naturalPerson.nationalIdentification.countryOfIssue` |
| `nationalities` | `naturalPerson.nationality` (first element) |
| `address` (nested object) | Mapped to `geographicAddress[0]` |

### LPID Attributes Supported

| ARF Attribute | Maps to OpenKYCAML |
|---|---|
| `legal_name` / `current_legal_name` | `legalPerson.name.nameIdentifier[0].legalPersonName` + `lpid.currentLegalName` |
| `legal_person_identifier` / `unique_identifier` | `legalPerson.nationalIdentification.nationalIdentifier` + `lpid.uniqueIdentifier` |
| `country_of_registration` / `issuing_country` | `legalPerson.countryOfRegistration` + `lpid.issuing_country` |
| `legal_address` / `registered_address` (nested object) | `legalPerson.geographicAddresses[0]` + `lpid.currentAddress` |
| `lei` | `lpid.lei` |
| `vat_registration_number` | `lpid.vatRegistrationNumber` |
| `tax_reference_number` | `lpid.taxReferenceNumber` |
| `eori_number` | `lpid.eoriNumber` |
| `european_unique_identifier` | `lpid.europeanUniqueIdentifier` |

## Usage Examples

```bash
# PID → OpenKYCAML
python tools/python/converter.py pid-to-openkycaml pid.json --out openkycaml-from-pid.json

# OpenKYCAML → PID
python tools/python/converter.py openkycaml-to-pid examples/natural-person-plain.json

# LPID → OpenKYCAML
python tools/python/converter.py lpid-to-openkycaml lpid.json --out openkycaml-from-lpid.json

# OpenKYCAML → LPID
python tools/python/converter.py openkycaml-to-lpid examples/legal-entity-plain.json

# IVMS 101 → OpenKYCAML
python tools/python/converter.py ivms101-to-openkycaml ivms101.json --out openkycaml.json

# OpenKYCAML → pacs.008 XML (full ISO 20022)
python iso20022-integration/libraries/python/converter.py openkycaml-to-pacs008 examples/minimal-travel-rule.json

# OpenKYCAML → pain.001 XML (full ISO 20022)
python iso20022-integration/libraries/python/converter.py openkycaml-to-pain001 examples/full-kyc-profile.json

# pacs.008 XML → OpenKYCAML
python iso20022-integration/libraries/python/converter.py iso20022-to-openkycaml message.xml
```

## Planned Converters

| Script | Language | Status |
|---|---|---|
| `swift-mt-to-openkycaml.py` | Python | Planned for v1.4 |
| `openvasp-to-openkycaml.js` | JavaScript | Planned for v1.4 |

## Usage

See the [Adoption Guide](../../docs/adoption-guide.md) for detailed conversion examples, including the [ISO 20022 integration section](../../docs/adoption-guide.md#6-use-case-5-integrating-with-legacy-payment-rails-via-iso-20022).
