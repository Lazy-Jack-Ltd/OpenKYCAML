#!/usr/bin/env python3
"""
OpenKYCAML × ISO 20022 Converter
=================================
Bidirectional converter between OpenKYCAML v1.3.0 payloads and ISO 20022
XML messages (pacs.008, pain.001).

Functions
---------
openkycaml_to_pacs008(payload, message_config=None) -> str
    Convert an OpenKYCAML payload to a pacs.008 FIToFICstmrCdtTrf XML string.

openkycaml_to_pain001(payload, message_config=None) -> str
    Convert an OpenKYCAML payload to a pain.001 CstmrCdtTrfInitn XML string.

iso20022_to_openkycaml(xml_string) -> dict
    Parse an ISO 20022 XML string and extract OpenKYCAML fields, including
    any KYCAMLEnvelope embedded in <SplmtryData>.

Dependencies
------------
- Python standard library only (xml.etree.ElementTree, json, re, uuid, datetime)
- Optional: jsonschema>=4.0 for envelope validation

Usage
-----
    from converter import openkycaml_to_pacs008, openkycaml_to_pain001, iso20022_to_openkycaml

    with open("examples/minimal-travel-rule.json") as f:
        payload = json.load(f)

    xml = openkycaml_to_pacs008(payload)
    print(xml)
"""

from __future__ import annotations

import html
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PACS008_NS = "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10"
PAIN001_NS = "urn:iso:std:iso:20022:tech:xsd:pain.001.001.11"
SPLMTRY_DATA_PLACE_AND_NAME = "OpenKYCAML/KYCAMLEnvelope/1.0"
ENVELOPE_VERSION = "1.0.0"

# IBAN pattern (basic structural check)
_IBAN_RE = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$")

# ISO 4217 fiat currency codes (non-exhaustive — covers common cases)
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


def _pretty_xml(element: Element) -> str:
    """Return a pretty-printed UTF-8 XML string from an Element.
    
    JSON content in <Envlp> elements is preserved using CDATA sections
    to avoid XML character escaping of the JSON payload.
    """
    raw = tostring(element, encoding="unicode", xml_declaration=False)
    dom = parseString(f'<?xml version="1.0" encoding="UTF-8"?>{raw}')
    pretty = dom.toprettyxml(indent="  ", encoding=None)
    # Wrap Envlp text content in CDATA to avoid &quot; escaping of the JSON
    pretty = re.sub(
        r"<Envlp>(.*?)</Envlp>",
        lambda m: f"<Envlp><![CDATA[{html.unescape(m.group(1))}]]></Envlp>",
        pretty,
        flags=re.DOTALL,
    )
    return pretty


def _is_iban(value: str) -> bool:
    return bool(_IBAN_RE.match(value.upper()))


def _is_iso4217(code: str) -> bool:
    return code.upper() in _ISO4217_CODES


def _get_name_string(person_block: dict[str, Any]) -> str:
    """Extract a display name string from an IVMS 101 person block."""
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


def _get_lei(person_block: dict[str, Any]) -> str | None:
    """Extract LEI from an IVMS 101 person block if nationalIdentifierType is LEIX."""
    person = person_block.get("naturalPerson") or person_block.get("legalPerson") or {}
    nat_id = person.get("nationalIdentification", {})
    if nat_id.get("nationalIdentifierType") == "LEIX":
        return nat_id.get("nationalIdentifier")
    return None


def _add_postal_address(parent: Element, addresses: list[dict[str, Any]]) -> None:
    """Add <PstlAdr> child to parent from an IVMS 101 geographicAddresses list."""
    if not addresses:
        return
    addr = addresses[0]
    pstl = SubElement(parent, "PstlAdr")
    if addr.get("streetName"):
        SubElement(pstl, "StrtNm").text = addr["streetName"]
    if addr.get("buildingNumber"):
        SubElement(pstl, "BldgNb").text = addr["buildingNumber"]
    if addr.get("postCode"):
        SubElement(pstl, "PstCd").text = addr["postCode"]
    if addr.get("townName"):
        SubElement(pstl, "TwnNm").text = addr["townName"]
    # Unstructured fallback
    for line in addr.get("addressLine", []):
        SubElement(pstl, "AdrLine").text = line
    if addr.get("country"):
        SubElement(pstl, "Ctry").text = addr["country"]


