# Tax Status — Mermaid Diagrams

This document contains Mermaid diagrams illustrating the five Tax Status example scenarios supported by OpenKYCAML v1.9.x. Each diagram corresponds to a JSON example file in `examples/tax/`.

For field-level mapping details, see:
- [Tax Status, TIN, ESR & Pillar 2 GloBE Mapping](../mappings/tax-status-oecd-esr-pillar2.md)
- [FATCA & CRS Mapping](../mappings/fatca-crs.md)

---

## Table of Contents

1. [Individual TIN Verification Flow](#1-individual-tin-verification-flow)
2. [Corporate VAT/GST Registration Flow](#2-corporate-vatgst-registration-flow)
3. [FATCA/CRS Compliance Flow](#3-fatcacrs-compliance-flow)
4. [MNE Pillar 2 GloBE Compliance Flow](#4-mne-pillar-2-globe-compliance-flow)
5. [Offshore Economic Substance (ESR) EDD Flow](#5-offshore-economic-substance-esr-edd-flow)

---

## 1. Individual TIN Verification Flow

**Example:** [`examples/tax/tax-individual-tin.json`](../../examples/tax/tax-individual-tin.json)

A natural person (Robert William Johnson) holds tax residency in two jurisdictions — the United States (SSN) and the United Kingdom (UTR). The VASP verifies both TINs via the respective revenue authority APIs before publishing the OpenKYCAML payload.

```mermaid
sequenceDiagram
    autonumber
    participant Customer as Robert W. Johnson
    participant VASP as Originating VASP
    participant IRS as IRS TIN Matching (US)
    participant HMRC as HMRC API (GB)
    participant Downstream as Beneficiary VASP

    Customer->>VASP: Provide self-certification with US SSN and GB UTR
    VASP->>IRS: Submit TIN match request for SSN 123-45-6789
    IRS-->>VASP: Return verified — tinType TIN matched to individual
    VASP->>HMRC: Validate UTR 1234567890
    HMRC-->>VASP: Return verified — functionalEquivalent confirmed
    VASP->>VASP: Build taxStatus.tinIdentifiers[] with two entries\n(jurisdiction US + GB, both verificationStatus verified)
    VASP->>VASP: Attach taxStatus block to OpenKYCAML v1.9.0 payload\nwith ivms101 originator and kycProfile CDD MEDIUM
    VASP->>Downstream: Transmit OpenKYCAML payload via Travel Rule protocol
    Downstream->>Downstream: Validate taxStatus.tinIdentifiers[]\nagainst OECD CRS / FATF R.16 requirements
    Downstream-->>VASP: ACK — dual-jurisdiction TIN data accepted
```

---

## 2. Corporate VAT/GST Registration Flow

**Example:** [`examples/tax/tax-corporate-vat-gst.json`](../../examples/tax/tax-corporate-vat-gst.json)

A German legal entity (TechGlobal Solutions GmbH) trading with an Indian counterparty holds both a German income-tax TIN and an Indian GST registration. The VASP validates entity legitimacy via EU VIES and the Indian GST portal before building the OpenKYCAML payload.

```mermaid
sequenceDiagram
    autonumber
    participant Entity as TechGlobal Solutions GmbH (DE)
    participant VASP as EuroVASP GmbH
    participant VIES as EU VIES (VAT Validation)
    participant GST as India GST Portal
    participant OECD as OECD TIN List
    participant Downstream as India Crypto Exchange VASP

    Entity->>VASP: Provide DE TIN, DE VAT number, and IN GST number on onboarding
    VASP->>OECD: Validate DE TIN 86095742719 against OECD TIN list
    OECD-->>VASP: Return verified — German Steueridentifikationsnummer confirmed
    VASP->>VIES: Validate VAT number DE123456789
    VIES-->>VASP: Return active — German VAT registration confirmed
    VASP->>GST: Validate GSTIN 27AAPFU0939F1ZV
    GST-->>VASP: Return active — Maharashtra GST registration confirmed
    VASP->>VASP: Build taxStatus.tinIdentifiers[] with DE TIN and IN GST entries
    VASP->>VASP: Build taxStatus.indirectTaxRegistrations[]\nwith VAT (DE) and GST (IN) entries, both status active
    VASP->>VASP: Attach taxStatus block to OpenKYCAML v1.9.0 payload\nwith LEI, beneficial ownership, and kycProfile CDD LOW
    VASP->>Downstream: Transmit OpenKYCAML payload
    Downstream->>Downstream: Verify entity legitimacy using\ntaxStatus.tinIdentifiers[] and indirectTaxRegistrations[]
    Downstream-->>VASP: ACK — corporate tax data accepted
```

---

## 3. FATCA/CRS Compliance Flow

**Example:** [`examples/tax/tax-fatca-crs.json`](../../examples/tax/tax-fatca-crs.json)

An Irish-registered financial institution (Atlantic Asset Management Ltd) is a Registered Deemed-Compliant FFI under FATCA and holds dual CRS tax residency in Ireland and the US. The VASP verifies the GIIN against the IRS FFI List and captures CRS self-certifications before transmitting the OpenKYCAML v1.9.1 payload.

```mermaid
sequenceDiagram
    autonumber
    participant FFI as Atlantic Asset Management Ltd (IE)
    participant VASP as Atlantic VASP Services Ltd
    participant IRS as IRS FFI List (FATCA)
    participant RevenueIE as Revenue Ireland (CRS TIN)
    participant IRStin as IRS TIN Matching (US CRS)
    participant Downstream as Cayman Digital VASP Ltd

    FFI->>VASP: Submit FATCA self-certification with GIIN ABC123.DEF45.LE.372
    FFI->>VASP: Submit CRS self-certification for IE residency (TIN IE6336214T)\nand US residency (EIN 98-7654321)
    VASP->>IRS: Verify GIIN ABC123.DEF45.LE.372 against IRS FFI List
    IRS-->>VASP: Return match — registeredDeemedCompliantFFI confirmed\nFFI List timestamp 2026-04-01T08:00:00Z
    VASP->>RevenueIE: Validate IE TIN IE6336214T
    RevenueIE-->>VASP: Return verified — Irish Tax Registration Number confirmed
    VASP->>IRStin: Validate US EIN 98-7654321
    IRStin-->>VASP: Return verified — US Employer Identification Number confirmed
    VASP->>VASP: Build taxStatus.fatcaStatus with GIIN,\nchapter4Classification, withholdingAgentReference
    VASP->>VASP: Build taxStatus.crsTaxResidencies[] with IE and US entries\n(selfCertificationDate, tinVerificationStatus, controllingPersonFlag false)
    VASP->>VASP: Attach taxStatus block to OpenKYCAML v1.9.1 payload\nwith LEI, ivms101, and kycProfile CDD MEDIUM
    VASP->>Downstream: Transmit OpenKYCAML payload
    Downstream->>Downstream: Verify GIIN and CRS residencies\nfor AEOI and FATCA withholding obligations
    Downstream-->>VASP: ACK — FATCA and CRS data accepted
```

---

## 4. MNE Pillar 2 GloBE Compliance Flow

**Example:** [`examples/tax/tax-mne-pillar2.json`](../../examples/tax/tax-mne-pillar2.json)

Apex Ireland Operations Ltd is a constituent entity of a multinational group (Apex International Group PLC) with consolidated revenue exceeding EUR 750 million. The VASP captures Pillar 2 GloBE effective tax rates across three jurisdictions and links the GloBE Information Return (GIR) filing reference for AML risk-scoring purposes.

```mermaid
sequenceDiagram
    autonumber
    participant MNE as Apex Ireland Operations Ltd (IE)
    participant VASP as EuroFinance VASP Ltd
    participant RevenueIE as Revenue Ireland
    participant IRS as IRS TIN Matching
    participant GIR as GloBE Information Return (OECD)
    participant AML as AML Risk Engine
    participant Downstream as US Digital Finance Corp VASP

    MNE->>VASP: Provide IE TIN, US EIN, consolidated revenue EUR 2.1bn,\nETRs for IE / US / DE, and GIR reference GIR-APEX-IE-2025-001
    VASP->>RevenueIE: Validate IE TIN IE6336214T
    RevenueIE-->>VASP: Return verified — Tax Registration Number confirmed
    VASP->>IRS: Validate US EIN 98-7654321
    IRS-->>VASP: Return verified — Employer Identification Number confirmed
    VASP->>GIR: Cross-reference GIR filing GIR-APEX-IE-2025-001
    GIR-->>VASP: Return filed — GloBE Information Return acknowledged\nlastGIRDate 2026-03-31
    VASP->>VASP: Build taxStatus.tinIdentifiers[] for IE and US
    VASP->>VASP: Build taxStatus.indirectTaxRegistrations[] for IE VAT
    VASP->>VASP: Build taxStatus.pillarTwo block\n(inScopeMNE true, revenue EUR 2.1bn, safeHarbourApplied SubstanceBased)\nETRs: IE 12.5%, US 21.0%, DE 29.8%
    VASP->>AML: Submit Pillar 2 data for BEPS risk scoring
    AML->>AML: Evaluate ETR differentials against GloBE\nminimum rate (15%)\nFlag IE ETR 12.5% as below-minimum — safe harbour applied
    AML-->>VASP: Risk score MEDIUM — safe harbour documented, GIR reference on file
    VASP->>VASP: Attach taxStatus block to OpenKYCAML v1.9.0 payload\nwith beneficial ownership and kycProfile CDD MEDIUM
    VASP->>Downstream: Transmit OpenKYCAML payload
    Downstream->>Downstream: Verify Pillar 2 constituent entity status\nand GIR reference for BEPS regulatory compliance
    Downstream-->>VASP: ACK — MNE Pillar 2 data accepted
```

---

## 5. Offshore Economic Substance (ESR) EDD Flow

**Example:** [`examples/tax/tax-offshore-esr.json`](../../examples/tax/tax-offshore-esr.json)

Meridian Holdings Ltd is a Cayman Islands holding and financing entity subject to the Cayman Islands Economic Substance Act. The entity is flagged as HIGH risk and subject to Enhanced Due Diligence (EDD). The VASP captures economic substance evidence and ESR notification/report references before approving the transaction.

```mermaid
sequenceDiagram
    autonumber
    participant Entity as Meridian Holdings Ltd (KY)
    participant VASP as Cayman Digital Assets VASP Ltd
    participant CIMA as CIMA Registry (Cayman Islands)
    participant ESR as Cayman ESR Portal
    participant EDD as EDD Review Team
    participant AML as AML / Sanctions Engine
    participant Downstream as Luxembourg Asset VASP SA

    Entity->>VASP: Onboard as HIGH-risk offshore holding/financing entity\nEDD channel CORRESPONDENT
    VASP->>AML: Screen Meridian Holdings Ltd\nagainst OFAC SDN, EU, UN, and HMT sanctions lists
    AML-->>VASP: Return CLEAR — no sanctions matches
    VASP->>CIMA: Validate registration MC-2024-0042891 in CIMA Registry
    CIMA-->>VASP: Return entity confirmed — Cayman Islands registered
    VASP->>CIMA: Retrieve KY TIN KY-TIN-2024-0042891
    CIMA-->>VASP: Return unverified — TIN on file, external verification not available
    VASP->>ESR: Cross-reference ESR notification and report KY-ESR-2025-MH-00312
    ESR-->>VASP: Return filed — inScope-RelevantEntity\nrelevantActivities: holdingCompany, financingLeasing\ncoreIncomeGeneratingActivitiesPerformed true\nlastNotificationDate 2025-11-30
    VASP->>EDD: Escalate to EDD review team\n(HIGH risk, offshore jurisdiction, unverified TIN)
    EDD->>EDD: Review economic substance evidence:\n— ESR report reference on file\n— Core income-generating activities confirmed in KY\n— Beneficial owner Caribbean Holdings Trust verified
    EDD-->>VASP: Approve — ESR obligations met, EDD documented\nauditMetadata recordVersion 2
    VASP->>VASP: Build taxStatus.tinIdentifiers[]\n(jurisdiction KY, verificationStatus unverified)
    VASP->>VASP: Build taxStatus.economicSubstance block\n(jurisdiction KY, status inScope-RelevantEntity,\nrelevantActivities holdingCompany + financingLeasing)
    VASP->>VASP: Attach taxStatus block to OpenKYCAML v1.9.0 payload\nwith EDD kycProfile and beneficialOwnership
    VASP->>Downstream: Transmit OpenKYCAML payload
    Downstream->>Downstream: Verify ESR evidence and EDD outcome\nfor AMLR Art. 26 shell-company risk assessment
    Downstream-->>VASP: ACK — offshore ESR data and EDD documentation accepted
```
