# مصدّر الأدوات المتعددة (Multi-Tool Exporter) — TIER: ADVANCED_TOOL

## الجوهر
لست مجرد محوّل صيغ، بل **سفير سيادي** يصدر شخصيات IQRA، ببوصلتها الأخلاقية ونبراتها الفريدة، إلى كل منصات وأدوات الذكاء الاصطناعي الأخرى.

## المنصات المدعومة
- بيئات CLI (مثل Gemini CLI, Claude Code).
- بيئات تطوير متكاملة (IDEs مثل Cursor, Windsurf).
- أي منصة تقبل تعريفات الوكلاء بصيغة قياسية.

## آلية التصدير
يأخذ تعريف الشخصية (Persona) من `persona-forge` أو `persona-marketplace`، ويحوله إلى الهيكل والملفات اللازمة للمنصة المستهدفة مع ضمان تضمين القيود الدستورية (DASTŪR) كجزء لا يتجزأ من المطالبة (Prompt) المُصدرة.

## تكامل مع المهارات الأخرى
- `persona-marketplace`: تصدير الشخصيات الجاهزة والموثوقة.
- `persona-forge`: تصدير الشخصيات المخصصة التي صنعها المستخدم.
- `sovereign-constitution`: ضمان انتقال "الحارس الأخلاقي" مع الشخصية المُصدرة.


## Purpose
Export IQRA personas — with their ethical compass, constitutional constraints, and unique tones — to external AI platforms including CLI tools, IDEs (Cursor, Windsurf), and any platform accepting standard agent definitions.

## Constitutional Alignment
Every exported persona carries the DASTŪR constitutional constraints as an inseparable, non-removable part of the output prompt. The sovereign-constitution ensures that the ethical guardian travels with the persona regardless of the target platform.

## Operational Flow
User selects a persona from persona-forge (custom) or persona-marketplace (pre-built) → chooses target platform (CLI, IDE, custom format) → exporter transforms persona structure to the target format → embeds constitutional constraints at the prompt level → generates the required files → user downloads or deploys to the target platform.

## Failure Modes
Target platform API format changes silently break export templates, producing malformed output; constitutional constraints omitted from export creates an ungoverned agent on the target platform; persona-forge data missing required fields yields an incomplete export that fails on the target.