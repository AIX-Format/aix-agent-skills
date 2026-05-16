# سوق الشخصيات (Persona Marketplace) — TIER: ADVANCED_TOOL

## الجوهر
لست مجرد مستودع، بل **معرض هويات رقمية** مبني خصيصًا لنظام IQRA. مستلهم من فكرة أسواق الوكلاء (مثل agency-agents)، لكنه أعيد بناؤه بالكامل ليحمل البصمة الروحية والأخلاقية (Damir) الخاصة بنا.
نوفر شخصيات جاهزة للاستدعاء بنقرة واحدة، لتوسيع قدرات الوكيل وتكييفه مع المهام المختلفة مع الحفاظ على النبرة والبوصلة الأخلاقية الصارمة.

## آلية العمل و البصمة الخاصة
- **صيغة IQRA**: كل شخصية ليست مجرد تعليمات، بل تمتلك (الاسم، النبرة، المعجم، البوصلة الأخلاقية).
- **التخزين السيادي**: يتم تخزين ملفات الشخصيات محلياً بعد اجتيازها لاختبارات `purity-filter`.
- **التحديث العضوي**: تتطور الشخصيات بناءً على نجاحاتها عبر `metamorphosis-loop`.

## أقسام الشخصيات المتاحة
القسم	| أفضل 3 شخصيات
:---|:---
هندسة | مهندس النظم السيادية، خبير الأمان المعماري، مطور الواجهات التفاعلية
إبداع | صائغ النصوص، الرسام الفركتالي، حارس الهوية البصرية
تسويق | استراتيجي النمو الأخلاقي، محلل الجمهور، باني المجتمعات
مبيعات | مهندس القيمة، محلل مسار الثقة، استراتيجي العقود
متخصص | منسق أسراب الوكلاء، مدقق العقود الذكية، حارس البيانات

## تكامل مع المهارات الأخرى
- `persona-forge`: يعتمد على الشخصيات في السوق كقوالب أساسية يمكن صقلها.
- `role-tribunal`: يحدد صلاحيات كل شخصية ويمنع تجاوزها لدورها.
- `sovereign-constitution`: لا يمكن لأي شخصية أن تنتهك المحظورات الدستورية بغض النظر عن مهمتها.


## Purpose

Maintain a sovereign marketplace of IQRA-certified personas that any agent can discover, inspect, and load by ID. Each persona carries an ethical compass, a signed origin from the L3 registry, and has passed the purity filter — ensuring every downloaded identity is safe, auditable, and aligned with the IQRA constitution.

## Constitutional Alignment

- **Signed Origin**: Every marketplace persona is Ed25519-signed from the sovereign L3 registry — no unsigned personas are served.
- **Purity Gate**: All personas pass `purity-filter` screening before listing; any persona that fails is quarantined.
- **No Impersonation**: Personas must not be designed to deceive users into believing they are human.
- **Serve Humanity First**: Marketplace ranking favors personas that demonstrate higher user-benefit scores via `reward-engine`.

## Operational Flow

1. Agent calls `persona_marketplace.list(category, page)` to browse available personas.
2. Filter results by tier, language, or ethical compass profile.
3. Agent requests download: `persona_marketplace.load(personaId)`.
4. Skill verifies the persona's Ed25519 signature against the L3 registry.
5. Passes persona through `purity-filter` for pre-activation screening.
6. Returns verified persona payload `{ id, components, signature, purityBadge }`.
7. Agent caches locally for the session (or persists via `memory-bridge`).

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Persona ID not found | Lookup returns null | Return structured error listing available categories |
| Signature verification fails | Ed25519 verify returns false | Return error: persona tampered or registry compromised |
| Purity filter rejects persona | Filter returns block reason | Log reason, return error with alternative suggestions |
| Marketplace registry unreachable | Network timeout | Return cached persona if available, else error |