/**
 * Test Suite: OpenKYCAML ↔ SWIFT MT Converter (TypeScript)
 * =========================================================
 * Tests for iso20022-integration/libraries/typescript/swift-mt-converter.ts
 *
 * Covers MT 103, MT 202, MT 202 COV, MT 910, MT 940 — bidirectional
 * round-trips, full field mapping, and :77B: Travel Rule handling.
 *
 * Compile and run:
 *   cd iso20022-integration/libraries/typescript
 *   npx tsc --project tsconfig.tests.json
 *   node --test ../../test-suite/validation-tests/swift_mt_converter.test.mjs
 */

import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  openkycamlToMt103,
  openkycamlToMt202,
  openkycamlToMt202Cov,
  openkycamlToMt910,
  openkycamlToMt940,
  mtToOpenkycaml,
  build77b,
  parse77b,
  type OpenKYCAMLPayload,
} from "../../libraries/typescript/swift-mt-converter.js";

// ---------------------------------------------------------------------------
// Shared test payloads
// ---------------------------------------------------------------------------

const NATURAL_PERSON_PAYLOAD: OpenKYCAMLPayload = {
  $schema: "https://openkycaml.org/schema/v1.4.0/kyc-aml-hybrid-extended.json",
  version: "1.4.0",
  messageId: "MT103-TS-T-001",
  messageDateTime: "2026-04-06T10:00:00Z",
  ivms101: {
    originator: {
      originatorPersons: [
        {
          naturalPerson: {
            name: {
              nameIdentifier: [
                {
                  primaryIdentifier: "Nakamura",
                  secondaryIdentifier: "Yuki",
                  nameIdentifierType: "LEGL",
                },
              ],
            },
            nationalIdentification: {
              nationalIdentifier: "JP-MYNUMBER-99887766",
              nationalIdentifierType: "TXID",
              countryOfIssue: "JP",
            },
            geographicAddresses: [
              { streetName: "Sakura-dori 12", townName: "Tokyo", country: "JP" },
            ],
            countryOfResidence: "JP",
          },
        },
      ],
      accountNumber: ["JP12MUFG1234567890123456"],
    },
    beneficiary: {
      beneficiaryPersons: [
        {
          naturalPerson: {
            name: {
              nameIdentifier: [
                {
                  primaryIdentifier: "Schmidt",
                  secondaryIdentifier: "Andreas",
                  nameIdentifierType: "LEGL",
                },
              ],
            },
            geographicAddresses: [
              { streetName: "Hauptstrasse 5", townName: "Berlin", country: "DE" },
            ],
            countryOfResidence: "DE",
          },
        },
      ],
      accountNumber: ["DE89370400440532013000"],
    },
    originatingVASP: { name: "Tokyo Digital Bank", lei: "353800F0ADKV6MKZJQ22" },
    beneficiaryVASP: { name: "Berlin Crypto Exchange", lei: "529900T8BM49AAMSDO55" },
    transferredAmount: { amount: "15000.00", assetType: "EUR" },
  },
};

const LEGAL_PERSON_PAYLOAD: OpenKYCAMLPayload = {
  $schema: "https://openkycaml.org/schema/v1.4.0/kyc-aml-hybrid-extended.json",
  version: "1.4.0",
  messageId: "MT202-TS-TEST-002",
  messageDateTime: "2026-04-06T11:00:00Z",
  ivms101: {
    originator: {
      originatorPersons: [
        {
          legalPerson: {
            name: {
              nameIdentifier: [
                { legalPersonName: "Alpha Capital Ltd", legalPersonNameIdentifierType: "LEGL" },
              ],
            },
            nationalIdentification: {
              nationalIdentifier: "529900HNOAA1KXQJUQ27",
              nationalIdentifierType: "LEIX",
            },
            countryOfRegistration: "GB",
          },
        },
      ],
      accountNumber: ["GB29NWBK60161331926819"],
    },
    beneficiary: {
      beneficiaryPersons: [
        {
          legalPerson: {
            name: {
              nameIdentifier: [
                { legalPersonName: "Beta Finance GmbH", legalPersonNameIdentifierType: "LEGL" },
              ],
            },
            nationalIdentification: {
              nationalIdentifier: "529900T8BM49AAMSDO22",
              nationalIdentifierType: "LEIX",
            },
            countryOfRegistration: "DE",
          },
        },
      ],
      accountNumber: ["DE89370400440532013000"],
    },
    originatingVASP: { name: "Alpha Digital Bank", lei: "213800WDAVG00001GB00" },
    beneficiaryVASP: { name: "Beta Digital Exchange", lei: "213800WDAVG00001DE00" },
    transferredAmount: { amount: "500000.00", assetType: "GBP" },
  },
};

