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

  // --- Additional LICENSE section tests ---

  test('LICENSE contains Submission of Contributions section', () => {
    assert.ok(
      licenseContent.includes('5. Submission of Contributions.'),
      'LICENSE must contain section "5. Submission of Contributions."'
    );
  });

  test('LICENSE contains Trademarks section', () => {
    assert.ok(
      licenseContent.includes('6. Trademarks.'),
      'LICENSE must contain section "6. Trademarks."'
    );
  });

  test('LICENSE contains Accepting Warranty or Additional Liability section', () => {
    assert.ok(
      licenseContent.includes('9. Accepting Warranty or Additional Liability.'),
      'LICENSE must contain section "9. Accepting Warranty or Additional Liability."'
    );
  });

  test('LICENSE contains APPENDIX section', () => {
    assert.ok(
      licenseContent.includes('APPENDIX: How to apply the Apache License to your work.'),
      'LICENSE must contain the APPENDIX section'
    );
  });

  test('LICENSE contains the full copy URL (LICENSE-2.0)', () => {
    assert.ok(
      licenseContent.includes('http://www.apache.org/licenses/LICENSE-2.0'),
      'LICENSE must contain the full Apache 2.0 copy URL'
    );
  });

  test('LICENSE has at least 200 lines', () => {
    const lineCount = licenseContent.split('\n').length;
    assert.ok(lineCount >= 200, `LICENSE must have at least 200 lines, got ${lineCount}`);
  });

  test('LICENSE contains "AS IS" disclaimer text', () => {
    assert.ok(
      licenseContent.includes('"AS IS"'),
      'LICENSE must contain the "AS IS" warranty disclaimer text'
    );
  });

  test('LICENSE contains "WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND"', () => {
    assert.ok(
      licenseContent.includes('WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND'),
      'LICENSE must contain the "WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND" disclaimer'
    );
  });

  test('LICENSE boilerplate states it is licensed under Apache License Version 2.0', () => {
    assert.ok(
      licenseContent.includes('Licensed under the Apache License, Version 2.0 (the "License")'),
      'LICENSE boilerplate must state it is licensed under Apache License Version 2.0'
    );
  });

  // --- Additional package.json tests ---

  test('package.json has a "name" field with value "aix-agent-skills"', () => {
    assert.strictEqual(
      pkg.name,
      'aix-agent-skills',
      'package.json "name" must be "aix-agent-skills"'
    );
  });

  test('package.json has a "scripts" field', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg, 'scripts'),
      'package.json must have a "scripts" field'
    );
  });

  test('package.json "scripts" has a "test" property', () => {
    assert.ok(
      pkg.scripts && Object.prototype.hasOwnProperty.call(pkg.scripts, 'test'),
      'package.json "scripts" must have a "test" property'
    );
  });

  test('package.json scripts.test includes validate_license_and_package.test.js', () => {
    assert.ok(
      pkg.scripts && typeof pkg.scripts.test === 'string' &&
        pkg.scripts.test.includes('validate_license_and_package.test.js'),
      'package.json "scripts.test" must include "validate_license_and_package.test.js"'
    );
  });

  test('package.json scripts.test includes all three test files', () => {
    const testScript = pkg.scripts && pkg.scripts.test || '';
    assert.ok(
      testScript.includes('validate_manifest.test.js'),
      'package.json "scripts.test" must include "validate_manifest.test.js"'
    );
    assert.ok(
      testScript.includes('validate_skill_format.test.js'),
      'package.json "scripts.test" must include "validate_skill_format.test.js"'
    );
    assert.ok(
      testScript.includes('validate_license_and_package.test.js'),
      'package.json "scripts.test" must include "validate_license_and_package.test.js"'
    );
  });

  test('package.json "license" is exactly "Apache-2.0" (case-sensitive)', () => {
    assert.ok(
      pkg.license === 'Apache-2.0',
      `package.json "license" must be exactly "Apache-2.0", got "${pkg.license}"`
    );
    assert.ok(
      pkg.license !== 'apache-2.0' && pkg.license !== 'APACHE-2.0',
      'package.json "license" must use the correct SPDX casing "Apache-2.0"'
    );
  });

  test('package.json "license" does not contain extra whitespace', () => {
    assert.strictEqual(
      pkg.license,
      pkg.license && pkg.license.trim(),
      'package.json "license" must not have leading or trailing whitespace'
    );
  });

  // Summary
  console.log(`\nResults: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);


runTests();
