#!/usr/bin/env node
/**
 * OpenKYCAML Schema Validator (JavaScript / Node.js)
 * ====================================================
 * Validates JSON payloads against the OpenKYCAML v1.19.0 schema.
 *
 * Usage (CLI):
 *   node validator.js <path-to-payload.json>
 *   cat payload.json | node validator.js --stdin
 *
 * Programmatic usage:
 *   const { OpenKYCAMLValidator } = require('./validator');
 *   const v = new OpenKYCAMLValidator();
 *   const result = v.validate(payloadObject);
 *   console.log(result.isValid, result.errors);
 *
 * Requirements:
 *   npm install  (installs Ajv and supporting packages)
 */

'use strict';

const fs = require('fs');
const path = require('path');
const Ajv = require('ajv/dist/2020');
const addFormats = require('ajv-formats');

// Resolve schema relative to this file.
const SCHEMA_PATH = path.resolve(__dirname, '../../schema/kyc-aml-hybrid-extended.json');

// Canonical pattern for OpenKYCAML Document ID URNs.
// Format: urn:openkycaml:doc:{country}:{doc-type-code}:{subject-ref}:{YYYY-MM}
const DOCUMENT_ID_PATTERN = /^urn:openkycaml:doc:[a-z]{2}:[a-z0-9-]+:[a-z0-9-]+:[0-9]{4}-[0-9]{2}$/;

/**
 * @typedef {Object} FieldError
 * @property {string} instancePath - JSON pointer to the failing field.
 * @property {string} message      - Human-readable error description.
 * @property {string} schemaPath   - JSON pointer into the schema.
 */

/**
 * @typedef {Object} ValidationResult
 * @property {boolean}      isValid         - True if the payload is schema-valid.
 * @property {FieldError[]} errors          - Array of field-level errors (empty if valid).
 * @property {string[]}     warnings        - Advisory warnings (not schema errors).
 * @property {string|null}  payloadVersion  - The `version` field from the payload.
 */

class OpenKYCAMLValidator {
  /**
   * @param {string} [schemaPath] - Path to the JSON Schema file. Defaults to bundled schema.
   */
  constructor(schemaPath) {
    const resolvedPath = schemaPath || SCHEMA_PATH;

    if (!fs.existsSync(resolvedPath)) {
      throw new Error(
        `OpenKYCAML schema not found at: ${resolvedPath}\n` +
        'Ensure you are running from within the openKYCAML repository.'
      );
    }

    const schemaJson = JSON.parse(fs.readFileSync(resolvedPath, 'utf-8'));

    const ajv = new Ajv({ allErrors: true, strict: false });
    addFormats(ajv);

    this._validate = ajv.compile(schemaJson);
  }

  /**
   * Validate a parsed JSON payload.
   *
   * @param {Object} payload - The decoded JSON payload.
   * @returns {ValidationResult}
   */
  validate(payload) {
    const isValid = this._validate(payload);
    const errors = isValid
      ? []
      : (this._validate.errors || []).map((err) => ({
          instancePath: err.instancePath || '(root)',
          message: err.message || 'Unknown error',
          schemaPath: err.schemaPath || '',
        }));

    const warnings = isValid ? this._businessWarnings(payload) : [];

    return {
      isValid,
      errors,
      warnings,
      payloadVersion: payload && payload.version ? payload.version : null,
    };
  }

  /**
   * Validate a JSON file on disk.
   *
   * @param {string} filePath - Absolute or relative path to a JSON file.
   * @returns {ValidationResult}
   */
  validateFile(filePath) {
    let payload;
    try {
      payload = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    } catch (err) {
      return {
        isValid: false,
        errors: [{ instancePath: '<file>', message: `Cannot parse JSON: ${err.message}`, schemaPath: '' }],
        warnings: [],
        payloadVersion: null,
      };
    }
    return this.validate(payload);
  }

  // ---------------------------------------------------------------------------
  // Private helpers
  // ---------------------------------------------------------------------------

