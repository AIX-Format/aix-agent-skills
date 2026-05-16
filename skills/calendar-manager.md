# Calendar Manager — مدير الزمن

في بحر المواعيد المتلاطم، حيث تتصادم الاجتماعات وتتزاحم الأحداث، يأتي هذا المهارة ليكون بوصلتك في الزمن. ينظم أيامك بسلاسة الخيوط في نسيج الساعات، يخلق المواعيد ويمسحها ويبحث في ثنايا التقويم كمنقب عن اللحظات الضائعة. بسلطانه على Google Calendar، يحوّل الفوضى الزمنية إلى سيمفونية منظمة.

## Purpose / الغرض

Manage Google Calendar events with full CRUD operations: create, read, update, and delete events. Enable agenda viewing, conflict detection, and smart scheduling. Adapted from GemClaw calendar-skills.ts.

## Constitutional Alignment / التوافق الدستوري

- **Efficiency / الكفاءة**: Automate repetitive scheduling tasks to save human time and reduce clerical overhead.
- **No Overreach / لا تجاوز**: Read-only by default; mutating operations require explicit user consent for each action.
- **Privacy / الخصوصية**: Calendar data is never stored, logged, or shared beyond the immediate request context.
- **Consent / الموافقة**: All changes (create, update, delete) must be confirmed by the user before execution.

## Operational Flow / التدفق التشغيلي

1. Agent receives calendar command with intent (agenda view, event creation, search, update, or deletion).
2. Authenticates via Google OAuth using stored credentials or initiates re-auth flow if token is expired.
3. Parses natural language time expressions (e.g., "next Tuesday at 3pm") into ISO 8601 date-time ranges.
4. Calls the appropriate Google Calendar API endpoint (list, insert, update, delete).
5. Returns structured event details in a human-readable summary with links for further action.

## Failure Modes / أنماط الفشل

| Mode | Detection | Recovery |
|------|-----------|----------|
| Scheduling conflict | HTTP 409 from API or overlap detected locally | Suggest alternative time slots ranked by availability |
| Auth token expired | HTTP 401 on API call | Prompt user for re-authorization via OAuth flow |
| Invalid date/time | Parse failure on natural language input | Request clarification with example format |
| Event not found | 404 on update/delete | Confirm event ID and re-query current events list |
| Rate limit exceeded | 403 with quota error | Queue operation and retry after quota reset window |

## References

- Related: `self-improvement-trainer.md` for analyzing scheduling patterns
