# schema/versions/archive/

This directory contains **pre-release draft schemas** from before the OpenKYCAML v1.0.0 stable release. They are preserved for historical reference only and are **not part of the stable schema series**.

| File | Description |
|---|---|
| `v0.1.0-hybrid.json` | Earliest hybrid IVMS 101 + VC draft schema |
| `v0.1.0-alpha.json` | Iterative alpha draft of the hybrid schema |
| `v0.1.1-hybrid.json` | Pre-release hybrid schema, patch iteration |

## Notes

- These files use JSON Schema drafts that predate the project's adoption of JSON Schema draft 2020-12.
- Field names and structure differ significantly from v1.x — do not use these for production integrations.
- For the current schema, see [`../v1.6.0.json`](../v1.6.0.json) or the canonical [`../../kyc-aml-hybrid-extended.json`](../../kyc-aml-hybrid-extended.json).
- These files were originally committed with uppercase `.JSON` extensions and dot-delimited qualifiers; they have been normalised to lowercase kebab-case (`v0.1.0-hybrid.json`, `v0.1.0-alpha.json`, `v0.1.1-hybrid.json`) for consistency with the repository naming convention.
