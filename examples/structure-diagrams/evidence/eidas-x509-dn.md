# evidence/eidas-x509-dn.json — Structure Diagram

**Scenario:** X.500 Distinguished Name + X.509 QSeal Certificate — Legal Entity (v1.8.0).  
Acme Bank PLC (GB) is verified via an eIDAS-qualified electronic seal (QSeal) certificate issued by a UK QTSP. The `legacyIdentifiers.x500DN` anchors the X.500 identity, while `pkiEvidence` carries the certificate OIDs including `id-pe-QCStatements`, `organizationIdentifier` (LEI in DN), and OCSP access.

```mermaid
flowchart TD
    subgraph Entity["Legal Entity — Subject"]
        LP["🏢 Acme Bank PLC · GB\nLEI: 213800WAVVOPS85N2205"]
    end

    subgraph X500["legacyIdentifiers — X.500 DN (v1.8.0)"]
        DN["📋 x500DNType: certificateSubject\nx500DN:\n  CN=Acme Bank PLC\n  OU=Treasury\n  O=AcmeBank\n  C=GB\n  serialNumber=213800WAVVOPS85N2205"]
    end

    subgraph PKI["pkiEvidence — X.509 QSeal Certificate (v1.8.0)"]
        CERT["🔐 Serial: 0A1B2C3D4E5F6A7B\nSubject DN: CN=Acme Bank PLC, OU=Treasury...\nIssuer: QTSP-UK-ROOT-CA\n(UK Qualified Trust Services Ltd · GB)"]

        subgraph OIDs["Certificate OIDs"]
            OID1["1.3.6.1.5.5.7.1.3\nid-pe-QCStatements\nQcCompliance + QcSSCD + QcType-eSeal\n(ETSI TS 119 495 — eIDAS 2.0)"]
            OID2["2.5.4.97\norganizationIdentifier\nLEIXG-213800WAVVOPS85N2205\n(LEI in X.500 Subject DN)"]
            OID3["1.3.6.1.5.5.7.48.1\nid-ad-ocsp — OCSP endpoint\nhttp://ocsp.qtsp-uk.example"]
        end
    end

    LP -.-> X500
    LP -.-> PKI

    style LP fill:#ede9fe,stroke:#7c3aed
    style DN fill:#dbeafe,stroke:#3b82f6
    style CERT fill:#f0fdf4,stroke:#16a34a
    style OID1 fill:#e0e7ff,stroke:#6366f1
    style OID2 fill:#e0e7ff,stroke:#6366f1
    style OID3 fill:#f8fafc,stroke:#64748b
```

## X.509 OID Summary

| OID | Short name | Value | Standard |
|---|---|---|---|
| `1.3.6.1.5.5.7.1.3` | `id-pe-QCStatements` | QcCompliance + QcSSCD + QcType-eSeal | ETSI TS 119 495 |
| `2.5.4.97` | `organizationIdentifier` | LEIXG-213800WAVVOPS85N2205 | eIDAS 2.0 LPID / LEI-in-DN |
| `1.3.6.1.5.5.7.48.1` | `id-ad-ocsp` | `http://ocsp.qtsp-uk.example` | RFC 5280 |

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.8.0 |
| Subject | Acme Bank PLC (GB) |
| x500DNType | `certificateSubject` |
| Certificate type | X.509 QSeal (eIDAS-qualified electronic seal) |
| Issuer | QTSP-UK-ROOT-CA (UK Qualified Trust Services Ltd) |
| LEI in DN | 213800WAVVOPS85N2205 (via `organizationIdentifier` OID) |
| KYC | CDD |
| Regulatory basis | eIDAS 2.0 Art. 3 (QSEAL); ETSI TS 119 495; X.500/X.509 (RFC 5280); AMLR Art. 22 |
