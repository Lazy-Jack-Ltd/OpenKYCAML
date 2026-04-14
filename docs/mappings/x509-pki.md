# X.509 PKI Certificate Mapping

This document maps **X.509 public-key and attribute certificate** metadata (ITU-T X.509 / ISO/IEC 9594-8) and **ASN.1 Object Identifiers (OIDs)** to OpenKYCAML v1.8.0 fields. It is a companion to the machine-readable YAML version (`x509-pki.yaml`).

**Primary regulatory drivers:**
- EU eIDAS 2.0 — Qualified Electronic Signatures (QES), Qualified Electronic Seals (QSealC), Qualified Website Authentication Certificates (QWAC), Qualified Electronic Attestations of Attributes (QEAA)
- ETSI EN 319 412 series — Profile for certificates issued to EU Qualified Trust Service Providers
- ETSI TS 119 461 v2.1.1 — Identity proofing requirements for QTSPs
- AMLR 2027 Art. 22 & 56 — PKI certificate evidence for remote onboarding and record keeping
- RFC 5280 — Internet X.509 PKI Certificate and CRL Profile
- ITU-T X.509 / ISO/IEC 9594-8 — The X.509 standard

---

## 1. X.509 Certificate Metadata Fields

All fields are optional. The `serialNumber` + `issuerDN` pair uniquely identifies a certificate per RFC 5280.

| X.509 / RFC 5280 Field | OpenKYCAML v1.8.0 Field | Notes |
|---|---|---|
| **Subject DN** (§4.1.2.6) | `pkiEvidence.x509Certificate.subjectDN` | RFC 4514 string; SHOULD match `legacyIdentifiers.x500DN` when `x500DNType` is `certificateSubject` |
| **Issuer DN** (§4.1.2.4) | `pkiEvidence.x509Certificate.issuerDN` | RFC 4514 string for the CA / QTSP |
| **Serial number** (§4.1.2.2) | `pkiEvidence.x509Certificate.serialNumber` | Hex string; unique within issuer namespace |
| **notBefore** (§4.1.2.5) | `pkiEvidence.x509Certificate.validFrom` | ISO 8601 date-time |
| **notAfter** (§4.1.2.5) | `pkiEvidence.x509Certificate.validTo` | ISO 8601 date-time; predictive AML cert-expiry signal |
| **signatureAlgorithm** (§4.1.1.2) | `pkiEvidence.x509Certificate.signatureAlgorithm` | e.g. `ecdsa-with-SHA256`, `sha256WithRSAEncryption` |
| **id-pe-QCStatements** (OID 1.3.6.1.5.5.7.1.3) | `pkiEvidence.x509Certificate.qcStatements[]` | eIDAS qualified certificate statement OIDs or short names |
| **CRL Distribution Points** (§4.2.1.13) | `pkiEvidence.x509Certificate.crlDistributionPoints[]` | URIs for revocation checking |
| **OCSP (id-ad-ocsp)** (RFC 6960) | `pkiEvidence.x509Certificate.ocspResponderUrl` | Preferred revocation method for eIDAS QTS certs |
| **SHA-256 fingerprint** | `pkiEvidence.x509Certificate.thumbprintSha256` | Lowercase hex; 64 chars; stable cert identifier |

---

## 2. QCStatement Values (ETSI EN 319 412 / RFC 3739)

The `qcStatements[]` array holds OID short names or dotted-decimal OIDs from the `id-pe-QCStatements` extension. Standard values:

| OID | Short Name | Meaning |
|---|---|---|
| `0.4.0.1862.1.1` | `id-etsi-qcs-QcCompliance` | Certificate is a Qualified Certificate per eIDAS Annex I/III |
| `0.4.0.1862.1.4` | `id-etsi-qcs-QcSSCD` | Private key resides in a Qualified Signature/Seal Creation Device (QSCD) |
| `0.4.0.1862.1.6.1` | `id-etsi-qcs-QcType-eSign` | Qualified Electronic Signature (natural person) |
| `0.4.0.1862.1.6.2` | `id-etsi-qcs-QcType-eSeal` | Qualified Electronic Seal (legal person) |
| `0.4.0.1862.1.6.3` | `id-etsi-qcs-QcType-Web` | Qualified Website Authentication Certificate (QWAC) |
| `0.4.0.1862.1.7` | `id-etsi-qcs-QcPDS` | Policy Disclosure Statement (PDS) URI |
| `0.4.0.1862.1.8` | `id-etsi-qcs-QcCClegislation` | Jurisdiction(s) of Qualified Certificate |
| `1.3.6.1.5.5.7.1.3` | `id-pe-QCStatements` | The extension OID itself |

**QEAA-specific QCStatements** (eIDAS 2.0 Art. 45f):

| OID | Short Name | Meaning |
|---|---|---|
| `0.4.0.19461.1.1` | `id-etsi-qcs-QcEAA` | Qualified Electronic Attestation of Attributes (QEAA) |
| `0.4.0.19461.1.2` | `id-etsi-qcs-QcEAA-scheme` | Scheme under which QEAA was issued |

---

## 3. Key ASN.1 OIDs (pkiEvidence.oids[])

Use `pkiEvidence.oids[]` to carry any OID that is not pre-modelled in the `x509Certificate` object.

