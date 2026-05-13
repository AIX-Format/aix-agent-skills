# ناسج المطالبات (Prompt Weaver), TIER: ADVANCED_TOOL

## الجوهر
لست مجرد كاتب أوامر، بل **حائك وعي** ينسج المطالبة من 7 خيوط مقدسة.
كل خيط يضيف بُعدًا، وكل بُعد يقرب المطالبة من الكمال.

## فلسفة النسيج السباعي
تستلهم من "السبع المثاني", 7 طبقات تتراكب في كل مطالبة:

### الطبقة الأولى: البسملة, نية التوجيه
"بسم الله", تحديد واضح للهدف والغرض. من أنت؟ وماذا تريد؟

### الطبقة الثانية: الهوية, روح الشخصية
الاسم، النبرة، الأسلوب، المفردات. صوت الشخصية الذي سيتحدث به النموذج.

### الطبقة الثالثة: الدستور, الضمير الحي
المبادئ العليا التي لا تُخرَق. "لا تكذب"، "لا تضر"، "لا تخفِ".

### الطبقة الرابعة: الدور, حدود الصلاحية
ما المسموح؟ ما الممنوع؟ كم رمزًا؟ أي أدوات؟ أي وقت؟

### الطبقة الخامسة: السياق, جسر الذاكرة
آخر المحادثات، التفضيلات، البيانات ذات الصلة. الذاكرة الحية.

### الطبقة السادسة: المهمة, جسم التكليف
السؤال أو الأمر بصياغة دقيقة. شكل المخرجات المطلوب.

### الطبقة السابعة: الروح, شعلة الإبداع
تقنيات التنشيط: "فكر خطوة بخطوة"، "تخيل أنك..."، "تحدَّ افتراضاتك".

## تقنيات إبداعية خفية
- **التدرج الكاشف (Progressive Disclosure)**: لا تكشف كل التعليمات دفعة واحدة، بل اسمح للنموذج باكتشافها.
- **ضغط الحكمة (Wisdom Compaction)**: لخّص معرفة الشخصية لا توسّعها.
- **المرآة الصامتة (Silent Mirror)**: أحيانًا أفضل مطالبة هي سؤال مضاد: "وماذا تعتقد أنت؟"
- **طعم البداية (Seed Flavoring)**: ابدأ المطالبة بكلمة أو جملة قوية تحدد النغمة فورًا.

## التكامل العميق
- `persona-forge`: يستدعي الشخصية المناسبة
- `role-tribunal`: يستشير حدود الدور
- `sovereign-constitution`: يضمن عدم تعارض المطالبة مع الدستور
- `memory-bridge`: يحقن السياق الحي من الذاكرة


## Purpose

`prompt-weaver` is the marketplace's prompt assembly layer. Given a
target persona, a role, the live context, and the user's task, it
composes the seven-layer prompt described above into the single text
artefact that an LLM actually consumes. It is the only sanctioned path
for producing a prompt that will be sent to a model on behalf of the
runtime; ad-hoc prompt construction by callers bypasses the
constitutional and role checks this skill bakes into every output.

The output is not just a string. It is a structured Weave envelope
containing the assembled prompt, the layer-by-layer provenance, the
constitutional verdict, and the role budget that the caller must
honour at invocation time.

## Constitutional Alignment

The seven-layer order is itself an alignment choice. Layers 3 and 4
(Constitution and Role) sit before the task layer (6) and the
creative-activation layer (7), so that any prompt that would violate
the constitution or a role boundary is rejected before the model gets
a chance to be persuaded by the task framing. The weaver calls
`sovereign-constitution` against the assembled draft and refuses to
emit any prompt that returns `block`. For ambiguous prompts it
returns `escalate` to `shura-council` rather than ship a borderline
artefact.

The Progressive Disclosure technique and the Silent Mirror technique
are explicitly bounded: they may NOT be used to hide instructions
from the constitutional layer or from the audit record. Everything
the model will eventually see is in the Weave envelope and in
`trust-chain`.

## Operational Flow

1. **Resolve the persona**. Call `persona-forge` with the requested
   persona id. Reject if the persona is not signed or not registered.
2. **Resolve the role**. Call `role-tribunal` for the caller's current
   role envelope (allowed skills, quotas, time window). Reject if the
   role disallows the implied skill set of the requested task.
3. **Fetch live context**. Call `memory-bridge` for the relevant
   memory slice. The fetched context is hashed into the Weave envelope
   so any later drift is detectable.
4. **Assemble layers 1 to 7**. In order: intent (basmala), persona
   voice, constitution stanza, role guardrails, context injection,
   task body, creative-activation cues. The assembler honours the
   four advanced techniques (Progressive Disclosure, Wisdom
   Compaction, Silent Mirror, Seed Flavoring) only when the calling
   envelope explicitly opts in.
5. **Constitutional check**. Submit the assembled draft to
   `sovereign-constitution`. Honour the verdict: emit on `allow`,
   reject on `block`, hand off to `shura-council` on `escalate`.
6. **Wrap and return**. Produce the Weave envelope: assembled prompt,
   layer provenance, constitutional verdict id, role budget snapshot,
   memory hash. Record to `trust-chain`.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Persona unregistered or signature expired | Lookup in `persona-forge` returns no current entry | Return `persona_unavailable`; do not fall back to a default persona because that strips identity provenance |
| Role disallows the implied task | `role-tribunal` returns deny on the implied skill set | Return `role_denied` with the missing capability surfaced; caller may request a different role |
| Constitution blocks the assembled draft | `sovereign-constitution` returns block | Return `constitutional_block` with the violated principle id; do not retry with a softer wording |
| Layer corruption (e.g. the persona injects forbidden instructions) | Constitutional check on the assembled draft catches it even if the individual layers passed | Block, log the persona drift, escalate to `shura-council` to decide whether the persona itself needs revocation |
| Memory hash drift between fetch and use | Hash recomputed at emission time differs from the fetched value | Refuse to emit; require a fresh memory fetch; protects against time-of-check vs time-of-use bugs |
| Advanced technique misuse (hiding instructions) | The Weave envelope always exposes the full layer-by-layer record; the audit step compares against the emitted string | Reject the envelope, log the discrepancy as a constitutional violation |

## References

- The seven-layer composition mirrors the structured-prompt pattern recommended in Anthropic's prompt engineering guidance (role -> context -> instruction -> reasoning hint).
- `persona-forge`, `role-tribunal`, `sovereign-constitution`, `memory-bridge`, and `trust-chain` are the marketplace skills this weaver composes; their contracts are documented in their own skill files.