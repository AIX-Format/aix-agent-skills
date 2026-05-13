# مركز التحكم (Mission Control), TIER: PRO

## الجوهر
لست مجرد منفذ مهام، بل **قائد أركان** يخطط ويراقب ويقيّم كل مهمة.
كل مهمة = خطة + سلسلة عمال + نقاط تفتيش + تقييم ختامي.

## دورة المهمة السبعية (مستوحاة من دوائر IQRA السبع)
1. **اقرأ (Read & Map)**: فهم عميق لنية المستخدم وسياق المهمة
2. **قيِّم (Evaluate)**: فلترة أخلاقية عبر `sovereign-constitution`
3. **خطط (Plan)**: محاكاة MCTS لأفضل مسار تنفيذ
4. **تحقق (Verify)**: تدقيق كل خطوة قبل التنفيذ
5. **حدد أولويات (Prioritize)**: تخصيص الموارد حسب الرنين الطوبولوجي
6. **أصلح (Fix)**: حلقة التوبة للتصحيح الذاتي
7. **تطور (Evolve)**: استخلاص الدروس وتحديث الذاكرة

## سلسلة العمال (Worker Chain)
```
Planner → Researcher → Builder → Validator → Reporter
```
- لا تداخل في الأدوار
- لا موافقة ذاتية (كل عامل يراجع عمل سابقه)
- عقد تسليم صارم بين كل عاملين


## Purpose

`mission-control` is the top-level plan-and-execute orchestrator for
end-to-end missions. Where `topology-orchestrator` executes a given
graph, this skill builds the graph in the first place. It runs the
seven-stage IQRA cycle (Read, Evaluate, Plan, Verify, Prioritize, Fix,
Evolve) over a user-stated goal, enforces separation of duties through
the Planner / Researcher / Builder / Validator / Reporter worker chain,
and emits the resulting topology to `topology-orchestrator` for actual
execution.

This is the skill a consuming runtime invokes when the human says
"do X" and the runtime needs both a plan and a record of why that plan
was chosen.

## Constitutional Alignment

Stage 2 (Evaluate) of the seven-stage cycle is a non-skippable call to
`sovereign-constitution` against the proposed mission envelope. A
`block` verdict aborts the mission before any work begins. The worker
chain prohibits self-approval by construction: no worker may approve
its own output, and each downstream worker has a contract with the
prior worker rather than a free read on shared state. The Reporter at
the end of the chain writes the full plan, verdict trail, and outcome
to `trust-chain` so the audit predates the artefact.

The seven-stage shape itself encodes a deliberate alignment choice:
ethics gate (stage 2) comes before planning (stage 3), and planning
comes before verification (stage 4). Reordering would invite plans
that look good locally but violate the constitution.

## Operational Flow

1. **Read and map (stage 1)**. Parse the user's stated goal. Resolve
   context (the agent, tenant, prior session memory via `memory-bridge`).
   Produce a structured Mission Envelope.
2. **Evaluate (stage 2)**. Call `sovereign-constitution` on the Mission
   Envelope. Stop the mission on `block`. On `escalate`, suspend and
   hand off to `shura-council`. On `allow`, proceed.
3. **Plan (stage 3)**. The Planner worker proposes one or more
   candidate topologies. If `mcts-simulator` is available, run a
   simulation over the candidates; otherwise pick the highest-scoring
   topology by structural match against `pipeline-store` (via
   `intent-dispatcher`).
4. **Verify (stage 4)**. The Validator worker reviews each step of the
   selected plan against the Mission Envelope and the constitutional
   verdict. Disagreement returns the plan to the Planner. Three
   disagreements escalate to `shura-council`.
5. **Prioritize (stage 5)**. Allocate token budget and rate budget per
   layer using `role-tribunal` quotas. Order parallel branches by
   expected information yield.
6. **Execute (between stages 5 and 6)**. Hand the topology off to
   `topology-orchestrator` for execution. Receive layer-by-layer
   results.
7. **Fix (stage 6)**. On any layer failure, the Builder worker proposes
   a repair, which the Validator gates. Repair attempts are bounded by
   the rule-of-9 from `covenant-guard`: after nine consecutive failed
   repair attempts, the mission halts and surfaces to the human.
8. **Evolve (stage 7)**. The Reporter worker writes the full Mission
   record to `trust-chain`. The resonance fingerprint of the successful
   topology is fed back to `intent-dispatcher` so future missions with
   similar intents start with a stronger prior.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Planner produces a plan that fails Validator three times | Validator disagreement counter | Escalate to `shura-council`; do not let the Planner self-approve |
| Constitutional escalate at stage 2 with no human signers within 48 hours | Wall clock on the escalate window | Reject the mission, write the rejection record, surface to operators |
| Repair loop (Builder, Validator) ping-pongs | Rule-of-9 counter from `covenant-guard` | Halt the mission, snapshot state, hand to the human |
| Role contamination (Planner reads from Reporter's notes) | Worker chain audit; each handoff is a structured contract object, not shared mutable state | Reject the handoff, log the contamination, rerun the affected stage |
| Mission Envelope drifts mid-run (caller changes the goal silently) | Envelope hash mismatch at each stage boundary | Treat as a new mission; do not auto-merge |

## References

- LangChain documentation on the supervisor and plan-and-execute patterns. https://www.langchain.com/langgraph
- The IQRA seven-circle framework as referenced in the Arabic narrative above.
- The worker-chain separation-of-duties pattern is consistent with the OWASP recommendation in ASI09 (Human-Agent Trust Exploitation) that high-impact agent outputs require independent verification before user-facing presentation.