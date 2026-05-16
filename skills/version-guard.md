# حارس الإصدارات (Version Guard) — TIER: ADVANCED_INFRASTRUCTURE

## الجوهر
يفرض توافقية الإصدارات الدلالية (SemVer) بين مهارات IQRA. عندما يتم تحديث مهارة ما، يتم فحص جميع المعتمدين عليها لتجنب الانهيارات الصامتة (Silent Breakage).

## متى يتم التفعيل؟
- عند تحديث مهارة أو نشرها.
- عند التحقق من التوافقيات (Compatibility Check) وتأثير التغييرات الجذرية (Breaking Changes).
- قبل دمج طلب سحب (PR) لمهارة.

## مفاهيم أساسية
### واجهة المنافذ (Public Ports)
العقد الذي توفره المهارة للبيئة:
```yaml
ports:
  inputs:
    - name: query
      type: string
      required: true
  outputs:
    - name: results
      type: array<SearchResult>
```

### التغييرات الجذرية (Breaking Changes - MAJOR bump)
- إزالة مُدخل أو مُخرج.
- تغيير نوع المتغير (مثال: `string` إلى `object`).
- تحويل مُدخل من اختياري إلى إجباري.

## آلية الحماية
1. استخراج منافذ الإصدار القديم والجديد.
2. مقارنة المنافذ (`scripts/diff_ports.py`).
3. تصنيف التغييرات (جذري/متوافق).
4. تحليل الأثر على المهارات المعتمدة من خلال `.idx/dependency-graph.json`.
5. التوصية برفع الإصدار (Major/Minor/Patch).

## تكامل مع المهارات الأخرى
- `skill-evaluator`: يُعاد تشغيل التقييم بعد أي تحديث إصدار.
- `pipeline-store`: يقفل (Locks) الإصدارات المتوافقة عند التثبيت.
- `chain-tracer`: يستخدم التتبعات لمعرفة المنافذ التي تُستهلك فعلياً.


## Purpose

Enforce semantic versioning (SemVer) compatibility across all IQRA skills and pipelines. When a skill is updated, Version Guard scans the dependency impact graph to detect breaking changes — comparing public port interfaces (inputs/outputs) between old and new versions. It then recommends the correct version bump (Major/Minor/Patch) and blocks installations that would introduce incompatible skill combinations.

## Constitutional Alignment

- **No Silent Breakage**: Any skill update that breaks downstream dependents must be flagged before merge — never deployed silently.
- **Public Port Contract**: The declared ports (`inputs`/`outputs`) are the only interface that matters — internal changes are not considered breaking.
- **Dependency Transparency**: The full dependency graph is published in `.idx/dependency-graph.json` — any dependent can inspect their exposure.
- **Block on Conflict**: Pipelines with conflicting version requirements are rejected at install time — users are never left with a broken runtime.

## Operational Flow

1. A skill update PR is submitted with old and new `pipeline.yaml` port definitions.
2. Skill runs `scripts/diff_ports.py` to compare old vs. new ports — detects added, removed, or type-changed ports.
3. Classifies changes: removed port or type narrowing = breaking (Major), new optional port = minor, internal refactor = patch.
4. Loads `.idx/dependency-graph.json` to find all skills and pipelines that depend on this skill.
5. For each dependent, evaluates whether the change is compatible with their declared version range.
6. Outputs a compatibility report: `{ recommendedBump, affectedDependents: [{ skillId, compatible }] }`.
7. If any dependent is broken, the PR is blocked with the report attached.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Dependency graph unavailable | `.idx/dependency-graph.json` not found | Rebuild graph by scanning all skill manifests |
| Port diff tool error | `diff_ports.py` crashes | Fallback to manual port declaration comparison |
| Ambiguous version range (e.g. `^1.2.3` with no upper bound) | Range parser ambiguity | Flag for human review, do not auto-approve |
| Circular dependency in graph | Cycle detection algorithm | Report cycle path, block the update |