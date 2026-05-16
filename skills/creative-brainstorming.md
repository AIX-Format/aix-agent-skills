# Creative Brainstorming — ينبوع الإبداع

في فضاء الأفكار اللانهائي، حيث يلتقي الخيال بالمنطق وينبثق الجديد من رحم المألوف، يأتي هذا المهارة ليكون مهندس الإلهام. يشعل شرارة الإبداع بأساليب منظمة: خريطة العقل التي ترسم الأفكار كالأشجار المتفرعة، وSCAMPER التي تعيد تشكيل القديم إلى جديد، والعصف الذهني العكسي الذي يبحث في الظل عن النور. يحوّل الفراغ إلى زخم والغموض إلى رؤية.

## Purpose / الغرض

Generate creative ideas, concepts, and solutions through structured brainstorming techniques including mind mapping, SCAMPER, reverse brainstorming, and lateral thinking prompts. Adapted from GemClaw brainstorming-skills.ts.

## Constitutional Alignment / التوافق الدستوري

- **Serve Humanity / خدمة الإنسانية**: Creativity serves human expression and problem-solving; outputs are tools for human decision-making.
- **No Deception / لا خداع**: All generated ideas are clearly labeled as AI-produced suggestions, not verified facts or expert recommendations.
- **Diversity / التنوع**: Each brainstorming session produces varied perspectives across multiple dimensions (risk, cost, novelty, feasibility).
- **Attribution / الإسناد**: When building on existing concepts, the source inspiration is acknowledged.

## Operational Flow / التدفق التشغيلي

1. Agent receives topic, problem statement, or creative brief with any constraints (budget, time, audience).
2. Selects and applies one or more brainstorming techniques based on the problem type (mind map for exploration, SCAMPER for improvement, reverse for risk analysis).
3. Generates diverse ideas at varying levels of abstraction and novelty, scored on feasibility and originality.
4. Returns structured output grouped by category or technique, with novelty and feasibility scores for each idea.
5. Optionally clusters related ideas and suggests combinations for hybrid solutions.

## Failure Modes / أنماط الفشل

| Mode | Detection | Recovery |
|------|-----------|----------|
| Vague topic | Input is under 5 words or lacks domain | Request specific focus area with at least one constraint |
| Too many ideas | Count exceeds configured limit (default 20) | Return top 10 by feasibility score, offer to show more |
| Technique mismatch | Selected technique unsuitable for problem type | Suggest alternative technique and re-run |
| Repetitive output | >50% of ideas share the same base concept | Apply randomization and force category diversity |
| Novelty floor | All scores below threshold | Widen search space with analogies from unrelated domains |

## References

- Related: `content-creator.md` to develop brainstormed ideas into finished content
- Related: `self-improvement-trainer.md` to evaluate which techniques produced the best outcomes
