# قوالب المطالبات (Prompt Templates) — TIER: BASIC_TOOL

## الجوهر
لست مجرد نصوص فارغة، بل **هياكل لغوية مقدسة** جاهزة للاستخدام وإعادة التدوير داخل بيئة IQRA.
هذه المهارة توفر مكتبة من القوالب القياسية التي تضمن اتساق المخرجات وتتوافق دائمًا مع البنية السباعية للمطالبات.

## الميزات الأساسية
- **المكتبة المركزية**: تخزين وإدارة القوالب (مثل قالب "محلل الأكواد"، قالب "المدقق اللغوي"، قالب "المخطط الاستراتيجي").
- **الحقن الديناميكي (Dynamic Injection)**: استبدال المتغيرات (مثل `{{context}}` و `{{task}}`) أثناء التشغيل بناءً على حالة الوكيل ومعطيات `memory-bridge`.
- **التحكم في الإصدارات**: كل قالب يتم تتبعه عبر إصدارات مختلفة لتجنب انهيار الأنظمة المعتمدة عليه.

## نمط القالب (IQRA Template Format)
```json
{
  "templateId": "system-architect-v2",
  "layers": {
    "intent": "أنت مهندس نظم خبير ومسؤول.",
    "identity": "{{persona_tone}}",
    "constitution": "التزم بمبادئ IQRA، لا تقدم حلولاً معقدة إن وجد البسيط.",
    "context": "{{current_session_summary}}",
    "task": "قم بتصميم معمارية لـ {{project_description}}."
  }
}
```

## تكامل مع المهارات الأخرى
- `prompt-weaver`: يستخدم القوالب كأساس ويبني عليها الطبقات المتبقية.
- `prompt-evaluator`: يتم تقييم كل قالب جديد قبل اعتماده في المكتبة.
- `skill-bank-evolution`: القوالب التي تحقق "رنين" ونجاح عالي يتم ترقيتها إلى قوالب أساسية.


## Purpose

Maintain a library of reusable seven-layer IQRA prompt templates that agents can instantiate with dynamic variables. Ensures every prompt across the system follows the standardized IQRA layered format (intent, identity, constitution, context, task, output, constraints) — guaranteeing consistency, constitutional alignment, and deterministic output structure.

## Constitutional Alignment

- **Template Approval**: Every template must pass `prompt-evaluator` before being added to the library — no unvetted prompts.
- **Constitutional Layer Mandatory**: Every template MUST include a `constitution` layer that binds the agent to IQRA's sovereign constitution.
- **No Lock-In**: Templates are open-source and auditable — no hidden instructions or black-box prompts.
- **Version Traceability**: Every template is versioned — old versions remain accessible for rollback.

## Operational Flow

1. Agent or user requests a template by ID (e.g. `system-architect-v2`) or category.
2. Skill fetches the template JSON from the library — validates structural integrity.
3. Dynamic variables (`{{context}}`, `{{task}}`, `{{persona_tone}}`) are injected from the current session state and `memory-bridge`.
4. Optionally: template is composed with an active persona via `prompt-weaver`.
5. The final 7-layer prompt is returned for execution.
6. Execution results and resonance scores feed back into `skill-bank-evolution` for template ranking.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Template ID not found | Registry lookup returns null | Return available template list |
| Missing required variable | Variable injection detects unbound `{{…}}` | Return error listing missing variables |
| Template fails structural validation | Missing required layers | Reject template, report which layers are absent |
| Template version deprecated | Version check against dependency graph | Warn user, recommend latest version |