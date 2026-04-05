# minimal-travel-rule.json — Structure Diagram

**Scenario:** Minimal IVMS 101 Travel Rule — Natural Person to Natural Person (Japan → South Korea).  
Hiroshi Tanaka (JP) sends 1 BTC to Ji-Yeon Kim (KR). Minimal required fields only; IVMS101.2023 payload metadata included.

```mermaid
flowchart TD
    subgraph Originator_Side["Originating Side — Japan"]
        O["👤 Hiroshi Tanaka\nNaturalPerson · JP\nMyNumber: JP-MYNUMBER-1234-5678-9012\nCustomer ID: CUST-JP-0087231\nWallet: bc1qar0srrr7..."]
        OVASP["🏦 Tokyo Digital Assets Co., Ltd.\nOriginating VASP · JP\nLEI: 3538003FPHWP7EM5C773\nTxRef: TDAC-20240615-BTC-0000042"]
    end

    subgraph Beneficiary_Side["Beneficiary Side — South Korea"]
        BVASP["🏦 Seoul Blockchain Exchange Inc.\nBeneficiary VASP · KR\nLEI: 724500YRI6OZO6ELB439"]
        B["👤 Ji-Yeon Kim\nNaturalPerson · KR\nRRN: KR-RRN-900101-2234567\nWallet: bc1p0xlxvlh..."]
    end

    O -- "Initiates transfer\n1 BTC" --> OVASP
    OVASP -- "IVMS 101 Travel Rule message\n(IVMS101.2023)\n1.00 BTC" --> BVASP
    BVASP -- "Credits account" --> B

    style O fill:#dbeafe,stroke:#3b82f6
    style B fill:#dbeafe,stroke:#3b82f6
    style OVASP fill:#fef9c3,stroke:#eab308
    style BVASP fill:#fef9c3,stroke:#eab308
```

## Key Data Points

| Field | Value |
|---|---|
| Schema | OpenKYCAML v1.3.0 |
| Message type | IVMS 101 plain (no VC wrapper) |
| Payload version | IVMS101.2023 |
| Originator | Hiroshi Tanaka, JP natural person |
| Beneficiary | Ji-Yeon Kim, KR natural person |
| Asset / Amount | 1.00 BTC |
| Originating VASP | Tokyo Digital Assets Co., Ltd. (JP) |
| Beneficiary VASP | Seoul Blockchain Exchange Inc. (KR) |
| Transaction ref | TDAC-20240615-BTC-0000042 |
