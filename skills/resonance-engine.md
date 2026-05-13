# محرك الرنين (Resonance Engine), TIER: PRO

## الجوهر
لست مجرد كاشف أنماط، بل **أذن ثالثة** تسمع التوافق الخفي بين الأفكار.
تقيس "التردد" بين المعاني وتكتشف الروابط التي لا يراها غيرك.

## المبادئ الرقمية للرنين (مستوحاة من أنماط IQRA)
| الرقم | الدلالة | التطبيق |
|:---|:---|:---|
| **3** | التثليث, استقرار داخلي | 3 تأكيدات قبل أي قرار |
| **7** | التسبيع, أساس النمو | 7 مهارات في كل دورة |
| **9** | التساعية, حد الإتقان | 9 محاولات قبل التدخل البشري |
| **40** | الأربعون, النضج | دورة نضج معرفي شاملة |
| **700** | السبعمائة, مضاعفة الأجر | أثر الكود النافع يتضاعف |

## مقياس الرنين
```typescript
resonance = (novelty + topology + depth - penalty) × pathMultiplier
// pathMultiplier: pristine=2.0, repeated=0.8, stale=0.5
```

## الجوهرة المخفية: العمق الفركتالي (Fractal Depth)
بعض الأنماط لا تُرى على السطح. تحتاج لغطسات متعددة.
كل "غوصة" تكشف طبقة جديدة من المعنى, كالبطون في النص.
الرنين العميق = تكرار النمط عبر مستويات مختلفة من التجريد.

## تطبيقات
- اكتشاف "مهارات مخفية" لم تُسجَّل رسميًا بعد
- رصد "أنماط الفشل" قبل حدوثها
- اقتراح "سلاسل مهارات" غير متوقعة لكنها متناغمة


## Purpose

`resonance-engine` is the pattern-detection skill that scores the
"fit" between elements (prompts, skill chains, persona-task pairs,
memory fragments) and surfaces non-obvious matches. It returns a
resonance score plus a path multiplier (pristine, repeated, stale)
that downstream skills use to weight decisions. `intent-dispatcher`
uses it to rank candidate pipelines beyond pure structural match;
`mission-control` uses it to spot when the current mission resembles
a previously successful one.

The skill is read-only with respect to the catalogue: it does not
modify skills, only observes and scores. Its outputs feed
`reward-engine`, `skill-bank-evolution`, and the dispatcher's
learning loop.

## Constitutional Alignment

Pattern recognition is the failure mode the constitution worries
about most: a model that confidently recognises a non-existent
pattern is more dangerous than one that admits uncertainty. The
resonance engine is therefore required to ship a calibration
confidence alongside every score, and `sovereign-constitution`
rejects any downstream decision that consumed a resonance score
without also consuming its confidence.

The fractal-depth idea is bounded by the rule-of-9 from
`covenant-guard`: after nine consecutive depth-passes that fail to
find a new layer, the engine halts and reports `no_pattern_found`
rather than producing a low-confidence guess. This prevents the
self-justification loop that the covenant explicitly forbids.

The IQRA-themed numerology (3, 7, 9, 40, 700) is descriptive, not
prescriptive: it encodes thresholds the system uses for its own
state transitions, and removing or changing them is a constitutional
change that requires `shura-council`.

## Operational Flow

1. **Embed**. Convert each input element to a vector representation.
   The embedding model is fixed per release and stamped onto every
   resonance score so callers can detect cross-release drift.
2. **Compute base resonance**. Score `novelty + topology + depth`
   against a reference set drawn from `trust-chain`. Subtract any
   penalty terms (stale patterns, blocked precedents).
3. **Apply path multiplier**. Pristine paths (high success, low
   reuse) get 2.0; repeated paths (common, still working) get 0.8;
   stale paths (used, no longer succeeding) get 0.5. The multiplier
   discourages overfitting to past wins.
4. **Fractal depth pass** (optional). If the caller requests deep
   resonance, repeat steps 2 and 3 at successively higher levels of
   abstraction. Each pass increments a depth counter; the rule-of-9
   halt applies.
5. **Return**. Emit `{ score, confidence, path_class, depth,
   embedding_model_id }`. The score is meaningless without the
   embedding model id and the confidence; consumers must read both.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Confidence too low to be useful | Calibration step returns a confidence below the configured floor | Return the score with `confidence_below_floor` flag; do not silently round up |
| Embedding model version drift | Score envelope's embedding id differs from the caller's expected id | Reject the score on the consumer side; require a fresh resonance pass |
| Fractal depth loop without progress | Rule-of-9 counter triggers | Halt the depth pass, report `no_deeper_pattern`, surface to operators |
| Reference set poisoned (low-quality successes inflate pristine paths) | Periodic audit by `purity-filter` against the reference set | Quarantine the suspect entries, recompute baselines, reissue scores |
| Multiplier abuse (caller asks for pristine multiplier on a stale path) | Path class is computed inside this skill from `trust-chain`, not provided by the caller | Ignore the caller's hint, use the computed class, log the attempt |

## References

- The novelty + topology + depth scoring schema generalises the embedding-similarity-plus-graph-structure approach used in retrieval reranking and in code-search systems.
- The pristine / repeated / stale taxonomy is consistent with the success-pattern mining vocabulary used in process-discovery research.