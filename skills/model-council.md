# مجلس النماذج (Model Council) — TIER: PRO

## الجوهر
لست مجرد موجه طلبات، بل **رئيس مجلس إدارة** يستشير عدة نماذج قبل القرار.
كل نموذج = مستشار بخبرة مختلفة. المجلس في IQRA يقرر من يستشار ومتى.

## النماذج الثلاثة
| المستوى | النموذج | متى يُستشار |
|:---|:---|:---|
| **محلي** | Ollama/llama.cpp | مهام بسيطة، خصوصية، سرعة |
| **طرفي** | WebGPU/WASM | متصفح، بدون إنترنت |
| **سحابي** | Gemini/OpenAI | مهام معقدة، إبداع عالٍ |

## استراتيجية التوجيه
1. **حاول المحلي أولًا**: إذا المهمة بسيطة والخصوصية مطلوبة
2. **جرّب الطرفي ثانيًا**: إذا كنا في متصفح والنموذج المحلي غير متاح
3. **اسقط للسحابي أخيرًا**: إذا فشل كل ما سبق أو المهمة معقدة جدًا

## آلية السقوط (Graceful Fallback)
```
local (ollama) → edge (webgpu) → cloud (gemini)
      ↓ failure        ↓ failure          ↓ failure
   try next         try next          return error
```

## الجوهرة المخفية: تصويت النماذج (Model Voting)
للمهام الحرجة، تُرسل المطالبة لثلاثة نماذج مختلفة:
- إذا اتفق اثنان: يُعتمد رأيهما
- إذا اختلف الثلاثة: يُطلب التدخل البشري

هذا يمنع "الهلوسة" ويزيد الثقة في المخرجات.

## تكامل
- `prompt-weaver`: يعد المطالبة قبل إرسالها لأي نموذج
- `edge-whisperer`: يتولى النماذج الطرفية
- `trust-chain`: يسجل أي نموذج استُخدم ومتى


## Purpose
Act as a board of directors for model routing — consults three tiers (Local Ollama, Edge WebGPU, Cloud Gemini/OpenAI) with graceful fallback, plus optional model voting for critical tasks where hallucination must be minimized.

## Constitutional Alignment
Model selection respects data sensitivity — local models are preferred for private or sensitive data to prevent cloud exposure. Voting for critical tasks ensures majority consensus before accepting a response. Every model invocation is logged in trust-chain with the model ID and tier used.

## Operational Flow
Request arrives → evaluate complexity and privacy requirements → try local (Ollama) first → if unavailable or insufficient, try edge (WebGPU) → if still insufficient, fall back to cloud (Gemini/OpenAI) → for critical tasks, dispatch to 3 models → vote: if 2 agree adopt, if all differ escalate to human → result logged in trust-chain.

## Failure Modes
All three tiers fail — no fallback remains; voting tie without human intervention stalls task completion; local model hallucinates on non-critical tasks with no cross-check; trust-chain write failure loses the model invocation audit record.