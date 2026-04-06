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

There are currently **25 example files** covering eight categories:

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

All files validate against [`schema/kyc-aml-hybrid-extended.json`](../schema/kyc-aml-hybrid-extended.json) (JSON Schema draft 2020-12), with the exception of `sd-jwt-compact-token.json` which is an annotated reference document — see [§6](#6-notes-on-special-files).

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
> `IVMS` = `ivms101` block present · `VC` = `verifiableCredential` block · `KYC` = `kycProfile` block · `Docs` = `identityDocuments` block · `GDPR` = `gdprSensitivityMetadata` block · `TxMon` = `transactionMonitoring` block

| File | Category | Subject | Ver | IVMS | VC | KYC | Docs | GDPR | TxMon | Scenario |
|---|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| [`minimal-travel-rule.json`](minimal-travel-rule.json) | A — Baseline | Natural person | 1.3.0 | ✓ | | | | | | Minimum-viable FATF Travel Rule payload: originator + beneficiary, no extras |
| [`minimal-travel-rule-eudi-wallet.json`](minimal-travel-rule-eudi-wallet.json) | A — Baseline | Natural person | 1.3.0 | ✓ | ✓ | | | | | Travel Rule with EUDI Wallet VC evidence; DID triangulation (JP→BTC→FR) |
| [`natural-person-plain.json`](natural-person-plain.json) | B — Natural Person | Natural person | 1.3.0 | ✓ | | | | | | Plain IVMS 101 natural person CDD — SDD-level KYC onboarding baseline |
| [`natural-person-eudi-wallet.json`](natural-person-eudi-wallet.json) | B — Natural Person | Natural person | 1.3.0 | ✓ | ✓ | | | | | EUDI Wallet onboarding (Anna Müller / DE); PID Issuer + VASP DID chain |
| [`natural-person-sd-jwt-eudi-wallet.json`](natural-person-sd-jwt-eudi-wallet.json) | B — Natural Person | Natural person | 1.3.0 | ✓ | ✓ | | | | | SD-JWT selective disclosure via EUDI Wallet; `_sd` digests for non-revealed claims |
| [`full-kyc-profile.json`](full-kyc-profile.json) | B — Natural Person | Natural person | 1.3.0 | ✓ | | ✓ | | | | Full KYC profile with EDD, PEP flag, source of wealth, and UBO list |
| [`full-kyc-profile-eudi-wallet.json`](full-kyc-profile-eudi-wallet.json) | B — Natural Person | Natural person | 1.3.0 | ✓ | ✓ | | | | | EDD / PEP KYC profile via EUDI Wallet (Fatima Al-Rashidi / AE); vLEI chain |
| [`legal-entity-plain.json`](legal-entity-plain.json) | C — Legal Entity | Legal entity | 1.3.0 | ✓ | | | | | | Plain IVMS 101 legal entity — minimal corporate CDD baseline |
| [`legal-entity-eudi-wallet.json`](legal-entity-eudi-wallet.json) | C — Legal Entity | Legal entity | 1.3.0 | ✓ | ✓ | | | | | EUDI Wallet LPID onboarding (Global Trade Solutions GmbH / DE) |
| [`legal-entity-sd-jwt-eudi-wallet.json`](legal-entity-sd-jwt-eudi-wallet.json) | C — Legal Entity | Legal entity | 1.3.0 | ✓ | ✓ | | | | | SD-JWT selective disclosure for LPID credential (Acme Digital Trading BV) |
| [`legal-entity-trust.json`](legal-entity-trust.json) | C — Legal Entity | Legal entity | 1.4.0 | ✓ | | ✓ | | | | ISO 20275 trust (ELF code `L295`); `trustDetails` sub-object; Cayman Islands discretionary trust |
| [`legal-entity-partnership.json`](legal-entity-partnership.json) | C — Legal Entity | Legal entity | 1.4.0 | ✓ | | ✓ | | | | ISO 20275 LLP (ELF code `Z13E`); `partnershipDetails` sub-object; Scottish LP |
| [`legal-entity-deep-ubo.json`](legal-entity-deep-ubo.json) | D — Complex Ownership | Legal entity | 1.3.0 | ✓ | ✓ | | | | | 4-tier corporate UBO chain — AMLR Art. 26 EDD beneficial ownership disclosure |
| [`complex-group-multi-tier.json`](complex-group-multi-tier.json) | D — Complex Ownership | Legal entity | 1.3.0 | ✓ | ✓ | | | | | 4-layer holding structure with natural person UBOs at every tier |
| [`foundation-complex-ubo.json`](foundation-complex-ubo.json) | D — Complex Ownership | Legal entity | 1.3.0 | ✓ | ✓ | | | | | Liechtenstein Privatstiftung; `foundationDetails`; settlor + protector + beneficiary roles |
| [`llp-complex-ubo.json`](llp-complex-ubo.json) | D — Complex Ownership | Legal entity | 1.3.0 | ✓ | ✓ | | | | | UK LLP with corporate general partner; multiple designated member roles |
| [`trust-complex-ubo.json`](trust-complex-ubo.json) | D — Complex Ownership | Legal entity | 1.3.0 | ✓ | ✓ | | | | | Jersey discretionary trust with corporate trustee and multiple beneficiary classes |
| [`hybrid-vc-wrapped.json`](hybrid-vc-wrapped.json) | E — VC-Wrapped | Natural person | 1.3.0 | ✓ | ✓ | | | | ✓ | IVMS 101 + `kycProfile` inside a W3C VC; transaction monitoring block |
| [`hybrid-vc-eudi-wallet.json`](hybrid-vc-eudi-wallet.json) | E — VC-Wrapped | Natural person | 1.3.0 | ✓ | ✓ | | | | ✓ | EUDI Wallet companion to `hybrid-vc-wrapped.json`; full DID triangulation |
| [`travel-rule-vc-wrapped.json`](travel-rule-vc-wrapped.json) | E — VC-Wrapped | Natural person | 1.3.0 | | ✓ | | | | ✓ | Travel Rule entirely inside a VC — no top-level `ivms101` (VC-only pattern) |
| [`travel-rule-vc-eudi-wallet.json`](travel-rule-vc-eudi-wallet.json) | E — VC-Wrapped | Natural person | 1.3.0 | ✓ | ✓ | | | | ✓ | EUDI Wallet companion to `travel-rule-vc-wrapped.json` |
| [`document-bundle-natural-person.json`](document-bundle-natural-person.json) | F — Document Bundles | Natural person | 1.5.0 | ✓ | | ✓ | ✓ | | | German national: Personalausweis + proof of address + eIDAS PID VC; `verifyingDocumentRef` linkage |
| [`document-bundle-legal-entity.json`](document-bundle-legal-entity.json) | F — Document Bundles | Legal entity | 1.5.0 | ✓ | | ✓ | ✓ | | | UK PLC: Certificate of Incorporation + Companies House extract + LEI + vLEI OOR |
| [`hybrid-with-sar-restriction.json`](hybrid-with-sar-restriction.json) | G — Advanced | Legal entity | 1.3.0 | ✓ | ✓ | | | ✓ | | SAR filing in progress; `gdprSensitivityMetadata` tipping-off protection; restricted field list |
| [`sd-jwt-compact-token.json`](sd-jwt-compact-token.json) | H — Reference Token | Natural person | 1.3.0 | | | ✓ | | | | ⚠ Annotated reference — decoded SD-JWT with `compactToken`, `decodedDisclosures`, `verificationSteps`; **not schema-valid** |

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

## 7. Future folder structure

The examples directory is intentionally kept **flat** at this stage.  Twenty-five files in a single directory is still easy to navigate, and a flat structure avoids updating every path reference in CI workflows, validators, and documentation in a disruptive reorganisation PR.

When the example count grows significantly (roughly 40+), the recommended subdirectory scheme is:

```
examples/
├── 01-baseline/          minimal-travel-rule*
├── 02-natural-person/    natural-person-*, full-kyc-profile*
├── 03-legal-entity/      legal-entity-*
├── 04-ownership/         *-deep-ubo, complex-group-*, foundation-*, llp-*, trust-complex-*
├── 05-vc-wrapped/        hybrid-vc-*, travel-rule-vc-*
├── 06-document-bundles/  document-bundle-*
├── 07-advanced/          hybrid-with-sar-restriction
└── 08-reference/         sd-jwt-compact-token
```

Any such reorganisation should be done in a dedicated PR that changes **only file paths** and updates every reference simultaneously (CI workflow glob patterns, README links, docs cross-references, validator tool defaults), with no content changes, so the diff is trivially reviewable.
