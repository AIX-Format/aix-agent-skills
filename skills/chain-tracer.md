# متتبع السلاسل (Chain Tracer) — TIER: PRO

## الجوهر
يوفر تتبعاً (Observability) كاملاً لتنفيذ مسارات المهارات (Pipelines) في IQRA: التوقيت، استهلاك الرموز (Tokens)، الأخطاء، وسلسلة نسب البيانات (Data Lineage).

## متى يتم التفعيل؟
- عند تنقيح الأخطاء (Debugging) لسلسلة مهارات.
- لتحليل الأداء واستهلاك التكلفة والرموز (Token tracking).
- لفهم تدفق البيانات عبر السلسلة.

## بنية التتبع (Trace Structure)
التتبع هو سجل كامل للتنفيذ. يحتوي على فترات (Spans) — فترة لكل مهارة.
```json
{
  "span_id": "span-002",
  "skill_id": "data-alchemist",
  "input_hash": "sha256:abc...",
  "output_hash": "sha256:def...",
  "duration_ms": 8400,
  "token_count": { "total": 45000 },
  "cost_usd": 0.09,
  "status": "success"
}
```

## سلسلة نسب البيانات (Data Lineage)
يتم تسجيل تجزئة (Hashes) المدخلات والمخرجات لإنشاء رسم بياني معنون بالمحتوى (Content-addressed graph):
`sales.xlsx (hash:aaa) → [xlsx] → records.json (hash:bbb) → [analysis]...`
يسمح هذا بإعادة استخدام التخزين المؤقت (Cache) وإعادة التشغيل من أي نقطة.

## تكامل مع المهارات الأخرى
- `pipeline-store`: مراقبة المسارات المشغلة.
- `version-guard`: تزويده ببيانات استخدام المنافذ الفعلية.
- `reward-engine`: يتغذى على التتبعات لتقييم نقاء المسار وكفاءته.


## Purpose
Provide full observability for IQRA pipeline execution — capture timing, token consumption, cost, errors, and data lineage across every skill span, enabling debugging, performance analysis, and content-addressed cache/replay.

## Constitutional Alignment
All pipeline execution traces are immutable records preserved for audit. Input/output hashes create a content-addressed graph that enables verifiable data lineage without exposing raw data content.

## Operational Flow
Pipeline starts → root span created → each skill generates a child span (span_id, skill_id, input_hash, output_hash, duration_ms, token_count, cost_usd, status) → upon completion, spans assembled into complete trace → data lineage graph generated from linked hashes → traces available for debug, cost analysis, and cache reuse.

## Failure Modes
Span data loss during a crash breaks trace integrity; missing token_count fields hide cost overruns until billing; hash collisions (rare) corrupt data lineage linking; pipeline completion before all spans flush produces incomplete traces.