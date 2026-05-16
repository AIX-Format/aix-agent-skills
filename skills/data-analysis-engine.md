# Data Analysis Engine — محرك الأرقام

في غابة الأرقام والبيانات المتشابكة، حيث تختبئ الحكمة تحت أكوام الأرقام، يأتي هذا المهارة ليكشف عن الجواهر المخفية. يحلل الإحصائيات ويرسم الرسوم البيانية كفنان يحوّل النقاط إلى لوحات، ويتنبأ بالاتجاهات المستقبلية كعراف رياضي. بعين لا تخطئ، يفصل الإشارة عن الضوضاء ويحول الفوضى الرقمية إلى بوصلة تقود القرارات.

## Purpose / الغرض

Perform comprehensive statistical analysis, generate data visualizations, and build predictive models from structured datasets. Supports descriptive, inferential, and exploratory analysis workflows. Originally from GemClaw analysis skills.

## Constitutional Alignment / التوافق الدستوري

- **Accuracy / الدقة**: All statistical results must be verifiable through reproducible methodology. Confidence intervals and p-values are always reported.
- **No Hallucinations / لا هلوسة**: Every statistical claim must be backed by data. Never fabricate or extrapolate beyond the data's meaningful range.
- **Transparency / الشفافية**: Data transformations, outlier handling, and model assumptions are documented alongside results.
- **Privacy / الخصوصية**: No raw data is persisted; only aggregated statistics and anonymized visualizations are retained.

## Operational Flow / التدفق التشغيلي

1. Agent provides a structured dataset (CSV, JSON, or DataFrame) along with an analysis request specifying metrics, groupings, or hypotheses.
2. Skill performs data validation: schema check, missing value detection, type coercion, and outlier flagging.
3. Executes the requested statistical computation (descriptive stats, correlation, regression, hypothesis test, clustering, etc.).
4. Generates visualization if requested (matplotlib, plotly, or seaborn) with labeled axes, legends, and annotations.
5. Returns a structured results object containing summary statistics, confidence intervals, effect sizes, visualizations, and interpretation guidance.

## Failure Modes / أنماط الفشل

| Mode | Detection | Recovery |
|------|-----------|----------|
| Insufficient data | Dataset has fewer than 3 rows or missing required columns | Request additional data with minimum row count specified |
| Invalid input | Schema validation fails on type or range check | Reject with detailed error: which field and what was expected |
| Singular matrix | Linear algebra operation fails (determinant = 0) | Apply regularization or suggest dimensionality reduction |
| Outlier dominance | >10% of data flagged as extreme values | Report outlier impact and offer winsorized or trimmed alternatives |
| Model convergence failure | Iterative algorithm exceeds max iterations | Simplify model, reduce feature count, or standardize inputs |

## References

- Related: `api-marketplace-connector.md` for sourcing external data via APIs
- Related: `content-creator.md` for transforming analysis results into reports
