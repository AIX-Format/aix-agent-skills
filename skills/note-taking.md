# Note Taking — تدوين الملاحظات الذكي

مدون الملاحظات ينشئ وينظم ويربط الملاحظات بذكاء. يستخدم العلامات والفئات والروابط التشعبية لبناء شبكة معرفية. يبحث في النص الكامل ويعثر على المعلومات في ثوان. يربط الملاحظات المتشابهة لاكتشاف العلاقات الخفية بين الأفكار.

## Purpose / الغرض

Create, organize, link, and search notes with tags, categories, semantic linking, and full-text search.

## Constitutional Alignment / التوافق الدستوري

- **Data Ownership**: جميع الملاحظات مملوكة للمستخدم
- **Privacy**: لا يشارك الملاحظات دون أمر صريح
- **Persistence**: لا تفقد البيانات بسبب خطأ تقني

## Operational Flow / التدفق التشغيلي

1. Agent receives note creation or query command
2. Parses and indexes content with tags and links
3. Stores note with metadata in knowledge base
4. Returns linked notes and relevant context

## Failure Modes / أنماط الفشل

- **Index corruption**: Detect via consistency check — rebuild index
- **Duplicate notes**: Detect via similarity scoring — suggest merge
- **Link rot**: Detect broken internal links — flag for update

## References

- `semantic-memory.md` — long-term memory integration
- `task-manager.md` — linking notes to tasks
