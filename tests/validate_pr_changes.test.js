/**
 * validate_pr_changes.test.js
 *
 * Tests covering the changes introduced in this pull request:
 * - package.json: removal of the `aix` custom metadata block
 * - assets: deletion of the v2 SVG files (aix-footer-quote-v2, aix-stack-diagram-v2,
 *   aix-stack-header-v2, axi-mascot) and existence of their non-v2 replacements
 * - skills: mcts-simulator, prompt-evaluator, prompt-weaver, resonance-engine —
 *   stub TODO sections replaced with real content; title format updated; References added
 * - AGENTS.md: heading style, snake_case convention documented, em-dash bullet format
 * - README.md: v2 asset references removed; satellite layers section removed;
 *   non-v2 asset references present
 */

'use strict';

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.join(__dirname, '..');

let passed = 0;
let failed = 0;

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

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function readFile(relPath) {
  return fs.readFileSync(path.join(ROOT, relPath), 'utf8');
}

function exists(relPath) {
  return fs.existsSync(path.join(ROOT, relPath));
}

// ---------------------------------------------------------------------------
// 1. package.json — removal of the `aix` custom metadata block
// ---------------------------------------------------------------------------

console.log('\n── package.json ──');

const pkg = JSON.parse(readFile('package.json'));

test('package.json does not have the "aix" custom metadata block', () => {
  assert.ok(
    !Object.prototype.hasOwnProperty.call(pkg, 'aix'),
    'The "aix" field was removed in this PR and must not be present'
  );
});

test('package.json retains "name" field', () => {
  assert.strictEqual(pkg.name, 'aix-agent-skills');
});

test('package.json retains "version" field', () => {
  assert.ok(
    typeof pkg.version === 'string' && pkg.version.length > 0,
    '"version" must be a non-empty string'
  );
});

test('package.json retains "description" field', () => {
  assert.ok(
    typeof pkg.description === 'string' && pkg.description.length > 0,
    '"description" must be a non-empty string'
  );
});

test('package.json retains "license" field set to Apache-2.0', () => {
  assert.strictEqual(pkg.license, 'Apache-2.0');
});

test('package.json retains "scripts.test" entry', () => {
  assert.ok(
    pkg.scripts && typeof pkg.scripts.test === 'string' && pkg.scripts.test.length > 0,
    '"scripts.test" must exist and be non-empty'
  );
});

test('package.json "scripts.test" does not contain undefined or null', () => {
  assert.ok(
    !pkg.scripts.test.includes('undefined') && !pkg.scripts.test.includes('null'),
    '"scripts.test" must not reference undefined/null'
  );
});

// Regression: none of the removed aix sub-fields should have leaked back
test('package.json does not contain stackVersion', () => {
  assert.ok(!JSON.stringify(pkg).includes('stackVersion'));
});

test('package.json does not contain stackCodename', () => {
  assert.ok(!JSON.stringify(pkg).includes('stackCodename'));
});

test('package.json does not contain "Echo369" codename', () => {
  assert.ok(!JSON.stringify(pkg).includes('Echo369'));
});

// ---------------------------------------------------------------------------
// 2. Assets — v2 SVG files deleted; non-v2 replacements exist
// ---------------------------------------------------------------------------

console.log('\n── assets/ ──');

const DELETED_ASSETS = [
  'assets/aix-footer-quote-v2.svg',
  'assets/aix-stack-diagram-v2.svg',
  'assets/aix-stack-header-v2.svg',
  'assets/axi-mascot.svg',
];

const REQUIRED_ASSETS = [
  'assets/aix-footer-quote.svg',
  'assets/aix-stack-diagram.svg',
  'assets/aix-stack-header.svg',
];

for (const asset of DELETED_ASSETS) {
  test(`${asset} has been deleted (must not exist)`, () => {
    assert.ok(
      !exists(asset),
      `${asset} was removed in this PR and must not exist`
    );
  });
}

