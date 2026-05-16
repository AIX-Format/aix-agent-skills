# Crypto Tracker — متتبع العملات الرقمية

متتبع الأسواق الرقمية يراقب أسعار العملات المشفرة في الوقت الحقيقي. يحلل المحافظ الاستثمارية ويحسب الأرباح والخسائر. يقدم بيانات تاريخية ورسوم بيانية للاتجاهات. ينبه عند تحقيق الأسعار أهدافاً محددة أو عند حدوث تغييرات حادة في السوق.

## Purpose / الغرض

Track cryptocurrency prices, manage portfolios, monitor market data, and set price alerts.

## Constitutional Alignment / التوافق الدستوري

- **Data Accuracy**: الأسعار محدثة ومجمعة من بورصات موثوقة
- **No Financial Advice**: لا يقدم توصيات استثمارية
- **Transparency**: جميع المصادر ومصادر البيانات موضحة

## Operational Flow / التدفق التشغيلي

1. Agent receives crypto query (price, portfolio, alert, history)
2. Queries exchange APIs and aggregators for current data
3. Calculates portfolio value and performance metrics
4. Returns formatted data with charts and alerts

## Failure Modes / أنماط الفشل

- **Stale price data**: Detect latency > 60s — flag delayed data
- **Exchange API outage**: Failover to alternative data source
- **Portfolio sync error**: Validate wallet addresses — retry with corrected input

## References

- `data-analysis-engine.md` — advanced market analysis
- `news-aggregator.md` — crypto news integration
