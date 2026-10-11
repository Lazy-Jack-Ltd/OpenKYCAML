"""
EWC Alignment Fixture Tests
=============================
Validates that the four EWC-ingested example files:
  1. Are schema-valid against kyc-aml-hybrid-extended.json.
  2. Contain the expected EWC-specific fields (eudiPidClaims, eudiLpidClaims,
     eudiUboAttestation, eudiIssuingMetadata, eudiCredentialType, sourceSchemaId).
  3. Preserve the correct EWC credential type identifiers in evidence items.
  4. Have intact IVMS 101 originator / beneficiary data alongside the EWC-native
     claim containers.

These tests act as CI fixtures that will fail if the EWC-aligned fields are
inadvertently removed or renamed during future schema refactoring.
"""

from __future__ import annotations

import json
import pathlib
import sys

import jsonschema
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_SCHEMA_PATH = _REPO_ROOT / "schema" / "kyc-aml-hybrid-extended.json"
_EXAMPLES_DIR = _REPO_ROOT / "examples"

# EWC-ingested example files introduced in v1.20.0
_EWC_EXAMPLES = {
    "pid": _EXAMPLES_DIR / "ewc-ingested-pid.json",
    "lpid": _EXAMPLES_DIR / "ewc-ingested-lpid.json",
    "ubo": _EXAMPLES_DIR / "ewc-ingested-ubo.json",
    "company_signatory": _EXAMPLES_DIR / "ewc-ingested-company-signatory.json",
}

# Expected eudiCredentialType values in the primary evidence item of each example
_EXPECTED_CREDENTIAL_TYPES = {
    "pid": "ds012-person-identification-data",
    "lpid": "ds004-legal-person-identification-data",
    "ubo": "ds006-ultimate-beneficial-owners-attestation",
    "company_signatory": "ds001-eu-company-certificate",
}


@pytest.fixture(scope="module")
def schema():
    with _SCHEMA_PATH.open() as f:
        return json.load(f)


def _load(key: str) -> dict:
    with _EWC_EXAMPLES[key].open() as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# 1. Schema validity
# ---------------------------------------------------------------------------


class TestSchemaValidity:
    """All EWC-ingested examples must be schema-valid."""

    @pytest.mark.parametrize("key", list(_EWC_EXAMPLES))
    def test_example_is_schema_valid(self, schema, key):
        data = _load(key)
        jsonschema.validate(data, schema)


# ---------------------------------------------------------------------------
# 2. EWC-native claim containers present
# ---------------------------------------------------------------------------


class TestEudiClaimContainers:
    """Each ingested example must carry the appropriate EWC-native claim container."""

    def test_pid_has_eudi_pid_claims(self):
        data = _load("pid")
        cs = data["verifiableCredential"]["credentialSubject"]
        assert "eudiPidClaims" in cs, "eudiPidClaims must be present for PID ingestion"

    def test_pid_eudi_pid_claims_has_core_fields(self):
        data = _load("pid")
        pid = data["verifiableCredential"]["credentialSubject"]["eudiPidClaims"]
        for field in ("family_name", "given_name", "birthdate"):
            assert field in pid, f"eudiPidClaims.{field} must be present"

    def test_pid_has_age_attestation_fields(self):
        data = _load("pid")
        pid = data["verifiableCredential"]["credentialSubject"]["eudiPidClaims"]
        assert "age_over_18" in pid or "age_in_years" in pid, (
            "eudiPidClaims must carry at least one age-attestation field"
        )

    def test_pid_has_structured_birth_place(self):
        data = _load("pid")
        pid = data["verifiableCredential"]["credentialSubject"]["eudiPidClaims"]
        if "birth_place" in pid:
            assert isinstance(pid["birth_place"], dict), "birth_place must be structured"

    def test_lpid_has_eudi_lpid_claims(self):
        data = _load("lpid")
        cs = data["verifiableCredential"]["credentialSubject"]
        assert "eudiLpidClaims" in cs, "eudiLpidClaims must be present for LPID ingestion"

    def test_lpid_eudi_lpid_claims_has_core_fields(self):
        data = _load("lpid")
        lpid = data["verifiableCredential"]["credentialSubject"]["eudiLpidClaims"]
        for field in ("legal_person_name", "country"):
            assert field in lpid, f"eudiLpidClaims.{field} must be present"

    def test_ubo_has_eudi_ubo_attestation(self):
        data = _load("ubo")
        cs = data["verifiableCredential"]["credentialSubject"]
        assert "eudiUboAttestation" in cs, (
            "eudiUboAttestation must be present for UBO attestation ingestion"
        )

    def test_ubo_attestation_has_ubos_list(self):
        data = _load("ubo")
        ubo = data["verifiableCredential"]["credentialSubject"]["eudiUboAttestation"]
        assert "ultimate_beneficial_owner" in ubo and len(ubo["ultimate_beneficial_owner"]) > 0, (
            "eudiUboAttestation must contain at least one UBO"
        )

    def test_ubo_entry_has_ownership_percentage(self):
        data = _load("ubo")
        ubo = data["verifiableCredential"]["credentialSubject"]["eudiUboAttestation"]
        for entry in ubo["ultimate_beneficial_owner"]:
            assert "ownership_details" in entry and len(entry["ownership_details"]) > 0, (
                "Each UBO entry must carry ownership_details"
            )
            assert "ownership_percentage" in entry["ownership_details"][0], (
                "Each UBO ownership_details entry must carry ownership_percentage"
            )


