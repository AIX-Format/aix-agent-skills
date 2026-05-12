# متجر مسارات العمل (Pipeline Store) — TIER: PRO

## الجوهر
سجل للمسارات الطوبولوجية المُجمَّعة مسبقًا (Topology Graphs) والتي يمكن للمستخدمين تثبيتها كوحدة واحدة في بيئة IQRA لحل مشاكل متكاملة بأمر واحد.

## متى يتم التفعيل؟
- عندما يطلب المستخدم دمج عدة مهارات أو يبحث عن سير عمل (Workflow) جاهز.
- عند نشر أو تثبيت سلسلة مهارات (Skill Chain) متكاملة.

## مفاهيم أساسية
المسار (Pipeline) هو رسم بياني موجه (DAG). كل عقدة هي مهارة، وكل حافة تحدد تدفق البيانات:
`تحميل CSV ← تحويل بيانات ← تحليل اتجاه ← رسم خطي`

### بيان المسار (Pipeline Manifest)
كل مسار يُعرّف بملف `pipeline.yaml`:
```yaml
name: sales-dashboard
version: 1.0.0
description: "Transform CSV sales data into a trend dashboard"
nodes:
  - id: upload
    skill: data-alchemist
    version: ">=1.0.0"
  - id: analyze
    skill: resonance-engine
    depends_on: [upload]
```

## دورة حياة المسار
1. **التأليف**: كتابة `pipeline.yaml` محليًا.
2. **التحقق**: التأكد من خلوه من الاعتمادات الدائرية وأن المهارات مجتازة لـ `skill-evaluator`.
3. **النشر**: الإرسال كـ PR لمتجر IQRA.
4. **التثبيت**: تشغيل `scripts/install_pipeline.py`.
5. **التشغيل**: تمرير المدخلات وتتبع الإخراج عبر `chain-tracer`.

## تكامل مع المهارات الأخرى
- `skill-evaluator`: يجب أن تجتاز جميع مكونات المسار التقييم.
- `version-guard`: يقفل (Locks) الإصدارات المتوافقة لتجنب الكسر.
- `intent-dispatcher`: يقترح المسارات الجاهزة بناءً على نية المستخدم.
- `chain-tracer`: يراقب تنفيذ المسار للتصحيح.
