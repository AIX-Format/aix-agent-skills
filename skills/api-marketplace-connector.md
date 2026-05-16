# API Marketplace Connector — السوق المفتوح

في سوق الواجهات المترامي، حيث تتناثر الخدمات كالنجوم في سماء الرقمنة، يأتي هذا المهارة ليكون دليلك عبر المتاهة. يبحث في أسواق الواجهات (RapidAPI، APILayer) ليكشف عن الخدمات التي تحتاجها، ويدمجها في عملك بسلاسة الأمواج. كجسر بين العوالم الرقمية، يفتح لك أبواب الإمكانيات اللانهائية.

## Purpose / الغرض

Connect to external API marketplaces (RapidAPI, APILayer) to discover, evaluate, and integrate third-party services into agent workflows. Adapted from GemClaw api-marketplace-skills.ts.

## Constitutional Alignment / التوافق الدستوري

- **Security / الأمان**: Validate all API endpoints before calling to prevent injection or data leakage. Never execute untrusted responses.
- **No Hardcoded Keys / لا مفاتيح ثابتة**: Credentials must come exclusively from environment variables or secure vaults. Hardcoded keys are rejected at validation time.
- **Rate Limiting / تحديد المعدل**: Respect marketplace rate limits and implement exponential backoff on 429 responses to avoid being throttled or banned.
- **Transparency / الشفافية**: All integrated APIs are logged with their source, version, and pricing tier for auditability.

## Operational Flow / التدفق التشغيلي

1. Agent receives service requirement specifying desired functionality, data format, and budget constraints.
2. Searches configured API marketplaces (RapidAPI, APILayer) for matching APIs using keyword and category filters.
3. Returns ranked list of available endpoints with pricing, rate limits, and documentation links.
4. Agent selects an API; the skill configures authentication and generates integration boilerplate.
5. Validates the integration with a test call and reports connectivity status.

## Failure Modes / أنماط الفشل

| Mode | Detection | Recovery |
|------|-----------|----------|
| No matching API | Empty search result set | Suggest alternative marketplaces or fallback services |
| API key missing | Env variable check fails | Report which credential is missing and where to set it |
| Rate limit exceeded | HTTP 429 response | Implement exponential backoff and notify agent of delay |
| Endpoint deprecated | 410 Gone or docs mismatch | Re-query marketplace for updated version of the API |
| Authentication failure | 401/403 on test call | Verify credential validity and permissions, request re-configuration |

## References

- Related: `data-analysis-engine.md` for processing API response data
- Related: `software-engineer.md` for generating integration code
