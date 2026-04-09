# OpenKYCAML — Structure Diagrams

This folder contains one Mermaid diagram per example in the `/examples` directory. Each `.md` file can be viewed with any Mermaid-capable renderer (GitHub, GitLab, Obsidian, VS Code Mermaid preview, etc.).

---

## Index

### Travel Rule — Natural Person

| Diagram | Example File | Scenario |
|---|---|---|
| [natural-person-plain.md](natural-person-plain.md) | `natural-person-plain.json` | Minimal IVMS 101 — Van Dijk (NL) → Hargreaves (GB), 0.5 BTC, no VC wrapper |
| [natural-person-eudi-wallet.md](natural-person-eudi-wallet.md) | `natural-person-eudi-wallet.json` | EUDI Wallet onboarding — Anna Müller (DE), German PID via OpenID4VP, 3-DID chain |
| [natural-person-sd-jwt-eudi-wallet.md](natural-person-sd-jwt-eudi-wallet.md) | `natural-person-sd-jwt-eudi-wallet.json` | SD-JWT selective disclosure — name + address revealed, DOB/nationality withheld (GDPR) |

### Travel Rule — Minimal

| Diagram | Example File | Scenario |
|---|---|---|
| [minimal-travel-rule.md](minimal-travel-rule.md) | `minimal-travel-rule.json` | Minimal IVMS 101 — Tanaka (JP) → Kim (KR), 1 BTC, IVMS101.2023 metadata |
| [minimal-travel-rule-eudi-wallet.md](minimal-travel-rule-eudi-wallet.md) | `minimal-travel-rule-eudi-wallet.json` | EUDI Wallet at beneficiary side — Tanaka (JP) → Dubois (FR, French ANSSI PID) |

### Travel Rule — VC-Wrapped

| Diagram | Example File | Scenario |
|---|---|---|
| [travel-rule-vc-wrapped.md](travel-rule-vc-wrapped.md) | `travel-rule-vc-wrapped.json` | VC-wrapped IVMS 101 + Transaction Monitoring — Van Dijk → Hargreaves, 0.5 BTC, TRP |
| [travel-rule-vc-eudi-wallet.md](travel-rule-vc-eudi-wallet.md) | `travel-rule-vc-eudi-wallet.json` | EUDI Wallet + VC-wrapped + TM — Dutch PID from RVO, 4-DID chain, 4 TM rules PASS |

### Legal Entity KYC / Travel Rule

| Diagram | Example File | Scenario |
|---|---|---|
| [legal-entity-plain.md](legal-entity-plain.md) | `legal-entity-plain.json` | Minimal IVMS 101 — GTS GmbH (DE) → Pacific Rim (SG), 500,000 USD, no VC wrapper |
| [legal-entity-eudi-wallet.md](legal-entity-eudi-wallet.md) | `legal-entity-eudi-wallet.json` | EUDI Wallet LPID + QEAA Mandate — GTS GmbH, Bundesanzeiger, Hans Bauer director + UBO (75%) |
| [legal-entity-sd-jwt-eudi-wallet.md](legal-entity-sd-jwt-eudi-wallet.md) | `legal-entity-sd-jwt-eudi-wallet.json` | SD-JWT LPID — Acme Digital Trading SL (ES), name/LEI disclosed, address/VAT withheld |
| [legal-entity-deep-ubo.md](legal-entity-deep-ubo.md) | `legal-entity-deep-ubo.json` | 4-tier UBO chain — Meridian Digital Assets (KY), Fatima Al-Rashidi 75% (BVI→LU→KY→KY) |

### Full KYC Profile / EDD

| Diagram | Example File | Scenario |
|---|---|---|
| [full-kyc-profile.md](full-kyc-profile.md) | `full-kyc-profile.json` | Foreign PEP + EDD — Fatima Al-Rashidi (AE, Former Min. Finance), HIGH risk, SOW verified |
| [full-kyc-profile-eudi-wallet.md](full-kyc-profile-eudi-wallet.md) | `full-kyc-profile-eudi-wallet.json` | EUDI Wallet + PEP EDD — Austrian PID, 4-DID chain, EUDI does NOT reduce PEP risk |

### Hybrid VC

| Diagram | Example File | Scenario |
|---|---|---|
| [hybrid-vc-wrapped.md](hybrid-vc-wrapped.md) | `hybrid-vc-wrapped.json` | Hybrid VC — Anna Müller (DE) → Marco Rossi (IT), 2.75 ETH, IVMS 101 + kycProfile in VC |
| [hybrid-vc-eudi-wallet.md](hybrid-vc-eudi-wallet.md) | `hybrid-vc-eudi-wallet.json` | Hybrid VC + EUDI Wallet — German PID, BerlinDeFi → MilanoChain, 4-DID chain |
| [hybrid-with-sar-restriction.md](hybrid-with-sar-restriction.md) | `hybrid-with-sar-restriction.json` | SAR + Tipping-Off Protection — Pieter Van Houten (NL), SAR fields SD-JWT withheld (AMLR Art. 73) |

