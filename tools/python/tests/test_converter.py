"""
Tests for tools/python/converter.py
=====================================
Covers:
- ivms101_to_openkycaml / openkycaml_to_ivms101 round-trip
- pid_to_openkycaml / openkycaml_to_pid round-trip
- lpid_to_openkycaml / openkycaml_to_lpid round-trip
- extract_vc
- Error paths (missing blocks)
"""

from __future__ import annotations

import pathlib
import sys

import pytest

_TOOLS_PYTHON = pathlib.Path(__file__).resolve().parents[1]
if str(_TOOLS_PYTHON) not in sys.path:
    sys.path.insert(0, str(_TOOLS_PYTHON))

from converter import (
    extract_vc,
    ivms101_to_openkycaml,
    lpid_to_openkycaml,
    openkycaml_to_ivms101,
    openkycaml_to_lpid,
    openkycaml_to_pid,
    pid_to_openkycaml,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_IVMS101 = {
    "originator": {
        "originatorPersons": [
            {
                "naturalPerson": {
                    "name": {
                        "nameIdentifier": [
                            {
                                "primaryIdentifier": "Müller",
                                "secondaryIdentifier": "Anna",
                                "nameIdentifierType": "LEGL",
                            }
                        ]
                    },
                    "nationalIdentification": {
                        "nationalIdentifier": "DE-987654321",
                        "nationalIdentifierType": "CCPT",
                    },
                    "countryOfResidence": "DE",
                }
            }
        ],
        "accountNumber": ["0xAABBCCDDEEFF00112233445566778899AABBCCDD"],
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
                    }
                }
            }
        ],
        "accountNumber": ["0x1122334455667788990011223344556677889900"],
    },
    "originatingVASP": {
        "vasp": {
            "legalPerson": {
                "name": {
                    "nameIdentifier": [
                        {
                            "legalPersonName": "Acme Exchange BV",
                            "legalPersonNameIdentifierType": "LEGL",
                        }
                    ]
                },
                "nationalIdentification": {
                    "nationalIdentifier": "529900T8BM49AURSDO55",
                    "nationalIdentifierType": "LEIX",
                },
                "countryOfRegistration": "NL",
            }
        }
    },
    "transferredAmount": {"amount": "2.0", "assetType": "BTC"},
}

SAMPLE_PID = {
    "family_name": "Müller",
    "given_name": "Anna",
    "birth_date": "1985-03-15",
    "resident_street": "Unter den Linden 77",
    "resident_city": "Berlin",
    "resident_postal_code": "10117",
    "resident_country": "DE",
    "document_number": "X123456789",
    "issuing_country": "DE",
    "nationality": "DE",
}

SAMPLE_LPID = {
    "current_legal_name": "Acme GmbH",
    "legal_person_identifier": "529900T8BM49AURSDO55",
    "registered_address": "Friedrichstraße 200",
    "country_of_registration": "DE",
    "legal_form_type": "GmbH",
    "registration_number": "HRB 12345",
}


# ---------------------------------------------------------------------------
# IVMS 101 round-trip
# ---------------------------------------------------------------------------


class TestIVMS101RoundTrip:
    def test_wrap_and_unwrap(self):
        envelope = ivms101_to_openkycaml(SAMPLE_IVMS101)
        assert envelope["version"] == "1.3.0"
        assert "messageId" in envelope
        assert "messageDateTime" in envelope
        assert envelope["ivms101"] == SAMPLE_IVMS101

    def test_unwrap_returns_original_ivms(self):
        envelope = ivms101_to_openkycaml(SAMPLE_IVMS101)
        extracted = openkycaml_to_ivms101(envelope)
        assert extracted == SAMPLE_IVMS101

    def test_unwrap_missing_ivms_raises(self):
        with pytest.raises(ValueError, match="ivms101"):
            openkycaml_to_ivms101({"version": "1.3.0"})

    def test_wrapped_envelope_has_schema_field(self):
        envelope = ivms101_to_openkycaml(SAMPLE_IVMS101)
        assert "$schema" in envelope
        assert "openkycaml" in envelope["$schema"].lower()


# ---------------------------------------------------------------------------
# PID round-trip
# ---------------------------------------------------------------------------


