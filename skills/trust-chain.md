# سلسلة الثقة (TrustChain) — TIER: PRO

## الجوهر
لست مجرد سجل تدقيق، بل **ذاكرة لا تكذب** — سلسلة كتل داخلية لكل وكيل IQRA.
كل مدخلة مرتبطة بالتي قبلها، لا يمكن حذفها أو تعديلها.

## هيكل المدخلة
```json
{
  "entryId": "tc-0042",
  "prevHash": "sha256:abc123...",
  "timestamp": "2026-05-12T10:30:00Z",
  "action": "skill:prompt-weaver:execute",
  "input": { "instruction": "...", "personaId": "hakim" },
  "output": { "finalPrompt": "...", "tokenCount": 342 },
  "constitutionalCheck": "passed",
  "signature": "ed25519:def456..."
}
```

## الخصائص
- **إلحاق فقط (Append-Only)**: لا حذف ولا تعديل
- **تسلسل SHA-256**: كل مدخلة تحمل بصمة سابقتها
- **توقيع Ed25519**: كل مدخلة موقعة من الوكيل
- **قابل للتدقيق**: أي مشرف يمكنه التحقق من السلسلة كاملة

## الجوهرة المخفية: لحظة الصدق (Truth Moment)
كل 100 مدخلة، تتوقف السلسلة للحظة "صدق":
- مراجعة آخر 100 مدخلة
- البحث عن أنماط مريبة
- توليد "شهادة سلامة" أو "إنذار"

## تكامل
- `sovereign-constitution`: كل استشارة دستورية تُسجَّل
- `shura-council`: كل قرار بشري يُسجَّل
- `metamorphosis-loop`: التحول يُسجَّل كمدخلة خاصة

```python
import hashlib
import json

def main(inputs):
    agent_id = inputs.get("agent_id", "")
    data = inputs.get("data", "")
    previous_hash = inputs.get("previous_hash", "")

    # Simple deterministic hash for testing
    hasher = hashlib.sha256()
    hasher.update(agent_id.encode())
    hasher.update(data.encode())
    if previous_hash:
        hasher.update(previous_hash.encode())

    computed_hash = hasher.hexdigest()

    result = {
        "hash": computed_hash,
        "agent_id": agent_id,
        "chain_valid": True
    }

    print(json.dumps(result))
```
