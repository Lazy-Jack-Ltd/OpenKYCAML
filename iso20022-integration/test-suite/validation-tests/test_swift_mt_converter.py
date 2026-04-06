"""
Test Suite: OpenKYCAML ↔ SWIFT MT Converter
=============================================
Tests for iso20022-integration/libraries/python/swift_mt_converter.py

Covers MT 103, MT 202, MT 202 COV, MT 910, MT 940 — bidirectional round-trips,
full field mapping, and :77B: Travel Rule carrier handling.

Run with:
    pip install pytest
    pytest iso20022-integration/test-suite/validation-tests/test_swift_mt_converter.py -v
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parents[3]
while REPO_ROOT.parent != REPO_ROOT and not (REPO_ROOT / "schema").exists():
    REPO_ROOT = REPO_ROOT.parent
sys.path.insert(0, str(REPO_ROOT / "iso20022-integration" / "libraries" / "python"))

from swift_mt_converter import (  # noqa: E402
    build_77b,
    mt_to_openkycaml,
    openkycaml_to_mt103,
    openkycaml_to_mt202,
    openkycaml_to_mt202cov,
    openkycaml_to_mt910,
    openkycaml_to_mt940,
    parse_77b,
)

# ---------------------------------------------------------------------------
# Shared test payloads
# ---------------------------------------------------------------------------

NATURAL_PERSON_PAYLOAD = {
    "$schema": "https://openkycaml.org/schema/v1.4.0/kyc-aml-hybrid-extended.json",
    "version": "1.4.0",
    "messageId": "MT103-TEST-001",
    "messageDateTime": "2026-04-06T10:00:00Z",
    "ivms101": {
        "originator": {
            "originatorPersons": [
                {
                    "naturalPerson": {
                        "name": {
                            "nameIdentifier": [
                                {
                                    "primaryIdentifier": "Nakamura",
                                    "secondaryIdentifier": "Yuki",
                                    "nameIdentifierType": "LEGL",
                                }
                            ]
                        },
                        "nationalIdentification": {
                            "nationalIdentifier": "JP-MYNUMBER-99887766",
                            "nationalIdentifierType": "TXID",
                            "countryOfIssue": "JP",
                        },
                        "dateAndPlaceOfBirth": {
                            "dateOfBirth": "1988-07-14",
                            "placeOfBirth": "Tokyo",
                        },
                        "geographicAddresses": [
                            {
                                "streetName": "Sakura-dori 12",
                                "townName": "Tokyo",
                                "country": "JP",
                            }
                        ],
                        "countryOfResidence": "JP",
                    }
                }
            ],
            "accountNumber": ["JP12MUFG1234567890123456"],
        },
        "beneficiary": {
            "beneficiaryPersons": [
                {
                    "naturalPerson": {
                        "name": {
                            "nameIdentifier": [
                                {
                                    "primaryIdentifier": "Schmidt",
                                    "secondaryIdentifier": "Andreas",
                                    "nameIdentifierType": "LEGL",
                                }
                            ]
                        },
                        "geographicAddresses": [
                            {
                                "streetName": "Hauptstrasse 5",
                                "townName": "Berlin",
                                "country": "DE",
                            }
                        ],
                        "countryOfResidence": "DE",
                    }
                }
            ],
            "accountNumber": ["DE89370400440532013000"],
        },
        "originatingVASP": {
            "name": "Tokyo Digital Bank",
            "lei": "353800F0ADKV6MKZJQ22",
        },
        "beneficiaryVASP": {
            "name": "Berlin Crypto Exchange",
            "lei": "529900T8BM49AAMSDO55",
        },
        "transferredAmount": {
            "amount": "15000.00",
            "assetType": "EUR",
        },
    },
}

LEGAL_PERSON_PAYLOAD = {
    "$schema": "https://openkycaml.org/schema/v1.4.0/kyc-aml-hybrid-extended.json",
    "version": "1.4.0",
    "messageId": "MT202-TEST-002",
    "messageDateTime": "2026-04-06T11:00:00Z",
    "ivms101": {
        "originator": {
            "originatorPersons": [
                {
                    "legalPerson": {
                        "name": {
                            "nameIdentifier": [
                                {
                                    "legalPersonName": "Alpha Capital Ltd",
                                    "legalPersonNameIdentifierType": "LEGL",
                                }
                            ]
                        },
                        "nationalIdentification": {
                            "nationalIdentifier": "529900HNOAA1KXQJUQ27",
                            "nationalIdentifierType": "LEIX",
                        },
                        "countryOfRegistration": "GB",
                    }
                }
            ],
            "accountNumber": ["GB29NWBK60161331926819"],
        },
        "beneficiary": {
            "beneficiaryPersons": [
                {
                    "legalPerson": {
                        "name": {
                            "nameIdentifier": [
                                {
                                    "legalPersonName": "Beta Finance GmbH",
                                    "legalPersonNameIdentifierType": "LEGL",
                                }
                            ]
                        },
                        "nationalIdentification": {
                            "nationalIdentifier": "529900T8BM49AAMSDO22",
                            "nationalIdentifierType": "LEIX",
                        },
                        "countryOfRegistration": "DE",
                    }
                }
            ],
            "accountNumber": ["DE89370400440532013000"],
        },
        "originatingVASP": {
            "name": "Alpha Digital Bank",
            "lei": "213800WDAVG00001GB00",
        },
        "beneficiaryVASP": {
            "name": "Beta Digital Exchange",
            "lei": "213800WDAVG00001DE00",
        },
        "transferredAmount": {
            "amount": "500000.00",
            "assetType": "GBP",
        },
    },
}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_field(mt_text: str, tag: str) -> str:
    """Extract the value of a given SWIFT MT field tag from message text."""
    pattern = re.compile(rf":{re.escape(tag)}:(.*?)(?=\r?\n:[0-9]{{2}}[A-Z]?:|$)", re.DOTALL)
    m = pattern.search(mt_text)
    return m.group(1).strip() if m else ""


# ---------------------------------------------------------------------------
# MT 103 — Outbound (OpenKYCAML → MT 103)
# ---------------------------------------------------------------------------

class TestMT103Producer:

    def test_produces_string(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_field_20_present(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        assert ":20:" in result

    def test_field_20_truncated_to_16(self):
        payload = {**NATURAL_PERSON_PAYLOAD, "messageId": "A" * 40}
        result = openkycaml_to_mt103(payload)
        f20 = _get_field(result, "20")
        assert len(f20) <= 16

    def test_field_23b_present(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        assert ":23B:" in result

    def test_field_23b_default_cred(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "23B")
        assert f == "CRED"

    def test_field_32a_contains_currency(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "32A")
        assert "EUR" in f

    def test_field_32a_contains_amount(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "32A")
        # Amount "15000.00" should appear as "15000,00"
        assert "15000,00" in f

    def test_field_32a_non_fiat_becomes_xxx(self):
        payload = {
            **NATURAL_PERSON_PAYLOAD,
            "ivms101": {
                **NATURAL_PERSON_PAYLOAD["ivms101"],
                "transferredAmount": {"amount": "5.5", "assetType": "BTC"},
            },
        }
        result = openkycaml_to_mt103(payload)
        f = _get_field(result, "32A")
        assert "XXX" in f

    def test_field_50k_contains_originator_name(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "50K")
        assert "Nakamura" in f or "Yuki" in f

    def test_field_59_contains_beneficiary_name(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "59")
        assert "Schmidt" in f or "Andreas" in f

    def test_field_59_contains_beneficiary_iban(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "59")
        assert "DE89370400440532013000" in f

    def test_field_71a_default_sha(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "71A")
        assert f == "SHA"

    def test_field_71a_custom_our(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD, config={"details_of_charges": "OUR"})
        f = _get_field(result, "71A")
        assert f == "OUR"

    def test_field_77b_present_by_default(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        assert ":77B:" in result

    def test_field_77b_suppressed_when_false(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD, config={"include_77b": False})
        assert ":77B:" not in result

    def test_field_77b_contains_orderres(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "77B")
        assert "/ORDERRES/" in f

    def test_field_77b_contains_benefres(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "77B")
        assert "/BENEFRES/" in f

    def test_field_77b_contains_uetr(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "77B")
        assert "/UETR/" in f

    def test_field_52a_originating_vasp(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        assert ":52A:" in result

    def test_field_57a_beneficiary_vasp(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        assert ":57A:" in result

    def test_raises_without_ivms101(self):
        with pytest.raises(ValueError, match="ivms101"):
            openkycaml_to_mt103({"version": "1.4.0", "messageId": "x"})

    def test_custom_value_date(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD, config={"value_date": "2026-12-31"})
        f = _get_field(result, "32A")
        assert f.startswith("261231")

    def test_remittance_info_field_70(self):
        result = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD, config={"remittance_info": "INV-2026-0042"})
        assert ":70:" in result
        f = _get_field(result, "70")
        assert "INV-2026-0042" in f


# ---------------------------------------------------------------------------
# MT 202 — Outbound
# ---------------------------------------------------------------------------

class TestMT202Producer:

    def test_produces_string(self):
        result = openkycaml_to_mt202(LEGAL_PERSON_PAYLOAD)
        assert isinstance(result, str)

    def test_field_20_present(self):
        result = openkycaml_to_mt202(LEGAL_PERSON_PAYLOAD)
        assert ":20:" in result

    def test_field_21_present(self):
        result = openkycaml_to_mt202(LEGAL_PERSON_PAYLOAD)
        assert ":21:" in result

    def test_field_32a_present(self):
        result = openkycaml_to_mt202(LEGAL_PERSON_PAYLOAD)
        assert ":32A:" in result

    def test_field_32a_contains_amount(self):
        result = openkycaml_to_mt202(LEGAL_PERSON_PAYLOAD)
        f = _get_field(result, "32A")
        assert "500000,00" in f

    def test_field_58a_beneficiary_institution(self):
        result = openkycaml_to_mt202(LEGAL_PERSON_PAYLOAD)
        assert ":58A:" in result

    def test_no_77b_in_mt202(self):
        result = openkycaml_to_mt202(LEGAL_PERSON_PAYLOAD)
        assert ":77B:" not in result

    def test_raises_without_ivms101(self):
        with pytest.raises(ValueError, match="ivms101"):
            openkycaml_to_mt202({"version": "1.4.0"})

    def test_custom_related_reference(self):
        result = openkycaml_to_mt202(LEGAL_PERSON_PAYLOAD, config={"related_reference": "MT103-REF-001"})
        f = _get_field(result, "21")
        assert "MT103-REF-001" in f

    def test_sender_to_receiver_field_72(self):
        result = openkycaml_to_mt202(LEGAL_PERSON_PAYLOAD, config={"sender_to_receiver": "/ACC/NOSTRO"})
        assert ":72:" in result


# ---------------------------------------------------------------------------
# MT 202 COV — Outbound
# ---------------------------------------------------------------------------

class TestMT202COVProducer:

    def test_produces_string(self):
        result = openkycaml_to_mt202cov(NATURAL_PERSON_PAYLOAD)
        assert isinstance(result, str)

    def test_field_23b_cred(self):
        result = openkycaml_to_mt202cov(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "23B")
        assert f == "CRED"

    def test_field_50a_underlying_originator(self):
        result = openkycaml_to_mt202cov(NATURAL_PERSON_PAYLOAD)
        assert ":50A:" in result

    def test_field_59_underlying_beneficiary(self):
        result = openkycaml_to_mt202cov(NATURAL_PERSON_PAYLOAD)
        assert ":59:" in result

    def test_field_72_cov_indicator(self):
        result = openkycaml_to_mt202cov(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "72")
        assert "/COV/" in f

    def test_raises_without_ivms101(self):
        with pytest.raises(ValueError, match="ivms101"):
            openkycaml_to_mt202cov({"version": "1.4.0"})

    def test_originator_name_in_50a(self):
        result = openkycaml_to_mt202cov(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "50A")
        assert "Nakamura" in f or "Yuki" in f


# ---------------------------------------------------------------------------
# MT 910 — Outbound
# ---------------------------------------------------------------------------

class TestMT910Producer:

    def test_produces_string(self):
        result = openkycaml_to_mt910(NATURAL_PERSON_PAYLOAD)
        assert isinstance(result, str)

    def test_field_20_present(self):
        result = openkycaml_to_mt910(NATURAL_PERSON_PAYLOAD)
        assert ":20:" in result

    def test_field_25_present(self):
        result = openkycaml_to_mt910(NATURAL_PERSON_PAYLOAD)
        assert ":25:" in result

    def test_field_32a_present(self):
        result = openkycaml_to_mt910(NATURAL_PERSON_PAYLOAD)
        assert ":32A:" in result

    def test_field_32a_contains_eur(self):
        result = openkycaml_to_mt910(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "32A")
        assert "EUR" in f

    def test_field_50_ordering_customer(self):
        result = openkycaml_to_mt910(NATURAL_PERSON_PAYLOAD)
        assert ":50:" in result

    def test_raises_without_ivms101(self):
        with pytest.raises(ValueError, match="ivms101"):
            openkycaml_to_mt910({"version": "1.4.0"})


# ---------------------------------------------------------------------------
# MT 940 — Outbound
# ---------------------------------------------------------------------------

class TestMT940Producer:

    def test_produces_string(self):
        result = openkycaml_to_mt940(NATURAL_PERSON_PAYLOAD)
        assert isinstance(result, str)

    def test_field_20_present(self):
        result = openkycaml_to_mt940(NATURAL_PERSON_PAYLOAD)
        assert ":20:" in result

    def test_field_28c_present(self):
        result = openkycaml_to_mt940(NATURAL_PERSON_PAYLOAD)
        assert ":28C:" in result

    def test_field_60f_opening_balance(self):
        result = openkycaml_to_mt940(NATURAL_PERSON_PAYLOAD)
        assert ":60F:" in result
        f = _get_field(result, "60F")
        assert f.startswith("C")

    def test_field_61_statement_line(self):
        result = openkycaml_to_mt940(NATURAL_PERSON_PAYLOAD)
        assert ":61:" in result

    def test_field_61_credit_entry(self):
        result = openkycaml_to_mt940(NATURAL_PERSON_PAYLOAD)
        f = _get_field(result, "61")
        assert "C" in f  # Credit marker

    def test_field_86_narrative(self):
        result = openkycaml_to_mt940(NATURAL_PERSON_PAYLOAD)
        assert ":86:" in result

    def test_field_62f_closing_balance(self):
        result = openkycaml_to_mt940(NATURAL_PERSON_PAYLOAD)
        assert ":62F:" in result

    def test_raises_without_ivms101(self):
        with pytest.raises(ValueError, match="ivms101"):
            openkycaml_to_mt940({"version": "1.4.0"})


# ---------------------------------------------------------------------------
# MT → OpenKYCAML (Inbound parsing)
# ---------------------------------------------------------------------------

class TestMTToOpenKYCAML:

    def test_parse_mt103_returns_dict(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        assert isinstance(result, dict)

    def test_parse_mt103_has_schema(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        assert result.get("$schema", "").startswith("https://openkycaml.org/schema/")

    def test_parse_mt103_has_version(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        assert result.get("version") == "1.4.0"

    def test_parse_mt103_has_message_id(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        assert result.get("messageId") == "MT103-TEST-001"

    def test_parse_mt103_has_ivms101(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        assert "ivms101" in result

    def test_parse_mt103_originator_name_recovered(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        orig_persons = result.get("ivms101", {}).get("originator", {}).get("originatorPersons", [])
        assert orig_persons
        name_ids = (orig_persons[0].get("naturalPerson") or {}).get("name", {}).get("nameIdentifier", [])
        assert name_ids
        full_name = " ".join(
            filter(None, [name_ids[0].get("secondaryIdentifier"), name_ids[0].get("primaryIdentifier")])
        )
        assert "Nakamura" in full_name or "Yuki" in full_name

    def test_parse_mt103_amount_recovered(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        transferred = result.get("ivms101", {}).get("transferredAmount", {})
        assert transferred.get("amount") == "15000.00"
        assert transferred.get("assetType") == "EUR"

    def test_parse_mt103_beneficiary_account_recovered(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        bene_accounts = result.get("ivms101", {}).get("beneficiary", {}).get("accountNumber", [])
        assert bene_accounts
        assert "DE89370400440532013000" in bene_accounts[0]

    def test_parse_mt103_message_type_tag(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        assert result.get("_swiftMtMetadata", {}).get("mtMessageType") == "MT103"

    def test_parse_mt202_message_type_tag(self):
        mt = openkycaml_to_mt202(LEGAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        assert result.get("_swiftMtMetadata", {}).get("mtMessageType") == "MT202"

    def test_parse_mt202cov_message_type_tag(self):
        mt = openkycaml_to_mt202cov(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        assert result.get("_swiftMtMetadata", {}).get("mtMessageType") == "MT202COV"

    def test_parse_mt940_message_type_tag(self):
        mt = openkycaml_to_mt940(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        assert result.get("_swiftMtMetadata", {}).get("mtMessageType") == "MT940"

    def test_parse_mt103_77b_metadata_stored(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        assert result.get("_swiftMtMetadata", {}).get("field77B")

    def test_parse_mt103_uetr_recovered(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        uetr = result.get("_swiftMtMetadata", {}).get("uetr")
        assert uetr  # should contain the message ID truncated

    def test_parse_mt103_charge_bearer_recovered(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        assert result.get("_swiftMtMetadata", {}).get("chargeBearer") == "SHA"

    def test_parse_mt202_amount_recovered(self):
        mt = openkycaml_to_mt202(LEGAL_PERSON_PAYLOAD)
        result = mt_to_openkycaml(mt)
        transferred = result.get("ivms101", {}).get("transferredAmount", {})
        assert transferred.get("amount") == "500000.00"
        assert transferred.get("assetType") == "GBP"

    def test_parse_raw_mt103_text(self):
        raw_mt = (
            ":20:TESTREF001\n"
            ":23B:CRED\n"
            ":32A:260406EUR9876,54\n"
            ":50K:/GB29NWBK60161331926819\n"
            "John Smith\n"
            "123 High Street\n"
            "London GB\n"
            ":59:/DE89370400440532013000\n"
            "Hans Mueller\n"
            "Berliner Str. 1\n"
            ":71A:SHA\n"
            ":77B:/ORDERRES/John Smith/GB29NW\n"
            "/BENEFRES/Hans Mueller/DE8937\n"
            "/UETR/TESTREF001\n"
        )
        result = mt_to_openkycaml(raw_mt)
        assert result["messageId"] == "TESTREF001"
        ivms = result.get("ivms101", {})
        assert ivms.get("transferredAmount", {}).get("amount") == "9876.54"
        assert ivms.get("transferredAmount", {}).get("assetType") == "EUR"

    def test_parse_raw_mt103_77b_originator_merged(self):
        raw_mt = (
            ":20:REFABC\n"
            ":23B:CRED\n"
            ":32A:260406USD500,00\n"
            ":59:/12345678\n"
            "Bene Corp\n"
            ":71A:OUR\n"
            ":77B:/ORDERRES/Alice Wang/ACCT-99\n"
            "/BENEFRES/Bene Corp/12345678\n"
            "/UETR/REFABC\n"
        )
        result = mt_to_openkycaml(raw_mt)
        ivms = result.get("ivms101", {})
        orig_persons = ivms.get("originator", {}).get("originatorPersons", [])
        assert orig_persons
        name_ids = orig_persons[0].get("naturalPerson", {}).get("name", {}).get("nameIdentifier", [])
        assert name_ids
        assert "Alice" in name_ids[0].get("primaryIdentifier", "")


# ---------------------------------------------------------------------------
# 77B round-trip
# ---------------------------------------------------------------------------

class TestField77B:

    def test_build_77b_returns_string(self):
        result = build_77b(NATURAL_PERSON_PAYLOAD)
        assert isinstance(result, str)

    def test_build_77b_has_orderres(self):
        result = build_77b(NATURAL_PERSON_PAYLOAD)
        assert "/ORDERRES/" in result

    def test_build_77b_has_benefres(self):
        result = build_77b(NATURAL_PERSON_PAYLOAD)
        assert "/BENEFRES/" in result

    def test_build_77b_has_uetr(self):
        result = build_77b(NATURAL_PERSON_PAYLOAD)
        assert "/UETR/" in result

    def test_build_77b_line_lengths(self):
        result = build_77b(NATURAL_PERSON_PAYLOAD)
        for line in result.splitlines():
            assert len(line) <= 35, f"Line exceeds 35 chars: {line!r}"

    def test_parse_77b_returns_dict(self):
        raw = "/ORDERRES/Yuki Nakamura/JP12MUFG\n/BENEFRES/Andreas Schmidt/DE8937\n/UETR/MT103-TEST-001"
        result = parse_77b(raw)
        assert isinstance(result, dict)

    def test_parse_77b_originator_name(self):
        raw = "/ORDERRES/Alice Wang/ACCT001\n/BENEFRES/Bob Jones/ACCT002\n/UETR/REF001"
        result = parse_77b(raw)
        np = result.get("originator_77b", {}).get("naturalPerson", {})
        name_ids = np.get("name", {}).get("nameIdentifier", [])
        assert name_ids
        assert "Alice" in name_ids[0].get("primaryIdentifier", "") or "Wang" in name_ids[0].get("primaryIdentifier", "")

    def test_parse_77b_beneficiary_name(self):
        raw = "/ORDERRES/Alice Wang/ACCT001\n/BENEFRES/Bob Jones/ACCT002\n/UETR/REF001"
        result = parse_77b(raw)
        np = result.get("beneficiary_77b", {}).get("naturalPerson", {})
        name_ids = np.get("name", {}).get("nameIdentifier", [])
        assert name_ids
        assert "Bob" in name_ids[0].get("primaryIdentifier", "") or "Jones" in name_ids[0].get("primaryIdentifier", "")

    def test_parse_77b_uetr(self):
        raw = "/ORDERRES/Alice/ACCT001\n/BENEFRES/Bob/ACCT002\n/UETR/REF-UETR-001"
        result = parse_77b(raw)
        assert result.get("uetr") == "REF-UETR-001"

    def test_parse_77b_originator_account(self):
        raw = "/ORDERRES/Alice Wang/MYACCT123\n/BENEFRES/Bob/BENACCT"
        result = parse_77b(raw)
        assert result.get("originator_77b", {}).get("_account") == "MYACCT123"

    def test_build_and_parse_round_trip(self):
        built = build_77b(NATURAL_PERSON_PAYLOAD)
        parsed = parse_77b(built)
        # UETR should contain at least part of the message ID
        uetr = parsed.get("uetr", "")
        msg_id = NATURAL_PERSON_PAYLOAD["messageId"]
        assert uetr and msg_id[:len(uetr)] == uetr or msg_id in uetr or uetr in msg_id


# ---------------------------------------------------------------------------
# Full round-trip: OpenKYCAML → MT 103 → OpenKYCAML
# ---------------------------------------------------------------------------

class TestMT103RoundTrip:

    def test_round_trip_preserves_amount(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        recovered = mt_to_openkycaml(mt)
        assert recovered["ivms101"]["transferredAmount"]["amount"] == "15000.00"

    def test_round_trip_preserves_currency(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        recovered = mt_to_openkycaml(mt)
        assert recovered["ivms101"]["transferredAmount"]["assetType"] == "EUR"

    def test_round_trip_preserves_bene_account(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        recovered = mt_to_openkycaml(mt)
        bene_accounts = recovered["ivms101"]["beneficiary"]["accountNumber"]
        assert any("DE89370400440532013000" in a for a in bene_accounts)

    def test_round_trip_preserves_message_id(self):
        mt = openkycaml_to_mt103(NATURAL_PERSON_PAYLOAD)
        recovered = mt_to_openkycaml(mt)
        assert recovered["messageId"] == "MT103-TEST-001"

    def test_round_trip_mt202_amount(self):
        mt = openkycaml_to_mt202(LEGAL_PERSON_PAYLOAD)
        recovered = mt_to_openkycaml(mt)
        assert recovered["ivms101"]["transferredAmount"]["amount"] == "500000.00"

    def test_round_trip_mt202cov_message_type(self):
        mt = openkycaml_to_mt202cov(NATURAL_PERSON_PAYLOAD)
        recovered = mt_to_openkycaml(mt)
        assert recovered["_swiftMtMetadata"]["mtMessageType"] == "MT202COV"
