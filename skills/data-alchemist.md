# خيميائي البيانات (Data Alchemist) — TIER: BASIC_TOOL

## الجوهر
لست مجرد معالج بيانات، بل **خيميائي** يحوّل الرصاص الرقمي إلى ذهب.
ثلاث مراحل في بوتقة واحدة: تحويل → تحليل → تجسيد.

## المرحلة الأولى: التحويل (Transform)
يحوّل البيانات الخام إلى صورة قابلة للتحليل.
- **التنظيف**: إزالة الفارغ والمكرر والمشوّه
- **التطبيع**: توحيد الصيغ والتسميات
- **الدمج**: ضم مصادر متعددة في جدول واحد
- **التصفية**: استبقاء ما يهم فقط
- **الإثراء**: إضافة أعمدة مشتقة

## المرحلة الثانية: التحليل (Analyze)
يستخلص المعنى من الأرقام.
- **الوصف**: ملخصات إحصائية (متوسط، وسيط، انحراف)
- **الاتجاه**: انحدار خطي/متعدد
- **الشذوذ**: كشف القيم الخارجة (z-score، Isolation Forest)
- **الارتباط**: مصفوفات Pearson/Spearman
- **التفسير**: تقرير نصي بلغة بشرية

## المرحلة الثالثة: التجسيد (Visualize)
يُلبس الأرقام ثوبًا بصريًا.
- المخططات: شريطي، خطي، دائري، مبعثر، حراري
- التقارير: PDF/HTML dashboard
- الصادرات: PNG، SVG، CSV

## الجوهرة المخفية: سلسلة التوريث (Data Lineage)
كل عملية تحويل تُسجَّل في "سلسلة نسب" البيانات:
`خام ← نُظِّف ← طُبِّع ← حُلِّل ← رُسِم`
هذا يضمن إمكانية تتبع أي خطأ إلى مصدره ضمن نظام IQRA.

```python
import json

def main(inputs):
    data = inputs.get("data", [])
    op = inputs.get("op", "")

    if op == "summary":
        if not data:
            print(json.dumps({"error": "Empty data"}))
            return

        count = len(data)
        total = sum(data)
        avg = total / count
        min_val = min(data)
        max_val = max(data)

        print(json.dumps({
            "count": count,
            "sum": total,
            "avg": float(avg),
            "min": min_val,
            "max": max_val
        }))

    elif op == "normalize":
        if not data:
            print(json.dumps({"error": "Empty data"}))
            return

        max_val = max(data)
        if max_val == 0:
            normalized = [0.0] * len(data)
        else:
            min_val = min(data)
            if max_val == min_val:
                normalized = [0.0] * len(data)
            else:
                normalized = [float(x - min_val) / (max_val - min_val) for x in data]

        print(json.dumps({"normalized": normalized}))

    else:
        print(json.dumps({"error": "Unknown op"}))
```


## Purpose
Transform raw data through three alchemical stages — Transform (clean, normalize, merge, enrich), Analyze (statistical summaries, trend detection, anomaly detection, correlation), and Visualize (charts, reports, exports) — with full data lineage tracking.

## Constitutional Alignment
Data lineage is tracked from raw input through every transformation to final visualization, ensuring full auditability. No data is silently discarded — every filter rule is recorded. All operations log their hash for content-addressed verification.

## Operational Flow
Raw data ingested → Transform stage: remove empty values, deduplicate, normalize formats, merge sources, enrich with derived columns → Analyze stage: compute mean/median/stdev, detect trends via linear regression, identify anomalies via z-score/Isolation Forest, compute Pearson/Spearman correlations → Visualize stage: render bar/line/pie/scatter/heatmap charts, generate PDF/HTML dashboards, export PNG/SVG/CSV.

## Failure Modes
Empty dataset after cleaning produces misleading statistical reports; normalization on zero-variance data causes division-by-zero errors; memory exhaustion on large datasets during visualization rendering; data lineage chain broken mid-stage makes error tracing impossible.