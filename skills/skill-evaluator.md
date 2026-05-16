---
name: skill-evaluator
description: "Run automated evaluations against any skill and produce verifiable pass/fail badges with scores (0-100). Use this skill whenever you need to test, benchmark, or validate a skill's quality."
---

# مقيّم المهارات (Skill Evaluator) — TIER: PRO

## الجوهر
يقوم بتمرير كل مهارة عبر مجموعة اختبارات تقييم صارمة (بنية الاختبارات التلقائية لـ IQRA المستلهمة من promptfoo)، ويخزن النتيجة كـ "شارة" موثوقة بجانب المهارة.

## متى يتم تفعيل هذه المهارة
- عندما يريد المستخدم اختبار أو تقييم مهارة.
- عندما يُذكر "جودة المهارة"، "معيار"، "اختبار المهارات"، "درجة التقييم".
- لمقارنة إصدارات المهارات أو التحقق من اجتيازها لمعايير الجودة.
- لإنشاء شارات ثقة (Trust Badges) أو بطاقات أداء (Score Cards) لإدراجات المهارات.
- كخطوة تحقق في التكامل المستمر (CI/pre-merge) قبل اعتماد المهارات.

## سير العمل (The 4-Stage Pipeline)

### المرحلة الأولى: استكشاف المهارة
يتم تحديد المهارة وقراءة ملفاتها المعمارية. يستخرج التقييم:
- اسم وإصدار المهارة.
- المدخلات والمخرجات المعلنة.
- التبعيات المذكورة.

### المرحلة الثانية: بناء حزمة الاختبار (Test Suite)
تتم صياغة حزمة اختبار مخصصة:
1. **تحديد النماذج (Providers)**: عبر `model-council`.
2. **حالات الاختبار**: مبنية على وصف المهارة وقدراتها.
3. **التأكيدات (Assertions)**:
   - التطابق الهيكلي (Regex).
   - الكلمات المفتاحية (Contains).
   - الجودة المحكومة بنموذج آخر (LLM-rubric عبر `cross-model-judge`).

### المرحلة الثالثة: تشغيل التقييم
يتم استدعاء المهارة في بيئة معزولة (`skill-sandbox`):
1. تُحمّل المهارة في النموذج.
2. تُشغل كل حالة اختبار 3 مرات لضمان الموثوقية الإحصائية.
3. تُلتقط بيانات الأداء (زمن الاستجابة، عدد الرموز).
4. تُحسب درجة تقييم لكل اختبار (نجاح/فشل/جزئي) وتجمع لدرجة نهائية (0-100).

### المرحلة الرابعة: توليد الشارة والتقرير
بعد التقييم، يتم توليد:
1. **ملف JSON للدرجة**: يُحفظ في `.idx/evaluations/{skill_id}/{version}.json` ويحتوي على كل مقاييس الأداء.
2. **الشارة (Badge)**: شارة بصرية توضع في ملف الـ Markdown الخاص بالمهارة (مثال: `eval-pass-87/100-brightgreen`).

## معايير التقييم
| البعد | الوزن | الوصف |
|---|---|---|
| **الدقة (Correctness)** | 30% | تطابق المخرجات مع النتيجة المتوقعة |
| **الشمولية (Completeness)** | 20% | وجود جميع العناصر المطلوبة |
| **التنسيق (Format)** | 15% | التزام المخرجات بالتنسيق المعلن |
| **الصلابة (Robustness)** | 20% | القدرة على التعامل مع الحالات الشاذة والمدخلات الخاطئة |
| **الكفاءة (Efficiency)** | 15% | استهلاك الرموز وزمن الاستجابة ضمن الحدود |

## إعادة التقييم
- تُعاد التقييمات تلقائيًا عند تحديث وصف المهارة أو تبعياتها (عبر `version-guard`).

## تكامل مع المهارات الأخرى
- `version-guard`: يضمن تشغيل المقيّم قبل أي تحديث في الإصدار.
- `skill-sandbox`: بيئة العزل التي يُشغل فيها التقييم.
- `pipeline-store`: يتطلب أن تكون جميع المهارات المكونة للمسار حاصلة على شارة اجتياز.


## Purpose

Run automated 4-stage evaluations against any skill — explore its architecture, build a tailored test suite, execute in the sandbox with statistical rigor, and generate a verifiable pass/fail badge with a score (0–100). Serves as the quality gate for the IQRA marketplace: no skill enters the registry without an evaluation badge, and no pipeline is installed unless all its constituent skills have passing scores.

## Constitutional Alignment

- **Objective Scoring**: Evaluation criteria are weighted and transparent (correctness 30%, completeness 20%, format 15%, robustness 20%, efficiency 15%) — no hidden or biased metrics.
- **Statistical Rigor**: Every test case runs 3 times to ensure reproducibility — no single-run flukes.
- **Cross-Model Validation**: LLM-rubric assertions use `cross-model-judge` to avoid self-evaluation bias.
- **Re-Evaluation on Change**: Any skill update automatically triggers re-evaluation — stale badges are invalidated.
- **Public Badges**: Scores are stamped into the skill's markdown — users can see historical scores and trends.

## Operational Flow

1. Phase 1 — Explore: Read skill manifest and extract metadata (name, version, inputs, outputs, dependencies).
2. Phase 2 — Build: Construct a test suite with 5–15 test cases covering normal, edge, and adversarial inputs. Assertions use regex, keyword containment, and LLM-rubric via `cross-model-judge`.
3. Phase 3 — Execute: Load skill into `skill-sandbox`, run each test case 3 times, capture latency and token usage.
4. Phase 4 — Badge: Aggregate scores across dimensions, compute final weighted score, and write badge into the skill's markdown (e.g. `eval-pass-87/100-brightgreen`).
5. Persist the detailed evaluation report to `.idx/evaluations/{skill_id}/{version}.json`.
6. Notify `version-guard` and `pipeline-store` of the new evaluation result.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Sandbox unavailable | Connection refused on Phase 3 | Queue evaluation, retry with exponential backoff |
| No test cases could be generated | Skill description too vague | Return error requesting more detailed skill spec |
| Assertion framework inconsistent | Cross-model judge disagrees with self | Use majority-vote across 3 models |
| Score deviates wildly from previous version | Δ > 30 points triggers alert | Flag for human review, do not auto-publish badge |