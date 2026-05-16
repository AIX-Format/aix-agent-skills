# Google Sheets — جدول البيانات الآلي

محلل الجداول يتعامل مع الخلايا والنطاقات والمخططات والصيغ عبر Sheets API. يمكنه إدراج البيانات وتحديثها وفرزها وتصفيتها وإنشاء الرسوم البيانية. يتعامل مع آلاف الصفوف بذاكرة فعالة. يوفر تحليلاً فورياً للبيانات المدخلة.

## Purpose / الغرض

Perform spreadsheet operations — create, read, update, format, chart, and analyze data in Google Sheets.

## Constitutional Alignment / التوافق الدستوري

- **Data Accuracy**: لا يُغير الصيغ دون التحقق من تأثيرها
- **Privacy**: لا يقرأ بيانات حساسة دون تفويض
- **Idempotency**: العمليات المتكررة لا تنتج تكراراً في البيانات

## Operational Flow / التدفق التشغيلي

1. Agent receives spreadsheet request (query, update, analyze, chart)
2. Authenticates with Google OAuth and targets the sheet range
3. Executes via spreadsheets.values.batchGet/batchUpdate or sheets.batchUpdate for formatting
4. Returns structured table or chart reference

## Failure Modes / أنماط الفشل

- **Range overflow**: Detect 400 — clamp to valid sheet dimensions
- **Formula parse error**: Validate formula syntax server-side before write
- **Concurrent write collision**: Detect 412 — implement retry with exponential backoff

## References

- `google-docs.md` — embedding sheet data in documents
- `data-analysis-engine.md` — advanced analytics on sheet data
