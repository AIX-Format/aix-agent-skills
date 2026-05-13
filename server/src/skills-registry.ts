/**
 * Skills registry. Loads /skills.json once at module load and exposes
 * typed accessors the Hono router consumes. The loader is intentionally
 * eager (not lazy) so a malformed skills.json fails the worker at boot
 * rather than producing 500s on the first request.
 */

import type { PublicSkill, SkillEntry, SkillTier } from './types';

// Static import so Cloudflare Workers bundles the JSON into the worker.
// Wrangler resolves the relative path against the worker's working dir.
import skillsJson from '../../skills.json' assert { type: 'json' };

interface SkillsJsonShape {
  name: string;
  description: string;
  skills: SkillEntry[];
}

const data = skillsJson as SkillsJsonShape;

/**
 * In-memory index keyed by skill name for O(1) lookup. Built once at
 * module init.
 */
const index = new Map<string, SkillEntry>();
for (const entry of data.skills) {
  if (index.has(entry.name)) {
    // Duplicate names are a content-layer bug; surface them loudly at
    // boot rather than silently using the first or last occurrence.
    throw new Error(`skills-registry: duplicate skill name "${entry.name}"`);
  }
  index.set(entry.name, entry);
}

/**
 * Default price per tier when a skill does not declare its own
 * `price_usdc`. Phase 6 starts with conservative defaults; operators can
 * override per skill or per tier without changing this map.
 */
const TIER_DEFAULT_PRICE_USDC: Record<SkillTier, string> = {
  BASIC_TOOL: '0',
  PRO: '0',
  ADVANCED_TOOL: '0',
  ADVANCED_INFRASTRUCTURE: '0',
  SOVEREIGN: '0',
};

/** All skills currently registered, in the order they appear in skills.json. */
export function listSkills(): SkillEntry[] {
  return Array.from(index.values());
}

/** Lookup by exact name. Returns `null` for unknown names. */
export function getSkill(name: string): SkillEntry | null {
  return index.get(name) ?? null;
}

/**
 * Resolve the USDC price for a skill, falling back to the tier default.
 * Returns "0" for free skills.
 */
export function priceFor(entry: SkillEntry): string {
  if (entry.price_usdc !== undefined && entry.price_usdc !== '') {
    return entry.price_usdc;
  }
  return TIER_DEFAULT_PRICE_USDC[entry.tier] ?? '0';
}

/** True iff the skill is payment-gated (price > 0). */
export function isPaid(entry: SkillEntry): boolean {
  const price = priceFor(entry);
  return price !== '0' && parseFloat(price) > 0;
}

/**
 * Project a registry entry into the public shape returned by the listing
 * endpoints. Strips the on-disk file path; returns a stable manifest_path
 * derived from the skill name.
 */
export function toPublic(entry: SkillEntry, defaultNetwork: string): PublicSkill {
  return {
    name: entry.name,
    description: entry.description,
    tier: entry.tier,
    price_usdc: priceFor(entry),
    network: entry.network ?? defaultNetwork,
    manifest_path: `/skills/${entry.name}/manifest`,
  };
}
