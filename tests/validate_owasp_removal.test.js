/**
 * Tests for PR changes to skills.json and skill markdown files.
 *
 * This PR:
 *   - Removed the owasp-agentic-guard entry from skills.json
 *   - Deleted skills/owasp-agentic-guard.md from disk
 *   - Changed title separator in covenant-guard.md, shura-council.md,
 *     and sovereign-constitution.md from ", TIER:" to " — TIER:"
 *   - Updated table entries in sovereign-constitution.md to use em-dash
 *   - Replaced detailed sections in three skill files with TODO stubs
 */

'use strict';

const fs = require('fs');
const path = require('path');
const assert = require('assert');

async function runTests() {
  let passed = 0;
  let failed = 0;

  const rootDir = path.join(__dirname, '..');
  const skillsJsonPath = path.join(rootDir, 'skills.json');
  const skillsDir = path.join(rootDir, 'skills');

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

  console.log('Running validate_owasp_removal.test.js...');
  console.log('');
  console.log('--- skills.json: owasp-agentic-guard removal ---');

  // Load skills.json once
  let manifest = {};
  let parseError = null;
  try {
    manifest = JSON.parse(fs.readFileSync(skillsJsonPath, 'utf8'));
  } catch (err) {
    parseError = err;
  }

  const skillsRaw = fs.existsSync(skillsJsonPath)
    ? fs.readFileSync(skillsJsonPath, 'utf8')
    : '';

  test('skills.json exists', () => {
    assert.ok(fs.existsSync(skillsJsonPath), 'skills.json must exist');
  });

  test('skills.json parses without error', () => {
    assert.ok(parseError === null, `skills.json must be valid JSON: ${parseError}`);
  });

  test('skills.json has a "skills" array', () => {
    assert.ok(Array.isArray(manifest.skills), '"skills" must be an array');
  });

  test('"owasp-agentic-guard" name is absent from skills array', () => {
    const names = (manifest.skills || []).map(s => s.name);
    assert.ok(
      !names.includes('owasp-agentic-guard'),
      `owasp-agentic-guard must not appear in the skills array; found: ${names.join(', ')}`
    );
  });

  test('"skills/owasp-agentic-guard.md" file reference is absent from skills array', () => {
    const files = (manifest.skills || []).map(s => s.file);
    assert.ok(
      !files.includes('skills/owasp-agentic-guard.md'),
      'skills/owasp-agentic-guard.md must not be referenced in skills.json'
    );
  });

  test('"owasp-agentic-guard" string does not appear anywhere in skills.json', () => {
    assert.ok(
      !skillsRaw.includes('owasp-agentic-guard'),
      'The string "owasp-agentic-guard" must not appear anywhere in skills.json'
    );
  });

  test('OWASP description text absent from skills.json', () => {
    assert.ok(
      !skillsRaw.includes('OWASP Top 10 for Agentic Applications'),
      'OWASP description must not appear in skills.json after removal'
    );
  });

  test('skills array has exactly 58 entries after removal', () => {
    assert.strictEqual(
      (manifest.skills || []).length,
      58,
      `Expected 58 skills after owasp-agentic-guard removal; got ${(manifest.skills || []).length}`
    );
  });

  test('"prompt-templates" is the last entry in the skills array', () => {
    const skills = manifest.skills || [];
    const last = skills[skills.length - 1];
    assert.strictEqual(
      last && last.name,
      'prompt-templates',
      `prompt-templates must be the last skill; got: ${last && last.name}`
    );
  });

  test('all remaining skill file references exist on disk', () => {
    const missing = [];
    for (const skill of manifest.skills || []) {
      const fullPath = path.join(rootDir, skill.file);
      if (!fs.existsSync(fullPath)) {
        missing.push(`${skill.name} -> ${skill.file}`);
      }
    }
    assert.strictEqual(
      missing.length,
      0,
      `Missing skill files: ${missing.join(', ')}`
    );
  });

  test('skills array is still non-empty', () => {
    assert.ok(
      (manifest.skills || []).length > 0,
      'skills array must not be empty after the removal'
    );
  });

  // -------------------------------------------------------------------
  console.log('');
  console.log('--- skills/owasp-agentic-guard.md: file deleted ---');

  const owaspPath = path.join(skillsDir, 'owasp-agentic-guard.md');

  test('skills/owasp-agentic-guard.md does not exist on disk', () => {
    assert.ok(
      !fs.existsSync(owaspPath),
      'skills/owasp-agentic-guard.md must have been deleted by this PR'
    );
  });

  // -------------------------------------------------------------------
  console.log('');
  console.log('--- skills/covenant-guard.md: title format ---');

  const covenantPath = path.join(skillsDir, 'covenant-guard.md');
  const covenantContent = fs.existsSync(covenantPath)
    ? fs.readFileSync(covenantPath, 'utf8')
    : '';
  const covenantFirstLine = covenantContent.split('\n')[0] || '';

  test('skills/covenant-guard.md exists', () => {
    assert.ok(fs.existsSync(covenantPath), 'covenant-guard.md must exist');
  });

  test('covenant-guard.md title uses em-dash separator', () => {
    assert.ok(
      covenantFirstLine.includes('—'),
      `covenant-guard.md H1 must use em-dash; got: ${covenantFirstLine}`
    );
  });

  test('covenant-guard.md title contains "— TIER: SOVEREIGN"', () => {
    assert.ok(
      covenantFirstLine.includes('— TIER: SOVEREIGN'),
      `covenant-guard.md must have "— TIER: SOVEREIGN" in title; got: ${covenantFirstLine}`
    );
  });

  test('covenant-guard.md title does not use old ", TIER:" format', () => {
    assert.ok(
      !covenantFirstLine.includes(', TIER:'),
      `covenant-guard.md must not use ", TIER:" format; got: ${covenantFirstLine}`
    );
  });

  test('covenant-guard.md oath item 3 uses em-dash separator', () => {
    assert.ok(
      covenantContent.includes('لا تضليل — والاعتراف الفوري بالخطأ'),
      'Oath item 3 must use em-dash: "لا تضليل — والاعتراف الفوري بالخطأ"'
    );
  });

  test('covenant-guard.md still has ## Purpose section', () => {
    assert.ok(covenantContent.includes('## Purpose'), 'covenant-guard.md must have ## Purpose section');
  });

  test('covenant-guard.md Purpose section has TODO stub', () => {
    assert.ok(
      covenantContent.includes('TODO: Define purpose.'),
      'covenant-guard.md Purpose section must have TODO stub'
    );
  });

  test('covenant-guard.md old detailed operational flow removed', () => {
    assert.ok(
      !covenantContent.includes('On first activation, present the canonical covenant text'),
      'Old operational flow detail must have been removed from covenant-guard.md'
    );
  });

  // -------------------------------------------------------------------
  console.log('');
  console.log('--- skills/shura-council.md: title format ---');

  const shuraPath = path.join(skillsDir, 'shura-council.md');
  const shuraContent = fs.existsSync(shuraPath)
    ? fs.readFileSync(shuraPath, 'utf8')
    : '';
  const shuraFirstLine = shuraContent.split('\n')[0] || '';

  test('skills/shura-council.md exists', () => {
    assert.ok(fs.existsSync(shuraPath), 'shura-council.md must exist');
  });

  test('shura-council.md title uses em-dash separator', () => {
    assert.ok(
      shuraFirstLine.includes('—'),
      `shura-council.md H1 must use em-dash; got: ${shuraFirstLine}`
    );
  });

  test('shura-council.md title contains "— TIER: ADVANCED_INFRASTRUCTURE"', () => {
    assert.ok(
      shuraFirstLine.includes('— TIER: ADVANCED_INFRASTRUCTURE'),
      `shura-council.md must have "— TIER: ADVANCED_INFRASTRUCTURE" in title; got: ${shuraFirstLine}`
    );
  });

  test('shura-council.md title does not use old ", TIER:" format', () => {
    assert.ok(
      !shuraFirstLine.includes(', TIER:'),
      `shura-council.md must not use ", TIER:" format; got: ${shuraFirstLine}`
    );
  });

  test('shura-council.md still has ## Purpose section', () => {
    assert.ok(shuraContent.includes('## Purpose'), 'shura-council.md must have ## Purpose section');
  });

  test('shura-council.md Purpose section has TODO stub', () => {
    assert.ok(
      shuraContent.includes('TODO: Define purpose.'),
      'shura-council.md Purpose section must have TODO stub'
    );
  });

  test('shura-council.md old Byzantine references removed', () => {
    assert.ok(
      !shuraContent.includes('Byzantine-Robust Decentralized Coordination'),
      'Old Byzantine references must be removed from shura-council.md'
    );
  });

  // -------------------------------------------------------------------
  console.log('');
  console.log('--- skills/sovereign-constitution.md: title and table format ---');

  const constitutionPath = path.join(skillsDir, 'sovereign-constitution.md');
  const constitutionContent = fs.existsSync(constitutionPath)
    ? fs.readFileSync(constitutionPath, 'utf8')
    : '';
  const constitutionFirstLine = constitutionContent.split('\n')[0] || '';

  test('skills/sovereign-constitution.md exists', () => {
    assert.ok(fs.existsSync(constitutionPath), 'sovereign-constitution.md must exist');
  });

  test('sovereign-constitution.md title uses em-dash separator', () => {
    assert.ok(
      constitutionFirstLine.includes('—'),
      `sovereign-constitution.md H1 must use em-dash; got: ${constitutionFirstLine}`
    );
  });

  test('sovereign-constitution.md title contains "— TIER: SOVEREIGN"', () => {
    assert.ok(
      constitutionFirstLine.includes('— TIER: SOVEREIGN'),
      `sovereign-constitution.md must have "— TIER: SOVEREIGN" in title; got: ${constitutionFirstLine}`
    );
  });

  test('sovereign-constitution.md title does not use old ", TIER:" format', () => {
    assert.ok(
      !constitutionFirstLine.includes(', TIER:'),
      `sovereign-constitution.md must not use ", TIER:" format; got: ${constitutionFirstLine}`
    );
  });

  test('sovereign-constitution.md HaramGuard table row uses em-dash', () => {
    assert.ok(
      constitutionContent.includes('قائمة المحظورات المطلقة — لا تُناقش ولا تُفاوض'),
      'HaramGuard row must use em-dash separator'
    );
  });

  test('sovereign-constitution.md EthicalFilter table row uses em-dash', () => {
    assert.ok(
      constitutionContent.includes('فلتر النوايا — يفحص كل مهمة قبل التنفيذ'),
      'EthicalFilter row must use em-dash separator'
    );
  });

  test('sovereign-constitution.md still has all five component names', () => {
    const components = ['HaramGuard', 'EthicalFilter', 'ConstitutionDB', 'ConsultationAPI', 'OverrideDetector'];
    for (const c of components) {
      assert.ok(
        constitutionContent.includes(c),
        `sovereign-constitution.md must still list component: ${c}`
      );
    }
  });

  test('sovereign-constitution.md Purpose section has TODO stub', () => {
    assert.ok(
      constitutionContent.includes('TODO: Define purpose.'),
      'sovereign-constitution.md Purpose section must have TODO stub'
    );
  });

  test('sovereign-constitution.md old Anthropic reference removed', () => {
    assert.ok(
      !constitutionContent.includes('Bai et al., "Constitutional AI'),
      'Old Anthropic Constitutional AI reference must be removed'
    );
  });

  // -------------------------------------------------------------------
  console.log('');
  console.log(`Results: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

runTests();
