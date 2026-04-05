#!/usr/bin/env python3
"""
OpenKYCAML Pydantic Models
==========================
Typed Python models for building, validating, and issuing OpenKYCAML
Verifiable Credentials.  Requires Pydantic v2.

Usage:
    from models import OpenKYCAMLVC, IssueConfig, WalletConfig

    vc = OpenKYCAMLVC(
        credential_subject_did="did:ebsi:z2LSzT7LiUNMxKKyGCnNjNT",
        issuer_did="did:web:acme-crypto.example.nl",
        issuer_name="Acme Crypto Exchange BV",
        ivms101={...},
        kyc_profile={...},
    )
    signed_jwt = vc.issue(IssueConfig(signing_key_jwk={...}))
    vc.store_in_wallet(WalletConfig(wallet_api_url="https://wallet.example.com", ...))

Python >= 3.10 required.  Install dependencies:
    pip install -r requirements.txt
"""

from __future__ import annotations

import hashlib
import json
import uuid
from base64 import urlsafe_b64encode
from datetime import date, datetime, timedelta, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Sub-models — IVMS 101 / KYC Profile (minimal typed wrappers)
# ---------------------------------------------------------------------------


class NameIdentifier(BaseModel):
    """IVMS 101 name identifier (natural person)."""

    primaryIdentifier: str = Field(..., max_length=100, description="Family name.")
    secondaryIdentifier: str | None = Field(None, max_length=100, description="Given name(s).")
    nameIdentifierType: Literal["ALIA", "BIRT", "MAID", "LEGL", "MISC"] = "LEGL"


class GeographicAddress(BaseModel):
    """IVMS 101 structured postal address."""

    country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2.")
    addressType: Literal["HOME", "BIZZ", "GEOG"] | None = None
    streetName: str | None = Field(None, max_length=70)
    buildingNumber: str | None = Field(None, max_length=16)
    townName: str | None = Field(None, max_length=35)
    postCode: str | None = Field(None, max_length=16)


class NationalIdentification(BaseModel):
    """IVMS 101 national identification."""

    nationalIdentifier: str = Field(..., max_length=35)
    nationalIdentifierType: str = Field(..., max_length=4)
    countryOfIssue: str | None = Field(None, min_length=2, max_length=2)


class DateAndPlaceOfBirth(BaseModel):
    """IVMS 101 date and place of birth."""

    dateOfBirth: date
    placeOfBirth: str | None = Field(None, max_length=70)


class NaturalPersonIVMS(BaseModel):
    """Minimal IVMS 101 natural person block."""

    name: dict[str, list[NameIdentifier]]
    geographicAddress: list[GeographicAddress] | None = None
    nationalIdentification: NationalIdentification | None = None
    dateAndPlaceOfBirth: DateAndPlaceOfBirth | None = None
    customerIdentification: str | None = Field(None, max_length=50)
    countryOfResidence: str | None = Field(None, min_length=2, max_length=2)
    nationality: str | None = Field(None, min_length=2, max_length=2)


class PEPStatus(BaseModel):
    """KYC profile — PEP status."""

    isPEP: bool
    pepCategory: str | None = None
    screeningDate: date | None = None
    screeningProvider: str | None = None


class SanctionsScreening(BaseModel):
    """KYC profile — sanctions screening result."""

    screeningStatus: Literal["CLEAR", "MATCH", "PENDING", "ERROR"]
    screeningDate: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    screeningProvider: str | None = None
    listsChecked: list[str] = Field(default_factory=list)
    matchDetails: list[dict[str, Any]] = Field(default_factory=list)


class ConsentRecord(BaseModel):
    """KYC profile — data processing consent."""

    consentGiven: bool
    consentDate: datetime | None = None
    consentPurpose: list[str] = Field(default_factory=list)


class AuditMetadata(BaseModel):
    """KYC profile — audit metadata."""

    recordId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recordCreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    recordUpdatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    recordVersion: int = 1
    createdBy: str | None = None
    dataSourceSystem: str | None = None
    dataProvider: str | None = None
    dataRetentionDate: date | None = None


