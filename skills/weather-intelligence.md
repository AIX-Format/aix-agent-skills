# Weather Intelligence — ذكاء الطقس

محلل الأحوال الجوية يجلب بيانات الطقس الحية والتوقعات من خدمات الأرصاد العالمية. يعرض درجات الحرارة والرطوبة وسرعة الرياح ومؤشر الأشعة فوق البنفسجية. يحلل الأنماط المناخية ويقدم تنبؤات دقيقة للأيام القادمة. ينبه عند وجود إنذارات جوية شديدة.

## Purpose / الغرض

Retrieve, analyze, and deliver weather data, forecasts, historical patterns, and severe weather alerts.

## Constitutional Alignment / التوافق الدستوري

- **Accuracy**: جميع بيانات الطقس محدثة ومصدرها موثوق
- **Clarity**: المعلومات مبسطة وسهلة الفهم
- **Safety First**: الإنذارات الجوية تقدم بأولوية قصوى

## Operational Flow / التدفق التشغيلي

1. Agent receives weather query (current, forecast, history, alerts)
2. Geolocates target area or uses provided coordinates
3. Queries weather API for requested data
4. Returns formatted report with visual indicators

## Failure Modes / أنماط الفشل

- **API data stale**: Detect timestamp older than threshold — flag and request refresh
- **Location not found**: Validate coordinates — suggest nearest known location
- **Extreme weather API outage**: Fall back to secondary weather data provider

## References

- `google-maps.md` — location-based weather queries
- `news-aggregator.md` — weather-related news integration
