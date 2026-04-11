# OpenKYCAML JavaScript Validator

A simple command-line tool to validate JSON data files against the OpenKYCAML
schema using [Ajv](https://ajv.js.org/).

## Requirements

- Node.js 16+
- [ajv](https://www.npmjs.com/package/ajv)
- [ajv-formats](https://www.npmjs.com/package/ajv-formats) (recommended)

## Installation

```bash
npm install ajv ajv-formats
```

## Usage

```bash
node validate.js <data-file> [--schema <schema-file>]
```

### Examples

```bash
# Validate an example file
node validate.js ../../examples/minimal-travel-rule.json

# Use a custom schema path
node validate.js data.json --schema /path/to/schema.json
```

### Output

- `✅ Valid: <file>` — the file conforms to the schema.
- `❌ Validation failed: <file>` — the file has errors, with path and message.