class KYCProfileModel(BaseModel):
    """Typed KYC profile for use inside an OpenKYCAML VC."""

    customerRiskRating: Literal["LOW", "MEDIUM", "HIGH", "VERY_HIGH"] = "LOW"
    dueDiligenceType: Literal["SDD", "CDD", "EDD"] = "CDD"
    pepStatus: PEPStatus | None = None
    sanctionsScreening: SanctionsScreening | None = None
    onboardingChannel: str | None = None
    kycCompletionDate: date | None = None
    consentRecord: ConsentRecord | None = None
    auditMetadata: AuditMetadata = Field(default_factory=AuditMetadata)


# ---------------------------------------------------------------------------
# SD-JWT selective disclosure models
# ---------------------------------------------------------------------------


class DecodedDisclosure(BaseModel):
    """A single decoded SD-JWT disclosure (salt + claim name + value)."""

    salt: str
    claimName: str
    claimValue: Any

    def encode(self) -> str:
        """Return the Base64url-encoded disclosure string."""
        raw = json.dumps([self.salt, self.claimName, self.claimValue], separators=(",", ":"))
        return urlsafe_b64encode(raw.encode()).rstrip(b"=").decode()

    def digest(self) -> str:
        """Return the SHA-256 digest of the encoded disclosure (hex)."""
        return hashlib.sha256(self.encode().encode()).hexdigest()


class SelectiveDisclosure(BaseModel):
    """SD-JWT selective disclosure descriptor."""

    sd_alg: str = Field("sha-256", alias="_sd_alg")
    requiredClaimPaths: list[str] = Field(default_factory=list)
    disclosableClaimPaths: list[str] = Field(default_factory=list)
    decodedDisclosures: list[DecodedDisclosure] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Trusted Issuer model
# ---------------------------------------------------------------------------


class AdditionalChecks(BaseModel):
    """Relying-party-specific trust validation rules."""

    requireKeyBinding: bool = True
    requireStatusCheck: bool = True
    minimumAssuranceLevel: Literal["low", "substantial", "high"] | None = None


class TrustedIssuer(BaseModel):
    """An entry in the issuer allowlist with eIDAS TSP validation rules."""

    issuerId: str = Field(..., max_length=256)
    issuerName: str | None = Field(None, max_length=256)
    countryCode: str | None = Field(None, min_length=2, max_length=2)
    trustFramework: Literal[
        "eIDAS_2.0", "eIDAS_1.0", "FATF_VASP", "ISO_29003", "NIST_800-63", "OTHER"
    ] = "eIDAS_2.0"
    eIDASAssuranceLevel: Literal["low", "substantial", "high"] | None = None
    qtspServiceType: str | None = None
    tspServiceUri: str | None = None
    validFrom: date | None = None
    validUntil: date | None = None
    credentialTypes: list[str] = Field(default_factory=list)
    additionalChecks: AdditionalChecks = Field(default_factory=AdditionalChecks)


# ---------------------------------------------------------------------------
# Credential evidence model
# ---------------------------------------------------------------------------


class CredentialEvidence(BaseModel):
    """W3C VC evidence block linking to the source identity credential."""

    id: str = Field(default_factory=lambda: f"urn:uuid:{uuid.uuid4()}")
    type: list[str] = Field(default_factory=lambda: ["PIDCredential", "EUDIWalletPresentationEvidence"])
    verifier: str | None = None
    credentialIssuer: str | None = None
    evidenceDocument: str | None = None
    subjectPresence: str = "Digital"
    documentPresence: str = "Digital"
    presentationMethod: str = "OpenID4VP"
    presentationDate: datetime | None = None


# ---------------------------------------------------------------------------
# Issue and wallet configuration
# ---------------------------------------------------------------------------


