const fs = require('fs');
const path = require('path');
const assert = require('assert');

// Tests for the four orchestration skill files updated in this PR:
// intent-dispatcher.md, mission-control.md, role-tribunal.md, topology-orchestrator.md
async function runTests() {
  let passed = 0;
  let failed = 0;

  console.log('Running validate_skill_orchestration_content.test.js...');

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

  const skillsDir = path.join(__dirname, '..', 'skills');

  const orchestrationSkills = [
    'intent-dispatcher.md',
    'mission-control.md',
    'role-tribunal.md',
    'topology-orchestrator.md',
  ];

  // ── Existence ────────────────────────────────────────────────────────────
  for (const filename of orchestrationSkills) {
    const skillPath = path.join(skillsDir, filename);
    test(`${filename} exists`, () => {
      assert.ok(fs.existsSync(skillPath), `${filename} must exist in skills/`);
    });
  }

  // Read file contents once for all subsequent checks
  const contents = {};
  for (const filename of orchestrationSkills) {
    const skillPath = path.join(skillsDir, filename);
    if (fs.existsSync(skillPath)) {
      contents[filename] = fs.readFileSync(skillPath, 'utf8');
    } else {
      contents[filename] = '';
    }
  }

  // ── Title format: comma before TIER, not em-dash ─────────────────────────
  // PR changed "— TIER:" to ", TIER:" in all four skill titles
  for (const filename of orchestrationSkills) {
    test(`${filename} title uses comma before TIER, not em-dash`, () => {
      const firstLine = contents[filename].split('\n')[0];
      assert.ok(
        firstLine.includes(', TIER:'),
        `${filename} first line must contain ", TIER:" (comma format), got: "${firstLine}"`
      );
    });

    test(`${filename} title does not use em-dash before TIER`, () => {
      const firstLine = contents[filename].split('\n')[0];
      assert.ok(
        !firstLine.includes('— TIER:'),
        `${filename} first line must not contain "— TIER:" (old em-dash format), got: "${firstLine}"`
      );
    });
  }

  // ── No TODO stubs in any of the four required sections ───────────────────
  // PR replaced all "TODO: Define ..." placeholders with real content
  const todoPattern = /^TODO:/m;
  for (const filename of orchestrationSkills) {
    test(`${filename} contains no TODO placeholders`, () => {
      assert.ok(
        !todoPattern.test(contents[filename]),
        `${filename} must not contain any "TODO:" placeholder text`
      );
    });
  }

  // ── Required sections present ─────────────────────────────────────────────
  const requiredSections = [
    '## Purpose',
    '## Constitutional Alignment',
    '## Operational Flow',
    '## Failure Modes',
    '## References',
  ];

  for (const filename of orchestrationSkills) {
    for (const section of requiredSections) {
      test(`${filename} contains "${section}"`, () => {
        assert.ok(
          contents[filename].includes(section),
          `${filename} must contain the section "${section}"`
        );
      });
    }
  }

  // ── Failure Modes section contains a markdown table ───────────────────────
  for (const filename of orchestrationSkills) {
    test(`${filename} Failure Modes section contains a table`, () => {
      const failureSection = contents[filename].split('## Failure Modes')[1] || '';
      assert.ok(
        failureSection.includes('|'),
        `${filename} Failure Modes section must contain a markdown table`
      );
    });
  }

  // ── intent-dispatcher.md specific content ────────────────────────────────
  const dispatcher = contents['intent-dispatcher.md'];

  test('intent-dispatcher Purpose describes pipeline recommendation', () => {
    assert.ok(
      dispatcher.includes('pipeline recommendation') || dispatcher.includes('pipeline'),
      'intent-dispatcher Purpose must describe pipeline recommendation'
    );
  });

  test('intent-dispatcher Purpose mentions skill discovery', () => {
    assert.ok(
      dispatcher.includes('skill discovery') || dispatcher.includes('entry point for skill discovery'),
      'intent-dispatcher Purpose must mention skill discovery'
    );
  });

  test('intent-dispatcher Operational Flow mentions 60% threshold', () => {
    assert.ok(
      dispatcher.includes('60%'),
      'intent-dispatcher Operational Flow must mention the 60% scoring threshold'
    );
  });

  test('intent-dispatcher Operational Flow describes parsing intent step', () => {
    assert.ok(
      dispatcher.includes('Parse intent') || dispatcher.includes('parse intent'),
      'intent-dispatcher Operational Flow must describe the parse-intent step'
    );
  });

  test('intent-dispatcher Operational Flow describes composition fallback step', () => {
    assert.ok(
      dispatcher.includes('Compose') || dispatcher.includes('compose'),
      'intent-dispatcher Operational Flow must describe the composition fallback'
    );
  });

  test('intent-dispatcher Failure Modes covers ambiguous intent case', () => {
    assert.ok(
      dispatcher.includes('ambiguous'),
      'intent-dispatcher Failure Modes must cover the ambiguous-intent case'
    );
  });

  test('intent-dispatcher Failure Modes covers no_pipeline_found case', () => {
    assert.ok(
      dispatcher.includes('no_pipeline_found'),
      'intent-dispatcher Failure Modes must mention no_pipeline_found'
    );
  });

  test('intent-dispatcher References section is non-empty', () => {
    const referencesContent = dispatcher.split('## References')[1] || '';
    assert.ok(
      referencesContent.trim().length > 0,
      'intent-dispatcher ## References section must not be empty'
    );
  });

  // ── mission-control.md specific content ──────────────────────────────────
  const missionControl = contents['mission-control.md'];

  test('mission-control Purpose describes plan-and-execute orchestration', () => {
    assert.ok(
      missionControl.includes('plan-and-execute') || missionControl.includes('orchestrator'),
      'mission-control Purpose must describe plan-and-execute orchestration'
    );
  });

  test('mission-control Purpose mentions seven-stage IQRA cycle', () => {
    assert.ok(
      missionControl.includes('seven-stage') || missionControl.includes('seven stage'),
      'mission-control Purpose must mention the seven-stage IQRA cycle'
    );
  });

  test('mission-control Constitutional Alignment mentions non-skippable ethics gate', () => {
    assert.ok(
      missionControl.includes('non-skippable'),
      'mission-control Constitutional Alignment must state the ethics gate is non-skippable'
    );
  });

  test('mission-control Constitutional Alignment mentions sovereign-constitution', () => {
    assert.ok(
      missionControl.includes('sovereign-constitution'),
      'mission-control Constitutional Alignment must reference sovereign-constitution'
    );
  });

  test('mission-control Operational Flow describes all seven numbered stages', () => {
    // The flow has 8 list items (stages 1-7, with stage 6 "execute" as item 6 between 5 and 7)
    const flowSection = missionControl.split('## Operational Flow')[1] || '';
    for (let i = 1; i <= 8; i++) {
      assert.ok(
        flowSection.includes(`${i}.`),
        `mission-control Operational Flow must have a step ${i}.`
      );
    }
  });

  test('mission-control Operational Flow describes worker chain', () => {
    assert.ok(
      missionControl.includes('Planner') && missionControl.includes('Validator') && missionControl.includes('Reporter'),
      'mission-control must reference Planner, Validator, and Reporter workers'
    );
  });

  test('mission-control Failure Modes covers rule-of-9 repair loop', () => {
    assert.ok(
      missionControl.includes('rule-of-9') || missionControl.includes('Rule-of-9'),
      'mission-control Failure Modes must reference the rule-of-9 repair loop'
    );
  });

  test('mission-control References section is non-empty', () => {
    const referencesContent = missionControl.split('## References')[1] || '';
    assert.ok(
      referencesContent.trim().length > 0,
      'mission-control ## References section must not be empty'
    );
  });

  // ── role-tribunal.md specific content ────────────────────────────────────
  const roleTribunal = contents['role-tribunal.md'];

  test('role-tribunal Purpose describes the three possible verdicts', () => {
    assert.ok(
      roleTribunal.includes('permit') && roleTribunal.includes('deny') && roleTribunal.includes('escalate'),
      'role-tribunal Purpose must mention permit, deny, and escalate verdicts'
    );
  });

  test('role-tribunal Purpose mentions Hourglass Gate', () => {
    assert.ok(
      roleTribunal.includes('Hourglass Gate') || roleTribunal.includes('Hourglass'),
      'role-tribunal Purpose must mention the Hourglass Gate'
    );
  });

  test('role-tribunal Constitutional Alignment references Oso or RBAC limitation', () => {
    assert.ok(
      roleTribunal.includes('RBAC') || roleTribunal.includes('Oso'),
      'role-tribunal Constitutional Alignment must reference RBAC limitation or Oso'
    );
  });

  test('role-tribunal Constitutional Alignment explains dynamic capability envelope', () => {
    assert.ok(
      roleTribunal.includes('dynamic') || roleTribunal.includes('shaped by recent'),
      'role-tribunal Constitutional Alignment must explain dynamic capability envelope'
    );
  });

  test('role-tribunal Operational Flow has 9 numbered steps', () => {
    const flowSection = roleTribunal.split('## Operational Flow')[1] || '';
    for (let i = 1; i <= 9; i++) {
      assert.ok(
        flowSection.includes(`${i}.`),
        `role-tribunal Operational Flow must have a step ${i}.`
      );
    }
  });

  test('role-tribunal Operational Flow mentions covenant verification step', () => {
    assert.ok(
      roleTribunal.includes('covenant') || roleTribunal.includes('Verify covenant'),
      'role-tribunal Operational Flow must describe the covenant verification step'
    );
  });

  test('role-tribunal Failure Modes covers Hourglass burnout case', () => {
    assert.ok(
      roleTribunal.includes('Hourglass burnout') || roleTribunal.includes('9 consecutive errors'),
      'role-tribunal Failure Modes must cover the Hourglass burnout case'
    );
  });

  test('role-tribunal Failure Modes covers escalation timeout case', () => {
    assert.ok(
      roleTribunal.includes('Escalation timeout') || roleTribunal.includes('escalation timeout'),
      'role-tribunal Failure Modes must cover the escalation timeout case'
    );
  });

  test('role-tribunal References section is non-empty', () => {
    const referencesContent = roleTribunal.split('## References')[1] || '';
    assert.ok(
      referencesContent.trim().length > 0,
      'role-tribunal ## References section must not be empty'
    );
  });

  // ── topology-orchestrator.md specific content ─────────────────────────────
  const topoOrchestrator = contents['topology-orchestrator.md'];

  test('topology-orchestrator Purpose describes execution graph composition', () => {
    assert.ok(
      topoOrchestrator.includes('execution graph') || topoOrchestrator.includes('directed execution'),
      'topology-orchestrator Purpose must describe directed execution graph composition'
    );
  });

  test('topology-orchestrator Purpose mentions all five execution modes', () => {
    const modes = ['sequential', 'parallel', 'conditional', 'hierarchical', 'swarm'];
    for (const mode of modes) {
      assert.ok(
        topoOrchestrator.includes(mode),
        `topology-orchestrator must mention the "${mode}" execution mode`
      );
    }
  });

  test('topology-orchestrator Constitutional Alignment describes per-layer constitutional gate', () => {
    assert.ok(
      topoOrchestrator.includes('per layer') || topoOrchestrator.includes('each layer'),
      'topology-orchestrator Constitutional Alignment must describe per-layer constitutional checks'
    );
  });

  test('topology-orchestrator Constitutional Alignment references role-tribunal', () => {
    assert.ok(
      topoOrchestrator.includes('role-tribunal'),
      'topology-orchestrator Constitutional Alignment must reference role-tribunal'
    );
  });

  test('topology-orchestrator Operational Flow describes DAG cycle detection', () => {
    assert.ok(
      topoOrchestrator.includes('cycle') || topoOrchestrator.includes('DAG'),
      'topology-orchestrator Operational Flow must describe cycle/DAG detection'
    );
  });

  test('topology-orchestrator Operational Flow describes resonance recording step', () => {
    assert.ok(
      topoOrchestrator.includes('resonance') || topoOrchestrator.includes('Record resonance'),
      'topology-orchestrator Operational Flow must describe resonance recording'
    );
  });

  test('topology-orchestrator Operational Flow describes fallback strategies', () => {
    const fallbackTerms = ['halt', 'retry', 'skip', 'divert'];
    for (const term of fallbackTerms) {
      assert.ok(
        topoOrchestrator.includes(term),
        `topology-orchestrator must mention the "${term}" fallback strategy`
      );
    }
  });

  test('topology-orchestrator Failure Modes covers cycle detection case', () => {
    assert.ok(
      topoOrchestrator.includes('cycle') || topoOrchestrator.includes('Topology contains a cycle'),
      'topology-orchestrator Failure Modes must cover the topology-cycle case'
    );
  });

  test('topology-orchestrator Failure Modes covers swarm divergence case', () => {
    assert.ok(
      topoOrchestrator.includes('Swarm divergence') || topoOrchestrator.includes('swarm divergence'),
      'topology-orchestrator Failure Modes must cover the swarm divergence case'
    );
  });

  test('topology-orchestrator References section is non-empty', () => {
    const referencesContent = topoOrchestrator.split('## References')[1] || '';
    assert.ok(
      referencesContent.trim().length > 0,
      'topology-orchestrator ## References section must not be empty'
    );
  });

  // ── Regression: skills must not end with an empty TODO line ──────────────
  for (const filename of orchestrationSkills) {
    test(`${filename} does not contain "TODO: Define" stub text`, () => {
      assert.ok(
        !contents[filename].includes('TODO: Define'),
        `${filename} must not contain any "TODO: Define" stub text`
      );
    });
  }

  // ── Summary ───────────────────────────────────────────────────────────────
  console.log(`\nResults: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

runTests();
