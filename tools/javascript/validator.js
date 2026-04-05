#!/usr/bin/env node
/**
 * OpenKYCAML Schema Validator (JavaScript / Node.js)
 * ====================================================
 * Validates JSON payloads against the OpenKYCAML v1.3.0 schema.
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
