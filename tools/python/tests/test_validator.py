"""
Tests for tools/python/validator.py
=====================================
Covers:
- Schema-level validation (valid and invalid payloads)
- All business-logic warning paths
- validate_file() helper
"""

from __future__ import annotations

import datetime
import json
import pathlib
import sys
import tempfile

import pytest

# Make sure the tools/python package is importable when running pytest from
# any working directory.
_TOOLS_PYTHON = pathlib.Path(__file__).resolve().parents[1]
if str(_TOOLS_PYTHON) not in sys.path:
    sys.path.insert(0, str(_TOOLS_PYTHON))

from validator import OpenKYCAMLValidator, ValidationResult

EXAMPLES_DIR = pathlib.Path(__file__).resolve().parents[3] / "examples"

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MINIMAL_VALID_PAYLOAD = {
    "$schema": "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
    "version": "1.3.0",
    "messageId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "messageDateTime": "2026-01-01T00:00:00Z",
    "ivms101": {
        "originator": {
            "originatorPersons": [
                {
                    "naturalPerson": {
                        "name": {
                            "nameIdentifier": [
                                {
                                    "primaryIdentifier": "Smith",
                                    "secondaryIdentifier": "Jane",
                                    "nameIdentifierType": "LEGL",
                                }
                            ]
                        },
                        "nationalIdentification": {
                            "nationalIdentifier": "DE-123456789",
                            "nationalIdentifierType": "CCPT",
                        },
                        "countryOfResidence": "DE",
                    }
                }
            ],
            "accountNumber": ["0xABCDEF1234567890ABCDEF1234567890ABCDEF12"],
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
            "accountNumber": ["0x9876543210ABCDEF9876543210ABCDEF98765432"],
        },
        "originatingVASP": {
            "vasp": {
                "legalPerson": {
                    "name": {
                        "nameIdentifier": [
                            {
                                "legalPersonName": "Acme Crypto Exchange BV",
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
        "beneficiaryVASP": {
            "vasp": {
                "legalPerson": {
                    "name": {
                        "nameIdentifier": [
                            {
                                "legalPersonName": "Fintech Exchange Ltd",
                                "legalPersonNameIdentifierType": "LEGL",
                            }
                        ]
                    },
                    "nationalIdentification": {
                        "nationalIdentifier": "213800QILIUD4ROSUO03",
                        "nationalIdentifierType": "LEIX",
                    },
                    "countryOfRegistration": "GB",
                }
            }
        },
        "transferredAmount": {"amount": "1.5", "assetType": "ETH"},
    },
}


@pytest.fixture
def validator() -> OpenKYCAMLValidator:
    return OpenKYCAMLValidator()


@pytest.fixture
def valid_payload() -> dict:
    import copy
    return copy.deepcopy(MINIMAL_VALID_PAYLOAD)


# ---------------------------------------------------------------------------
# Schema-level validation tests
# ---------------------------------------------------------------------------


class TestSchemaValidation:
    def test_valid_minimal_payload_passes(self, validator, valid_payload):
        result = validator.validate(valid_payload)
        assert result.is_valid is True
        assert result.errors == []

    def test_missing_required_fields_fails(self, validator):
        result = validator.validate({"version": "1.3.0"})
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_invalid_version_pattern_fails(self, validator, valid_payload):
        valid_payload["version"] = "not-semver"
        result = validator.validate(valid_payload)
        assert result.is_valid is False

    def test_result_has_version(self, validator, valid_payload):
        result = validator.validate(valid_payload)
        assert result.payload_version == "1.3.0"

    def test_errors_is_always_list(self, validator, valid_payload):
        result = validator.validate(valid_payload)
        assert isinstance(result.errors, list)

    def test_empty_dict_fails(self, validator):
        result = validator.validate({})
        assert result.is_valid is False

    def test_validate_file_with_known_good_example(self, validator):
        example = EXAMPLES_DIR / "minimal-travel-rule.json"
        if not example.exists():
            pytest.skip("Example file not found")
        result = validator.validate_file(example)
        assert result.is_valid is True, f"Expected valid: {result.errors}"

    def test_validate_file_with_tempfile_invalid_payload(self, validator):
        invalid = {"version": "1.3.0", "messageId": "bad"}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp:
            json.dump(invalid, tmp)
            tmp_path = pathlib.Path(tmp.name)
        try:
            result = validator.validate_file(tmp_path)
            assert result.is_valid is False
        finally:
            tmp_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Business-logic warning tests
# ---------------------------------------------------------------------------


class TestBusinessWarnings:
    def test_no_warnings_for_minimal_valid_payload(self, validator, valid_payload):
        result = validator.validate(valid_payload)
        assert result.warnings == []

    def test_warning_missing_originating_vasp(self, validator, valid_payload):
        # originatingVASP is required by the schema, so removing it produces a
        # schema error rather than a business warning. The test confirms this
        # (schema-level enforcement supersedes the business-logic warning).
        del valid_payload["ivms101"]["originatingVASP"]
        result = validator.validate(valid_payload)
        assert result.is_valid is False
        assert any("originatingVASP" in str(e) for e in result.errors)

    def test_warning_legal_entity_without_ubo(self, validator, valid_payload):
        # Replace natural person originator with legal person
        valid_payload["ivms101"]["originator"]["originatorPersons"] = [
            {
                "legalPerson": {
                    "name": {
                        "nameIdentifier": [
                            {
                                "legalPersonName": "TestCorp Ltd",
                                "legalPersonNameIdentifierType": "LEGL",
                            }
                        ]
                    },
                    "nationalIdentification": {
                        "nationalIdentifier": "529900T8BM49AURSDO55",
                        "nationalIdentifierType": "LEIX",
                    },
                    "countryOfRegistration": "DE",
                }
            }
        ]
        # No kycProfile.beneficialOwnership set
        result = validator.validate(valid_payload)
        assert any("beneficialOwnership" in w for w in result.warnings)

    def test_warning_pep_without_edd(self, validator, valid_payload):
        valid_payload["kycProfile"] = {
            "customerRiskRating": "HIGH",
            "dueDiligenceType": "SDD",
            "pepStatus": {
                "isPEP": True,
                "pepCategory": "DOMESTIC_PEP",
                "screeningDate": "2026-01-01",
                "screeningProvider": "TestProvider",
            },
        }
        result = validator.validate(valid_payload)
        assert any("PEP" in w or "EDD" in w for w in result.warnings)

    def test_warning_stale_sanctions_screening(self, validator, valid_payload):
        # Set screening date to 60 days ago
        stale_date = (
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=60)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        valid_payload["kycProfile"] = {
            "customerRiskRating": "LOW",
            "dueDiligenceType": "SDD",
            "sanctionsScreening": {
                "screeningStatus": "CLEAR",
                "screeningDate": stale_date,
                "screeningProvider": "TestProvider",
                "listsChecked": ["OFAC_SDN"],
            },
        }
        result = validator.validate(valid_payload)
        assert any("screeningDate" in w or "re-screening" in w for w in result.warnings)

    def test_no_stale_warning_for_recent_screening(self, validator, valid_payload):
        recent_date = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        valid_payload["kycProfile"] = {
            "customerRiskRating": "LOW",
            "dueDiligenceType": "SDD",
            "sanctionsScreening": {
                "screeningStatus": "CLEAR",
                "screeningDate": recent_date,
                "screeningProvider": "TestProvider",
                "listsChecked": ["OFAC_SDN"],
            },
        }
        result = validator.validate(valid_payload)
        assert not any("screeningDate" in w for w in result.warnings)

    def test_warning_tipping_off_mismatch_sar_restricted(self, validator, valid_payload):
        valid_payload["gdprSensitivityMetadata"] = {
            "classification": "sar_restricted",
            "tippingOffProtected": False,
            "legalBasis": "AMLR-Art73",
            "retentionPeriod": "P5Y",
        }
        result = validator.validate(valid_payload)
        assert any("tippingOffProtected" in w for w in result.warnings)

    def test_warning_tipping_off_mismatch_internal_suspicion(
        self, validator, valid_payload
    ):
        valid_payload["gdprSensitivityMetadata"] = {
            "classification": "internal_suspicion",
            "tippingOffProtected": False,
            "legalBasis": "AMLR-Art73",
            "retentionPeriod": "P5Y",
        }
        result = validator.validate(valid_payload)
        assert any("tippingOffProtected" in w for w in result.warnings)

    def test_no_tipping_off_warning_when_flag_set(self, validator, valid_payload):
        valid_payload["gdprSensitivityMetadata"] = {
            "classification": "sar_restricted",
            "tippingOffProtected": True,
            "legalBasis": "AMLR-Art73",
            "retentionPeriod": "P5Y",
        }
        result = validator.validate(valid_payload)
        assert not any("tippingOffProtected" in w for w in result.warnings)
