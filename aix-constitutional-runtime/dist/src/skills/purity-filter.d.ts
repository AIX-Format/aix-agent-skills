/**
 * purity-filter.ts
 * TIER: ADVANCED_INFRASTRUCTURE
 * Constitutional middleware — executes BEFORE any skill.
 * Deterministic, zero external deps, observable.
 */
export interface PurityFilterInput {
    requestId: string;
    content: string;
    source?: string;
    context?: string;
}
export interface PurityFlag {
    layer: FilterLayer;
    severity: "low" | "medium" | "high" | "absolute";
    reason: string;
    matched?: string;
}
export interface PurityFilterResult {
    requestId: string;
    passed: boolean;
    score: number;
    flags: PurityFlag[];
    recommendation: "allow" | "warn" | "block" | "escalate";
    timestamp: string;
    durationMs: number;
}
export type FilterLayer = "intent" | "source" | "impact" | "context" | "timing";
export declare function runPurityFilter(input: PurityFilterInput): PurityFilterResult;