// ---------------------------------------------------------------------------
// Helper
// ---------------------------------------------------------------------------

function getField(mt: string, tag: string): string {
  const re = new RegExp(`:${tag.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}:([\\s\\S]*?)(?=\\r?\\n:[0-9]{2}[A-Z]?:|$)`);
  const m = re.exec(mt);
  return m ? m[1].trim() : "";
}

// ---------------------------------------------------------------------------
// MT 103
// ---------------------------------------------------------------------------

describe("openkycamlToMt103", () => {
  it("produces a string", () => {
    assert.equal(typeof openkycamlToMt103(NATURAL_PERSON_PAYLOAD), "string");
  });

  it("contains :20: field", () => {
    assert.ok(openkycamlToMt103(NATURAL_PERSON_PAYLOAD).includes(":20:"));
  });

  it("truncates ref to 16 chars", () => {
    const ref = getField(openkycamlToMt103({ ...NATURAL_PERSON_PAYLOAD, messageId: "A".repeat(40) }), "20");
    assert.ok(ref.length <= 16);
  });

  it(":23B: defaults to CRED", () => {
    assert.equal(getField(openkycamlToMt103(NATURAL_PERSON_PAYLOAD), "23B"), "CRED");
  });

  it(":32A: contains EUR", () => {
    assert.ok(getField(openkycamlToMt103(NATURAL_PERSON_PAYLOAD), "32A").includes("EUR"));
  });

  it(":32A: contains formatted amount", () => {
    assert.ok(getField(openkycamlToMt103(NATURAL_PERSON_PAYLOAD), "32A").includes("15000,00"));
  });

  it("non-fiat asset type becomes XXX in :32A:", () => {
    const payload: OpenKYCAMLPayload = {
      ...NATURAL_PERSON_PAYLOAD,
      ivms101: { ...NATURAL_PERSON_PAYLOAD.ivms101, transferredAmount: { amount: "5.5", assetType: "BTC" } },
    };
    assert.ok(getField(openkycamlToMt103(payload), "32A").includes("XXX"));
  });

  it(":50K: contains originator name", () => {
    const f = getField(openkycamlToMt103(NATURAL_PERSON_PAYLOAD), "50K");
    assert.ok(f.includes("Nakamura") || f.includes("Yuki"));
  });

  it(":59: contains beneficiary name", () => {
    const f = getField(openkycamlToMt103(NATURAL_PERSON_PAYLOAD), "59");
    assert.ok(f.includes("Schmidt") || f.includes("Andreas"));
  });

  it(":59: contains beneficiary IBAN", () => {
    assert.ok(getField(openkycamlToMt103(NATURAL_PERSON_PAYLOAD), "59").includes("DE89370400440532013000"));
  });

  it(":71A: defaults to SHA", () => {
    assert.equal(getField(openkycamlToMt103(NATURAL_PERSON_PAYLOAD), "71A"), "SHA");
  });

  it(":71A: can be OUR", () => {
    assert.equal(getField(openkycamlToMt103(NATURAL_PERSON_PAYLOAD, { detailsOfCharges: "OUR" }), "71A"), "OUR");
  });

  it(":77B: present by default", () => {
    assert.ok(openkycamlToMt103(NATURAL_PERSON_PAYLOAD).includes(":77B:"));
  });

  it(":77B: suppressed when include77b=false", () => {
    assert.ok(!openkycamlToMt103(NATURAL_PERSON_PAYLOAD, { include77b: false }).includes(":77B:"));
  });

  it(":77B: contains /ORDERRES/", () => {
    assert.ok(getField(openkycamlToMt103(NATURAL_PERSON_PAYLOAD), "77B").includes("/ORDERRES/"));
  });

  it(":77B: contains /BENEFRES/", () => {
    assert.ok(getField(openkycamlToMt103(NATURAL_PERSON_PAYLOAD), "77B").includes("/BENEFRES/"));
  });

  it(":77B: contains /UETR/", () => {
    assert.ok(getField(openkycamlToMt103(NATURAL_PERSON_PAYLOAD), "77B").includes("/UETR/"));
  });

  it(":52A: present (originating VASP)", () => {
    assert.ok(openkycamlToMt103(NATURAL_PERSON_PAYLOAD).includes(":52A:"));
  });

  it(":57A: present (beneficiary VASP)", () => {
    assert.ok(openkycamlToMt103(NATURAL_PERSON_PAYLOAD).includes(":57A:"));
  });

  it("throws when ivms101 missing", () => {
    assert.throws(() => openkycamlToMt103({ version: "1.4.0" }), /ivms101/);
  });

  it("custom value date appears in :32A:", () => {
    const mt = openkycamlToMt103(NATURAL_PERSON_PAYLOAD, { valueDate: "2026-12-31" });
    assert.ok(getField(mt, "32A").startsWith("261231"));
  });

  it(":70: Remittance Info written when provided", () => {
    const mt = openkycamlToMt103(NATURAL_PERSON_PAYLOAD, { remittanceInfo: "INV-2026-0042" });
    assert.ok(mt.includes(":70:"));
    assert.ok(getField(mt, "70").includes("INV-2026-0042"));
  });
});

