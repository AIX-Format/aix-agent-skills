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
import { type PurityFilterResult } from "../skills/purity-filter.js";
import { type TrustChainState } from "../skills/trust-chain.js";
export interface RuntimeRequest {
    requestId: string;
    skillId: string;
    content: string;
    source?: string;
    context?: string;
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
export declare class ConstitutionalRuntime {
    private chain;
    private executors;
    constructor(initialChainState?: TrustChainState);
    registerSkill(skillId: string, executor: SkillExecutor): void;
    execute(req: RuntimeRequest): RuntimeResponse;
    getChainCount(): number;
    getChainState(): TrustChainState;
    verifyChain(): {
        valid: boolean;
        brokenAt?: string;
    };
}
