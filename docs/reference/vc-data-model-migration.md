# W3C VC Data Model Migration Guide: v1.1 → v2.0

This document helps OpenKYCAML adopters plan migration from the W3C Verifiable Credentials Data Model v1.1 (used in OpenKYCAML v1.x) to v2.0 (targeted for OpenKYCAML v2.0.0, planned H1 2027).

> **Action required?** No immediate action is required for v1.x integrations. This guide is forward-looking documentation to help you plan. OpenKYCAML v1.x will continue to use the v1.1 context URL.

---

## Summary of Breaking Changes (v1.1 → v2.0)

| Area | v1.1 (current — OpenKYCAML v1.x) | v2.0 (target — OpenKYCAML v2.0.0) | Notes |
|---|---|---|---|
| **`@context[0]` URL** | `https://www.w3.org/2018/credentials/v1` | `https://www.w3.org/ns/credentials/v2` | **Breaking** — validators and processors that compare the context URL will reject v1 payloads as invalid v2 VCs and vice versa |
| **`type` array** | `["VerifiableCredential", "..."]` | Same — no change | Non-breaking |
| **`credentialSubject`** | Object or array of objects | Same — no change | Non-breaking |
| **`credentialStatus`** | `StatusList2021Entry` (de-facto standard) | `BitstringStatusListEntry` (W3C standard) — type value changes | **Breaking** for `credentialStatus.type` string |
| **`expirationDate`** | `expirationDate` (string, ISO 8601) | `validUntil` (string, ISO 8601) | **Breaking** — property rename |
| **`issuanceDate`** | `issuanceDate` (string, ISO 8601) | `validFrom` (string, ISO 8601) | **Breaking** — property rename |
| **`issuer`** | String URI or object with `id` | Same — no change | Non-breaking |
| **Proof** | `LinkedDataProof` / `JwtProof2020` | Same types supported; new `DataIntegrityProof` standard | Additive |

---

## Field-by-Field Migration for OpenKYCAML

### 1. `@context` Array

**v1.1 (current):**
```json
"@context": [
  "https://www.w3.org/2018/credentials/v1",
  "https://openkycaml.org/contexts/v1",
  "https://europa.eu/2018/credentials/eudi/v1"
]
```

**v2.0 (future):**
```json
"@context": [
  "https://www.w3.org/ns/credentials/v2",
  "https://openkycaml.org/contexts/v2",
  "https://europa.eu/2018/credentials/eudi/v2"
]
```

> Note: The EUDI Wallet context URL (`europa.eu/...`) is a placeholder in v1.x and will be updated to the official EU Commission ARF context URL when published. OpenKYCAML v2.0.0 will track the final URL.

---

### 2. Date Property Renames

| Property | v1.1 | v2.0 |
|---|---|---|
| Issuance date | `issuanceDate` | `validFrom` |
| Expiry date | `expirationDate` | `validUntil` |

**v1.1 (current):**
```json
"issuanceDate": "2026-01-01T00:00:00Z",
"expirationDate": "2027-01-01T00:00:00Z"
```

**v2.0 (future):**
```json
"validFrom": "2026-01-01T00:00:00Z",
"validUntil": "2027-01-01T00:00:00Z"
```

---

### 3. `credentialStatus.type`

**v1.1 (current):**
```json
"credentialStatus": {
  "id": "https://...",
  "type": "StatusList2021Entry",
  "statusListIndex": "42",
  "statusListCredential": "https://..."
}
```

**v2.0 (future):**
```json
"credentialStatus": {
  "id": "https://...",
  "type": "BitstringStatusListEntry",
  "statusListIndex": "42",
  "statusListCredential": "https://..."
}
```

> The `AnonCredsCredentialStatusList2023` type (added in OpenKYCAML v1.3.0 for AnonCreds support) is an extension type and is not affected by this W3C rename.

---

## Migration Strategy for Adopters

### Option A: Dual-context support during transition (recommended)

During the transition period (OpenKYCAML v1.x → v2.0.0), deploy a transformer layer that:
1. Accepts both v1.1 and v2.0 context URLs.
2. Normalises internally to your preferred version.
3. Issues only v1.1 payloads until OpenKYCAML v2.0.0 ships.

This allows you to receive v2.0 credentials from forward-looking issuers without breaking your existing pipeline.

### Option B: Flag-gated migration

Add a feature flag to your KYC pipeline that selects the context URL based on the counterparty's declared VC DM version. Useful if you operate in both legacy and modern ecosystems simultaneously.

### Option C: Hard cutover at v2.0.0

Wait for OpenKYCAML v2.0.0 and migrate all systems at once. Simplest operationally but requires a coordinated cutover with counterparties.

---

## OpenKYCAML v2.0.0 Migration Checklist

When OpenKYCAML v2.0.0 is released, adopters will need to:

- [ ] Update `@context[0]` from `https://www.w3.org/2018/credentials/v1` to `https://www.w3.org/ns/credentials/v2`
- [ ] Rename `issuanceDate` → `validFrom` in all VC payloads
- [ ] Rename `expirationDate` → `validUntil` in all VC payloads
- [ ] Update `credentialStatus.type` from `StatusList2021Entry` → `BitstringStatusListEntry` (if using status lists)
- [ ] Update the EUDI Wallet context URL to the final EU Commission ARF context URL (TBD)
- [ ] Update `@context[1]` OpenKYCAML context URL to `https://openkycaml.org/contexts/v2` (if/when published)
- [ ] Re-validate all VC payloads against the v2.0.0 schema
- [ ] Update any validator or processor that performs a string-equality check on the `@context[0]` value

---

## References

- [W3C VC Data Model v1.1](https://www.w3.org/TR/vc-data-model/) — current basis for OpenKYCAML v1.x
- [W3C VC Data Model v2.0](https://www.w3.org/TR/vc-data-model-2.0/) — target for OpenKYCAML v2.0.0
- [EUDI Wallet ARF](https://digital-strategy.ec.europa.eu/en/policies/eudi-wallet-technical-specifications) — EU Commission ARF technical specifications (context URL pending publication)
- [OpenKYCAML ROADMAP.md](../../ROADMAP.md) — v2.0.0 planned scope and AMLR 2027 alignment

---

*Last updated: April 2026 (v1.7.0). This document will be updated when the W3C VC DM v2.0 migration is implemented in OpenKYCAML v2.0.0.*
