/**
 * OpenKYCAML × ISO 20022 Converter (TypeScript / ESM)
 * =====================================================
 * Bidirectional converter between OpenKYCAML v1.3.0 payloads and ISO 20022
 * XML messages (pacs.008, pain.001).
 *
 * Exports
 * -------
 * openkycamlToPacs008(payload, config?)  → Promise<string>
 * openkycamlToPain001(payload, config?)  → Promise<string>
 * iso20022ToOpenkycaml(xmlString)        → OpenKYCAMLPayload
 *
 * Dependencies
 * ------------
 * fast-xml-parser  ^4  — XML serialisation / deserialisation
 * ajv              ^8  — JSON Schema validation (optional)
 *
 * Usage
 * -----
 *   import { openkycamlToPacs008 } from "./converter.js";
 *   const xml = await openkycamlToPacs008(payload);
 */

import { XMLBuilder, XMLParser } from "fast-xml-parser";
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
  registrationAuthority?: string;
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
  dateAndPlaceOfBirth?: {
    dateOfBirth?: string;
    placeOfBirth?: string;
    countryOfBirth?: string;
  };
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
}

export interface KYCProfile {
  customerRiskRating?: {
    overallRiskRating?: "LOW" | "MEDIUM" | "HIGH" | "VERY_HIGH" | "UNRATED";
    riskScore?: number;
    ratingDate?: string;
  };
  dueDiligenceType?: "SDD" | "CDD" | "EDD";
  customerClassification?: string;
  kycCompletionDate?: string;
  onboardingChannel?: string;
  sanctionsScreening?: Record<string, unknown>;
  pepStatus?: Record<string, unknown>;
  adverseMedia?: Record<string, unknown>;
  consentRecord?: Record<string, unknown>;
  thirdPartyCDDReliance?: Record<string, unknown>;
  beneficialOwnership?: unknown[];
  auditMetadata?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface OpenKYCAMLPayload {
  $schema?: string;
  version?: string;
  messageId?: string;
  messageDateTime?: string;
  ivms101?: {
    originator?: {
      originatorPersons?: PersonWrapper[];
      accountNumber?: string[];
    };
    beneficiary?: {
      beneficiaryPersons?: PersonWrapper[];
      accountNumber?: string[];
    };
    originatingVASP?: VASP;
    beneficiaryVASP?: VASP;
    transferredAmount?: {
      amount?: string;
      assetType?: string;
    };
    payloadMetadata?: Record<string, unknown>;
  };
  kycProfile?: KYCProfile;
  verifiableCredential?: Record<string, unknown>;
  gdprSensitivityMetadata?: Record<string, unknown>;
}

export interface MessageConfig {
  settlementMethod?: string;
  chargeBearer?: string;
  interbankSettlementDate?: string;
  serviceLevel?: string;
  paymentMethod?: string;
  requestedExecutionDate?: string;
  remittanceInfo?: string;
}

export interface KYCAMLEnvelope {
  envelopeVersion: "1.0.0";
  messageRef: string;
  openKycAmlVersion?: string;
  kycProfile?: KYCProfile;
  screeningResults?: {
    sanctionsScreening?: {
      result: string;
      screeningDate: string;
      listsScreened: string[];
      hitDetails: string | null;
    };
    pepScreening?: {
      isPEP: boolean;
      pepCategory: string | null;
      pepRole: string | null;
      screeningDate: string;
    };
    adverseMediaScreening?: {
      result: string;
      screeningDate: string;
      hitSummary: string | null;
    };
  };
  consentRecord?: Record<string, unknown>;
  vcProofs?: Array<{
    issuerDid: string;
    subjectDid: string;
    verifierDid?: string;
    credentialType?: string[];
    presentationMethod?: string;
    presentationDate?: string;
    proofType?: string;
    verificationMethod?: string;
    proofValue?: string | null;
  }>;
  gdprSensitivityMetadata?: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PACS008_NS = "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10";
const PAIN001_NS = "urn:iso:std:iso:20022:tech:xsd:pain.001.001.11";
const SPLMTRY_PLACE_AND_NAME = "OpenKYCAML/KYCAMLEnvelope/1.0";
const ENVELOPE_VERSION = "1.0.0" as const;

/** ISO 4217 fiat currencies (non-exhaustive subset for crypto detection). */
const ISO4217_CODES = new Set(
  "AED AFN ALL AMD ANG AOA ARS AUD AWG AZN BAM BBD BDT BGN BHD BMD BND "
  .concat("BOB BRL BSD BTN BWP BYN BZD CAD CDF CHF CLP CNY COP CRC CUP CVE ")
  .concat("CZK DJF DKK DOP DZD EGP ETB EUR FJD GBP GEL GHS GIP GMD GNF ")
  .concat("GTQ GYD HKD HNL HTG HUF IDR ILS INR IQD IRR ISK JMD JOD JPY KES ")
  .concat("KGS KHR KMF KRW KWD KYD KZT LAK LBP LKR LRD LSL LYD MAD MDL ")
  .concat("MGA MKD MMK MNT MOP MRU MUR MVR MWK MXN MYR MZN NAD NGN NIO NOK ")
  .concat("NPR NZD OMR PAB PEN PGK PHP PKR PLN PYG QAR RON RSD RUB RWF SAR ")
  .concat("SBD SCR SDG SEK SGD SHP SLE SOS SRD STN SVC SYP SZL THB TJS TMT ")
  .concat("TND TOP TRY TTD TWD TZS UAH UGX USD UYU UZS VES VND VUV WST XAF ")
  .concat("XCD XOF XPF YER ZAR ZMW ZWL XXX")
  .split(" ")
);

const IBAN_RE = /^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$/;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function isIso4217(code: string): boolean {
  return ISO4217_CODES.has(code.toUpperCase());
}

function isIban(value: string): boolean {
  return IBAN_RE.test(value.toUpperCase());
}

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

function getLei(person: PersonWrapper): string | undefined {
  const p = person.naturalPerson ?? person.legalPerson;
  if (p?.nationalIdentification?.nationalIdentifierType === "LEIX") {
    return p.nationalIdentification.nationalIdentifier;
  }
  return undefined;
}

function buildAddress(addr: Address): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  if (addr.streetName) out.StrtNm = addr.streetName;
  if (addr.buildingNumber) out.BldgNb = addr.buildingNumber;
  if (addr.postCode) out.PstCd = addr.postCode;
  if (addr.townName) out.TwnNm = addr.townName;
  if (addr.addressLine?.length) out.AdrLine = addr.addressLine;
  if (addr.country) out.Ctry = addr.country;
  return out;
}

function buildPartyId(person: PersonWrapper): Record<string, unknown> | undefined {
  const nat = person.naturalPerson;
  const leg = person.legalPerson;

  if (leg) {
    const ni = leg.nationalIdentification;
    if (!ni) return undefined;
    if (ni.nationalIdentifierType === "LEIX") {
      return { OrgId: { LEI: ni.nationalIdentifier } };
    }
    return { OrgId: { Othr: { Id: ni.nationalIdentifier, SchmeNm: { Prtry: ni.nationalIdentifierType } } } };
  }

  if (nat) {
    const ni = nat.nationalIdentification;
    const dob = nat.dateAndPlaceOfBirth;
    const prvtId: Record<string, unknown> = {};
    if (dob?.dateOfBirth) {
      prvtId.DtAndPlcOfBirth = {
        BirthDt: dob.dateOfBirth,
        CityOfBirth: dob.placeOfBirth ?? "UNKNOWN",
        CtryOfBirth: dob.countryOfBirth ?? "XX",
      };
    }
    if (ni?.nationalIdentifier && ni.nationalIdentifierType) {
      prvtId.Othr = {
        Id: ni.nationalIdentifier,
        SchmeNm: { Prtry: ni.nationalIdentifierType },
      };
    }
    return Object.keys(prvtId).length ? { PrvtId: prvtId } : undefined;
  }
  return undefined;
}

function buildPartyBlock(person: PersonWrapper): Record<string, unknown> {
  const block: Record<string, unknown> = {};
  const nm = getNameString(person);
  if (nm) block.Nm = nm.slice(0, 140);
  const id = buildPartyId(person);
  if (id) block.Id = id;
  const p = person.naturalPerson ?? person.legalPerson;
  const addrs = p?.geographicAddresses ?? [];
  if (addrs.length) block.PstlAdr = buildAddress(addrs[0]);
  const country = (p as NaturalPerson)?.countryOfResidence ?? (p as LegalPerson)?.countryOfRegistration;
  if (country) block.CtryOfRes = country;
  return block;
}

function buildAccountBlock(accountNumbers: string[], assetType: string): Record<string, unknown> {
  const acctNo = accountNumbers[0];
  if (isIban(acctNo)) {
    return { Id: { IBAN: acctNo.toUpperCase() } };
  }
  return {
    Id: {
      Othr: {
        Id: acctNo,
        SchmeNm: { Prtry: !isIso4217(assetType) ? assetType : "ACCT" },
      },
    },
  };
}

function buildKycAmlEnvelope(payload: OpenKYCAMLPayload, messageRef: string): KYCAMLEnvelope {
  const envelope: KYCAMLEnvelope = {
    envelopeVersion: ENVELOPE_VERSION,
    messageRef: messageRef.slice(0, 35),
    openKycAmlVersion: payload.version ?? "1.3.0",
  };

  if (payload.kycProfile) {
    envelope.kycProfile = payload.kycProfile;
  }

  // Build screeningResults
  const kyc = payload.kycProfile;
  if (kyc) {
    const screening: KYCAMLEnvelope["screeningResults"] = {};
    const sanctions = kyc.sanctionsScreening as Record<string, unknown> | undefined;
    if (sanctions) {
      screening.sanctionsScreening = {
        result: (sanctions.result ?? sanctions.screeningResult ?? "NOT_SCREENED") as string,
        screeningDate: (sanctions.screeningDate ?? sanctions.lastScreenedDate ?? "") as string,
        listsScreened: (sanctions.listsScreened as string[]) ?? [],
        hitDetails: (sanctions.hitDetails as string | null) ?? null,
      };
    }
    const pep = kyc.pepStatus as Record<string, unknown> | undefined;
    if (pep) {
      screening.pepScreening = {
        isPEP: (pep.isPEP as boolean) ?? false,
        pepCategory: (pep.pepCategory as string | null) ?? null,
        pepRole: (pep.pepRole as string | null) ?? null,
        screeningDate: (pep.pepScreeningDate as string) ?? "",
      };
    }
    const adverse = kyc.adverseMedia as Record<string, unknown> | undefined;
    if (adverse) {
      screening.adverseMediaScreening = {
        result: (adverse.result ?? "NOT_SCREENED") as string,
        screeningDate: (adverse.screeningDate ?? "") as string,
        hitSummary: (adverse.hitSummary as string | null) ?? null,
      };
    }
    if (Object.keys(screening).length) {
      envelope.screeningResults = screening;
    }
    if (kyc.consentRecord) {
      envelope.consentRecord = kyc.consentRecord as Record<string, unknown>;
    }
  }

  // VC proofs
  const vc = payload.verifiableCredential as Record<string, unknown> | undefined;
  if (vc) {
    const evidenceList = (vc.evidence as Record<string, unknown>[]) ?? [];
    const proof = (vc.proof as Record<string, unknown>) ?? {};
    const subjectDid = ((vc.credentialSubject as Record<string, unknown>)?.id as string) ?? "";
    envelope.vcProofs = evidenceList.map((ev) => ({
      issuerDid: (ev.credentialIssuer as string) ?? "",
      subjectDid,
      verifierDid: ev.verifier as string | undefined,
      credentialType: ev.type as string[] | undefined,
      presentationMethod: ev.presentationMethod as string | undefined,
      presentationDate: ev.presentationDate as string | undefined,
      proofType: proof.type as string | undefined,
      verificationMethod: proof.verificationMethod as string | undefined,
      proofValue: (proof.proofValue ?? proof.jws) as string | null | undefined,
    }));
  } else {
    envelope.vcProofs = [];
  }

  if (payload.gdprSensitivityMetadata) {
    envelope.gdprSensitivityMetadata = payload.gdprSensitivityMetadata;
  }

  return envelope;
}

function nowIso(): string {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

function buildXml(root: Record<string, unknown>, ns: string): string {
  const builder = new XMLBuilder({
    attributeNamePrefix: "@_",
    ignoreAttributes: false,
    format: true,
    indentBy: "  ",
    suppressEmptyNode: true,
  });
  const doc = { "?xml": { "@_version": "1.0", "@_encoding": "UTF-8" }, Document: { "@_xmlns": ns, ...root } };
  return builder.build(doc) as string;
}

// ---------------------------------------------------------------------------
// openkycamlToPacs008
// ---------------------------------------------------------------------------

/**
 * Convert an OpenKYCAML payload to a pacs.008 FIToFICstmrCdtTrf XML string.
 *
 * @param payload    OpenKYCAML envelope containing an ivms101 block.
 * @param config     Optional overrides for settlement method, charge bearer, etc.
 * @returns          UTF-8 XML string.
 */
export async function openkycamlToPacs008(
  payload: OpenKYCAMLPayload,
  config: MessageConfig = {}
): Promise<string> {
  const ivms = payload.ivms101;
  if (!ivms) throw new Error("No 'ivms101' block found. Cannot produce pacs.008.");

  const msgId = (payload.messageId ?? randomUUID()).slice(0, 35);
  const msgDt = payload.messageDateTime ?? nowIso();
  const assetType = ivms.transferredAmount?.assetType ?? "XXX";
  const ccy = isIso4217(assetType) ? assetType : "XXX";
  const amount = ivms.transferredAmount?.amount ?? "0";
  const origVasp = ivms.originatingVASP ?? {};
  const beneVasp = ivms.beneficiaryVASP ?? {};
  const origPersons = ivms.originator?.originatorPersons ?? [];
  const benePersons = ivms.beneficiary?.beneficiaryPersons ?? [];
  const origAccounts = ivms.originator?.accountNumber ?? [];
  const beneAccounts = ivms.beneficiary?.accountNumber ?? [];

  const envelope = buildKycAmlEnvelope(payload, msgId);
  const envelopeJson = JSON.stringify(envelope, null, 2);

  const grpHdr: Record<string, unknown> = {
    MsgId: msgId,
    CreDtTm: msgDt,
    NbOfTxs: "1",
    SttlmInf: { SttlmMtd: config.settlementMethod ?? "CLRG" },
  };
  if (origVasp.lei || origVasp.name) {
    grpHdr.InstgAgt = {
      FinInstnId: {
        ...(origVasp.lei && { LEI: origVasp.lei }),
        ...(origVasp.name && { Nm: origVasp.name.slice(0, 140) }),
      },
    };
  }
  if (beneVasp.lei || beneVasp.name) {
    grpHdr.InstdAgt = {
      FinInstnId: {
        ...(beneVasp.lei && { LEI: beneVasp.lei }),
        ...(beneVasp.name && { Nm: beneVasp.name.slice(0, 140) }),
      },
    };
  }

  const txMeta = (ivms.payloadMetadata as Record<string, unknown>) ?? {};
  const cdtTrf: Record<string, unknown> = {
    PmtId: {
      EndToEndId: msgId,
      TxId: ((txMeta.transactionIdentifier as string) ?? msgId).slice(0, 35),
    },
    IntrBkSttlmAmt: { "@_Ccy": ccy, "#text": amount },
    IntrBkSttlmDt: config.interbankSettlementDate ?? msgDt.slice(0, 10),
    ChrgBr: config.chargeBearer ?? "SHAR",
  };

  if (origPersons.length) {
    cdtTrf.Dbtr = buildPartyBlock(origPersons[0]);
  }
  if (origAccounts.length) {
    cdtTrf.DbtrAcct = buildAccountBlock(origAccounts, assetType);
  }
  if (origVasp.lei) {
    cdtTrf.DbtrAgt = { FinInstnId: { LEI: origVasp.lei } };
  }
  if (benePersons.length) {
    cdtTrf.Cdtr = buildPartyBlock(benePersons[0]);
  }
  if (beneAccounts.length) {
    cdtTrf.CdtrAcct = buildAccountBlock(beneAccounts, assetType);
  }
  if (beneVasp.lei) {
    cdtTrf.CdtrAgt = { FinInstnId: { LEI: beneVasp.lei } };
  }

  cdtTrf.SplmtryData = {
    PlcAndNm: SPLMTRY_PLACE_AND_NAME,
    Envlp: envelopeJson,
  };

  return buildXml(
    { FIToFICstmrCdtTrf: { GrpHdr: grpHdr, CdtTrfTxInf: cdtTrf } },
    PACS008_NS
  );
}

// ---------------------------------------------------------------------------
// openkycamlToPain001
// ---------------------------------------------------------------------------

/**
 * Convert an OpenKYCAML payload to a pain.001 CstmrCdtTrfInitn XML string.
 *
 * @param payload    OpenKYCAML envelope containing an ivms101 block.
 * @param config     Optional overrides.
 * @returns          UTF-8 XML string.
 */
export async function openkycamlToPain001(
  payload: OpenKYCAMLPayload,
  config: MessageConfig = {}
): Promise<string> {
  const ivms = payload.ivms101;
  if (!ivms) throw new Error("No 'ivms101' block found. Cannot produce pain.001.");

  const msgId = (payload.messageId ?? randomUUID()).slice(0, 35);
  const msgDt = payload.messageDateTime ?? nowIso();
  const assetType = ivms.transferredAmount?.assetType ?? "XXX";
  const ccy = isIso4217(assetType) ? assetType : "XXX";
  const amount = ivms.transferredAmount?.amount ?? "0";
  const origVasp = ivms.originatingVASP ?? {};
  const beneVasp = ivms.beneficiaryVASP ?? {};
  const origPersons = ivms.originator?.originatorPersons ?? [];
  const benePersons = ivms.beneficiary?.beneficiaryPersons ?? [];
  const origAccounts = ivms.originator?.accountNumber ?? [];
  const beneAccounts = ivms.beneficiary?.accountNumber ?? [];

  const envelope = buildKycAmlEnvelope(payload, msgId);
  const envelopeJson = JSON.stringify(envelope, null, 2);

  // InitgPty
  const initgPty: Record<string, unknown> = {};
  if (origPersons.length) {
    const nm = getNameString(origPersons[0]);
    if (nm) initgPty.Nm = nm.slice(0, 140);
    const lei = getLei(origPersons[0]);
    if (lei) initgPty.Id = { OrgId: { LEI: lei } };
  } else if (origVasp.name) {
    initgPty.Nm = origVasp.name.slice(0, 140);
  }

  const grpHdr: Record<string, unknown> = {
    MsgId: msgId,
    CreDtTm: msgDt,
    NbOfTxs: "1",
    CtrlSum: amount,
    InitgPty: initgPty,
  };

  const pmtTpInf: Record<string, unknown> = {
    SvcLvl: { Cd: config.serviceLevel ?? "SEPA" },
  };

  const dbtr = origPersons.length ? buildPartyBlock(origPersons[0]) : {};
  const cdtr = benePersons.length ? buildPartyBlock(benePersons[0]) : {};

  const cdtTrf: Record<string, unknown> = {
    PmtId: { EndToEndId: msgId },
    Amt: { InstdAmt: { "@_Ccy": ccy, "#text": amount } },
  };
  if (beneVasp.lei) {
    cdtTrf.CdtrAgt = { FinInstnId: { LEI: beneVasp.lei } };
  }
  if (Object.keys(cdtr).length) cdtTrf.Cdtr = cdtr;
  if (beneAccounts.length) cdtTrf.CdtrAcct = buildAccountBlock(beneAccounts, assetType);
  if (config.remittanceInfo) {
    cdtTrf.RmtInf = { Ustrd: config.remittanceInfo.slice(0, 140) };
  }
  cdtTrf.SplmtryData = {
    PlcAndNm: SPLMTRY_PLACE_AND_NAME,
    Envlp: envelopeJson,
  };

  const dbtrAgt: Record<string, unknown> = {
    FinInstnId: origVasp.lei ? { LEI: origVasp.lei } : { Othr: "NOTPROVIDED" },
  };

  const dbtrAcct = origAccounts.length ? buildAccountBlock(origAccounts, assetType) : undefined;

  const pmt: Record<string, unknown> = {
    PmtInfId: msgId,
    PmtMtd: config.paymentMethod ?? "TRF",
    NbOfTxs: "1",
    CtrlSum: amount,
    PmtTpInf: pmtTpInf,
    ReqdExctnDt: { Dt: config.requestedExecutionDate ?? msgDt.slice(0, 10) },
    Dbtr: Object.keys(dbtr).length ? dbtr : { Nm: "UNKNOWN" },
    ...(dbtrAcct && { DbtrAcct: dbtrAcct }),
    DbtrAgt: dbtrAgt,
    CdtTrfTxInf: cdtTrf,
  };

  return buildXml(
    { CstmrCdtTrfInitn: { GrpHdr: grpHdr, PmtInf: pmt } },
    PAIN001_NS
  );
}

// ---------------------------------------------------------------------------
// iso20022ToOpenkycaml
// ---------------------------------------------------------------------------

/**
 * Parse an ISO 20022 XML message and reconstruct an OpenKYCAML payload.
 *
 * @param xmlString  UTF-8 XML string of a pacs.008 or pain.001 message.
 * @returns          OpenKYCAML payload reconstructed from the XML.
 */
export function iso20022ToOpenkycaml(xmlString: string): OpenKYCAMLPayload {
  const parser = new XMLParser({
    attributeNamePrefix: "@_",
    ignoreAttributes: false,
    parseTagValue: false,
    removeNSPrefix: true,
  });
  const parsed = parser.parse(xmlString) as Record<string, unknown>;

  const doc = (parsed.Document ?? parsed) as Record<string, unknown>;
  const fiToFi = doc.FIToFICstmrCdtTrf as Record<string, unknown> | undefined;
  const cstmr = doc.CstmrCdtTrfInitn as Record<string, unknown> | undefined;
  const root = fiToFi ?? cstmr ?? doc;

  const grpHdr = (root.GrpHdr ?? {}) as Record<string, unknown>;
  const msgId = String(grpHdr.MsgId ?? "");
  const msgDt = String(grpHdr.CreDtTm ?? "");

  // Locate the credit transfer transaction info
  const pmt = (root.PmtInf ?? {}) as Record<string, unknown>;
  const tx = ((fiToFi?.CdtTrfTxInf ?? pmt.CdtTrfTxInf) ?? {}) as Record<string, unknown>;

  function getText(obj: unknown, ...keys: string[]): string | undefined {
    let cur: unknown = obj;
    for (const k of keys) {
      if (typeof cur !== "object" || cur === null) return undefined;
      cur = (cur as Record<string, unknown>)[k];
    }
    if (cur === null || cur === undefined) return undefined;
    return typeof cur === "object" ? String((cur as Record<string, unknown>)["#text"] ?? "") : String(cur);
  }

  // Extract KYCAMLEnvelope
  let envelope: KYCAMLEnvelope | null = null;
  const findSplmtry = (obj: unknown): void => {
    if (typeof obj !== "object" || obj === null) return;
    const o = obj as Record<string, unknown>;
    if ("PlcAndNm" in o && String(o.PlcAndNm) === SPLMTRY_PLACE_AND_NAME) {
      const envlp = o.Envlp;
      if (typeof envlp === "string") {
        try { envelope = JSON.parse(envlp) as KYCAMLEnvelope; } catch { /* ignore */ }
      }
      return;
    }
    for (const v of Object.values(o)) findSplmtry(v);
  };
  findSplmtry(doc);

  // Parse parties
  const dbtr = (tx.Dbtr ?? pmt.Dbtr ?? {}) as Record<string, unknown>;
  const cdtr = (tx.Cdtr ?? {}) as Record<string, unknown>;
  const dbtrAcct = (tx.DbtrAcct ?? pmt.DbtrAcct ?? {}) as Record<string, unknown>;
  const cdtrAcct = (tx.CdtrAcct ?? {}) as Record<string, unknown>;
  const instgAgt = ((root.GrpHdr as Record<string, unknown>)?.InstgAgt as Record<string, unknown>) ?? {};
  const instdAgt = ((root.GrpHdr as Record<string, unknown>)?.InstdAgt as Record<string, unknown>) ?? {};

  function parseParty(el: Record<string, unknown>): PersonWrapper | null {
    const nm = getText(el, "Nm");
    const lei = getText(el, "Id", "OrgId", "LEI");
    if (lei) {
      const lp: LegalPerson = { nationalIdentification: { nationalIdentifier: lei, nationalIdentifierType: "LEIX" } };
      if (nm) lp.name = { nameIdentifier: [{ legalPersonName: nm, legalPersonNameIdentifierType: "LEGL" }] };
      return { legalPerson: lp };
    }
    const np: NaturalPerson = { name: { nameIdentifier: [] } };
    if (nm) {
      const parts = nm.split(/\s+/);
      np.name!.nameIdentifier!.push({
        primaryIdentifier: parts[parts.length - 1],
        secondaryIdentifier: parts.slice(0, -1).join(" "),
        nameIdentifierType: "LEGL",
      });
    }
    const birthDt = getText(el, "Id", "PrvtId", "DtAndPlcOfBirth", "BirthDt");
    if (birthDt) {
      np.dateAndPlaceOfBirth = {
        dateOfBirth: birthDt,
        placeOfBirth: getText(el, "Id", "PrvtId", "DtAndPlcOfBirth", "CityOfBirth"),
        countryOfBirth: getText(el, "Id", "PrvtId", "DtAndPlcOfBirth", "CtryOfBirth"),
      };
    }
    const othId = getText(el, "Id", "PrvtId", "Othr", "Id");
    if (othId) {
      np.nationalIdentification = {
        nationalIdentifier: othId,
        nationalIdentifierType: getText(el, "Id", "PrvtId", "Othr", "SchmeNm", "Prtry") ?? "MISC",
      };
    }
    const country = getText(el, "CtryOfRes");
    if (country) np.countryOfResidence = country;
    const pstl = (el.PstlAdr ?? {}) as Record<string, unknown>;
    const addr: Address = {};
    if (getText(pstl, "StrtNm")) addr.streetName = getText(pstl, "StrtNm");
    if (getText(pstl, "BldgNb")) addr.buildingNumber = getText(pstl, "BldgNb");
    if (getText(pstl, "PstCd")) addr.postCode = getText(pstl, "PstCd");
    if (getText(pstl, "TwnNm")) addr.townName = getText(pstl, "TwnNm");
    if (getText(pstl, "Ctry")) addr.country = getText(pstl, "Ctry");
    if (Object.keys(addr).length) np.geographicAddresses = [addr];
    return { naturalPerson: np };
  }

  function parseAccount(el: Record<string, unknown>): string | undefined {
    return getText(el, "Id", "IBAN") ?? getText(el, "Id", "Othr", "Id");
  }

  const origPerson = Object.keys(dbtr).length ? parseParty(dbtr) : null;
  const benePerson = Object.keys(cdtr).length ? parseParty(cdtr) : null;
  const origAcct = parseAccount(dbtrAcct);
  const beneAcct = parseAccount(cdtrAcct);

  const origVaspLei = getText(instgAgt, "FinInstnId", "LEI");
  const origVaspNm = getText(instgAgt, "FinInstnId", "Nm");
  const beneVaspLei = getText(instdAgt, "FinInstnId", "LEI");
  const beneVaspNm = getText(instdAgt, "FinInstnId", "Nm");

  const amtEl = (tx.IntrBkSttlmAmt ?? (tx.Amt as Record<string, unknown>)?.InstdAmt) as Record<string, unknown> | undefined;
  const amtValue = amtEl ? (getText(amtEl, "#text") ?? String(amtEl)) : undefined;
  const amtCcy = amtEl?.["@_Ccy"] as string | undefined;

  const assetTypeRecovered = envelope?.kycProfile?.transferredAmount
    ? (envelope.kycProfile.transferredAmount as Record<string, unknown>).assetType as string
    : amtCcy ?? "XXX";

  // Assemble result
  const result: OpenKYCAMLPayload = {
    $schema: "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
    version: envelope?.openKycAmlVersion ?? "1.3.0",
    messageId: msgId || randomUUID(),
    messageDateTime: msgDt || nowIso(),
  };

  const ivms: OpenKYCAMLPayload["ivms101"] = {};
  if (origPerson || origAcct) {
    ivms.originator = {
      ...(origPerson && { originatorPersons: [origPerson] }),
      ...(origAcct && { accountNumber: [origAcct] }),
    };
  }
  if (benePerson || beneAcct) {
    ivms.beneficiary = {
      ...(benePerson && { beneficiaryPersons: [benePerson] }),
      ...(beneAcct && { accountNumber: [beneAcct] }),
    };
  }
  if (origVaspLei || origVaspNm) {
    ivms.originatingVASP = {
      ...(origVaspLei && { lei: origVaspLei }),
      ...(origVaspNm && { name: origVaspNm }),
    };
  }
  if (beneVaspLei || beneVaspNm) {
    ivms.beneficiaryVASP = {
      ...(beneVaspLei && { lei: beneVaspLei }),
      ...(beneVaspNm && { name: beneVaspNm }),
    };
  }
  if (amtValue) {
    ivms.transferredAmount = { amount: amtValue, assetType: assetTypeRecovered };
  }
  if (Object.keys(ivms).length) result.ivms101 = ivms;

  if (envelope?.kycProfile) result.kycProfile = envelope.kycProfile;
  if (envelope?.gdprSensitivityMetadata) result.gdprSensitivityMetadata = envelope.gdprSensitivityMetadata;

  const vcProofs = envelope?.vcProofs ?? [];
  if (vcProofs.length) {
    const p = vcProofs[0];
    result.verifiableCredential = {
      issuer: { id: p.issuerDid },
      credentialSubject: { id: p.subjectDid },
      evidence: [
        {
          type: p.credentialType,
          credentialIssuer: p.issuerDid,
          verifier: p.verifierDid,
          presentationMethod: p.presentationMethod,
          presentationDate: p.presentationDate,
        },
      ],
      proof: {
        type: p.proofType,
        verificationMethod: p.verificationMethod,
        proofValue: p.proofValue,
      },
    };
  }

  return result;
}
