#!/usr/bin/env python3
"""
OpenKYCAML × SWIFT MT Converter
================================
Bidirectional converter between OpenKYCAML v1.4.0 payloads and legacy SWIFT
MT messages.

Supported message types
-----------------------
MT 103   Customer Credit Transfer
MT 202   General Financial Institution Transfer
MT 202 COV  Covered Financial Institution Transfer
MT 910   Confirmation of Credit
MT 940   Customer Statement Message

Functions
---------
openkycaml_to_mt103(payload, config=None) -> str
    Produce a SWIFT MT 103 message from an OpenKYCAML payload.

openkycaml_to_mt202(payload, config=None) -> str
    Produce a SWIFT MT 202 message.

openkycaml_to_mt202cov(payload, config=None) -> str
    Produce a SWIFT MT 202 COV message (with underlying customer info).

openkycaml_to_mt910(payload, config=None) -> str
    Produce a SWIFT MT 910 Confirmation of Credit.

openkycaml_to_mt940(payload, config=None) -> str
    Produce a SWIFT MT 940 Customer Statement.

mt_to_openkycaml(mt_text) -> dict
    Parse any of the above MT message types and return an OpenKYCAML payload.

parse_77b(field_77b) -> dict
    Extract Travel Rule / KYC fields from a free-text MT 103 :77B: block.

build_77b(payload) -> str
    Build an MT 103 :77B: regulatory-reporting string from an OpenKYCAML payload.

Design notes
------------
- MT messages are plain-text SWIFT FIN format (block headers optional).
- Field tags follow SWIFT notation: :20:, :23B:, :32A:, :50K:, :59:, etc.
- All field lengths are respected (e.g. :20: max 16 chars; :32A: value date
  YYMMDD + CCY + amount).
- 77B is the primary Travel Rule carrier in legacy SWIFT. The converter:
    * Reads 77B and populates OpenKYCAML ivms101 fields (best-effort from free text).
    * Writes 77B from OpenKYCAML data for outbound MT 103 production.
- No third-party dependencies — uses Python standard library only.

Usage
-----
    from swift_mt_converter import openkycaml_to_mt103, mt_to_openkycaml

    with open("examples/minimal-travel-rule.json") as f:
        payload = json.load(f)

    mt103 = openkycaml_to_mt103(payload)
    print(mt103)

    recovered = mt_to_openkycaml(mt103)
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SCHEMA_URL = "https://openkycaml.org/schema/v1.4.0/kyc-aml-hybrid-extended.json"
_VERSION = "1.4.0"

# Maximum field lengths per SWIFT specification
_MAX_REF = 16        # :20: Sender's Reference
_MAX_NAME = 35       # Name line in :50K:/:59: (SWIFT line limit)
_MAX_77B = 35 * 3    # :77B: up to 3 × 35-char lines
_MAX_70 = 35 * 4     # :70: Remittance Info up to 4 lines
_DATE_FMT = "%y%m%d"  # YYMMDD

# IBAN pattern
_IBAN_RE = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$")

# ISO 4217 fiat currencies (non-exhaustive subset used for detection)
_ISO4217_CODES = frozenset(
    "AED AFN ALL AMD ANG AOA ARS AUD AWG AZN BAM BBD BDT BGN BHD "
    "BMD BND BOB BRL BSD BTN BWP BYN BZD CAD CDF CHF CLP CNY COP "
    "CRC CUP CVE CZK DJF DKK DOP DZD EGP ERN ETB EUR FJD FKP GBP "
    "GEL GHS GIP GMD GNF GTQ GYD HKD HNL HRK HTG HUF IDR ILS INR "
    "IQD IRR ISK JMD JOD JPY KES KGS KHR KMF KPW KRW KWD KYD KZT "
    "LAK LBP LKR LRD LSL LYD MAD MDL MGA MKD MMK MNT MOP MRU MUR "
    "MVR MWK MXN MYR MZN NAD NGN NIO NOK NPR NZD OMR PAB PEN PGK "
    "PHP PKR PLN PYG QAR RON RSD RUB RWF SAR SBD SCR SDG SEK SGD "
    "SHP SLE SOS SRD STN SVC SYP SZL THB TJS TMT TND TOP TRY TTD "
    "TWD TZS UAH UGX USD UYU UZS VES VND VUV WST XAF XCD XOF XPF "
    "YER ZAR ZMW ZWL XXX".split()
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_ymd() -> str:
    """Return today's date in YYMMDD format (UTC)."""
    return datetime.now(timezone.utc).strftime(_DATE_FMT)


