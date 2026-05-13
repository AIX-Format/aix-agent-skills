const fs = require('fs');
const path = require('path');
const assert = require('assert');

// Tests for the PR changes to: AGENTS.md, package.json, deleted SVG assets, README.md
async function runTests() {
  let passed = 0;
  let failed = 0;

  console.log('Running validate_agents_and_package_pr.test.js...');

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

  const rootDir = path.join(__dirname, '..');

  // ════════════════════════════════════════════════════════════════
  // AGENTS.md — title format and convention changes
  // ════════════════════════════════════════════════════════════════
  const agentsPath = path.join(rootDir, 'AGENTS.md');

  test('AGENTS.md exists', () => {
    assert.ok(fs.existsSync(agentsPath), 'AGENTS.md must exist at repo root');
  });

  const agentsContent = fs.existsSync(agentsPath)
    ? fs.readFileSync(agentsPath, 'utf8')
    : '';

  test('AGENTS.md title uses em-dash separator', () => {
    const firstLine = agentsContent.split('\n')[0];
    assert.ok(
      firstLine.includes('—'),
      `AGENTS.md title must use an em-dash separator, got: "${firstLine}"`
    );
  });

  test('AGENTS.md title is "# AGENTS.md — Operating Manual for AI Coding Agents"', () => {
    const firstLine = agentsContent.split('\n')[0];
    assert.strictEqual(
      firstLine.trim(),
      '# AGENTS.md — Operating Manual for AI Coding Agents',
      'AGENTS.md title must match the updated em-dash format'
    );
  });

  test('AGENTS.md title does not use colon as title separator', () => {
    const firstLine = agentsContent.split('\n')[0];
    assert.ok(
      !firstLine.includes('AGENTS.md:'),
      `AGENTS.md title must not use "AGENTS.md:" (colon format), got: "${firstLine}"`
    );
  });

  test('AGENTS.md Conventions section specifies snake_case for skill names', () => {
    assert.ok(
      agentsContent.includes('snake_case'),
      'AGENTS.md Conventions must specify snake_case for skill names'
    );
  });

  test('AGENTS.md skill name regex is the snake_case pattern', () => {
    assert.ok(
      agentsContent.includes('^[a-z0-9_]+$'),
      'AGENTS.md must include the snake_case regex pattern ^[a-z0-9_]+$'
    );
  });

  test('AGENTS.md Skill names convention line does not use kebab-case', () => {
    // The PR changed skill naming from kebab-case to snake_case.
    // The "Skill names" bullet in Conventions must not say kebab-case.
    // (Branch names still correctly use kebab-case — that is a separate bullet.)
    const skillNamesLine = agentsContent
      .split('\n')
      .find((line) => line.includes('**Skill names**'));
    assert.ok(
      skillNamesLine !== undefined,
      'AGENTS.md must have a "**Skill names**" convention line'
    );
    assert.ok(
      !skillNamesLine.includes('kebab-case'),
      `AGENTS.md "Skill names" convention line must not say kebab-case, got: "${skillNamesLine}"`
    );
  });

  test('AGENTS.md repository overview bullets use em-dash separator', () => {
    // PR changed ": " to " — " in overview bullets
    assert.ok(
      agentsContent.includes('`skills/` —') ||
        agentsContent.includes('skills/` —'),
      'AGENTS.md repository overview bullets must use " — " em-dash separator'
    );
  });

  test('AGENTS.md PR reading list items use em-dash separator', () => {
    // PR changed "1. [AXIOM.md]...: the supreme" to "1. [AXIOM.md]... — the supreme"
    assert.ok(
      agentsContent.includes('AXIOM.md') &&
        agentsContent.includes('— the supreme constitution'),
      'AGENTS.md reading list items must use " — " em-dash separator'
    );
  });

  // ════════════════════════════════════════════════════════════════
  // package.json — removal of `aix` custom metadata block
  // ════════════════════════════════════════════════════════════════
  const packagePath = path.join(rootDir, 'package.json');

  test('package.json exists', () => {
    assert.ok(fs.existsSync(packagePath), 'package.json must exist at repo root');
  });

  let pkg = {};
  try {
    pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  } catch (_) {
    // parse error handled in the next test
  }

  test('package.json is valid JSON', () => {
    assert.doesNotThrow(
      () => JSON.parse(fs.readFileSync(packagePath, 'utf8')),
      'package.json must be valid JSON'
    );
  });

  test('package.json does not have an "aix" metadata field', () => {
    assert.ok(
      !Object.prototype.hasOwnProperty.call(pkg, 'aix'),
      'package.json must not contain the "aix" custom metadata block (it was removed in this PR)'
    );
  });

  test('package.json does not contain stackVersion field', () => {
    const raw = fs.readFileSync(packagePath, 'utf8');
    assert.ok(
      !raw.includes('"stackVersion"'),
      'package.json must not contain "stackVersion" (part of the removed "aix" block)'
    );
  });

  test('package.json does not contain stackCodename field', () => {
    const raw = fs.readFileSync(packagePath, 'utf8');
    assert.ok(
      !raw.includes('"stackCodename"'),
      'package.json must not contain "stackCodename" (part of the removed "aix" block)'
    );
  });

  test('package.json does not contain Echo369 codename string', () => {
    const raw = fs.readFileSync(packagePath, 'utf8');
    assert.ok(
      !raw.includes('Echo369'),
      'package.json must not contain "Echo369" (part of the removed "aix" block)'
    );
  });

  test('package.json retains "name" field as "aix-agent-skills"', () => {
    assert.strictEqual(
      pkg.name,
      'aix-agent-skills',
      'package.json "name" must remain "aix-agent-skills"'
    );
  });

  test('package.json retains "version" field', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg, 'version'),
      'package.json must still have a "version" field'
    );
  });

  test('package.json retains "license" field as "Apache-2.0"', () => {
    assert.strictEqual(
      pkg.license,
      'Apache-2.0',
      'package.json "license" must remain "Apache-2.0"'
    );
  });

  test('package.json retains "scripts" field', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg, 'scripts'),
      'package.json must still have a "scripts" field'
    );
  });

  test('package.json retains "description" field', () => {
    assert.ok(
      Object.prototype.hasOwnProperty.call(pkg, 'description'),
      'package.json must still have a "description" field'
    );
  });

  // ════════════════════════════════════════════════════════════════
  // Deleted SVG assets — files must not exist
  // ════════════════════════════════════════════════════════════════
  const deletedAssets = [
    'assets/aix-footer-quote-v2.svg',
    'assets/aix-stack-diagram-v2.svg',
    'assets/aix-stack-header-v2.svg',
    'assets/axi-mascot.svg',
  ];

  for (const assetRelPath of deletedAssets) {
    const assetPath = path.join(rootDir, assetRelPath);
    test(`deleted asset ${assetRelPath} does not exist`, () => {
      assert.ok(
        !fs.existsSync(assetPath),
        `${assetRelPath} was deleted in this PR and must not exist in the repository`
      );
    });
  }

  // ════════════════════════════════════════════════════════════════
  // README.md — asset path references changed from -v2 to non-v2
  // ════════════════════════════════════════════════════════════════
  const readmePath = path.join(rootDir, 'README.md');

  test('README.md exists', () => {
    assert.ok(fs.existsSync(readmePath), 'README.md must exist at repo root');
  });

  const readmeContent = fs.existsSync(readmePath)
    ? fs.readFileSync(readmePath, 'utf8')
    : '';

  test('README.md references aix-stack-header.svg (not -v2)', () => {
    assert.ok(
      readmeContent.includes('aix-stack-header.svg'),
      'README.md must reference aix-stack-header.svg'
    );
  });

  test('README.md does not reference aix-stack-header-v2.svg', () => {
    assert.ok(
      !readmeContent.includes('aix-stack-header-v2.svg'),
      'README.md must not reference the deleted aix-stack-header-v2.svg'
    );
  });

  test('README.md references aix-stack-diagram.svg (not -v2)', () => {
    assert.ok(
      readmeContent.includes('aix-stack-diagram.svg'),
      'README.md must reference aix-stack-diagram.svg'
    );
  });

  test('README.md does not reference aix-stack-diagram-v2.svg', () => {
    assert.ok(
      !readmeContent.includes('aix-stack-diagram-v2.svg'),
      'README.md must not reference the deleted aix-stack-diagram-v2.svg'
    );
  });

  test('README.md references aix-footer-quote.svg (not -v2)', () => {
    assert.ok(
      readmeContent.includes('aix-footer-quote.svg'),
      'README.md must reference aix-footer-quote.svg'
    );
  });

  test('README.md does not reference aix-footer-quote-v2.svg', () => {
    assert.ok(
      !readmeContent.includes('aix-footer-quote-v2.svg'),
      'README.md must not reference the deleted aix-footer-quote-v2.svg'
    );
  });

  test('README.md does not reference axi-mascot.svg', () => {
    assert.ok(
      !readmeContent.includes('axi-mascot.svg'),
      'README.md must not reference the deleted axi-mascot.svg'
    );
  });

  // Regression: README.md should not reference the old Echo369-labelled v2 assets at all
  test('README.md contains no reference to any -v2.svg asset', () => {
    assert.ok(
      !readmeContent.includes('-v2.svg'),
      'README.md must not contain any reference to "-v2.svg" assets'
    );
  });

  // ── Summary ───────────────────────────────────────────────────────────────
  console.log(`\nResults: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

runTests();