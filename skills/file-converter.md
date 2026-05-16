# File Converter — محول الملفات الشامل

محول الصيغ يتعامل مع جميع أنواع الملفات: مستندات وصور وفيديو وصوت وأرشيفات. يحول بين الصيغ بجودة عالية وبسرعة. يكتشف الصيغة الأصلية تلقائياً ويقترح أفضل صيغة للتحويل. يتعامل مع التحويلات المجمعة بذكاء لزيادة الإنتاجية.

## Purpose / الغرض

Convert files between formats including documents, images, audio, video, and archives.

## Constitutional Alignment / التوافق الدستوري

- **Quality Preservation**: الجودة الأصلية محفوظة في التحويل
- **Lossless Priority**: التحويل بدون فقدان هو الخيار الافتراضي
- **Data Security**: الملفات لا تُخزن بعد التحويل

## Operational Flow / التدفق التشغيلي

1. Agent receives file conversion request
2. Detects source format and validates file integrity
3. Selects optimal conversion parameters
4. Converts and returns file in target format

## Failure Modes / أنماط الفشل

- **Unsupported format**: Detect unknown extension — suggest alternatives
- **Corrupted source file**: Detect via header validation — request reupload
- **Output too large**: Detect size threshold — offer compression options

## References

- `multi-tool-exporter.md` — multi-format export pipeline
- `data-analysis-engine.md` — data format conversions