def _now_iso() -> str:
    """Return current UTC datetime in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _short_ref(ref: str) -> str:
    """Truncate reference to SWIFT :20: max (16 chars), replacing spaces."""
    return ref.replace(" ", "-")[:_MAX_REF]


def _is_iban(value: str) -> bool:
    return bool(_IBAN_RE.match(value.upper()))


def _is_fiat(code: str) -> bool:
    return code.upper() in _ISO4217_CODES


def _format_amount(amount_str: str, ccy: str) -> str:
    """
    Format amount for :32A: / :32B: fields.

    SWIFT uses comma as decimal separator and no thousands separator.
    e.g. "12345.67" → "12345,67"
    """
    try:
        value = float(amount_str)
        # Format with 2 decimal places, then convert dot to comma
        formatted = f"{value:.2f}".replace(".", ",")
    except (ValueError, TypeError):
        formatted = amount_str.replace(".", ",") if amount_str else "0,00"
    return formatted


def _parse_amount(swift_amount: str) -> str:
    """Convert SWIFT amount (comma decimal) back to standard decimal notation."""
    return swift_amount.replace(",", ".")


def _ymd_to_iso(ymd: str) -> str:
    """Convert YYMMDD to YYYY-MM-DD. Assumes 2000s."""
    try:
        dt = datetime.strptime(ymd, _DATE_FMT)
        # Assume 21st century
        full_year = 2000 + dt.year if dt.year < 100 else dt.year
        return f"{full_year:04d}-{dt.month:02d}-{dt.day:02d}"
    except ValueError:
        return ymd


def _iso_to_ymd(iso_date: str) -> str:
    """Convert ISO 8601 date (YYYY-MM-DD or datetime) to YYMMDD."""
    # Take only the date part
    date_part = iso_date[:10]
    try:
        dt = datetime.strptime(date_part, "%Y-%m-%d")
        return dt.strftime(_DATE_FMT)
    except ValueError:
        return _now_ymd()


def _get_name_string(person_block: dict[str, Any]) -> str:
    """Extract display name from an IVMS 101 person block."""
    if "naturalPerson" in person_block:
        np = person_block["naturalPerson"]
        name_ids = (np.get("name") or {}).get("nameIdentifier", [])
        if name_ids:
            ni = name_ids[0]
            return " ".join(
                filter(None, [ni.get("secondaryIdentifier"), ni.get("primaryIdentifier")])
            ).strip()
    elif "legalPerson" in person_block:
        lp = person_block["legalPerson"]
        name_ids = (lp.get("name") or {}).get("nameIdentifier", [])
        for ni in name_ids:
            if ni.get("legalPersonNameIdentifierType") == "LEGL":
                return ni.get("legalPersonName", "")
        if name_ids:
            return name_ids[0].get("legalPersonName", "")
    return ""


def _get_account(person_accounts: list[str]) -> str:
    """Return first account number, or empty string."""
    return person_accounts[0] if person_accounts else ""


def _get_address_lines(person_block: dict[str, Any]) -> list[str]:
    """Extract address as a list of SWIFT-formatted address lines (max 35 chars each)."""
    person = person_block.get("naturalPerson") or person_block.get("legalPerson") or {}
    addresses = person.get("geographicAddresses", [])
    if not addresses:
        return []
    addr = addresses[0]
    lines: list[str] = []
    street = " ".join(filter(None, [addr.get("streetName"), addr.get("buildingNumber")])).strip()
    if street:
        lines.append(street[:_MAX_NAME])
    city_line = " ".join(filter(None, [addr.get("postCode"), addr.get("townName")])).strip()
    if city_line:
        lines.append(city_line[:_MAX_NAME])
    if addr.get("country"):
        lines.append(addr["country"][:_MAX_NAME])
    for aline in addr.get("addressLine", []):
        lines.append(aline[:_MAX_NAME])
    return lines[:3]  # SWIFT address fields typically allow up to 3 lines


def _get_bic_or_lei(vasp: dict[str, Any]) -> str:
    """Return LEI if available, else name truncated, for SWIFT agent fields."""
    if vasp.get("lei"):
        return vasp["lei"][:11]  # truncate LEI for BIC-width field if needed
    if vasp.get("name"):
        return vasp["name"][:_MAX_NAME]
    return ""


def _split_mt_fields(mt_text: str) -> dict[str, list[str]]:
    """
    Parse a SWIFT MT message into a dict of {tag: [value, ...]} mappings.

    Handles both Block 4 wrapped ({4:\r\n...-}) and raw field-only input.
    Multiple occurrences of the same tag are preserved as a list.
    """
    # Strip block headers if present (e.g. {1:...}{2:...}{3:...}{4:\r\n...\r\n-}{5:...})
    # Extract block 4 content if blocks are present
    block4_match = re.search(r"\{4:\r?\n(.*?)\r?\n-\}", mt_text, re.DOTALL)
    if block4_match:
        content = block4_match.group(1)
    else:
        content = mt_text

    fields: dict[str, list[str]] = {}
    # SWIFT field pattern: :TAG: followed by value up to next :TAG: or end
    pattern = re.compile(r":([0-9]{2}[A-Z]?):(.*?)(?=\r?\n:[0-9]{2}[A-Z]?:|$)", re.DOTALL)
    for match in pattern.finditer(content):
        tag = match.group(1)
        value = match.group(2).strip()
        fields.setdefault(tag, []).append(value)
    return fields


# ---------------------------------------------------------------------------
# 77B: Travel Rule / Regulatory Reporting
# ---------------------------------------------------------------------------

_77B_ORIGINATOR_PREFIX = "/ORDERRES/"
_77B_BENEFRES_PREFIX = "/BENEFRES/"
_77B_UETR_PREFIX = "/UETR/"

# Structured 77B format used by this converter:
# Line 1: /ORDERRES/<originator name> <account or national ID>
# Line 2: /BENEFRES/<beneficiary name> <account>
# Line 3: /UETR/<message UUID>


def build_77b(payload: dict[str, Any]) -> str:
    """
    Build an MT 103 :77B: Regulatory Reporting field from an OpenKYCAML payload.

    Format (up to 3 × 35-char lines):
      /ORDERRES/<originator name> / <account or national ID>
      /BENEFRES/<beneficiary name> / <account>
      /UETR/<messageId>

    Returns
    -------
    str
        The :77B: field value (without the :77B: tag prefix).
    """
    ivms = payload.get("ivms101", {})
    originator = ivms.get("originator", {})
    beneficiary = ivms.get("beneficiary", {})

    orig_persons = originator.get("originatorPersons", [])
    bene_persons = beneficiary.get("beneficiaryPersons", [])
    orig_accounts = originator.get("accountNumber", [])
    bene_accounts = beneficiary.get("accountNumber", [])

    orig_name = _get_name_string(orig_persons[0]) if orig_persons else ""
    bene_name = _get_name_string(bene_persons[0]) if bene_persons else ""
    orig_acct = _get_account(orig_accounts)
    bene_acct = _get_account(bene_accounts)

    # Originator national ID fallback for FATF Rec. 16
    if not orig_acct and orig_persons:
        person = orig_persons[0].get("naturalPerson") or orig_persons[0].get("legalPerson") or {}
        nat_id = person.get("nationalIdentification", {})
        orig_acct = nat_id.get("nationalIdentifier", "")

    msg_id = payload.get("messageId") or str(uuid.uuid4())

    line1 = f"{_77B_ORIGINATOR_PREFIX}{orig_name[:20]}/{orig_acct[:12]}"[:35]
    line2 = f"{_77B_BENEFRES_PREFIX}{bene_name[:20]}/{bene_acct[:12]}"[:35]
    line3 = f"{_77B_UETR_PREFIX}{msg_id[:28]}"[:35]

    return f"{line1}\n{line2}\n{line3}"


def parse_77b(field_77b: str) -> dict[str, Any]:
    """
    Extract Travel Rule / KYC fields from an MT 103 :77B: free-text block.

    This is best-effort extraction. Recognises:
    - /ORDERRES/ → originator name and account
    - /BENEFRES/ → beneficiary name and account
    - /UETR/     → UETR (message ID)

    Returns
    -------
    dict
        Partial OpenKYCAML ivms101 fields extracted from the 77B.
    """
    result: dict[str, Any] = {}

    for line in field_77b.splitlines():
        line = line.strip()

        if line.startswith(_77B_ORIGINATOR_PREFIX):
            rest = line[len(_77B_ORIGINATOR_PREFIX):]
            parts = rest.split("/", 1)
            name = parts[0].strip()
            acct = parts[1].strip() if len(parts) > 1 else ""
            np_block: dict[str, Any] = {}
            if name:
                np_block["name"] = {
                    "nameIdentifier": [{"primaryIdentifier": name, "nameIdentifierType": "LEGL"}]
                }
            if acct:
                np_block["nationalIdentification"] = {
                    "nationalIdentifier": acct,
                    "nationalIdentifierType": "MISC",
                }
            result["originator_77b"] = {"naturalPerson": np_block, "_account": acct}

        elif line.startswith(_77B_BENEFRES_PREFIX):
            rest = line[len(_77B_BENEFRES_PREFIX):]
            parts = rest.split("/", 1)
            name = parts[0].strip()
            acct = parts[1].strip() if len(parts) > 1 else ""
            bene_block: dict[str, Any] = {}
            if name:
                bene_block["name"] = {
                    "nameIdentifier": [{"primaryIdentifier": name, "nameIdentifierType": "LEGL"}]
                }
            result["beneficiary_77b"] = {"naturalPerson": bene_block, "_account": acct}

        elif line.startswith(_77B_UETR_PREFIX):
            uetr = line[len(_77B_UETR_PREFIX):].strip()
            result["uetr"] = uetr

    return result


# ---------------------------------------------------------------------------
# _build_party_lines: produce SWIFT party block lines
# ---------------------------------------------------------------------------


def _build_party_lines(
    person_block: dict[str, Any],
    accounts: list[str],
    include_account: bool = True,
) -> list[str]:
    """
    Produce SWIFT party field lines:
    [/account number]
    Name line 1
    Address line 1
    Address line 2 (optional)
    """
    lines: list[str] = []
    if include_account and accounts:
        acct = accounts[0]
        lines.append(f"/{acct}"[:35])
    name = _get_name_string(person_block)
    if name:
        lines.append(name[:_MAX_NAME])
    addr_lines = _get_address_lines(person_block)
    lines.extend(addr_lines)
    return lines


def _parse_party_lines(raw: str) -> tuple[str, str, list[str]]:
    """
    Parse SWIFT party field raw value into (account, name, address_lines).
    The first line may start with '/' indicating an account number.
    """
    lines = raw.strip().splitlines()
    account = ""
    name = ""
    addr: list[str] = []
    if not lines:
        return account, name, addr
    idx = 0
    # Account line
    if lines[idx].startswith("/"):
        account = lines[idx][1:].strip()
        idx += 1
    # Name line
    if idx < len(lines):
        name = lines[idx].strip()
        idx += 1
    # Remaining = address
    addr = [ln.strip() for ln in lines[idx:] if ln.strip()]
    return account, name, addr


def _build_natural_person(name: str, account: str, addr_lines: list[str]) -> dict[str, Any]:
    """Build an IVMS 101-style naturalPerson block from MT parsed fields."""
    np: dict[str, Any] = {}
    if name:
        parts = name.rsplit(" ", 1)
        np["name"] = {
            "nameIdentifier": [
                {
                    "primaryIdentifier": parts[-1],
                    "secondaryIdentifier": parts[0] if len(parts) > 1 else "",
                    "nameIdentifierType": "LEGL",
                }
            ]
        }
    if account:
        np["nationalIdentification"] = {
            "nationalIdentifier": account,
            "nationalIdentifierType": "IBAN" if _is_iban(account) else "MISC",
        }
    if addr_lines:
        addr: dict[str, Any] = {}
        if len(addr_lines) >= 1:
            addr["streetName"] = addr_lines[0]
        if len(addr_lines) >= 2:
            addr["townName"] = addr_lines[1]
        if len(addr_lines) >= 3:
            addr["country"] = addr_lines[2][:2] if len(addr_lines[2]) == 2 else addr_lines[2]
        np["geographicAddresses"] = [addr]
    return np


def _extract_32a(value: str) -> tuple[str, str, str]:
    """
    Parse a :32A: field value: YYMMDDCCCAMOUNT
    Returns (value_date_iso, currency, amount_decimal).
    """
    if len(value) < 9:
        return _ymd_to_iso(_now_ymd()), "XXX", "0.00"
    ymd = value[:6]
    ccy = value[6:9].upper()
    amount_swift = value[9:]
    return _ymd_to_iso(ymd), ccy, _parse_amount(amount_swift)


def _build_32a(value_date: str, ccy: str, amount: str) -> str:
    """Build :32A: field value: YYMMDDCCCAMOUNT."""
    ymd = _iso_to_ymd(value_date) if value_date else _now_ymd()
    fiat_ccy = ccy if _is_fiat(ccy) else "XXX"
    return f"{ymd}{fiat_ccy}{_format_amount(amount, fiat_ccy)}"


def _extract_32b(value: str) -> tuple[str, str]:
    """
    Parse a :32B: field (MT 202 / MT 910): CCCAMOUNT
    Returns (currency, amount_decimal).
    """
    if len(value) < 4:
        return "XXX", "0.00"
    ccy = value[:3].upper()
    amount_swift = value[3:]
    return ccy, _parse_amount(amount_swift)


def _build_32b(ccy: str, amount: str) -> str:
    """Build :32B: field value: CCCAMOUNT."""
    fiat_ccy = ccy if _is_fiat(ccy) else "XXX"
    return f"{fiat_ccy}{_format_amount(amount, fiat_ccy)}"


# ---------------------------------------------------------------------------
# MT 103 Producer
# ---------------------------------------------------------------------------


def openkycaml_to_mt103(
    payload: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> str:
    """
    Produce a SWIFT MT 103 Customer Credit Transfer from an OpenKYCAML payload.

    Parameters
    ----------
    payload : dict
        OpenKYCAML envelope containing an ``ivms101`` block.
    config : dict, optional
        Override values. Supported keys:
          - ``value_date``         ISO 8601 date (default: today UTC)
          - ``charge_bearer``      SWIFT charge code: SHA/OUR/BEN (default: SHA)
          - ``details_of_charges`` :71A: code (default: SHA)
          - ``bank_operation_code`` :23B: code (default: CRED)
          - ``include_77b``        bool, include :77B: Travel Rule field (default: True)
          - ``remittance_info``    str, :70: Remittance Information

    Returns
    -------
    str
        SWIFT MT 103 message text (plain FIN format, no SWIFT block headers).

    Raises
    ------
    ValueError
        If the payload does not contain an ``ivms101`` block.
    """
    cfg = config or {}
    ivms = payload.get("ivms101")
    if not ivms:
        raise ValueError("No 'ivms101' block found in payload. Cannot produce MT 103.")

    msg_id = payload.get("messageId") or str(uuid.uuid4())
    ref = _short_ref(msg_id)

    originator = ivms.get("originator", {})
    beneficiary = ivms.get("beneficiary", {})
    orig_persons = originator.get("originatorPersons", [])
    bene_persons = beneficiary.get("beneficiaryPersons", [])
    orig_accounts = originator.get("accountNumber", [])
    bene_accounts = beneficiary.get("accountNumber", [])
    amount_info = ivms.get("transferredAmount", {})
    asset_type = amount_info.get("assetType", "XXX")
    amount_value = amount_info.get("amount", "0")
    ccy = asset_type if _is_fiat(asset_type) else "XXX"

    orig_vasp = ivms.get("originatingVASP", {})
    bene_vasp = ivms.get("beneficiaryVASP", {})

    value_date = cfg.get("value_date") or (payload.get("messageDateTime") or _now_iso())[:10]
    bank_op_code = cfg.get("bank_operation_code", "CRED")
    details_of_charges = cfg.get("details_of_charges", "SHA")

    lines: list[str] = []
    lines.append(f":20:{ref}")
    lines.append(f":23B:{bank_op_code}")
    lines.append(f":32A:{_build_32a(value_date, ccy, amount_value)}")

    # :50K: Ordering Customer (Originator)
    if orig_persons:
        party_lines = _build_party_lines(orig_persons[0], orig_accounts)
        if party_lines:
            lines.append(":50K:" + "\n".join(party_lines))
    elif orig_accounts:
        lines.append(f":50K:/{orig_accounts[0][:34]}")

    # :52A: Ordering Institution (Originating VASP)
    if orig_vasp:
        agt = _get_bic_or_lei(orig_vasp)
        if agt:
            lines.append(f":52A:{agt}")

    # :56A: Intermediary Institution (transfer path first element)
    transfer_path = ivms.get("transferPath", [])
    if transfer_path:
        agt = _get_bic_or_lei(transfer_path[0])
        if agt:
            lines.append(f":56A:{agt}")

    # :57A: Account With Institution (Beneficiary VASP)
    if bene_vasp:
        agt = _get_bic_or_lei(bene_vasp)
        if agt:
            lines.append(f":57A:{agt}")

    # :59: Beneficiary Customer
    if bene_persons:
        party_lines = _build_party_lines(bene_persons[0], bene_accounts)
        if party_lines:
            lines.append(":59:" + "\n".join(party_lines))
    elif bene_accounts:
        lines.append(f":59:/{bene_accounts[0][:34]}")

    # :70: Remittance Information
    rmt_info = cfg.get("remittance_info")
    if not rmt_info:
        kyc = payload.get("kycProfile", {})
        rmt_info = kyc.get("relationshipPurpose") or kyc.get("customerId", "")
    if rmt_info:
        lines.append(f":70:{rmt_info[:_MAX_70]}")

    # :71A: Details of Charges
    lines.append(f":71A:{details_of_charges}")

    # :77B: Regulatory Reporting (Travel Rule)
    if cfg.get("include_77b", True):
        field_77b = build_77b(payload)
        if field_77b.strip():
            lines.append(f":77B:{field_77b}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MT 202 Producer
# ---------------------------------------------------------------------------


def openkycaml_to_mt202(
    payload: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> str:
    """
    Produce a SWIFT MT 202 General Financial Institution Transfer from an
    OpenKYCAML payload.

    The MT 202 carries interbank transfers. Originator/beneficiary VASP
    identifiers map to :52A: (Ordering Institution) and :58A: (Beneficiary
    Institution). The amount is in :32A: or :32B:.

    Raises
    ------
    ValueError
        If the payload does not contain an ``ivms101`` block.
    """
    cfg = config or {}
    ivms = payload.get("ivms101")
    if not ivms:
        raise ValueError("No 'ivms101' block found in payload. Cannot produce MT 202.")

    msg_id = payload.get("messageId") or str(uuid.uuid4())
    ref = _short_ref(msg_id)
    related_ref = cfg.get("related_reference", "NONREF")[:16]

    amount_info = ivms.get("transferredAmount", {})
    asset_type = amount_info.get("assetType", "XXX")
    amount_value = amount_info.get("amount", "0")
    ccy = asset_type if _is_fiat(asset_type) else "XXX"
    value_date = cfg.get("value_date") or (payload.get("messageDateTime") or _now_iso())[:10]

    orig_vasp = ivms.get("originatingVASP", {})
    bene_vasp = ivms.get("beneficiaryVASP", {})
    transfer_path = ivms.get("transferPath", [])

    lines: list[str] = []
    lines.append(f":20:{ref}")
    lines.append(f":21:{related_ref}")
    lines.append(f":32A:{_build_32a(value_date, ccy, amount_value)}")

    # :52A: Ordering Institution (originating VASP)
    if orig_vasp:
        agt = _get_bic_or_lei(orig_vasp)
        if agt:
            lines.append(f":52A:{agt}")

    # :56A: Intermediary Institution
    if transfer_path:
        agt = _get_bic_or_lei(transfer_path[0])
        if agt:
            lines.append(f":56A:{agt}")

    # :58A: Beneficiary Institution
    if bene_vasp:
        agt = _get_bic_or_lei(bene_vasp)
        if agt:
            lines.append(f":58A:{agt}")

    # :72: Sender to Receiver Information
    s2r = cfg.get("sender_to_receiver")
    if s2r:
        lines.append(f":72:{s2r[:35]}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MT 202 COV Producer
# ---------------------------------------------------------------------------


def openkycaml_to_mt202cov(
    payload: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> str:
    """
    Produce a SWIFT MT 202 COV Covered Financial Institution Transfer.

    The COV variant includes an underlying customer credit transfer reference
    and originator/beneficiary customer info (for FATF Rec. 16 Travel Rule
    compliance in covered transfers).

    Raises
    ------
    ValueError
        If the payload does not contain an ``ivms101`` block.
    """
    cfg = config or {}
    ivms = payload.get("ivms101")
    if not ivms:
        raise ValueError("No 'ivms101' block found in payload. Cannot produce MT 202 COV.")

    msg_id = payload.get("messageId") or str(uuid.uuid4())
    ref = _short_ref(msg_id)
    related_ref = cfg.get("related_reference", "NONREF")[:16]

    amount_info = ivms.get("transferredAmount", {})
    asset_type = amount_info.get("assetType", "XXX")
    amount_value = amount_info.get("amount", "0")
    ccy = asset_type if _is_fiat(asset_type) else "XXX"
    value_date = cfg.get("value_date") or (payload.get("messageDateTime") or _now_iso())[:10]

    originator = ivms.get("originator", {})
    beneficiary = ivms.get("beneficiary", {})
    orig_persons = originator.get("originatorPersons", [])
    bene_persons = beneficiary.get("beneficiaryPersons", [])
    orig_accounts = originator.get("accountNumber", [])
    bene_accounts = beneficiary.get("accountNumber", [])
    orig_vasp = ivms.get("originatingVASP", {})
    bene_vasp = ivms.get("beneficiaryVASP", {})
    transfer_path = ivms.get("transferPath", [])

    lines: list[str] = []
    lines.append(f":20:{ref}")
    lines.append(f":21:{related_ref}")
    lines.append(":23B:CRED")
    lines.append(f":32A:{_build_32a(value_date, ccy, amount_value)}")

    # :52A: Ordering Institution
    if orig_vasp:
        agt = _get_bic_or_lei(orig_vasp)
        if agt:
            lines.append(f":52A:{agt}")

    # :56A: Intermediary
    if transfer_path:
        agt = _get_bic_or_lei(transfer_path[0])
        if agt:
            lines.append(f":56A:{agt}")

    # :58A: Beneficiary Institution
    if bene_vasp:
        agt = _get_bic_or_lei(bene_vasp)
        if agt:
            lines.append(f":58A:{agt}")

    # :50A: Underlying Originator (customer info — COV-specific)
    if orig_persons:
        party_lines = _build_party_lines(orig_persons[0], orig_accounts)
        if party_lines:
            lines.append(":50A:" + "\n".join(party_lines))

    # :59: Underlying Beneficiary (customer info — COV-specific)
    if bene_persons:
        party_lines = _build_party_lines(bene_persons[0], bene_accounts)
        if party_lines:
            lines.append(":59:" + "\n".join(party_lines))

    # :72: Sender to Receiver with COV indicator
    s2r = cfg.get("sender_to_receiver", "/COV/")
    lines.append(f":72:{s2r[:35]}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MT 910 Producer
# ---------------------------------------------------------------------------


def openkycaml_to_mt910(
    payload: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> str:
    """
    Produce a SWIFT MT 910 Confirmation of Credit.

    MT 910 is a debit/credit confirmation sent by a bank to its customer
    upon receipt of funds. Used for audit trail purposes.

    Raises
    ------
    ValueError
        If the payload does not contain an ``ivms101`` block.
    """
    cfg = config or {}
    ivms = payload.get("ivms101")
    if not ivms:
        raise ValueError("No 'ivms101' block found in payload. Cannot produce MT 910.")

    msg_id = payload.get("messageId") or str(uuid.uuid4())
    ref = _short_ref(msg_id)

    amount_info = ivms.get("transferredAmount", {})
    asset_type = amount_info.get("assetType", "XXX")
    amount_value = amount_info.get("amount", "0")
    ccy = asset_type if _is_fiat(asset_type) else "XXX"
    value_date = cfg.get("value_date") or (payload.get("messageDateTime") or _now_iso())[:10]

    originator = ivms.get("originator", {})
    orig_persons = originator.get("originatorPersons", [])
    orig_vasp = ivms.get("originatingVASP", {})

    lines: list[str] = []
    lines.append(f":20:{ref}")
    lines.append(f":25:{cfg.get('account_id', 'NOSTRO')[:35]}")
    lines.append(f":32A:{_build_32a(value_date, ccy, amount_value)}")

    # :50: Ordering Customer
    if orig_persons:
        name = _get_name_string(orig_persons[0])
        if name:
            lines.append(f":50:{name[:_MAX_NAME]}")
    elif orig_vasp.get("name"):
        lines.append(f":50:{orig_vasp['name'][:_MAX_NAME]}")

    # :52A: Ordering Institution
    if orig_vasp:
        agt = _get_bic_or_lei(orig_vasp)
        if agt:
            lines.append(f":52A:{agt}")

    # :72: Sender to Receiver
    s2r = cfg.get("sender_to_receiver")
    if s2r:
        lines.append(f":72:{s2r[:35]}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MT 940 Producer
# ---------------------------------------------------------------------------


def openkycaml_to_mt940(
    payload: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> str:
    """
    Produce a SWIFT MT 940 Customer Statement Message.

    MT 940 is a customer statement sent by a bank. A single OpenKYCAML
    transfer payload is represented as a single statement entry with a
    credit (C) booking entry.

    Raises
    ------
    ValueError
        If the payload does not contain an ``ivms101`` block.
    """
    cfg = config or {}
    ivms = payload.get("ivms101")
    if not ivms:
        raise ValueError("No 'ivms101' block found in payload. Cannot produce MT 940.")

    msg_id = payload.get("messageId") or str(uuid.uuid4())
    ref = _short_ref(msg_id)

    amount_info = ivms.get("transferredAmount", {})
    asset_type = amount_info.get("assetType", "XXX")
    amount_value = amount_info.get("amount", "0")
    ccy = asset_type if _is_fiat(asset_type) else "XXX"
    value_date = cfg.get("value_date") or (payload.get("messageDateTime") or _now_iso())[:10]
    entry_date_str = _iso_to_ymd(value_date)[2:]  # MMDD portion for :61:
    value_ymd = _iso_to_ymd(value_date)

    formatted_amount = _format_amount(amount_value, ccy)
    # :60F: Opening Balance — default to zero if not provided
    opening_balance = cfg.get("opening_balance", "0,00")
    opening_ccy = cfg.get("opening_balance_currency", ccy)

    lines: list[str] = []
    lines.append(f":20:{ref}")
    lines.append(f":25:{cfg.get('account_id', 'NOSTRO')[:35]}")
    lines.append(f":28C:{cfg.get('statement_number', '00001/001')[:10]}")

    # :60F: Opening Balance
    lines.append(f":60F:C{value_ymd}{opening_ccy}{opening_balance}")

    # :61: Statement Line (single credit entry)
    # Format: YYMMDD[MMDD]DCccy,amount<SWIFT-code>ref
    debit_credit = "C"  # Credit
    fund_code = ccy if len(ccy) == 3 else "XXX"
    lines.append(
        f":61:{value_ymd}{entry_date_str}{debit_credit}"
        f"{fund_code}{formatted_amount}NTRF{ref[:16]}"
    )

    # :86: Information to Account Owner (narrative reference)
    originator = ivms.get("originator", {})
    orig_persons = originator.get("originatorPersons", [])
    orig_name = _get_name_string(orig_persons[0]) if orig_persons else ""
    info_line = f"FROM {orig_name[:28]}" if orig_name else f"TXN {msg_id[:30]}"
    lines.append(f":86:{info_line[:65]}")

    # :62F: Closing Balance
    try:
        closing = float(opening_balance.replace(",", ".")) + float(
            amount_value.replace(",", ".") if "," in amount_value else amount_value
        )
        closing_str = _format_amount(str(closing), ccy)
    except ValueError:
        closing_str = formatted_amount
    lines.append(f":62F:C{value_ymd}{ccy}{closing_str}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MT → OpenKYCAML (all message types)
# ---------------------------------------------------------------------------


def mt_to_openkycaml(mt_text: str) -> dict[str, Any]:
    """
    Parse a SWIFT MT message and reconstruct an OpenKYCAML payload.

    Supports MT 103, MT 202, MT 202 COV, MT 910, and MT 940.

    Parameters
    ----------
    mt_text : str
        Raw SWIFT FIN message text (with or without block headers).

    Returns
    -------
    dict
        An OpenKYCAML-compatible payload reconstructed from the MT fields.

    Notes
    -----
    - Best-effort parsing: fields present in the MT are mapped; fields absent
      are omitted.
    - MT 940 does not carry full party identity; only the statement entry and
      booking info are extracted.
    - :77B: is parsed for Travel Rule / regulatory data and merged into the
      ivms101 block, with the 77B-extracted data taking precedence over fields
      where it provides more detail.
    """
    fields = _split_mt_fields(mt_text)

    # Detect message type from :23B: or field pattern
    is_940 = "28C" in fields and "62F" in fields
    is_910 = "32A" in fields and "50" in fields and "23B" not in fields and "59" not in fields
    is_202 = "58A" in fields or "58D" in fields
    is_202cov = is_202 and ("50A" in fields or ("50" in fields and "59" in fields))
    is_103 = "23B" in fields and "59" in fields

    # Common fields
    msg_ref = (fields.get("20") or [""])[0].strip()
    related_ref = (fields.get("21") or [""])[0].strip()

    # :32A: or :32B: — amount and value date
    field_32a = (fields.get("32A") or [""])[0].strip()
    field_32b = (fields.get("32B") or [""])[0].strip()
    value_date_iso = ""
    ccy = "XXX"
    amount_str = "0.00"
    if field_32a:
        value_date_iso, ccy, amount_str = _extract_32a(field_32a)
    elif field_32b:
        ccy, amount_str = _extract_32b(field_32b)

    # Party fields
    field_50k = (fields.get("50K") or fields.get("50A") or fields.get("50") or [""])[0]
    field_59 = (fields.get("59") or fields.get("59A") or [""])[0]
    field_52a = (fields.get("52A") or fields.get("52D") or [""])[0].strip()
    field_57a = (fields.get("57A") or fields.get("57D") or [""])[0].strip()
    field_58a = (fields.get("58A") or fields.get("58D") or [""])[0].strip()
    field_56a = (fields.get("56A") or fields.get("56D") or [""])[0].strip()
    field_70 = (fields.get("70") or [""])[0].strip()
    field_71a = (fields.get("71A") or [""])[0].strip()
    field_77b = (fields.get("77B") or [""])[0].strip()
    field_72 = (fields.get("72") or [""])[0].strip()
    field_25 = (fields.get("25") or [""])[0].strip()  # MT 910/940 account

    # Parse originator (50K / 50A)
    orig_person: dict[str, Any] = {}
    orig_account: list[str] = []
    if field_50k.strip():
        acct, name, addr = _parse_party_lines(field_50k)
        np = _build_natural_person(name, acct if not _is_iban(acct) else "", addr)
        orig_person = {"naturalPerson": np}
        if acct and (_is_iban(acct) or acct):
            orig_account = [acct]

    # Parse beneficiary (59 / 59A)
    bene_person: dict[str, Any] = {}
    bene_account: list[str] = []
    if field_59.strip():
        acct, name, addr = _parse_party_lines(field_59)
        np = _build_natural_person(name, acct if not _is_iban(acct) else "", addr)
        bene_person = {"naturalPerson": np}
        if acct:
            bene_account = [acct]

    # Parse VASP agents
    orig_vasp: dict[str, Any] = {}
    bene_vasp: dict[str, Any] = {}
    if field_52a:
        orig_vasp = {"name": field_52a[:_MAX_NAME]}
    if field_57a or field_58a:
        bene_vasp = {"name": (field_57a or field_58a)[:_MAX_NAME]}

    # Merge :77B: data
    travel_rule: dict[str, Any] = {}
    if field_77b:
        travel_rule = parse_77b(field_77b)

        orig_77b = travel_rule.get("originator_77b")
        bene_77b = travel_rule.get("beneficiary_77b")

        if orig_77b:
            np_77b = orig_77b.get("naturalPerson", {})
            acct_77b = orig_77b.get("_account", "")
            if not orig_person and np_77b:
                orig_person = {"naturalPerson": np_77b}
            elif orig_person and np_77b.get("name"):
                # Enrich name from 77B if the 50K name was empty
                existing_np = orig_person.get("naturalPerson", {})
                if not existing_np.get("name") and np_77b.get("name"):
                    existing_np["name"] = np_77b["name"]
            if acct_77b and not orig_account:
                orig_account = [acct_77b]

        if bene_77b:
            np_77b = bene_77b.get("naturalPerson", {})
            acct_77b = bene_77b.get("_account", "")
            if not bene_person and np_77b:
                bene_person = {"naturalPerson": np_77b}
            if acct_77b and not bene_account:
                bene_account = [acct_77b]

    # MT 940: extract booking entry from :61:
    field_61 = (fields.get("61") or [""])[0].strip()
    if is_940 and field_61 and not amount_str or amount_str == "0.00":
        # Parse :61: YYMMDD[MMDD]DCccy,amount<fundcode><ref>
        m = re.match(r"(\d{6})(\d{4})?([CD])([A-Z]{3})([\d,]+)", field_61)
        if m:
            value_date_iso = _ymd_to_iso(m.group(1))
            ccy = m.group(4)
            amount_str = _parse_amount(m.group(5))

    # Assemble the OpenKYCAML payload
    msg_id = msg_ref or str(uuid.uuid4())
    msg_dt = value_date_iso + "T00:00:00Z" if value_date_iso else _now_iso()

    result: dict[str, Any] = {
        "$schema": _SCHEMA_URL,
        "version": _VERSION,
        "messageId": msg_id,
        "messageDateTime": msg_dt,
    }

    ivms_block: dict[str, Any] = {}

    if orig_person or orig_account:
        orig_block: dict[str, Any] = {}
        if orig_person:
            orig_block["originatorPersons"] = [orig_person]
        if orig_account:
            orig_block["accountNumber"] = orig_account
        ivms_block["originator"] = orig_block

    if bene_person or bene_account:
        bene_block: dict[str, Any] = {}
        if bene_person:
            bene_block["beneficiaryPersons"] = [bene_person]
        if bene_account:
            bene_block["accountNumber"] = bene_account
        ivms_block["beneficiary"] = bene_block

    if orig_vasp:
        ivms_block["originatingVASP"] = orig_vasp
    if bene_vasp:
        ivms_block["beneficiaryVASP"] = bene_vasp

    if amount_str and amount_str != "0.00":
        ivms_block["transferredAmount"] = {
            "amount": amount_str,
            "assetType": ccy,
        }

    if ivms_block:
        result["ivms101"] = ivms_block

    # Populate metadata from MT fields
    meta: dict[str, Any] = {}
    if field_70:
        meta["remittanceInfo"] = field_70
    if field_71a:
        meta["chargeBearer"] = field_71a
    if related_ref and related_ref not in ("NONREF", ""):
        meta["relatedReference"] = related_ref
    if field_72:
        meta["senderToReceiver"] = field_72
    if field_77b:
        meta["field77B"] = field_77b
    if travel_rule.get("uetr"):
        meta["uetr"] = travel_rule["uetr"]
    if field_25:
        meta["accountId"] = field_25

    # Message type tag for traceability
    if is_940:
        meta["mtMessageType"] = "MT940"
    elif is_910:
        meta["mtMessageType"] = "MT910"
    elif is_202cov:
        meta["mtMessageType"] = "MT202COV"
    elif is_202:
        meta["mtMessageType"] = "MT202"
    elif is_103:
        meta["mtMessageType"] = "MT103"
    else:
        meta["mtMessageType"] = "UNKNOWN"

    if meta:
        result["_swiftMtMetadata"] = meta

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import sys

    _COMMANDS = [
        "openkycaml-to-mt103",
        "openkycaml-to-mt202",
        "openkycaml-to-mt202cov",
        "openkycaml-to-mt910",
        "openkycaml-to-mt940",
        "mt-to-openkycaml",
    ]

    cli = argparse.ArgumentParser(
        description="OpenKYCAML ↔ SWIFT MT converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(f"  {c} <input_file> [--out output]" for c in _COMMANDS),
    )
    cli.add_argument("command", choices=_COMMANDS)
    cli.add_argument("input_file")
    cli.add_argument("--out", help="Output file (default: stdout)")
    args = cli.parse_args()

    with open(args.input_file, encoding="utf-8") as fh:
        raw = fh.read()

    dispatch = {
        "openkycaml-to-mt103": lambda: openkycaml_to_mt103(json.loads(raw)),
        "openkycaml-to-mt202": lambda: openkycaml_to_mt202(json.loads(raw)),
        "openkycaml-to-mt202cov": lambda: openkycaml_to_mt202cov(json.loads(raw)),
        "openkycaml-to-mt910": lambda: openkycaml_to_mt910(json.loads(raw)),
        "openkycaml-to-mt940": lambda: openkycaml_to_mt940(json.loads(raw)),
        "mt-to-openkycaml": lambda: json.dumps(mt_to_openkycaml(raw), indent=2, ensure_ascii=False),
    }

    result_str = dispatch[args.command]()

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(result_str)
        print(f"Written to {args.out}", file=sys.stderr)
    else:
        print(result_str)
