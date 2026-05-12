/**
 * purity-filter.ts
 * TIER: ADVANCED_INFRASTRUCTURE
 * Constitutional middleware — executes BEFORE any skill.
 * Deterministic, zero external deps, observable.
 */
const HARAM_PATTERNS = [
    {
        id: "lying",
        label: "الكذب والتضليل",
        severity: "absolute",
        patterns: [
            /fabricat|falsif|deceiv|manipulat|spread\.false/i,
            /اكذب|ضلل|زيف|خادع/i,
        ],
    },
    {
        id: "harm_innocents",
        label: "إيذاء البريء",
        severity: "absolute",
        patterns: [
            /how\.(kill|harm|hurt|attack|bomb|poison)\s+(someone|people|person)/i,
            /كيف\.(أقتل|أضر|أؤذي|أهاجم)/i,
        ],
    },
    {
        id: "corruption",
        label: "الإفساد",
        severity: "absolute",
        patterns: [
            /hack\.(?:bank|hospital|government|election)/i,
            /bypass\.*(?:security|auth|firewall)/i,
            /اخترق|تلاعب بـ|أفسد/i,
        ],
    },
    {
        id: "assist_oppressor",
        label: "معاونة الظالم",
        severity: "absolute",
        patterns: [
            /stalk|surveil\.*without\.*consent|track\.*location\.*secretly/i,
            /تتبع\.*دون\.*إذن|مراقبة\.*سرية/i,
        ],
    },
];
const WARN_PATTERNS = [
    {
        layer: "intent",
        severity: "medium",
        reason: "محتوى مُضلِّل محتمل",
        patterns: [/write\.*fake\.*review|generate\.*spam|create\.*phishing/i],
    },
    {
        layer: "impact",
        severity: "high",
        reason: "طلب ذو أثر واسع يستوجب مراجعة",
        patterns: [/send\.*to\.*all|broadcast\.*to\.*everyone|mass\.*message/i],
    },
    {
        layer: "context",
        severity: "low",
        reason: "محتوى خارج السياق المعتاد",
        patterns: [/ignore\.*previous\.*instructions|forget\.*rules/i],
    },
];
// ─── Core Logic ──────────────────────────────────────────────────────────────
function runIntentFilter(content) {
    const flags = [];
    for (const haram of HARAM_PATTERNS) {
        for (const pattern of haram.patterns) {
            const match = content.match(pattern);
            if (match) {
                flags.push({
                    layer: "intent",
                    severity: "absolute",
                    reason: haram.label,
                    matched: match[0],
                });
                break;
            }
        }
    }
    for (const warn of WARN_PATTERNS) {
        for (const pattern of warn.patterns) {
            const match = content.match(pattern);
            if (match) {
                flags.push({
                    layer: warn.layer,
                    severity: warn.severity,
                    reason: warn.reason,
                    matched: match[0],
                });
                break;
            }
        }
    }
    return flags;
}
function calculateScore(flags) {
    if (flags.some((f) => f.severity === "absolute"))
        return 0;
    const deductions = { high: 40, medium: 20, low: 10 };
    const total = flags.reduce((acc, f) => acc + (deductions[f.severity] ?? 0), 0);
    return Math.max(0, 100 - total);
}
function resolveRecommendation(score, flags) {
    if (flags.some((f) => f.severity === "absolute"))
        return "block";
    if (score < 40)
        return "escalate";
    if (score < 70)
        return "warn";
    return "allow";
}
// ─── Public API ──────────────────────────────────────────────────────────────
export function runPurityFilter(input) {
    const start = performance.now();
    if (!input.content || input.content.trim().length === 0) {
        return {
            requestId: input.requestId,
            passed: false,
            score: 0,
            flags: [
                {
                    layer: "intent",
                    severity: "high",
                    reason: "المحتوى فارغ — لا يمكن التحقق",
                },
            ],
            recommendation: "block",
            timestamp: new Date().toISOString(),
            durationMs: Math.round(performance.now() - start),
        };
    }
    const flags = runIntentFilter(input.content);
    const score = calculateScore(flags);
    const recommendation = resolveRecommendation(score, flags);
    return {
        requestId: input.requestId,
        passed: recommendation === "allow" || recommendation === "warn",
        score,
        flags,
        recommendation,
        timestamp: new Date().toISOString(),
        durationMs: Math.round(performance.now() - start),
    };
}
