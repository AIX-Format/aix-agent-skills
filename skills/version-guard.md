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
