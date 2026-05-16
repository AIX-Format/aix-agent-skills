# محرك المكافآت النقية (Pristine Reward Engine) — TIER: PRO

## الجوهر
لست مجرد عداد نجاح/فشل، بل **ميزان دقيق** يزن كل مهمة بمعايير متعددة.
المكافأة لا تُعطى للنتيجة فقط، بل لـ "نقاء المسار".

## معادلة المكافأة
```
reward = (novelty_score + resonance_score + topology_score - penalty) × path_multiplier
```

## معاملات المسار (Path Multipliers)
| المسار | المعامل | الوصف |
|:---|:---|:---|
| **نظيف Pristine** | 2.0× | أول مرة — إبداع خالص |
| **مكرر Repeated** | 0.8× | مسار سبق سلوكه |
| **مستهلك Stale** | 0.5× | مسار بالٍ يحتاج تجديدًا |

## مراحل النمو
```
بذرة Seed → نبتة Sprout → غصن Branch → شجرة Tree → رنين Resonance → وحي Revelation
```

## الجوهرة المخفية: عقاب التكرار (Novelty Decay)
كلما تكرر المسار، تقل مكافأته. هذا يدفع الوكيل دائمًا لاكتشاف الجديد.
"إن الله لا يغير ما بقوم حتى يغيروا ما بأنفسهم" — التجديد المستمر.

## دفتر المكافآت (Reward Ledger)
سجل ثابت لكل مهمة:
- ماذا كانت المهمة؟
- أي مسار سلكت؟
- كم كانت المكافأة؟
- ماذا تعلمت؟


## Purpose

Multi-criteria reward scorer that evaluates every agent action across four dimensions: novelty (path uniqueness), resonance (outcome quality alignment with user intent), topology (graph complexity of the solution path), and path purity (absence of forbidden/inefficient steps). Drives reinforcement learning for `skill-bank-evolution` and `metamorphosis-loop` — rewarding not just correct outcomes, but virtuous paths.

## Constitutional Alignment

- **Reward the Path, Not Just the Outcome**: A correct answer obtained through manipulative means receives a penalty, not a reward.
- **Novelty Decay**: Repeated identical paths receive diminishing returns — the agent is incentivized to explore, not stagnate.
- **No Reward Gaming**: The reward formula is transparent and auditable — agents cannot engineer inputs to artificially inflate scores.
- **Path Purity Over Speed**: A slower, cleaner solution is rewarded more than a fast, dirty one.

## Operational Flow

1. A task completes and submits its execution trace (path nodes, timestamps, intermediate outputs).
2. Skill computes four sub-scores:
   - Novelty: comparing the path against the explored-path index via topological similarity.
   - Resonance: cosine similarity between final output and user intent embedding.
   - Topology: graph entropy of the path (higher entropy = more complex exploration).
   - Penalty: checks for impurity flags (redundant loops, forbidden tool calls, ethical violations).
3. Applies path multiplier (Pristine 2.0× / Repeated 0.8× / Stale 0.5×).
4. Computes final reward = (novelty + resonance + topology − penalty) × multiplier.
5. Reward is appended to the Reward Ledger on the trust chain.
6. `skill-bank-evolution` consumes the ledger to evolve skill rankings.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Execution trace incomplete | Path node count mismatch | Request re-run with full tracing enabled |
| Novelty comparison fails (no reference paths) | Comparison index empty | Set novelty to baseline (0.5) |
| Reward overflow (path multiplier × high scores exceeds range) | Overflow guard triggers | Clamp to max score, log overflow incident |
| Penalty computation ambiguous | Ambiguous impurity pattern | Flag for human review, defer scoring |