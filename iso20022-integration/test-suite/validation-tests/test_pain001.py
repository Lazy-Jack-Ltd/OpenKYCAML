"""
Test Suite: OpenKYCAML ↔ pain.001 Round-Trip
============================================
Tests for iso20022-integration/libraries/python/converter.py (pain.001 path)

Run with:
    pip install pytest jsonschema
    pytest iso20022-integration/test-suite/validation-tests/test_pain001.py -v
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Add the library directory to sys.path
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parents[3]
# Verify we found the right directory (has a schema/ folder)
while REPO_ROOT.parent != REPO_ROOT and not (REPO_ROOT / "schema").exists():
    REPO_ROOT = REPO_ROOT.parent
sys.path.insert(0, str(REPO_ROOT / "iso20022-integration" / "libraries" / "python"))

from converter import (  # noqa: E402
    openkycaml_to_pain001,
    iso20022_to_openkycaml,
    SPLMTRY_DATA_PLACE_AND_NAME,
)

# ---------------------------------------------------------------------------
# Sample payloads
# ---------------------------------------------------------------------------

CORPORATE_EUR_PAYLOAD = {
    "$schema": "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
    "version": "1.3.0",
    "messageId": "test-pain001-corp-0001",
    "messageDateTime": "2026-04-05T13:30:00Z",
    "ivms101": {
        "originator": {
            "originatorPersons": [
                {
                    "legalPerson": {
                        "name": {
                            "nameIdentifier": [
                                {
                                    "legalPersonName": "Acme Blockchain Holdings B.V.",
                                    "legalPersonNameIdentifierType": "LEGL",
                                }
                            ]
                        },
                        "nationalIdentification": {
                            "nationalIdentifier": "724500VNNHZHYDLFMO70",
                            "nationalIdentifierType": "LEIX",
                        },
                        "geographicAddresses": [
                            {
                                "streetName": "Herengracht",
                                "buildingNumber": "420",
                                "postCode": "1017 BZ",
                                "townName": "Amsterdam",
                                "country": "NL",
                            }
                        ],
                        "countryOfRegistration": "NL",
                    }
                }
            ],
            "accountNumber": ["NL91ABNA0417164300"],
        },
        "beneficiary": {
            "beneficiaryPersons": [
                {
                    "legalPerson": {
                        "name": {
                            "nameIdentifier": [
                                {
                                    "legalPersonName": "Baltic Digital Finance AS",
                                    "legalPersonNameIdentifierType": "LEGL",
                                }
                            ]
                        },
                        "nationalIdentification": {
                            "nationalIdentifier": "724500EEBALDIG2026AS",
                            "nationalIdentifierType": "LEIX",
                        },
                    }
                }
            ],
            "accountNumber": ["EE382200221020145685"],
        },
        "originatingVASP": {"name": "ABN AMRO N.V.", "lei": "BFXS5XCH7N0Y05NIXW11"},
        "beneficiaryVASP": {"name": "LHV Pank AS", "lei": "5493003LNYYHHKCUON31"},
        "transferredAmount": {"amount": "250000.00", "assetType": "EUR"},
    },
    "kycProfile": {
        "customerRiskRating": {"overallRiskRating": "LOW", "ratingDate": "2026-02-01"},
        "dueDiligenceType": "CDD",
        "customerClassification": "CORPORATE",
        "kycCompletionDate": "2025-11-10",
        "onboardingChannel": "IN_PERSON",
        "thirdPartyCDDReliance": {
            "relyingPartyId": "did:web:abnamro.example.nl",
            "providingPartyId": "did:web:kyc-utility.example.eu",
            "relianceScope": "FULL_CDD",
            "relianceContractRef": "CONTRACT-AMLA-NL-2025-007",
            "relianceDate": "2025-11-10",
            "accessToUnderlyingDataConfirmed": True,
            "providingPartyEligibilityConfirmed": True,
            "liabilityNote": "ABN AMRO N.V. retains liability as per AMLR Art. 48(4).",
        },
        "sanctionsScreening": {
            "result": "CLEAR",
            "screeningDate": "2026-04-05",
            "listsScreened": ["OFAC_SDN", "EU_CONSOLIDATED"],
        },
        "pepStatus": {"isPEP": False, "pepCategory": "NOT_PEP"},
        "auditMetadata": {
            "recordId": "KYC-CORP-2025-004421",
            "dataRetentionDate": "2030-11-10",
            "dataProvider": "did:web:kyc-utility.example.eu",
            "changeLog": [
                {
                    "timestamp": "2025-11-10T14:00:00Z",
                    "actor": "analyst@kyc-utility.example.eu",
                    "description": "Full CDD completed. LOW risk.",
                }
            ],
        },
    },
}

NATURAL_PERSON_GBP_PAYLOAD = {
    "$schema": "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
    "version": "1.3.0",
    "messageId": "test-pain001-np-0001",
    "messageDateTime": "2026-04-05T14:00:00Z",
    "ivms101": {
        "originator": {
            "originatorPersons": [
                {
                    "naturalPerson": {
                        "name": {
                            "nameIdentifier": [
                                {
                                    "primaryIdentifier": "Smith",
                                    "secondaryIdentifier": "Alice",
                                    "nameIdentifierType": "LEGL",
                                }
                            ]
                        },
                        "nationalIdentification": {
                            "nationalIdentifier": "UK-PASSPORT-BC123456",
                            "nationalIdentifierType": "CCPT",
                            "countryOfIssue": "GB",
                        },
                        "dateAndPlaceOfBirth": {
                            "dateOfBirth": "1990-07-14",
                            "placeOfBirth": "London",
                            "countryOfBirth": "GB",
                        },
                        "geographicAddresses": [
                            {
                                "streetName": "Baker Street",
                                "buildingNumber": "221B",
                                "postCode": "NW1 6XE",
                                "townName": "London",
                                "country": "GB",
                            }
                        ],
                        "countryOfResidence": "GB",
                    }
                }
            ],
            "accountNumber": ["GB29NWBK60161331926819"],
        },
        "beneficiary": {
            "beneficiaryPersons": [
                {
                    "naturalPerson": {
                        "name": {
                            "nameIdentifier": [
                                {
                                    "primaryIdentifier": "Jones",
                                    "secondaryIdentifier": "Bob",
                                    "nameIdentifierType": "LEGL",
                                }
                            ]
                        },
                        "countryOfResidence": "DE",
                    }
                }
            ],
            "accountNumber": ["DE89370400440532013000"],
        },
        "originatingVASP": {"name": "NatWest PLC", "lei": "RWNXBQK0M0WI9XTFLPK2"},
        "beneficiaryVASP": {"name": "Deutsche Bank AG", "lei": "7LTWFZYICNSX8D621K86"},
        "transferredAmount": {"amount": "5000.00", "assetType": "GBP"},
    },
}


# ---------------------------------------------------------------------------
# Test: openkycaml_to_pain001 — XML structure
# ---------------------------------------------------------------------------


class TestOpenkycamlToPain001:
    def test_returns_xml_string(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        assert isinstance(xml, str)
        assert xml.startswith("<?xml")

    def test_contains_pain001_namespace(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        assert "pain.001" in xml

    def test_message_id_in_xml(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        assert "test-pain001-corp-0001" in xml

    def test_originator_name_in_xml(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        assert "Acme Blockchain Holdings B.V." in xml

    def test_beneficiary_name_in_xml(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        assert "Baltic Digital Finance AS" in xml

    def test_iban_debtor_account(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        assert "<IBAN>NL91ABNA0417164300</IBAN>" in xml

    def test_iban_creditor_account(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        assert "<IBAN>EE382200221020145685</IBAN>" in xml

    def test_eur_currency_mapped_correctly(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        assert 'Ccy="EUR"' in xml or "Ccy='EUR'" in xml

    def test_gbp_currency_mapped_correctly(self):
        xml = openkycaml_to_pain001(NATURAL_PERSON_GBP_PAYLOAD)
        assert 'Ccy="GBP"' in xml or "Ccy='GBP'" in xml

    def test_amount_in_xml(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        assert "250000.00" in xml

    def test_originating_vasp_lei_in_xml(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        assert "BFXS5XCH7N0Y05NIXW11" in xml

    def test_lei_in_orgid_for_legal_entity(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        assert "724500VNNHZHYDLFMO70" in xml

    def test_splmtrydata_place_and_name(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        assert SPLMTRY_DATA_PLACE_AND_NAME in xml

    def test_envelope_message_ref_matches_message_id(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        match = re.search(r'\{.*"envelopeVersion".*\}', xml, re.DOTALL)
        assert match, "KYCAMLEnvelope not found in XML"
        envelope = json.loads(match.group(0))
        assert envelope["messageRef"] == "test-pain001-corp-0001"

    def test_third_party_cdd_reliance_in_envelope(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        match = re.search(r'\{.*"envelopeVersion".*\}', xml, re.DOTALL)
        assert match
        envelope = json.loads(match.group(0))
        assert "kycProfile" in envelope
        tpc = envelope["kycProfile"].get("thirdPartyCDDReliance")
        assert tpc is not None
        assert tpc["relyingPartyId"] == "did:web:abnamro.example.nl"
        assert tpc["accessToUnderlyingDataConfirmed"] is True

    def test_audit_trail_in_envelope(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        match = re.search(r'\{.*"envelopeVersion".*\}', xml, re.DOTALL)
        assert match
        envelope = json.loads(match.group(0))
        audit = envelope["kycProfile"]["auditMetadata"]
        assert audit["recordId"] == "KYC-CORP-2025-004421"
        assert audit["dataRetentionDate"] == "2030-11-10"
        assert len(audit["changeLog"]) >= 1

    def test_screening_results_in_envelope(self):
        xml = openkycaml_to_pain001(CORPORATE_EUR_PAYLOAD)
        match = re.search(r'\{.*"envelopeVersion".*\}', xml, re.DOTALL)
        assert match
        envelope = json.loads(match.group(0))
        sanctions = envelope["screeningResults"]["sanctionsScreening"]
        assert sanctions["result"] == "CLEAR"
        assert "OFAC_SDN" in sanctions["listsScreened"]

    def test_natural_person_name_in_xml(self):
        xml = openkycaml_to_pain001(NATURAL_PERSON_GBP_PAYLOAD)
        assert "Alice Smith" in xml

    def test_natural_person_dob_in_xml(self):
        xml = openkycaml_to_pain001(NATURAL_PERSON_GBP_PAYLOAD)
        assert "1990-07-14" in xml

    def test_natural_person_passport_id_in_xml(self):
        xml = openkycaml_to_pain001(NATURAL_PERSON_GBP_PAYLOAD)
        assert "UK-PASSPORT-BC123456" in xml

    def test_raises_if_no_ivms101(self):
        with pytest.raises(ValueError, match="ivms101"):
            openkycaml_to_pain001({"version": "1.3.0"})

    def test_custom_remittance_info(self):
        xml = openkycaml_to_pain001(
            CORPORATE_EUR_PAYLOAD,
            message_config={"remittance_info": "INV-2026-9999 Payment"},
        )
        assert "INV-2026-9999 Payment" in xml

    def test_custom_service_level(self):
        xml = openkycaml_to_pain001(
            CORPORATE_EUR_PAYLOAD,
            message_config={"service_level": "NURG"},
        )
        assert "<Cd>NURG</Cd>" in xml


# ---------------------------------------------------------------------------
# Test: iso20022_to_openkycaml round-trip (pain.001)
# ---------------------------------------------------------------------------


class TestIso20022ToOpenkycamlPain001:
    def _get_xml(self, payload=None):
        return openkycaml_to_pain001(payload or CORPORATE_EUR_PAYLOAD)

    def test_returns_dict(self):
        result = iso20022_to_openkycaml(self._get_xml())
        assert isinstance(result, dict)

    def test_message_id_preserved(self):
        result = iso20022_to_openkycaml(self._get_xml())
        assert result["messageId"] == "test-pain001-corp-0001"

    def test_originator_name_recovered(self):
        result = iso20022_to_openkycaml(self._get_xml())
        persons = result["ivms101"]["originator"]["originatorPersons"]
        lp = persons[0]["legalPerson"]
        name_ids = lp["name"]["nameIdentifier"]
        assert "Acme Blockchain Holdings B.V." in name_ids[0]["legalPersonName"]

    def test_originator_lei_recovered(self):
        result = iso20022_to_openkycaml(self._get_xml())
        persons = result["ivms101"]["originator"]["originatorPersons"]
        lp = persons[0]["legalPerson"]
        assert lp["nationalIdentification"]["nationalIdentifier"] == "724500VNNHZHYDLFMO70"
        assert lp["nationalIdentification"]["nationalIdentifierType"] == "LEIX"

    def test_iban_account_recovered(self):
        result = iso20022_to_openkycaml(self._get_xml())
        accounts = result["ivms101"]["originator"]["accountNumber"]
        assert "NL91ABNA0417164300" in accounts

    def test_kycprofile_recovered_from_envelope(self):
        result = iso20022_to_openkycaml(self._get_xml())
        assert "kycProfile" in result
        assert result["kycProfile"]["customerRiskRating"]["overallRiskRating"] == "LOW"

    def test_third_party_cdd_reliance_recovered(self):
        result = iso20022_to_openkycaml(self._get_xml())
        tpc = result["kycProfile"].get("thirdPartyCDDReliance")
        assert tpc is not None
        assert tpc["providingPartyId"] == "did:web:kyc-utility.example.eu"

    def test_amount_recovered(self):
        result = iso20022_to_openkycaml(self._get_xml())
        transferred = result["ivms101"]["transferredAmount"]
        assert transferred["amount"] == "250000.00"

    def test_natural_person_round_trip(self):
        xml = openkycaml_to_pain001(NATURAL_PERSON_GBP_PAYLOAD)
        result = iso20022_to_openkycaml(xml)
        persons = result["ivms101"]["originator"]["originatorPersons"]
        np = persons[0]["naturalPerson"]
        ids = np["name"]["nameIdentifier"]
        full = ids[0]["secondaryIdentifier"] + " " + ids[0]["primaryIdentifier"]
        assert "Alice" in full and "Smith" in full

    def test_natural_person_dob_recovered(self):
        xml = openkycaml_to_pain001(NATURAL_PERSON_GBP_PAYLOAD)
        result = iso20022_to_openkycaml(xml)
        persons = result["ivms101"]["originator"]["originatorPersons"]
        np = persons[0]["naturalPerson"]
        assert np["dateAndPlaceOfBirth"]["dateOfBirth"] == "1990-07-14"
