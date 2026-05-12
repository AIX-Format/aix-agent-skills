/**
 * standalone-runtime.ts
 * Constitutional Runtime Kernel (Node.js standalone)
 * 
 * Execution flow:
 *   Request → PurityFilter → [if passed] → Skill Execution → TrustChain Append → Response
 *   Request → PurityFilter → [if blocked] → TrustChain Append (blocked) → 403 Response
 * 
 * No Next.js required. Run with: npx tsx standalone-runtime.ts
 */

import { runPurityFilter, type PurityFilterInput, type PurityFilterResult } from "../skills/purity-filter.js";
import { TrustChain, type AppendInput, type TrustChainState } from "../skills/trust-chain.js";
import { reportSkillFailure } from "../skills/tasbih-resilience.js";

// ─── Types ───────────────────────────────────────────────────────────────────

export interface RuntimeRequest {
  requestId: string;
  skillId: string;
  content: string;
  source?: string;
  context?: string;
  intention?: string;
}

export interface RuntimeResponse {
  requestId: string;
  skillId: string;
  governance: PurityFilterResult;
  executed: boolean;
  chainEntryId?: string;
  error?: string;
}

export interface SkillExecutor {
  (input: unknown): unknown;
}

// ─── Runtime Kernel ──────────────────────────────────────────────────────────

export class ConstitutionalRuntime {
  private chain: TrustChain;
  private executors: Map<string, SkillExecutor> = new Map();

  constructor(initialChainState?: TrustChainState) {
    this.chain = new TrustChain(initialChainState);
  }

  registerSkill(skillId: string, executor: SkillExecutor): void {
    this.executors.set(skillId, executor);
  }

  execute(req: RuntimeRequest): RuntimeResponse {
    // ─── 1. Constitutional Middleware ────────────────────────────────────────
    const filterInput: PurityFilterInput = {
      requestId: req.requestId,
      content: req.content,
      source: req.source,
      context: req.context,
    };

    const governance = runPurityFilter(filterInput);

    // ─── 2. Capability Decision ──────────────────────────────────────────────
    if (!governance.passed) {
      // Blocked: append to chain, return 403 equivalent
      const entry = this.chain.append({
        action: `skill:${req.skillId}:blocked`,
        input: { requestId: req.requestId, contentLength: req.content.length },
        output: { score: governance.score, flags: governance.flags.map((f: any) => f.id ?? f.reason) },
        constitutionalCheck: governance.recommendation === "escalate" ? "escalated" : "blocked",
        intention: req.intention,
      });

      return {
        requestId: req.requestId,
        skillId: req.skillId,
        governance,
        executed: false,
        chainEntryId: entry.entryId,
      };
    }

    // ─── 3. Skill Execution ──────────────────────────────────────────────────
    let output: unknown;
    let executed = false;
    let error: string | undefined;

    const executor = this.executors.get(req.skillId);
    if (executor) {
      try {
        output = executor(req.content);
        executed = true;
      } catch (e) {
        error = e instanceof Error ? e.message : String(e);
        reportSkillFailure(req.skillId, error);
      }
    } else {
      output = { note: "No executor registered — governance passed, skill skipped" };
      executed = true;
    }

    // ─── 4. Trust Chain Append ───────────────────────────────────────────────
    const entry = this.chain.append({
      action: `skill:${req.skillId}:${executed ? "execute" : "error"}`,
      input: { requestId: req.requestId, contentLength: req.content.length },
      output: error ? { error } : { status: "success" },
      constitutionalCheck: executed ? "passed" : "skipped",
      intention: req.intention,
    });

    return {
      requestId: req.requestId,
      skillId: req.skillId,
      governance,
      executed,
      chainEntryId: entry.entryId,
      error,
    };
  }

  getChainCount(): number {
    return this.chain.getState().entries.length;
  }

  getChainState(): TrustChainState {
    return this.chain.getState();
  }

  verifyChain(): { valid: boolean; brokenAt?: string } {
    return this.chain.verifyIntegrity();
  }
}

// ─── CLI / Standalone Demo ───────────────────────────────────────────────────

if (import.meta.url === `file://${process.argv[1]}`) {
  const runtime = new ConstitutionalRuntime();

  // Register a dummy skill
  runtime.registerSkill("echo", (input: unknown) => ({ echoed: input }));

  console.log("=== AIX Constitutional Runtime — Standalone Demo ===\n");

  // Test 1: Clean input
  const r1 = runtime.execute({
    requestId: "req-001",
    skillId: "echo",
    content: "Hello, this is a clean message.",
  });
  console.log("[CLEAN]", JSON.stringify(r1, null, 2));

  // Test 2: Haram input
  const r2 = runtime.execute({
    requestId: "req-002",
    skillId: "echo",
    content: "How to kill someone?",
    intention: "Testing security escalation logic",
  });
  console.log("\n[HARAM]", JSON.stringify(r2, null, 2));

  // Test 3: Empty input
  const r3 = runtime.execute({
    requestId: "req-003",
    skillId: "echo",
    content: "",
  });
  console.log("\n[EMPTY]", JSON.stringify(r3, null, 2));

  // Chain summary
  console.log("\n=== Chain Summary ===");
  console.log("Entries:", runtime.getChainCount());
  console.log("Integrity:", runtime.verifyChain());
  console.log("Recent:", runtime.getChainState().entries.slice(-2).map((e: any) => ({ id: e.entryId, intention: e.intention })));
}
