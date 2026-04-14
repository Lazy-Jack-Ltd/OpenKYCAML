# OpenKYCAML — File and Document Naming Convention

This document defines the file and directory naming convention for the entire OpenKYCAML repository.  
All contributors must follow these rules. See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full contributor guide.

---

## 1. General rule

**All file and directory names must use `lowercase-kebab-case`.**

- Words are separated by hyphens (`-`), not underscores or spaces.
- No uppercase letters anywhere in a filename (except conventional root-level files — see §7).
- No camelCase, PascalCase, or SCREAMING_SNAKE_CASE.

✅ Good: `natural-person-plain.json`, `travel-rule-implementation-guide.md`, `openvasp-converter.js`  
❌ Bad: `naturalPersonPlain.json`, `Travel_Rule_Guide.md`, `openvaspConverter.js`, `AMLR-requirements.md`

---

## 2. Docs (`docs/`)

Documentation files are organised into sub-folders by type so the purpose of a file is clear from its path alone.

| Sub-folder | Contains |
|---|---|
| `docs/guides/` | Step-by-step integration and implementation guides |
| `docs/mappings/` | Field-level mapping documents to other standards |
| `docs/compliance/` | Regulatory compliance documents and checklists |
| `docs/reference/` | API references, generated model docs, migration guides |
| `docs/diagrams/` | Mermaid diagram sources |
| `docs/versions/` | Historical roadmap and version notes |

**Naming pattern:** `<topic>.md` within the appropriate sub-folder.  
Example: `docs/guides/adoption-guide.md`, `docs/compliance/amlr-requirements.md`

---

## 3. Examples (`examples/`)

**Pattern:** `<subject-type>[-<variant>][-<format>].json`

| Segment | Meaning | Examples |
|---|---|---|
| `<subject-type>` | What the example describes | `natural-person`, `legal-entity`, `minimal-travel-rule` |
| `[-<variant>]` | Optional — specific scenario | `-plain`, `-deep-ubo`, `-partnership` |
| `[-<format>]` | Optional — encoding / wallet | `-eudi-wallet`, `-sd-jwt-eudi-wallet`, `-vc-wrapped` |

Examples: `natural-person-plain.json`, `legal-entity-eudi-wallet.json`, `travel-rule-vc-wrapped.json`

Structure diagram companion files (in `examples/structure-diagrams/`) follow the same stem with a `.md` extension:  
`examples/structure-diagrams/natural-person-plain.md`

---

## 4. Schema versions (`schema/versions/`)

**Pattern:** `v<major>.<minor>.<patch>.json` for stable releases, e.g. `v1.5.0.json`.

Pre-release / archive files in `schema/versions/archive/` use a hyphen before any qualifier:

| Pattern | Example |
|---|---|
| `v<major>.<minor>.<patch>-<qualifier>.json` | `v0.1.0-hybrid.json` |
| `v<major>.<minor>.<patch>-alpha.json` | `v0.1.0-alpha.json` |

---

## 5. Tools

Tool files follow the **idiomatic naming convention of their target language**, which takes precedence over the general kebab-case rule for source files:

| Language | Convention | Example |
|---|---|---|
| Python | `snake_case` | `converter.py`, `swift_mt_converter.py` |
| JavaScript / TypeScript | `kebab-case` | `validator.js`, `openvasp-converter.js` |
| Go | `snake_case` | `validator.go`, `validator_test.go` |

---

## 6. Versioned artefacts

Any file that encodes a version number must include the version suffix **before** the extension, separated by a hyphen:

**Pattern:** `<name>-v<semver>.<ext>`  
Example: `openkycaml-kyc-envelope-v1.0.0.json`

---

## 7. Conventional root-level files

The following uppercase filenames are a widely adopted open-source convention and are **exempt** from the lowercase-kebab-case rule:

`README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `GOVERNANCE.md`, `LICENSE`, `SECURITY.md`, `ROADMAP.md`, `CODE_OF_CONDUCT.md`, `NOTICE`

---

## 8. CI enforcement

A naming-lint check runs in CI (`.github/workflows/validate-schema.yml`) on every push and pull request.  
It rejects any new file that violates rules §1–§6 above.

If you need an exemption (e.g., a third-party generated file), add the path to the `.namingignore` file at the repository root.
