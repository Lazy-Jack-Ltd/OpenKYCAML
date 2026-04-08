# X.500 Distinguished Names and X.400 Legacy Mapping

This document maps **X.500 Distinguished Names (DNs)** and **X.400 O/R Addresses** to OpenKYCAML v1.8.0 fields. It is a companion to the machine-readable YAML version (`x500-x400-legacy.yaml`).

**Assessment basis:** X.500 DNs carry significant value for eIDAS 2.0 Qualified Trust Services, SWIFTNet technical addressing, and LDAP/enterprise-directory interoperability. X.400 O/R Addresses carry no meaningful AML predictive or interoperability value and are explicitly excluded from the schema.

---

## 1. Executive Summary

| Standard | OpenKYCAML v1.8.0 Support | Rationale |
|---|---|---|
| **X.500 Distinguished Names (ITU-T X.500 / RFC 4514)** | ✅ `legacyIdentifiers.x500DN` + `pkiEvidence` | Core to eIDAS QTS certificates, SWIFTNet addressing, LDAP directories |
| **X.400 O/R Addresses (ITU-T X.400 / RFC 2156)** | ⬜ Not added — legacy reference only | No current regulatory mandate; replaced by SMTP, ISO 20022, modern messaging |

---

## 2. X.500 Distinguished Name Mapping

### 2.1 Primary Field

| Use Case | OpenKYCAML v1.8.0 Field | Notes |
|---|---|---|
| X.509 certificate Subject DN | `legacyIdentifiers.x500DN` + `x500DNType: "certificateSubject"` | RFC 4514 string form; e.g. `CN=Entity,O=Bank,C=GB` |
| X.509 certificate Issuer DN | `legacyIdentifiers.x500DN` + `x500DNType: "certificateIssuer"` | Points to the CA or QTSP issuing the certificate |
| LDAP / Active Directory entry | `legacyIdentifiers.x500DN` + `x500DNType: "directoryEntry"` | Legacy bank or enterprise directory reference |
| SWIFTNet technical address | `legacyIdentifiers.x500DN` + `x500DNType: "swiftNetAddress"` | Format: `cn=user1,ou=Finance,o=BankName,o=swift` |

### 2.2 Evidence Linkage

When an X.500 DN is derived from an X.509 certificate, the full certificate metadata is held in `pkiEvidence.x509Certificate`. The `pkiEvidence.x509Certificate.subjectDN` field SHOULD match `legacyIdentifiers.x500DN` when `x500DNType` is `"certificateSubject"`.

For full eIDAS triangulation, `pkiEvidence.certificateDocumentRef` links to the corresponding entry in `identityDocuments.naturalPersonDocuments[]` or `identityDocuments.legalEntityDocuments[]`.

### 2.3 Regulatory Drivers

| Regulation / Standard | Requirement | OpenKYCAML Field |
|---|---|---|
| **eIDAS 2.0** — Qualified Trust Services (ETSI EN 319 412 series) | X.500 DN mandatory in QES/QSealC/QWAC/QEAA certificate Subject and Issuer fields | `legacyIdentifiers.x500DN` + `pkiEvidence.x509Certificate.subjectDN` |
| **AMLR 2027 Art. 22(6)** | Qualified Certificates accepted as remote CDD evidence | `pkiEvidence` (full cert metadata) |
| **eIDAS Art. 24** | Identity proofing via Qualified Electronic Signature | `pkiEvidence.x509Certificate.qcStatements` |
| **SWIFTNet Identifiers Directory** | Technical addresses use X.500 DN format | `legacyIdentifiers.x500DN` (`x500DNType: "swiftNetAddress"`) |
| **ETSI TS 119 461 v2.1.1** | Identity proofing for Qualified Trust Service Providers | `pkiEvidence` + `identityDocuments` |

### 2.4 Common X.500 Attribute Types (RFC 4519 / ETSI EN 319 412)

| OID | Short Name | Purpose | Where captured |
|---|---|---|---|
| `2.5.4.3` | CN (commonName) | Person or entity name | `legacyIdentifiers.x500DN` |
| `2.5.4.10` | O (organizationName) | Legal entity name | `legacyIdentifiers.x500DN` |
| `2.5.4.11` | OU (organizationalUnitName) | Department / division | `legacyIdentifiers.x500DN` |
| `2.5.4.6` | C (countryName) | ISO 3166-1 alpha-2 country | `legacyIdentifiers.x500DN` |
| `2.5.4.5` | serialNumber | Entity serial number / LEI / registration number | `legacyIdentifiers.x500DN`; also `pkiEvidence.oids[]` |
| `2.5.4.97` | organizationIdentifier | eIDAS LPID / LEI in QES Subject DN (ETSI EN 319 412-1) | `pkiEvidence.oids[]` (`oid: "2.5.4.97"`) |
| `2.5.4.8` | ST (stateOrProvinceName) | State or province | `legacyIdentifiers.x500DN` |
| `2.5.4.7` | L (localityName) | City / locality | `legacyIdentifiers.x500DN` |

