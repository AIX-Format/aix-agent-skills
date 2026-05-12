/**
 * 🦴 IQRA Caveman Protocol — "الضغط اللغوي السيادي"
 *
 * Linguistic Compression Skill for IQRA.
 * Reduces token usage by ~60% using terse, high-density patterns.
 *
 * "why use many token when few token do trick"
 */
export declare class CavemanSkill {
    /**
     * 🛡️ Deterministic Shield
     * Filters noisy patterns and system prompt leakage artifacts.
     */
    static deterministicShield(text: string): string;
    /**
     * 💧 Cognitive Rehydration
     * Injects a 'Rehydration Header' to guide local models.
     */
    static rehydratePrompt(compressed: string): string;
    /**
     * Arabic Morphological Root Compression (Experimental)
     * Tries to keep only core roots for maximum density.
     */
    private static extractArabicRoots;
    /**
     * Compresses a prompt into Caveman style.
     * Removes fluff, prepositions, and redundant polite forms.
     * Supports both English and Arabic.
     */
    static compressPrompt(text: string, mode?: 'basic' | 'ultra'): string;
    /**
     * Transforms a response into a more 'Sovereign Brevity' style if requested.
     */
    static sovereignBrevity(text: string): string;
}