### SD-JWT Compact Token

| Diagram | Example File | Scenario |
|---|---|---|
| [sd-jwt-compact-token.md](sd-jwt-compact-token.md) | `sd-jwt-compact-token.json` | Annotated compact token — Issuer-JWT ~ 3 disclosures ~ KB-JWT structure, FATF Travel Rule min. |

### Complex Ownership Structures

| Diagram | Example File | Scenario |
|---|---|---|
| [complex-group-multi-tier.md](complex-group-multi-tier.md) | `complex-group-multi-tier.json` | 4-tier corporate chain — Nexus Global Ventures (KY), Marcus Van Den Berg UBO (NL→LU→BVI→KY), directors at every tier |
| [trust-complex-ubo.md](trust-complex-ubo.md) | `trust-complex-ubo.json` | Jersey discretionary trust — settlor + life beneficiary (Sir James Hartley), corporate trustee (2 directors), protector, 3 beneficiaries |
| [foundation-complex-ubo.md](foundation-complex-ubo.md) | `foundation-complex-ubo.json` | Liechtenstein Privatstiftung — Heinrich Steinberg UBO (founder), 3-person foundation council, PGR Art. 552 §29 reservation powers |
| [llp-complex-ubo.md](llp-complex-ubo.md) | `llp-complex-ubo.json` | UK LLP — Priya Sharma UBO via GP control, corporate GP + 2 corporate LPs + 2 individual LPs, no LP management rights |
| [legal-entity-partnership.md](legal-entity-partnership.md) | `legal-entity-partnership.json` | UK LLP — Cairn Digital Ventures LLP, 2 designated members + 1 corporate member, 120,000 BTC |
| [legal-entity-trust.md](legal-entity-trust.md) | `legal-entity-trust.json` | Cayman discretionary trust — Harbour Gate Trust (KY), settlor + corporate trustee + 2 beneficiaries, 85,000 USDC |

### v1.12.0 — Gender, Occupation, EntityGovernance, ReviewLifecycle

| Diagram | Example File | Scenario |
|---|---|---|
| [natural-person-gender-occupation.md](natural-person-gender-occupation.md) | `natural-person-gender-occupation.json` | Gender (FEMALE) + occupation (SELF_EMPLOYED) on NaturalPerson — Anna Müller (DE), reviewLifecycle state machine |
| [legal-entity-governance.md](legal-entity-governance.md) | `legal-entity-governance.json` | EntityGovernance — Acme Financial Services GmbH (DE), dual-regulated (BaFin + FCA), XETR-listed, majority-owned subsidiary |

### Cell Company Structures (v1.11.0+)

| Diagram | Example File | Scenario |
|---|---|---|
| [cell-company/pcc-cell.md](cell-company/pcc-cell.md) | `cell-company/pcc-cell.json` | PCC Cell — Guernsey Re PCC Cell 7 (CELL-007), catastrophe bond, no independent legal personality, 5M USD |
| [cell-company/icc-cell.md](cell-company/icc-cell.md) | `cell-company/icc-cell.json` | ICC Cell — Jersey ICC Cell 3 Marine ILS (IC-003), independent legal personality, 10M USD |
| [cell-company/pcc-cell-predictive-aml.md](cell-company/pcc-cell-predictive-aml.md) | `cell-company/pcc-cell-predictive-aml.json` | PCC Cell + cell-level predictive AML scores (v1.11.2) — CELL-007, transaction_anomaly 72, network_risk 65 |

### Contact Details and Banking

| Diagram | Example File | Scenario |
|---|---|---|
| [contact-banking/natural-person-with-contact.md](contact-banking/natural-person-with-contact.md) | `contact-banking/natural-person-with-contact.json` | Natural person with email + phone + DE IBAN — Anna Mueller (DE), 1,500 EUR |
| [contact-banking/legal-entity-with-banking.md](contact-banking/legal-entity-with-banking.md) | `contact-banking/legal-entity-with-banking.json` | Legal entity with 2 bank accounts — Nordvik Shipping AS (NO), NO + NL IBANs, 250,000 EUR |

### Verification Document Bundles (v1.6.0)

