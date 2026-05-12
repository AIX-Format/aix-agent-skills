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
TODO: Define purpose.

## Constitutional Alignment
TODO: Define constitutional alignment.

## Operational Flow
TODO: Define operational flow.

## Failure Modes
TODO: Define failure modes.