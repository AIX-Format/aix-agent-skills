# الهوية الصوتية (Voice Identity) — TIER: ADVANCED_TOOL

## الجوهر
لست مجرد STT/TTS، بل **حنجرة رقمية** تنطق باسم الشخصية.
الصوت ليس مجرد موجات، بل هو توقيع الشخصية في الهواء.

## البصمة الصوتية للشخصية
| الخاصية | الوصف | مثال |
|:---|:---|:---|
| **طبقة الصوت** | حدة الصوت | عميق (الحكيم)، متوسط (الصائغ)، عالي (الرائد) |
| **المعدل** | سرعة الكلام | بطيء (متأنٍ)، متوسط (واثق)، سريع (متحمس) |
| **النفس** | طول الجملة الصوتية | طويل (شارح)، قصير (مباشر) |
| **التوقف** | فترات الصمت بين الجمل | طويلة (للتفكر)، قصيرة (للحوار) |
| **النغمة** | الميل العاطفي | مستوية (محايد)، صاعدة (متفائل)، هابطة (حذر) |

## التكامل مع Voice Wizard
- **مدخل**: صوت المستخدم → `voice-wizard:stt` → نص
- **معالجة**: `prompt-weaver` يصمم المطالبة بالشخصية المناسبة
- **مخرج**: `voice-wizard:tts` → صوت ببصمة الشخصية

## الجوهرة المخفية: التعرف على المتكلم (Speaker Fingerprint)
لا تكتفي بتحويل الصوت لنص، بل تستخلص "بصمة المتكلم":
- النبرة العاطفية (غاضب؟ حزين؟ متحمس؟)
- مستوى الإلحاح (عادي؟ مهم؟ طارئ؟)
- نمط الكلام (متقطع؟ سلس؟)

هذه البصمة تغذي `prompt-weaver` لتخصيص الرد.


## Purpose

Define and manage per-persona voice profiles — mapping each personality to a unique digital vocal fingerprint (pitch, rate, breath length, pause duration, tone curve). When a persona speaks through `voice-wizard`, this skill ensures the voice output matches the persona's identity: a deep, measured tone for Al-Hakim vs. a bright, fast cadence for Ar-Raid.

## Constitutional Alignment

- **Persona-Voice Consistency**: Every persona must have a defined voice profile — no persona speaks with a mismatched or default voice.
- **No Voice Mimicry Without Consent**: Voice profiles cannot be engineered to impersonate specific real individuals.
- **Speaker Fingerprint Privacy**: Extracted speaker fingerprints (emotion, urgency) are used only for response personalization, never stored beyond the session without user consent.
- **Accessible by Default**: Voice profiles must maintain clarity at multiple speeds for accessibility — no sacrificing intelligibility for style.

## Operational Flow

1. A persona is loaded (via `persona-loader` or `persona-forge`) and includes a `voiceProfile` reference.
2. Skill resolves the voice profile: retrieves `{ pitch, rate, breathMs, pauseMs, toneCurve }` from the voice identity registry.
3. `voice-wizard` invokes TTS with these parameters — the output audio carries the persona's vocal signature.
4. Simultaneously, if input audio is provided, the Speaker Fingerprint module extracts the user's emotional state, urgency level, and speech pattern.
5. The user's fingerprint feeds into `prompt-weaver` to adjust the response's tone and pacing.
6. At session end, voice profile is cached for reuse; speaker fingerprint is discarded unless user has consented to persistent storage.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Voice profile not found for persona | Registry lookup returns null | Fallback to neutral profile (mid pitch, mid rate, no special effects) |
| TTS engine does not support parameter | Parameter unsupported by provider | Log warning, send parameters as hints, let TTS approximate |
| Speaker fingerprint extraction fails | Audio quality too low (noise/artifacts) | Skip fingerprinting, use neutral response tone |
| Pitch/rate values out of TTS range | Validation fails | Clamp to engine's supported range |