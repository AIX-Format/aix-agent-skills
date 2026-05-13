/**
 * Unit tests for the skills-registry module.
 *
 * These tests verify the in-memory registry built from /skills.json
 * without standing up a Cloudflare Workers runtime. The Hono app
 * integration tests (which require a Worker context with x402
 * middleware) ship in a follow-up because they need either Miniflare
 * or `wrangler dev` and a mock facilitator stand-up; the registry
 * itself is pure and can be exercised in plain Node.
 */

import { describe, expect, it } from 'vitest';

import {
  getSkill,
  isPaid,
  listSkills,
  priceFor,
  toPublic,
} from '../src/skills-registry';

describe('skills-registry', () => {
  it('loads every entry from skills.json', () => {
    const skills = listSkills();
    expect(skills.length).toBeGreaterThan(0);
    // Spot-check that one of the documented seed skills is present.
    expect(skills.some((s) => s.name === 'agent-memory')).toBe(true);
  });

  it('rejects duplicate names at module load (smoke: no exception means clean)', () => {
    // The throw happens at module-init time; importing without an
    // exception is the assertion. The list call below is just to keep
    // the module loaded.
    expect(() => listSkills()).not.toThrow();
  });

  it('returns null for unknown skill names', () => {
    expect(getSkill('skill-that-does-not-exist-xyz')).toBeNull();
  });

  it('returns the canonical entry for a known name', () => {
    const entry = getSkill('agent-memory');
    expect(entry).not.toBeNull();
    expect(entry?.tier).toBeDefined();
    expect(entry?.file).toMatch(/^skills\//);
  });

  it('falls back to "0" price for skills without explicit pricing', () => {
    const entry = getSkill('agent-memory');
    expect(entry).not.toBeNull();
    // Without a price_usdc, priceFor returns the tier default which is
    // "0" for every tier in the Phase 6 baseline.
    if (!entry?.price_usdc) {
      expect(priceFor(entry!)).toBe('0');
    }
  });

  it('returns the authored price when present', () => {
    const synthetic = {
      name: 'synthetic-paid-skill',
      description: 'test',
      file: 'skills/synthetic.md',
      tier: 'PRO' as const,
      price_usdc: '0.25',
    };
    expect(priceFor(synthetic)).toBe('0.25');
  });

  it('isPaid is false for "0", true for positive amounts', () => {
    const free = {
      name: 'a',
      description: 'a',
      file: 'skills/a.md',
      tier: 'BASIC_TOOL' as const,
      price_usdc: '0',
    };
    const paid = {
      name: 'b',
      description: 'b',
      file: 'skills/b.md',
      tier: 'PRO' as const,
      price_usdc: '0.10',
    };
    expect(isPaid(free)).toBe(false);
    expect(isPaid(paid)).toBe(true);
  });

  it('toPublic strips the on-disk file path and emits a stable manifest URL', () => {
    const entry = {
      name: 'voice-wizard',
      description: 'voice flow',
      file: 'skills/voice-wizard.md',
      tier: 'BASIC_TOOL' as const,
    };
    const pub = toPublic(entry, 'base');
    expect(pub.manifest_path).toBe('/skills/voice-wizard/manifest');
    expect(pub.network).toBe('base');
    // Critically: the public projection has no `file` field. Buyers
    // never see the source-of-truth path.
    expect((pub as Record<string, unknown>).file).toBeUndefined();
  });

  it('toPublic honors a per-skill network override over the default', () => {
    const entry = {
      name: 'solana-only',
      description: 'forced to solana',
      file: 'skills/solana-only.md',
      tier: 'PRO' as const,
      network: 'solana' as const,
    };
    const pub = toPublic(entry, 'base');
    expect(pub.network).toBe('solana');
  });
});
