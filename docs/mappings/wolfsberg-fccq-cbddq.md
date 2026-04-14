# Wolfsberg FCCQ v1.2 and CBDDQ v1.4 Mapping

This document maps the **Wolfsberg Financial Crime Compliance Questionnaire (FCCQ) v1.2** and the **Correspondent Banking Due Diligence Questionnaire (CBDDQ) v1.4** to OpenKYCAML v1.7.0 fields. It is primarily relevant for bank-to-bank relationships (respondent and correspondent bank onboarding) and is a companion to the machine-readable YAML version (`wolfsberg-fccq-cbddq.yaml`).

**Wolfsberg sources:**
- FCCQ v1.2 — Financial Crime Compliance Questionnaire (2022)
- CBDDQ v1.4 — Correspondent Banking Due Diligence Questionnaire (2022)

**Coverage legend:**
- ✅ Full coverage — direct field mapping exists
- 🟡 Partial — concept captured; supplementary fields or notes required
- ⬜ Out of scope — operational/process item not applicable to a data model

---

## 1. FCCQ / CBDDQ Section Mapping Table

| Wolfsberg Section | Question(s) | OpenKYCAML v1.7.0 Field | Notes |
|---|---|---|---|
| **A — Organisation & Structure** | | | |
| Legal name and registration | Q1–Q3 | `ivms101.originator.originatorPersons[].legalPerson.name.nameIdentifiers[]` | LEGL name type; also `legalPerson.legalFormCode` (ISO 20275 ELF) |
| Jurisdiction of incorporation | Q4 | `ivms101.originator.originatorPersons[].legalPerson.countryOfRegistration` | ISO 3166-1 alpha-2 |
| LEI | Q5 | `ivms101.originator.originatorPersons[].legalPerson.nationalIdentification` (LEIX type) | Also `legalPerson.lpid.lei` for LPID-bearing entities |
| **B — Ownership and Control** | | | |
| Entity and ownership structure | Q6–Q8 | `kycProfile.beneficialOwnership[]` + `legalPerson.ownershipStructure` | Extend with `nomineeFlags.bearerShareFlag`; chain depth via `ownershipChainDepth` |
| Bearer shares | Q8b | `kycProfile.beneficialOwnership[].nomineeFlags.bearerShareFlag` | New in v1.7.0; true = enhanced due diligence required |
| Nominee arrangements | Q8c | `kycProfile.beneficialOwnership[].nomineeFlags.isNominee` + `nominatorIdentified` | FATF R.24 (2023) compliant |
| **C — AML/CTF Programme** | | | |
| AML/CTF policy and governance | Q12–Q16 | `kycProfile.dueDiligenceType` (SDD/CDD/EDD framework) | Officer expertise captured in `predictiveAML.modelMetadata.provider` |
| AML model and system | Q22 | `kycProfile.monitoringInfo.tmModelVersion` + `predictiveAML.modelMetadata` | EU AI Act classification via `predictiveAML.modelMetadata.euAiActClassification` |
| STR/SAR filing process | Q18 | `kycProfile.monitoringInfo.alerts[].alertStatus` = `SAR_FILED` | SAR content protected via `gdprSensitivityMetadata.classification` = `sar_restricted` |
| **D — Customer Due Diligence** | | | |
| Customer identification | Q19a | `ivms101.originator.originatorPersons[].naturalPerson.*` or `legalPerson.*` | Full IVMS 101 v1.0 support |
| Products and services | Q19b | `kycProfile.productUsage[]` | Planned extension field (see ROADMAP.md) |
| CDD risk categorisation | Q20 | `kycProfile.customerRiskRating` + `kycProfile.dueDiligenceType` | Risk rating: LOW/MEDIUM/HIGH/VERY_HIGH |
| EDD triggers | Q21 | `kycProfile.monitoringInfo.eddRequired` | Automatically required when `pepStatus.isPEP = true` or high-risk country |
| **E — Sanctions and PEP** | | | |
| Sanctions screening | Q22j | `kycProfile.sanctionsScreening` | `screeningStatus`, `screeningProvider`, `listsChecked[]`, `matchDetails[]` |
| PEP screening | Q22k | `kycProfile.pepStatus` | Category aligned to AMLA draft PEP taxonomy; EDD linkage |
| CBDDQ-specific sanctions evidence | Q22j (CBDDQ) | `kycProfile.sanctionsScreening.matchDetails[]` | Add `evidenceRef` pointing to identityDocuments entry |
| **F — Monitoring** | | | |
| Transaction monitoring | Q24 | `kycProfile.monitoringInfo` + `predictiveAML.predictiveScores[]` | ML-enhanced monitoring via predictiveAML extension |
| Alert management | Q25 | `kycProfile.monitoringInfo.alerts[]` + `ruleTriggerHistory[]` | Full alert lifecycle: OPEN → UNDER_REVIEW → SAR_FILED |
| **G — Information Sharing** | | | |
| Correspondent bank sharing | Q27 | `informationSharingFlags.section314bSafeHarbor` | US FinCEN 314(b); CBDDQ relevant for US correspondent banks |
| Third-party CDD reliance | Q28 | `kycProfile.thirdPartyCDDReliance` | Full AMLR Art. 48 structured record |

