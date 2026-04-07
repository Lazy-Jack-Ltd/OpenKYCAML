#!/usr/bin/env python3
"""
Wolfsberg CBDDQ v1.4 ↔ OpenKYCAML v1.8.0 Importer/Exporter
============================================================

Converts Wolfsberg CBDDQ v1.4 questionnaire responses to OpenKYCAML v1.8.0
envelopes and vice versa. Produces gap reports for unmapped fields.

Usage:
    python wolfsberg_importer.py import  --input cbddq.json --output kyc.json
    python wolfsberg_importer.py export  --input kyc.json   --output cbddq.json
    python wolfsberg_importer.py gap-report --input cbddq.json

Mapping reference: docs/mappings/wolfsberg-fccq-cbddq.md
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
# Field mapping: CBDDQ key → OpenKYCAML path
# ---------------------------------------------------------------------------

_CBDDQ_TO_OPENKYCAML: dict[str, str] = {
    # A — Organisation & Structure
    "legalName": "ivms101.originator.originatorPersons[0].legalPerson.name.nameIdentifiers[0].legalPersonName",
    "jurisdiction": "ivms101.originator.originatorPersons[0].legalPerson.countryOfRegistration",
    "lei": "ivms101.originator.originatorPersons[0].legalPerson.nationalIdentification.nationalIdentifier",
    # B — Ownership
    "bearerSharesIssued": "kycProfile.beneficialOwnership[0].nomineeFlags.bearerShareFlag",
    "nomineeArrangements": "kycProfile.beneficialOwnership[0].nomineeFlags.isNominee",
    # C — AML Programme
    "amlModelVersion": "kycProfile.monitoringInfo.tmModelVersion",
    # D — Customer Due Diligence
    "customerRiskCategory": "kycProfile.customerRiskRating",
    "dueDiligenceLevel": "kycProfile.dueDiligenceType",
    "eddRequired": "kycProfile.monitoringInfo.eddRequired",
    # E — Sanctions & PEP
    "sanctionsScreeningStatus": "kycProfile.sanctionsScreening.screeningStatus",
    "sanctionsScreeningProvider": "kycProfile.sanctionsScreening.screeningProvider",
    "isPEP": "kycProfile.pepStatus.isPEP",
    # F — Monitoring
    "monitoringLevel": "kycProfile.monitoringInfo.monitoringLevel",
    "lastReviewDate": "kycProfile.monitoringInfo.lastReviewDate",
    "nextReviewDate": "kycProfile.monitoringInfo.nextReviewDate",
    # G — Information Sharing
    "section314bSafeHarbor": "informationSharingFlags.section314bSafeHarbor",
}

_CBDDQ_RISK_RATING_MAP: dict[str, str] = {
    "low": "LOW",
    "medium": "MEDIUM",
    "high": "HIGH",
    "very high": "VERY_HIGH",
    "Low": "LOW",
    "Medium": "MEDIUM",
    "High": "HIGH",
    "Very High": "VERY_HIGH",
}

_CBDDQ_DD_TYPE_MAP: dict[str, str] = {
    "simplified": "SDD",
    "standard": "CDD",
    "enhanced": "EDD",
    "Simplified": "SDD",
    "Standard": "CDD",
    "Enhanced": "EDD",
}

# Fields in CBDDQ with no current OpenKYCAML mapping
_GAP_FIELDS: list[dict[str, str]] = [
    {"cbddqField": "productUsage", "reason": "kycProfile.productUsage[] planned in future version"},
    {"cbddqField": "regulatoryLicenceNumber", "reason": "Partial — use nationalIdentification with RAID type"},
    {"cbddqField": "amlAuditReportDate", "reason": "Use kycProfile.auditMetadata.dataSourceSystem as reference"},
    {"cbddqField": "correspondentBankCount", "reason": "Not in scope — operational field"},
    {"cbddqField": "swiftBic", "reason": "Not in schema — use ivms101 VASP fields"},
]


# ---------------------------------------------------------------------------
# Import: CBDDQ → OpenKYCAML
# ---------------------------------------------------------------------------

def cbddq_to_openkycaml(cbddq: dict[str, Any]) -> dict[str, Any]:
    """Convert a flat CBDDQ v1.4 JSON response to an OpenKYCAML v1.8.0 envelope."""
    envelope: dict[str, Any] = {
        "version": "1.8.0",
        "messageId": str(uuid.uuid4()),
        "messageDateTime": datetime.now(timezone.utc).isoformat(),
        "kycProfile": {
            "auditMetadata": {
                "recordId": str(uuid.uuid4()),
                "recordCreatedAt": datetime.now(timezone.utc).isoformat(),
                "recordVersion": 1,
                "dataSourceSystem": "wolfsberg-cbddq-importer",
            }
        },
    }

    kyc = envelope["kycProfile"]

    # Legal entity name and jurisdiction
    if "legalName" in cbddq:
        envelope.setdefault("ivms101", {}).setdefault("originator", {}).setdefault(
            "originatorPersons", [{}]
        )[0].setdefault("legalPerson", {}).setdefault("name", {}).setdefault(
            "nameIdentifiers", [{}]
        )[0].update({"legalPersonName": cbddq["legalName"], "legalPersonNameIdentifierType": "LEGL"})

    if "jurisdiction" in cbddq:
        envelope.setdefault("ivms101", {}).setdefault("originator", {}).setdefault(
            "originatorPersons", [{}]
        )[0].setdefault("legalPerson", {})["countryOfRegistration"] = cbddq["jurisdiction"]

    if "lei" in cbddq:
        envelope.setdefault("ivms101", {}).setdefault("originator", {}).setdefault(
            "originatorPersons", [{}]
        )[0].setdefault("legalPerson", {})["nationalIdentification"] = {
            "nationalIdentifier": cbddq["lei"],
            "nationalIdentifierType": "LEIX",
        }

    # Risk and due diligence
    raw_risk = cbddq.get("customerRiskCategory", "")
    if raw_risk:
        kyc["customerRiskRating"] = _CBDDQ_RISK_RATING_MAP.get(raw_risk, "MEDIUM")

    raw_dd = cbddq.get("dueDiligenceLevel", "")
    if raw_dd:
        kyc["dueDiligenceType"] = _CBDDQ_DD_TYPE_MAP.get(raw_dd, "CDD")

    # Monitoring
    monitoring: dict[str, Any] = {}
    if "monitoringLevel" in cbddq:
        monitoring["monitoringLevel"] = cbddq["monitoringLevel"].upper()
    if "lastReviewDate" in cbddq:
        monitoring["lastReviewDate"] = cbddq["lastReviewDate"]
    if "nextReviewDate" in cbddq:
        monitoring["nextReviewDate"] = cbddq["nextReviewDate"]
    if "eddRequired" in cbddq:
        monitoring["eddRequired"] = bool(cbddq["eddRequired"])
    if "amlModelVersion" in cbddq:
        monitoring["tmModelVersion"] = cbddq["amlModelVersion"]
    if monitoring:
        kyc["monitoringInfo"] = monitoring

    # Sanctions screening
    if "sanctionsScreeningStatus" in cbddq or "sanctionsScreeningProvider" in cbddq:
        kyc["sanctionsScreening"] = {
            "screeningStatus": cbddq.get("sanctionsScreeningStatus", "PENDING").upper(),
            "screeningDate": datetime.now(timezone.utc).isoformat(),
            "screeningProvider": cbddq.get("sanctionsScreeningProvider"),
        }

    # PEP
    if "isPEP" in cbddq:
        kyc["pepStatus"] = {"isPEP": bool(cbddq["isPEP"])}

    # Beneficial ownership
    bo: dict[str, Any] = {"ownershipPercentage": cbddq.get("uboOwnershipPct", 0)}
    if "bearerSharesIssued" in cbddq:
        bo.setdefault("nomineeFlags", {})["bearerShareFlag"] = bool(cbddq["bearerSharesIssued"])
    if "nomineeArrangements" in cbddq:
        bo.setdefault("nomineeFlags", {})["isNominee"] = bool(cbddq["nomineeArrangements"])
    if len(bo) > 1:
        kyc["beneficialOwnership"] = [bo]

    # Information sharing flags
    if "section314bSafeHarbor" in cbddq:
        envelope["informationSharingFlags"] = {
            "section314bSafeHarbor": bool(cbddq["section314bSafeHarbor"]),
            "sharingConsentTimestamp": datetime.now(timezone.utc).isoformat(),
        }

    return envelope


# ---------------------------------------------------------------------------
# Export: OpenKYCAML → CBDDQ
# ---------------------------------------------------------------------------

def openkycaml_to_cbddq(envelope: dict[str, Any]) -> dict[str, Any]:
    """Convert an OpenKYCAML v1.8.0 envelope to a flat CBDDQ v1.4 JSON representation."""
    cbddq: dict[str, Any] = {}
    kyc = envelope.get("kycProfile", {})
    ivms = envelope.get("ivms101", {})

    # Legal entity
    persons = ivms.get("originator", {}).get("originatorPersons", [{}])
    lp = persons[0].get("legalPerson", {}) if persons else {}
    names = lp.get("name", {}).get("nameIdentifiers", [{}])
    if names:
        cbddq["legalName"] = names[0].get("legalPersonName", "")
    cbddq["jurisdiction"] = lp.get("countryOfRegistration", "")
    nat_id = lp.get("nationalIdentification", {})
    if nat_id.get("nationalIdentifierType") == "LEIX":
        cbddq["lei"] = nat_id.get("nationalIdentifier", "")

    # Risk
    _inv_risk = {v: k for k, v in _CBDDQ_RISK_RATING_MAP.items() if k[0].isupper()}
    cbddq["customerRiskCategory"] = _inv_risk.get(kyc.get("customerRiskRating", ""), "Medium")
    _inv_dd = {v: k for k, v in _CBDDQ_DD_TYPE_MAP.items() if k[0].isupper()}
    cbddq["dueDiligenceLevel"] = _inv_dd.get(kyc.get("dueDiligenceType", ""), "Standard")

    # Monitoring
    mon = kyc.get("monitoringInfo", {})
    cbddq["monitoringLevel"] = mon.get("monitoringLevel", "")
    cbddq["lastReviewDate"] = mon.get("lastReviewDate", "")
    cbddq["nextReviewDate"] = mon.get("nextReviewDate", "")
    cbddq["eddRequired"] = mon.get("eddRequired", False)
    cbddq["amlModelVersion"] = mon.get("tmModelVersion", "")

    # Sanctions
    ss = kyc.get("sanctionsScreening", {})
    cbddq["sanctionsScreeningStatus"] = ss.get("screeningStatus", "")
    cbddq["sanctionsScreeningProvider"] = ss.get("screeningProvider", "")

    # PEP
    pep = kyc.get("pepStatus", {})
    cbddq["isPEP"] = pep.get("isPEP", False)

    # Beneficial ownership / nominee
    bos = kyc.get("beneficialOwnership", [{}])
    if bos:
        nom = bos[0].get("nomineeFlags", {})
        cbddq["bearerSharesIssued"] = nom.get("bearerShareFlag", False)
        cbddq["nomineeArrangements"] = nom.get("isNominee", False)

    # Information sharing
    isf = envelope.get("informationSharingFlags", {})
    cbddq["section314bSafeHarbor"] = isf.get("section314bSafeHarbor", False)

    return cbddq


# ---------------------------------------------------------------------------
# Gap report
# ---------------------------------------------------------------------------

def produce_gap_report(cbddq: dict[str, Any]) -> list[dict[str, str]]:
    """Identify CBDDQ fields with no or partial OpenKYCAML mapping."""
    gaps = list(_GAP_FIELDS)
    unmapped = [
        {"cbddqField": k, "reason": "Field not in current OpenKYCAML mapping table"}
        for k in cbddq
        if k not in _CBDDQ_TO_OPENKYCAML and k not in {g["cbddqField"] for g in _GAP_FIELDS}
    ]
    return gaps + unmapped


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wolfsberg_importer",
        description="Wolfsberg CBDDQ v1.4 ↔ OpenKYCAML v1.8.0 converter",
    )
    sub = p.add_subparsers(dest="command", required=True)

    imp = sub.add_parser("import", help="CBDDQ → OpenKYCAML")
    imp.add_argument("--input", required=True)
    imp.add_argument("--output", required=False)

    exp = sub.add_parser("export", help="OpenKYCAML → CBDDQ")
    exp.add_argument("--input", required=True)
    exp.add_argument("--output", required=False)

    gap = sub.add_parser("gap-report", help="Produce gap report for a CBDDQ file")
    gap.add_argument("--input", required=True)

    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    with open(args.input, encoding="utf-8") as fh:
        data = json.load(fh)

    if args.command == "import":
        result = cbddq_to_openkycaml(data)
    elif args.command == "export":
        result = openkycaml_to_cbddq(data)
    elif args.command == "gap-report":
        result = {"gaps": produce_gap_report(data)}
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 2

    output_str = json.dumps(result, indent=2)
    if hasattr(args, "output") and args.output:
        Path(args.output).write_text(output_str, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(output_str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