# ---------------------------------------------------------------------------
# 3. Evidence items carry EWC metadata
# ---------------------------------------------------------------------------


class TestEvidenceMetadata:
    """Evidence items in EWC-ingested examples must carry eudiCredentialType,
    sourceSchemaId, and eudiIssuingMetadata."""

    @pytest.mark.parametrize("key", list(_EWC_EXAMPLES))
    def test_evidence_has_eudi_credential_type(self, key):
        data = _load(key)
        evidence = data["verifiableCredential"]["evidence"]
        assert len(evidence) > 0, f"{key}: evidence array must not be empty"
        primary = evidence[0]
        assert "eudiCredentialType" in primary, (
            f"{key}: primary evidence item must have eudiCredentialType"
        )

    @pytest.mark.parametrize("key", list(_EWC_EXAMPLES))
    def test_evidence_credential_type_value(self, key):
        data = _load(key)
        primary = data["verifiableCredential"]["evidence"][0]
        assert primary["eudiCredentialType"] == _EXPECTED_CREDENTIAL_TYPES[key], (
            f"{key}: eudiCredentialType must be '{_EXPECTED_CREDENTIAL_TYPES[key]}'"
        )

    @pytest.mark.parametrize("key", list(_EWC_EXAMPLES))
    def test_evidence_has_source_schema_id(self, key):
        data = _load(key)
        primary = data["verifiableCredential"]["evidence"][0]
        assert "sourceSchemaId" in primary, (
            f"{key}: primary evidence item must have sourceSchemaId"
        )
        assert primary["sourceSchemaId"].startswith("https://"), (
            f"{key}: sourceSchemaId must be an HTTPS URI"
        )

    @pytest.mark.parametrize("key", list(_EWC_EXAMPLES))
    def test_evidence_has_eudi_issuing_metadata(self, key):
        data = _load(key)
        primary = data["verifiableCredential"]["evidence"][0]
        assert "eudiIssuingMetadata" in primary, (
            f"{key}: primary evidence item must have eudiIssuingMetadata"
        )
        meta = primary["eudiIssuingMetadata"]
        for field in ("issuing_authority", "issuing_country", "issuance_date"):
            assert field in meta, (
                f"{key}: eudiIssuingMetadata.{field} must be present"
            )

    @pytest.mark.parametrize("key", list(_EWC_EXAMPLES))
    def test_evidence_issuing_country_is_alpha2(self, key):
        data = _load(key)
        meta = data["verifiableCredential"]["evidence"][0]["eudiIssuingMetadata"]
        country = meta.get("issuing_country", "")
        assert len(country) == 2 and country.isupper(), (
            f"{key}: issuing_country must be an ISO 3166-1 alpha-2 code"
        )


# ---------------------------------------------------------------------------
# 4. IVMS 101 originator data is intact
# ---------------------------------------------------------------------------


class TestIvms101Integrity:
    """EWC-native containers must not replace IVMS 101 data — both must coexist."""

    @pytest.mark.parametrize("key", list(_EWC_EXAMPLES))
    def test_top_level_ivms101_present(self, key):
        data = _load(key)
        assert "ivms101" in data, f"{key}: top-level ivms101 block must be present"

    @pytest.mark.parametrize("key", list(_EWC_EXAMPLES))
    def test_originator_account_present(self, key):
        data = _load(key)
        originator = data["ivms101"]["originator"]
        assert "accountNumber" in originator and len(originator["accountNumber"]) > 0, (
            f"{key}: originator.accountNumber must be present"
        )

    @pytest.mark.parametrize("key", list(_EWC_EXAMPLES))
    def test_credential_subject_ivms101_present(self, key):
        data = _load(key)
        cs = data["verifiableCredential"]["credentialSubject"]
        assert "ivms101" in cs, (
            f"{key}: credentialSubject.ivms101 must be present alongside EWC containers"
        )


# ---------------------------------------------------------------------------
# 5. Schema version is at least 1.20.0
# ---------------------------------------------------------------------------


class TestSchemaVersion:
    """EWC-ingested examples must reference schema version 1.20.0+."""

    @pytest.mark.parametrize("key", list(_EWC_EXAMPLES))
    def test_version_is_1_20_or_later(self, key):
        data = _load(key)
        version = data.get("version", "0.0.0")
        major, minor, _ = (int(x) for x in version.split("."))
        assert (major, minor) >= (1, 20), (
            f"{key}: version must be >= 1.20.0, got {version}"
        )
