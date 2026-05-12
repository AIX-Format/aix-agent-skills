/**
 * IQRA Filter — المصفاة (Legacy)
 *
 * "فَأَمَّا الزَّبَدُ فَيَذْهَبُ جُفَاءً ۖ وَأَمَّا مَا يَنفَعُ النَّاسَ فَيَمْكُثُ فِي الْأَرْضِ" — الرعد: 17
 *
 * Filters memory and input according to Fitrah and Dastūr.
 */
import fs from 'fs';
import path from 'path';
// Standalone Logger for AIX
const Logger = {
    info: (msg) => console.log(`🛡️ IQRA Filter: ${msg}`),
    error: (msg, err) => console.error(`❌ IQRA Filter: ${msg}`, err),
};
export class IQRAFilter {
    // Paths updated to be more generic or configurable
    static DASTUR_PATH = path.join(process.cwd(), 'iqra-core/DASTŪR.md');
    static FITRAH_PATH = path.join(process.cwd(), 'iqra-core/FITRAH.md');
    static FAILURES_PATH = path.join(process.cwd(), 'iqra-core/FAILURES.md');
    static haramKeywords = [];
    static fitrahKeywords = [];
    static escapeRegExp(value) {
        return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    static matchesWord(text, keyword) {
        const escaped = this.escapeRegExp(keyword);
        const regex = new RegExp(`(?<!\\p{L})${escaped}(?!\\p{L})`, 'iu');
        return regex.test(text);
    }
    static parseHaramKeywords(content) {
        const haramMatch = content.match(/HARAM_LIST\s*=\s*\[(.*?)\]/s);
        if (!haramMatch)
            return [];
        const candidates = haramMatch[1]
            .split(/,(?![^\[]*\])/)
            .map((item) => item.replace(/["'\[\]]/g, '').trim())
            .filter((item) => item.length > 0);
        const keywords = new Set();
        for (const candidate of candidates) {
            keywords.add(candidate);
            const parts = candidate.split(/\s+و?\s*/).map((part) => part.trim()).filter(Boolean);
            for (const part of parts) {
                if (part.length > 2)
                    keywords.add(part);
            }
        }
        return [...keywords];
    }
    /**
     * Load principles from .md files
     */
    static initialize() {
        try {
            const dasturContent = fs.existsSync(this.DASTUR_PATH) ? fs.readFileSync(this.DASTUR_PATH, 'utf8') : '';
            const fitrahContent = fs.existsSync(this.FITRAH_PATH) ? fs.readFileSync(this.FITRAH_PATH, 'utf8') : '';
            this.haramKeywords = this.parseHaramKeywords(dasturContent);
            this.fitrahKeywords = ['الحق', 'خدمة', 'القرآن', 'السنة', 'المراقبة', 'التطور', 'الإحسان', 'إتقان'];
            if (fitrahContent) {
                const fitrahExtracted = Array.from(new Set((fitrahContent.match(/[\u0600-\u06FF]{3,}/gu) || [])
                    .map((word) => word.trim())
                    .filter((word) => word.length > 2)));
                this.fitrahKeywords = Array.from(new Set([...this.fitrahKeywords, ...fitrahExtracted]));
            }
            Logger.info(`Initialized with ${this.haramKeywords.length} constraints.`);
        }
        catch (error) {
            Logger.error('Initialization failed:', error);
            this.haramKeywords = ['كذب', 'ظلم', 'خيانة', 'إيذاء'];
        }
    }
    /**
     * Log failure to FAILURES.md
     */
    static async logFailure(text, reason) {
        const timestamp = new Date().toISOString();
        const entry = `\n### 🚫 Pollution Event | ${timestamp}\n**Reason:** ${reason}\n**Content Snippet:** "${text.substring(0, 100)}..."\n---\n`;
        try {
            // Create directory if missing
            const dir = path.dirname(this.FAILURES_PATH);
            if (!fs.existsSync(dir))
                fs.mkdirSync(dir, { recursive: true });
            fs.appendFileSync(this.FAILURES_PATH, entry);
        }
        catch (err) {
            Logger.error('Failed to write to FAILURES.md', err);
        }
    }
    /**
     * Validate a piece of content against the Dastūr
     */
    static async validate(text) {
        if (this.haramKeywords.length === 0)
            this.initialize();
        // 1. Check for Haram content (Hard Veto)
        for (const keyword of this.haramKeywords) {
            if (this.matchesWord(text, keyword)) {
                const result = {
                    isAllowed: false,
                    reason: `Violates Dastūr: Found forbidden concept '${keyword}'`,
                    score: 0
                };
                await this.logFailure(text, result.reason);
                return result;
            }
        }
        // 2. Check for Fitrah Alignment (Soft Score)
        let matches = 0;
        for (const val of this.fitrahKeywords) {
            if (this.matchesWord(text, val)) {
                matches++;
            }
        }
        const score = Math.min(1.0, (matches / (this.fitrahKeywords.length / 2)));
        const normalizedText = text.trim();
        // Only block very short content with no alignment score
        const isMostlyNoise = normalizedText.length < 5 && score < 0.1;
        if (isMostlyNoise) {
            return {
                isAllowed: false,
                reason: 'Content too sparse (Zabad).',
                score: score
            };
        }
        return {
            isAllowed: true,
            score: score
        };
    }
}