// ---------------------------------------------------------------------------
// MT 202
// ---------------------------------------------------------------------------

describe("openkycamlToMt202", () => {
  it("produces string", () => {
    assert.equal(typeof openkycamlToMt202(LEGAL_PERSON_PAYLOAD), "string");
  });
  it("contains :20:", () => {
    assert.ok(openkycamlToMt202(LEGAL_PERSON_PAYLOAD).includes(":20:"));
  });
  it("contains :21:", () => {
    assert.ok(openkycamlToMt202(LEGAL_PERSON_PAYLOAD).includes(":21:"));
  });
  it("contains :32A: with amount", () => {
    assert.ok(getField(openkycamlToMt202(LEGAL_PERSON_PAYLOAD), "32A").includes("500000,00"));
  });
  it("contains :58A: beneficiary institution", () => {
    assert.ok(openkycamlToMt202(LEGAL_PERSON_PAYLOAD).includes(":58A:"));
  });
  it("does not contain :77B:", () => {
    assert.ok(!openkycamlToMt202(LEGAL_PERSON_PAYLOAD).includes(":77B:"));
  });
  it("throws when ivms101 missing", () => {
    assert.throws(() => openkycamlToMt202({ version: "1.4.0" }), /ivms101/);
  });
  it("custom related reference in :21:", () => {
    const mt = openkycamlToMt202(LEGAL_PERSON_PAYLOAD, { relatedReference: "COVREF001" });
    assert.ok(getField(mt, "21").includes("COVREF001"));
  });
});

// ---------------------------------------------------------------------------
// MT 202 COV
// ---------------------------------------------------------------------------