---

## 2. CBDDQ-Specific Extensions

The CBDDQ v1.4 requires respondent banks to provide additional evidence for correspondent banking due diligence. The following OpenKYCAML fields are particularly relevant:

| CBDDQ Requirement | OpenKYCAML Field | Notes |
|---|---|---|
| Legal entity structure evidence | `identityDocuments.legalEntityDocuments[]` | REGISTRY_EXTRACT, CONSTITUTIONAL_DOCUMENT, SHAREHOLDER_REGISTER |
| UBO register extract | `identityDocuments.legalEntityDocuments[].documentType` = `ULTIMATE_BENEFICIAL_OWNER_REGISTER` | With `verifyingDocumentRefs[]` in `beneficialOwnership[]` |
| AML audit report reference | `kycProfile.auditMetadata.dataSourceSystem` | Reference to most recent AML/CTF programme audit |
| Wolfsberg CBDDQ submission date | `kycProfile.kycCompletionDate` | Date of CBDDQ completion |
| Regulatory status / licence | `legalPerson.lpid.uniqueIdentifier` or `nationalIdentification` (LEIX/RAID) | Regulatory licence number as RAID type national identifier |

---

## 3. JSON Export Template (Wolfsberg Importer)

A machine-readable import/export template mapping CBDDQ v1.4 XML fields to OpenKYCAML JSON paths is available in `tools/wolfsberg-importer/`. The importer supports:

- CBDDQ XML → OpenKYCAML JSON conversion
- OpenKYCAML JSON → CBDDQ XML export for platform ingestion
- Gap analysis report (fields present in CBDDQ but not yet in OpenKYCAML)

---

## 4. Coverage Summary

| Wolfsberg Category | OpenKYCAML Coverage |
|---|---|
| Organisation & Structure (Q1–Q5) | ✅ Full |
| Ownership & Control (Q6–Q8) | ✅ Full (v1.7.0 nominee/bearer-share flags) |
| AML/CTF Programme (Q12–Q22) | ✅ Full + predictiveAML extension |
| Customer Due Diligence (Q19–Q21) | ✅ Full |
| Sanctions & PEP (Q22j/k) | ✅ Full |
| Transaction Monitoring (Q24–Q25) | ✅ Full (v1.7.0 rule trigger history) |
| Information Sharing (Q27–Q28) | ✅ Full (v1.7.0 FinCEN 314(b) flag) |
| Products & Services (Q19b) | 🟡 Partial (productUsage[] planned) |

---

*Last updated: April 2026 — OpenKYCAML v1.12.0*
