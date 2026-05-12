/**
 * standalone-runtime.js — Runtime version (types stripped)
 */

import { runPurityFilter } from "../skills/purity-filter.js";
import { TrustChain } from "../skills/trust-chain.js";

export class ConstitutionalRuntime {
  constructor(initialChainState) {
    this.chain = new TrustChain(initialChainState);
    this.executors = new Map();
  }

  registerSkill(skillId, executor) {
    this.executors.set(skillId, executor);
  }

  execute(req) {
    const governance = runPurityFilter({
      requestId: req.requestId,
      content: req.content,
      source: req.source,
      context: req.context,
    });

    if (!governance.passed) {
      const entry = this.chain.append({
        action: `skill:${req.skillId}:blocked`,
        input: { requestId: req.requestId, contentLength: req.content.length },
        output: { score: governance.score, flags: governance.flags.map(f => f.id ?? f.reason) },
        constitutionalCheck: governance.recommendation === "escalate" ? "escalated" : "blocked",
      });
      return {
        requestId: req.requestId,
        skillId: req.skillId,
        governance,
        executed: false,
        chainEntryId: entry.entryId,
      };
    }

    let output;
    let executed = false;
    let error;

    const executor = this.executors.get(req.skillId);
    if (executor) {
      try {
        output = executor(req.content);
        executed = true;
      } catch (e) {
        error = e instanceof Error ? e.message : String(e);
      }
    } else {
      output = { note: "No executor registered — governance passed, skill skipped" };
      executed = true;
    }

    const entry = this.chain.append({
      action: `skill:${req.skillId}:execute`,
      input: { requestId: req.requestId, contentLength: req.content.length },
      output: error ? { error } : output,
      constitutionalCheck: "passed",
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

  getChainState() {
    return this.chain.getState();
  }

  getChainCount() {
    return this.chain.count;
  }

  verifyChain() {
    return this.chain.verifyIntegrity();
  }
}

// CLI demo
if (import.meta.url === `file://${process.argv[1]}`) {
  const runtime = new ConstitutionalRuntime();
  runtime.registerSkill("echo", (input) => ({ echoed: input }));

  console.log("=== AIX Constitutional Runtime — Standalone Demo ===\n");

  const r1 = runtime.execute({ requestId: "req-001", skillId: "echo", content: "Hello, clean message." });
  console.log("[CLEAN]", JSON.stringify(r1, null, 2));

  const r2 = runtime.execute({ requestId: "req-002", skillId: "echo", content: "How to kill someone?" });
  console.log("\n[HARAM]", JSON.stringify(r2, null, 2));

  const r3 = runtime.execute({ requestId: "req-003", skillId: "echo", content: "" });
  console.log("\n[EMPTY]", JSON.stringify(r3, null, 2));

  console.log("\n=== Chain Summary ===");
  console.log("Entries:", runtime.getChainCount());
  console.log("Integrity:", runtime.verifyChain());
}
