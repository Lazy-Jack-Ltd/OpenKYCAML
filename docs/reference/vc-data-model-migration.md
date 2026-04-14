# W3C VC Data Model: v1.1 → v2.0 Migration Reference

> **Status:** Migration **complete** as of OpenKYCAML **v1.18.0** (April 2026).
> OpenKYCAML now uses the W3C VC Data Model 2.0 (W3C Recommendation, May 2024).
> This document serves as a historical reference and adopter guide for upgrading existing integrations.

---

## What Changed in v1.18.0

| Area | v1.1 (≤ v1.17.0) | v2.0 (≥ v1.18.0) | Breaking? |
|---|---|---|---|
| **`@context[0]` URL** | `https://www.w3.org/2018/credentials/v1` | `https://www.w3.org/ns/credentials/v2` | **Yes** — context URL comparison will fail |
| **Issuance date field** | `issuanceDate` (string, ISO 8601) | `validFrom` (string, ISO 8601) | **Yes** — property renamed |
| **Expiry date field** | `expirationDate` (string, ISO 8601) | `validUntil` (string, ISO 8601) | **Yes** — property renamed |
| **`type` array** | `["VerifiableCredential", "..."]` | Same | No |
| **`credentialSubject`** | Object or array | Same | No |
| **`credentialStatus.type`** | `StatusList2021Entry` | `BitstringStatusListEntry` (recommended) | Soft — both types accepted |
| **`issuer`** | String URI or `{id}` object | Same | No |
| **Proof** | `LinkedDataProof` / `JwtProof2020` | Same + `DataIntegrityProof` | Additive |

---

## Adopter Migration Checklist

If you integrated against OpenKYCAML v1.x (≤ v1.17.0), update your VC payloads as follows:

- [x] Update `@context[0]` from `https://www.w3.org/2018/credentials/v1` to `https://www.w3.org/ns/credentials/v2`
- [x] Rename `issuanceDate` → `validFrom` in all VC payloads
- [x] Rename `expirationDate` → `validUntil` in all VC payloads
- [ ] Optionally update `credentialStatus.type` from `StatusList2021Entry` → `BitstringStatusListEntry` (both values are accepted by the schema)
- [ ] Update the EUDI Wallet context URL to the final EU Commission ARF context URL when published (currently `https://europa.eu/2018/credentials/eudi/v1` as a placeholder)
- [ ] Update any validator or processor that performs string-equality checks on `@context[0]`
- [ ] Re-validate all VC payloads against the v1.18.0+ schema

---

## Example: Updated VC Wrapper

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://openkycaml.org/contexts/v1",
    "https://europa.eu/2018/credentials/eudi/v1"
  ],
  "id": "urn:uuid:example-vc-id",
  "type": ["VerifiableCredential", "OpenKYCAMLCredential"],
  "issuer": "did:example:issuer",
  "validFrom": "2026-01-01T00:00:00Z",
  "validUntil": "2027-01-01T00:00:00Z",
  "credentialSubject": { "..." : "..." }
}
```

---

## Why Now?

The W3C VC Data Model 2.0 was published as a W3C Recommendation in May 2024. As OpenKYCAML is still in its build phase with no production adopters yet, upgrading now avoids future breaking changes for deployed integrations. The EU eIDAS 2.0 / EUDI Wallet architecture (ARF 1.4+) is designed around VC DM 2.0 structures, and OID4VP / W3C DID Auth implementations increasingly expect the v2 context URL.

---

## References

- [W3C VC Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/) — W3C Recommendation, May 2024
- [W3C VC Data Model v1.1](https://www.w3.org/TR/vc-data-model/) — historical reference
- [EUDI Wallet ARF](https://digital-strategy.ec.europa.eu/en/policies/eudi-wallet-technical-specifications) — EU Commission ARF technical specifications

---

*Last updated: April 2026 (v1.18.0). Migration completed from v1.1 to v2.0.*
