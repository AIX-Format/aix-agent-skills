const fs = require('fs');
const path = require('path');
const assert = require('assert');

async function runTests() {
  let passed = 0;
  let failed = 0;

  console.log('Running validate_license_and_package.test.js...');

  const rootDir = path.join(__dirname, '..');
  const licensePath = path.join(rootDir, 'LICENSE');
  const packagePath = path.join(rootDir, 'package.json');

  // --- LICENSE tests ---

  function test(description, fn) {
    try {
      fn();
      console.log(`  ✅ ${description}`);
      passed++;
    } catch (err) {
      console.error(`  ❌ ${description}`);
      console.error(`     ${err.message}`);
      failed++;
    }
  }

  // LICENSE file existence
  test('LICENSE file exists', () => {
    assert.ok(fs.existsSync(licensePath), 'LICENSE file must exist at repo root');
  });

  // Only proceed with content tests if file exists
  let licenseContent = '';
  if (fs.existsSync(licensePath)) {
    licenseContent = fs.readFileSync(licensePath, 'utf8');
  }

  test('LICENSE contains Apache License header', () => {
    assert.ok(
      licenseContent.includes('Apache License'),
      'LICENSE must contain "Apache License"'
    );
  });

  test('LICENSE specifies Version 2.0', () => {
    assert.ok(
      licenseContent.includes('Version 2.0'),
      'LICENSE must specify "Version 2.0"'
    );
  });

  test('LICENSE references January 2004', () => {
    assert.ok(
      licenseContent.includes('January 2004'),
      'LICENSE must include the standard Apache 2.0 date "January 2004"'
    );
  });

  test('LICENSE contains TERMS AND CONDITIONS section', () => {
    assert.ok(
      licenseContent.includes('TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION'),
      'LICENSE must contain terms and conditions section'
    );
  });

  test('LICENSE contains Definitions section', () => {
    assert.ok(
      licenseContent.includes('1. Definitions.'),
      'LICENSE must contain Definitions section'
    );
  });

  test('LICENSE contains Grant of Copyright License section', () => {
    assert.ok(
      licenseContent.includes('2. Grant of Copyright License.'),
      'LICENSE must contain Grant of Copyright License section'
    );
  });

  test('LICENSE contains Grant of Patent License section', () => {
    assert.ok(
      licenseContent.includes('3. Grant of Patent License.'),
      'LICENSE must contain Grant of Patent License section'
    );
  });

  test('LICENSE contains Redistribution section', () => {
    assert.ok(
      licenseContent.includes('4. Redistribution.'),
      'LICENSE must contain Redistribution section'
    );
  });

  test('LICENSE contains Disclaimer of Warranty section', () => {
    assert.ok(
      licenseContent.includes('7. Disclaimer of Warranty.'),
      'LICENSE must contain Disclaimer of Warranty section'
    );
  });

  test('LICENSE contains Limitation of Liability section', () => {
    assert.ok(
      licenseContent.includes('8. Limitation of Liability.'),
      'LICENSE must contain Limitation of Liability section'
    );
  });

  test('LICENSE contains END OF TERMS AND CONDITIONS marker', () => {
    assert.ok(
      licenseContent.includes('END OF TERMS AND CONDITIONS'),
      'LICENSE must contain "END OF TERMS AND CONDITIONS"'
    );
  });

  test('LICENSE contains Apache 2.0 URL', () => {
    assert.ok(
      licenseContent.includes('http://www.apache.org/licenses/'),
      'LICENSE must reference the Apache license URL'
    );
  });

  test('LICENSE contains copyright year 2026', () => {
    assert.ok(
      licenseContent.includes('Copyright 2026'),
      'LICENSE must contain copyright year 2026'
    );
  });

  test('LICENSE contains copyright owner name', () => {
    assert.ok(
      licenseContent.includes('Mohamed H Abdelaziz'),
      'LICENSE must contain copyright owner "Mohamed H Abdelaziz"'
    );
  });

  test('LICENSE is not empty', () => {
    assert.ok(licenseContent.length > 0, 'LICENSE file must not be empty');
  });

  test('LICENSE does not reference a different license type', () => {
    assert.ok(
      !licenseContent.includes('MIT License') && !licenseContent.includes('GNU General Public License'),
      'LICENSE must not reference other license types'
    );
  });

  // --- package.json tests ---

  test('package.json file exists', () => {
    assert.ok(fs.existsSync(packagePath), 'package.json must exist at repo root');
  });

  let pkg = {};
  let packageParseError = null;
  try {
    pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  } catch (err) {
    packageParseError = err;
  }

  test('package.json is valid JSON', () => {
    assert.ok(packageParseError === null, `package.json must be valid JSON: ${packageParseError}`);
  });

  test('package.json has a "license" field', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg, 'license'),
      'package.json must have a "license" field'
    );
  });

  test('package.json "license" field is "Apache-2.0"', () => {
    assert.strictEqual(
      pkg.license,
      'Apache-2.0',
      'package.json "license" must be "Apache-2.0"'
    );
  });

  test('package.json "license" field is a string', () => {
    assert.strictEqual(
      typeof pkg.license,
      'string',
      'package.json "license" must be a string'
    );
  });

  test('package.json "license" value matches SPDX identifier format', () => {
    // SPDX identifiers use alphanumeric characters and hyphens
    assert.match(
      pkg.license,
      /^[A-Za-z0-9][A-Za-z0-9\-.+]*$/,
      'package.json "license" must be a valid SPDX-format identifier'
    );
  });

  test('package.json "license" is consistent with Apache-2.0 LICENSE file', () => {
    // The license field should correspond to the Apache 2.0 license in LICENSE file
    assert.strictEqual(pkg.license, 'Apache-2.0', '"license" field must match Apache-2.0 SPDX identifier');
    assert.ok(
      licenseContent.includes('Apache License'),
      'LICENSE file content must correspond to Apache-2.0 declared in package.json'
    );
  });

  // --- package.json `aix` metadata block removal (this PR) ---
  // The PR removed the top-level `aix` object that previously held
  // stackVersion, stackCodename, spec, layer, layerName, and authority.
  // These tests guard against accidental reintroduction.

  test('package.json does not contain an "aix" top-level field', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'aix'),
      'package.json must not have an "aix" metadata block after this PR'
    );
  });

  test('package.json does not contain a top-level "stackVersion" field', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'stackVersion'),
      'package.json must not have a top-level "stackVersion" field'
    );
  });

  test('package.json does not contain a top-level "stackCodename" field', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'stackCodename'),
      'package.json must not have a top-level "stackCodename" field'
    );
  });

  test('package.json does not contain a top-level "spec" field', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'spec'),
      'package.json must not have a top-level "spec" field'
    );
  });

  test('package.json does not contain a top-level "authority" field', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'authority'),
      'package.json must not have a top-level "authority" field'
    );
  });

  test('package.json has only the expected top-level keys after aix block removal', () => {
    const allowed = new Set(['name', 'version', 'description', 'license', 'scripts']);
    const actual = Object.keys(pkg);
    const unexpected = actual.filter(k => !allowed.has(k));
    assert.deepStrictEqual(
      unexpected,
      [],
      `Unexpected top-level keys in package.json: ${unexpected.join(', ')}`
    );
  });

  test('package.json "name" field is still "aix-agent-skills"', () => {
    assert.strictEqual(pkg.name, 'aix-agent-skills', '"name" must remain "aix-agent-skills"');
  });

  test('package.json "version" field is still "1.0.0"', () => {
    assert.strictEqual(pkg.version, '1.0.0', '"version" must remain "1.0.0"');
  });

  // Summary
  console.log(`\nResults: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);


runTests();