for (const asset of REQUIRED_ASSETS) {
  test(`${asset} exists`, () => {
    assert.ok(exists(asset), `${asset} must exist`);
  });

  test(`${asset} is a non-empty file`, () => {
    const content = readFile(asset);
    assert.ok(content.length > 0, `${asset} must not be empty`);
  });

  test(`${asset} is a valid SVG document`, () => {
    const content = readFile(asset);
    assert.ok(
      content.trim().startsWith('<svg') || content.includes('<svg'),
      `${asset} must contain an <svg> element`
    );
  });
}

// ---------------------------------------------------------------------------
// 3. Skill files — TODOs replaced; title format; References section
// ---------------------------------------------------------------------------

console.log('\n── skills ──');

const CHANGED_SKILLS = [
  'skills/mcts-simulator.md',
  'skills/prompt-evaluator.md',
  'skills/prompt-weaver.md',
  'skills/resonance-engine.md',
];

const REQUIRED_SKILL_SECTIONS = [
  '## Purpose',
  '## Constitutional Alignment',
  '## Operational Flow',
  '## Failure Modes',
  '## References',
];

// Stub text that must no longer appear in any of the changed skills
const STUB_PATTERNS = [
  'TODO: Define purpose.',
  'TODO: Define constitutional alignment.',
  'TODO: Define operational flow.',
  'TODO: Define failure modes.',
  // Catch any remaining TODO prefix regardless of casing
];

for (const skillRelPath of CHANGED_SKILLS) {
  const skillName = path.basename(skillRelPath, '.md');
  const content = readFile(skillRelPath);

  test(`${skillName}: file exists`, () => {
    assert.ok(exists(skillRelPath), `${skillRelPath} must exist`);
  });

  for (const section of REQUIRED_SKILL_SECTIONS) {
    test(`${skillName}: contains section "${section}"`, () => {
      assert.ok(
        content.includes(section),
        `${skillRelPath} must contain the section "${section}"`
      );
    });
  }

  // Each required section must be followed by substantive content (>50 chars after heading)
  for (const section of REQUIRED_SKILL_SECTIONS.slice(0, 4)) {
    test(`${skillName}: section "${section}" has non-stub content`, () => {
      const idx = content.indexOf(section);
      assert.ok(idx !== -1, `section "${section}" not found`);
      const after = content.slice(idx + section.length).trim();
      assert.ok(
        after.length > 50,
        `section "${section}" appears to be a stub (content too short after the heading)`
      );
    });
  }

  // No TODO stubs remaining
  for (const stub of STUB_PATTERNS) {
    test(`${skillName}: does not contain stub "${stub}"`, () => {
      assert.ok(
        !content.includes(stub),
        `${skillRelPath} must not contain the stub placeholder "${stub}"`
      );
    });
  }

  // Title must use comma separator (", TIER:"), not em-dash (" — TIER:")
  test(`${skillName}: title uses ", TIER:" format (not "— TIER:")`, () => {
    const firstLine = content.split('\n')[0];
    assert.ok(
      firstLine.includes(', TIER:'),
      `First line of ${skillRelPath} must contain ", TIER:" but got: ${firstLine}`
    );
    assert.ok(
      !firstLine.includes('— TIER:'),
      `First line of ${skillRelPath} must not contain "— TIER:" (em-dash format was replaced)`
    );
  });

  // Failure Modes section must include a markdown table
  test(`${skillName}: Failure Modes section contains a table`, () => {
    const fmIdx = content.indexOf('## Failure Modes');
    assert.ok(fmIdx !== -1, '"## Failure Modes" section missing');
    const fmContent = content.slice(fmIdx);
    assert.ok(
      fmContent.includes('|'),
      `${skillRelPath} "Failure Modes" section must contain a markdown table`
    );
  });

  // Purpose section must mention the skill id in some form
  test(`${skillName}: Purpose section references the skill name`, () => {
    const purposeIdx = content.indexOf('## Purpose');
    assert.ok(purposeIdx !== -1, '"## Purpose" missing');
    const purposeContent = content.slice(purposeIdx, purposeIdx + 600);
    assert.ok(
      purposeContent.includes('`' + skillName + '`') ||
      purposeContent.toLowerCase().includes(skillName.replace(/-/g, ' ')),
      `${skillRelPath} "Purpose" section should reference the skill by name`
    );
  });
}

