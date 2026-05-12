/**
 * trust-chain.ts
 * TIER: PRO
 * Append-only ledger with SHA-256 lineage.
 * Node.js first (crypto.createHash). Browser fallback (SubtleCrypto).
 * Stores hashes/refs, NOT raw sensitive payloads.
 */
export interface TrustEntry {
    entryId: string;
    prevHash: string;
    timestamp: string;
    action: string;
    inputHash: string;
    outputHash: string;
    payloadRef?: string;
    constitutionalCheck: "passed" | "blocked" | "escalated" | "skipped";
    hash: string;
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
}
export declare class TrustChain {
    private state;
    constructor(initialState?: TrustChainState);
    /** إلحاق مدخلة جديدة بالسلسلة */
    append(input: AppendInput): TrustEntry;
    /** التحقق من سلامة السلسلة كاملة */
    verifyIntegrity(): {
        valid: boolean;
        brokenAt?: string;
    };
    /** الحالة الكاملة (للحفظ في Redis / Upstash) */
    getState(): TrustChainState;
    /** آخر N مدخلات */
    getRecent(n?: number): TrustEntry[];
    get count(): number;
}
