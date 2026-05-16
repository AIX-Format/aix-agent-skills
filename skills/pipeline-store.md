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


## Purpose

Registry of pre-assembled DAG topology graphs (pipelines) that users can discover, install, and execute as single units within IQRA. Each pipeline chains multiple skills together with defined data-flow edges — enabling complex multi-step workflows (e.g. CSV upload → transform → analyze → visualize) to be deployed with one command.

## Constitutional Alignment

- **No Circular Dependencies**: All pipelines must be valid DAGs — cycles are rejected at install time.
- **Skill Integrity**: Every skill node in a pipeline must have passed `skill-evaluator` before the pipeline is listed.
- **Version-Locked**: Pipelines are installed with pinned versions via `version-guard` — silent breaking changes are prevented.
- **Transparent Flow**: The pipeline manifest must document every node, edge, and data transformation — no hidden side effects.

## Operational Flow

1. User searches for a pipeline via `pipeline_store.search(query)` or `intent-dispatcher` suggests one.
2. Pipeline manifest `pipeline.yaml` is fetched and validated (no cycles, all skills exist, versions compatible).
3. `version-guard` locks all skill version ranges to compatible releases.
4. User installs via `scripts/install_pipeline.py` — all constituent skills are fetched.
5. On execution, `chain-tracer` monitors every node's input/output for debugging.
6. Results flow through the DAG edges to produce the final output.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Circular dependency in manifest | Graph cycle detection | Reject install, report the cycle path |
| Missing required skill | Dependency check fails | List missing skills, abort install |
| Version conflict (incompatible skill semver) | `version-guard` rejects | Report conflict, suggest compatible alternatives |
| Node execution failure mid-pipeline | `chain-tracer` detects error | Halt pipeline, return partial-results with error node ID |