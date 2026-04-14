/**
 * OpenVASP ↔ OpenKYCAML Converter
 * ================================
 * Converts between OpenVASP 1.0 identity payload objects and the
 * OpenKYCAML ivms101 block.
 *
 * OpenVASP uses the IVMS 101 standard for identity data in its VAAN/
 * Session/Transfer message flow. This converter handles the structural
 * differences between the OpenVASP Whitepaper identity object format and
 * the OpenKYCAML ivms101 block.
 *
 * Reference: OpenVASP Whitepaper (https://www.openvasp.org/)
 *
 * Usage (Node.js):
 *   const { openvaspToOpenKYCAML, openKYCAMLToOpenVASP } = require('./openvasp-converter');
 *
 *   const envelope  = openvaspToOpenKYCAML(openvaspTransferPayload);
 *   const ovPayload = openKYCAMLToOpenVASP(openKYCAMLEnvelope);
 */

'use strict';

const { randomUUID } = require('crypto');

// ---------------------------------------------------------------------------
// OpenVASP → OpenKYCAML
// ---------------------------------------------------------------------------

/**
 * Convert an OpenVASP Transfer message body (identity section) into an
 * OpenKYCAML envelope.
 *
 * @param {object} openvaspPayload - OpenVASP Transfer1/Transfer2 message body.
 *   Expected keys: originator (IVMS101 Originator object), beneficiary
 *   (IVMS101 Beneficiary object), originatingVASP (IVMS101 OriginatingVASP),
 *   beneficiaryVASP (IVMS101 BeneficiaryVASP), transferredAmount (optional).
 * @returns {object} OpenKYCAML envelope with ivms101 block populated.
 */
function openvaspToOpenKYCAML(openvaspPayload) {
  if (!openvaspPayload || typeof openvaspPayload !== 'object') {
    throw new TypeError('openvaspPayload must be a non-null object');
  }

  const ivms101 = {};

  // --- Originator ----------------------------------------------------------
  if (openvaspPayload.originator) {
    ivms101.originator = _mapOpenVASPPerson(openvaspPayload.originator, 'originator');
  }

  // --- Beneficiary ---------------------------------------------------------
  if (openvaspPayload.beneficiary) {
    ivms101.beneficiary = _mapOpenVASPPerson(openvaspPayload.beneficiary, 'beneficiary');
  }

  // --- Originating VASP ----------------------------------------------------
  if (openvaspPayload.originatingVASP || openvaspPayload.originator_vasp) {
    ivms101.originatingVASP = _mapOpenVASPVASP(
      openvaspPayload.originatingVASP || openvaspPayload.originator_vasp
    );
  }

  // --- Beneficiary VASP ----------------------------------------------------
  if (openvaspPayload.beneficiaryVASP || openvaspPayload.beneficiary_vasp) {
    ivms101.beneficiaryVASP = _mapOpenVASPVASP(
      openvaspPayload.beneficiaryVASP || openvaspPayload.beneficiary_vasp
    );
  }

  // --- Transferred amount --------------------------------------------------
  if (openvaspPayload.transferredAmount) {
    ivms101.transferredAmount = openvaspPayload.transferredAmount;
  } else if (openvaspPayload.virtualAsset && openvaspPayload.transferAmount) {
    ivms101.transferredAmount = {
      amount: String(openvaspPayload.transferAmount),
      assetType: openvaspPayload.virtualAsset,
    };
  }

  return {
    $schema: 'https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json',
    version: '1.3.0',
    messageId: openvaspPayload.messageId || randomUUID(),
    messageDateTime:
      openvaspPayload.messageDateTime ||
      new Date().toISOString().replace(/\.\d{3}Z$/, 'Z'),
    ivms101,
  };
}

// ---------------------------------------------------------------------------
// OpenKYCAML → OpenVASP
// ---------------------------------------------------------------------------

/**
 * Extract the OpenVASP-compatible Transfer message body from an OpenKYCAML
 * envelope.
 *
 * @param {object} openKYCAMLPayload - Full OpenKYCAML envelope.
 * @returns {object} OpenVASP Transfer message body (identity section).
 * @throws {Error} If the payload does not contain an ivms101 block.
 */
