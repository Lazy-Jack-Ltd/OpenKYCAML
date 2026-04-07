# OpenKYCAML Certification

This document defines the **"OpenKYCAML Certified"** badge criteria and the self-assessment process for obliged entities, technology providers, and KYC utility platforms adopting the OpenKYCAML v1.7.0 schema.

The certification programme is maintained by the OpenKYCAML Core Maintainers under the Apache 2.0 licence. The badge is a **community-governed, self-attested** mark — not a formal regulatory authorisation. Adopters are responsible for their own regulatory compliance.

---

## 1. Badge Levels

### Level 1 — OpenKYCAML Core Compliant

Awarded to implementations that demonstrate schema-valid payloads for core KYC/AML use cases.

**Criteria:**
- [ ] All submitted example payloads pass `make validate-all` (Python + Node.js + Go validators)
- [ ] At least one example covers a natural person and one covers a legal entity
- [ ] `kycProfile.customerRiskRating`, `dueDiligenceType`, `sanctionsScreening`, and `auditMetadata` are populated
- [ ] Travel Rule envelope (`ivms101` block) is present in at least one example (if VASP)

### Level 2 — OpenKYCAML AMLR 2027 Ready

Awarded to implementations aligned with EU AMLR 2027 requirements.

**Criteria (all Level 1 criteria, plus):**
- [ ] `kycProfile.thirdPartyCDDReliance` populated in at least one example
- [ ] `kycProfile.beneficialOwnership[]` with `intermediateEntities[]` in legal entity examples
- [ ] `gdprSensitivityMetadata` present and valid in at least one example
- [ ] `kycProfile.pepStatus` populated in at least one example
- [ ] SAR-restricted example with `gdprSensitivityMetadata.tippingOffProtected: true`

### Level 3 — OpenKYCAML PredictiveAML Certified

Awarded to AI/ML-powered AML platforms implementing the predictiveAML extension with EU AI Act compliance.

**Criteria (all Level 2 criteria, plus):**
- [ ] `predictiveAML.modelMetadata.euAiActClassification` set to `"high-risk-aml"`
- [ ] `predictiveAML.modelMetadata.conformityAssessmentReference` populated
- [ ] At least one score type from `predictiveScores[]` with `confidence` >= 0.7
- [ ] `predictiveAML.explainability` present with SHAP, LIME, or counterfactual values
- [ ] `predictiveAML.riskEvolutionHistory[]` present with at least 2 snapshots
- [ ] `predictiveAML.dataAggregationMetadata.bcbs239ComplianceLevel` set to `"full"` or `"partial"`
- [ ] All three example files in `examples/predictive/` pass schema validation

### Level 4 — OpenKYCAML Blockchain Certified

Awarded to XRPL/blockchain VASP implementations.

**Criteria (all Level 1 criteria, plus):**
- [ ] `kycProfile.blockchainAccountIds[]` present with `address` and `network`
- [ ] XRPL-specific: at least one of `xrplCredentialType`, `mptIssuanceId`, `xrplPermissionedDomainId`
- [ ] Lightning: `lightningNodePubkey` present if offering Lightning wallet services
- [ ] Bitcoin: `bitcoinScriptType` populated if offering Bitcoin custody
- [ ] Schema passes validation with all blockchain fields present

---

## 2. Self-Assessment Process

1. **Fork** the OpenKYCAML repository.
2. **Run validators**: `make validate-all` — all examples must pass.
3. **Prepare evidence** — a JSON file listing the criteria met, with references to your example payloads.
4. **Open a Pull Request** to `main` adding your organisation to `ADOPTERS.md` with the badge level claimed.
5. **Two maintainer approvals** are required before the badge is awarded.

The badge may be revoked if a new schema version introduces breaking changes that the adopter does not update to within 90 days.

---

## 3. Badge Usage

Once certified, adopters may display the following badge in their documentation:

```markdown
[![OpenKYCAML Certified Level N](https://img.shields.io/badge/OpenKYCAML-Certified%20Level%20N-brightgreen)](https://github.com/Lazy-Jack-Ltd/OpenKYCAML/blob/main/CERTIFICATION.md)
```

Replace `N` with the awarded level (1, 2, 3, or 4).

---

## 4. Regulatory Disclaimer

The OpenKYCAML certification badge does not constitute:
- Regulatory approval or authorisation by any financial supervisory authority
- Legal advice on AMLR 2027, FATF, EU AI Act, or other regulatory compliance
- A guarantee that adopters' implementations are compliant with applicable law

Adopters must obtain independent legal and compliance advice for their jurisdiction.

---

*Maintained by the OpenKYCAML Core Maintainers — Apache 2.0 — v1.7.0 — April 2026*
