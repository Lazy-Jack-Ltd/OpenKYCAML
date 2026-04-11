#!/usr/bin/env node
/**
 * OpenKYCAML Schema Validator
 *
 * Validates a JSON data file against the OpenKYCAML Hybrid Extended Schema.
 *
 * Usage:
 *   node validate.js <data-file> [--schema <schema-file>]
 *
 * Examples:
 *   node validate.js ../../examples/minimal-travel-rule.json
 *   node validate.js data.json --schema ../../schema/kyc-aml-hybrid-extended.json
 */

"use strict";

const fs = require("fs");
const path = require("path");

let Ajv;
try {
  Ajv = require("ajv");
} catch {
  console.error("Error: ajv package is required. Install it with:");
  console.error("  npm install ajv ajv-formats");
  process.exit(1);
}

let addFormats;
try {
  addFormats = require("ajv-formats");
} catch {
  // ajv-formats is optional but recommended
  addFormats = null;
}

const DEFAULT_SCHEMA = path.resolve(
  __dirname,
  "..",
  "..",
  "schema",
  "kyc-aml-hybrid-extended.json"
);

function loadJson(filePath) {
  const resolved = path.resolve(filePath);
  if (!fs.existsSync(resolved)) {
    console.error(`Error: File not found: ${filePath}`);
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(resolved, "utf-8"));
}

function parseArgs(argv) {
  const args = { dataFile: null, schemaFile: DEFAULT_SCHEMA };
  const positional = [];

  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === "--schema" && i + 1 < argv.length) {
      args.schemaFile = argv[++i];
    } else if (!argv[i].startsWith("--")) {
      positional.push(argv[i]);
    }
  }

  if (positional.length === 0) {
    console.error("Usage: node validate.js <data-file> [--schema <schema-file>]");
    process.exit(1);
  }

  args.dataFile = positional[0];
  return args;
}

function main() {
  const args = parseArgs(process.argv);
  const schema = loadJson(args.schemaFile);
  const data = loadJson(args.dataFile);

  const ajv = new Ajv({ allErrors: true, strict: false, validateSchema: false });
  if (addFormats) {
    addFormats(ajv);
  }

  const valid = ajv.validate(schema, data);

  if (valid) {
    console.log(`✅ Valid: ${args.dataFile}`);
  } else {
    console.error(`❌ Validation failed: ${args.dataFile}`);
    for (const err of ajv.errors) {
      console.error(`   Path: ${err.instancePath || "/"}`);
      console.error(`   Error: ${err.message}`);
    }
    process.exit(1);
  }
}

main();
