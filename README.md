# OpenKYCAML — Open Schema Standard for KYC/AML Data Interchange

[![Validate Examples](https://github.com/Lazy-Jack-Ltd/OpenKYCAML/actions/workflows/validate-examples.yml/badge.svg)](https://github.com/Lazy-Jack-Ltd/OpenKYCAML/actions/workflows/validate-examples.yml)

**OpenKYCAML** is an open, extensible JSON Schema standard for representing
Know Your Customer (KYC) and Anti-Money Laundering (AML) data. It is designed
for financial institutions, virtual asset service providers (VASPs), identity
verification platforms, and compliance technology providers who need a common
data format for customer identity, risk assessment, and regulatory reporting.

> **Note:** This public repository is curated and auto-generated from selected
> folders in the private source-of-truth repository. It contains only the
> published schema, curated examples, public documentation, and validation
> tools.

---

## What's Inside

```
OpenKYCAML/
├── schema/          → The canonical JSON Schema (source of truth)
├── examples/        → Curated example payloads (5 files)
├── docs/            → Public documentation and mapping guides
├── tools/           → Validation tools (Python & JavaScript)
├── .github/         → CI workflows for automated validation
├── README.md        → This file
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── GOVERNANCE.md
├── ROADMAP.md
├── CODE_OF_CONDUCT.md
└── SECURITY.md
```

## Key Features

- **Unified schema** covering natural persons, legal entities, travel rule
  data, verifiable credentials, and risk assessments
- **IVMS 101 aligned** for FATF Travel Rule compliance
- **W3C Verifiable Credential** wrapper for decentralized identity
  interoperability
- **Risk assessment** section for sanctions, PEP, and adverse media screening
- **Extensible** — add custom fields without breaking core validation

## Quick Start

### 1. Get the Schema

```bash
# Clone the repository
git clone https://github.com/Lazy-Jack-Ltd/OpenKYCAML.git
cd OpenKYCAML

# The schema is at:
# schema/kyc-aml-hybrid-extended.json
```

### 2. Validate Data

**Python:**

```bash
pip install jsonschema
python tools/python/validate.py examples/minimal-travel-rule.json
```

**JavaScript / Node.js:**

```bash
npm install ajv ajv-formats
node tools/javascript/validate.js examples/minimal-travel-rule.json
```

### 3. Explore the Examples

See [`examples/EXAMPLES.md`](examples/EXAMPLES.md) for a catalog of curated
examples showing different schema features:

| Example | Demonstrates |
|---------|-------------|
| `minimal-travel-rule.json` | Minimum viable Travel Rule message |
| `natural-person-plain.json` | Individual KYC profile |
| `legal-entity-plain.json` | Corporate KYC profile |
| `full-kyc-profile.json` | Comprehensive multi-section profile |
| `hybrid-vc-wrapped.json` | VC-wrapped KYC credential |

## Documentation

- [Getting Started](docs/getting-started.md)
- [Schema Reference](docs/schema-reference.md)
- [Compliance Overview](docs/compliance-overview.md)
- [IVMS 101 Mapping](docs/mappings/ivms101-mapping.md)
- [eIDAS Basics](docs/mappings/eidas-basics.md)

## About This Repository

This public repository is the **curated distribution** of the OpenKYCAML
standard. It is automatically synchronized from the private development
repository, which serves as the internal source of truth. Only the following
content is published here:

- The full public schema
- A curated set of example files
- Public-facing documentation
- Validation tools

Internal drafts, experimental features, and private documentation are
maintained separately and are not included in this repository.

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md)
for guidelines on submitting issues, suggesting improvements, and opening
pull requests.

## Governance

See [GOVERNANCE.md](GOVERNANCE.md) for information about the project's
governance model and decision-making process.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the project's public roadmap and planned
features.

## Security

To report a security vulnerability, please see [SECURITY.md](SECURITY.md).

## License

This project is licensed under the terms described in [LICENSE](LICENSE).

---

**OpenKYCAML** — Making KYC/AML data interoperable, verifiable, and open.