def _add_party_id(parent: Element, person_block: dict[str, Any]) -> None:
    """Add <Id> child to parent from an IVMS 101 person block."""
    person = person_block.get("naturalPerson") or person_block.get("legalPerson") or {}
    nat_id = person.get("nationalIdentification", {})
    nat_id_type = nat_id.get("nationalIdentifierType")
    nat_id_value = nat_id.get("nationalIdentifier")

    id_el = SubElement(parent, "Id")

    if nat_id_type == "LEIX" and nat_id_value:
        org = SubElement(id_el, "OrgId")
        SubElement(org, "LEI").text = nat_id_value
    elif "naturalPerson" in person_block:
        prv = SubElement(id_el, "PrvtId")
        np = person_block["naturalPerson"]
        dob = np.get("dateAndPlaceOfBirth", {})
        if dob.get("dateOfBirth"):
            dob_el = SubElement(prv, "DtAndPlcOfBirth")
            SubElement(dob_el, "BirthDt").text = dob["dateOfBirth"]
            SubElement(dob_el, "CityOfBirth").text = dob.get("placeOfBirth") or "UNKNOWN"
            SubElement(dob_el, "CtryOfBirth").text = dob.get("countryOfBirth") or "XX"
        if nat_id_value and nat_id_type:
            othr = SubElement(prv, "Othr")
            SubElement(othr, "Id").text = nat_id_value
            schme = SubElement(othr, "SchmeNm")
            SubElement(schme, "Prtry").text = nat_id_type
    elif nat_id_value:
        org = SubElement(id_el, "OrgId")
        othr = SubElement(org, "Othr")
        SubElement(othr, "Id").text = nat_id_value
        if nat_id_type:
            schme = SubElement(othr, "SchmeNm")
            SubElement(schme, "Prtry").text = nat_id_type


def _add_account(parent: Element, account_numbers: list[str], asset_type: str = "") -> None:
    """Add account identifier elements to parent."""
    if not account_numbers:
        return
    acct_id = SubElement(parent, "Id")
    acct_no = account_numbers[0]
    if _is_iban(acct_no):
        SubElement(acct_id, "IBAN").text = acct_no.upper()
    else:
        othr = SubElement(acct_id, "Othr")
        SubElement(othr, "Id").text = acct_no
        if asset_type and not _is_iso4217(asset_type):
            schme = SubElement(othr, "SchmeNm")
            SubElement(schme, "Prtry").text = asset_type