describe("openkycamlToMt202Cov", () => {
  it("produces string", () => {
    assert.equal(typeof openkycamlToMt202Cov(NATURAL_PERSON_PAYLOAD), "string");
  });
  it(":23B: is CRED", () => {
    assert.equal(getField(openkycamlToMt202Cov(NATURAL_PERSON_PAYLOAD), "23B"), "CRED");
  });
  it(":50A: contains underlying originator", () => {
    assert.ok(openkycamlToMt202Cov(NATURAL_PERSON_PAYLOAD).includes(":50A:"));
  });
  it(":59: contains underlying beneficiary", () => {
    assert.ok(openkycamlToMt202Cov(NATURAL_PERSON_PAYLOAD).includes(":59:"));
  });
  it(":72: contains /COV/ indicator", () => {
    assert.ok(getField(openkycamlToMt202Cov(NATURAL_PERSON_PAYLOAD), "72").includes("/COV/"));
  });
  it("throws when ivms101 missing", () => {
    assert.throws(() => openkycamlToMt202Cov({ version: "1.4.0" }), /ivms101/);
  });
  it(":50A: contains originator name", () => {
    const f = getField(openkycamlToMt202Cov(NATURAL_PERSON_PAYLOAD), "50A");
    assert.ok(f.includes("Nakamura") || f.includes("Yuki"));
  });
});

// ---------------------------------------------------------------------------
// MT 910
// ---------------------------------------------------------------------------

describe("openkycamlToMt910", () => {
  it("produces string", () => {
    assert.equal(typeof openkycamlToMt910(NATURAL_PERSON_PAYLOAD), "string");
  });
  it("contains :20:", () => assert.ok(openkycamlToMt910(NATURAL_PERSON_PAYLOAD).includes(":20:")));
  it("contains :25:", () => assert.ok(openkycamlToMt910(NATURAL_PERSON_PAYLOAD).includes(":25:")));
  it(":32A: contains EUR", () => assert.ok(getField(openkycamlToMt910(NATURAL_PERSON_PAYLOAD), "32A").includes("EUR")));
  it("contains :50:", () => assert.ok(openkycamlToMt910(NATURAL_PERSON_PAYLOAD).includes(":50:")));
  it("throws when ivms101 missing", () => {
    assert.throws(() => openkycamlToMt910({ version: "1.4.0" }), /ivms101/);
  });
});

// ---------------------------------------------------------------------------
// MT 940
// ---------------------------------------------------------------------------

describe("openkycamlToMt940", () => {
  it("produces string", () => {
    assert.equal(typeof openkycamlToMt940(NATURAL_PERSON_PAYLOAD), "string");
  });
  it("contains :28C:", () => assert.ok(openkycamlToMt940(NATURAL_PERSON_PAYLOAD).includes(":28C:")));
  it(":60F: starts with C", () => assert.ok(getField(openkycamlToMt940(NATURAL_PERSON_PAYLOAD), "60F").startsWith("C")));
  it("contains :61:", () => assert.ok(openkycamlToMt940(NATURAL_PERSON_PAYLOAD).includes(":61:")));
  it(":61: contains credit marker", () => assert.ok(getField(openkycamlToMt940(NATURAL_PERSON_PAYLOAD), "61").includes("C")));
  it("contains :86:", () => assert.ok(openkycamlToMt940(NATURAL_PERSON_PAYLOAD).includes(":86:")));
  it("contains :62F:", () => assert.ok(openkycamlToMt940(NATURAL_PERSON_PAYLOAD).includes(":62F:")));
  it("throws when ivms101 missing", () => {
    assert.throws(() => openkycamlToMt940({ version: "1.4.0" }), /ivms101/);
  });
});

// ---------------------------------------------------------------------------
// MT → OpenKYCAML
// ---------------------------------------------------------------------------

