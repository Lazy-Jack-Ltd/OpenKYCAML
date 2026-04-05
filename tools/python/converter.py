#!/usr/bin/env python3
"""
OpenKYCAML Format Converter
============================
Converts between OpenKYCAML and other common formats:

  - IVMS 101 plain JSON  ↔  OpenKYCAML
  - eIDAS 2.0 flat PID   ↔  OpenKYCAML (natural person)
  - eIDAS 2.0 flat LPID  ↔  OpenKYCAML (legal entity)
  - OpenKYCAML  →  ISO 20022 pain.001-compatible dict
  - OpenKYCAML  →  W3C VC JSON-LD (VC-only output)

Usage:
    python converter.py ivms101-to-openkycaml  <ivms101.json>  [--out output.json]
    python converter.py openkycaml-to-ivms101  <payload.json>  [--out output.json]
    python converter.py pid-to-openkycaml      <pid.json>      [--out output.json]
    python converter.py openkycaml-to-pid      <payload.json>  [--out output.json]
    python converter.py lpid-to-openkycaml     <lpid.json>     [--out output.json]
    python converter.py openkycaml-to-lpid     <payload.json>  [--out output.json]
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
        "$schema": "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
        "version": "1.3.0",
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
# eIDAS 2.0 flat PID → OpenKYCAML
# ---------------------------------------------------------------------------


def pid_to_openkycaml(pid_payload: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a flat eIDAS 2.0 Person Identification Data (PID) payload into an
    OpenKYCAML envelope with the natural person placed as the IVMS 101 originator.

    The PID attribute names follow the EU Digital Identity Architecture and
    Reference Framework (ARF) §5.1 mandatory and optional attributes.  Common
    attribute names emitted by Member State PID Providers are supported
    (both snake_case ARF names and camelCase SDK variants).

    Parameters
    ----------
    pid_payload : dict
        Flat PID attribute map as issued by an eIDAS 2.0 PID Provider or
        decoded from an SD-JWT VC / mdoc presentation.

    Returns
    -------
    dict
        An OpenKYCAML-compliant envelope with ``ivms101.originator`` populated
        from the PID attributes.
    """
    # --- Name ---------------------------------------------------------------
    family_name = pid_payload.get("family_name") or pid_payload.get("familyName", "")
    given_name = pid_payload.get("given_name") or pid_payload.get("givenName", "")

    name_identifier: list[dict[str, Any]] = []
    if family_name or given_name:
        name_identifier.append(
            {
                "primaryIdentifier": family_name,
                "secondaryIdentifier": given_name,
                "nameIdentifierType": "LEGL",
            }
        )

    # --- Address ------------------------------------------------------------
    geographic_address: list[dict[str, Any]] = []
    street = (
        pid_payload.get("resident_street")
        or pid_payload.get("residentStreet")
        or pid_payload.get("address", {}).get("street_address", "")
        if isinstance(pid_payload.get("address"), dict)
        else pid_payload.get("address", "")
    )
    house_number = (
        pid_payload.get("resident_house_number")
        or pid_payload.get("residentHouseNumber")
        or (pid_payload.get("address", {}).get("house_number", "") if isinstance(pid_payload.get("address"), dict) else "")
    )
    postal_code = (
        pid_payload.get("resident_postal_code")
        or pid_payload.get("residentPostalCode")
        or (pid_payload.get("address", {}).get("postal_code", "") if isinstance(pid_payload.get("address"), dict) else "")
    )
    city = (
        pid_payload.get("resident_city")
        or pid_payload.get("residentCity")
        or (pid_payload.get("address", {}).get("locality", "") if isinstance(pid_payload.get("address"), dict) else "")
    )
    country = (
        pid_payload.get("resident_country")
        or pid_payload.get("residentCountry")
        or (pid_payload.get("address", {}).get("country", "") if isinstance(pid_payload.get("address"), dict) else "")
        or pid_payload.get("issuing_country")
        or pid_payload.get("issuingCountry", "")
    )
    if any([street, city, country]):
        addr: dict[str, Any] = {"addressType": "HOME"}
        if street:
            addr["streetName"] = street
        if house_number:
            addr["buildingNumber"] = house_number
        if postal_code:
            addr["postCode"] = postal_code
        if city:
            addr["townName"] = city
        if country:
            addr["country"] = country
        geographic_address.append(addr)

    # --- National identification --------------------------------------------
    national_id_value = (
        pid_payload.get("personal_administrative_number")
        or pid_payload.get("personalAdministrativeNumber")
        or pid_payload.get("document_number")
        or pid_payload.get("documentNumber", "")
    )
    national_id_country = (
        pid_payload.get("issuing_country")
        or pid_payload.get("issuingCountry")
        or country
        or ""
    )
    national_identification: dict[str, Any] = {}
    if national_id_value:
        national_identification = {
            "nationalIdentifier": national_id_value,
            "nationalIdentifierType": "IDCD",
        }
        if national_id_country:
            national_identification["countryOfIssue"] = national_id_country

    # --- Date and place of birth --------------------------------------------
    date_of_birth = (
        pid_payload.get("birth_date")
        or pid_payload.get("birthdate")
        or pid_payload.get("dateOfBirth", "")
    )
    place_of_birth = (
        pid_payload.get("birth_place")
        or pid_payload.get("birthPlace")
        or pid_payload.get("place_of_birth", "")
    )
    date_place_of_birth: dict[str, Any] = {}
    if date_of_birth:
        date_place_of_birth["dateOfBirth"] = date_of_birth
    if place_of_birth:
        date_place_of_birth["placeOfBirth"] = place_of_birth

    # --- Nationality --------------------------------------------------------
    nationality_raw = (
        pid_payload.get("nationality")
        or pid_payload.get("nationalities")
        or pid_payload.get("birth_country")
        or pid_payload.get("birthCountry")
    )
    nationality: str | None = None
    if isinstance(nationality_raw, list) and nationality_raw:
        nationality = nationality_raw[0]
    elif isinstance(nationality_raw, str) and nationality_raw:
        nationality = nationality_raw

    # --- Assemble natural person --------------------------------------------
    natural_person: dict[str, Any] = {}
    if name_identifier:
        natural_person["name"] = {"nameIdentifier": name_identifier}
    if geographic_address:
        natural_person["geographicAddress"] = geographic_address
    if national_identification:
        natural_person["nationalIdentification"] = national_identification
    if date_place_of_birth:
        natural_person["dateAndPlaceOfBirth"] = date_place_of_birth
    if nationality:
        natural_person["nationality"] = nationality
    if country:
        natural_person["countryOfResidence"] = country

    return {
        "$schema": "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
        "version": "1.3.0",
        "messageId": str(uuid.uuid4()),
        "messageDateTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ivms101": {
            "originator": {
                "originatorPersons": [{"naturalPerson": natural_person}],
            },
        },
    }


