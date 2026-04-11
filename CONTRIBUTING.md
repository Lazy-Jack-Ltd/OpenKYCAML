# Contributing to OpenKYCAML

Thank you for your interest in contributing to the OpenKYCAML Open Schema
Standard! We welcome contributions from the community.

## How to Contribute

### Reporting Issues

- Use [GitHub Issues](https://github.com/Lazy-Jack-Ltd/OpenKYCAML/issues) to
  report bugs, suggest features, or ask questions.
- Search existing issues before opening a new one.
- Provide as much context as possible: schema version, example data,
  validation error messages, etc.

### Suggesting Schema Changes

1. Open an issue describing the proposed change and the regulatory or
   technical rationale.
2. Reference relevant standards (FATF, IVMS 101, eIDAS, W3C VC, etc.)
   where applicable.
3. The maintainers will review and discuss before any schema modification.

### Submitting Pull Requests

1. Fork the repository.
2. Create a feature branch from `main`.
3. Make your changes — keep them focused and well-documented.
4. Ensure all examples validate against the schema:
   ```bash
   python tools/python/validate.py examples/<your-file>.json
   ```
5. Open a pull request with a clear description of what and why.

### Code Style

- JSON files: 2-space indentation, no trailing commas.
- Markdown: wrap lines at ~80 characters where practical.
- Python: follow PEP 8.
- JavaScript: use `"use strict"` and semicolons.

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add support for tax identification numbers
fix: correct LEI pattern to allow lowercase
docs: update IVMS 101 mapping for beneficiary fields
```

## Code of Conduct

All contributors are expected to follow our
[Code of Conduct](CODE_OF_CONDUCT.md).

## Questions?

Open an issue or start a discussion on the repository. We're happy to help!
