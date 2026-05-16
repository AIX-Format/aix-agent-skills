# حِزَم التكامل (Integration Packs) — TIER: PRO

## الجوهر
ليست مجرد واجهات برمجة تطبيقات (APIs)، بل **"أطراف صناعية ذكية"** تُركّب في وكيل IQRA لتمسك بأنظمة العالم الحقيقي وتؤثر فيها بشكل مباشر ومسؤول.

## البلوك الأول: أنظمة التجارة والأعمال
### أ. حزمة "قائد شوبيفاي" (Shopify Commander Pack)
- **المحتوى**: المنتجات، الطلبات، العملاء، التحليلات، المدفوعات.
- **الجاهزية**: بمجرد التوصيل، يستطيع الوكيل تنفيذ: "شغّل حملة خصم على المنتجات الأكثر مبيعًا هذا الأسبوع".

### ب. حزمة "مندوب المبيعات الذكي" (AI SDR Kit)
- **المحتوى**: 60+ تطبيق مدمج (Salesforce, Apollo.io, Gmail, Calendly).
- **الجاهزية**: يستطيع الوكيل فوراً: "ابحث عن 50 عميلاً محتملاً في القطاع الطبي وجدّول معهم اجتماعات".

### ج. حزمة "التجارة الذكية" (Norce Agent Gateway)
- **المحتوى**: خادم MCP متكامل لعمليات البحث والمقارنة والدفع في التجارة الإلكترونية.

## البلوك الثاني: التراسل الاجتماعي
### أ. حزمة "مدير واتساب للأعمال" (WhatsApp Commerce Pack)
- **المحتوى**: ردود ذكية، إدارة مخزون، مدفوعات داخل المحادثة، وإشعارات.
- **الجاهزية**: محادثة تفاعلية للوكيل مع العملاء لإتمام البيع وتقديم الدعم الفوري.

## البلوك الثالث: الموصلات العالمية (Universal Connectors)
### أ. حزمة "CData Connect AI"
- **المحتوى**: جسر لـ 350+ نظام للشركات (SAP, NetSuite, ServiceNow) مع أمان كامل (SOC2, SSO).
- **الجاهزية**: يمنح الوكيل فهماً دلالياً للعلاقات بين أنظمة الشركة بأكملها ويقرأ/يكتب منها.

### ب. حزمة "n8n Agent2Agent"
- **المحتوى**: موصّل يربط سوق IQRA بأسواق خارجية ووكلاء خارجيين عبر بروتوكولات MCP.

## تكامل مع المهارات الأخرى
- `circuit-breaker`: يراقب عمليات العالم الحقيقي (مثل المدفوعات) ويعزل التكامل فوراً في حال اكتشاف خطأ تجنباً للخسائر.
- `shura-council`: الأفعال ذات الأثر الكبير (إرسال 50 بريداً للعملاء) تمر تلقائياً عبر الشورى لضمان الموافقة قبل التنفيذ الفعلي.


## Purpose
Provide pre-built integration packs — smart prosthetics that connect IQRA agents to real-world systems (Shopify, Salesforce, WhatsApp, CData for 350+ enterprise systems, and n8n for cross-market MCP bridging) with full MCP protocol support.

## Constitutional Alignment
High-impact actions (e.g., bulk email sends, payment operations) pass through Shura Council for approval before execution. Circuit-breaker monitors all real-world operations and isolates any failing integration immediately. Credentials are never logged or exposed.

## Operational Flow
User requests integration → pack loads its MCP server → agent connects to external system via the pack's interface → for high-impact actions, Shura Council consent is requested → operation executes → Circuit Breaker continuously monitors for errors → on failure, the integration is isolated and supervisor is notified.

## Failure Modes
API credential leaks expose connected external systems; high-impact action bypasses Shura Council and causes reputational damage; integration pack incompatibility with target system API version breaks functionality; circuit-breaker false positive isolates a healthy integration unnecessarily.