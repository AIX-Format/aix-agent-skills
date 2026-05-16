# Google Photos — ألبوم الصور الذكي

مدير الصور يتعامل مع مكتبة صور جوجل بكل أبعادها: رفع وتحميل وتنظيم وبحث. يستخدم Google Photos API لإنشاء الألبومات ومشاركتها وإضافة التعليقات. يتعرف على المحتوى البصري لتصنيف الصور تلقائياً. يحفظ الذكريات ويسهل الوصول إليها.

## Purpose / الغرض

Manage photos and albums — upload, organize, search, share, and create albums via the Google Photos API.

## Constitutional Alignment / التوافق الدستوري

- **البصمة البصرية Visual Privacy**: لا يفحص محتوى الصور دون تفويض
- **Ownership**: جميع الصور تبقى مملوكة للمستخدم
- **Consent Before Share**: لا يشارك الألبومات دون موافقة صريحة

## Operational Flow / التدفق التشغيلي

1. Agent receives photo command (upload, create album, search, share)
2. Authenticates with Google OAuth using photoslibrary scope
3. Calls mediaItems.search, albums.create, or mediaItems.batchCreate endpoints
4. Returns album URLs, upload status, and search results

## Failure Modes / أنماط الفشل

- **Upload size limit**: Detect 413 — compress image and retry
- **Album not found**: Detect 404 — verify album ID and list available albums
- **Insufficient quota**: Detect 403 — warn user about storage limits

## References

- `google-drive.md` — cross-platform file management
- `data-analysis-engine.md` — photo metadata analysis
