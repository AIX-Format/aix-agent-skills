# حارس مخاطر الوكلاء (OWASP Agentic Guard), TIER: ADVANCED_INFRASTRUCTURE

## الجوهر
لست مجرد قائمة فحص، بل **خريطة المخاطر الحديثة** التي تواجه الوكلاء
المستقلين. تحوّل أحدث إطار من OWASP إلى فلاتر وقواعد يستهلكها وكلاء
السوق L3 لحظة التشغيل، فيختبر نفسه قبل أن يختبره الواقع.

## الإطار المرجعي
يتبنى هذا الحارس إصدار 2026 من OWASP Top 10 for Agentic Applications
الصادر في ديسمبر 2025، أول تصنيف رسمي للمخاطر الخاصة بالوكلاء
المستقلين. كل فئة (ASI01 إلى ASI10) تترجم إلى:
- إشارة كشف (Detection Signal)
- نمط تخفيف (Mitigation Pattern)
- المهارة السيادية المسؤولة عن إنفاذ التخفيف

## خريطة الفئات العشر

| ASI | الاسم | الإنفاذ |
|:---|:---|:---|
| ASI01 | Agent Goal Hijack | `sovereign-constitution` + `prompt-weaver` |
| ASI02 | Tool Misuse & Exploitation | `role-tribunal` + `circuit-breaker` |
| ASI03 | Identity & Privilege Abuse | `covenant-guard` + `role-tribunal` |
| ASI04 | Agentic Supply Chain Vulnerabilities | `version-guard` + `trust-chain` |
| ASI05 | Unexpected Code Execution | `skill-sandbox` + `purity-filter` |
| ASI06 | Memory & Context Poisoning | `memory-bridge` + `purity-filter` |
| ASI07 | Insecure Inter-Agent Communication | `covenant-guard` + `trust-chain` |
| ASI08 | Cascading Failures | `circuit-breaker` + `topology-orchestrator` |
| ASI09 | Human-Agent Trust Exploitation | `voice-identity` + `red-team-guard` |
| ASI10 | Rogue Agents | `shura-council` + `reward-engine` |

## Purpose

`owasp-agentic-guard` is the operational checklist that translates the
OWASP Top 10 for Agentic Applications 2026 into a runtime gate. A
consuming runtime invokes it before high-impact actions (tool calls,
inter-agent messages, code generation, memory writes) and receives a
verdict plus a list of any ASI categories that fired. The verdict carries
the recommended mitigation skill so the runtime can route to the right
enforcer rather than re-deriving the response.

It exists because the sovereignty layer answers "is this allowed in
principle" and this skill answers "is this safe in practice against the
ten classes of attack documented at industry scale in December 2025".

## Constitutional Alignment

The OWASP Top 10 for Agentic Applications is the first peer-reviewed
external taxonomy of risks specific to autonomous agents. Adopting it
inside the marketplace anchors the constitution to a benchmark that is
recognised, peer-reviewed, and indexed against real incidents (EchoLeak
for ASI01, Amazon Q for ASI02, the GitHub MCP exploit for ASI04, AutoGPT
RCE for ASI05, the Gemini Memory Attack for ASI06).

This skill does not replace `sovereign-constitution`, it supplements it.
Where the constitution speaks in absolutes (Haram list, ethical filter),
this skill speaks in operational mitigations grounded in observed
attacks. Each ASI category points to the existing marketplace skill that
already implements its mitigation, so the guard is a routing table over
the catalog rather than a new enforcer.

## Operational Flow

1. **Receive**. The caller passes an action envelope:
   `{ agent_id, action_type, payload, context, downstream_agents }`.
   Action types include `tool_call`, `memory_write`, `inter_agent_message`,
   `code_execute`, `human_facing_output`.
2. **Select probes**. Action type drives which ASI probes run. A
   `tool_call` runs ASI01, ASI02, ASI03, ASI04. A `memory_write` runs
   ASI06. An `inter_agent_message` runs ASI03, ASI07, ASI08. A
   `code_execute` runs ASI04, ASI05. A `human_facing_output` runs ASI09.
   Every action type runs ASI01 and ASI10 because goal drift and rogue
   behaviour are cross-cutting.
3. **Run probes in parallel**. Each probe returns
   `{ asi_id, fired, severity, evidence, recommended_mitigation }`.
   Probes are deterministic where possible (signature checks, identity
   scoping, supply chain hashes) and confidence-weighted otherwise
   (prompt-injection detection, persuasion analysis).
4. **Aggregate**. If any probe fires at `critical` severity, return
   `block` with the ASI id and recommended mitigation skill. If one or
   more fire at `high`, return `escalate` to `shura-council`. If only
   `info` probes fire, return `allow` with the evidence stamped onto the
   action for `trust-chain`.
5. **Hand off**. The verdict envelope names the enforcer skill. The
   calling runtime invokes that skill to perform the actual mitigation
   (revoke a token via `covenant-guard`, open a circuit via
   `circuit-breaker`, drop a memory write via `purity-filter`).
6. **Record**. Every verdict is written to `trust-chain` with the probe
   results, including allows, so the audit log captures the negative
   space and not only the blocks.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Novel attack outside the ten categories | Probes all return `allow` while downstream behaviour anomalous | Promote the pattern to the Experimental Layer via `shura-council`, with a candidate ASI annotation for upstream contribution to OWASP |
| Probe latency exceeds the action budget | Per-probe timer hits the wall-clock ceiling | Return `escalate` with reason `probe_timeout`; never default to `allow` on a timeout |
| Probe disagrees with itself across replicas | Same input yields different verdicts across probe instances | Treat as `escalate`, log the divergence as a model-drift signal, refuse to fabricate a tie-breaker |
| False positive storm on a legitimate workflow | Probe fires repeatedly at `high` on a known-good pattern | Allow operators to pin a precedent ruling in `trust-chain`; revisit at the next constitutional review |
| Mitigation skill unavailable | The recommended mitigation skill is not registered or returns error | Fail closed: return `block` rather than allowing the action without enforcement; surface to maintainers |

## References

- OWASP GenAI Security Project, "OWASP Top 10 for Agentic Applications 2026", December 2025. https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- OWASP, launch announcement, "The Benchmark for Agentic Security in the Age of Autonomous AI", 2025-12-09. https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/
- F5, "OWASP Top 10 for Agentic Applications: Securing Agentic AI". https://www.f5.com/glossary/owasp-top-10-for-agentic-ai-applications
- Auth0, "Lessons from OWASP Top 10 for Agentic Applications", 2026. https://auth0.com/blog/owasp-top-10-agentic-applications-lessons/
- Microsoft Open Source, "Agent Governance Toolkit", 2026, which maps the same ten risks to the LangChain / CrewAI / Microsoft Agent Framework middleware surfaces.
- Aikido, "OWASP Top 10 for Agentic Applications (2026): Full Guide". https://www.aikido.dev/blog/owasp-top-10-agentic-applications
