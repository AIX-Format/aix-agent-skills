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
import { runPurityFilter } from "../skills/purity-filter.js";
import { TrustChain } from "../skills/trust-chain.js";
// ─── Runtime Kernel ──────────────────────────────────────────────────────────
export class ConstitutionalRuntime {
    chain;
    executors = new Map();
    constructor(initialChainState) {
        this.chain = new TrustChain(initialChainState);
    }
    registerSkill(skillId, executor) {
        this.executors.set(skillId, executor);
    }
    execute(req) {
        // ─── 1. Constitutional Middleware ────────────────────────────────────────
        const filterInput = {
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
                output: { score: governance.score, flags: governance.flags.map((f) => f.id ?? f.reason) },
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
        // ─── 3. Skill Execution ──────────────────────────────────────────────────
        let output;
        let executed = false;
        let error;
        const executor = this.executors.get(req.skillId);
        if (executor) {
            try {
                output = executor(req.content);
                executed = true;
            }
            catch (e) {
                error = e instanceof Error ? e.message : String(e);
            }
        }
        else {
            output = { note: "No executor registered — governance passed, skill skipped" };
            executed = true;
        }
        // ─── 4. Trust Chain Append ───────────────────────────────────────────────
        const entry = this.chain.append({
            action: `skill:${req.skillId}:${executed ? "execute" : "error"}`,
            input: { requestId: req.requestId, contentLength: req.content.length },
            output: error ? { error } : { status: "success" },
            constitutionalCheck: executed ? "passed" : "skipped",
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
    getChainCount() {
        return this.chain.getState().entries.length;
    }
    getChainState() {
        return this.chain.getState();
    }
    verifyChain() {
        return this.chain.verifyIntegrity();
    }
}
// ─── CLI / Standalone Demo ───────────────────────────────────────────────────
if (import.meta.url === `file://${process.argv[1]}`) {
    const runtime = new ConstitutionalRuntime();
    // Register a dummy skill
    runtime.registerSkill("echo", (input) => ({ echoed: input }));
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
    console.log("Recent:", runtime.getChainState().entries.slice(-2).map((e) => e.entryId));
}
