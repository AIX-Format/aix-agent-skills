# صندوق حماية المهارات (Skill Sandbox) — TIER: PRO

## الجوهر
بيئة معزولة متكاملة مع CI تقوم بتشغيل كل مهارة مقدمة قبل أن تُدرج في متجر IQRA. تحمي المستخدمين من المهارات الخبيثة أو المستهلكة للموارد بكثافة.

## متى يتم التفعيل؟
- عند نشر مهارة جديدة.
- عند التحقق من أمان المهارة قبل التثبيت الخارجي.

## بروتوكولات الحماية والمراقبة
1. **الوصول للملفات**: تقييد الوصول للمسارات المصرح بها فقط (`/home/z/my-project/skills/{skill_id}/`) ومنع (`/etc/`, `/root/`).
2. **مكالمات الشبكة**: حصر الاتصال بنقاط النهاية المُعلنة فقط ومنع تسريب البيانات.
3. **حدود الموارد**: مراقبة (CPU < 30s)، (RAM < 512MB)، والعمليات الفرعية.
4. **الفريق الأحمر (Red Team Light)**: اختبار اختراق المطالبات (Prompt Injection) باستخدام سيناريوهات معادية.
5. **سلامة المحتوى**: تحليل ساكن (Static Analysis) للكود لضمان عدم وجود برمجيات خبيثة.

## مستويات العزل (Isolation Levels)
- **صارم (Strict)**: Docker + seccomp (عند النشر للسوق).
- **متوسط (Moderate)**: Deno Sandbox (للـ CI).
- **خفيف (Light)**: Process monitoring (للفحص المحلي السريع).

## تكامل مع المهارات الأخرى
- `skill-evaluator`: يكمل عمل الصندوق؛ الصندوق يتأكد من الأمان، والمقيم يتأكد من الجودة.
- `pipeline-store`: يمنع نشر المسارات إذا فشلت أي مهارة في الصندوق.


## Purpose

Provide an isolated execution environment for testing and verifying skills before they are published to the IQRA marketplace. Enforces filesystem restrictions (skill-owned paths only), network egress limits (declared endpoints only), resource caps (CPU < 30s, RAM < 512 MB), static analysis for malicious code, and lightweight red-team prompt-injection scanning. Supports three isolation levels (Strict/Docker, Moderate/Deno, Light/Process) depending on the deployment context.

## Constitutional Alignment

- **Principle of Least Privilege**: Skills run with the minimum permissions needed — no access to system files, environment secrets, or other skills' data.
- **No Silent Escapes**: Any sandbox breach attempt is logged, alerted, and blocks the skill from marketplace publication.
- **Defense in Depth**: Multiple isolation layers (filesystem + network + resource + static analysis) — no single point of failure.
- **Auditable**: Every sandbox execution leaves a trace on the trust chain with resource consumption and verdict.

## Operational Flow

1. Skill source code arrives for sandboxing (from `skill-evaluator` or `pipeline-store`).
2. Static analysis runs first — scans for obfuscated code, dangerous imports, and network calls to undeclared endpoints.
3. Isolation level is selected based on context (Strict for marketplace publish, Moderate for CI, Light for local dev).
4. Sandbox boots with filesystem mounted to `/home/skills/{skill_id}/`, network egress restricted to declared endpoints, CPU/memory cgroup limits applied.
5. Lightweight red-team probe runs 3 prompt-injection scenarios against the skill.
6. Execution proceeds — all syscalls, file I/O, and network connections are monitored.
7. On completion: resource usage report and security verdict are generated.
8. If any violation detected → skill is blocked from marketplace, detail logged.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Docker daemon unavailable (Strict mode) | Docker API connection refused | Fallback to Moderate (Deno) isolation |
| Static analysis false positive | Known-good library flagged | Whitelist library hash, re-run |
| Resource leak (skill consumes all RAM) | OOM killer triggers | Kill container, log peak usage, flag skill |
| Network egress to undeclared host | DNS resolution outside allowlist | Block connection, log violation, fail the skill |
| Sandbox escape attempt detected | Syscall filter triggers | Immediately terminate, alert system admin |