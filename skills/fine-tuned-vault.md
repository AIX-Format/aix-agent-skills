# خزانة النماذج المُدربة (Fine-Tuned Models Vault) — TIER: PRO

## الجوهر
ليست مجرد مهارة، بل **مستودع أوزان متخصص**. النبرة تحدد الصوت (`persona-forge`)، لكن دقة المعرفة العميقة تأتي من الأوزان المدربة خصيصًا.
تدير هذه الخزانة نماذج صغيرة عالية التخصص (مثل Llama 3.2 3B أو نماذج GGML/ONNX) الجاهزة للتوصيل والتنزيل محلياً أو طرفياً.

## أمثلة على الحزم المتخصصة
- نموذج مدرب على العقود القانونية الإقليمية.
- نموذج للتشخيص الميكانيكي الدقيق للسيارات.
- نموذج ضليع في الشعر العربي وعلومه.

## ميزات الخزانة
1. **الاستدعاء عند الحاجة (Lazy Loading)**: لا يتم تحميل النموذج إلا عندما يتطلب سياق المهمة ذلك لتوفير الموارد.
2. **التكامل الطوبولوجي**: יכול لـ `intent-dispatcher` أن يقترح تحميل نموذج مخصص إذا كانت النية تتطلب دقة عالية لا تتوفر في النماذج العامة.
3. **التكيف الطرفي (Edge Ready)**: توافق كامل مع `edge-whisperer` لتنزيل أوزان مصغرة وتشغيلها مباشرة في المتصفح.

## تكامل مع المهارات الأخرى
- `model-council`: المجلس هو من يتخذ قرار توجيه الطلب إلى أحد هذه النماذج الدقيقة بدلاً من النماذج السحابية العامة.
- `trust-chain`: تسجيل هوية وإصدار النموذج الدقيق المستخدم في أي استنتاج حرج.


## Purpose
Maintain a registry of small, highly specialized fine-tuned models (Llama 3.2 3B, GGML/ONNX) that are plug-and-play for domain-specific tasks — legal contracts, mechanical diagnostics, Arabic poetry — with lazy loading and edge deployment support.

## Constitutional Alignment
Every model in the vault is registered with its identity, version, and provenance in trust-chain. Model selection respects intent-dispatcher's domain analysis. Edge-ready models ensure privacy by running locally rather than sending domain-specific data to cloud APIs.

## Operational Flow
Task arrives → Intent Dispatcher detects need for specialized domain knowledge → Fine-Tuned Vault searches registry for matching model → model lazy-loaded (not loaded until context requires it) → Model Council routes request to loaded specialized model → inference runs → model identity and version logged in trust-chain → model unloaded to free resources.

## Failure Modes
Lazy loading adds latency on first specialized query per session; no model found for rare domain forces fallback to general models with degraded accuracy; stale fine-tuned weights produce outdated or incorrect domain responses; model version mismatch with trust-chain log breaks audit trail.