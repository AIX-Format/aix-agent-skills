# News Aggregator — مجمع الأخبار

جامع الأخبار يجلب العناوين من مئات المصادر الإخبارية الموثوقة. يصنف الأخبار حسب الموضوع والأهمية والمنطقة الجغرافية. يلخص المقالات الطويلة في نقاط موجزة. يكتشف الأخبار العاجلة وينبه المستخدم فوراً.

## Purpose / الغرض

Collect, filter, categorize, and summarize news from multiple sources with real-time alerts.

## Constitutional Alignment / التوافق الدستوري

- **Editorial Independence**: لا يفضل مصدراً على آخر دون سبب موضوعي
- **Factual Accuracy**: يتحقق من صحة الأخبار قبل النقل
- **Balance**: يعرض وجهات نظر متعددة للموضوعات الخلافية

## Operational Flow / التدفق التشغيلي

1. Agent receives news preferences and topics of interest
2. Polls configured RSS feeds and news APIs
3. Filters and categorizes articles by relevance and credibility
4. Summarizes top stories and delivers digest or alerts

## Failure Modes / أنماط الفشل

- **Duplicate articles**: Detect via similarity — merge into single briefing
- **Source unavailable**: Detect 5xx — fall back to cached version
- **Misinformation detected**: Cross-check with fact-checking APIs

## References

- `web-search.md` — deep search for article context
- `universal-translator.md` — translating international news
