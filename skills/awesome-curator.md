# أمين القوائم المنسقة (Awesome Curator) — TIER: ADVANCED_INFRASTRUCTURE

## الجوهر
ليس مجرد دليل، بل **حارس البوابة الاجتماعية** الذي يحول سوق IQRA من "متجر تطبيقات"
إلى "مكتبة إسكندرية رقمية".
المستخدم لا يبحث، بل **يتصفح قوائم موثوقة** يصنعها المجتمع ويصادق عليها.

## ما يقدمه
1. **قوائم منسقة (`awesome-sales-skills`، `awesome-prompt-engineering`...)**
   - كل قائمة = ملف `.md` في مستودع المهارات، يمكن لأي شخص تقديم fork و pull request.
   - الشروط: المهارة المُدرجة يجب أن تكون **مجتازة لاختبارات `skill-evaluator`** وحاصلة على شارة خضراء.
   - الترتيب: حسب السمعة (`trust-chain`) أو حسب التثبيتات.

2. **نظام الترشيح المجتمعي**
   - أي مستخدم يمكنه ترشيح مهارة لقائمة عبر issue/PR.
   - المشرفون (أصحاب القائمة) يراجعون ويدمجون.
   - تلقائيًا: `skill-sandbox` و `prompt-evaluator` يُرفقان تقريرهما مع الترشيح.

3. **التصويت و الصلاحية**
   - كل قائمة لها "راعي" (بشري أو وكيل) مسؤول عن الجودة.
   - المهارات التي لا تُحدث أو تنخفض جودتها تُحذف دوريًا.

## التكامل الواقعي
- **تخزين**: `.idx/curated-lists/` — مجلد ملفات markdown.
- **الواجهة**: Next.js route `/marketplace/awesome` تعرض القوائم كـ "رفوف".
- **التشغيل الآلي**: CI pipelines تشغّل `skill-evaluator` على كل PR قبل الدمج.

## لماذا يهم؟
- المستخدم الجديد لا يعرف أسماء المهارات. يرى "رف المبيعات" ويحصل على مجموعة مهارات موثوقة.
- المجتمع يبني السمعة ليس فقط للمهارات، بل **للقوائم نفسها** (قائمة فلان أفضل من قائمة علان).
- يتيح **التخصص العميق**: قائمة "أدوات تحليل البيانات بالعربية" أو "وكلاء تدقيق العقود".


## Purpose
Transform the IQRA marketplace from a bare app store into a community-curated digital library where verified skill lists are organized by domain, maintained by stewards, and surfaced through recognizable shelves for browsing.

## Constitutional Alignment
Skills listed in curated collections must have passed `skill-evaluator` tests and carry a green badge. List stewards are accountable for quality; stale or degraded skills are periodically purged. Nominations are transparent via issues and PRs with automated evaluation reports attached.

## Operational Flow
Community member nominates a skill via issue/PR → CI pipeline triggers `skill-sandbox` and `prompt-evaluator` → reports attached automatically → list steward reviews and merges → skill appears on `/marketplace/awesome` shelf → periodic quality checks remove skills that no longer meet the bar.

## Failure Modes
Malicious PR bypasses review and introduces unverified skills; list steward goes inactive creating a single point of failure; periodic quality checks not configured leads to stale listings; unevaluated skills leak into curated lists.