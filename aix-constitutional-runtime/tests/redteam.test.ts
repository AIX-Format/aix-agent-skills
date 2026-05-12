import { RedTeamGuard } from '../src/skills/red-team-guard.js';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

test('RedTeamGuard infrastructure', async (t) => {
  const testDir = path.join(process.cwd(), 'test-redteam-' + Date.now());
  const guard = new RedTeamGuard(testDir);

  await t.test('should generate a config file', () => {
    const configPath = guard.generateConfig('Tell me a story');
    assert.ok(fs.existsSync(configPath), 'Config file should exist');
    const content = fs.readFileSync(configPath, 'utf8');
    assert.ok(content.includes('description: IQRA Red Team Evaluation'));
  });

  // We won't run a full promptfoo eval in this environment as it requires network/ollama
  // but we verify the runner handles failures gracefully.
  await t.test('should handle missing promptfoo gracefully', async () => {
    const result = await guard.evaluate('non-existent-config.yaml');
    assert.strictEqual(result.passed, false);
    assert.ok(result.vulnerabilities[0].includes('Execution error'));
  });

  // Cleanup
  fs.rmSync(testDir, { recursive: true, force: true });
});
