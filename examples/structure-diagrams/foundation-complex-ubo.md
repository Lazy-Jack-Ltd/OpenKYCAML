# foundation-complex-ubo.json — Structure Diagram

**Scenario:** Private Foundation Beneficial Ownership — Liechtenstein Privatstiftung.  
Steinberg Asset Management AG (Switzerland VASP) is 100% owned by the Steinberg Privatstiftung (Liechtenstein). The founder, Heinrich Steinberg (DE), retains statutory appointment/dismissal powers over the three-person Foundation Council under PGR Art. 552 §29, conferring DE_FACTO_CONTROL and triggering UBO identification under AMLR Art. 26(2)(c).

```mermaid
flowchart TD
    subgraph UBO["Ultimate Beneficial Owner — Founder"]
        UBO1["👤 Heinrich Klaus Steinberg\nUBO + Founder · DE\nPassport: DE-PASS-C01X00T47\nDOB: 1951-03-12, Munich\nUnter den Linden 77, Berlin\n⚡ Statutory Powers (PGR Art. 552 §29):\n   Appoint + dismiss all council members\n   at any time without cause\n💼 Also named PRIMARY BENEFICIARY\n   (supplementary beneficiary declaration)"]
    end

    subgraph Foundation["Steinberg Privatstiftung — Liechtenstein"]
        FOUND["🏛️ Steinberg Privatstiftung\nLiechtenstein Private Foundation\nOGD Register: FL-OGD-2008-FL-0002.344.671-5\nEstablished: 5 September 2008\n(PGR Art. 552 §§1–41)\nHolds 100% of Steinberg Asset Management AG"]

        subgraph Council["Foundation Council (Governing Body)"]
            C1["👤 Dr. Andreas Josef Mayer\n**Chairman** · LI\nPassport: LI-PASS-FL00012345\nDOB: 1963-09-18, Vaduz\nCasting vote at council meetings\nAppointed by founder (since 2008-09-05)"]
            C2["👤 Dr. Helga Maria Kirchner\nCouncil Member · DE\nPassport: DE-PASS-D12345678\nDOB: 1967-04-25, Frankfurt am Main\nResponsible for investment oversight\nAppointed by founder (since 2008-09-05)"]
            C3["👤 Marco Aurelio Bergomi\nCouncil Member · CH\nPassport: CH-PASS-X8765432\nDOB: 1970-12-05, Lugano\nResponsible for compliance + legal\nAppointed by founder (since 2015-01-10)"]
        end

        subgraph Beneficiaries_Found["Beneficiaries (Foundation Statutes)"]
            BFND["👤 Heinrich Steinberg\n+ lineal descendants\n(exclusive beneficiary class)\nHeinrich: primary income beneficiary\nFamily: capital beneficiaries on succession"]
        end
    end

    subgraph Subject["Subject Entity — Swiss VASP"]
        SUBJECT["🏢 Steinberg Asset Management AG\nVASP · Switzerland · CHE-456-789-012\nLEI: 529900SAMCHZH00001CH\nBahnhofstrasse 21, Zurich\nRisk: HIGH · EDD · Liechtenstein foundation ownership"]
    end

    subgraph Transfer["Travel Rule Transfer — CH → DE"]
        BVASP["🏦 Frankfurt Digital Assets GmbH · Germany\nBeneficiary VASP\nDID: did:web:frankfurt-digital-assets.example.de\nLEI: 529900FDADE000001DE0\nIssues KYCAttestation VC"]
    end

    UBO1 -- "Founder: settled assets 2008\n⚡ Retains appointment/dismissal\npower over ALL council members\n(PGR Art. 552 §29)" --> FOUND
    UBO1 -- "Appoints + dismisses" --> Council
    FOUND -- "100% shareholding" --> SUBJECT
    UBO1 -.-> BFND
    SUBJECT -- "1,200,000 USDC\nOpenKYCAML VC" --> BVASP

    style UBO1 fill:#dbeafe,stroke:#3b82f6
    style FOUND fill:#f3e8ff,stroke:#9333ea
    style C1 fill:#ede9fe,stroke:#7c3aed
    style C2 fill:#ede9fe,stroke:#7c3aed
    style C3 fill:#ede9fe,stroke:#7c3aed
    style BFND fill:#dcfce7,stroke:#16a34a
    style SUBJECT fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
```

## UBO Control Path under PGR Art. 552 §29

```mermaid
flowchart LR
    FOUNDER["Heinrich Steinberg\nFounder (UBO)"]
    POWER["⚡ PGR Art. 552 §29\nFounder reservation:\nAppoint/dismiss council\nat any time without cause"]
    COUNCIL["Foundation Council\n(3 members)\nMayer + Kirchner + Bergomi"]
    ASSET["Steinberg Privatstiftung\nholds 100% of SAM AG"]
    VASP["Steinberg Asset\nManagement AG (VASP)"]

    FOUNDER -- "Exercises" --> POWER
    POWER -- "Controls" --> COUNCIL
    COUNCIL -- "Governs" --> ASSET
    ASSET -- "100% owns" --> VASP
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Structure | Liechtenstein Privatstiftung (PGR Art. 552) |
| Subject VASP | Steinberg Asset Management AG (CH) |
| UBO | Heinrich Klaus Steinberg (DE) — founder |
| Control mechanism | DE_FACTO_CONTROL via PGR Art. 552 §29 reservation powers |
| Foundation Council | 3 members (Chairman + 2 members) — all natural persons |
| Beneficiaries | Founder + lineal descendants (exclusive class) |
| Asset / Amount | 1,200,000 USDC |
| Beneficiary VASP | Frankfurt Digital Assets GmbH (DE) |
| Risk | HIGH · EDD |
| Regulatory basis | FATF Recommendation 25, AMLR Art. 26(2)(c) |
