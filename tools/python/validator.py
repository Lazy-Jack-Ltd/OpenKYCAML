#!/usr/bin/env python3
"""
OpenKYCAML Schema Validator
===========================
Validates JSON payloads against the OpenKYCAML schema (v1.0.0).

Usage:
    python validator.py <path-to-payload.json>
    python validator.py --stdin < payload.json
    python validator.py --help

Programmatic usage:
    from validator import OpenKYCAMLValidator, ValidationResult

    v = OpenKYCAMLValidator()
    result = v.validate(payload_dict)
    if result.is_valid:
        print("Valid!")
    else:
        for error in result.errors:
            print(f"  [{error.path}] {error.message}")
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator, ValidationError
from jsonschema.exceptions import SchemaError

# Resolve schema relative to this file so the validator works from any CWD.
_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schema" / "kyc-aml-hybrid-extended.json"


@dataclass
class FieldError:
    """A single field-level validation error."""

    path: str
    message: str
    schema_path: str = ""

    def __str__(self) -> str:
        return f"[{self.path or '<root>'}] {self.message}"


@dataclass
class ValidationResult:
    """The result of validating a single OpenKYCAML payload."""

    is_valid: bool
    errors: list[FieldError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    payload_version: str | None = None

    def __str__(self) -> str:
        if self.is_valid:
            return f"VALID (OpenKYCAML v{self.payload_version or 'unknown'})"
        lines = [f"INVALID — {len(self.errors)} error(s):"]
        for err in self.errors:
            lines.append(f"  {err}")
        return "\n".join(lines)


class OpenKYCAMLValidator:
    """
    Validates JSON payloads against the OpenKYCAML hybrid schema.

    Parameters
    ----------
    schema_path : Path | None
        Path to the JSON Schema file. Defaults to the bundled schema.
    """

    def __init__(self, schema_path: Path | None = None) -> None:
        resolved = schema_path or _SCHEMA_PATH
        if not resolved.exists():
            raise FileNotFoundError(
                f"OpenKYCAML schema not found at: {resolved}\n"
                "Ensure you are running from within the openKYCAML repository."
            )
        with resolved.open(encoding="utf-8") as fh:
            self._schema = json.load(fh)

        try:
            Draft202012Validator.check_schema(self._schema)
        except SchemaError as exc:
            raise ValueError(f"Invalid schema file: {exc.message}") from exc

        self._validator = Draft202012Validator(self._schema)

    def validate(self, payload: dict[str, Any]) -> ValidationResult:
        """
        Validate a parsed JSON payload.

        Parameters
        ----------
        payload : dict
            The decoded JSON payload to validate.

        Returns
        -------
        ValidationResult
        """
        errors: list[FieldError] = []
        warnings: list[str] = []

        for ve in self._validator.iter_errors(payload):
            path = ".".join(str(p) for p in ve.absolute_path) if ve.absolute_path else ""
            schema_path = "/".join(str(p) for p in ve.absolute_schema_path)
            errors.append(FieldError(path=path, message=ve.message, schema_path=schema_path))

        # Business-logic warnings (not enforced by JSON Schema).
        if not errors:
            warnings.extend(self._business_warnings(payload))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            payload_version=payload.get("version"),
        )

    def validate_file(self, path: Path) -> ValidationResult:
        """Validate a JSON file on disk."""
        with path.open(encoding="utf-8") as fh:
            try:
                payload = json.load(fh)
            except json.JSONDecodeError as exc:
                return ValidationResult(
                    is_valid=False,
                    errors=[FieldError(path="<file>", message=f"Invalid JSON: {exc}")],
                )
        return self.validate(payload)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _business_warnings(self, payload: dict[str, Any]) -> list[str]:  # noqa: C901
        """
        Emit advisory warnings for common compliance oversights.
        These are not schema violations but may indicate incomplete data.
        """
        warns: list[str] = []

        ivms = payload.get("ivms101", {})
        kyc = payload.get("kycProfile", {})

        # Warn if Travel Rule message is missing originating VASP.
        if ivms and not ivms.get("originatingVASP"):
            warns.append(
                "ivms101.originatingVASP is missing — required for FATF Rec 16 / TFR compliance."
            )

        # Warn if legal entity has no beneficial ownership.
        for person_wrapper in (ivms.get("originator") or {}).get("originatorPersons", []):
            if "legalPerson" in person_wrapper and not kyc.get("beneficialOwnership"):
                warns.append(
                    "kycProfile.beneficialOwnership is empty for a legal entity — "
                    "required under AMLR Art. 26 and FATF Rec 24."
                )
                break

        # Warn if PEP but not EDD.
        pep = (kyc.get("pepStatus") or {}).get("isPEP")
        dd_type = kyc.get("dueDiligenceType")
        if pep and dd_type and dd_type != "EDD":
            warns.append(
                f"kycProfile.dueDiligenceType is '{dd_type}' but customer is a PEP — "
                "EDD is mandatory under AMLR Art. 28 and FATF Rec 12."
            )

        # Warn if sanctions screening is older than 30 days.
        import datetime

        screening = kyc.get("sanctionsScreening", {})
        screening_date_str = screening.get("screeningDate")
        if screening_date_str:
            try:
                screening_dt = datetime.datetime.fromisoformat(
                    screening_date_str.replace("Z", "+00:00")
                )
                age = datetime.datetime.now(datetime.timezone.utc) - screening_dt
                if age.days > 30:
                    warns.append(
                        f"kycProfile.sanctionsScreening.screeningDate is {age.days} days old — "
                        "consider re-screening (recommended: every 30 days for high-risk customers)."
                    )
            except ValueError:
                pass

        return warns


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validator",
        description="Validate a JSON payload against the OpenKYCAML schema.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("file", nargs="?", metavar="FILE", help="Path to JSON file to validate.")
    group.add_argument("--stdin", action="store_true", help="Read JSON from stdin.")
    parser.add_argument(
        "--schema",
        metavar="SCHEMA_PATH",
        help="Path to a custom OpenKYCAML schema file (default: bundled schema).",
    )
    parser.add_argument(
        "--no-warnings",
        action="store_true",
        help="Suppress advisory warnings.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    schema_path = Path(args.schema) if args.schema else None
    try:
        validator = OpenKYCAMLValidator(schema_path=schema_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.stdin:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            print(f"ERROR: Invalid JSON on stdin: {exc}", file=sys.stderr)
            return 2
        result = validator.validate(payload)
        source = "<stdin>"
    else:
        path = Path(args.file)
        if not path.exists():
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            return 2
        result = validator.validate_file(path)
        source = str(path)

    print(f"Source : {source}")
    print(result)

    if not args.no_warnings and result.warnings:
        print(f"\n{len(result.warnings)} warning(s):")
        for w in result.warnings:
            print(f"  ⚠  {w}")

    return 0 if result.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
