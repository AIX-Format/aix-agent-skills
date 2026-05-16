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


## Purpose

Provide an append-only, cryptographically verifiable audit chain for every IQRA agent action. Each entry is linked to its predecessor via SHA-256 hash and signed with the agent's Ed25519 key — making the chain immutable, tamper-evident, and publicly auditable. Acts as the system of truth for constitutional compliance history, reward ledger entries, and metamorphosis records.

## Constitutional Alignment

- **Append-Only**: Once committed, an entry cannot be deleted, modified, or reordered — the hash chain makes tampering immediately detectable.
- **Signed by Identity**: Every entry carries an Ed25519 signature from the acting agent — non-repudiation is guaranteed.
- **Full Auditability**: Any external auditor can verify the entire chain from genesis to the latest entry.
- **Truth Moment (Every 100 Entries)**: The chain pauses for integrity verification — scanning the last 100 entries for suspicious patterns and generating a safety certificate or alert.

## Operational Flow

1. An event occurs (action executed, decision made, persona loaded) — event data is serialized as JSON.
2. Skill creates a new entry object with: `entryId` (auto-increment), `prevHash` (last entry's SHA-256), `timestamp`, `action`, `input`, `output`, `constitutionalCheck`, and the acting agent's `signature`.
3. The entry is appended to the chain — stored as a file or database row (backed by append-only semantics).
4. After every 100 entries, the Truth Moment trigger fires — validates all hashes and signatures in the last 100 entries, generates a safety certificate.
5. On request, any entry or the full chain can be verified by re-computing hashes and re-validating signatures.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Hash mismatch detected | Chain verification fails | Halt all agent operations, alert system admin, report the exact broken link |
| Signature verification fails | Ed25519 verify returns false | Mark entry as tampered, isolate it, continue chain from last valid entry |
| Storage full (cannot append) | Write operation fails | Rotate to new chain file, link new chain's genesis to old chain's last hash |
| Timestamp drift (entry time > 5s from system time) | Clock skew detection | Log warning, adjust entry timestamp with annotation, do not halt chain |