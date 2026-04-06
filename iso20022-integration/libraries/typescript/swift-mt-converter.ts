/**
 * OpenKYCAML × SWIFT MT Converter (TypeScript / ESM)
 * =====================================================
 * Bidirectional converter between OpenKYCAML v1.4.0 payloads and legacy SWIFT
 * MT messages.
 *
 * Supported message types
 * -----------------------
 * MT 103   Customer Credit Transfer
 * MT 202   General Financial Institution Transfer
 * MT 202 COV  Covered Financial Institution Transfer
 * MT 910   Confirmation of Credit
 * MT 940   Customer Statement Message
 *
 * Exports
 * -------
 * openkycamlToMt103(payload, config?)   → string
 * openkycamlToMt202(payload, config?)   → string
 * openkycamlToMt202Cov(payload, config?) → string
 * openkycamlToMt910(payload, config?)   → string
 * openkycamlToMt940(payload, config?)   → string
 * mtToOpenkycaml(mtText)                → OpenKYCAMLPayload
 * build77b(payload)                     → string
 * parse77b(field77b)                    → Parsed77B
 *
 * Dependencies
 * ------------
 * None — pure Node.js standard library (crypto for randomUUID).
 *
 * Usage
 * -----
 *   import { openkycamlToMt103, mtToOpenkycaml } from "./swift-mt-converter.js";
 *   const mt103 = openkycamlToMt103(payload);
 *   const recovered = mtToOpenkycaml(mt103);
 */

import { randomUUID } from "crypto";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface NameIdentifier {
  primaryIdentifier?: string;
  secondaryIdentifier?: string;
  nameIdentifierType?: string;
  legalPersonName?: string;
  legalPersonNameIdentifierType?: string;
}

export interface NationalIdentification {
  nationalIdentifier?: string;
  nationalIdentifierType?: string;
  countryOfIssue?: string;
}

export interface Address {
  streetName?: string;
  buildingNumber?: string;
  postCode?: string;
  townName?: string;
  country?: string;
  addressLine?: string[];
}

export interface NaturalPerson {
  name?: { nameIdentifier?: NameIdentifier[] };
  nationalIdentification?: NationalIdentification;
  dateAndPlaceOfBirth?: { dateOfBirth?: string; placeOfBirth?: string; countryOfBirth?: string };
  geographicAddresses?: Address[];
  countryOfResidence?: string;
}

export interface LegalPerson {
  name?: { nameIdentifier?: NameIdentifier[] };
  nationalIdentification?: NationalIdentification;
  geographicAddresses?: Address[];
  countryOfRegistration?: string;
}

export interface PersonWrapper {
  naturalPerson?: NaturalPerson;
  legalPerson?: LegalPerson;
}

export interface VASP {
  name?: string;
  lei?: string;
  vaspIdentifier?: string;
}

export interface OpenKYCAMLPayload {
  $schema?: string;
  version?: string;
  messageId?: string;
  messageDateTime?: string;
  ivms101?: {
    originator?: { originatorPersons?: PersonWrapper[]; accountNumber?: string[] };
    beneficiary?: { beneficiaryPersons?: PersonWrapper[]; accountNumber?: string[] };
    originatingVASP?: VASP;
    beneficiaryVASP?: VASP;
    transferPath?: VASP[];
    transferredAmount?: { amount?: string; assetType?: string };
    payloadMetadata?: Record<string, unknown>;
  };
  kycProfile?: Record<string, unknown>;
  verifiableCredential?: Record<string, unknown>;
  gdprSensitivityMetadata?: Record<string, unknown>;
  _swiftMtMetadata?: Record<string, unknown>;
}

export interface SwiftMtConfig {
  /** ISO 8601 date override for value date (:32A:) */
  valueDate?: string;
  /** :23B: bank operation code (default: CRED) */
  bankOperationCode?: string;
  /** :71A: details of charges (SHA/OUR/BEN, default: SHA) */
  detailsOfCharges?: string;
  /** :21: related reference for MT 202 / MT 202 COV */
  relatedReference?: string;
  /** :72: Sender to Receiver Information */
  senderToReceiver?: string;
  /** :70: Remittance Information */
  remittanceInfo?: string;
  /** Include :77B: Travel Rule field in MT 103 (default: true) */
  include77b?: boolean;
  /** :25: account identifier for MT 910 / MT 940 */
  accountId?: string;
  /** :28C: statement number / sequence for MT 940 */
  statementNumber?: string;
  /** :60F: opening balance for MT 940 */
  openingBalance?: string;
  /** Currency for opening balance (default: transfer currency) */
  openingBalanceCurrency?: string;
}

