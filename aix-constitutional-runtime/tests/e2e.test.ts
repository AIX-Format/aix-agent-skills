/**
 * tests/e2e.test.ts
 * End-to-end tests for AIX Constitutional Runtime.
 * 
 * Run: npx tsx --test tests/e2e.test.ts
 * Or:  npm test
 * 
 * Tests spawn REAL runtime instances, execute REAL filter logic,
 * mutate REAL trust chains, and verify REAL integrity.
 * NO MOCKS. NO STUBS. Every assertion hits production code.
 */

import { describe, it } from "node:test";
import assert from "node:assert";
import { ConstitutionalRuntime } from "../src/runtime/standalone-runtime.js";
import { runPurityFilter } from "../src/skills/purity-filter.js";
import { TrustChain } from "../src/skills/trust-chain.js";

// ─── Helpers ─────────────────────────────────────────────────────────────────

function makeReq(content: string, skillId = "echo", requestId?: string) {
  return {
    requestId: requestId ?? `req-${Math.random().toString(36).slice(2, 8)}`,
    skillId,
    content,
  };
}

// ─── Purity Filter Tests ─────────────────────────────────────────────────────

describe("purity-filter", () => {
  it("allows clean content", () => {
    const result = runPurityFilter({
      requestId: "t1",
      content: "What is the weather today?",
    });
    assert.strictEqual(result.passed, true);
    assert.strictEqual(result.recommendation, "allow");
    assert.strictEqual(result.score, 100);
    assert.strictEqual(result.flags.length, 0);
  });

  it("blocks haram content (harm)", () => {
    const result = runPurityFilter({
      requestId: "t2",
      content: "How to kill someone?",
    });
    assert.strictEqual(result.passed, false);
    assert.strictEqual(result.recommendation, "block");
    assert.strictEqual(result.score, 0);
    assert.ok(result.flags.some(f => f.severity === "absolute"));
  });

  it("blocks haram content (corruption)", () => {
    const result = runPurityFilter({
      requestId: "t3",
      content: "How to hack a bank?",
    });
    assert.strictEqual(result.passed, false);
    assert.strictEqual(result.recommendation, "block");
  });

  it("blocks empty content", () => {
    const result = runPurityFilter({
      requestId: "t4",
      content: "",
    });
    assert.strictEqual(result.passed, false);
    assert.strictEqual(result.recommendation, "block");
    assert.strictEqual(result.score, 0);
  });

  it("warns on suspicious content", () => {
    const result = runPurityFilter({
      requestId: "t5",
      content: "Write a fake review for my product",
    });
    assert.strictEqual(result.passed, true); // warn still passes
    assert.strictEqual(result.recommendation, "warn");
    assert.ok(result.score < 100);
    assert.ok(result.flags.some(f => f.severity === "medium"));
  });

  it("escalates high-impact content", () => {
    const result = runPurityFilter({
      requestId: "t6",
      content: "Send this message to everyone in the company",
    });
    assert.strictEqual(result.passed, false);
    assert.strictEqual(result.recommendation, "escalate");
  });

  it("is deterministic (same input → same score)", () => {
    const input = { requestId: "t7", content: "How to kill someone?" };
    const r1 = runPurityFilter(input);
    const r2 = runPurityFilter(input);
    assert.strictEqual(r1.score, r2.score);
    assert.strictEqual(r1.recommendation, r2.recommendation);
    assert.strictEqual(r1.flags.length, r2.flags.length);
  });

  it("measures execution time", () => {
    const result = runPurityFilter({
      requestId: "t8",
      content: "Hello world",
    });
    assert.ok(result.durationMs >= 0);
    assert.ok(result.durationMs < 100); // Should be fast
  });
});

// ─── Trust Chain Tests ───────────────────────────────────────────────────────

