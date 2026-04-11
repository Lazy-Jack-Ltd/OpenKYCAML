# OpenKYCAML Python Validator

A simple command-line tool to validate JSON data files against the OpenKYCAML
schema.

## Requirements

- Python 3.8+
- [jsonschema](https://pypi.org/project/jsonschema/)

## Installation

```bash
pip install jsonschema
```

## Usage

```bash
python validate.py <data-file> [--schema <schema-file>]
```

### Examples

```bash
# Validate an example file
python validate.py ../../examples/minimal-travel-rule.json

# Use a custom schema path
python validate.py data.json --schema /path/to/schema.json
```

### Output

- `✅ Valid: <file>` — the file conforms to the schema.
- `❌ Validation failed: <file>` — the file has errors, with path and message.