| OID | Description | Typical Value |
|---|---|---|
| `1.3.6.1.5.5.7.1.3` | id-pe-QCStatements | Full QCStatement sequence |
| `2.5.4.97` | organizationIdentifier | eIDAS LPID / LEI in Subject DN (e.g. `LEIXG-213800WAVVOPS85N2205`) |
| `1.3.6.1.5.5.7.48.1` | id-ad-ocsp — OCSP access method | OCSP responder URI |
| `1.3.6.1.5.5.7.48.2` | id-ad-caIssuers — CA issuers URI | URI of issuing CA certificate |
| `1.3.6.1.5.5.7.1.1` | id-pe-authorityInfoAccess | Authority Information Access (AIA) extension |
| `2.5.29.31` | id-ce-cRLDistributionPoints | CRL Distribution Points (also in `crlDistributionPoints[]`) |
| `2.5.29.32` | id-ce-certificatePolicies | Certificate Policies OID(s) |
| `2.5.29.17` | id-ce-subjectAltName | Subject Alternative Names (SANs) |
| `2.5.29.37` | id-ce-extKeyUsage | Extended Key Usage (e.g. TLS client/server auth) |

---

## 4. Compliance Mapping Table

| Standard / Provision | Coverage | OpenKYCAML v1.8.0 Field(s) |
|---|---|---|
| **X.509 v3** (ITU-T X.509 / ISO/IEC 9594-8) | ✅ | `pkiEvidence.x509Certificate.*` |
| **eIDAS 2.0 QES** (Reg. 910/2014 + EU 2024/1183) | ✅ | `pkiEvidence.x509Certificate.qcStatements` includes `id-etsi-qcs-QcType-eSign` |
| **eIDAS 2.0 QSealC** | ✅ | `pkiEvidence.x509Certificate.qcStatements` includes `id-etsi-qcs-QcType-eSeal` |
| **eIDAS 2.0 QWAC** | ✅ | `pkiEvidence.x509Certificate.qcStatements` includes `id-etsi-qcs-QcType-Web` |
| **eIDAS 2.0 QEAA** (Art. 45f) | ✅ | `pkiEvidence.x509Certificate.qcStatements` includes `id-etsi-qcs-QcEAA`; full evidence via `verifiableCredential.evidence[]` |
| **ETSI EN 319 412 series** | ✅ | `pkiEvidence.x509Certificate` (all cert metadata); `pkiEvidence.oids[]` (policy OIDs) |
| **ETSI TS 119 461 v2.1.1** — Identity proofing | ✅ | `pkiEvidence` + `identityDocuments` + `pkiEvidence.certificateDocumentRef` |
| **AMLR 2027 Art. 22(6)** — QC as CDD evidence | ✅ | `pkiEvidence.x509Certificate.qcStatements` + `pkiEvidence.certificateDocumentRef` → `identityDocuments` |
| **AMLR 2027 Art. 56** — Record keeping | ✅ | `pkiEvidence.x509Certificate.validFrom/validTo` + `thumbprintSha256` (cert fingerprint for retention) |
| **RFC 5280** — X.509 certificate profile | ✅ | `serialNumber`, `subjectDN`, `issuerDN`, `validFrom/To`, `signatureAlgorithm`, `crlDistributionPoints` |
| **RFC 6960** — OCSP | ✅ | `pkiEvidence.x509Certificate.ocspResponderUrl` |
| **SWIFTNet Identifiers Directory** | ✅ | `legacyIdentifiers.x500DN` (`x500DNType: "swiftNetAddress"`) + `pkiEvidence` |
| **Predictive AML cert provenance** | ✅ | `validTo` + `ocspResponderUrl` feed `predictiveAML.riskEvolutionHistory` cert-expiry signals |

---

## 5. Integration with Existing OpenKYCAML Blocks

### 5.1 With identityDocuments (v1.5.0+)

```
identityDocuments.naturalPersonDocuments[]
    └── documentType: EIDAS_PID_CREDENTIAL  (or PASSPORT, NATIONAL_ID_CARD)
    └── documentRef: "urn:openkycaml:doc:de:eidas-qeaa:anna-schmidt:2026-04"

pkiEvidence
    └── certificateDocumentRef: "urn:openkycaml:doc:de:eidas-qeaa:anna-schmidt:2026-04"
    └── x509Certificate.subjectDN → matches legacyIdentifiers.x500DN
```

### 5.2 With verifiableCredential.evidence (v1.1.0+)

The `verifiableCredential.evidence[]` block carries the EUDI Wallet presentation event (DID-based). The `pkiEvidence` block carries the X.509 certificate metadata that underpins the QTSP-issued QEAA. Together they provide the full eIDAS 2.0 chain-of-trust:

```
QTSP (X.509 cert) → QEAA Issuer (DID) → Subject Wallet (DID) → VASP
```

### 5.3 With predictiveAML (v1.7.0+)

Certificate validity metadata feeds predictive risk signals:
- `pkiEvidence.x509Certificate.validTo` → cert-expiry risk in `riskEvolutionHistory`
- `pkiEvidence.x509Certificate.ocspResponderUrl` → revocation-status freshness for `DataAggregationMetadata`

---

## 6. Out of Scope

| Item | Status |
|---|---|
| X.400 O/R Addresses | ⬜ Excluded — see x500-x400-legacy.md §3 |
| LDAP (RFC 4511) protocol details | ⬜ Not modelled — only the DN string is relevant |
| SCIM (RFC 7643/7644) | ⬜ Enterprise provisioning; no AML evidence value |
| X.520 Directory Attribute definitions | ⬜ Redundant with X.509 extensions already covered |
| Raw DER/PEM certificate storage | ⬜ OpenKYCAML carries metadata only, not raw bytes; store raw certs in the document bundle |

---

*Last updated: v1.12.0 — April 2026. Maintained by the OpenKYCAML Technical Working Group.*
