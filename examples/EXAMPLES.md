# OpenKYCAML Example Payloads

This document is the definitive index for all JSON examples in the [`examples/`](./) directory.  
Every example is a complete, schema-valid payload that can be used as a starting point for integration, a regression fixture for CI, or a reference when building test suites.

---

## Contents

1. [Overview](#1-overview)
2. [How to validate an example](#2-how-to-validate-an-example)
3. [How to use examples for testing](#3-how-to-use-examples-for-testing)
4. [Example catalogue](#4-example-catalogue)
5. [Category descriptions](#5-category-descriptions)
6. [Notes on special files](#6-notes-on-special-files)
7. [Future folder structure](#7-future-folder-structure)

---

## 1. Overview

> **Fictional data notice:** All names, passport numbers, national identifiers, addresses, entity names, LEIs, DIDs, wallet addresses, and any other personal or entity data in the example payloads are **entirely fictional** and have been created solely for illustrative purposes. Any resemblance to real persons (living or deceased), real legal entities, or real transactions is entirely coincidental.

There are currently **49 example files** covering seventeen categories:

| # | Category | Files |
|---|---|---|
| A | Baseline — Travel Rule | 2 |
| B | Natural Person | 5 |
| C | Legal Entity | 5 |
| D | Complex Ownership Structures | 5 |
| E | VC-Wrapped & Travel Rule VC | 4 |
| F | Document Bundles (v1.5.0) | 2 |
| G | Advanced / Compliance Scenarios | 1 |
| H | Reference / Annotated Tokens | 1 |
| I | PKI Evidence — X.509 / X.500 (v1.8.0) | 2 |
| J | Tax Status (v1.9.0) | 5 |
| K | PredictiveAML / EU AI Act (v1.7.0) | 3 |
| L | Contact / Banking Identifiers (v1.10.0) | 2 |
| M | Cell Companies — PCC / ICC (v1.11.0) | 3 |
| N | Entity & Person Governance (v1.12.0) | 3 |
| O | Presentation Definitions (OpenID4VP) | 1 |
| P | CRM Completeness (v1.13.0) | 2 |
| Q | Company Identifiers (v1.16.0) | 1 |
| R | Array Grouping (v1.17.0) | 2 |

All files in `examples/` and its sub-directories (`evidence/`, `tax/`, `predictive/`, `contact-banking/`, `cell-company/`, `presentation-definitions/`) validate against [`schema/kyc-aml-hybrid-extended.json`](../schema/kyc-aml-hybrid-extended.json) (JSON Schema draft 2020-12), with the exception of `sd-jwt-compact-token.json` which is an annotated reference document — see [§6](#6-notes-on-special-files).

---

## 2. How to validate an example

### Python

```bash
pip install -r tools/python/requirements.txt
python tools/python/validator.py examples/minimal-travel-rule.json
```

To validate all examples in one pass:

```bash
python - <<'EOF'
import json, pathlib
from jsonschema import Draft202012Validator

schema = json.load(open("schema/kyc-aml-hybrid-extended.json"))
validator = Draft202012Validator(schema)
failed = 0
for f in sorted(pathlib.Path("examples").glob("*.json")):
    errors = list(validator.iter_errors(json.load(open(f))))
    print(("FAIL" if errors else "PASS") + f": {f.name}")
    for e in errors:
        print(f"      {e.message}")
    if errors:
        failed += 1
print(f"\n{len(list(pathlib.Path('examples').glob('*.json'))) - failed} passed, {failed} failed.")
EOF
```

### Node.js / JavaScript

```bash
cd tools/javascript
npm install
node validator.js ../../examples/minimal-travel-rule.json
```

### Go

```bash
cd tools/go
go run . ../../examples/minimal-travel-rule.json
```

---

## 3. How to use examples for testing

### CI — automatic regression coverage

The GitHub Actions workflow [`.github/workflows/validate-schema.yml`](../.github/workflows/validate-schema.yml) runs **all** `examples/*.json` files against the canonical schema on every push and pull request that touches `schema/`, `examples/`, or `tools/`.  
**Adding a new example file to `examples/` automatically enrolls it in CI** — no workflow changes are needed.

### Integration test fixtures

Examples are designed as copy-paste fixtures.  A typical test pattern:

```python
import json, pytest
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA = json.load(open("schema/kyc-aml-hybrid-extended.json"))
VALIDATOR = Draft202012Validator(SCHEMA)

@pytest.mark.parametrize("example", sorted(Path("examples").glob("*.json")))
def test_example_validates(example):
    payload = json.load(open(example))
    errors = list(VALIDATOR.iter_errors(payload))
    assert not errors, f"{example.name}: {[e.message for e in errors]}"
```

### Scenario-based testing

Each example targets a specific compliance scenario.  Use the catalogue table in [§4](#4-example-catalogue) to identify the example that matches your use-case, then:

1. Copy the file into your test fixtures directory.
2. Substitute fictional persona fields (names, addresses, dates of birth) with your own test data.
3. Run your integration's inbound parser or outbound serialiser against the mutated fixture.

---

## 4. Example catalogue

> **Column key**  
> `IVMS` = `ivms101` block present · `VC` = `verifiableCredential` block · `KYC` = `kycProfile` block · `Docs` = `identityDocuments` block · `GDPR` = `gdprSensitivityMetadata` block · `TxMon` = `transactionMonitoring` block · `PKI` = `pkiEvidence` / `legacyIdentifiers` blocks

| File | Category | Subject | Ver | IVMS | VC | KYC | Docs | GDPR | TxMon | PKI | Scenario |
|---|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| [`minimal-travel-rule.json`](minimal-travel-rule.json) | A — Baseline | Natural person | 1.3.0 | ✓ | | | | | | | Minimum-viable FATF Travel Rule payload: originator + beneficiary, no extras |
| [`minimal-travel-rule-eudi-wallet.json`](minimal-travel-rule-eudi-wallet.json) | A — Baseline | Natural person | 1.3.0 | ✓ | ✓ | | | | | | Travel Rule with EUDI Wallet VC evidence; DID triangulation (JP→BTC→FR) |
| [`natural-person-plain.json`](natural-person-plain.json) | B — Natural Person | Natural person | 1.3.0 | ✓ | | | | | | | Plain IVMS 101 natural person CDD — SDD-level KYC onboarding baseline |
| [`natural-person-eudi-wallet.json`](natural-person-eudi-wallet.json) | B — Natural Person | Natural person | 1.3.0 | ✓ | ✓ | | | | | | EUDI Wallet onboarding (Anna Müller / DE); PID Issuer + VASP DID chain |
| [`natural-person-sd-jwt-eudi-wallet.json`](natural-person-sd-jwt-eudi-wallet.json) | B — Natural Person | Natural person | 1.3.0 | ✓ | ✓ | | | | | | SD-JWT selective disclosure via EUDI Wallet; `_sd` digests for non-revealed claims |
| [`full-kyc-profile.json`](full-kyc-profile.json) | B — Natural Person | Natural person | 1.3.0 | ✓ | | ✓ | | | | | Full KYC profile with EDD, PEP flag, source of wealth, and UBO list |
| [`full-kyc-profile-eudi-wallet.json`](full-kyc-profile-eudi-wallet.json) | B — Natural Person | Natural person | 1.3.0 | ✓ | ✓ | | | | | | EDD / PEP KYC profile via EUDI Wallet (Fatima Al-Rashidi / AE); vLEI chain |
| [`legal-entity-plain.json`](legal-entity-plain.json) | C — Legal Entity | Legal entity | 1.3.0 | ✓ | | | | | | | Plain IVMS 101 legal entity — minimal corporate CDD baseline |
| [`legal-entity-eudi-wallet.json`](legal-entity-eudi-wallet.json) | C — Legal Entity | Legal entity | 1.3.0 | ✓ | ✓ | | | | | | EUDI Wallet LPID onboarding (Global Trade Solutions GmbH / DE) |
| [`legal-entity-sd-jwt-eudi-wallet.json`](legal-entity-sd-jwt-eudi-wallet.json) | C — Legal Entity | Legal entity | 1.3.0 | ✓ | ✓ | | | | | | SD-JWT selective disclosure for LPID credential (Acme Digital Trading BV) |
| [`legal-entity-trust.json`](legal-entity-trust.json) | C — Legal Entity | Legal entity | 1.4.0 | ✓ | | ✓ | | | | | ISO 20275 trust (ELF code `L295`); `trustDetails` sub-object; Cayman Islands discretionary trust |
| [`legal-entity-partnership.json`](legal-entity-partnership.json) | C — Legal Entity | Legal entity | 1.4.0 | ✓ | | ✓ | | | | | ISO 20275 LLP (ELF code `Z13E`); `partnershipDetails` sub-object; Scottish LP |
| [`legal-entity-deep-ubo.json`](legal-entity-deep-ubo.json) | D — Complex Ownership | Legal entity | 1.3.0 | ✓ | ✓ | | | | | | 4-tier corporate UBO chain — AMLR Art. 26 EDD beneficial ownership disclosure |
| [`complex-group-multi-tier.json`](complex-group-multi-tier.json) | D — Complex Ownership | Legal entity | 1.3.0 | ✓ | ✓ | | | | | | 4-layer holding structure with natural person UBOs at every tier |
| [`foundation-complex-ubo.json`](foundation-complex-ubo.json) | D — Complex Ownership | Legal entity | 1.3.0 | ✓ | ✓ | | | | | | Liechtenstein Privatstiftung; `foundationDetails`; settlor + protector + beneficiary roles |
| [`llp-complex-ubo.json`](llp-complex-ubo.json) | D — Complex Ownership | Legal entity | 1.3.0 | ✓ | ✓ | | | | | | UK LLP with corporate general partner; multiple designated member roles |
| [`trust-complex-ubo.json`](trust-complex-ubo.json) | D — Complex Ownership | Legal entity | 1.3.0 | ✓ | ✓ | | | | | | Jersey discretionary trust with corporate trustee and multiple beneficiary classes |
| [`hybrid-vc-wrapped.json`](hybrid-vc-wrapped.json) | E — VC-Wrapped | Natural person | 1.3.0 | ✓ | ✓ | | | | ✓ | | IVMS 101 + `kycProfile` inside a W3C VC; transaction monitoring block |
| [`hybrid-vc-eudi-wallet.json`](hybrid-vc-eudi-wallet.json) | E — VC-Wrapped | Natural person | 1.3.0 | ✓ | ✓ | | | | ✓ | | EUDI Wallet companion to `hybrid-vc-wrapped.json`; full DID triangulation |
| [`travel-rule-vc-wrapped.json`](travel-rule-vc-wrapped.json) | E — VC-Wrapped | Natural person | 1.3.0 | | ✓ | | | | ✓ | | Travel Rule entirely inside a VC — no top-level `ivms101` (VC-only pattern) |
| [`travel-rule-vc-eudi-wallet.json`](travel-rule-vc-eudi-wallet.json) | E — VC-Wrapped | Natural person | 1.3.0 | ✓ | ✓ | | | | ✓ | | EUDI Wallet companion to `travel-rule-vc-wrapped.json` |
| [`document-bundle-natural-person.json`](document-bundle-natural-person.json) | F — Document Bundles | Natural person | 1.5.0 | ✓ | | ✓ | ✓ | | | | German national: Personalausweis + proof of address + eIDAS PID VC; `verifyingDocumentRef` linkage |
| [`document-bundle-legal-entity.json`](document-bundle-legal-entity.json) | F — Document Bundles | Legal entity | 1.5.0 | ✓ | | ✓ | ✓ | | | | UK PLC: Certificate of Incorporation + Companies House extract + LEI + vLEI OOR |
| [`hybrid-with-sar-restriction.json`](hybrid-with-sar-restriction.json) | G — Advanced | Legal entity | 1.3.0 | ✓ | ✓ | | | ✓ | | | SAR filing in progress; `gdprSensitivityMetadata` tipping-off protection; restricted field list |
| [`sd-jwt-compact-token.json`](sd-jwt-compact-token.json) | H — Reference Token | Natural person | 1.3.0 | | | ✓ | | | | | ⚠ Annotated reference — decoded SD-JWT with `compactToken`, `decodedDisclosures`, `verificationSteps`; **not schema-valid** |
| [`evidence/eidas-x509-dn.json`](evidence/eidas-x509-dn.json) | I — PKI Evidence | Legal entity | 1.8.0 | ✓ | | ✓ | ✓ | | | ✓ | Legal entity QSealC certificate: `legacyIdentifiers.x500DN` + `pkiEvidence.x509Certificate` (ETSI EN 319 412 QCStatements, OCSP) |
| [`evidence/eidas-x509-qeaa.json`](evidence/eidas-x509-qeaa.json) | I — PKI Evidence | Natural person | 1.8.0 | ✓ | ✓ | ✓ | ✓ | | | ✓ | Natural person QEAA + EUDI Wallet triangulation: VC evidence + `pkiEvidence` X.509 metadata + `legacyIdentifiers.x500DN` + OIDs |
| [`tax/tax-individual-tin.json`](tax/tax-individual-tin.json) | J — Tax Status | Natural person | 1.9.0 | ✓ | | ✓ | | | | | Individual TIN self-certification — OECD CRS multi-jurisdiction TIN array, unverified status |
| [`tax/tax-corporate-vat-gst.json`](tax/tax-corporate-vat-gst.json) | J — Tax Status | Legal entity | 1.9.0 | ✓ | | ✓ | | | | | Corporate VAT/GST registrations across EU/UK/AU/SG jurisdictions; VIES and GST-portal verification |
| [`tax/tax-fatca-crs.json`](tax/tax-fatca-crs.json) | J — Tax Status | Legal entity | 1.9.1 | ✓ | | ✓ | | | | | FATCA GIIN + Chapter 4 classification (participatingFFI) + CRS crsTaxResidencies[] |
| [`tax/tax-mne-pillar2.json`](tax/tax-mne-pillar2.json) | J — Tax Status | Legal entity | 1.9.0 | ✓ | | ✓ | | | | | Multinational constituent entity — OECD Pillar 2 GloBE ETR per jurisdiction + GIR filing reference |
| [`tax/tax-offshore-esr.json`](tax/tax-offshore-esr.json) | J — Tax Status | Legal entity | 1.9.0 | ✓ | | ✓ | | | | | Cayman Islands holding company — Economic Substance Regulation compliance (inScope + compliant) |
| [`predictive/predictive-static.json`](predictive/predictive-static.json) | K — PredictiveAML | Natural person | 1.7.0 | ✓ | | ✓ | | | | | Static risk snapshot with SHAP feature importance; EU AI Act model card metadata |
| [`predictive/predictive-delta.json`](predictive/predictive-delta.json) | K — PredictiveAML | Natural person | 1.7.0 | ✓ | | ✓ | | | | | Delta-based cKYC — risk evolution history with multiple scored snapshots |
| [`predictive/predictive-ai-high-risk.json`](predictive/predictive-ai-high-risk.json) | K — PredictiveAML | Natural person | 1.7.0 | ✓ | | ✓ | | | | | High-risk AI score with EU AI Act conformity statement and BCBS 239 gap-analysis flags |
| [`contact-banking/natural-person-with-contact.json`](contact-banking/natural-person-with-contact.json) | L — Contact/Banking | Natural person | 1.10.0 | ✓ | | ✓ | | | | | Natural person with email, E.164 phone/mobile, and verified IBAN/BIC banking details |
| [`contact-banking/legal-entity-with-banking.json`](contact-banking/legal-entity-with-banking.json) | L — Contact/Banking | Legal entity | 1.10.0 | ✓ | | ✓ | | | | | Legal entity with business email, phone, and multi-account banking details (IBAN + BIC + accountType) |
| [`cell-company/pcc-cell.json`](cell-company/pcc-cell.json) | M — Cell Companies | Legal entity | 1.11.0 | ✓ | | ✓ | | | | | PCC Cell with `cellCompanyDetails` + mandatory `parentCellCompanyReference`; Guernsey PCC structure |
| [`cell-company/icc-cell.json`](cell-company/icc-cell.json) | M — Cell Companies | Legal entity | 1.11.0 | ✓ | | ✓ | | | | | ICC Cell with own legal personality (`hasIndependentLegalPersonality: true`) + registration number; Jersey ICC |
| [`cell-company/pcc-cell-predictive-aml.json`](cell-company/pcc-cell-predictive-aml.json) | M — Cell Companies | Legal entity | 1.11.2 | ✓ | | ✓ | | | | | PCC Cell with `cellLevelPredictiveScores[]` in predictiveAML block (v1.11.2 addition) |
| [`legal-entity-governance.json`](legal-entity-governance.json) | N — Governance | Legal entity | 1.12.0 | ✓ | | ✓ | | | | | Dual-regulated, exchange-listed subsidiary; `entityGovernance` with `regulators[]`, `listedStatus` (XETR), `parentRegulated`, `majorityOwnedSubsidiary` |
| [`natural-person-gender-occupation.json`](natural-person-gender-occupation.json) | N — Governance | Natural person | 1.12.0 | ✓ | | ✓ | | | | | Natural person with `gender: FEMALE`, `occupation.occupationCode: SELF_EMPLOYED`, and `reviewLifecycle` state history |
| [`amlr2027-fatca-ai-act.json`](amlr2027-fatca-ai-act.json) | N — Governance | Legal entity | 1.9.1 | ✓ | ✓ | ✓ | ✓ | | | ✓ | End-to-end reference: predictiveAML (EU AI Act) + taxStatus (FATCA/CRS/Pillar 2) + pkiEvidence (QSealC) + legacyIdentifiers (X.500 DN) |
| [`crm-natural-person-full.json`](crm-natural-person-full.json) | P — CRM Completeness | Natural person | 1.13.0 | ✓ | | ✓ | | | | | Full CRM natural person: historicalNames, marital status, emergency contact, typed emailAddresses/phoneNumbers, preferred language/channel, relationship manager, customer segment, estimated net worth |
| [`crm-legal-entity-full.json`](crm-legal-entity-full.json) | P — CRM Completeness | Legal entity | 1.13.0 | ✓ | | ✓ | | | | | Full CRM legal entity: incorporation/dissolution dates, operational status, employee count, revenue, website, social media, industryCodes, registeredAgent, typed contact arrays, entityGovernance (ultimate parent, group LEI), mandates, relationship manager |
| [`company-identifiers.json`](company-identifiers.json) | Q — Company Identifiers | Legal entity | 1.16.0 | ✓ | | ✓ | | | | | Legal entity with `companyIdentifiers[]` using the 23-value `CompanyIdentifier` $def (DUNS, LEI, CRN_GB, ABN_AU, EIN_US, etc.) |
| [`array-grouping-v1-17.json`](array-grouping-v1-17.json) | R — Array Grouping | Natural person | 1.17.0 | ✓ | | ✓ | | | | | Natural person with new v1.17.0 structured arrays: `naturalPersonIdentifiers[]`, `countriesOfResidence[]`, `nationalities[]`, `occupations[]`, `emergencyContacts[]`; `kycProfile` with `riskRatingHistory[]`, `pepStatuses[]`, `consentRecords[]` |
| [`array-grouping-legal-entity-v1-17.json`](array-grouping-legal-entity-v1-17.json) | R — Array Grouping | Legal entity | 1.17.0 | ✓ | | ✓ | | | | | Legal entity with new v1.17.0 structured arrays: `legalNationalIdentifiers[]`, `revenueHistory[]`, `registeredAgents[]`; `entityGovernance.parentCompanies[]` |
| [`presentation-definitions/travel-rule-minimum.json`](presentation-definitions/travel-rule-minimum.json) | O — Presentation Defs | — | 1.7.0 | — | — | — | — | — | — | — | OpenID4VP Presentation Definition for the FATF Travel Rule minimum credential request |

---

## 5. Category descriptions

### A — Baseline: Travel Rule

The two `minimal-travel-rule` files are the lightest possible payloads that satisfy FATF Travel Rule requirements: originator and beneficiary IVMS 101 blocks, a `messageId`, and a timestamp.  Use these as the starting point when building a new integration or when you need a minimal fixture for unit tests.

### B — Natural Person

Natural person examples span the full range of onboarding complexity, from a plain SDD CDD payload through to a full EDD profile with PEP flag, source-of-wealth narrative, and UBO list.  The three EUDI Wallet variants (`-eudi-wallet`, `-sd-jwt-eudi-wallet`, `full-kyc-profile-eudi-wallet`) demonstrate EBSI DID triangulation and selective disclosure using SD-JWT `_sd` digest arrays.

### C — Legal Entity

Legal entity examples mirror the natural person set.  The plain and EUDI Wallet baselines cover standard corporate CDD.  The `legal-entity-trust.json` and `legal-entity-partnership.json` files (both v1.4.0) exercise the ISO 20275 ELF `legalFormCode`, `entityType` enum, and the typed sub-objects (`trustDetails`, `partnershipDetails`) introduced in v1.4.0.

### D — Complex Ownership Structures

Five files cover high-complexity beneficial ownership disclosure required by AMLR Art. 26 EDD.  `legal-entity-deep-ubo.json` demonstrates a 4-tier holding chain terminating in natural person UBOs.  `complex-group-multi-tier.json` adds intermediate SPVs at each level.  The `foundation-complex-ubo`, `llp-complex-ubo`, and `trust-complex-ubo` files each isolate a distinct legal structure, showing how settlor / protector / general-partner / designated-member roles map onto the IVMS 101 `beneficialOwner` array.

### E — VC-Wrapped & Travel Rule VC

Four files show how to embed IVMS 101 data inside W3C Verifiable Credentials.  The `hybrid-vc-*` pair adds a `kycProfile` and `transactionMonitoring` block alongside the VC.  The `travel-rule-vc-*` pair demonstrates the VC-only pattern where the IVMS 101 originator / beneficiary objects live entirely within the credential subject — note that `travel-rule-vc-wrapped.json` has **no top-level `ivms101` key**.

### F — Document Bundles (v1.5.0)

Introduced in schema v1.5.0, these two files demonstrate the `identityDocuments` block (`VerificationDocumentBundle`).  Each document in the bundle is typed (e.g. `PASSPORT`, `PROOF_OF_ADDRESS`, `CORPORATE_REGISTRATION`), carries extracted attribute references, and links back to IVMS 101 fields via `verifyingDocumentRef` pointers.  The legal entity bundle also illustrates `registrationAuthorityDetail` with a GLEIF RAL entry (`RA000585`, Companies House) and ELF code `Z13E`.

### G — Advanced: Compliance Scenarios

`hybrid-with-sar-restriction.json` is the reference example for the `gdprSensitivityMetadata` block (v1.3.0).  It demonstrates how a VASP that has filed a SAR sets `classification: "sar_restricted"`, `tippingOffProtected: true`, and enumerates restricted field paths.  The SD-JWT encoding guidance for this scenario is covered in [§12 of the EUDI Wallet Integration Guide](../docs/eudi-wallet-integration.md).

### H — Reference Tokens

`sd-jwt-compact-token.json` is an **annotated reference document**, not a schema-valid payload.  It decodes a compact SD-JWT into its constituent parts — Issuer-JWT, disclosure array, key-binding JWT — and adds human-readable `verificationSteps` annotations.  Use it as a companion when reading the SD-JWT spec or debugging a presentation flow.  It deliberately fails schema validation; see [§6](#6-notes-on-special-files).

### I — PKI Evidence: X.509 / X.500 (v1.8.0)

Two files in `examples/evidence/` demonstrate the new optional `legacyIdentifiers` and `pkiEvidence` blocks introduced in schema v1.8.0.

`eidas-x509-dn.json` shows a legal entity (Acme Bank PLC) with a QSealC (Qualified Electronic Seal Certificate) issued by a UK QTSP.  It populates `legacyIdentifiers.x500DN` (certificateSubject), `pkiEvidence.x509Certificate` with ETSI EN 319 412 QCStatements (`id-etsi-qcs-QcCompliance`, `id-etsi-qcs-QcType-eSeal`, `id-etsi-qcs-QcSSCD`), CRL distribution points, an OCSP responder URL, and an `oids[]` array with the `organizationIdentifier` OID (2.5.4.97) carrying the entity's LEI in LEIX format.

`eidas-x509-qeaa.json` shows a natural person (fictional name) with a QEAA (Qualified Electronic Attestation of Attributes) from a German QTSP, presented via an EUDI Wallet.  It combines three identity layers: a W3C VC `evidence[]` block (EUDI Wallet DID triangulation), a `pkiEvidence.x509Certificate` block (X.509 metadata), and `legacyIdentifiers.x500DN` (certificateSubject).  The `oids[]` array carries the `id-etsi-qcs-QcType-eAttestation` QCStatement OID confirming QEAA status.

### J — Tax Status (v1.9.0)

Five files in `examples/tax/` demonstrate the `taxStatus` block introduced in v1.9.0 (extended in v1.9.1 with FATCA/CRS first-class elements).  Each file isolates a distinct tax scenario:

- `tax-individual-tin.json` — individual TIN self-certification with multi-jurisdiction OECD CRS TIN array.
- `tax-corporate-vat-gst.json` — corporate VAT/GST registrations across EU/UK/AU/SG with VIES and GST-portal verification statuses.
- `tax-fatca-crs.json` — FATCA GIIN + Chapter 4 classification (`participatingFFI`) + `crsTaxResidencies[]`.
- `tax-mne-pillar2.json` — multinational constituent entity OECD Pillar 2 GloBE ETR per jurisdiction + GIR filing reference.
- `tax-offshore-esr.json` — Cayman Islands holding company ESR compliance (inScope + compliant status).

### K — PredictiveAML / EU AI Act (v1.7.0)

Three files in `examples/predictive/` demonstrate the `predictiveAML` extension introduced in v1.7.0:

- `predictive-static.json` — single static risk snapshot with SHAP feature importance and EU AI Act model card.
- `predictive-delta.json` — delta-based cKYC with a `riskEvolutionHistory[]` showing progressive risk changes.
- `predictive-ai-high-risk.json` — high-risk AI-generated score with EU AI Act conformity statement (`euAiActConformity`), BCBS 239 data lineage (`dataAggregationMetadata`), and explainability block (`explanationMethod: SHAP`).

### L — Contact / Banking Identifiers (v1.10.0)

Two files in `examples/contact-banking/` demonstrate the contact and banking identifier fields added in v1.10.0:

- `natural-person-with-contact.json` — natural person with validated email (RFC 5321), E.164 phone/mobile, and IBAN/BIC banking details.
- `legal-entity-with-banking.json` — legal entity with business email, phone, and multi-account banking details (IBAN + BIC + `accountType` classification).

### M — Cell Companies — PCC / ICC (v1.11.0)

Three files in `examples/cell-company/` demonstrate PCC and ICC cell company structures introduced in v1.11.0:

- `pcc-cell.json` — Protected Cell Company cell with `cellCompanyDetails` and mandatory `parentCellCompanyReference`; Guernsey PCC structure.
- `icc-cell.json` — Incorporated Cell Company cell with own legal personality (`hasIndependentLegalPersonality: true`) and cell-specific registration number; Jersey ICC.
- `pcc-cell-predictive-aml.json` — PCC cell extended with `cellLevelPredictiveScores[]` in the `predictiveAML` block (v1.11.2).

### N — Entity & Person Governance (v1.12.0)

Three files demonstrate the v1.12.0 governance extensions:

- `legal-entity-governance.json` — dual-regulated, exchange-listed subsidiary with `entityGovernance` (BaFin + FCA `regulators[]`, `listedStatus.marketIdentifier: XETR`, `parentRegulated`, `majorityOwnedSubsidiary`).
- `natural-person-gender-occupation.json` — natural person with `gender: FEMALE`, `occupation.occupationCode: SELF_EMPLOYED`, and a `reviewLifecycle` state history (ONBOARDING → INITIAL_REVIEW → PERIODIC_REVIEW).
- `amlr2027-fatca-ai-act.json` — end-to-end reference payload combining predictiveAML (EU AI Act), taxStatus (FATCA/CRS/Pillar 2), pkiEvidence (X.509 QSealC), legacyIdentifiers (X.500 DN), and full EDD kycProfile.

### O — Presentation Definitions (OpenID4VP)

`presentation-definitions/travel-rule-minimum.json` is an OpenID4VP Presentation Definition for the FATF Travel Rule minimum credential request.  Use it as a starting point when building an OpenID4VP verifier that requests the minimum set of claims required for FATF Rec. 16 compliance.

### P — CRM Completeness (v1.13.0)

Two files demonstrate the 20 CRM-completeness field gaps closed in schema v1.13.0:

- `crm-natural-person-full.json` — natural person with the full set of v1.13.0 CRM fields: `historicalNames[]`, `maritalStatus`, `numberOfDependants`, `householdSize`, `emergencyContact`, typed `emailAddresses[]` and `phoneNumbers[]`, `faxNumber`, `preferredLanguage`, `preferredCommunicationChannel`, `marketingOptOut`, `isDeceased`, `tags`, and `customAttributes`; `kycProfile` adds `relationshipManagerId`, `relationshipManagerName`, `primaryBranchCode`, `servingBusinessUnit`, `customerSegment`, `estimatedNetWorth` (with currency and date), `tags`, and `customAttributes`.
- `crm-legal-entity-full.json` — legal entity with the full set of v1.13.0 CRM fields: `dateOfIncorporation`, `dateOfRegistration`, `operationalStatus`, `numberOfEmployees`, `annualRevenue` (with currency and verification date), `websiteUrl`, `socialMediaProfiles[]`, `industryCodes[]`, `registeredAgent`, typed `emailAddresses[]` and `phoneNumbers[]`, `faxNumber`, `entityGovernance` (including `ultimateParentLEI`, `ultimateParentName`, `groupName`, `groupLEI`), structured `mandates[]`, `tags`, and `customAttributes`; `kycProfile` mirrors the natural person CRM profile additions.

### Q — Company Identifiers (v1.16.0)

One file demonstrates the new `CompanyIdentifier` $def and `LegalPerson.companyIdentifiers[]` array added in schema v1.16.0:

- `company-identifiers.json` — legal entity with a `companyIdentifiers[]` block populated with multiple identifier types from the 23-value enum (DUNS, LEI, CRN_GB, ABN_AU, EIN_US, BVDID). Includes an `OTHER` entry with `identifierIssuingBody` as required by the schema's `if`/`then` constraint.

### R — Array Grouping (v1.17.0)

Two files demonstrate the 12 new structured array properties and 4 new $defs (`PersonIdentifier`, `RiskRatingEntry`, `RevenueRecord`, `ConsentRecord`) added in schema v1.17.0:

- `array-grouping-v1-17.json` — natural person with `naturalPersonIdentifiers[]`, `countriesOfResidence[]`, `nationalities[]`, `occupations[]`, `emergencyContacts[]`; `kycProfile` with `riskRatingHistory[]`, `pepStatuses[]`, and `consentRecords[]` (GDPR consent tracking with legalBasis and dataCategories).
- `array-grouping-legal-entity-v1-17.json` — legal entity with `legalNationalIdentifiers[]`, `revenueHistory[]`, `registeredAgents[]`; `entityGovernance.parentCompanies[]` demonstrating multi-parent chain representation.

---

## 6. Notes on special files

### `sd-jwt-compact-token.json`

This file contains top-level keys (`compactToken`, `decodedDisclosures`, `decodedIssuerJWT`, `decodedKeyBindingJWT`, `verificationSteps`, `openid4vpPresentationRequest`) that are not part of the OpenKYCAML schema.  It is intentionally excluded from strict schema validation and is provided purely as a developer reference.  The CI workflow currently validates it as it is structured to pass — it includes a `kycProfile` block — but treat it as documentation rather than a production template.

### `travel-rule-vc-wrapped.json`

This file has **no top-level `ivms101` key**.  The originator and beneficiary data live exclusively inside `verifiableCredential.credentialSubject`.  This is a valid pattern under the schema (`ivms101` is not required at root) but differs from the majority of examples.  Use it when your protocol requires a pure-VC Travel Rule message with no bare IVMS 101 envelope.

### `document-bundle-*.json` (v1.5.0)

These two files use the `identityDocuments` root property and several `$defs` types (`VerificationDocumentBundle`, `NaturalPersonDocument`, `LegalEntityDocument`, `RegistrationAuthorityDetail`, `ExtractedAttribute`) introduced in schema v1.5.0.  They will **not** validate against earlier schema versions.  Check `"version": "1.5.0"` in the file header before using them with a version-pinned validator.

### `legal-entity-trust.json` and `legal-entity-partnership.json` (v1.4.0)

These files use `legalFormCode` (ISO 20275 ELF), `entityType`, and typed sub-objects (`trustDetails`, `partnershipDetails`) introduced in v1.4.0.  They will not validate against v1.3.x schemas.

---

## 7. Folder structure

The examples directory uses a hybrid structure: flat files at the root for the core baseline, natural person, legal entity, ownership, VC-wrapped, document bundle, and advanced scenarios; and sub-directories for the feature-specific categories introduced in v1.7.0–v1.12.0 (predictive AML, tax status, contact/banking, cell companies, and evidence).

The current layout is:

```
examples/
├── minimal-travel-rule*.json        A — Baseline
├── natural-person-*.json            B — Natural Person
├── full-kyc-profile*.json           B — Natural Person
├── legal-entity-*.json              C — Legal Entity
├── *-deep-ubo.json                  D — Complex Ownership
├── complex-group-*.json             D — Complex Ownership
├── foundation-*.json                D — Complex Ownership
├── llp-*.json                       D — Complex Ownership
├── trust-complex-*.json             D — Complex Ownership
├── hybrid-vc-*.json                 E — VC-Wrapped
├── travel-rule-vc-*.json            E — VC-Wrapped
├── document-bundle-*.json           F — Document Bundles
├── hybrid-with-sar-restriction.json G — Advanced
├── sd-jwt-compact-token.json        H — Reference Token
├── amlr2027-fatca-ai-act.json       N — Governance
├── legal-entity-governance.json     N — Governance
├── natural-person-gender-occupation.json N — Governance
├── crm-natural-person-full.json     P — CRM Completeness (v1.13.0)
├── crm-legal-entity-full.json       P — CRM Completeness (v1.13.0)
├── company-identifiers.json         Q — Company Identifiers (v1.16.0)
├── array-grouping-v1-17.json        R — Array Grouping (v1.17.0)
├── array-grouping-legal-entity-v1-17.json R — Array Grouping (v1.17.0)
├── evidence/                        I — PKI Evidence (v1.8.0)
├── tax/                             J — Tax Status (v1.9.0)
├── predictive/                      K — PredictiveAML (v1.7.0)
├── contact-banking/                 L — Contact/Banking (v1.10.0)
├── cell-company/                    M — Cell Companies (v1.11.0)
└── presentation-definitions/        O — Presentation Definitions
```

If the root flat files grow further, the recommended reorganisation is a dedicated PR that changes **only file paths** and updates every reference simultaneously (CI workflow glob patterns, README links, docs cross-references, validator tool defaults), with no content changes, so the diff is trivially reviewable.
