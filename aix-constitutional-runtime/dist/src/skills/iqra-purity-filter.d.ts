/**
 * IQRA Filter — المصفاة (Legacy)
 *
 * "فَأَمَّا الزَّبَدُ فَيَذْهَبُ جُفَاءً ۖ وَأَمَّا مَا يَنفَعُ النَّاسَ فَيَمْكُثُ فِي الْأَرْضِ" — الرعد: 17
 *
 * Filters memory and input according to Fitrah and Dastūr.
 */
export interface FilterResult {
    isAllowed: boolean;
    reason?: string;
    score: number;
}
export declare class IQRAFilter {
    private static DASTUR_PATH;
    private static FITRAH_PATH;
    private static FAILURES_PATH;
    private static haramKeywords;
    private static fitrahKeywords;
    private static escapeRegExp;
    private static matchesWord;
    private static parseHaramKeywords;
    /**
     * Load principles from .md files
     */
    static initialize(): void;
    /**
     * Log failure to FAILURES.md
     */
    private static logFailure;
    /**
     * Validate a piece of content against the Dastūr
     */
    static validate(text: string): Promise<FilterResult>;
}