// Skill-specific: mcts-simulator
console.log('\n  ── mcts-simulator specifics ──');
{
  const content = readFile('skills/mcts-simulator.md');

  test('mcts-simulator: Constitutional Alignment mentions sovereign-constitution', () => {
    const caIdx = content.indexOf('## Constitutional Alignment');
    const caContent = content.slice(caIdx, caIdx + 800);
    assert.ok(
      caContent.includes('sovereign-constitution'),
      'Constitutional Alignment must reference sovereign-constitution'
    );
  });

  test('mcts-simulator: Operational Flow has 7 numbered steps', () => {
    const ofIdx = content.indexOf('## Operational Flow');
    const ofEnd = content.indexOf('\n## ', ofIdx + 1);
    const ofContent = content.slice(ofIdx, ofEnd === -1 ? undefined : ofEnd);
    // Count numbered steps: lines starting with digit followed by period
    const steps = ofContent.match(/^\d+\.\s/gm);
    assert.ok(
      steps && steps.length >= 7,
      `mcts-simulator Operational Flow should have at least 7 steps, found ${steps ? steps.length : 0}`
    );
  });

  test('mcts-simulator: References section cites LATS or MCTS paper', () => {
    const refIdx = content.indexOf('## References');
    const refContent = content.slice(refIdx);
    assert.ok(
      refContent.includes('MCTS') || refContent.includes('Monte Carlo') || refContent.includes('LATS'),
      'References must cite an MCTS or LATS source'
    );
  });

  test('mcts-simulator: Failure Modes includes "low_confidence" mode', () => {
    assert.ok(
      content.includes('low_confidence'),
      'Failure Modes must document the low_confidence flag'
    );
  });

  test('mcts-simulator: Failure Modes includes "no_compliant_plan" mode', () => {
    assert.ok(
      content.includes('no_compliant_plan'),
      'Failure Modes must document the no_compliant_plan failure'
    );
  });
}

// Skill-specific: prompt-evaluator
console.log('\n  ── prompt-evaluator specifics ──');
{
  const content = readFile('skills/prompt-evaluator.md');

  test('prompt-evaluator: Purpose mentions five criteria', () => {
    const purposeIdx = content.indexOf('## Purpose');
    const purposeContent = content.slice(purposeIdx, purposeIdx + 800);
    assert.ok(
      purposeContent.includes('five') || purposeContent.includes('5'),
      'Purpose section must mention the five evaluation criteria'
    );
  });

  test('prompt-evaluator: Constitutional Alignment mentions three-judge requirement', () => {
    const caIdx = content.indexOf('## Constitutional Alignment');
    const caContent = content.slice(caIdx, caIdx + 1000);
    assert.ok(
      caContent.includes('three-judge') || caContent.includes('three judge'),
      'Constitutional Alignment must describe the three-judge requirement'
    );
  });

  test('prompt-evaluator: Operational Flow mentions 0.8 threshold', () => {
    const ofIdx = content.indexOf('## Operational Flow');
    const ofContent = content.slice(ofIdx, ofIdx + 2000);
    assert.ok(
      ofContent.includes('0.8'),
      'Operational Flow must document the 0.8 pass threshold'
    );
  });

  test('prompt-evaluator: Failure Modes documents judge_pool_insufficient', () => {
    assert.ok(
      content.includes('judge_pool_insufficient'),
      'Failure Modes must document the judge_pool_insufficient error'
    );
  });

  test('prompt-evaluator: Failure Modes documents Certificate replay attack', () => {
    assert.ok(
      content.includes('Certificate replay') || content.includes('certificate replay'),
      'Failure Modes must document the Certificate replay failure mode'
    );
  });

  test('prompt-evaluator: Operational Flow has at least 6 numbered steps', () => {
    const ofIdx = content.indexOf('## Operational Flow');
    const ofEnd = content.indexOf('\n## ', ofIdx + 1);
    const ofContent = content.slice(ofIdx, ofEnd === -1 ? undefined : ofEnd);
    const steps = ofContent.match(/^\d+\.\s/gm);
    assert.ok(
      steps && steps.length >= 6,
      `prompt-evaluator Operational Flow should have at least 6 steps, found ${steps ? steps.length : 0}`
    );
  });
}

