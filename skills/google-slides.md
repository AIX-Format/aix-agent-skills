# Google Slides — صانع العروض التقديمية

مصمم الشرائح ينشئ عروضاً تقديمية متكاملة من الصفر أو من قوالب. يتعامل مع النصوص والصور والرسوم البيانية والانتقالات. يستخدم Slides API لإضافة الشرائح وتنسيقها وترتيبها. يحول البيانات والمحتوى إلى عروض جاهزة للعرض.

## Purpose / الغرض

Create, edit, format, and present Google Slides presentations via the Google Slides API.

## Constitutional Alignment / التوافق الدستوري

- **Aesthetic Integrity**: يحافظ على التناسق البصري للعرض
- **No Unauthorized Publish**: لا ينشر العرض دون موافقة المستخدم
- **Accessibility**: جميع الشرائح تتبع معايير الوصول للألوان والخطوط

## Operational Flow / التدفق التشغيلي

1. Agent receives presentation request (create slide deck, add content, apply theme)
2. Authenticates via Google OAuth and creates or opens presentation
3. Uses presentations.batchUpdate for slide operations
4. Returns link to presentation and slide count summary

## Failure Modes / أنماط الفشل

- **Theme mismatch**: Detect layout errors — fall back to default theme
- **Image insertion failure**: Detect 400 — verify image URL accessibility before submission
- **Slide limit exceeded**: Detect 403 — warn user about maximum slide count

## References

- `google-docs.md` — content sourcing for presentations
- `google-drive.md` — final storage and sharing of presentations
