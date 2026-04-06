# Security Policy

## Scope

This repository contains:
- The **OpenKYCAML JSON Schema** — a data format standard. It does not execute code and has no runtime attack surface of its own.
- **Reference tooling** — Python, JavaScript/Node.js, and (planned) Go validator and converter tools that process JSON payloads.
- **Documentation and examples** — Markdown files and JSON reference payloads.

Security vulnerabilities in the **tooling** (e.g., unsafe JSON parsing, prototype pollution in validators, dependency vulnerabilities) are in scope. Schema design issues that could cause adopters to build insecure systems (e.g., missing required fields for PII protection) are also in scope.

The **domain** (`openkycaml.org`) and hosting infrastructure are managed separately and are out of scope for this repository's security policy.

---

## Supported Versions

| Version | Supported |
|---|---|
| v1.3.x (current) | ✅ Security fixes accepted |
| v1.2.x | 🟡 Critical fixes only |
| v1.1.x and earlier | ❌ No longer supported |

---

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Use GitHub's built-in **Private Security Advisory** feature:

1. Go to the [Security tab](https://github.com/Lazy-Jack-Ltd/openKYCAML/security) of this repository.
2. Click **"Report a vulnerability"**.
3. Provide a description of the issue, affected versions, steps to reproduce, and (if known) a suggested fix.

We aim to acknowledge all reports within **5 business days** and to provide a resolution timeline within **14 calendar days** for critical issues.

---

## Severity Classification

| Severity | Description | Example |
|---|---|---|
| **Critical** | Remote code execution or data exfiltration in reference tooling | Unsafe `eval()` in validator; dependency with known RCE |
| **High** | Schema design flaw enabling PII bypass or tipping-off violation | Missing required SAR-flag field allowing inadvertent disclosure |
| **Medium** | Dependency vulnerability with limited real-world exploitability | Prototype pollution in a dev-only dependency |
| **Low** | Information disclosure in documentation or example payloads | Realistic-looking personal data in examples |

---

## Nature of This Standard

OpenKYCAML is a **data format specification**. The schema itself does not execute code. Vulnerabilities in implementations that use this schema are the responsibility of those implementations. However, if a schema design issue is identified that would systematically lead adopters to build insecure systems, we treat that as a security issue in scope for this policy.

---

## Disclosure Policy

We follow **coordinated disclosure**. Once a fix is ready:
- A GitHub Security Advisory will be published.
- Release notes will describe the issue and fix at an appropriate level of detail.
- Credit will be given to the reporter unless they request anonymity.

---

*This policy was introduced in v1.4.0 (April 2026).*
