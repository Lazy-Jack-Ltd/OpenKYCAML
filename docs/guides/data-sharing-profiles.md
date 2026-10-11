# OpenKYCAML Data Sharing Profiles

This guide defines canonical sharing profiles so OpenKYCAML implementations use **minimum necessary disclosure** by default.

## Core principle

- OpenKYCAML schema is a **superset**.
- Every exchange payload should be a **purpose-bound subset**.
- External sharing profiles must exclude internal-only fields unless exception criteria are met.

---

## Profile 1 — Travel Rule minimum (external)

**Purpose:** FATF Rec 16 / TFR transfer identity exchange between VASPs.  
**Recipient type:** Counterparty VASP / CASP.

| Control | Requirement |
|---|---|
| Allowed fields | IVMS minimum identity + account + transfer context (`ivms101`) |
| Prohibited fields | Full `kycProfile`, `monitoringInfo.alerts`, internal case references, SAR-linked fields |
| Legal basis | FATF Rec 16 / TFR legal obligation |
| Retention | Regulatory minimum retention period under applicable AML law |

---

## Profile 2 — CDD reliance minimum (external)

**Purpose:** Third-party CDD reliance with minimum attributes for reliance decision.  
**Recipient type:** Regulated financial institution under written reliance arrangement.

| Control | Requirement |
|---|---|
| Allowed fields | Reliance-relevant `kycProfile` subset (risk rating, due diligence type, sanctions/PEP status, audit references) |
| Prohibited fields | Internal monitoring alerts, investigative narratives, unnecessary full history blocks |
| Legal basis | AMLR Art. 48 (and equivalent jurisdictional provisions) + reliance contract |
| Retention | AML record-keeping period; recipient must enforce documented deletion/archival controls |

---

## Profile 3 — Enhanced investigation exchange (restricted external)

**Purpose:** Exceptional cross-institution investigation support where additional data is required.  
**Recipient type:** Competent authority, FIU, or explicitly authorised regulated counterparty.

| Control | Requirement |
|---|---|
| Allowed fields | Expanded profile fields required for the specific investigation objective |
| Prohibited fields | Any data outside documented investigation scope; unrestricted onward transfer |
| Legal basis | Legal obligation, lawful request, or explicit contractual/regulatory mandate |
| Retention | Case-bounded retention with documented review and deletion schedule |

---

## Profile 4 — Internal case management (internal only)

**Purpose:** Internal AML operations, escalation, and case lifecycle management.  
**Recipient type:** Internal compliance, AML investigations, controlled audit functions.

| Control | Requirement |
|---|---|
| Allowed fields | Full internal case context as needed under least-privilege access |
| Prohibited fields | External transmission without re-profiling and approval gate |
| Legal basis | Internal compliance operations under AML/GDPR governance framework |
| Retention | Internal AML retention schedule with role-based access and audit logging |

---

## Operational requirements for all profiles

1. Document purpose, recipient type, legal basis, and retention before exchange.
2. Apply a field-level allowlist at serialization time.
3. Block restricted fields by policy and cryptographic disclosure controls.
4. Log profile selection and approval decisions for auditability.
