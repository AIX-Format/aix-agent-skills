# موزع النوايا (Intent Dispatcher), TIER: ADVANCED_TOOL

## الجوهر
يأخذ هدف المستخدم المعبر عنه بلغة طبيعية ويربطه بالطوبولوجيا المناسبة (سلسلة مهارات) من متجر مسارات IQRA. يسد الفجوة بين "أريد أن أفعل X" و "إليك المهارات والمسار الدقيق الذي تحتاجه".

## متى يتم التفعيل؟
- عندما يصف المستخدم هدفًا دون تحديد مهارات معينة (مثل: "كيف أقوم بـ X؟").
- عند الحاجة لاكتشاف المهارات (Skill Discovery).

## آلية العمل (4 خطوات)
1. **تحليل النية (Parse Intent)**: استخراج الهدف ككائن مهيكل (النطاق، صيغة المدخلات/المخرجات، العمليات).
2. **الرسم المجرد (Abstract Workflow)**: تحويل النية إلى رسم بياني مجرد للعمليات (مثل `[ابتلاع] ← [تحليل] ← [تصوير]`).
3. **البحث في المسارات**: البحث في `pipeline-store` وتصنيف النتائج (بناءً على تطابق الهيكل والقدرات بنسبة مئوية).
4. **التوصية أو التكوين**: تقديم المسارات الجاهزة للتثبيت، أو اقتراح تجميع مسار جديد (`pipeline.yaml`) إذا لم يوجد مسار يحقق نسبة >60%.

## حلقة التعلم (Learning Loop)
يتحسن الموزع بمرور الوقت عبر تسجيل النتائج في `.idx/dispatcher-history.jsonl`:
- رفع تقييم المسارات المقبولة مسبقًا.
- خفض تقييم المسارات المرفوضة.

## تكامل مع المهارات الأخرى
- `pipeline-store`: المصدر الأساسي للمسارات الجاهزة.
- `skill-evaluator`: لا يقترح إلا المهارات أو المسارات الموثوقة.
- `version-guard`: التحقق من التوافق قبل التوصية.


## Purpose

`intent-dispatcher` converts a natural-language goal into a concrete
pipeline recommendation. It is the answer to "the user said something
fuzzy, which marketplace skills should we wire up". It returns either a
ranked list of pre-built pipelines from `pipeline-store` or, when no
candidate scores above the 60% threshold, a freshly composed
`pipeline.yaml` for `mission-control` to validate.

This skill is the entry point for skill discovery. Without it, every
runtime would have to hardcode the mapping from intent to topology.

## Constitutional Alignment

The dispatcher never recommends a skill that is not present in
`skills.json` and whose entry has not been signed against `trust-chain`.
It calls `version-guard` for compatibility before promoting a candidate
pipeline, so a recommendation cannot land that depends on a deprecated
skill version. The learning loop in `.idx/dispatcher-history.jsonl`
records both accepted and rejected recommendations, which prevents the
ranker from drifting toward whatever it last produced. Together these
constraints keep recommendations grounded in the catalogue rather than
in the model's prior.

## Operational Flow

1. **Parse intent**. Extract a structured Intent object from the
   user's natural-language goal: domain, input shape, output shape,
   operations, and any explicit constraints.
2. **Build abstract workflow**. Convert the Intent into an abstract
   operation graph, for example `[ingest] -> [analyze] -> [visualize]`,
   without binding to specific skills yet.
3. **Search pipeline-store**. Match the abstract workflow against
   pre-built pipelines. Score by structural similarity and capability
   coverage; produce a ranked list with percentage match.
4. **Threshold**. If the top candidate scores above 60% and all its
   skills are currently registered and `version-guard` compatible, emit
   it as the recommendation. If nothing scores above 60%, hand off to
   the composition path.
5. **Compose** (only when no candidate clears 60%). Synthesise a
   `pipeline.yaml` by binding each abstract operation to the
   highest-rated marketplace skill that satisfies the operation's
   contract. Return the synthesised pipeline with confidence and
   provenance.
6. **Record outcome**. Whether the recommendation was accepted or
   rejected by the caller, append the result to the history file so
   the ranker improves over time.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Intent is ambiguous (multiple valid interpretations) | Confidence below threshold across all candidates | Return all interpretations with their scores; do not auto-pick |
| Every candidate scores below 60% and composition fails | Both pipeline-store search and composition exhausted | Return `no_pipeline_found` with the abstract workflow attached, so the caller can ask the user for clarification |
| Recommended skill becomes unavailable between dispatch and execution | Re-check at the `mission-control` validation stage; not in this skill | Surface to `mission-control` for re-dispatch |
| History file corruption or drift | Learning loop produces oscillating recommendations | Quarantine the history file, rebuild from `trust-chain`, recompute rankings |
| Caller bypasses the dispatcher and hardcodes a topology | Out of scope here but visible in `trust-chain` analytics | Surface as an anti-pattern in operator dashboards; do not block, the dispatcher is advisory |

## References

- The four-step intent-to-pipeline pattern documented in the Arabic narrative above is consistent with the supervisor architecture in LangGraph, where a router agent maps user goals to a downstream worker chain.
- `pipeline-store` (separate skill) is the persistence layer this dispatcher reads from.