function openKYCAMLToOpenVASP(openKYCAMLPayload) {
  if (!openKYCAMLPayload || typeof openKYCAMLPayload !== 'object') {
    throw new TypeError('openKYCAMLPayload must be a non-null object');
  }

  const ivms = openKYCAMLPayload.ivms101;
  if (!ivms) {
    throw new Error(
      "No 'ivms101' block found in this OpenKYCAML payload. Cannot convert to OpenVASP format."
    );
  }

  const result = {
    messageId: openKYCAMLPayload.messageId,
    messageDateTime: openKYCAMLPayload.messageDateTime,
  };

  if (ivms.originator) result.originator = ivms.originator;
  if (ivms.beneficiary) result.beneficiary = ivms.beneficiary;
  if (ivms.originatingVASP) result.originatingVASP = ivms.originatingVASP;
  if (ivms.beneficiaryVASP) result.beneficiaryVASP = ivms.beneficiaryVASP;
  if (ivms.transferredAmount) {
    result.transferredAmount = ivms.transferredAmount;
    result.transferAmount = ivms.transferredAmount.amount;
    result.virtualAsset = ivms.transferredAmount.assetType;
  }

  return result;
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Map an OpenVASP originator/beneficiary person object to an OpenKYCAML
 * originator/beneficiary structure.
 *
 * @private
 */
function _mapOpenVASPPerson(person, role) {
  // OpenVASP person objects closely mirror IVMS 101. Pass through directly
  // if already in IVMS 101 format (naturalPerson / legalPerson wrapper).
  const key = role === 'originator' ? 'originatorPersons' : 'beneficiaryPersons';
  const accountKey = 'accountNumber';

  // Already IVMS 101 structured (OpenVASP v1.1+)
  if (person[key] || person.originatorPersons || person.beneficiaryPersons) {
    return person;
  }

  // Legacy flat structure (OpenVASP Whitepaper format)
  const persons = [];

  if (person.naturalPerson) {
    persons.push({ naturalPerson: person.naturalPerson });
  } else if (person.legalPerson) {
    persons.push({ legalPerson: person.legalPerson });
  } else if (person.name || person.vaan) {
    // Minimal flat format: name only
    persons.push({
      naturalPerson: {
        name: {
          nameIdentifier: [
            {
              primaryIdentifier: person.lastName || person.name || '',
              secondaryIdentifier: person.firstName || '',
              nameIdentifierType: 'LEGL',
            },
          ],
        },
        countryOfResidence: person.country || person.countryOfResidence || '',
      },
    });
  }

  const out = { [key]: persons };
  if (person.vaan || person.accountNumber) {
    out[accountKey] = person.vaan
      ? [person.vaan]
      : Array.isArray(person.accountNumber)
        ? person.accountNumber
        : [person.accountNumber];
  }
  return out;
}

/**
 * Map an OpenVASP VASP object to an OpenKYCAML VASP structure.
 *
 * @private
 */
function _mapOpenVASPVASP(vasp) {
  // Already IVMS 101 structured
  if (vasp && vasp.vasp) {
    return vasp;
  }

  // Flat format with VAAN and optional name / LEI
  const legalPersonName = vasp.name || vasp.legalName || '';
  const lei = vasp.lei || vasp.nationalIdentifier || '';
  const country = vasp.country || vasp.countryOfRegistration || '';

  return {
    vasp: {
      legalPerson: {
        name: {
          nameIdentifier: [
            {
              legalPersonName,
              legalPersonNameIdentifierType: 'LEGL',
            },
          ],
        },
        ...(lei && {
          nationalIdentification: {
            nationalIdentifier: lei,
            nationalIdentifierType: 'LEIX',
          },
        }),
        ...(country && { countryOfRegistration: country }),
      },
    },
  };
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

if (require.main === module) {
  const fs = require('fs');
  const path = require('path');

  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('Usage: node openvasp-converter.js <command> <input.json>');
    console.error('Commands:');
    console.error('  openvasp-to-openkycaml  Convert OpenVASP Transfer body to OpenKYCAML');
    console.error('  openkycaml-to-openvasp  Extract OpenVASP Transfer body from OpenKYCAML');
    process.exit(2);
  }

  const [command, inputFile] = args;
  const inputPath = path.resolve(inputFile);
  const payload = JSON.parse(fs.readFileSync(inputPath, 'utf-8'));

  let result;
  switch (command) {
    case 'openvasp-to-openkycaml':
      result = openvaspToOpenKYCAML(payload);
      break;
    case 'openkycaml-to-openvasp':
      result = openKYCAMLToOpenVASP(payload);
      break;
    default:
      console.error(`Unknown command: ${command}`);
      process.exit(2);
  }

  console.log(JSON.stringify(result, null, 2));
}

module.exports = { openvaspToOpenKYCAML, openKYCAMLToOpenVASP };