def _build_kyc_aml_envelope(
    payload: dict[str, Any],
    message_ref: str,
) -> str:
    """Build the KYCAMLEnvelope JSON string from an OpenKYCAML payload."""
    envelope: dict[str, Any] = {
        "envelopeVersion": ENVELOPE_VERSION,
        "messageRef": message_ref,
        "openKycAmlVersion": payload.get("version", "1.3.0"),
    }

    kyc = payload.get("kycProfile")
    if kyc:
        envelope["kycProfile"] = kyc

    # Build screeningResults from kycProfile sub-blocks
    screening: dict[str, Any] = {}
    if kyc:
        sanctions = kyc.get("sanctionsScreening")
        if sanctions:
            screening["sanctionsScreening"] = {
                "result": sanctions.get("result") or sanctions.get("screeningResult", "NOT_SCREENED"),
                "screeningDate": sanctions.get("screeningDate") or sanctions.get("lastScreenedDate", ""),
                "listsScreened": sanctions.get("listsScreened", []),
                "hitDetails": sanctions.get("hitDetails"),
            }
        pep = kyc.get("pepStatus")
        if pep:
            screening["pepScreening"] = {
                "isPEP": pep.get("isPEP", False),
                "pepCategory": pep.get("pepCategory"),
                "pepRole": pep.get("pepRole"),
                "screeningDate": pep.get("pepScreeningDate", ""),
            }
        adverse = kyc.get("adverseMedia")
        if adverse:
            screening["adverseMediaScreening"] = {
                "result": adverse.get("result", "NOT_SCREENED"),
                "screeningDate": adverse.get("screeningDate", ""),
                "hitSummary": adverse.get("hitSummary"),
            }
    if screening:
        envelope["screeningResults"] = screening

    # Consent record
    if kyc and kyc.get("consentRecord"):
        envelope["consentRecord"] = kyc["consentRecord"]

    # VC proofs
    vc = payload.get("verifiableCredential", {})
    vc_proofs: list[dict[str, Any]] = []
    if vc:
        evidence_list = vc.get("evidence", [])
        proof = vc.get("proof", {})
        for ev in evidence_list:
            entry: dict[str, Any] = {
                "issuerDid": ev.get("credentialIssuer", ""),
                "subjectDid": (vc.get("credentialSubject") or {}).get("id", ""),
                "verifierDid": ev.get("verifier", ""),
                "credentialType": ev.get("type", []),
                "presentationMethod": ev.get("presentationMethod", ""),
                "presentationDate": ev.get("presentationDate", ""),
                "proofType": proof.get("type", ""),
                "verificationMethod": proof.get("verificationMethod", ""),
                "proofValue": proof.get("proofValue") or proof.get("jws"),
            }
            vc_proofs.append(entry)
    envelope["vcProofs"] = vc_proofs

    # GDPR sensitivity metadata
    gdpr = payload.get("gdprSensitivityMetadata")
    if gdpr:
        envelope["gdprSensitivityMetadata"] = gdpr

    return json.dumps(envelope, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# openkycaml_to_pacs008
# ---------------------------------------------------------------------------


def openkycaml_to_pacs008(
    payload: dict[str, Any],
    message_config: dict[str, Any] | None = None,
) -> str:
    """
    Convert an OpenKYCAML payload to an ISO 20022 pacs.008 XML string.

    The KYC/AML envelope is embedded in <SplmtryData> using the
    OpenKYCAML/KYCAMLEnvelope/1.0 discriminator.

    Parameters
    ----------
    payload : dict
        A valid OpenKYCAML envelope (must contain an ``ivms101`` block).
    message_config : dict, optional
        Override values. Supported keys:
          - ``settlement_method`` (str, default "CLRG")
          - ``charge_bearer`` (str, default "SHAR")
          - ``interbank_settlement_date`` (str ISO 8601 date)

    Returns
    -------
    str
        A UTF-8 XML string representing the pacs.008 message.

    Raises
    ------
    ValueError
        If the payload does not contain an ``ivms101`` block.
    """
    cfg = message_config or {}
    ivms = payload.get("ivms101")
    if not ivms:
        raise ValueError("No 'ivms101' block found. Cannot produce pacs.008.")

    msg_id = payload.get("messageId") or str(uuid.uuid4())
    msg_dt = payload.get("messageDateTime") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    originator = ivms.get("originator", {})
    beneficiary = ivms.get("beneficiary", {})
    orig_persons = originator.get("originatorPersons", [])
    bene_persons = beneficiary.get("beneficiaryPersons", [])
    orig_accounts = originator.get("accountNumber", [])
    bene_accounts = beneficiary.get("accountNumber", [])
    amount_info = ivms.get("transferredAmount", {})
    asset_type = amount_info.get("assetType", "XXX")
    amount_value = amount_info.get("amount", "0")
    ccy = asset_type if _is_iso4217(asset_type) else "XXX"

    originating_vasp = ivms.get("originatingVASP", {})
    beneficiary_vasp = ivms.get("beneficiaryVASP", {})

    # Root element
    doc = Element("Document", attrib={"xmlns": PACS008_NS})
    fi_to_fi = SubElement(doc, "FIToFICstmrCdtTrf")

    # Group Header
    grp_hdr = SubElement(fi_to_fi, "GrpHdr")
    SubElement(grp_hdr, "MsgId").text = msg_id[:35]
    SubElement(grp_hdr, "CreDtTm").text = msg_dt
    SubElement(grp_hdr, "NbOfTxs").text = "1"
    sttlm_inf = SubElement(grp_hdr, "SttlmInf")
    SubElement(sttlm_inf, "SttlmMtd").text = cfg.get("settlement_method", "CLRG")

    # InstgAgt (originating VASP)
    if originating_vasp:
        instg_agt = SubElement(grp_hdr, "InstgAgt")
        fin = SubElement(instg_agt, "FinInstnId")
        if originating_vasp.get("lei"):
            SubElement(fin, "LEI").text = originating_vasp["lei"]
        if originating_vasp.get("name"):
            SubElement(fin, "Nm").text = originating_vasp["name"][:140]

    # InstdAgt (beneficiary VASP)
    if beneficiary_vasp:
        instd_agt = SubElement(grp_hdr, "InstdAgt")
        fin = SubElement(instd_agt, "FinInstnId")
        if beneficiary_vasp.get("lei"):
            SubElement(fin, "LEI").text = beneficiary_vasp["lei"]
        if beneficiary_vasp.get("name"):
            SubElement(fin, "Nm").text = beneficiary_vasp["name"][:140]

    # Credit Transfer Transaction Information
    cdt_trf = SubElement(fi_to_fi, "CdtTrfTxInf")

    pmt_id = SubElement(cdt_trf, "PmtId")
    SubElement(pmt_id, "EndToEndId").text = msg_id[:35]
    SubElement(pmt_id, "TxId").text = (ivms.get("payloadMetadata") or {}).get(
        "transactionIdentifier", msg_id
    )[:35]

    # Amount
    SubElement(cdt_trf, "IntrBkSttlmAmt", attrib={"Ccy": ccy}).text = amount_value
    sttlm_date = cfg.get("interbank_settlement_date", msg_dt[:10])
    SubElement(cdt_trf, "IntrBkSttlmDt").text = sttlm_date
    SubElement(cdt_trf, "ChrgBr").text = cfg.get("charge_bearer", "SHAR")

    # Debtor
    if orig_persons:
        op = orig_persons[0]
        dbtr = SubElement(cdt_trf, "Dbtr")
        name = _get_name_string(op)
        if name:
            SubElement(dbtr, "Nm").text = name[:140]
        _add_party_id(dbtr, op)
        person = op.get("naturalPerson") or op.get("legalPerson") or {}
        _add_postal_address(dbtr, person.get("geographicAddresses", []))
        country = person.get("countryOfResidence") or person.get("countryOfRegistration")
        if country:
            SubElement(dbtr, "CtryOfRes").text = country

    # Debtor Account
    if orig_accounts:
        dbtr_acct = SubElement(cdt_trf, "DbtrAcct")
        _add_account(dbtr_acct, orig_accounts, asset_type)

    # DbtrAgt
    if originating_vasp:
        dbtr_agt = SubElement(cdt_trf, "DbtrAgt")
        fin = SubElement(dbtr_agt, "FinInstnId")
        if originating_vasp.get("lei"):
            SubElement(fin, "LEI").text = originating_vasp["lei"]

    # Creditor
    if bene_persons:
        bp = bene_persons[0]
        cdtr = SubElement(cdt_trf, "Cdtr")
        name = _get_name_string(bp)
        if name:
            SubElement(cdtr, "Nm").text = name[:140]
        _add_party_id(cdtr, bp)
        person = bp.get("naturalPerson") or bp.get("legalPerson") or {}
        _add_postal_address(cdtr, person.get("geographicAddresses", []))
        country = person.get("countryOfResidence") or person.get("countryOfRegistration")
        if country:
            SubElement(cdtr, "CtryOfRes").text = country

    # Creditor Account
    if bene_accounts:
        cdtr_acct = SubElement(cdt_trf, "CdtrAcct")
        _add_account(cdtr_acct, bene_accounts, asset_type)

    # CdtrAgt
    if beneficiary_vasp:
        cdtr_agt = SubElement(cdt_trf, "CdtrAgt")
        fin = SubElement(cdtr_agt, "FinInstnId")
        if beneficiary_vasp.get("lei"):
            SubElement(fin, "LEI").text = beneficiary_vasp["lei"]

    # Supplementary Data — KYCAMLEnvelope
    envelope_json = _build_kyc_aml_envelope(payload, msg_id)
    splmtry = SubElement(cdt_trf, "SplmtryData")
    SubElement(splmtry, "PlcAndNm").text = SPLMTRY_DATA_PLACE_AND_NAME
    SubElement(splmtry, "Envlp").text = envelope_json

    return _pretty_xml(doc)


# ---------------------------------------------------------------------------
# openkycaml_to_pain001
# ---------------------------------------------------------------------------


def openkycaml_to_pain001(
    payload: dict[str, Any],
    message_config: dict[str, Any] | None = None,
) -> str:
    """
    Convert an OpenKYCAML payload to an ISO 20022 pain.001 XML string.

    Parameters
    ----------
    payload : dict
        A valid OpenKYCAML envelope (must contain an ``ivms101`` block).
    message_config : dict, optional
        Override values. Supported keys:
          - ``service_level`` (str, default "SEPA")
          - ``payment_method`` (str, default "TRF")
          - ``requested_execution_date`` (str ISO 8601 date)
          - ``remittance_info`` (str unstructured remittance information)

    Returns
    -------
    str
        A UTF-8 XML string representing the pain.001 message.

    Raises
    ------
    ValueError
        If the payload does not contain an ``ivms101`` block.
    """
    cfg = message_config or {}
    ivms = payload.get("ivms101")
    if not ivms:
        raise ValueError("No 'ivms101' block found. Cannot produce pain.001.")

    msg_id = payload.get("messageId") or str(uuid.uuid4())
    msg_dt = payload.get("messageDateTime") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    originator = ivms.get("originator", {})
    beneficiary = ivms.get("beneficiary", {})
    orig_persons = originator.get("originatorPersons", [])
    bene_persons = beneficiary.get("beneficiaryPersons", [])
    orig_accounts = originator.get("accountNumber", [])
    bene_accounts = beneficiary.get("accountNumber", [])
    amount_info = ivms.get("transferredAmount", {})
    asset_type = amount_info.get("assetType", "XXX")
    amount_value = amount_info.get("amount", "0")
    ccy = asset_type if _is_iso4217(asset_type) else "XXX"

    originating_vasp = ivms.get("originatingVASP", {})
    beneficiary_vasp = ivms.get("beneficiaryVASP", {})

    # Root element
    doc = Element("Document", attrib={"xmlns": PAIN001_NS})
    initn = SubElement(doc, "CstmrCdtTrfInitn")

    # Group Header
    grp_hdr = SubElement(initn, "GrpHdr")
    SubElement(grp_hdr, "MsgId").text = msg_id[:35]
    SubElement(grp_hdr, "CreDtTm").text = msg_dt
    SubElement(grp_hdr, "NbOfTxs").text = "1"
    SubElement(grp_hdr, "CtrlSum").text = amount_value

    init_pty = SubElement(grp_hdr, "InitgPty")
    if orig_persons:
        op = orig_persons[0]
        name = _get_name_string(op)
        if name:
            SubElement(init_pty, "Nm").text = name[:140]
        lei = _get_lei(op)
        if lei:
            id_el = SubElement(init_pty, "Id")
            org = SubElement(id_el, "OrgId")
            SubElement(org, "LEI").text = lei
    elif originating_vasp.get("name"):
        SubElement(init_pty, "Nm").text = originating_vasp["name"][:140]

    # Payment Information block
    pmt_inf = SubElement(initn, "PmtInf")
    SubElement(pmt_inf, "PmtInfId").text = msg_id[:35]
    SubElement(pmt_inf, "PmtMtd").text = cfg.get("payment_method", "TRF")
    SubElement(pmt_inf, "NbOfTxs").text = "1"
    SubElement(pmt_inf, "CtrlSum").text = amount_value

    pmt_tp = SubElement(pmt_inf, "PmtTpInf")
    svc = SubElement(pmt_tp, "SvcLvl")
    SubElement(svc, "Cd").text = cfg.get("service_level", "SEPA")

    exec_date_str = cfg.get("requested_execution_date", msg_dt[:10])
    reqd = SubElement(pmt_inf, "ReqdExctnDt")
    SubElement(reqd, "Dt").text = exec_date_str

    # Debtor
    if orig_persons:
        op = orig_persons[0]
        dbtr = SubElement(pmt_inf, "Dbtr")
        name = _get_name_string(op)
        if name:
            SubElement(dbtr, "Nm").text = name[:140]
        _add_party_id(dbtr, op)
        person = op.get("naturalPerson") or op.get("legalPerson") or {}
        _add_postal_address(dbtr, person.get("geographicAddresses", []))

    # Debtor Account
    if orig_accounts:
        dbtr_acct = SubElement(pmt_inf, "DbtrAcct")
        _add_account(dbtr_acct, orig_accounts, asset_type)
        if ccy != "XXX":
            SubElement(dbtr_acct, "Ccy").text = ccy

    # Debtor Agent
    dbtr_agt = SubElement(pmt_inf, "DbtrAgt")
    fin = SubElement(dbtr_agt, "FinInstnId")
    if originating_vasp.get("lei"):
        SubElement(fin, "LEI").text = originating_vasp["lei"]
    else:
        SubElement(fin, "Othr").text = "NOTPROVIDED"

    # Credit Transfer Transaction Information
    cdt_trf = SubElement(pmt_inf, "CdtTrfTxInf")

    pmt_id = SubElement(cdt_trf, "PmtId")
    SubElement(pmt_id, "EndToEndId").text = msg_id[:35]

    amt_el = SubElement(cdt_trf, "Amt")
    SubElement(amt_el, "InstdAmt", attrib={"Ccy": ccy}).text = amount_value

    # Creditor Agent
    if beneficiary_vasp:
        cdtr_agt = SubElement(cdt_trf, "CdtrAgt")
        fin = SubElement(cdtr_agt, "FinInstnId")
        if beneficiary_vasp.get("lei"):
            SubElement(fin, "LEI").text = beneficiary_vasp["lei"]

    # Creditor
    if bene_persons:
        bp = bene_persons[0]
        cdtr = SubElement(cdt_trf, "Cdtr")
        name = _get_name_string(bp)
        if name:
            SubElement(cdtr, "Nm").text = name[:140]
        _add_party_id(cdtr, bp)
        person = bp.get("naturalPerson") or bp.get("legalPerson") or {}
        _add_postal_address(cdtr, person.get("geographicAddresses", []))

    # Creditor Account
    if bene_accounts:
        cdtr_acct = SubElement(cdt_trf, "CdtrAcct")
        _add_account(cdtr_acct, bene_accounts, asset_type)

    # Remittance Info
    rmt_info = cfg.get("remittance_info")
    if rmt_info:
        rmt = SubElement(cdt_trf, "RmtInf")
        SubElement(rmt, "Ustrd").text = rmt_info[:140]

    # Supplementary Data — KYCAMLEnvelope
    envelope_json = _build_kyc_aml_envelope(payload, msg_id)
    splmtry = SubElement(cdt_trf, "SplmtryData")
    SubElement(splmtry, "PlcAndNm").text = SPLMTRY_DATA_PLACE_AND_NAME
    SubElement(splmtry, "Envlp").text = envelope_json

    return _pretty_xml(doc)


# ---------------------------------------------------------------------------
# iso20022_to_openkycaml
# ---------------------------------------------------------------------------


def iso20022_to_openkycaml(xml_string: str) -> dict[str, Any]:
    """
    Parse an ISO 20022 XML message and reconstruct an OpenKYCAML payload.

    Supports pacs.008 and pain.001 message structures. Extracts the
    KYCAMLEnvelope from any <SplmtryData> element whose <PlcAndNm> matches
    the OpenKYCAML discriminator.

    Parameters
    ----------
    xml_string : str
        UTF-8 XML string of a pacs.008 or pain.001 message.

    Returns
    -------
    dict
        An OpenKYCAML-compatible payload reconstructed from the XML.
        Fields that cannot be recovered from ISO 20022 natively are
        populated from the KYCAMLEnvelope in <SplmtryData>.
    """
    # Use a namespace-agnostic approach: strip all namespaces from tags
    import xml.etree.ElementTree as ET

    # Remove namespace prefixes for simpler XPath
    xml_no_ns = re.sub(r' xmlns(?::\w+)?="[^"]*"', "", xml_string)
    xml_no_ns = re.sub(r"<(\w+):(\w+)", r"<\2", xml_no_ns)
    xml_no_ns = re.sub(r"</(\w+):(\w+)", r"</\2", xml_no_ns)

    root = ET.fromstring(xml_no_ns)

    def find_text(element: ET.Element, path: str) -> str | None:
        el = element.find(path)
        return el.text.strip() if el is not None and el.text else None

    # Detect message type
    msg_id: str | None = None
    msg_dt: str | None = None
    is_pacs008 = root.find(".//FIToFICstmrCdtTrf") is not None
    is_pain001 = root.find(".//CstmrCdtTrfInitn") is not None

    if is_pacs008:
        grp = root.find(".//FIToFICstmrCdtTrf/GrpHdr")
    elif is_pain001:
        grp = root.find(".//CstmrCdtTrfInitn/GrpHdr")
    else:
        grp = root.find(".//GrpHdr")

    if grp is not None:
        msg_id = find_text(grp, "MsgId")
        msg_dt = find_text(grp, "CreDtTm")

    # Extract KYCAMLEnvelope from SplmtryData
    envelope: dict[str, Any] = {}
    for splmtry in root.iter("SplmtryData"):
        place_name = find_text(splmtry, "PlcAndNm")
        if place_name == SPLMTRY_DATA_PLACE_AND_NAME:
            envlp_el = splmtry.find("Envlp")
            if envlp_el is not None and envlp_el.text:
                raw = envlp_el.text.strip()
                try:
                    envelope = json.loads(raw)
                except json.JSONDecodeError:
                    pass
            break

    # Extract debtor (originator) fields
    if is_pacs008:
        tx_path = ".//FIToFICstmrCdtTrf/CdtTrfTxInf"
    else:
        tx_path = ".//CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf"

    tx = root.find(tx_path)
    if tx is None:
        # Fallback
        tx = root.find(".//CdtTrfTxInf")

    orig_person: dict[str, Any] = {}
    bene_person: dict[str, Any] = {}
    orig_account: list[str] = []
    bene_account: list[str] = []
    amount_value: str | None = None
    ccy: str | None = None
    orig_vasp: dict[str, Any] = {}
    bene_vasp: dict[str, Any] = {}

    if tx is not None:
        # For pain.001, the Dbtr and DbtrAcct are at PmtInf level, not CdtTrfTxInf level
        pmt_inf_el = root.find(".//CstmrCdtTrfInitn/PmtInf") if is_pain001 else None

        dbtr = tx.find("Dbtr")
        if dbtr is None and pmt_inf_el is not None:
            dbtr = pmt_inf_el.find("Dbtr")

        if dbtr is not None:
            nm = find_text(dbtr, "Nm")
            nat_person: dict[str, Any] = {"name": {"nameIdentifier": []}}
            if nm:
                parts = nm.rsplit(" ", 1)
                nat_person["name"]["nameIdentifier"].append({
                    "primaryIdentifier": parts[-1],
                    "secondaryIdentifier": parts[0] if len(parts) > 1 else "",
                    "nameIdentifierType": "LEGL",
                })

            # DOB
            dob_el = dbtr.find(".//DtAndPlcOfBirth")
            if dob_el is not None:
                nat_person["dateAndPlaceOfBirth"] = {
                    "dateOfBirth": find_text(dob_el, "BirthDt"),
                    "placeOfBirth": find_text(dob_el, "CityOfBirth"),
                    "countryOfBirth": find_text(dob_el, "CtryOfBirth"),
                }

            # National ID
            othr = dbtr.find(".//PrvtId/Othr")
            if othr is not None:
                nat_person["nationalIdentification"] = {
                    "nationalIdentifier": find_text(othr, "Id"),
                    "nationalIdentifierType": find_text(othr, "SchmeNm/Prtry") or "MISC",
                }

            # LEI (legal person)
            lei = dbtr.find(".//OrgId/LEI")
            if lei is not None and lei.text:
                legal_person: dict[str, Any] = {
                    "nationalIdentification": {
                        "nationalIdentifier": lei.text.strip(),
                        "nationalIdentifierType": "LEIX",
                    }
                }
                if nm:
                    legal_person["name"] = {
                        "nameIdentifier": [{"legalPersonName": nm, "legalPersonNameIdentifierType": "LEGL"}]
                    }
                orig_person = {"legalPerson": legal_person}
            else:
                # Address
                pstl = dbtr.find("PstlAdr")
                if pstl is not None:
                    addr: dict[str, Any] = {}
                    for field, key in [
                        ("StrtNm", "streetName"),
                        ("BldgNb", "buildingNumber"),
                        ("PstCd", "postCode"),
                        ("TwnNm", "townName"),
                        ("Ctry", "country"),
                    ]:
                        val = find_text(pstl, field)
                        if val:
                            addr[key] = val
                    lines = [el.text.strip() for el in pstl.findall("AdrLine") if el.text]
                    if lines:
                        addr["addressLine"] = lines
                    nat_person["geographicAddresses"] = [addr]

                country_of_res = find_text(dbtr, "CtryOfRes")
                if country_of_res:
                    nat_person["countryOfResidence"] = country_of_res

                orig_person = {"naturalPerson": nat_person}

        # Debtor account — check both CdtTrfTxInf and PmtInf levels
        dbtr_acct = tx.find("DbtrAcct")
        if dbtr_acct is None and pmt_inf_el is not None:
            dbtr_acct = pmt_inf_el.find("DbtrAcct")
        if dbtr_acct is not None:
            iban = find_text(dbtr_acct, ".//IBAN")
            othr_id = find_text(dbtr_acct, ".//Othr/Id")
            if iban:
                orig_account = [iban]
            elif othr_id:
                orig_account = [othr_id]

        # Creditor
        cdtr = tx.find("Cdtr")
        if cdtr is not None:
            nm = find_text(cdtr, "Nm")
            bene_nat: dict[str, Any] = {"name": {"nameIdentifier": []}}
            if nm:
                parts = nm.rsplit(" ", 1)
                bene_nat["name"]["nameIdentifier"].append({
                    "primaryIdentifier": parts[-1],
                    "secondaryIdentifier": parts[0] if len(parts) > 1 else "",
                    "nameIdentifierType": "LEGL",
                })
            lei = cdtr.find(".//OrgId/LEI")
            if lei is not None and lei.text:
                bene_legal: dict[str, Any] = {
                    "nationalIdentification": {
                        "nationalIdentifier": lei.text.strip(),
                        "nationalIdentifierType": "LEIX",
                    }
                }
                if nm:
                    bene_legal["name"] = {
                        "nameIdentifier": [{"legalPersonName": nm, "legalPersonNameIdentifierType": "LEGL"}]
                    }
                bene_person = {"legalPerson": bene_legal}
            else:
                country_of_res = find_text(cdtr, "CtryOfRes")
                if country_of_res:
                    bene_nat["countryOfResidence"] = country_of_res
                bene_person = {"naturalPerson": bene_nat}

        # Creditor account
        cdtr_acct = tx.find("CdtrAcct")
        if cdtr_acct is not None:
            iban = find_text(cdtr_acct, ".//IBAN")
            othr_id = find_text(cdtr_acct, ".//Othr/Id")
            if iban:
                bene_account = [iban]
            elif othr_id:
                bene_account = [othr_id]

        # Amount — use explicit None check to avoid ElementTree falsy-element bug
        amt_el = tx.find(".//IntrBkSttlmAmt")
        if amt_el is None:
            amt_el = tx.find(".//InstdAmt")
        if amt_el is not None:
            amount_value = amt_el.text.strip() if amt_el.text else None
            ccy = amt_el.attrib.get("Ccy")

    # VASP agents
    instg = root.find(".//InstgAgt/FinInstnId")
    if instg is not None:
        lei = find_text(instg, "LEI")
        nm = find_text(instg, "Nm")
        if lei or nm:
            orig_vasp = {k: v for k, v in {"lei": lei, "name": nm}.items() if v}

    instd = root.find(".//InstdAgt/FinInstnId")
    if instd is not None:
        lei = find_text(instd, "LEI")
        nm = find_text(instd, "Nm")
        if lei or nm:
            bene_vasp = {k: v for k, v in {"lei": lei, "name": nm}.items() if v}

    # Reconstruct asset type from envelope if available
    envelope_kyc = envelope.get("kycProfile", {})
    tx_amount = envelope_kyc.get("transferredAmount") or {}
    reconstructed_asset = tx_amount.get("assetType") or ccy or "XXX"

    # Assemble OpenKYCAML payload
    result: dict[str, Any] = {
        "$schema": "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
        "version": envelope.get("openKycAmlVersion", "1.3.0"),
        "messageId": msg_id or str(uuid.uuid4()),
        "messageDateTime": msg_dt or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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

    if amount_value:
        ivms_block["transferredAmount"] = {
            "amount": amount_value,
            "assetType": reconstructed_asset,
        }

    if ivms_block:
        result["ivms101"] = ivms_block

    # Merge KYCAMLEnvelope back into result
    if envelope.get("kycProfile"):
        result["kycProfile"] = envelope["kycProfile"]

    if envelope.get("gdprSensitivityMetadata"):
        result["gdprSensitivityMetadata"] = envelope["gdprSensitivityMetadata"]

    # Reconstruct minimal VC block from vcProofs
    vc_proofs = envelope.get("vcProofs", [])
    if vc_proofs:
        proof = vc_proofs[0]
        result["verifiableCredential"] = {
            "issuer": {"id": proof.get("issuerDid", "")},
            "credentialSubject": {"id": proof.get("subjectDid", "")},
            "evidence": [
                {
                    "type": proof.get("credentialType", []),
                    "credentialIssuer": proof.get("issuerDid", ""),
                    "verifier": proof.get("verifierDid", ""),
                    "presentationMethod": proof.get("presentationMethod", ""),
                    "presentationDate": proof.get("presentationDate", ""),
                }
            ],
            "proof": {
                "type": proof.get("proofType", ""),
                "verificationMethod": proof.get("verificationMethod", ""),
                "proofValue": proof.get("proofValue"),
            },
        }

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="OpenKYCAML ↔ ISO 20022 converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  openkycaml-to-pacs008  <payload.json>  [--out output.xml]
  openkycaml-to-pain001  <payload.json>  [--out output.xml]
  iso20022-to-openkycaml <message.xml>   [--out output.json]
""",
    )
    parser.add_argument("command", choices=["openkycaml-to-pacs008", "openkycaml-to-pain001", "iso20022-to-openkycaml"])
    parser.add_argument("input_file")
    parser.add_argument("--out", help="Output file path (default: stdout)")
    args = parser.parse_args()

    with open(args.input_file, encoding="utf-8") as f:
        raw_input = f.read()

    if args.command == "openkycaml-to-pacs008":
        result_str = openkycaml_to_pacs008(json.loads(raw_input))
    elif args.command == "openkycaml-to-pain001":
        result_str = openkycaml_to_pain001(json.loads(raw_input))
    else:
        result_str = json.dumps(iso20022_to_openkycaml(raw_input), indent=2, ensure_ascii=False)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(result_str)
        print(f"Written to {args.out}", file=sys.stderr)
    else:
        print(result_str)
