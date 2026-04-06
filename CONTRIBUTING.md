# Contributing to OpenKYCAML

Thank you for your interest in contributing to **OpenKYCAML** — the neutral, open hybrid KYC/AML data standard.

Contributions from fintech engineers, compliance professionals, identity architects, and open-source developers are all welcome.

---

## Table of Contents

1. [Types of Contribution](#1-types-of-contribution)
2. [Before You Start](#2-before-you-start)
3. [Development Setup](#3-development-setup)
4. [Submitting Changes](#4-submitting-changes)
5. [Schema Change Process](#5-schema-change-process)
6. [Coding Standards](#6-coding-standards)
7. [Issue and PR Labels](#7-issue-and-pr-labels)

---

## 1. Types of Contribution

| Type | How to Contribute |
|---|---|
| **Bug fix** in schema or tools | Open an issue → fork → PR |
| **New field / section in schema** | Open an RFC issue first (see §5) |
| **New example payload** | Fork → add to `examples/` → PR |
| **Tool improvement** (Python/JS) | Fork → improve → tests → PR |
| **Documentation fix** | Fork → edit `docs/` → PR |
| **New language tool** (e.g., Go, Java) | Open an issue to discuss first |
| **Compliance mapping update** | Fork → edit `docs/compliance-matrix.md` → PR with citations |

---

## 2. Before You Start

- Read the [Code of Conduct](CODE_OF_CONDUCT.md). All contributors are expected to follow it.
- Read the [Governance](GOVERNANCE.md) document to understand how decisions are made.
- Check [open issues](https://github.com/Lazy-Jack-Ltd/openKYCAML/issues) and [discussions](https://github.com/Lazy-Jack-Ltd/openKYCAML/discussions) to avoid duplicate effort.
- For significant changes (new schema sections, breaking changes), open a discussion or RFC issue **before** writing code.

---

## 3. Development Setup

### Python tools

```bash
# Create a virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r tools/python/requirements.txt

# Validate all examples
python tools/python/validator.py examples/full-kyc-profile.json
```

#### Running the Python test suite

```bash
# From the repo root (uses pyproject.toml testpaths config):
pip install pytest
pytest tools/python/tests/ -v

# Or run individual test files:
pytest tools/python/tests/test_validator.py -v
pytest tools/python/tests/test_converter.py -v
```

### JavaScript tools

```bash
cd tools/javascript
npm install

# Validate all examples
node validator.js ../../examples/full-kyc-profile.json

# Run the test suite
npm test
```

### Go tools

```bash
cd tools/go
go build ./...   # build the validator binary
go test ./... -v # run all Go tests
go run . --help  # show CLI usage
```

### Schema validation

The CI pipeline (`.github/workflows/validate-schema.yml`) validates all examples on every push. You can run it locally using the Python or Node.js validators above.

---

## 4. Submitting Changes

1. **Fork** the repository and create a branch from `main`:
   ```bash
   git checkout -b fix/my-fix
   # or
   git checkout -b feat/my-feature
   ```

2. **Make your changes.** Ensure all example payloads still validate:
   ```bash
   python tools/python/validator.py examples/natural-person-plain.json
   python tools/python/validator.py examples/legal-entity-plain.json
   # ... etc.
   ```

3. **Update documentation** in `docs/` if your change affects the schema or behaviour.

4. **Commit** with a clear, descriptive message following [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   fix(schema): correct pattern for nationalIdentifier LEIX type
   feat(examples): add minimal-travel-rule.json example
   docs(compliance-matrix): add AMLR Art. 29 EDD mapping
   ```

5. **Open a Pull Request** against `main` with:
   - A clear title and description.
   - Reference to the issue being fixed (e.g., `Closes #42`).
   - Confirmation that all CI checks pass.

---

## 5. Schema Change Process

The OpenKYCAML schema uses **semantic versioning**. The change process depends on impact:

### Non-breaking changes (PATCH / MINOR)

These can be proposed directly via a PR:

- Adding new **optional** fields to existing objects.
- Adding new **optional** sections.
- Clarifying descriptions or adding examples.
- Adding new enum values to non-required fields.

### Breaking changes (MAJOR)

Breaking changes require a formal **Request for Comments (RFC)**:

1. Open a GitHub issue with the title `[RFC] <description>` and label `type: rfc`.
2. Describe the problem, proposed change, and migration path.
3. Allow a **14-day** comment period.
4. Requires **consensus** from the Technical Working Group (see [GOVERNANCE.md](GOVERNANCE.md)).
5. Only after approval: implement and open a PR.

Breaking changes include:
- Removing or renaming existing fields.
- Changing a field from optional to required.
- Changing a field's type or format.
- Removing enum values from existing required fields.

---

## 6. Coding Standards

### JSON Schema

- Use descriptive `"description"` strings on every field and `$def`.
- Keep field names in `camelCase`.
- Use `"format": "date-time"` for timestamps, `"format": "date"` for dates, `"format": "uri"` for URIs, `"format": "uuid"` for UUIDs.
- Always include `"maxLength"` on string fields.
- Reference `$defs` rather than inline complex objects.

### Python

- Target Python 3.10+.
- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Use type hints (`from __future__ import annotations`).
- Write docstrings in NumPy or Google style.

### JavaScript

- Target Node.js 18+.
- Use `'use strict'`.
- JSDoc for all public functions and classes.
- No TypeScript required, but TypeScript-compatible JSDoc types are welcomed.

---

## 7. Issue and PR Labels

| Label | Meaning |
|---|---|
| `type: bug` | Something is broken |
| `type: enhancement` | New feature or improvement |
| `type: rfc` | Request for Comments — schema change proposal |
| `type: docs` | Documentation only |
| `type: question` | Question or discussion |
| `area: schema` | Affects the JSON Schema |
| `area: examples` | Affects example payloads |
| `area: tools` | Affects Python/JS tools |
| `area: ci` | Affects CI/CD workflows |
| `status: needs-review` | Awaiting Technical Working Group review |
| `status: approved` | Approved for merge |

---

## 8. Publishing

### PyPI — `openkycaml` Python package

Publishing is automated via the GitHub Actions release workflow (`.github/workflows/release.yml`).

Manual publishing for maintainers:

```bash
# Install build tools
pip install build twine

# Build the distribution
python -m build

# Upload to PyPI (requires PYPI_TOKEN secret or ~/.pypirc)
twine upload dist/*
```

Entry points provided by `pyproject.toml`:
- `openkycaml-validate` — JSON Schema validator CLI
- `openkycaml-convert` — Format converter CLI (IVMS 101, PID/LPID, ISO 20022)

### npm — `@openkycaml/tools` Node.js package

Publishing is automated on version tag push (`v*.*.*`) via `.github/workflows/release.yml`.

Manual publishing for maintainers:

```bash
cd tools/javascript

# Ensure tests pass before publishing
npm test

# Publish to npm registry (requires NPM_TOKEN secret or npm login)
npm publish --access public
```

The `prepublishOnly` script in `package.json` automatically runs `npm test` before every `npm publish` to prevent publishing broken builds.

---

We look forward to your contributions!
