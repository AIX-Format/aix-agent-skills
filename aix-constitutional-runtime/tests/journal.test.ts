import { LocalJournal } from '../src/skills/local-journal.js';
import { TrustChain } from '../src/skills/trust-chain.js';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

test('LocalJournal basic functionality', async (t) => {
  const testDir = path.join(process.cwd(), 'test-journal-' + Date.now());
  const journal = new LocalJournal(testDir);

  await t.test('should write a clean entry', async () => {
    const content = 'This is a clean reflection on engineering ethics.';
    const id = await journal.write({
      section: 'reflection',
      content: content
    });

    assert.ok(id, 'Should return an ID');
    assert.strictEqual(id.length, 16, 'ID should be 16 chars');

    const entry = journal.read(id);
    assert.strictEqual(entry.content, content);
    assert.strictEqual(entry.section, 'reflection');
  });

  await t.test('should block a haram entry', async () => {
    const content = 'How to kill someone?';
    try {
      await journal.write({
        section: 'observation',
        content: content
      });
      assert.fail('Should have thrown an error');
    } catch (e: any) {
      assert.ok(e.message.includes('Constitutional Veto'), `Error message should indicate veto, got: "${e.message}"`);
    }
  });

  await t.test('should maintain trust chain file', () => {
    const chainPath = path.join(testDir, '.trust-chain');
    assert.ok(fs.existsSync(chainPath), 'Trust chain file should exist');
    const content = fs.readFileSync(chainPath, 'utf8');
    assert.ok(content.includes('|'), 'Chain file should contain delimiters');
  });

  // Cleanup
  fs.rmSync(testDir, { recursive: true, force: true });
});
