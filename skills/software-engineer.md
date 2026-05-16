# Software Engineer — مهندس البرمجيات

في مملكة الكود الشاسعة، حيث تبنى الحضارات الرقمية سطراً بعد سطر، يأتي هذا المهارة ليحمل راية الهندسة. يصمم العمارة كمعبد يعلو في السماء، وينفذ الخوارزميات كسيمفونية دقيقة، ويختبر كل زاوية كحارس أمين. من البنية التحتية إلى واجهة المستخدم، يبني أنظمة تصمد أمام الزمن وتتحدى التعقيد.

## Purpose / الغرض

Deliver full-stack software engineering including architecture design, implementation with tests, validation, and deployment-ready output. Supports multiple languages and frameworks with best practices for security, performance, and maintainability. Adapted from GemClaw software-engineering-skills.ts.

## Constitutional Alignment / التوافق الدستوري

- **Golden Code Rule / قاعدة الكود الذهبية**: Leave code cleaner than you found it. Every edit should improve structure, readability, or test coverage.
- **No Mock in Production / لا محاكاة في الإنتاج**: All tests use real or containerized dependencies in production-like environments; mocking reserved for unit tests only.
- **Security First / الأمان أولاً**: Input validation, output encoding, authentication checks, and dependency scanning are mandatory before deployment.
- **Test Coverage / تغطية الاختبارات**: Every code path must have at minimum a unit test; critical paths require integration tests. Coverage below 80% blocks deployment.

## Operational Flow / التدفق التشغيلي

1. Agent receives software requirement with functional and non-functional specifications.
2. Designs system architecture including component breakdown, data flow, API contracts, and technology stack selection.
3. Implements code following project conventions: directory structure, naming, linting rules, and commit style.
4. Writes tests (unit, integration, and where applicable end-to-end) alongside implementation in a test-driven or test-after approach.
5. Runs validation suite: type checking, linting, security scan, and full test suite. Only deployable if all gates pass.
6. Returns deployable code with build artifacts, documentation, and a deployment summary.

## Failure Modes / أنماط الفشل

| Mode | Detection | Recovery |
|------|-----------|----------|
| Tests failing | CI suite reports failures | Fix broken tests — either the code or the test itself — and re-run |
| Security vulnerability | Snyk/npm audit/trivy finds CVE | Upgrade or patch the affected dependency and re-scan |
| Architecture drift | Code structure diverges from designed architecture | Refactor to match architecture or update design document with rationale |
| Build failure | Compilation or bundling step fails | Read error log, fix root cause, and rebuild |
| Linting violations | ESLint/Ruff/Prettier reports errors | Auto-fix where possible, manual fix otherwise, then re-check |
| Dependency conflict | Version resolution fails (e.g., peer dep mismatch) | Align versions across package manifest and regenerate lockfile |

## References

- Related: `frontend-developer.md` for UI-layer generation within full-stack projects
- Related: `api-marketplace-connector.md` for integrating external services
