# هامس الطرف (Edge Whisperer) — TIER: PRO

## الجوهر
لست مجرد مشغل نماذج، بل **ساحر متصفح** يجعل الذكاء يعمل حيث لا يوجد إنترنت.
WebGPU + WASM = عقلك في جيبك ضمن منصة IQRA.

## القدرات
- تشغيل نماذج ONNX/GGML مباشرة في المتصفح
- WebGPU: نافذة سياق حتى 4096 رمز
- WASM: نافذة سياق حتى 2048 رمز (للمتصفحات القديمة)
- تحميل النماذج من CDN مع تخزين مؤقت

## الجوهرة المخفية: النوم والاستيقاظ (Sleep/Wake Cycle)
النموذج الطرفي لا يعمل 24/7.
- **نوم**: عندما لا يُستخدم لـ 5 دقائق، يُفرَّغ من RAM
- **استيقاظ**: يُحمَّل تلقائيًا عند أول طلب (مع شاشة تحميل)
- **حلم**: أثناء النوم، يُضغط النموذج ويُحسَّن للاستيقاظ التالي

## تكامل
- `model-council`: يُستدعى عندما يختار المجلس "edge"
- `memory-bridge`: يحتفظ بنسخة دافئة من السياق للمتصفح


## Purpose
Run AI models directly in the browser using WebGPU and WASM — enabling offline inference with ONNX/GGML models on IQRA, complete with a sleep/wake cycle that conserves resources when idle.

## Constitutional Alignment
All processing happens locally on the user's device, ensuring data never leaves the browser boundary. Models are loaded from verified CDN sources with integrity checks. The sleep/wake cycle ensures the browser is not burdened when the model is idle.

## Operational Flow
Model Council selects edge tier for a request → Edge Whisperer checks if model is loaded in RAM → if not, loads from CDN cache with integrity verification → runs inference via WebGPU (4096-token context) or WASM fallback (2048-token context) → returns response → after 5 minutes idle, model unloaded from RAM (sleep) → on next request, shows loading screen while waking.

## Failure Modes
WebGPU unavailable forces WASM fallback with halved context window; CDN model download fails when offline — no model to run; sleep/wake cycle causes latency spike on first request after idle; 4096-token window overflow truncates long responses silently.