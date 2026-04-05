### 1. AMLR Timeline and Scope (Directly Applicable Single Rulebook)
- **Entry into force**: 10 July 2027 (full application; no national transposition needed).
- **Scope**: All obliged entities (banks, payment providers, crypto-asset service providers/CASPs/VASPs, crowdfunding platforms, etc.) across the EU.
- **Core goal**: Harmonise CDD/KYC rules, reduce fragmentation, and explicitly embrace trusted digital identity to support remote onboarding while maintaining a risk-based approach.

AMLR replaces and strengthens parts of the old AML Directives with directly binding rules.

### 2. Key AMLR Integration Requirements for KYC/CDD
AMLR Article 22 (and recitals) is the centrepiece for **remote customer due diligence** and identity verification:

| Requirement | AMLR Detail | Relevance to Your Schema / App |
|-------------|-------------|--------------------------------|
| **Electronic identification acceptance** | Must accept eIDAS-compliant electronic identification means at **"substantial" or "high" assurance level** (or qualified trust services when eID unavailable). | Your **VerifiableCredential** wrapper (W3C VC v2 + SD-JWT support) matches eIDAS 2.0 / EUDI Wallet exactly. EUDI Wallets will be the primary high-assurance channel by end-2027. |
| **EUDI Wallet mandate** | Obliged entities **must accept** the European Digital Identity Wallet (EUDI) for identification/authentication where strong user authentication is required (cross-referenced with eIDAS Article 5f). | Hybrid schema lets you ingest wallet-presented credentials directly (selective disclosure of PID/LPID attributes) and embed them in `credentialSubject.ivms101`. |
| **Attribute verification** | Verify identity against authoritative sources via eIDAS methods. AMLA will issue RTS specifying required attribute sets for standard/simplified/enhanced DD. | The mapping table we already provided (IVMS 101 ↔ eIDAS PID/LPID) covers the expected fields (name, DOB, address, national ID, LEI, etc.). |
| **Record-keeping & evidence** | Retain full evidence of verification (including cryptographic proofs from eIDAS). | `proof` field in the VC wrapper + IVMS 101 payload provides auditable, tamper-evident records. |
| **Risk-based flexibility** | High-assurance eIDAS methods can reduce risk rating to standard/low (with appropriate controls). | Using the VC path in your schema can justify lighter ongoing monitoring. |
| **Legal entities / beneficial owners** | Same rules apply to legal persons and UBO verification. | `legalPerson` block + optional nested natural-person representatives in the schema fully supports this. |

Additional AMLR provisions relevant to data sharing:
- Reliance on third-party CDD (with conditions and access to underlying data).
- Group-wide data sharing (with safeguards).
- No new mandates conflicting with IVMS 101 for Travel Rule (crypto transfers remain zero-threshold in the EU and continue to use IVMS 101 as the interoperability standard).
