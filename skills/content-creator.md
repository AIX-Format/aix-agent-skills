# Content Creator — صانع الكلمات

في مملكة القلم والورق الرقمية، حيث الكلمات تبني عوالم وتحرك المشاعر، يأتي هذا المهارة ليصوغ الأفكار كالخزاف الذي يشكل الطين. ينسج المقالات ويخط المسودات الإعلانية ويصوغ منشورات التواصل كالنحات الذي يحيي الصخر. من التقرير الفني إلى التغريدة العابرة، يحول الرسالة إلى فن مقروء يلامس القلوب والعقول.

## Purpose / الغرض

Create engaging content across multiple formats: long-form articles, social media posts, marketing copy, technical documentation, and email campaigns. Adapts tone, style, and structure to audience and platform requirements. Adapted from GemClaw content-creation-advanced-skills.ts.

## Constitutional Alignment / التوافق الدستوري

- **Serve Humanity / خدمة الإنسانية**: All content serves the user's stated goals and avoids manipulation or dark patterns.
- **No Deception / لا خداع**: Content is labeled as AI-generated where required by platform policies or applicable regulations.
- **Originality / الأصالة**: Generated content passes plagiarism checks; direct copying from sources is avoided.
- **Tone Fidelity / دقة النبرة**: The output matches the requested tone (formal, casual, persuasive) without unintended stylistic drift.

## Operational Flow / التدفق التشغيلي

1. Agent receives content brief specifying topic, format (article, post, email, doc), target audience, tone, and length.
2. Researches topic from available sources including search results, knowledge base, and provided reference materials.
3. Structures content with appropriate outline, headings, and flow for the chosen format.
4. Drafts content applying tone guidelines, SEO keywords (if requested), and platform-specific formatting.
5. Returns final piece with metadata: word count, reading time, format, and any required disclaimers.

## Failure Modes / أنماط الفشل

| Mode | Detection | Recovery |
|------|-----------|----------|
| Insufficient context | Brief is under 10 words or has no topic | Request expanded brief with at least topic + audience |
| Tone inconsistency | Style guide comparison flags mismatch | Rewrite with stricter tone adherence and re-check |
| Plagiarism detected | External checker finds >15% match | Rewrite flagged sections with original phrasing |
| Format violation | Output missing required sections | Re-format and resubmit for validation |
| Length out of bounds | Word count differs >30% from request | Trim or expand content and re-balance structure |

## References

- Related: `creative-brainstorming.md` for ideation phase before content creation
- Related: `data-analysis-engine.md` for data-driven content (reports, infographics)
