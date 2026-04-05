#!/usr/bin/env python3
"""
OpenKYCAML Format Converter
============================
Converts between OpenKYCAML and other common formats:

  - IVMS 101 plain JSON  ↔  OpenKYCAML
  - OpenKYCAML  →  ISO 20022 pain.001-compatible dict
  - OpenKYCAML  →  W3C VC JSON-LD (VC-only output)

Usage:
    python converter.py ivms101-to-openkycaml  <ivms101.json>  [--out output.json]
    python converter.py openkycaml-to-ivms101  <payload.json>  [--out output.json]
    python converter.py openkycaml-to-iso20022 <payload.json>  [--out output.json]
    python converter.py extract-vc             <payload.json>  [--out output.json]
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# IVMS 101 → OpenKYCAML
# ---------------------------------------------------------------------------


def ivms101_to_openkycaml(ivms101_payload: dict[str, Any]) -> dict[str, Any]:
    """
    Wrap a plain IVMS 101 JSON object into an OpenKYCAML envelope.

    The IVMS 101 payload is placed verbatim into the ``ivms101`` key.
    Minimal envelope metadata (``version``, ``messageId``, ``messageDateTime``)
    are added.

    Parameters
    ----------
    ivms101_payload : dict
        A raw IVMS 101 payload (as produced by most Travel Rule SDKs).

    Returns
    -------
    dict
        An OpenKYCAML-compliant envelope.
    """
    return {
        "$schema": "https://openkycaml.org/schema/v1.0.0/kyc-aml-hybrid-extended.json",
        "version": "1.0.0",
        "messageId": str(uuid.uuid4()),
        "messageDateTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ivms101": ivms101_payload,
    }


# ---------------------------------------------------------------------------
# OpenKYCAML → IVMS 101
# ---------------------------------------------------------------------------


def openkycaml_to_ivms101(openkycaml_payload: dict[str, Any]) -> dict[str, Any]:
    """
    Extract the raw IVMS 101 block from an OpenKYCAML envelope.

    Parameters
    ----------
    openkycaml_payload : dict
        A full OpenKYCAML envelope.

    Returns
    -------
    dict
        The raw ``ivms101`` block.

    Raises
    ------
    ValueError
        If the payload does not contain an ``ivms101`` block.
    """
    ivms = openkycaml_payload.get("ivms101")
    if not ivms:
        raise ValueError(
            "No 'ivms101' block found in this OpenKYCAML payload. "
            "Cannot convert to plain IVMS 101."
        )
    return ivms


# ---------------------------------------------------------------------------
# OpenKYCAML → ISO 20022 pain.001 (dict representation)
# ---------------------------------------------------------------------------


def openkycaml_to_iso20022(openkycaml_payload: dict[str, Any]) -> dict[str, Any]:
    """
    Convert the originator fields of an OpenKYCAML payload to a
    simplified ISO 20022 pain.001 credit transfer initiation dict.

    This is a best-effort field mapping. Full ISO 20022 XML serialisation
    is outside the scope of this tool — use a dedicated ISO 20022 library
    for production-grade output.

    Parameters
    ----------
    openkycaml_payload : dict
        A full OpenKYCAML envelope containing an ``ivms101`` block.

    Returns
    -------
    dict
        A simplified ISO 20022 pain.001 representation.
    """
    ivms = openkycaml_payload.get("ivms101", {})
    originator_persons = (ivms.get("originator") or {}).get("originatorPersons", [])
    originator_accounts = (ivms.get("originator") or {}).get("accountNumber", [])
    beneficiary_persons = (ivms.get("beneficiary") or {}).get("beneficiaryPersons", [])
    beneficiary_accounts = (ivms.get("beneficiary") or {}).get("accountNumber", [])
    amount_info = ivms.get("transferredAmount", {})

    debtor: dict[str, Any] = {}
    creditor: dict[str, Any] = {}

    # Map originator
    if originator_persons:
        person_wrapper = originator_persons[0]
        if "naturalPerson" in person_wrapper:
            np = person_wrapper["naturalPerson"]
            name_ids = (np.get("name") or {}).get("nameIdentifiers", [])
            if name_ids:
                ni = name_ids[0]
                full_name = " ".join(
                    filter(None, [ni.get("secondaryIdentifier"), ni.get("primaryIdentifier")])
                )
                debtor["Nm"] = full_name
            nat_id = np.get("nationalIdentification", {})
            if nat_id.get("nationalIdentifierType") == "LEIX":
                debtor["Id"] = {"OrgId": {"LEI": nat_id.get("nationalIdentifier")}}
            addr = ((np.get("geographicAddresses") or [{}])[0])
            if addr:
                debtor["PstlAdr"] = {
                    "StrtNm": addr.get("streetName", ""),
                    "BldgNb": addr.get("buildingNumber", ""),
                    "PstCd": addr.get("postCode", ""),
                    "TwnNm": addr.get("townName", ""),
                    "Ctry": addr.get("country", ""),
                }
        elif "legalPerson" in person_wrapper:
            lp = person_wrapper["legalPerson"]
            name_ids = (lp.get("name") or {}).get("nameIdentifiers", [])
            if name_ids:
                for ni in name_ids:
                    if ni.get("legalPersonNameIdentifierType") == "LEGL":
                        debtor["Nm"] = ni["legalPersonName"]
                        break
            nat_id = lp.get("nationalIdentification", {})
            if nat_id.get("nationalIdentifierType") == "LEIX":
                debtor["Id"] = {"OrgId": {"LEI": nat_id.get("nationalIdentifier")}}

    # Map beneficiary
    if beneficiary_persons:
        person_wrapper = beneficiary_persons[0]
        if "naturalPerson" in person_wrapper:
            np = person_wrapper["naturalPerson"]
            name_ids = (np.get("name") or {}).get("nameIdentifiers", [])
            if name_ids:
                ni = name_ids[0]
                creditor["Nm"] = " ".join(
                    filter(None, [ni.get("secondaryIdentifier"), ni.get("primaryIdentifier")])
                )
        elif "legalPerson" in person_wrapper:
            lp = person_wrapper["legalPerson"]
            name_ids = (lp.get("name") or {}).get("nameIdentifiers", [])
            if name_ids:
                for ni in name_ids:
                    if ni.get("legalPersonNameIdentifierType") == "LEGL":
                        creditor["Nm"] = ni["legalPersonName"]
                        break

    return {
        "Document": {
            "CstmrCdtTrfInitn": {
                "GrpHdr": {
                    "MsgId": openkycaml_payload.get("messageId", str(uuid.uuid4())),
                    "CreDtTm": openkycaml_payload.get(
                        "messageDateTime",
                        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    ),
                    "NbOfTxs": "1",
                },
                "PmtInf": [
                    {
                        "Dbtr": debtor,
                        "DbtrAcct": {
                            "Id": {"Othr": {"Id": originator_accounts[0] if originator_accounts else ""}}
                        },
                        "CdtTrfTxInf": [
                            {
                                "Amt": {
                                    "InstdAmt": {
                                        "@Ccy": amount_info.get("assetType", ""),
                                        "#text": amount_info.get("amount", "0"),
                                    }
                                },
                                "Cdtr": creditor,
                                "CdtrAcct": {
                                    "Id": {
                                        "Othr": {
                                            "Id": beneficiary_accounts[0] if beneficiary_accounts else ""
                                        }
                                    }
                                },
                            }
                        ],
                    }
                ],
            }
        }
    }


# ---------------------------------------------------------------------------
# OpenKYCAML → W3C VC (extract VC block only)
# ---------------------------------------------------------------------------


def extract_vc(openkycaml_payload: dict[str, Any]) -> dict[str, Any]:
    """
    Extract the Verifiable Credential block from an OpenKYCAML envelope.

    Parameters
    ----------
    openkycaml_payload : dict
        A full OpenKYCAML envelope.

    Returns
    -------
    dict
        The raw ``verifiableCredential`` block.

    Raises
    ------
    ValueError
        If no ``verifiableCredential`` block is present.
    """
    vc = openkycaml_payload.get("verifiableCredential")
    if not vc:
        raise ValueError(
            "No 'verifiableCredential' block found. "
            "This payload was not issued as a Verifiable Credential."
        )
    return vc


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_COMMANDS = {
    "ivms101-to-openkycaml": ("ivms101.json", ivms101_to_openkycaml),
    "openkycaml-to-ivms101": ("openkycaml.json", openkycaml_to_ivms101),
    "openkycaml-to-iso20022": ("openkycaml.json", openkycaml_to_iso20022),
    "extract-vc": ("openkycaml.json", extract_vc),
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="converter",
        description="Convert between OpenKYCAML and other formats.",
    )
    parser.add_argument(
        "command",
        choices=list(_COMMANDS.keys()),
        help="Conversion direction.",
    )
    parser.add_argument("input", metavar="INPUT", help="Path to the input JSON file.")
    parser.add_argument(
        "--out",
        metavar="OUTPUT",
        help="Path to write the output JSON file (default: stdout).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        return 2

    with input_path.open(encoding="utf-8") as fh:
        try:
            payload = json.load(fh)
        except json.JSONDecodeError as exc:
            print(f"ERROR: Invalid JSON: {exc}", file=sys.stderr)
            return 2

    _, convert_fn = _COMMANDS[args.command]
    try:
        result = convert_fn(payload)
    except (ValueError, KeyError) as exc:
        print(f"ERROR: Conversion failed — {exc}", file=sys.stderr)
        return 1

    output = json.dumps(result, indent=2, ensure_ascii=False)

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(output, encoding="utf-8")
        print(f"Written to {out_path}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
