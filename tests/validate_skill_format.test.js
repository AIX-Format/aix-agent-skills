const fs = require('fs');
const path = require('path');
const assert = require('assert');

async function runTests() {
  let passed = 0;
  let failed = 0;

  console.log('Running validate_skill_format.test.js...');

  try {
    const manifestPath = path.join(__dirname, '..', 'skills.json');
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

    const requiredSections = [
      '## Purpose',
      '## Constitutional Alignment',
      '## Operational Flow',
      '## Failure Modes'
    ];

    const missingSections = [];

    for (const skill of manifest.skills) {
      const skillPath = path.join(__dirname, '..', skill.file);
      if (fs.existsSync(skillPath)) {
        const content = fs.readFileSync(skillPath, 'utf8');
        for (const section of requiredSections) {
          if (!content.includes(section)) {
            missingSections.push(`${skill.name} (${skill.file}) is missing '${section}'`);
          }
        }
      }
    }

    if (missingSections.length > 0) {
      throw new Error(missingSections.join('\n'));
    }

    console.log('✅ validate_skill_format.test.js passed');
    passed++;
  } catch (error) {
    console.error('❌ validate_skill_format.test.js failed:');
    console.error(error.message);
    failed++;
  }

  if (failed > 0) process.exit(1);
}

runTests();
