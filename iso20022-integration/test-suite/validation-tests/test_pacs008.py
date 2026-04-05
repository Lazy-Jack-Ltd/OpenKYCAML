"""
Test Suite: OpenKYCAML ↔ pacs.008 Round-Trip
=============================================
Tests for iso20022-integration/libraries/python/converter.py

Run with:
    pip install pytest jsonschema
    pytest iso20022-integration/test-suite/validation-tests/test_pacs008.py -v
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
sys.path.insert(0, str(REPO_ROOT / "iso20022-integration" / "libraries" / "python"))

from converter import (  # noqa: E402
    openkycaml_to_pacs008,
    iso20022_to_openkycaml,
    SPLMTRY_DATA_PLACE_AND_NAME,
)

# ---------------------------------------------------------------------------
# Sample payloads
# ---------------------------------------------------------------------------

MINIMAL_TRAVEL_RULE = {
    "$schema": "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
    "version": "1.3.0",
    "messageId": "test-pacs008-msg-0001",
    "messageDateTime": "2026-04-05T10:00:00Z",
    "ivms101": {
        "originator": {
            "originatorPersons": [
                {
                    "naturalPerson": {
                        "name": {
                            "nameIdentifier": [
                                {
                                    "primaryIdentifier": "Tanaka",
                                    "secondaryIdentifier": "Hiroshi",
                                    "nameIdentifierType": "LEGL",
                                }
                            ]
                        },
                        "nationalIdentification": {
                            "nationalIdentifier": "JP-MYNUMBER-1234",
                            "nationalIdentifierType": "TXID",
                            "countryOfIssue": "JP",
                        },
                        "dateAndPlaceOfBirth": {
                            "dateOfBirth": "1985-03-22",
                            "placeOfBirth": "Tokyo",
                            "countryOfBirth": "JP",
                        },
                        "geographicAddresses": [
                            {
                                "streetName": "Roppongi Hills Mori Tower",
                                "buildingNumber": "6-10-1",
                                "postCode": "106-6108",
                                "townName": "Tokyo",
                                "country": "JP",
                            }
                        ],
                        "countryOfResidence": "JP",
                    }
                }
            ],
            "accountNumber": ["bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"],
        },
        "beneficiary": {
            "beneficiaryPersons": [
                {
                    "naturalPerson": {
                        "name": {
                            "nameIdentifier": [
                                {
                                    "primaryIdentifier": "Kim",
                                    "secondaryIdentifier": "Ji-Yeon",
                                    "nameIdentifierType": "LEGL",
                                }
                            ]
                        },
                        "countryOfResidence": "KR",
                    }
                }
            ],
            "accountNumber": ["bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqzk5jj0"],
        },
        "originatingVASP": {
            "name": "Tokyo Digital Assets Co., Ltd.",
            "lei": "3538003FPHWP7EM5C773",
        },
        "beneficiaryVASP": {
            "name": "Seoul Blockchain Exchange Inc.",
            "lei": "724500YRI6OZO6ELB439",
        },
        "transferredAmount": {"amount": "1.00", "assetType": "BTC"},
    },
}

LEGAL_ENTITY_PAYLOAD = {
    "$schema": "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
    "version": "1.3.0",
    "messageId": "test-pacs008-le-0001",
    "messageDateTime": "2026-04-05T11:00:00Z",
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
        },
    },
}


# ---------------------------------------------------------------------------
# Test: openkycaml_to_pacs008 — XML structure
# ---------------------------------------------------------------------------


class TestOpenkycamlToPacs008:
    def test_returns_xml_string(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        assert isinstance(xml, str)
        assert xml.startswith("<?xml")

    def test_contains_pacs008_namespace(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        assert "pacs.008" in xml

    def test_message_id_in_xml(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        assert "test-pacs008-msg-0001" in xml

    def test_originator_name_in_xml(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        assert "Hiroshi Tanaka" in xml

    def test_beneficiary_name_in_xml(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        assert "Ji-Yeon Kim" in xml

    def test_originator_account_in_xml(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        assert "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq" in xml

    def test_originating_vasp_lei_in_xml(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        assert "3538003FPHWP7EM5C773" in xml

    def test_beneficiary_vasp_lei_in_xml(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        assert "724500YRI6OZO6ELB439" in xml

    def test_crypto_currency_mapped_to_xxx(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        # BTC is not ISO 4217 → should appear as XXX
        assert 'Ccy="XXX"' in xml or "Ccy='XXX'" in xml

    def test_fiat_currency_mapped_directly(self):
        xml = openkycaml_to_pacs008(LEGAL_ENTITY_PAYLOAD)
        assert 'Ccy="EUR"' in xml or "Ccy='EUR'" in xml

    def test_iban_account_in_iban_element(self):
        xml = openkycaml_to_pacs008(LEGAL_ENTITY_PAYLOAD)
        assert "<IBAN>NL91ABNA0417164300</IBAN>" in xml

    def test_lei_in_orgid_for_legal_entity(self):
        xml = openkycaml_to_pacs008(LEGAL_ENTITY_PAYLOAD)
        assert "724500VNNHZHYDLFMO70" in xml

    def test_splmtrydata_place_and_name(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        assert SPLMTRY_DATA_PLACE_AND_NAME in xml

    def test_splmtrydata_contains_json_envelope(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        # The Envlp element should contain JSON
        assert '"envelopeVersion"' in xml
        assert '"messageRef"' in xml

    def test_envelope_message_ref_matches_message_id(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        # Extract envelope JSON from XML
        match = re.search(r'\{.*"envelopeVersion".*\}', xml, re.DOTALL)
        assert match, "Could not find KYCAMLEnvelope JSON in XML"
        envelope = json.loads(match.group(0))
        assert envelope["messageRef"] == "test-pacs008-msg-0001"

    def test_kycprofile_in_envelope(self):
        xml = openkycaml_to_pacs008(LEGAL_ENTITY_PAYLOAD)
        match = re.search(r'\{.*"envelopeVersion".*\}', xml, re.DOTALL)
        assert match
        envelope = json.loads(match.group(0))
        assert "kycProfile" in envelope
        assert envelope["kycProfile"]["dueDiligenceType"] == "CDD"

    def test_screening_results_in_envelope(self):
        xml = openkycaml_to_pacs008(LEGAL_ENTITY_PAYLOAD)
        match = re.search(r'\{.*"envelopeVersion".*\}', xml, re.DOTALL)
        assert match
        envelope = json.loads(match.group(0))
        assert "screeningResults" in envelope
        assert envelope["screeningResults"]["sanctionsScreening"]["result"] == "CLEAR"

    def test_raises_if_no_ivms101(self):
        with pytest.raises(ValueError, match="ivms101"):
            openkycaml_to_pacs008({"version": "1.3.0"})

    def test_date_of_birth_in_xml(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        assert "1985-03-22" in xml

    def test_custom_settlement_method(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE, message_config={"settlement_method": "INGA"})
        assert "<SttlmMtd>INGA</SttlmMtd>" in xml

    def test_beneficiary_vasp_name_in_xml(self):
        xml = openkycaml_to_pacs008(MINIMAL_TRAVEL_RULE)
        assert "Seoul Blockchain Exchange Inc." in xml


# ---------------------------------------------------------------------------
# Test: iso20022_to_openkycaml — round-trip
# ---------------------------------------------------------------------------


class TestIso20022ToOpenkycaml:
    def _get_xml(self, payload=None):
        return openkycaml_to_pacs008(payload or MINIMAL_TRAVEL_RULE)

    def test_returns_dict(self):
        xml = self._get_xml()
        result = iso20022_to_openkycaml(xml)
        assert isinstance(result, dict)

    def test_message_id_preserved(self):
        xml = self._get_xml()
        result = iso20022_to_openkycaml(xml)
        assert result["messageId"] == "test-pacs008-msg-0001"

    def test_schema_key_present(self):
        xml = self._get_xml()
        result = iso20022_to_openkycaml(xml)
        assert "$schema" in result
        assert "openkycaml.org" in result["$schema"]

    def test_originator_name_recovered(self):
        xml = self._get_xml()
        result = iso20022_to_openkycaml(xml)
        persons = result["ivms101"]["originator"]["originatorPersons"]
        np = persons[0]["naturalPerson"]
        ids = np["name"]["nameIdentifier"]
        full = ids[0]["secondaryIdentifier"] + " " + ids[0]["primaryIdentifier"]
        assert "Hiroshi" in full and "Tanaka" in full

    def test_beneficiary_name_recovered(self):
        xml = self._get_xml()
        result = iso20022_to_openkycaml(xml)
        persons = result["ivms101"]["beneficiary"]["beneficiaryPersons"]
        np = persons[0]["naturalPerson"]
        ids = np["name"]["nameIdentifier"]
        full = ids[0]["secondaryIdentifier"] + " " + ids[0]["primaryIdentifier"]
        assert "Ji-Yeon" in full and "Kim" in full

    def test_originator_account_recovered(self):
        xml = self._get_xml()
        result = iso20022_to_openkycaml(xml)
        accounts = result["ivms101"]["originator"]["accountNumber"]
        assert "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq" in accounts

    def test_originating_vasp_lei_recovered(self):
        xml = self._get_xml()
        result = iso20022_to_openkycaml(xml)
        assert result["ivms101"]["originatingVASP"]["lei"] == "3538003FPHWP7EM5C773"

    def test_kycprofile_recovered_from_envelope(self):
        xml = self._get_xml(LEGAL_ENTITY_PAYLOAD)
        result = iso20022_to_openkycaml(xml)
        assert "kycProfile" in result
        assert result["kycProfile"]["dueDiligenceType"] == "CDD"
        assert result["kycProfile"]["customerRiskRating"]["overallRiskRating"] == "LOW"

    def test_iban_account_recovered(self):
        xml = self._get_xml(LEGAL_ENTITY_PAYLOAD)
        result = iso20022_to_openkycaml(xml)
        accounts = result["ivms101"]["originator"]["accountNumber"]
        assert "NL91ABNA0417164300" in accounts

    def test_legal_entity_lei_recovered(self):
        xml = self._get_xml(LEGAL_ENTITY_PAYLOAD)
        result = iso20022_to_openkycaml(xml)
        persons = result["ivms101"]["originator"]["originatorPersons"]
        lp = persons[0]["legalPerson"]
        assert lp["nationalIdentification"]["nationalIdentifier"] == "724500VNNHZHYDLFMO70"
        assert lp["nationalIdentification"]["nationalIdentifierType"] == "LEIX"

    def test_transfer_amount_recovered(self):
        xml = self._get_xml(LEGAL_ENTITY_PAYLOAD)
        result = iso20022_to_openkycaml(xml)
        assert result["ivms101"]["transferredAmount"]["amount"] == "250000.00"


# ---------------------------------------------------------------------------
# Test: KYCAMLEnvelope schema validation (optional — requires jsonschema)
# ---------------------------------------------------------------------------


class TestKycAmlEnvelopeSchemaValidation:
    @pytest.fixture
    def envelope_schema(self):
        schema_path = (
            REPO_ROOT
            / "iso20022-integration"
            / "supplementary-data"
            / "kyc-aml-envelope-schema.json"
        )
        with open(schema_path, encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture
    def reference_envelope(self):
        envelope_path = (
            REPO_ROOT
            / "iso20022-integration"
            / "supplementary-data"
            / "openkycaml-kyc-envelope-v1.0.0.json"
        )
        with open(envelope_path, encoding="utf-8") as f:
            return json.load(f)

    def test_reference_envelope_validates_against_schema(self, envelope_schema, reference_envelope):
        try:
            import jsonschema
        except ImportError:
            pytest.skip("jsonschema not installed")

        jsonschema.validate(instance=reference_envelope, schema=envelope_schema)

    def test_generated_envelope_validates_against_schema(self, envelope_schema):
        try:
            import jsonschema
        except ImportError:
            pytest.skip("jsonschema not installed")

        xml = openkycaml_to_pacs008(LEGAL_ENTITY_PAYLOAD)
        match = re.search(r'\{.*"envelopeVersion".*\}', xml, re.DOTALL)
        assert match, "Could not find KYCAMLEnvelope JSON in XML"
        envelope = json.loads(match.group(0))
        jsonschema.validate(instance=envelope, schema=envelope_schema)

    def test_envelope_requires_envelope_version(self, envelope_schema):
        try:
            import jsonschema
        except ImportError:
            pytest.skip("jsonschema not installed")

        invalid = {"messageRef": "MSG-001"}  # missing envelopeVersion
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid, schema=envelope_schema)

    def test_envelope_requires_message_ref(self, envelope_schema):
        try:
            import jsonschema
        except ImportError:
            pytest.skip("jsonschema not installed")

        invalid = {"envelopeVersion": "1.0.0"}  # missing messageRef
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid, schema=envelope_schema)

    def test_sar_restricted_requires_tipping_off_protected(self, envelope_schema):
        try:
            import jsonschema
        except ImportError:
            pytest.skip("jsonschema not installed")

        # sar_restricted without tippingOffProtected=true should fail the `if/then`
        invalid_sar = {
            "envelopeVersion": "1.0.0",
            "messageRef": "MSG-001",
            "gdprSensitivityMetadata": {
                "classification": "sar_restricted",
                "tippingOffProtected": False,  # must be true
                "legalBasis": "AMLR-Art73",
                "retentionPeriod": "P5Y",
                "disclosurePolicy": {"allowedRecipients": [], "prohibitedRecipients": ["data_subject"]},
            },
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_sar, schema=envelope_schema)