export interface Parsed77B {
  originator77b?: { naturalPerson: NaturalPerson; _account?: string };
  beneficiary77b?: { naturalPerson: NaturalPerson; _account?: string };
  uetr?: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SCHEMA_URL = "https://openkycaml.org/schema/v1.4.0/kyc-aml-hybrid-extended.json";
const SCHEMA_VERSION = "1.4.0";
const MAX_REF = 16;
const MAX_NAME = 35;
const DATE_FORMAT_RE = /^(\d{4})-(\d{2})-(\d{2})/;
const IBAN_RE = /^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$/;

const ISO4217_CODES = new Set(
  ("AED AFN ALL AMD ANG AOA ARS AUD AWG AZN BAM BBD BDT BGN BHD BMD BND BOB BRL BSD BTN BWP BYN "
  + "BZD CAD CDF CHF CLP CNY COP CRC CUP CVE CZK DJF DKK DOP DZD EGP ETB EUR FJD GBP GEL GHS "
  + "GIP GMD GNF GTQ GYD HKD HNL HTG HUF IDR ILS INR IQD IRR ISK JMD JOD JPY KES KGS KHR KMF "
  + "KRW KWD KYD KZT LAK LBP LKR LRD LSL LYD MAD MDL MGA MKD MMK MNT MOP MRU MUR MVR MWK MXN "
  + "MYR MZN NAD NGN NIO NOK NPR NZD OMR PAB PEN PGK PHP PKR PLN PYG QAR RON RSD RUB RWF SAR "
  + "SBD SCR SDG SEK SGD SHP SLE SOS SRD STN SVC SYP SZL THB TJS TMT TND TOP TRY TTD TWD TZS "
  + "UAH UGX USD UYU UZS VES VND VUV WST XAF XCD XOF XPF YER ZAR ZMW ZWL XXX").split(" ")
);

const ORDERRES_PREFIX = "/ORDERRES/";
const BENEFRES_PREFIX = "/BENEFRES/";
const UETR_PREFIX = "/UETR/";

// ---------------------------------------------------------------------------
// Utility helpers
// ---------------------------------------------------------------------------

function nowIso(): string {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

function nowYmd(): string {
  const d = new Date();
  const yy = String(d.getUTCFullYear()).slice(2);
  const mm = String(d.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(d.getUTCDate()).padStart(2, "0");
  return `${yy}${mm}${dd}`;
}

function isoToYmd(isoDate: string): string {
  const m = DATE_FORMAT_RE.exec(isoDate);
  if (!m) return nowYmd();
  const yy = m[1].slice(2);
  return `${yy}${m[2]}${m[3]}`;
}

function ymdToIso(ymd: string): string {
  if (ymd.length < 6) return nowIso().slice(0, 10);
  const year = 2000 + parseInt(ymd.slice(0, 2), 10);
  const month = ymd.slice(2, 4);
  const day = ymd.slice(4, 6);
  return `${year}-${month}-${day}`;
}

function isFiat(code: string): boolean {
  return ISO4217_CODES.has(code.toUpperCase());
}

function isIban(value: string): boolean {
  return IBAN_RE.test(value.toUpperCase());
}

function shortRef(ref: string): string {
  return ref.replace(/\s/g, "-").slice(0, MAX_REF);
}

function formatAmount(amountStr: string): string {
  const v = parseFloat(amountStr);
  if (isNaN(v)) return amountStr.replace(".", ",");
  return v.toFixed(2).replace(".", ",");
}

function parseAmount(swiftAmount: string): string {
  return swiftAmount.replace(",", ".");
}

// ---------------------------------------------------------------------------
// Party helpers
// ---------------------------------------------------------------------------

function getNameString(person: PersonWrapper): string {
  if (person.naturalPerson) {
    const ids = person.naturalPerson.name?.nameIdentifier ?? [];
    if (ids.length > 0) {
      const ni = ids[0];
      return [ni.secondaryIdentifier, ni.primaryIdentifier].filter(Boolean).join(" ").trim();
    }
  }
  if (person.legalPerson) {
    const ids = person.legalPerson.name?.nameIdentifier ?? [];
    const legl = ids.find((n) => n.legalPersonNameIdentifierType === "LEGL");
    return (legl ?? ids[0])?.legalPersonName ?? "";
  }
  return "";
}

function getAddressLines(person: PersonWrapper): string[] {
  const p = person.naturalPerson ?? person.legalPerson;
  const addrs = p?.geographicAddresses ?? [];
  if (!addrs.length) return [];
  const addr = addrs[0];
  const lines: string[] = [];
  const street = [addr.streetName, addr.buildingNumber].filter(Boolean).join(" ").trim();
  if (street) lines.push(street.slice(0, MAX_NAME));
  const city = [addr.postCode, addr.townName].filter(Boolean).join(" ").trim();
  if (city) lines.push(city.slice(0, MAX_NAME));
  if (addr.country) lines.push(addr.country.slice(0, MAX_NAME));
  for (const al of addr.addressLine ?? []) lines.push(al.slice(0, MAX_NAME));
  return lines.slice(0, 3);
}

function buildPartyLines(person: PersonWrapper, accounts: string[], includeAccount = true): string[] {
  const lines: string[] = [];
  if (includeAccount && accounts.length > 0) {
    lines.push(`/${accounts[0]}`.slice(0, 35));
  }
  const nm = getNameString(person);
  if (nm) lines.push(nm.slice(0, MAX_NAME));
  lines.push(...getAddressLines(person));
  return lines;
}

function getBicOrLei(vasp: VASP): string {
  if (vasp.lei) return vasp.lei.slice(0, 11);
  if (vasp.name) return vasp.name.slice(0, MAX_NAME);
  return "";
}

function build32a(valueDate: string, ccy: string, amount: string): string {
  const ymd = valueDate ? isoToYmd(valueDate) : nowYmd();
  const fiatCcy = isFiat(ccy) ? ccy : "XXX";
  return `${ymd}${fiatCcy}${formatAmount(amount)}`;
}

function build32b(ccy: string, amount: string): string {
  const fiatCcy = isFiat(ccy) ? ccy : "XXX";
  return `${fiatCcy}${formatAmount(amount)}`;
}

function extract32a(value: string): { valueDate: string; ccy: string; amount: string } {
  if (value.length < 9) return { valueDate: nowIso().slice(0, 10), ccy: "XXX", amount: "0.00" };
  const ymd = value.slice(0, 6);
  const ccy = value.slice(6, 9).toUpperCase();
  const amtSwift = value.slice(9);
  return { valueDate: ymdToIso(ymd), ccy, amount: parseAmount(amtSwift) };
}

function extract32b(value: string): { ccy: string; amount: string } {
  if (value.length < 4) return { ccy: "XXX", amount: "0.00" };
  const ccy = value.slice(0, 3).toUpperCase();
  const amtSwift = value.slice(3);
  return { ccy, amount: parseAmount(amtSwift) };
}

// ---------------------------------------------------------------------------
// MT field parser
// ---------------------------------------------------------------------------

/** Parse raw SWIFT FIN text into a map of tag → [value, ...] */
function splitMtFields(mtText: string): Map<string, string[]> {
  const fields = new Map<string, string[]>();
  // Strip block 4 wrapper if present
  const block4Match = /\{4:\r?\n([\s\S]*?)\r?\n-\}/.exec(mtText);
  const content = block4Match ? block4Match[1] : mtText;

  const pattern = /:([0-9]{2}[A-Z]?):([\s\S]*?)(?=\r?\n:[0-9]{2}[A-Z]?:|$)/g;
  let m: RegExpExecArray | null;
  while ((m = pattern.exec(content)) !== null) {
    const tag = m[1];
    const value = m[2].trim();
    if (!fields.has(tag)) fields.set(tag, []);
    fields.get(tag)!.push(value);
  }
  return fields;
}

function getField(fields: Map<string, string[]>, ...tags: string[]): string {
  for (const tag of tags) {
    const vals = fields.get(tag);
    if (vals?.length) return vals[0].trim();
  }
  return "";
}

// ---------------------------------------------------------------------------
// :77B: Travel Rule carrier
// ---------------------------------------------------------------------------

/**
 * Build an MT 103 :77B: Regulatory Reporting field value from an
 * OpenKYCAML payload (outbound — OpenKYCAML → MT).
 *
 * Format (up to 3 × 35-char lines):
 *   /ORDERRES/<originator name>/<account>
 *   /BENEFRES/<beneficiary name>/<account>
 *   /UETR/<messageId>
 */
export function build77b(payload: OpenKYCAMLPayload): string {
  const ivms = payload.ivms101 ?? {};
  const origPersons = ivms.originator?.originatorPersons ?? [];
  const benePersons = ivms.beneficiary?.beneficiaryPersons ?? [];
  const origAccounts = ivms.originator?.accountNumber ?? [];
  const beneAccounts = ivms.beneficiary?.accountNumber ?? [];

  const origName = origPersons.length ? getNameString(origPersons[0]) : "";
  const beneName = benePersons.length ? getNameString(benePersons[0]) : "";
  let origAcct = origAccounts[0] ?? "";
  const beneAcct = beneAccounts[0] ?? "";

  // FATF fallback: use national ID if no account
  if (!origAcct && origPersons.length) {
    const p = origPersons[0].naturalPerson ?? origPersons[0].legalPerson;
    origAcct = p?.nationalIdentification?.nationalIdentifier ?? "";
  }

  const msgId = payload.messageId ?? randomUUID();

  const line1 = `${ORDERRES_PREFIX}${origName.slice(0, 20)}/${origAcct.slice(0, 12)}`.slice(0, 35);
  const line2 = `${BENEFRES_PREFIX}${beneName.slice(0, 20)}/${beneAcct.slice(0, 12)}`.slice(0, 35);
  const line3 = `${UETR_PREFIX}${msgId.slice(0, 28)}`.slice(0, 35);

  return `${line1}\n${line2}\n${line3}`;
}

/**
 * Parse an MT 103 :77B: field value (inbound — MT → OpenKYCAML).
 *
 * Best-effort extraction of:
 * - /ORDERRES/ → originator name and account
 * - /BENEFRES/ → beneficiary name and account
 * - /UETR/     → message UETR
 */
export function parse77b(field77b: string): Parsed77B {
  const result: Parsed77B = {};

  for (const line of field77b.split(/\r?\n/)) {
    const trimmed = line.trim();

    if (trimmed.startsWith(ORDERRES_PREFIX)) {
      const rest = trimmed.slice(ORDERRES_PREFIX.length);
      const [namePart, acctPart] = rest.split("/");
      const name = (namePart ?? "").trim();
      const acct = (acctPart ?? "").trim();
      const np: NaturalPerson = {};
      if (name) {
        np.name = { nameIdentifier: [{ primaryIdentifier: name, nameIdentifierType: "LEGL" }] };
      }
      if (acct) {
        np.nationalIdentification = { nationalIdentifier: acct, nationalIdentifierType: "MISC" };
      }
      result.originator77b = { naturalPerson: np, _account: acct };
    } else if (trimmed.startsWith(BENEFRES_PREFIX)) {
      const rest = trimmed.slice(BENEFRES_PREFIX.length);
      const [namePart, acctPart] = rest.split("/");
      const name = (namePart ?? "").trim();
      const acct = (acctPart ?? "").trim();
      const np: NaturalPerson = {};
      if (name) {
        np.name = { nameIdentifier: [{ primaryIdentifier: name, nameIdentifierType: "LEGL" }] };
      }
      result.beneficiary77b = { naturalPerson: np, _account: acct };
    } else if (trimmed.startsWith(UETR_PREFIX)) {
      result.uetr = trimmed.slice(UETR_PREFIX.length).trim();
    }
  }

  return result;
}

// ---------------------------------------------------------------------------
// MT 103 Producer
// ---------------------------------------------------------------------------

/**
 * Produce a SWIFT MT 103 Customer Credit Transfer from an OpenKYCAML payload.
 *
 * @param payload  OpenKYCAML envelope containing an ivms101 block.
 * @param config   Optional overrides (valueDate, detailsOfCharges, include77b, etc.)
 * @returns        SWIFT MT 103 message string (plain FIN format).
 * @throws         Error if payload lacks an ivms101 block.
 */
export function openkycamlToMt103(payload: OpenKYCAMLPayload, config: SwiftMtConfig = {}): string {
  const ivms = payload.ivms101;
  if (!ivms) throw new Error("No 'ivms101' block found in payload. Cannot produce MT 103.");

  const msgId = payload.messageId ?? randomUUID();
  const ref = shortRef(msgId);
  const origPersons = ivms.originator?.originatorPersons ?? [];
  const benePersons = ivms.beneficiary?.beneficiaryPersons ?? [];
  const origAccounts = ivms.originator?.accountNumber ?? [];
  const beneAccounts = ivms.beneficiary?.accountNumber ?? [];
  const amount = ivms.transferredAmount?.amount ?? "0";
  const assetType = ivms.transferredAmount?.assetType ?? "XXX";
  const ccy = isFiat(assetType) ? assetType : "XXX";
  const origVasp = ivms.originatingVASP ?? {};
  const beneVasp = ivms.beneficiaryVASP ?? {};
  const transferPath = ivms.transferPath ?? [];

  const valueDate =
    config.valueDate ?? (payload.messageDateTime ?? nowIso()).slice(0, 10);
  const bankOpCode = config.bankOperationCode ?? "CRED";
  const chargesCode = config.detailsOfCharges ?? "SHA";

  const lines: string[] = [];
  lines.push(`:20:${ref}`);
  lines.push(`:23B:${bankOpCode}`);
  lines.push(`:32A:${build32a(valueDate, ccy, amount)}`);

  // :50K: Ordering Customer
  if (origPersons.length) {
    const partyLines = buildPartyLines(origPersons[0], origAccounts);
    if (partyLines.length) lines.push(`:50K:${partyLines.join("\n")}`);
  } else if (origAccounts.length) {
    lines.push(`:50K:/${origAccounts[0].slice(0, 34)}`);
  }

  // :52A: Ordering Institution (originating VASP)
  const origAgt = getBicOrLei(origVasp);
  if (origAgt) lines.push(`:52A:${origAgt}`);

  // :56A: Intermediary Institution
  if (transferPath.length) {
    const intAgt = getBicOrLei(transferPath[0]);
    if (intAgt) lines.push(`:56A:${intAgt}`);
  }

  // :57A: Account With Institution (beneficiary VASP)
  const beneAgt = getBicOrLei(beneVasp);
  if (beneAgt) lines.push(`:57A:${beneAgt}`);

  // :59: Beneficiary Customer
  if (benePersons.length) {
    const partyLines = buildPartyLines(benePersons[0], beneAccounts);
    if (partyLines.length) lines.push(`:59:${partyLines.join("\n")}`);
  } else if (beneAccounts.length) {
    lines.push(`:59:/${beneAccounts[0].slice(0, 34)}`);
  }

  // :70: Remittance Information
  const rmt =
    config.remittanceInfo ??
    ((payload.kycProfile?.relationshipPurpose as string | undefined) ||
      (payload.kycProfile?.customerId as string | undefined) ||
      "");
  if (rmt) lines.push(`:70:${rmt.slice(0, 140)}`);

  // :71A: Details of Charges
  lines.push(`:71A:${chargesCode}`);

  // :77B: Regulatory Reporting (Travel Rule)
  if (config.include77b !== false) {
    const field77b = build77b(payload);
    if (field77b.trim()) lines.push(`:77B:${field77b}`);
  }

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// MT 202 Producer
// ---------------------------------------------------------------------------

/**
 * Produce a SWIFT MT 202 General Financial Institution Transfer.
 *
 * @param payload  OpenKYCAML envelope.
 * @param config   Optional overrides.
 * @returns        SWIFT MT 202 message string.
 * @throws         Error if payload lacks an ivms101 block.
 */
export function openkycamlToMt202(payload: OpenKYCAMLPayload, config: SwiftMtConfig = {}): string {
  const ivms = payload.ivms101;
  if (!ivms) throw new Error("No 'ivms101' block found in payload. Cannot produce MT 202.");

  const msgId = payload.messageId ?? randomUUID();
  const ref = shortRef(msgId);
  const relatedRef = (config.relatedReference ?? "NONREF").slice(0, 16);
  const amount = ivms.transferredAmount?.amount ?? "0";
  const assetType = ivms.transferredAmount?.assetType ?? "XXX";
  const ccy = isFiat(assetType) ? assetType : "XXX";
  const valueDate = config.valueDate ?? (payload.messageDateTime ?? nowIso()).slice(0, 10);
  const origVasp = ivms.originatingVASP ?? {};
  const beneVasp = ivms.beneficiaryVASP ?? {};
  const transferPath = ivms.transferPath ?? [];

  const lines: string[] = [];
  lines.push(`:20:${ref}`);
  lines.push(`:21:${relatedRef}`);
  lines.push(`:32A:${build32a(valueDate, ccy, amount)}`);

  const origAgt = getBicOrLei(origVasp);
  if (origAgt) lines.push(`:52A:${origAgt}`);

  if (transferPath.length) {
    const intAgt = getBicOrLei(transferPath[0]);
    if (intAgt) lines.push(`:56A:${intAgt}`);
  }

  const beneAgt = getBicOrLei(beneVasp);
  if (beneAgt) lines.push(`:58A:${beneAgt}`);

  if (config.senderToReceiver) lines.push(`:72:${config.senderToReceiver.slice(0, 35)}`);

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// MT 202 COV Producer
// ---------------------------------------------------------------------------

/**
 * Produce a SWIFT MT 202 COV Covered Financial Institution Transfer.
 * Includes underlying customer originator/beneficiary for FATF Rec. 16.
 *
 * @param payload  OpenKYCAML envelope.
 * @param config   Optional overrides.
 * @returns        SWIFT MT 202 COV message string.
 * @throws         Error if payload lacks an ivms101 block.
 */
export function openkycamlToMt202Cov(payload: OpenKYCAMLPayload, config: SwiftMtConfig = {}): string {
  const ivms = payload.ivms101;
  if (!ivms) throw new Error("No 'ivms101' block found in payload. Cannot produce MT 202 COV.");

  const msgId = payload.messageId ?? randomUUID();
  const ref = shortRef(msgId);
  const relatedRef = (config.relatedReference ?? "NONREF").slice(0, 16);
  const amount = ivms.transferredAmount?.amount ?? "0";
  const assetType = ivms.transferredAmount?.assetType ?? "XXX";
  const ccy = isFiat(assetType) ? assetType : "XXX";
  const valueDate = config.valueDate ?? (payload.messageDateTime ?? nowIso()).slice(0, 10);
  const origPersons = ivms.originator?.originatorPersons ?? [];
  const benePersons = ivms.beneficiary?.beneficiaryPersons ?? [];
  const origAccounts = ivms.originator?.accountNumber ?? [];
  const beneAccounts = ivms.beneficiary?.accountNumber ?? [];
  const origVasp = ivms.originatingVASP ?? {};
  const beneVasp = ivms.beneficiaryVASP ?? {};
  const transferPath = ivms.transferPath ?? [];

  const lines: string[] = [];
  lines.push(`:20:${ref}`);
  lines.push(`:21:${relatedRef}`);
  lines.push(`:23B:CRED`);
  lines.push(`:32A:${build32a(valueDate, ccy, amount)}`);

  const origAgt = getBicOrLei(origVasp);
  if (origAgt) lines.push(`:52A:${origAgt}`);

  if (transferPath.length) {
    const intAgt = getBicOrLei(transferPath[0]);
    if (intAgt) lines.push(`:56A:${intAgt}`);
  }

  const beneAgt = getBicOrLei(beneVasp);
  if (beneAgt) lines.push(`:58A:${beneAgt}`);

  // Underlying customer info (COV-specific)
  if (origPersons.length) {
    const partyLines = buildPartyLines(origPersons[0], origAccounts);
    if (partyLines.length) lines.push(`:50A:${partyLines.join("\n")}`);
  }
  if (benePersons.length) {
    const partyLines = buildPartyLines(benePersons[0], beneAccounts);
    if (partyLines.length) lines.push(`:59:${partyLines.join("\n")}`);
  }

  const s2r = config.senderToReceiver ?? "/COV/";
  lines.push(`:72:${s2r.slice(0, 35)}`);

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// MT 910 Producer
// ---------------------------------------------------------------------------

/**
 * Produce a SWIFT MT 910 Confirmation of Credit.
 *
 * @param payload  OpenKYCAML envelope.
 * @param config   Optional overrides.
 * @returns        SWIFT MT 910 message string.
 * @throws         Error if payload lacks an ivms101 block.
 */
export function openkycamlToMt910(payload: OpenKYCAMLPayload, config: SwiftMtConfig = {}): string {
  const ivms = payload.ivms101;
  if (!ivms) throw new Error("No 'ivms101' block found in payload. Cannot produce MT 910.");

  const msgId = payload.messageId ?? randomUUID();
  const ref = shortRef(msgId);
  const amount = ivms.transferredAmount?.amount ?? "0";
  const assetType = ivms.transferredAmount?.assetType ?? "XXX";
  const ccy = isFiat(assetType) ? assetType : "XXX";
  const valueDate = config.valueDate ?? (payload.messageDateTime ?? nowIso()).slice(0, 10);
  const origPersons = ivms.originator?.originatorPersons ?? [];
  const origVasp = ivms.originatingVASP ?? {};

  const lines: string[] = [];
  lines.push(`:20:${ref}`);
  lines.push(`:25:${(config.accountId ?? "NOSTRO").slice(0, 35)}`);
  lines.push(`:32A:${build32a(valueDate, ccy, amount)}`);

  // :50: Ordering Customer
  const orderingName =
    origPersons.length ? getNameString(origPersons[0]) : (origVasp.name ?? "");
  if (orderingName) lines.push(`:50:${orderingName.slice(0, MAX_NAME)}`);

  // :52A: Ordering Institution
  const origAgt = getBicOrLei(origVasp);
  if (origAgt) lines.push(`:52A:${origAgt}`);

  if (config.senderToReceiver) lines.push(`:72:${config.senderToReceiver.slice(0, 35)}`);

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// MT 940 Producer
// ---------------------------------------------------------------------------

/**
 * Produce a SWIFT MT 940 Customer Statement Message.
 * A single OpenKYCAML transfer payload becomes one credit statement entry.
 *
 * @param payload  OpenKYCAML envelope.
 * @param config   Optional overrides.
 * @returns        SWIFT MT 940 message string.
 * @throws         Error if payload lacks an ivms101 block.
 */
export function openkycamlToMt940(payload: OpenKYCAMLPayload, config: SwiftMtConfig = {}): string {
  const ivms = payload.ivms101;
  if (!ivms) throw new Error("No 'ivms101' block found in payload. Cannot produce MT 940.");

  const msgId = payload.messageId ?? randomUUID();
  const ref = shortRef(msgId);
  const amount = ivms.transferredAmount?.amount ?? "0";
  const assetType = ivms.transferredAmount?.assetType ?? "XXX";
  const ccy = isFiat(assetType) ? assetType : "XXX";
  const valueDate = config.valueDate ?? (payload.messageDateTime ?? nowIso()).slice(0, 10);
  const valueYmd = isoToYmd(valueDate);
  const entryDate = valueYmd.slice(2); // MMDD
  const formattedAmt = formatAmount(amount);
  const openingBalance = config.openingBalance ?? "0,00";
  const openingCcy = config.openingBalanceCurrency ?? ccy;

  const origPersons = ivms.originator?.originatorPersons ?? [];
  const origName = origPersons.length ? getNameString(origPersons[0]) : "";

  const lines: string[] = [];
  lines.push(`:20:${ref}`);
  lines.push(`:25:${(config.accountId ?? "NOSTRO").slice(0, 35)}`);
  lines.push(`:28C:${(config.statementNumber ?? "00001/001").slice(0, 10)}`);
  lines.push(`:60F:C${valueYmd}${openingCcy}${openingBalance}`);
  lines.push(`:61:${valueYmd}${entryDate}C${ccy}${formattedAmt}NTRF${ref.slice(0, 16)}`);

  const infoLine = origName ? `FROM ${origName.slice(0, 28)}` : `TXN ${msgId.slice(0, 30)}`;
  lines.push(`:86:${infoLine.slice(0, 65)}`);

  // :62F: Closing balance = opening + transferred
  let closingStr = formattedAmt;
  try {
    const openingNum = parseFloat(openingBalance.replace(",", "."));
    const transferNum = parseFloat(amount);
    closingStr = formatAmount(String(openingNum + transferNum));
  } catch {
    /* use formattedAmt as fallback */
  }
  lines.push(`:62F:C${valueYmd}${ccy}${closingStr}`);

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// MT → OpenKYCAML (Inbound)
// ---------------------------------------------------------------------------

function parsePartyLines(raw: string): { account: string; name: string; addrLines: string[] } {
  const lines = raw.trim().split(/\r?\n/);
  let account = "";
  let name = "";
  const addrLines: string[] = [];
  let idx = 0;
  if (lines[idx]?.startsWith("/")) {
    account = lines[idx].slice(1).trim();
    idx++;
  }
  if (idx < lines.length) {
    name = lines[idx].trim();
    idx++;
  }
  for (; idx < lines.length; idx++) {
    const ln = lines[idx].trim();
    if (ln) addrLines.push(ln);
  }
  return { account, name, addrLines };
}

function buildNaturalPerson(name: string, account: string, addrLines: string[]): NaturalPerson {
  const np: NaturalPerson = {};
  if (name) {
    const parts = name.split(/\s+/);
    np.name = {
      nameIdentifier: [
        {
          primaryIdentifier: parts[parts.length - 1],
          secondaryIdentifier: parts.slice(0, -1).join(" "),
          nameIdentifierType: "LEGL",
        },
      ],
    };
  }
  if (account) {
    np.nationalIdentification = {
      nationalIdentifier: account,
      nationalIdentifierType: isIban(account) ? "IBAN" : "MISC",
    };
  }
  if (addrLines.length) {
    const addr: Address = {};
    if (addrLines[0]) addr.streetName = addrLines[0];
    if (addrLines[1]) addr.townName = addrLines[1];
    if (addrLines[2]) addr.country = addrLines[2].length === 2 ? addrLines[2] : addrLines[2].slice(0, 2);
    np.geographicAddresses = [addr];
  }
  return np;
}

/**
 * Parse a SWIFT MT message and reconstruct an OpenKYCAML payload.
 *
 * Supports MT 103, MT 202, MT 202 COV, MT 910, MT 940.
 * Best-effort: fields present in the MT are mapped; absent fields are omitted.
 * :77B: is parsed and merged into the ivms101 originator/beneficiary blocks.
 *
 * @param mtText  Raw SWIFT FIN message (with or without block headers).
 * @returns       OpenKYCAML payload reconstructed from the MT.
 */
export function mtToOpenkycaml(mtText: string): OpenKYCAMLPayload {
  const fields = splitMtFields(mtText);

  const f20 = getField(fields, "20");
  const f21 = getField(fields, "21");
  const f23b = getField(fields, "23B");
  const f32a = getField(fields, "32A");
  const f32b = getField(fields, "32B");
  const f50 = getField(fields, "50K", "50A", "50");
  const f52a = getField(fields, "52A", "52D");
  const f56a = getField(fields, "56A", "56D");
  const f57a = getField(fields, "57A", "57D");
  const f58a = getField(fields, "58A", "58D");
  const f59 = getField(fields, "59", "59A");
  const f70 = getField(fields, "70");
  const f71a = getField(fields, "71A");
  const f72 = getField(fields, "72");
  const f77b = getField(fields, "77B");
  const f25 = getField(fields, "25");
  const f28c = getField(fields, "28C");
  const f60f = getField(fields, "60F");
  const f61 = getField(fields, "61");
  const f62f = getField(fields, "62F");

  // Detect message type
  const is940 = !!(f28c && f62f);
  const is202 = !!(f58a || fields.has("58D"));
  const is202cov = is202 && !!(f50 && f59 && f23b);
  const is910 = !!(f32a && f25 && !f59 && !f23b && !f28c);
  const is103 = !!(f23b && f59);

  // Amount
  let valueDate = "";
  let ccy = "XXX";
  let amountStr = "0.00";

  if (f32a) {
    const p = extract32a(f32a);
    valueDate = p.valueDate;
    ccy = p.ccy;
    amountStr = p.amount;
  } else if (f32b) {
    const p = extract32b(f32b);
    ccy = p.ccy;
    amountStr = p.amount;
  }

  // MT 940: fall back to :61: for amount if :32A: not present
  if (is940 && f61 && (amountStr === "0.00" || !amountStr)) {
    const m940 = /^(\d{6})(\d{4})?([CD])([A-Z]{3})([\d,]+)/.exec(f61);
    if (m940) {
      valueDate = ymdToIso(m940[1]);
      ccy = m940[4];
      amountStr = parseAmount(m940[5]);
    }
  }

  // Originator party
  let origPerson: PersonWrapper | null = null;
  let origAccounts: string[] = [];
  if (f50) {
    const { account, name, addrLines } = parsePartyLines(f50);
    origPerson = { naturalPerson: buildNaturalPerson(name, isIban(account) ? "" : account, addrLines) };
    if (account) origAccounts = [account];
  }

  // Beneficiary party
  let benePerson: PersonWrapper | null = null;
  let beneAccounts: string[] = [];
  if (f59) {
    const { account, name, addrLines } = parsePartyLines(f59);
    benePerson = { naturalPerson: buildNaturalPerson(name, isIban(account) ? "" : account, addrLines) };
    if (account) beneAccounts = [account];
  }

  // VASP agents
  let origVasp: VASP | null = null;
  let beneVasp: VASP | null = null;
  if (f52a) origVasp = { name: f52a.slice(0, MAX_NAME) };
  if (f57a || f58a) beneVasp = { name: (f57a || f58a).slice(0, MAX_NAME) };

  // :77B: merge
  const travelRule = f77b ? parse77b(f77b) : {};
  if (travelRule.originator77b) {
    const { naturalPerson: np77b, _account: acct77b } = travelRule.originator77b;
    if (!origPerson) {
      origPerson = { naturalPerson: np77b };
    } else if (!origPerson.naturalPerson?.name && np77b.name) {
      origPerson.naturalPerson = { ...(origPerson.naturalPerson ?? {}), name: np77b.name };
    }
    if (acct77b && origAccounts.length === 0) origAccounts = [acct77b];
  }
  if (travelRule.beneficiary77b) {
    const { naturalPerson: np77b, _account: acct77b } = travelRule.beneficiary77b;
    if (!benePerson) benePerson = { naturalPerson: np77b };
    if (acct77b && beneAccounts.length === 0) beneAccounts = [acct77b];
  }

  // Assemble OpenKYCAML payload
  const msgId = f20 || randomUUID();
  const msgDt = valueDate ? `${valueDate}T00:00:00Z` : nowIso();

  const result: OpenKYCAMLPayload = {
    $schema: SCHEMA_URL,
    version: SCHEMA_VERSION,
    messageId: msgId,
    messageDateTime: msgDt,
  };

  const ivms: OpenKYCAMLPayload["ivms101"] = {};

  if (origPerson || origAccounts.length) {
    ivms.originator = {
      ...(origPerson && { originatorPersons: [origPerson] }),
      ...(origAccounts.length && { accountNumber: origAccounts }),
    };
  }
  if (benePerson || beneAccounts.length) {
    ivms.beneficiary = {
      ...(benePerson && { beneficiaryPersons: [benePerson] }),
      ...(beneAccounts.length && { accountNumber: beneAccounts }),
    };
  }
  if (origVasp) ivms.originatingVASP = origVasp;
  if (beneVasp) ivms.beneficiaryVASP = beneVasp;
  if (amountStr && amountStr !== "0.00") {
    ivms.transferredAmount = { amount: amountStr, assetType: ccy };
  }
  if (Object.keys(ivms).length) result.ivms101 = ivms;

  // Metadata
  const meta: Record<string, unknown> = {};
  if (f70) meta.remittanceInfo = f70;
  if (f71a) meta.chargeBearer = f71a;
  if (f21 && f21 !== "NONREF") meta.relatedReference = f21;
  if (f72) meta.senderToReceiver = f72;
  if (f77b) meta.field77B = f77b;
  if (travelRule.uetr) meta.uetr = travelRule.uetr;
  if (f25) meta.accountId = f25;

  // Message type tag
  if (is940) meta.mtMessageType = "MT940";
  else if (is910) meta.mtMessageType = "MT910";
  else if (is202cov) meta.mtMessageType = "MT202COV";
  else if (is202) meta.mtMessageType = "MT202";
  else if (is103) meta.mtMessageType = "MT103";
  else meta.mtMessageType = "UNKNOWN";

  if (Object.keys(meta).length) result._swiftMtMetadata = meta;

  return result;
}