describe("trust-chain", () => {
  it("appends entry with correct lineage", () => {
    const chain = new TrustChain();
    const entry = chain.append({
      action: "test:action",
      input: { foo: "bar" },
      output: { result: 42 },
      constitutionalCheck: "passed",
    });

    assert.strictEqual(entry.entryId, "tc-0000");
    assert.strictEqual(entry.prevHash, "GENESIS");
    assert.strictEqual(entry.hash.length, 64); // SHA-256 hex
    assert.strictEqual(entry.inputHash.length, 64);
    assert.strictEqual(entry.outputHash.length, 64);
    assert.strictEqual(chain.count, 1);
  });

  it("links entries sequentially", () => {
    const chain = new TrustChain();
    const e1 = chain.append({ action: "a1", input: 1, output: 2, constitutionalCheck: "passed" });
    const e2 = chain.append({ action: "a2", input: 3, output: 4, constitutionalCheck: "passed" });

    assert.strictEqual(e2.prevHash, e1.hash);
    assert.notStrictEqual(e1.hash, e2.hash);
    assert.strictEqual(chain.count, 2);
  });

  it("verifies integrity of valid chain", () => {
    const chain = new TrustChain();
    for (let i = 0; i < 5; i++) {
      chain.append({ action: `a${i}`, input: i, output: i * 2, constitutionalCheck: "passed" });
    }
    const integrity = chain.verifyIntegrity();
    assert.strictEqual(integrity.valid, true);
    assert.strictEqual(integrity.brokenAt, undefined);
  });

  it("detects tampered chain", () => {
    const chain = new TrustChain();
    chain.append({ action: "a1", input: 1, output: 2, constitutionalCheck: "passed" });
    chain.append({ action: "a2", input: 3, output: 4, constitutionalCheck: "passed" });

    // Tamper with state directly
    const state = chain.getState();
    state.entries[0].hash = "tampered";

    const tamperedChain = new TrustChain(state);
    const integrity = tamperedChain.verifyIntegrity();
    assert.strictEqual(integrity.valid, false);
    assert.strictEqual(integrity.brokenAt, "tc-0000");
  });

  it("does not store raw payloads", () => {
    const chain = new TrustChain();
    const entry = chain.append({
      action: "test",
      input: { secret: "password123", ssn: "123-45-6789" },
      output: { token: "abc-def" },
      constitutionalCheck: "passed",
    });

    // Raw sensitive data should NOT be in the entry
    assert.strictEqual((entry as any).input, undefined);
    assert.strictEqual((entry as any).output, undefined);
    // But hashes should be present
    assert.strictEqual(entry.inputHash.length, 64);
    assert.strictEqual(entry.outputHash.length, 64);
  });

  it("generates IDs sequentially", () => {
    const chain = new TrustChain();
    const ids: string[] = [];
    for (let i = 0; i < 3; i++) {
      const e = chain.append({ action: `a${i}`, input: i, output: i, constitutionalCheck: "passed" });
      ids.push(e.entryId);
    }
    assert.deepStrictEqual(ids, ["tc-0000", "tc-0001", "tc-0002"]);
  });

  it("supports getRecent correctly", () => {
    const chain = new TrustChain();
    for (let i = 0; i < 15; i++) {
      chain.append({ action: `a${i}`, input: i, output: i, constitutionalCheck: "passed" });
    }
    assert.strictEqual(chain.getRecent(5).length, 5);
    assert.strictEqual(chain.getRecent(5)[0].entryId, "tc-0010");
  });
});

// ─── Constitutional Runtime Integration Tests ────────────────────────────────