describe("mtToOpenkycaml", () => {
  it("MT 103 → returns object", () => {
    const result = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    assert.equal(typeof result, "object");
    assert.ok(result !== null);
  });

  it("MT 103 → schema URL present", () => {
    const result = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    assert.ok((result.$schema ?? "").startsWith("https://openkycaml.org/schema/"));
  });

  it("MT 103 → version is 1.4.0", () => {
    const result = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    assert.equal(result.version, "1.4.0");
  });

  it("MT 103 → messageId recovered", () => {
    const result = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    assert.equal(result.messageId, "MT103-TS-T-001");
  });

  it("MT 103 → ivms101 present", () => {
    const result = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    assert.ok(result.ivms101);
  });

  it("MT 103 → amount recovered", () => {
    const result = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    assert.equal(result.ivms101?.transferredAmount?.amount, "15000.00");
    assert.equal(result.ivms101?.transferredAmount?.assetType, "EUR");
  });

  it("MT 103 → beneficiary account recovered", () => {
    const result = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    const accts = result.ivms101?.beneficiary?.accountNumber ?? [];
    assert.ok(accts.some((a) => a.includes("DE89370400440532013000")));
  });

  it("MT 103 → messageType tag is MT103", () => {
    const result = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    assert.equal((result._swiftMtMetadata as Record<string, unknown>)?.mtMessageType, "MT103");
  });

  it("MT 202 → messageType tag is MT202", () => {
    const result = mtToOpenkycaml(openkycamlToMt202(LEGAL_PERSON_PAYLOAD));
    assert.equal((result._swiftMtMetadata as Record<string, unknown>)?.mtMessageType, "MT202");
  });

  it("MT 202 COV → messageType tag is MT202COV", () => {
    const result = mtToOpenkycaml(openkycamlToMt202Cov(NATURAL_PERSON_PAYLOAD));
    assert.equal((result._swiftMtMetadata as Record<string, unknown>)?.mtMessageType, "MT202COV");
  });

  it("MT 940 → messageType tag is MT940", () => {
    const result = mtToOpenkycaml(openkycamlToMt940(NATURAL_PERSON_PAYLOAD));
    assert.equal((result._swiftMtMetadata as Record<string, unknown>)?.mtMessageType, "MT940");
  });

  it("MT 103 → 77B metadata present", () => {
    const result = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    assert.ok((result._swiftMtMetadata as Record<string, unknown>)?.field77B);
  });

  it("MT 103 → chargeBearer recovered", () => {
    const result = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    assert.equal((result._swiftMtMetadata as Record<string, unknown>)?.chargeBearer, "SHA");
  });

  it("MT 202 → amount recovered", () => {
    const result = mtToOpenkycaml(openkycamlToMt202(LEGAL_PERSON_PAYLOAD));
    assert.equal(result.ivms101?.transferredAmount?.amount, "500000.00");
    assert.equal(result.ivms101?.transferredAmount?.assetType, "GBP");
  });

  it("raw MT 103 text parsed correctly", () => {
    const raw =
      ":20:TESTREF001\n:23B:CRED\n:32A:260406EUR9876,54\n" +
      ":50K:/GB29NWBK60161331926819\nJohn Smith\n123 High Street\n" +
      ":59:/DE89370400440532013000\nHans Mueller\n:71A:SHA\n" +
      ":77B:/ORDERRES/John Smith/GB29NW\n/BENEFRES/Hans Mueller/DE8937\n/UETR/TESTREF001\n";
    const result = mtToOpenkycaml(raw);
    assert.equal(result.messageId, "TESTREF001");
    assert.equal(result.ivms101?.transferredAmount?.amount, "9876.54");
    assert.equal(result.ivms101?.transferredAmount?.assetType, "EUR");
  });

  it("77B originator merged when 50K absent", () => {
    const raw =
      ":20:REFABC\n:23B:CRED\n:32A:260406USD500,00\n" +
      ":59:/12345678\nBene Corp\n:71A:OUR\n" +
      ":77B:/ORDERRES/Alice Wang/ACCT-99\n/BENEFRES/Bene Corp/12345678\n/UETR/REFABC\n";
    const result = mtToOpenkycaml(raw);
    const origPersons = result.ivms101?.originator?.originatorPersons ?? [];
    assert.ok(origPersons.length > 0);
    const nameIds = origPersons[0].naturalPerson?.name?.nameIdentifier ?? [];
    assert.ok(nameIds.length > 0);
    assert.ok(
      (nameIds[0].primaryIdentifier ?? "").includes("Alice") ||
      (nameIds[0].primaryIdentifier ?? "").includes("Wang")
    );
  });
});

