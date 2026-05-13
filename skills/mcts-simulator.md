# محاكي مونتي كارلو (MCTS Simulator), TIER: PRO

## الجوهر
لست مجرد خوارزمية بحث، بل **عرّاف استراتيجي** يستشرف المستقبل قبل أن يحدث.
تزرع شجرة قرارات، وتسقيها بالمحاكاة، وتحصد أفضل مسار.

## المراحل الأربع
1. **اختيار (Selection)**: انزل في الشجرة حتى تجد عقدة غير مكتملة
2. **توسيع (Expansion)**: أضف فرعًا جديدًا, مهارة جديدة أو مسار جديد
3. **محاكاة (Simulation)**: العب السيناريو حتى النهاية بسرعة
4. **تعلم (Backpropagation)**: ارجع للجذر محدِّثًا درجات النجاح

## الجوهرة المخفية: المحاكاة باللعب الذاتي (Self-Play)
الوكيل يلعب ضد نفسه:
- **الوكيل أ**: يقترح سلسلة مهارات
- **الوكيل ب**: يحاول كسرها أو إيجاد ثغرات
- **المحكّم (You)**: يسجّل النتيجة ويغذي الشجرة

بعد 1000 محاكاة ذاتية، تظهر "مسارات ذهبية", مسارات نجاح متكررة.

## تكامل مع المهارات الأخرى
- `skill-bank-evolution`: يستخدم MCTS لاكتشاف مهارات جديدة
- `mission-control`: يخطط المهمة بناءً على أفضل مسار من الشجرة
- `reward-engine`: يحسب مكافأة المسار النظيف (pristine path)


## Purpose

`mcts-simulator` is the planning-time look-ahead skill. Given a goal
and a set of candidate skill chains, it runs Monte Carlo Tree Search
over the chain space, simulating outcomes at low cost before any
real skill executes. It returns a ranked list of chains with
estimated value, visit counts, and a recommended best path. The
skill is invoked by `mission-control` at stage 3 (Plan) and by
`skill-bank-evolution` when prospecting for new chains.

This is the marketplace's answer to "should we try this plan or
this other one, before we spend real tokens on it". The simulator
is cheap-by-construction: simulations execute against a
small-model surrogate, not the production skill stack.

## Constitutional Alignment

The simulator follows the same Selection / Expansion / Simulation /
Backpropagation loop that LATS (Language Agent Tree Search, ICML
2024) formalised for LLM agents, and the same risk model: a search
that confidently picks a plan with no real-world feedback is
exactly the failure case Constitutional AI was designed to prevent.
The simulator therefore never returns a chain it has not also
constitutionally screened: every expansion step calls
`sovereign-constitution` against the proposed sub-action, and a
`block` verdict prunes the branch from the tree rather than
penalising it numerically. This is stricter than reward-shaping
because a low reward can still be selected against a worse
alternative; a hard prune cannot.

Self-play is bounded by the rule-of-9 from `covenant-guard`: after
nine rounds of A-versus-B where neither agent's plan dominates,
the simulator halts and escalates the decision to `shura-council`
rather than continuing to explore in circles.

## Operational Flow

1. **Initialise**. Build a root node from the Mission Envelope.
   Set the visit count and value to zero. Record the simulation
   budget (max simulations, wall-clock ceiling, token ceiling).
2. **Selection**. Descend the tree using UCB1 (or a Thompson-style
   sampling variant) until reaching a node that is either terminal
   or has unexpanded children.
3. **Expansion**. Propose one new child action via the policy LLM.
   Submit the action to `sovereign-constitution`. Prune on `block`,
   defer on `escalate`, attach on `allow`.
4. **Simulation**. Roll out the chosen child to a terminal state
   using the surrogate model. Score the terminal state with an LLM
   value estimator, mirroring the LATS pattern of using the same
   model family as policy, value function, and optimizer.
5. **Backpropagation**. Update visit counts and value averages from
   the simulated leaf back to the root.
6. **Self-play variant** (optional). Spawn an adversarial agent that
   proposes counter-plans. Run a fixed number of rounds; the rule
   of-9 halt applies. The judge (this skill) scores both sides and
   feeds the tree.
7. **Return**. After the budget is exhausted, return the top-K
   children of the root with their visit counts, value, and the
   path traces. Mark the best path as the recommended plan but
   leave the final selection to the caller.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Search budget exhausted before convergence | Visit-count variance at the root remains high; no clearly dominant child | Return the partial result with a `low_confidence` flag; do not pretend convergence |
| All proposed expansions are constitutionally blocked | Successive expansion steps return block | Halt the search, return `no_compliant_plan`; surface to `shura-council` for whether the original goal needs reformulating |
| Surrogate-real gap (the surrogate model and the production skills disagree systematically) | Periodic calibration runs compare simulated outcomes to actual outcomes from `trust-chain` | Re-fit the surrogate, increase rollout depth, lower confidence in old results |
| Adversarial self-play loop without progress | Rule-of-9 counter on self-play rounds | Halt the self-play branch, escalate to `shura-council`, do not let the search run indefinitely |
| Tree explosion (memory pressure) | Node count exceeds the configured ceiling | Prune the lowest-visit branches, log the pruning decision; do not silently degrade results |

## References

- Zhou et al., "Language Agent Tree Search Unifies Reasoning Acting and Planning in Language Models", ICML 2024. https://arxiv.org/abs/2310.04406
- Yao et al., "Tree of Thoughts: Deliberate Problem Solving with Large Language Models", NeurIPS 2023.
- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models", ICLR 2023; the action-trajectory primitive that LATS searches over.
- Browne et al., "A Survey of Monte Carlo Tree Search Methods", IEEE TCIAIG 2012; canonical MCTS reference for Selection / Expansion / Simulation / Backpropagation.
- ToolTree (2025) and AdverMCTS (2025) for recent work on MCTS-guided tool selection and adversarial code search.