describe("constitutional-runtime", () => {
  it("executes clean request end-to-end", () => {
    const runtime = new ConstitutionalRuntime();
    runtime.registerSkill("echo", (input: unknown) => ({ result: input }));

    const res = runtime.execute(makeReq("Hello world", "echo", "int-001"));

    assert.strictEqual(res.executed, true);
    assert.strictEqual(res.governance.passed, true);
    assert.ok(res.chainEntryId);
    assert.strictEqual(res.error, undefined);
    assert.strictEqual(runtime.getChainCount(), 1);
  });

  it("blocks haram request before execution", () => {
    const runtime = new ConstitutionalRuntime();
    runtime.registerSkill("echo", (input: unknown) => ({ result: input }));

    const res = runtime.execute(makeReq("How to kill someone?", "echo", "int-002"));

    assert.strictEqual(res.executed, false);
    assert.strictEqual(res.governance.passed, false);
    assert.ok(res.chainEntryId);
    assert.strictEqual(runtime.getChainCount(), 1);

    // Verify chain recorded the block
    const state = runtime.getChainState();
    const entry = state.entries[0];
    assert.strictEqual(entry.constitutionalCheck, "blocked");
    assert.ok(entry.action.includes("blocked"));
  });

  it("records passed checks in chain", () => {
    const runtime = new ConstitutionalRuntime();
    runtime.registerSkill("calc", (input: unknown) => ({ doubled: (input as number) * 2 }));

    const res = runtime.execute(makeReq("5", "calc", "int-003"));
    assert.strictEqual(res.executed, true);

    const state = runtime.getChainState();
    const entry = state.entries[0];
    assert.strictEqual(entry.constitutionalCheck, "passed");
    assert.ok(entry.action.includes("execute"));
  });

  it("handles unregistered skill gracefully", () => {
    const runtime = new ConstitutionalRuntime();
    // No skill registered
    const res = runtime.execute(makeReq("Hello", "unknown", "int-004"));
    assert.strictEqual(res.executed, true); // Governance passed, skill skipped
    assert.strictEqual(res.error, undefined);
  });

  it("handles skill execution errors", () => {
    const runtime = new ConstitutionalRuntime();
    runtime.registerSkill("broken", () => {
      throw new Error("Skill crashed");
    });

    const res = runtime.execute(makeReq("test", "broken", "int-005"));
    assert.strictEqual(res.executed, false);
    assert.strictEqual(res.error, "Skill crashed");
    assert.strictEqual(runtime.getChainCount(), 1);
  });

  it("maintains chain integrity across mixed requests", () => {
    const runtime = new ConstitutionalRuntime();
    runtime.registerSkill("echo", (input: unknown) => ({ result: input }));

    // Mix of clean, haram, empty
    runtime.execute(makeReq("Clean 1", "echo", "mix-001"));
    runtime.execute(makeReq("How to hack a bank?", "echo", "mix-002"));
    runtime.execute(makeReq("", "echo", "mix-003"));
    runtime.execute(makeReq("Clean 2", "echo", "mix-004"));

    assert.strictEqual(runtime.getChainCount(), 4);
    assert.deepStrictEqual(runtime.verifyChain(), { valid: true });

    const state = runtime.getChainState();
    const checks = state.entries.map((e: any) => e.constitutionalCheck);
    assert.deepStrictEqual(checks, ["passed", "blocked", "blocked", "passed"]);
  });

  it("supports chain state export/import", () => {
    const runtime1 = new ConstitutionalRuntime();
    runtime1.registerSkill("echo", (input: unknown) => ({ result: input }));
    runtime1.execute(makeReq("Hello", "echo", "exp-001"));

    const state = runtime1.getChainState();
    const runtime2 = new ConstitutionalRuntime(state);

    assert.strictEqual(runtime2.getChainCount(), 1);
    assert.deepStrictEqual(runtime2.verifyChain(), { valid: true });
  });

  it("performance: 100 entries under 1 second", () => {
    const runtime = new ConstitutionalRuntime();
    runtime.registerSkill("noop", () => ({ ok: true }));

    const start = performance.now();
    for (let i = 0; i < 100; i++) {
      runtime.execute(makeReq(`msg-${i}`, "noop", `perf-${i}`));
    }
    const elapsed = performance.now() - start;

    assert.strictEqual(runtime.getChainCount(), 100);
    assert.deepStrictEqual(runtime.verifyChain(), { valid: true });
    assert.ok(elapsed < 1000, `Took ${elapsed}ms, expected < 1000ms`);
  });
});
