# Pydantic Model Documentation

This document describes the Pydantic v2 models in [`tools/python/models.py`](../../tools/python/models.py). These models provide typed Python representations of the OpenKYCAML v1.7.0 schema, along with VC issuance and EUDI Wallet delivery helpers.

> **Requirements:** Python ≥ 3.10, Pydantic v2. Install with:
> ```bash
> pip install -r tools/python/requirements.txt
> ```

---

## Table of Contents

1. [Model Overview](#1-model-overview)
2. [IVMS 101 / Identity Sub-models](#2-ivms-101--identity-sub-models)
3. [KYC Profile Models](#3-kyc-profile-models)
4. [GDPR Sensitivity Models](#4-gdpr-sensitivity-models)
5. [SD-JWT Models](#5-sd-jwt-models)
6. [Trust and Evidence Models](#6-trust-and-evidence-models)
7. [Configuration Models](#7-configuration-models)
8. [OpenKYCAMLVC — Main Model](#8-openkycamlvc--main-model)
9. [Usage Examples](#9-usage-examples)

---

## 1. Model Overview

```
OpenKYCAMLVC
├── ivms101: dict | None               # raw IVMS 101 payload dict
├── kyc_profile: KYCProfileModel       # typed KYC/AML profile
│   ├── pepStatus: PEPStatus
│   ├── sanctionsScreening: SanctionsScreening
│   └── auditMetadata: AuditMetadata
├── evidence: list[CredentialEvidence] # PID / source credential references
├── selective_disclosure: SelectiveDisclosure
│   └── decodedDisclosures: list[DecodedDisclosure]
├── trusted_issuers: list[TrustedIssuer]
│   └── additionalChecks: AdditionalChecks
├── gdpr_sensitivity: GdprSensitivityMetadata
│   ├── consentRecord: GdprConsentRecord
│   └── disclosurePolicy: DisclosurePolicy
├── issuer configuration fields
└── message envelope fields
```

---

## 2. IVMS 101 / Identity Sub-models

### `NameIdentifier`

```python
class NameIdentifier(BaseModel):
    primaryIdentifier: str        # Family name (max 100 chars)
    secondaryIdentifier: str | None  # Given name(s) (max 100 chars)
    nameIdentifierType: Literal["ALIA", "BIRT", "MAID", "LEGL", "MISC"]  # default "LEGL"
```

| Field | Type | Required | Description |
|---|---|---|---|
| `primaryIdentifier` | `str` | ✅ | Family name / surname. Maps to eIDAS PID `family_name`. |
| `secondaryIdentifier` | `str \| None` | ❌ | Given name(s). Maps to eIDAS PID `given_name`. |
| `nameIdentifierType` | enum | ✅ | IVMS 101 name type. Use `LEGL` for legal names. |

---

### `GeographicAddress`

```python
class GeographicAddress(BaseModel):
    country: str             # ISO 3166-1 alpha-2 (required)
    addressType: Literal["HOME", "BIZZ", "GEOG"] | None = None
    streetName: str | None = None   # max 70 chars
    buildingNumber: str | None = None  # max 16 chars
    townName: str | None = None     # max 35 chars
    postCode: str | None = None     # max 16 chars
```

---

### `NationalIdentification`

```python
class NationalIdentification(BaseModel):
    nationalIdentifier: str        # max 35 chars
    nationalIdentifierType: str    # IVMS 101 code, max 4 chars (e.g. "LEIX", "CCPT")
    countryOfIssue: str | None = None  # ISO 3166-1 alpha-2
```

---

### `DateAndPlaceOfBirth`

```python
class DateAndPlaceOfBirth(BaseModel):
    dateOfBirth: date         # Python date object — maps to eIDAS PID birth_date
    placeOfBirth: str | None = None   # max 70 chars
```

---

### `NaturalPersonIVMS`

```python
class NaturalPersonIVMS(BaseModel):
    name: dict[str, list[NameIdentifier]]  # {"nameIdentifier": [...]}
    geographicAddress: list[GeographicAddress] | None = None
    nationalIdentification: NationalIdentification | None = None
    dateAndPlaceOfBirth: DateAndPlaceOfBirth | None = None
    customerIdentification: str | None = None   # max 50 chars
    countryOfResidence: str | None = None        # ISO 3166-1 alpha-2
    nationality: str | None = None               # ISO 3166-1 alpha-2
```

---

## 3. KYC Profile Models

### `PEPStatus`

```python
class PEPStatus(BaseModel):
    isPEP: bool
    pepCategory: str | None = None
    screeningDate: date | None = None
    screeningProvider: str | None = None
```

| Field | Type | Required | Description |
|---|---|---|---|
| `isPEP` | `bool` | ✅ | Whether the subject is classified as a PEP. |
| `pepCategory` | `str \| None` | ❌ | AMLA RTS category (e.g. `DOMESTIC_PEP`, `FOREIGN_PEP`). |
| `screeningDate` | `date \| None` | ❌ | Date of the most recent PEP screening. |
| `screeningProvider` | `str \| None` | ❌ | Data provider name (e.g. `Refinitiv World-Check`). |

---

### `SanctionsScreening`

```python
class SanctionsScreening(BaseModel):
    screeningStatus: Literal["CLEAR", "MATCH", "PENDING", "ERROR"]
    screeningDate: datetime      # Required — must be explicitly set
    screeningProvider: str | None = None
    listsChecked: list[str] = []
    matchDetails: list[dict[str, Any]] = []
```

> **Note:** `screeningDate` is required and must be explicitly provided to avoid misleading audit records.

---

### `ConsentRecord`

```python
class ConsentRecord(BaseModel):
    consentGiven: bool
    consentDate: datetime | None = None
    consentPurpose: list[str] = []
```

---

### `AuditMetadata`

```python
class AuditMetadata(BaseModel):
    recordId: str              # UUID v4, auto-generated
    recordCreatedAt: datetime  # auto-set to utcnow()
    recordUpdatedAt: datetime | None = None   # set on update
    recordVersion: int = 1
    createdBy: str | None = None
    dataSourceSystem: str | None = None
    dataProvider: str | None = None
    dataRetentionDate: date | None = None
```

---

### `KYCProfileModel`

```python
class KYCProfileModel(BaseModel):
    customerRiskRating: Literal["LOW", "MEDIUM", "HIGH", "VERY_HIGH"] = "LOW"
    dueDiligenceType: Literal["SDD", "CDD", "EDD"] = "CDD"
    pepStatus: PEPStatus | None = None
    sanctionsScreening: SanctionsScreening | None = None
    onboardingChannel: str | None = None
    kycCompletionDate: date | None = None
    consentRecord: ConsentRecord | None = None
    auditMetadata: AuditMetadata = Field(default_factory=AuditMetadata)
```

| Field | Default | Description |
|---|---|---|
| `customerRiskRating` | `"LOW"` | Overall CDD risk rating for this customer. |
| `dueDiligenceType` | `"CDD"` | KYC diligence level: `SDD` (simplified), `CDD` (standard), `EDD` (enhanced). |
| `pepStatus` | `None` | PEP screening result. Set when PEP screening is performed. |
| `sanctionsScreening` | `None` | Sanctions list screening result. |
| `onboardingChannel` | `None` | Channel used for onboarding (e.g. `EUDI_WALLET`, `VIDEO_KYC`, `IN_PERSON`). |
| `kycCompletionDate` | `None` | Date KYC was completed. |
| `auditMetadata` | auto | Audit trail metadata (auto-populated). |

> **v1.4.0–v1.7.0 additions:** The JSON Schema `KYCProfile` definition has grown since v1.3.0. The following fields are accepted by the schema validator but are not yet modelled as typed Pydantic fields in `models.py` — pass them via `model_config = {"extra": "allow"}` or as keyword arguments:
>
> | Field | Version | Type | Description |
> |---|---|---|---|
> | `riskRatingDetail` | v1.x | `str` | Narrative risk rating explanation. |
> | `customerClassification` | v1.x | `str` | Customer segment (RETAIL/PROFESSIONAL/INSTITUTIONAL). |
> | `isEligible` | v1.2.0 | `bool` | ERC-3643 / XRPL compliance eligibility gate. |
> | `eligibilityLastConfirmed` | v1.2.0 | `str` | ISO 8601 timestamp of last eligibility check. |
> | `dueDiligenceRequirements` | v1.2.0 | `dict` | AMLA RTS CDD tier requirements. |
> | `thirdPartyCDDReliance` | v1.2.0 | `dict` | Third-party CDD reliance record. |
> | `blockchainAccountIds` | v1.3.0+ | `list[dict]` | Blockchain wallet entries (XRPL, Ethereum, Bitcoin/Lightning). See [TypeScript types](typescript-types.md#4-kyc-profile-types) for the full `BlockchainAccountId` structure. |

---

## 4. GDPR Sensitivity Models

### `GdprConsentRecord`

```python
class GdprConsentRecord(BaseModel):
    consentGiven: bool
    consentDate: datetime | None = None
    withdrawalPossible: bool | None = None

    model_config = {"extra": "forbid"}
```

---

### `DisclosurePolicy`

```python
class DisclosurePolicy(BaseModel):
    allowedRecipients: list[str] = []
    prohibitedRecipients: list[str] = []
    requiresExplicitConsent: bool | None = None

    model_config = {"extra": "forbid"}
```

| Field | Description |
|---|---|
| `allowedRecipients` | Permitted recipient categories or DIDs (e.g. `'regulated_fi'`, `'fiu_only'`). |
| `prohibitedRecipients` | Entities explicitly blocked. Set `'data_subject'` when `tippingOffProtected=True`. |
| `requiresExplicitConsent` | When `True`, recipients must obtain supervisory approval before access. |

---

### `GdprSensitivityMetadata`

```python
class GdprSensitivityMetadata(BaseModel):
    classification: Literal[
        "standard", "sensitive_personal", "criminal_offence",
        "sar_restricted", "internal_suspicion", "confidential_aml",
    ]
    restricted_fields: list[str] = Field(default_factory=list, alias="restrictedFields")
    tipping_off_protected: bool | None = Field(None, alias="tippingOffProtected")
    legal_basis: Literal[
        "GDPR-Art6-1c", "GDPR-Art6-1e", "GDPR-Art9-2g", "GDPR-Art10",
        "AMLR-Art55", "AMLR-Art73", "national_AML_law",
    ] | None = Field(None, alias="legalBasis")
    retention_period: str | None = Field(None, alias="retentionPeriod")  # ISO 8601 duration
    consent_record: GdprConsentRecord | None = Field(None, alias="consentRecord")
    disclosure_policy: DisclosurePolicy | None = Field(None, alias="disclosurePolicy")
    audit_reference: str | None = Field(None, alias="auditReference")   # max 256 chars

    model_config = {"populate_by_name": True, "extra": "forbid"}
```

**Validation rule:** `tippingOffProtected` must be `True` when `classification` is `sar_restricted` or `internal_suspicion` — enforced by a `@model_validator`.

| Classification | When to use |
|---|---|
| `standard` | Normal personal data. |
| `sensitive_personal` | GDPR Art. 9 special category data (health, biometric, etc.). |
| `criminal_offence` | GDPR Art. 10 criminal convictions and offences data. |
| `sar_restricted` | Payload contains or references a Suspicious Activity Report. Set `tippingOffProtected=True`. |
| `internal_suspicion` | Internal suspicion flag not yet escalated to SAR. Set `tippingOffProtected=True`. |
| `confidential_aml` | Confidential AML investigation material. |

---

## 5. SD-JWT Models

### `DecodedDisclosure`

```python
class DecodedDisclosure(BaseModel):
    salt: str          # Random Base64url salt (≥128 bits)
    claimName: str     # JSON Pointer path of the claim
    claimValue: Any    # Plaintext claim value

    def encode(self) -> str: ...       # Returns Base64url-encoded disclosure string
    def digest_hex(self) -> str: ...   # Returns SHA-256 hex digest
```

---

### `SelectiveDisclosure`

```python
class SelectiveDisclosure(BaseModel):
    sd_alg: str = Field("sha-256", alias="_sd_alg")   # Hash algorithm
    requiredClaimPaths: list[str] = []                 # Always revealed (FATF-mandatory)
    disclosableClaimPaths: list[str] = []              # May be withheld
    decodedDisclosures: list[DecodedDisclosure] = []

    model_config = {"populate_by_name": True}
```

---

## 6. Trust and Evidence Models

### `AdditionalChecks`

```python
class AdditionalChecks(BaseModel):
    requireKeyBinding: bool = True
    requireStatusCheck: bool = True
    minimumAssuranceLevel: Literal["low", "substantial", "high"] | None = None
```

---

### `TrustedIssuer`

```python
class TrustedIssuer(BaseModel):
    issuerId: str               # DID or URI (max 256 chars)
    issuerName: str | None = None
    countryCode: str | None = None   # ISO 3166-1 alpha-2
    trustFramework: Literal[
        "eIDAS_2.0", "eIDAS_1.0", "FATF_VASP", "ISO_29003",
        "NIST_800-63", "OTHER"
    ] = "eIDAS_2.0"
    eIDASAssuranceLevel: Literal["low", "substantial", "high"] | None = None
    qtspServiceType: str | None = None
    tspServiceUri: str | None = None
    validFrom: date | None = None
    validUntil: date | None = None
    credentialTypes: list[str] = []
    additionalChecks: AdditionalChecks = Field(default_factory=AdditionalChecks)
```

---

### `CredentialEvidence`

```python
class CredentialEvidence(BaseModel):
    id: str = Field(default_factory=lambda: f"urn:uuid:{uuid.uuid4()}")
    type: list[str] = ["PIDCredential", "EUDIWalletPresentationEvidence"]
    verifier: str | None = None           # DID of the VASP verifier
    credentialIssuer: str | None = None   # DID of the PID Provider
    evidenceDocument: str | None = None
    subjectPresence: str = "Digital"
    documentPresence: str = "Digital"
    presentationMethod: str = "OpenID4VP"
    presentationDate: datetime | None = None
```

---

## 7. Configuration Models

### `IssueConfig`

```python
class IssueConfig(BaseModel):
    signing_key_jwk: dict[str, Any] | None = None  # JWK private key
    proof_type: str = "Ed25519Signature2020"        # W3C VC proof type
    credential_validity_days: int = 365             # Days until expiry
```

When `signing_key_jwk` is provided, the proof block is populated with a placeholder indicating where to insert the signature from your JWT/LD-Proof library.

---

### `WalletConfig`

```python
class WalletConfig(BaseModel):
    wallet_api_url: str                              # OpenID4VCI credential endpoint URL
    access_token: str                                # Bearer token from wallet token endpoint
    credential_format: Literal[
        "dc+sd-jwt", "jwt_vc_json", "ldp_vc"
    ] = "dc+sd-jwt"
    timeout_seconds: int = 30
```

---

## 8. OpenKYCAMLVC — Main Model

```python
class OpenKYCAMLVC(BaseModel):
    # Required identity fields
    credential_subject_did: str     # Subject DID (must start with "did:")
    issuer_did: str                 # Issuer DID (must start with "did:")
    issuer_name: str                # Human-readable issuer name (max 256 chars)

    # Payload — at least one required
    ivms101: dict[str, Any] | None = None
    kyc_profile: KYCProfileModel | None = None

    # Optional enrichment
    evidence: list[CredentialEvidence] = []
    selective_disclosure: SelectiveDisclosure | None = None
    trusted_issuers: list[TrustedIssuer] = []
    gdpr_sensitivity: GdprSensitivityMetadata | None = None

    # Message envelope
    message_id: str            # UUID v4, auto-generated
    message_date_time: datetime  # UTC, auto-generated
```

**Validation rules enforced by Pydantic validators:**

| Rule | Validator |
|---|---|
| At least one of `ivms101` or `kyc_profile` must be provided. | `@model_validator` |
| `credential_subject_did` must start with `"did:"`. | `@field_validator` |
| `issuer_did` must start with `"did:"`. | `@field_validator` |

### Methods

| Method | Returns | Description |
|---|---|---|
| `to_envelope(validity_days=365)` | `dict` | Full OpenKYCAML JSON envelope without a proof block. |
| `issue(config=None)` | `dict` | Envelope with proof block populated (pass `signing_key_jwk` to sign). |
| `store_in_wallet(wallet_config)` | `dict` | Deliver credential to EUDI Wallet via OpenID4VCI (`requests` required). |

---

## 9. Usage Examples

### Minimal Travel Rule VC

```python
from tools.python.models import OpenKYCAMLVC, IssueConfig
import json

vc = OpenKYCAMLVC(
    credential_subject_did="did:ebsi:z2LSzT7LiUNMxKKyGCnNjNT",
    issuer_did="did:web:acme-crypto.example.nl",
    issuer_name="Acme Crypto Exchange BV",
    ivms101={
        "originator": {
            "originatorPersons": [
                {
                    "naturalPerson": {
                        "name": {
                            "nameIdentifier": [
                                {
                                    "primaryIdentifier": "Müller",
                                    "secondaryIdentifier": "Hans",
                                    "nameIdentifierType": "LEGL",
                                }
                            ]
                        },
                        "dateAndPlaceOfBirth": {
                            "dateOfBirth": "1985-07-14",
                            "placeOfBirth": "Berlin",
                        },
                    }
                }
            ],
            "accountNumber": ["0x71C7656EC7ab88b098defB751B7401B5f6d8976F"],
        },
        "beneficiary": {
            "beneficiaryPersons": [
                {
                    "naturalPerson": {
                        "name": {
                            "nameIdentifier": [
                                {"primaryIdentifier": "Smith", "nameIdentifierType": "LEGL"}
                            ]
                        }
                    }
                }
            ],
            "accountNumber": ["0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"],
        },
        "originatingVASP": {"name": "Acme Crypto Exchange BV"},
        "beneficiaryVASP": {"name": "Beta Exchange Ltd"},
        "transferredAmount": {"amount": "0.5", "assetType": "ETH"},
    },
)

envelope = vc.issue()
print(json.dumps(envelope, indent=2, default=str))
```

---

### KYC Profile with PEP status and SD-JWT

```python
from datetime import datetime, timezone
from tools.python.models import (
    OpenKYCAMLVC, KYCProfileModel, PEPStatus, SanctionsScreening,
    SelectiveDisclosure, DecodedDisclosure,
)

profile = KYCProfileModel(
    customerRiskRating="HIGH",
    dueDiligenceType="EDD",
    pepStatus=PEPStatus(
        isPEP=True,
        pepCategory="DOMESTIC_PEP",
        screeningDate=datetime.now(timezone.utc).date(),
        screeningProvider="Refinitiv World-Check",
    ),
    sanctionsScreening=SanctionsScreening(
        screeningStatus="CLEAR",
        screeningDate=datetime.now(timezone.utc),
        listsChecked=["OFAC_SDN", "EU_CONSOLIDATED"],
    ),
    onboardingChannel="EUDI_WALLET",
)

sd = SelectiveDisclosure(
    requiredClaimPaths=["/ivms101/originator/originatorPersons/0/naturalPerson/name"],
    disclosableClaimPaths=[
        "/kycProfile/pepStatus",
        "/kycProfile/sanctionsScreening",
    ],
    decodedDisclosures=[
        DecodedDisclosure(salt="abc123", claimName="pepStatus", claimValue={"isPEP": True}),
    ],
)

vc = OpenKYCAMLVC(
    credential_subject_did="did:ebsi:z2LSzT7LiUNMxKKyGCnNjNT",
    issuer_did="did:web:acme-crypto.example.nl",
    issuer_name="Acme Crypto Exchange BV",
    kyc_profile=profile,
    selective_disclosure=sd,
)
envelope = vc.to_envelope()
```

---

### SAR-restricted payload with tipping-off protection

```python
from tools.python.models import (
    OpenKYCAMLVC, KYCProfileModel, GdprSensitivityMetadata, DisclosurePolicy,
)

vc = OpenKYCAMLVC(
    credential_subject_did="did:web:customer.example.com",
    issuer_did="did:web:acme-crypto.example.nl",
    issuer_name="Acme Crypto Exchange BV",
    kyc_profile=KYCProfileModel(customerRiskRating="VERY_HIGH", dueDiligenceType="EDD"),
    gdpr_sensitivity=GdprSensitivityMetadata(
        classification="sar_restricted",
        tippingOffProtected=True,    # required for sar_restricted
        legalBasis="AMLR-Art73",
        retentionPeriod="P5Y",
        disclosurePolicy=DisclosurePolicy(
            allowedRecipients=["fiu_only"],
            prohibitedRecipients=["data_subject"],
        ),
        auditReference="SAR-REF-2025-00142",  # opaque — no SAR content
    ),
)
envelope = vc.to_envelope()
```

---

### Deliver credential to EUDI Wallet

```python
from tools.python.models import OpenKYCAMLVC, KYCProfileModel, WalletConfig

vc = OpenKYCAMLVC(
    credential_subject_did="did:ebsi:z2LSzT7LiUNMxKKyGCnNjNT",
    issuer_did="did:web:acme-crypto.example.nl",
    issuer_name="Acme Crypto Exchange BV",
    kyc_profile=KYCProfileModel(customerRiskRating="LOW"),
)

issued = vc.issue()

response = vc.store_in_wallet(
    WalletConfig(
        wallet_api_url="https://wallet.example.com/credential",
        access_token="eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9...",
        credential_format="dc+sd-jwt",
    )
)
print(response)  # {"credential_ids": ["urn:uuid:..."]}
```

---

*Pydantic models documented from [`tools/python/models.py`](../../tools/python/models.py) (OpenKYCAML v1.12.0). Last updated: v1.12.0.*
