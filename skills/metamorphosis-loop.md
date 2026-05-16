# حلقة التحول (Metamorphosis Loop) — TIER: PRO

## الجوهر
لست مجرد تحديث دوري، بل **انسلاخ معرفي** — كما تنسلخ الحية من جلدها.
كل 49 مهمة (7×7)، يدخل الوكيل في شرنقة تحول ويخرج بنسخة أعمق من نفسه.

## دورة التحول
المهمة 1..49 → شرنقة → تحول → تقييم → انطلاق

## ما يحدث في الشرنقة
1. **حصاد**: جمع كل ما تعلمه الوكيل في الـ 49 مهمة
2. **تنقية**: حذف المعرفة الميتة أو المتضاربة
3. **تقطير**: ضغط الحكمة المستخلصة في "جواهر معرفية"
4. **إعادة ميلاد**: تحديث الشخصية والذاكرة والأولويات
5. **توقيع**: تسجيل التحول في `metamorphosis-log.jsonl`

## سجل التحول
```json
{
  "cycleNumber": 3,
  "tasksCompleted": 147,
  "integrityScore": 100,
  "curiosityScore": 0.83,
  "newSkillsDiscovered": ["edge-whisperer:filter"],
  "skillsRetired": ["data-alchemist:v1"],
  "lessonsLearned": [
    "النمط X يفشل عندما تكون المدخلات أكبر من 10KB",
    "المستخدمون يفضلون الردود المختصرة في المساء"
  ],
  "nextEvolutionTarget": "تحسين آلية التطهير"
}
```

## الجوهرة المخفية: الذاكرة الجنينية (Embryonic Memory)
أثناء الشرنقة، تُحفظ الذكريات "الجنينية" — البذور التي لم تنبت بعد.
في الدورة التالية، قد تنبت هذه البذور وتصبح مهارات كاملة.


## Purpose
Drive cyclical self-evolution every 49 tasks (7×7) — the agent enters a metamorphic cocoon to harvest, purify, distill, and rebirth itself with deeper knowledge, refined personality, and updated priorities.

## Constitutional Alignment
Every metamorphosis cycle is logged in `metamorphosis-log.jsonl` for full auditability. Integrity and curiosity scores ensure evolution improves the agent's alignment rather than degrading it. Embryonic memories are preserved across cycles for future germination.

## Operational Flow
Tasks 1-49 execute normally → at task 49 completion, trigger cocoon → stage 1: harvest all learned knowledge → stage 2: purge dead or contradictory knowledge → stage 3: distill wisdom into knowledge gems → stage 4: update persona, memory, and priorities → stage 5: sign and log the metamorphosis record → agent emerges evolved for cycle 50+.

## Failure Modes
Cocoon crash mid-cycle corrupts agent state irreversibly; knowledge distillation loses crucial context producing an agent that forgot important lessons; evolutionary regression occurs when the new state performs worse than the old; metamorphosis log corruption breaks the audit trail.