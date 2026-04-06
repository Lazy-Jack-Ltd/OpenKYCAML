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
// Constants
// ---------------------------------------------------------------------------
const PACS008_NS = "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10";
const PAIN001_NS = "urn:iso:std:iso:20022:tech:xsd:pain.001.001.11";
const SPLMTRY_PLACE_AND_NAME = "OpenKYCAML/KYCAMLEnvelope/1.0";
const ENVELOPE_VERSION = "1.0.0";
/** ISO 4217 fiat currencies (non-exhaustive subset for crypto detection). */
const ISO4217_CODES = new Set("AED AFN ALL AMD ANG AOA ARS AUD AWG AZN BAM BBD BDT BGN BHD BMD BND "
    .concat("BOB BRL BSD BTN BWP BYN BZD CAD CDF CHF CLP CNY COP CRC CUP CVE ")
    .concat("CZK DJF DKK DOP DZD EGP ETB EUR FJD GBP GEL GHS GIP GMD GNF ")
    .concat("GTQ GYD HKD HNL HTG HUF IDR ILS INR IQD IRR ISK JMD JOD JPY KES ")
    .concat("KGS KHR KMF KRW KWD KYD KZT LAK LBP LKR LRD LSL LYD MAD MDL ")
    .concat("MGA MKD MMK MNT MOP MRU MUR MVR MWK MXN MYR MZN NAD NGN NIO NOK ")
    .concat("NPR NZD OMR PAB PEN PGK PHP PKR PLN PYG QAR RON RSD RUB RWF SAR ")
    .concat("SBD SCR SDG SEK SGD SHP SLE SOS SRD STN SVC SYP SZL THB TJS TMT ")
    .concat("TND TOP TRY TTD TWD TZS UAH UGX USD UYU UZS VES VND VUV WST XAF ")
    .concat("XCD XOF XPF YER ZAR ZMW ZWL XXX")
    .split(" "));
