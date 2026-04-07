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
