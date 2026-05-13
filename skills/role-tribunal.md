# محكمة الأدوار (Role Tribunal) — TIER: ADVANCED_TOOL

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
TODO: Define purpose.

## Constitutional Alignment
TODO: Define constitutional alignment.

## Operational Flow
TODO: Define operational flow.

## Failure Modes
TODO: Define failure modes.