const IBAN_RE = /^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$/;
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function isIso4217(code) {
    return ISO4217_CODES.has(code.toUpperCase());
}
function isIban(value) {
    return IBAN_RE.test(value.toUpperCase());
}
function getNameString(person) {
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
function getLei(person) {
    const p = person.naturalPerson ?? person.legalPerson;
    if (p?.nationalIdentification?.nationalIdentifierType === "LEIX") {
        return p.nationalIdentification.nationalIdentifier;
    }
    return undefined;
}
function buildAddress(addr) {
    const out = {};
    if (addr.streetName)
        out.StrtNm = addr.streetName;
    if (addr.buildingNumber)
        out.BldgNb = addr.buildingNumber;
    if (addr.postCode)
        out.PstCd = addr.postCode;
    if (addr.townName)
        out.TwnNm = addr.townName;
    if (addr.addressLine?.length)
        out.AdrLine = addr.addressLine;
    if (addr.country)
        out.Ctry = addr.country;
    return out;
}
function buildPartyId(person) {
    const nat = person.naturalPerson;
    const leg = person.legalPerson;
    if (leg) {
        const ni = leg.nationalIdentification;
        if (!ni)
            return undefined;
        if (ni.nationalIdentifierType === "LEIX") {
            return { OrgId: { LEI: ni.nationalIdentifier } };
        }
        return { OrgId: { Othr: { Id: ni.nationalIdentifier, SchmeNm: { Prtry: ni.nationalIdentifierType } } } };
    }
    if (nat) {
        const ni = nat.nationalIdentification;
        const dob = nat.dateAndPlaceOfBirth;
        const prvtId = {};
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
function buildPartyBlock(person) {
    const block = {};
    const nm = getNameString(person);
    if (nm)
        block.Nm = nm.slice(0, 140);
    const id = buildPartyId(person);
    if (id)
        block.Id = id;
    const p = person.naturalPerson ?? person.legalPerson;
    const addrs = p?.geographicAddresses ?? [];
    if (addrs.length)
        block.PstlAdr = buildAddress(addrs[0]);
    const country = p?.countryOfResidence ?? p?.countryOfRegistration;
    if (country)
        block.CtryOfRes = country;
    return block;
}
function buildAccountBlock(accountNumbers, assetType) {
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
function buildKycAmlEnvelope(payload, messageRef) {
    const envelope = {
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
        const screening = {};
        const sanctions = kyc.sanctionsScreening;
        if (sanctions) {
            screening.sanctionsScreening = {
                result: (sanctions.result ?? sanctions.screeningResult ?? "NOT_SCREENED"),
                screeningDate: (sanctions.screeningDate ?? sanctions.lastScreenedDate ?? ""),
                listsScreened: sanctions.listsScreened ?? [],
                hitDetails: sanctions.hitDetails ?? null,
            };
        }
        const pep = kyc.pepStatus;
        if (pep) {
            screening.pepScreening = {
                isPEP: pep.isPEP ?? false,
                pepCategory: pep.pepCategory ?? null,
                pepRole: pep.pepRole ?? null,
                screeningDate: pep.pepScreeningDate ?? "",
            };
        }
        const adverse = kyc.adverseMedia;
        if (adverse) {
            screening.adverseMediaScreening = {
                result: (adverse.result ?? "NOT_SCREENED"),
                screeningDate: (adverse.screeningDate ?? ""),
                hitSummary: adverse.hitSummary ?? null,
            };
        }
        if (Object.keys(screening).length) {
            envelope.screeningResults = screening;
        }
        if (kyc.consentRecord) {
            envelope.consentRecord = kyc.consentRecord;
        }
    }
    // VC proofs
    const vc = payload.verifiableCredential;
    if (vc) {
        const evidenceList = vc.evidence ?? [];
        const proof = vc.proof ?? {};
        const subjectDid = vc.credentialSubject?.id ?? "";
        envelope.vcProofs = evidenceList.map((ev) => ({
            issuerDid: ev.credentialIssuer ?? "",
            subjectDid,
            verifierDid: ev.verifier,
            credentialType: ev.type,
            presentationMethod: ev.presentationMethod,
            presentationDate: ev.presentationDate,
            proofType: proof.type,
            verificationMethod: proof.verificationMethod,
            proofValue: (proof.proofValue ?? proof.jws),
        }));
    }
    else {
        envelope.vcProofs = [];
    }
    if (payload.gdprSensitivityMetadata) {
        envelope.gdprSensitivityMetadata = payload.gdprSensitivityMetadata;
    }
    return envelope;
}
function nowIso() {
    return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}
function buildXml(root, ns) {
    const builder = new XMLBuilder({
        attributeNamePrefix: "@_",
        ignoreAttributes: false,
        format: true,
        indentBy: "  ",
        suppressEmptyNode: true,
    });
    const doc = { "?xml": { "@_version": "1.0", "@_encoding": "UTF-8" }, Document: { "@_xmlns": ns, ...root } };
    return builder.build(doc);
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
export async function openkycamlToPacs008(payload, config = {}) {
    const ivms = payload.ivms101;
    if (!ivms)
        throw new Error("No 'ivms101' block found. Cannot produce pacs.008.");
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
    const grpHdr = {
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
    const txMeta = ivms.payloadMetadata ?? {};
    const cdtTrf = {
        PmtId: {
            EndToEndId: msgId,
            TxId: (txMeta.transactionIdentifier ?? msgId).slice(0, 35),
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
    return buildXml({ FIToFICstmrCdtTrf: { GrpHdr: grpHdr, CdtTrfTxInf: cdtTrf } }, PACS008_NS);
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
export async function openkycamlToPain001(payload, config = {}) {
    const ivms = payload.ivms101;
    if (!ivms)
        throw new Error("No 'ivms101' block found. Cannot produce pain.001.");
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
    const initgPty = {};
    if (origPersons.length) {
        const nm = getNameString(origPersons[0]);
        if (nm)
            initgPty.Nm = nm.slice(0, 140);
        const lei = getLei(origPersons[0]);
        if (lei)
            initgPty.Id = { OrgId: { LEI: lei } };
    }
    else if (origVasp.name) {
        initgPty.Nm = origVasp.name.slice(0, 140);
    }
    const grpHdr = {
        MsgId: msgId,
        CreDtTm: msgDt,
        NbOfTxs: "1",
        CtrlSum: amount,
        InitgPty: initgPty,
    };
    const pmtTpInf = {
        SvcLvl: { Cd: config.serviceLevel ?? "SEPA" },
    };
    const dbtr = origPersons.length ? buildPartyBlock(origPersons[0]) : {};
    const cdtr = benePersons.length ? buildPartyBlock(benePersons[0]) : {};
    const cdtTrf = {
        PmtId: { EndToEndId: msgId },
        Amt: { InstdAmt: { "@_Ccy": ccy, "#text": amount } },
    };
    if (beneVasp.lei) {
        cdtTrf.CdtrAgt = { FinInstnId: { LEI: beneVasp.lei } };
    }
    if (Object.keys(cdtr).length)
        cdtTrf.Cdtr = cdtr;
    if (beneAccounts.length)
        cdtTrf.CdtrAcct = buildAccountBlock(beneAccounts, assetType);
    if (config.remittanceInfo) {
        cdtTrf.RmtInf = { Ustrd: config.remittanceInfo.slice(0, 140) };
    }
    cdtTrf.SplmtryData = {
        PlcAndNm: SPLMTRY_PLACE_AND_NAME,
        Envlp: envelopeJson,
    };
    const dbtrAgt = {
        FinInstnId: origVasp.lei ? { LEI: origVasp.lei } : { Othr: "NOTPROVIDED" },
    };
    const dbtrAcct = origAccounts.length ? buildAccountBlock(origAccounts, assetType) : undefined;
    const pmt = {
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
    return buildXml({ CstmrCdtTrfInitn: { GrpHdr: grpHdr, PmtInf: pmt } }, PAIN001_NS);
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
export function iso20022ToOpenkycaml(xmlString) {
    const parser = new XMLParser({
        attributeNamePrefix: "@_",
        ignoreAttributes: false,
        parseTagValue: false,
        removeNSPrefix: true,
    });
    const parsed = parser.parse(xmlString);
    const doc = (parsed.Document ?? parsed);
    const fiToFi = doc.FIToFICstmrCdtTrf;
    const cstmr = doc.CstmrCdtTrfInitn;
    const root = fiToFi ?? cstmr ?? doc;
    const grpHdr = (root.GrpHdr ?? {});
    const msgId = String(grpHdr.MsgId ?? "");
    const msgDt = String(grpHdr.CreDtTm ?? "");
    // Locate the credit transfer transaction info
    const pmt = (root.PmtInf ?? {});
    const tx = ((fiToFi?.CdtTrfTxInf ?? pmt.CdtTrfTxInf) ?? {});
    function getText(obj, ...keys) {
        let cur = obj;
        for (const k of keys) {
            if (typeof cur !== "object" || cur === null)
                return undefined;
            cur = cur[k];
        }
        if (cur === null || cur === undefined)
            return undefined;
        return typeof cur === "object" ? String(cur["#text"] ?? "") : String(cur);
    }
    // Extract KYCAMLEnvelope
    let envelope = null;
    const findSplmtry = (obj) => {
        if (typeof obj !== "object" || obj === null)
            return;
        const o = obj;
        if ("PlcAndNm" in o && String(o.PlcAndNm) === SPLMTRY_PLACE_AND_NAME) {
            const envlp = o.Envlp;
            if (typeof envlp === "string") {
                try {
                    envelope = JSON.parse(envlp);
                }
                catch { /* ignore */ }
            }
            return;
        }
        for (const v of Object.values(o))
            findSplmtry(v);
    };
    findSplmtry(doc);
    // Parse parties
    const dbtr = (tx.Dbtr ?? pmt.Dbtr ?? {});
    const cdtr = (tx.Cdtr ?? {});
    const dbtrAcct = (tx.DbtrAcct ?? pmt.DbtrAcct ?? {});
    const cdtrAcct = (tx.CdtrAcct ?? {});
    const instgAgt = root.GrpHdr?.InstgAgt ?? {};
    const instdAgt = root.GrpHdr?.InstdAgt ?? {};
    function parseParty(el) {
        const nm = getText(el, "Nm");
        const lei = getText(el, "Id", "OrgId", "LEI");
        if (lei) {
            const lp = { nationalIdentification: { nationalIdentifier: lei, nationalIdentifierType: "LEIX" } };
            if (nm)
                lp.name = { nameIdentifier: [{ legalPersonName: nm, legalPersonNameIdentifierType: "LEGL" }] };
            return { legalPerson: lp };
        }
        const np = { name: { nameIdentifier: [] } };
        if (nm) {
            const parts = nm.split(/\s+/);
            np.name.nameIdentifier.push({
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
        if (country)
            np.countryOfResidence = country;
        const pstl = (el.PstlAdr ?? {});
        const addr = {};
        if (getText(pstl, "StrtNm"))
            addr.streetName = getText(pstl, "StrtNm");
        if (getText(pstl, "BldgNb"))
            addr.buildingNumber = getText(pstl, "BldgNb");
        if (getText(pstl, "PstCd"))
            addr.postCode = getText(pstl, "PstCd");
        if (getText(pstl, "TwnNm"))
            addr.townName = getText(pstl, "TwnNm");
        if (getText(pstl, "Ctry"))
            addr.country = getText(pstl, "Ctry");
        if (Object.keys(addr).length)
            np.geographicAddresses = [addr];
        return { naturalPerson: np };
    }
    function parseAccount(el) {
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
    const amtEl = (tx.IntrBkSttlmAmt ?? tx.Amt?.InstdAmt);
    const amtValue = amtEl ? (getText(amtEl, "#text") ?? String(amtEl)) : undefined;
    const amtCcy = amtEl?.["@_Ccy"];
    const assetTypeRecovered = envelope?.kycProfile?.transferredAmount
        ? envelope.kycProfile.transferredAmount.assetType
        : amtCcy ?? "XXX";
    // Assemble result
    const result = {
        $schema: "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
        version: envelope?.openKycAmlVersion ?? "1.3.0",
        messageId: msgId || randomUUID(),
        messageDateTime: msgDt || nowIso(),
    };
    const ivms = {};
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
    if (Object.keys(ivms).length)
        result.ivms101 = ivms;
    if (envelope?.kycProfile)
        result.kycProfile = envelope.kycProfile;
    if (envelope?.gdprSensitivityMetadata)
        result.gdprSensitivityMetadata = envelope.gdprSensitivityMetadata;
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
