# Google Drive — الملاحة في سحابة الملفات

مدير ملفات جوجل درايف يتولى رفع وتنزيل ومشاركة وترتيب الملفات في السحابة. يمكنه البحث في آلاف المستندات باستخدام الكلمات المفتاحية والتاريخ والأنواع. يتكامل مع مساحة التخزين السحابية بأذونات دقيقة تمنع الوصول غير المصرح به. يحول تنقلات الملفات المعقدة إلى أوامر بسيطة تنفذ بسرعة.

## Purpose / الغرض

Upload, download, share, search, and organize files and folders on Google Drive via the Drive API.

## Constitutional Alignment / التوافق الدستوري

- **الخصوصية أولاً Privacy First**: لا يُطلّع على محتوى الملفات دون إذن صريح
- **الملكية Ownership**: يُحترم مالك الملف فلا يُنقل أو يُحذف بدون تفويض
- **Transparency**: كل عملية تسجيل تدقيق متاح للرجوع إليه

## Operational Flow / التدفق التشغيلي

1. Agent receives Drive command (upload, download, search, share, organize)
2. Authenticates via Google OAuth 2.0 with Drive-scoped token
3. Calls appropriate Drive API endpoint (files.create, files.get, permissions.create)
4. Returns structured result with file ID, name, and share status

## Failure Modes / أنماط الفشل

- **Storage quota exceeded**: Detect 403 — alert user and suggest cleanup
- **File not found**: Detect 404 — verify path and retry with corrected query
- **Permission denied**: Detect 403 — escalate access request to user

## References

- `gmail-integration.md` — sibling Google Workspace skill
- `calendar-manager.md` — sibling calendar skill for unified auth flow
