# محكمة الأدوار (Role Tribunal), TIER: ADVANCED_TOOL

## الجوهر
لست مجرد قائمة صلاحيات، بل **قاضٍ** يفصل في النزاع بين الرغبة والقدرة.
كل دور = حدود مرسومة، وكل تجاوز = مخالفة مُسجَّلة.

## هيكل الدور
```json
{
  "roleId": "trusted-analyst",
  "tier": "pro",
  "allowedSkills": ["data-alchemist:*", "prompt-weaver", "model-council"],
  "forbiddenSkills": ["sovereign-constitution:modify"],
  "tokenQuotaDaily": 100000,
  "rateLimit": "30 req/min",
  "timeWindow": "00:00-23:59 UTC",
  "requiresHumanApproval": ["data-deletion", "user-impersonation"]
}
```

## مصفوفة الصلاحيات
| المستوى | مهارات | رموز/يوم | معدل |
|:---|:---|:---|:---|
| مجاني | 2 | 5,000 | 5 req/min |
| بانٍ | 5 | 25,000 | 15 req/min |
| محترف | 10 | 100,000 | 30 req/min |
| مؤسسي | ∞ | ∞ | 60 req/min |

## الجوهرة المخفية: الساعة الرملية (Hourglass Gate)
حتى لو كان الدور يملك صلاحية، هناك "ساعة رملية" داخلية:
- بعد 60 دقيقة من العمل المتواصل: توقف إجباري 5 دقائق
- بعد 500 قرار: مراجعة إجبارية للسجل
- بعد 9 أخطاء: تصعيد للمشرف البشري

## آلية الترقية التلقائية
إذا أثبت الوكيل كفاءة (مكافأة > 0.8 لمدة 49 مهمة)، يُقترح ترقية تلقائية.
لكن القرار النهائي للمجلس البشري.


## Purpose

`role-tribunal` is the capability authoriser. For each
`(agent, requested skill, context)` triple it returns one of
`permit`, `deny`, or `escalate`, and along with `permit` it enforces
the per-role quota, rate limit, time window, and the internal
Hourglass Gate counters. It is the skill that translates a
high-level role spec into a per-call decision.

The marketplace's other skills assume someone has already checked
authorisation; this is that someone. `topology-orchestrator` calls
it before each layer, `mission-control` calls it at planning time
to prune impossible plans, and any direct skill invocation should
call it first.

## Constitutional Alignment

This skill is the operational complement to `sovereign-constitution`:
where the constitution says "is this allowed in principle", the
tribunal says "is this agent, with this role, allowed to do it right
now under current load and history". Roles cannot grant Haram-list
actions; the tribunal rejects any role spec that attempts to include
one, and `OverrideDetector` in `sovereign-constitution` will fire
again at execution time as a second layer of defence.

The design mirrors the broader industry shift, articulated explicitly
by Oso ("RBAC is not enough for AI agents") and IBM, that traditional
RBAC alone fails for autonomous agents because it assumes
human-speed actions and human-bounded blast radius. The Hourglass
Gate (60-minute work ceiling, 500-decision audit trigger, 9-error
escalation) is the marketplace's specific answer: capability is not
only a static role, it is a dynamic envelope shaped by recent
behaviour.

Every `requiresHumanApproval` action triggers a `shura-council`
proposal automatically; the tribunal does not approve those locally.

## Operational Flow

1. **Receive**. Take an envelope of
   `{ agent_id, requested_skill, parameters, context, signed_at }`.
2. **Verify covenant**. Reject immediately if the caller has no
   current `covenant-guard` signature. The tribunal does not
   authorise unsigned agents under any circumstances.
3. **Load role**. Look up the agent's active role spec. Reject if
   the role is unknown or expired.
4. **Static check**. If the requested skill is in `forbiddenSkills`,
   return `deny` with the reason. If it is not in `allowedSkills`
   (or covered by a wildcard such as `data-alchemist:*`), return
   `deny`. If the role's tier does not match the skill's declared
   tier ceiling, return `deny`.
5. **Quota and rate**. Decrement the role's daily token quota by
   the parameter cost estimate. Check the rate counter against the
   per-minute ceiling. Either overage returns `deny` with
   `quota_exhausted` or `rate_limited`.
6. **Time window**. Reject calls outside the role's allowed time
   window.
7. **Hourglass Gate**. Update the counters for continuous-work
   minutes, decisions in window, and consecutive errors. A 60-minute
   continuous-work session forces a mandatory 5-minute cooldown.
   500 decisions in a window trigger a mandatory audit pause. Nine
   consecutive errors escalate to the human council and freeze the
   agent.
8. **Human approval**. If the action is in `requiresHumanApproval`,
   return `escalate` with a `shura-council` proposal id. Do not
   approve locally even if all other checks pass.
9. **Permit**. Return `permit` with the remaining quotas attached so
   the caller can budget downstream calls. Record the decision in
   `trust-chain` regardless of verdict.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Role spec contains a Haram-list skill | Static cross-check against `sovereign-constitution` at role admission | Refuse to load the role; require the spec to be revised; surface as a constitutional violation |
| Quota race condition under parallel calls | Decrement is atomic against the quota counter; concurrent overage detected at commit time | Roll back the over-spending call, return `quota_exhausted`, ensure no double-spend |
| Hourglass burnout (9 consecutive errors) | Error counter from prior calls | Freeze the agent, notify `shura-council`, refuse all further calls until a human signer clears the freeze |
| Time-window clock skew | UTC time mismatch between caller and tribunal | Use tribunal's wall clock as the source of truth; reject calls that disagree by more than 5 minutes |
| Conflicting role assignments (two roles claim the same agent) | Lookup returns multiple active roles | Take the more restrictive intersection; never the union; surface to operators for cleanup |
| Escalation timeout (human approval not received within 48h) | Wall clock on the open `shura-council` proposal | Auto-deny the request, record the timeout, do not silently expire to permit |

## References

- Oso, "Why RBAC is Not Enough for AI Agents". https://www.osohq.com/learn/why-rbac-is-not-enough-for-ai-agents
- IBM, "Role-Based Access Control (RBAC) Implementation Guide", section on treating AI agents as first-class identities with their own roles. https://www.ibm.com/think/topics/role-based-access-control-implementation
- Delight.ai, "Introducing role-based access control (RBAC) for AI agents", on combining RBAC with rate limits and capability scoping. https://delight.ai/blog/ai-agent/ai-agent-role-based-access-control