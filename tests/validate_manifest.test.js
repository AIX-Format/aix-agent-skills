const fs = require('fs');
const path = require('path');
const assert = require('assert');

// A simple test runner since node --test is required
async function runTests() {
  let passed = 0;
  let failed = 0;

  console.log('Running validate_manifest.test.js...');

  try {
    const manifestPath = path.join(__dirname, '..', 'skills.json');
    assert.ok(fs.existsSync(manifestPath), 'skills.json must exist');

    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    assert.ok(Array.isArray(manifest.skills), 'manifest.skills must be an array');

    for (const skill of manifest.skills) {
      const skillPath = path.join(__dirname, '..', skill.file);
      assert.ok(fs.existsSync(skillPath), `File for skill ${skill.name} (${skill.file}) must exist`);
    }

    console.log('✅ validate_manifest.test.js passed');
    passed++;
  } catch (error) {
    console.error('❌ validate_manifest.test.js failed:');
    console.error(error.message);
    failed++;
  }

  if (failed > 0) process.exit(1);
}

runTests();
