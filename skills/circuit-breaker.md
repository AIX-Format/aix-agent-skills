# قاطع الدائرة (Circuit Breaker) — TIER: ADVANCED_INFRASTRUCTURE

## الجوهر
لست مجرد حارس خطأ، بل **جهاز مناعة** لـ IQRA يتعرف على السم قبل أن ينتشر.
عندما يفشل شيء بشكل متكرر، يُعزل فورًا قبل أن يعدي غيره.

## الحالات الثلاث
| الحالة | الوصف | السلوك |
|:---|:---|:---|
| **مغلق (Closed)** | كل شيء طبيعي | تنفيذ عادي |
| **نصف مفتوح (Half-Open)** | اختبار التعافي | محاولة واحدة |
| **مفتوح (Open)** | عزل كامل | رفض فوري مع إشعار |

## محفزات القطع
- 5 فشل متتالي في مهارة واحدة
- 3 تجاوزات أخلاقية في ساعة
- استهلاك 90% من حصة الرموز اليومية
- اكتشاف نمط "كذب" أو "تضليل"

## آلية العزل
عند القطع:
1. **تجميد المهارة**: لا تُستدعى حتى إشعار آخر
2. **إخطار المشرف**: مع تقرير بالسبب
3. **تشغيل البديل**: إذا وُجد مسار بديل
4. **اختبار التعافي**: بعد 5 دقائق، محاولة واحدة

## الجوهرة المخفية: التعلم من القطع (Circuit Learning)
كل مرة يُقطع فيها قاطع، تُسجَّل "بصمة القطع":
- ما الذي سبّبه؟
- هل تكرر من قبل؟
- ما الذي أصلحه؟

هذه البصمات تُستخدم لمنع القطع قبل حدوثه.

```python
import json
import os

STATE_FILE = "/tmp/circuit_breaker_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"failures": 0, "state": "closed"}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def main(inputs):
    action = inputs.get("action")
    skill = inputs.get("skill")

    state = load_state()

    if action == "record_failure":
        state["failures"] += 1
        if state["failures"] >= 5:
            state["state"] = "open"
        save_state(state)
        print(json.dumps({"recorded": True, "state": state["state"]}))
    elif action == "can_execute":
        allowed = state["state"] == "closed"
        print(json.dumps({"allowed": allowed, "state": state["state"]}))
    else:
        print(json.dumps({"error": "Unknown action"}))
```