# ---------------------------------------------------------------------------
# OpenKYCAML → eIDAS 2.0 flat PID
# ---------------------------------------------------------------------------


def openkycaml_to_pid(openkycaml_payload: dict[str, Any]) -> dict[str, Any]:
    """
    Extract the natural person originator from an OpenKYCAML envelope and
    return a flat eIDAS 2.0 PID attribute map.

    Parameters
    ----------
    openkycaml_payload : dict
        A full OpenKYCAML envelope.

    Returns
    -------
    dict
        Flat PID attribute map using ARF snake_case attribute names.

    Raises
    ------
    ValueError
        If no natural person originator is present.
    """
    ivms = openkycaml_payload.get("ivms101", {})
    originator_persons = (ivms.get("originator") or {}).get("originatorPersons", [])

    np: dict[str, Any] | None = None
    for person_wrapper in originator_persons:
        if "naturalPerson" in person_wrapper:
            np = person_wrapper["naturalPerson"]
            break

    if np is None:
        raise ValueError(
            "No natural person originator found. Cannot convert to PID format."
        )

    pid: dict[str, Any] = {}

    # Name
    name_ids = (np.get("name") or {}).get("nameIdentifier", [])
    if name_ids:
        ni = name_ids[0]
        if ni.get("primaryIdentifier"):
            pid["family_name"] = ni["primaryIdentifier"]
        if ni.get("secondaryIdentifier"):
            pid["given_name"] = ni["secondaryIdentifier"]

    # Date / place of birth
    dob_block = np.get("dateAndPlaceOfBirth", {})
    if dob_block.get("dateOfBirth"):
        pid["birth_date"] = dob_block["dateOfBirth"]
    if dob_block.get("placeOfBirth"):
        pid["birth_place"] = dob_block["placeOfBirth"]

    # Address
    addresses = np.get("geographicAddress", [])
    if addresses:
        addr = addresses[0]
        address_parts: dict[str, str] = {}
        if addr.get("streetName"):
            address_parts["street_address"] = addr["streetName"]
            pid["resident_street"] = addr["streetName"]
        if addr.get("buildingNumber"):
            pid["resident_house_number"] = addr["buildingNumber"]
        if addr.get("postCode"):
            pid["resident_postal_code"] = addr["postCode"]
        if addr.get("townName"):
            pid["resident_city"] = addr["townName"]
            address_parts["locality"] = addr["townName"]
        if addr.get("country"):
            pid["resident_country"] = addr["country"]
            address_parts["country"] = addr["country"]
        if address_parts:
            pid["address"] = address_parts

    # National identification
    nat_id = np.get("nationalIdentification", {})
    if nat_id.get("nationalIdentifier"):
        pid["personal_administrative_number"] = nat_id["nationalIdentifier"]
    if nat_id.get("countryOfIssue"):
        pid["issuing_country"] = nat_id["countryOfIssue"]

    # Nationality
    if np.get("nationality"):
        pid["nationalities"] = [np["nationality"]]

    return pid


