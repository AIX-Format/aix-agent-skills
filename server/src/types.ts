/**
 * Types shared across the L3 gateway.
 *
 * The gateway loads skills.json at boot, extends each entry with optional
 * pricing metadata (the additive `price_usdc` field this Phase introduces),
 * and exposes the resulting registry over a Hono router.
 */

export type SkillTier =
  | 'BASIC_TOOL'
  | 'PRO'
  | 'ADVANCED_TOOL'
  | 'ADVANCED_INFRASTRUCTURE'
  | 'SOVEREIGN';

/**
 * Authored shape of an entry in /skills.json. Only `name`, `description`,
 * `file`, and `tier` were present pre-Phase-6; the rest are new and optional
 * so existing consumers (the constitutional runtime, the go-engine sentinel)
 * keep parsing the file unchanged.
 */
export interface SkillEntry {
  name: string;
  description: string;
  file: string;
  tier: SkillTier;
  /**
   * Phase 6: optional USDC price per call. Decimal string ("0.10" = ten
   * cents). Absent or "0" means free (no payment required, no 402).
   */
  price_usdc?: string;
  /**
   * Phase 6: optional x402 network override. Defaults to env
   * X402_NETWORK ("base" prod / "base-sepolia" staging).
   */
  network?: 'base' | 'base-sepolia' | 'solana' | 'polygon';
}

/**
 * Public projection of a SkillEntry: everything except the file path on
 * disk. Returned by the listing endpoints so the gateway never leaks the
 * source-of-truth path.
 */
export interface PublicSkill {
  name: string;
  description: string;
  tier: SkillTier;
  price_usdc: string;
  network: string;
  manifest_path: string;
}

/**
 * Cloudflare Workers env bindings. Mirrors wrangler.toml [vars] and the
 * secrets declared via `wrangler secret put`. The gateway crashes at
 * startup if any required binding is missing.
 */
export interface Env {
  X402_NETWORK: 'base' | 'base-sepolia';
  X402_FACILITATOR_URL: string;
  GATEWAY_VERSION: string;
  RECEIVING_WALLET: string;
  NONCE_STORE?: KVNamespace;
}
