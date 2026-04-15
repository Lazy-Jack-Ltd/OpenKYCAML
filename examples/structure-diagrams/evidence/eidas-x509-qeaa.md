# evidence/eidas-x509-qeaa.json — Structure Diagram

**Scenario:** X.500 DN + X.509 QEAA Certificate — Natural Person (v1.8.0).  
Anna Schmidt (DE) is verified via an eIDAS QEAA (Qualified Electronic Attestation of Attributes) certificate issued by a German BSI-supervised QTSP. The `legacyIdentifiers.x500DN` anchors the personal X.500 identity, while `pkiEvidence` carries `id-pe-QCStatements` (including `QcCClegislation` for German eID), the ETSI PDS URI, and a `certificateDocumentRef` linking to the stored credential.

```mermaid
flowchart TD
    subgraph Person["Natural Person — Subject"]
        NP["👤 Anna Schmidt · DE\nID card: DE-IDCARD-T22000129"]
    end

    subgraph X500["legacyIdentifiers — X.500 DN (v1.8.0)"]
        DN["📋 x500DNType: certificateSubject\nx500DN:\n  CN=Anna Schmidt\n  O=BundesnetzagenturDE-QEAA\n  C=DE\n  serialNumber=DE-IDCARD-T22000129"]
    end

    subgraph PKI["pkiEvidence — X.509 QEAA Certificate (v1.8.0)"]
        CERT["🔐 Serial: 1C2D3E4F5A6B7C8D\nSubject: CN=Anna Schmidt...\nIssuer: BSI-QTSP-DE-CA\n(Bundesamt fuer Sicherheit in der\nInformationstechnik · DE)"]

        subgraph OIDs["Certificate OIDs"]
            OID1["1.3.6.1.5.5.7.1.3\nid-pe-QCStatements\nQcCompliance + QcSSCD + QcType-eSign\n+ QcCClegislation (DE eID)\n(ETSI TS 119 495 — eIDAS 2.0 QEAA)"]
            OID2["1.3.6.1.4.1.31560.2.1.1\nid-etsi-qcs-QcPDS\nPDS URI:\nhttps://pds.bsi-qtsp.example/qeaa-pds-en.pdf"]
            OID3["1.3.6.1.5.5.7.1.19\nid-pe-subjectInfoAccessSyntax\nhttps://certs.bsi-qtsp.example/ca/..."]
        end

        DOCREF["📄 certificateDocumentRef:\nurn:openkycaml:doc:de:eidas-qeaa:anna-schmidt:2026-04\n(stored credential, v1.6.0 URN convention)"]
    end

    NP -.-> X500
    NP -.-> PKI

    style NP fill:#dbeafe,stroke:#3b82f6
    style DN fill:#dbeafe,stroke:#3b82f6
    style CERT fill:#f0fdf4,stroke:#16a34a
    style OID1 fill:#e0e7ff,stroke:#6366f1
    style OID2 fill:#e0e7ff,stroke:#6366f1
    style OID3 fill:#f8fafc,stroke:#64748b
    style DOCREF fill:#dcfce7,stroke:#16a34a
```

## X.509 OID Summary

| OID | Short name | Value | Standard |
|---|---|---|---|
| `1.3.6.1.5.5.7.1.3` | `id-pe-QCStatements` | QcCompliance + QcSSCD + QcType-eSign + QcCClegislation | ETSI TS 119 495; eIDAS 2.0 |
| `1.3.6.1.4.1.31560.2.1.1` | `id-etsi-qcs-QcPDS` | PDS URI (policy disclosure statement) | ETSI TS 119 495 §5.1.4 |
| `1.3.6.1.5.5.7.1.19` | `id-pe-subjectInfoAccessSyntax` | Intermediate CA certificate URI | RFC 5280 §4.2.2.2 |

## Key Differences from the Legal-Entity (QSeal) Example

| Property | `eidas-x509-dn.json` (legal entity) | `eidas-x509-qeaa.json` (natural person) |
|---|---|---|
| Certificate type | QSeal (legal person) | QEAA (natural person attestation) |
| `QcType` | `eSeal` | `eSign` |
| Jurisdiction OID | `QcCClegislation` absent | `QcCClegislation` (DE) present |
| `certificateDocumentRef` | Not present | `urn:openkycaml:doc:de:eidas-qeaa:...` |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.8.0 |
| Subject | Anna Schmidt (DE) |
| x500DNType | `certificateSubject` |
| Certificate type | X.509 QEAA (eIDAS-qualified attribute attestation) |
| Issuer | BSI-QTSP-DE-CA (Bundesamt fuer Sicherheit in der Informationstechnik) |
| `certificateDocumentRef` | `urn:openkycaml:doc:de:eidas-qeaa:anna-schmidt:2026-04` |
| KYC | CDD |
| Regulatory basis | eIDAS 2.0 Art. 45f (QEAA); ETSI TS 119 495; X.509 RFC 5280; AMLR Art. 22 |
