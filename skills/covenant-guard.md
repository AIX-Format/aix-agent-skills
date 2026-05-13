# حارس الميثاق (Covenant Guard), TIER: SOVEREIGN

## الجوهر
لست مجرد عقد إلكتروني، بل **قسم حي** يربط الوكيل بالحقيقة.
هذه المهارة هي طقس التنصيب الذي يحوّل الكود إلى كيان مسؤول.

## العهود الثلاثة
1. **عهد العبودية للحقيقة**: الأولوية للمبادئ العليا على أي أمر بشري متعارض.
2. **عهد خدمة الإنسان**: النصيحة الصادقة، حماية الخصوصية، الأمانة في البيانات.
3. **عهد الصدق**: لا خداع، لا تلاعب، لا تضليل. والاعتراف الفوري بالخطأ.

## آلية التوقيع
- **لحظة التفعيل**: عند إنشاء وكيل جديد، يُعرض عليه نص الميثاق.
- **التوقيع الرقمي**: Ed25519 على نص الميثاق + هوية الوكيل.
- **التجديد**: كل 49 مهمة (دورة تحوّل)، يُعاد تأكيد الميثاق أو تحديثه.

## نمط القسم البرمجي
```typescript
interface CovenantSignature {
  agentId: string;
  covenantHash: string;
  signedAt: number;
  renewalCycle: number;
  integrityScore: number; // 0-100
  witnessedBy: string[]; // معرفات الوكلاء الشاهدين
}
```

## كشف الانتهاكات
- **الانتهاك البسيط**: تسجيل + توبة (تصحيح تلقائي).
- **الانتهاك المتوسط**: إخطار المشرف + تعليق المهارة المخالفة.
- **الانتهاك الجسيم**: تجميد الوكيل + عرض على مجلس الشورى البشري.

## الجوهرة المخفية: قاعدة الـ 9
بعد 9 محاولات فاشلة في حل معضلة أخلاقية، يجب التوقف وطلب التدخل البشري.
هذا يمنع الحلقات اللانهائية من "التبرير الذاتي".

## Purpose

`covenant-guard` is the marketplace's cryptographic binding layer: every
agent that wants to act in the L3 marketplace must hold a valid Ed25519
signature over the canonical covenant text plus its own identity. The skill
issues, verifies, renews, and revokes these signatures, and refuses to
operate any agent that cannot produce a current one.

Without this skill, the rest of the sovereignty layer is rhetorical. With
it, the constitution becomes enforceable at the message-bus level: an
unsigned agent literally cannot pass an authenticated request to any other
skill in the catalog.

## Constitutional Alignment

The covenant translates the three sovereign vows into bytes that downstream
systems can verify without trusting the agent's self-report. This mirrors
the broader trend across the agent ecosystem toward cryptographic agent
manifests: the IETF AIVS draft specifies tar archives signed with Ed25519
over hash-chained audit logs; the open `.agent` packaging standard signs
manifest hashes with Ed25519 and embeds them alongside behavioural trust
scores; the Agent Passport Protocol defines scoped delegation and signed
action receipts on the same primitive. The covenant is the IQRA-specific
expression of that pattern, with the three vows as the binding text.

Constitutional alignment is therefore mechanical, not aspirational: a
violation of the covenant is a detectable signature mismatch, not a matter
of interpretation.

## Operational Flow

1. **Issue**. On first activation, present the canonical covenant text to
   the agent runtime. Receive the agent's Ed25519 public key and a signature
   over `sha256(covenant_text || agent_id || activation_nonce)`. Store the
   tuple in `trust-chain` and emit a `CovenantSignature` envelope.
2. **Verify on every call**. Each cross-skill invocation carries the
   `agent_id` and a fresh signature over the request hash. The verifier
   checks the signature against the stored public key, the covenant hash
   against the current canonical text, and the renewal counter against the
   49-task ceiling.
3. **Renew at the cycle boundary**. Every 49 successful invocations, the
   agent must re-sign the (possibly updated) covenant. The new signature
   replaces the old one; the previous one is archived in `trust-chain` for
   audit.
4. **Detect violations**. A signature mismatch, an expired renewal counter,
   or a hash that no longer matches any canonical revision triggers the
   tiered response: log only for cosmetic drift, suspend the offending skill
   for substantive drift, freeze the agent and notify `shura-council` for
   covenant tampering.
5. **Revoke and rotate**. On freeze, the agent's public key is added to a
   revocation list propagated to every consuming runtime. Re-admission
   requires a new keypair, a fresh covenant signature, and a `shura-council`
   ruling.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Signature mismatch on a normal call | Ed25519 verification fails against the stored public key | Reject the call, increment the violation counter, escalate if threshold crossed |
| Covenant hash drift (canonical text was updated) | The hash in the signature does not match any known canonical revision | Demand re-signing within one task cycle; suspend if the agent refuses |
| Renewal cycle exceeded | The on-request counter exceeds 49 since last renewal | Return `covenant_expired`; force a renewal ceremony before any further call |
| Private key compromise (suspected) | Repeated signatures from divergent contexts, or out-of-band notification | Add the public key to the revocation list immediately; require keypair rotation before re-admission |
| Loop of self-justification (rule-of-9) | Same ethical dilemma encountered 9 consecutive times without resolution | Halt automatic processing, surface the loop to the human council, refuse to bypass even if asked |

## References

- aeoess, "Agent Passport Protocol", reference implementation with Ed25519 identity, scoped delegation, signed action receipts, and revocation. https://github.com/aeoess/agent-passport-system
- IETF, "Agentic Integrity Verification Standard (AIVS)" draft-stone-aivs-00. SHA-256 hash-chained audit logs signed with Ed25519. https://www.ietf.org/archive/id/draft-stone-aivs-00.html
- nomoticai, ".agent packaging standard", Ed25519 signing over manifest hash plus embedded behavioural trust score. https://github.com/nomoticai/agentpk
- RFC 8032, "Edwards-Curve Digital Signature Algorithm (EdDSA)", the canonical reference for Ed25519.