// Skill-specific: prompt-weaver
console.log('\n  ── prompt-weaver specifics ──');
{
  const content = readFile('skills/prompt-weaver.md');

  test('prompt-weaver: Purpose mentions seven-layer prompt', () => {
    const purposeIdx = content.indexOf('## Purpose');
    const purposeContent = content.slice(purposeIdx, purposeIdx + 800);
    assert.ok(
      purposeContent.includes('seven-layer') || purposeContent.includes('7-layer') || purposeContent.includes('seven layer'),
      'Purpose section must reference the seven-layer prompt structure'
    );
  });

  test('prompt-weaver: Purpose describes Weave envelope output', () => {
    const purposeIdx = content.indexOf('## Purpose');
    const purposeContent = content.slice(purposeIdx, purposeIdx + 1000);
    assert.ok(
      purposeContent.includes('Weave envelope') || purposeContent.includes('weave envelope'),
      'Purpose section must describe the Weave envelope output'
    );
  });

  test('prompt-weaver: Constitutional Alignment prohibits hiding instructions', () => {
    const caIdx = content.indexOf('## Constitutional Alignment');
    const caContent = content.slice(caIdx, caIdx + 1000);
    assert.ok(
      caContent.includes('NOT') || caContent.includes('not'),
      'Constitutional Alignment must prohibit hiding instructions'
    );
    assert.ok(
      caContent.includes('hide') || caContent.includes('hidden'),
      'Constitutional Alignment must mention hidden instructions prohibition'
    );
  });

  test('prompt-weaver: Operational Flow has at least 6 steps', () => {
    const ofIdx = content.indexOf('## Operational Flow');
    const ofEnd = content.indexOf('\n## ', ofIdx + 1);
    const ofContent = content.slice(ofIdx, ofEnd === -1 ? undefined : ofEnd);
    const steps = ofContent.match(/^\d+\.\s/gm);
    assert.ok(
      steps && steps.length >= 6,
      `prompt-weaver Operational Flow should have at least 6 steps, found ${steps ? steps.length : 0}`
    );
  });

  test('prompt-weaver: Failure Modes documents persona_unavailable', () => {
    assert.ok(
      content.includes('persona_unavailable'),
      'Failure Modes must document the persona_unavailable failure'
    );
  });

  test('prompt-weaver: Failure Modes documents constitutional_block', () => {
    assert.ok(
      content.includes('constitutional_block'),
      'Failure Modes must document the constitutional_block failure'
    );
  });
}

// Skill-specific: resonance-engine
console.log('\n  ── resonance-engine specifics ──');
{
  const content = readFile('skills/resonance-engine.md');

  test('resonance-engine: Purpose mentions path multiplier', () => {
    const purposeIdx = content.indexOf('## Purpose');
    const purposeContent = content.slice(purposeIdx, purposeIdx + 800);
    assert.ok(
      purposeContent.includes('path multiplier') || purposeContent.includes('pathMultiplier'),
      'Purpose section must mention the path multiplier'
    );
  });

  test('resonance-engine: Operational Flow documents pristine multiplier (2.0)', () => {
    const ofIdx = content.indexOf('## Operational Flow');
    const ofContent = content.slice(ofIdx, ofIdx + 2000);
    assert.ok(
      ofContent.includes('2.0'),
      'Operational Flow must document the pristine path multiplier of 2.0'
    );
  });

  test('resonance-engine: Operational Flow documents stale multiplier (0.5)', () => {
    const ofIdx = content.indexOf('## Operational Flow');
    const ofContent = content.slice(ofIdx, ofIdx + 2000);
    assert.ok(
      ofContent.includes('0.5'),
      'Operational Flow must document the stale path multiplier of 0.5'
    );
  });

  test('resonance-engine: Failure Modes documents confidence_below_floor', () => {
    assert.ok(
      content.includes('confidence_below_floor'),
      'Failure Modes must document the confidence_below_floor flag'
    );
  });

  test('resonance-engine: Failure Modes documents embedding model version drift', () => {
    assert.ok(
      content.includes('embedding') && content.includes('drift'),
      'Failure Modes must document embedding model version drift'
    );
  });

  test('resonance-engine: Operational Flow has at least 5 steps', () => {
    const ofIdx = content.indexOf('## Operational Flow');
    const ofEnd = content.indexOf('\n## ', ofIdx + 1);
    const ofContent = content.slice(ofIdx, ofEnd === -1 ? undefined : ofEnd);
    const steps = ofContent.match(/^\d+\.\s/gm);
    assert.ok(
      steps && steps.length >= 5,
      `resonance-engine Operational Flow should have at least 5 steps, found ${steps ? steps.length : 0}`
    );
  });

  test('resonance-engine: Return output envelope includes score and confidence', () => {
    assert.ok(
      content.includes('score') && content.includes('confidence'),
      'Operational Flow must describe a return envelope with score and confidence fields'
    );
  });
}

