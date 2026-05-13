/**
 * Tests for package.json changes introduced in this PR.
 *
 * This PR removed the `aix` metadata block from package.json:
 *   { stackVersion, stackCodename, spec, layer, layerName, authority }
 *
 * These tests verify:
 *   - The `aix` block is no longer present.
 *   - All required core fields (name, version, description, license, scripts)
 *     remain intact.
 *   - The package is still valid JSON.
 *   - No extraneous top-level AIX-stack keys were inadvertently left behind.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

function test(description, fn) {
  try {
    fn();
    console.log(`  ✅ ${description}`);
    return true;
  } catch (err) {
    console.error(`  ❌ ${description}`);
    console.error(`     ${err.message}`);
    return false;
  }
}

async function runTests() {
  let passed = 0;
  let failed = 0;

  console.log('Running test_pr_package_json.js...');

  const rootDir = path.join(__dirname, '..');
  const packagePath = path.join(rootDir, 'package.json');

  // Parse package.json once
  let pkg = {};
  let parseError = null;
  try {
    pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  } catch (err) {
    parseError = err;
  }

  // --- Structural integrity ---

  const ok0 = test('package.json exists', () => {
    assert.ok(fs.existsSync(packagePath), 'package.json must exist at repo root');
  });
  ok0 ? passed++ : failed++;

  const ok1 = test('package.json is valid JSON', () => {
    assert.ok(parseError === null, `package.json must be valid JSON: ${parseError}`);
  });
  ok1 ? passed++ : failed++;

  // --- aix block removal (the core change in this PR) ---

  const ok2 = test('package.json does NOT have an "aix" top-level key (removed in this PR)', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'aix'),
      'package.json must not contain an "aix" key; the Echo369 metadata block was removed in this PR'
    );
  });
  ok2 ? passed++ : failed++;

  const ok3 = test('package.json does not contain "stackVersion" anywhere at top level', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'stackVersion'),
      'stackVersion must not be a top-level key in package.json'
    );
  });
  ok3 ? passed++ : failed++;

  const ok4 = test('package.json does not contain "stackCodename" at top level', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'stackCodename'),
      'stackCodename must not be a top-level key in package.json'
    );
  });
  ok4 ? passed++ : failed++;

  const ok5 = test('package.json does not contain "spec" at top level', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'spec'),
      '"spec" must not be a top-level key in package.json'
    );
  });
  ok5 ? passed++ : failed++;

  const ok6 = test('package.json does not contain "layer" at top level', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'layer'),
      '"layer" must not be a top-level key in package.json'
    );
  });
  ok6 ? passed++ : failed++;

  const ok7 = test('package.json does not contain "layerName" at top level', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'layerName'),
      '"layerName" must not be a top-level key in package.json'
    );
  });
  ok7 ? passed++ : failed++;

  const ok8 = test('package.json does not contain "authority" at top level', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'authority'),
      '"authority" must not be a top-level key in package.json'
    );
  });
  ok8 ? passed++ : failed++;

  // Regression: raw string check so even a differently-shaped aix block is caught
  const ok9 = test('raw package.json text does not contain "Echo369"', () => {
    const raw = fs.readFileSync(packagePath, 'utf8');
    assert.ok(
      !raw.includes('Echo369'),
      'package.json must not contain the "Echo369" codename; it was part of the removed aix block'
    );
  });
  ok9 ? passed++ : failed++;

  const ok10 = test('raw package.json text does not contain "axiomid.app"', () => {
    const raw = fs.readFileSync(packagePath, 'utf8');
    assert.ok(
      !raw.includes('axiomid.app'),
      'package.json must not contain "axiomid.app"; it was part of the removed aix block'
    );
  });
  ok10 ? passed++ : failed++;

  // --- Required fields that must survive the removal ---

  const ok11 = test('package.json "name" is "aix-agent-skills"', () => {
    assert.strictEqual(
      pkg.name,
      'aix-agent-skills',
      'package.json "name" must remain "aix-agent-skills"'
    );
  });
  ok11 ? passed++ : failed++;

  const ok12 = test('package.json "version" field is present', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg, 'version'),
      'package.json must have a "version" field'
    );
  });
  ok12 ? passed++ : failed++;

  const ok13 = test('package.json "version" is a non-empty string', () => {
    assert.strictEqual(typeof pkg.version, 'string', '"version" must be a string');
    assert.ok(pkg.version.length > 0, '"version" must not be empty');
  });
  ok13 ? passed++ : failed++;

  const ok14 = test('package.json "description" field is present', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg, 'description'),
      'package.json must have a "description" field'
    );
  });
  ok14 ? passed++ : failed++;

  const ok15 = test('package.json "license" is "Apache-2.0"', () => {
    assert.strictEqual(pkg.license, 'Apache-2.0', '"license" must be "Apache-2.0"');
  });
  ok15 ? passed++ : failed++;

  const ok16 = test('package.json "scripts" object is present', () => {
    assert.ok(
      typeof pkg.scripts === 'object' && pkg.scripts !== null,
      'package.json must have a "scripts" object'
    );
  });
  ok16 ? passed++ : failed++;

  const ok17 = test('package.json "scripts.test" invokes validate_manifest', () => {
    assert.ok(
      typeof pkg.scripts.test === 'string' &&
        pkg.scripts.test.includes('validate_manifest'),
      '"scripts.test" must invoke validate_manifest'
    );
  });
  ok17 ? passed++ : failed++;

  // Boundary / negative: the aix block's sub-keys must not exist inside any nested object
  const ok18 = test('removed aix block sub-key "stackVersion" is absent from the aix object (if aix existed)', () => {
    // If the aix key somehow came back, its sub-keys should not include stackVersion
    if (pkg.aix) {
      assert.ok(
        !Object.prototype.hasOwnProperty.call(pkg.aix, 'stackVersion'),
        'aix.stackVersion must not exist'
      );
    }
    // If pkg.aix is absent the test trivially passes — which is the expected state.
  });
  ok18 ? passed++ : failed++;

  // Summary
  console.log(`\nResults: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

runTests();