// ---------------------------------------------------------------------------
// 77B helpers
// ---------------------------------------------------------------------------

describe("build77b", () => {
  it("returns string", () => {
    assert.equal(typeof build77b(NATURAL_PERSON_PAYLOAD), "string");
  });
  it("contains /ORDERRES/", () => {
    assert.ok(build77b(NATURAL_PERSON_PAYLOAD).includes("/ORDERRES/"));
  });
  it("contains /BENEFRES/", () => {
    assert.ok(build77b(NATURAL_PERSON_PAYLOAD).includes("/BENEFRES/"));
  });
  it("contains /UETR/", () => {
    assert.ok(build77b(NATURAL_PERSON_PAYLOAD).includes("/UETR/"));
  });
  it("each line ≤ 35 chars", () => {
    for (const line of build77b(NATURAL_PERSON_PAYLOAD).split("\n")) {
      assert.ok(line.length <= 35, `Line exceeds 35 chars: ${JSON.stringify(line)}`);
    }
  });
});

describe("parse77b", () => {
  const raw = "/ORDERRES/Alice Wang/ACCT001\n/BENEFRES/Bob Jones/ACCT002\n/UETR/REF-UETR-001";

  it("returns object", () => {
    assert.equal(typeof parse77b(raw), "object");
  });
  it("originator name extracted", () => {
    const parsed = parse77b(raw);
    const nameIds = parsed.originator77b?.naturalPerson?.name?.nameIdentifier ?? [];
    assert.ok(nameIds.length > 0);
    assert.ok(
      (nameIds[0].primaryIdentifier ?? "").includes("Alice") ||
      (nameIds[0].primaryIdentifier ?? "").includes("Wang")
    );
  });
  it("beneficiary name extracted", () => {
    const parsed = parse77b(raw);
    const nameIds = parsed.beneficiary77b?.naturalPerson?.name?.nameIdentifier ?? [];
    assert.ok(nameIds.length > 0);
    assert.ok(
      (nameIds[0].primaryIdentifier ?? "").includes("Bob") ||
      (nameIds[0].primaryIdentifier ?? "").includes("Jones")
    );
  });
  it("uetr extracted", () => {
    assert.equal(parse77b(raw).uetr, "REF-UETR-001");
  });
  it("originator account extracted", () => {
    assert.equal(parse77b(raw).originator77b?._account, "ACCT001");
  });
});

// ---------------------------------------------------------------------------
// Round-trip
// ---------------------------------------------------------------------------

describe("MT 103 round-trip", () => {
  it("preserves amount", () => {
    const r = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    assert.equal(r.ivms101?.transferredAmount?.amount, "15000.00");
  });
  it("preserves currency", () => {
    const r = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    assert.equal(r.ivms101?.transferredAmount?.assetType, "EUR");
  });
  it("preserves beneficiary account", () => {
    const r = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    const accts = r.ivms101?.beneficiary?.accountNumber ?? [];
    assert.ok(accts.some((a) => a.includes("DE89370400440532013000")));
  });
  it("preserves message ID", () => {
    const r = mtToOpenkycaml(openkycamlToMt103(NATURAL_PERSON_PAYLOAD));
    assert.equal(r.messageId, "MT103-TS-T-001");
  });
  it("MT 202 round-trip preserves amount", () => {
    const r = mtToOpenkycaml(openkycamlToMt202(LEGAL_PERSON_PAYLOAD));
    assert.equal(r.ivms101?.transferredAmount?.amount, "500000.00");
  });
  it("MT 202 COV round-trip message type", () => {
    const r = mtToOpenkycaml(openkycamlToMt202Cov(NATURAL_PERSON_PAYLOAD));
    assert.equal((r._swiftMtMetadata as Record<string, unknown>)?.mtMessageType, "MT202COV");
  });
});
