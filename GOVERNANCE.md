# Governance

## Overview

OpenKYCAML is maintained by [Lazy Jack Ltd](https://github.com/Lazy-Jack-Ltd)
with input from the open-source community. This document describes how
decisions are made and how the project is governed.

## Roles

### Maintainers

Maintainers are responsible for:

- Reviewing and merging pull requests
- Managing releases and schema versioning
- Ensuring the schema remains consistent with relevant regulatory standards
- Moderating discussions and enforcing the Code of Conduct

Current maintainers are listed in the repository's team settings.

### Contributors

Anyone who submits issues, pull requests, documentation improvements, or
participates in discussions is a valued contributor.

## Decision-Making

- **Schema changes** are discussed in GitHub Issues before implementation.
  Breaking changes require a new major version and a clear migration path.
- **Documentation and tooling** changes follow the standard pull request
  review process.
- **Governance changes** are proposed via issues and require maintainer
  consensus.

## Versioning

The schema follows [Semantic Versioning](https://semver.org/):

- **Major** — breaking changes to required fields or structure
- **Minor** — new optional fields or sections
- **Patch** — documentation, examples, or non-breaking fixes

## Regulatory Alignment

Schema changes that affect compliance-relevant sections (Travel Rule, risk
assessment, PEP/sanctions) are reviewed against the latest FATF guidance,
IVMS 101, and applicable EU/US regulations before merging.

## Contact

For governance questions, open an issue or contact the maintainers through
the repository.