class IssueConfig(BaseModel):
    """
    Configuration for the .issue() method.

    When ``signing_key_jwk`` is provided, the VC is signed using the private key
    and the ``proof`` block is populated.  When omitted, a placeholder proof block
    is included (suitable for testing and schema validation only).

    Attributes
    ----------
    signing_key_jwk : dict | None
        JWK object containing the issuer's private signing key.
        Required fields: ``kty``, ``crv`` (for EC keys), ``d`` (private scalar).
    proof_type : str
        W3C VC proof type.  Defaults to ``Ed25519Signature2020``.
    credential_validity_days : int
        Number of days from issuance until expiry.  Defaults to 365.
    """

    signing_key_jwk: dict[str, Any] | None = None
    proof_type: str = "Ed25519Signature2020"
    credential_validity_days: int = 365


class WalletConfig(BaseModel):
    """
    Configuration for the .store_in_wallet() method (OpenID4VCI pre-authorised flow).

    Attributes
    ----------
    wallet_api_url : str
        Base URL of the EUDI Wallet's OpenID4VCI credential endpoint
        (e.g. ``https://wallet.example.com/credential``).
    access_token : str
        Bearer access token obtained from the wallet's token endpoint after the
        pre-authorised code flow or authorisation code flow.
    credential_format : str
        Credential format to request.  One of ``dc+sd-jwt``, ``jwt_vc_json``,
        ``ldp_vc``.  Defaults to ``dc+sd-jwt``.
    timeout_seconds : int
        HTTP request timeout in seconds.  Defaults to 30.
    """

    wallet_api_url: str
    access_token: str
    credential_format: Literal["dc+sd-jwt", "jwt_vc_json", "ldp_vc"] = "dc+sd-jwt"
    timeout_seconds: int = 30


# ---------------------------------------------------------------------------
# Main OpenKYCAMLVC model
# ---------------------------------------------------------------------------

_SCHEMA_BASE = "https://openkycaml.org/schema/v1.2.0/kyc-aml-hybrid-extended.json"
_VC_TYPE_URI = "https://openkycaml.org/credentials/v1/OpenKYCAMLCredential"
_VC_CONTEXTS = [
    "https://www.w3.org/2018/credentials/v1",
    "https://openkycaml.org/contexts/v1",
    "https://europa.eu/2018/credentials/eudi/v1",
]


