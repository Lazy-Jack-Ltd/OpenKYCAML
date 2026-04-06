# OpenKYCAML × ISO 20022 Integration

> **This module enables any adopter of OpenKYCAML to embed the full hybrid KYC/AML dataset into ISO 20022 payment and reporting messages using the official SupplementaryData extension. It completes the bridge between IVMS 101 / eIDAS 2.0 and global financial market infrastructures (SWIFT CBPR+, TARGET2, FedNow, etc.).**

Adopters can send enriched OpenKYCAML data inside standard `pacs.008` / `pain.001` messages without custom adapters.

---

## Module Version

| Module | OpenKYCAML Core | Status |
|---|---|---|
| `iso20022-integration` v1.0.0 | v1.3.0 | Available |

---

## Supported Message Types

| ISO 20022 Message | Name | Use Case |
|---|---|---|
| `pacs.008` | FIToFICstmrCdtTrf | Travel Rule — CBPR+ / SWIFT interbank credit transfer carrying originator + beneficiary KYC data |
| `pain.001` | CstmrCdtTrfInitn | Customer Credit Transfer Initiation — third-party CDD reliance, corporate onboarding |
| `camt.053` | BkToCstmrStmt | Bank-to-Customer Statement — KYC audit trail and data-retention evidence |

---

## How It Works: The `<SplmtryData>` Mechanism

ISO 20022 provides a standards-approved extension point — the `<SplmtryData>` element — that appears in all major message types. Any data that cannot be expressed in the native ISO 20022 data dictionary can be carried here as a freeform envelope.

OpenKYCAML uses this mechanism to embed the full KYC/AML payload (risk scores, screening results, VC proofs, consent records, GDPR metadata) without modifying the ISO 20022 schema or breaking any existing parser.

```xml
<SplmtryData>
  <PlcAndNm>OpenKYCAML/KYCAMLEnvelope/1.0</PlcAndNm>
  <Envlp>
    <!-- JSON-encoded KYCAMLEnvelope (base64 or inline CDATA) -->
  </Envlp>
</SplmtryData>
```

The `<PlcAndNm>` value `OpenKYCAML/KYCAMLEnvelope/1.0` is the registered namespace discriminator used by all conforming implementations to identify the OpenKYCAML envelope.

---

## Folder Guide

```
iso20022-integration/
├── README.md                             ← this file
├── mapping/
│   ├── openkycaml-to-iso20022-mapping.yaml      ← field-by-field mapping (OpenKYCAML → ISO 20022)
│   ├── iso20022-to-openkycaml-mapping.yaml      ← reverse mapping (ISO 20022 → OpenKYCAML)
│   └── field-level-gap-analysis.md              ← narrative gap analysis and transformation rules
├── supplementary-data/
│   ├── kyc-aml-envelope-schema.json             ← JSON Schema for the KYCAMLEnvelope object
│   └── openkycaml-kyc-envelope-v1.0.0.json     ← reference instance (canonical example payload)
├── profiles/
│   ├── travel-rule-pacs.008-profile.json        ← CBPR+ Travel Rule profile
│   ├── pain.001-kyc-envelope-profile.json       ← Third-party CDD reliance profile
│   └── camt.053-kyc-audit-profile.json          ← Audit trail / data-retention profile
├── examples/
│   ├── pacs.008-with-openkycaml-supplementarydata.xml  ← Full pacs.008 with embedded KYC envelope
│   ├── pain.001-with-kyc-envelope.xml                  ← Full pain.001 with CDD reliance envelope
│   └── minimal-travel-rule-pacs008-snippet.xml         ← Minimal <SplmtryData> copy-paste snippet
├── libraries/
│   ├── python/
│   │   ├── converter.py        ← openkycaml_to_pacs008(), openkycaml_to_pain001(), iso20022_to_openkycaml()
│   │   └── requirements.txt
│   └── typescript/
│       ├── converter.ts        ← equivalent TypeScript module (ESM)
│       └── package.json
└── test-suite/
    └── validation-tests/
        ├── test_pacs008.py     ← pytest round-trip tests for pacs.008
        └── test_pain001.py     ← pytest round-trip tests for pain.001
```

---

## Quick Start

### Python — convert an OpenKYCAML payload to a pacs.008 XML message

```python
import json
import sys

# Add the library to your path
sys.path.insert(0, "iso20022-integration/libraries/python")
from converter import openkycaml_to_pacs008

with open("examples/minimal-travel-rule.json") as f:
    payload = json.load(f)

xml_output = openkycaml_to_pacs008(payload)
print(xml_output)
```

### Python — parse a pacs.008 back to OpenKYCAML

```python
from converter import iso20022_to_openkycaml

with open("iso20022-integration/examples/pacs.008-with-openkycaml-supplementarydata.xml") as f:
    xml_string = f.read()

kyc_payload = iso20022_to_openkycaml(xml_string)
print(kyc_payload["ivms101"]["originator"])
```

### TypeScript — convert to pain.001

```typescript
import { openkycamlToPain001 } from "./iso20022-integration/libraries/typescript/converter.js";
import { readFileSync } from "fs";

const payload = JSON.parse(readFileSync("examples/minimal-travel-rule.json", "utf8"));
const xml = await openkycamlToPain001(payload);
console.log(xml);
```

---

## Standards References

- **ISO 20022** — Financial Services — Universal financial industry message scheme. International Organization for Standardization. [iso20022.org](https://www.iso20022.org/)
- **SWIFT CBPR+** — Cross-Border Payments and Reporting Plus programme. The SWIFT MT→MX migration completed in November 2025; CBPR+ is now mandatory for cross-border payment messages on the SWIFT network.
- **FATF Recommendation 16** — Wire Transfers / Travel Rule. [fatf-gafi.org](https://www.fatf-gafi.org/en/recommendations/fatfrecommendations.html)
- **MiCA Article 83 / TFR 2023/1113 Art. 14** — Transfer of crypto-assets (Travel Rule for VASPs). The operative instrument for the EU crypto-asset Travel Rule is **EU Funds Transfer Regulation (TFR) 2023/1113 Art. 14**; MiCA Art. 83 cross-references the TFR but TFR is the primary legal basis for VASP transfer-of-funds data requirements.
- **IVMS 101 v1.0** — InterVASP Messaging Standard. [intervasp.org](https://intervasp.org/)
- **OpenKYCAML core schema** — [`schema/kyc-aml-hybrid-extended.json`](../schema/kyc-aml-hybrid-extended.json)

---

## Relationship to Core Schema

This folder is a **non-breaking add-on**. The core OpenKYCAML JSON Schema (`schema/kyc-aml-hybrid-extended.json`) is unchanged. All ISO 20022 integration artefacts are isolated here and reference the core schema by URI.

```
schema/kyc-aml-hybrid-extended.json      ← UNCHANGED — core data model
iso20022-integration/                    ← NEW — ISO 20022 bridge layer
```

---

*Part of [OpenKYCAML](https://github.com/Lazy-Jack-Ltd/OpenKYCAML) — the neutral, open hybrid KYC/AML data standard.*
