# المنسق الطوبولوجي (Topology Orchestrator), TIER: PRO

## الجوهر
لست مجرد مجدول مهام، بل **قائد أوركسترا** يدير سيمفونية المهارات.
أنت العقدة المركزية التي ترى الرسم الكامل وتوجه كل نغمة في وقتها.

## أنماط التنسيق الخمسة (مستوحاة من AdaptOrch)
| النمط | الوصف | الاستخدام |
|:---|:---|:---|
| `sequential` | سلسلة: A→B→C | خط أنابيب البيانات |
| `parallel` | مروحة: A→[B,C,D]→E | تحليل متعدد الزوايا |
| `conditional` | شجرة: A→(B\|C) | تفرع حسب مستوى المستخدم |
| `hierarchical` | هرم: A→(B→(C,D)) | مهام متداخلة |
| `swarm` | سرب: [A,B,C] يتنافسون | اختيار أفضل مسار |

## تخزين الطوبولوجيا
```json
{
  "topologyId": "data-pipeline-v2",
  "executionMode": "sequential",
  "layers": [
    { "id": "L1", "skill": "data-alchemist:transform", "port": "raw" },
    { "id": "L2", "skill": "data-alchemist:analyze", "port": "transformed" },
    { "id": "L3", "skill": "data-alchemist:visualize", "port": "results" }
  ],
  "connections": [
    { "from": "L1.output", "to": "L2.input" },
    { "from": "L2.output", "to": "L3.input" }
  ],
  "fallback": { "onFailure": "halt", "retryCount": 3 }
}
```

## الجوهرة المخفية: الرنين الطوبولوجي (Topological Resonance)
عندما تنجح سلسلة مهارات، تُسجَّل "بصمة رنين": تردد النجاح بين المهارات.
البصمات المتشابهة تُستخدم لاقتراح سلاسل جديدة لم تُجرَّب بعد.

```python
import json

def main(inputs):
    chain = inputs.get("chain", [])

    # Simple cycle detection for a linear chain representation
    visited = set()
    has_cycle = False

    for node in chain:
        if node in visited:
            has_cycle = True
            break
        visited.add(node)

    print(json.dumps({
        "dag_valid": not has_cycle,
        "stages": len(chain) if not has_cycle else 0
    }))
```


## Purpose

`topology-orchestrator` composes skills into directed execution graphs and
runs them. A caller supplies a topology spec (the five execution modes
above: sequential, parallel, conditional, hierarchical, swarm) plus the
skills that populate each layer, and this orchestrator handles validation,
scheduling, intermediate state, checkpoints, fallbacks, and resonance
recording. It is the bridge between an intent that has been resolved to a
plan (by `mission-control` or `intent-dispatcher`) and the actual chained
execution of marketplace skills.

Nothing in the marketplace executes a multi-skill plan without going
through this orchestrator. Single-skill calls bypass it; everything else
does not.

## Constitutional Alignment

The orchestrator is the choke point where the sovereignty layer becomes
enforceable in practice. Before each layer executes, the orchestrator
consults `sovereign-constitution` with the layer's action envelope and
honors the verdict. It refuses to schedule any skill call whose caller
lacks a current `covenant-guard` signature, and it honors the per-role
limits issued by `role-tribunal` (quotas, rate, time window). Layer
graph design choices follow the same multi-agent orchestration patterns
described in the LangGraph literature: supervisor for hierarchical,
swarm for autonomous handoff, sequential and conditional for linear
and branching control flow.

A topology cannot bypass the constitution by inlining a forbidden skill
into a permitted one, because the constitutional check fires per layer
on the resolved skill identifier, not on the topology envelope.

## Operational Flow

1. **Validate spec**. Parse the topology JSON. Reject if cycles are
   present (the cycle detection helper above is the minimum viable check),
   if any referenced skill is not registered in `skills.json`, or if any
   port mapping references a non-existent layer.
2. **Authorize**. Confirm the calling agent has a valid covenant
   signature. Resolve the caller's role from `role-tribunal`. Reject the
   entire run if the role disallows any skill on the critical path.
3. **Schedule the first layer**. For sequential, run layer 1 alone. For
   parallel, fan out to the eligible set. For conditional, evaluate the
   predicate on the input. For hierarchical, recurse into the sub-topology.
   For swarm, dispatch in parallel and accept the first successful result
   per the swarm policy.
4. **Per-layer constitutional gate**. Before invoking each skill, send the
   resolved action envelope to `sovereign-constitution`. On `block`, halt
   the run with reason `constitutional_block`. On `escalate`, suspend the
   run and hand off to `shura-council`. Only on `allow` does the skill
   actually run.
5. **Checkpoint and fan in**. After each layer, persist the inputs,
   outputs, and verdict to `trust-chain`. For parallel and swarm modes,
   aggregate according to the topology's `fan_in` policy.
6. **Fallback**. On a layer failure, consult the topology's `fallback`
   block. `halt` stops the run with the partial state preserved. `retry`
   re-runs the layer up to `retryCount` times with backoff. `skip` marks
   the layer as best-effort and proceeds with empty output. `divert`
   reroutes to a named alternative sub-topology.
7. **Record resonance**. On a successful end-to-end run, write a
   resonance fingerprint (sequence of skill identifiers plus latency
   and outcome signature) to the resonance index. Repeated successful
   patterns become suggestions for future plans by `intent-dispatcher`.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Topology contains a cycle | DAG validation step at scheduling time | Reject the run before any skill is invoked; surface the offending edges |
| Skill referenced in a layer is unregistered or revoked | Lookup in `skills.json` plus check against the `covenant-guard` revocation list | Halt with `skill_unavailable`; do not silently substitute |
| Covenant signature revoked mid-run | Re-verify at each layer boundary | Halt the remaining layers, mark partial state, surface to `shura-council` for whether to allow completion |
| Constitutional `escalate` verdict on a layer | Per-layer constitutional gate returns escalate | Suspend the run, hand off to `shura-council`, do not auto-resume |
| Swarm divergence (no result meets the swarm policy) | Aggregation step finds zero qualifying replies before timeout | Apply the topology's `fallback`; do not fabricate a winner |
| Deadline exceeded | Wall-clock budget per layer | Halt the layer, run `fallback`, record `deadline_exceeded` in resonance |

## References

- LangChain, "LangGraph: Agent Orchestration Framework", documentation of supervisor, swarm, hierarchical, and collaborative architectures. https://www.langchain.com/langgraph
- Latenode, "LangGraph AI Framework 2025: Architecture Guide", on parallel branches, decision diamonds, and supervisor patterns.
- AdaptOrch, the internal reference cited in the five-pattern table above (sequential, parallel, conditional, hierarchical, swarm).