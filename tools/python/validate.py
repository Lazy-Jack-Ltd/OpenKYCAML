#!/usr/bin/env python3
"""
OpenKYCAML Schema Validator

Validates a JSON data file against the OpenKYCAML Hybrid Extended Schema.

Usage:
    python validate.py <data-file> [--schema <schema-file>]

Examples:
    python validate.py ../../examples/minimal-travel-rule.json
    python validate.py data.json --schema ../../schema/kyc-aml-hybrid-extended.json
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from jsonschema import validate, ValidationError, SchemaError
except ImportError:
    print("Error: jsonschema package is required. Install it with:")
    print("  pip install jsonschema")
    sys.exit(1)

DEFAULT_SCHEMA = Path(__file__).resolve().parent.parent.parent / "schema" / "kyc-aml-hybrid-extended.json"


def load_json(filepath: str) -> dict:
    """Load and parse a JSON file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a JSON file against the OpenKYCAML schema.")
    parser.add_argument("data_file", help="Path to the JSON data file to validate.")
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA),
        help=f"Path to the JSON Schema file (default: {DEFAULT_SCHEMA}).",
    )
    args = parser.parse_args()

    schema = load_json(args.schema)
    data = load_json(args.data_file)

    try:
        validate(instance=data, schema=schema)
        print(f"✅ Valid: {args.data_file}")
    except SchemaError as e:
        print(f"❌ Schema error: {e.message}")
        sys.exit(1)
    except ValidationError as e:
        print(f"❌ Validation failed: {args.data_file}")
        print(f"   Path: {' → '.join(str(p) for p in e.absolute_path)}")
        print(f"   Error: {e.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
