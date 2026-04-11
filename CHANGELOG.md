# Changelog

All notable changes to the OpenKYCAML schema and public repository will be
documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2025-04-10

### Added

- Initial public release of the OpenKYCAML Hybrid Extended Schema (`v1.0.0`).
- Natural person identity section with name, DOB, nationality, address,
  identification documents, PEP status, and source of funds/wealth.
- Legal entity identity section with legal name, LEI, entity type,
  beneficial owners, directors, and registered address.
- FATF Travel Rule section aligned with IVMS 101 — originator, beneficiary,
  VASP identification, and transaction data.
- W3C Verifiable Credential wrapper for decentralized identity
  interoperability.
- Risk assessment section with risk levels, sanctions screening, PEP
  screening, and adverse media checks.
- Record-keeping metadata section.
- Five curated example files demonstrating key schema features.
- Python and JavaScript validation tools.
- Public documentation: getting started guide, schema reference, compliance
  overview, IVMS 101 mapping, and eIDAS basics mapping.
- CI workflow for automated example validation.