# ---------------------------------------------------------------------------
# eIDAS 2.0 flat LPID → OpenKYCAML
# ---------------------------------------------------------------------------


def lpid_to_openkycaml(lpid_payload: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a flat eIDAS 2.0 Legal Person Identification Data (LPID) payload
    into an OpenKYCAML envelope with the legal person as the IVMS 101 originator.

    The LPID attribute names follow the EU Digital Identity ARF §5.2 mandatory
    and optional attributes.

    Parameters
    ----------
    lpid_payload : dict
        Flat LPID attribute map as issued by an eIDAS 2.0 LPID Provider or
        decoded from an SD-JWT VC presentation.

    Returns
    -------
    dict
        An OpenKYCAML-compliant envelope with ``ivms101.originator`` and
        ``verifiableCredential.credentialSubject.lpid`` populated from the
        LPID attributes.
    """
    # Legal name
    legal_name = (
        lpid_payload.get("legal_name")
        or lpid_payload.get("legalName")
        or lpid_payload.get("current_legal_name")
        or lpid_payload.get("currentLegalName", "")
    )

    # Unique identifier
    unique_id = (
        lpid_payload.get("legal_person_identifier")
        or lpid_payload.get("legalPersonIdentifier")
        or lpid_payload.get("unique_identifier")
        or lpid_payload.get("uniqueIdentifier")
        or lpid_payload.get("registration_number")
        or lpid_payload.get("registrationNumber", "")
    )

    # Country of registration
    country_of_reg = (
        lpid_payload.get("country_of_registration")
        or lpid_payload.get("countryOfRegistration")
        or lpid_payload.get("issuing_country")
        or lpid_payload.get("issuingCountry", "")
    )

    # LEI
    lei = lpid_payload.get("lei") or lpid_payload.get("LEI", "")

    # Address
    geographic_address: list[dict[str, Any]] = []
    addr_raw = lpid_payload.get("legal_address") or lpid_payload.get("legalAddress") or lpid_payload.get("registered_address") or {}
    if isinstance(addr_raw, dict):
        addr: dict[str, Any] = {"addressType": "BIZZ"}
        for src_key, dst_key in [
            ("street_address", "streetName"),
            ("streetName", "streetName"),
            ("house_number", "buildingNumber"),
            ("buildingNumber", "buildingNumber"),
            ("postal_code", "postCode"),
            ("postCode", "postCode"),
            ("locality", "townName"),
            ("townName", "townName"),
            ("country", "country"),
        ]:
            val = addr_raw.get(src_key)
            if val and dst_key not in addr:
                addr[dst_key] = val
        if len(addr) > 1:
            geographic_address.append(addr)

    # Build IVMS 101 legal person
    legal_person: dict[str, Any] = {
        "name": {
            "nameIdentifier": [
                {
                    "legalPersonName": legal_name,
                    "legalPersonNameIdentifierType": "LEGL",
                }
            ]
        }
    }
    if unique_id:
        id_type = "LEIX" if (lei and lei == unique_id) else "RAID"
        nat_id: dict[str, Any] = {
            "nationalIdentifier": unique_id,
            "nationalIdentifierType": id_type,
        }
        if country_of_reg:
            nat_id["countryOfIssue"] = country_of_reg
        legal_person["nationalIdentification"] = nat_id
    if country_of_reg:
        legal_person["countryOfRegistration"] = country_of_reg
    if geographic_address:
        legal_person["geographicAddresses"] = geographic_address

    # Build OpenKYCAML LPID block (credentialSubject.lpid)
    lpid_block: dict[str, Any] = {
        "currentLegalName": legal_name,
        "uniqueIdentifier": unique_id,
    }
    if geographic_address:
        lpid_block["currentAddress"] = geographic_address[0]
    if lei:
        lpid_block["lei"] = lei
    for src, dst in [
        ("vat_registration_number", "vatRegistrationNumber"),
        ("vatRegistrationNumber", "vatRegistrationNumber"),
        ("tax_reference_number", "taxReferenceNumber"),
        ("taxReferenceNumber", "taxReferenceNumber"),
        ("eori_number", "eoriNumber"),
        ("eoriNumber", "eoriNumber"),
        ("european_unique_identifier", "europeanUniqueIdentifier"),
    ]:
        val = lpid_payload.get(src)
        if val and dst not in lpid_block:
            lpid_block[dst] = val

    return {
        "$schema": "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
        "version": "1.3.0",
        "messageId": str(uuid.uuid4()),
        "messageDateTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ivms101": {
            "originator": {
                "originatorPersons": [{"legalPerson": legal_person}],
            },
        },
        "verifiableCredential": {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://openkycaml.org/contexts/v1",
                "https://europa.eu/2018/credentials/eudi/v1",
            ],
            "type": ["VerifiableCredential", "OpenKYCAMLCredential"],
            "issuer": {"id": "did:example:issuer"},
            "issuanceDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "credentialSubject": {
                "lpid": lpid_block,
            },
        },
    }


# ---------------------------------------------------------------------------
# OpenKYCAML → eIDAS 2.0 flat LPID
# ---------------------------------------------------------------------------


def openkycaml_to_lpid(openkycaml_payload: dict[str, Any]) -> dict[str, Any]:
    """
    Extract the legal person originator from an OpenKYCAML envelope and return
    a flat eIDAS 2.0 LPID attribute map.

    Parameters
    ----------
    openkycaml_payload : dict
        A full OpenKYCAML envelope.

    Returns
    -------
    dict
        Flat LPID attribute map using ARF snake_case attribute names.

    Raises
    ------
    ValueError
        If no legal person originator is present.
    """
    # Try the dedicated LPID block first (preferred, richer attributes)
    vc = openkycaml_payload.get("verifiableCredential", {})
    cs = vc.get("credentialSubject", {})
    lpid_block = cs.get("lpid")

    ivms = openkycaml_payload.get("ivms101", {})
    originator_persons = (ivms.get("originator") or {}).get("originatorPersons", [])

    lp: dict[str, Any] | None = None
    for person_wrapper in originator_persons:
        if "legalPerson" in person_wrapper:
            lp = person_wrapper["legalPerson"]
            break

    if lp is None and lpid_block is None:
        raise ValueError(
            "No legal person originator or LPID block found. Cannot convert to LPID format."
        )

    lpid_out: dict[str, Any] = {}

    # Prefer structured LPID block fields
    if lpid_block:
        if lpid_block.get("currentLegalName"):
            lpid_out["legal_name"] = lpid_block["currentLegalName"]
        if lpid_block.get("uniqueIdentifier"):
            lpid_out["legal_person_identifier"] = lpid_block["uniqueIdentifier"]
        if lpid_block.get("lei"):
            lpid_out["lei"] = lpid_block["lei"]
        addr = lpid_block.get("currentAddress", {})
        if addr:
            addr_flat: dict[str, str] = {}
            if addr.get("streetName"):
                addr_flat["street_address"] = addr["streetName"]
            if addr.get("postCode"):
                addr_flat["postal_code"] = addr["postCode"]
            if addr.get("townName"):
                addr_flat["locality"] = addr["townName"]
            if addr.get("country"):
                addr_flat["country"] = addr["country"]
            if addr_flat:
                lpid_out["legal_address"] = addr_flat
        for src, dst in [
            ("vatRegistrationNumber", "vat_registration_number"),
            ("taxReferenceNumber", "tax_reference_number"),
            ("eoriNumber", "eori_number"),
            ("europeanUniqueIdentifier", "european_unique_identifier"),
        ]:
            if lpid_block.get(src):
                lpid_out[dst] = lpid_block[src]

    # Fall back to / enrich from IVMS 101 legal person
    if lp:
        if "legal_name" not in lpid_out:
            name_ids = (lp.get("name") or {}).get("nameIdentifier", [])
            for ni in name_ids:
                if ni.get("legalPersonNameIdentifierType") == "LEGL":
                    lpid_out["legal_name"] = ni["legalPersonName"]
                    break
        if "legal_person_identifier" not in lpid_out:
            nat_id = lp.get("nationalIdentification", {})
            if nat_id.get("nationalIdentifier"):
                lpid_out["legal_person_identifier"] = nat_id["nationalIdentifier"]
            if nat_id.get("countryOfIssue"):
                lpid_out["issuing_country"] = nat_id["countryOfIssue"]
        if lp.get("countryOfRegistration"):
            lpid_out["country_of_registration"] = lp["countryOfRegistration"]

    return lpid_out


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
    "pid-to-openkycaml": ("pid.json", pid_to_openkycaml),
    "openkycaml-to-pid": ("openkycaml.json", openkycaml_to_pid),
    "lpid-to-openkycaml": ("lpid.json", lpid_to_openkycaml),
    "openkycaml-to-lpid": ("openkycaml.json", openkycaml_to_lpid),
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
