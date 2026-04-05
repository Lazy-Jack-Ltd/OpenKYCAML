# OpenKYCAML Governance

This document describes the governance model for the **OpenKYCAML** open standard.

---

## 1. Principles

OpenKYCAML is governed by the following principles:

- **Openness** — all technical decisions are made publicly in the GitHub repository.
- **Neutrality** — no single vendor, institution, or jurisdiction controls the standard.
- **Consensus** — changes require broad agreement from stakeholders.
- **Compliance-first** — every change is evaluated against regulatory requirements (FATF, AMLR, eIDAS 2.0).
- **Backward compatibility** — breaking changes are exceptional and require a major version bump.

---

## 2. Roles

### Maintainers

Maintainers are individuals with merge rights to the `main` branch. They are responsible for:

- Reviewing and merging pull requests.
- Triaging issues.
- Enforcing the Code of Conduct.
- Publishing new schema versions.

Current maintainers are listed in the [CODEOWNERS](.github/CODEOWNERS) file (when present).

### Technical Working Group (TWG)

The TWG is the decision-making body for schema changes. It consists of:

- Appointed representatives from adopting institutions (VASPs, banks, KYC utilities).
- Subject-matter experts in IVMS 101, eIDAS 2.0, AMLR, and FATF standards.
- At least one representative from an open-source fintech project.

TWG membership is open. To join, open an issue with the label `governance: twg-membership`.

### Contributors

Anyone who has submitted a merged pull request is a Contributor. Contributors are listed in the GitHub Contributors graph.

### Adopters

Organisations that have publicly declared adoption of OpenKYCAML. To register as an adopter, open an issue with the label `governance: adopter`.

---

## 3. Decision Making

### Routine changes (PATCH / MINOR)

Changes that add optional fields, improve documentation, or fix bugs are reviewed by **any two Maintainers** and merged without a formal TWG vote, provided:

- CI passes.
- No Maintainer has raised an objection within 5 business days.

### Significant changes (non-breaking MINOR)

Changes that add new optional sections or significantly alter tool behaviour require:

- A pull request with a clear description.
- Review and approval from **at least two Maintainers**.
- A 5-business-day comment period on the PR.
- No blocking objections from TWG members.

### Breaking changes (MAJOR)

Breaking changes to the schema require:

1. A [Request for Comments (RFC)](CONTRIBUTING.md#5-schema-change-process) issue.
2. A **14-day** public comment period.
3. A formal TWG vote: **simple majority** of active TWG members.
4. A 30-day migration notice before the new major version is tagged.

---

## 4. Versioning and Releases

OpenKYCAML follows [Semantic Versioning 2.0.0](https://semver.org/):

| Change | Version Bump | Example |
|---|---|---|
| Backward-compatible bug fix | PATCH | `1.0.0` → `1.0.1` |
| New optional field or section | MINOR | `1.0.0` → `1.1.0` |
| Breaking change (field removed/required/renamed) | MAJOR | `1.0.0` → `2.0.0` |

### Release process

1. Tag the release on `main` with `git tag v<version>`.
2. Copy the canonical schema to `schema/versions/v<version>.json`.
3. Update `ROADMAP.md` with the changelog entry.
4. Publish a GitHub Release with release notes.

---

## 5. Conflict Resolution

If a consensus cannot be reached through discussion:

1. Any TWG member may request a formal vote.
2. A vote is conducted via GitHub issue comments (👍 / 👎 / 🤷) over 7 days.
3. Simple majority of active TWG members decides (abstentions do not count).
4. In case of a tie, the Maintainer with the most commits in the last 6 months casts the deciding vote.

---

## 6. Amending This Document

Amendments to this Governance document require:

- An RFC issue with the label `governance: amendment`.
- A 14-day comment period.
- A TWG vote with a **two-thirds majority**.

---

*This governance model is inspired by the [IVMS 101 Working Group](https://intervasp.org/) and the [OpenSSF](https://openssf.org/) governance framework.*