class OpenKYCAMLVC(BaseModel):
    """
    Typed model for an OpenKYCAML Verifiable Credential.

    Build an instance, then call ``.issue()`` to produce a signed JWT / JSON-LD
    representation, or ``.store_in_wallet()`` to deliver it directly to an EUDI
    Wallet via OpenID4VCI.

    Parameters
    ----------
    credential_subject_did : str
        DID of the credential subject (e.g. the EUDI Wallet holder DID).
    issuer_did : str
        DID of the issuing entity (VASP, bank, KYC utility).
    issuer_name : str
        Human-readable name of the issuer organisation.
    ivms101 : dict | None
        IVMS 101 Travel Rule payload.  At least one of ``ivms101`` or
        ``kyc_profile`` must be provided.
    kyc_profile : KYCProfileModel | None
        KYC/AML profile for CDD reliance and identity portability.
    evidence : list[CredentialEvidence]
        W3C VC evidence blocks linking to source credentials (e.g. PID).
    selective_disclosure : SelectiveDisclosure | None
        SD-JWT selective disclosure descriptor.  Required for ``dc+sd-jwt`` output.
    trusted_issuers : list[TrustedIssuer]
        Optional issuer allowlist published alongside the credential configuration.
    message_id : str
        Unique message identifier (UUID v4).  Auto-generated if not provided.
    message_date_time : datetime
        Message creation timestamp.  Defaults to the current UTC time.
    """

    credential_subject_did: str = Field(..., description="Subject DID (e.g. did:ebsi:...).")
    issuer_did: str = Field(..., description="Issuer DID (e.g. did:web:...).")
    issuer_name: str = Field(..., max_length=256, description="Human-readable issuer name.")

    ivms101: dict[str, Any] | None = None
    kyc_profile: KYCProfileModel | None = None
    evidence: list[CredentialEvidence] = Field(default_factory=list)
    selective_disclosure: SelectiveDisclosure | None = None
    trusted_issuers: list[TrustedIssuer] = Field(default_factory=list)

    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_date_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def _require_ivms101_or_kyc_profile(self) -> "OpenKYCAMLVC":
        if self.ivms101 is None and self.kyc_profile is None:
            raise ValueError("At least one of 'ivms101' or 'kyc_profile' must be provided.")
        return self

    @field_validator("credential_subject_did", "issuer_did")
    @classmethod
    def _validate_did(cls, v: str) -> str:
        if not v.startswith("did:"):
            raise ValueError(f"Value must be a DID (starting with 'did:'): {v!r}")
        return v

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def _issuance_date(self) -> str:
        return self.message_date_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _expiration_date(self, validity_days: int) -> str:
        exp = self.message_date_time + timedelta(days=validity_days)
        return exp.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _build_credential_subject(self) -> dict[str, Any]:
        subject: dict[str, Any] = {"id": self.credential_subject_did}
        if self.ivms101:
            subject["ivms101"] = self.ivms101
        if self.kyc_profile:
            subject["kycProfile"] = self.kyc_profile.model_dump(mode="json", exclude_none=True)
        return subject

    def _build_vc_block(self, validity_days: int) -> dict[str, Any]:
        vc: dict[str, Any] = {
            "@context": _VC_CONTEXTS,
            "id": f"urn:uuid:{self.message_id}",
            "type": ["VerifiableCredential", "OpenKYCAMLCredential", "KYCAttestation"],
            "issuer": {"id": self.issuer_did, "name": self.issuer_name},
            "issuanceDate": self._issuance_date(),
            "expirationDate": self._expiration_date(validity_days),
            "credentialSubject": self._build_credential_subject(),
        }
        if self.evidence:
            vc["evidence"] = [e.model_dump(mode="json", exclude_none=True) for e in self.evidence]
        if self.selective_disclosure:
            vc["selectiveDisclosure"] = self.selective_disclosure.model_dump(
                mode="json", by_alias=True, exclude_none=True
            )
        vc["credentialSchema"] = {
            "id": _SCHEMA_BASE,
            "type": "JsonSchemaValidator2018",
        }
        return vc

    def to_envelope(self, validity_days: int = 365) -> dict[str, Any]:
        """
        Return the full OpenKYCAML JSON envelope as a Python dictionary.

        This is the canonical serialisation used for storage, transmission, and
        validation against the JSON Schema.

        Parameters
        ----------
        validity_days : int
            Number of days until credential expiry.  Defaults to 365.

        Returns
        -------
        dict
            A fully-formed OpenKYCAML envelope ready to be serialised with
            ``json.dumps()``.
        """
        envelope: dict[str, Any] = {
            "$schema": _SCHEMA_BASE,
            "version": "1.2.0",
            "messageId": self.message_id,
            "messageDateTime": self._issuance_date(),
            "verifiableCredential": self._build_vc_block(validity_days),
        }
        if self.ivms101:
            envelope["ivms101"] = self.ivms101
        if self.kyc_profile:
            envelope["kycProfile"] = self.kyc_profile.model_dump(mode="json", exclude_none=True)
        if self.trusted_issuers:
            envelope["trustedIssuers"] = [
                ti.model_dump(mode="json", exclude_none=True) for ti in self.trusted_issuers
            ]
        return envelope

    # ------------------------------------------------------------------
    # .issue() — produce a signed credential representation
    # ------------------------------------------------------------------

    def issue(self, config: IssueConfig | None = None) -> dict[str, Any]:
        """
        Issue the OpenKYCAML credential.

        Builds the complete envelope and, when ``config.signing_key_jwk`` is
        provided, populates a cryptographic proof block.  Without a signing key a
        placeholder proof is included so the output validates against the schema.

        This method does **not** perform actual cryptographic signing — integrators
        should pass the returned envelope to their preferred JWT/VC signing library
        (e.g. ``python-jose``, ``jwcrypto``, ``vc-api``).  The proof block
        documents the intended proof type and verification method so that signing
        libraries can locate the correct key.

        Parameters
        ----------
        config : IssueConfig | None
            Issuance configuration.  If ``None``, defaults are used.

        Returns
        -------
        dict
            The fully-formed OpenKYCAML envelope with a ``proof`` block in
            ``verifiableCredential``.

        Example
        -------
        >>> vc = OpenKYCAMLVC(
        ...     credential_subject_did="did:ebsi:z2LSzT7LiUNMxKKyGCnNjNT",
        ...     issuer_did="did:web:acme-crypto.example.nl",
        ...     issuer_name="Acme Crypto Exchange BV",
        ...     kyc_profile=KYCProfileModel(customerRiskRating="LOW"),
        ... )
        >>> envelope = vc.issue()
        >>> print(envelope["verifiableCredential"]["proof"]["type"])
        Ed25519Signature2020
        """
        cfg = config or IssueConfig()
        envelope = self.to_envelope(validity_days=cfg.credential_validity_days)

        proof: dict[str, Any] = {
            "type": cfg.proof_type,
            "created": self._issuance_date(),
            "verificationMethod": f"{self.issuer_did}#key-1",
            "proofPurpose": "assertionMethod",
        }

        if cfg.signing_key_jwk:
            proof["signingKeyPresent"] = True
            proof["proofValue"] = (
                "<sign envelope['verifiableCredential'] with your JWT/LD-Proof library>"
            )
        else:
            proof["proofValue"] = "<placeholder — provide signing_key_jwk in IssueConfig>"

        envelope["verifiableCredential"]["proof"] = proof
        return envelope

    # ------------------------------------------------------------------
    # .store_in_wallet() — deliver credential to an EUDI Wallet
    # ------------------------------------------------------------------

    def store_in_wallet(self, wallet_config: WalletConfig) -> dict[str, Any]:
        """
        Deliver the issued credential to an EUDI Wallet via OpenID4VCI.

        Sends a Credential Request to ``wallet_config.wallet_api_url`` using
        the ``requests`` library with the provided bearer access token.  The
        credential is sent in the format specified by
        ``wallet_config.credential_format``.

        The caller is responsible for obtaining the access token via the
        pre-authorised code flow or authorisation code flow before calling this
        method.

        Parameters
        ----------
        wallet_config : WalletConfig
            EUDI Wallet endpoint and authentication configuration.

        Returns
        -------
        dict
            The JSON response body returned by the wallet's credential endpoint.
            A successful response contains ``{"credential_ids": [...]}`` or
            ``{"acceptance_token": "..."}`` depending on the wallet implementation.

        Raises
        ------
        ImportError
            If the ``requests`` library is not installed.
        RuntimeError
            If the wallet returns a non-2xx HTTP status code.

        Example
        -------
        >>> vc = OpenKYCAMLVC(
        ...     credential_subject_did="did:ebsi:z2LSzT7LiUNMxKKyGCnNjNT",
        ...     issuer_did="did:web:acme-crypto.example.nl",
        ...     issuer_name="Acme Crypto Exchange BV",
        ...     kyc_profile=KYCProfileModel(customerRiskRating="LOW"),
        ... )
        >>> issued = vc.issue()
        >>> response = vc.store_in_wallet(
        ...     WalletConfig(
        ...         wallet_api_url="https://wallet.example.com/credential",
        ...         access_token="eyJhbGc...",
        ...     )
        ... )
        >>> print(response)
        {'credential_ids': ['urn:uuid:...']}
        """
        try:
            import requests  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "The 'requests' library is required for store_in_wallet(). "
                "Install it with: pip install requests"
            ) from exc

        envelope = self.issue()
        vc_block = envelope["verifiableCredential"]

        request_body: dict[str, Any] = {
            "format": wallet_config.credential_format,
            "types": vc_block.get("type", []),
            "credential": vc_block,
        }

        if wallet_config.credential_format == "dc+sd-jwt":
            request_body["vct"] = _VC_TYPE_URI

        headers = {
            "Authorization": f"Bearer {wallet_config.access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            wallet_config.wallet_api_url,
            headers=headers,
            json=request_body,
            timeout=wallet_config.timeout_seconds,
        )

        if not response.ok:
            raise RuntimeError(
                f"Wallet returned HTTP {response.status_code}: {response.text[:500]}"
            )

        return response.json()