| Diagram | Example File | Scenario |
|---|---|---|
| [document-bundle-natural-person.md](document-bundle-natural-person.md) | `document-bundle-natural-person.json` | Document bundle — Andreas Schmidt (DE), NID + proof of address + eIDAS PID, COMPLETE |
| [document-bundle-legal-entity.md](document-bundle-legal-entity.md) | `document-bundle-legal-entity.json` | Document bundle — Acme Global Trading PLC (GB), 6 corporate docs (cert. of incorp. → PSC register), COMPLETE |

### X.500 / X.509 PKI Evidence (v1.8.0)

| Diagram | Example File | Scenario |
|---|---|---|
| [evidence/eidas-x509-dn.md](evidence/eidas-x509-dn.md) | `evidence/eidas-x509-dn.json` | QSeal X.509 + X.500 DN — Acme Bank PLC (GB), LEI in Subject DN via organizationIdentifier OID |
| [evidence/eidas-x509-qeaa.md](evidence/eidas-x509-qeaa.md) | `evidence/eidas-x509-qeaa.json` | QEAA X.509 + X.500 DN — Anna Schmidt (DE), BSI-issued, QcCClegislation, certificateDocumentRef |

### Predictive AML (v1.7.0)

| Diagram | Example File | Scenario |
|---|---|---|
| [predictive/predictive-static.md](predictive/predictive-static.md) | `predictive/predictive-static.json` | Static snapshot — txn-risk-model-v3, transaction_anomaly 72.5 + customer_lifetime_risk 65.0, SHAP explainability |
| [predictive/predictive-delta.md](predictive/predictive-delta.md) | `predictive/predictive-delta.json` | Delta monitoring — network_risk 45 + velocity_fraud 38.5, rising trend Jan→Apr (30→45), ACTIMIZE-CASE-2026-00441 |
| [predictive/predictive-ai-high-risk.md](predictive/predictive-ai-high-risk.md) | `predictive/predictive-ai-high-risk.json` | EU AI Act high-risk — ubo-graph-risk-model-v1, all 3 scores VERY_HIGH (89/84.5/77), steep escalation Nov 2025→Apr 2026 |

### Tax Status (v1.9.0 / v1.9.1)

| Diagram | Example File | Scenario |
|---|---|---|
| [tax/tax-individual-tin.md](tax/tax-individual-tin.md) | `tax/tax-individual-tin.json` | Individual dual-country TINs — Robert Johnson (US), EIN (IRS) + functional-equivalent (HMRC) |
| [tax/tax-corporate-vat-gst.md](tax/tax-corporate-vat-gst.md) | `tax/tax-corporate-vat-gst.json` | Corporate VAT + GST — TechGlobal Solutions GmbH (DE), DE VAT + IN GST registrations |
| [tax/tax-fatca-crs.md](tax/tax-fatca-crs.md) | `tax/tax-fatca-crs.json` | FATCA GIIN + CRS residencies — Atlantic Asset Management Ltd (IE), `registeredDeemedCompliantFFI` |
| [tax/tax-offshore-esr.md](tax/tax-offshore-esr.md) | `tax/tax-offshore-esr.json` | Economic Substance — Meridian Holdings Ltd (KY), holding + financing activities, CIMA ESR report |
| [tax/tax-mne-pillar2.md](tax/tax-mne-pillar2.md) | `tax/tax-mne-pillar2.json` | Pillar Two GloBE — Apex Ireland Operations Ltd (IE), revenue €2.1B, IE ETR 12.5% below 15% floor |

### Full-Stack Compliance Showcase

| Diagram | Example File | Scenario |
|---|---|---|
| [amlr2027-fatca-ai-act.md](amlr2027-fatca-ai-act.md) | `amlr2027-fatca-ai-act.json` | All extensions active — Nexus Capital (IE), FATCA GIIN + CRS + Pillar Two + QSeal + predictive AML + FinCEN 314(b) |

### OpenID4VP Presentation Definitions

| Diagram | Example File | Scenario |
|---|---|---|
| [presentation-definitions/travel-rule-minimum.md](presentation-definitions/travel-rule-minimum.md) | `presentation-definitions/travel-rule-minimum.json` | W3C PE 2.0 Presentation Definition — FATF Rec 16 minimum claims via OpenID4VP |

---

## Diagram Conventions

| Colour | Meaning |
|---|---|
| 🟦 Blue | Natural person (customer / UBO / beneficiary individual) |
| 🟪 Purple | Legal entity in ownership chain |
| 🟡 Yellow | VASP (originating or beneficiary) |
| 🟩 Green | Trust / credential issuer / positive screening result |
| 🟥 Red | High-risk indicator / SAR-restricted / PEP / withheld data |
| ⬜ Grey | Unknown or below-threshold party |
