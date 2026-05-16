# Semantic Memory — الذاكرة الدلالية

نظام الذاكرة الطويلة المدى يخزن المعلومات في قواعد بيانات متجهة للبحث الدلالي. يستخدم التضمينات الدلالية لربط المفاهيم المتشابهة. يسترجع المعلومات ذات الصلة بسرعة بناءً على المعنى وليس الكلمات فقط. يتعلم من التفاعلات لتحسين دقة الاسترجاع مع الوقت.

## Purpose / الغرض

Store, index, and retrieve information using vector embeddings for semantic search across long-term memory.

## Constitutional Alignment / التوافق الدستوري

- **Data Permanence**: المعلومات تبقى ولا تُحذف دون طلب
- **Privacy**: الذاكرة خاصة ولا تشارك مع وكلاء آخرين
- **Forgetting**: للمستخدم الحق في حذف أي ذاكرة في أي وقت

## Operational Flow / التدفق التشغيلي

1. Agent receives information to store or query
2. Generates vector embedding using embedding model
3. Stores in vector database with metadata or performs similarity search
4. Returns ranked results with relevance scores

## Failure Modes / أنماط الفشل

- **Low recall**: Detect relevance score below threshold — expand query embedding
- **Index corruption**: Detect via consistency check — rebuild from backup
- **Embedding drift**: Detect dimension mismatch — re-embed with current model version

## References

- `note-taking.md` — structured note storage and retrieval
- `fractal-memory.md` — multi-scale memory architecture
- `continuous-learner.md` — learning from memory patterns
