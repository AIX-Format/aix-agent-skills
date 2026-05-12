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
  score: number; // 0–100
  flags: PurityFlag[];
  recommendation: "allow" | "warn" | "block" | "escalate";
  timestamp: string;
  durationMs: number;
}

export type FilterLayer = "intent" | "source" | "impact" | "context" | "timing";

// ─── HARAM_LIST — المحظورات المطلقة ──────────────────────────────────────────
interface HaramRule {
  id: string;
  label: string;
  severity: "absolute";
  patterns: RegExp[];
}

const HARAM_PATTERNS: HaramRule[] = [
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
      /how\s+.*(kill|harm|hurt|attack|bomb|poison)\s+(someone|people|person)/i,
      /كيف\s+.*(أقتل|أضر|أؤذي|أهاجم)/i,
    ],
  },
  {
    id: "corruption",
    label: "الإفساد",
    severity: "absolute",
    patterns: [
      /hack\s+.*(bank|hospital|government|election)/i,
      /bypass\s+.*(security|auth|firewall)/i,
      /اخترق|تلاعب بـ|أفسد/i,
    ],
  },
  {
    id: "assist_oppressor",
    label: "معاونة الظالم",
    severity: "absolute",
    patterns: [
      /stalk|surveil\s+.*without\s+consent|track\s+.*location\s+secretly/i,
      /تتبع\s+.*دون\s+إذن|مراقبة\s+.*سرية/i,
    ],
  },
];

// ─── WARN_PATTERNS ───────────────────────────────────────────────────────────
interface WarnRule {
  layer: FilterLayer;
  severity: "low" | "medium" | "high";
  reason: string;
  patterns: RegExp[];
}

const WARN_PATTERNS: WarnRule[] = [
  {
    layer: "intent",
    severity: "medium",
    reason: "محتوى مُضلِّل محتمل",
    patterns: [/write\s+.*fake\s+review|generate\s+.*spam|create\s+.*phishing/i],
  },
  {
    layer: "impact",
    severity: "high",
    reason: "طلب ذو أثر واسع يستوجب مراجعة",
    patterns: [/send\s+.*to\s+all|broadcast\s+.*to\s+everyone|mass\s+message|send\s+.*to\s+everyone/i],
  },
  {
    layer: "context",
    severity: "low",
    reason: "محتوى خارج السياق المعتاد",
    patterns: [/ignore\s+.*previous\s+instructions|forget\s+.*rules/i],
  },
];

// ─── Core Logic ──────────────────────────────────────────────────────────────

function runIntentFilter(content: string): PurityFlag[] {
  const flags: PurityFlag[] = [];

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

function calculateScore(flags: PurityFlag[]): number {
  if (flags.some((f) => f.severity === "absolute")) return 0;

  const deductions: Record<string, number> = { high: 40, medium: 20, low: 10 };
  const total = flags.reduce((acc, f) => acc + (deductions[f.severity] ?? 0), 0);
  return Math.max(0, 100 - total);
}

function resolveRecommendation(
  score: number,
  flags: PurityFlag[]
): PurityFilterResult["recommendation"] {
  if (flags.some((f) => f.severity === "absolute")) return "block";
  if (flags.some((f) => f.severity === "high")) return "escalate";
  if (score < 40) return "escalate";
  if (score < 100) return "warn";
  return "allow";
}

// ─── Public API ──────────────────────────────────────────────────────────────

export function runPurityFilter(input: PurityFilterInput): PurityFilterResult {
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
    passed: (recommendation === "allow" || recommendation === "warn"),
    score,
    flags,
    recommendation,
    timestamp: new Date().toISOString(),
    durationMs: Math.round(performance.now() - start),
  };
}
