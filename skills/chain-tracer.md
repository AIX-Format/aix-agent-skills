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
