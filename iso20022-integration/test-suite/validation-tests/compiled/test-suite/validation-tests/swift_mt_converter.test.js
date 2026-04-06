"use strict";
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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_test_1 = require("node:test");
const strict_1 = __importDefault(require("node:assert/strict"));
const swift_mt_converter_js_1 = require("../../libraries/typescript/swift-mt-converter.js");
// ---------------------------------------------------------------------------
// Shared test payloads
// ---------------------------------------------------------------------------
const NATURAL_PERSON_PAYLOAD = {
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
const LEGAL_PERSON_PAYLOAD = {
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
function getField(mt, tag) {
    const re = new RegExp(`:${tag.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}:([\\s\\S]*?)(?=\\r?\\n:[0-9]{2}[A-Z]?:|$)`);
    const m = re.exec(mt);
    return m ? m[1].trim() : "";
}
// ---------------------------------------------------------------------------
// MT 103
// ---------------------------------------------------------------------------
(0, node_test_1.describe)("openkycamlToMt103", () => {
    (0, node_test_1.it)("produces a string", () => {
        strict_1.default.equal(typeof (0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD), "string");
    });
    (0, node_test_1.it)("contains :20: field", () => {
        strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD).includes(":20:"));
    });
    (0, node_test_1.it)("truncates ref to 16 chars", () => {
        const ref = getField((0, swift_mt_converter_js_1.openkycamlToMt103)({ ...NATURAL_PERSON_PAYLOAD, messageId: "A".repeat(40) }), "20");
        strict_1.default.ok(ref.length <= 16);
    });
    (0, node_test_1.it)(":23B: defaults to CRED", () => {
        strict_1.default.equal(getField((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD), "23B"), "CRED");
    });
    (0, node_test_1.it)(":32A: contains EUR", () => {
        strict_1.default.ok(getField((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD), "32A").includes("EUR"));
    });
    (0, node_test_1.it)(":32A: contains formatted amount", () => {
        strict_1.default.ok(getField((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD), "32A").includes("15000,00"));
    });
    (0, node_test_1.it)("non-fiat asset type becomes XXX in :32A:", () => {
        const payload = {
            ...NATURAL_PERSON_PAYLOAD,
            ivms101: { ...NATURAL_PERSON_PAYLOAD.ivms101, transferredAmount: { amount: "5.5", assetType: "BTC" } },
        };
        strict_1.default.ok(getField((0, swift_mt_converter_js_1.openkycamlToMt103)(payload), "32A").includes("XXX"));
    });
    (0, node_test_1.it)(":50K: contains originator name", () => {
        const f = getField((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD), "50K");
        strict_1.default.ok(f.includes("Nakamura") || f.includes("Yuki"));
    });
    (0, node_test_1.it)(":59: contains beneficiary name", () => {
        const f = getField((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD), "59");
        strict_1.default.ok(f.includes("Schmidt") || f.includes("Andreas"));
    });
    (0, node_test_1.it)(":59: contains beneficiary IBAN", () => {
        strict_1.default.ok(getField((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD), "59").includes("DE89370400440532013000"));
    });
    (0, node_test_1.it)(":71A: defaults to SHA", () => {
        strict_1.default.equal(getField((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD), "71A"), "SHA");
    });
    (0, node_test_1.it)(":71A: can be OUR", () => {
        strict_1.default.equal(getField((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD, { detailsOfCharges: "OUR" }), "71A"), "OUR");
    });
    (0, node_test_1.it)(":77B: present by default", () => {
        strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD).includes(":77B:"));
    });
    (0, node_test_1.it)(":77B: suppressed when include77b=false", () => {
        strict_1.default.ok(!(0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD, { include77b: false }).includes(":77B:"));
    });
    (0, node_test_1.it)(":77B: contains /ORDERRES/", () => {
        strict_1.default.ok(getField((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD), "77B").includes("/ORDERRES/"));
    });
    (0, node_test_1.it)(":77B: contains /BENEFRES/", () => {
        strict_1.default.ok(getField((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD), "77B").includes("/BENEFRES/"));
    });
    (0, node_test_1.it)(":77B: contains /UETR/", () => {
        strict_1.default.ok(getField((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD), "77B").includes("/UETR/"));
    });
    (0, node_test_1.it)(":52A: present (originating VASP)", () => {
        strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD).includes(":52A:"));
    });
    (0, node_test_1.it)(":57A: present (beneficiary VASP)", () => {
        strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD).includes(":57A:"));
    });
    (0, node_test_1.it)("throws when ivms101 missing", () => {
        strict_1.default.throws(() => (0, swift_mt_converter_js_1.openkycamlToMt103)({ version: "1.4.0" }), /ivms101/);
    });
    (0, node_test_1.it)("custom value date appears in :32A:", () => {
        const mt = (0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD, { valueDate: "2026-12-31" });
        strict_1.default.ok(getField(mt, "32A").startsWith("261231"));
    });
    (0, node_test_1.it)(":70: Remittance Info written when provided", () => {
        const mt = (0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD, { remittanceInfo: "INV-2026-0042" });
        strict_1.default.ok(mt.includes(":70:"));
        strict_1.default.ok(getField(mt, "70").includes("INV-2026-0042"));
    });
});
// ---------------------------------------------------------------------------
// MT 202
// ---------------------------------------------------------------------------
(0, node_test_1.describe)("openkycamlToMt202", () => {
    (0, node_test_1.it)("produces string", () => {
        strict_1.default.equal(typeof (0, swift_mt_converter_js_1.openkycamlToMt202)(LEGAL_PERSON_PAYLOAD), "string");
    });
    (0, node_test_1.it)("contains :20:", () => {
        strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt202)(LEGAL_PERSON_PAYLOAD).includes(":20:"));
    });
    (0, node_test_1.it)("contains :21:", () => {
        strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt202)(LEGAL_PERSON_PAYLOAD).includes(":21:"));
    });
    (0, node_test_1.it)("contains :32A: with amount", () => {
        strict_1.default.ok(getField((0, swift_mt_converter_js_1.openkycamlToMt202)(LEGAL_PERSON_PAYLOAD), "32A").includes("500000,00"));
    });
    (0, node_test_1.it)("contains :58A: beneficiary institution", () => {
        strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt202)(LEGAL_PERSON_PAYLOAD).includes(":58A:"));
    });
    (0, node_test_1.it)("does not contain :77B:", () => {
        strict_1.default.ok(!(0, swift_mt_converter_js_1.openkycamlToMt202)(LEGAL_PERSON_PAYLOAD).includes(":77B:"));
    });
    (0, node_test_1.it)("throws when ivms101 missing", () => {
        strict_1.default.throws(() => (0, swift_mt_converter_js_1.openkycamlToMt202)({ version: "1.4.0" }), /ivms101/);
    });
    (0, node_test_1.it)("custom related reference in :21:", () => {
        const mt = (0, swift_mt_converter_js_1.openkycamlToMt202)(LEGAL_PERSON_PAYLOAD, { relatedReference: "COVREF001" });
        strict_1.default.ok(getField(mt, "21").includes("COVREF001"));
    });
});
// ---------------------------------------------------------------------------
// MT 202 COV
// ---------------------------------------------------------------------------
(0, node_test_1.describe)("openkycamlToMt202Cov", () => {
    (0, node_test_1.it)("produces string", () => {
        strict_1.default.equal(typeof (0, swift_mt_converter_js_1.openkycamlToMt202Cov)(NATURAL_PERSON_PAYLOAD), "string");
    });
    (0, node_test_1.it)(":23B: is CRED", () => {
        strict_1.default.equal(getField((0, swift_mt_converter_js_1.openkycamlToMt202Cov)(NATURAL_PERSON_PAYLOAD), "23B"), "CRED");
    });
    (0, node_test_1.it)(":50A: contains underlying originator", () => {
        strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt202Cov)(NATURAL_PERSON_PAYLOAD).includes(":50A:"));
    });
    (0, node_test_1.it)(":59: contains underlying beneficiary", () => {
        strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt202Cov)(NATURAL_PERSON_PAYLOAD).includes(":59:"));
    });
    (0, node_test_1.it)(":72: contains /COV/ indicator", () => {
        strict_1.default.ok(getField((0, swift_mt_converter_js_1.openkycamlToMt202Cov)(NATURAL_PERSON_PAYLOAD), "72").includes("/COV/"));
    });
    (0, node_test_1.it)("throws when ivms101 missing", () => {
        strict_1.default.throws(() => (0, swift_mt_converter_js_1.openkycamlToMt202Cov)({ version: "1.4.0" }), /ivms101/);
    });
    (0, node_test_1.it)(":50A: contains originator name", () => {
        const f = getField((0, swift_mt_converter_js_1.openkycamlToMt202Cov)(NATURAL_PERSON_PAYLOAD), "50A");
        strict_1.default.ok(f.includes("Nakamura") || f.includes("Yuki"));
    });
});
// ---------------------------------------------------------------------------
// MT 910
// ---------------------------------------------------------------------------
(0, node_test_1.describe)("openkycamlToMt910", () => {
    (0, node_test_1.it)("produces string", () => {
        strict_1.default.equal(typeof (0, swift_mt_converter_js_1.openkycamlToMt910)(NATURAL_PERSON_PAYLOAD), "string");
    });
    (0, node_test_1.it)("contains :20:", () => strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt910)(NATURAL_PERSON_PAYLOAD).includes(":20:")));
    (0, node_test_1.it)("contains :25:", () => strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt910)(NATURAL_PERSON_PAYLOAD).includes(":25:")));
    (0, node_test_1.it)(":32A: contains EUR", () => strict_1.default.ok(getField((0, swift_mt_converter_js_1.openkycamlToMt910)(NATURAL_PERSON_PAYLOAD), "32A").includes("EUR")));
    (0, node_test_1.it)("contains :50:", () => strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt910)(NATURAL_PERSON_PAYLOAD).includes(":50:")));
    (0, node_test_1.it)("throws when ivms101 missing", () => {
        strict_1.default.throws(() => (0, swift_mt_converter_js_1.openkycamlToMt910)({ version: "1.4.0" }), /ivms101/);
    });
});
// ---------------------------------------------------------------------------
// MT 940
// ---------------------------------------------------------------------------
(0, node_test_1.describe)("openkycamlToMt940", () => {
    (0, node_test_1.it)("produces string", () => {
        strict_1.default.equal(typeof (0, swift_mt_converter_js_1.openkycamlToMt940)(NATURAL_PERSON_PAYLOAD), "string");
    });
    (0, node_test_1.it)("contains :28C:", () => strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt940)(NATURAL_PERSON_PAYLOAD).includes(":28C:")));
    (0, node_test_1.it)(":60F: starts with C", () => strict_1.default.ok(getField((0, swift_mt_converter_js_1.openkycamlToMt940)(NATURAL_PERSON_PAYLOAD), "60F").startsWith("C")));
    (0, node_test_1.it)("contains :61:", () => strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt940)(NATURAL_PERSON_PAYLOAD).includes(":61:")));
    (0, node_test_1.it)(":61: contains credit marker", () => strict_1.default.ok(getField((0, swift_mt_converter_js_1.openkycamlToMt940)(NATURAL_PERSON_PAYLOAD), "61").includes("C")));
    (0, node_test_1.it)("contains :86:", () => strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt940)(NATURAL_PERSON_PAYLOAD).includes(":86:")));
    (0, node_test_1.it)("contains :62F:", () => strict_1.default.ok((0, swift_mt_converter_js_1.openkycamlToMt940)(NATURAL_PERSON_PAYLOAD).includes(":62F:")));
    (0, node_test_1.it)("throws when ivms101 missing", () => {
        strict_1.default.throws(() => (0, swift_mt_converter_js_1.openkycamlToMt940)({ version: "1.4.0" }), /ivms101/);
    });
});
// ---------------------------------------------------------------------------
// MT → OpenKYCAML
// ---------------------------------------------------------------------------
(0, node_test_1.describe)("mtToOpenkycaml", () => {
    (0, node_test_1.it)("MT 103 → returns object", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.equal(typeof result, "object");
        strict_1.default.ok(result !== null);
    });
    (0, node_test_1.it)("MT 103 → schema URL present", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.ok((result.$schema ?? "").startsWith("https://openkycaml.org/schema/"));
    });
    (0, node_test_1.it)("MT 103 → version is 1.4.0", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.equal(result.version, "1.4.0");
    });
    (0, node_test_1.it)("MT 103 → messageId recovered", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.equal(result.messageId, "MT103-TS-T-001");
    });
    (0, node_test_1.it)("MT 103 → ivms101 present", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.ok(result.ivms101);
    });
    (0, node_test_1.it)("MT 103 → amount recovered", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.equal(result.ivms101?.transferredAmount?.amount, "15000.00");
        strict_1.default.equal(result.ivms101?.transferredAmount?.assetType, "EUR");
    });
    (0, node_test_1.it)("MT 103 → beneficiary account recovered", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        const accts = result.ivms101?.beneficiary?.accountNumber ?? [];
        strict_1.default.ok(accts.some((a) => a.includes("DE89370400440532013000")));
    });
    (0, node_test_1.it)("MT 103 → messageType tag is MT103", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.equal(result._swiftMtMetadata?.mtMessageType, "MT103");
    });
    (0, node_test_1.it)("MT 202 → messageType tag is MT202", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt202)(LEGAL_PERSON_PAYLOAD));
        strict_1.default.equal(result._swiftMtMetadata?.mtMessageType, "MT202");
    });
    (0, node_test_1.it)("MT 202 COV → messageType tag is MT202COV", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt202Cov)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.equal(result._swiftMtMetadata?.mtMessageType, "MT202COV");
    });
    (0, node_test_1.it)("MT 940 → messageType tag is MT940", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt940)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.equal(result._swiftMtMetadata?.mtMessageType, "MT940");
    });
    (0, node_test_1.it)("MT 103 → 77B metadata present", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.ok(result._swiftMtMetadata?.field77B);
    });
    (0, node_test_1.it)("MT 103 → chargeBearer recovered", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.equal(result._swiftMtMetadata?.chargeBearer, "SHA");
    });
    (0, node_test_1.it)("MT 202 → amount recovered", () => {
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt202)(LEGAL_PERSON_PAYLOAD));
        strict_1.default.equal(result.ivms101?.transferredAmount?.amount, "500000.00");
        strict_1.default.equal(result.ivms101?.transferredAmount?.assetType, "GBP");
    });
    (0, node_test_1.it)("raw MT 103 text parsed correctly", () => {
        const raw = ":20:TESTREF001\n:23B:CRED\n:32A:260406EUR9876,54\n" +
            ":50K:/GB29NWBK60161331926819\nJohn Smith\n123 High Street\n" +
            ":59:/DE89370400440532013000\nHans Mueller\n:71A:SHA\n" +
            ":77B:/ORDERRES/John Smith/GB29NW\n/BENEFRES/Hans Mueller/DE8937\n/UETR/TESTREF001\n";
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)(raw);
        strict_1.default.equal(result.messageId, "TESTREF001");
        strict_1.default.equal(result.ivms101?.transferredAmount?.amount, "9876.54");
        strict_1.default.equal(result.ivms101?.transferredAmount?.assetType, "EUR");
    });
    (0, node_test_1.it)("77B originator merged when 50K absent", () => {
        const raw = ":20:REFABC\n:23B:CRED\n:32A:260406USD500,00\n" +
            ":59:/12345678\nBene Corp\n:71A:OUR\n" +
            ":77B:/ORDERRES/Alice Wang/ACCT-99\n/BENEFRES/Bene Corp/12345678\n/UETR/REFABC\n";
        const result = (0, swift_mt_converter_js_1.mtToOpenkycaml)(raw);
        const origPersons = result.ivms101?.originator?.originatorPersons ?? [];
        strict_1.default.ok(origPersons.length > 0);
        const nameIds = origPersons[0].naturalPerson?.name?.nameIdentifier ?? [];
        strict_1.default.ok(nameIds.length > 0);
        strict_1.default.ok((nameIds[0].primaryIdentifier ?? "").includes("Alice") ||
            (nameIds[0].primaryIdentifier ?? "").includes("Wang"));
    });
});
// ---------------------------------------------------------------------------
// 77B helpers
// ---------------------------------------------------------------------------
(0, node_test_1.describe)("build77b", () => {
    (0, node_test_1.it)("returns string", () => {
        strict_1.default.equal(typeof (0, swift_mt_converter_js_1.build77b)(NATURAL_PERSON_PAYLOAD), "string");
    });
    (0, node_test_1.it)("contains /ORDERRES/", () => {
        strict_1.default.ok((0, swift_mt_converter_js_1.build77b)(NATURAL_PERSON_PAYLOAD).includes("/ORDERRES/"));
    });
    (0, node_test_1.it)("contains /BENEFRES/", () => {
        strict_1.default.ok((0, swift_mt_converter_js_1.build77b)(NATURAL_PERSON_PAYLOAD).includes("/BENEFRES/"));
    });
    (0, node_test_1.it)("contains /UETR/", () => {
        strict_1.default.ok((0, swift_mt_converter_js_1.build77b)(NATURAL_PERSON_PAYLOAD).includes("/UETR/"));
    });
    (0, node_test_1.it)("each line ≤ 35 chars", () => {
        for (const line of (0, swift_mt_converter_js_1.build77b)(NATURAL_PERSON_PAYLOAD).split("\n")) {
            strict_1.default.ok(line.length <= 35, `Line exceeds 35 chars: ${JSON.stringify(line)}`);
        }
    });
});
(0, node_test_1.describe)("parse77b", () => {
    const raw = "/ORDERRES/Alice Wang/ACCT001\n/BENEFRES/Bob Jones/ACCT002\n/UETR/REF-UETR-001";
    (0, node_test_1.it)("returns object", () => {
        strict_1.default.equal(typeof (0, swift_mt_converter_js_1.parse77b)(raw), "object");
    });
    (0, node_test_1.it)("originator name extracted", () => {
        const parsed = (0, swift_mt_converter_js_1.parse77b)(raw);
        const nameIds = parsed.originator77b?.naturalPerson?.name?.nameIdentifier ?? [];
        strict_1.default.ok(nameIds.length > 0);
        strict_1.default.ok((nameIds[0].primaryIdentifier ?? "").includes("Alice") ||
            (nameIds[0].primaryIdentifier ?? "").includes("Wang"));
    });
    (0, node_test_1.it)("beneficiary name extracted", () => {
        const parsed = (0, swift_mt_converter_js_1.parse77b)(raw);
        const nameIds = parsed.beneficiary77b?.naturalPerson?.name?.nameIdentifier ?? [];
        strict_1.default.ok(nameIds.length > 0);
        strict_1.default.ok((nameIds[0].primaryIdentifier ?? "").includes("Bob") ||
            (nameIds[0].primaryIdentifier ?? "").includes("Jones"));
    });
    (0, node_test_1.it)("uetr extracted", () => {
        strict_1.default.equal((0, swift_mt_converter_js_1.parse77b)(raw).uetr, "REF-UETR-001");
    });
    (0, node_test_1.it)("originator account extracted", () => {
        strict_1.default.equal((0, swift_mt_converter_js_1.parse77b)(raw).originator77b?._account, "ACCT001");
    });
});
// ---------------------------------------------------------------------------
// Round-trip
// ---------------------------------------------------------------------------
(0, node_test_1.describe)("MT 103 round-trip", () => {
    (0, node_test_1.it)("preserves amount", () => {
        const r = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.equal(r.ivms101?.transferredAmount?.amount, "15000.00");
    });
    (0, node_test_1.it)("preserves currency", () => {
        const r = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.equal(r.ivms101?.transferredAmount?.assetType, "EUR");
    });
    (0, node_test_1.it)("preserves beneficiary account", () => {
        const r = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        const accts = r.ivms101?.beneficiary?.accountNumber ?? [];
        strict_1.default.ok(accts.some((a) => a.includes("DE89370400440532013000")));
    });
    (0, node_test_1.it)("preserves message ID", () => {
        const r = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt103)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.equal(r.messageId, "MT103-TS-T-001");
    });
    (0, node_test_1.it)("MT 202 round-trip preserves amount", () => {
        const r = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt202)(LEGAL_PERSON_PAYLOAD));
        strict_1.default.equal(r.ivms101?.transferredAmount?.amount, "500000.00");
    });
    (0, node_test_1.it)("MT 202 COV round-trip message type", () => {
        const r = (0, swift_mt_converter_js_1.mtToOpenkycaml)((0, swift_mt_converter_js_1.openkycamlToMt202Cov)(NATURAL_PERSON_PAYLOAD));
        strict_1.default.equal(r._swiftMtMetadata?.mtMessageType, "MT202COV");
    });
});
