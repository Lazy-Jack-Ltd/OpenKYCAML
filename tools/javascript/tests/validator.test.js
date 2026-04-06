/**
 * OpenKYCAML JavaScript Validator — Basic Test Suite
 * ====================================================
 * Uses Node.js built-in test runner (node:test), available from Node.js 18+.
 *
 * Run: node --test tests/
 */

'use strict';

const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');
const { OpenKYCAMLValidator } = require('../validator');

const EXAMPLES_DIR = path.resolve(__dirname, '../../../examples');

// ---------------------------------------------------------------------------
// Minimal valid payload (Travel Rule — natural person)
// ---------------------------------------------------------------------------
const VALID_PAYLOAD = {
  $schema: 'https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json',
  version: '1.3.0',
  messageId: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
  messageDateTime: '2026-01-01T00:00:00Z',
  ivms101: {
    originator: {
      originatorPersons: [
        {
          naturalPerson: {
            name: {
              nameIdentifier: [
                {
                  primaryIdentifier: 'Smith',
                  secondaryIdentifier: 'Jane',
                  nameIdentifierType: 'LEGL'
                }
              ]
            },
            nationalIdentification: {
              nationalIdentifier: 'DE-123456789',
              nationalIdentifierType: 'CCPT'
            },
            countryOfResidence: 'DE'
          }
        }
      ],
      accountNumber: ['0xABCDEF1234567890ABCDEF1234567890ABCDEF12']
    },
    beneficiary: {
      beneficiaryPersons: [
        {
          naturalPerson: {
            name: {
              nameIdentifier: [
                {
                  primaryIdentifier: 'Jones',
                  secondaryIdentifier: 'Bob',
                  nameIdentifierType: 'LEGL'
                }
              ]
            }
          }
        }
      ],
      accountNumber: ['0x9876543210ABCDEF9876543210ABCDEF98765432']
    },
    originatingVASP: {
      vasp: {
        legalPerson: {
          name: {
            nameIdentifier: [
              {
                legalPersonName: 'Acme Crypto Exchange BV',
                legalPersonNameIdentifierType: 'LEGL'
              }
            ]
          },
          nationalIdentification: {
            nationalIdentifier: '529900T8BM49AURSDO55',
            nationalIdentifierType: 'LEIX'
          },
          countryOfRegistration: 'NL'
        }
      }
    },
    beneficiaryVASP: {
      vasp: {
        legalPerson: {
          name: {
            nameIdentifier: [
              {
                legalPersonName: 'Fintech Exchange Ltd',
                legalPersonNameIdentifierType: 'LEGL'
              }
            ]
          },
          nationalIdentification: {
            nationalIdentifier: '213800QILIUD4ROSUO03',
            nationalIdentifierType: 'LEIX'
          },
          countryOfRegistration: 'GB'
        }
      }
    },
    transferredAmount: {
      amount: '1.5',
      assetType: 'ETH'
    }
  }
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('OpenKYCAMLValidator', () => {
  const validator = new OpenKYCAMLValidator();

  it('should accept a valid minimal Travel Rule payload', () => {
    const result = validator.validate(VALID_PAYLOAD);
    assert.equal(result.isValid, true, `Expected valid but got errors: ${JSON.stringify(result.errors)}`);
  });

  it('should reject a payload missing required top-level fields', () => {
    const invalid = { version: '1.3.0' }; // missing messageId, messageDateTime
    const result = validator.validate(invalid);
    assert.equal(result.isValid, false, 'Expected invalid payload to fail validation');
    assert.ok(result.errors.length > 0, 'Expected at least one error');
  });

  it('should reject a payload with an invalid version string', () => {
    const invalid = { ...VALID_PAYLOAD, version: 'not-a-version' };
    const result = validator.validate(invalid);
    assert.equal(result.isValid, false, 'Expected invalid version to fail');
  });

  it('should validate a file path from the examples directory', () => {
    const filePath = path.join(EXAMPLES_DIR, 'minimal-travel-rule.json');
    const result = validator.validateFile(filePath);
    assert.equal(result.isValid, true, `Expected example to be valid: ${JSON.stringify(result.errors)}`);
  });

  it('should return errors array even for valid payloads (empty array)', () => {
    const result = validator.validate(VALID_PAYLOAD);
    assert.ok(Array.isArray(result.errors), 'errors should always be an array');
    assert.equal(result.errors.length, 0);
  });
});
