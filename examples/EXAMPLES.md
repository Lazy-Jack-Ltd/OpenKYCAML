# OpenKYCAML Examples Catalog

This directory contains curated example files demonstrating key features of the
[OpenKYCAML schema](../schema/kyc-aml-hybrid-extended.json). The examples are
intentionally limited to a small, representative set — they are not exhaustive.

## Examples

| File | Purpose |
|------|---------|
| [`minimal-travel-rule.json`](minimal-travel-rule.json) | Simplest valid payload satisfying FATF Travel Rule requirements. Shows the minimum originator/beneficiary and VASP fields needed for a compliant virtual-asset transfer message. |
| [`natural-person-plain.json`](natural-person-plain.json) | Individual (natural person) KYC profile with identification documents, contact details, PEP status, and record metadata. |
| [`legal-entity-plain.json`](legal-entity-plain.json) | Corporate (legal entity) KYC profile including beneficial owners, directors, risk assessment, and sanctions screening results. |
| [`full-kyc-profile.json`](full-kyc-profile.json) | Comprehensive profile combining a natural person, travel rule data, full risk assessment, and metadata — exercising most schema fields. |
| [`hybrid-vc-wrapped.json`](hybrid-vc-wrapped.json) | Demonstrates wrapping KYC data inside a W3C Verifiable Credential, showing the interoperability pattern for decentralized identity systems. |

## Validation

Every example can be validated against the schema using the tools in
[`tools/`](../tools/):

```bash
# Python
python tools/python/validate.py examples/minimal-travel-rule.json

# Node.js
node tools/javascript/validate.js examples/minimal-travel-rule.json
```

## Further Reading

- [Schema Reference](../docs/schema-reference.md)
- [Getting Started](../docs/getting-started.md)
- [Compliance Overview](../docs/compliance-overview.md)