class TestPIDRoundTrip:
    def test_pid_to_openkycaml_contains_natural_person(self):
        envelope = pid_to_openkycaml(SAMPLE_PID)
        persons = envelope["ivms101"]["originator"]["originatorPersons"]
        assert len(persons) >= 1
        assert "naturalPerson" in persons[0]

    def test_pid_family_name_mapped(self):
        envelope = pid_to_openkycaml(SAMPLE_PID)
        np = envelope["ivms101"]["originator"]["originatorPersons"][0]["naturalPerson"]
        names = np["name"]["nameIdentifier"]
        assert any(n.get("primaryIdentifier") == "Müller" for n in names)

    def test_pid_dob_mapped(self):
        envelope = pid_to_openkycaml(SAMPLE_PID)
        np = envelope["ivms101"]["originator"]["originatorPersons"][0]["naturalPerson"]
        dob = np.get("dateAndPlaceOfBirth", {}).get("dateOfBirth")
        assert dob == "1985-03-15"

    def test_openkycaml_to_pid_contains_family_name(self):
        envelope = pid_to_openkycaml(SAMPLE_PID)
        pid_out = openkycaml_to_pid(envelope)
        assert pid_out.get("family_name") == "Müller"

    def test_openkycaml_to_pid_missing_natural_person_raises(self):
        # Build an envelope with only a legal person — should raise
        envelope = {
            "version": "1.3.0",
            "ivms101": {
                "originator": {
                    "originatorPersons": [
                        {
                            "legalPerson": {
                                "name": {
                                    "nameIdentifier": [
                                        {
                                            "legalPersonName": "Acme Ltd",
                                            "legalPersonNameIdentifierType": "LEGL",
                                        }
                                    ]
                                },
                                "countryOfRegistration": "DE",
                            }
                        }
                    ]
                }
            },
        }
        with pytest.raises((ValueError, KeyError)):
            openkycaml_to_pid(envelope)


# ---------------------------------------------------------------------------
# LPID round-trip
# ---------------------------------------------------------------------------


class TestLPIDRoundTrip:
    def test_lpid_to_openkycaml_contains_legal_person(self):
        envelope = lpid_to_openkycaml(SAMPLE_LPID)
        persons = envelope["ivms101"]["originator"]["originatorPersons"]
        assert len(persons) >= 1
        assert "legalPerson" in persons[0]

    def test_lpid_legal_name_mapped(self):
        envelope = lpid_to_openkycaml(SAMPLE_LPID)
        lp = envelope["ivms101"]["originator"]["originatorPersons"][0]["legalPerson"]
        names = lp["name"]["nameIdentifier"]
        assert any(n.get("legalPersonName") == "Acme GmbH" for n in names)

    def test_lpid_lei_mapped(self):
        envelope = lpid_to_openkycaml(SAMPLE_LPID)
        lp = envelope["ivms101"]["originator"]["originatorPersons"][0]["legalPerson"]
        lei = lp.get("nationalIdentification", {}).get("nationalIdentifier")
        assert lei == "529900T8BM49AURSDO55"

    def test_openkycaml_to_lpid_round_trip(self):
        envelope = lpid_to_openkycaml(SAMPLE_LPID)
        lpid_out = openkycaml_to_lpid(envelope)
        # The converter uses 'legal_name' as the output key for the legal name
        assert lpid_out.get("legal_name") == "Acme GmbH" or lpid_out.get("current_legal_name") == "Acme GmbH"


# ---------------------------------------------------------------------------
# extract_vc
# ---------------------------------------------------------------------------


class TestExtractVC:
    def test_extract_vc_returns_vc_block(self):
        payload = {
            "version": "1.3.0",
            "verifiableCredential": {
                "@context": ["https://www.w3.org/2018/credentials/v1"],
                "type": ["VerifiableCredential"],
                "issuer": "did:web:example.com",
                "issuanceDate": "2026-01-01T00:00:00Z",
                "credentialSubject": {},
            },
        }
        vc = extract_vc(payload)
        assert "type" in vc
        assert "VerifiableCredential" in vc["type"]

    def test_extract_vc_missing_raises(self):
        with pytest.raises(ValueError, match="verifiableCredential"):
            extract_vc({"version": "1.3.0", "ivms101": {}})
