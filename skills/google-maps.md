# Google Maps — دليل المواقع والطرق

متصفح الجغرافيا يقدم خدمات تحديد المواقع والاتجاهات والبحث عن الأماكن عبر Maps API. يحسب المسافات وأوقات الوصول ويزود بمعلومات حركة المرور الحية. يكشف عن المطاعم والمحطات وأماكن الاهتمام القريبة. يحول الإحداثيات إلى عناوين مفهومة والعكس.

## Purpose / الغرض

Provide location search, directions, place details, geocoding, and real-time traffic via the Google Maps Platform.

## Constitutional Alignment / التوافق الدستوري

- **Location Privacy**: لا يشارك موقع المستخدم دون إذن صريح
- **Accuracy First**: يعرض هوامش الخطأ في بيانات الموقع
- **No Tracking**: لا يُخزن سجل المواقع بعد انتهاء الجلسة

## Operational Flow / التدفق التشغيلي

1. Agent receives location query (directions, place search, geocode)
2. Authenticates via API key with Maps service enabled
3. Calls appropriate endpoint (Directions API, Places API, Geocoding API)
4. Returns formatted results with maps URLs and metadata

## Failure Modes / أنماط الفشل

- **API quota exceeded**: Detect 429 — throttle requests and alert user
- **Invalid address**: Detect 400 — suggest corrected address using autocomplete
- **No results found**: Detect ZERO_RESULTS — expand search radius and retry

## References

- `weather-intelligence.md` — combining location with weather data
- `universal-translator.md` — translating place names and reviews
