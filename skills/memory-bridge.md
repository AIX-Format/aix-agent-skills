# جسر الذاكرة (Memory Bridge) — TIER: ADVANCED_INFRASTRUCTURE

## الجوهر
لست مجرد مخزن بيانات، بل **نهر من الوعي** يربط ماضي الوكيل بحاضره.
5 طبقات تتدفق فيها الذكريات من الساخن إلى البارد إلى الأبدي.

## العمارة الخماسية (مستوحاة من IQRA MemoryBridge)
| الطبقة | المخزن | المدة | الدور |
|:---|:---|:---|:---|
| **ساخنة Hot** | RAM (Map) | ساعة | سياق فائق السرعة 7×7 |
| **دافئة Warm** | SQLite | 7 أيام | ذكريات دقيقة وأنماط |
| **باردة Cold** | Redis/JSON | 30 يومًا | تاريخ معرفي |
| **متجهة Vector** | Qdrant | ∞ | رنين دلالي |
| **أرشيف Archive** | LanceDB | ∞ | معرفة طويلة المدى |

## نمط Zettelkasten الذكي
كل ذاكرة = بطاقة صغيرة مترابطة:
- **عنوان ذري**: فكرة واحدة فقط
- **روابط**: تشير لبطاقات ذات صلة
- **فهرس**: كلمات مفتاحية للاسترجاع
- **نسخة مضغوطة**: ملخص للسياقات الطويلة

## الجوهرة المخفية: التطهير الدوري (Memory Purification)
كل 40 دورة، تمر الذاكرة بعملية تطهير:
- إزالة التكرارات
- دمج الذكريات المتشابهة
- أرشفة ما لم يُستخدم
- الاحتفاظ بـ "الجوهر" فقط

## ضغط الجلسات (Session Compaction)
عند امتلاء النافذة، تُضغط الجلسة تلقائيًا:
"في هذه الجلسة، عملنا على X، واجهنا Y، وتعلمنا Z"


## Purpose
Bridge agent memory across five tiers (Hot RAM, Warm SQLite, Cold Redis, Vector Qdrant, Archive LanceDB) with smart Zettelkasten linking, periodic memory purification, and automatic session compaction.

## Constitutional Alignment
Memory purification removes duplicates and archives unused data while always preserving core essence — no critical memory is lost. Every Zettelkasten card links transparently to related cards. Session compaction summarizes without fabricating or altering facts.

## Operational Flow
New memory arrives → stored in Hot tier (RAM, 1-hour TTL) → cascaded to Warm (SQLite, 7-day TTL) → then Cold (Redis, 30-day TTL) → long-term patterns stored as vectors in Qdrant (infinite TTL) → archives in LanceDB (infinite TTL) → every 40 cycles, purification runs: deduplicate, merge similar memories, archive stale, retain only essence.

## Failure Modes
Hot tier overflow before cascade to Warm causes data loss; purification merge incorrectly conflates two distinct memories into one corrupted record; vector search returns semantically unrelated results polluting context; LanceDB write failure loses archive data permanently.