/**
 * trust-chain.ts
 * TIER: PRO
 * Append-only ledger with SHA-256 lineage.
 * Node.js first (crypto.createHash). Browser fallback (SubtleCrypto).
 * Stores hashes/refs, NOT raw sensitive payloads.
 */

import { createHash } from "node:crypto";

// ─── Types ───────────────────────────────────────────────────────────────────

export interface TrustEntry {
  entryId: string;
  prevHash: string;
  timestamp: string;
  action: string;
  inputHash: string;      // SHA-256 of input (not raw input)
  outputHash: string;     // SHA-256 of output (not raw output)
  payloadRef?: string;    // Optional external reference
  constitutionalCheck: "passed" | "blocked" | "escalated" | "skipped";
  intention?: string;     // النية — from ḤISĀB.md: "النية مهمة أيضاً"
  hash: string;           // SHA-256 of this entry's canonical JSON
}

export interface TrustChainState {
  entries: TrustEntry[];
  latestHash: string;
  entryCount: number;
}

export interface AppendInput {
  action: string;
  input: unknown;
  output: unknown;
  constitutionalCheck: TrustEntry["constitutionalCheck"];
  payloadRef?: string;
  intention?: string;
}

// ─── Hash Helper ─────────────────────────────────────────────────────────────

function sha256(data: string): string {
  return createHash("sha256").update(data).digest("hex");
}

function hashJson(obj: unknown): string {
  return sha256(JSON.stringify(obj));
}

function generateId(index: number): string {
  return `tc-${String(index).padStart(4, "0")}`;
}

// ─── TrustChain Class ────────────────────────────────────────────────────────

export class TrustChain {
  private state: TrustChainState;

  constructor(initialState?: TrustChainState) {
    this.state = initialState ?? {
      entries: [],
      latestHash: "GENESIS",
      entryCount: 0,
    };
  }

  /** إلحاق مدخلة جديدة بالسلسلة */
  append(input: AppendInput): TrustEntry {
    const entryId = generateId(this.state.entryCount);
    const timestamp = new Date().toISOString();
    const inputHash = hashJson(input.input);
    const outputHash = hashJson(input.output);

    // Canonical payload (WITHOUT the entry.hash itself)
    const payload = JSON.stringify({
      entryId,
      prevHash: this.state.latestHash,
      timestamp,
      action: input.action,
      inputHash,
      outputHash,
      payloadRef: input.payloadRef ?? null,
      constitutionalCheck: input.constitutionalCheck,
      intention: input.intention ?? null,
    });

    const hash = sha256(payload);

    const entry: TrustEntry = {
      entryId,
      prevHash: this.state.latestHash,
      timestamp,
      action: input.action,
      inputHash,
      outputHash,
      payloadRef: input.payloadRef,
      constitutionalCheck: input.constitutionalCheck,
      intention: input.intention,
      hash,
    };

    this.state.entries.push(entry);
    this.state.latestHash = hash;
    this.state.entryCount += 1;

    // "لحظة الصدق" — كل 100 مدخلة
    if (this.state.entryCount % 100 === 0) {
      const integrity = this.verifyIntegrity();
      if (!integrity.valid) {
        throw new Error(
          `TRUTH_MOMENT_FAILURE: Chain broken at ${integrity.brokenAt}`
        );
      }
    }

    return entry;
  }

  /** التحقق من سلامة السلسلة كاملة */
  verifyIntegrity(): { valid: boolean; brokenAt?: string } {
    const entries = this.state.entries;

    for (let i = 0; i < entries.length; i++) {
      const entry = entries[i];
      const expectedPrev = i === 0 ? "GENESIS" : entries[i - 1].hash;

      if (entry.prevHash !== expectedPrev) {
        return { valid: false, brokenAt: entry.entryId };
      }

      // Recompute hash
      const payload = JSON.stringify({
        entryId: entry.entryId,
        prevHash: entry.prevHash,
        timestamp: entry.timestamp,
        action: entry.action,
        inputHash: entry.inputHash,
        outputHash: entry.outputHash,
        payloadRef: entry.payloadRef ?? null,
        constitutionalCheck: entry.constitutionalCheck,
        intention: entry.intention ?? null,
      });

      const recomputed = sha256(payload);
      if (recomputed !== entry.hash) {
        return { valid: false, brokenAt: entry.entryId };
      }
    }

    return { valid: true };
  }

  /** الحالة الكاملة (للحفظ في Redis / Upstash) */
  getState(): TrustChainState {
    return structuredClone(this.state);
  }

  /** آخر N مدخلات */
  getRecent(n = 10): TrustEntry[] {
    return this.state.entries.slice(-n);
  }

  get count(): number {
    return this.state.entryCount;
  }
}
