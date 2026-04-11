# Getting Started with OpenKYCAML

Welcome to **OpenKYCAML** — an Open Schema Standard for KYC/AML data
interchange across financial services, virtual asset service providers (VASPs),
and identity verification platforms.

## Quick Overview

OpenKYCAML provides a single, extensible JSON Schema that covers:

- **Natural Person** identity (individuals)
- **Legal Entity** identity (companies, trusts, etc.)
- **FATF Travel Rule** data (IVMS 101 aligned)
- **Verifiable Credential** wrappers (W3C VC compatible)
- **Risk Assessment** outputs (sanctions, PEP, adverse media)

## 1. Get the Schema

The canonical schema lives at:

```
schema/kyc-aml-hybrid-extended.json
```

You can reference it directly in your application or download it from the
repository.

## 2. Explore the Examples

The [`examples/`](../examples/) directory contains curated sample payloads:

| Example | What It Shows |
|---------|---------------|
| `minimal-travel-rule.json` | Minimum viable Travel Rule message |
| `natural-person-plain.json` | Individual KYC profile |
| `legal-entity-plain.json` | Corporate KYC profile |
| `full-kyc-profile.json` | Comprehensive multi-section profile |
| `hybrid-vc-wrapped.json` | VC-wrapped KYC credential |

See [`examples/EXAMPLES.md`](../examples/EXAMPLES.md) for detailed
descriptions.

## 3. Validate Your Data

### Python

```bash
pip install jsonschema
python tools/python/validate.py path/to/your-data.json
```

### JavaScript / Node.js

```bash
npm install ajv
node tools/javascript/validate.js path/to/your-data.json
```

Both validators load the schema automatically and report any errors.

## 4. Integrate into Your System

Typical integration patterns:

1. **API payload validation** — validate incoming/outgoing KYC/AML JSON
   against the schema at your API boundary.
2. **Data pipeline checks** — add schema validation as a step in ETL or
   compliance pipelines.
3. **Verifiable Credential issuance** — use the VC wrapper section when
   issuing KYC credentials in decentralized identity workflows.

## 5. Next Steps

- Read the [Schema Reference](schema-reference.md) for field-by-field
  documentation.
- Review the [Compliance Overview](compliance-overview.md) for regulatory
  context.
- Check the [mappings](mappings/) directory for IVMS 101 and eIDAS alignment
  guides.

## Questions?

Open an issue on the [GitHub repository](https://github.com/Lazy-Jack-Ltd/OpenKYCAML)
or see [CONTRIBUTING.md](../CONTRIBUTING.md) for how to get involved.
