const fs = require('fs');
const path = require('path');
const assert = require('assert');

async function runTests() {
  let passed = 0;
  let failed = 0;

  console.log('Running validate_package_aix_metadata.test.js...');

  const rootDir = path.join(__dirname, '..');
  const packagePath = path.join(rootDir, 'package.json');

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

  // Load package.json once
  let pkg = {};
  let parseError = null;
  try {
    pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  } catch (err) {
    parseError = err;
  }

  test('package.json parses without error', () => {
    assert.ok(parseError === null, `package.json must be valid JSON: ${parseError}`);
  });

  // --- aix block existence ---

  test('package.json has an "aix" field', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg, 'aix'),
      'package.json must contain an "aix" metadata block (added in this PR)'
    );
  });

  test('"aix" field is an object', () => {
    assert.strictEqual(
      typeof pkg.aix,
      'object',
      '"aix" must be a JSON object, not a primitive'
    );
    assert.ok(pkg.aix !== null, '"aix" must not be null');
    assert.ok(!Array.isArray(pkg.aix), '"aix" must not be an array');
  });

  // --- individual aix fields ---

  test('"aix.stackVersion" field exists', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg.aix || {}, 'stackVersion'),
      '"aix" must have a "stackVersion" field'
    );
  });

  test('"aix.stackVersion" is "0.369.0"', () => {
    assert.strictEqual(
      pkg.aix && pkg.aix.stackVersion,
      '0.369.0',
      '"aix.stackVersion" must equal "0.369.0"'
    );
  });

  test('"aix.stackVersion" follows SemVer pattern', () => {
    const semver = /^\d+\.\d+\.\d+$/;
    assert.match(
      (pkg.aix && pkg.aix.stackVersion) || '',
      semver,
      '"aix.stackVersion" must be a valid SemVer string (MAJOR.MINOR.PATCH)'
    );
  });

  test('"aix.stackCodename" field exists', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg.aix || {}, 'stackCodename'),
      '"aix" must have a "stackCodename" field'
    );
  });

  test('"aix.stackCodename" is "Echo369"', () => {
    assert.strictEqual(
      pkg.aix && pkg.aix.stackCodename,
      'Echo369',
      '"aix.stackCodename" must equal "Echo369" (the doctrine codename)'
    );
  });

  test('"aix.stackCodename" is a non-empty string', () => {
    const codename = pkg.aix && pkg.aix.stackCodename;
    assert.ok(typeof codename === 'string' && codename.length > 0, '"aix.stackCodename" must be a non-empty string');
  });

  test('"aix.spec" field exists', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg.aix || {}, 'spec'),
      '"aix" must have a "spec" field'
    );
  });

  test('"aix.spec" is "AIX/1.0"', () => {
    assert.strictEqual(
      pkg.aix && pkg.aix.spec,
      'AIX/1.0',
      '"aix.spec" must equal "AIX/1.0"'
    );
  });

  test('"aix.spec" matches AIX/<version> pattern', () => {
    const specPattern = /^AIX\/\d+\.\d+$/;
    assert.match(
      (pkg.aix && pkg.aix.spec) || '',
      specPattern,
      '"aix.spec" must match "AIX/<MAJOR>.<MINOR>" pattern'
    );
  });

  test('"aix.layer" field exists', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg.aix || {}, 'layer'),
      '"aix" must have a "layer" field'
    );
  });

  test('"aix.layer" is "L3"', () => {
    assert.strictEqual(
      pkg.aix && pkg.aix.layer,
      'L3',
      '"aix.layer" must equal "L3" (this repo is the L3 Marketplace)'
    );
  });

  test('"aix.layer" matches L<N> pattern', () => {
    const layerPattern = /^L\d+$/;
    assert.match(
      (pkg.aix && pkg.aix.layer) || '',
      layerPattern,
      '"aix.layer" must match the "L<number>" layer identifier pattern'
    );
  });

  test('"aix.layerName" field exists', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg.aix || {}, 'layerName'),
      '"aix" must have a "layerName" field'
    );
  });

  test('"aix.layerName" is "marketplace"', () => {
    assert.strictEqual(
      pkg.aix && pkg.aix.layerName,
      'marketplace',
      '"aix.layerName" must equal "marketplace"'
    );
  });

  test('"aix.layerName" is lowercase', () => {
    const name = (pkg.aix && pkg.aix.layerName) || '';
    assert.strictEqual(
      name,
      name.toLowerCase(),
      '"aix.layerName" must be all-lowercase'
    );
  });

  test('"aix.authority" field exists', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg.aix || {}, 'authority'),
      '"aix" must have an "authority" field'
    );
  });

  test('"aix.authority" is "axiomid.app"', () => {
    assert.strictEqual(
      pkg.aix && pkg.aix.authority,
      'axiomid.app',
      '"aix.authority" must equal "axiomid.app"'
    );
  });

  test('"aix.authority" looks like a domain name', () => {
    const domain = (pkg.aix && pkg.aix.authority) || '';
    assert.ok(
      domain.includes('.') && domain.length >= 3,
      '"aix.authority" must look like a domain name (contain a dot and be at least 3 chars)'
    );
  });

  // --- consistency checks ---

  test('"aix" block has exactly 6 fields', () => {
    const aix = pkg.aix || {};
    const keys = Object.keys(aix);
    assert.strictEqual(
      keys.length,
      6,
      `"aix" block should have exactly 6 fields (stackVersion, stackCodename, spec, layer, layerName, authority); got ${keys.length}: ${keys.join(', ')}`
    );
  });

  test('"aix" all field values are strings', () => {
    const aix = pkg.aix || {};
    for (const [key, val] of Object.entries(aix)) {
      assert.strictEqual(
        typeof val,
        'string',
        `"aix.${key}" must be a string, got ${typeof val}`
      );
    }
  });

  test('"aix" block does not shadow top-level required fields', () => {
    // The aix block should not accidentally contain "name", "version", "license"
    const aix = pkg.aix || {};
    assert.ok(!Object.prototype.hasOwnProperty.call(aix, 'name'), '"aix" must not contain a "name" key (would shadow top-level)');
    assert.ok(!Object.prototype.hasOwnProperty.call(aix, 'version'), '"aix" must not contain a "version" key');
    assert.ok(!Object.prototype.hasOwnProperty.call(aix, 'license'), '"aix" must not contain a "license" key');
  });

  test('top-level "version" is still "1.0.0"', () => {
    assert.strictEqual(
      pkg.version,
      '1.0.0',
      'package.json top-level "version" must still be "1.0.0"'
    );
  });

  test('top-level "name" is still "aix-agent-skills"', () => {
    assert.strictEqual(
      pkg.name,
      'aix-agent-skills',
      'package.json top-level "name" must still be "aix-agent-skills"'
    );
  });

  // Summary
  console.log(`\nResults: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

runTests();