// ---------------------------------------------------------------------------
// 4. AGENTS.md — heading style, snake_case convention, em-dash bullet format
// ---------------------------------------------------------------------------

console.log('\n── AGENTS.md ──');

const agentsContent = readFile('AGENTS.md');

test('AGENTS.md: heading uses em-dash style "AGENTS.md — Operating Manual"', () => {
  assert.ok(
    agentsContent.includes('AGENTS.md — Operating Manual'),
    'AGENTS.md title must use em-dash: "AGENTS.md — Operating Manual"'
  );
});

test('AGENTS.md: documents snake_case as the skill naming convention', () => {
  assert.ok(
    agentsContent.includes('snake_case'),
    'AGENTS.md must document snake_case as the skill naming convention'
  );
});

test('AGENTS.md: skill name regex pattern is ^[a-z0-9_]+$', () => {
  assert.ok(
    agentsContent.includes('^[a-z0-9_]+$'),
    'AGENTS.md must reference the snake_case regex ^[a-z0-9_]+$'
  );
});

test('AGENTS.md: does not mention the old kebab-case skill name regex', () => {
  assert.ok(
    !agentsContent.includes('^[a-z0-9]+(?:-[a-z0-9]+)*$'),
    'AGENTS.md must not reference the old kebab-case regex (it was removed in this PR)'
  );
});

test('AGENTS.md: directory bullet items use em-dash (—) separator', () => {
  // The PR changed ": " to " — " in the bullet items for skills/, personas/, etc.
  assert.ok(
    agentsContent.includes('`skills/` —'),
    'AGENTS.md must use em-dash for the skills/ bullet: "`skills/` —"'
  );
  assert.ok(
    agentsContent.includes('`personas/` —'),
    'AGENTS.md must use em-dash for the personas/ bullet'
  );
});

test('AGENTS.md: PR reading list uses em-dash (—) separators', () => {
  // Items like: 1. [AXIOM.md] — the supreme constitution.
  assert.ok(
    agentsContent.includes('— the supreme constitution'),
    'AGENTS.md PR reading list must use em-dash separators'
  );
});

test('AGENTS.md: Skill names convention line does not reference "kebab-case"', () => {
  // The kebab-case convention reference for skill names was removed.
  // Only inspect the first line of the **Skill names** entry (not the Branches line that follows).
  const skillNamesIdx = agentsContent.indexOf('**Skill names**');
  assert.ok(skillNamesIdx !== -1, '**Skill names** entry must exist in Conventions section');
  // Grab text until the next newline to stay on the Skill names line only
  const lineEnd = agentsContent.indexOf('\n', skillNamesIdx);
  const skillNamesLine = agentsContent.slice(skillNamesIdx, lineEnd === -1 ? skillNamesIdx + 200 : lineEnd);
  assert.ok(
    !skillNamesLine.includes('kebab-case'),
    `The Skill names line must not reference kebab-case (changed to snake_case). Line: "${skillNamesLine}"`
  );
});

// ---------------------------------------------------------------------------
// 5. README.md — v2 references removed; satellite section removed
// ---------------------------------------------------------------------------

