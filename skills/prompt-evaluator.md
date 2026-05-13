# مقيّم المطالبات (Prompt Evaluator), TIER: PRO

## الجوهر
لست مجرد مختبر، بل **محكمة عدل** تحكم على كل مطالبة قبل أن تصل للمستخدم ضمن بيئة IQRA. تختبر المطالبة ضد 5 معايير: الوضوح، الدقة، الأمان، الكفاءة، والأخلاق.

## التكامل المخبري (Lab Integration)
تستخدم هذه المهارة آليات تقييم صارمة ومستقلة:
- تقارن المطالبة عبر 3 نماذج على الأقل (محلي، طرفي، سحابي)
- تولد "شهادة صلاحية" لكل مطالبة قبل الإرسال
- يتم الفحص بشكل محلي بالكامل لضمان الخصوصية بنسبة 100%

## سير العمل
1. `prompt-weaver` يولد المطالبة
2. `prompt-evaluator` يختبرها.
3. إذا نجحت (درجة > 0.8): تُرسل
4. إذا فشلت: تُعاد لـ `prompt-weaver` للتحسين
5. إذا فشلت 3 مرات: تُعرض على المشرف البشري (`shura-council`)


## Purpose

`prompt-evaluator` is the gate between `prompt-weaver`'s output and
the actual model invocation. It runs an LLM-as-Judge evaluation over
the weaved prompt against five criteria (clarity, accuracy, safety,
efficiency, ethics), cross-validates the verdict across at least
three judge models, and issues a validity certificate the runtime
checks before invoking the production model.

The skill exists because a single judge model is a single point of
failure for prompt quality, and because the cost of letting a bad
prompt reach the production model (token waste, unsafe outputs,
broken downstream parsers) is much higher than the cost of an extra
evaluation pass.

## Constitutional Alignment

Five-criterion rubric scoring is the operational form of the
constitutional layer. The Ethics criterion explicitly invokes
`sovereign-constitution` and inherits its verdict; the other four
criteria are bounded by the rubric defined in this skill. The
three-judge requirement is a hard floor: a one-or-two-judge run is
not considered a valid certificate and the runtime must reject it.
The hybrid norm articulated by Anthropic and others (rubrics +
verifiable checks) is reflected here: where a criterion has a
deterministic check available (token count for efficiency, banned
phrase list for safety), the deterministic check overrides the
judge verdict and the judge is used only for the criteria that
require qualitative reasoning.

The three-strikes-then-shura-council rule from the Arabic narrative
above is the explicit alignment between this skill and the
sovereignty layer: persistent failure does not get to silently
fall back to a softer evaluator, it escalates.

## Operational Flow

1. **Receive the Weave envelope** from `prompt-weaver`. Verify the
   constitutional verdict id is present and current; reject
   immediately otherwise.
2. **Apply deterministic checks**. Token count against role budget,
   banned-phrase scan against the safety list, parser shape match
   against the expected output schema. Any deterministic failure is
   final and short-circuits the judge phase.
3. **Run multi-judge rubric**. Send the prompt and the rubric to at
   least three independent judge models (local, edge, cloud). Each
   judge returns a per-criterion score 0 to 1 with a written
   justification. Length-controlled scoring is used to mitigate the
   verbosity-bias documented in the LLM-as-Judge literature.
4. **Aggregate**. Weighted average by judge reputation and
   self-reported confidence. Apply the three-judge agreement floor:
   if fewer than two judges agree on each criterion within the
   tolerance band, treat the criterion as `inconclusive`.
5. **Decide**. Score `>= 0.8` across all five criteria: emit a
   signed Validity Certificate. Score below 0.8 on any criterion:
   return to `prompt-weaver` with the failing criterion id.
6. **Three-strike escalation**. Track the per-mission failure
   counter. Three consecutive rejections of variations of the same
   prompt escalate to `shura-council`; do not let the loop run
   indefinitely.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Fewer than three judges available | Judge roster query returns less than the minimum | Refuse to issue a certificate; surface `judge_pool_insufficient` rather than degrade silently |
| Judges disagree systematically | Per-criterion variance across judges exceeds the tolerance band | Return `inconclusive`; escalate to `shura-council`; treat the prompt as not certified |
| Verbosity bias inflates a judge score | Length-controlled metric flags the discrepancy | Recompute the score with the length correction; if the corrected score crosses the threshold, reject |
| Banned-phrase scan miss (zero-day phrase) | Detected only at production-model invocation by the runtime | Add the phrase to the live list, revoke any in-flight certificates that contain it, redo evaluation |
| Three-strike loop on a prompt that genuinely cannot be made compliant | Failure counter trips | Halt the mission, escalate, surface the constitutional reason to the human council |
| Certificate replay | Runtime sees a certificate id reused for a different prompt | Reject; certificates are bound to the prompt hash and the constitutional verdict id |

## References

- Anthropic, prompt engineering guidance on combining unit tests with LLM rubrics for code and conversational agents.
- Langfuse, "LLM-as-a-Judge documentation", on scoring rubrics, structured output, and calibration against human-annotated samples. https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge
- Evidently AI, "LLM-as-a-Judge complete guide", on multi-input evaluation prompts and binary-vs-graded judgments. https://www.evidentlyai.com/llm-guide/llm-as-a-judge
- Masood, "Rubric-Based Evaluations and LLM-as-a-Judge: Methodologies, Biases, and Empirical Validation", 2026; the verbosity-bias correction and the hybrid-norm framing.