  /**
   * @private
   * @param {Object} payload
   * @returns {string[]}
   */
  _businessWarnings(payload) {
    const warns = [];
    const ivms = payload.ivms101 || {};
    const kyc = payload.kycProfile || {};

    // Missing originating VASP.
    if (ivms.originator && !ivms.originatingVASP) {
      warns.push(
        'ivms101.originatingVASP is missing — required for FATF Rec 16 / TFR compliance.'
      );
    }

    // Legal entity without UBOs.
    const originatorPersons = (ivms.originator || {}).originatorPersons || [];
    for (const personWrapper of originatorPersons) {
      if (personWrapper.legalPerson && (!kyc.beneficialOwnership || kyc.beneficialOwnership.length === 0)) {
        warns.push(
          'kycProfile.beneficialOwnership is empty for a legal entity — ' +
          'required under AMLR Art. 26 and FATF Rec 24.'
        );
        break;
      }
    }

    // PEP without EDD.
    const isPEP = (kyc.pepStatus || {}).isPEP;
    const ddType = kyc.dueDiligenceType;
    if (isPEP && ddType && ddType !== 'EDD') {
      warns.push(
        `kycProfile.dueDiligenceType is '${ddType}' but customer is a PEP — ` +
        'EDD is mandatory under AMLR Art. 28 and FATF Rec 12.'
      );
    }

    // Stale sanctions screening.
    const screeningDateStr = (kyc.sanctionsScreening || {}).screeningDate;
    if (screeningDateStr) {
      const screeningDate = new Date(screeningDateStr);
      const ageMs = Date.now() - screeningDate.getTime();
      const ageDays = Math.floor(ageMs / (1000 * 60 * 60 * 24));
      if (ageDays > 30) {
        warns.push(
          `kycProfile.sanctionsScreening.screeningDate is ${ageDays} days old — ` +
          'consider re-screening (recommended: every 30 days for high-risk customers).'
        );
      }
    }

    // Tipping-off protection check.
    const gdpr = payload.gdprSensitivityMetadata || {};
    if (gdpr.classification === 'sar_restricted' || gdpr.classification === 'internal_suspicion') {
      if (gdpr.tippingOffProtected !== true) {
        warns.push(
          `gdprSensitivityMetadata.tippingOffProtected should be true when classification is '${gdpr.classification}' ` +
          '(AMLR Art. 73 / FATF Rec. 21).'
        );
      }
    }

    // Warn when documents in identityDocuments lack a canonical documentId or
    // carry a documentId that does not conform to the OpenKYCAML URN scheme.
    const identityDocs = payload.identityDocuments || {};
    for (const collectionKey of ['naturalPersonDocuments', 'legalEntityDocuments']) {
      const docs = identityDocs[collectionKey] || [];
      docs.forEach((doc, idx) => {
        const location = `identityDocuments.${collectionKey}[${idx}]`;
        if (!doc.documentId) {
          warns.push(
            `${location} is missing documentId — a canonical URN is recommended ` +
            'for cross-system deduplication (see docs/reference/document-id-convention.md).'
          );
        } else if (!DOCUMENT_ID_PATTERN.test(doc.documentId)) {
          warns.push(
            `${location}.documentId '${doc.documentId}' does not conform to the ` +
            "OpenKYCAML Document ID URN scheme " +
            "'urn:openkycaml:doc:{country}:{doc-type-code}:{subject-ref}:{YYYY-MM}'."
          );
        }
      });
    }

    // XRPL confidential transfer compliance warning.
    const blockchainIds = kyc.blockchainAccountIds || [];
    for (let idx = 0; idx < blockchainIds.length; idx++) {
      const ct = blockchainIds[idx].xrplConfidentialTransfer || {};
      if (ct.enabled && (!ct.authorisedViewingKeys || ct.authorisedViewingKeys.length === 0)) {
        warns.push(
          `kycProfile.blockchainAccountIds[${idx}].xrplConfidentialTransfer.enabled is true ` +
          'but authorisedViewingKeys is empty — AMLR Art. 21 / FATF R.16 require ' +
          'supervisory viewing key access for confidential transfers (XLS-96d).'
        );
      }
    }

    // Tax status ESR and Pillar 2 warnings (v1.9.0).
    const tax = payload.taxStatus || {};
    const esr = tax.economicSubstance || {};
    if (esr.status === 'nonCompliant') {
      const jur = esr.jurisdiction || 'unknown';
      warns.push(
        `taxStatus.economicSubstance.status is 'nonCompliant' for jurisdiction '${jur}' — ` +
        'ESR non-compliance is a direct AML red flag under AMLR Art. 26 and EBA ML/TF ' +
        'risk-factor guidelines. EDD is required; consider SAR filing.'
      );
    }

    const p2 = tax.pillarTwo || {};
    if (p2.inScopeMNE && (!p2.girFilingReference || !p2.girFilingReference.trim())) {
      warns.push(
        'taxStatus.pillarTwo.inScopeMNE is true but girFilingReference is absent — ' +
        'in-scope MNEs must file a GloBE Information Return (GIR). ' +
        'Request the GIR reference and perform enhanced due diligence.'
      );
    }

    // FATCA warnings (v1.9.1).
    const fatca = tax.fatcaStatus || null;
    if (fatca) {
      const GIIN_REGEX = /^[0-9A-Z]{6}\.[0-9A-Z]{5}\.[0-9A-Z]{2}\.[0-9A-Z]{3}$/;
      if (fatca.giin && !GIIN_REGEX.test(fatca.giin)) {
        warns.push(
          `taxStatus.fatcaStatus.giin '${fatca.giin}' does not match the IRS GIIN format ` +
          '(XXXXXX.XXXXX.XX.XXX). Please verify against the IRS FATCA FFI List.'
        );
      }
      if (fatca.chapter4Classification === 'nonParticipatingFFI') {
        warns.push(
          "taxStatus.fatcaStatus.chapter4Classification is 'nonParticipatingFFI' — " +
          'non-participating FFIs are subject to 30% FATCA withholding and represent ' +
          'elevated US tax-risk. EDD is recommended.'
        );
      }
      if (fatca.ffiListVerificationTimestamp) {
        const ts = new Date(fatca.ffiListVerificationTimestamp);
        const ageMs = Date.now() - ts.getTime();
        if (!isNaN(ageMs) && ageMs > 35 * 24 * 60 * 60 * 1000) {
          warns.push(
            'taxStatus.fatcaStatus.ffiListVerificationTimestamp is more than 35 days old — ' +
            'the IRS FATCA FFI List is updated monthly; please re-verify the GIIN.'
          );
        }
      }
    }

    // EDD contact data warnings — check typed arrays (emailAddresses[], phoneNumbers[]).
    const ddTypeOuter = kyc.dueDiligenceType;
    if (ddTypeOuter === 'ENHANCED') {
      const originatorPersons = (ivms.originator || {}).originatorPersons || [];
      for (let idx = 0; idx < originatorPersons.length; idx++) {
        const np = originatorPersons[idx].naturalPerson;
        if (np) {
          const hasEmail = Array.isArray(np.emailAddresses) && np.emailAddresses.length > 0;
          const hasPhone = Array.isArray(np.phoneNumbers) && np.phoneNumbers.length > 0;
          if (!hasEmail && !hasPhone) {
            warns.push(
              `ivms101.originator.originatorPersons[${idx}].naturalPerson has neither ` +
              'emailAddresses[] nor phoneNumbers[] — FATF Rec. 16 / AMLR Art. 22 require ' +
              'verified contact data for Enhanced Due Diligence customers.'
            );
          }
        }
      }
    }

    // isPrimary uniqueness warnings — at most one entry per array may be isPrimary: true.
    const checkIsPrimary = (arr, location) => {
      if (!Array.isArray(arr)) return;
      const count = arr.filter((item) => item && item.isPrimary === true).length;
      if (count > 1) {
        warns.push(
          `${location} has ${count} entries with isPrimary: true — ` +
          'at most one entry should be marked as primary.'
        );
      }
    };
    const partyLabels = [
      { partyKey: 'originator', personsKey: 'originatorPersons' },
      { partyKey: 'beneficiary', personsKey: 'beneficiaryPersons' },
    ];
    for (const { partyKey, personsKey } of partyLabels) {
      const persons = ((ivms[partyKey] || {})[personsKey]) || [];
      for (let idx = 0; idx < persons.length; idx++) {
        for (const personType of ['naturalPerson', 'legalPerson']) {
          const person = persons[idx][personType];
          if (person) {
            const base = `ivms101.${partyKey}.${personsKey}[${idx}].${personType}`;
            checkIsPrimary(person.geographicAddress, `${base}.geographicAddress`);
            checkIsPrimary(person.emailAddresses, `${base}.emailAddresses`);
            checkIsPrimary(person.phoneNumbers, `${base}.phoneNumbers`);
          }
        }
      }
    }

    // IBAN without BIC warnings (v1.10.0).
    const partyChecks = [
      { partyKey: 'originator', personsKey: 'originatorPersons' },
      { partyKey: 'beneficiary', personsKey: 'beneficiaryPersons' },
    ];
    for (const { partyKey, personsKey } of partyChecks) {
      const persons = ((ivms[partyKey] || {})[personsKey]) || [];
      for (let idx = 0; idx < persons.length; idx++) {
        for (const personType of ['naturalPerson', 'legalPerson']) {
          const person = persons[idx][personType];
          if (person) {
            const bankingDetails = person.bankingDetails || [];
            for (let bidx = 0; bidx < bankingDetails.length; bidx++) {
              const bd = bankingDetails[bidx];
              if (bd.iban && !bd.bic) {
                warns.push(
                  `ivms101.${partyKey}.${personsKey}[${idx}].${personType}` +
                  `.bankingDetails[${bidx}].iban is present but bic is absent — ` +
                  'BIC is required for SEPA credit transfers and correspondent ' +
                  'banking identification (ISO 9362 / FATF Rec. 16).'
                );
              }
            }
          }
        }
      }
    }

    return warns;
  }
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

function printResult(source, result) {
  const status = result.isValid
    ? `\x1b[32mVALID\x1b[0m (OpenKYCAML v${result.payloadVersion || 'unknown'})`
    : `\x1b[31mINVALID\x1b[0m — ${result.errors.length} error(s)`;

  console.log(`Source : ${source}`);
  console.log(status);

  if (!result.isValid) {
    for (const err of result.errors) {
      console.error(`  \x1b[31m✗\x1b[0m [${err.instancePath}] ${err.message}`);
    }
  }

  if (result.warnings && result.warnings.length > 0) {
    console.log(`\n${result.warnings.length} warning(s):`);
    for (const w of result.warnings) {
      console.warn(`  \x1b[33m⚠\x1b[0m  ${w}`);
    }
  }
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const stdinFlag = args.includes('--stdin');
  const fileArg = args.find((a) => !a.startsWith('--'));

  let validator;
  try {
    validator = new OpenKYCAMLValidator();
  } catch (err) {
    console.error(`ERROR: ${err.message}`);
    process.exit(2);
  }

  if (stdinFlag) {
    let raw = '';
    process.stdin.setEncoding('utf-8');
    process.stdin.on('data', (chunk) => { raw += chunk; });
    process.stdin.on('end', () => {
      let payload;
      try {
        payload = JSON.parse(raw);
      } catch (err) {
        console.error(`ERROR: Invalid JSON on stdin: ${err.message}`);
        process.exit(2);
      }
      const result = validator.validate(payload);
      printResult('<stdin>', result);
      process.exit(result.isValid ? 0 : 1);
    });
  } else if (fileArg) {
    const filePath = path.resolve(fileArg);
    if (!fs.existsSync(filePath)) {
      console.error(`ERROR: File not found: ${filePath}`);
      process.exit(2);
    }
    const result = validator.validateFile(filePath);
    printResult(fileArg, result);
    process.exit(result.isValid ? 0 : 1);
  } else {
    console.error('Usage: node validator.js <file.json>  OR  node validator.js --stdin < file.json');
    process.exit(2);
  }
}

module.exports = { OpenKYCAMLValidator };
