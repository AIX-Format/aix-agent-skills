/**
 * Local Journal Skill — اليومية المحلية
 * TIER: PRO
 *
 * "Local memory + Local files + Trust Chain"
 *
 * This skill allows the agent to record reflections, technical notes, and observations
 * into local Markdown files, protected by the Purity Filter and logged in the Trust Chain.
 */

import fs from 'fs';
import path from 'path';
import { createHash } from 'crypto';
import { runPurityFilter } from './purity-filter.js';
import { TrustChain } from './trust-chain.js';

export interface JournalEntry {
  id?: string;
  timestamp: number;
  section: 'reflection' | 'technical' | 'observation';
  content: string;
}

export class LocalJournal {
  private journalDir: string;
  private trustChain: TrustChain;
  private chainFilePath: string;

  constructor(baseDir: string = path.join(process.cwd(), 'journal'), chain?: TrustChain) {
    this.journalDir = baseDir;
    this.trustChain = chain ?? new TrustChain();
    this.chainFilePath = path.join(this.journalDir, '.trust-chain');

    if (!fs.existsSync(this.journalDir)) {
      fs.mkdirSync(this.journalDir, { recursive: true });
    }
  }

  /**
   * Writes an entry to the journal after passing constitutional checks.
   */
  async write(entry: Omit<JournalEntry, 'id'>): Promise<string> {
    // 1. Constitutional Check
    const filterResult = runPurityFilter({
      requestId: `jrnl-${Date.now()}`,
      content: entry.content,
      context: `section:${entry.section}`
    });

    if (!filterResult.passed) {
      this.trustChain.append({
        action: 'journal:write:blocked',
        input: entry,
        output: filterResult,
        constitutionalCheck: 'blocked'
      });
      throw new Error(`Constitutional Veto: ${filterResult.flags[0]?.reason || 'Unknown violation'}`);
    }

    // 2. Generate ID and Metadata
    const id = createHash('sha256')
      .update(`${Date.now()}${entry.content}`)
      .digest('hex')
      .slice(0, 16);

    const timestamp = Date.now();
    const filePath = path.join(this.journalDir, `${id}.md`);

    // 3. Write to File
    const yamlFrontmatter = `---
id: ${id}
timestamp: ${timestamp}
section: ${entry.section}
constitution: passed
---
`;
    fs.writeFileSync(filePath, yamlFrontmatter + '\n' + entry.content);

    // 4. Update Trust Chain (Memory)
    this.trustChain.append({
      action: 'journal:write',
      input: { id, section: entry.section },
      output: { success: true, path: filePath },
      constitutionalCheck: 'passed'
    });

    // 5. Update Local Trust Chain File (Persistence)
    this.appendLocalTrustChain(id, entry.content);

    return id;
  }

  private appendLocalTrustChain(id: string, content: string) {
    const prevHash = fs.existsSync(this.chainFilePath)
      ? createHash('sha256').update(fs.readFileSync(this.chainFilePath)).digest('hex').slice(0, 16)
      : 'genesis';

    const entryLine = `${Date.now()}|${id}|${prevHash}\n`;
    fs.appendFileSync(this.chainFilePath, entryLine);
  }

  /**
   * Reads an entry by ID.
   */
  read(id: string): JournalEntry {
    const filePath = path.join(this.journalDir, `${id}.md`);
    if (!fs.existsSync(filePath)) {
      throw new Error('Entry not found');
    }

    const raw = fs.readFileSync(filePath, 'utf8');
    const sections = raw.split('---\n');
    const content = sections.slice(2).join('---\n').trim();

    // Basic YAML parsing (since we wrote it)
    const metadata = sections[1];
    const sectionMatch = metadata.match(/section: (.*)/);
    const tsMatch = metadata.match(/timestamp: (.*)/);

    return {
      id,
      content,
      section: (sectionMatch ? sectionMatch[1].trim() : 'observation') as any,
      timestamp: tsMatch ? parseInt(tsMatch[1].trim()) : Date.now()
    };
  }

  list(): string[] {
    return fs.readdirSync(this.journalDir)
      .filter(f => f.endsWith('.md'))
      .map(f => f.replace('.md', ''));
  }
}