---

## 3. X.400 O/R Address — Explicitly Out of Scope

X.400 (ITU-T X.400 / RFC 2156) Originator/Recipient (O/R) Addresses are **not modelled in OpenKYCAML**. They are referenced here only to document the scope decision and prevent scope creep.

### 3.1 Rationale for Exclusion

| Criterion | Assessment |
|---|---|
| Current regulatory mandate | None — X.400 is not referenced in AMLR, eIDAS 2.0, FATF Recommendations, Wolfsberg FCCQ/CBDDQ, BCBS 239, or ISO 20022 business payloads (2026) |
| Active production fintech systems | X.400 MHS (Message Handling System) has been displaced by SMTP, MQ messaging, ISO 20022 pacs.008/pain.001, and REST APIs |
| AML / Travel Rule relevance | Zero — IVMS 101, OpenVASP, and Notabene use HTTP/gRPC, not X.400 |
| Maintenance burden | Adding a field with no adopters creates dead schema weight |

### 3.2 Legacy Reference

If an organisation must carry an X.400 address for interoperability with a legacy EDI system, the recommended approach is to store it as an unstructured string in `kycProfile.auditMetadata.dataSourceSystem` or in a custom extension field (using `additionalProperties` at the root), with a comment explaining the source system. This preserves backward compatibility without polluting the canonical schema.

X.400 O/R Address format for reference: `G=John; S=Doe; O=AcmeBank; P=Finance; A=ADMD; C=GB`

---

## 4. Comparison with Existing OpenKYCAML Identifier Types

| Identifier Type | Schema Location | Standard |
|---|---|---|
| LEI | `legalPerson.nationalIdentification` (`LEIX` type) | ISO 17442 |
| DID | `verifiableCredential.issuer` | W3C DID Core |
| vLEI | `legalPerson.lpid.uniqueIdentifier` | GLEIF vLEI |
| BIC | `ivms101.originatingVASP` name fields | ISO 9362 |
| EORI / DUNS / GS1 GLN | Planned — `officialIdentifiers[]` (v1.9.0) | — |
| **X.500 DN** | **`legacyIdentifiers.x500DN`** (v1.8.0) | **ITU-T X.500 / RFC 4514** |

---

## 5. Implementation Notes for Adopters

1. **Minimal implementation** — Populate only `legacyIdentifiers.x500DN` and `x500DNType` when you need to carry the DN from a certificate.
2. **Full PKI evidence** — Combine with `pkiEvidence.x509Certificate` to carry the complete certificate metadata needed for automated validation.
3. **eIDAS triangulation** — Set `pkiEvidence.certificateDocumentRef` to the `identityDocuments` entry to complete the chain: DN → Certificate → Document Bundle → Identity Attributes.
4. **Predictive AML** — The `pkiEvidence.x509Certificate.validTo` and `ocspResponderUrl` fields feed certificate provenance into `predictiveAML.riskEvolutionHistory` for cert-expiry risk signals.

---

## 6. Deprecation Policy — `legacyIdentifiers.X400` (Not Applicable)

X.400 O/R Addresses were **never added to the schema** and therefore have no deprecation lifecycle. This section exists to formally document that decision and close any future scope-creep requests.

### 6.1 Policy Statement

> **OpenKYCAML does not and will not add a `legacyIdentifiers.x400OR` (or equivalent) field to any published release of the schema, including v2.0.0, unless a binding regulatory mandate (AMLR, MiCA, eIDAS, FATF R.16, or equivalent) explicitly requires machine-readable X.400 O/R Address exchange.**

This policy is **permanent and not subject to community override** without a formal TWG RFC and documented evidence of a regulatory or production adoption requirement.

### 6.2 Rationale (Summary)

- No AMLR 2027, eIDAS 2.0, FATF, Wolfsberg, BCBS 239, or ISO 20022 obligation references X.400.
- No active production Travel Rule protocol (TRISA, OpenVASP, Notabene, TRP, Sygna Bridge) uses X.400 transport.
- Every real-world adopter that needs to carry a legacy X.400 address can do so via `kycProfile.auditMetadata.dataSourceSystem` or a root-level `additionalProperties` extension (see §3.2 above).

### 6.3 Guidance for Mapping Docs and Downstream Tools

Any compliance mapping document, converter tool, or validator that currently includes a row or field referencing `legacyIdentifiers.x400OR` or `x400Address` MUST:

1. Remove the row/field reference.
2. Replace with a footnote: *"X.400 O/R Addresses are explicitly excluded from OpenKYCAML. See `docs/mappings/x500-x400-legacy.md` §6 for the formal deprecation policy."*
3. Log a `WARNING`-level message if a submitted payload contains any key matching `x400*` at the root level.

---

*Last updated: v1.9.1 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*
