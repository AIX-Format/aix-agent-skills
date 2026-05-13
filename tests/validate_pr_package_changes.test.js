/**
 * Tests for package.json changes introduced in this pull request.
 *
 * The PR removed the "aix" metadata block that previously contained:
 *   stackVersion, stackCodename, spec, layer, layerName, authority
 *
 * These tests verify:
 *  - The "aix" block no longer exists.
 *  - All other required fields are preserved.
 *  - package.json is still valid JSON.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.join(__dirname, '..');
const PACKAGE_JSON_PATH = path.join(ROOT_DIR, 'package.json');

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

  console.log('Running validate_pr_package_changes.test.js...');

  // ── Load package.json ──────────────────────────────────────────────────────

  const ok_exists = test('package.json exists at repo root', () => {
    assert.ok(fs.existsSync(PACKAGE_JSON_PATH), 'package.json must exist');
  });
  if (ok_exists) passed++; else failed++;

  let pkg = null;
  let parseErr = null;
  try {
    pkg = JSON.parse(fs.readFileSync(PACKAGE_JSON_PATH, 'utf8'));
  } catch (e) {
    parseErr = e;
  }

  if (test('package.json is valid JSON', () => {
    assert.ok(parseErr === null, `package.json parse error: ${parseErr}`);
  })) passed++; else failed++;

  if (pkg === null) {
    console.error('Cannot continue: package.json could not be parsed.');
    process.exit(1);
  }

  // ── "aix" block removed ────────────────────────────────────────────────────

  if (test('"aix" metadata block does not exist', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'aix'),
      'package.json must not have an "aix" field after this PR'
    );
  })) passed++; else failed++;

  if (test('"stackVersion" is not a top-level field', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'stackVersion'),
      '"stackVersion" must not be a top-level field (it was nested inside the removed "aix" block)'
    );
  })) passed++; else failed++;

  if (test('"stackCodename" is not a top-level field', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'stackCodename'),
      '"stackCodename" must not be a top-level field'
    );
  })) passed++; else failed++;

  if (test('"authority" is not a top-level field', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'authority'),
      '"authority" must not be a top-level field'
    );
  })) passed++; else failed++;

  // ── Required fields still present ─────────────────────────────────────────

  if (test('"name" field is present and equals "aix-agent-skills"', () => {
    assert.strictEqual(pkg.name, 'aix-agent-skills');
  })) passed++; else failed++;

  if (test('"version" field is present', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg, 'version'),
      '"version" must be present'
    );
    assert.strictEqual(typeof pkg.version, 'string');
  })) passed++; else failed++;

  if (test('"version" is "1.0.0"', () => {
    assert.strictEqual(pkg.version, '1.0.0');
  })) passed++; else failed++;

  if (test('"description" field is present and non-empty', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg, 'description'),
      '"description" must be present'
    );
    assert.ok(pkg.description.length > 0, '"description" must be non-empty');
  })) passed++; else failed++;

  if (test('"license" field is "Apache-2.0"', () => {
    assert.strictEqual(pkg.license, 'Apache-2.0');
  })) passed++; else failed++;

  if (test('"scripts" field is present and is an object', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg, 'scripts'),
      '"scripts" must be present'
    );
    assert.strictEqual(typeof pkg.scripts, 'object');
    assert.ok(pkg.scripts !== null);
  })) passed++; else failed++;

  if (test('"scripts.test" is defined and non-empty', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg.scripts, 'test'),
      '"scripts.test" must be defined'
    );
    assert.ok(
      pkg.scripts.test.length > 0,
      '"scripts.test" must not be empty'
    );
  })) passed++; else failed++;

  // ── Structural shape ───────────────────────────────────────────────────────

  if (test('package.json has exactly the expected top-level keys', () => {
    const expectedKeys = new Set(['name', 'version', 'description', 'license', 'scripts']);
    const actualKeys = new Set(Object.keys(pkg));
    const unexpected = [...actualKeys].filter(k => !expectedKeys.has(k));
    assert.strictEqual(
      unexpected.length,
      0,
      `Unexpected top-level keys in package.json: ${unexpected.join(', ')}`
    );
  })) passed++; else failed++;

  // ── Regression: "aix" sub-fields do not appear at any level ───────────────

  if (test('package.json serialised form does not contain "stackCodename"', () => {
    const raw = fs.readFileSync(PACKAGE_JSON_PATH, 'utf8');
    assert.ok(
      !raw.includes('"stackCodename"'),
      'The string "stackCodename" must not appear anywhere in package.json'
    );
  })) passed++; else failed++;

  if (test('package.json serialised form does not contain "Echo369"', () => {
    const raw = fs.readFileSync(PACKAGE_JSON_PATH, 'utf8');
    assert.ok(
      !raw.includes('Echo369'),
      '"Echo369" must not appear in package.json after the aix block was removed'
    );
  })) passed++; else failed++;

  if (test('package.json serialised form does not contain "axiomid.app"', () => {
    const raw = fs.readFileSync(PACKAGE_JSON_PATH, 'utf8');
    assert.ok(
      !raw.includes('axiomid.app'),
      '"axiomid.app" authority must not appear in package.json'
    );
  })) passed++; else failed++;

  // ── Summary ────────────────────────────────────────────────────────────────

  console.log(`\nResults: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

runTests();
