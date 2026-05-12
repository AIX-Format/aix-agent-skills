/**
 * Legacy TrustChain Entry — سجل الثقة (النسخة القديمة)
 */
export interface TrustChainEntry {
    timestamp: number;
    action: string;
    inputHash: string;
    outputHash: string;
    auditHash: string;
    safetyScore: number;
    /** النية — من ḤISĀB.md: "النية مهمة أيضاً" */
    intention?: string;
}
/**
 * Append to TrustChain with audit hash verification
 *
 * ḤISĀB.md: "النية مهمة أيضاً" — النية تُسجَّل لتحليل المساءلة
 */
export declare function appendToTrustChain(action: string, input: string, output: string, safetyScore: number, intention?: string): string;
/**
 * Returns the current state of the legacy trust chain
 */
export declare function getLegacyTrustChain(): TrustChainEntry[];
