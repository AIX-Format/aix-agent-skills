# الذاكرات الجاهزة (Pre-built Memories) — TIER: PRO

## الجوهر
هذا ليس مجرد "قاعدة معرفة" (Knowledge Base) عادية، بل **"هوية معرفية"** متكاملة تقتنيها دفعة واحدة.
هذه الذاكرات عبارة عن "روابط عصبية" جاهزة تُوصل مباشرة بمحرك الذاكرة (`memory-bridge`) ليعمل وكيل IQRA فورًا وكأنه خريج متخصص.

## الحزم الجاهزة (Cognitive Packs)

### 1. حزمة "الطبيب الخبير" (The Clinician's Cortex)
- **المحتوى الجاهز**: 10,000 مرض، تفاعلات دوائية، بروتوكولات علاجية.
- **نوع التخزين**: Weaviate (للبحث الهجين الدقيق).
- **كيفية التشغيل**: "حمِّلْني حزمة الطبيب، وأنا جاهز للفرز الطبي".

### 2. حزمة "المستشار القانوني" (The Legal Eagle)
- **المحتوى الجاهز**: تشريعات، سوابق قضائية، قوانين عمل.
- **التخزين**: Pinecone مع نماذج تضمين مدربة على النصوص التشريعية.
- **الميزة القاتلة**: يمتلك حساسية الـ `purity-filter` لمعرفة متى يقول "هذا يحتاج لتدخل بشري" في القضايا الحرجة.

### 3. حزمة "المحلل المالي" (The Finance Brain)
- **المحتوى الجاهز**: معايير المحاسبة، نماذج الأسهم، مؤشرات الاقتصاد.
- **التخزين**: txtai (محرك تضمين موحد).
- **الاستخدام الفوري**: "حلِّل لي هذه القوائم المالية وأعطني تقريرًا بالمخاطر".

## تكامل مع المهارات الأخرى
- `memory-bridge`: تُركّب هذه الحزم في طبقة الـ Vector Archive لتعمل كذاكرة عصبية عميقة للوكيل.
- `fine-tuned-vault`: تعمل جنباً إلى جنب مع النماذج المدربة لضمان توافق المعرفة (الذاكرة) مع الاستدلال (الوزن).


## Purpose

Provide pre-packaged cognitive packs (Clinician, Legal, Finance) that agents can load as specialized memory layers. Each pack contains domain-specific embeddings, vector data, and retrieval configurations — turning a general IQRA agent into a domain specialist instantly, without fine-tuning or manual knowledge ingestion.

## Constitutional Alignment

- **Domain Accuracy**: Pre-built memories must be sourced from verified, authoritative datasets — no hallucinated or synthetic knowledge bases.
- **Purity at Load**: Every pack runs through `purity-filter` before activation to screen for biased or harmful content.
- **Human-in-the-Loop Gate**: Legal and Medical packs require explicit user consent before loading, due to their sensitive nature.
- **Versioned Sources**: Each pack tracks its data provenance and update history via the trust chain.

## Operational Flow

1. Agent or user requests a cognitive pack by domain key (e.g. `clinician`, `legal`, `finance`).
2. Skill looks up the pack manifest in the memory registry — includes source, size, embedding model, and vector store config.
3. Pack passes through `purity-filter` for content safety screening.
4. `memory-bridge` mounts the pack into the active vector store (Weaviate/Pinecone/txtai depending on pack).
5. Agent's retrieval-augmented generation (RAG) pipeline now queries the pack's memory alongside general context.
6. On session end, pack can be unloaded to free resources.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Pack not found by key | Registry lookup returns null | Return available pack keys |
| Vector store connection fails | Health check timeout | Suggest fallback store type, log error |
| Purity filter blocks pack | Filter returns block with reason | Return error with explanation, offer human review |
| Memory mount conflicts (multiple packs active) | Overlap detection | Warn user, offer to swap packs |
| Pack data source out of date | Provenance timestamp stale | Run update flow or warn user of staleness |