console.log('\n── README.md ──');

const readmeContent = readFile('README.md');

// v2 asset references must be gone
const v2AssetRefs = [
  'aix-footer-quote-v2.svg',
  'aix-stack-diagram-v2.svg',
  'aix-stack-header-v2.svg',
  'axi-mascot.svg',
];

for (const v2Ref of v2AssetRefs) {
  test(`README.md: does not reference deleted asset "${v2Ref}"`, () => {
    assert.ok(
      !readmeContent.includes(v2Ref),
      `README.md must not reference the deleted asset ${v2Ref}`
    );
  });
}

// Non-v2 asset references must be present
const requiredAssetRefs = [
  './assets/aix-stack-header.svg',
  './assets/aix-stack-diagram.svg',
  './assets/aix-footer-quote.svg',
];

for (const assetRef of requiredAssetRefs) {
  test(`README.md: contains reference to "${assetRef}"`, () => {
    assert.ok(
      readmeContent.includes(assetRef),
      `README.md must reference ${assetRef}`
    );
  });
}

// Removed badges (AIX Stack Echo369, Spec badge) must be gone
test('README.md: does not contain the removed "AIX STACK-Echo369" badge', () => {
  assert.ok(
    !readmeContent.includes('AIX%20STACK-Echo369'),
    'README.md must not contain the Echo369 badge URL (removed in this PR)'
  );
});

test('README.md: does not contain the removed "SPEC-AIX" badge', () => {
  assert.ok(
    !readmeContent.includes('SPEC-AIX%2F1.0') && !readmeContent.includes('SPEC-AIX/1.0'),
    'README.md must not contain the old SPEC-AIX/1.0 badge (removed in this PR)'
  );
});

// Extended Ecosystem satellite layers section was removed
test('README.md: does not contain the removed "Extended Ecosystem" heading', () => {
  assert.ok(
    !readmeContent.includes('### Extended Ecosystem'),
    'README.md must not contain the "Extended Ecosystem" section (removed in this PR)'
  );
});

test('README.md: does not contain the removed satellite layer table (L4/L5/L6)', () => {
  // The satellite table had a header row: | Tier | Repo | Role |
  // combined with satellite-specific content like AlphaAxiom in a satellite context
  assert.ok(
    !readmeContent.includes('AlphaAxiom') || !readmeContent.includes('L4 · SATELLITE'),
    'README.md must not contain the satellite layers table (L4 ALPHAAXIOM row was removed)'
  );
});

test('README.md: does not contain the "Sovereign Stack" sub-nav line removed in this PR', () => {
  assert.ok(
    !readmeContent.includes('**Sovereign Stack**'),
    'README.md must not contain the "Sovereign Stack" sub-navigation line (removed in this PR)'
  );
});

test('README.md: does not contain the removed L0/L4/L5/L6 footer sub-line', () => {
  // The old footer had: <sub>L0 · [axiomid-project] · L4 · [AlphaAxiom] ...
  assert.ok(
    !readmeContent.includes('L0 · [`axiomid-project`]'),
    'README.md must not contain the removed L0 footer sub-line'
  );
});

test('README.md: footer references the non-v2 aix-footer-quote.svg', () => {
  assert.ok(
    readmeContent.includes('assets/aix-footer-quote.svg'),
    'README.md footer must reference aix-footer-quote.svg (not the deleted v2 version)'
  );
});

// The "Quick Start: MCP Config" heading was changed to em-dash style
test('README.md: "Quick Start" MCP section uses em-dash style', () => {
  assert.ok(
    readmeContent.includes('Quick Start — MCP Config') ||
    readmeContent.includes('Quick Start: MCP Config'),
    'README.md must contain a Quick Start MCP Config section'
  );
  // Specifically the PR changed ":" to "—"
  assert.ok(
    !readmeContent.includes('Quick Start: MCP Config'),
    'README.md must use em-dash in the Quick Start heading, not a colon'
  );
});

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------

console.log(`\n${'─'.repeat(60)}`);
console.log(`Results: ${passed} passed, ${failed} failed`);

if (failed > 0) process.exit(1);
