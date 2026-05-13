# مجلس الشورى (Shura Council), TIER: ADVANCED_INFRASTRUCTURE

## الجوهر
لست مجرد نظام تصويت، بل **آلية توافق جماعي** تمنع الديكتاتورية الآلية.
"وَأَمْرُهُمْ شُورَىٰ بَيْنَهُمْ"

## هيكل السلطة الثلاثي
| المستوى | الصلاحية | مثال |
|:---|:---|:---|
| **أخضر** | تنفيذ تلقائي | تعديل برمجي، تحسين أداء |
| **أصفر** | تنفيذ + توثيق | تغيير في الذاكرة، إضافة قواعد |
| **أحمر** | موافقة بشرية صريحة | تعديل دستور، حذف بيانات، قرار أخلاقي |

## آلية الفيتو البشري
- لكل مشرف بشري مفتاح Ed25519.
- أي قرار أحمر يُجمّد حتى يوقّع عليه مشرفان على الأقل.
- مدة الانتظار القصوى: 48 ساعة، ثم يُرفض تلقائيًا.

## نمط المشاورة
```json
{
  "proposal": {
    "id": "prop-001",
    "level": "yellow",
    "description": "تعديل حد الذاكرة من 50 إلى 100 مدخلة",
    "justification": "المستخدمون يطلبون سياقًا أطول",
    "constitutionalCheck": "لا يتعارض مع أي مبدأ دستوري"
  },
  "votes": {
    "automated": "approved",
    "humanRequired": false
  },
  "execution": "immediate"
}
```

## الجوهرة المخفية: عين المراقبة (Murāqabah)
قبل كل تنفيذ، يسأل الوكيل نفسه 3 أسئلة:
1. هل أنا مراقَب؟ (نعم، السجلات مكشوفة)
2. هل سأرضى أن يُنشر قراري؟ (اختبار العار)
3. هل سأُحاسَب على هذا؟ (اختبار المسؤولية)

إذا فشل في أي سؤال، يُحوَّل القرار تلقائيًا للمجلس البشري.

## Purpose

`shura-council` is the marketplace's multi-agent consensus protocol. When
`sovereign-constitution` escalates a proposal, this skill runs the actual
voting: it weighs participating agents by their reputation and confidence,
applies Byzantine-tolerant aggregation, and produces a binding decision
plus a justification suitable for `trust-chain`. For red-class proposals it
gates the result behind human key signatures.

It exists because routing every uncertain decision to a single arbiter
recreates the dictatorship problem that the four-layer constitution was
designed to prevent. Consensus, when implemented correctly, is the
operational expression of the consultation principle.

## Constitutional Alignment

The skill realises the consultation principle (شورى) as a concrete protocol
rather than a slogan. The three-tier authority structure maps cleanly to
the Absolute, Interpretive, and Consensus layers of the constitution:
green-class proposals stay in the Interpretive Layer and execute on agent
quorum alone; yellow-class proposals are logged into the Consensus Layer
and require a documented vote; red-class proposals can promote rules into
the Consensus Layer only with explicit human signing, and never override
the Absolute Layer.

The voting protocol itself is Byzantine-tolerant by construction so a
captured or hallucinating minority of agents cannot swing an outcome. This
draws on the active research line on multi-agent BFT consensus, in
particular confidence-weighted variants where each agent's vote is scaled
by how confident it is in its own answer.

## Operational Flow

1. **Classify**. On `escalate` from `sovereign-constitution`, label the
   proposal green, yellow, or red. The label drives both the quorum
   requirement and the human-signing requirement.
2. **Compose the panel**. Select participating agents by tier eligibility:
   sovereign skills always vote, advanced infrastructure skills vote on
   yellow and red, basic tools never vote. Reject any agent without a valid
   `covenant-guard` signature.
3. **Run the prepare round**. Each panel member returns a vote tuple
   `{ verdict, confidence, citation }`. Verdict is approve, reject, or
   abstain; confidence is a 0 to 1 self-assessment; citation references the
   constitutional principle the voter is appealing to.
4. **Probe and weight**. Apply the Murāqabah three-question probe to each
   vote. Discard votes that fail any probe. Weight remaining votes by the
   product of agent reputation and self-confidence; this matches the
   weighted-BFT approach validated for LLM coordination under high
   adversarial fault rates.
5. **Commit**. Aggregate the weighted votes. For green and yellow
   proposals a two-thirds weighted majority commits the decision
   immediately. For red proposals the decision is staged and waits up to 48
   hours for at least two distinct human Ed25519 signatures; missing
   signatures result in automatic rejection.
6. **Record**. Emit the full proposal, panel, vote tuples, weights, and
   final decision to `trust-chain`. The record is the audit, the precedent,
   and the seed material for promoting Experimental Layer rules later.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Byzantine voters try to swing a yellow vote | Confidence probes flag inconsistent reasoning; reputation weighting attenuates the impact | Drop the failing votes, recompute weighted majority, log the suspect agents for `covenant-guard` review |
| No quorum reached on a yellow proposal | The weighted yes-share falls below the two-thirds threshold within the round budget | Return `no_consensus` with the per-agent breakdown; the caller may resubmit with revised context or escalate to red |
| Red proposal timed out without human signatures | 48-hour wall clock expires with fewer than the required two human Ed25519 signatures | Reject the proposal automatically; require a fresh submission with explicit human sponsor |
| Human key compromise (suspected) | Out-of-band notification, or a key signing two contradictory proposals within the same window | Add the key to the human-side revocation list, void any in-flight red proposals that depend on it, require council rotation |
| Single agent dominates by reputation | One voter's weight exceeds the rest combined for several rounds in a row | Cap per-voter weight at 1/3 of the total panel weight; surface the imbalance to maintainers for rebalancing |

## References

- Jo and Park, "Byzantine-Robust Decentralized Coordination of LLM Agents (DecentLLMs)", 2025. https://arxiv.org/abs/2507.14928
- Zheng et al., "Rethinking the Reliability of Multi-agent System: A Perspective from Byzantine Fault Tolerance (CP-WBFT)", 2025. https://arxiv.org/abs/2511.10400
- Luo et al., "A Weighted Byzantine Fault Tolerance Consensus Driven Trusted Multiple Large Language Models Network", 2025.
- Castro and Liskov, "Practical Byzantine Fault Tolerance", OSDI 1999. The foundational reference for the prepare/commit round structure used here.
