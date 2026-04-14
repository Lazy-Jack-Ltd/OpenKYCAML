#!/usr/bin/env python3
"""
OpenKYCAML Schema Validator
===========================
Validates JSON payloads against the OpenKYCAML schema (v1.19.0).

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
import datetime
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator, ValidationError
from jsonschema.exceptions import SchemaError

# Resolve schema relative to this file so the validator works from any CWD.
_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schema" / "kyc-aml-hybrid-extended.json"

# Canonical pattern for OpenKYCAML Document ID URNs.
# Format: urn:openkycaml:doc:{country}:{doc-type-code}:{subject-ref}:{YYYY-MM}
_DOCUMENT_ID_PATTERN = re.compile(
    r"^urn:openkycaml:doc:[a-z]{2}:[a-z0-9-]+:[a-z0-9-]+:[0-9]{4}-[0-9]{2}$"
)


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
        screening = kyc.get("sanctionsScreening", {})
        screening_date_str = screening.get("screeningDate")
        if screening_date_str:
            try:
                screening_dt = datetime.datetime.fromisoformat(
                    screening_date_str.replace("Z", "+00:00")
                )
                # Normalise to UTC — fromisoformat may return an offset-aware or
                # offset-naive datetime depending on whether the string contains tz info.
                if screening_dt.tzinfo is None:
                    screening_dt = screening_dt.replace(tzinfo=datetime.timezone.utc)
                else:
                    screening_dt = screening_dt.astimezone(datetime.timezone.utc)
                age = datetime.datetime.now(datetime.timezone.utc) - screening_dt
                if age.days > 30:
                    warns.append(
                        f"kycProfile.sanctionsScreening.screeningDate is {age.days} days old — "
                        "consider re-screening (recommended: every 30 days for high-risk customers)."
                    )
            except ValueError:
                pass

        # Warn if sensitivity metadata indicates tipping-off restriction but
        # the classification doesn't match a SAR-protected class.
        gdpr = payload.get("gdprSensitivityMetadata", {})
        if gdpr:
            cls = gdpr.get("classification")
            tipping_off = gdpr.get("tippingOffProtected")
            if cls in ("sar_restricted", "internal_suspicion") and not tipping_off:
                warns.append(
                    "gdprSensitivityMetadata.tippingOffProtected should be true when "
                    f"classification is '{cls}' (AMLR Art. 73 / FATF Rec. 21)."
                )

        # Warn when documents in identityDocuments lack a canonical documentId or
        # carry a documentId that does not conform to the OpenKYCAML URN scheme.
        identity_docs = payload.get("identityDocuments", {})
        for collection_key in ("naturalPersonDocuments", "legalEntityDocuments"):
            for idx, doc in enumerate(identity_docs.get(collection_key, [])):
                doc_id = doc.get("documentId")
                location = f"identityDocuments.{collection_key}[{idx}]"
                if not doc_id:
                    warns.append(
                        f"{location} is missing documentId — a canonical URN is recommended "
                        "for cross-system deduplication (see docs/reference/document-id-convention.md)."
                    )
                elif not _DOCUMENT_ID_PATTERN.match(doc_id):
                    warns.append(
                        f"{location}.documentId '{doc_id}' does not conform to the "
                        "OpenKYCAML Document ID URN scheme "
                        "'urn:openkycaml:doc:{{country}}:{{doc-type-code}}:{{subject-ref}}:{{YYYY-MM}}'."
                    )

        # PredictiveAML EU AI Act warnings.
        predictive = payload.get("predictiveAML", {})
        if predictive:
            model_meta = predictive.get("modelMetadata", {})
            eu_class = model_meta.get("euAiActClassification")
            if eu_class == "high-risk-aml" and not model_meta.get("conformityAssessmentReference", "").strip():
                warns.append(
                    "predictiveAML.modelMetadata.conformityAssessmentReference is missing — "
                    "required for EU AI Act Art. 43 conformity assessment when "
                    "euAiActClassification is 'high-risk-aml'."
                )

            scores = predictive.get("predictiveScores", [])
            for idx, score in enumerate(scores):
                if score.get("confidence") is None:
                    warns.append(
                        f"predictiveAML.predictiveScores[{idx}].confidence is missing — "
                        "required for EU AI Act Art. 13(3)(b)(ii) reliability disclosure."
                    )

            if not predictive.get("explainability"):
                warns.append(
                    "predictiveAML.explainability is absent — EU AI Act Art. 13(3)(b)(iii) "
                    "requires output interpretation guidance for high-risk AML systems."
                )

            data_agg = predictive.get("dataAggregationMetadata", {})
            if data_agg.get("bcbs239ComplianceLevel") == "gap-analysis":
                warns.append(
                    "predictiveAML.dataAggregationMetadata.bcbs239ComplianceLevel is 'gap-analysis' — "
                    "BCBS 239 compliance gaps should be remediated before supervisory review (Principle 12)."
                )

        # Beneficial ownership nominee/bearer-share warnings (FATF R.24 2022 revision).
        bos = kyc.get("beneficialOwnership", [])
        for idx, bo in enumerate(bos):
            nom = bo.get("nomineeFlags", {})
            location = f"kycProfile.beneficialOwnership[{idx}]"
            if nom.get("bearerShareFlag") and dd_type and dd_type != "EDD":
                warns.append(
                    f"{location}.nomineeFlags.bearerShareFlag is true but dueDiligenceType is "
                    f"'{dd_type}' — FATF R.24 (2022 revision) requires EDD when bearer shares are in issue."
                )
            if nom.get("isNominee") and not nom.get("nominatorIdentified"):
                warns.append(
                    f"{location}.nomineeFlags.isNominee is true but nominatorIdentified is false — "
                    "FATF R.24 (2022 revision) requires the actual owner behind the nominee to be identified."
                )

        # XRPL confidential transfer compliance warning.
        blockchain_ids = kyc.get("blockchainAccountIds", [])
        for idx, acct in enumerate(blockchain_ids):
            ct = acct.get("xrplConfidentialTransfer", {})
            if ct.get("enabled") and not ct.get("authorisedViewingKeys"):
                warns.append(
                    f"kycProfile.blockchainAccountIds[{idx}].xrplConfidentialTransfer.enabled is true "
                    "but authorisedViewingKeys is empty — AMLR Art. 21 / FATF R.16 require "
                    "supervisory viewing key access for confidential transfers (XLS-96d)."
                )

        # Tax status ESR and Pillar 2 warnings (v1.9.0).
        tax = payload.get("taxStatus", {})
        if tax:
            esr = tax.get("economicSubstance", {})
            if esr.get("status") == "nonCompliant":
                jur = esr.get("jurisdiction", "unknown")
                warns.append(
                    f"taxStatus.economicSubstance.status is 'nonCompliant' for jurisdiction '{jur}' — "
                    "ESR non-compliance is a direct AML red flag under AMLR Art. 26 and EBA ML/TF "
                    "risk-factor guidelines. EDD is required; consider SAR filing."
                )

            p2 = tax.get("pillarTwo", {})
            if p2.get("inScopeMNE") and not p2.get("girFilingReference", "").strip():
                warns.append(
                    "taxStatus.pillarTwo.inScopeMNE is true but girFilingReference is absent — "
                    "in-scope MNEs must file a GloBE Information Return (GIR). "
                    "Request the GIR reference and perform enhanced due diligence."
                )

            # FATCA warnings (v1.9.1).
            fatca = tax.get("fatcaStatus", {})
            if fatca:
                giin = fatca.get("giin", "")
                if giin and not re.match(r'^[0-9A-Z]{6}\.[0-9A-Z]{5}\.[0-9A-Z]{2}\.[0-9A-Z]{3}$', giin):
                    warns.append(
                        f"taxStatus.fatcaStatus.giin '{giin}' does not match the IRS GIIN format "
                        "(XXXXXX.XXXXX.XX.XXX). Please verify against the IRS FATCA FFI List."
                    )
                if fatca.get("chapter4Classification") == "nonParticipatingFFI":
                    warns.append(
                        "taxStatus.fatcaStatus.chapter4Classification is 'nonParticipatingFFI' — "
                        "non-participating FFIs are subject to 30% FATCA withholding and represent "
                        "elevated US tax-risk. EDD is recommended."
                    )
                ts_str = fatca.get("ffiListVerificationTimestamp", "")
                if ts_str:
                    try:
                        ts = datetime.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        if datetime.datetime.now(datetime.timezone.utc) - ts > datetime.timedelta(days=35):
                            warns.append(
                                "taxStatus.fatcaStatus.ffiListVerificationTimestamp is more than 35 days old — "
                                "the IRS FATCA FFI List is updated monthly; please re-verify the GIIN."
                            )
                    except (ValueError, TypeError):
                        pass

        # EDD contact data warnings — check typed arrays (emailAddresses[], phoneNumbers[]).
        dd_type_outer = kyc.get("dueDiligenceType")
        if dd_type_outer == "ENHANCED":
            for idx, person_wrapper in enumerate(
                (ivms.get("originator") or {}).get("originatorPersons", [])
            ):
                np = person_wrapper.get("naturalPerson")
                if np:
                    has_email = bool(np.get("emailAddresses"))
                    has_phone = bool(np.get("phoneNumbers"))
                    if not has_email and not has_phone:
                        warns.append(
                            f"ivms101.originator.originatorPersons[{idx}].naturalPerson has neither "
                            "emailAddresses[] nor phoneNumbers[] — FATF Rec. 16 / AMLR Art. 22 require "
                            "verified contact data for Enhanced Due Diligence customers."
                        )

        # isPrimary uniqueness warnings — at most one entry per array may be isPrimary: true.
        def _check_is_primary(arr: list, location: str) -> list[str]:
            primary_count = sum(1 for item in arr if isinstance(item, dict) and item.get("isPrimary") is True)
            if primary_count > 1:
                return [
                    f"{location} has {primary_count} entries with isPrimary: true — "
                    "at most one entry should be marked as primary."
                ]
            return []

        for person_key in ("originator", "beneficiary"):
            persons_key = "originatorPersons" if person_key == "originator" else "beneficiaryPersons"
            for idx, person_wrapper in enumerate(
                (ivms.get(person_key) or {}).get(persons_key, [])
            ):
                base = f"ivms101.{person_key}.{persons_key}[{idx}]"
                for person_type in ("naturalPerson", "legalPerson"):
                    person = person_wrapper.get(person_type)
                    if person:
                        loc = f"{base}.{person_type}"
                        for arr_field in ("geographicAddress", "emailAddresses", "phoneNumbers"):
                            arr = person.get(arr_field)
                            if arr:
                                warns.extend(_check_is_primary(arr, f"{loc}.{arr_field}"))

        # IBAN without BIC warnings (v1.10.0).
        for person_key in ("originator", "beneficiary"):
            persons_key = "originatorPersons" if person_key == "originator" else "beneficiaryPersons"
            for idx, person_wrapper in enumerate(
                (ivms.get(person_key) or {}).get(persons_key, [])
            ):
                for person_type in ("naturalPerson", "legalPerson"):
                    person = person_wrapper.get(person_type)
                    if person:
                        for bidx, bd in enumerate(person.get("bankingDetails") or []):
                            if bd.get("iban") and not bd.get("bic"):
                                warns.append(
                                    f"ivms101.{person_key}.{persons_key}[{idx}].{person_type}"
                                    f".bankingDetails[{bidx}].iban is present but bic is absent — "
                                    "BIC is required for SEPA credit transfers and correspondent "
                                    "banking identification (ISO 9362 / FATF Rec. 16)."
                                )

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
