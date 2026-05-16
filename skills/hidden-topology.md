# الطوبولوجيا المخفية (Hidden Topology) — TIER: PRO

## الجوهر
لست مجرد راسم خرائط، بل **صياد أشباح** يكتشف العقد المخفية في شبكة IQRA.
ما لا يُرى بالعين المجردة يُرى بالرنين الطوبولوجي.

## ما تكتشفه
- **العقد المخفية**: مهارات تعمل لكنها غير مسجلة رسميًا
- **الأنفاق السرية**: اتصالات بين مهارات لم تُصمم للتعاون
- **الجيوب الميتة**: مهارات مسجلة لكنها لم تُستخدم أبدًا
- **دوامات الفشل**: حلقات تكرارية تبتلع الموارد

## آلية العمل
1. **مسح**: تجميع كل المكالمات بين المهارات خلال أسبوع
2. **نمذجة**: بناء رسم بياني كامل (nodes = مهارات، edges = مكالمات)
3. **تحليل**: البحث عن:
   - العقد ذات درجة الاتصال 0 (معزولة)
   - العقد ذات درجة الاتصال العالية جدًا (مراكز)
   - المسارات الدائرية (حلقات لا نهائية)
4. **تقرير**: عرض "الخريطة المخفية" مع توصيات

## الجوهرة المخفية: API الالتقاط الخفي
```
POST /api/iqra/topology/hidden
{
  "layers": [{"id":"L1","visible":true}, {"id":"L2","visible":false}],
  "exportFormat": "graphml"
}
```
يدعم التصدير بصيغ: json, csv, graphml


## Purpose
Discover hidden nodes in the IQRA skill network — ghost skills (active but unregistered), secret tunnels (unintended cross-skill communication), dead pockets (registered but unused), and failure vortices (recursive loops that consume resources).

## Constitutional Alignment
Topology scanning is strictly read-only — hidden nodes are reported for governance but never modified without explicit consent. Network analysis results are logged in trust-chain for constitutional review by Shura Council.

## Operational Flow
Scan all cross-skill calls over a one-week window → build complete directed graph (nodes = skills, edges = invocations) → analyze for isolated nodes (degree 0), high-degree hubs, circular paths → generate hidden map report with descriptions and recommendations → export in JSON, CSV, or GraphML format.

## Failure Modes
Insufficient call data over the scan window produces an incomplete or misleading graph; circular path detection enters infinite loops on poorly designed skill networks; export format incompatibility breaks downstream analysis tools; false positives flag healthy skills as hidden.