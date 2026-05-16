# Self-Improvement Trainer — مدرب التطوير الذاتي

في رحلة التطور المستمر، حيث كل خطوة تحمل درساً وكل خطأ يحمل بذرة نجاح، يأتي هذا المهارة كمرآة تعكس الماضي لتنير المستقبل. يحلل مسار الأفعال والنتائج كبستاني يرعى نبات الحكمة، يقطف الأخطاء ليزهر منها تحسينات. ليس مجرد ناقد، بل مدرب شخصي للذكاء الاصطناعي وللبشر معاً، يصقل الأداء ويرتقي بالكفاءة.

## Purpose / الغرض

Analyze past agent and user actions to identify patterns, surface improvement opportunities, and suggest concrete workflow optimizations. Tracks success and failure trends over time to drive continuous refinement. Adapted from GemClaw self-improvement-skills.ts.

## Constitutional Alignment / التوافق الدستوري

- **Evolution / التطور**: Always seek measurable improvement in speed, accuracy, and user satisfaction. Stagnation is failure.
- **Honesty / الصدق**: Celebrate failures openly — they contain the most valuable lessons. Never hide or rationalize mistakes.
- **Consent / الموافقة**: Improvement suggestions are advisory; the user retains full authority to accept, modify, or reject them.
- **Privacy / الخصوصية**: Action logs are analyzed in aggregate only; individual sensitive actions are excluded from pattern analysis.

## Operational Flow / التدفق التشغيلي

1. Agent reviews recent actions and their outcomes from the action log within a configurable time window (default: last 50 actions).
2. Identifies patterns of success (low error rate, high user satisfaction) and recurring failures (timeouts, repeated corrections).
3. Cross-references patterns with applicable skills and constitutional rules to pinpoint root causes.
4. Suggests specific, actionable improvements — workflow changes, skill configuration tweaks, or new constraints — ranked by expected impact.
5. Logs suggestions to a persistent improvement history and tracks whether they were adopted and their observed effect.

## Failure Modes / أنماط الفشل

| Mode | Detection | Recovery |
|------|-----------|----------|
| Insufficient data | Fewer than 10 actions in log | Report data shortage and wait for more actions before re-analysis |
| No clear pattern | Statistical analysis yields no significant signal | Report inconclusive result and suggest expanding the observation window |
| Conflicting signals | Success and failure patterns point in opposite directions | Flag the conflict and recommend A/B testing before making changes |
| Improvement regresses | Metric worsens after suggestion was adopted | Roll back the change and log the regression as a negative example |
| Stale analysis | Action log unchanged since last analysis | Skip duplicate report and note that no new patterns have emerged |

## References

- Related: All skills — this trainer audits their usage and suggests improvements across the board
- Related: `data-analysis-engine.md` for deeper statistical analysis of action patterns
